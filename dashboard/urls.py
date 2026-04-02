from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
]
