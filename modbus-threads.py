'''----------------Antes de modificar----------------
Este script está realizado para el laboratorio de Remediación perteneciente a la Facultad de Agronomia UANL
El funcionamiento de este es mayormente por la librería de 'pymodbus' el cual realiza la conectividad a un
puerto COM recuperando el valor deseado del sensor alojadas en su protocolo de comunicación.
--------------------------------------------------'''

from pymodbus.client import ModbusSerialClient
import time
import sqlite3
from datetime import datetime
import threading
import os
import csv

#Introducir aquí la dirección de la base de datos
Dir_DB = "C:/SQLite/remediacion_2024.db"

#Directorio a exportar los archivos csv (Tarjeta SD)
Dir_CSV = "D:/"

#Tiempo para imprimir la información en consola (segundos).
t_muestreo = 10

#Tiempo para enviar la información a la base de datos (minutos).
t_registro = 10


sqlite3.register_adapter(datetime, lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"))
sqlite3.register_converter("DATETIME", lambda s: datetime.strptime(s.decode(), "%Y-%m-%d %H:%M:%S"))

def Database(db):
    try:
        conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
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
                TEMP_2 INTEGER,
                PAR INTEGER
            )""")
        conn.commit()
        print("\n[SQLite] Conexión a la base de datos realizada con éxito.\n")
        
    except Exception as e:
        print(f"[SQLite] Error al crear el archivo de SQLite. {e}\n")
        
    finally:
        if conn:
            conn.close()


def Dispositivos(lista, puerto, nombre, baudrate, paridad):
    lista.append({"Puerto": puerto, "Nombre": nombre, "Baudrate": baudrate, "Paridad": paridad})
    

def Transmisores(sensor):
    client = None
    conectado = False
    while True:
        time.sleep(t_muestreo)
        try:
            if not client:
                client = ModbusSerialClient(port=sensor['Puerto'], 
                                            baudrate=sensor['Baudrate'], 
                                            parity=sensor['Paridad'], 
                                            stopbits=1, 
                                            bytesize=8, 
                                            timeout=1)
                
            if not client.connect():
                if conectado:
                    print(f"[PySerial] No se pudo conectar al puerto {sensor['Puerto']}-{sensor['Nombre']}")
                    conectado = False
                time.sleep(2)
                continue
            
            if not conectado:
                print(f"[PySerial] Conectado al puerto {sensor['Puerto']}-{sensor['Nombre']}.")
                conectado = True

            result = client.read_holding_registers(0)
            if result.isError():
                print(f"[Modbus] Error en {sensor['Puerto']}-{sensor['Nombre']}: {result}")
            else:
                with lock:
                    registros[sensor["Nombre"]] = {"Valor": result.registers[0]}

        except Exception as e:
            print(f"[Modbus] Excepción en {sensor['Puerto']}-{sensor['Nombre']}: {e}")
            
        finally:
            if client:
                client.close()
                client = None
            


def ImprimirRegistros():
    while True:
        time.sleep(t_muestreo)
        with lock:
            print(f"[Registros] Estado actual: {registros}")
        
        
        
def Querry():
    while True:
        time.sleep(t_registro * 60)
        try:
            conn = sqlite3.connect(Dir_DB)
            cursor = conn.cursor()
            timestamp = datetime.now()

            with lock:
                datos = {nombre: registro["Valor"] for nombre, registro in registros.items()}

            # Verificar si hay datos para insertar
            if not datos:
                print(f"[SQLite] No hay datos para registrar en {timestamp}.")
            else:
                columnas = ", ".join(datos.keys())
                valores_placeholder = ", ".join(["?"] * len(datos))
                query = f"""
                INSERT INTO sensor_logs (timestamp, {columnas})
                VALUES (?, {valores_placeholder})
                """
                valores = [timestamp] + list(datos.values())

                cursor.execute(query, valores)
                conn.commit()
                print(f"[SQLite] Registro insertado: {datos} en {timestamp}")
                ExportarCSV()

        except sqlite3.Error as e:
            print(f"[SQLite] Error al insertar datos: {e}")

        except Exception as e:
            print(f"[Python] Error inesperado: {e}")

        finally:
            if conn:
                conn.close()


def ExportarCSV():
    try:
        # Obtener la fecha actual en formato YYYY-MM-DD
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        archivo_csv = os.path.join(Dir_CSV, f"{fecha_actual}.csv")

        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(Dir_DB)
        cursor = conn.cursor()

        # Consulta para obtener todos los datos del día actual
        consulta = f"""
            SELECT * FROM sensor_logs
            WHERE DATE(timestamp) = ?
        """
        cursor.execute(consulta, (fecha_actual,))
        filas = cursor.fetchall()

        # Obtener los nombres de las columnas
        columnas = [descripcion[0] for descripcion in cursor.description]

        # Escribir el archivo CSV
        with open(archivo_csv, mode="w", newline="") as archivo:
            escritor = csv.writer(archivo, delimiter=',')
            
            # Escribir encabezados
            escritor.writerow(columnas)

            # Escribir los datos
            escritor.writerows(filas)
            print(f"[CSV] Datos exportados a {archivo_csv} con {len(filas)} registros.")

    except sqlite3.Error as e:
        print(f"[SQLite] Error al consultar la base de datos: {e}")

    except Exception as e:
        print(f"[CSV] Error al exportar datos: {e}")

    finally:
        if conn:
            conn.close()


# *****************************************************INICIO DE EJECUCIÓN*****************************************************

print('''------------------------------------------------------------------
                LABORATORIO DE REMEDIACIÓN 2024
      Registro de sensores por protocolo RS485 Modbus RTU
      
            Para detener el proceso cierre la ventana
------------------------------------------------------------------''')
time.sleep(10)

Database(Dir_DB)

#-----Lista global con los sensores a monitorear.
Sensores = []

#-----Conjunto 1 de transmisores-----
Dispositivos(Sensores, 'COM8', 'CO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM9', 'NO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM10', 'SO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM7', 'TEMP_1', 9600, 'N')
#-----Conjunto 2 de transmisores-----
Dispositivos(Sensores, 'COM11', 'CO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM12', 'NO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM13', 'SO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM14', 'TEMP_2', 9600, 'N')
#-----Sensor de Radiación fotosintética-----
Dispositivos(Sensores, 'COM19', 'PAR', 4800, 'N')


registros = {}
lock = threading.Lock()

threads = []

#Hilos de sensores
for sensor in Sensores:
    thread = threading.Thread(target=Transmisores, args=(sensor,))
    threads.append(thread)
    thread.start()

#Hilo de Muestreo
thread = threading.Thread(target=ImprimirRegistros)
threads.append(thread)
thread.start()

#Hilos de Querry
thread = threading.Thread(target=Querry)
threads.append(thread)
thread.start()
    
for thread in threads:
    thread.join()

print("[Threads] Hilos creados correctamente.")