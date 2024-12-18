from django.test import TestCase
from project.models import Project
from employee.models import Employee
from .models import Allocation
from datetime import date
from rest_framework.test import APIClient
from django.urls import reverse
from.views import AllocationSuggestionViewSet

from django.http import HttpResponse
from django.conf import settings
import os
from unittest.mock import patch
from io import BytesIO


# Create your tests here.
class AllocationModelTests(TestCase):

    def setUp(self):
        """
        This method runs before each test to set up any necessary data.
        """
        # Create an employee
        self.employee = Employee.objects.create(
            name="John Doe",
            position="Software Engineer",
            availability=Employee.FULL_TIME,
            department="Engineering"
        )

        # Create a project
        self.project = Project.objects.create(
            name="Project A",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            capacity=5
        )

        # Create an allocation
        self.allocation = Allocation.objects.create(
            employee=self.employee,
            project=self.project,
            allocation_percentage=75.0,
            allocation_start_date=date(2023, 1, 1),
            allocation_end_date=date(2023, 12, 31)
        )

    def test_allocation_str_method(self):
        """
        Test the __str__ method of the Allocation model.
        """
        self.assertEqual(str(self.allocation), 'John Doe to Project A')

    def test_allocation_fields(self):
        """
        Test that the Allocation model fields are correctly set.
        """
        # Test the employee and project relationships
        self.assertEqual(self.allocation.employee, self.employee)
        self.assertEqual(self.allocation.project, self.project)

        # Test the allocation percentage and dates
        self.assertEqual(self.allocation.allocation_percentage, 75.0)
        self.assertEqual(self.allocation.allocation_start_date, date(2023, 1, 1))
        self.assertEqual(self.allocation.allocation_end_date, date(2023, 12, 31))

    def test_allocation_percentage_range(self):
        """
        Test that the allocation percentage is a valid number between 0 and 100.
        """
        # Valid allocation percentage
        self.allocation.allocation_percentage = 100.0
        self.allocation.save()
        self.assertEqual(self.allocation.allocation_percentage, 100.0)

        # Invalid allocation percentage (greater than 100)
        with self.assertRaises(ValueError):
            self.allocation.allocation_percentage = 150.0
            self.allocation.save()

        # Invalid allocation percentage (less than 0)
        with self.assertRaises(ValueError):
            self.allocation.allocation_percentage = -10.0
            self.allocation.save()

    def test_allocation_date_range(self):
        """
        Test that the allocation start date is before the end date.
        """
        # Valid date range
        self.allocation.allocation_start_date = date(2023, 1, 1)
        self.allocation.allocation_end_date = date(2023, 12, 31)
        self.allocation.save()
        self.assertTrue(self.allocation.allocation_start_date < self.allocation.allocation_end_date)

        # Invalid date range (start date after end date)
        with self.assertRaises(ValueError):
            self.allocation.allocation_start_date = date(2023, 12, 31)
            self.allocation.allocation_end_date = date(2023, 1, 1)
            self.allocation.save()

    def test_allocation_indexes(self):
        """
        Test the indexes on the Allocation model (checking that the fields are indexed).
        """
        # Ensure that the model has the correct indexes
        index_fields = [index.fields for index in Allocation._meta.indexes]
        self.assertIn(['employee', 'project'], index_fields)
        self.assertIn(['allocation_start_date', 'allocation_end_date'], index_fields)




