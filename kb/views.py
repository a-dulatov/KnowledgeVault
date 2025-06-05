from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .models import (Label, Article, Space, ArticleAttachment, ArticleParagraph, 
                     ParagraphAttachment, ShareSettings, SecureShareLink, ShareLinkView,
                     ArticleRating, ArticleComment, ParagraphLike, ArticleReadStatus, ArticleFavorite)
from .forms import LoginForm, RegistrationForm, ArticleForm, ParagraphForm
from django.db.models import Q
import json
import markdown
import bleach
import urllib.parse
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def index(request):
    """Home page with featured articles and spaces"""
    spaces = Space.objects.select_related('label').all()
    labels = Label.objects.all()
    latest_articles = Article.objects.order_by('-created_at')[:5]
    
    # Add read, favorite status, and view counts for all users
    for article in latest_articles:
        article.view_count = article.get_view_count()
        article.unique_view_count = article.get_unique_view_count()
        article.favorites_count = article.get_favorites_count()
        if request.user.is_authenticated:
            article.is_read = article.is_read_by_user(request.user)
            article.is_favorited = article.is_favorited_by_user(request.user)
    
    context = {
        'spaces': spaces,
        'labels': labels,
        'recent_articles': latest_articles,
        'title': 'Knowledge Base Home'
    }
    return render(request, 'index.html', context)

def article_detail(request, article_id):
    """Display a single article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Record view for both authenticated and anonymous users
    article.record_view(request)
    
    # Mark article as read for authenticated users
    if request.user.is_authenticated:
        ArticleReadStatus.mark_as_read(article, request.user)
    
    # Get rating and comment data
    user_rating = None
    if request.user.is_authenticated:
        user_rating = article.get_user_rating(request.user)
    
    # Get approved comments (only top-level comments, replies are loaded via model method)
    comments = article.comments.filter(is_approved=True, parent__isnull=True).order_by('-created_at')
    
    # Add read and favorite status for the current article
    if request.user.is_authenticated:
        article.is_read = article.is_read_by_user(request.user)
        article.is_favorited = article.is_favorited_by_user(request.user)
    
    context = {
        'article': article,
        'title': article.title,
        'user_rating': user_rating,
        'comments': comments,
        'average_rating': article.average_rating(),
        'rating_count': article.rating_count(),
        'comment_count': article.comment_count(),
        'view_count': article.get_view_count(),
        'unique_view_count': article.get_unique_view_count(),
        'favorites_count': article.get_favorites_count(),
    }
    return render(request, 'article.html', context)

def space_detail(request, space_id):
    """Display articles in a space"""
    space = get_object_or_404(Space, id=space_id)
    articles = Article.objects.filter(space=space)
    
    # Add read, favorite status, and view counts for all users
    for article in articles:
        article.view_count = article.get_view_count()
        article.unique_view_count = article.get_unique_view_count()
        article.favorites_count = article.get_favorites_count()
        if request.user.is_authenticated:
            article.is_read = article.is_read_by_user(request.user)
            article.is_favorited = article.is_favorited_by_user(request.user)
    
    context = {
        'space': space,
        'articles': articles,
        'title': f'Space: {space.name}'
    }
    return render(request, 'space.html', context)

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

def api_spaces(request):
    """API endpoint to get all spaces"""
    spaces = Space.objects.all()
    results = []
    
    for space in spaces:
        results.append({
            'id': space.id,
            'name': space.name,
            'description': space.description
        })
    
    return JsonResponse({'spaces': results})

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
        form = ArticleForm(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.created_at = timezone.now()
            article.updated_at = timezone.now()
            article.save()
            
            # Handle multiple file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                if file:
                    ArticleAttachment.objects.create(
                        article=article,
                        file=file,
                        original_name=file.name
                    )
            
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
        form = ArticleForm(request.POST, request.FILES, instance=article)
        print(f"Edit form is valid: {form.is_valid()}")
        if form.is_valid():
            article = form.save(commit=False)
            article.updated_at = timezone.now()
            article.save()
            
            # Handle multiple file uploads
            files = request.FILES.getlist('attachments')
            for file in files:
                if file:
                    ArticleAttachment.objects.create(
                        article=article,
                        file=file,
                        original_name=file.name
                    )
            
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

@login_required
def delete_attachment(request, attachment_id):
    """Delete an attachment from an article"""
    attachment = get_object_or_404(ArticleAttachment, id=attachment_id)
    article = attachment.article
    
    # Check if user is the author of the article
    if article.author != request.user:
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        # Delete the file from filesystem
        attachment.file.delete(save=False)
        # Delete the attachment record
        attachment.delete()
        messages.success(request, f"Attachment '{attachment.original_name}' was deleted successfully.")
        
        # Redirect back to edit page if came from there, otherwise to article detail
        if 'edit' in request.META.get('HTTP_REFERER', ''):
            return redirect('edit_article', article_id=article.id)
        else:
            return redirect('article_detail', article_id=article.id)
    
    return redirect('article_detail', article_id=article.id)


@login_required
def add_paragraph(request, article_id):
    """Add a new paragraph to an article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Check if user is the author
    if article.author != request.user:
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        form = ParagraphForm(request.POST)
        if form.is_valid():
            paragraph = form.save(commit=False)
            paragraph.article = article
            # Set order to be last
            last_paragraph = article.paragraphs.order_by('-order').first()
            paragraph.order = (last_paragraph.order + 1) if last_paragraph else 1
            paragraph.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                ParagraphAttachment.objects.create(
                    paragraph=paragraph,
                    file=file,
                    original_name=file.name
                )
            
            messages.success(request, "Paragraph added successfully.")
            return redirect('edit_article', article_id=article.id)
    else:
        form = ParagraphForm()
    
    return render(request, 'paragraph_form.html', {
        'form': form,
        'article': article,
        'title': f'Add Paragraph to: {article.title}',
        'submit_text': 'Add Paragraph'
    })


