from pymodbus.client import ModbusSerialClient
import time
import sqlite3
from datetime import datetime
import threading

#Introducir aquí la dirección de la base de datos
Dir_DB = "C:/SQLite/remediacion_2024.db"

#Directorio a exportar los archivos csv (Tarjeta SD)
Dir_CSV = "D:/"

#Tiempo para imprimir la información en consola (segundos).
muestreo = 10

#Tiempo para enviar la información a la base de datos (minutos).
registro = 10



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
        print("[SQLite] Conexión a la base de datos realizada con éxito.")
        conn.close()
    except Exception as e:
        print(f"[SQLite] Error al crear el archivo de SQLite.\n {e}")
        

def Dispositivos(lista, puerto, nombre, baudrate, paridad):
    lista.append({"Puerto": puerto, "Nombre": nombre, "Baudrate": baudrate, "Paridad": paridad})
    

def Transmisores(Sensor):
    while True:
        try:
            client = ModbusSerialClient(port=sensor['Puerto'], baudrate=sensor['Baudrate'], parity=sensor['Paridad'], stopbits=1, bytesize=8, timeout=3)
            if not client.connect():
                print(f"[PySerial] No se pudo conectar al puerto {sensor['Puerto']}-{sensor['Nombre']}")
                continue
                        
            print(f"[PySerial] Conectado al puerto {sensor['Puerto']}-{sensor['Nombre']}.")

            try:
                result = client.read_holding_registers(0)
                if result.isError():
                    print(f"[Modbus] Error en {sensor['Puerto']}-{sensor['Nombre']}: {result}")
                else:
                    #Añadir a la lista de valores
                    print(f"[Modbus] {result.registers[0]}")
            except Exception as e:
                print(f"[Modbus] Excepción en {sensor['Puerto']}-{sensor['Nombre']}: {e}")
                break  
                        
        except Exception as e:
                    print(f"[PySerial] Excepción general {sensor['Puerto']}-{sensor['Nombre']}: {e}")
                    
        finally:
            client.close()
            time.sleep(muestreo)


# *****************************************************INICIO DE EJECUCIÓN*****************************************************

print('''------------------------------------------------------------------
                LABORATORIO DE REMEDIACIÓN 2024
      Registro de sensores por protocolo RS485 Modbus RTU
      
            Para detener el proceso cierre la ventana
------------------------------------------------------------------''')
time.sleep(3)

Database(Dir_DB)

#-----Lista global con los sensores a monitorear.
Sensores = []

#-----Conjunto 1 de transmisores-----
Dispositivos(Sensores, 'COM7', 'CO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM8', 'NO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM9', 'SO2_IN', 4800, 'N')
Dispositivos(Sensores, 'COM10', 'TEMP_1', 9600, 'E')
#-----Conjunto 2 de transmisores-----
Dispositivos(Sensores, 'COM11', 'CO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM12', 'NO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM13', 'SO2_OUT', 4800, 'N')
Dispositivos(Sensores, 'COM14', 'TEMP_2', 9600, 'E')
#-----Sensor de Radiación fotosintética-----
Dispositivos(Sensores, 'COM15', 'PAR', 4800, 'N')


threads = []

for sensor in Sensores:
    thread = threading.Thread(target=Transmisores, args=(sensor,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("[Threads] Hilos creados correctamente.")


Sensores 