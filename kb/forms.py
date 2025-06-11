from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Article, ArticleAttachment, ArticleParagraph, Tag, TagCategory, TagGroup


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
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tags (comma separated)'})
    )

    
    class Meta:
        model = Article
        fields = ('title', 'summary', 'space', 'status')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'space': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing article, convert list to comma-separated string
        if self.instance and self.instance.pk and self.instance.tags:
            self.initial['tags_input'] = ', '.join(self.instance.tags)
    

    def clean_tags_input(self):
        tags_input = self.cleaned_data.get('tags_input', '')
        if tags_input:
            # Convert comma-separated string to list
            return [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        return []
    
    def save(self, commit=True):
        article = super().save(commit=False)
        article.tags = self.cleaned_data.get('tags_input', [])
        
        if commit:
            article.save()
        return article
        
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