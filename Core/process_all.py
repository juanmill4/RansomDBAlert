import sys
import os
import urllib3
import sys
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
from descomp import descomprimir_archivos
from txt_json import txt_to_json
from organiza import organiza_dir
from filtradodoc import  filtrado_docx
from doc_json import docs_to_json
from filtradopdfs import filtrado_pdfs
from pdf_json import pdfs_to_json
from docx_to_images import docs_to_pdf
from pdf_to_images import pdfs_to_images
from yolov11 import yolo_faces
# la parte de minicpm
from head_csv import csv_filter
from head_xls import xlxs_filter
from head_xml import xml_filter
from csv_json import csv_to_json
from xml_json import xml_to_json
from xls_json import xls_to_json

from index_all import index_all_docs
from index_id import pii_index

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


def pedir_metadatos():
    print("Introduce los siguientes datos del documento:")

    post_title = input("post_title: ").strip()
    group_name = input("group_name: ").strip()
    description = input("description: ").strip()
    website = input("website: ").strip()
    post_url = input("post_url: ").strip()
    country = input("country (puede estar vacío): ").strip()

    # timestamps actuales si no quieres pedirlos manualmente
    now = datetime.utcnow().isoformat()


    discovered = input(f"discovered [{now}]: ").strip() or now
    indexed = now


    try:
        id_value = int(input("id (número): ").strip())
    except ValueError:
        print(" Valor no válido para id. Se asigna 0.")
        id_value = 0

    datos = {
        "id_source_metadata": {
        "post_title": post_title,
        "group_name": group_name,
        "discovered": discovered,
        "description": description,
        "website": website,
        "indexed": indexed,
        "post_url": post_url,
        "country": country,
        "id": id_value
        }
    }

    es.index(index=INDEX_NAME, document=datos)

    return id_value


def main():

    if len(sys.argv) < 2:
        print("Uso: python process_all.py <ruta_directorio_base>")
        sys.exit(1)

    base_dir = sys.argv[1]
    if not os.path.exists(base_dir):
        print(f"Error: El directorio '{base_dir}' no existe.")
        sys.exit(1)

    print("\n⚠️ WARNING: For file types (.sql, .db, .accdb, .sqlite, .pst, .rtf, .MYD, .mdb, etc) that require advanced processing")

    print("If you want specialized processing for databases, please contact: juanma@darkeye.io")
    input("Press ENTER to confirm that you have read this prompt and continue with standard processing...")

    id_souc = pedir_metadatos()

    descomprimir_archivos(base_dir)
    organiza_dir(base_dir)

    PDF_dir = os.path.join(base_dir, "Dir_PDF")
    DOC_dir = os.path.join(base_dir, "Dir_documentos")
    TXT_dir = os.path.join(base_dir, "Dir_texto")
    DB_dir = os.path.join(base_dir, "Dir_basesdatos")
    IMG_dir = os.path.join(base_dir, "Dir_Imagenes")

    txt_to_json(TXT_dir)
    dig_doc, esc_doc, mllm_doc = filtrado_docx(DOC_dir)
    docs_to_json(dig_doc)
    dig_pdf, esc_pdf, mllm_pdf = filtrado_pdfs(PDF_dir)
    pdfs_to_json(dig_pdf)

    # YOLO para esc_doc y esc_pdf move to mllm

    docs_to_pdf(base_dir)
    pdfs_to_images(base_dir)

    yolo_faces(base_dir)

    csv_fil = csv_filter(DB_dir)
    xls_fil = xlxs_filter(DB_dir)
    xlm_fil = xml_filter(DB_dir)

    csv_to_json(csv_fil)
    xls_to_json(xls_fil)
    xml_to_json(xlm_fil)

    # MLLM con docker 2 pasadas

    index_all_docs(base_dir, id_souc)
    pii_index(base_dir, id_souc)


if __name__ == "__main__":
    main()