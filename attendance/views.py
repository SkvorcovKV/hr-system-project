from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

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