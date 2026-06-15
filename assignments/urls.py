from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('lesson/<int:lesson_id>/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('<int:pk>/edit/', views.AssignmentUpdateView.as_view(), name='assignment_edit'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    path('grade/', views.grade_submissions, name='grade_list'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade'),
]