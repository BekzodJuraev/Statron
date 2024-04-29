from django.shortcuts import render,redirect
from rest_framework import generics
from django.db.models import Value,Case,When
from django.core.cache import cache
from django.db.models.functions import TruncHour
from datetime import date, timedelta, datetime
from .serializers import ChanelSerializer,LoginFormSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import Chanel,Profile,Add_chanel,Like,Posts,SubPerday,Subperhour
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
from django.db.models import Sum,Q,Count,F
from django.utils import timezone

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
    model = Chanel

    def get_context_data(self, *, object_list=None, **kwargs):

        context =super().get_context_data(**kwargs)
        chart_month = Posts.objects.filter(
            mention=True,
            created_at__gte=date.today() - timedelta(days=29)
        ).values('created_at__date').annotate(count=Count('id'))
        #print(chart_month)
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



















        #dict_monthly = {item['created_at__date'].strftime("%Y-%m-%d"): item['count'] for item in chart_month}










        context['chart_month']=chart_month
        context['daily_chart']=daily
        context['chart_three_month']=chart_three_month
        context['chart_six_month']=chart_six_month
        context['top_sub']=self.object_list.all().order_by('-subscribers')[:6]
        context['top_views'] =self.object_list.all().order_by('-views')
        context['posts_today']=Posts.objects.filter(mention=True,created_at__date=date.today()).count()
        context['total']=Posts.objects.all().count()
        context['mentioned'] =Posts.objects.filter(mention=True).count()
        return context

class UpdateCabinet(LoginRequiredMixin,DetailView):
    model = Profile
    login_url = reverse_lazy('login_site')
    success_url = reverse_lazy('updatecabinet')
    template_name = 'cabinet.html'
    context_object_name = 'item'


class UpdateView(LoginRequiredMixin,View):
    login_url = reverse_lazy('login_site')

    def post(self, request, *args, **kwargs):
        try:
            qiwi = request.POST.get('qiwi')
            photo = request.FILES.get('photo')
            instance_id = self.request.user.profile.id  # Assuming you pass the instance ID in the request

            # Validate data if needed

            if instance_id:
                # If instance_id is provided, update the existing instance
                instance = Profile.objects.get(pk=instance_id)
                if qiwi:
                    instance.qiwi = qiwi
                    instance.save()
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

class DetailChanel(DetailView):
    model = Chanel
    template_name = 'detail.html'
    context_object_name = 'item'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        er=(self.object.subscribers/self.object.views)*10
        er_daily = (self.object.daily_subscribers / self.object.views) * 10
        channel_link_suffix = self.object.chanel_link.split('/')[-1]

        mention_filter = (
                Q(text__icontains=f"@{channel_link_suffix}") |
                Q(text__icontains=f"t.me/{channel_link_suffix}") |
                Q(text__icontains=channel_link_suffix)
        )
        mention = Posts.objects.filter(mention=True).filter(mention_filter)
        repost = Posts.objects.filter(id_channel_forward_from=self.object.chanel_id)


        count_repost=repost.count()
        count_mention=mention.count()
        count_all=count_repost+count_mention

        count_repost_week = repost.filter(created_at__gt=timezone.now() - timedelta(days=6)).count()
        count_mention_week=mention.filter(created_at__gt=timezone.now() - timedelta(days=6)).count()
        count_all_week=count_repost_week+count_mention_week

        count_repost_month = repost.filter(created_at__gt=timezone.now() - timedelta(days=29)).count()
        count_mention_month= mention.filter(created_at__gt=timezone.now() - timedelta(days=29)).count()
        count_all_month = count_repost_month + count_mention_month





        context['count_all_week']=count_all_week
        context['count_repost_week'] = count_repost_week
        context['count_mention_week'] = count_mention_week

        context['count_all_month'] = count_all_month
        context['count_mention_month'] = count_mention_month
        context['count_repost_month'] = count_repost_month














        context['count_all'] = count_all
        context['count_repost'] = count_repost
        context['count_mention'] = count_mention
        context['mention'] = mention
        context['repost'] = repost

        context['er']=round(er,1)
        context['er_daily'] = round(er_daily, 1)
        context['subperhour'] = Subperhour.objects.filter(chanel=self.object)[:50]
        context['post'] = Posts.objects.filter(chanel=self.object)[:30]
        context['subperday']=SubPerday.objects.filter(chanel=self.object).annotate(er=F('subperday') / F('viewsperday'))
        context['posts']=Posts.objects.filter(chanel=self.object).values('created_at__date').annotate(count=Count('id'))
        context['posts_ads'] = Posts.objects.filter(chanel=self.object,mention=True).values('created_at__date').annotate(
            count=Count('id'))
        context['form']=LikeForm







        context['day'] = self.object.daily_subscribers
        context['week'] = self.object.weekly_subscribers
        context['month'] = self.object.weekly_monthy

        return context

    def post(self, request, *args, **kwargs):
        form = LikeForm(request.POST)
        if form.is_valid():
            form.instance.username=self.request.user.profile
            form.instance.chanel_name=self.get_object()
            form.save()
            return redirect('like')




