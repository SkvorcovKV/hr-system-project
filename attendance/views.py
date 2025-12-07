from django.shortcuts import render, get_object_or_404, redirect  # объединили
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
import calendar
import logging
from datetime import date, datetime, timedelta
from .models import AttendanceRecord, AbsenceType
from employees.models import EmployeeProfile

from collections import defaultdict
from django.utils import timezone

logger = logging.getLogger(__name__)

def custom_logout(request):
    """Кастомный выход с поддержкой GET"""
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """Главная страница дашборда"""
    today = timezone.now().date()
    
    # Статистика за текущий месяц
    current_month = today.month
    current_year = today.year
    
    # Получаем записи за текущий месяц
    month_records = AttendanceRecord.objects.filter(
        employee=request.user,
        date__year=current_year,
        date__month=current_month
    )
    
    # Статистика по типам
    stats = {}
    for record in month_records:
        type_name = record.absence_type.name
        stats[type_name] = stats.get(type_name, 0) + 1
    
    # Найдем тип "Работал в дневное время"
    work_type_code = '01'  # код для "Работал в дневное время"
    work_days = month_records.filter(absence_type__code=work_type_code).count()
    
    context = {
        'today': today,
        'month_records': month_records,
        'stats': stats,
        'total_days': month_records.count(),
        'work_days': work_days,
    }
    
    return render(request, 'attendance/dashboard.html', context)

@login_required
def month_view(request, year=None, month=None):
    """Табель учета по месяцам"""
    today = timezone.now().date()
    
    # Определяем год и месяц
    if year and month:
        view_date = date(year, month, 1)
    else:
        month_param = request.GET.get('month')
        if month_param:
            try:
                view_date = datetime.strptime(month_param, '%Y-%m').date().replace(day=1)
            except:
                view_date = today.replace(day=1)
        else:
            view_date = today.replace(day=1)
    
    # Определяем, чей табель показываем
    employee_id = request.GET.get('employee_id')
    
    if employee_id:
        # Если указан конкретный сотрудник
        employee = get_object_or_404(User, id=employee_id)
        # Проверяем права
        if not request.user.is_staff and employee != request.user:
            return redirect('attendance:month_view')
    else:
        # Если сотрудник не указан
        if request.user.is_staff:
            # Админ по умолчанию видит свой табель
            employee = request.user
        else:
            # Сотрудник видит только свой табель
            employee = request.user
    
    # Получаем календарь
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(view_date.year, view_date.month)
    
    # Получаем записи за месяц
    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__year=view_date.year,
        date__month=view_date.month
    )
    
    print(f"DEBUG: Пользователь запроса: {request.user.username}")
    print(f"DEBUG: Показываем табель для: {employee.username}")
    print(f"DEBUG: Месяц: {view_date.year}-{view_date.month}")
    print(f"DEBUG: Найдено записей: {records.count()}")
    
    # Преобразуем в словарь
    records_dict = {record.date.day: record for record in records}
    
    # Навигация
    prev_month = view_date - timedelta(days=1)
    next_month = view_date + timedelta(days=32)
    
    absence_types = AbsenceType.objects.all()
    
    context = {
        'view_date': view_date,
        'month_days': month_days,
        'records_dict': records_dict,
        'employee': employee,
        'prev_month': prev_month.replace(day=1),
        'next_month': next_month.replace(day=1),
        'absence_types': absence_types,
        'today': today,
        'is_admin': request.user.is_staff,
        'all_employees': User.objects.all() if request.user.is_staff else None,
    }
    
    return render(request, 'attendance/month_view.html', context)

from collections import defaultdict
from django.utils import timezone

@login_required
def year_view(request):
    # Получаем записи отпусков
    vacations = AttendanceRecord.objects.filter(
        absence_type__code='09', # Убедитесь, что код соответствует типу "Отпуск"
        date__gte=timezone.now().date()
    ).select_related('employee', 'employee__profile', 'employee__profile__department')

    # Используем defaultdict для автоматической инициализации ключей
    vacations_by_year = defaultdict(lambda: {'records': [], 'count': 0})

    # Заполняем словарь: добавляем записи и считаем количество отпусков по годам
    for record in vacations:
        year = record.date.year
        vacations_by_year[year]['records'].append(record)
        vacations_by_year[year]['count'] += 1

    # Статистика по отделам
    department_stats = {}
    for record in vacations:
        # Проверяем наличие профиля и отдела
        employee = record.employee
        if hasattr(employee, 'profile') and employee.profile.department:
            dept_name = employee.profile.department.name
            department_stats[dept_name] = department_stats.get(dept_name, 0) + 1
    # Количество отпусков по годам
    context = {
        'vacations_by_year': dict(vacations_by_year),  # преобразуем обратно в dict для шаблона
        'department_stats': department_stats,
    }
    return render(request, 'attendance/year_view.html', context)


