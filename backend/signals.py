from django.db.models.signals import post_save,pre_save
from .models import Chanel,Add_chanel,Add_userbot,Posts,Subperhour,Mentions,Payment,Profile,Commission,Notify
from django.dispatch import receiver
from .tasks import add_chanel,process_user_bot
from django.db.models import Sum,Q,Count,F
from celery import shared_task
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
import telegram
from config import TOKEN_NOTIFY,TOKEN_WEBHOOK
bot = telegram.Bot(TOKEN_NOTIFY)



# @receiver(pre_save, sender=Payment)
# def create_payment(sender, instance, *args, **kwargs):
#     profile = instance.profile
#
#     # Check if the profile has enough balance
#     if profile.balance < instance.amount:
#         # Prevent the payment from proceeding by marking it
#         return ""
#     else:
#         # Update the profile balance if there's enough money
#         profile.balance = F('balance') - instance.amount
#         profile.save(update_fields=['balance'])
@receiver(post_save,sender=Add_chanel)
def create_chanel(sender,instance,created,*args,**kwargs):
    if created:
        add_chanel.delay(instance.chanel_link)
        Chanel.objects.create(add_chanel=instance.username,chanel_link=instance.chanel_link,subscribers=0,views=0)



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
        instance.chanel.save(update_fields=['views','daily_views','yesterday_views'])
        notify=Notify.objects.filter(start=True).select_related('profile')
        for item in notify:

            try:
                if  item.profile.notify_id and item.word.lower() in instance.text.lower():
                    text = f"Новые уведомления по запросу'{item.word}'" \
                           f"{instance.link} {instance.chanel.name} - {instance.date}"
                    item.count=F('count')+1
                    item.save(update_fields=['count'])
                    bot.send_message(item.profile.notify_id, text)




            except  Exception as e:
                print(e)




@receiver(post_save,sender=Subperhour)
def send_detail(sender,instance,created,*args,**kwargs):
    if not created:
        return

    try:
        instance = sender.objects.select_related('chanel__add_chanel').get(pk=instance.pk)
        if instance.chanel.add_chanel and instance.chanel.add_chanel.telegram_id:
            bot = telegram.Bot(TOKEN_WEBHOOK)
            text = (
                f"📅Подписок по часам:\n\n"
                f"{instance.chanel.name}\n"
                f"{instance.created_at.strftime('%Y-%m-%d %H:%M')}: {instance.subperhour}: {'+' + str(instance.difference) if instance.difference >= 0 else str(instance.difference)}\n"
                f"👆Выше Вы сможете просмотреть детальную аналитику за запрашиваемый канал / Спасибо за запрос ❤"
            )
            bot.send_message(instance.chanel.add_chanel.telegram_id, text=text)
    except Exception as e:
        pass






@receiver(post_save,sender=Chanel)
def create_views(sender,instance,created,*args,**kwargs):
    hour=timezone.now() - timedelta(hours=1)
    first = Subperhour.objects.filter(chanel=instance, created_at__lte=hour).first()


    try:
        obj = Subperhour.objects.get(chanel=instance, created_at__gte=hour)

        obj.subperhour = instance.subscribers
        if first:
            obj.difference = instance.subscribers - first.subperhour
        else:
            obj.difference = 0

            # Corrected line
        obj.save(update_fields=['subperhour','difference'])
    except Subperhour.DoesNotExist:
        if first:
            Subperhour.objects.create(
                chanel=instance,
                subperhour=instance.subscribers,
                difference=instance.subscribers - first.subperhour
            )
        else:
            Subperhour.objects.create(
                chanel=instance,
                subperhour=instance.subscribers,
                difference=0
            )




@receiver(post_save,sender=Posts)
def create_mention(sender,instance,created,*args,**kwargs):
    if instance.mention:
        chanel_all = Chanel.objects.all()
        text=instance.text.lower()
        chanel_instance =instance.chanel.chanel_link.split('/')[-1].lower()
        for item in chanel_all:
            chanel_link_split = item.chanel_link.split('/')[-1].lower()
            if (chanel_link_split in text or  f'@{chanel_link_split}' in  text or f"t.me/{chanel_link_split}" in text or  f'https://t.me/{chanel_link_split}' in text) and (chanel_instance not in text and f'@{chanel_instance}' not in text and f"t.me/{chanel_instance}"  not in text and f'https://t.me/{chanel_instance}' not in text):
                Mentions.objects.create(mentioned_channel=item, post=instance)










