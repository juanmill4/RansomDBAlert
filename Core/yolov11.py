from ultralytics import YOLO
import os
import shutil
from pathlib import Path
import glob

def process_images_directory(input_dir, output_dir, model, confidence):
    """
    Procesa las imágenes de un directorio buscando caras y las mueve al directorio de salida
    """
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Obtener lista de imágenes (considerando diferentes extensiones comunes)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(glob.glob(os.path.join(input_dir, ext)))
        image_paths.extend(glob.glob(os.path.join(input_dir, ext.upper())))

    # Lista para almacenar las imágenes que no tuvieron detecciones
    images_without_detection = []

    print(f"Procesando {len(image_paths)} imágenes...")

    # Primera pasada
    for image_path in image_paths:
        try:
            # Ejecutar la inferencia
            results = model(image_path, verbose=False)

            # Verificar si se detectó una cara
            if len(results[0].boxes) > 0:
                # Mover la imagen al directorio de salida
                dest_path = os.path.join(output_dir, os.path.basename(image_path))
                shutil.move(image_path, dest_path)
                print(f"Cara detectada en {os.path.basename(image_path)} - Movida a {output_dir}")
            else:
                images_without_detection.append(image_path)

        except Exception as e:
            print(f"Error al procesar {image_path}: {e}")

    # Segunda pasada con las imágenes que no tuvieron detecciones
    print("\nRealizando segunda pasada para minimizar falsos negativos...")

    for image_path in images_without_detection:
        try:
            # Ejecutar la inferencia con un umbral de confianza más bajo
            results = model(image_path, conf=confidence*0.95, verbose=False)  # Reducimos un poco el umbral

            # Verificar si se detectó una cara
            if len(results[0].boxes) > 0:
                # Mover la imagen al directorio de salida
                dest_path = os.path.join(output_dir, os.path.basename(image_path))
                shutil.move(image_path, dest_path)
                print(f"Cara detectada en segunda pasada en {os.path.basename(image_path)} - Movida a {output_dir}")

        except Exception as e:
            print(f"Error al procesar {image_path} en segunda pasada: {e}")



def yolo_faces(base_dir):
    # Cargar el modelo
    MLLM_path = "ocrminicpm/"
    model = YOLO("yolov11l-face.pt")  # Asegúrate de tener el modelo correcto

    # Configurar directorios
    input_directory = os.path.join(base_dir, "Dir_Imagenes")
    output_directory = os.path.join(base_dir, "MLLM")

    # Configurar umbral de confianza
    confidence_threshold = 0.59

    # Procesar las imágenes
    process_images_directory(input_directory, output_directory, model, confidence_threshold)

    shutil.move(output_directory, MLLM_path)

    print("\nProcesamiento completado!")


def main():
    # Cargar el modelo
    model = YOLO("yolov11m-face.pt")  # Asegúrate de tener el modelo correcto

    # Configurar directorios
    input_directory = 'directorio_entrada'  # Reemplaza con tu directorio de entrada
    output_directory = 'directorio_salida'  # Reemplaza con tu directorio de salida

    # Configurar umbral de confianza
    confidence_threshold = 0.25

    # Procesar las imágenes
    process_images_directory(input_directory, output_directory, model, confidence_threshold)

    print("\nProcesamiento completado!")

if __name__ == "__main__":
    main()