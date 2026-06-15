from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('course/<slug:course_slug>/add/', views.add_review, name='add_review'),
    path('<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('course/<slug:course_slug>/', views.course_reviews, name='course_reviews'),
    path('moderate/', views.moderate_reviews, name='moderate'),
    path('<int:review_id>/approve/', views.approve_review, name='approve_review'),
    path('<int:review_id>/delete/', views.delete_review, name='delete_review'),
]
