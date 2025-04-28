from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Article, Category
from django.db.models import Q
import json

def index(request):
    """Home page with featured articles and categories"""
    categories = Category.objects.all()
    latest_articles = Article.objects.order_by('-created_at')[:5]
    
    context = {
        'categories': categories,
        'latest_articles': latest_articles,
        'title': 'Knowledge Base Home'
    }
    return render(request, 'index.html', context)

def article_detail(request, article_id):
    """Display a single article"""
    article = get_object_or_404(Article, id=article_id)
    context = {
        'article': article,
        'title': article.title
    }
    return render(request, 'article.html', context)

def category_detail(request, category_id):
    """Display articles in a category"""
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category)
    
    context = {
        'category': category,
        'articles': articles,
        'title': f'Category: {category.name}'
    }
    return render(request, 'category.html', context)

def search_view(request):
    """Search page"""
    query = request.GET.get('q', '')
    
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__contains=query)
        )
    else:
        articles = []
    
    context = {
        'query': query,
        'articles': articles,
        'title': 'Search Results'
    }
    return render(request, 'search.html', context)

# API endpoints
def api_search(request):
    """API endpoint for search functionality"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'articles': []})
    
    articles = Article.objects.filter(
        Q(title__icontains=query) | 
        Q(content__icontains=query) |
        Q(summary__icontains=query) |
        Q(tags__contains=query)
    )
    
    results = []
    for article in articles:
        results.append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'category_id': article.category.id,
            'category_name': article.category.name
        })
    
    return JsonResponse({'articles': results})

def api_articles(request):
    """API endpoint to get all articles"""
    articles = Article.objects.all()
    results = []
    
    for article in articles:
        results.append({
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'category_id': article.category.id,
            'category_name': article.category.name
        })
    
    return JsonResponse({'articles': results})

def api_article(request, article_id):
    """API endpoint to get a specific article"""
    article = get_object_or_404(Article, id=article_id)
    
    result = {
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'summary': article.summary,
        'category_id': article.category.id,
        'category_name': article.category.name,
        'tags': article.tags,
        'created_at': article.created_at,
        'updated_at': article.updated_at
    }
    
    return JsonResponse(result)

def api_categories(request):
    """API endpoint to get all categories"""
    categories = Category.objects.all()
    results = []
    
    for category in categories:
        results.append({
            'id': category.id,
            'name': category.name,
            'description': category.description
        })
    
    return JsonResponse({'categories': results})
