# import os

import tensorflow as tf
import tensorflow_decision_forests as tfdf
from sklearn.model_selection import train_test_split
from flask import Flask, request, make_response, render_template, send_from_directory
import uuid
import numpy as np
import pandas as pd


app = Flask(__name__)

database = {}


model = tf.keras.models.load_model('modelv2')


# Fungsi untuk melakukan prediksi kanal
def predict_channel(freq, freq_pair, latitude, longitude):
    # Lakukan proses prediksi kanal berdasarkan frekuensi, latitude, dan longitude
    # Di sini Anda dapat menambahkan logika atau model prediksi yang sesuai
    
    input_features = ['FREQ', 'FREQ_PAIR', 'ERP_PWR_DBM', 'SID_LONG', 'SID_LAT']
    
    tes = np.array([[   freq, freq_pair, 53, longitude, latitude	]])
    tes_df = pd.DataFrame(tes, columns=input_features)
    tes_ds = tfdf.keras.pd_dataframe_to_tf_dataset(tes_df)


    predicted_channel = model.predict(tes_ds)  
    # Sesuaikan dengan format input yang dibutuhkan oleh model Anda
    return predicted_channel

# # Fungsi untuk mendapatkan Street View menggunakan API
# def get_street_view(latitude, longitude):
#     # Di sini tambahkan logika untuk memanggil Street View API
#     # Pastikan untuk menggunakan API key Anda
#     # Contoh sederhana untuk demonstrasi
#     street_view_url = f"https://maps.googleapis.com/maps/api/streetview?size=400x400&location={latitude},{longitude}&key=YOUR_API_KEY"
#     return street_view_url


@app.get('/')
def mainpage():
    return render_template('index.html')


@app.route('/<path:name>')
def return_flutter_doc(name):

    datalist = str(name).split('/')
    DIR_NAME = 'templates'

    if len(datalist) > 1:
        for i in range(0, len(datalist) - 1):
            DIR_NAME += '/' + datalist[i]

    return send_from_directory(DIR_NAME, datalist[-1])


# Route untuk handling permintaan chatbot
@app.post('/chatbot')
def chatbot():

    message = request.form.get('message').lower()
    
    print(message)
    
    try:
        token = request.headers['token']
    except:
        token = str(uuid.uuid1())
        database[token] = {}
        database[token]['messages'] = []

    try:
        database[token]['messages'].append({
            'role': 'user',
            'message' : message
        })
    except:
        token = str(uuid.uuid1())
        database[token] = {}
        database[token]['messages'] = [{
            'role' : 'user',
            'message' : message
        }]

    if 'selesai' in message or 'batalkan' in message:
        json_response = {
            'message' : 'Terima kasih sudah menggunakan layanan kami'
        }  
        database.pop(token)
        response = make_response(json_response)
        response.status_code = 200
        response.headers['token'] = token

        return response
    elif 'cek kanal' in message:
        text_response = "Silahkan masukkan Frekuensi (dalam satuan Hz):"
        json_response = {
            "message": text_response,
            "assist" : "freq",
            "shortcut" : [
                'batalkan',
            ]
        }
    elif 'freq' in message:
        print(message[4:])
        database[token]['freq'] = float(str(message[4:]))
        # print(database)
        text_response = "Nilai frekuensi diterima, masukkan Frekuensi Pair"
        json_response = {
            "message": text_response,
            "shortcut":[
                'Batalkan'
            ],
            "assist" : 'pair'
        }
    elif 'pair' in message:
        print(message[4:])
        database[token]['freq-pair'] = float(str(message[4:]))
        # print(database)
        text_response = "Nilai frekuensi pair diterima, selanjutnya silahkan masukkan koordinat Latitude dan Longitude lokasi Anda!"
        json_response = {
            "message": text_response,
            "shortcut":[
                'Ambil titik poin dari peta',
                'Batalkan'
            ],
            "assist" : 'latlng'
        }
    elif 'latlng' in message:
        data = message.split(', ')
        database[token]['lat'] = float(data[0][6:])
        database[token]['lon'] = float(data[1])
        
        hasil = predict_channel(database[token]['freq'], database[token]['freq-pair'], database[token]['lat'], database[token]['lon'])
        
        # result = np.array(hasil[0]).argmax()
        
        # if result == 1:
        text_response = 'Berikut hasil prediksi kanal kosong \nTersedia : ' + str(round(hasil[0][1]*100, 2)) + '%\nTersedia dengan pertimbangan : ' + str(round(hasil[0][2]*100, 2)) + '%\nTidak Tersedia : ' + str(round(hasil[0][3]*100, 2)) + '%'
        # text_response = str(hasil)
        json_response = {
            'message' : text_response,
            'shortcut' : [
                'Silahkan melanjutkan registrasi di Kominfo',
                'Selesai'
            ],
            'link' : 'https://isr.postel.go.id/'
        }
        # elif result == 2:
        #     text_response = 'Berikut hasil prediksi kanal kosong \nDisetujui dengan pertimbangan : ' + str(round(hasil[0][2]*100, 2)) + '%'
        #     json_response = {
        #         'message' : text_response,
        #         'shortcut' : [
        #             'selesai'
        #         ]
        #     }
        # elif result == 3:
        #     text_response = 'Berikut hasil prediksi kanal kosong \nDibatalkan : ' + str(round(hasil[0][3]*100, 2)) + '%'
        #     json_response = {
        #         'message' : text_response,
        #         'shortcut' : [
        #             'selesai'
        #         ]
        #     }
     
    else:
        text_response =  "Selamat datang!, Silahkan pilih menu bantuan"
        json_response = {
            "message": text_response,
            "shortcut" : [
                'Cek kanal',
                'Batalkan'
            ]
        }
        
    database[token]['messages'].append({
        'role': 'system',
        'message' : text_response
    })

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
    
    try:
        data = database[token]['messages']
    except:
        response = make_response(
            {
                "message" : [],
                "error" : "token invalid"
            }
        )
        response.status_code = 401
        return response
        
    response = make_response(
        {
            "message" : data,
            "error" : None
        }
    )
    response.status_code = 200
    return response

if __name__ == '__main__':
    app.run(debug=False)
