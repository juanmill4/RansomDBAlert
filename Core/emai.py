import re
import json
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

FROM = "TXT Archive"

directorio = "/home/juan/Descargas/honeywell/Dir_texto"  # Ruta principal
subdirectorio = os.path.join(directorio, "Process_TXT_JSON")


# Crear el subdirectorio si no existe
if not os.path.exists(subdirectorio):
    os.makedirs(subdirectorio)

# Lista de archivos XML en el directorio
archivos_txt = [
    f for f in os.listdir(directorio)
    if os.path.isfile(os.path.join(directorio, f))  # Filtra solo archivos
]


# Expresión regular para extraer emails RFC 2822
email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)

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

# Conjunto en memoria para los hashes ya procesados
procesados = set()
lock = Lock()  # Bloqueo para evitar problemas de concurrencia en el set

def extraer_emails(archivo, subdirectorio, limite_contexto=100, max_lineas=5000):
    archivo_path = os.path.join(directorio, archivo)
    print(archivo_path)
    # Calculamos el hash del archivo
    file_hash = generar_hash_archivo(archivo_path)
    
    # Verificamos si ya fue procesado
    with lock:
        if file_hash in procesados:
            print(f"El archivo '{archivo}' ya fue procesado anteriormente. Se omite.")
            os.remove(archivo_path)
            return
        else:
            # Marcamos como procesado para evitar que otro hilo lo haga
            procesados.add(file_hash)

    salida_json = os.path.join(subdirectorio, f"{archivo}.json")

    try:
        correos_unicos = {}
        email_found = False  # Bandera para detectar si se encontró al menos un email
        with open(archivo_path, 'r', encoding='utf-8', errors='ignore') as f:
            for num_linea, linea in enumerate(f, start=1):
                matches = email_regex.finditer(linea)
                for match in matches:
                    email = match.group(0)
                    start_idx = max(match.start() - limite_contexto, 0)
                    end_idx = min(match.end() + limite_contexto, len(linea))
                    contexto = linea[start_idx:end_idx].strip()
                    
                    ID = generate_id(email, contexto)
                    if email not in correos_unicos:
                        correos_unicos[email] = {
                            "email_context": contexto,
                            "ID": ID,
                            "FROM": FROM
                        }
                    # Se marca que se encontró al menos un email
                    email_found = True
                
                # Si aún no se encontró ningún email y se llegó al límite, se interrumpe la lectura
                if not email_found and num_linea >= max_lineas:
                    print(f"Ningún correo encontrado en las primeras {max_lineas} líneas del archivo '{archivo}'. Se omite.")
                    os.remove(archivo_path)
                    return

        if correos_unicos:
            with open(salida_json, 'w', encoding='utf-8') as json_file:
                json.dump(correos_unicos, json_file, ensure_ascii=False, indent=4)
            print(f"Correos extraídos y guardados en '{salida_json}' ({len(correos_unicos)} emails).")
        else:
            print(f"Ningún correo encontrado en las primeras 5000 líneas del archivo '{archivo}'.")
        
        os.remove(archivo_path)

    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error procesando '{archivo}': {e}")


# Procesamos archivos en paralelo
if __name__ == "__main__":
    with ThreadPoolExecutor() as executor:
        # Creamos las tareas
        futures = [executor.submit(extraer_emails, archivo, subdirectorio) for archivo in archivos_txt]
        # Esperamos que todas terminen (capturamos excepciones si queremos)
        for future in futures:
            try:
                future.result()
            except Exception as exc:
                print(f"Error ejecutando hilo: {exc}")