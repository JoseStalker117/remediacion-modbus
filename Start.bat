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
)
else (
    echo.
    echo Pull completado exitosamente
    echo.
)


REM Ejecutar archivos Python especificos
echo Ejecutando archivos Python...
echo.
pip install -r "requirements.txt"

REM Verificar si existe modbus-async.py
if exist "modbus-async.py" (
    echo Ejecutando modbus-async.py...
    cls
    py modbus-async.py
) else (
    echo Advertencia: modbus-async.py no encontrado
)

REM Verificar si existe modbus-window.py
if exist "modbus-window.py" (
    echo Ejecutando modbus-window.py...
    py modbus-window.py
    echo.
) else (
    echo Advertencia: modbus-window.py no encontrado
)
