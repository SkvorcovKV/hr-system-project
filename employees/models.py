# employees/models.py
from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отдела")
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_departments',
        verbose_name="Руководитель отдела"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(
        Department, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Отдел"
    )
    position = models.CharField(max_length=100, verbose_name="Должность", blank=True)
    hire_date = models.DateField(verbose_name="Дата приема", null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    avatar = models.ImageField(
        upload_to='avatars/', 
        default='avatars/default.png',
        verbose_name="Фотография"
    )
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.position})"
    
    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"