from rest_framework import serializers

from .models import Person, Record, Department


class PersonSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name')

    class Meta:
        model = Person
        fields = ('pk', 'uuid', 'name', 'position', 'employee_number', 'image', 'urls', 'is_active', 'employment_date',
                  'departure_date', 'department_name', 'devices')
        read_only_fields = ('pk', 'uuid', 'devices')


class RecordSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    target__name = serializers.CharField(source='target.name', read_only=True)
    target__position = serializers.CharField(source='target.position', read_only=True)
    target__employee_number = serializers.CharField(source='target.employee_number', read_only=True)
    target__department = serializers.CharField(source='target.department', read_only=True)

    class Meta:
        model = Record
        read_only_fields = ('pk', 'target__name', 'target__position', 'target__employee_number', 'target__department')
        fields = (
            'pk', 'target', 'created', 'record_type', 'target__name', 'target__position', 'target__employee_number',
            'target__department')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('pk', 'name','urls',)