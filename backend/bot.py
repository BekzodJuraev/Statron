from pyrogram import Client
import aiohttp
import asyncio
from django.utils import timezone
import requests
from pyrogram.enums import ChatAction,ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from backend.models import Add_userbot,Chanel,Posts,Profile
import os
import telegram
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pyrogram import filters
from django.core.files import File

#client=Client('me_client', api_id, api_hash)


clients = {}  # Dictionary to store multiple Pyrogram clients






async def update(client):
    while True:
        try:
            await waiting()

            # Fetch data asynchronously from Django ORM
            chanel_all = await sync_to_async(list)(Chanel.objects.all())

            for i in chanel_all:
                chanel_link = i.chanel_link.split('/')[-1]

                try:
                    chat = await client.get_chat(chanel_link)
                    total_view = client.get_chat_history(chanel_link, limit=10)

                    # Update subscribers
                    i.subscribers = chat.members_count
                    await sync_to_async(i.save)()

                    # Get last recorded post to avoid duplicates
                    post_get = await sync_to_async(
                        lambda: Posts.objects.filter(chanel=i).order_by('-date').first()
                    )()

                    async for views in total_view:
                        text_content = views.text or views.caption
                        if not text_content:
                            continue

                        media = ""
                        media_file = None

                        # Determine media type and extract file_id
                        if views.photo:
                            media = "photo"
                            media_file = views.photo.file_id
                        elif views.video:
                            media = "video"
                            media_file = views.video.file_id
                        elif views.animation:
                            media = "animation"

                        # Check mentions
                        text_lower = text_content.lower()
                        chanel_link_lower = chanel_link.lower()

                        mention_flag = (
                            ("@" in text_lower or "t.me/" in text_lower or "https://t.me/" in text_lower) and
                            (f"@{chanel_link_lower}" not in text_lower and
                             f"t.me/{chanel_link_lower}" not in text_lower and
                             f"https://t.me/{chanel_link_lower}" not in text_lower)
                        )

                        post_date = timezone.make_aware(views.date) if timezone.is_naive(views.date) else views.date

                        # Create new post if it's newer than the latest stored post
                        if post_get is None or post_date > post_get.date:
                            await sync_to_async(Posts.objects.create)(
                                chanel=i,
                                text=text_content,
                                view=views.views,
                                media=media,
                                media_file=media_file,
                                forwards_count=views.forwards,
                                link=views.link,
                                date=post_date,
                                id_channel_forward_from=getattr(views.forward_from_chat, 'id', None),
                                mention=mention_flag
                            )

                except Exception as e:
                    print(f"Error updating channel {chanel_link}: {e}")

            await asyncio.sleep(600)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")















@database_sync_to_async
def get_userbots():
    return list(Add_userbot.objects.filter(is_active=True))

async def initialize_clients():
    userbots = await get_userbots()


    for userbot in userbots:
        # Retrieve the session data from the model
        session_data = userbot.session

        client = Client(
            userbot.name,
            api_id=userbot.api_id,
            api_hash=userbot.api_hash,
            phone_number=userbot.phone_number,
            session_string=session_data
        )

        # Set the session data for the client


        clients[userbot.id] = client
        #print('userbot_added')

async def remove_inactive_clients():
    while True:
        #print('hi')
        active_userbot_ids = [userbot.id for userbot in await get_userbots()]

        # Remove clients that are no longer in the database
        for client_id in list(clients.keys()):
            if client_id not in active_userbot_ids:
                del clients[client_id]
                print(f"Client with ID {client_id} removed.")

        await asyncio.sleep(10)

@database_sync_to_async
def get_expired_profiles():
    return list(Profile.objects.filter(expire_data__lte=timezone.now(), is_premium=True))

@database_sync_to_async
def update_profile(profile):
    profile.is_premium = False
    profile.expire_data = None
    profile.save(update_fields=['is_premium', 'expire_data'])

async def check_expired_subscriptions():
    while True:
        expired_profiles = await get_expired_profiles()
        for profile in expired_profiles:
            await update_profile(profile)
        print("Checked for expired subscriptions.")
        await asyncio.sleep(60)

async def waiting():
    while not clients:  # Check if clients is empty
        print('Waiting for clients...')
        await asyncio.sleep(60)
        await initialize_clients()

async def run_userbots():
    await waiting()

    tasks = [client.start() for client in clients.values()]

    # Wait for all clients to start
    await asyncio.gather(*tasks)


    # Run update tasks concurrently

    message_handler_tasks = [asyncio.create_task(update(client)) for client in clients.values()]
    asyncio.create_task(remove_inactive_clients())
    #message_handler_tasks_new = [asyncio.create_task(update_new(client)) for client in clients.values()]

    # Wait for all update tasks to run
    await asyncio.gather(*message_handler_tasks)




    # Run the update task for each client concurrently


#celery -A Statron worker -l info --pool=solo

#celery -A your_project worker -l info -c 4 -n worker3@%h

#celery -A your_project flower --port=5555


#STATIC_ROOT = '/var/www/html/static/'
#sudo systemctl reload gunicorn
#sudo service nginx reload
async def run_userbot():
    await initialize_clients()
    await run_userbots()



async def main_loop():
    await asyncio.gather(
        run_userbot(),  # Runs concurrently
        check_expired_subscriptions()  # Runs concurrently
    )













