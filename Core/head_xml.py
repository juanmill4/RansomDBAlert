# procesar_xml.py
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

# Expresión regular a nivel de módulo
email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)

def procesar_xml(archivo_path, subdirectorio):
    """
    Lee un archivo .xml y determina si debe moverse al subdirectorio.
    Criterios:
     - Contiene 'email' (en minúsculas) en TODO el contenido
     - O las primeras 10 líneas contienen un email válido (email_regex)
    """
    try:
        mover_archivo = False

        # 1) Revisa todo el archivo para detectar 'email'
        with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as file:
            contenido = file.read()
            if "email" in contenido.lower():
                mover_archivo = True

        # 2) Si no se movió, revisa las primeras 10 líneas con la regex
        if not mover_archivo:
            with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as file:
                for i, line in enumerate(file):
                    if i >= 10:
                        break
                    if email_regex.search(line):
                        mover_archivo = True
                        break

        # 3) Mover o informar
        if mover_archivo:
            print(f"Moviendo {archivo_path} (contiene 'email' o patrón de email).")
            shutil.move(archivo_path,
                        os.path.join(subdirectorio, os.path.basename(archivo_path)))
        else:
            print(f"{archivo_path} no contiene 'email' ni patrón de email en las primeras 10 líneas.")
            os.remove(archivo_path)
    except Exception as e:
        print(f"Error al procesar {archivo_path}: {e}")


def xml_filter(directorio, nombre_subdir="XML_filtrados"):
    """
    Función principal que:
    1) Crea el subdirectorio 'nombre_subdir' dentro de 'directorio'
    2) Busca archivos .xml
    3) Revisa cada archivo (en paralelo) y decide si se mueve o se ignora
    """
    subdirectorio = os.path.join(directorio, nombre_subdir)
    if not os.path.exists(subdirectorio):
        os.makedirs(subdirectorio)

    # Lista de archivos XML en el directorio
    archivos_xml = [
        os.path.join(directorio, f)
        for f in os.listdir(directorio)
        if f.lower().endswith(".xml")
    ]

    # Procesarlos en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(procesar_xml, archivo, subdirectorio)
            for archivo in archivos_xml
        ]
        for future in futures:
            future.result()

    return subdirectorio

# Para que se ejecute como script independiente:
if __name__ == "__main__":
    ruta = "Dir_basesdatos"
    filtrar_archivos_xml(ruta)
