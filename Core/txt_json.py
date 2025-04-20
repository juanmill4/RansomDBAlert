import re
import json
import os
import hashlib
import math
import magic
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# Conjunto en memoria para los hashes ya procesados
procesados = set()
lock = Lock()  # Bloqueo para evitar problemas de concurrencia en el set

# Expresión regular para extraer emails RFC 2822
email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)


def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+'
    return re.findall(email_pattern, text)

def generar_hash_archivo(ruta):
    """Genera el SHA1 del contenido de un archivo."""
    sha1 = hashlib.sha1()
    with open(ruta, 'rb') as f:
        while True:
            data = f.read(8192)  # Leer en bloques
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def generate_id(email, email_context):
    unique_string = f"{email}_{email_context}"
    return hashlib.sha1(unique_string.encode()).hexdigest()


def extraer_emails(archivo, directorio, subdirectorio, limite_contexto=150):
    archivo_path = os.path.join(directorio, archivo)
    print(f"Procesando: {archivo}")

    # Calculamos el hash y verificamos duplicados
    file_hash = generar_hash_archivo(archivo_path)
    with lock:
        if file_hash in procesados:
            print(f"Archivo '{archivo}' ya procesado. Omitiendo.")
            os.remove(archivo_path)
            return
        procesados.add(file_hash)

    salida_json = os.path.join(subdirectorio, f"{archivo}.json")
    correos_unicos = {}

    try:
        with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
            for num_linea, linea in enumerate(f, start=1):
                try:
                    # Intento con regex complejo primero
                    matches = list(email_regex.finditer(linea))
                    emails = [match.group(0) for match in matches]

                except Exception as e:
                    print(f"Error con regex complejo en {archivo}, línea {num_linea}: {e}")
                    continue

                # Procesamiento normal de emails encontrados
                for email in emails:
                    # Verificación adicional solo para regex simple
                    if not usar_regex_simple:
                        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                            continue

                    # Obtener contexto
                    email_pos = linea.find(email)
                    start_idx = max(email_pos - limite_contexto, 0)
                    end_idx = min(email_pos + len(email) + limite_contexto, len(linea))
                    contexto = linea[start_idx:end_idx].strip()

                    # Guardar email
                    ID = generate_id(email, contexto)
                    if email not in correos_unicos:
                        correos_unicos[email] = {
                            "email_context": contexto,
                            "ID": ID,
                            "FROM": archivo
                        }

        # Guardar resultados y limpiar
        if correos_unicos:
            with open(salida_json, 'w', encoding='utf-8') as json_file:
                json.dump(correos_unicos, json_file, ensure_ascii=False, indent=4)
            print(f"Correos extraídos y guardados en '{salida_json}' ({len(correos_unicos)} emails).")
        else:
            print(f"Ningún correo encontrado en el archivo '{archivo}'.")

        os.remove(archivo_path)  # Eliminar archivo original

    except Exception as e:
        print(f"Error general procesando '{archivo}': {e}")


def txt_to_json(ruta_directorio, nombre_subdirectorio="Process_TXT_JSON", limite_contexto=150):

    ruta_subdirectorio = os.path.join(ruta_directorio, nombre_subdirectorio)
    if not os.path.exists(ruta_subdirectorio):
        os.makedirs(ruta_subdirectorio)

    # Lista de archivos (ajusta si solo quieres .txt, filtra con endswith(".txt"))
    archivos_txt = [f for f in os.listdir(ruta_directorio) if os.path.isfile(os.path.join(ruta_directorio, f))]


    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                extraer_emails,
                archivo,
                ruta_directorio,
                ruta_subdirectorio,
                limite_contexto
            )
            for archivo in archivos_txt
        ]

        # Esperamos que todas las tareas finalicen
        for future in futures:
            try:
                future.result()
            except Exception as exc:
                print(f"Error en un hilo: {exc}")



# Procesamos archivos en paralelo
if __name__ == "__main__":

    ruta_principal = "Route"
    txt_to_json(ruta_principal)