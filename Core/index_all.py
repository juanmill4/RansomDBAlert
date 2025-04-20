import os
import json
import hashlib
import urllib3
import sys
from elasticsearch import Elasticsearch, helpers
from datetime import datetime

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



def index_json_files_bulk(directory_path, id_ransom, batch_size=500):
    bulk_data = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):  # Solo procesa archivos JSON
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)

                    for email, details in data.items():
                        # Obtener el campo "from" original y añadir el nombre del archivo y el ID
                        from_field = details.get("FROM", "")
                        enhanced_from = f"{from_field} {filename}"
						
                        domain = ""
                        if "@" in email:
                            domain = email.split("@")[1]

                        doc_id = details.get("ID", "")

                        email = email.lower()
                        domain = domain.lower()

                        document = {
                            "_index": INDEX_NAME,
                            "_id": doc_id,  # Establecer el ID de Elasticsearch
                            "_source": {
                                "email": email,
                                "email_context": details.get("email_context", ""),
                                "domain": domain,
                                "from": enhanced_from,
                                "id_source": id_ransom
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


def index_email_object_format(directory_path, id_ransom, batch_size=500):
    """
    Process JSON files where each file is an object with email addresses as keys
    Example: {"email@example.com": {"email_context": "text content"}, ...}
    """
    bulk_data = []
    processed_count = 0

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)

                    for email, details in data.items():
                        domain = email.split("@")[1] if "@" in email else ""
                        email_context = details.get("email_context", "")

                        email = email.lower()
                        domain = domain.lower()

                        # Generate SHA1 hash using email and email_context
                        hash_input = f"{email}{email_context}"
                        doc_id = hashlib.sha1(hash_input.encode()).hexdigest()


                        document = {
                            "_index": INDEX_NAME,
                            "_id": doc_id,
                            "_source": {
                                "email": email,
                                "email_context": email_context,
                                "domain": domain,
                                "from": filename,
                                "id_source": id_ransom
                            }
                        }

                        bulk_data.append(document)
                        processed_count += 1

                        if len(bulk_data) >= batch_size:
                            helpers.bulk(es, bulk_data)
                            print(f"Indexados {len(bulk_data)} documentos...")
                            bulk_data = []

                except Exception as e:
                    print(f"Error al procesar {filename}: {e}")

    if bulk_data:
        helpers.bulk(es, bulk_data)
        print(f"Indexados {len(bulk_data)} documentos finales...")

def index_email_array_format(directory_path, id_ransom, batch_size=2000):
    """
    Process JSON files where each file is an array of objects with email and email_context fields
    Example: [{"email": "example@email.com", "email_context": {"ID": 1234, ...}}, ...]
    """
    bulk_data = []
    processed_count = 0

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)

                    for item in data:
                        if "email" in item and "email_context" in item:
                            email = item["email"]
                            email_context = item["email_context"]
                            domain = email.split("@")[1] if "@" in email else ""

                            email = email.lower()
                            domain = domain.lower()

                            # Convert email_context to string if it's a dictionary
                            email_context_str = json.dumps(email_context) if isinstance(email_context, dict) else str(email_context)

                            # Generate SHA1 hash using email and email_context
                            hash_input = f"{email}{email_context_str}"
                            doc_id = hashlib.sha1(hash_input.encode()).hexdigest()


                            document = {
                                "_index": INDEX_NAME,
                                "_id": doc_id,
                                "_source": {
                                    "email": email,
                                    "email_context": email_context_str,
                                    "domain": domain,
                                    "from": filename,
                                    "id_source": id_ransom
                                }
                            }

                            bulk_data.append(document)
                            processed_count += 1

                            if len(bulk_data) >= batch_size:
                                helpers.bulk(es, bulk_data)
                                print(f"Indexados {len(bulk_data)} documentos...")
                                bulk_data = []

                except Exception as e:
                    print(f"Error al procesar {filename}: {e}")

    if bulk_data:
        helpers.bulk(es, bulk_data)
        print(f"Indexados {len(bulk_data)} documentos finales...")





def index_all_docs(base_dir, id_sor):

    pdf_dir = os.path.join(base_dir, "Dir_PDF", "digitalizados", "PDF_to_json")
    doc_dir = os.path.join(base_dir, "Dir_documentos", "digitalizados", "DOCX_to_json")
    ppt_dir = os.path.join(base_dir, "Dir_documentos", "digitalizados", "PPTX_to_json")
    txt_dir = os.path.join(base_dir, "Dir_texto", "Process_TXT_JSON")
    
    xml_dir = os.path.join(base_dir, "Dir_basesdatos", "XML_filtrados", "json_files")
    csv_dir = os.path.join(base_dir, "Dir_basesdatos", "CSV_filtrados", "json_files", "transformed")
    xls_dir = os.path.join(base_dir, "Dir_basesdatos", "XLSX_filtrados", "json_files", "transformed")

    index_json_files_bulk(txt_dir, id_sor)
    print("Indexación txt completada.")
    index_json_files_bulk(pdf_dir, id_sor)
    print("Indexación pdf completada.")
    index_json_files_bulk(doc_dir, id_sor)
    print("Indexación doc completada.")
    index_json_files_bulk(ppt_dir, id_sor)
    print("Indexación doc completada.")

    index_email_array_format(csv_dir, id_sor)
    print("CSV Indexados")

    index_email_array_format(xls_dir, id_sor)
    print("XLX Indexados")

    index_email_object_format(xml_dir, id_sor)
    print("FINNN")

    return id_sor



def main():

    if len(sys.argv) < 2:
        print("Uso: python index_all.py <ruta_directorio_base>")
        sys.exit(1)

    base_dir = sys.argv[1]
    if not os.path.exists(base_dir):
        print(f"Error: El directorio '{base_dir}' no existe.")
        sys.exit(1)

    pdf_dir = os.path.join(base_dir, "Dir_PDF", "digitalizados", "PDF_to_json")
    doc_dir = os.path.join(base_dir, "Dir_documentos", "digitalizados", "DOCX_to_json")
    txt_dir = os.path.join(base_dir, "Dir_texto", "Process_TXT_JSON")
    
    xml_dir = os.path.join(base_dir, "Dir_basesdatos", "XML_filtrados", "json_files")
    csv_dir = os.path.join(base_dir, "Dir_basesdatos", "CSV_filtrados", "json_files", "transformed")
    xls_dir = os.path.join(base_dir, "Dir_basesdatos", "XLSX_filtrados", "json_files", "transformed")

    id_sor = pedir_metadatos()

    index_json_files_bulk(txt_dir, id_sor)
    print("Indexación txt completada.")
    index_json_files_bulk(pdf_dir, id_sor)
    print("Indexación pdf completada.")
    index_json_files_bulk(doc_dir, id_sor)
    print("Indexación doc completada.")

    index_email_array_format(csv_dir, id_sor)
    print("CSV Indexados")

    index_email_array_format(xls_dir, id_sor)
    print("XLX Indexados")

    index_email_object_format(xml_dir, id_sor)
    print("FINNN")


if __name__ == "__main__":
    main()
