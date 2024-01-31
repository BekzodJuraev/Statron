from django.shortcuts import render,redirect
from rest_framework import generics
from .serializers import ChanelSerializer,LoginFormSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import Chanel,Profile,Add_chanel
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

def login_user(request):
    return render(request,'login.html')

def register(request):
    logout(request)
    return render(request,'register.html')



def logout_view(request):
    logout(request)
    return redirect('main')