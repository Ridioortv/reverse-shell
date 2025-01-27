import mysql.connector

# Configuración de MySQL
mysql_config = {
    'user': 'root',  # Cambia esto si es necesario
    'password': 'almanaque',
    'host': '127.0.0.1',
    'database': 'sys'
}

def probar_conexion():
    try:
        connection = mysql.connector.connect(**mysql_config)
        if connection.is_connected():
            print("Conexión exitosa a la base de datos.")
            # Prueba una inserción
            with connection.cursor() as cursor:
                sql = "INSERT INTO consultas_peligrosas2 (consulta, ip, latitud, longitud, pais, region, ciudad) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = ("Prueba de inserción", "127.0.0.1", None, None, None, None, None)
                cursor.execute(sql, val)
                connection.commit()
                print("Inserción realizada con éxito.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

probar_conexion()
