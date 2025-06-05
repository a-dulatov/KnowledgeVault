from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tinymce.models import HTMLField
import secrets
import hashlib
from datetime import timedelta

class Label(models.Model):
    COLOR_CHOICES = [
        ('#007bff', 'Blue'),
        ('#28a745', 'Green'),
        ('#dc3545', 'Red'),
        ('#ffc107', 'Yellow'),
        ('#6f42c1', 'Purple'),
        ('#fd7e14', 'Orange'),
        ('#20c997', 'Teal'),
        ('#e83e8c', 'Pink'),
        ('#6c757d', 'Gray'),
        ('#17a2b8', 'Cyan'),
    ]
    
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#007bff')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Labels"

class Space(models.Model):
    ICON_CHOICES = [
        ('fas fa-folder', 'Folder'),
        ('fas fa-book', 'Book'),
        ('fas fa-lightbulb', 'Lightbulb'),
        ('fas fa-cog', 'Settings'),
        ('fas fa-rocket', 'Rocket'),
        ('fas fa-star', 'Star'),
        ('fas fa-heart', 'Heart'),
        ('fas fa-trophy', 'Trophy'),
        ('fas fa-graduation-cap', 'Education'),
        ('fas fa-code', 'Code'),
        ('fas fa-database', 'Database'),
        ('fas fa-shield-alt', 'Security'),
        ('fas fa-users', 'Team'),
        ('fas fa-chart-line', 'Analytics'),
        ('fas fa-puzzle-piece', 'Puzzle'),
        ('fas fa-tools', 'Tools'),
        ('fas fa-globe', 'Global'),
        ('fas fa-mobile-alt', 'Mobile'),
        ('fas fa-cloud', 'Cloud'),
        ('fas fa-fire', 'Fire'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True, related_name='spaces')
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fas fa-folder')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Spaces"

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField()
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='articles')
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
    
    def average_rating(self):
        """Calculate average rating for this article"""
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum(r.rating for r in ratings) / len(ratings)
    
    def rating_count(self):
        """Get total number of ratings"""
        return self.ratings.count()
    
    def get_user_rating(self, user):
        """Get rating by specific user"""
        if not user.is_authenticated:
            return None
        try:
            return self.ratings.get(user=user).rating
        except ArticleRating.DoesNotExist:
            return None
    
    def comment_count(self):
        """Get total number of approved comments"""
        return self.comments.filter(is_approved=True, parent__isnull=True).count()
    
    def is_read_by_user(self, user):
        """Check if article has been read by a specific user"""
        if not user.is_authenticated:
            return False
        return self.read_status.filter(user=user).exists()
    
    def get_read_status(self, user):
        """Get read status object for a user"""
        if not user.is_authenticated:
            return None
        try:
            return self.read_status.get(user=user)
        except ArticleReadStatus.DoesNotExist:
            return None
    
    def is_favorited_by_user(self, user):
        """Check if this article has been favorited by the given user"""
        if not user.is_authenticated:
            return False
        return self.favorites.filter(user=user).exists()
    
    def get_view_count(self):
        """Get total number of views for this article"""
        return self.views.count()
    
    def get_unique_view_count(self):
        """Get unique views (by user/IP) for this article"""
        # Count unique users + unique anonymous IPs
        user_views = self.views.filter(user__isnull=False).values('user').distinct().count()
        anonymous_views = self.views.filter(user__isnull=True).values('ip_address').distinct().count()
        return user_views + anonymous_views
    
    def record_view(self, request):
        """Record a view for this article"""
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Get user agent and referrer
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        
        # For anonymous users, use session key
        session_key = request.session.session_key or ''
        
        # Create view record
        ArticleView.objects.create(
            article=self,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip,
            user_agent=user_agent,
            referrer=referrer,
            session_key=session_key
        )


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
    
    def like_count(self):
        """Get number of likes for this paragraph"""
        return self.likes.filter(is_like=True).count()
    
    def dislike_count(self):
        """Get number of dislikes for this paragraph"""
        return self.likes.filter(is_like=False).count()
    
    def get_user_like_status(self, user):
        """Get user's like status for this paragraph (True=like, False=dislike, None=no action)"""
        if not user.is_authenticated:
            return None
        try:
            return self.likes.get(user=user).is_like
        except ParagraphLike.DoesNotExist:
            return None


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
    """Secure, time-limited sharing links for articles and paragraphs"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='share_links')
    paragraph = models.ForeignKey(ArticleParagraph, on_delete=models.CASCADE, related_name='share_links', null=True, blank=True)
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
        if self.paragraph:
            return f"Share link for paragraph '{self.paragraph.title}' in {self.article.title} (expires: {self.expires_at})"
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
        return cls._create_share_link(article=article, paragraph=None, user=user, custom_expiry_hours=custom_expiry_hours)
    
    @classmethod
    def create_for_paragraph(cls, paragraph, user=None, custom_expiry_hours=None):
        """Create a new secure share link for a specific paragraph"""
        return cls._create_share_link(article=paragraph.article, paragraph=paragraph, user=user, custom_expiry_hours=custom_expiry_hours)
    
    @classmethod
    def _create_share_link(cls, article, paragraph=None, user=None, custom_expiry_hours=None):
        """Internal method to create secure share links for articles or paragraphs"""
        settings = ShareSettings.get_settings()
        
        # Build filter for existing shares
        filter_params = {
            'article': article,
            'is_active': True,
            'expires_at__gt': timezone.now()
        }
        if paragraph:
            filter_params['paragraph'] = paragraph
        else:
            filter_params['paragraph__isnull'] = True
        
        # Check if we've reached the maximum shares for this content
        active_shares = cls.objects.filter(**filter_params).count()
        
        if active_shares >= settings.max_shares_per_article:
            # Deactivate oldest link to make room
            oldest_link = cls.objects.filter(**filter_params).order_by('created_at').first()
            if oldest_link:
                oldest_link.is_active = False
                oldest_link.save()
        
        # Create new link
        expiry_hours = custom_expiry_hours or settings.link_expiry_hours
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        
        return cls.objects.create(
            article=article,
            paragraph=paragraph,
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


class ArticleRating(models.Model):
    """User ratings for articles (1-5 stars)"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_ratings')
    rating = models.PositiveIntegerField(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['article', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} rated {self.article.title}: {self.rating}/5"


class ArticleComment(models.Model):
    """Comments on articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
    
    def get_replies(self):
        """Get approved replies to this comment"""
        return self.replies.filter(is_approved=True).order_by('created_at')


class ParagraphLike(models.Model):
    """Like/dislike for individual paragraphs"""
    paragraph = models.ForeignKey(ArticleParagraph, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paragraph_likes')
    is_like = models.BooleanField()  # True for like, False for dislike
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['paragraph', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paragraph', 'is_like']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        action = "liked" if self.is_like else "disliked"
        return f"{self.user.username} {action} paragraph: {self.paragraph.title}"


class ArticleReadStatus(models.Model):
    """Track when registered users read articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_read_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now=True)
    read_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('article', 'user')
        indexes = [
            models.Index(fields=['user', 'last_read_at']),
            models.Index(fields=['article', 'user']),
        ]

    def __str__(self):
        return f"{self.user.username} read '{self.article.title}'"

    @classmethod
    def mark_as_read(cls, article, user):
        """Mark an article as read by a user, or update read count if already read"""
        if not user.is_authenticated:
            return None
            
        read_status, created = cls.objects.get_or_create(
            article=article,
            user=user,
            defaults={'read_count': 1}
        )
        
        if not created:
            read_status.read_count += 1
            read_status.save(update_fields=['last_read_at', 'read_count'])
            
        return read_status


class ArticleFavorite(models.Model):
    """Track articles favorited by users"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_articles')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('article', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} favorited '{self.article.title}'"


class ArticleView(models.Model):
    """Track article views for both registered and anonymous users"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # None for anonymous users
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True)  # For anonymous users
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['article', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['ip_address', '-viewed_at']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"{user_info} viewed '{self.article.title}' at {self.viewed_at}"
