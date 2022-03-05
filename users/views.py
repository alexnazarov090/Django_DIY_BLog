from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from blog.models import User
from .forms import SignUpForm
from .tokens import account_activation_token


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user.is_active = False
            user.save()
            if user.is_authenticated:
                current_site = get_current_site(request)
                subject = 'Activate Your Blog Account'
                message = render_to_string('registration/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)
                return redirect(reverse('users:account_activation_sent'))
            return redirect(reverse('blog:index'))
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect(reverse('blog:index'))
    else:
        return render(request, 'registration/account_activation_invalid.html')


def validate_username(request):
    """
    A view to check username
    """
    if request.is_ajax and request.method == 'GET':
        username = request.GET.get('username')
        data = {}.fromkeys(('valid', 'error_message'))
        data['valid'] = True

        if User.objects.filter(username__iexact=username).exists():
            data['valid'], data['error_message'] = False, 'A user with this username already exists!'

        return JsonResponse(data, status=200)


def validate_email(request):
    """
    A view to check email address
    """
    if request.is_ajax and request.method == 'GET':
        email = request.GET.get('email')
        data = {}.fromkeys(('valid', 'error_message'))
        data['valid'] = True

        if User.objects.filter(email__iexact=email).exists():
            data['valid'], data['error_message'] = False, 'A user with this email already exists!'

        return JsonResponse(data, status=200)


def manage_account(request):
    return render(request, 'registration/manage_account.html')


class UserUpdate(LoginRequiredMixin, UpdateView):
    """
    A form to update a blogger profile
    """
    model = User
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'registration/update_user.html'

    def get_success_url(self):
        user = User.objects.get(pk=self.kwargs['pk'])
        if user.is_blogger:
            return reverse('blog:blogger-profile', kwargs={'pk': user.blogauthor.pk})
        else:
            return reverse('users:manage_account')


class UserDelete(LoginRequiredMixin, DeleteView):
    """
    A view to delete a user account
    """
    model = User
    template_name = 'registration/delete_user.html'
    success_url = reverse_lazy('blog:index')
