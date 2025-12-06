# инструкция по запуску

# Установка и запуск проекта

## 1. Клонировать репозиторий
```bash
git clone https://github.com/ваш-репозиторий/hr-system.git
cd hr-system

## 2. Активировать виртуальное окружение

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

## 3. Установить зависимости
bash
pip install -r requirements.txt

## 4. Применить миграции
bash
python manage.py migrate

## 5. Создать суперпользователя
bash
python manage.py createsuperuser

## 6. Запустить сервер
bash
python manage.py runserver

→ Открыть: http://127.0.0.1:8000

