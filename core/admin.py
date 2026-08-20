from django.contrib import admin
from .models import Task

# Register Task model to manage it in the Django admin interface
admin.site.register(Task)