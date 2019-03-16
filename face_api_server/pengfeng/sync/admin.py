from django.contrib import admin

from .models import Device


class MembershipInline(admin.TabularInline):
    model = Device.members.through


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('uuid', 'name', 'device_type')
    fields = ['name', 'device_type']
    list_filter = ('device_type',)
    exclude = ('members',)
