# -*- coding: utf-8 -*-
import os
import bpy
from flask import Flask, render_template, request
path_to_jpeg_folder = "D:/work/jpeg"
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
        bpy.ops.import_scene.gltf(filepath=temp_file_path) 
        output_filename = os.path.splitext(uploaded_file.filename)[0] + '.jpeg'
        output_filepath = os.path.join(path_to_jpeg_folder, output_filename)

        bpy.context.scene.render.filepath = output_filepath
        bpy.context.scene.render.image_settings.file_format = "JPEG"
        bpy.ops.render.render(write_still=True)
        return {"Сё оке": output_filename}, 200
    
    except Exception as e:
        return f"Ошибка при импорте файла: {str(e)}", 500
    
    finally:
        #удаляем файлик
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(path_to_jpeg_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
