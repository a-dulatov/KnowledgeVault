from django.contrib import admin
from .models import Category, Article, ArticleAttachment, ArticleParagraph, ParagraphAttachment

class ArticleAttachmentInline(admin.TabularInline):
    model = ArticleAttachment
    extra = 1
    fields = ('file', 'original_name')
    readonly_fields = ('uploaded_at',)


class ArticleParagraphInline(admin.TabularInline):
    model = ArticleParagraph
    extra = 1
    fields = ('title', 'content', 'order')
    ordering = ['order']


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'attachment_count', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at', 'updated_at')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'title': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ArticleParagraphInline, ArticleAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'summary', 'category', 'tags')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def attachment_count(self, obj):
        return obj.attachments.count()
    attachment_count.short_description = 'Attachments'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count')
    search_fields = ('name', 'description')
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Number of Articles'

class ParagraphAttachmentInline(admin.TabularInline):
    model = ParagraphAttachment
    extra = 1
    fields = ('file', 'original_name')
    readonly_fields = ('uploaded_at',)


class ParagraphAdmin(admin.ModelAdmin):
    list_display = ('title', 'article', 'order', 'attachment_count', 'created_at')
    list_filter = ('article__category', 'created_at')
    search_fields = ('title', 'content', 'article__title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ParagraphAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('article', 'title', 'content', 'order')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def attachment_count(self, obj):
        return obj.attachments.count()
    attachment_count.short_description = 'Attachments'


# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleAttachment)
admin.site.register(ArticleParagraph, ParagraphAdmin)
admin.site.register(ParagraphAttachment)
