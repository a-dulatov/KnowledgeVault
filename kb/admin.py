from django.contrib import admin
from .models import (Label, Space, Article, ArticleAttachment, ArticleParagraph, 
                     ParagraphAttachment, ShareSettings, SecureShareLink, ShareLinkView,
                     ArticleRating, ArticleComment, ParagraphLike, ArticleReadStatus, ReadLater,
                     TagGroup, TagCategory, Tag)

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
    list_display = ('title', 'space', 'status', 'author', 'attachment_count', 'created_at', 'updated_at')
    list_filter = ('space', 'status', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'title': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ArticleParagraphInline, ArticleAttachmentInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'summary', 'space', 'author', 'status', 'tags')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def attachment_count(self, obj):
        return obj.attachments.count()
    attachment_count.short_description = 'Attachments'

class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'colored_label_display')
    search_fields = ('name',)
    list_filter = ('color',)
    
    def colored_label_display(self, obj):
        return f'<span style="background-color: {obj.color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">{obj.name}</span>'
    colored_label_display.short_description = 'Preview'
    colored_label_display.allow_tags = True


class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'icon_display', 'article_count')
    search_fields = ('name', 'description')
    list_filter = ('label',)
    fields = ('name', 'description', 'label', 'icon')
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Number of Articles'
    
    def icon_display(self, obj):
        return f'<i class="{obj.icon}"></i>'
    icon_display.short_description = 'Icon'
    icon_display.allow_tags = True

class ParagraphAttachmentInline(admin.TabularInline):
    model = ParagraphAttachment
    extra = 1
    fields = ('file', 'original_name')
    readonly_fields = ('uploaded_at',)


class ParagraphAdmin(admin.ModelAdmin):
    list_display = ('title', 'article', 'order', 'attachment_count', 'created_at')
    list_filter = ('article__space', 'created_at')
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
admin.site.register(Label, LabelAdmin)
admin.site.register(Space, SpaceAdmin)
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
    list_filter = ('is_active', 'created_at', 'expires_at', 'article__space')
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
    list_filter = ('viewed_at', 'share_link__article__space')
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
    list_filter = ('rating', 'created_at', 'article__space')
    search_fields = ('article__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'content_preview', 'parent', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'article__space')
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
    list_filter = ('is_like', 'created_at', 'paragraph__article__space')
    search_fields = ('paragraph__title', 'paragraph__article__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']


@admin.register(ArticleReadStatus)
class ArticleReadStatusAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'read_count', 'first_read_at', 'last_read_at')
    list_filter = ('first_read_at', 'last_read_at', 'article__space')
    search_fields = ('article__title', 'user__username')
    readonly_fields = ('first_read_at', 'last_read_at')
    ordering = ['-last_read_at']
    
    def has_add_permission(self, request):
        # Prevent manual creation of read status records
        return False


@admin.register(ReadLater)
class ReadLaterAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
    list_filter = ('created_at', 'article__space')
    search_fields = ('article__title', 'user__username')
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # Prevent manual creation of read later records
        return False


# Tag Structure Administration
class TagCategoryInline(admin.TabularInline):
    model = TagCategory
    extra = 1
    fields = ('name', 'description', 'color')
    show_change_link = True


class TagInline(admin.TabularInline):
    model = Tag
    extra = 1
    fields = ('name', 'description', 'color', 'usage_count')
    readonly_fields = ('usage_count',)
    show_change_link = True


@admin.register(TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'icon', 'category_count', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TagCategoryInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'color', 'icon')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_count(self, obj):
        return obj.categories.count()
    category_count.short_description = 'Categories'


@admin.register(TagCategory)
class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'description', 'color', 'tag_count', 'created_at')
    list_filter = ('group', 'color', 'created_at')
    search_fields = ('name', 'description', 'group__name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TagInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'group', 'description', 'color')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tag_count(self, obj):
        return obj.tags.count()
    tag_count.short_description = 'Tags'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'group_name', 'usage_count', 'color', 'created_at')
    list_filter = ('category__group', 'category', 'color', 'created_at')
    search_fields = ('name', 'description', 'category__name', 'category__group__name')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    ordering = ['category__group__name', 'category__name', 'name']
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'color')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def group_name(self, obj):
        return obj.category.group.name
    group_name.short_description = 'Group'
    group_name.admin_order_field = 'category__group__name'
