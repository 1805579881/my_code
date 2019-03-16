import logging

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from rest_framework_bulk import BulkModelViewSet
from rest_framework.response import Response
from .models import Person, Record, Department
from .ordering import PersonOrdering, RecordOrdering
from .serializers import PersonSerializer, RecordSerializer, DepartmentSerializer

logger = logging.getLogger(__name__)


class PersonViewSet(BulkModelViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.filter(
        Q(is_deleted=False) & (Q(raw_image__isnull=False) | Q(image__isnull=False))).order_by('-is_active')
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, PersonOrdering)
    search_fields = ('name', 'position', 'employment_date', 'departure_date', 'department__name')
    filter_fields = ('uuid', 'id', 'name', 'position', 'is_active', 'employee_number', 'employment_date', 'department__name', 'departure_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        depart_name = serializer.validated_data['department'].get('name')
        departments = Department.objects.filter(Q(is_deleted=False) & Q(name=depart_name))
        if departments.count() < 1:
            return Response({
                'error': 'true',
                'detail': '没有此部门'
            })
        else:
            try:
                department = Department.objects.get(Q(name=depart_name) & Q(is_deleted=False))
                serializer.validated_data['department'] = department
                self.perform_create(serializer)
                return Response({
                    'error': 'false'
                })
            except Exception as e:
                return Response({
                    'error': 'true',
                    'detail': e
                })

    def update(self, request, *args, **kwargs):
        depart_name = request.POST['department_name']
        departments = Department.objects.filter(Q(name=depart_name) & Q(is_deleted=False))
        if departments.count() < 1:
            return Response({
                'error': 'true',
                'detail': '没有此部门'
            })
        else:
            try:
                instance = self.get_object()
                department = Department.objects.get(Q(name=depart_name) & Q(is_deleted=False))
                instance.department = department
                instance.name = request.POST['name']
                instance.position = request.POST['position']
                instance.employee_number = request.POST['employee_number']
                instance.image = request.POST['image']

                if 'is_active' in request.data.keys():
                    if request.POST['is_active'] == 'true':
                        instance.is_active = True
                    else:
                        instance.is_active = False
                else:
                    instance.is_active = False
                instance.employment_date = request.POST['employment_date']
                if request.POST['departure_date'] == "":
                    instance.departure_date = None
                else:
                    instance.departure_date = request.POST['departure_date']
                instance.save()
                return Response({
                    'error': 'false'
                })
            except Exception as e:
                return Response({
                    'error': 'true',
                    'detail': e
                })


class CustomPersonViewSet(BulkModelViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.filter(
        (Q(raw_image__isnull=False) | Q(image__isnull=False)) & Q(is_deleted=False)).order_by('-is_active')
    lookup_field = 'uuid'
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('uuid', 'id', 'name', 'position', 'is_active', 'employee_number', 'employment_date', 'department', 'departure_date')

    def destroy(self, request, *args, **kwargs):
        """应Android端的要求将返回状态码改为200"""
        response = super(CustomPersonViewSet, self).destroy(request, *args, **kwargs)
        response.status_code = 200
        response.data = {}
        return response


class RecordViewSet(BulkModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, RecordOrdering)
    filter_fields = ('target', 'created', 'record_type')
    search_fields = ('target__name', 'target__position', 'target__employee_number',
                     'target__department__name', 'created', 'record_type')


class DepartmentViewSet(BulkModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.filter(Q(is_deleted=False))
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = ('name',)
    filter_fields = ('name',)
    ordering_fields = ('name',)
