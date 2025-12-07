# employees/admin.py
from django.contrib import admin

# Register your models here.
from .models import Department, EmployeeProfile
from .forms import EmployeeProfileForm  # ← импортируем форму для смены цветов отпусков

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'description')
    search_fields = ('name', 'manager__username')
    list_filter = ('manager',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    form = EmployeeProfileForm  # ✅ Указываем использовать кастомную форму
    list_display = ('user', 'department', 'position', 'hire_date', 'color_code')  # ✅ Добавил color_code для отображения в списке
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position')
    list_filter = ('department', 'hire_date')
    autocomplete_fields = ['user']