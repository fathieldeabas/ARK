from django.test import TestCase
from .models import Employee


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Employee
from employee.serializers import EmployeeSerializer

# Create your tests here.
class EmployeeModelTests(TestCase):

    def setUp(self):
        """
        This method runs before every test. 
        We create a couple of Employee instances for testing.
        """
        self.full_time_employee = Employee.objects.create(
            name="John Doe",
            position="Software Engineer",
            availability=Employee.FULL_TIME,
            department="Engineering"
        )
        
        self.part_time_employee = Employee.objects.create(
            name="Jane Smith",
            position="Data Analyst",
            availability=Employee.PART_TIME,
            department="Data Science"
        )

    def test_employee_str(self):
        """
        Test the __str__ method of the Employee model.
        """
        self.assertEqual(str(self.full_time_employee), "John Doe")
        self.assertEqual(str(self.part_time_employee), "Jane Smith")

    def test_get_available_hours_full_time(self):
        """
        Test the get_available_hours method for a full-time employee.
        """
        self.assertEqual(self.full_time_employee.get_available_hours(), 40)

    def test_get_available_hours_part_time(self):
        """
        Test the get_available_hours method for a part-time employee.
        """
        self.assertEqual(self.part_time_employee.get_available_hours(), 20)

    def test_employee_fields(self):
        """
        Test the fields of the Employee model.
        """
        # Check if the employee is created with the correct values
        self.assertEqual(self.full_time_employee.name, "John Doe")
        self.assertEqual(self.full_time_employee.position, "Software Engineer")
        self.assertEqual(self.full_time_employee.availability, Employee.FULL_TIME)
        self.assertEqual(self.full_time_employee.department, "Engineering")
        
        # Check if the part-time employee has the correct values
        self.assertEqual(self.part_time_employee.name, "Jane Smith")
        self.assertEqual(self.part_time_employee.position, "Data Analyst")
        self.assertEqual(self.part_time_employee.availability, Employee.PART_TIME)
        self.assertEqual(self.part_time_employee.department, "Data Science")

    def test_default_availability(self):
        """
        Test if the default availability is set to FULL_TIME when no availability is specified.
        """
        # Create an employee without specifying availability (defaults to FULL_TIME)
        employee = Employee.objects.create(
            name="Alice Cooper",
            position="Product Manager",
            department="Product"
        )
        self.assertEqual(employee.availability, Employee.FULL_TIME)

    def test_availability_choices(self):
        """
        Test the choices for the availability field.
        """
        # Check if the full-time choice is correct
        full_time_employee = Employee.objects.create(
            name="Mark Twain",
            position="CTO",
            availability=Employee.FULL_TIME,
            department="Executive"
        )
        self.assertEqual(full_time_employee.availability, Employee.FULL_TIME)

        # Check if the part-time choice is correct
        part_time_employee = Employee.objects.create(
            name="Emily Bronte",
            position="HR Specialist",
            availability=Employee.PART_TIME,
            department="Human Resources"
        )
        self.assertEqual(part_time_employee.availability, Employee.PART_TIME)





class EmployeeListCreateViewTests(APITestCase):
    def setUp(self):
        # URL for listing and creating employees
        self.url = reverse('employee-list-create')  

        # Data to create an employee
        self.employee_data = {
            "name": "John Doe",
            "position": "Software Engineer",
            "availability": "FT",
            "department": "Engineering"
        }

    def test_get_employees(self):
        """
        Test GET request to retrieve all employees (list view).
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No employees initially

    def test_create_employee(self):
        """
        Test POST request to create a new employee.
        """
        response = self.client.post(self.url, self.employee_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.employee_data['name'])
        self.assertEqual(response.data['position'], self.employee_data['position'])
        self.assertEqual(response.data['availability'], self.employee_data['availability'])
        self.assertEqual(response.data['department'], self.employee_data['department'])

        # Ensure the employee is saved to the database
        self.assertEqual(Employee.objects.count(), 1)

    def test_create_employee_invalid(self):
        """
        Test POST request with invalid data (e.g., missing required field).
        """
        invalid_data = {"name": "Jane Doe", "position": "HR Specialist"}  # Missing 'availability' and 'department'
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('availability', response.data)  # Availability should be required
        self.assertIn('department', response.data)  # Department should be required


class EmployeeDetailViewTests(APITestCase):
    def setUp(self):
        # Create a sample employee for testing
        self.employee = Employee.objects.create(
            name="Alice Cooper",
            position="Product Manager",
            availability=Employee.FULL_TIME,
            department="Product"
        )
        self.url = reverse('employee-detail', args=[self.employee.id])  # Make sure 'employee-detail' is the correct URL

    def test_get_employee(self):
        """
        Test GET request to retrieve a specific employee.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.employee.name)
        self.assertEqual(response.data['position'], self.employee.position)
        self.assertEqual(response.data['availability'], self.employee.availability)
        self.assertEqual(response.data['department'], self.employee.department)

    def test_update_employee(self):
        """
        Test PUT request to update a specific employee.
        """
        updated_data = {
            "name": "Alice Cooper Updated",
            "position": "Senior Product Manager",
            "availability": Employee.PART_TIME,
            "department": "Product"
        }
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], updated_data['name'])
        self.assertEqual(response.data['position'], updated_data['position'])
        self.assertEqual(response.data['availability'], updated_data['availability'])
        self.assertEqual(response.data['department'], updated_data['department'])

        # Ensure the employee data is updated in the database
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.name, updated_data['name'])
        self.assertEqual(self.employee.position, updated_data['position'])
        self.assertEqual(self.employee.availability, updated_data['availability'])
        self.assertEqual(self.employee.department, updated_data['department'])

    def test_delete_employee(self):
        """
        Test DELETE request to delete a specific employee.
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure the employee is deleted from the database
        self.assertEqual(Employee.objects.count(), 0)

    def test_delete_employee_not_found(self):
        """
        Test DELETE request for a non-existent employee (404).
        """
        non_existent_url = reverse('employee-detail', args=[9999])  # Non-existent employee ID
        response = self.client.delete(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


