from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('month/', views.month_view, name='month_view'),
    path('month/<int:year>/<int:month>/', views.month_view, name='month_view_date'),
    path('update-attendance/', views.update_attendance, name='update_attendance'),
    path('get-record/<int:record_id>/', views.get_record, name='get_record'),
    path('save-record/', views.save_record, name='save_record'),
    path('confirm/<int:record_id>/', views.confirm_record, name='confirm_record'),
    path('employees/', views.employee_list, name='employee_list'),
    path('test-template/', views.test_template, name='test_template'),
    path('hello/', views.hello_world, name='hello'),
    path('year-view/', views.year_view, name='year_view'),
]