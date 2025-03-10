from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import mysql.connector
import requests

# Configuración de MySQL
mysql_config = {
    'user': 'root',
    'password': 'almanaque',
    'host': '127.0.0.1',
    'database': 'sys'
}

app = Flask(__name__)

# Función para cargar palabras peligrosas
def cargar_palabras_ilegales(archivo='C:/Users/Withe/OneDrive/Documents/palabras_peligrosas.csv'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            palabras = f.read().splitlines()
            print("Palabras peligrosas cargadas:", palabras)  # Debug
            return [palabra.strip().lower() for palabra in palabras]  # Asegurar que están en minúsculas y sin espacios
    except Exception as e:
        print(f"Error al cargar palabras ilegales: {e}")
        return []

# Función para obtener geolocalización
def obtener_geolocalizacion(ip):
    # Tu lógica de geolocalización aquí
    return {'latitud': None, 'longitud': None, 'pais': None, 'region': None, 'ciudad': None}

# Función para registrar consultas
def registrar_consulta(consulta, palabras_ilegales):
    ip_usuario = '127.0.0.1'
    consulta_lower = consulta.lower()
    print(f"Consulta en minúsculas: {consulta_lower}")  # Debug

    # Verificar si hay alguna palabra peligrosa en la consulta
    palabras_encontradas = [palabra for palabra in palabras_ilegales if palabra in consulta_lower]
    es_peligrosa = bool(palabras_encontradas)
    print(f"Consulta: '{consulta}', ¿Es peligrosa? {es_peligrosa}, Palabras encontradas: {palabras_encontradas}")  # Debug

    if es_peligrosa:
        geolocalizacion = obtener_geolocalizacion(ip_usuario)
        try:
            with mysql.connector.connect(**mysql_config) as connection:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO consultas_peligrosas2 
                    (consulta, ip, latitud, longitud, pais, region, ciudad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        consulta, ip_usuario,
                        geolocalizacion['latitud'],
                        geolocalizacion['longitud'],
                        geolocalizacion['pais'],
                        geolocalizacion['region'],
                        geolocalizacion['ciudad']
                    )
                    print(f"Ejecutando SQL: {sql} con valores: {val}")  # Debug
                    cursor.execute(sql, val)
                    connection.commit()
            return {'mensaje': "Consulta peligrosa registrada exitosamente."}
        except mysql.connector.Error as error:
            print(f"Error al insertar la consulta: {error}")  # Debug
            return {'error': f"Error al insertar la consulta: {error}"}
    else:
        return {'mensaje': "Consulta segura. No se registrará en la base de datos."}

# Endpoint para manejar mensajes de WhatsApp
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    mensaje = request.form.get('Body')
    telefono = request.form.get('From')

    if not mensaje:
        respuesta = MessagingResponse()
        respuesta.message("No se recibió ningún mensaje.")
        return str(respuesta)

    # Procesar el mensaje
    palabras_ilegales = cargar_palabras_ilegales()
    print(f"Mensaje recibido: {mensaje}")  # Debug
    resultado = registrar_consulta(mensaje, palabras_ilegales)

    # Responder al usuario
    respuesta = MessagingResponse()
    respuesta.message(resultado.get('mensaje', "Error procesando la consulta."))
    return str(respuesta)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
