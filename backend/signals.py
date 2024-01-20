from django.db.models.signals import post_save,pre_save
from .models import Chanel,Add_chanel,Add_userbot
from django.dispatch import receiver
from .tasks import add_chanel,process_user_bot
from celery import shared_task




@receiver(post_save,sender=Add_chanel)
def create_chanel(sender,instance,created,*args,**kwargs):
    if created:
        add_chanel.delay(instance.chanel_link)
        Chanel.objects.create(username=instance.username,add_chanel=instance,chanel_link=instance.chanel_link,subscribers=0,views=0)



@receiver(post_save, sender=Add_userbot)
def handle_new_userbot(sender, instance,created, **kwargs):
    if created:
        # Ensure that the instance is saved with the provided phone number


        # Schedule the Celery task after the instance is saved
        process_user_bot.delay(
            name=instance.name,
            api_id=instance.api_id,
            api_hash=instance.api_hash,
            phone=instance.phone_number
        )
