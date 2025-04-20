import os
import csv
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

# Función para convertir CSV a lista de diccionarios
def csv_too_json(csv_path):
    data_list = []
    with open(csv_path, mode='r', encoding='utf-8', errors='ignore') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data_list.append(row)
    return data_list

# Función para guardar datos en un archivo JSON
def save_json(data, json_path, pretty_print=True):
    with open(json_path, mode='w', encoding='utf-8') as json_file:
        if pretty_print:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        else:
            json.dump(data, json_file, ensure_ascii=False)


# Función para extraer emails usando expresión regular
def context_extract_emails(text):
    email_regex = re.compile(
        r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
        r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
        r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
        r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
    )
    matches = email_regex.findall(text)
    return [match[0] for match in matches]

# Función para extraer emails de un texto
def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+'
    return re.findall(email_pattern, text)

# Función para limpiar valores (reemplaza saltos de línea internos)
def clean_values(entry):
    return {key: (value.replace("\n", " ") if isinstance(value, str) else value)
            for key, value in entry.items()}

# Función para transformar la data: extrae el primer email y separa su contexto
def transform_data(data):
    transformed_data = []
    for entry in data:
        cleaned_entry = clean_values(entry)
        # Busca el primer campo que contenga un email
        email_field = None
        emails = None
        email = None
        for key, value in cleaned_entry.items():
            if isinstance(value, str):
                emails = extract_emails(value)
                if emails:
                    email = emails[0]
                    email_field = key
                    break

        if email:
            email_context = {key: value for key, value in cleaned_entry.items() if key != email_field}
            transformed_data.append({
                "email": email,
                "email_context": email_context
            })

    return transformed_data

# Función para procesar cada archivo: conversión y transformación
def process_file(csv_file, input_dir, output_dir, transformed_dir):
    csv_path = os.path.join(input_dir, csv_file)
    base_name = os.path.splitext(csv_file)[0]
    
    # Convertir CSV a data (lista de diccionarios)
    data = csv_too_json(csv_path)
    
    # Guardar JSON “crudo”
    json_path = os.path.join(output_dir, f"{base_name}.json")
    save_json(data, json_path, pretty_print=True)
    print(f"CSV convertido a JSON: {csv_path} -> {json_path}")
    
    # Transformar la data para extraer emails y contexto
    transformed_data = transform_data(data)
    # Guardar JSON transformado (sin pretty-print, según lo solicitado)
    transformed_json_path = os.path.join(transformed_dir, f"transformed_{base_name}.json")
    with open(transformed_json_path, "w", encoding="utf-8") as f:
        f.write('[\n')
        for idx, item in enumerate(transformed_data):
            json.dump(item, f, ensure_ascii=False, separators=(',', ':'))
            if idx < len(transformed_data) - 1:
                f.write(',\n')
        f.write('\n]')
    print(f"JSON transformado guardado: {transformed_json_path}")

    os.remove(csv_path)
    os.remove(json_path)


def csv_to_json(input_dir):
    
    # Directorio para guardar los JSON “crudos”
    output_dir = os.path.join(input_dir, "json_files")
    
    # Directorio para guardar los JSON transformados
    transformed_dir = os.path.join(output_dir, "transformed")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(transformed_dir, exist_ok=True)
    
    # Lista de archivos CSV en el directorio de entrada
    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".csv")]
    

    # Procesa cada archivo CSV en paralelo
    with ThreadPoolExecutor() as executor:
        for csv_file in csv_files:
            executor.submit(process_file, csv_file, input_dir, output_dir, transformed_dir)



def main():
    # Directorio de entrada (donde están los CSV)
    input_dir = "Dir_basesdatos/CSV_filtrados/"
    
    # Directorio para guardar los JSON “crudos”
    output_dir = os.path.join(input_dir, "json_files")
    
    # Directorio para guardar los JSON transformados
    transformed_dir = os.path.join(output_dir, "transformed")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(transformed_dir, exist_ok=True)
    
    # Lista de archivos CSV en el directorio de entrada
    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".csv")]

    json_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".json")]

    for json_file in json_files:
        json_p = os.path.join(input_dir, json_file)
        shutil.move(json_p, output_dir)

    # Procesa cada archivo CSV en paralelo
    with ThreadPoolExecutor() as executor:
        for csv_file in csv_files:
            executor.submit(process_file, csv_file, input_dir, output_dir, transformed_dir)

if __name__ == "__main__":
    main()
