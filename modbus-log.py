'''----------------Antes de modificar----------------
Este script está realizado para el laboratorio de Remediación perteneciente a la Facultad de Agronomia UANL
El funcionamiento de este es mayormente por la librería de 'pymodbus' el cual realiza la conectividad a un
puerto COM recuperando el valor deseado del sensor alojadas en su protocolo de comunicación.
--------------------------------------------------'''

import threading
import queue
from pymodbus.client import ModbusSerialClient
import time
import sqlite3
from datetime import datetime


# Dirección de alojamiento del archivo de base de datos SQLite
DB_NAME = "C:/SQLite/remediacion_2024.db"

# Tiempo asignado para añadir registro a la tabla
t_registro = 60
# Tiempo asignado para el muestreo de datos en consola
t_muestreo = 2


detener_hilos = False
lock = threading.Lock()
cola_lecturas = queue.Queue()
sqlite3.register_adapter(datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))
sqlite3.register_converter("DATETIME", lambda s: datetime.strptime(s.decode(), "%Y-%m-%d %H:%M:%S"))


# Este método realiza la conectividad de SQLite y crea la tabla "sensor_logs" en caso de que no exista
# En caso de querer modificar las cabeceras de la tabla realizarlo en este apartado (restableciendo el archivo de la db)
def init_db():
    conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            CO2_IN INTEGER,
            NO2_IN INTEGER,
            SO2_IN INTEGER,
            TEMP_1 INTEGER,
            CO2_OUT INTEGER,
            NO2_OUT INTEGER,
            SO2_OUT INTEGER,
            TEMP_2 INTEGER
        )
    """)
    conn.commit()
    print("[SQLite] Conexión a la base de datos realizada con éxito.")
    conn.close()


# Insertar lecturas, como su nombre indica recolecta los registros de los puertos y los inserta como un nuevo registro de la tabla.
# Este método funciona con la Queue, creando una cola de espera para que cada variable esté en su sitio para su inserción.
def insertar_lecturas():
    while not detener_hilos or not cola_lecturas.empty():
        try:
            registros = cola_lecturas.get(timeout=1)
            conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            timestamp = datetime.now()

            cursor.execute("""
                INSERT INTO sensor_logs (timestamp,
                CO2_IN, NO2_IN, SO2_IN,TEMP_1,
                CO2_OUT, NO2_OUT, SO2_OUT, TEMP_2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, *registros))

            conn.commit()
            print(f"[SQLite] Datos insertados correctamente: {registros}")
            conn.close()

        except queue.Empty:
            pass


'''Método principal de todo el proyecto este requiere de los parametros: 
Puerto que determina la dirección COM donde se establece la conexión
Nombre este es meramente indicativo para poder identificar los puertos y valores que se rastrean
Lecturas lista temporal para mostrar en consola las lecturas en tiempo real'''
def read_modbus(port, nombre_dispositivo, lecturas):
    while not detener_hilos:
        try:
            client = ModbusSerialClient(port=port, baudrate=4800, timeout=1)
            if not client.connect():
                print(f"[PySerial] No se pudo conectar a {nombre_dispositivo} ({port}).")
                time.sleep(5)
                continue

            print(f"[PySerial] Conectado a {nombre_dispositivo} ({port})")

            while not detener_hilos:
                try:
                    result = client.read_holding_registers(0, 11, slave=1)
                    if result.isError():
                        print(f"[Modbus] Error en {nombre_dispositivo}: {result}")
                    else:
                        primer_registro = result.registers[0]
                        print(f"[Modbus] {nombre_dispositivo}: {primer_registro}")

                        with lock:
                            lecturas[nombre_dispositivo] = primer_registro  

                except Exception as e:
                    print(f"[Modbus] Excepción en {nombre_dispositivo}: {e}")
                    break

                time.sleep(t_muestreo)

        except Exception as e:
            print(f"[PySerial] Excepción general en {nombre_dispositivo}: {e}")

        finally:
            client.close()
            time.sleep(5)


# Esta clase requiere de la lista de lecturas para añadirla en la cola de insersión de registros, aqui se puede modificar el tiempo de registro
# Cuidar las etiquetas de clave valor asignados en la lista de "dispositivos".
def recolectar_lecturas(lecturas):
    while not detener_hilos:
        time.sleep(t_registro)

        with lock:
            registros = [
                lecturas.get('CO2_IN', None), 
                lecturas.get('NO2_IN', None),
                lecturas.get('SO2_IN', None),
                lecturas.get('TEMP_1', None),
                lecturas.get('CO2_OUT', None),
                lecturas.get('CO2_OUT', None),
                lecturas.get('SO2_OUT', None),
                lecturas.get('TEMP_2', None)
            ]

        print(f"[QUEUE] Lecturas recolectadas: {registros}")
        # Envía las lecturas a la cola para insertar
        cola_lecturas.put(registros)  


# *****************************************************INICIO DE EJECUCIÓN*****************************************************

print('''------------------------------------------------------------------
                LABORATORIO DE REMEDIACIÓN 2024
      Registro de sensores por protocolo RS485 Modbus RTU
      
      Para detener el proceso cierre la ventana o presione
                        [CTRL + C]
------------------------------------------------------------------''')
time.sleep(10)

# Se abre o crea la base de datos y la tabla para almacenar los datos
init_db()
time.sleep(2)

# Lista global de los dispositivos conectados al ordenador, aqui se modifica la dirección COM que se encuentra el sensor.
dispositivos = {
    'COM4': 'CO2_IN',
    'COM5': 'NO2_IN',
    'COM3': 'SO2_IN'
    # 'COM7': 'TEMP_1',
    # 'COM8': 'CO2_OUT',
    # 'COM9': 'NO2_OUT',
    # 'COM10': 'SO2_OUT',
    # 'COM11': 'TEMP_2'
}

# Lista global de las lecturas recibidas en tiempo real
lecturas = {}

# Lista global que contendrá todos los hilos de ejecución de los sensores
hilos = []


# Se recorre la lista dispositivos y se genera una instancia thread para cada uno repitiendo el método "read_modbus"
for puerto, nombre in dispositivos.items():
    hilo = threading.Thread(target=read_modbus, args=(puerto, nombre, lecturas))
    hilo.start()
    hilos.append(hilo)

# Se define un nuevo hilo controlador de "recolectar_lecturas" para insertar los registros a la tabla
hilo_recolector = threading.Thread(target=recolectar_lecturas, args=(lecturas,))
hilo_recolector.start()
hilos.append(hilo_recolector)

# Crear y lanzar el hilo para insertar lecturas en la base de datos
hilo_insercion = threading.Thread(target=insertar_lecturas)
hilo_insercion.start()
hilos.append(hilo_insercion)

# Se añade un control de pausa a todos los hilos mediante la combinación "CTRL + C"
try:
    while any(hilo.is_alive() for hilo in hilos):
        time.sleep(1)
except KeyboardInterrupt:
    print("[Threads] Interrupción detectada, deteniendo hilos...")
    detener_hilos = True

# Esperar a que todos los hilos terminen
for hilo in hilos:
    hilo.join()

print("\r[Threads] Todos los hilos terminados.")
