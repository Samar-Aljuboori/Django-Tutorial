from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.core, name='core'),
     # New path for creating categories
    path('add-category/', views.add_category, name='add_category'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    # URL route for clearing completed tasks
    path('clear-completed/', views.clear_completed, name='clear_completed'),
    # URL route for editing a task
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
     # URL route for user login 
    path('login/', views.login_view, name='login'),
     # URL route for register new user  
    path('register/', views.register_view, name='register'),
     # URL route for user logout  
    path('logout/', views.logout_view, name='logout'),
     # URL route for user profile  
    path('profile/', views.profile_view, name='profile'),
    # URL route for user account settings 
    path('settings/', views.settings_view, name='settings'),
    # URL route for user account settings / performance 
    path('performance/', views.performance_view, name='performance'),
    # URL route for user account settings / notifications 
    path('notifications/', views.notifications_view, name='notifications'),
    # URL route for  categories
    path('categories/', views.categories_view, name='categories'),
     # URL route for  delete category
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
     # URL route for  edit category
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
     # URL route for  analytics
    path('analytics/', views.analytics_view, name='analytics'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)