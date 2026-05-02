from django.urls import path
from . import views

urlpatterns = [
    path('post_room/', views.post_room, name='post_room'),
    path('room_details/', views.room_details, name='room_details'),
    path('room_details/<int:room_id>/', views.room_details, name='room_details_by_id'),
    path('toggle-save/<int:room_id>/', views.toggle_save_room, name='toggle_save_room'),
    path('review/<int:room_id>/', views.submit_review, name='submit_review'),
    path('matches/', views.matches, name='matches'),
    path('ai-match/', views.ai_match_view, name='ai_match'),
    path('room/<int:room_id>/faqs/', views.room_faqs, name='room_faqs'),
    path('room/<int:pk>/edit/', views.edit_room, name='room_edit'),
    path('room/<int:pk>/delete/', views.delete_room, name = 'room_delete'),
    path('post/', views.post_gate, name='post_gate'),
    path('post/flatmate/', views.post_flatmate, name='post_flatmate'),
    ]