from rest_framework import generics
from .models import Project
from .serializers import ProjectSerializer

# List and Create projects (GET and POST)
class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# Retrieve, Update, and Delete a specific project (GET, PUT, DELETE)
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
