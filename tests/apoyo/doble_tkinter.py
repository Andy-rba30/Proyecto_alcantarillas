"""
tests/apoyo/doble_tkinter.py
============================
El doble de `tkinter` con el que se importa la GUI sin escritorio, en UN solo
sitio para que lo usen `test_gui_contrato.py` y `test_ext5_forma_gui.py`.

Es el MISMO doble que `test_gui_contrato._con_doble_de_tkinter` instalaba, y
no una copia con otra forma: lo que se prueba con el es la logica PURA de la
GUI --- interpretar un texto tecleado, validar al escribir ---, que no toca la
pantalla. El codigo que CONSTRUYE widgets no se prueba con esto (seria un
espejismo): eso lo hacen los modulos de `tests/apoyo/gui_*_real.py` en un
proceso aparte con una ventana de verdad.

Una vez instalado no se retira: `gui.app` y `gui.ventana_normativa` quedan
importados contra el doble para el resto del proceso de la suite.
"""

import sys
import types


class _Cualquiera:
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, nombre):
        return _Cualquiera()

    def __call__(self, *a, **k):
        return _Cualquiera()


def _doble(nombre):
    modulo = types.ModuleType(nombre)
    modulo.__getattr__ = lambda n: _Cualquiera
    return modulo


def instalar():
    """Pone el doble en `sys.modules` si no esta; no toca un tkinter real."""
    for nombre in ("tkinter", "tkinter.filedialog", "tkinter.messagebox",
                   "tkinter.ttk", "ttkbootstrap", "ttkbootstrap.constants"):
        sys.modules.setdefault(nombre, _doble(nombre))
    sys.modules["tkinter"].filedialog = sys.modules["tkinter.filedialog"]
    sys.modules["tkinter"].messagebox = sys.modules["tkinter.messagebox"]
    sys.modules["tkinter"].ttk = sys.modules["tkinter.ttk"]


def gui_app():
    """Importa `gui.app` con el doble instalado y devuelve el modulo."""
    instalar()
    import gui.app as app
    return app


def gui_ventana_normativa():
    """Importa `gui.ventana_normativa` con el doble instalado."""
    instalar()
    import gui.ventana_normativa as gvn
    return gvn


def gui_componentes():
    """Importa `gui.componentes` con el doble instalado."""
    instalar()
    import gui.componentes as comp
    return comp


class VariableDeTexto:
    """Un `StringVar` de mentira: solo `get`/`set`, que es lo que la logica usa."""

    def __init__(self, texto=""):
        self._texto = texto

    def get(self):
        return self._texto

    def set(self, texto):
        self._texto = texto
