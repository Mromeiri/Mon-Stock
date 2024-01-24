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
    list_display = ('employee', 'date', 'salaire')
    
    
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

