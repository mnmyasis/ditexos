from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services import parser


# Create your views here.
@login_required
def file_load(request):
    if request.method == 'POST' and request.FILES.get('file_crm'):
        file = request.FILES['file_crm']
        columns = parser.get_columns(file)
        return render(request, 'excel/load_file.html', {'require': columns})
    return render(request, 'excel/load_file.html', {})
