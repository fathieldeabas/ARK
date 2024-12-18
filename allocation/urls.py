from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AllocationSuggestionViewSet, BestAllocationSuggestionViewSet, download_exported, export_report_view,add_employee_to_project,remove_employee_from_project

from .views import current_allocations

urlpatterns = [
    path('current-allocations/', current_allocations, name='current_allocations'),
]

# Initialize the router
router = DefaultRouter()
router.register(r'projects/(?P<project_id>\d+)/allocation-suggestions', AllocationSuggestionViewSet, basename='allocation-suggestions')
router.register(r'projects/(?P<project_id>\d+)/best-allocation-suggestions', BestAllocationSuggestionViewSet, basename='best-allocation-suggestions')


# Include the router URLs in your app's URL configuration
urlpatterns = [
    path('', include(router.urls)),
    path(
        'download_exported/',
        download_exported,
        name='download_exported',
    ),
    path('export_employee_report/', export_report_view, name='export_employee_report'),
    path('current-allocations/', current_allocations, name='current_allocations'),
    path('add-employee-to-project/', add_employee_to_project, name='add_employee_to_project'),
    path('remove-employee-from-project/<int:allocation_id>/', remove_employee_from_project, name='remove_employee_from_project'),


]
