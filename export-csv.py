#TODO: añadir assets al git

from pathlib import Path
from tkinter import *
import sqlite3
import csv
from datetime import datetime
import os


# <<<--- Adaptadores de Timestamp SQLite --->>>

def adapt_datetime(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(ts):
    return datetime.strptime(ts.decode(), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)


# Función que exporta la consulta que retorna la DB, requiere el objeto resultante de la DB y el DIR donde se almacenará el archivo
def export_to_csv(query_result, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        # Esta linea escribe los encabezados de la tabla a través del "query_result.description"
        csv_writer.writerow([i[0] for i in query_result.description])
        # Iteracción que escribe todos los registros encontrados en la búsqueda.
        csv_writer.writerows(query_result.fetchall())
    #TODO: añadir una ventana de confirmación tipo tkinter.
    print(f'Archivo CSV guardado como {csv_filename}')


# Función para obtener la ruta del escritorio del usuario
def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")


# Función para realizar la consulta entre dos fechas
#TODO: crear variables database y csv_filename como globales para acceder a ellas en la función
def query_between_dates(database, start_date, end_date, csv_filename):
    try:
        conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        # Adaptador de marca de tiempo SQLite
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        # Query SQLite entre las fechas seleccionadas
        query = '''SELECT * FROM sensor_logs WHERE timestamp BETWEEN ? AND ? '''
        cursor.execute(query, (start_date, end_date))

        #TODO: pasar a como variable global.
        desktop_path = get_desktop_path()
        full_csv_path = os.path.join(desktop_path, csv_filename)

        # Ejecutar la función de exportar archivo
        export_to_csv(cursor, full_csv_path)
    
    #Manejo de excepción en caso de un error.
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()




#------------------------------------Tkinter Window------------------------------------#
OUTPUT_PATH = Path(__file__).parent
#TODO: cambiar a una dirección raiz del disco (Assets).
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\josef\Desktop\Nueva carpeta\build\assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("350x400")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 400,
    width = 350,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_text(
    91.0,
    26.0,
    anchor="nw",
    text="Exportación CSV",
    fill="#000000",
    font=("Inter Bold", 20 * -1)
)

canvas.create_text(
    34.0,
    61.0,
    anchor="nw",
    text="Selecciona el rango de fechas que desea\ngenerar o presione el segundo botón para \nexportar todos los registros",
    fill="#000000",
    font=("Inter", 14 * -1)
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    175.0,
    186.0,
    image=image_image_1
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    175.0,
    262.0,
    image=image_image_2
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=34.0,
    y=316.0,
    width=100.0,
    height=40.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=216.0,
    y=316.0,
    width=100.0,
    height=40.0
)
window.resizable(False, False)
window.mainloop()
