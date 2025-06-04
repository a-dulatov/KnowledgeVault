from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tinymce.models import HTMLField
import secrets
import hashlib
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    tags = models.JSONField(default=list)
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
    @property
    def content(self):
        """Backward compatibility property that combines all paragraph content"""
        return "".join([paragraph.content for paragraph in self.paragraphs.all().order_by('order')])


class ArticleParagraph(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='paragraphs')
    title = models.CharField(max_length=200)
    content = HTMLField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.article.title} - {self.title}"


class ParagraphAttachment(models.Model):
    paragraph = models.ForeignKey(ArticleParagraph, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='paragraph_attachments/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_name} - {self.paragraph.title}"
    
    @property
    def file_size(self):
        try:
            return self.file.size
        except:
            return 0
    
    @property
    def file_extension(self):
        return self.original_name.split('.')[-1].lower() if '.' in self.original_name else ''


# Keep ArticleAttachment for backward compatibility
class ArticleAttachment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_name} - {self.article.title}"
    
    @property
    def file_size(self):
        try:
            return self.file.size
        except:
            return 0
    
    @property
    def file_extension(self):
        return self.original_name.split('.')[-1].lower() if '.' in self.original_name else ''


class ShareSettings(models.Model):
    """Global settings for article sharing"""
    link_expiry_hours = models.PositiveIntegerField(default=24, help_text="Hours until share links expire")
    max_shares_per_article = models.PositiveIntegerField(default=100, help_text="Maximum active shares per article")
    require_authentication = models.BooleanField(default=False, help_text="Require login to view shared articles")
    track_views = models.BooleanField(default=True, help_text="Track views on shared links")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Share Settings"
        verbose_name_plural = "Share Settings"
    
    def __str__(self):
        return f"Share Settings (Expires: {self.link_expiry_hours}h)"
    
    @classmethod
    def get_settings(cls):
        """Get or create default settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class SecureShareLink(models.Model):
    """Secure, time-limited sharing links for articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='share_links')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    view_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['article', '-created_at']),
        ]
    
    def __str__(self):
        return f"Share link for '{self.article.title}' (expires: {self.expires_at})"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_secure_token()
        if not self.expires_at:
            settings = ShareSettings.get_settings()
            self.expires_at = timezone.now() + timedelta(hours=settings.link_expiry_hours)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_secure_token():
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(32)
    
    @property
    def is_expired(self):
        """Check if the link has expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the link is valid (active and not expired)"""
        return self.is_active and not self.is_expired
    
    def record_view(self):
        """Record a view on this share link"""
        self.view_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['view_count', 'last_accessed'])
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired share links"""
        expired_count = cls.objects.filter(expires_at__lt=timezone.now()).delete()[0]
        return expired_count
    
    @classmethod
    def create_for_article(cls, article, user=None, custom_expiry_hours=None):
        """Create a new secure share link for an article"""
        settings = ShareSettings.get_settings()
        
        # Check if we've reached the maximum shares for this article
        active_shares = cls.objects.filter(
            article=article,
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        if active_shares >= settings.max_shares_per_article:
            # Deactivate oldest link to make room
            oldest_link = cls.objects.filter(
                article=article,
                is_active=True,
                expires_at__gt=timezone.now()
            ).order_by('created_at').first()
            if oldest_link:
                oldest_link.is_active = False
                oldest_link.save()
        
        # Create new link
        expiry_hours = custom_expiry_hours or settings.link_expiry_hours
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        
        return cls.objects.create(
            article=article,
            created_by=user,
            expires_at=expires_at
        )


class ShareLinkView(models.Model):
    """Track individual views on shared links"""
    share_link = models.ForeignKey(SecureShareLink, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['share_link', '-viewed_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"View of {self.share_link.article.title} at {self.viewed_at}"
