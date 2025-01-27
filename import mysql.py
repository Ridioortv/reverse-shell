import mysql.connector

mysql_config = {
    'user': 'root',
    'password': 'almanaque',
    'host': '127.0.0.1',
    'database': 'sys'
}

try:
    connection = mysql.connector.connect(**mysql_config)
    if connection.is_connected():
        print("Conectado a MySQL")
    connection.close()
except mysql.connector.Error as error:
    print(f"Error de conexión: {error}")
