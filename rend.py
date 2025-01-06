import os
import bpy

# Папки с glb и для jpeg
input_folder = "D:/work/gltf"  
output_folder = "D:/work/jpeg" 


os.makedirs(output_folder, exist_ok=True)

# Список файлов
gltf_files = [f for f in os.listdir(input_folder) if f.endswith(('.glb'))]

for gltf_file in gltf_files:
    
    file_path = os.path.join(input_folder, gltf_file)

    # Импорт
    bpy.ops.import_scene.gltf(filepath=file_path)
    
    
    # Настройка выходного файла
    output_filename = os.path.splitext(gltf_file)[0] + '.jpeg'
    output_filepath = os.path.join(output_folder, output_filename)
    
    # Удаляю куб по умолчанию
    if "Cube" in bpy.data.objects:
        object_to_delete = bpy.data.objects["Cube"]
        bpy.data.objects.remove(object_to_delete, do_unlink=True)
    
    # Настройки рендеринга
    bpy.context.scene.render.filepath = output_filepath
    bpy.context.scene.render.image_settings.file_format = 'JPEG'

    # Рендер и сохранение файла
    bpy.ops.render.render(write_still=True)

    # Очищаем объекты для следующего импорта
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

print(f"Рендеринг завершен. Файл сохранился в формате JPEG.")