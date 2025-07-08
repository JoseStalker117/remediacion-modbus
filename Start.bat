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


REM Intentando ejecutar la ventana principal
if exist "modbus-gui.pyw" (
    echo Ejecutando modbus-gui.pyw...
    cls
    start py modbus-gui.pyw
) else (
    echo Advertencia: modbus-gui.pyw no encontrado
)
