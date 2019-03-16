from django.contrib import admin

from sync.models import Device

from .models import Person, Record, Department


class MembershipInline(admin.TabularInline):
    model = Device.members.through


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('name', 'position', 'employee_number', 'is_active', 'is_deleted', 'employment_date', 'departure_date','department')
    fields = ('name', 'position', 'employee_number', 'raw_image', 'is_active', 'is_deleted', 'employment_date', 'departure_date', 'department')
    list_filter = ('position', 'is_active', 'is_deleted', 'employment_date', 'departure_date')
    search_fields = ('name', 'position')
    list_per_page = 20


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('created', 'target')
    fields = ['target']
    list_filter = ('created',)
    search_fields = ('target',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_deleted')
    fields = ['name', 'is_deleted']
    list_filter = ('name', 'is_deleted')
    search_fields = ('name', 'is_deleted')


admin.site.disable_action('delete_selected')

admin.AdminSite.site_title = '人脸识别系统'
admin.AdminSite.site_header = '人脸识别系统'
admin.AdminSite.index_title = '人脸识别系统'
