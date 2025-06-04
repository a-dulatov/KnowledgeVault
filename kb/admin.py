from django.contrib import admin
from .models import (Category, Article, ArticleAttachment, ArticleParagraph, 
                     ParagraphAttachment, ShareSettings, SecureShareLink, ShareLinkView,
                     ArticleRating, ArticleComment, ParagraphLike)

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


@admin.register(ShareSettings)
class ShareSettingsAdmin(admin.ModelAdmin):
    list_display = ('link_expiry_hours', 'max_shares_per_article', 'require_authentication', 'track_views', 'updated_at')
    fields = ('link_expiry_hours', 'max_shares_per_article', 'require_authentication', 'track_views')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not ShareSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


class ShareLinkViewInline(admin.TabularInline):
    model = ShareLinkView
    extra = 0
    readonly_fields = ('ip_address', 'user_agent', 'referrer', 'viewed_at')
    fields = ('ip_address', 'viewed_at', 'referrer')
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(SecureShareLink)
class SecureShareLinkAdmin(admin.ModelAdmin):
    list_display = ('article', 'token_preview', 'created_by', 'view_count', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'expires_at', 'article__category')
    search_fields = ('article__title', 'token', 'created_by__username')
    readonly_fields = ('token', 'view_count', 'last_accessed', 'created_at')
    fields = ('article', 'token', 'created_by', 'expires_at', 'is_active', 'view_count', 'last_accessed', 'created_at')
    inlines = [ShareLinkViewInline]
    actions = ['deactivate_links', 'cleanup_expired']
    
    def token_preview(self, obj):
        return f"{obj.token[:8]}..." if obj.token else "N/A"
    token_preview.short_description = 'Token (Preview)'
    
    def deactivate_links(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} share links deactivated.')
    deactivate_links.short_description = 'Deactivate selected share links'
    
    def cleanup_expired(self, request, queryset):
        expired_count = SecureShareLink.cleanup_expired()
        self.message_user(request, f'{expired_count} expired share links removed.')
    cleanup_expired.short_description = 'Clean up expired share links'


@admin.register(ShareLinkView)
class ShareLinkViewAdmin(admin.ModelAdmin):
    list_display = ('share_link', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at', 'share_link__article__category')
    search_fields = ('share_link__article__title', 'ip_address')
    readonly_fields = ('share_link', 'ip_address', 'user_agent', 'referrer', 'viewed_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Rating and Comment Administration
@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'article__category')
    search_fields = ('article__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'content_preview', 'parent', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'article__category')
    search_fields = ('article__title', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']
    actions = ['approve_comments', 'unapprove_comments']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} comments unapproved.')
    unapprove_comments.short_description = 'Unapprove selected comments'


@admin.register(ParagraphLike)
class ParagraphLikeAdmin(admin.ModelAdmin):
    list_display = ('paragraph', 'user', 'is_like', 'created_at')
    list_filter = ('is_like', 'created_at', 'paragraph__article__category')
    search_fields = ('paragraph__title', 'paragraph__article__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']
