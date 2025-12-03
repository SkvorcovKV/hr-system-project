# attendance/models.py
from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone

class AbsenceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    code = models.CharField(max_length=20, verbose_name="Код", unique=True)
    color = models.CharField(max_length=7, default="#007bff", verbose_name="Цвет (HEX)")
    is_paid = models.BooleanField(default=True, verbose_name="Оплачиваемый")
    requires_approval = models.BooleanField(default=True, verbose_name="Требует подтверждения")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тип отсутствия"
        verbose_name_plural = "Типы отсутствий"
        ordering = ['order', 'name']

class AttendanceRecord(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Сотрудник")
    date = models.DateField(verbose_name="Дата")
    absence_type = models.ForeignKey(
        AbsenceType, 
        on_delete=models.PROTECT, 
        verbose_name="Тип"
    )
    marked_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_records',
        verbose_name="Кто отметил"
    )
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтверждено")
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_records',
        verbose_name="Кто подтвердил"
    )
    confirmed_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата подтверждения")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Запись в табеле"
        verbose_name_plural = "Записи в табеле"
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']
    
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.absence_type}"
    
    def can_edit(self, user):
        from django.utils import timezone
        today = timezone.now().date()
        
        if user.is_staff or (hasattr(self.employee, 'profile') and 
                           hasattr(self.employee.profile, 'department') and 
                           self.employee.profile.department and 
                           self.employee.profile.department.manager == user):
            return True
        
        if user == self.employee:
            return self.date > today and not self.is_confirmed
        
        return False