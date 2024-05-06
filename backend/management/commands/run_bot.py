from django.core.management.base import BaseCommand
from backend.bot import  run_userbot
import asyncio
class Command(BaseCommand):
    help = 'Run the Pyrogram userbot'


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Pyrogram userbot...'))
        asyncio.run(run_userbot())