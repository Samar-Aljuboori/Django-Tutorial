from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Task, Category, Profile
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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
# 8. User profile Views 
# ==========================================
@login_required
def profile_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        profile_pic = request.FILES.get('profile_picture')

        if username:
            request.user.username = username
            request.user.save()

        if profile_pic and hasattr(request.user, 'profile'):
            request.user.profile.avatar = profile_pic
            request.user.profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')  

    return render(request, 'profile.html')

# ==========================================
# 9. User profile settings view 
# ==========================================
@login_required
def settings_view(request):
    profile = request.user.profile 
    
    if request.method == 'POST':
        # 1. Check if the user is attempting to change their password
        password_form = PasswordChangeForm(request.user, request.POST)
        
        # We check if the user actually typed something in the old_password field
        is_changing_password = bool(request.POST.get('old_password'))
        
        if is_changing_password:
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
            else:
                # If password is wrong, stop everything and show error message
                messages.error(request, "Please correct the password errors below.")
                context = {'password_form': password_form}
                return render(request, 'settings.html', context)

        # 2. Update basic user info (username and email) only if password check passed (or wasn't attempted)
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # 3. Handle avatar removal
        remove_flag = request.POST.get('remove_avatar')
        if remove_flag == 'true':
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None
                profile.save()
        
        # 4. Handle avatar upload
        if 'profile_picture' in request.FILES:
            profile.avatar = request.FILES['profile_picture']
            profile.save()
            
        messages.success(request, "Settings updated successfully!")
        return redirect('settings')

    else:
        password_form = PasswordChangeForm(request.user)

    context = {
        'password_form': password_form,
    }
    return render(request, 'settings.html', context)

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
@login_required
def delete_category(request, category_id):
    """
    Delete a specific category by its ID if it belongs to the logged-in user.
    """
    category = get_object_or_404(Category, id=category_id, user=request.user)
    category.delete()
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