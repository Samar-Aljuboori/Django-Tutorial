from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Task, Category
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# ==========================================
# 1. Main Dashboard View (Task List, Search, Filter, Pagination & Creation)
# ==========================================
@login_required
def core(request):
    # Process new task creation via POST request
    if request.method == 'POST':
        task_title = request.POST.get('title')
        task_priority = request.POST.get('priority', 'low') 
        task_due_date = request.POST.get('due_date') or None
        category_id = request.POST.get('category')

        category = Category.objects.filter(id=category_id, user=request.user).first() if category_id else None

        if task_title:
            Task.objects.create(
                user=request.user,
                title=task_title, 
                priority=task_priority,
                due_date=task_due_date,
                category=category
            )
            return redirect('core')

    # Get URL parameters for search, filtering, and sorting
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority_filter', 'all')
    category_filter = request.GET.get('category_filter', 'all')
    sort_by = request.GET.get('sort', 'newest')

    # Fetch tasks belonging ONLY to the logged-in user
    tasks = Task.objects.filter(user=request.user)

    # Filter tasks by search query in title
    if search_query:
        tasks = tasks.filter(title__icontains=search_query)

    # Filter tasks by completion status
    if status_filter == 'active':
        tasks = tasks.filter(completed=False)
    elif status_filter == 'completed':
        tasks = tasks.filter(completed=True)

    # Filter tasks by priority level
    if priority_filter in ['low', 'high']:
        tasks = tasks.filter(priority=priority_filter)

    # Filter tasks by category ID
    if category_filter != 'all' and category_filter.isdigit():
        tasks = tasks.filter(category_id=int(category_filter))

    # Apply task sorting order
    if sort_by == 'due_date':
        tasks = tasks.order_by('due_date')
    elif sort_by == 'oldest':
        tasks = tasks.order_by('id')
    else:  # Default: newest first
        tasks = tasks.order_by('-id')

    # Fetch user's custom categories
    categories = Category.objects.filter(user=request.user)

    # Apply Pagination (Show 3 tasks per page)
    paginator = Paginator(tasks, 3)
    page_number = request.GET.get('page')

    try:
        tasks_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        tasks_page = paginator.get_page(1)
    except EmptyPage:
        tasks_page = paginator.get_page(paginator.num_pages)

    # Context dictionary
    context = {
        'tasks': tasks_page,  # Pass the paginated object!
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }
    return render(request, 'index.html', context)


# ==========================================
# 2. Add New Category View
# ==========================================
@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            # Check for existing category before creating a new one
            Category.objects.get_or_create(
                user=request.user,
                name__iexact=name,
                defaults={'name': name}
            )
    return redirect('/')
# ==========================================
# 3. Edit Task View
# ==========================================
@login_required
def edit_task(request, task_id):
    # Fetch task and categories for current authenticated user
    task = get_object_or_404(Task, id=task_id, user=request.user)
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.priority = request.POST.get('priority', 'low')
        task.due_date = request.POST.get('due_date') or None
        
        # Update category selection
        category_id = request.POST.get('category')
        if category_id:
            task.category = Category.objects.get(id=category_id, user=request.user)
        else:
            task.category = None
            
        task.save()
        return redirect('core')

    context = {
        'task': task,
        'categories': categories,
    }
    return render(request, 'edit_task.html', context)


# ==========================================
# 4. Delete Task View
# ==========================================
@login_required
def delete_task(request, pk):
    # Safely delete task owned by logged-in user
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.delete()
    return redirect('core')


# ==========================================
# 5. Toggle Complete Status View
# ==========================================
@login_required
def toggle_complete(request, pk):
    # Switch completion status (True/False)
    task = get_object_or_404(Task, id=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('core')


# ==========================================
# 6. Clear Completed Tasks View
# ==========================================
@login_required
def clear_completed(request):
    # Delete all completed tasks for the active user only
    Task.objects.filter(user=request.user, completed=True).delete()
    return redirect('core')


# ==========================================
# 7. Task Detail View
# ==========================================
@login_required
def task_detail(request, pk):
    # Display single task detail page
    task = get_object_or_404(Task, id=pk, user=request.user)
    return render(request, 'task_detail.html', {'task': task})


# ==========================================
# 8. User Authentication Views (Login, Register, Logout)
# ==========================================
def login_view(request):
    # Process user login form
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Start user session
            return redirect('core')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def register_view(request):
    # Process new user registration form
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()    # Save new user to database
            login(request, user)  # Auto-login after successful registration
            return redirect('core')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    # Terminate user session and redirect to login page
    logout(request)
    return redirect('login')

def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('core')

