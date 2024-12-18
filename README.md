> [!IMPORTANT]
> Dependencias:
> pymodbus, pyserial, tkcalendar
>
> Añadir script al arranque (Windows)
> "shell:startup"

Este proyecto se basa en una red de sensores comunicados por RS485 mediante el protocolo ModBus RTU, creando conjuntos de datos siendo CO2, NO2, SO2, Radiación Fotosintética y Temperatura, estos transmiten la información de forma directa al ordenador por un puerto COM asignado interpretandola en información.

Una vez que los datos han sido recolectados por los sensores, se almacenan de manera estructurada en una base de datos SQLite, ya que por el momento se utiliza el mismo ordenador para manipular la información.
Este almacenamiento permite la organización de la información de manera eficiente, facilitando consultas y análisis posteriores. Utilizando lenguajes de consulta, como SQL en el caso de bases de datos relacionales, es posible acceder y analizar los datos de manera rápida y precisa para identificar patrones, generar informes.

El diseño de este sistema permite la integración de sensores adicionales* a medida que se necesiten, así como la escalabilidad en la base de datos para gestionar grandes volúmenes de datos.

*Cada sensor está conectado a un COM individual, estos se pueden unificar en uno solo modificando la dirección de dispositivo de cada sensor y creando un arreglo. Se decide dejar por default para futuros usos sin realizar muchas modificaciones.

--------------------------------------------------------------------------------------------------------

<img src="https://cdsentec.com/wp-content/uploads/2022/06/CH4-sensor.jpg" alt="Sensor de gas marca Sentec" width="300" height="300"> 
Se emplean 6 sensores de gas de la marca Sentec que operan por Modbus RTU como el de la imagen.

<img src="https://github.com/user-attachments/assets/951e18f7-7898-40e4-9064-9d703e4dd94b" alt="Circuito del ordenador y sus puertos COM" width="500" height="350">
