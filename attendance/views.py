from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
import logging
from django.db.models import Q
import calendar
from datetime import date, datetime, timedelta
from .models import AttendanceRecord, AbsenceType
from employees.models import EmployeeProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout
from django.shortcuts import redirect

logger = logging.getLogger(__name__)

def custom_logout(request):
    """Кастомный выход с поддержкой GET"""
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """Главная страница дашборда"""
    logger.info(f"Dashboard accessed by {request.user.username}")
    
    context = {
        'today': timezone.now().date(),
        'user': request.user,
        'page_title': 'Дашборд HR системы'
    }
    
    return render(request, 'attendance/dashboard_simple.html', context)

@login_required
def month_view(request, year=None, month=None):
    """Табель учета по месяцам"""
    # Определяем год и месяц
    today = timezone.now().date()
    
    if year and month:
        view_date = date(year, month, 1)
    else:
        # Получаем месяц из GET параметра или текущий
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
    if employee_id and request.user.is_staff:
        # Админ может смотреть чужие табели
        from django.contrib.auth.models import User
        employee = get_object_or_404(User, id=employee_id)
    else:
        # Сотрудник видит только свой табель
        employee = request.user
    
    # Получаем календарь
    cal = calendar.Calendar(firstweekday=0)  # Понедельник первый
    month_days = cal.monthdayscalendar(view_date.year, view_date.month)
    
    # Получаем записи за месяц
    records = AttendanceRecord.objects.filter(
        employee=employee,
        date__year=view_date.year,
        date__month=view_date.month
    )
    
    # Преобразуем в словарь для быстрого доступа
    records_dict = {record.date.day: record for record in records}
    
    # Навигация по месяцам
    prev_month = view_date - timedelta(days=1)
    next_month = view_date + timedelta(days=32)
    
    # Получаем все типы отсутствий для формы
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
    }
    
    return render(request, 'attendance/month_view.html', context)

@login_required
@csrf_exempt
def update_attendance(request):
    """Обновление записи в табеле (AJAX)"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        date_str = request.POST.get('date')
        absence_type_id = request.POST.get('absence_type_id')
        comment = request.POST.get('comment', '')
        
        try:
            record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            absence_type = AbsenceType.objects.get(id=absence_type_id)
            
            # Проверяем, можно ли редактировать
            today = timezone.now().date()
            
            # Для сотрудников ограничиваем редактирование будущих дат
            if not request.user.is_staff:
                if record_date <= today:
                    return JsonResponse({
                        'success': False,
                        'error': 'Вы можете редактировать только будущие даты'
                    })
            
            # Создаем или обновляем запись
            record, created = AttendanceRecord.objects.update_or_create(
                employee=request.user,
                date=record_date,
                defaults={
                    'absence_type': absence_type,
                    'marked_by': request.user,
                    'is_confirmed': False,  # Сначала не подтверждено
                    'comment': comment,
                }
            )
            
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
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
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