from django.urls import path
from . import views

urlpatterns = [
    path('inbox/',                   views.inbox,        name='inbox'),
    path('inbox/<int:listing_id>/',  views.chat_view,    name='chat_view'),
    path('send/<int:listing_id>/',   views.send_message, name='send_message'),
    path('unread/', views.unread_count_api, name='unread_count_api'),
    path('flatmate/chat/<int:profile_id>/', views.flatmate_chat_view, name='flatmate_chat'),
    path('flatmate/message/<int:profile_id>/', views.send_flatmate_message, name='send_flatmate_message'),
]