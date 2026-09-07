from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Task, Category, Profile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from datetime import datetime

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
            messages.success(request, 'Task created successfully!')
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
    if status_filter in ['active', 'pending']:
        tasks = tasks.filter(completed=False)
    elif status_filter == 'completed':
        tasks = tasks.filter(completed=True)

    # Filter tasks by priority level
    if priority_filter in ['low', 'high', 'medium']:
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
    paginator = Paginator(tasks, 5)
    page_number = request.GET.get('page')

    try:
        tasks_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        tasks_page = paginator.get_page(1)
    except EmptyPage:
        tasks_page = paginator.get_page(paginator.num_pages)

    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    pending_tasks = Task.objects.filter(user=request.user, completed=False).count()

    # Context dictionary
    context = {
       'tasks': tasks_page,
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
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
            messages.success(request, 'Category added successfully!')
    return redirect('/')
# ==========================================
# 3. Edit Task View
# ==========================================
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.priority = request.POST.get('priority', 'low')
        task.due_date = request.POST.get('due_date') or None
        
        category_id = request.POST.get('category')
        if category_id:
            task.category = Category.objects.get(id=category_id, user=request.user)
        else:
            task.category = None
            
        task.save()
        messages.info(request, 'Task updated successfully!')
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
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.warning(request, 'Task deleted successfully!')
    return redirect('core')


# ==========================================
# 5. Clear Completed Tasks View
# ==========================================
@login_required
def clear_completed(request):
    # Delete all completed tasks for the active user only
    Task.objects.filter(user=request.user, completed=True).delete()
    return redirect('core')


# ==========================================
# 6. Task Detail View
# ==========================================
@login_required
def task_detail(request, pk):
    # Display single task detail page
    task = get_object_or_404(Task, id=pk, user=request.user)
    return render(request, 'task_detail.html', {'task': task})


# ==========================================
# 7. User Authentication Views (Login, Register, Logout)
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

@login_required
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    
    if task.completed:
        messages.success(request, 'Task marked as completed!')
    else:
        messages.info(request, 'Task marked as pending!')
        
    return redirect('core')


# ==========================================
# Main Settings Dashboard View: Renders the main settings hub
# ==========================================
@login_required
def settings_view(request):
    if request.method == 'POST':
        # Extract username and email data from POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if username:
            request.user.username = username
        if email:
            request.user.email = email
        request.user.save()
        
        # Handle user profile and avatar operations
        profile = request.user.profile
        
        # Check if profile picture removal was requested
        remove_avatar = request.POST.get('remove_avatar')
        if remove_avatar == 'true':
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
        
        # Check if a new profile picture file was uploaded
        elif 'profile_picture' in request.FILES:
            profile.avatar = request.FILES['profile_picture']
            profile.save()
            
        # Send a single consolidated success notification message
        messages.success(request, "Settings updated successfully.")
        return redirect('settings')
        
    return render(request, 'settings.html')
# ==========================================
# 8. User Profile View: Handle basic user info, avatar upload, and avatar removal
# ==========================================
@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        # 1. Update Username & Email
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if username:
            request.user.username = username
        if email:
            request.user.email = email
        request.user.save()

        # 2. Handle Avatar Upload
        if 'profile_picture' in request.FILES:
            if profile.avatar:
                profile.avatar.delete(save=False)  # حذف الصورة القديمة من الفولدر
            profile.avatar = request.FILES['profile_picture']
            profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('settings')

    return render(request, 'settings.html')


@login_required
def remove_avatar_view(request):
    profile = request.user.profile
    if profile.avatar:
        profile.avatar.delete(save=False)  
        profile.avatar = None            
        profile.save()
        messages.success(request, 'Profile picture removed successfully!')
    
    return redirect('settings')

# ==========================================
# 9. Security Settings View: Handle password changes securely
# ==========================================
@login_required
def security_settings_view(request):
    """
    Handle password updates in an independent, secure page.
    """
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            updated_user = password_form.save()
            update_session_auth_hash(request, updated_user)  # Keep user logged in after password change
            messages.success(request, "Password updated successfully!")
            return redirect('security_settings')
        else:
            messages.error(request, "Please correct the password errors below.")
    else:
        password_form = PasswordChangeForm(request.user)

    context = {
        'password_form': password_form,
    }
    return render(request, 'security_settings.html', context)


# ==========================================
# 10. User profile performancen view
# ==========================================

@login_required
def performance_view(request):
    """
    Handle the performance and analytics dashboard logic for the authenticated user.
    Calculates metrics such as total tasks, completed tasks, pending tasks, 
    productivity rate percentage, and retrieves recent tasks.
    """
    # Fetch tasks belonging exclusively to the currently logged-in user
    user_tasks = Task.objects.filter(user=request.user)
    
    # Calculate key metrics
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    pending_tasks = user_tasks.filter(completed=False).count()
    
    # Compute productivity rate percentage (handle division by zero safeguard)
    if total_tasks > 0:
        productivity_rate = int((completed_tasks / total_tasks) * 100)
    else:
        productivity_rate = 0
        
    # Retrieve the 5 most recent tasks created by the user
    recent_tasks = user_tasks.order_by('-created_at')[:5]

    # Prepare context dictionary to pass data to the template
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'productivity_rate': productivity_rate,
        'recent_tasks': recent_tasks,
    }
    
    return render(request, 'performance.html', context)

