from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Article, ArticleAttachment, ArticleParagraph, Tag, TagCategory, TagGroup, Space


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class ArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.select_related('category__group').all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select tags that apply to this article"
    )

    class Meta:
        model = Article
        fields = ('title', 'summary', 'space', 'status', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'space': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Group tags by category for better display
        tag_groups = {}
        for tag in Tag.objects.select_related('category__group').all():
            group_name = tag.category.group.name
            category_name = tag.category.name
            if group_name not in tag_groups:
                tag_groups[group_name] = {}
            if category_name not in tag_groups[group_name]:
                tag_groups[group_name][category_name] = []
            tag_groups[group_name][category_name].append((tag.id, f"{tag.name} ({tag.get_full_path()})"))
        
        # Create choices with hierarchical structure
        choices = []
        for group_name, categories in sorted(tag_groups.items()):
            for category_name, tags in sorted(categories.items()):
                for tag_id, tag_label in sorted(tags, key=lambda x: x[1]):
                    choices.append((tag_id, tag_label))
        
        self.fields['tags'].queryset = Tag.objects.filter(id__in=[choice[0] for choice in choices])
        
        # Set initial values for tags when editing
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()
        
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.4.2/skins/ui/oxide-dark/skin.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.4.2/tinymce.min.js',
        )


class ParagraphForm(forms.ModelForm):
    class Meta:
        model = ArticleParagraph
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Paragraph title'}),
            'content': forms.Textarea(attrs={'class': 'tinymce', 'required': False}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        if not content or content.strip() == '':
            raise forms.ValidationError("Please provide some content for the paragraph.")
        return content
    
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.4.2/skins/ui/oxide-dark/skin.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.4.2/tinymce.min.js',
        )