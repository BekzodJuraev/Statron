from django.contrib import admin
from .models import Profile,Chanel,Add_chanel,Like,Category_chanels,Add_userbot
# Register your models here.
@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['username','created_at']


@admin.register(Chanel)
class ChanelAdmin(admin.ModelAdmin):
    list_display = ['username','subscribers','chanel_link','views','update_date','created_at']

    list_display_links = ['chanel_link']


@admin.register(Like)
class Category_chanelsAdmin(admin.ModelAdmin):
    list_display = ['username','chanel_name','created_at']
@admin.register(Category_chanels)
class Category_chanelsAdmin(admin.ModelAdmin):
    list_display = ['name','created_at']

@admin.register(Add_chanel)
class Category_chanelsAdmin(admin.ModelAdmin):
    list_display = ['username','chanel_link']


class AddUserbotAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_id', 'api_hash', 'phone_number','is_active')



admin.site.register(Add_userbot, AddUserbotAdmin)