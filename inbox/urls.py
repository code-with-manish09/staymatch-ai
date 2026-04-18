from django.urls import path
from . import views

urlpatterns = [
    path('inbox/',                   views.inbox,        name='inbox'),
    path('inbox/<int:listing_id>/',  views.chat_view,    name='chat_view'),
    path('send/<int:listing_id>/',   views.send_message, name='send_message'),
    path('unread/', views.unread_count_api, name='unread_count_api'),
]