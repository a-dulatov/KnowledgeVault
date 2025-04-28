import json
import os
from django.core.management.base import BaseCommand
from kb.models import Category, Article

class Command(BaseCommand):
    help = 'Load categories and articles from JSON files'

    def handle(self, *args, **options):
        self.stdout.write('Loading data from JSON files...')
        
        # Load categories
        categories_file = os.path.join('data', 'categories.json')
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                categories_data = json.load(f)
                
            for category_data in categories_data:
                Category.objects.get_or_create(
                    id=category_data['id'],
                    defaults={
                        'name': category_data['name'],
                        'description': category_data['description']
                    }
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(categories_data)} categories'))
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {categories_file}'))
        
        # Load articles
        articles_file = os.path.join('data', 'articles.json')
        if os.path.exists(articles_file):
            with open(articles_file, 'r') as f:
                articles_data = json.load(f)
                
            for article_data in articles_data:
                category = Category.objects.get(id=article_data['category_id'])
                Article.objects.get_or_create(
                    id=article_data['id'],
                    defaults={
                        'title': article_data['title'],
                        'content': article_data['content'],
                        'summary': article_data['summary'],
                        'category': category,
                        'tags': article_data['tags'],
                        'created_at': article_data['created_at'],
                        'updated_at': article_data['updated_at']
                    }
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(articles_data)} articles'))
        else:
            self.stdout.write(self.style.WARNING(f'File not found: {articles_file}'))