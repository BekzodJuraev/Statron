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
 path('detail/<int:pk>',views.DetailChanel.as_view(), name='detail'),
 path('create/',views.CreateChanel.as_view(),name='create'),
 path('analysis/',views.AnalisChanel.as_view(),name='analysis'),
 path('mychanels/',views.MyChanels.as_view(),name='my_chanels'),
 path('search/',views.Search.as_view(),name='search'),
 path('tracking-posts/', views.TrackingPosts.as_view(), name='tracking'),
 path('posts/',views.Ad_posts.as_view(), name='posts'),
 path('note/',views.Like_chanel.as_view(),name='like'),
 path('report/',views.ReportView.as_view(),name='report'),
 path('',views.Main.as_view(),name='main')
]