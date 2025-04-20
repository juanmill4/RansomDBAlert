import os
import shutil
import fitz  # PyMuPDF
from concurrent.futures import ThreadPoolExecutor

def process_pdf(file_path, umbral, digitalizados_dir, escaneados_dir, mllm_dir):
    filename = os.path.basename(file_path)
    filename_lower = filename.lower()
    
    # Si el título del archivo contiene "hiring" y ("cv" o "resume")
    if "hiring" in filename_lower and ("cv" in filename_lower or "resume" in filename_lower or "passport" in filename_lower):
        # Renombrar a minúsculas y clasificar directamente como escaneado
        new_filename = filename_lower
        destino = os.path.join(mllm_dir, new_filename)
        print(f"{filename} renombrado a {new_filename} y clasificado como escaneado por coincidencia en el título")
    else:
        try:
            doc = fitz.open(file_path)
            text = ""
            es_digitalizado = False  # Bandera para determinar la clasificación
            # Extraer texto página a página
            for page in doc:
                text += page.get_text()
                # Si se supera el umbral, detenemos la extracción
                if len(text.strip()) > umbral:
                    es_digitalizado = True
                    break
            doc.close()
        except Exception as e:
            print(f"Error al procesar {e}")
            return

        if es_digitalizado:
            destino = os.path.join(digitalizados_dir, filename)
            print(f"{filename} clasificado como digitalizado")
        else:
            destino = os.path.join(escaneados_dir, filename)
            print(f"{filename} clasificado como escaneado")

    try:
        shutil.move(file_path, destino)
    except Exception as e:
        print(f"Error al mover {filename}: {e}")




def filtrado_pdfs(root_dir):

    # Directorios de destino para los PDFs clasificados
    digitalizados_dir = os.path.join(root_dir, "digitalizados")
    escaneados_dir = os.path.join(root_dir, "escaneados")
    mllm_dir = os.path.join(root_dir, "to_MLLM")

    os.makedirs(digitalizados_dir, exist_ok=True)
    os.makedirs(escaneados_dir, exist_ok=True)
    os.makedirs(mllm_dir, exist_ok=True)

    # Umbral de caracteres para distinguir entre PDF digitalizado y escaneado
    umbral = 50

    # Obtener la lista de archivos PDF en el directorio
    pdf_files = [
        os.path.join(root_dir, f)
        for f in os.listdir(root_dir) if f.lower().endswith(".pdf")
    ]

    # Procesamiento concurrente de los PDFs
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_pdf, file, umbral, digitalizados_dir, escaneados_dir, mllm_dir)
            for file in pdf_files
        ]
        for future in futures:
            future.result()

    return digitalizados_dir, escaneados_dir, mllm_dir



if __name__ == "__main__":
    # Directorio raíz donde se encuentran los PDFs
    root_dir = "Dir_PDF" 
    # Directorios de destino para los PDFs clasificados
    digitalizados_dir = os.path.join(root_dir, "digitalizados")
    escaneados_dir = os.path.join(root_dir, "escaneados")
    mllm_dir = os.path.join(root_dir, "to_MLLM")

    os.makedirs(digitalizados_dir, exist_ok=True)
    os.makedirs(escaneados_dir, exist_ok=True)
    os.makedirs(mllm_dir, exist_ok=True)

    # Umbral de caracteres para distinguir entre PDF digitalizado y escaneado
    umbral = 50

    # Obtener la lista de archivos PDF en el directorio
    pdf_files = [
        os.path.join(root_dir, f)
        for f in os.listdir(root_dir) if f.lower().endswith(".pdf")
    ]

    # Procesamiento concurrente de los PDFs
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_pdf, file, umbral, digitalizados_dir, escaneados_dir, mllm_dir)
            for file in pdf_files
        ]
        for future in futures:
            future.result()