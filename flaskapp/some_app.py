from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
import io
import base64
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)

# Настройки
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаём папки если их нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/results', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def spiral_shift_image(image_array, shift_pixels, num_layers):
    """
    Сдвиг изображения по прямоугольным рамкам (спиральный эффект)
    """
    height, width = image_array.shape[:2]
    result = image_array.copy()
    
    for layer in range(min(num_layers, height//2, width//2)):
        top = layer
        bottom = height - layer - 1
        left = layer
        right = width - layer - 1
        
        # Проверяем, чтобы рамка была валидной
        if bottom <= top or right <= left:
            break
            
        # Рассчитываем сдвиг для текущей рамки (уменьшаем к центру)
        current_shift = max(1, shift_pixels - layer)
        perimeter = 2 * ((bottom - top) + (right - left)) - 4
        
        if perimeter == 0:
            continue
            
        # Нормализуем сдвиг
        current_shift = current_shift % perimeter
        
        # Извлекаем пиксели рамки
        pixels = []
        
        # Верхняя сторона
        for x in range(left, right):
            pixels.append(result[top, x])
        
        # Правая сторона
        for y in range(top, bottom):
            pixels.append(result[y, right])
        
        # Нижняя сторона (справа налево)
        for x in range(right, left, -1):
            pixels.append(result[bottom, x])
        
        # Левая сторона (снизу вверх)
        for y in range(bottom, top, -1):
            pixels.append(result[y, left])
        
        # Применяем циклический сдвиг
        if current_shift > 0:
            pixels = pixels[-current_shift:] + pixels[:-current_shift]
        
        # Возвращаем пиксели на место
        idx = 0
        
        # Верхняя сторона
        for x in range(left, right):
            result[top, x] = pixels[idx]
            idx += 1
        
        # Правая сторона
        for y in range(top, bottom):
            result[y, right] = pixels[idx]
            idx += 1
        
        # Нижняя сторона (справа налево)
        for x in range(right, left, -1):
            result[bottom, x] = pixels[idx]
            idx += 1
        
        # Левая сторона (снизу вверх)
        for y in range(bottom, top, -1):
            result[y, left] = pixels[idx]
            idx += 1
    
    return result

def create_color_histogram(image_array):
    """Создаёт график распределения цветов"""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    colors = ['Red', 'Green', 'Blue']
    
    for i, color in enumerate(colors):
        axes[i].hist(image_array[:, :, i].flatten(), bins=50, 
                    color=color.lower(), alpha=0.7, density=True)
        axes[i].set_title(f'{color} Channel Distribution')
        axes[i].set_xlabel('Intensity')
        axes[i].set_ylabel('Frequency')
        axes[i].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    
    return buf

@app.route("/")
def hello():
    return render_template('simple.html')

@app.route('/process', methods=['GET', 'POST'])
def process_image():
    if request.method == 'POST':
        # Проверяем файл
        if 'image' not in request.files:
            return render_template('simple.html', error='Нет файла изображения')
        
        file = request.files['image']
        if file.filename == '':
            return render_template('simple.html', error='Файл не выбран')
        
        if not allowed_file(file.filename):
            return render_template('simple.html', 
                                 error='Недопустимый формат файла. Используйте PNG, JPG, JPEG, GIF')
        
        # Получаем параметры
        try:
            shift_pixels = int(request.form.get('shift', 10))
            num_layers = int(request.form.get('layers', 5))
        except ValueError:
            return render_template('simple.html', error='Некорректные параметры')
        
        # Сохраняем файл
        filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(original_path)
        
        try:
            # Открываем изображение
            img = Image.open(original_path)
            img_array = np.array(img)
            
            # Проверяем формат (RGB/RGBA)
            if len(img_array.shape) == 2:  # Grayscale
                img_array = np.stack([img_array]*3, axis=-1)
            elif img_array.shape[2] == 4:  # RGBA to RGB
                img_array = img_array[:, :, :3]
            
            # Применяем спиральный сдвиг
            processed_array = spiral_shift_image(img_array, shift_pixels, num_layers)
            
            # Сохраняем результат
            processed_img = Image.fromarray(processed_array)
            processed_filename = f'processed_{filename}'
            processed_path = os.path.join('static/results', processed_filename)
            processed_img.save(processed_path)
            
            # Создаём гистограмму цветов
            histogram_buf = create_color_histogram(img_array)
            chart_filename = f'chart_{filename.split(".")[0]}.png'
            chart_path = os.path.join('static/results', chart_filename)
            
            with open(chart_path, 'wb') as f:
                f.write(histogram_buf.read())
            
            # Отображаем результат
            return render_template('simple.html',
                                 original_image=f'/static/uploads/{filename}',
                                 processed_image=f'/static/results/{processed_filename}',
                                 chart_image=f'/static/results/{chart_filename}',
                                 shift=shift_pixels,
                                 layers=num_layers)
        
        except Exception as e:
            return render_template('simple.html', 
                                 error=f'Ошибка обработки: {str(e)}')
    
    return render_template('simple.html')

@app.route("/data_to")
def data_to():
    """Пример страницы с данными (для тестов)"""
    some_pars = {'user':'Иван', 'color':'красный'}
    some_str = 'Пример работы шаблонов Flask'
    some_value = 42
    return render_template('simple.html', some_str=some_str,
                         some_value=some_value, some_pars=some_pars)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
