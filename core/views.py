from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

def core(request):
    # Handle new task creation via POST
    if request.method == 'POST':
        task_title = request.POST.get('title')
        task_priority = request.POST.get('priority', 'low') 
        task_due_date = request.POST.get('due_date') or None # Set None if no date is picked  
        if task_title:
            Task.objects.create(title=task_title, priority=task_priority)
            due_date=task_due_date
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

 # Delete all tasks marked as completed
def clear_completed(request):
    Task.objects.filter(completed=True).delete()
    return redirect('core')

# View to edit an existing task
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.priority = request.POST.get('priority', 'low')
        task.due_date = request.POST.get('due_date') or None
        task.save()
        return redirect('core')

    return render(request, 'edit_task.html', {'task': task})