from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('theme-preview/', TemplateView.as_view(template_name='theme_preview.html'), name='theme_preview'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('space/<int:space_id>/', views.space_detail, name='space_detail'),
    path('search/', views.search_view, name='search'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Article management
    path('article/create/', views.create_article, name='create_article'),
    path('article/create-from-file/', views.create_article_from_file, name='create_article_from_file'),
    path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('attachment/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Export functionality
    path('article/<int:article_id>/export/pdf/', views.export_article_pdf, name='export_article_pdf'),
    path('article/<int:article_id>/export/markdown/', views.export_article_markdown, name='export_article_markdown'),
    
    # Sharing functionality
    path('article/<int:article_id>/share/', views.share_article, name='share_article'),
    path('article/<int:article_id>/share-preview/', views.generate_share_preview, name='generate_share_preview'),
    path('article/<int:article_id>/generate-link/', views.generate_share_link, name='generate_share_link'),
    path('paragraph/<int:paragraph_id>/share/', views.share_paragraph, name='share_paragraph'),
    path('paragraph/<int:paragraph_id>/generate-link/', views.generate_paragraph_share_link, name='generate_paragraph_share_link'),
    path('shared/<str:token>/', views.shared_article, name='shared_article'),
    
    # Paragraph management
    path('article/<int:article_id>/paragraph/add/', views.add_paragraph, name='add_paragraph'),
    path('paragraph/<int:paragraph_id>/edit/', views.edit_paragraph, name='edit_paragraph'),
    path('paragraph/<int:paragraph_id>/delete/', views.delete_paragraph, name='delete_paragraph'),
    path('paragraph-attachment/<int:attachment_id>/delete/', views.delete_paragraph_attachment, name='delete_paragraph_attachment'),
    path('article/<int:article_id>/reorder-paragraphs/', views.reorder_paragraphs, name='reorder_paragraphs'),
    
    # Rating and commenting
    path('article/<int:article_id>/rate/', views.rate_article, name='rate_article'),
    path('article/<int:article_id>/comment/', views.comment_article, name='comment_article'),
    path('paragraph/<int:paragraph_id>/like/', views.like_paragraph, name='like_paragraph'),
    
    # Favorites
    path('article/<int:article_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    
    # Read Later
    path('article/<int:article_id>/toggle-read-later/', views.toggle_read_later, name='toggle_read_later'),
    path('my-read-later/', views.my_read_later, name='my_read_later'),
    
    # API endpoints
    path('api/search/', views.api_search, name='api_search'),
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/article/<int:article_id>/', views.api_article, name='api_article'),
    path('api/spaces/', views.api_spaces, name='api_spaces'),
]