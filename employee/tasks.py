# myapp/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Employee
from project.models import Project

@shared_task
def notify_manager_allocation_exceeded(employee_id):
    employee = Employee.objects.get(id=employee_id)
    # if employee.allocation_percentage > 100:
    #     send_email_to_manager(employee, "Employee allocation exceeded 100%")

@shared_task
def notify_manager_project_capacity_exceeded(project_id):
    project = Project.objects.get(id=project_id)
    if project.capacity > project.capacity:
        send_email_to_manager(project, "Project capacity exceeded")

def send_email_to_manager(entity, message):
    # For testing, we use a mock email service (console email backend)
    send_mail(
        'Task Notification',
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['manager@example.com'],
        fail_silently=False,
    )
