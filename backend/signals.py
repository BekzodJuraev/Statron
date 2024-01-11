from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import User

@receiver(post_save,sender=User)
def create_profile_for_user(sender,instance,created,*args,**kwargs):
    if created:
        Profile.objects.create(username=instance, first_name=instance.username, last_name=instance.last_name,email=instance.email)