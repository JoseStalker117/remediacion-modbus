import os
from dotenv import load_dotenv

# Cargar variables de entorno desde config.env
load_dotenv('config.env')

class Config:
    """Clase para manejar la configuración del sistema de sensores Modbus"""
    
    # Configuración de Base de Datos
    DB_PATH = os.getenv('DB_PATH', 'C:/SQLite/remediacion_2024.db')
    CSV_EXPORT_DIR = os.getenv('CSV_EXPORT_DIR', 'D:/')
    
    # Configuración de tiempos
    SAMPLE_TIME = int(os.getenv('SAMPLE_TIME', 10))
    REGISTRATION_TIME = int(os.getenv('REGISTRATION_TIME', 600))
    
    # Configuración de comunicación Modbus
    MODBUS_TIMEOUT = int(os.getenv('MODBUS_TIMEOUT', 1))
    MODBUS_STOPBITS = int(os.getenv('MODBUS_STOPBITS', 1))
    MODBUS_BYTESIZE = int(os.getenv('MODBUS_BYTESIZE', 8))
    MODBUS_REGISTER_ADDRESS = int(os.getenv('MODBUS_REGISTER_ADDRESS', 0))
    
    # Configuración de reintentos
    CONNECTION_RETRY_DELAY = int(os.getenv('CONNECTION_RETRY_DELAY', 2))
    
    # Configuración de sensores
    SENSORS = {
        'CO2_IN': {
            'port': os.getenv('SENSOR_CO2_IN_PORT', 'COM8'),
            'baudrate': int(os.getenv('SENSOR_CO2_IN_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_CO2_IN_PARITY', 'N')
        },
        'NO2_IN': {
            'port': os.getenv('SENSOR_NO2_IN_PORT', 'COM9'),
            'baudrate': int(os.getenv('SENSOR_NO2_IN_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_NO2_IN_PARITY', 'N')
        },
        'SO2_IN': {
            'port': os.getenv('SENSOR_SO2_IN_PORT', 'COM10'),
            'baudrate': int(os.getenv('SENSOR_SO2_IN_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_SO2_IN_PARITY', 'N')
        },
        'TEMP_1': {
            'port': os.getenv('SENSOR_TEMP_1_PORT', 'COM7'),
            'baudrate': int(os.getenv('SENSOR_TEMP_1_BAUDRATE', 9600)),
            'parity': os.getenv('SENSOR_TEMP_1_PARITY', 'N')
        },
        'CO2_OUT': {
            'port': os.getenv('SENSOR_CO2_OUT_PORT', 'COM11'),
            'baudrate': int(os.getenv('SENSOR_CO2_OUT_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_CO2_OUT_PARITY', 'N')
        },
        'NO2_OUT': {
            'port': os.getenv('SENSOR_NO2_OUT_PORT', 'COM12'),
            'baudrate': int(os.getenv('SENSOR_NO2_OUT_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_NO2_OUT_PARITY', 'N')
        },
        'SO2_OUT': {
            'port': os.getenv('SENSOR_SO2_OUT_PORT', 'COM13'),
            'baudrate': int(os.getenv('SENSOR_SO2_OUT_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_SO2_OUT_PARITY', 'N')
        },
        'TEMP_2': {
            'port': os.getenv('SENSOR_TEMP_2_PORT', 'COM14'),
            'baudrate': int(os.getenv('SENSOR_TEMP_2_BAUDRATE', 9600)),
            'parity': os.getenv('SENSOR_TEMP_2_PARITY', 'N')
        },
        'PAR': {
            'port': os.getenv('SENSOR_PAR_PORT', 'COM19'),
            'baudrate': int(os.getenv('SENSOR_PAR_BAUDRATE', 4800)),
            'parity': os.getenv('SENSOR_PAR_PARITY', 'N')
        }
    }
    
    @classmethod
    def get_sensor_config(cls, sensor_name):
        """Obtener configuración de un sensor específico"""
        return cls.SENSORS.get(sensor_name, {})
    
    @classmethod
    def get_all_sensors(cls):
        """Obtener lista de todos los sensores configurados"""
        return list(cls.SENSORS.keys())
    
    @classmethod
    def print_config(cls):
        """Imprimir toda la configuración actual"""
        print("=== CONFIGURACIÓN ACTUAL ===")
        print(f"Base de datos: {cls.DB_PATH}")
        print(f"Directorio CSV: {cls.CSV_EXPORT_DIR}")
        print(f"Tiempo de muestreo: {cls.SAMPLE_TIME} segundos")
        print(f"Tiempo de registro: {cls.REGISTRATION_TIME} segundos")
        print(f"Timeout Modbus: {cls.MODBUS_TIMEOUT} segundos")
        print("\n=== SENSORES CONFIGURADOS ===")
        for name, config in cls.SENSORS.items():
            print(f"{name}: {config['port']} @ {config['baudrate']} baud")

# Ejemplo de uso
if __name__ == "__main__":
    Config.print_config() 