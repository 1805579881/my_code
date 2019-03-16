import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from .models import Device

tz = timezone.get_current_timezone()


class MonitorConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'monitor',
            self.channel_name
        )
        self.accept()
        for device in Device.objects.all():
            online_time = device.latest_time - device.start_time
            self.send(text_data=json.dumps({
                'pk': device.pk,
                'uuid': str(device.uuid),
                'name': device.name,
                'device_type': device.device_type,
                'online_time': str(online_time),
                'urls': device.urls,
                'position': device.position,
                'latest': device.latest_time.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'),
                'ip': device.ip
            }))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'monitor',
            self.channel_name
        )

    def device_info_message(self, event):
        message = event['device_info']
        self.send(text_data=json.dumps(message))


class LoggingConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'logging',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'logging',
            self.channel_name
        )

    def logging_info_message(self, event):
        self.send(text_data=json.dumps(event['msg']))
