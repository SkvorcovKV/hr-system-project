# employees/urls.py
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    # другие маршруты...
]