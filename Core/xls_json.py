import os
import json
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def xlsx_to_json(xlsx_path):
    try:
        # Leer el archivo XLSX utilizando pandas (asegúrate de tener instalado openpyxl)
        df = pd.read_excel(xlsx_path, engine="openpyxl")
        # Reemplazar valores NaN por cadena vacía para evitar problemas de serialización
        df = df.fillna('')
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error leyendo {xlsx_path}: {e}")
        return []

def save_json(data, json_path, pretty_print=True):
    with open(json_path, mode='w', encoding='utf-8') as json_file:
        if pretty_print:
            json.dump(data, json_file, indent=4, ensure_ascii=False, default=str)
        else:
            json.dump(data, json_file, ensure_ascii=False, default=str)

def extract_emails(text):
    email_regex = re.compile(
        r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
        r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
        r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
        r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
    )
    matches = email_regex.findall(text)
    return [match[0] for match in matches]

def clean_values(entry):
    return {key: (value.replace("\n", " ") if isinstance(value, str) else value)
            for key, value in entry.items()}

def transform_data(data):
    transformed_data = []
    for entry in data:
        cleaned_entry = clean_values(entry)
        # Buscar el primer campo que contenga un email
        email_field = None
        for key, value in cleaned_entry.items():
            if isinstance(value, str) and extract_emails(value):
                email_field = key
                break
        if email_field:
            email = cleaned_entry[email_field]
            email_context = {key: value for key, value in cleaned_entry.items() if key != email_field}
            transformed_data.append({
                "email": email,
                "email_context": email_context
            })
    return transformed_data

def process_file(xlsx_file, input_dir, output_dir, transformed_dir):
    xlsx_path = os.path.join(input_dir, xlsx_file)
    base_name = os.path.splitext(xlsx_file)[0]

    # Convertir XLSX a data (lista de diccionarios)
    data = xlsx_to_json(xlsx_path)

    # Guardar JSON “crudo”
    json_path = os.path.join(output_dir, f"{base_name}.json")
    save_json(data, json_path, pretty_print=True)
    print(f"XLSX convertido a JSON: {xlsx_path} -> {json_path}")

    # Transformar la data para extraer emails y contexto
    transformed_data = transform_data(data)
    transformed_json_path = os.path.join(transformed_dir, f"transformed_{base_name}.json")
    
    # Guardar el JSON transformado usando json.dump directamente
    with open(transformed_json_path, "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, ensure_ascii=False, separators=(',', ':'), default=str)
    print(f"JSON transformado guardado: {transformed_json_path}")

    # Eliminar archivos originales y JSON "crudo"
    os.remove(xlsx_path)
    os.remove(json_path)


def xls_to_json(input_dir):

    
    # Directorio para guardar los JSON "crudos"
    output_dir = os.path.join(input_dir, "json_files")
    
    # Directorio para guardar los JSON transformados
    transformed_dir = os.path.join(output_dir, "transformed")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(transformed_dir, exist_ok=True)
    
    # Lista de archivos XLSX en el directorio de entrada
    xlsx_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".xlsx")]
    
    # Procesar cada archivo XLSX en paralelo
    with ThreadPoolExecutor() as executor:
        for xlsx_file in xlsx_files:
            executor.submit(process_file, xlsx_file, input_dir, output_dir, transformed_dir)



def main():
    # Directorio de entrada (donde están los XLSX filtrados)
    input_dir = "Dir_basesdatos/XLSX_filtrados/"
    
    # Directorio para guardar los JSON "crudos"
    output_dir = os.path.join(input_dir, "json_files")
    
    # Directorio para guardar los JSON transformados
    transformed_dir = os.path.join(output_dir, "transformed")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(transformed_dir, exist_ok=True)
    
    # Lista de archivos XLSX en el directorio de entrada
    xlsx_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".xlsx")]
    
    # Procesar cada archivo XLSX en paralelo
    with ThreadPoolExecutor() as executor:
        for xlsx_file in xlsx_files:
            executor.submit(process_file, xlsx_file, input_dir, output_dir, transformed_dir)

if __name__ == "__main__":
    main()
