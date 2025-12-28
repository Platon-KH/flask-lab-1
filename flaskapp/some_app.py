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
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lab20-secret'
Bootstrap(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
RESULT_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

class ShiftForm(FlaskForm):
    image = FileField('Загрузите изображение', validators=[DataRequired()])
    shift = IntegerField('Сдвиг (пиксели)', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ])
    submit = SubmitField('Обработать')

def get_rectangular_layers(h, w):
    layers = []
    top, bottom = 0, h - 1
    left, right = 0, w - 1
    while top <= bottom and left <= right:
        layer = []
        for j in range(left, right + 1):
            layer.append((top, j))
        for i in range(top + 1, bottom + 1):
            layer.append((i, right))
        if top != bottom:
            for j in range(right - 1, left - 1, -1):
                layer.append((bottom, j))
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
    out = img_array.copy()
    h, w = img_array.shape[:2]
    layers = get_rectangular_layers(h, w)
    for layer in layers:
        if not layer:
            continue
        pixels = np.array([img_array[i, j] for (i, j) in layer])
        actual_shift = shift % len(pixels)
        shifted = np.roll(pixels, actual_shift, axis=0)
        for idx, (i, j) in enumerate(layer):
            out[i, j] = shifted[idx]
    return out

def plot_histogram(img_array, path):
    plt.figure(figsize=(6, 4))
    for i, color in enumerate(['r', 'g', 'b']):
        hist, bins = np.histogram(img_array[:, :, i].flatten(), bins=256, range=(0, 256))
        plt.plot(bins[:-1], hist, color=color, alpha=0.7)
    plt.title('Распределение цветов (RGB)')
    plt.xlabel('Интенсивность')
    plt.ylabel('Частота')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

@app.route('/')
def index():
    return render_template('form_example.html')

@app.route('/data_to', methods=['GET', 'POST'])
def data_to():
    form = ShiftForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        form.image.data.save(img_path)

        img = Image.open(img_path).convert('RGB')
        img_array = np.array(img)
        shift = form.shift.data

        result_array = shift_rectangular_layers(img_array, shift)
        result_img = Image.fromarray(result_array.astype('uint8'))
        result_filename = 'result_' + filename
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        result_img.save(result_path)

        orig_hist = os.path.join(RESULT_FOLDER, 'hist_orig_' + os.path.splitext(filename)[0] + '.png')
        result_hist = os.path.join(RESULT_FOLDER, 'hist_result_' + os.path.splitext(filename)[0] + '.png')

        plot_histogram(img_array, orig_hist)
        plot_histogram(result_array, result_hist)

        return render_template('form_result.html',
                               orig_img=url_for('static', filename=f'uploads/{filename}'),
                               result_img=url_for('static', filename=f'results/{result_filename}'),
                               orig_hist=url_for('static', filename=f'results/hist_orig_{os.path.splitext(filename)[0]}.png'),
                               result_hist=url_for('static', filename=f'results/hist_result_{os.path.splitext(filename)[0]}.png')
                               )
    return render_template('form_example.html', form=form)