class AllocationSuggestionViewSetTests(TestCase):

    def setUp(self):
        """
        This method runs before each test to set up any necessary data.
        """
        # Create a project
        self.project = Project.objects.create(
            name="Project A",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            capacity=5
        )

        # Create employees
        self.employee1 = Employee.objects.create(
            name="Employee 1",
            position="Software Engineer",
            availability=Employee.FULL_TIME,
            department="Engineering"
        )

        self.employee2 = Employee.objects.create(
            name="Employee 2",
            position="Data Scientist",
            availability=Employee.PART_TIME,
            department="Data Science"
        )

        self.employee3 = Employee.objects.create(
            name="Employee 3",
            position="UX Designer",
            availability=Employee.FULL_TIME,
            department="Design"
        )

        # Create allocations for employee 1 and 2 (simulating overlapping dates with project)
        self.allocation1 = Allocation.objects.create(
            employee=self.employee1,
            project=self.project,
            allocation_percentage=50.0,
            allocation_start_date=date(2024, 1, 1),
            allocation_end_date=date(2024, 3, 31)
        )

        self.allocation2 = Allocation.objects.create(
            employee=self.employee2,
            project=self.project,
            allocation_percentage=50.0,
            allocation_start_date=date(2024, 4, 1),
            allocation_end_date=date(2024, 6, 30)
        )

        # Set up the APIClient
        self.client = APIClient()

    def test_list_allocation_suggestions(self):
        """
        Test that the allocation suggestions are returned correctly.
        The employee1 should not be suggested due to overlapping allocations,
        employee2 should be suggested as their availability matches the project duration.
        """
        # Get allocation suggestions for the project
        url = reverse('allocation-suggestions', kwargs={'project_id': self.project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        
        # Check that employee1 is excluded because of allocation overlap
        suggestions = response.json()
        employee_names = [suggestion['employee'] for suggestion in suggestions]
        self.assertNotIn("Employee 1", employee_names)

        # Check that employee2 is included (as they have availability during the project period)
        self.assertIn("Employee 2", employee_names)

    def test_suggest_allocation(self):
        """
        Test the suggestion logic. Check that employee3 is suggested even though they have no allocations.
        """
        suggestions = self.client.get(reverse('allocation-suggestions', kwargs={'project_id': self.project.id})).json()
        employee_names = [suggestion['employee'] for suggestion in suggestions]

        self.assertIn("Employee 3", employee_names)  # Employee 3 has no current allocation, should be suggested.
    
    def test_can_allocate_true(self):
        """
        Test that `can_allocate` correctly returns True when no overlapping allocation exists.
        """
        # Employee 3 should be able to be allocated to the project (no current allocations)
        can_allocate = AllocationSuggestionViewSet().can_allocate(self.employee3, self.project)
        self.assertTrue(can_allocate)

    def test_can_allocate_false(self):
        """
        Test that `can_allocate` correctly returns False when there is an overlapping allocation.
        """
        # Employee 1 should NOT be able to be allocated to the project (due to overlapping allocation)
        can_allocate = AllocationSuggestionViewSet().can_allocate(self.employee1, self.project)
        self.assertFalse(can_allocate)

    def test_empty_allocation_suggestions(self):
        """
        Test that when no employees are available for allocation, an empty list is returned.
        """
        # Create a project with a date range where no employees can be allocated
        project = Project.objects.create(
            name="Project B",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 12, 31),
            capacity=5
        )

        # Get allocation suggestions for the new project
        url = reverse('allocation-suggestions', kwargs={'project_id': project.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])  # No available employees



class DownloadExportedTests(TestCase):
    
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_download_exported_no_filename(self, mock_open, mock_exists):
        """
        Test that Http404 is raised when no filename is provided in the request.
        """
        url = reverse('download_exported')
        response = self.client.get(url)  # No filename in the query string
        
        self.assertEqual(response.status_code, 404)

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_download_exported_path_traversal(self, mock_open, mock_exists):
        """
        Test that path traversal is prevented by ensuring the file path is within the allowed directory.
        """
        filename = "../outside_file.xlsx"  # Malicious filename attempting path traversal
        url = reverse('download_exported') + f"?filename={filename}"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)  # Should return 404 due to path traversal attempt
    
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_download_exported_file_exists(self, mock_open, mock_exists):
        """
        Test that the file is downloaded when it exists.
        """
        filename = "valid_file.xlsx"
        file_path = os.path.join(settings.MEDIA_ROOT, "documents", filename)
        
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Mock the open() function to return some file content
        mock_file = BytesIO(b"some fake content")
        mock_open.return_value.__enter__.return_value = mock_file

        url = reverse('download_exported') + f"?filename={filename}"
        response = self.client.get(url)
        
        # Check the response status and content type
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename={filename}')
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # Ensure the file content is returned
        self.assertEqual(response.content, b"some fake content")

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_download_exported_file_does_not_exist(self, mock_open, mock_exists):
        """
        Test that Http404 is raised when the file does not exist.
        """
        filename = "non_existent_file.xlsx"
        file_path = os.path.join(settings.MEDIA_ROOT, "documents", filename)
        
        # Mock os.path.exists to return False, simulating file not found
        mock_exists.return_value = False
        
        url = reverse('download_exported') + f"?filename={filename}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)  # Should return 404 as the file doesn't exist




class ExportReportViewTests(TestCase):

    @patch("your_app.views.Export_Employee_allocation_percentages.run")
    def test_export_report_view_post(self, mock_export_task):
        """
        Test that the background task is triggered when a POST request is made.
        """
        url = reverse('export_report')  # Replace with the actual URL name of the view
        
        # Send a POST request to the export_report_view
        response = self.client.post(url)
        
        # Check that the Celery task was triggered
        mock_export_task.assert_called_once()  # Verify that run() was called once
        
        # Check the response status and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'The report is being generated. You will receive an email with the download link.'})

    def test_export_report_view_get(self):
        """
        Test that a GET request to the export_report_view returns a 405 Method Not Allowed.
        """
        url = reverse('export_report')  # Replace with the actual URL name of the view
        
        # Send a GET request to the export_report_view
        response = self.client.get(url)
        
        # Check that the response status is 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['detail'], 'Method "GET" not allowed.')

