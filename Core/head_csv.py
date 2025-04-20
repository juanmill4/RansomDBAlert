import os
import re
import csv
import shutil
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]"
    r"+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]"
    r"+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+"
    r"|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+"
    r"|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)

def procesar_csv(archivo_path, subdirectorio):
    """
    Verifica si el archivo CSV contiene columnas 'name'/'email' o
    direcciones de correo en las primeras 10 líneas.
    Si las contiene, mueve el CSV a 'subdirectorio'. Si no, lo elimina.
    """
    try:
        # Intentar leer con codificación UTF-8
        try:
            df = pd.read_csv(archivo_path, encoding='utf-8', on_bad_lines='skip', nrows=20)
        except UnicodeDecodeError:
            print(f"Error de codificación en {archivo_path}, probando con 'ISO-8859-1'.")
            return

        # Verificar columnas (minúsculas para que sea más robusto)
        columnas = df.columns.str.lower()
        contiene_cabecera = any(col in columnas for col in ["name", "email"])

        # Revisar las primeras 10 líneas como texto para ver si hay emails
        contiene_email_regex = False
        with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as file:
            for i, line in enumerate(file):
                if i >= 10:
                    break
                if email_regex.search(line):
                    contiene_email_regex = True
                    break

        # Si hay cabecera 'name'/'email' o hay coincidencia de email en las primeras 10 líneas
        if contiene_cabecera or contiene_email_regex:
            print(f"Moviendo (cabecera/email detectado).")
            shutil.move(archivo_path, os.path.join(subdirectorio, os.path.basename(archivo_path)))
        else:
            print(f"{archivo_path} no contiene 'name', 'email' ni emails en las primeras 10 líneas. Eliminando.")
            os.remove(archivo_path)

    except Exception as e:
        print(f"Error al procesar archivo {archivo_path}: {e}")
        os.remove(archivo_path)

def csv_filter(directorio):
    """
    Función principal para filtrar archivos CSV. 
    1) Crea un subdirectorio (si no existe),
    2) Procesa cada CSV con `procesar_csv(...)` en paralelo.
    
    :param directorio: Carpeta donde buscar los CSV.
    :param subdirectorio: Carpeta donde mover los CSV que cumplan la condición. 
                          Si no se especifica, se crea un subdirectorio "CSV_filtrados"
                          dentro de `directorio`.
    :param email_regex: Expresión regular para detectar emails.
    """
    subdirectorio = os.path.join(directorio, "CSV_filtrados")

    if not os.path.exists(subdirectorio):
        os.makedirs(subdirectorio)


    # Obtener lista de CSV en el directorio
    archivos_csv = [
        os.path.join(directorio, f) for f in os.listdir(directorio)
        if f.lower().endswith(".csv")
    ]

    json_files = [f for f in os.listdir(directorio) if f.lower().endswith(".json")]


    for json_file in json_files:
        json_p = os.path.join(input_dir, json_file)
        shutil.move(json_p, output_dir)

    # Procesamos en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                procesar_csv,
                archivo,
                subdirectorio
            )
            for archivo in archivos_csv
        ]
        for future in futures:
            future.result()

    return subdirectorio

# Permite que se ejecute desde la línea de comandos como script
if __name__ == "__main__":
    # Ejemplo de uso: filtra los CSV en el directorio "CSV_filtrados"
    csv_filter("/Dir_basesdatos/")
