from django.urls import path
from . import views


urlpatterns=[
 path('api/',views.ChanelAPI.as_view()),
 path('login/', views.LoginAPIView.as_view(), name='login'),
 path('register/',views.RegistrationAPIView.as_view(),name='register'),
 path('',views.index,name='main')
]