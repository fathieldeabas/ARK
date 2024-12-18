from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.IntegerField()  # Number of team members for this project

    def __str__(self):
        return self.name
