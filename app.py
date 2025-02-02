import os
import bpy
import time
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, session
from flask_session import Session

current_dir = os.getcwd()
path_to_jpeg_folder = os.path.join(current_dir, "../uploads")
hdri_image_path = os.path.join(current_dir, "../assets", "studio.hdr")
uploads_folder = os.path.join(current_dir, "../uploads")
rendered_samples = 0
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False #время жизни сессии, при закрытии браузера закроется.
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def show_main_page():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_file_upload():
    global rendered_samples
    session.clear()
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

        # Настройка выхода
        output_filename = os.path.splitext(uploaded_file.filename)[0] + '.jpeg'
        output_filepath = os.path.join(path_to_jpeg_folder, output_filename)

        bpy.context.scene.render.filepath = output_filepath
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        # Установка количества семплов
        bpy.context.scene.cycles.samples = 64
        start_time = time.time()
        # Рендер и сохранение

        #bpy.app.handlers.render_post.append(save) вывод прогресса в консоль если надо
        #bpy.app.handlers.render_complete.append(end)
        for sample in range(total_samples):
            bpy.ops.render.render(write_still=True)  # Рендер текущего кадра
            rendered_samples += 1
            render_stats(bpy.context.scene)

        end_time = time.time()
        render_time = end_time - start_time

    except Exception as e:
        return f"Ошибка при импорте файла: {str(e)}", 500

    return render_template('index.html', download_link=output_filename, render_time=render_time)

scene = bpy.context.scene
total_samples = scene.cycles.samples

render_status = {}
#Запись в сессию статы и времени
def render_stats(scene):
    progress = (rendered_samples / total_samples) * 100

    print(f'Прогресс рендеринга: {progress:.2f}% ({rendered_samples}/{total_samples} сэмплов)')

    render_status['render_stats'] = f"Рендеринг... {progress:.2f}% ({rendered_samples}/{total_samples} обработано)"

    if progress >= 100:
        render_status['render_stats'] = f'Завершено!'

@app.route('/poll', methods=['GET'])
def poll():
    if 'render_stats' in render_status:
        return jsonify(render_status), 200
    return jsonify({"Info": "Нет данных"}), 204

#Для вывода в консоль если надо-
#def save(scene):
#    print("Сохранение изображения..")
#def end(scene):
#print("Рендер завершен.")

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(path_to_jpeg_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
