from django.db import models
from django.utils import timezone  # Import Django's timezone utility
# Task model to store user to-do items
class Task(models.Model):   # creat table
    title = models.CharField(max_length=200)      # create first column
    completed = models.BooleanField(default=False)      # create second column
    created_at = models.DateTimeField(auto_now_add=True)      # create third column
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('low', 'Low'),
    ]

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    due_date = models.DateField(null=True, blank=True)
    @property
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    def __str__(self):            # The actual task name will appear.
        return self.title