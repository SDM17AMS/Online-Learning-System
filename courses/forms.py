from django import forms
from .models import Course, Category, Tag


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'tags', 'price', 'image', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'tags': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['tags'].queryset = Tag.objects.all()