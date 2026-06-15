import re
from django import forms
from .models import Lesson


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video_url', 'video_file', 'pdf_resource', 'description', 'order', 'duration']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'duration': forms.NumberInput(attrs={'min': 0}),
            'video_url': forms.URLInput(attrs={
                'placeholder': 'Paste YouTube link here (any format)',
                'class': 'form-control'
            }),
        }
    
    def clean_video_url(self):
        url = self.cleaned_data.get('video_url', '')
        if not url:
            return url
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f'https://www.youtube.com/embed/{match.group(1)}'
        
        return url
