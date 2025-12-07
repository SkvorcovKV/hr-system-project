# employees/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import EmployeeProfileForm

@login_required
def edit_profile(request):
    profile = request.user.profile  # Получаем профиль текущего пользователя

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # Перенаправление на просмотр профиля
    else:
        form = EmployeeProfileForm(instance=profile)
        print(form)  # проверьте, что форма не пуста
        print(form.fields.keys())  # выведите все поля формы
    return render(request, 'employees/profile_form.html', {'form': form})


# Create your views here.
