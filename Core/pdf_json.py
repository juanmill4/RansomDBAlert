import fitz  # PyMuPDF
import re
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

# Expresión regular para extraer emails RFC 2822
email_regex = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)

def generar_id(email, contexto):
    """Genera un hash SHA-1 único basado en email + contexto"""
    return hashlib.sha1(f"{email}{contexto}".encode()).hexdigest()

def extraer_emails_con_contexto(pdf, directorio, directorio_json):
    """Extrae emails con contexto de un PDF de manera optimizada."""
    ruta_pdf = os.path.join(directorio, pdf)
    nombre_pdf = os.path.splitext(pdf)[0]
    print(f"Procesando: {ruta_pdf}")

    doc = fitz.open(ruta_pdf)
    max_pages = min(30, len(doc))  # Limitar lectura a las primeras 30 páginas
    email_detectado = False  # Variable para saber si encontramos algún email

    # Procesar primeras 30 páginas
    for i in range(max_pages):
        texto = doc[i].get_text("text")
        if email_regex.search(texto):

            email_detectado = True
            break  # Si encontramos un email, terminamos la búsqueda inicial

    # Si no hay emails en las primeras 30 páginas, terminamos el proceso
    if not email_detectado:
        print(f"No se encontraron emails en las primeras 30 páginas de {ruta_pdf}. Saliendo.")
        doc.close()
        os.remove(ruta_pdf)
        return

    # Si encontramos un email, procesamos el documento completo **por partes**
    resultados = {}

    for i in range(len(doc)):  # Procesar todas las páginas

        texto = doc[i].get_text("text")
        
        for match in email_regex.finditer(texto):
            email = match.group(0)
            start = max(0, match.start() - 500)
            end = min(len(texto), match.end() + 500)
            contexto = texto[start:end].replace("\n", " ")  # Extraer contexto limpio

            # Generar ID único
            id_hash = generar_id(email, contexto)

            # Guardar email y contexto en el diccionario
            resultados[email] = {
                "email_context": contexto,
                "ID": id_hash,
                "FROM": nombre_pdf
            }

    # Guardar resultados si encontramos correos
    if resultados:
        nombre_json = os.path.splitext(os.path.basename(ruta_pdf))[0] + ".json"
        ruta_json = os.path.join(directorio_json, nombre_json)

        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=4, ensure_ascii=False)

        print(f"Procesado: {ruta_pdf} → {ruta_json} ({len(resultados)} emails extraídos)")
    else:
        print(f"No se encontraron emails en todo el documento {ruta_pdf}")
        os.remove(ruta_pdf)

    doc.close()

def pdfs_to_json(directorio):
    """Procesa todos los archivos PDF en el directorio y guarda los JSON en 'PDF_to_json'."""
    directorio_json = os.path.join(directorio, "PDF_to_json")
    
    # Crear el directorio de salida si no existe
    os.makedirs(directorio_json, exist_ok=True)

    # Listar archivos en el directorio
    pdfs = [f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))]
    

    if not pdfs:
        print("No se encontraron archivos PDF en el directorio.")
        return

    print(f" Se encontraron {len(pdfs)} archivos PDF. Procesando...\n")


    # Usar ThreadPoolExecutor para procesar archivos en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(extraer_emails_con_contexto, pdf, directorio, directorio_json) for pdf in pdfs]
        for future in futures:
            future.result()  # Esperar a que terminen todas las tareas

    print("Todos los PDFs han sido procesados y los JSON están en 'PDF_to_json'.")



if __name__ == "__main__":
    # Uso del script
    ruta_pdf = "/Dir_PDF/digitalizados/"  # Cambia esto por la ruta de tu PDF

    procesar_directorio(ruta_pdf)
