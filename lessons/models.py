import re
from django.db import models


class Lesson(models.Model):
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, help_text="Paste any YouTube link — it will auto-clean")
    video_file = models.FileField(upload_to='lessons/videos/%Y/%m/', blank=True)
    pdf_resource = models.FileField(upload_to='lessons/resources/%Y/%m/', blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.video_url:
            self.video_url = self._clean_youtube_url(self.video_url)
        super().save(*args, **kwargs)
    
    @staticmethod
    def _clean_youtube_url(url):
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
    
    @property
    def embed_url(self):
        return self.video_url
