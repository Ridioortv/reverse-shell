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
def cargar_palabras_ilegales(archivo='C:/Users/Withe/OneDrive/Documents/palabras peligrosas.txt'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            palabras = f.read().splitlines()
            print("Palabras peligrosas cargadas:", palabras)  # Debug
            return palabras
    except Exception as e:
        print(f"Error al cargar palabras ilegales: {e}")
        return []

# Función para obtener geolocalización
def obtener_geolocalizacion(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data['status'] == 'fail':
            return {'latitud': None, 'longitud': None, 'pais': None, 'region': None, 'ciudad': None}
        return {
            'latitud': data.get('lat'),
            'longitud': data.get('lon'),
            'pais': data.get('country'),
            'region': data.get('regionName'),
            'ciudad': data.get('city')
        }
    except Exception as e:
        print(f"No se pudo obtener la geolocalización: {e}")
        return {'latitud': None, 'longitud': None, 'pais': None, 'region': None, 'ciudad': None}

# Función para registrar consultas
def registrar_consulta(consulta, palabras_ilegales):
    ip_usuario = '127.0.0.1'  # Twilio no proporciona IP real del usuario
    consulta_lower = consulta.lower()
    es_peligrosa = any(palabra.strip().lower() in consulta_lower for palabra in palabras_ilegales)
    print(f"Consulta '{consulta}', Palabras peligrosas: {palabras_ilegales}, ¿Es peligrosa? {es_peligrosa}")  # Debug

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
                    cursor.execute(sql, val)
                    connection.commit()
            return {'mensaje': "Consulta peligrosa registrada exitosamente."}
        except mysql.connector.Error as error:
            return {'error': f"Error al insertar la consulta: {error}"}
    else:
        return {'mensaje': "Consulta segura. No se registrará en la base de datos."}

# Endpoint para manejar mensajes de WhatsApp
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    # Extraer datos del mensaje entrante de Twilio
    mensaje = request.form.get('Body')  # Texto enviado por el usuario
    telefono = request.form.get('From')  # Número del remitente

    if not mensaje:
        respuesta = MessagingResponse()
        respuesta.message("No se recibió ningún mensaje.")
        return str(respuesta)

    # Procesar el mensaje
    palabras_ilegales = cargar_palabras_ilegales()
    resultado = registrar_consulta(mensaje, palabras_ilegales)

    # Responder al usuario
    respuesta = MessagingResponse()
    respuesta.message(resultado.get('mensaje', "Error procesando la consulta."))
    return str(respuesta)

# Endpoint para obtener palabras ilegales (para pruebas)
@app.route('/palabras-ilegales', methods=['GET'])
def palabras_ilegales():
    palabras = cargar_palabras_ilegales()
    return jsonify({'palabras_ilegales': palabras}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
