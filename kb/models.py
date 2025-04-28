from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    tags = models.JSONField(default=list)
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)
    
    def __str__(self):
        return self.title
