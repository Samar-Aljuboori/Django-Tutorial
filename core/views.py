from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

def core(request):
    # Handle new task creation via POST
    if request.method == 'POST':
        task_title = request.POST.get('title')
        if task_title:
            Task.objects.create(title=task_title)
            return redirect('core')

    # Handle search functionality via GET query parameter
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = Task.objects.filter(title__icontains=search_query)
    else:
        tasks = Task.objects.all()

    context = {
        'tasks': tasks,
        'search_query': search_query,
    }
    return render(request, 'index.html', context)

def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    return redirect('core')

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('core')

# Detail view for a single task
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'task_detail.html', {'task': task})