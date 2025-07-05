import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from tkcalendar import Calendar
import pandas as pd

class CalendarPlotsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Semana y Análisis de Datos")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
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
        
        # Generar datos iniciales
        self.generate_sample_data()
        
        # Actualizar plots iniciales
        self.update_plots()
    
    def setup_main_layout(self):
        """Configurar el layout principal con dos frames"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo para el calendario
        self.left_frame = ttk.LabelFrame(main_frame, text="Selector de Semana", padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Frame derecho para los plots
        self.right_frame = ttk.LabelFrame(main_frame, text="Análisis de Datos", padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def setup_calendar(self):
        """Configurar el calendario y controles"""
        # Título del calendario
        title_label = ttk.Label(self.left_frame, text="Seleccionar Fecha", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Calendario
        self.calendar = Calendar(self.left_frame, 
                                selectmode='day',
                                date_pattern='dd/mm/yyyy',
                                background='darkblue',
                                foreground='white',
                                bordercolor='darkblue',
                                headersbackground='lightblue',
                                normalbackground='white',
                                weekendbackground='lightgray',
                                selectbackground='red',
                                selectforeground='white')
        self.calendar.pack(pady=10)
        
        # Botón para seleccionar semana
        select_button = ttk.Button(self.left_frame, text="Seleccionar Semana", 
                                  command=self.select_week)
        select_button.pack(pady=10)
        
        # Label para mostrar la semana seleccionada
        self.week_label = ttk.Label(self.left_frame, text="Semana: No seleccionada", 
                                   font=('Arial', 10))
        self.week_label.pack(pady=5)
        
        # Separador
        separator = ttk.Separator(self.left_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Información adicional
        info_label = ttk.Label(self.left_frame, 
                              text="Selecciona una fecha y presiona\n'Seleccionar Semana' para\nactualizar los gráficos",
                              justify=tk.CENTER,
                              font=('Arial', 9))
        info_label.pack(pady=5)
    
    def setup_plots(self):
        """Configurar los 5 plots en el frame derecho"""
        # Crear figura con subplots
        self.fig = Figure(figsize=(12, 10), facecolor='white')
        self.fig.suptitle('Análisis Semanal de Datos', fontsize=16, fontweight='bold')
        
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
    
    def select_week(self):
        """Seleccionar la semana basada en la fecha del calendario"""
        selected_date = self.calendar.selection_get()
        
        # Calcular el inicio y fin de la semana (lunes a domingo)
        days_since_monday = selected_date.weekday()
        self.selected_week_start = selected_date - timedelta(days=days_since_monday)
        self.selected_week_end = self.selected_week_start + timedelta(days=6)
        
        # Actualizar label
        week_text = f"Semana: {self.selected_week_start.strftime('%d/%m/%Y')} - {self.selected_week_end.strftime('%d/%m/%Y')}"
        self.week_label.config(text=week_text)
        
        # Actualizar plots
        self.update_plots()
    
    def generate_sample_data(self):
        """Generar datos de ejemplo para los plots"""
        # Generar datos para diferentes métricas
        np.random.seed(42)  # Para reproducibilidad
        
        # Datos base para una semana
        self.days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        # Diferentes conjuntos de datos
        self.base_data = {
            'ventas': np.random.randint(100, 500, 7),
            'usuarios': np.random.randint(50, 200, 7),
            'ingresos': np.random.uniform(1000, 5000, 7),
            'conversiones': np.random.uniform(0.1, 0.8, 7),
            'satisfaccion': np.random.uniform(3.5, 5.0, 7)
        }
    
    def get_week_data(self):
        """Obtener datos específicos para la semana seleccionada"""
        if not self.selected_week_start:
            return self.base_data
        
        # Simular variación de datos basada en la semana seleccionada
        week_number = self.selected_week_start.isocalendar()[1]
        np.random.seed(week_number)  # Seed basado en el número de semana
        
        # Generar datos variables según la semana
        factor = 1 + (week_number % 10) * 0.1  # Factor de variación
        
        return {
            'ventas': np.random.randint(int(100*factor), int(500*factor), 7),
            'usuarios': np.random.randint(int(50*factor), int(200*factor), 7),
            'ingresos': np.random.uniform(1000*factor, 5000*factor, 7),
            'conversiones': np.random.uniform(0.1, 0.8, 7),
            'satisfaccion': np.random.uniform(3.5, 5.0, 7)
        }
    
    def update_plots(self):
        """Actualizar todos los plots con los datos de la semana seleccionada"""
        data = self.get_week_data()
        
        # Limpiar plots anteriores
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5]:
            ax.clear()
        
        # Plot 1: Ventas diarias (Gráfico de barras)
        self.ax1.bar(self.days, data['ventas'], color='skyblue', alpha=0.7)
        self.ax1.set_title('Ventas Diarias', fontweight='bold')
        self.ax1.set_ylabel('Cantidad')
        self.ax1.grid(True, alpha=0.3)
        
        # Plot 2: Usuarios activos (Gráfico de líneas)
        self.ax2.plot(self.days, data['usuarios'], marker='o', linewidth=2, 
                     color='green', markersize=6)
        self.ax2.set_title('Usuarios Activos', fontweight='bold')
        self.ax2.set_ylabel('Usuarios')
        self.ax2.grid(True, alpha=0.3)
        
        # Plot 3: Ingresos (Gráfico de área)
        self.ax3.fill_between(self.days, data['ingresos'], alpha=0.6, color='orange')
        self.ax3.plot(self.days, data['ingresos'], color='darkorange', linewidth=2)
        self.ax3.set_title('Ingresos Diarios', fontweight='bold')
        self.ax3.set_ylabel('Ingresos ($)')
        self.ax3.grid(True, alpha=0.3)
        
        # Plot 4: Tasa de conversión (Gráfico de barras horizontales)
        colors = ['red' if x < 0.4 else 'yellow' if x < 0.6 else 'green' 
                 for x in data['conversiones']]
        self.ax4.barh(self.days, data['conversiones'], color=colors, alpha=0.7)
        self.ax4.set_title('Tasa de Conversión', fontweight='bold')
        self.ax4.set_xlabel('Tasa (%)')
        self.ax4.grid(True, alpha=0.3)
        
        # Plot 5: Satisfacción del cliente (Gráfico combinado)
        ax5_twin = self.ax5.twinx()
        
        # Barras para satisfacción
        bars = self.ax5.bar(self.days, data['satisfaccion'], alpha=0.6, 
                           color='purple', label='Satisfacción')
        
        # Línea para tendencia
        ax5_twin.plot(self.days, np.cumsum(data['satisfaccion']), 
                     color='red', marker='s', linewidth=2, 
                     label='Satisfacción Acumulada')
        
        self.ax5.set_title('Satisfacción del Cliente', fontweight='bold')
        self.ax5.set_ylabel('Puntuación (1-5)', color='purple')
        ax5_twin.set_ylabel('Acumulado', color='red')
        self.ax5.grid(True, alpha=0.3)
        
        # Leyenda combinada
        lines1, labels1 = self.ax5.get_legend_handles_labels()
        lines2, labels2 = ax5_twin.get_legend_handles_labels()
        self.ax5.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Actualizar título principal con la semana seleccionada
        if self.selected_week_start:
            week_str = f"{self.selected_week_start.strftime('%d/%m')} - {self.selected_week_end.strftime('%d/%m/%Y')}"
            self.fig.suptitle(f'Análisis Semanal de Datos - Semana: {week_str}', 
                             fontsize=16, fontweight='bold')
        
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
