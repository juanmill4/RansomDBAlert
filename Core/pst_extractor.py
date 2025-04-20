import pypff
from email.parser import Parser
from email.header import decode_header, make_header
from email.utils import parseaddr, getaddresses

# Diccionario global para recopilar direcciones sin repetirse
# Clave: email en minúsculas, Valor: nombre (el último o primero encontrado).
unique_emails = {}

pst = pypff.file()
pst.open("/home/juan/Descargas/ddd/julio.puentes@pioneer-mex.com.mx_unsearchable.pst")

root = pst.get_root_folder()
email_count = 0

def guardar_email_sin_duplicado(nombre, correo):
    """
    Recibe el nombre y correo.
    Almacena en el diccionario global si no existe todavía.
    """
    if not correo:
        return  # Evitar correos vacíos
    correo_lower = correo.lower()
    if correo_lower not in unique_emails:
        unique_emails[correo_lower] = nombre.strip() if nombre else ""

def extract_emails(folder):
    global email_count

    for message in folder.sub_messages:
        try:
            if hasattr(message, 'subject') and hasattr(message, 'sender_name'):
                email_count += 1
                print(f"Email #{email_count}")
                print(f"Asunto: {message.subject}")
                print(f"Remitente (Outlook): {message.sender_name}")

                # ¿El remitente desde pypff?
                if hasattr(message, 'sender_email_address') and message.sender_email_address:
                    print(f"Correo (pypff): {message.sender_email_address}")
                    # Guardarlo también en el diccionario de únicos
                    guardar_email_sin_duplicado(message.sender_name, message.sender_email_address)

                # Parsear los transport_headers
                headers = message.transport_headers
                if headers:
                    parsed_headers = Parser().parsestr(headers)

                    # FROM
                    raw_from = parsed_headers['From']
                    if raw_from:
                        decoded_from = str(make_header(decode_header(raw_from)))
                        from_name, from_email = parseaddr(decoded_from)
                        print(f"From (cabeceras): {from_name} <{from_email}>")
                        guardar_email_sin_duplicado(from_name, from_email)

                    # TO
                    raw_to = parsed_headers['To']
                    if raw_to:
                        decoded_to = str(make_header(decode_header(raw_to)))
                        to_addrs = getaddresses([decoded_to])
                        print("To (cabeceras):")
                        for (name, email) in to_addrs:
                            print(f"   {name} <{email}>")
                            guardar_email_sin_duplicado(name, email)

                    # CC
                    raw_cc = parsed_headers['CC']
                    if raw_cc:
                        decoded_cc = str(make_header(decode_header(raw_cc)))
                        cc_addrs = getaddresses([decoded_cc])
                        print("CC (cabeceras):")
                        for (name, email) in cc_addrs:
                            print(f"   {name} <{email}>")
                            guardar_email_sin_duplicado(name, email)

                print("-" * 50)
        except Exception as e:
            pass

    # Recorrer subcarpetas recursivamente
    for subfolder in folder.sub_folders:
        extract_emails(subfolder)

print("Extrayendo emails del archivo PST...")
extract_emails(root)
print(f"Total de emails encontrados: {email_count}")

pst.close()

# Al terminar, mostramos las direcciones recopiladas sin duplicado
print("\n=== Direcciones recopiladas (sin repetir) ===")
for correo, nombre in unique_emails.items():
    if nombre:
        print(f"{nombre} {correo}")
    else:
        print(f"{correo}")
