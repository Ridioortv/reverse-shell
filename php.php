<?php
// Guardar los datos recibidos en un archivo de log para depuración
file_put_contents('twilio_debug.log', print_r($_POST, true));

// Si deseas verificar la recepción visualmente
echo "<pre>";
print_r($_POST);
echo "</pre>";
?>
