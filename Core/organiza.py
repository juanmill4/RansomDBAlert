#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil

# Diccionario de extensiones -> carpeta de destino
file_types = {
    # PDFs
    "pdf": "Dir_PDF",
    # Imágenes
    "jpg": "Dir_Imagenes",
    "jpeg": "Dir_Imagenes",
    "png": "Dir_Imagenes",
    "bmp": "Dir_Imagenes",
    "tiff": "Dir_Imagenes",
    "svg": "Dir_Imagenes",
    "heif": "Dir_Imagenes",
    "heic": "Dir_Imagenes",
    # Documentos
    "docx": "Dir_documentos",
    "doc": "Dir_documentos",
    "odt": "Dir_documentos",
    "rtf": "Dir_documentos",
    "epub": "Dir_documentos",
    "pptx": "Dir_documentos",
    "ppt": "Dir_documentos",
    # Bases de datos
    "xlsx": "Dir_basesdatos",
    "pst": "Dir_basesdatos",
    "ods": "Dir_basesdatos",
    "xls": "Dir_basesdatos",
    "csv": "Dir_basesdatos",
    "json": "Dir_basesdatos",
    "sql": "Dir_basesdatos",
    "mdb": "Dir_basesdatos",
    "accdb": "Dir_basesdatos",
    "db": "Dir_basesdatos",
    "sqlite": "Dir_basesdatos",
    "xml": "Dir_basesdatos",
    "bson": "Dir_basesdatos",
    "ndjson": "Dir_basesdatos",
    "dump": "Dir_basesdatos",
    "pgsql": "Dir_basesdatos",
    "pgpass": "Dir_basesdatos",
    "frm": "Dir_basesdatos",
    "ibd": "Dir_basesdatos",
    "myd": "Dir_basesdatos",
    "myi": "Dir_basesdatos",
    "xql": "Dir_basesdatos",
    "dmp": "Dir_basesdatos",
    "ora": "Dir_basesdatos",
    "psql": "Dir_basesdatos",
    "nosql": "Dir_basesdatos",
    # Textos
    "yml": "Dir_texto",
    "md": "Dir_texto",
    "txt": "Dir_texto",
    "dat": "Dir_texto"
}

# Nombres de los directorios que deben persistir
REQUIRED_DIRS = {
    "Dir_texto",
    "Dir_PDF",
    "Dir_basesdatos",
    "Dir_Imagenes",
    "Dir_documentos"
}

def create_required_dirs(base_dir):
    """
    Crea los directorios requeridos en el directorio base.
    """
    for d in REQUIRED_DIRS:
        path = os.path.join(base_dir, d)
        if not os.path.exists(path):
            os.makedirs(path)

def move_file_to_directory(file_path, base_dir):
    """
    Mueve el archivo 'file_path' al directorio correspondiente dentro de 'base_dir'
    según la extensión. Si no tiene extensión, va a 'Dir_texto'. Si la extensión
    no está en el diccionario, no se mueve (luego se eliminará en remove_unwanted).
    """
    # Recupera la extensión del archivo en minúsculas
    _, extension = os.path.splitext(file_path)
    extension = extension.lower().lstrip('.')  # "pdf", "jpg", etc.

    filename = os.path.basename(file_path)

    if extension == '':
        # Si no hay extensión, mover a Dir_texto
        target_dir_name = "Dir_texto"
        target_dir = os.path.join(base_dir, target_dir_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        destination_path = os.path.join(target_dir, filename)
        shutil.move(file_path, destination_path)
    elif extension in file_types:
        # Si la extensión está en el diccionario
        target_dir_name = file_types[extension]
        target_dir = os.path.join(base_dir, target_dir_name)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        destination_path = os.path.join(target_dir, filename)
        shutil.move(file_path, destination_path)
    else:
        # Extensión no reconocida: no se mueve
        pass

def remove_unwanted_directories(base_dir):
    """
    1. Elimina de la carpeta base los archivos con extensión no reconocida (y distinta de vacía).
    2. Elimina todos los directorios dentro de 'base_dir' que no estén en la lista REQUIRED_DIRS.
    """
    # 1. Eliminar archivos no reconocidos que queden en base_dir (o subcarpetas que no sean las requeridas)
    #    Si hay subcarpetas no requeridas, se borrarán igualmente en el segundo paso.

    # Recorremos primero la raíz base_dir para borrar archivos sueltos no reconocidos
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isfile(item_path):
            _, ext = os.path.splitext(item)
            ext = ext.lower().lstrip('.')
            # Si la extensión no está en el diccionario y no es vacía => se elimina
            if ext not in file_types and ext != '':
                os.remove(item_path)

    # 2. Eliminar directorios que no sean los requeridos
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item not in REQUIRED_DIRS:
            shutil.rmtree(item_path, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Uso: python organize.py <ruta_directorio_base>")
        sys.exit(1)

    base_dir = sys.argv[1]
    if not os.path.exists(base_dir):
        print(f"Error: El directorio '{base_dir}' no existe.")
        sys.exit(1)

    # 1. Crear directorios necesarios
    create_required_dirs(base_dir)

    # 2. Recorrer el árbol de archivos y moverlos a las carpetas correspondientes
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # Evitar que busque en los directorios que acabamos de crear
        # Filtramos subdirectorios para no entrar en los que vamos a mantener
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in
                   [os.path.join(base_dir, req_dir) for req_dir in REQUIRED_DIRS]]

        for f in files:
            file_path = os.path.join(root, f)

            if os.path.islink(file_path):
                os.unlink(file_path)
                
            # Verificar el tamaño del archivo
            else:
                file_size = os.path.getsize(file_path)

                if file_size < 0.5 * 1024:  # 1 KB en bytes
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error al eliminar el archivo {file_path}: {e}")
                else:
                    move_file_to_directory(file_path, base_dir)

    # 3. Eliminar todos los archivos y directorios no deseados
    remove_unwanted_directories(base_dir)

    print("Organización completa.")



def organiza_dir(base_dir):

    # 1. Crear directorios necesarios
    create_required_dirs(base_dir)

    # 2. Recorrer el árbol de archivos y moverlos a las carpetas correspondientes
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # Evitar que busque en los directorios que acabamos de crear
        # Filtramos subdirectorios para no entrar en los que vamos a mantener
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in
                   [os.path.join(base_dir, req_dir) for req_dir in REQUIRED_DIRS]]

        for f in files:
            file_path = os.path.join(root, f)

            if os.path.islink(file_path):
                os.unlink(file_path)
                
            # Verificar el tamaño del archivo
            else:
                file_size = os.path.getsize(file_path)

                if file_size < 0.5 * 1024:  # 1 KB en bytes
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error al eliminar el archivo {file_path}: {e}")
                else:
                    move_file_to_directory(file_path, base_dir)

    # 3. Eliminar todos los archivos y directorios no deseados
    remove_unwanted_directories(base_dir)

    print("Organización completa.")



if __name__ == "__main__":
    main()
