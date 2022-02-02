from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup', views.signup, name='signup'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('get/ajax/validate-username', views.validate_username, name='validate_username'),
    path('get/ajax/validate-email', views.validate_email, name='validate_email'),
]
