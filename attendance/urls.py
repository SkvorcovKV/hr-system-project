from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Главная страница attendance - перенаправление на дашборд
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test-template/', views.test_template, name='test_template'),
    path('hello/', views.hello_world, name='hello'),
]