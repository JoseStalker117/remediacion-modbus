import os, sys, sqlite3, subprocess, threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta, date
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from tkcalendar import Calendar
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
from dotenv import load_dotenv


load_dotenv("config.env")

def CargarDB():
    
    DB_PATH = str(os.getenv("DB_PATH"))
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM sensor_logs"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
    
class CalendarPlotsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BIOINSIGHT - Modbus GUI")
        # self.root.geometry("1400x800")
        self.root.configure(bg='#eaf6fb')  # Fondo azul muy claro
        self.root.state("zoomed")
        
        # Variables para almacenar datos
        self.selected_week_start = None
        self.selected_week_end = None
        
        # Configurar el layout principal
        self.setup_main_layout()
        
        # Configurar el calendario
        self.setup_calendar()
        
        # Configurar los plots
        self.setup_plots()
        
        # Seleccionar la semana actual automáticamente (domingo a sábado)
        today = date.today()
        days_since_sunday = today.weekday() + 1 if today.weekday() < 6 else 0
        self.selected_week_start = today - timedelta(days=days_since_sunday)
        self.selected_week_end = self.selected_week_start + timedelta(days=6)
        # Actualizar el calendario y el label
        self.calendar.selection_set(today)
        week_text = f"Semana: {self.selected_week_start.strftime('%d/%m/%Y')} - {self.selected_week_end.strftime('%d/%m/%Y')}"
        self.week_label.config(text=week_text)
        
        # Actualizar plots iniciales
        self.update_plots()

        # Ejecutar el comando automáticamente solo cuando el mainloop ya está activo
        self.root.after(0, self.ejecutar_comando_threaded)

    def ejecutar_comando(self):
        process = subprocess.Popen(
            ["py", "modbus-async.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Borra el contenido anterior en el hilo principal
        self.root.after(0, lambda: self.salida_text.delete("1.0", tk.END))
        for line in process.stdout:
            self.root.after(0, lambda l=line: self.salida_text.insert(tk.END, l))
            self.root.after(0, lambda: self.salida_text.see(tk.END))  # Scroll automático
        process.stdout.close()
        process.wait()

    def ejecutar_comando_threaded(self):
        threading.Thread(target=self.ejecutar_comando, daemon=True).start()
    
    def setup_main_layout(self):
        """Configurar el layout principal con dos frames"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo para el calendario
        self.left_frame = ttk.LabelFrame(main_frame, text="Selector de Semana", padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.left_frame.configure(style="Left.TLabelframe")
        
        # Frame derecho para los plots
        self.right_frame = ttk.LabelFrame(main_frame, text="Análisis de Datos", padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame.configure(style="Right.TLabelframe")
    
    def setup_calendar(self):
        """Configurar el calendario y controles"""
        # Título del calendario
        title_label = ttk.Label(self.left_frame, text="Seleccionar Fecha", 
                               font=('Arial', 14, 'bold'), background='#eaf6fb', foreground='#2d415a')
        title_label.pack(pady=(0, 10))
        
        # Calendario
        self.calendar = Calendar(
            self.left_frame,
            selectmode='day',
            date_pattern='dd/mm/yyyy',
            background='#d6eaf8',  # azul muy claro
            foreground='#2d415a',
            bordercolor='#b7d6ec',
            headersbackground='#b7d6ec',
            normalbackground='#fafdff',
            weekendbackground='#eaf6fb',
            selectbackground='#7ec6e6',
            selectforeground='#1a2a3a',
            font=('Arial', 14),
            headersforeground='#2d415a',
            othermonthbackground='#f0f4f8',
            othermonthwebackground='#eaf6fb',
            othermonthforeground='#b0b0b0',
            weekendforeground='#2d415a',
            disabledbackground='#f0f4f8',
            disabledforeground='#b0b0b0',
            borderwidth=2,
            showweeknumbers=False,
            mindate=None,
            maxdate=None,
            firstweekday='sunday',
            rowheight=40,  # hace el calendario más grande
            colwidth=40
        )
        self.calendar.pack(pady=10, ipadx=10, ipady=10)
        
        # Botón para seleccionar semana
        select_button = ttk.Button(self.left_frame, text="Seleccionar Semana", 
                                  command=self.select_week)
        select_button.pack(pady=10)
        
        # Label para mostrar la semana seleccionada
        self.week_label = ttk.Label(self.left_frame, text="Semana: No seleccionada", 
                                   font=('Arial', 12), background='#eaf6fb', foreground='#2d415a')
        self.week_label.pack(pady=5)
        
        # Separador
        separator = ttk.Separator(self.left_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Información adicional
        info_label = ttk.Label(
            self.left_frame,
            text="Selecciona una fecha y presiona\n'Seleccionar Semana' para\nactualizar los gráficos",
            justify=tk.CENTER,
            font=('Arial', 11),
            background='#eaf6fb',
            foreground='#2d415a'
        )
        info_label.pack(pady=5)
        
         # Separador
        separator = ttk.Separator(self.left_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(self.left_frame, text="Consola", 
                               font=('Arial', 13, 'bold'), background='#eaf6fb', foreground='#2d415a')
        title_label.pack(pady=(0, 10))
        
        # Consola de salida
        self.salida_text = tk.Text(self.left_frame, height=20, width=42, background="black", foreground="white", font=("Consolas", 12))
        self.salida_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    def setup_plots(self):
        """Configurar los 5 plots en el frame derecho"""
        # Crear figura con subplots
        self.fig = Figure(figsize=(12, 10), facecolor='#fafdff')
        self.fig.suptitle('Análisis Semanal de Datos', fontsize=16, fontweight='bold', color='#2d415a')
        
        # Crear los 5 subplots en una disposición 3x2
        self.ax1 = self.fig.add_subplot(3, 2, 1)
        self.ax2 = self.fig.add_subplot(3, 2, 2)
        self.ax3 = self.fig.add_subplot(3, 2, 3)
        self.ax4 = self.fig.add_subplot(3, 2, 4)
        self.ax5 = self.fig.add_subplot(3, 1, 3)  # Plot más ancho en la parte inferior
        
        # Ajustar espaciado
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Crear canvas para matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de herramientas de matplotlib
        toolbar_frame = ttk.Frame(self.right_frame)
        toolbar_frame.pack(fill=tk.X)
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

        # Estilos para los frames
        style = ttk.Style()
        style.configure("Left.TLabelframe", background="#eaf6fb", foreground="#2d415a", font=("Arial", 13, "bold"))
        style.configure("Right.TLabelframe", background="#fafdff", foreground="#2d415a", font=("Arial", 13, "bold"))
        style.configure("TLabelframe.Label", font=("Arial", 13, "bold"))
        style.configure("TLabel", background="#eaf6fb", foreground="#2d415a")
    
    def select_week(self):
        """Seleccionar la semana basada en la fecha del calendario"""
        selected_date = self.calendar.selection_get()
        # Calcular el inicio y fin de la semana (domingo a sábado)
        days_since_sunday = selected_date.weekday() + 1 if selected_date.weekday() < 6 else 0
        self.selected_week_start = selected_date - timedelta(days=days_since_sunday)
        self.selected_week_end = self.selected_week_start + timedelta(days=6)
        # Actualizar label
        week_text = f"Semana: {self.selected_week_start.strftime('%d/%m/%Y')} - {self.selected_week_end.strftime('%d/%m/%Y')}"
        self.week_label.config(text=week_text)
        # Actualizar plots
        self.update_plots()
    

    def get_week_data(self):
        """Obtener datos de la semana seleccionada desde la base de datos"""
        import pandas as pd
        df = CargarDB()
        if not self.selected_week_start:
            # Si no hay semana seleccionada, usar todo el rango
            return df
        # Filtrar por la semana seleccionada
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        end = pd.Timestamp(self.selected_week_end) + pd.Timedelta(days=1)
        mask = (df['timestamp'] >= pd.Timestamp(self.selected_week_start)) & (df['timestamp'] < end)
        return df.loc[mask]

    def update_plots(self):
        """Actualizar todos los plots con los datos de la semana seleccionada"""
        df = self.get_week_data()
        # Limpiar plots anteriores
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5]:
            ax.clear()
            
        # Eje x: fechas
        x = df['timestamp']
        
        # Plot 1: CO2_IN y CO2_OUT
        self.ax1.stackplot(x, df['CO2_IN'], df['CO2_OUT'], labels=['CO2_IN', 'CO2_OUT'], colors=['#8884d8', '#82ca9d'])
        self.ax1.set_title('CO2 IN/OUT', fontweight='bold')
        self.ax1.legend(loc='upper left')
        
        # Plot 2: NO2_IN y NO2_OUT
        self.ax2.stackplot(x, df['NO2_IN'], df['NO2_OUT'], labels=['NO2_IN', 'NO2_OUT'], colors=['#FF8042', '#FFBB28'])
        self.ax2.set_title('NO2 IN/OUT', fontweight='bold')
        self.ax2.legend(loc='upper left')
        
        # Plot 3: SO2_IN y SO2_OUT
        self.ax3.stackplot(x, df['SO2_IN'], df['SO2_OUT'], labels=['SO2_IN', 'SO2_OUT'], colors=['#d62728', '#7f7f7f'])
        self.ax3.set_title('SO2 IN/OUT', fontweight='bold')
        self.ax3.legend(loc='upper left')
        
        # Plot 4: TEMP_1 y TEMP_2
        self.ax4.stackplot(x, df['TEMP_1'], df['TEMP_2'], labels=['TEMP_1', 'TEMP_2'], colors=['#E377C2', '#17BECF'])
        self.ax4.set_title('TEMP 1/2', fontweight='bold')
        self.ax4.legend(loc='upper left')
        
        # Plot 5: PAR
        self.ax5.stackplot(x, df['PAR'], labels=['PAR'], colors=['#0088FE'])
        self.ax5.set_title('PAR', fontweight='bold')
        self.ax5.legend(loc='upper left')
        
        # Por ejemplo, para todos los ejes:
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
            ax.tick_params(axis='x', rotation=30)  # Rota las etiquetas para mejor lectura
        
        # Ajustar layout y redibujar
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        self.canvas.draw()

def main():
    """Función principal para ejecutar la aplicación"""
    root = tk.Tk()
    app = CalendarPlotsApp(root)
    
    # Configurar el cierre de la aplicación
    def on_closing():
        plt.close('all')
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
    
