from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
import re
# Create your views here.
from .models import CustomUser
from calltouch.models import ApiToken


def login_view(request):
    error = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('dashboard:dash_board_page')
            else:
                error['error'] = 'Учетная зпись неактивна'
        else:
            error['error'] = 'Неверный логин или пароль'
    return render(request, 'accounts/login.html', error)


def register(request):
    error = {}
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            return redirect('accounts:login')
        else:
            error['error'] = 'Некорректно заполнена форма'
    return render(request, 'accounts/register.html', error)


def recovery(request):
    return render(request, 'accounts/password.html', {})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_form(request):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=request.user.pk)
    if request.method == 'POST':
        google_ads_id = request.POST.get('google_ads_id')
        google_ads_id = re.sub(r'-', '', google_ads_id)
        user.google_customer = google_ads_id
        user.save()
        if request.POST.get('calltouch_site_id') and request.POST.get('calltouch_token'):
            site_id = request.POST.get('calltouch_site_id')
            token = request.POST.get('calltouch_token')
            obj, created = ApiToken.objects.update_or_create(
                user=user,
                token=token,
                site_id=site_id,
                defaults={
                    'user': user,
                    'token': token,
                    'site_id': site_id
                }
            )
            obj.set_periodic_task('calltouch_reports')
        return redirect('accounts:profile_form')
    calltouch = ApiToken.objects.filter(user=user).first()
    return render(request, 'accounts/profile.html', {'calltouch': calltouch})