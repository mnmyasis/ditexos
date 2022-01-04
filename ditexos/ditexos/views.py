from django.shortcuts import render


def privacy_view(request):
    return render(request, 'privacy.html', {})