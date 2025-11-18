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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.conf import settings

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
            total_view = client.get_chat_history(channel_username, limit=10)
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
                #for key, value in payload.items():
                 #   files[key] = (None, str(value))



                #response = requests.post('https://stattron.ru/chanel/', files=files)
                response = requests.post('http://127.0.0.1:8001/chanel/', data=payload, files=files)




            chanel_id = Chanel.objects.get(chanel_link=chanel_link)


            for view in total_view:
                # Get text or caption
                text_content = view.text or view.caption
                if not text_content:
                    continue  # skip if no text

                media = ""
                photo_file = None
                video_file = None

                # Helper function to download and wrap file
                def download_to_django(file_id, ext, folder="posts"):
                     local_path = client.download_media(file_id, file_name=f"{folder}_{file_id}.{ext}")
                     with open(local_path, 'rb') as f:
                         django_file = File(f)
                         filename = f"{folder}/{folder}_{file_id}.{ext}"
                         saved_path = default_storage.save(filename, django_file)
                         return saved_path
                    # filename = f"{folder}/{folder}_{file_id}.{ext}"
                    # file_content = ContentFile(local_path)
                    # saved_path = Posts.photo.field.storage.save(filename, file_content)
                    # return saved_path



                # Determine media type and download
                if view.photo:
                    media = "photo"
                    photo_file = download_to_django(view.photo.file_id, "jpg", folder="photo")
                elif view.video:
                    media = "video"
                    video_file = download_to_django(view.video.file_id, "mp4", folder="video")
                elif view.animation:
                    media = "animation"

                # Lowercase for mention checking
                text_lower = text_content.lower()
                channel_username_lower = channel_username.lower()

                mention_flag = (
                        ("@" in text_lower or "t.me/" in text_lower or 'https://t.me/' in text_lower) and
                        (f'@{channel_username_lower}' not in text_lower and
                         f't.me/{channel_username_lower}' not in text_lower and
                         f'https://t.me/{channel_username_lower}' not in text_lower)
                )

                # Save post immediately
                Posts.objects.create(
                    chanel=chanel_id,
                    text=text_content,
                    view=view.views,
                    media=media,
                    photo=photo_file if media == "photo" else None,
                    video=video_file if media == "video" else None,
                    forwards_count=view.forwards,
                    link=view.link,
                    date=timezone.make_aware(view.date),
                    id_channel_forward_from=getattr(view.forward_from_chat, 'id', None),
                    mention=mention_flag
                )


















            if response.status_code == 200:
                break


#celery -A Statron worker -l info --pool=solo