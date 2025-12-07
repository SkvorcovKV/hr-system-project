# employees/forms.py
from django import forms
from .models import EmployeeProfile
from django.utils.safestring import mark_safe

COLOR_CHOICES = [
    ("#3498db", "Синий"),
    ("#e74c3c", "Красный"),
    ("#2ecc71", "Зелёный"),
    ("#f39c12", "Оранжевый"),
    ("#9b59b6", "Фиолетовый"),
    ("#1abc9c", "Бирюзовый"),
    ("#34495e", "Тёмно-серый"),
    ("#e67e22", "Тыквенный"),
    ("#16a085", "Изумрудный"),
    ("#8e44ad", "Тёмно-фиолетовый"),
]

class ColorPickerWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = [
            forms.RadioSelect(choices=[
                (value, mark_safe(f'<span style="color:{value};">■</span> {label}'))
                for value, label in COLOR_CHOICES
            ]),
            forms.TextInput(attrs={'type': 'color', 'style': 'height: 30px; width: 50px;'}),
            forms.TextInput(attrs={'placeholder': '#3498db', 'size': 10}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, value, value]
        return [None, '#3498db', '#3498db']

    def format_output(self, rendered_widgets):
        # Генерируем HTML с предпросмотром
        return f"""
        <div style="font-family: sans-serif; line-height: 1.6;">
            <div style="margin-bottom: 10px;">
                <b>Выберите цвет:</b>
            </div>

            <!-- Быстрые цвета -->
            <div style="margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center;">
                {rendered_widgets[0]}
            </div>

            <!-- Пикер и ввод -->
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <b>Пикер:</b> {rendered_widgets[1]} 
                <b>Или введите:</b> {rendered_widgets[2]}
            </div>

            <!-- Предпросмотр цвета -->
            <div style="display: flex; align-items: center; gap: 10px;">
                <b>Текущий цвет:</b>
                <div id="color-preview" style="
                    width: 32px; 
                    height: 32px; 
                    border: 2px solid #ccc; 
                    border-radius: 6px; 
                    background-color: #3498db; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                </div>
                <span id="color-value" style="font-family: monospace; font-size: 14px;">#3498db</span>
            </div>

            <!-- Скрипт для обновления предпросмотра -->
            <script>
                (function() {{
                    const widgets = document.currentScript.parentNode.querySelectorAll('input');
                    const preview = document.getElementById('color-preview');
                    const valueSpan = document.getElementById('color-value');

                    function updatePreview(color) {{
                        preview.style.backgroundColor = color;
                        valueSpan.textContent = color;
                    }}

                    // Обновляем при изменении любого поля
                    widgets.forEach(input => {{
                        input.addEventListener('change', function() {{
                            let color = '#3498db';

                            // Приоритет: текстовое поле → пикер → радио
                            if (input.type === 'text' && input.value.startsWith('#') && input.value.length === 7) {{
                                color = input.value;
                            }} else if (input.type === 'color') {{
                                color = input.value;
                            }} else if (input.type === 'radio' && input.checked) {{
                                color = input.value;
                            }}

                            // Обновляем все поля, чтобы синхронизировать
                            widgets.forEach(inp => {{
                                if (inp.type === 'color' && inp.value !== color) inp.value = color;
                                if (inp.type === 'text' && inp.placeholder) inp.value = color;
                            }});

                            updatePreview(color);
                        }});
                    }});

                    // Инициализация
                    updatePreview('#3498db');
                }})();
            </script>
        </div>
        """    
class ColorPickerField(forms.MultiValueField):
    """Поле, которое объединяет выбор цвета"""
    widget = ColorPickerWidget

    def __init__(self, *args, **kwargs):
        fields = [
            forms.ChoiceField(choices=[(v, v) for v, _ in COLOR_CHOICES], required=False),
            forms.CharField(max_length=7),
            forms.CharField(max_length=7),
        ]
        super().__init__(fields, *args, required=True, **kwargs)

    def compress(self, data_list):
        # Берём последнее непустое значение
        return next((value for value in reversed(data_list) if value), '#3498db')


class EmployeeProfileForm(forms.ModelForm):
    color_code = ColorPickerField(
        label="Цвет в графике отпусков",
        help_text="Выберите цвет из палитры, через пикер или введите HEX-код."
    )

    class Meta:
        model = EmployeeProfile
        fields = ['user', 'department', 'position', 'hire_date', 'phone', 'avatar', 'color_code']

    class Media:
        css = {
            'all': ('css/admin_color_radio.css',)  # можно оставить или удалить — не обязательно
        }
        # Важно: 'user' здесь, потому что в админке мы выбираем пользователя



