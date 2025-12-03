# employees/admin.py
from django.contrib import admin

# Register your models here.
from .models import Department, EmployeeProfile

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'description')
    search_fields = ('name', 'manager__username')
    list_filter = ('manager',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position')
    list_filter = ('department', 'hire_date')
    autocomplete_fields = ['user']