@login_required
def edit_paragraph(request, paragraph_id):
    """Edit an existing paragraph"""
    paragraph = get_object_or_404(ArticleParagraph, id=paragraph_id)
    article = paragraph.article
    
    # Check if user is the author
    if article.author != request.user:
        messages.error(request, "You don't have permission to edit this paragraph.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        form = ParagraphForm(request.POST, instance=paragraph)
        if form.is_valid():
            form.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                ParagraphAttachment.objects.create(
                    paragraph=paragraph,
                    file=file,
                    original_name=file.name
                )
            
            messages.success(request, "Paragraph updated successfully.")
            return redirect('edit_article', article_id=article.id)
    else:
        form = ParagraphForm(instance=paragraph)
    
    return render(request, 'paragraph_form.html', {
        'form': form,
        'paragraph': paragraph,
        'article': article,
        'title': f'Edit Paragraph: {paragraph.title}',
        'submit_text': 'Update Paragraph'
    })


@login_required
def delete_paragraph(request, paragraph_id):
    """Delete a paragraph"""
    paragraph = get_object_or_404(ArticleParagraph, id=paragraph_id)
    article = paragraph.article
    
    # Check if user is the author
    if article.author != request.user:
        messages.error(request, "You don't have permission to delete this paragraph.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        # Delete all attachments first
        for attachment in paragraph.attachments.all():
            attachment.file.delete(save=False)
            attachment.delete()
        
        paragraph.delete()
        messages.success(request, f"Paragraph '{paragraph.title}' was deleted successfully.")
        return redirect('edit_article', article_id=article.id)
    
    return redirect('edit_article', article_id=article.id)


@login_required
def reorder_paragraphs(request, article_id):
    """Update paragraph order via AJAX"""
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        
        # Check if user is the author
        if article.author != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        
        try:
            data = json.loads(request.body)
            paragraph_orders = data.get('paragraph_orders', [])
            
            for item in paragraph_orders:
                paragraph_id = item.get('id')
                new_order = item.get('order')
                
                paragraph = ArticleParagraph.objects.get(id=paragraph_id, article=article)
                paragraph.order = new_order
                paragraph.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def delete_paragraph_attachment(request, attachment_id):
    """Delete a paragraph attachment"""
    attachment = get_object_or_404(ParagraphAttachment, id=attachment_id)
    paragraph = attachment.paragraph
    article = paragraph.article
    
    # Check if user is the author
    if article.author != request.user:
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('article_detail', article_id=article.id)
    
    if request.method == 'POST':
        # Delete the file from filesystem
        attachment.file.delete(save=False)
        # Delete the attachment record
        attachment.delete()
        messages.success(request, f"Attachment '{attachment.original_name}' was deleted successfully.")
        
        # Redirect back to edit page if came from there, otherwise to article detail
        if 'edit' in request.META.get('HTTP_REFERER', ''):
            return redirect('edit_paragraph', paragraph_id=paragraph.id)
        else:
            return redirect('article_detail', article_id=article.id)
    
    return redirect('article_detail', article_id=article.id)


def export_article_pdf(request, article_id):
    """Export article to PDF format"""
    article = get_object_or_404(Article, id=article_id)
    
    # Prepare context for PDF template
    context = {
        'article': article,
        'paragraphs': article.paragraphs.all().order_by('order'),
        'export_date': timezone.now(),
    }
    
    # Render HTML template for PDF
    html_string = render_to_string('article_pdf.html', context, request)
    
    # Create PDF
    font_config = FontConfiguration()
    css = CSS(string='''
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .header {
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .article-title {
            color: #007bff;
            font-size: 24px;
            margin-bottom: 10px;
        }
        .article-meta {
            color: #666;
            font-size: 12px;
            margin-bottom: 20px;
        }
        .paragraph {
            margin-bottom: 30px;
        }
        .paragraph-title {
            color: #495057;
            font-size: 18px;
            margin-bottom: 15px;
            border-left: 4px solid #007bff;
            padding-left: 10px;
        }
        .paragraph-content {
            text-align: justify;
        }
        .attachments {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .attachment-list {
            list-style: none;
            padding: 0;
        }
        .attachment-item {
            padding: 5px 0;
            border-bottom: 1px solid #dee2e6;
        }
        .attachment-item:last-child {
            border-bottom: none;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    ''', font_config=font_config)
    
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.title}.pdf"'
    
    return response


def export_article_markdown(request, article_id):
    """Export article to Markdown format"""
    article = get_object_or_404(Article, id=article_id)
    paragraphs = article.paragraphs.all().order_by('order')
    
    # Generate Markdown content
    markdown_content = []
    
    # Article header
    markdown_content.append(f"# {article.title}\n")
    markdown_content.append(f"**Category:** {article.category.name}\n")
    markdown_content.append(f"**Created:** {article.created_at.strftime('%Y-%m-%d')}\n")
    markdown_content.append(f"**Updated:** {article.updated_at.strftime('%Y-%m-%d')}\n")
    
    if article.tags:
        tags = ', '.join(article.tags)
        markdown_content.append(f"**Tags:** {tags}\n")
    
    markdown_content.append("\n---\n")
    
    # Article summary
    if article.summary:
        markdown_content.append("## Summary\n")
        markdown_content.append(f"{article.summary}\n\n")
    
    # Article paragraphs
    for paragraph in paragraphs:
        markdown_content.append(f"## {paragraph.title}\n")
        
        # Clean HTML and convert to markdown-friendly format
        clean_content = bleach.clean(
            paragraph.content,
            tags=['p', 'br', 'strong', 'em', 'u', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote'],
            strip=True
        )
        
        # Simple HTML to Markdown conversion
        clean_content = clean_content.replace('<strong>', '**').replace('</strong>', '**')
        clean_content = clean_content.replace('<em>', '*').replace('</em>', '*')
        clean_content = clean_content.replace('<code>', '`').replace('</code>', '`')
        clean_content = clean_content.replace('<pre>', '```\n').replace('</pre>', '\n```')
        clean_content = clean_content.replace('<p>', '').replace('</p>', '\n\n')
        clean_content = clean_content.replace('<br>', '\n')
        clean_content = clean_content.replace('<br/>', '\n')
        clean_content = clean_content.replace('<br />', '\n')
        
        markdown_content.append(f"{clean_content}\n")
        
        # Add attachments if any
        if paragraph.attachments.exists():
            markdown_content.append("### Attachments\n")
            for attachment in paragraph.attachments.all():
                attachment_url = request.build_absolute_uri(attachment.file.url)
                markdown_content.append(f"- [{attachment.original_name}]({attachment_url})\n")
            markdown_content.append("\n")
    
    # Article-level attachments
    if article.attachments.exists():
        markdown_content.append("## Article Attachments\n")
        for attachment in article.attachments.all():
            attachment_url = request.build_absolute_uri(attachment.file.url)
            markdown_content.append(f"- [{attachment.original_name}]({attachment_url})\n")
        markdown_content.append("\n")
    
    # Join all content
    final_content = ''.join(markdown_content)
    
    # Create response
    response = HttpResponse(final_content, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="{article.title}.md"'
    
    return response


def generate_share_preview(request, article_id):
    """Generate article preview data for sharing"""
    article = get_object_or_404(Article, id=article_id)
    
    # Create clean summary for sharing
    clean_summary = strip_tags(article.summary)
    if len(clean_summary) > 160:
        clean_summary = clean_summary[:157] + "..."
    
    # Get first paragraph content for preview
    first_paragraph = article.paragraphs.first()
    preview_content = ""
    if first_paragraph:
        preview_content = strip_tags(first_paragraph.content)
        if len(preview_content) > 300:
            preview_content = preview_content[:297] + "..."
    
    # Build absolute URLs
    article_url = request.build_absolute_uri(reverse('article_detail', args=[article.id]))
    
    # Prepare sharing data
    share_data = {
        'title': article.title,
        'summary': clean_summary,
        'preview_content': preview_content,
        'url': article_url,
        'category': article.category.name,
        'author': article.author.username if article.author else 'Anonymous',
        'created_date': article.created_at.strftime('%B %d, %Y'),
        'tags': article.tags if article.tags else [],
        'paragraph_count': article.paragraphs.count(),
        'attachment_count': article.attachments.count(),
    }
    
    return JsonResponse(share_data)


def share_article(request, article_id):
    """Article sharing page with secure time-limited links"""
    article = get_object_or_404(Article, id=article_id)
    
    # Create or get existing secure share link
    user = request.user if request.user.is_authenticated else None
    share_link = SecureShareLink.create_for_article(article, user)
    
    # Build secure sharing URL
    secure_url = request.build_absolute_uri(reverse('shared_article', args=[share_link.token]))
    encoded_url = urllib.parse.quote(secure_url)
    encoded_title = urllib.parse.quote(article.title)
    encoded_summary = urllib.parse.quote(strip_tags(article.summary)[:160])
    
    share_urls = {
        'twitter': f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        'reddit': f"https://reddit.com/submit?url={encoded_url}&title={encoded_title}",
        'telegram': f"https://t.me/share/url?url={encoded_url}&text={encoded_title}",
        'whatsapp': f"https://wa.me/?text={encoded_title}%20{encoded_url}",
        'email': f"mailto:?subject={encoded_title}&body=Check out this article: {encoded_url}"
    }
    
    # Get share settings
    settings = ShareSettings.get_settings()
    
    context = {
        'article': article,
        'share_link': share_link,
        'secure_url': secure_url,
        'share_urls': share_urls,
        'settings': settings,
        'title': f'Share: {article.title}'
    }
    
    return render(request, 'share_article.html', context)


def shared_article(request, token):
    """View article via secure share link"""
    try:
        share_link = get_object_or_404(SecureShareLink, token=token)
        
        # Check if link is valid
        if not share_link.is_valid:
            if share_link.is_expired:
                return render(request, 'shared_expired.html', {
                    'title': 'Link Expired',
                    'article_title': share_link.article.title
                })
            else:
                return render(request, 'shared_inactive.html', {
                    'title': 'Link Inactive',
                    'article_title': share_link.article.title
                })
        
        # Get share settings
        settings = ShareSettings.get_settings()
        
        # Check if authentication is required
        if settings.require_authentication and not request.user.is_authenticated:
            return redirect('login')
        
        # Record the view if tracking is enabled
        if settings.track_views:
            share_link.record_view()
            
            # Create detailed view record
            ShareLinkView.objects.create(
                share_link=share_link,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                referrer=request.META.get('HTTP_REFERER')
            )
        
        article = share_link.article
        
        # Check if this is a paragraph-specific share link
        if share_link.paragraph:
            context = {
                'article': article,
                'paragraph': share_link.paragraph,
                'share_link': share_link,
                'is_shared_view': True,
                'is_paragraph_share': True,
                'expires_at': share_link.expires_at,
                'title': f"{share_link.paragraph.title} - {article.title}"
            }
        else:
            context = {
                'article': article,
                'share_link': share_link,
                'is_shared_view': True,
                'is_paragraph_share': False,
                'expires_at': share_link.expires_at,
                'title': article.title
            }
        
        return render(request, 'shared_article.html', context)
        
    except SecureShareLink.DoesNotExist:
        return render(request, 'shared_not_found.html', {
            'title': 'Share Link Not Found'
        })


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_share_link(request, article_id):
    """Generate a new secure share link for an article"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    article = get_object_or_404(Article, id=article_id)
    
    # Get custom expiry hours from request
    custom_hours = request.GET.get('hours')
    if custom_hours:
        try:
            custom_hours = int(custom_hours)
            if custom_hours <= 0 or custom_hours > 8760:  # Max 1 year
                custom_hours = None
        except ValueError:
            custom_hours = None
    
    # Create new share link
    share_link = SecureShareLink.create_for_article(article, request.user, custom_hours)
    
    # Build secure URL
    secure_url = request.build_absolute_uri(reverse('shared_article', args=[share_link.token]))
    
    return JsonResponse({
        'success': True,
        'token': share_link.token,
        'url': secure_url,
        'expires_at': share_link.expires_at.isoformat(),
        'view_count': share_link.view_count
    })


def generate_paragraph_share_link(request, paragraph_id):
    """Generate a new secure share link for a specific paragraph"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    paragraph = get_object_or_404(ArticleParagraph, id=paragraph_id)
    
    # Get custom expiry hours from request
    custom_hours = request.GET.get('hours')
    if custom_hours:
        try:
            custom_hours = int(custom_hours)
            if custom_hours <= 0 or custom_hours > 8760:  # Max 1 year
                custom_hours = None
        except ValueError:
            custom_hours = None
    
    # Create new share link for paragraph
    share_link = SecureShareLink.create_for_paragraph(paragraph, request.user, custom_hours)
    
    # Build secure URL
    secure_url = request.build_absolute_uri(reverse('shared_article', args=[share_link.token]))
    
    return JsonResponse({
        'success': True,
        'token': share_link.token,
        'url': secure_url,
        'expires_at': share_link.expires_at.isoformat(),
        'view_count': share_link.view_count,
        'paragraph_title': paragraph.title
    })


def share_paragraph(request, paragraph_id):
    """Paragraph sharing page with secure time-limited links"""
    paragraph = get_object_or_404(ArticleParagraph, id=paragraph_id)
    article = paragraph.article
    
    # Create or get existing secure share link for this paragraph
    user = request.user if request.user.is_authenticated else None
    share_link = SecureShareLink.create_for_paragraph(paragraph, user)
    
    # Build secure sharing URL
    secure_url = request.build_absolute_uri(reverse('shared_article', args=[share_link.token]))
    encoded_url = urllib.parse.quote(secure_url)
    encoded_title = urllib.parse.quote(f"{paragraph.title} - {article.title}")
    encoded_summary = urllib.parse.quote(strip_tags(paragraph.content)[:160])
    
    share_urls = {
        'twitter': f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
        'reddit': f"https://reddit.com/submit?url={encoded_url}&title={encoded_title}",
        'telegram': f"https://t.me/share/url?url={encoded_url}&text={encoded_title}",
        'whatsapp': f"https://wa.me/?text={encoded_title}%20{encoded_url}",
        'email': f"mailto:?subject={encoded_title}&body=Check out this content: {encoded_url}"
    }
    
    # Get share settings
    settings = ShareSettings.get_settings()
    
    context = {
        'paragraph': paragraph,
        'article': article,
        'share_link': share_link,
        'secure_url': secure_url,
        'share_urls': share_urls,
        'settings': settings,
        'title': f'Share: {paragraph.title}'
    }
    
    return render(request, 'share_paragraph.html', context)


@login_required
def rate_article(request, article_id):
    """Rate an article (1-5 stars)"""
    if request.method == 'POST':
        article = get_object_or_404(Article, pk=article_id)
        rating_value = int(request.POST.get('rating', 0))
        
        if 1 <= rating_value <= 5:
            rating, created = ArticleRating.objects.update_or_create(
                article=article,
                user=request.user,
                defaults={'rating': rating_value}
            )
            
            return JsonResponse({
                'success': True,
                'rating': rating.rating,
                'average_rating': round(article.average_rating(), 1),
                'rating_count': article.rating_count(),
                'message': 'Rating updated' if not created else 'Rating added'
            })
        else:
            return JsonResponse({'success': False, 'error': 'Invalid rating value'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def comment_article(request, article_id):
    """Add a comment to an article"""
    if request.method == 'POST':
        article = get_object_or_404(Article, pk=article_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent = None
            if parent_id:
                try:
                    parent = ArticleComment.objects.get(pk=parent_id, article=article)
                except ArticleComment.DoesNotExist:
                    pass
            
            comment = ArticleComment.objects.create(
                article=article,
                user=request.user,
                content=content,
                parent=parent
            )
            
            # Render the comment HTML
            comment_html = render_to_string('partials/comment.html', {
                'comment': comment,
                'user': request.user
            })
            
            return JsonResponse({
                'success': True,
                'comment_html': comment_html,
                'comment_count': article.comment_count()
            })
        else:
            return JsonResponse({'success': False, 'error': 'Comment content cannot be empty'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def like_paragraph(request, paragraph_id):
    """Like or dislike a paragraph"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    paragraph = get_object_or_404(ArticleParagraph, pk=paragraph_id)
    action = request.POST.get('action')  # 'like', 'dislike', or 'remove'
    
    try:
        existing_like = ParagraphLike.objects.get(paragraph=paragraph, user=request.user)
        
        if action == 'remove':
            existing_like.delete()
            user_action = None
        elif action == 'like':
            existing_like.is_like = True
            existing_like.save()
            user_action = True
        elif action == 'dislike':
            existing_like.is_like = False
            existing_like.save()
            user_action = False
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
            
    except ParagraphLike.DoesNotExist:
        if action == 'like':
            ParagraphLike.objects.create(paragraph=paragraph, user=request.user, is_like=True)
            user_action = True
        elif action == 'dislike':
            ParagraphLike.objects.create(paragraph=paragraph, user=request.user, is_like=False)
            user_action = False
        else:
            user_action = None
    
    return JsonResponse({
        'success': True,
        'like_count': paragraph.like_count(),
        'dislike_count': paragraph.dislike_count(),
        'user_action': user_action
    })


@login_required
def toggle_favorite(request, article_id):
    """Toggle favorite status for an article"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    article = get_object_or_404(Article, id=article_id)
    
    favorite, created = ArticleFavorite.objects.get_or_create(
        article=article,
        user=request.user
    )
    
    if not created:
        # If favorite exists, remove it (unfavorite)
        favorite.delete()
        is_favorited = False
    else:
        # New favorite was created
        is_favorited = True
    
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited
    })


@login_required
def my_favorites(request):
    """Display user's favorite articles"""
    favorites = ArticleFavorite.objects.filter(user=request.user).select_related('article', 'article__space')
    articles = [favorite.article for favorite in favorites]
    
    # Add favorite status for each article
    for article in articles:
        article.is_favorited = True  # All articles in this view are favorited
        if request.user.is_authenticated:
            article.is_read = article.is_read_by_user(request.user)
    
    context = {
        'articles': articles,
        'title': 'My Favorites',
        'spaces': Space.objects.all(),
        'labels': Label.objects.all(),
    }
    return render(request, 'my_favorites.html', context)
