import os
import json
from elasticsearch import Elasticsearch, helpers

INDEX_NAME = "ramsombreachindex"  # Nombre del índice en Elasticsearch

# Conectar a Elasticsearch
es = Elasticsearch(
    ["https://localhost:9200"],
    http_auth=('elastic', '3XMai+F_X73x49JjuLW0'),
    verify_certs=False,
)

# Crear índice si no existe
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME)

# Directorio donde están los archivos JSON
DIRECTORY_PATH = "/home/juan/Descargas/honeywell/Dir_PDF/digitalizados/PDF_to_json/"
doc_dir = "/home/juan/Descargas/honeywell/Dir_documentos/digitalizados/DOCX_to_json/"

def index_json_files_bulk(directory_path, batch_size=500):
    bulk_data = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):  # Solo procesa archivos JSON
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    
                    for email, details in data.items():
                        document = {
                            "_index": INDEX_NAME,
                            "_source": {
                                "email": email,
                                "email_context": details.get("email_context", ""),
                                "id": details.get("ID", ""),
                                "from": details.get("FROM", "")
                            }
                        }
                        
                        bulk_data.append(document)
                        
                        # Procesar en lotes para mejorar rendimiento
                        if len(bulk_data) >= batch_size:
                            helpers.bulk(es, bulk_data)
                            print(f"Indexados {len(bulk_data)} documentos...")
                            bulk_data = []  # Vaciar lista después de indexar

                except json.JSONDecodeError as e:
                    print(f"Error al leer {filename}: {e}")
    
    # Indexar los documentos restantes
    if bulk_data:
        helpers.bulk(es, bulk_data)
        print(f"Indexados {len(bulk_data)} documentos finales...")

# Ejecutar la indexación
index_json_files_bulk(doc_dir)
print("Indexación completada.")


