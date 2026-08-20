from django.shortcuts import render, redirect
from .models import Task

def core(request):
    # Handle new task submission via POST request
    if request.method == 'POST':
        task_title = request.POST.get('title')
        if task_title:
            Task.objects.create(title=task_title)
            return redirect('core')

    # Fetch all tasks from the database
    tasks = Task.objects.all()
    context = {
        'tasks': tasks
    }
    return render(request, 'index.html', context)