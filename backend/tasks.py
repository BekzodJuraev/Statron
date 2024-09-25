from celery import Celery
from django.utils import timezone
from time import sleep
from pyrogram import Client
from pyrogram import filters
import logging
from django.db import transaction
from .models import Add_userbot,Posts,Chanel
from celery import shared_task
import os
import requests
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models.signals import post_save

@shared_task
@transaction.atomic
def process_user_bot(name, api_id, api_hash, phone):
    client = Client(name, api_id, api_hash)
    client.connect()
    sent_code = client.send_code(phone)
    sleep(30)
    userbot = Add_userbot.objects.select_for_update().get(name=name)



    signed_in = client.sign_in(phone, sent_code.phone_code_hash, userbot.code)
    try:

        # Export the session string
        session_data = client.export_session_string()

        # Update the Add_userbot instance


        userbot.session = session_data
        userbot.is_active = True
        userbot.save()

    except Exception as e:
        print(f"Authentication failed: {str(e)}")

    client.disconnect()





@shared_task
def add_chanel(chanel_link):
    userbots = Add_userbot.objects.filter(is_active=True)

    for userbot in userbots:
        session_data = userbot.session
        name = userbot.name
        api_id = userbot.api_id
        api_hash = userbot.api_hash
        phone = userbot.phone_number

        with Client(name, api_id=api_id, api_hash=api_hash, phone_number=phone,session_string=session_data) as client:
            channel_username = chanel_link.split('/')[-1]
            chat = client.get_chat(channel_username)
            total_view = client.get_chat_history(channel_username, limit=100)
            payload = {
                'name': chat.title,
                'subscribers': str(chat.members_count),
                'chanel_id':chat.id,
                'chanel_link':chanel_link,
                'description ': chat.description
            }

            if chat.photo is not None:
                file_path = client.download_media(chat.photo.big_file_id, file_name="channel_photo.jpg")
                files = {'pictures': open(file_path, 'rb')}



                # Add the payload as form fields
                for key, value in payload.items():
                    files[key] = (None, str(value))

                #response = requests.post('https://stattron.ru/chanel/', files=files)
                response = requests.post('http://127.0.0.1:8000/chanel/', files=files)



            chanel_id = Chanel.objects.get(chanel_link=chanel_link)

            for views in total_view:
                if views.text is not None:
                    text=views.text
                else:
                    text=views.caption

                media = ""
                if views.photo:
                    media="photo"
                elif views.video:
                    media="video"
                elif views.animation:
                    media="animation"






                if text is not None:
                    view_text=text
                    text=text.lower()
                    channel_username=channel_username.lower()
                    instance=Posts.objects.create(
                        chanel=chanel_id,  # Assuming chanel_id is the ID of the channel
                        text=view_text,
                        view=views.views,
                        media=media,
                        forwards_count=views.forwards,
                        link=views.link,
                        date=timezone.make_aware(views.date),
                        id_channel_forward_from=views.forward_from_chat.id if views.forward_from_chat is not None else None,
                        mention=("@" in text or "t.me/" in text or 'https://t.me/' in text) and (
                                    f'@{channel_username}' not in text and f't.me/{channel_username}' not in text and f'https://t.me/{channel_username}' not in text)
                    )
                    #post_save.send(sender=Posts,instance=instance,created=True)


















            if response.status_code == 200:
                break


#celery -A Statron worker -l info --pool=solo