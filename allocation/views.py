from django.shortcuts import render

from allocation.tasks import Export_Employee_allocation_percentages
from .models import Allocation
# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from employee.models import Employee
from project.models import Project
from employee.serializers import EmployeeSerializer
from collections import defaultdict
from datetime import timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Allocation, Employee, Project
from .serializers import AllocationSerializer
from django.utils import timezone


class AllocationSuggestionViewSet(viewsets.ViewSet):
    def list(self, request, project_id):
        # 1. Fetch the project and all available employees.
        project = Project.objects.get(id=project_id)
        employees = Employee.objects.all()

        # 2. Filter employees based on their availability and current allocations.
        suggestions = self.suggest_allocation(employees, project)

        return Response(suggestions)

    def suggest_allocation(self, employees, project):
        suggestions = []
        for employee in employees:
            # Prioritize employees based on their availability, ensuring there is no overlap
            if self.can_allocate(employee, project):
                suggestions.append({
                    'employee': employee.name,
                    'available_hours': employee.get_available_hours(),
                })
        return suggestions

    def can_allocate(self, employee, project):
        # Check if employee's existing allocations overlap with project dates.
        allocations = Allocation.objects.filter(employee=employee)
        for allocation in allocations:
            if project.start_date < allocation.allocation_end_date and project.end_date > allocation.allocation_start_date:
                return False
        return True


from datetime import datetime

def check_overlap(start_date1, end_date1, start_date2, end_date2):
    return max(start_date1, start_date2) < min(end_date1, end_date2)





class BestAllocationSuggestionViewSet(viewsets.ViewSet):
    def list(self, request, project_id=None):
        project = Project.objects.get(id=project_id)
        employees = Employee.objects.all()
        
        # Get the best allocation suggestion based on the given criteria
        suggestions = self.suggest_best_allocation(employees, project)
        
        return Response(suggestions)

    def suggest_best_allocation(self, employees, project):
        # Step 1: Prioritize employees based on utilization
        employees_utilization = self.get_employees_utilization()
        employees_sorted_by_utilization = sorted(employees, key=lambda emp: employees_utilization.get(emp.id, 0))
        print("3333")
        print(employees_sorted_by_utilization)
        
        # Step 2: Find best matching employees
        allocation_suggestions = []
        project_capacity = project.capacity
        available_hours = project.capacity * 40  # Total hours that can be allocated in the project

        for employee in employees_sorted_by_utilization:
            if project_capacity == 0:
                break  # If project is full, stop suggesting

            # Step 3: Check if employee is eligible to be allocated to this project
            if self.can_allocate(employee, project):
                allocation_percentage = self.calculate_allocation_percentage(employee, project)
                
                # Step 4: Minimize gaps for part-time employees (allocate in contiguous blocks)
                if employee.availability == Employee.PART_TIME:
                    allocation_percentage = self.optimize_part_time_allocation(employee, project, allocation_percentage)

                allocation_suggestions.append({
                    'employee': employee.name,
                    'available_hours': employee.get_available_hours(),
                    'allocation_percentage': allocation_percentage,
                })
                
                project_capacity -= 1  # Reduce project capacity
        return allocation_suggestions

    def get_employees_utilization(self):
        """Fetch total hours allocated for each employee."""
        utilization = defaultdict(int)
        allocations = Allocation.objects.all()
        print("11")
        print(utilization)
        for allocation in allocations:
            utilization[allocation.employee.id] += allocation.allocation_percentage
        print("222")
        print(utilization)
        return utilization


    def can_allocate(self, employee, project):
        """Check if an employee has overlapping allocations with the project dates."""
        allocations = Allocation.objects.filter(employee=employee)
        for allocation in allocations:
            if project.start_date < allocation.allocation_end_date and project.end_date > allocation.allocation_start_date:
                return False
        return True

    def calculate_allocation_percentage(self, employee, project):
        """Calculate how much allocation an employee can take based on their availability."""
        available_hours = employee.get_available_hours()
        project_duration = (project.end_date - project.start_date).days // 7  # Duration in weeks
        hours_needed = project_duration * 40  # 40 hours per week for full-time projects
        allocation_percentage = min(100, (hours_needed / available_hours) * 100)
        return allocation_percentage

    def optimize_part_time_allocation(self, employee, project, allocation_percentage):
        """Minimize gaps for part-time employees (e.g., allocating continuous hours)."""
        # For part-time employees, ensure their allocation is as continuous as possible
        # We could refine this logic to check for more efficient continuous allocation
        if allocation_percentage < 100:
            allocation_percentage = 75  # Prefer continuous allocation
        return allocation_percentage




