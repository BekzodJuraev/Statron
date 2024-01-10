from django.contrib import admin
from .models import Profile,Chanel
# Register your models here.
@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['username','created_at']


@admin.register(Chanel)
class ChanelAdmin(admin.ModelAdmin):
    list_display = ['username','subscribers','chanel_link','views']

    list_display_links = ['chanel_link']