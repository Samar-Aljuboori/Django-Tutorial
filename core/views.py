from django.shortcuts import render

def core(request):
    return render(request, 'index.html')