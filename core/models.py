from django.db import models
from django.contrib.auth.models import User

# ==========================================
# Category Model: Handles task categories (e.g., Work, Study)
# ==========================================
class Category(models.Model):
    # Foreign key linking the category to a specific user; deletes categories if the user is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Stores the name of the category (e.g., Work, Study, Shopping)
    name = models.CharField(max_length=50)

    # Meta class to fix the plural spelling in Django Admin panel ("Categories" instead of "Categorys")
    class Meta:
        verbose_name_plural = "Categories"

    # Returns the category name as a string representation in the admin panel
    def __str__(self):
        return self.name


# ==========================================
# Task Model: Handles individual user tasks
# ==========================================
class Task(models.Model):
    # Foreign key linking the task to the user who owns it; deletes tasks if the user is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)    
    # Stores the title or main text of the task
    title = models.CharField(max_length=200)
    
    # Stores the priority level of the task (e.g., low, medium, high) with 'low' as default
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('high', 'High'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')    
    # Optional due date for the task; allows null values in the database and empty forms
    due_date = models.DateField(null=True, blank=True)
    
    # Boolean flag to track if the task is completed (True) or pending (False)
    completed = models.BooleanField(default=False)
    
    # Optional relationship linking the task to a Category
    # SET_NULL: Keeps the task safe and sets its category to NULL if the category is deleted
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Automatically saves the exact date and time when the task was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Returns the task title as its string representation
    def __str__(self):
        return self.title