# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Папка для загрузки файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Убедитесь, что папка для загрузки существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def show_main_page():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_file_upload():
    if 'file' not in request.files:
        return "Файл не выбран", 400
    
    uploaded_file = request.files['file']
    
    if uploaded_file.filename == '':
        return "Файл не выбран", 400
    
    # Сохранение файла в папку uploads
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(file_path)
    
    return f"Файл '{uploaded_file.filename}' успешно загружен!"

if __name__ == '__main__':
    app.run(debug=True)
