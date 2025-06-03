from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tinymce.models import HTMLField

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
