from flask import Flask, request, make_response, jsonify
import uuid
from tensorflow_decision_forests import keras

model = keras.load_model('model')

app = Flask(__name__)

database = {}

# model = load_model('path_ke_model_yang_disimpan')
# # Fungsi untuk melakukan prediksi kanal
# def predict_channel(freq, latitude, longitude):
#     # Lakukan proses prediksi kanal berdasarkan frekuensi, latitude, dan longitude
#     # Di sini Anda dapat menambahkan logika atau model prediksi yang sesuai

#     predicted_channel = model.predict([[freq, latitude, longitude]])  
#     # Sesuaikan dengan format input yang dibutuhkan oleh model Anda
#     return predicted_channel

# # Fungsi untuk mendapatkan Street View menggunakan API
# def get_street_view(latitude, longitude):
#     # Di sini tambahkan logika untuk memanggil Street View API
#     # Pastikan untuk menggunakan API key Anda
#     # Contoh sederhana untuk demonstrasi
#     street_view_url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location={latitude},{longitude}&key=YOUR_API_KEY"
#     return street_view_url

# Route untuk handling permintaan chatbot
@app.post('/chatbot')
def chatbot():

    message = request.form.get('message').lower()
    try:
        token = request.headers['token']
    except:
        token = str(uuid.uuid1())
        database[token] = []

    try:
        database[token].append(message)
    except:
        token = str(uuid.uuid1())
        database[token] = [message]

    
    if 'cek kanal' in message:
        json_response = {
            "message": "Please enter frequency (in Hz):",
            "assist" : "FREQ"
        }
    elif 'freq' in message:
        json_response = {
            "message": "Nilai frekuensi diterima, selanjutnya silakan masukkan titik point peta",
            "shortcut":[
                'https://google.com'
            ],
            "assist" : [
                'latlng'
            ]
        }
    elif 'latlng' in message:
        json_response = {
            'message' : 'berikut hasil prediksi kanal kosong',
        }
    else:
        json_response = {
            "message": "Selamat pagi!, Silahkan pilih menu bantuan",
            "shortcut" : [
                'Cek kanal',
                'bantuan GPT AI'
            ]
        }

    response = make_response(json_response)
    response.status_code = 200
    response.headers['token'] = token

    return response


@app.get('/chatbot/all')
def getAll():
    try:
        token = request.headers['token']
    except:
        response = make_response(
            {
                "message" : [],
                "error" : "no token provide"
            }
        )
        response.status_code = 401
        return response
    
    response = make_response(
        {
            "message" : database[token],
            "error" : None
        }
    )
    response.status_code = 200
    return response

if __name__ == '__main__':
    app.run(debug=True)
