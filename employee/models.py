from django.db import models

# Create your models here.

class Employee(models.Model):
    FULL_TIME = 'FT'
    PART_TIME = 'PT'
    AVAILABILITY_CHOICES = [
        (FULL_TIME, 'Full-Time'),
        (PART_TIME, 'Part-Time')
    ]
    
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    availability = models.CharField(
        max_length=2,
        choices=AVAILABILITY_CHOICES,
        default=FULL_TIME
    )
    department = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_available_hours(self):
        if self.availability == self.FULL_TIME:
            return 40  # Full-time: 40 hours/week
        return 20  # Part-time: 20 hours/week
