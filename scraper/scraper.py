import os
import subprocess

#obtener el directorio actual
cur_dir = os.getcwd()

#obtener los archivos en el directorio
arch_dir = os.listdir(cur_dir)

#iterar sobre los archivos y ejecutar los archivos .py
for arch in arch_dir:
    if arch.endswith(".py") and arch != os.path.basename(__file__): #esto ultimo es para que no se ejecute este archivo
        file_path = os.path.join(cur_dir, arch)
        print(f"Ejecutando {file_path}...")
        subprocess.run(['python', file_path])