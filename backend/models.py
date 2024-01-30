from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
import pytz
# Create your models here.
class Profile(models.Model):
    username=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    phone_number = PhoneNumberField()
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=140)
    email=models.EmailField()
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    currency=models.CharField(max_length=10)
    created_at=models.DateTimeField(auto_now_add=True)
    photo=models.ImageField()
    is_online = models.BooleanField(default=False)
    last_visited = models.DateTimeField(auto_now=True)
    qiwi=models.CharField(max_length=200)
    timezone = models.CharField(max_length=63, choices=[(tz, tz) for tz in pytz.all_timezones], default='UTC')

    def save(self, *args, **kwargs):
        # Update the associated User's email before saving
        self.username.email = self.email
        self.username.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username.username



class Chanel(models.Model):
    chanel_link=models.CharField(max_length=150)
    name=models.CharField(max_length=150,verbose_name="Называние канала")
    pictures=models.ImageField(verbose_name='Лого')
    subscribers=models.IntegerField()
    views=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    add_chanel =models.ForeignKey("Add_chanel", on_delete=models.CASCADE,null=True)
    username=models.CharField(max_length=140)






    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Канал"
        verbose_name_plural="Канал"
        ordering=['-subscribers']





class Add_chanel(models.Model):
    username = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='profile')
    #category=models.ForeignKey('Category_chanels',on_delete=models.CASCADE)
    chanel_link = models.CharField(max_length=150)
    description=models.TextField()

    def __str__(self):
        return self.username.username.username


class Category_chanels(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Like(models.Model):
    username=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    chanel_name=models.ForeignKey(Chanel,on_delete=models.CASCADE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username.username


class Add_userbot(models.Model):
    name=models.CharField(max_length=100)
    api_id=models.IntegerField()
    api_hash=models.CharField(max_length=100)
    session=models.TextField(blank=True)
    created=models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, null=True)
    code = models.CharField(max_length=200,blank=True)
    is_active = models.BooleanField(default=False, help_text="Is this userbot active?")


    def __str__(self):
        return self.name