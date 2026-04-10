from django.urls import path
from . import views

urlpatterns =[
    path('post_room/', views.post_room , name='post_room'),
    path('room_details/', views.room_details , name='room_details'),
    path('room_details/<int:room_id>/', views.room_details , name='room_details_by_id'),
]