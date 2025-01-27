from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms():
    data = request.form
    message = data['Body']
    response = "Recibido: " + message
    return jsonify({'message': response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
