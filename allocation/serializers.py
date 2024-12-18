from rest_framework import serializers
from .models import Allocation

class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = ['employee', 'project', 'allocation_percentage', 'allocation_start_date', 'allocation_end_date']
