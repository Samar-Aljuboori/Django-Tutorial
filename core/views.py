
from django.shortcuts import render

def core(request):
    #   Data list
    context = {
        'user_name': 'Samar',
        'tasks': ['Setup Django', 'Understand URLs', 'Master Templates']
    }
    return render(request, 'index.html', context)