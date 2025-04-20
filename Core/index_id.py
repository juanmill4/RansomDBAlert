import os
import json
import urllib3
import shutil
from elasticsearch import Elasticsearch, helpers    
import docker
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INDEX_NAME = "your index name"  # Nombre del índice en Elasticsearch

# Conectar a Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    http_auth=('elastic', 'Your Elasticsearch Password'),
    verify_certs=False,
)

# Crear índice si no existe
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)



def run_test_in_container(container_name, script_path):
    """
    Arranca un contenedor existente, ejecuta un script y lo para, dos veces
    """
    client = docker.from_env()
    results = []


    print(f"Iniciando ejecución")

    # Obtener el contenedor existente
    container = client.containers.get(container_name)

    try:
        # Arrancar el contenedor
        print(f"Arrancando contenedor {container_name}")
        container.start()

        # Ejecutar el script Python
        exit_code, output = container.exec_run(f"python3 {script_path}")

        # Parar el contenedor
        print(f"Parando contenedor {container_name}")
        container.stop()


    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        container.stop()
        raise


def index_json_files_one_by_one(directory_path, directory_do, id_source):
    error_files = []  # Archivos con errores
    skipped_files = []  # Archivos omitidos (sin ID o Name)

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        data = json.load(file)

                        if "Information" in data:
                            # Verificar si existen ID Number y Name
                            id_number = data["Information"].get("ID Number", "")
                            name = data["Information"].get("Name", "")

                            if not id_number and not name:
                                skipped_files.append(filename)
                                print(f"Archivo omitido (sin ID o Name): {filename}")
                                os.remove(file_path)
                                continue  # Saltar este archivo

                            # Validar y limpiar el campo Expiration Date
                            expiration_date = data["Information"].get("Expiration Date", "")
                            if not expiration_date:  # Si está vacío, asignar None
                                expiration_date = None
                            birth_date = data["Information"].get("Date of Birth", "")
                            if not birth_date:  # Si está vacío, asignar None
                                birth_date = None
                            # Agregar campo FROM (nombre del archivo sin extensión)
                            from_field = os.path.splitext(filename)[0]
                            file_path_png = os.path.splitext(file_path)[0]

                            document = {
                                "_index": INDEX_NAME,
                                "_source": {
                                    "Country": data["Information"].get("Country", ""),
                                    "Authority": data["Information"].get("Authority", ""),
                                    "Expiration Date": expiration_date,
                                    "Name": name,
                                    "Gender": data["Information"].get("Gender", ""),
                                    "Date of Birth": birth_date,
                                    "Address": data["Information"].get("Address", ""),
                                    "ID Number": id_number,
                                    "FROM": from_field,
                                    "id_source": id_source
                                }
                            }

                            # Intentar indexar el documento
                            try:
                                es.index(index=INDEX_NAME, body=document["_source"])
                                #print(f"Documento indexado: {filename}")
                                os.remove(file_path)
                                shutil.move(file_path_png, directory_do)
                            except Exception as e:
                                error_files.append(filename)
                                print(f"Error al indexar {filename}: {e}")
                                os.remove(file_path)

                    except json.JSONDecodeError as e:
                        error_files.append(filename)
                        print(f"Error al leer {filename} (JSON inválido): {e}")

            except Exception as e:
                error_files.append(filename)
                print(f"Error al abrir {filename}: {e}")

    # Resumen del procesamiento
    print("\nResumen del procesamiento:")
    print(f"- Total de archivos con error: {len(error_files)}")
    if error_files:
        print("- Archivos con error:")
        for file in error_files:
            print(f"  - {file}")

    print(f"- Total de archivos omitidos (sin ID o Name): {len(skipped_files)}")
    if skipped_files:
        print("- Archivos omitidos:")
        for file in skipped_files:
            print(f"  - {file}")
        

def pii_index(base_dir, id_source):
    # Directorio donde están los archivos JSON
    DIRECTORY_PATH = "MLLM/"
    DIRECTORY_PATH_DO = "MLLM_DOO"

    os.makedirs(DIRECTORY_PATH, exist_ok=True)
    os.makedirs(DIRECTORY_PATH_DO, exist_ok=True)

    script_minicpm = "testminicpm.py"
    minicmp_name = "boring_liskov"

    run_test_in_container(minicmp_name, script_minicpm)
    # Ejecutar la indexación
    index_json_files_one_by_one(DIRECTORY_PATH, DIRECTORY_PATH_DO, id_source)

    shutil.rmtree(DIRECTORY_PATH)
    shutil.move(DIRECTORY_PATH_DO, base_dir)

    print("FINNNN PII INDEX")


def main():
    # Directorio donde están los archivos JSON
    DIRECTORY_PATH = ""
    DIRECTORY_PATH_DO = ""
    base_dir =""

    os.makedirs(DIRECTORY_PATH_DO, exist_ok=True)

    script_minicpm = "testminicpm.py"
    minicmp_name = "boring_liskov"

    id_source = 7255
    run_test_in_container(minicmp_name, script_minicpm)
    # Ejecutar la indexación
    index_json_files_one_by_one(DIRECTORY_PATH, DIRECTORY_PATH_DO, id_source)

    run_test_in_container(minicmp_name, script_minicpm)
    # Ejecutar la indexación
    index_json_files_one_by_one(DIRECTORY_PATH, DIRECTORY_PATH_DO, id_source)

    shutil.rmtree(DIRECTORY_PATH)
    shutil.move(DIRECTORY_PATH_DO, base_dir)

    print("FINNNN")



if __name__ == "__main__":

    main()
