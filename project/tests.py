from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import Project
from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Project
from django.urls import reverse
from rest_framework.exceptions import ErrorDetail


class ProjectModelTest(TestCase):

    def setUp(self):
        """
        Set up the test data.
        """
        self.project_data = {
            "name": "Test Project",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "capacity": 5,
        }
        # Create a project instance
        self.project = Project.objects.create(**self.project_data)

    def test_project_creation(self):
        """
        Test that a Project can be created successfully.
        """
        project = Project.objects.get(name="Test Project")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.start_date, date(2024, 1, 1))
        self.assertEqual(project.end_date, date(2024, 12, 31))
        self.assertEqual(project.capacity, 5)

    def test_project_string_representation(self):
        """
        Test the __str__ method of the Project model.
        """
        self.assertEqual(str(self.project), "Test Project")

    def test_invalid_project_name(self):
        """
        Test that the project name field is required and can't be blank.
        """
        with self.assertRaises(ValueError):
            Project.objects.create(name="", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), capacity=5)

    def test_project_name_max_length(self):
        """
        Test the max length constraint for the name field.
        """
        long_name = "A" * 256  # Name exceeding max length of 255
        with self.assertRaises(ValueError):
            Project.objects.create(name=long_name, start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), capacity=5)

    def test_project_capacity(self):
        """
        Test that the project capacity field accepts valid integer values.
        """
        project = Project.objects.create(name="Another Project", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), capacity=10)
        self.assertEqual(project.capacity, 10)

        with self.assertRaises(ValueError):
            Project.objects.create(name="Invalid Project", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31), capacity="invalid")

    def test_project_start_date(self):
        """
        Test that the start_date field accepts valid date values.
        """
        valid_start_date = date(2024, 1, 1)
        project = Project.objects.create(name="Valid Start Project", start_date=valid_start_date, end_date=date(2024, 12, 31), capacity=5)
        self.assertEqual(project.start_date, valid_start_date)

        with self.assertRaises(ValueError):
            Project.objects.create(name="Invalid Date Project", start_date="invalid", end_date=date(2024, 12, 31), capacity=5)

    def test_project_end_date(self):
        """
        Test that the end_date field accepts valid date values.
        """
        valid_end_date = date(2024, 12, 31)
        project = Project.objects.create(name="Valid End Project", start_date=date(2024, 1, 1), end_date=valid_end_date, capacity=5)
        self.assertEqual(project.end_date, valid_end_date)

        with self.assertRaises(ValueError):
            Project.objects.create(name="Invalid End Date Project", start_date=date(2024, 1, 1), end_date="invalid", capacity=5)





class ProjectListCreateViewTests(APITestCase):
    def setUp(self):
        # Set up initial data for testing
        self.url = reverse('project-list-create')  
        self.project_data = {
            "name": "Test Project",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "capacity": 5,
        }

    def test_get_projects(self):
        # Test GET request (list all projects)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No projects yet

    def test_create_project(self):
        # Test POST request (create a new project)
        response = self.client.post(self.url, self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.project_data['name'])
        # Ensure the project is saved to the database
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_invalid(self):
        # Test invalid POST request (missing required field)
        invalid_data = {"name": "Invalid Project"}  # Missing description
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)  # Description should be required





class ProjectDetailViewTests(APITestCase):
    def setUp(self):
        # Create a sample project to use in the tests
        self.project_data = {
            "name": "Test Project",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "capacity": 5,
        }
        self.url = reverse('project-detail', args=[self.project.id])

    def test_get_project(self):
        # Test GET request to retrieve a specific project
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.project.name)

    def test_update_project(self):
        # Test PUT request to update the project
        updated_data = {"name": "Updated Project"}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])
        
        # Ensure the project is updated in the database
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, updated_data['name'])

    def test_delete_project(self):
        # Test DELETE request to delete the project
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure the project is deleted from the database
        self.assertEqual(Project.objects.count(), 0)

    def test_delete_project_not_found(self):
        # Test DELETE request when project does not exist (404 error)
        non_existent_url = reverse('project-detail', args=[9999])  # Non-existent ID
        response = self.client.delete(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


