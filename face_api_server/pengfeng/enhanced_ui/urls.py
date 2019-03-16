from django.urls import path, include

from .views import (BatchUpload, FaceCreateView, FaceDeleteView,
                    FaceDetailView, FaceListView, FaceUpdateView,
                    RecordListView, ReportView, export_test_records,
                    delete_selected_people, get_personal_records_by_date, set_devices, IndexRedirectView,
                    DepartmentListView, DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, DepartmentDetailView , delete_selected_department, find_department_name, update_department_is_delete)
from .views import PersonalDateRangeReportView, LogoutView, CustomPasswordChangeView, IndexView


app_name = 'enhanced_ui'
face_patterns = [
    path('', FaceListView.as_view(), name='face-list'),
    path('create/', FaceCreateView.as_view(), name='face-create'),
    path('update/<int:pk>/', FaceUpdateView.as_view(), name='face-update'),
    path('delete/<int:pk>/', FaceDeleteView.as_view(), name='face-delete'),
    path('detail/<int:pk>/', FaceDetailView.as_view(), name='face-detail'),
    path('create/batch/', BatchUpload.as_view(), name='face-batch-create'),
    path('delete_selected/', delete_selected_people, name='face-delete-selected'),
    path('set_devices/', set_devices, name='face-set-devices'),
    path('date_range_report/<int:pk>/', PersonalDateRangeReportView.as_view(), name='face-date-range-report'),
]
record_patterns = [
    path('', RecordListView.as_view(), name='record-list'),
    path('personal_records/', get_personal_records_by_date, name='personal-records'),
    path('export_records/', export_test_records, name='export-records'),
]
report_patterns = [
    path('', ReportView.as_view(), name='report'),
    path(r'<str:date>/', ReportView.as_view(), name='report-date'),
]
auth_patterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change-password')
]
department_patterns = [
    path('', DepartmentListView.as_view(), name='department-list'),
    path('create/', DepartmentCreateView.as_view(), name='department-create'),
    path('update/<int:pk>/', DepartmentUpdateView.as_view(), name='department-update'),
    path('delete/<int:pk>/', DepartmentDeleteView.as_view(), name='department-delete'),
    path('detail/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),
    path('delete_selected/', delete_selected_department, name='department-delete-selected'),
    path('find_name/', find_department_name, name='find_department_name'),
    path('update_dtment/', update_department_is_delete , name='update_department_is_delete'),
]

urlpatterns = [
    #path('', IndexRedirectView.as_view(), name='index'),
    path('', IndexView.as_view(), name='index'),
    path('faces/', include(face_patterns)),
    path('records/', include(record_patterns)),
    path('report/', include(report_patterns)),
    path('auth/', include(auth_patterns)),
    path('departments/', include(department_patterns)),
]
