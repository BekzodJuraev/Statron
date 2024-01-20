from django.urls import path
from . import views


urlpatterns=[
 path('chanel/',views.ChanelAPI.as_view(),name="chanel"),
 path('login/', views.LoginAPIView.as_view(), name='login'),
 path('register/',views.RegistrationAPIView.as_view(),name='register'),
 path('',views.index,name='main')
]