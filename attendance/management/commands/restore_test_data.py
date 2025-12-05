from django.core.management.base import BaseCommand
from attendance.models import AbsenceType
from employees.models import Department, EmployeeProfile
from django.contrib.auth.models import User
from datetime import date

class Command(BaseCommand):
    help = 'Восстанавливает тестовые данные'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Восстановление тестовых данных...")
        
        # 1. Типы отсутствий
        types = [
            {'name': 'Отпуск основной', 'code': '09', 'color': '#009900'},
            {'name': 'Больничный', 'code': '19', 'color': '#660000'},
            {'name': 'Удаленная работа', 'code': '38', 'color': '#006666'},
            {'name': 'Командировка', 'code': '06', 'color': '#003300'},
            {'name': 'Отпуск за свой счет', 'code': '16', 'color': '#99004C'},
            {'name': 'Работал в дневное время', 'code': '01', 'color': '#00FF00'},
        ]
        
        for i, data in enumerate(types):
            obj, created = AbsenceType.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'color': data['color'],
                    'is_paid': True,
                    'requires_approval': True,
                    'order': i + 1
                }
            )
            status = "создан" if created else "уже существует"
            self.stdout.write(f"  - {data['name']}: {status}")
        
        # 2. Отдел
        dept, created = Department.objects.get_or_create(
            name='техническая поддержка',
            defaults={'description': 'Отдел технической поддержки'}
        )
        self.stdout.write(f"  - Отдел '{dept.name}': {'создан' if created else 'уже существует'}")
        
        # 3. Сотрудники
        employees_data = [
            ('Синцов', 'Андрей', 'Владимирович', 'sintsov'),
            ('Терентьев', 'Дмитрий', 'Васильевич', 'terentev'),
            ('Юнисов', 'Рамиль', 'Наилевич', 'unisov'),
        ]
        
        for last_name, first_name, middle_name, username in employees_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f'{username}@example.com',
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')  # простой пароль для теста
                user.save()
            
            profile, created = EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': dept,
                    'position': 'Специалист техподдержки',
                    'hire_date': date.today(),
                    'phone': '+7 999 999 99 99'
                }
            )
            
            status = "создан" if created else "уже существует"
            self.stdout.write(f"  - Сотрудник {last_name} {first_name}: {status}")
        
        self.stdout.write(self.style.SUCCESS("Тестовые данные восстановлены!"))
        self.stdout.write("\nДанные для входа:")
        self.stdout.write("  Логин: sintsov, terentev, unisov")
        self.stdout.write("  Пароль: password123")