from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    # 1. Circular Import se bachne ke liye import yahan andar rakho
    from dashboard.models import Profile 
    
    if created:
        # Naya user hai toh profile banao
        Profile.objects.get_or_create(user=instance)
    else:
        # Purana user hai (Update ho raha hai) toh profile save karo
        # hasattr check karta hai ki profile exist karti hai ya nahi
        if hasattr(instance, 'profile'):
            instance.profile.save()