from django.conf import settings
import os
from django.http import (Http404, HttpResponse)


def download_exported(request):
    filename = request.GET.get("filename", None)
    if not filename:
        raise Http404
    file_path = "%s%s%s" % (settings.MEDIA_ROOT, "/documents/", filename)

    # prevent path traversal vulnerability
    real_path = os.path.realpath(file_path)
    base_dir = "%s%s" % (settings.MEDIA_ROOT, "/documents/")
    common_prefix = os.path.commonprefix([real_path, base_dir])
    if common_prefix != base_dir:
        raise Http404

    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(
                fh.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = "attachment; filename=%s" % filename
           
            return response
    else:
        raise Http404


from django.shortcuts import render
from django.http import JsonResponse
from .tasks import Export_Employee_allocation_percentages

def export_report_view(request):
    if request.method == 'POST':
        # Trigger the background task (Celery)
        Export_Employee_allocation_percentages.run()

            # Send a response indicating that the task has been triggered
        return JsonResponse({'status': 'success', 'message': 'The report is being generated. You will receive an email with the download link.'})

    



@api_view(['GET'])
def current_allocations(request):
    # Get parameters (employee or project)
    employee_id = request.query_params.get('employee_id', None)
    project_id = request.query_params.get('project_id', None)
    
    # Filter allocations based on employee or project
    if employee_id:
        allocations = Allocation.objects.filter(employee_id=employee_id)
    elif project_id:
        allocations = Allocation.objects.filter(project_id=project_id)
    else:
        return Response({"detail": "Either 'employee_id' or 'project_id' must be provided."}, status=400)
    
    # Serialize the data
    serializer = AllocationSerializer(allocations, many=True)
    return Response(serializer.data)




from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Count
from .models import Allocation, Employee, Project
from .serializers import AllocationSerializer
from django.core.exceptions import ValidationError
from django.utils import timezone

# Validation for overlapping allocations
def check_employee_availability(employee, start_date, end_date):
    overlapping_allocations = Allocation.objects.filter(
        employee=employee,
        allocation_start_date__lt=end_date,
        allocation_end_date__gt=start_date
    )
    if overlapping_allocations.exists():
        raise ValidationError("Employee is already allocated to another project during this period.")

# Validation for project capacity
def check_project_capacity(project):
    current_team_size = Allocation.objects.filter(project=project).count()
    if current_team_size >= project.capacity:
        raise ValidationError("Project capacity exceeded.")

# Add employee to a project
@api_view(['POST'])
def add_employee_to_project(request):
    employee_id = request.data.get('employee')
    project_id = request.data.get('project')
    allocation_percentage = request.data.get('allocation_percentage')
    allocation_start_date = request.data.get('allocation_start_date')
    allocation_end_date = request.data.get('allocation_end_date')

    try:
        employee = Employee.objects.get(id=employee_id)
        project = Project.objects.get(id=project_id)

        # Validate that the employee is available for the allocation period
        check_employee_availability(employee, allocation_start_date, allocation_end_date)

        # Validate that the project capacity is not exceeded
        check_project_capacity(project)

        # Create the allocation
        allocation = Allocation(
            employee=employee,
            project=project,
            allocation_percentage=allocation_percentage,
            allocation_start_date=allocation_start_date,
            allocation_end_date=allocation_end_date
        )
        allocation.save()

        return Response(AllocationSerializer(allocation).data, status=status.HTTP_201_CREATED)

    except Employee.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Remove employee from a project
@api_view(['DELETE'])
def remove_employee_from_project(request, allocation_id):
    try:
        allocation = Allocation.objects.get(id=allocation_id)
        allocation.delete()
        return Response({"detail": "Employee removed from the project successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Allocation.DoesNotExist:
        return Response({"detail": "Allocation not found."}, status=status.HTTP_404_NOT_FOUND)
