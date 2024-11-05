from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date,timedelta,datetime
import pytz
import random
import string
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
from django.db.models import Sum
# Create your models here.
from decimal import Decimal
import uuid
from django.utils import timezone
class Profile(models.Model):
    username=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    phone_number = PhoneNumberField()
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=140)
    email=models.EmailField()
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    photo=models.ImageField()
    is_onedollar = models.BooleanField(default=True)
    last_visited = models.DateTimeField(auto_now=True)
    telegram_bio=models.CharField(max_length=150,null=True, blank=True, default=None)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, default=None)
    timezone = models.CharField(max_length=63, choices=[(tz, tz) for tz in pytz.all_timezones], default='UTC')
    recommended_by = models.ForeignKey('Ref', on_delete=models.CASCADE, related_name='recommended_profiles',
                                       null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    expire_data=models.DateTimeField(null=True, blank=True, default=None)
    notify_bio=models.CharField(max_length=150,null=True, blank=True, default=None)
    notify_name=models.CharField(max_length=150,null=True, blank=True, default=None)
    notify_id=models.BigIntegerField(unique=True, null=True, blank=True, default=None)



    def save(self, *args, **kwargs):
        # Update the associated User's email before saving
        self.username.email = self.email
        self.username.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username.username

class Ref(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='referal')
    code = models.UUIDField(default=uuid.uuid4, unique=True)


    def __str__(self):
        return self.profile.username.username





class Chanel(models.Model):
    chanel_link=models.CharField(max_length=150)
    chanel_id=models.IntegerField(default=0)
    description = models.TextField()
    name=models.CharField(max_length=150,verbose_name="Называние канала")
    pictures=models.ImageField(verbose_name='Лого')
    subscribers=models.IntegerField()
    views=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    last_update=models.DateTimeField(auto_now=True)
    add_chanel =models.ForeignKey("Add_chanel", on_delete=models.CASCADE)
    username=models.CharField(max_length=140)
    daily_views=models.IntegerField(default=0,blank=True,null=True)
    yesterday_views=models.IntegerField(default=0,blank=True,null=True)
    daily_subscribers=models.IntegerField(default=0, blank=True, null=True)
    yesterday_subscribers=models.IntegerField(default=0,blank=True,null=True)
    weekly_subscribers=models.IntegerField(default=0, blank=True, null=True)
    weekly_monthy = models.IntegerField(default=0, blank=True, null=True)



    @property
    def er(self):
        return (self.subscribers/self.views) * 100









    def save(self, *args, **kwargs):
        if self.pk is not None:

            old_instance = Chanel.objects.select_related('add_chanel').get(pk=self.pk)
            old_subscribers = old_instance.subscribers
            old_views=old_instance.views

            if old_subscribers != 0 and old_views!=0:
                difference = self.subscribers - old_subscribers
                difference_views=self.views - old_views
                if self.last_update.date() == date.today()-timedelta(days=1):
                    self.yesterday_subscribers=self.daily_subscribers
                    self.yesterday_views=self.daily_views


                if self.last_update.date() == date.today():

                    self.daily_subscribers += difference
                    self.daily_views+=difference_views
                    existing_sub_per_day = SubPerday.objects.filter(chanel=old_instance,created_at__date=date.today()).first()

                    if not existing_sub_per_day:
                        SubPerday.objects.create(chanel=old_instance,subperday=self.subscribers,viewsperday=self.daily_views)
                    else:
                        existing_sub_per_day.subperday=self.subscribers
                        existing_sub_per_day.viewsperday=self.daily_views
                        existing_sub_per_day.save(update_fields=['subperday','viewsperday'])

                else:
                    self.daily_subscribers = difference
                    self.daily_views = difference_views






                if self.last_update.date() >= (date.today() - timedelta(days=date.today().weekday())):
                    self.weekly_subscribers += difference
                else:
                    self.weekly_subscribers = 0

                if self.last_update.date().month == date.today().month:
                    self.weekly_monthy += difference

                else:
                    self.weekly_monthy = 0

        super().save(*args, **kwargs)





    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Канал"
        verbose_name_plural="Канал"
        ordering=['-subscribers']


class Demo(models.Model):
    chanel = models.ForeignKey(Chanel, on_delete=models.CASCADE, related_name='demo_chanel')
    profile=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='demo_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chanel.name

class Chanel_img(Chanel):
    class Meta:
        proxy=True
    class Chanel_manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(pictures__isnull=False).exclude(pictures='')

    objects = Chanel_manager()




class Subperhour(models.Model):
    chanel = models.ForeignKey(Chanel, on_delete=models.CASCADE, related_name='subperhour')
    created_at = models.DateTimeField(auto_now_add=True)
    subperhour = models.IntegerField()
    difference=models.IntegerField()

    class Meta:
        unique_together = ('chanel', 'created_at')
        ordering=['-created_at']
    def __str__(self):
        return self.chanel.name



class SubPerday(models.Model):
    chanel = models.ForeignKey(Chanel, on_delete=models.CASCADE, related_name='subperday')
    created_at = models.DateTimeField(auto_now_add=True)
    subperday=models.IntegerField()
    viewsperday=models.IntegerField()

    class Meta:
        unique_together = ('chanel', 'created_at')
    def __str__(self):
        return self.chanel.name


class Posts(models.Model):
    chanel=models.ForeignKey(Chanel,on_delete=models.CASCADE,related_name='post')
    text=models.TextField()
    view=models.IntegerField()
    media=models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    mention=models.BooleanField(default=False)
    date=models.DateTimeField(default=None)
    id_channel_forward_from=models.IntegerField(null=True)
    link=models.CharField(null=True, blank=True, default=None,max_length=250)
    forwards_count=models.BigIntegerField(null=True, blank=True, default=None)


    class Meta:
        ordering=['-date']





    def __str__(self):
        return self.chanel.name

class Notify(models.Model):
    Type_enter = (
        ('chanel', 'Упоминания канала '),
        ('word', ' Упоминание слова и фразы'),

    )
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='notify_profile')
    word=models.CharField(max_length=250)
    Type_notify = models.CharField(max_length=20, choices=Type_enter)
    start=models.BooleanField(default=False)
    check_date = models.DateTimeField(null=True, blank=True,default=None)
    count=models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # Update the associated User's email before saving
        if self.start is True:
            self.check_date=timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.word


