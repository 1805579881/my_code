from .index import IndexRedirectView,LogoutView,CustomPasswordChangeView, IndexView
from .face import FaceListView, FaceCreateView, FaceUpdateView, FaceDeleteView, FaceDetailView, BatchUpload
from .face import delete_selected_people, set_devices
from .record import RecordListView
from .report import ReportView, export_test_records, get_personal_records_by_date,PersonalDateRangeReportView
from .department import DepartmentListView,DepartmentCreateView, DepartmentUpdateView, DepartmentDeleteView, DepartmentDetailView, delete_selected_department, find_department_name, update_department_is_delete
