import threading
import queue
from pymodbus.client import ModbusSerialClient
import time
import sqlite3
from datetime import datetime

detener_hilos = False
DB_NAME = "C:/SQLite/remediacion_2024.db"
lock = threading.Lock()  # Lock para sincronizar lecturas
cola_lecturas = queue.Queue()  # Cola para almacenar lecturas a insertar

# Adaptadores para datetime -> string y viceversa
sqlite3.register_adapter(datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))
sqlite3.register_converter("DATETIME", lambda s: datetime.strptime(s.decode(), "%Y-%m-%d %H:%M:%S"))

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe."""
    conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            registro_com1 INTEGER,
            registro_com2 INTEGER,
            registro_com3 INTEGER,
            registro_com4 INTEGER,
            registro_com5 INTEGER,
            registro_com6 INTEGER,
            registro_com7 INTEGER,
            registro_com8 INTEGER
        )
    """)
    conn.commit()
    print("[SQLite] Conexión a la base de datos realizada con éxito.")
    conn.close()

def insertar_lecturas():
    """Hilo dedicado a insertar lecturas en la base de datos."""
    while not detener_hilos or not cola_lecturas.empty():
        try:
            registros = cola_lecturas.get(timeout=1)  # Espera un nuevo lote de lecturas
            conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            timestamp = datetime.now()

            cursor.execute("""
                INSERT INTO sensor_logs (timestamp, registro_com1, registro_com2, registro_com3,
                                          registro_com4, registro_com5, registro_com6, 
                                          registro_com7, registro_com8)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, *registros))

            conn.commit()
            print(f"[SQLite] Datos insertados correctamente: {registros}")
            conn.close()

        except queue.Empty:
            pass  # Si la cola está vacía, sigue esperando

def read_modbus(port, nombre_dispositivo, lecturas):
    """Intenta conectar al puerto y leer datos continuamente."""
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

                time.sleep(2)

        except Exception as e:
            print(f"[PySerial] Excepción general en {nombre_dispositivo}: {e}")

        finally:
            client.close()
            time.sleep(5)

def recolectar_lecturas(lecturas):
    """Reúne las lecturas de todos los dispositivos cada 10 segundos."""
    while not detener_hilos:
        time.sleep(60)

        with lock:
            registros = [
                lecturas.get('CO2', None), 
                lecturas.get('NO2', None),
                lecturas.get('COM6', None),
                lecturas.get('COM7', None),
                lecturas.get('COM8', None),
                lecturas.get('COM9', None),
                lecturas.get('COM10', None),
                lecturas.get('COM11', None)
            ]

        print(f"[QUEUE] Lecturas recolectadas: {registros}")
        cola_lecturas.put(registros)  # Envía las lecturas a la cola para insertar

# Inicializa la base de datos
init_db()

# Diccionario de puertos con nombres descriptivos
dispositivos = {
    'COM4': 'CO2',
    'COM5': 'NO2'
    # 'COM6': 'Medidor de Presión',
    # 'COM7': 'Sensor de Humedad',
    # 'COM8': 'Control de Luz',
    # 'COM9': 'Medidor de Flujo',
    # 'COM10': 'Sensor de Nivel',
    # 'COM11': 'Control de Ventilación'
}

# Diccionario para almacenar lecturas
lecturas = {}

# Crear y lanzar hilos para cada puerto
hilos = []
for puerto, nombre in dispositivos.items():
    hilo = threading.Thread(target=read_modbus, args=(puerto, nombre, lecturas))
    hilo.start()
    hilos.append(hilo)

# Crear y lanzar el hilo para recolectar lecturas
hilo_recolector = threading.Thread(target=recolectar_lecturas, args=(lecturas,))
hilo_recolector.start()
hilos.append(hilo_recolector)

# Crear y lanzar el hilo para insertar lecturas en la base de datos
hilo_insercion = threading.Thread(target=insertar_lecturas)
hilo_insercion.start()
hilos.append(hilo_insercion)

# Manejar interrupción con Ctrl+C para detener los hilos
try:
    while any(hilo.is_alive() for hilo in hilos):
        time.sleep(1)
except KeyboardInterrupt:
    print("[Threads] Interrupción detectada, deteniendo hilos...")
    detener_hilos = True

# Esperar a que todos los hilos terminen
for hilo in hilos:
    hilo.join()

print("[Threads] Todos los hilos terminados.")
