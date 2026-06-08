from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('events/', views.view_all, name='view_all'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'), 
    path('event/new/', views.event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.event_update, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),


    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Booking & My Page
    path('event/<int:pk>/book/', views.event_booking, name='event_booking'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-page/', views.my_page, name='my_page'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('review/<int:booking_id>/', views.create_review, name='create_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('profile/', views.profile_settings, name='profile_settings'),

    # Delete Account
    path('delete-account/', views.delete_account, name='delete_account'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    path('search/', views.event_search, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)