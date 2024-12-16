from django.shortcuts import render,redirect
from rest_framework import generics
from django.db.models import Value,Case,When
from django.core.cache import cache
from decimal import Decimal
import re
import hashlib
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.db import connection
from django.contrib.auth.models import User
from django.db.models.functions import TruncHour
from datetime import date, timedelta, datetime
from .serializers import ChanelSerializer,LoginFormSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import Chanel,Profile,Add_chanel,Like,Posts,SubPerday,Subperhour,Mentions,Category_chanels,Chanel_img,Ref,Notify,Demo,Payment,Subscribe,Type_sub,Discount,Commission
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View,ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView,FormView
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import AddChanelForm,LikeForm
from django.db.models import Sum,Q,Count,F,Max,Prefetch
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import asyncio
import telegram
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo

import time

from config import TOKEN_NOTIFY, TOKEN_WEBHOOK, ID_OWNER_TELGRAM,TOKEN_AUTH,URL,SHOP_ID,SECRET_KEY,SECRET_KEY,CUR,Wallet_public,Wallet_private



my_id=ID_OWNER_TELGRAM

bot = telegram.Bot(TOKEN_WEBHOOK)

#dp = Dispatcher(bot)
#dp.middleware.setup(LoggingMiddleware())


class Freekassa(TemplateView):
    template_name = 'fk-verify.html'

def authenticate_user_with_session(request):
    session_key = request.GET.get('session_key')

    if session_key:
        # Retrieve the session using the session key
        try:
            session = get_object_or_404(Session, session_key=session_key)
        except:
            return redirect('main')
        session_data = session.get_decoded()

        # Get the user_id from the session data
        username = session_data.get('username')

        if username:
            # Authenticate and log the user in
            user = get_object_or_404(User, username=username)
            login(request, user)

            # Redirect the user to the dashboard or another authenticated page
            return redirect('main')

    return HttpResponse("Invalid session", status=400)

@csrf_exempt
@require_POST
def telegram_notify(request):
    bot_notify = telegram.Bot(token=TOKEN_NOTIFY)
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        chat_info = json_data['message']['chat']
        text = json_data['message'].get('text', '')

        id = chat_info.get('id')
        bio = chat_info.get('username')
        first_name = chat_info.get('first_name')

        if text.startswith('/start profile_'):
            profile_id = text.split('profile_')[1]
            try:
                profile = Profile.objects.get(id=profile_id)

                if not profile.notify_id:

                    profile.notify_id = id
                    profile.notify_name = first_name
                    profile.notify_bio = bio
                    profile.save(update_fields=['notify_id', 'notify_name', 'notify_bio'])


                    bot_notify.send_message(id,
                                            'Отлично, ваш аккаунт привязан, вернитесь на страницу - https://stattron.ru/tracking-posts/')
                else:

                    bot_notify.send_message(id,
                                            f"Упс, этот аккаунт Телеграм ({id}) уже привязан к другому аккаунту в сервисе")

            except Profile.DoesNotExist:

                bot_notify.send_message(id, "Указанный профиль не найден.")
                return JsonResponse({'status': 'Profile not found'}, status=404)

        return JsonResponse({'status': 'Success'})








@csrf_exempt
@require_POST
def telegram_auth(request):

    bot_auth = telegram.Bot(token=TOKEN_AUTH)
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        id=json_data['message']['chat']['id']
        nickname=None
        try:
            nickname = json_data['message']['chat']['username']

        except:
            pass
        first_name=json_data['message']['chat']['first_name']
        text=json_data['message']['text']



        if text.startswith('/start profile_'):
            try:
                profile = Profile.objects.filter(telegram_id=id).first()
                if profile:
                    bot_auth.send_message(id, "Your Telegram account is already connected to an existing profile.")
                else:
                    profile_id = text.split('profile_')[1]
                    profile = Profile.objects.get(id=profile_id)

                    # Check if profile already has a connected telegram_id
                    if profile.telegram_id:
                        bot_auth.send_message(id, "Your Telegram account is already connected.")
                    else:
                        # Connect the telegram account
                        profile.telegram_id = id
                        profile.telegram_bio = nickname
                        profile.save(update_fields=['telegram_id','telegram_bio'])
                        bot_auth.send_message(id,
                                              f"Your Telegram account has been connected with profile {profile_id}.")

            except Profile.DoesNotExist:
                bot_auth.send_message(id, "Error: Profile not found.")
            except Exception as e:
                bot_auth.send_message(id, f"Error: {str(e)}")
        else:

            try:
                # Check if a user with this telegram_id already exists
                profile = Profile.objects.filter(telegram_id=id).first()
                if profile:
                    #bot_auth.send_message(id, "Your Telegram account is already connected to an existing profile.")
                    request.session['username'] = profile.username.username
                    request.session.set_expiry(3600)  # Expires after 1 hour
                    request.session.save()

                    # Get the session key to send to the user
                    session_key = request.session.session_key

                    # Construct the URL with the session key
                    url_with_session = f"https://127.0.0.1:8000/telegram/login/?session_key={session_key}"

                    # Send the URL with the session key via the Telegram bot
                    bot_auth.send_message(id, f"Visit this link to authenticate: {url_with_session}")




                else:
                    # Create a new User and Profile if no telegram_id is found
                    user, created = User.objects.get_or_create(username=id)
                    if created:
                        Profile.objects.create(
                            username=user,
                            first_name=first_name,
                            telegram_bio=nickname,
                            telegram_id=id
                        )
                        bot_auth.send_message(id, "New profile created and connected to your Telegram.")
                    else:
                        bot_auth.send_message(id, "You already have an account")

                    # Set the session for authentication
                    request.session['username'] = user.username
                    request.session.set_expiry(3600)  # Expires after 1 hour
                    request.session.save()

                    # Get the session key to send to the user
                    session_key = request.session.session_key

                    # Construct the URL with the session key
                    url_with_session = f"https://127.0.0.1:8000/telegram/login/?session_key={session_key}"

                    # Send the URL with the session key via the Telegram bot
                    bot_auth.send_message(id, f"Visit this link to authenticate: {url_with_session}")
            except Exception as e:
                bot_auth.send_message(id, f"Error during user creation: {str(e)}")

        return HttpResponse(status=200)






