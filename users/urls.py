from django.urls import path, include
import django.contrib.auth.views as auth_views
from django.urls import reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/',
        auth_views.PasswordResetView.as_view(
        template_name="registration/password_reset_form.html",
        email_template_name="registration/password_reset_email.html",
        success_url=reverse_lazy('users:password_reset_done'),
    ),
    name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('users:password_reset_complete'),
    ),
    name='password_reset_confirm'),

    path('signup', views.signup, name='signup'),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('get/ajax/validate-username', views.validate_username, name='validate_username'),
    path('get/ajax/validate-email', views.validate_email, name='validate_email'),
]
