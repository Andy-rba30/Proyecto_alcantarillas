# -*- mode: python ; coding: utf-8 -*-
"""
Receta de PyInstaller (Windows --onedir, plan C3) para distribuir
Proyecto_alcantarillas sin requerir Python instalado.

Genera `dist/proyecto_alcantarillas/` con:
- `alcantarillas_cli.exe` (consola: --prevuelo, corrida, JSON, HTML, PDF)
- `alcantarillas_gui.exe` (ventana Tkinter / ttkbootstrap)

Uso desde la raiz del repositorio:
    py -3.13 -m PyInstaller --noconfirm empaquetado/proyecto_alcantarillas.spec
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

RAIZ = Path(SPECPATH).resolve().parent

datas = [
    (str(RAIZ / "docs" / "hoja_de_ruta_alcantarillas_v8.md"), "docs"),
    (str(RAIZ / "docs" / "ruta_familia_c.md"), "docs"),
    (str(RAIZ / "docs" / "manifiesto_citas.md"), "docs"),
    (str(RAIZ / "docs" / "contrato_entradas.md"), "docs"),
    (str(RAIZ / "docs" / "guia_perfil.md"), "docs"),
    (str(RAIZ / "docs" / "manual_usuario.md"), "docs"),
    (str(RAIZ / "docs" / "guia_del_desarrollador.md"), "docs"),
    (str(RAIZ / "plantillas"), "plantillas"),
]

# En tiempo de ejecucion `M11_reporte` lee `src/plantillas/*.html`, `servicio`
# calcula el SHA-1 sobre los archivos de criterios en `src/`, y el pre-vuelo
# (`src/variables_entrada.py`) inspecciona el AST de `src/modulos/`. Se copian
# los `.py` y `.html` bajo `src/` conservando la jerarquia exacta respecto a la
# raiz del paquete (`contents_directory="."`).
for archivo in sorted((RAIZ / "src").rglob("*")):
    if archivo.is_file() and "__pycache__" not in archivo.parts:
        if archivo.suffix in (".py", ".html"):
            destino = str(archivo.relative_to(RAIZ).parent).replace("\\", "/")
            datas.append((str(archivo), destino))

datas += collect_data_files("ttkbootstrap")
datas += collect_data_files("weasyprint")

hiddenimports = (
    collect_submodules("src")
    + collect_submodules("gui")
    + collect_submodules("ttkbootstrap")
)

a_cli = Analysis(
    [str(RAIZ / "cli.py")],
    pathex=[str(RAIZ)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest", "_pytest", "openpyxl", "fitz", "pymupdf",
        "PyQt6", "PyQt5", "PySide6", "matplotlib",
    ],
    noarchive=False,
)

a_gui = Analysis(
    [str(RAIZ / "gui" / "app.py")],
    pathex=[str(RAIZ)],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest", "_pytest", "openpyxl", "fitz", "pymupdf",
        "PyQt6", "PyQt5", "PySide6", "matplotlib",
    ],
    noarchive=False,
)

MERGE((a_cli, "alcantarillas_cli", "alcantarillas_cli"),
      (a_gui, "alcantarillas_gui", "alcantarillas_gui"))

pyz_cli = PYZ(a_cli.pure)
exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    [],
    exclude_binaries=True,
    name="alcantarillas_cli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    contents_directory=".",
)

pyz_gui = PYZ(a_gui.pure)
exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    [],
    exclude_binaries=True,
    name="alcantarillas_gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    contents_directory=".",
)

coll = COLLECT(
    exe_cli,
    a_cli.binaries,
    a_cli.datas,
    exe_gui,
    a_gui.binaries,
    a_gui.datas,
    strip=False,
    upx=False,
    name="proyecto_alcantarillas",
)
