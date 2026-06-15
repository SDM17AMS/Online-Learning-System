from django.db import models


class Lesson(models.Model):
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo embed URL")
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