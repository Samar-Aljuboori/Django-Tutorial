from django.db import models

# Task model to store user to-do items
class Task(models.Model):   # creat table
    title = models.CharField(max_length=200)      # create first coulumn
    completed = models.BooleanField(default=False)      # create second coulumn
    created_at = models.DateTimeField(auto_now_add=True)      # create third coulumn

    def __str__(self):           # The actual task name will appear.
        return self.title