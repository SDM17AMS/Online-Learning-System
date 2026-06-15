from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_redirect, name='redirect'),
    path('student/', views.StudentDashboardView.as_view(), name='student'),
    path('instructor/', views.InstructorDashboardView.as_view(), name='instructor'),
    path('employee/', views.EmployeeDashboardView.as_view(), name='employee'),
]