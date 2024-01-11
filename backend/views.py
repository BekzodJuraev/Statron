from django.shortcuts import render
from rest_framework import generics
from .serializers import ChanelSerializer,LoginFormSerializer,RegistrationSerializer
from rest_framework.views import APIView
from .models import Chanel
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
# Create your views here.

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
                return Response({'detail': 'Invalid login credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'detail': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)
class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Add any additional logic here, such as sending a welcome email
        return Response({'detail': 'Registration successful'}, status=status.HTTP_201_CREATED)
def index(requests):
    return render(requests,'index.html')