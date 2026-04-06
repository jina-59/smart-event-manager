from django.contrib import admin
from django.urls import path
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'), 
    path('event/new/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_update, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Booking & My Page
    path('event/<int:pk>/book/', views.event_booking, name='event_booking'),
    path('my-page/', views.my_page, name='my_page'), # 📍 이 경로가 마이페이지 연결 고리입니다!
]