class CreateChanel(LoginRequiredMixin,CreateView):
    model = Add_chanel
    form_class = AddChanelForm
    login_url = reverse_lazy('login_site')
    success_url = reverse_lazy('create')
    template_name = 'detail-statistics.html'

    def form_valid(self, form):
        # Associate the current user with the model instance
        form.instance.username = self.request.user.profile
        return super().form_valid(form)
class AnalisChanel(LoginRequiredMixin,TemplateView):
    template_name = 'audience-analysis.html'
    login_url = reverse_lazy('login_site')



class MyChanels(LoginRequiredMixin,TemplateView):
    template_name = 'my-channels.html'
    login_url = reverse_lazy('login_site')

class Search(ListView):
    model = Chanel
    context_object_name = 'item'
    template_name = 'search.html'
    paginate_by = 8

    def get_queryset(self):
        search_query = self.request.GET.get('chanel_link')
        #select_category = self.request.GET.get('selected_category')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        mention_from=self.request.GET.get('mention_from')
        mention_to=self.request.GET.get('mention_to')
        description=self.request.GET.get('description')
        queryset = Chanel.objects.all()

        if search_query:
            queryset = queryset.filter(chanel_link__icontains=search_query)

        if chanel_name:
            queryset = queryset.filter(name__icontains=chanel_name)

        if description:
            queryset = queryset.filter(description__icontains=description)


        if mention_from and mention_to:
            queryset=queryset.filter(mentioned__range=[mention_from,mention_to])



        if views_from and views_to:
            queryset = queryset.filter(views__range=[views_from, views_to])

        if subscribers_from and subscribers_to:
            queryset = queryset.filter(subscribers__range=[subscribers_from, subscribers_to])



        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lists'] = self.get_queryset().count()
        context['count'] = Chanel.objects.select_related('add_chanel').prefetch_related('add_chanel__cost_formats')


        return context

class TrackingPosts(TemplateView):
    template_name = 'tracking-posts.html'

class Ad_posts(LoginRequiredMixin,TemplateView):
    template_name = 'ad-posts.html'
    login_url = reverse_lazy('login_site')


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




class ReportView(View):
    template_name = 'report.html'

    def get(self, request, *args, **kwargs):
        # Get daily report for each channel
        daily_reports = self.get_report('day')

        # Get weekly report for each channel
        weekly_reports = self.get_report('week')

        # Get monthly report for each channel
        monthly_reports = self.get_report('month')

        context = {
            'daily_reports': daily_reports,
            'weekly_reports': weekly_reports,
            'monthly_reports': monthly_reports,
        }

        return render(request, self.template_name, context)

    def get_report(self, period):
        now = timezone.now()

        if period == 'day':
            start_date = now - timedelta(days=1)
        elif period == 'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now - timedelta(days=30)  # Approximating a month

        end_date = now

        reports = []
        channels = Chanel.objects.all()

        for channel in channels:
            queryset = Chanel.objects.filter(
                update_date__range=(start_date, end_date),
                id=channel.id
            )

            report = {
                'channel': channel,
                'total_subscribers': queryset.aggregate(Sum('subscribers'))['subscribers__sum'] or 0,
                'total_views': queryset.aggregate(Sum('views'))['views__sum'] or 0,
                'total_channels': queryset.count(),
            }

            reports.append(report)

        return reports

def login_user(request):
    return render(request,'login.html')

def register(request):
    logout(request)
    return render(request,'register.html')



def logout_view(request):
    logout(request)
    return redirect('main')