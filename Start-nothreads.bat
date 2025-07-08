@echo off
echo Iniciando proceso de actualizacion y ejecucion...

cd /d C:\remediacion-modbus
echo Realizando pull del repositorio...
echo.

git pull

REM Verificar si el pull fue exitoso
if %errorlevel% neq 0 (
    echo Error: No se pudo realizar el pull del repositorio
    echo Verifique su conexion a internet o la configuracion del repositorio
    timeout /t 3 /nobreak
) else (
    echo.
    echo Pull completado exitosamente
    echo.
)

REM Ejecutar archivos Python especificos
echo Ejecutando archivos Python...
echo.
pip install -r "requirements.txt"


REM Intentando ejecutar la consola modbus-async
if exist "modbus-async.py" (
    echo Ejecutando modbus-async.py...
    cls
    start py modbus-async.py
) else (
    echo Advertencia: modbus-async.py no encontrado
)


REM Intentando ejecutar la ventana principal
if exist "modbus-gui.py" (
    echo Ejecutando modbus-gui.py...
    cls
    start py modbus-gui.py
) else (
    echo Advertencia: modbus-gui.py no encontrado
)
