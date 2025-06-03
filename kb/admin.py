from django.contrib import admin
from .models import Category, Article, ArticleAttachment

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'attachment', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'summary')
    prepopulated_fields = {'title': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'summary', 'content', 'category', 'tags', 'attachment')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count')
    search_fields = ('name', 'description')
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Number of Articles'

# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
