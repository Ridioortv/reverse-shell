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
except mysql.connector.Error as error:
    logging.error(f"Error al insertar la consulta: {error}")
    return {'error': f"Error al insertar la consulta: {error}"}
