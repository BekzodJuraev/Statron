from django.contrib import admin
from .models import Profile,Chanel,Add_chanel,Like,Category_chanels,Add_userbot,Posts,SubPerday,Subperhour,Mentions,Ref,Notify,Demo,Payment,Type_sub,Subscribe,Commission,Discount
@admin.register(Discount)
class Discount(admin.ModelAdmin):
    list_display = ['code','discount_percentage']
    readonly_fields = ['code']



@admin.register(Commission)
class Commission(admin.ModelAdmin):
    pass
@admin.register(Subscribe)
class Subscribe(admin.ModelAdmin):
    pass
@admin.register(Type_sub)
class Type_sub(admin.ModelAdmin):
    list_display = ['id','price','name']

@admin.register(Payment)
class Payment(admin.ModelAdmin):
    list_display = ['profile','wallet','amount']

@admin.register(Demo)
class Demo(admin.ModelAdmin):
    list_display = ['profile','chanel']


@admin.register(Notify)
class Notify(admin.ModelAdmin):
    list_display = ['profile','word']
@admin.register(Ref)
class Ref(admin.ModelAdmin):
    list_display = ['profile','code']

@admin.register(Mentions)
class Mentions(admin.ModelAdmin):
    list_display = ['mentioned_channel']
@admin.register(Subperhour)
class Subperhour(admin.ModelAdmin):
    list_display = ['chanel','created_at']
@admin.register(SubPerday)
class SubPerday(admin.ModelAdmin):
    list_display = ['chanel','created_at','subperday']
# Register your models here.
@admin.register(Posts)
class Posts(admin.ModelAdmin):
    list_display = ['chanel','created_at','mention','id_channel_forward_from','date','media']

@admin.register(Profile)
class Profile(admin.ModelAdmin):
    list_display = ['username','created_at','recommended_by']


@admin.register(Chanel)
class ChanelAdmin(admin.ModelAdmin):
    list_display = ['subscribers','chanel_link','views','last_update','created_at']

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