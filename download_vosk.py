import urllib.request
import zipfile
import os
import shutil

url = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
zip_path = "vosk_model.zip"
extract_path = "config/vosk-model-small-es-0.42"
target_path = "config/vosk_model"

print("Downloading Vosk Spanish model (39MB)...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall("config")

print("Renaming...")
if os.path.exists(target_path):
    shutil.rmtree(target_path)
os.rename(extract_path, target_path)

print("Cleaning up...")
os.remove(zip_path)

print("Done! Vosk model installed at", target_path)