@csrf_exempt
@require_POST
def notification_freekassa(request):
    try:

        MERCHANT_ID=request.POST.get('MERCHANT_ID')
        order_id = request.POST.get('MERCHANT_ORDER_ID')
        amount = request.POST.get('AMOUNT')
        signature = request.POST.get('SIGN')
        us_key=request.POST.get('us_key')



        # Step 2: Rebuild the signature string using the data from FreeKassa
        signature_string = f"{MERCHANT_ID}:{amount}:{SECRET_KEY}:{order_id}"


        calculated_signature = hashlib.md5(signature_string.encode()).hexdigest()


        if calculated_signature == signature:
            profile=Profile.objects.filter(first_name=us_key).first()
            sub=Type_sub.objects.filter(id=order_id).first()
            Subscribe.objects.create(profile=profile,type_sub=sub,status=True)
            if profile.recommended_by:
                Commission.objects.create(profile=profile.recommended_by, amount=amount)


            if profile.promo_code:
                profile.promo_code = None
                profile.save(update_fields=['promo_code'])




            return HttpResponse(status=200)

        else:

            print(f"Invalid signature for Order ID {order_id}.")
            return HttpResponse(status=400)  # Bad Request

    except Exception as e:

        print(f"Error processing notification: {e}")
        return HttpResponse(status=500)

@csrf_exempt
@require_POST
def telegram_webhook(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))
        if 'message' in json_data:
            process_message(json_data)
        elif 'callback_query' in json_data:
            process_callback_query(json_data)

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)



def process_message(json_data):
    chat_id = json_data['message']['chat']['id']
    message_text = json_data['message'].get('text',"")
    forward_id = json_data['message'].get('forward_from_chat', {}).get('id')
    chat_username = json_data['message']['chat'].get('first_name', 'Someone')

    if message_text.startswith("@") or message_text.startswith("-") or forward_id:
        try:
            chanel_chanel_id = message_text if message_text else forward_id
            chat = bot.get_chat(chat_id=chanel_chanel_id)
            message_text = f"https://t.me/{chat.username}" if chat.username else chat.invite_link
        except:
            bot.send_message(chat_id,"Мы не нашли ваш канал")
            return












    if message_text:
        if message_text == '/start':
            reply_keyboard = [
                [KeyboardButton("🔗Наш сайт")],
            ]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(chat_id=chat_id,
                             text=f"✌️Привет, {chat_username} Добро пожаловать на сервис STATTRON. Тут можно легко и просто получить подробную статистику на канал. Отправьте ссылку/id на канал, либо перешлите пост из канала, чтобы мы могли его проанализировать:",
                             reply_markup=reply_markup)
        elif message_text == "🔗Наш сайт":
            bot.send_message(chat_id=chat_id, text="https://stattron.ru")
        else:

            chanel_link = Chanel.objects.all().values_list('chanel_link', flat=True)



            if message_text in chanel_link:
                chanel_get = SubPerday.objects.filter(
                    chanel__chanel_link=message_text ).values('created_at', 'subperday')
                Mention_count = Posts.objects.filter(
                    chanel__chanel_link=message_text, mention=True).count()
                Ads_count=Mentions.objects.filter(mentioned_channel__chanel_link=message_text).count()

                chanel = Chanel.objects.get(chanel_link=message_text)

                chanel_pk = chanel.pk
                chanel_name = chanel.name

                analytics_data = '\n'.join(
                    [f"📅 {data['created_at'].strftime('%Y-%m-%d')}: {data['subperday']}" for data in chanel_get])

                text = (
                    f"👆Выше Вы сможете просмотреть подробную аналитику за запрашиваемый канал / Спасибо за запрос ❤️\n"
                    f"📅Подписок за месяц по дням:\n{analytics_data}"
                )

                inline_keyboard = [
                    [InlineKeyboardButton("📊Анализ на сайте",
                                          web_app=WebAppInfo(
                                              f'https://stattron.ru/detail/{chanel_pk}'))],
                    [InlineKeyboardButton(f"📌Упоминаний - {Ads_count}",
                                          web_app=WebAppInfo(
                                              f'https://stattron.ru/posts/?mention={chanel_name}'))],
                    [InlineKeyboardButton(f"📈Рекламы на канале - {Mention_count}",
                                          web_app=WebAppInfo(
                                              f'https://stattron.ru/posts_ads/?chanel={chanel_name}'))],
                ]
                # Convert inline keyboard to InlineKeyboardMarkup
                inline_markup = InlineKeyboardMarkup(inline_keyboard, resize_keyboard=True)

                bot.send_message(chat_id=chat_id, text=text, reply_markup=inline_markup)
            else:



                # Convert dictionary to JSON string

                bot.send_message(chat_id,
                                 f"🤷‍♂️Мы не увидели, что в нашей базе есть этот канал. Мы передали информацию администрации на добавление этого канала. Если его добавят в базу, Вам придёт уведомление ❗️Анализ этого канала могут добавить только если в канале больше 200 подписчиков")
                inline_keyboard = [
                    [InlineKeyboardButton("✅Добавить", callback_data=f'add#{message_text}#{chat_id}'),
                     InlineKeyboardButton("❌Отклонить", callback_data=f'reject#{message_text}#{chat_id}')],
                ]
                inline_markup = InlineKeyboardMarkup(inline_keyboard, resize_keyboard=True)
                bot.send_message(my_id,
                                 text=f"🔥Пользователь {chat_username}  пытался проанализировать канал  {message_text}, но его нету в базе каналов. Добавим?",
                                 reply_markup=inline_markup)

    else:
        bot.send_message(chat_id=chat_id,
                         text="Неправильный ввод. Чтобы проанализировать канал, просто отправьте сюда его адрес или юзернейм. Например, https://t.me/statron или @telemetr_me или stattron.")



