import os
import subprocess
import sys
import shutil

def descomprimir_archivos(directorio):
    cuarentena = os.path.join(directorio, "cuarentena")
    os.makedirs(cuarentena, exist_ok=True)

    while True:
        archivos_comprimidos = []

        # Buscar archivos comprimidos en el directorio y subdirectorios
        for root, _, files in os.walk(directorio):
            for file in files:
                if file.endswith(('.zip', '.rar', '.7z')):
                    archivos_comprimidos.append(os.path.join(root, file))

        # Si no hay archivos comprimidos, salir del bucle
        if not archivos_comprimidos:
            break

        # Descomprimir cada archivo encontrado
        for ruta_archivo in archivos_comprimidos:
            print(f"Descomprimiendo: {ruta_archivo}")
            try:
                comando = ['7z', 'e', '-y', ruta_archivo, f'-o{directorio}', '-p']
                resultado = subprocess.run(comando, capture_output=True, text=True)

                if "Wrong password" in resultado.stderr:
                    print(f"Contraseña incorrecta para el archivo {ruta_archivo}. Eliminando.")
                    os.remove(ruta_archivo)
                else:
                    print(f"Descompresión exitosa: {ruta_archivo}")
                    os.remove(ruta_archivo)  # Eliminar el archivo comprimido original
            except Exception as e:
                print(f"Error procesando {ruta_archivo}: {e}")
                os.remove(ruta_archivo)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python descomprimir.py <directorio>")
        sys.exit(1)

    directorio = sys.argv[1]

    if not os.path.isdir(directorio):
        print(f"El directorio {directorio} no existe o no es válido.")
        sys.exit(1)

    descomprimir_archivos(directorio)