@login_required
@csrf_exempt
def update_attendance(request):
    """Обновление записи в табеле (AJAX)"""
    print("=== DEBUG update_attendance ===")
    print(f"Метод запроса: {request.method}")
    print(f"Заголовок X-Requested-With: {request.headers.get('x-requested-with')}")
    print(f"Все POST данные: {dict(request.POST)}")
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        date_str = request.POST.get('date')
        absence_type_id = request.POST.get('absence_type_id')
        comment = request.POST.get('comment', '')
        
        print(f"DEBUG: Получена дата строка: '{date_str}'")
        print(f"DEBUG: Получен тип отсутствия: {absence_type_id}")
        print(f"DEBUG: Получен комментарий: '{comment}'")
        
        try:
            # Пробуем распарсить дату
            print(f"DEBUG: Пытаемся распарсить дату: {date_str}")
            record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            print(f"DEBUG: Успешно распарсено: {record_date}")
            
            absence_type = AbsenceType.objects.get(id=absence_type_id)
            print(f"DEBUG: Найден тип отсутствия: {absence_type.name}")
            
            # Проверяем, можно ли редактировать
            today = timezone.now().date()
            print(f"DEBUG: Сегодня: {today}")
            print(f"DEBUG: Дата записи: {record_date}")
            print(f"DEBUG: Пользователь staff: {request.user.is_staff}")
            
            # Для сотрудников ограничиваем редактирование будущих дат
            if not request.user.is_staff:
                if record_date <= today:
                    print(f"DEBUG: Ошибка - сотрудник пытается редактировать прошедшую дату")
                    return JsonResponse({
                        'success': False,
                        'error': 'Вы можете редактировать только будущие даты'
                    })
            
            # Создаем или обновляем запись
            print(f"DEBUG: Создаем/обновляем запись для пользователя: {request.user.username}")
            record, created = AttendanceRecord.objects.update_or_create(
                employee=request.user,
                date=record_date,
                defaults={
                    'absence_type': absence_type,
                    'marked_by': request.user,
                    'is_confirmed': False,
                    'comment': comment,
                }
            )
            
            print(f"DEBUG: Запись {'создана' if created else 'обновлена'}: {record.id}")
            
            return JsonResponse({
                'success': True,
                'record': {
                    'id': record.id,
                    'type_name': record.absence_type.name,
                    'type_color': record.absence_type.color,
                    'is_confirmed': record.is_confirmed,
                    'comment': record.comment,
                }
            })
            
        except ValueError as e:
            print(f"DEBUG: ValueError при парсинге даты: {e}")
            print(f"DEBUG: Дата которую пытались распарсить: '{date_str}'")
            return JsonResponse({
                'success': False, 
                'error': f"Ошибка формата даты: {str(e)}. Получено: '{date_str}'"
            })
        except AbsenceType.DoesNotExist:
            print(f"DEBUG: Тип отсутствия с ID {absence_type_id} не найден")
            return JsonResponse({
                'success': False, 
                'error': f'Тип отсутствия с ID {absence_type_id} не найден'
            })
        except Exception as e:
            print(f"DEBUG: Общая ошибка: {str(e)}")
            import traceback
            print(f"DEBUG: Трейсбэк: {traceback.format_exc()}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    print(f"DEBUG: Не AJAX запрос или не POST")
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def get_record(request, record_id):
    """Получение данных записи (AJAX)"""
    record = get_object_or_404(AttendanceRecord, id=record_id, employee=request.user)
    
    return JsonResponse({
        'success': True,
        'record': {
            'id': record.id,
            'absence_type_id': record.absence_type.id,
            'comment': record.comment,
            'date': record.date.isoformat(),
        }
    })

@login_required
@csrf_exempt
def save_record(request):
    """Сохранение изменений записи (AJAX)"""
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        absence_type_id = request.POST.get('absence_type')
        comment = request.POST.get('comment', '')
        
        try:
            record = AttendanceRecord.objects.get(id=record_id, employee=request.user)
            absence_type = AbsenceType.objects.get(id=absence_type_id)
            
            record.absence_type = absence_type
            record.comment = comment
            record.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def employee_list(request):
    """Список сотрудников (для администраторов)"""
    if not request.user.is_staff:
        return redirect('attendance:dashboard')
    
    employees = EmployeeProfile.objects.select_related('user', 'department').all()
    
    context = {
        'employees': employees,
    }
    return render(request, 'attendance/employee_list.html', context)

@login_required
def confirm_record(request, record_id):
    """Подтверждение записи (только для администраторов)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для подтверждения записей')
        return redirect('attendance:month_view')
    
    record = get_object_or_404(AttendanceRecord, id=record_id)
    record.is_confirmed = True
    record.confirmed_by = request.user
    record.confirmed_date = timezone.now()
    record.save()
    
    messages.success(request, f'Запись от {record.date} подтверждена')
    return redirect('attendance:month_view')

@login_required  
def test_template(request):
    """Тестовый шаблон без сложного наследования"""
    return HttpResponse("""
    <html>
    <body>
    <h1>Тестовый шаблон работает!</h1>
    <p>Это простой HTML без наследования.</p>
    <p><a href="/attendance/">На дашборд</a></p>
    </body>
    </html>
    """)

def hello_world(request):
    """Абсолютно простой view для теста"""
    return HttpResponse("""
    <html>
    <body>
    <h1>Hello World работает!</h1>
    <p>Если это видите, Django работает правильно.</p>
    <p><a href="/attendance/">На дашборд</a></p>
    </body>
    </html>
    """)