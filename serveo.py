from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return "¡Hola, Serveo!"

if _name_ == '_main_':
    app.run(port=5000)  # Asegúrate de que se ejecute en el puerto 5000