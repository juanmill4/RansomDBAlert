import os
import shutil
import subprocess
import concurrent.futures


# Función para convertir DOCX a PDF usando unoconv
def docx_to_pdf(docx_path, pdf_path):
    print(docx_path)
    try:
        subprocess.run(["libreoffice", "--convert-to", "pdf", "--outdir", pdf_path, docx_path], check=True, timeout=5)
        os.remove(docx_path)
        print("Eliminado")
    except subprocess.TimeoutExpired:
        print(f"Tiempo de espera excedido al convertir {docx_path}")
    finally:
        print("parado")
        subprocess.run(["killall", "soffice.bin"])

# Función para procesar un solo archivo
def process_file(src_dir, filename, pdf_dir):
    docx_path = os.path.join(src_dir, filename)
    pdf_path = os.path.join(pdf_dir, f"{os.path.splitext(filename)[0]}.pdf")
    try:
        docx_to_pdf(docx_path, pdf_path)
        return f"Convertido: {filename}"
    except subprocess.CalledProcessError as e:
        return f"Error al convertir {filename} a PDF: {e}"


def docs_to_pdf(base_dir):
    # Directorios de entrada y salida
    input_dir = os.path.join(base_dir, "Dir_documentos", "to_MLLM")
    escaneados_dir = os.path.join(base_dir, "Dir_documentos", "escaneados")
    pdf_dir = os.path.join(base_dir, "Dir_PDF", "escaneados")

    # Asegurar que el directorio de salida exista
    os.makedirs(pdf_dir, exist_ok=True)

    # Recopilar todos los archivos a procesar
    files_to_process = []
    for filename in os.listdir(input_dir):
        files_to_process.append((input_dir, filename))

    for filename in os.listdir(escaneados_dir):
        files_to_process.append((escaneados_dir, filename))

    # Procesar archivos en paralelo
    for src_dir, filename in files_to_process:
        result = process_file(src_dir, filename, pdf_dir)
        print(result)

    print("Proceso completado.")



def main():


    # Directorios de entrada y salida
    input_dir = "Dir_documentos/to_MLLM"
    escaneados_dir = "Dir_documentos/escaneados"
    pdf_dir = "Dir_PDF/escaneados"  

    # Procesar cada archivo DOCX
    for filename in os.listdir(input_dir):
        docx_path = os.path.join(input_dir, filename)
        pdf_path = os.path.join(pdf_dir, f"{os.path.splitext(filename)[0]}.pdf")

        # Convertir DOCX a PDF
        try:
            docx_to_pdf(docx_path, pdf_path)
        except subprocess.CalledProcessError as e:
            print(f"Error al convertir {filename} a PDF: {e}")
            continue
            
    print("Proceso completado.")
