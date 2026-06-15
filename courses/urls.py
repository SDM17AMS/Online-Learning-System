from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
]