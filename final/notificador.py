import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_config import get_db_connection
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_asunto(asunto):
    if not isinstance(asunto, str):
        asunto = str(asunto)  # Convertir a cadena si no lo es
    return asunto

def enviar_alerta_stock(destinatario, alertas):
    remitente = os.environ.get("CORREO_ALERTAS")
    clave = os.environ.get("CLAVE_CORREO")
    
    asunto = "⚠️ Alerta de Stock Bajo"
    asunto = obtener_asunto(asunto)  # Asegurar que el asunto sea un string

    cuerpo = "Los siguientes productos están por debajo del stock mínimo:\n\n"
    for alerta in alertas:
        cuerpo += f"- {alerta['nombre']} (Stock actual: {alerta['stock_actual']}, Mínimo: {alerta['cantidad_minima']})\n"

    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conexión al servidor SMTP
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remitente, clave)
        servidor.send_message(mensaje)
        servidor.quit()
        return True
    except Exception as e:
        return False, str(e)

def comprobar_bajo_stock():
    """Consulta los productos con stock bajo y envía alertas por correo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, stock_actual, cantidad_minima FROM productos WHERE stock_actual <= cantidad_minima")
    productos_bajos = cursor.fetchall()
    
    alertas = []
    for prod in productos_bajos:
        alertas.append({
            "nombre": prod[0],
            "stock_actual": prod[1],
            "cantidad_minima": prod[2]
        })

    cursor.close()
    conn.close()

    if alertas:
        # Enviar correo con las alertas
        destinatario = os.environ.get("CORREO_DESTINO")  # Correo para recibir las alertas
        resultado = enviar_alerta_stock(destinatario, alertas)
        return resultado
    else:
        return "No hay productos con stock bajo."
