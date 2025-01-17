import os
import bpy
import time
from flask import Flask, render_template, request, send_from_directory




current_dir = os.getcwd()
path_to_jpeg_folder = os.path.join(current_dir, "../uploads")
hdri_image_path = os.path.join(current_dir, "../assets", "studio.hdr")
uploads_folder = os.path.join(current_dir, "../uploads")
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
    
    upload_path = os.path.join(uploads_folder, uploaded_file.filename)
    uploaded_file.save(upload_path)
    
    try:
        
        
    # Импортируем GLB файл
        bpy.ops.import_scene.gltf(filepath=upload_path)
        # Удаление куба по умолчанию
        if "Cube" in bpy.data.objects:
            object_to_delete = bpy.data.objects["Cube"]
            bpy.data.objects.remove(object_to_delete, do_unlink=True)
        
        # Настройка HDRI
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world
            
        world.use_nodes = True
        
        # Добавляем узлы
        env_texture_node = world.node_tree.nodes.new(type='ShaderNodeTexEnvironment')

        # hdri_image_path = os.path.join(hdri_folder, hdri_files[0])


        env_texture_node.image = bpy.data.images.load(hdri_image_path)
        # Текстурные координаты
        tex_coord_node = world.node_tree.nodes.new(type='ShaderNodeTexCoord')
        
        # Отображение
        mapping_node = world.node_tree.nodes.new(type='ShaderNodeMapping')
        
        # Фоновый узел
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node is None:
            bg_node = world.node_tree.nodes.new(type='ShaderNodeBackground')
        # Соединяем узлы
        links = world.node_tree.links
        links.new(tex_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], env_texture_node.inputs['Vector'])
        links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])
        # Установка количества семплов 
        bpy.context.scene.cycles.samples = 128

        # Настройка выхода
        output_filename = os.path.splitext(uploaded_file.filename)[0] + '.jpeg'
        output_filepath = os.path.join(path_to_jpeg_folder, output_filename)
        
        bpy.context.scene.render.filepath = output_filepath
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        start_time = time.time()
        # Рендер и сохранение
        bpy.ops.render.render(write_still=True)
        end_time = time.time()
        render_time = end_time - start_time

    except Exception as e:
        return f"Ошибка при импорте файла: {str(e)}", 500
    
    return render_template('index.html', download_link=output_filename, render_time=render_time)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(path_to_jpeg_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