class Add_chanel(models.Model):
    username = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='add_chanel')
    category=models.ManyToManyField('Category_chanels',blank=True)
    chanel_link = models.CharField(default=None,max_length=150,unique=True)





    def __str__(self):
        return self.username.username.username


class Category_chanels(models.Model):
    name=models.CharField(max_length=150)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mentions(models.Model):
    mentioned_channel = models.ForeignKey(Chanel, on_delete=models.CASCADE, related_name="mentions")
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="mentions_post")


    class Meta:
        ordering=['-post__date']

    def __str__(self):
        return self.mentioned_channel.name

class Discount(models.Model):
    code=models.CharField(max_length=200,editable=False,unique=True)
    discount_percentage=models.IntegerField(default=0,validators=[MinValueValidator(0), MaxValueValidator(100)])

    def save(self, *args, **kwargs):
        self.code=''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)


    def __str__(self):
        return self.code

class Like(models.Model):
    username = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='like')
    chanel_name=models.ForeignKey(Chanel,on_delete=models.CASCADE,null=True)
    node=models.CharField(max_length=255,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username.username.username


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

class PaymentGateway(models.Model):

    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=255)
    api_secret = models.CharField(max_length=255)  # If needed
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.name




class Payment(models.Model):
    profile=models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='withdraw')
    paymentgatway=models.ForeignKey(PaymentGateway,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    wallet=models.CharField(max_length=200)
    amount=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    status=models.BooleanField(default=False)




    def __str__(self):
        return self.profile.first_name


class Type_sub(models.Model):
    price=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    name=models.CharField(max_length=200)
    days = models.IntegerField(default=0)

    def __str__(self):
        return self.name




class Subscribe(models.Model):
    profile=models.ForeignKey(Profile, on_delete=models.CASCADE,related_name='subscribe')
    type_sub=models.ForeignKey(Type_sub,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.status:
            self.profile.expire_data=None
            self.profile.is_premium=False
            self.profile.save(update_fields=['expire_data','is_premium'])
            super().save(*args, **kwargs)
            return
        if self.profile.expire_data is not None and self.profile.expire_data > timezone.now():
            return


        if self.type_sub.price == 1.00 and self.profile.is_onedollar == False:
            return

        if self.type_sub.price == 1.00 and self.profile.is_onedollar:
            self.profile.is_onedollar=False
            self.profile.expire_data = timezone.now() + timedelta(days=self.type_sub.days)
            self.profile.is_premium = True
            self.profile.save(update_fields=['is_onedollar','is_premium','expire_data'])
            super().save(*args, **kwargs)
            return

        self.profile.expire_data=timezone.now() + timedelta(days=self.type_sub.days)
        self.profile.is_premium=True
        self.profile.save(update_fields=['is_premium','expire_data'])


        super().save(*args, **kwargs)




    def __str__(self):
        return self.type_sub.name


class Commission(models.Model):
    code=models.ForeignKey(Ref,on_delete=models.CASCADE,related_name='commission')
    amount=models.DecimalField(max_digits=10, decimal_places=2,default=0)


    def save(self, *args, **kwargs):
        # Only apply the commission rate when the instance is first created
        if self._state.adding:  # Check if it's a new instance
            self.amount = self.amount * Decimal('0.1')  # Use Decimal instead of float

        super().save(*args, **kwargs)



