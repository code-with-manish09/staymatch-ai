from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('save-quiz-tags/', views.save_quiz_tags, name='save_quiz_tags'),
    
]