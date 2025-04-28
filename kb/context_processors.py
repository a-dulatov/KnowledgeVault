from .models import Category

def categories_processor(request):
    """Add categories to the context for all templates"""
    return {
        'categories': Category.objects.all()
    }