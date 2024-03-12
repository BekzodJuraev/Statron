from django.shortcuts import render,redirect
from rest_framework import generics
from django.core.cache import cache
from datetime import date,timedelta
from .serializers import ChanelSerializer,LoginFormSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import Chanel,Profile,Add_chanel,Like
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View,ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import AddChanelForm
from django.db.models import Sum
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
        context['er']=round(er,1)
        context['er_daily'] = round(er_daily, 1)

        hourly_data = cache.get('hourly_data', [])

        old_subscribers=cache.get('old_subscribers',0)

        # Check if the last update date is different from today
        if self.object.last_update.date() != date.today():
            # Clear the 'hourly_data' list
            hourly_data.clear()

        # Check if the last update value is different

        if old_subscribers != 0:
            if self.object.last_update != cache.get('last_update', 0):
                # Update the cache with the new last_update value

                cache.set('last_update', self.object.last_update)
                difference=self.object.subscribers-old_subscribers
                cache.set('old_subscribers',self.object.subscribers)

                # Append a dictionary representing the data for this hour
                hourly_data.append({
                    'hourly': difference,
                    'subscribers': self.object.subscribers,
                    'last_update': self.object.last_update,
                })
        else:
            cache.set('old_subscribers',self.object.subscribers)



        # Store the updated 'hourly_data' list in the cache
        cache.set('hourly_data', hourly_data, timeout=24 * 60 * 60)

        context['hourly_data'] = hourly_data

        context['day'] = self.object.daily_subscribers
        context['week'] = self.object.weekly_subscribers
        context['month'] = self.object.weekly_monthy

        return context

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
    paginate_by = 1

    def get_queryset(self):
        search_query = self.request.GET.get('chanel_link')
        select_category = self.request.GET.get('selected_category')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        queryset = Chanel.objects.all()

        if search_query:
            queryset = queryset.filter(chanel_link__icontains=search_query)

        if chanel_name:
            queryset = queryset.filter(name__icontains=chanel_name)

            # If no search parameters are provided, return all objects

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
    paginate_by = 1

    def get_queryset(self):
        search_query = self.request.GET.get('chanel_link')
        chanel_name = self.request.GET.get('chanel_name')
        views_from = self.request.GET.get('views_from')
        views_to = self.request.GET.get('views_to')
        subscribers_from = self.request.GET.get('subscribers_from')
        subscribers_to = self.request.GET.get('subscribers_to')
        cost_from = self.request.GET.get('cost_from')
        cost_to = self.request.GET.get('cost_to')
        like = Like.objects.filter(username=self.request.user)
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
        context['count'] = self.get_queryset().count()
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