# ==========================================
# 11. User notifications view 
# ==========================================

@login_required
def notifications_view(request):
    """
    Handle the notifications preferences page logic for the authenticated user.
    """
    context = {}
    return render(request, 'notifications.html', context)


# ==========================================
# 12. Categories view 
# ==========================================

@login_required
def categories_view(request):
    """
    Handle task categories page logic, including saving new categories and listing existing ones.
    """
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        if category_name:
            # Create a new category linked to the logged-in user
            Category.objects.create(user=request.user, name=category_name.strip())
            messages.success(request, "Category added successfully!")
            return redirect('categories')

    # Fetch all categories belonging to the current logged-in user
    categories = Category.objects.filter(user=request.user)

    context = {
        'categories': categories,
    }
    return render(request, 'categories.html', context)


# ==========================================
# 13. Delete Category View: Removes a category from the database
# ==========================================
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.error(request, "Category deleted successfully!")
        return redirect('categories')
    
    return redirect('categories')


# ==========================================
# 14. Edit Category View: Updates an existing category name
# ==========================================
@login_required
def edit_category(request, category_id):
    """
    Update an existing category name using a dedicated edit page.
    """
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        new_name = request.POST.get('category_name')
        if new_name:
            category.name = new_name.strip()
            category.save()
            return redirect('categories')
            
    context = {'category': category}
    return render(request, 'edit_category.html', context)

# ==========================================
# 15.  Analytics View: Calculate task statistics and metrics for user
# ==========================================
@login_required
def analytics_view(request):
    """
    Handle analytics dashboard showing task completion rates, counts, and categories distribution.
    """
    user_tasks = Task.objects.filter(user=request.user)
    
    # Calculate statistics metrics using the correct field 'completed'
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count() # تم التعديل هنا لتتوافق مع حقول جدولك
    pending_tasks = total_tasks - completed_tasks
    
    # Calculate completion percentage
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': completion_rate,
    }
    return render(request, 'analytics.html', context)

# ==========================================
# 16. Calendar View: Renders the calendar page and user tasks
# ==========================================
@login_required(login_url='login')
def calendar_view(request):
    # Fetch all tasks belonging to the logged-in user
    user_tasks = Task.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'user_tasks': user_tasks,
        'categories': categories,
    }
    # Corrected path to match your templates folder structure
    return render(request, 'calendar.html', context)

# ==========================================
# 17. Add/Edit Calendar Task View: Handles task creation & updates from calendar modal
# ==========================================
@login_required(login_url='login')
def add_calendar_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        title = request.POST.get('title')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        category_name = request.POST.get('category')
        description = request.POST.get('description')

        # Parse date safely
        due_date = None
        if date_str:
            try:
                due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                due_date = None

        # Parse time safely
        task_time = None
        if time_str:
            try:
                task_time = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                task_time = None

        # Handle category association
        category_obj = None
        if category_name:
            category_obj, created = Category.objects.get_or_create(
                user=request.user, 
                name=category_name
            )

        if task_id:
            # Update existing task
            task = get_object_or_404(Task, id=task_id, user=request.user)
            task.title = title
            if due_date:
                task.due_date = due_date
            task.time = task_time
            task.category = category_obj
            task.description = description
            task.save()
        else:
            # Create new task
            Task.objects.create(
                user=request.user,
                title=title,
                due_date=due_date,
                time=task_time,
                category=category_obj,
                description=description,
                priority='medium'
            )

    return redirect('calendar_view')