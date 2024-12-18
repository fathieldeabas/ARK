from django.db import models
from employee.models import Employee
from project.models import Project
# Create your models here.

class Allocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    allocation_percentage = models.FloatField()
    allocation_start_date = models.DateField()
    allocation_end_date = models.DateField()
    def __str__(self):
        return f'{self.employee.name} to {self.project.name}'

    class Meta:
        indexes = [
            models.Index(fields=['employee', 'project']),
            models.Index(fields=['allocation_start_date', 'allocation_end_date']),
        ]
