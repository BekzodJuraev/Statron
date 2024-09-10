from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
 path('detail/<int:pk>',views.DetailChanel.as_view(), name='detail'),
 path('create/',views.CreateChanel.as_view(),name='create'),
 path('analysis/',views.AnalisChanel.as_view(),name='analysis'),
 path('mychanels/',views.MyChanels.as_view(),name='my_chanels'),
 path('search/',views.Search.as_view(),name='search'),
 path('search_view/', views.search_view, name='search_view'),
 path('tracking-posts/', views.TrackingPosts.as_view(), name='tracking'),
 path('posts/',views.Ad_posts.as_view(), name='posts'),
 path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
 path('telegram_auth/', views.telegram_auth, name='telegram_auth'),
 path('note/',views.Like_chanel.as_view(),name='like'),
 path('posts_ads/',views.Ads_posts.as_view(), name='posts_ads'),
 path('hello/',views.HelloWorldView.as_view(),name='hello'),
 path('',views.Main.as_view(),name='main'),
 path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
 path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
 path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
 path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]