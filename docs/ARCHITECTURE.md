# архитектура приложения

# Архитектура приложения

HR-система построена на Django и использует два основных приложения: `attendance` и `employees`.  
Все данные связаны через модели, поддерживающие иерархию подчинённости и подтверждение записей.

## 🧱 Основные модели

### `employees.Employee` — сотрудник
Хранит профиль пользователя и иерархию.

```python
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField("Должность", max_length=100)
    department = models.CharField("Подразделение", max_length=100)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Руководитель"
    )
    is_hr = models.BooleanField("HR-специалист", default=False)

🔗 Связь: User ←→ Employee (1:1)
🔄 Иерархия: сотрудник может иметь одного руководителя, у руководителя — много подчинённых.

attendance.AbsenceType — тип отсутствия
Определяет виды отсутствия (отпуск, больничный и др.).

python
class AbsenceType(models.Model):
    code = models.CharField("Код", max_length=10, unique=True)  # например, '01', '09'
    name = models.CharField("Название", max_length=100)
    color = models.CharField("Цвет", max_length=7, default="#007bff")  # HEX

    🎨 Примеры:

01 — Работа по графику (#007bff)
09 — Ежегодный отпуск (#28a745)
19 — Больничный (#dc3545)
38 — Удалённая работа (#ffc107)

attendance.AttendanceRecord — запись в табеле
Фиксирует статус сотрудника по дням.

class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField("Дата")
    absence_type = models.ForeignKey(AbsenceType, on_delete=models.PROTECT)
    comment = models.TextField("Комментарий", blank=True)
    is_confirmed = models.BooleanField("Подтверждено", default=False)
    confirmed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='confirmed_records')

📅 Уникальность: (employee, date) — один сотрудник не может иметь две записи в день.
✅ Подтверждение: руководитель подтверждает запись, система отмечает is_confirmed=True.

User
  │
  └── Employee (1:1)
        │
        ├── manager → Employee (самоотношение)
        │
        └── AttendanceRecord (1:N)
              │
              └── AbsenceType (N:1)

🗂️ Приложения
Приложение	Назначение
employees	Управление профилями, иерархией, правами
attendance	Учёт посещаемости, табель, подтверждение
hr_system	Настройки, URL, аутентификация
🛠️ База данных
Используется SQLite (для разработки)
Для продакшена рекомендуется PostgreSQL
Миграции: python manage.py makemigrations / migrate