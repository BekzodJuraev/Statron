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
    timezone = models.CharField(max_length=63, choices=[(tz, tz) for tz in pytz.all_timezones], default='UTC')

    def save(self, *args, **kwargs):
        # Update the associated User's email before saving
        self.username.email = self.email
        self.username.save()
        super().save(*args, **kwargs)



class Chanel(models.Model):
    chanel_link=models.CharField(max_length=150)
    name=models.CharField(max_length=150,verbose_name="Называние канала")
    pictures=models.ImageField(verbose_name='Лого')
    subscribers=models.IntegerField()
    views=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    #add_chanel =models.ForeignKey(Add_chanel, on_delete=models.CASCADE)
    username=models.CharField(max_length=140)






    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Канал"
        verbose_name_plural="Канал"
        ordering=['-subscribers']
