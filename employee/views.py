# Create your views here.
from rest_framework import generics
from .models import Employee
from employee.serializers import EmployeeSerializer
# List and Create employees (GET and POST)
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

# Retrieve, Update, and Delete a specific employee (GET, PUT, DELETE)
class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
