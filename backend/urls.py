from django.urls import path
from . import views


urlpatterns=[
 path('chanel/',views.ChanelAPI.as_view(),name="chanel"),
 path('update_cabinet/<int:pk>',views.UpdateCabinet.as_view(),name='updatecabinet'),
 path('login/', views.LoginAPIView.as_view(), name='login'),
 path('register/',views.RegistrationAPIView.as_view(),name='register'),
 path('login_site/', views.login_user, name='login_site'),
 path('register_site/', views.register, name='register_site'),
 path('logout/',views.logout_view,name='logout'),
 path('update_ajax',views.UpdateView.as_view(),name='update'),
 path('password_update/',views.UpdatePassword.as_view(),name='update_password'),
 path('',views.Main.as_view(),name='main')
]