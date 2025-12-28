# some_app.py
from flask import Flask, render_template, request, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import FileField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # важно для работы без GUI
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
Bootstrap(app)

UPLOAD_FOLDER = os.path.join('flaskapp', 'static', 'uploads')
RESULT_FOLDER = os.path.join('flaskapp', 'static', 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

class ShiftForm(FlaskForm):
    image = FileField('Загрузите изображение', validators=[
        DataRequired(),
        lambda form, field: field.data.filename.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    shift = IntegerField('Сдвиг (пиксели)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ])
    submit = SubmitField('Обработать')

def shift_layer(arr, shift):
    """Циклический сдвиг 1D массива (слоя)"""
    return np.roll(arr, shift)

def get_rectangular_layers(img_array):
    """Генератор: возвращает индексы слоёв (рамок) прямоугольного изображения"""
    h, w = img_array.shape[:2]
    layers = []
    top, bottom = 0, h - 1
    left, right = 0, w - 1

    while top <= bottom and left <= right:
        layer = []
        # Верхняя горизонталь
        for j in range(left, right + 1):
            layer.append((top, j))
        # Правая вертикаль (без угла)
        for i in range(top + 1, bottom + 1):
            layer.append((i, right))
        # Нижняя горизонталь (если есть)
        if top != bottom:
            for j in range(right - 1, left - 1, -1):
                layer.append((bottom, j))
        # Левая вертикаль (без углов)
        if left != right:
            for i in range(bottom - 1, top, -1):
                layer.append((i, left))
        layers.append(layer)
        top += 1
        bottom -= 1
        left += 1
        right -= 1
    return layers

def shift_rectangular_layers(img_array, shift):
    """Сдвигает каждый прямоугольный слой изображения циклически"""
    out = img_array.copy()
    layers = get_rectangular_layers(img_array)

    for layer in layers:
        if len(layer) == 0:
            continue
        # Извлекаем пиксели слоя
        pixels = np.array([img_array[i, j] for (i, j) in layer])
        # Ограничиваем сдвиг длиной слоя
        actual_shift = shift % len(pixels) if len(pixels) > 0 else 0
        shifted_pixels = shift_layer(pixels, actual_shift)
        # Записываем обратно
        for idx, (i, j) in enumerate(layer):
            out[i, j] = shifted_pixels[idx]

    return out

def plot_color_histogram(img_array, path):
    """Сохраняет гистограмму RGB распределения"""
    plt.figure(figsize=(6, 4))
    colors = ('r', 'g', 'b')
    for i, color in enumerate(colors):
        hist, bins = np.histogram(img_array[:, :, i].flatten(), bins=256, range=(0, 256))
        plt.plot(bins[:-1], hist, color=color, alpha=0.7, label=f'{color.upper()} channel')
    plt.title('Распределение цветов (RGB)')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ShiftForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        form.image.data.save(img_path)

        shift = form.shift.data
        img = Image.open(img_path).convert('RGB')
        img_array = np.array(img)

        # Обработка
        result_array = shift_rectangular_layers(img_array, shift)
        result_img = Image.fromarray(result_array.astype('uint8'))
        result_filename = 'result_' + filename
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        result_img.save(result_path)

        # Гистограммы
        orig_hist = os.path.join(RESULT_FOLDER, 'hist_orig_' + filename.replace('.jpg', '.png').replace('.jpeg', '.png'))
        result_hist = os.path.join(RESULT_FOLDER, 'hist_result_' + filename.replace('.jpg', '.png').replace('.jpeg', '.png'))

        plot_color_histogram(img_array, orig_hist)
        plot_color_histogram(result_array, result_hist)

        return render_template('form_result.html',
                               orig_img=url_for('static', filename=f'uploads/{filename}'),
                               result_img=url_for('static', filename=f'results/{result_filename}'),
                               orig_hist=url_for('static', filename=f'results/hist_orig_{filename.replace(".jpg", ".png").replace(".jpeg", ".png")}'),
                               result_hist=url_for('static', filename=f'results/hist_result_{filename.replace(".jpg", ".png").replace(".jpeg", ".png")}')
                               )

    return render_template('form_example.html', form=form)
