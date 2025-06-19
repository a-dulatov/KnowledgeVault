class FileUploadForm(forms.Form):
    """Form for uploading MS Word files to create articles"""
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article title (optional - will use filename if empty)'})
    )
    space = forms.ModelChoiceField(
        queryset=Space.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the space where this article will be created"
    )
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.docx,.doc'
        }),
        help_text="Upload a Microsoft Word document (.docx or .doc)"
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith(('.docx', '.doc')):
                raise forms.ValidationError("Only Microsoft Word documents (.docx, .doc) are supported.")
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("File size cannot exceed 10MB.")
        return file