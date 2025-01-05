# -*- coding: utf-8 -*-
import os
import bpy
from flask import Flask, render_template, request

app = Flask(__name__)

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
    
    file_content = uploaded_file.read()
    temp_file_path = os.path.join("/tmp", uploaded_file.filename)
    
    #открываем полученный файл
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)
    try:
        bpy.ops.import_scene.gltf(filepath=temp_file_path) #какая-то шляпа.. нужно почитать как верно связать данные файлы. Нужно ли открывать файл в блендере? и тд.. мног7о тупых вопросов :")"
        bpy.ops.render.render(write_still=True)
        return "Сё оке", 200
    
    except Exception as e:
        return f"Ошибка при импорте файла: {str(e)}", 500
    
    finally:
        #удаляем файлик
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
if __name__ == '__main__':
    app.run(debug=True)
