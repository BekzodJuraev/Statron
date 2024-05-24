from django.db.models.signals import post_save,pre_save
from .models import Chanel,Add_chanel,Add_userbot,Posts,Subperhour,Mentions
from django.dispatch import receiver
from .tasks import add_chanel,process_user_bot
from django.db.models import Sum,Q,Count
from celery import shared_task
from datetime import date, timedelta, datetime
from django.utils import timezone



@receiver(post_save,sender=Add_chanel)
def create_chanel(sender,instance,created,*args,**kwargs):
    if created:
        #add_chanel.delay(instance.chanel_link)
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
@receiver(post_save,sender=Posts)
def create_views(sender,instance,created,*args,**kwargs):
    if created:
        total = instance.chanel.post.aggregate(total_views=Sum('view'))['total_views']
        instance.chanel.views = total
        instance.chanel.save(update_fields=['views'])

@receiver(post_save,sender=Chanel)
def create_views(sender,instance,created,*args,**kwargs):
    hour=timezone.now() - timedelta(hours=1)

    try:
        obj = Subperhour.objects.get(chanel=instance, created_at__gte=hour)
        obj.subperhour = instance.subscribers
        obj.difference = instance.daily_subscribers  # Corrected line
        obj.save(update_fields=['subperhour','difference'])
    except Subperhour.DoesNotExist:
        Subperhour.objects.create(
            chanel=instance,
            subperhour=instance.subscribers,
            difference=instance.daily_subscribers
        )

@receiver(post_save,sender=Posts)
def create_mention(sender,instance,created,*args,**kwargs):
    if instance.mention:
        chanel_all = Chanel.objects.all()
        text=instance.text.lower()
        for item in chanel_all:
            chanel_link_split = item.chanel_link.split('/')[-1].lower()
            if chanel_link_split in text or  f'@{chanel_link_split}' in  text or f"t.me/{chanel_link_split}" in text:
                Mentions.objects.create(mentioned_channel=item, post=instance)









