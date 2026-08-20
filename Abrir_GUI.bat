@echo off
setlocal
title Alcantarillas - Lanzador de la interfaz grafica

rem ===========================================================================
rem Abrir_GUI.bat - Abre la interfaz grafica (gui\app.py) con doble clic.
rem
rem Es SOLO un lanzador: no toca la logica de la aplicacion ni del pipeline.
rem La app que abre es exactamente la misma que "python gui/app.py".
rem
rem   1. Resuelve la raiz del repo desde su propia ubicacion (%~dp0), asi
rem      funciona sin importar desde que carpeta se ejecute.
rem   2. Comprueba Python y las dependencias minimas ANTES de lanzar, para
rem      que un fallo se lea en pantalla en vez de parpadear y desaparecer.
rem   3. Lanza con pythonw.exe (sin ventana de consola) y cierra esta.
rem
rem ttkbootstrap NO se exige aqui a proposito: gui/app.py lo importa dentro
rem de un try/except y cae a Tkinter plano si falta (misma app, otro tema).
rem ===========================================================================

rem La raiz del repo es la carpeta donde vive este .bat.
cd /d "%~dp0"

rem --- 1. Python en el PATH? -------------------------------------------------
where python >nul 2>nul
if errorlevel 1 goto sin_python

rem --- 2. Dependencias minimas, con error legible ----------------------------
rem tkinter viene con el instalador oficial de python.org; numpy y scipy son
rem de requirements.txt. El detalle del error se captura y se muestra entero.
set "ERRTMP=%TEMP%\alcantarillas_gui_error.txt"
python -c "import tkinter, numpy, scipy" 2>"%ERRTMP%"
if errorlevel 1 goto sin_dependencias
del "%ERRTMP%" >nul 2>nul

rem --- 3. Lanzar la GUI sin dejar consola ------------------------------------
rem pythonw.exe no abre ventana de consola; start "" desacopla el proceso
rem para que esta ventana se cierre sola en cuanto la app arranca.
where pythonw >nul 2>nul
if errorlevel 1 goto lanzar_con_python
start "" pythonw "%~dp0gui\app.py"
exit /b 0

:lanzar_con_python
rem Sin pythonw en el PATH (poco comun): se lanza con python normal,
rem minimizado. Queda una consola minimizada mientras la app este abierta,
rem pero la aplicacion funciona igual.
start "Alcantarillas (consola auxiliar)" /min python "%~dp0gui\app.py"
exit /b 0

:sin_python
echo.
echo  ==========================================================================
echo   No se encontro Python en el PATH de Windows.
echo.
echo   Instala Python 3.11 o superior desde:
echo       https://www.python.org/downloads/
echo   y durante la instalacion marca la casilla "Add python.exe to PATH".
echo   Despues vuelve a hacer doble clic en este archivo.
echo  ==========================================================================
echo.
pause
exit /b 1

:sin_dependencias
echo.
echo  ==========================================================================
echo   Falta una dependencia de la aplicacion. Detalle del error:
echo  ==========================================================================
echo.
type "%ERRTMP%"
del "%ERRTMP%" >nul 2>nul
echo.
echo   Para instalarlas, abre una consola en esta carpeta y corre:
echo       python -m pip install -r requirements.txt
echo.
echo   (Si el error de arriba menciona "tkinter", reinstala Python desde
echo   python.org con la opcion "tcl/tk and IDLE" marcada: tkinter no se
echo   instala con pip.)
echo.
pause
exit /b 1
