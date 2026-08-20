# Proyecto Alcantarillas

Expediente de diseño de alcantarillas (Vía de Evitamiento La Unión, Bajo
Piura): pipeline de cálculo M0–M11 con CLI, interfaz gráfica y memoria de
cálculo exportable. Las reglas del proyecto están en `Claude.md`; la fuente
normativa única es la hoja de ruta en `docs/`.

## Cómo abrir la aplicación

### Vía 1 — Doble clic (Windows)

Haz doble clic en **`Abrir_GUI.bat`** (en la raíz del repositorio). El
lanzador resuelve la carpeta del proyecto por sí mismo, comprueba que Python
y las dependencias estén instalados —si algo falta, muestra el error en
pantalla en vez de cerrarse— y abre la interfaz sin dejar una consola negra
detrás.

Es solo un lanzador: la aplicación que abre es exactamente la misma que la
del comando manual.

### Vía 2 — Comando manual (respaldo, cualquier sistema)

Desde la raíz del repositorio:

```
python gui/app.py
```

## Requisitos

- Python 3.11 o superior (en Windows, instalado desde
  [python.org](https://www.python.org/downloads/) con la casilla
  *"Add python.exe to PATH"* marcada; `tkinter` viene incluido con ese
  instalador y no se instala con pip).
- Dependencias del proyecto:

  ```
  python -m pip install -r requirements.txt
  ```

- `ttkbootstrap` es **opcional**: la GUI lo usa para el tema visual y, si
  falta, cae automáticamente a Tkinter plano — misma aplicación, otra
  apariencia. Viene en `requirements.txt`, así que el comando de arriba lo
  deja instalado. Para comprobarlo: `python -c "import ttkbootstrap"` (sin
  error = instalado).
