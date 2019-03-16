from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^sync/device_list/$', consumers.MonitorConsumer),
    url(r'^sync/logging/$', consumers.LoggingConsumer),
]
