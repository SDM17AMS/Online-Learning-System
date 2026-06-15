from django import forms
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'max_score': forms.NumberInput(attrs={'min': 1, 'max': 1000}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file_upload', 'code_text']
        widgets = {
            'code_text': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Paste your code or text here...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        file_upload = cleaned_data.get('file_upload')
        code_text = cleaned_data.get('code_text')
        
        if not file_upload and not code_text:
            raise forms.ValidationError("Please upload a file or enter text/code.")
        
        return cleaned_data


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 0}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.max_score = kwargs.pop('max_score', 100)
        super().__init__(*args, **kwargs)
        self.fields['score'].widget.attrs['max'] = self.max_score
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is not None and score > self.max_score:
            raise forms.ValidationError(f"Score cannot exceed maximum of {self.max_score}.")
        return score