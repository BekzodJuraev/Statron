from django.urls import path
from . import views


urlpatterns=[
 path('chanel/',views.ChanelAPI.as_view(),name="chanel"),
 path('login/', views.LoginAPIView.as_view(), name='login'),
 path('register/',views.RegistrationAPIView.as_view(),name='register'),
 path('login_site/', views.login, name='login_site'),
 path('register_site/', views.register, name='register_site'),
 path('',views.index,name='main')
]