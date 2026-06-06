from django.db import models
from django.contrib.auth.models import User
from rooms.models import FlatmateProfile, Listing

class Message(models.Model):
    sender    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    listing   = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    flatmate_profile = models.ForeignKey('rooms.FlatmateProfile', on_delete=models.SET_NULL,related_name='messages',null=True, blank=True )
    body      = models.TextField()
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # oldest first inside chat

    def __str__(self):
        return f"{self.sender} → {self.recipient}"
    
    #================flatmates msg model===========================
class FlatmateInquiry(models.Model):
    sender    = models.ForeignKey(User, related_name='sent_inquiries',     on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_inquiries', on_delete=models.CASCADE)
    flatmate_profile = models.ForeignKey(FlatmateProfile, related_name='inquiries', on_delete=models.CASCADE)
    body      = models.TextField(default='Hi, I am interested in your flatmate profile!')
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'flatmate_profile')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} → {self.recipient} | {self.flatmate_profile.name}"    