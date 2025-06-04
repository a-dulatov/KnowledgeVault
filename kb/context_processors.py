from .models import Space

def categories_processor(request):
    """Add spaces to the context for all templates"""
    return {
        'spaces': Space.objects.all()
    }