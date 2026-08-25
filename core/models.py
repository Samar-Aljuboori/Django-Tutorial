from django.db import models
from django.utils import timezone  # Import Django's timezone utility
                                   # Task model to store user to-do items
from django.contrib.auth.models import User   # addd user login/ Authentication

class Task(models.Model):   # creat table
    title = models.CharField(max_length=200)      # create first column
    completed = models.BooleanField(default=False)      # create second column
    created_at = models.DateTimeField(auto_now_add=True)      # create third column
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('low', 'Low'),
    ]

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')   # 4th column
    due_date = models.DateField(null=True, blank=True)                       # 5th column
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

     # @property is a built-in Python decorator that turns this method into a dynamic attribute.
     # It allows accessing 'task.is_overdue' without parentheses (), which is required for Django HTML templates.
   
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 6th column 
   
    def __str__(self):            # The actual task name will appear.
        return self.title