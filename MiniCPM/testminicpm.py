import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from huggingface_hub import login
import json
import re
import glob
import os

# Función para limpiar ID: remover espacios, puntos, guiones y dejar solo letras o números
def limpiar_id(id_str):
    return re.sub(r'[^A-Za-z0-9]', '', id_str)


def extraer_json_de_respuesta(respuesta_str):
    """
    Busca la primera llave '{' y la última '}' para extraer solo la porción JSON.
    Luego, lo parsea con json.loads().
    """
    start_idx = respuesta_str.find("{")
    end_idx = respuesta_str.rfind("}")
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError("No se encontró un bloque válido de JSON en la respuesta.")

    json_str = respuesta_str[start_idx:end_idx + 1].strip()
    

    json_str = json_str.strip('`').strip()
    
    return json.loads(json_str)

# Función para procesar una imagen y guardar la respuesta JSON
def procesar_imagen_y_guardar_json(image_path, question, output_filename):
    image = Image.open(image_path).convert('RGB')
    msgs = [{'role': 'user', 'content': [image, question]}]
    res = model.chat(msgs=msgs, tokenizer=tokenizer)
    # Se asume que la respuesta del modelo es un string JSON o algo muy cercano;
    # si no es JSON válido, es necesario depurarlo.
    try:
        data = extraer_json_de_respuesta(res)
    except json.JSONDecodeError:
        print(f"Error decodificando JSON en {image_path}")
        return

    # Guardar en un archivo JSON con formato
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)




model = AutoModel.from_pretrained('openbmb/MiniCPM-o-2_6', trust_remote_code=True,
    attn_implementation='sdpa', torch_dtype=torch.bfloat16) # sdpa or flash_attention_2, no eager
model = model.eval().cuda()
tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-o-2_6', trust_remote_code=True)

question = """ 

TASK:
You are provided with an image containing identity data. I need to extract the following information and return the result in JSON format with the structure and conventions described. IF you do NOT clearly see a piece of data in the image, leave it blank.

{
  "Information": {
    "Country": "",
    "Authority": "",
    "Expiration Date": "",
    "Name": "",
    "Gender": "M or F", 
    "Date of Birth": "",
    "Address": "",
    "ID Number": ""
  }
}

PRESENTS the response in JSON only, without adding additional explanations."""


# Directorio donde se encuentran las imágenes
directorio_imagenes = "MLLM/"

# Extensiones válidas de imágenes
patrones = ["*.png", "*.jpg", "*.jpeg"]
archivos_imagen = []
for patron in patrones:
    archivos_imagen.extend(glob.glob(os.path.join(directorio_imagenes, patron)))

for i, image_path in enumerate(archivos_imagen, start=1):
    nombre_salida = f"{image_path}.json"
    procesar_imagen_y_guardar_json(image_path, question, nombre_salida)
    print(f"Procesado: {image_path} -> {nombre_salida}")
