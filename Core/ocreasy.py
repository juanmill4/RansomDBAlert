import easyocr

# Crear un lector para el idioma español ('es') y otros si necesitas
reader = easyocr.Reader(['es'])  # 'es' para español

# Realizar OCR en la imagen
resultado = reader.readtext('/home/juan/Imágenes/1.jpeg')

# Mostrar los resultados
for texto in resultado:
    print("Texto detectado:", texto[1])
