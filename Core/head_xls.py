import os
import re
import shutil
import subprocess
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)



def convert_xls_to_xlsx(xls_file):
    """
    Convierte un archivo .xls a .xlsx utilizando LibreOffice en modo headless.
    Retorna la ruta del nuevo archivo .xlsx o None si falla.
    """
    try:
        parent_dir = os.path.dirname(xls_file)
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to",
            "xlsx",
            xls_file
        ], cwd=parent_dir, check=True)

        base, _ = os.path.splitext(xls_file)
        new_file = base + ".xlsx"

        if os.path.exists(new_file):
            return new_file
        else:
            return None
    except Exception as e:
        print(f"Error convirtiendo {xls_file} a XLSX: {e}")
        return None

def procesar_xlsx(archivo_path, subdirectorio):
    """
    Procesa el archivo XLSX para verificar si contiene cabeceras
    'name'/'email' o correos en las primeras 10 filas.
    Si se cumple, mueve el archivo al subdirectorio; si no, lo elimina.
    """
    try:
        # Intentar leer el archivo XLSX (se leen hasta 20 filas)
        try:
            df = pd.read_excel(archivo_path, nrows=20)
        except Exception as e:
            print(f"Error leyendo {archivo_path}: {e}. Eliminando archivo.")
            os.remove(archivo_path)
            return

        # Verificar las cabeceras (convertidas a minúsculas)
        columnas = [str(col).lower() for col in df.columns]
        contiene_cabecera = any(col in columnas for col in ["name", "email"])

        # Verificar las primeras 10 filas buscando emails en cada celda (si es string)
        contiene_email_regex = False
        num_rows = min(len(df), 10)
        for i in range(num_rows):
            for cell in df.iloc[i]:
                if isinstance(cell, str) and email_regex.search(cell):
                    contiene_email_regex = True
                    break
            if contiene_email_regex:
                break

        # Mover o eliminar el archivo según se detecten las coincidencias
        if contiene_cabecera or contiene_email_regex:
            print(f"Moviendo {archivo_path} (cabecera o email detectado).")
            shutil.move(archivo_path,
                        os.path.join(subdirectorio, os.path.basename(archivo_path)))
        else:
            print(f"{archivo_path} no contiene 'name', 'email' ni emails en las primeras 10 filas. Eliminando.")
            os.remove(archivo_path)

    except Exception as e:
        print(f"Error al procesar {archivo_path}: {e}. Eliminando archivo.")
        if os.path.exists(archivo_path):
            os.remove(archivo_path)

def xlxs_filter(directorio, subdirectorio=None):
    """
    Función principal que:
    1) Crea un subdirectorio si no existe
    2) Busca archivos .xls/.xlsx en 'directorio'
    3) Convierte .xls a .xlsx usando LibreOffice en modo headless
    4) Verifica si los .xlsx contienen 'name', 'email' o correos en las primeras 10 filas
    5) Mueve los que cumplan la condición a 'subdirectorio', elimina el resto
    """

    # Si no pasas 'subdirectorio', se crea por defecto "XLSX_filtrados" dentro de `directorio`
    if subdirectorio is None:
        subdirectorio = os.path.join(directorio, "XLSX_filtrados")
    if not os.path.exists(subdirectorio):
        os.makedirs(subdirectorio)

    # Lista de archivos Excel (.xls o .xlsx)
    archivos_excel = [
        os.path.join(directorio, f)
        for f in os.listdir(directorio)
        if f.lower().endswith(".xls") or f.lower().endswith(".xlsx")
    ]

    # Convertir los .xls a .xlsx
    archivos_convertidos = []
    for archivo in archivos_excel:
        if archivo.lower().endswith(".xls"):
            nuevo_archivo = convert_xls_to_xlsx(archivo)
            if nuevo_archivo:
                archivos_convertidos.append(nuevo_archivo)
                # Eliminar el archivo .xls original para evitar duplicados
                os.remove(archivo)
            else:
                print(f"La conversión falló para {archivo}")
        else:
            # Si ya es .xlsx, no se convierte
            archivos_convertidos.append(archivo)

    # Procesar los archivos XLSX en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(procesar_xlsx, archivo, subdirectorio)
            for archivo in archivos_convertidos
        ]
        for future in futures:
            future.result()

    return subdirectorio

# Para permitir que se ejecute directamente desde línea de comandos:
if __name__ == "__main__":
    ruta_directorio = "Dir_basesdatos/"
    procesar_archivos_excel(ruta_directorio)