def process_callback_query(json_data):
    query = json_data['callback_query']
    chat_id = query['message']['chat']['id']
    callback_data = query['data'].split("#")
    callback_data_message=callback_data[0]
    callback_data_link_or_id=callback_data[1]
    callback_data_chat_id=callback_data[2]
    message_id=query['message']['message_id']
    if callback_data_message == 'reject':
        bot.delete_message(chat_id=my_id, message_id=message_id)
    if callback_data_message == "add":
        add,created=Add_chanel.objects.get_or_create(username_id=1,chanel_link=callback_data_link_or_id)
        if created:
            bot.send_message(chat_id=my_id,text=f"✅Канал {callback_data_link_or_id} успешно добавлен в базу!")
            bot.send_message(chat_id=callback_data_chat_id, text=f"🤝Здравствуйте. Вы недавно пытались найти анализ на канал {callback_data_link_or_id}. Теперь мы его добавили в нашу базу и Вы сможете каждый день проверять статистику этого канала в нашем боте и сайте")
        else:
            bot.send_message(chat_id=my_id, text="Ошибка не получился!")






class ChanelAPI(APIView):
    def get(self, request):
        chanel_links = Chanel.objects.all()
        serializer = ChanelSerializer(chanel_links, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChanelSerializer(data=request.data)
        if serializer.is_valid():
            chanel_link = serializer.validated_data['chanel_link']

            try:
                chanel = Chanel.objects.get(chanel_link=chanel_link)
                serializer = ChanelSerializer(chanel, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'message': 'Chanel updated'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Chanel.DoesNotExist:
                # If the user does not exist, save the serializer and return the response
                serializer.save()
                return Response({'message': "We added chanel"}, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetReferralCodeView(View):

    def get(self, request, *args, **kwargs):
        referral_code = request.session.get('referral_code', 'No referral code set')

        return HttpResponse(f"Referral Code: {referral_code}")





class LoginAPIView(APIView):


    def post(self, request, *args, **kwargs):

        next_url = request.data.get('next')
        form = LoginFormSerializer(data=request.data)

        if form.is_valid():
            username = form.validated_data.get('username')
            password = form.validated_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                if next_url:
                    return Response({'detail': 'Login successful', 'next': next_url}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Login successful'}, status=status.HTTP_200_OK)

            else:
                return Response({'detail': 'Логин или пароль неверны'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'detail': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)
class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.profile.phone_number = serializer.validated_data.get('phone_number')
        user.profile.save()
        # Add any additional logic here, such as sending a welcome email
        return Response({'detail': 'Registration successful'}, status=status.HTTP_201_CREATED)
class Main(ListView):
    template_name = 'main.html'
    context_object_name = "item"
    model = Chanel_img

    def get_context_data(self, *, object_list=None, **kwargs):

        context =super().get_context_data(**kwargs)

        chart_month = Posts.objects.filter(
            mention=True,
            created_at__gte=date.today() - timedelta(days=29)
        ).values('created_at__date').annotate(count=Count('id'))

        chart_three_month = Posts.objects.filter(
            mention=True,
            created_at__gte=date.today() - timedelta(days=89)
        ).values('created_at__date').annotate(count=Count('id'))

        chart_six_month = Posts.objects.filter(
            mention=True,
            created_at__gte=date.today() - timedelta(days=179)
        ).values('created_at__date').annotate(count=Count('id'))

        daily=Posts.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)

        ).annotate(hour=TruncHour('created_at')).values("hour").annotate(count=Count('id')).order_by('hour')





        context['main']=self.object_list.all().annotate(v=F('views')/Count('post')).order_by('-subscribers')[:6]


        context['chart_month']=chart_month
        context['daily_chart']=daily
        context['chart_three_month']=chart_three_month
        context['chart_six_month']=chart_six_month
        context['top_sub']=self.object_list.all().order_by('-subscribers')[:6]
        context['top_views'] =self.object_list.all().order_by('-views')[:6]
        context['posts_today']=Posts.objects.filter(mention=True,created_at__date=date.today()).count()
        context['total']=Posts.objects.all().count()
        context['mentioned'] =Posts.objects.filter(mention=True).count()
        return context
class PlansView(TemplateView):
    login_url = reverse_lazy('login_site')
    template_name = 'plans.html'


class PaymentView(LoginRequiredMixin,TemplateView):
    login_url = reverse_lazy('login_site')
    template_name = 'payment.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
    #
    def post(self, request, *args, **kwargs):
        promo = self.request.POST.get('promo')
        discount = Discount.objects.filter(code=promo).first()
        if discount:
            profile = self.request.user.profile
            profile.promo_code = discount
            profile.save(update_fields=['promo_code'])
            messages.success(self.request, "Promo code applied successfully!")
        else:
            messages.error(self.request, "Invalid promo code. Please try again.")

        query_params = request.GET.urlencode()
        redirect_url = f"{request.path}?{query_params}" if query_params else request.path
        return redirect(redirect_url)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        amount = float(self.request.GET.get('price'))
        id_order=self.request.GET.get('order_id')
        try:
            Type_sub.objects.get(price=amount, id=id_order)
            if self.request.user.profile.promo_code:
                amount = amount * (1 - self.request.user.profile.promo_code.discount_percentage / 100)
            amount = round(amount, 2)
            signature_string = f"{SHOP_ID}:{amount}:{SECRET_KEY}:{CUR}:{id_order}"
            signature = hashlib.md5(signature_string.encode()).hexdigest()
            url = f"https://pay.freekassa.ru/?m={SHOP_ID}&oa={amount}&o={id_order}&s={signature}&currency={CUR}&us_key={self.request.user.username}"

            context['freekassa_url'] = url

        except:
            pass



        return context






class WithdrawView(LoginRequiredMixin,TemplateView):
    login_url = reverse_lazy('login_site')
    template_name = 'withdraw.html'

    def post(self, request, *args, **kwargs):
        payment_cryptomus=request.POST.get('payment-cryptomus')
        payment_iokassa=request.POST.get('payment-iokassa')
        wallet=self.request.POST.get('wallet')
        amount=float(self.request.POST.get('amount'))
        password=request.POST.get('password-for-payment')
        password_repeat=request.POST.get('password-for-payment-repeat')

        if password != password_repeat:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

            # Verify the user's password
        user = request.user  # Get the currently authenticated user
        if not user.check_password(password):
            messages.error(request, "Incorrect password.")
            return redirect(request.path)

        if user.profile.balance > Decimal(wallet):  # Convert wallet to Decimal
            messages.error(request, "You don't have enough money")
            return redirect(request.path)
        # Process payment logic

        if payment_cryptomus:
            Payment.objects.create(profile=user.profile, paymentgatway="Freekassa", wallet=wallet,
                                                              amount=amount, status=False)
            messages.success(request, "Payment is processing!")
            return redirect(request.path)
        elif payment_iokassa:
            Payment.objects.create(profile=user.profile, paymentgatway="Yukassa", wallet=wallet,
                                   amount=amount, status=False)
            messages.success(request, "Payment is processing!")
            return redirect(request.path)

        # if payment_cryptomus:
        #
        #     data={
        #         'to_wallet_id':wallet,
        #         'amount':amount,
        #         'currency_id':2,
        #         'fee_from_balance':0,
        #         'description':'withdraw',
        #         'idempotence_key':'5'
        #
        #     }
        # #
        #     data_string = json.dumps(data)  # Compact JSON format
        #     sign = hashlib.sha256((data_string + Wallet_private).encode()).hexdigest()
        #     headers = {
        #         'Content-Type': 'application/json',
        #         'Authorization': f'Bearer {sign}'
        #     }
        #     url = f'https://api.fkwallet.io/v1/{Wallet_public}/transfer'
        #
        #     # Make the POST request
        #     response = requests.post(url, headers=headers, data=json.dumps(data))
        #     if response.status_code == 200:
        #         try:
        #             result = response.json()  # Parse JSON response
        #             Payment.objects.create(profile=user.profile, paymentgatway="Freekassa", wallet=wallet,
        #                                    amount=amount, status=False)
        #             print("Request successful:", result)
        #         except ValueError:
        #             print("Request successful, but response is not JSON:", response.text)
        #     else:
        #         Payment.objects.create(profile=user.profile,paymentgatway="Freekassa",wallet=wallet,amount=amount,status=False)
        #         print(f"Request failed with status code {response.status_code}: {response.text}")
        # #
        # # elif payment_iokassa:
        # #     pass




        # Add your payment logic here...
        messages.success(request, "Error wallet")
        return redirect(request.path)

class UpdateCabinet(LoginRequiredMixin,DetailView):
    model = Profile
    login_url = reverse_lazy('login_site')
    template_name = 'cabinet.html'
    context_object_name = 'item'



    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = self.object
        Ref.objects.create(profile=self.object)





        # Redirect back to the current page (refresh the page)
        return redirect(request.path)




    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        ref=Profile.objects.filter(recommended_by__profile=self.object).count()
        withdraw=Payment.objects.filter(profile=self.object)
        context['withdraw']=withdraw
        context['history']=Subscribe.objects.filter(profile=self.object).select_related('type_sub')

        context['ref_code']=Ref.objects.filter(profile=self.object).prefetch_related('recommended_profiles','commission').annotate(count_commission=Count('commission',distinct=True),total_commission_amount=Sum('commission__amount',distinct=True),count_register=Count('recommended_profiles',distinct=True))
        #prefetch_related('commission').annotate(count_commission=Count('commission'),total_commission_amount=Sum('commission__amount'))


        context['ref']=ref

        return context






    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.username:

            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class UpdateView(LoginRequiredMixin,View):
    login_url = reverse_lazy('login_site')

    def post(self, request, *args, **kwargs):
        try:


            photo = request.FILES.get('photo')
            instance_id = self.request.user.profile.id  # Assuming you pass the instance ID in the request

            # Validate data if needed

            if instance_id:
                # If instance_id is provided, update the existing instance
                instance = Profile.objects.get(pk=instance_id)
                if photo:
                    instance.photo = photo
                    instance.save()






            response_data = {'success': True, 'message': 'Data saved successfully'}
        except Profile.DoesNotExist:
            response_data = {'success': False, 'error': 'Instance not found'}
        except Exception as e:
            response_data = {'success': False, 'error': str(e)}

        return JsonResponse(response_data)

class UpdatePassword(LoginRequiredMixin,View):

    def post(self, request, *args, **kwargs):
        current_password = request.POST.get('current-pass')
        new_password = request.POST.get('new-pass')
        new_password_repeat = request.POST.get('new-pass-repeat')
        if new_password != new_password_repeat:
            return JsonResponse({'success': False, 'error': 'New passwords do not match.'})

            # Verify the current password
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'error': 'Incorrect current password.'})

            # Change the password
        request.user.set_password(new_password)
        request.user.save()

        # Update the session to avoid logging out the user
        update_session_auth_hash(request, request.user)

        return JsonResponse({'success': True})

       # return JsonResponse({'success': False, 'error': 'Invalid request method.'})

class DetailChanel(LoginRequiredMixin,DetailView):
    model = Chanel_img
    template_name = 'detail.html'
    login_url = reverse_lazy('login_site')
    context_object_name = 'item'



    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.annotate(v=F('views')/Count('post'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_is = self.request.user.profile
        if not profile_is.is_premium and  profile_is.created_at <= timezone.now() - timedelta(days=21):
            context['day_limit']=True
            return context

        today = timezone.now().date()

        demo_chanel_count=Demo.objects.filter(profile=profile_is,created_at__date=today)
        if not profile_is.is_premium and demo_chanel_count.count() >= 0 and  demo_chanel_count.count() < 4:

            demo, created = Demo.objects.get_or_create(
                chanel=self.object,
                profile=profile_is,
                created_at__date=today
            )
        try:
            if not profile_is.is_premium:
                chanel_saved = Demo.objects.get(profile=profile_is,chanel=self.object, created_at__date=today)

            er = (self.object.subscribers / self.object.views) * 10
            er_daily = (self.object.daily_subscribers / self.object.views) * 10

            repost_param = self.request.GET.get('repost')
            chanel_name = self.request.GET.get('chanel_name')

            if repost_param == "true":
                mention = Mentions.objects.filter(mentioned_channel=self.object,
                                                  post__id_channel_forward_from=self.object.chanel_id).values(
                    'post__chanel__pictures', 'post__chanel__name', 'post__chanel__pk',
                    'post__chanel__subscribers', ).annotate(
                    count=Count('id'), date=Max('post__date'))

            else:
                mention = Mentions.objects.filter(mentioned_channel=self.object).values('post__chanel__pictures',
                                                                                        'post__chanel__name',
                                                                                        'post__chanel__pk',
                                                                                        'post__chanel__subscribers', ).annotate(
                    count=Count('id'), date=Max('post__date'))

            if chanel_name:
                mention = Mentions.objects.filter(mentioned_channel=self.object,
                                                  post__chanel__name__icontains=chanel_name).values(
                    'post__chanel__pictures',
                    'post__chanel__name',
                    'post__chanel__pk',
                    'post__chanel__subscribers', ).annotate(
                    count=Count('id'), date=Max('post__date'))

            repost = Posts.objects.filter(chanel=self.object, id_channel_forward_from__isnull=False).select_related(
                'chanel')

            if profile_is.is_premium:
                mention_chanel = Subperhour.objects.filter(chanel=self.object).select_related(
                    'chanel').prefetch_related(
                    'chanel__mentions')
            else:
                mention_chanel = Subperhour.objects.filter(
                    chanel=self.object,
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).select_related('chanel').prefetch_related('chanel__mentions')

            all_posts = Posts.objects.filter(
                id_channel_forward_from=self.object.chanel_id
            ).select_related('chanel')

            chanel_ads = Mentions.objects.filter(post__chanel=self.object).prefetch_related(
                'mentioned_channel__subperhour').values('mentioned_channel__name', 'mentioned_channel__pk',
                                                        'mentioned_channel__pictures', 'mentioned_channel__chanel_link',
                                                        'mentioned_channel__chanel_id').annotate(
                count=Count('id'), date=Max('post__date'), views=Max('post__view'))

            channel_names = chanel_ads.values_list('mentioned_channel__name', flat=True).distinct()
            channel_id = chanel_ads.values_list('mentioned_channel__chanel_id', flat=True)

            chanel_ads_new = Chanel_img.objects.filter(name__in=channel_names).prefetch_related(
                'subperhour',
                Prefetch('mentions', queryset=Mentions.objects.select_related('post__chanel')),
            )
            all_posts_new = Posts.objects.filter(
                id_channel_forward_from__in=channel_id
            ).select_related('chanel')

            rank = (
                Chanel.objects
                    .filter(subscribers__gt=self.object.subscribers)
                    .aggregate(rank=Count('id') + 1)

            )
            context['rank'] = rank


            get_posts = Posts.objects.filter(chanel=self.object).select_related('chanel')

            text = Posts.objects.filter(chanel=self.object).values_list('text')

            repost_count = Posts.objects.filter(id_channel_forward_from=self.object.chanel_id, text__in=text).values(
                'text').annotate(
                repost_count=Count('id')
            )

            context['repost_count'] = repost_count

            count_repost = repost.count()
            count_mention = get_posts.filter(mention=True).count()
            count_all = count_repost + count_mention

            count_repost_week = repost.filter(created_at__gt=timezone.now() - timedelta(days=6)).count()
            count_mention_week = get_posts.filter(mention=True,
                                                  created_at__gt=timezone.now() - timedelta(days=6)).count()
            count_all_week = count_repost_week + count_mention_week

            count_repost_month = repost.filter(created_at__gt=timezone.now() - timedelta(days=29)).count()
            count_mention_month = get_posts.filter(mention=True,
                                                   created_at__gt=timezone.now() - timedelta(days=29)).count()
            count_all_month = count_repost_month + count_mention_month

            context['all_posts_new'] = all_posts_new

            context['count_all_week'] = count_all_week
            context['count_repost_week'] = count_repost_week
            context['count_mention_week'] = count_mention_week
            context['chanel_ads_new'] = chanel_ads_new

            context['count_all_month'] = count_all_month
            context['count_mention_month'] = count_mention_month
            context['count_repost_month'] = count_repost_month

            context['count_all'] = count_all
            context['count_repost'] = count_repost
            context['count_mention'] = count_mention

            context['repost'] = repost

            context['mention'] = mention
            context['mention_popup'] = Mentions.objects.filter(mentioned_channel=self.object).select_related(
                'post__chanel')

            context['chanel_ads'] = chanel_ads

            context['er'] = round(er, 1)
            if self.request.user.is_authenticated:
                context['like'] = Like.objects.filter(username=self.request.user.profile, chanel_name=self.object)

            context['er_daily'] = round(er_daily, 1)
            context['all_posts'] = all_posts
            context['subperhour'] = mention_chanel
            context['post_all'] = get_posts
            context['post_mention'] = get_posts.filter(mention=True)
            context['post'] = get_posts[:30]
            context['count'] = get_posts.filter(mention=True).count()
            context['subperday'] = SubPerday.objects.filter(chanel=self.object).annotate(
                er=F('subperday') / F('viewsperday') * 10)
            context['posts'] = Posts.objects.filter(chanel=self.object).values('created_at__date').annotate(
                count=Count('id'))
            context['posts_ads'] = Posts.objects.filter(chanel=self.object, mention=True).values(
                'created_at__date').annotate(
                count=Count('id'))
            context['form'] = LikeForm

            context['day'] = self.object.daily_subscribers
            context['week'] = self.object.weekly_subscribers
            context['month'] = self.object.weekly_monthy

            return context

        except Exception as e:
            context['limit'] =' Вы не можете смотреть эту страницу, поскольку достигли дневное ограничение тарифа.'
            return context





    def post(self, request, *args, **kwargs):
        form = LikeForm(request.POST)
        if form.is_valid():
            form.instance.username=self.request.user.profile
            form.instance.chanel_name=self.get_object()
            form.save()
            return redirect('like')


def search_view(request):
    query = request.GET.get('q', '')
    if query:
        results = Chanel_img.objects.filter(name__iregex=query)
    else:
        results = Chanel_img.objects.none()

    data = []
    for obj in results:
        data.append({
            'id': obj.id,
            'name': obj.name,
            'pictures': obj.pictures.url if obj.pictures else ''  # Use obj.pictures.url if it's an ImageField
        })

    return JsonResponse(data, safe=False)

class CreateChanel(LoginRequiredMixin,CreateView):
    model = Add_chanel
    form_class = AddChanelForm
    login_url = reverse_lazy('login_site')
    success_url = reverse_lazy('create')
    template_name = 'detail-statistics.html'

    def form_valid(self, form):
        # Associate the current user with the model instance
        if self.request.user.profile.telegram_id:
            form.instance.username = self.request.user.profile
            messages.success(self.request, "Proccessing")
            return super().form_valid(form)
        else:
            form.add_error(None, "User's profile is missing a Telegram ID.")
            return self.form_invalid(form)



class Search(LoginRequiredMixin,ListView):
    model = Chanel_img
    context_object_name = 'item'
    template_name = 'search.html'
    login_url = reverse_lazy('login_site')
    paginate_by = 8

    def get_queryset(self):

        search_query = self.request.GET.get('chanel_link')
        select_category = self.request.GET.get('selected_category')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        mention_from=self.request.GET.get('mention_from')
        mention_to=self.request.GET.get('mention_to')
        description=self.request.GET.get('description')
        queryset = Chanel_img.objects.all().prefetch_related('subperday')
        #print(views_from,views_to)
        #print(subscribers_from,subscribers_to)

        if search_query is not None and search_query.startswith("@"):
            search_query = search_query.strip("@")
            search_query = f'https://t.me/{search_query}'




        if select_category:
            queryset=queryset.filter(add_chanel__category__name=select_category)



        if search_query:
            queryset = queryset.filter(chanel_link__icontains=search_query)

        if chanel_name:
            queryset = queryset.filter(name__iregex=chanel_name)

        if description:
            queryset = queryset.filter(description__iregex=description)



        try:
            if mention_from and mention_to:
                queryset = queryset.filter(mentioned__range=[mention_from, mention_to])

            elif mention_from:
                queryset = queryset.filter(mentioned__gte=mention_from)
            elif mention_from:
                queryset = queryset.filter(mentioned__lte=mention_from)
        except:
            pass





        if views_from and views_to:
            queryset = queryset.filter(views__range=[views_from, views_to])

        elif views_from:
            queryset = queryset.filter(views__gte=views_from)
        elif views_to:
            queryset = queryset.filter(views__lte=views_to)





        if subscribers_from and subscribers_to:
            queryset = queryset.filter(subscribers__range=[subscribers_from, subscribers_to])

        elif subscribers_from:
            queryset = queryset.filter(subscribers__gte=subscribers_from)
        elif subscribers_to:
            queryset = queryset.filter(subscribers__lte=subscribers_to)





        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category']=Category_chanels.objects.all()
        context['lists'] = self.get_queryset().count()
        context['count'] = Chanel_img.objects.select_related('add_chanel').prefetch_related('add_chanel__cost_formats')


        return context

class TrackingPosts(LoginRequiredMixin,TemplateView):
    login_url = reverse_lazy('login_site')
    template_name = 'tracking-posts.html'

    def post(self, request, *args, **kwargs):
        action_type = request.POST.get('action_type')

        if action_type == 'connect_account':
            # Logic for clearing profile fields
            profile = request.user.profile
            fields_to_clear = ['notify_id', 'notify_bio', 'notify_name']
            for field in fields_to_clear:
                setattr(profile, field, None)
            profile.save(update_fields=fields_to_clear)

        elif action_type == 'create_notify':

            profile = request.user.profile
            word = request.POST.get('word')
            notify_type=request.POST.get('notify_type')
            if word:
                Notify.objects.create(profile=profile, word=word, Type_notify=notify_type,start=True)

        elif action_type == "delete_notify":

            profile = request.user.profile
            id=request.POST.get('delete')

            if id:
                Notify.objects.filter(profile=profile, id=id).delete()

        elif action_type=="start_notify":

            profile = request.user.profile
            id = request.POST.get('notify_id')


            if id:
                notify=Notify.objects.filter(profile=profile,id=id).first()
                notify.start = False
                notify.save(update_fields=['start'])

        elif action_type=="stop_notify":

            profile = request.user.profile
            id = request.POST.get('notify_id')

            if id:
                notify=Notify.objects.filter(profile=profile,id=id).first()
                notify.start = True
                notify.save(update_fields=['start'])


        return redirect(request.path)




    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notify']=Notify.objects.filter(profile=self.request.user.profile)


        return context


class Ad_posts(LoginRequiredMixin,ListView):
    template_name = 'ad-posts.html'
    model = Posts
    context_object_name = 'obj'
    paginate_by = 6
    login_url = reverse_lazy('login_site')

    def get_queryset(self):
        queryset=self.model.objects.all()
        mention=self.request.GET.get("mention")
        text=self.request.GET.get("text")
        chanel=self.request.GET.get('chanel')
        period=self.request.GET.get('period')
        view_from=self.request.GET.get('view_from')
        view_to=self.request.GET.get('view_to')



        if mention:
            queryset=queryset.filter(mentions_post__mentioned_channel__name__iregex=mention)

        if text:
            queryset=queryset.filter(text__icontains=text)

        if chanel:
            queryset=queryset.filter(chanel__name__iregex=chanel)

        if view_from and view_to:
            queryset=queryset.filter(view__range=[view_from,view_to])

        if period:
            try:
                period_from, period_to = period.split(" - ")
                queryset = queryset.filter(date__range=(period_from, period_to))
            except:
                pass



        return queryset




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_demo_user = not self.request.user.profile.is_premium

        # Handle pagination manually
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')

        if is_demo_user:
            limited_page_range = paginator.page_range[:5]
        else:
            limited_page_range = paginator.page_range

            # Pass the modified page range to the context
        context['page_range'] = limited_page_range





        context['count']=self.object_list.count()
        return context


class Ads_posts(LoginRequiredMixin,ListView):
    template_name = 'ads-posts.html'
    model = Posts
    context_object_name = 'obj'
    paginate_by = 6
    login_url = reverse_lazy('login_site')




    def get_queryset(self):
        queryset=self.model.objects.filter(mention=True)
        mention=self.request.GET.get("mention")
        text=self.request.GET.get("text")
        chanel=self.request.GET.get('chanel')
        period=self.request.GET.get('period')
        view_from=self.request.GET.get('view_from')
        view_to=self.request.GET.get('view_to')



        if mention:
            queryset=queryset.filter(mentions_post__mentioned_channel__name__iregex=mention)

        if text:
            queryset=queryset.filter(text__icontains=text)

        if chanel:
            queryset=queryset.filter(chanel__name__iregex=chanel)

        if view_from and view_to:
            queryset=queryset.filter(view__range=[view_from,view_to])

        if period:
            period_from, period_to = period.split(" - ")
            queryset = queryset.filter(date__range=(period_from, period_to))



        return queryset




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_demo_user = not self.request.user.profile.is_premium

        # Handle pagination manually
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')

        if is_demo_user:
            limited_page_range = paginator.page_range[:5]
        else:
            limited_page_range = paginator.page_range

            # Pass the modified page range to the context
        context['page_range'] = limited_page_range
        context['count']=self.object_list.count()
        return context


class Like_chanel(LoginRequiredMixin,ListView):
    template_name = 'like_chanel.html'
    login_url = reverse_lazy('login_site')
    context_object_name = 'item'
    model = Like
    paginate_by = 6

    def get_queryset(self):
        search_query = self.request.GET.get('chanel_link')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        cost_from = self.request.GET.get('cost_from')
        cost_to = self.request.GET.get('cost_to')
        like = Like.objects.filter(username__username=self.request.user)
        if search_query:
            like = like.filter(chanel_name__chanel_link__icontains=search_query)

        if chanel_name:
            like = like.filter(chanel_name__name__icontains=chanel_name)

            # If no search parameters are provided, return all objects

        if views_from and views_to:
            like = like.filter(chanel_name__views__range=[views_from, views_to])

        if subscribers_from and subscribers_to:
            like = like.filter(chanel_name__subscribers__range=[subscribers_from, subscribers_to])

        return like

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('chanel_link')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        cost_from = self.request.GET.get('cost_from')
        cost_to = self.request.GET.get('cost_to')
        note=self.object_list.filter(username__username=self.request.user).exclude(node='')


        if search_query:
            note = note.filter(chanel_name__chanel_link__icontains=search_query)

        if chanel_name:
            note = note.filter(chanel_name__name__icontains=chanel_name)

            # If no search parameters are provided, return all objects

        if views_from and views_to:
            note = note.filter(chanel_name__views__range=[views_from, views_to])

        if subscribers_from and subscribers_to:
            note = note.filter(chanel_name__subscribers__range=[subscribers_from, subscribers_to])



        context['count'] = self.get_queryset().count()
        context['node']=note
        context['count_node']=note.count()

        return context






def login_user(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request,'login.html')

def register(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, 'register.html')



def logout_view(request):
    logout(request)
    return redirect('main')


class Ref_View(View):

    def get(self, request, *args, **kwargs):
        referral_code = kwargs.get('referral_code')

        if referral_code:
            # Store the referral code in the session
            request.session['referral_code'] = referral_code
            request.session.set_expiry(3600)
            request.session.save()




        return redirect(reverse_lazy('main'))