import os
import fitz  # PyMuPDF
from PIL import Image
import concurrent.futures


def process_pdf(pdf_path, filename, images_dir):
    results = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_path = os.path.join(images_dir, f"{os.path.splitext(filename)[0]}_page_{page_num + 1}.png")
            img.save(img_path, "PNG")
            results.append(f"Imagen guardada: {img_path}")
        doc.close()
        return results
    except Exception as e:
        return [f"Error procesando {filename}: {str(e)}"]


def pdfs_to_images(base_dir, max_workers=4):
    # Directorios de entrada y salida
    input_dir = os.path.join(base_dir, "Dir_PDF", "to_MLLM")
    escaneados_dir = os.path.join(base_dir, "Dir_PDF", "escaneados")
    images_dir = os.path.join(base_dir, "Dir_Imagenes")

    # Asegurar que el directorio de salida exista
    os.makedirs(images_dir, exist_ok=True)

    # Recopilar todos los archivos PDF a procesar
    pdf_files = []

    # Archivos del directorio input
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            pdf_files.append((pdf_path, filename))

    # Archivos del directorio escaneados
    for filename in os.listdir(escaneados_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(escaneados_dir, filename)
            pdf_files.append((pdf_path, filename))

    # Procesar archivos en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, pdf_path, filename, images_dir)
                  for pdf_path, filename in pdf_files]

        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            for msg in results:
                print(msg)

    print("Proceso completado.")





def main():
    # Directorios de entrada y salida
    input_dir = "Dir_PDF/to_MLLM"  
    escaneados_dir = "Dir_PDF/escaneados"
    images_dir = "Dir_Imagenes"

    # Asegurar que el directorio de salida exista
    os.makedirs(images_dir, exist_ok=True)

    # Recopilar todos los archivos PDF a procesar
    pdf_files = []

    # Archivos del directorio input
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            pdf_files.append((pdf_path, filename))

    # Archivos del directorio escaneados
    for filename in os.listdir(escaneados_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(escaneados_dir, filename)
            pdf_files.append((pdf_path, filename))

    # Procesar archivos en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, pdf_path, filename)
                  for pdf_path, filename in pdf_files]

        for future in concurrent.futures.as_completed(futures):
            results = future.result()
            for msg in results:
                print(msg)

    print("Proceso completado.")


if __name__ == "__main__":
    main()