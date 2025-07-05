@echo off
echo Iniciando proceso de actualizacion y ejecucion...

REM Cambiar al directorio del proyecto
cd /d C:\modbus

REM Verificar si existe el directorio
if not exist "C:\modbus" (
    echo Error: El directorio C:\modbus no existe
    pause
    exit /b 1
)

REM Verificar si es un repositorio git
if not exist ".git" (
    echo Error: No se encontro un repositorio git en C:\modbus
    pause
    exit /b 1
)

echo Realizando pull del repositorio...
echo.

REM Intentar hacer pull con timeout de 30 segundos
timeout /t 30 /nobreak >nul 2>&1
git pull --timeout=30

REM Verificar si el pull fue exitoso
if %errorlevel% neq 0 (
    echo Error: No se pudo realizar el pull del repositorio
    echo Verifique su conexion a internet o la configuracion del repositorio
    pause
    exit /b 1
)

echo.
echo Pull completado exitosamente
echo.

REM Ejecutar archivos Python especificos
echo Ejecutando archivos Python...
echo.

REM Verificar si existe modbus-async.py
if exist "modbus-async.py" (
    echo Ejecutando modbus-async.py...
    py modbus-async.py
    echo.
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

:continue
echo.
echo Proceso completado
pause
