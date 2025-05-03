from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Article, Category
from .forms import LoginForm, RegistrationForm, ArticleForm
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

# Authentication Views
def login_view(request):
    """User login page"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in.")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form, 'title': 'Login'})

def register_view(request):
    """User registration page"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}. You can now log in.")
            return redirect('login')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form, 'title': 'Register'})

def logout_view(request):
    """Log user out"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('index')

# Article management
@login_required
def create_article(request):
    """Create a new article"""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.created_at = timezone.now()
            article.updated_at = timezone.now()
            article.save()
            messages.success(request, f"Article '{article.title}' was created successfully.")
            return redirect('article_detail', article_id=article.id)
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ArticleForm()
    
    return render(request, 'article_form.html', {
        'form': form, 
        'title': 'Create New Article',
        'submit_text': 'Create Article'
    })

@login_required
def edit_article(request, article_id):
    """Edit an existing article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Check if user is the author of the article
    if article.author != request.user:
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        print(f"Edit form is valid: {form.is_valid()}")
        if form.is_valid():
            article = form.save(commit=False)
            article.updated_at = timezone.now()
            article.save()
            messages.success(request, f"Article '{article.title}' was updated successfully.")
            return redirect('article_detail', article_id=article.id)
        else:
            print(f"Edit form errors: {form.errors}")
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'article_form.html', {
        'form': form, 
        'article': article,
        'title': f'Edit Article: {article.title}',
        'submit_text': 'Update Article'
    })
