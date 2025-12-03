# attendance/admin.py
from django.contrib import admin

# Register your models here.
from .models import AbsenceType, AttendanceRecord

@admin.register(AbsenceType)
class AbsenceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'color', 'is_paid', 'requires_approval', 'order')
    list_editable = ('order', 'color', 'is_paid')
    ordering = ('order', 'name')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'absence_type', 'is_confirmed', 'marked_by', 'created_at')
    list_filter = ('date', 'absence_type', 'is_confirmed', 'employee')
    search_fields = ('employee__username', 'employee__first_name', 'employee__last_name', 'comment')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee=request.user)