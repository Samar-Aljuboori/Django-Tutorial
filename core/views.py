from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

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


  # User Login Page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})



# 1. User registration view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()        # Save the new user to the database
            login(request, user)       # Automatically log the user in after registration
            return redirect('core')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


# 2. User logout view
def logout_view(request):
    logout(request)                    # Clear the session and log out the user
    return redirect('login')           # Redirect to the login page


# 1. Edit Task View
@login_required
def edit_task(request, pk):
    # Make sure the task belongs to the logged-in user
    task = get_object_or_404(Task, id=pk, user=request.user)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.priority = request.POST.get('priority', 'low')
        task.due_date = request.POST.get('due_date') or None
        task.save()
        return redirect('core')

    return render(request, 'edit_task.html', {'task': task})


# 2. Delete Task View
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.delete()
    return redirect('core')


# 3. Toggle Complete Status View
@login_required
def toggle_complete(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('core')


# 4. Clear Completed Tasks View
@login_required
def clear_completed(request):
    # Delete completed tasks ONLY for the logged-in user
    Task.objects.filter(user=request.user, completed=True).delete()
    return redirect('core')