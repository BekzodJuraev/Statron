from pyrogram import Client
import aiohttp
import asyncio
from django.utils import timezone
import requests
from pyrogram.enums import ChatAction,ParseMode
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from backend.models import Add_userbot,Chanel,Posts
import os
import telegram
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from pyrogram import filters


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
                    total_view =   client.get_chat_history(chanel_link, limit=10)

                    # Update ORM asynchronously
                    chanel_get = await sync_to_async(Chanel.objects.get)(chanel_link=i.chanel_link)
                    chanel_get.subscribers = chat.members_count
                    await sync_to_async(chanel_get.save)()

                    post_query = await sync_to_async(Posts.objects.filter)(chanel=chanel_get)
                    Post_get = await sync_to_async(post_query.order_by('-date').first)()







                    async for views in total_view:
                        if views.text is not None:
                            text = views.text
                        else:
                            text = views.caption

                        media = ""
                        if views.photo:
                            media = "photo"
                        elif views.video:
                            media = "video"
                        elif views.animation:
                            media = "animation"


                        if text is not None:
                            view_text = text
                            text = text.lower()
                            chanel_link=chanel_link.lower()
                            if Post_get is None or timezone.make_aware(views.date) > Post_get.date:
                                await sync_to_async(Posts.objects.create)(
                                    chanel=chanel_get,  # Assuming chanel_id is the ID of the channel
                                    text=view_text,
                                    view=views.views,
                                    media=media,
                                    date=timezone.make_aware(views.date),
                                    id_channel_forward_from=views.forward_from_chat.id if views.forward_from_chat is not None else None,
                                    mention=("@" in text or "t.me/" in text or 'https://t.me/' in text) and (
                                            f'@{chanel_link}' not in text and f't.me/{chanel_link}' not in text and f'https://t.me/{chanel_link}' not in text)
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
















