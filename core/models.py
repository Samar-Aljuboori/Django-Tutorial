from django.db import models
from django.utils import timezone  # Utility for handling timezone-aware dates and times
from django.contrib.auth.models import User  # Built-in User model for authentication


# ==========================================
# Category Model: Stores custom user categories (e.g., Work, Study)
# ==========================================
class Category(models.Model):
    # Links the category to a specific user; deletes categories if the user is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Category name field (e.g., Work, Study, Shopping)
    name = models.CharField(max_length=50)

    # Meta options to fix the plural spelling in Django Admin ("Categories" instead of "Categorys")
    class Meta:
        verbose_name_plural = "Categories"

    # String representation showing the category name in admin and queries
    def __str__(self):
        return self.name


# ==========================================
# Task Model: Stores individual user tasks
# ==========================================
class Task(models.Model):
    # 1st column: Title or main description of the task
    title = models.CharField(max_length=200)

    # 2nd column: Completion status (False = active, True = completed)
    completed = models.BooleanField(default=False)

    # 3rd column: Creation timestamp (automatically set on creation)
    created_at = models.DateTimeField(auto_now_add=True)

    # Predefined priority choices
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('low', 'Low'),
    ]

    # 4th column: Priority level with 'low' set as default
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')

    # 5th column: Optional due date for the task
    due_date = models.DateField(null=True, blank=True)

    # 6th column: Links task to the logged-in user who created it
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # 7th column: Optional relationship linking the task to a Category
    # SET_NULL: If the category is deleted, the task remains safe and category becomes NULL
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    # Dynamic property decorator converting this method into an attribute (accessible as 'task.is_overdue' in HTML templates)
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    # Returns the actual task title when printed in python shell or admin
    def __str__(self):
        return self.title