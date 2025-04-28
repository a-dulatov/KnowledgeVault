from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('search/', views.search_view, name='search'),
    
    # API endpoints
    path('api/search/', views.api_search, name='api_search'),
    path('api/articles/', views.api_articles, name='api_articles'),
    path('api/article/<int:article_id>/', views.api_article, name='api_article'),
    path('api/categories/', views.api_categories, name='api_categories'),
]