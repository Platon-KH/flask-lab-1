from flask import Flask, render_template, request, send_from_directory
import os
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Конфигурация
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'super-secret-key'

# Разрешенные расширения
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_directories():
    """Создаёт необходимые директории"""
    directories = ['static/uploads', 'static/results', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Создаём директории при старте
create_directories()

# ============================================================================
# ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ВАРИАНТА 20
# ============================================================================

def spiral_shift_image(image_array, shift_pixels, num_layers):
    """
    Вариант 20: Сдвиг по замкнутым прямоугольным составляющим
    
    image_array: numpy array изображения (H, W, 3)
    shift_pixels: количество пикселов для сдвига
    num_layers: количество прямоугольных рамок
    """
    if len(image_array.shape) != 3:
        raise ValueError("Требуется RGB изображение")
    
    height, width, channels = image_array.shape
    result = image_array.copy()
    
    # Ограничиваем количество слоёв
    max_layers = min(height // 2, width // 2)
    actual_layers = min(num_layers, max_layers)
    
    print(f"Обработка {actual_layers} рамок, сдвиг {shift_pixels} пикселов")
    
    for layer in range(actual_layers):
        top = layer
        bottom = height - layer - 1
        left = layer
        right = width - layer - 1
        
        # Пропускаем если рамка слишком маленькая
        if bottom - top < 2 or right - left < 2:
            continue
        
        # Вычисляем периметр текущей рамки
        perimeter = 2 * (bottom - top + right - left)
        
        # Корректируем сдвиг для текущей рамки (уменьшаем к центру)
        current_shift = shift_pixels % perimeter if perimeter > 0 else 0
        
        if current_shift == 0:
            continue
        
        # Извлекаем пиксели рамки
        pixels = []
        
        # Верх (слева направо)
        for x in range(left, right):
            pixels.append(result[top, x].copy())
        
        # Право (сверху вниз)
        for y in range(top + 1, bottom):
            pixels.append(result[y, right].copy())
        
        # Низ (справа налево)
        for x in range(right, left, -1):
            pixels.append(result[bottom, x].copy())
        
        # Лево (снизу вверх)
        for y in range(bottom - 1, top, -1):
            pixels.append(result[y, left].copy())
        
        # Применяем циклический сдвиг
        pixels = pixels[-current_shift:] + pixels[:-current_shift]
        
        # Возвращаем пиксели на место
        idx = 0
        
        # Верх
        for x in range(left, right):
            result[top, x] = pixels[idx]
            idx += 1
        
        # Право
        for y in range(top + 1, bottom):
            result[y, right] = pixels[idx]
            idx += 1
        
        # Низ
        for x in range(right, left, -1):
            result[bottom, x] = pixels[idx]
            idx += 1
        
        # Лево
        for y in range(bottom - 1, top, -1):
            result[y, left] = pixels[idx]
            idx += 1
    
    return result

def create_color_histogram(image_array, filename):
    """Создаёт гистограмму распределения цветов"""
    try:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        colors = ['Red', 'Green', 'Blue']
        
        for i in range(3):
            channel = image_array[:, :, i].flatten()
            axes[i].hist(channel, bins=50, color=colors[i].lower(), 
                        alpha=0.7, density=True)
            axes[i].set_title(f'Распределение {colors[i]} канала')
            axes[i].set_xlabel('Интенсивность (0-255)')
            axes[i].set_ylabel('Частота')
            axes[i].grid(True, alpha=0.3)
        
        plt.suptitle(f'Гистограмма цветов: {filename}', fontsize=14)
        plt.tight_layout()
        
        # Сохраняем
        chart_path = f'static/results/chart_{filename}'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"Ошибка создания гистограммы: {e}")
        return None

# ============================================================================
# РОУТЫ FLASK
# ============================================================================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Обработка загрузки и обработки изображения"""
    if request.method == 'POST':
        # Проверяем, что файл есть
        if 'file' not in request.files:
            return render_template('index.html', error='Файл не выбран')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='Файл не выбран')
        
        if not allowed_file(file.filename):
            return render_template('index.html', 
                                 error='Разрешены только PNG, JPG, JPEG, GIF, BMP')
        
        # Получаем параметры
        try:
            shift = int(request.form.get('shift', 10))
            layers = int(request.form.get('layers', 5))
            
            if shift < 1 or shift > 100:
                return render_template('index.html', error='Сдвиг должен быть от 1 до 100')
            if layers < 1 or layers > 20:
                return render_template('index.html', error='Количество рамок должно быть от 1 до 20')
                
        except ValueError:
            return render_template('index.html', error='Неверные параметры')
        
        # Сохраняем файл
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)
        
        try:
            # Открываем и обрабатываем изображение
            img = Image.open(original_path)
            
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            
            # Применяем спиральный сдвиг (ВАРИАНТ 20)
            processed_array = spiral_shift_image(img_array, shift, layers)
            
            # Сохраняем результат
            processed_img = Image.fromarray(processed_array)
            processed_filename = f'processed_{filename}'
            processed_path = os.path.join('static/results', processed_filename)
            processed_img.save(processed_path)
            
            # Создаём гистограмму
            chart_path = create_color_histogram(img_array, filename)
            
            # Возвращаем результат
            return render_template('result.html',
                                 original=f'static/uploads/{filename}',
                                 processed=f'static/results/{processed_filename}',
                                 chart=chart_path,
                                 shift=shift,
                                 layers=layers,
                                 filename=filename)
            
        except Exception as e:
            return render_template('index.html', 
                                 error=f'Ошибка обработки: {str(e)}')
    
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Тестовая страница для CI"""
    return "Flask приложение работает! ✅"

@app.route('/health')
def health_check():
    """Проверка здоровья приложения"""
    return "OK", 200

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Отдача статических файлов"""
    return send_from_directory('static', filename)

# ============================================================================
# ДЛЯ ЛАБОРАТОРНОЙ РАБОТЫ (разделы 2.6, 2.7)
# ============================================================================

@app.route('/data_to')
def data_to():
    """Пример из методички - передача данных в шаблон"""
    data = {
        'user': 'Иван',
        'color': 'красный',
        'title': 'Пример работы шаблонов Flask',
        'values': [1, 2, 3, 4, 5]
    }
    return render_template('data_to.html', data=data)

@app.route('/form_example', methods=['GET', 'POST'])
def form_example():
    """Пример формы (раздел 2.7)"""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        return render_template('form_result.html', name=name, email=email)
    return render_template('form_example.html')

if __name__ == '__main__':
    # Создаём тестовое изображение при запуске
    if not os.path.exists('static/test_image.png'):
        test_img = Image.new('RGB', (300, 300), color='blue')
        for i in range(100, 200):
            for j in range(100, 200):
                test_img.putpixel((i, j), (255, 0, 0))  # Красный квадрат
        test_img.save('static/test_image.png')
        print("Создано тестовое изображение: static/test_image.png")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
