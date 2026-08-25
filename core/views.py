from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth.decorators import login_required

@login_required
def core(request):
    # 1. Handle new task creation via POST
    if request.method == 'POST':
        task_title = request.POST.get('title')
        task_priority = request.POST.get('priority', 'low') 
        task_due_date = request.POST.get('due_date') or None # Set None if no date is picked 

        if task_title:
            Task.objects.create(
                user=request.user,
                title=task_title, 
                priority=task_priority,
                due_date=task_due_date
            )
            return redirect('core')

    # 2. Get query parameters for search, filtering, and sorting
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority_filter', 'all')
    sort_by = request.GET.get('sort', 'newest')

    
    tasks = Task.objects.filter(user=request.user)

    # Apply search filter
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Apply status filter
    if status_filter == 'active':
        tasks = tasks.filter(completed=False)
    elif status_filter == 'completed':
        tasks = tasks.filter(completed=True)

    # Apply priority filter
    if priority_filter in ['low', 'high']:
        tasks = tasks.filter(priority=priority_filter)

    # Apply sorting
    if sort_by == 'due_date':
        tasks = tasks.order_by('due_date')
    elif sort_by == 'oldest':
        tasks = tasks.order_by('id')
    else:  # Default to newest first
        tasks = tasks.order_by('-id')

    context = {
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'sort_by': sort_by,
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