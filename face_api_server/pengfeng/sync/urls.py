from django.urls import include, path

from sync.views import DeviceCreateView, DeviceDeleteView, DeviceDetailView, DeviceListView, DeviceUpdateView, \
    LoggingView
from sync.views import create_or_update_device, get_version_difference, heart_beats, set_people, upload_record

app_name = 'sync'
urlpatterns = [
    path('face/', get_version_difference, name='get-version-difference'),
    path('record/', upload_record, name='upload-record'),
    path('heart_beats/', heart_beats, name='heart-beats'),
    path('device_list/', DeviceListView.as_view(), name='device-list'),
    path('device_list/create/', DeviceCreateView.as_view(), name='device-create'),
    path('device_list/update/<int:pk>/', DeviceUpdateView.as_view(), name='device-update'),
    path('device_list/detail/<int:pk>/', DeviceDetailView.as_view(), name='device-detail'),
    path('device_list/delete/<int:pk>/', DeviceDeleteView.as_view(), name='device-delete'),
    path('devices/set_people/', set_people, name='set-people'),
    path('devices/create_or_update_device/', create_or_update_device, name='create-or-update-device'),
    path('logging/', LoggingView.as_view(), name='logging'),
]
