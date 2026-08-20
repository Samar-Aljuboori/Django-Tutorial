from django.shortcuts import render
from .models import Task

def core(request):
    # Retrieve all task objects from the SQLite database
    tasks = Task.objects.all()
    
    # Prepare data dictionary to pass to the HTML template
    context = {
        'tasks': tasks
    }
    
    # Render and return the HTML response with database content
    return render(request, 'index.html', context)