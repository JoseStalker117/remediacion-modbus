import firebase_admin
from firebase_admin import credentials, db
import time, os
from datetime import datetime


cred = credentials.Certificate('Firebase-admin.json')

# Inicializar Firebase Admin SDK
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tu-proyecto.firebaseio.com'
    })
    print("[Firebase] Conexión inicializada correctamente")
except ValueError:
    print("[Firebase] Firebase ya está inicializado")
except Exception as e:
    print(f"[Firebase] Error al inicializar: {e}")

def timestamp():
    return int(time.time())

def write_data(registros):
    try:
        ref = db.reference('Modbus')
        
        datos_sensores = {}
        for nombre, datos in registros.items():
            datos_sensores[nombre] = datos['Valor']
        
        ref.child(str(timestamp())).set(datos_sensores)
        
        print(f"[Firebase] Datos insertados en nodo 'Modbus/{timestamp()}': {len(registros)} sensores")
        
    except Exception as e:
        print(f"[Firebase] Error al escribir datos: {e}")