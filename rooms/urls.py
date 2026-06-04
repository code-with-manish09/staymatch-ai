from django.urls import path
from . import views

urlpatterns = [
    path('post_room/', views.post_room, name='post_room'),
    path('room_details/', views.room_details, name='room_details'),
    path('room_details/<int:room_id>/', views.room_details, name='room_details_by_id'),
    path('toggle-save/<int:room_id>/', views.toggle_save_room, name='toggle_save_room'),
    path('review/<int:room_id>/', views.submit_review, name='submit_review'),
    path('room_matches/', views.room_matches, name='room_matches'),
    path('ai-match/', views.ai_match_view, name='ai_match'),
    path('room/<int:room_id>/faqs/', views.room_faqs, name='room_faqs'),
    path('room/<int:pk>/edit/', views.edit_room, name='room_edit'),
    path('room/<int:pk>/delete/', views.delete_room, name = 'room_delete'),
    path('post/', views.post_gate, name='post_gate'),
    path('post/flatmate/', views.post_flatmate, name='post_flatmate'),
    path('flatmate/edit/<int:pk>/', views.edit_flatmate, name='edit_flatmate'),
    path('flatmate/delete/<int:pk>/', views.delete_flatmate, name='delete_flatmate'),
    path('flatmate/<int:pk>/', views.flatmate_detail, name='flatmate_detail'),
    path('flatmates/save/<int:profile_id>/', views.toggle_save_flatmate, name='toggle_save_flatmate'),
    path('match_gateway/', views.match_gateway, name='match_gateway'),
    path('flatmate-match/', views.flatmate_match, name='flatmate_match'),
    path('ai-flatmate-match/', views.ai_flatmate_match_view, name='ai_flatmate_match'),
        ]