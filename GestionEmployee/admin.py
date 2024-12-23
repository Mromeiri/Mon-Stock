from django.contrib import admin

# your_app/admin.py

from django.contrib import admin
from .models import *

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('id', 'name', 'address', 'phone', 'daily_salary', 'center','balance')
    search_fields = ('id', 'name', 'phone')
    list_filter = ('center',)

@admin.register(Salaire)
class SalaireAdmin(admin.ModelAdmin):
    actions = ['imprimer_pdf']
    list_display = ('employee', 'display_date', 'salaire')
    # def has_add_permission(self, request):
    #     return False

    # # def has_delete_permission(self, request, obj=None):
    # #     return False
    # def has_change_permission(self, request, obj=None):
    #     return False
    def display_date(self, obj):
        return obj.date.strftime('%Y-%m')

    display_date.short_description = 'Date'
    display_date.admin_order_field = 'date'
    
    
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date')
    list_filter = ( 'date',)

class AdvanceRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'request_date')
    list_filter = ('request_date', )

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'activity_type', 'details', 'date')
    list_filter = ('activity_type', 'date')

admin.site.register(Absence, AttendanceAdmin)
admin.site.register(AdvanceRequest, AdvanceRequestAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)

