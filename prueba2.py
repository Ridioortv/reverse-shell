@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Maneja los mensajes entrantes de WhatsApp desde Twilio."""
    mensaje = request.form.get('Body')  # Texto enviado por el usuario
    telefono = request.form.get('From')  # Número del remitente

    logging.debug(f"Mensaje recibido: {mensaje} de {telefono}")

    if not mensaje:
        respuesta = MessagingResponse()
        respuesta.message("No se recibió ningún mensaje.")
        return str(respuesta)

    palabras_ilegales = cargar_palabras_ilegales()  # Carga las palabras desde el archivo
    resultado = registrar_consulta(mensaje, palabras_ilegales)

    respuesta = MessagingResponse()
    if resultado.get('error'):
        respuesta.message(f"Hubo un problema al procesar tu consulta. Detalle: {resultado['error']}")
    else:
        respuesta.message(resultado.get('mensaje', "Consulta procesada correctamente."))
    return str(respuesta)
