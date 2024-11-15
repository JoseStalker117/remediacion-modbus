from pathlib import Path
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
import csv
from datetime import datetime
import os

timestamp = datetime.now()
DB_NAME = "C:/SQLite/remediacion_2024.db"
csv_filename = timestamp.strftime("%m-%d-%Y")
csv_filename = csv_filename + ".csv"
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
full_csv_path = os.path.join(desktop_path, csv_filename)


# <<<--- Adaptadores de Timestamp SQLite --->>>

def adapt_datetime(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(ts):
    return datetime.strptime(ts.decode(), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)


# Función que exporta la consulta que retorna la DB, requiere el objeto resultante de la DB y el DIR donde se almacenará el archivo
def export_to_csv(query_result):
    with open(full_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        # Esta linea escribe los encabezados de la tabla a través del "query_result.description"
        csv_writer.writerow([i[0] for i in query_result.description])
        # Iteracción que escribe todos los registros encontrados en la búsqueda.
        csv_writer.writerows(query_result.fetchall())
    messagebox.showinfo("OK", "Archivo generado " +csv_filename+ " en: " +desktop_path)
    


# Función para realizar la consulta entera de la tabla
def query_full():
    try:
        conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        query = '''SELECT * FROM sensor_logs'''
        cursor.execute(query)        

        # Ejecutar la función de exportar archivo
        export_to_csv(cursor)
    
    #Manejo de excepción en caso de un error.
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()


# Función para realizar la consulta entre dos fechas
def query_between_dates():
    if inicio_entry.get_date() <= fin_entry.get_date():
        try:
            start_date = inicio_entry.get_date()
            end_date = fin_entry.get_date()
            
            conn = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()

            # Adaptador de marca de tiempo SQLite
            # start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            # end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

            # Query SQLite entre las fechas seleccionadas
            query = '''SELECT * FROM sensor_logs WHERE timestamp BETWEEN ? AND ? '''
            cursor.execute(query, (start_date, end_date))        

            # Ejecutar la función de exportar archivo
            export_to_csv(cursor)
    
        #Manejo de excepción en caso de un error.
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
        finally:
            if conn:
                conn.close()
                
    else:
        messagebox.showinfo("ERROR", "Formato de fecha no válido, fecha inicial debe ser mayor a la fecha final.")
                    
        


#------------------------------------Tkinter Window------------------------------------#
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(os.getcwd() + r"\assets")


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

#Widget 1
canvas.create_text(
    60.0,
    140.0,
    anchor="nw",
    text="Texto 1",
    fill="#000000",
    font=("Inter", 14 * -1)
)

image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    175.0,
    180.0,
    image=image_image_1
)

inicio_entry = DateEntry(
    window,
    width=24,
    font=("Inter", 12),
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="yyyy-mm-dd"
)
canvas.create_window(192, 180, window=inicio_entry)

#Widget 2
canvas.create_text(
    60.0,
    220.0,
    anchor="nw",
    text="Texto 2",
    fill="#000000",
    font=("Inter", 14 * -1)
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    175.0,
    260.0,
    image=image_image_2
)

fin_entry = DateEntry(
    window,
    width=24,
    font=("Inter", 12),
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="yyyy-mm-dd"
)
canvas.create_window(192, 260, window=fin_entry)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command= query_full,
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
    command= query_between_dates,
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
