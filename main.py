from flask import Flask, request, jsonify
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

# Funciones del programa original
def cargar_palabras_ilegales(archivo='G:/peligro.txt'):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    except Exception as e:
        print(f"Error al cargar palabras ilegales: {e}")
        return []

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

def obtener_ip_publica():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json().get('ip')
    except Exception as e:
        print(f"No se pudo obtener la IP pública: {e}")
        return None

def registrar_consulta(consulta, palabras_ilegales):
    ip_usuario = obtener_ip_publica()
    if not ip_usuario:
        return {"error": "No se pudo obtener la IP pública."}

    if any(palabra.strip().lower() in consulta.lower() for palabra in palabras_ilegales):
        geolocalizacion = obtener_geolocalizacion(ip_usuario)
        try:
            with mysql.connector.connect(**mysql_config) as connection:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO consultas_peligrosas 
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
            return {"mensaje": "Consulta peligrosa registrada exitosamente."}
        except mysql.connector.Error as error:
            return {"error": f"Error al insertar la consulta: {error}"}
    else:
        return {"mensaje": "Consulta segura. No se registrará en la base de datos."}

# Endpoint para registrar consultas
@app.route('/consultas', methods=['POST'])
def consultas():
    data = request.json
    consulta = data.get('consulta')
    if not consulta:
        return jsonify({"error": "Consulta no proporcionada"}), 400
    
    palabras_ilegales = cargar_palabras_ilegales()
    resultado = registrar_consulta(consulta, palabras_ilegales)
    return jsonify(resultado), 200

# Endpoint para obtener palabras ilegales
@app.route('/palabras-ilegales', methods=['GET'])
def palabras_ilegales():
    palabras = cargar_palabras_ilegales()
    return jsonify({"palabras_ilegales": palabras}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
