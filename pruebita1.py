import os 
import logging
import pandas as pd
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import mysql.connector
import requests

# Configuración del registro de logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de MySQL a través de variables de entorno
mysql_config = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'almanaque'),
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'database': os.getenv('MYSQL_DATABASE', 'sys')
}

app = Flask(__name__)

# Cache para palabras ilegales
palabras_ilegales_cache = []

def cargar_palabras_ilegales(archivo='G:\\venice\\palabras peligrosas.csv'):
    """Carga las palabras peligrosas desde un archivo CSV, utilizando un caché."""
    global palabras_ilegales_cache
    if not palabras_ilegales_cache:
        try:
            # Leer el archivo CSV
            df = pd.read_csv(archivo, header=None)
            palabras_ilegales_cache = df[0].tolist()  # Convertir a lista
            logging.info(f"Palabras peligrosas cargadas correctamente: {palabras_ilegales_cache}")
        except Exception as e:
            logging.error(f"Error al cargar palabras ilegales: {e}")
            palabras_ilegales_cache = []
    return palabras_ilegales_cache

def obtener_geolocalizacion(ip):
    """Obtiene la geolocalización basada en la IP usando ip-api.com."""
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
        logging.error(f"No se pudo obtener la geolocalización: {e}")
        return {'latitud': None, 'longitud': None, 'pais': None, 'region': None, 'ciudad': None}

def registrar_consulta(consulta, palabras_ilegales):
    """Registra una consulta en la base de datos si contiene palabras peligrosas."""
    ip_usuario = '127.0.0.1'  # Twilio no proporciona la IP real del usuario
    consulta_lower = consulta.lower()
    es_peligrosa = any(palabra.strip().lower() in consulta_lower for palabra in palabras_ilegales)
    logging.debug(f"Consulta '{consulta}', ¿Es peligrosa? {es_peligrosa}")

    if es_peligrosa:
        logging.debug("La consulta es peligrosa, proceder a registrar.")
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
            logging.info("Consulta peligrosa registrada exitosamente.")
            return {'mensaje': "Consulta peligrosa registrada exitosamente."}
        except mysql.connector.Error as error:
            logging.error(f"Error al insertar la consulta: {error}")
            return {'error': f"Error al insertar la consul
