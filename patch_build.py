import zipfile
import os
import shutil

build_dir = r"C:\Users\Leguion T\Desktop\JARVIS-IA-main (7)\JARVIS-IA-main\build\exe.win-amd64-3.12"
lib_dir = os.path.join(build_dir, "lib")
library_zip = os.path.join(lib_dir, "library.zip")
temp_zip_dir = os.path.join(build_dir, "temp_zip")

# 1. Extraer library.zip
with zipfile.ZipFile(library_zip, 'r') as zip_ref:
    zip_ref.extractall(temp_zip_dir)

# 2. Eliminar archivos .pyc de nuestras carpetas para forzar el uso de .pyd
folders_to_delete = ["actions", "agent", "memory", "core"]
files_to_delete = ["main.pyc", "ui.pyc", "beta_config.pyc", "sitecustomize.pyc"]

for f in folders_to_delete:
    p = os.path.join(temp_zip_dir, f)
    if os.path.exists(p):
        shutil.rmtree(p)

for f in files_to_delete:
    p = os.path.join(temp_zip_dir, f)
    if os.path.exists(p):
        os.remove(p)

# 3. Volver a empaquetar library.zip
os.remove(library_zip)
with zipfile.ZipFile(library_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(temp_zip_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, temp_zip_dir)
            zipf.write(file_path, arcname)

shutil.rmtree(temp_zip_dir)
print("library.zip purgado de código byte. Listo para inyección C.")

# 4. Copiar archivos .pyd a la carpeta lib
src_clean = r"C:\Users\Leguion T\Desktop\JARVIS-IA-main (7)\JARVIS-IA-main\src_clean"
for root, _, files in os.walk(src_clean):
    for file in files:
        if file.endswith(".pyd"):
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(root, src_clean)
            dest_folder = os.path.join(lib_dir, rel_path) if rel_path != "." else lib_dir
            os.makedirs(dest_folder, exist_ok=True)
            dest_file = os.path.join(dest_folder, file)
            shutil.copy2(src_file, dest_file)
            print(f"Inyectado {file} en {dest_folder}")

print("¡Parcheo de binarios C completado exitosamente!")
