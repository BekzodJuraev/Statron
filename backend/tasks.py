from celery import Celery
from django.utils import timezone
from time import sleep
from pyrogram import Client
from pyrogram import filters
import logging
from django.db import transaction
from .models import Add_userbot
from celery import shared_task
import os
import requests


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
            channel_link = chanel_link
            channel_username = channel_link.split('/')[-1]
            chat = client.get_chat("@" + channel_username)
            total_view = client.get_chat_history("@" + channel_username, limit=5)
            send_view = 0
            for views in total_view:
                if views.views:
                    send_view += views.views

            payload = {
                'name': chat.title,
                'subscribers': str(chat.members_count),
                'chanel_link': channel_link,
                'views': str(send_view),
            }

            if chat.photo is not None:
                file_path = client.download_media(chat.photo.big_file_id, file_name="channel_photo.jpg")
                files = {'pictures': open(file_path, 'rb')}

                # Add the payload as form fields
                for key, value in payload.items():
                    files[key] = (None, str(value))

                response = requests.post('https://6083-217-30-171-58.ngrok-free.app/chanel/', files=files)


                with open(file_path, "rb") as photo:
                    client.send_photo("@lsbnvVm9TmhjZDNi", photo)


            if response.status_code == 200:
                break
