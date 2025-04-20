import os
import json
import re
from lxml import etree
from concurrent.futures import ThreadPoolExecutor

# Expresión regular para encontrar emails
EMAIL_REGEX = re.compile(
    r"([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*"
    r"\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)"
    r"(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff\x7c]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))"
)

def extract_emails_with_context(text, context_len=200):
    """
    Extrae emails y sus contextos desde el texto completo.
    """
    results = {}
    for match in EMAIL_REGEX.finditer(text):
        email = match.group(0)
        start, end = match.span()
        left_context = text[max(0, start - context_len):start]
        right_context = text[end:end + context_len]
        full_context = (left_context + email + right_context).strip()
        results[email] = {"email_context": full_context}
    return results

def xml_to_json_full_lxml(xml_path, output_dir):
    """
    Carga el XML completo en memoria usando lxml, extrae los emails y guarda el resultado en un archivo JSON.
    """
    base_name = os.path.splitext(os.path.basename(xml_path))[0]
    json_filename = f"{base_name}.json"
    json_path = os.path.join(output_dir, json_filename)
    
    # Configuramos el parser para manejar árboles grandes
    parser = etree.XMLParser(huge_tree=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()
    
    # Extraemos todo el texto del XML y lo limpiamos
    text = " ".join(root.itertext()).replace("\n", " ").replace("\r", " ")
    
    # Aplicamos la búsqueda de emails sobre el texto completo
    results = extract_emails_with_context(text)
    
    with open(json_path, mode='w', encoding='utf-8') as json_file:
        json.dump(results, json_file, indent=4, ensure_ascii=False)
    
    print(f"Convertido: {xml_path} -> {json_path}")



def xml_to_json(input_dir):

    output_dir = os.path.join(input_dir, "json_files")
    os.makedirs(output_dir, exist_ok=True)
    
    xml_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".xml")
    ]
    
    with ThreadPoolExecutor() as executor:
        for xml_file in xml_files:
            executor.submit(xml_to_json_full_lxml, xml_file, output_dir)

def main():
    input_dir = "Dir_basesdatos/XML_filtrados/"
    output_dir = os.path.join(input_dir, "json_files")
    os.makedirs(output_dir, exist_ok=True)
    
    xml_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".xml")
    ]
    
    with ThreadPoolExecutor() as executor:
        for xml_file in xml_files:
            executor.submit(xml_to_json_full_lxml, xml_file, output_dir)

if __name__ == "__main__":
    main()
