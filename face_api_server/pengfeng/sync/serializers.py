from rest_framework import serializers

from .models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('pk', 'uuid', 'name', 'descriptions', 'device_type', 'position', 'ip', 'members')
