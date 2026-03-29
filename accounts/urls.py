from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

# Add this line correctly **outside the list**
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)