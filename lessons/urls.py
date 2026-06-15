from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    path('<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:pk>/complete/', views.mark_lesson_complete, name='mark_complete'),
    path('course/<int:course_id>/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('<int:pk>/edit/', views.LessonUpdateView.as_view(), name='lesson_edit'),
    path('<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
]