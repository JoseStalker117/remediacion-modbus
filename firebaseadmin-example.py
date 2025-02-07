import pyrebase
import time

config = {
    # "apiKey": "tu_api_key",
    # "authDomain": "tu_auth_domain",
    # "databaseURL": "tu_database_url",
    # "projectId": "tu_project_id",
    # "storageBucket": "tu_storage_bucket",
    # "messagingSenderId": "tu_messaging_sender_id",
    # "appId": "tu_app_id"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()


# Inicializar Firebase
def initialize_app():
    return pyrebase.initialize_app(config)


# Obtener referencia a la base de datos en tiempo real
def database():
    firebase = pyrebase.initialize_app(config)
    return firebase.database()


def write_data(user_token, data):  # {{ edit_1 }}
    try:
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        timestamp = int(time.time())  # Obtener el timestamp actual en segundos
        db.child("Modbus").child(timestamp).set(data, user_token)  # {{ edit_2 }}
        print(f"[Firebase] Datos escritos correctamente en Modbus")
    except Exception as e:
        print(f"[Firebase] Error al escribir datos: {e}")


def login(email, password):
    try:
        firebase = pyrebase.initialize_app(config)
        user = firebase.auth().sign_in_with_email_and_password(email, password)
        print("[Firebase] Inicio de sesión exitoso.")
        user_token = user['idToken']  # {{ edit_3 }}
        return user_token  # {{ edit_4 }}
    except Exception as e:
        print(f"[Firebase] Error al iniciar sesión: {e}")
        return None