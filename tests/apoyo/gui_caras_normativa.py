"""
tests/apoyo/gui_caras_normativa.py
==================================
Las TRES CARAS de `gui/ventana_normativa.py` que el smoke de I1 no abria
--- RANGO, CATALOGO y CAMPO --- construidas bajo un `Tk` de verdad, y el
camino de `_declarar` recorrido de punta a punta en cada una: lo que el
auditor adversarial de I1b midio como alcance abierto de SIS-F-01 y la ficha
de decisiones_diferidas.md dejo escrito («_pintar_rango, _pintar_catalogo,
_pintar_campo y el camino de _declarar siguen sin construirse bajo Tk»).

    python -m tests.apoyo.gui_caras_normativa <archivo de salida .json>

Corre en un proceso limpio por la misma razon que los otros apoyos:
`test_gui_contrato.py` instala dobles de `tkinter` que no se pueden retirar,
y con ellos la ventana seria un espejismo. Por cada cara se mide, en orden:

  1. que la emergente se construye Y QUE LA CARA ESTA PINTADA: un texto
     que solo pinta esa cara aparece entre los widgets (el numero de
     widgets solo no lo dice: la carcasa ya suma mas de diez), y el campo
     validable del pie existe: la variable es declarable desde aqui;
  2. que un valor MALO tecleado y declarado PULSANDO EL BOTON (`invoke`)
     NO declara nada: el rotulo de estado dice «No se declaro», el criterio
     no queda en caliente y no hay procedencia; y que en la cara RANGO la
     validacion al escribir ya lo avisa antes de pulsar;
  3. que un valor BUENO declara: el rotulo dice «Declarado para esta
     corrida», el criterio queda en caliente, la procedencia registrada lo
     nombra y el `al_declarar` recibe la clave.

Las tres claves se eligen por su cara MEDIDA con `src.ventana_normativa`
(el apoyo lo vuelve a medir y lo escribe, para que el test compare contra
el modelo y no contra una lista copiada): el techo del concreto es la unica
`en_rango`, el catalogo de M2 la unica `de_catalogo`, y el esviaje maximo
(C10) una `libre` de perfil declarable.
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# (clave, texto MALO, texto BUENO, texto que SOLO pinta esa cara), tecleados
# como los teclea el proyectista. El cuarto elemento es lo que mata al
# mutante «_pintar_<cara> = no-op» (auditor adversarial de C09): la carcasa
# --cabecera y pie-- ya suma mas de diez widgets, de modo que contar no
# distingue una cara pintada de una vacia.
CARAS = {
    "RANGO": ("v_max_concreto_eleccion", "9,0", "4,5", "Que acota:"),
    "CATALOGO": ("D_max_catalogo", "nan",
                 '{"concreto_reforzado": 2.70, "tmc": 2.10, "hdpe": 1.50}',
                 "ESTO NO ES UNA NORMA"),
    "CAMPO": ("esviaje_max_grados", "95", "60", "Lo fija:"),
}
TEXTO_DEL_BOTON = "Declarar para esta corrida"


def _descendientes(widget):
    for hijo in widget.winfo_children():
        yield hijo
        yield from _descendientes(hijo)


def _textos(widget):
    """Los textos de todos los widgets que tienen `text`."""
    out = []
    for w in _descendientes(widget):
        try:
            out.append(str(w.cget("text")))
        except Exception:
            pass
    return out


def _boton_declarar(widget):
    for w in _descendientes(widget):
        try:
            if str(w.cget("text")) == TEXTO_DEL_BOTON:
                return w
        except Exception:
            pass
    return None


def main(destino: Path) -> int:
    import ttkbootstrap as tb

    from gui import ventana_normativa
    from src import criterios_adoptados as ca
    from src import declaracion as dec
    from src import ventana_normativa as vn

    raiz = tb.Window(themename="litera")
    obs = {}
    try:
        for cara, (clave, malo, bueno, texto_de_la_cara) in CARAS.items():
            ca.limpiar_valores_dinamicos()
            dec.limpiar()
            recibidas = []
            v = ventana_normativa.VentanaNormativa(
                raiz, clave, al_declarar=recibidas.append)
            raiz.update()
            textos = _textos(v)
            boton = _boton_declarar(v)
            o = {
                "clave": clave,
                "cara_modelo": vn.ventana(clave).cara.name,
                "titulo": v.title(),
                "widgets": sum(1 for _ in _descendientes(v)),
                "campo_construido": v.campo is not None,
                "texto_de_la_cara": texto_de_la_cara,
                "la_cara_esta_pintada": any(texto_de_la_cara in t for t in textos),
                "boton_construido": boton is not None,
            }
            # 2. El valor malo, POR EL BOTON (`invoke` ejecuta su `command`,
            #    que es `_declarar`): si el boton no estuviera atado, nada
            #    cambiaria y el rotulo seguiria vacio.
            v.valor_var.set(malo)
            raiz.update()
            o["validacion_al_escribir_tras_malo"] = v.lbl_validacion.cget("text")
            boton.invoke()
            raiz.update()
            o["rotulo_tras_malo"] = v.lbl_estado.cget("text")
            o["en_caliente_tras_malo"] = ca.declarado_en_caliente(clave)
            o["procedencia_tras_malo"] = dec.procedencia_de(clave) is not None
            o["callback_tras_malo"] = list(recibidas)
            # 3. El valor bueno, tambien por el boton.
            v.valor_var.set(bueno)
            raiz.update()
            o["validacion_al_escribir_tras_bueno"] = v.lbl_validacion.cget("text")
            boton.invoke()
            raiz.update()
            o["rotulo_tras_bueno"] = v.lbl_estado.cget("text")
            o["en_caliente_tras_bueno"] = ca.declarado_en_caliente(clave)
            procedencia = dec.procedencia_de(clave)
            o["procedencia_tras_bueno"] = (procedencia.como_texto()
                                           if procedencia is not None else "")
            o["callback_tras_bueno"] = list(recibidas)
            o["valor_efectivo"] = repr(ca.criterio_efectivo(clave).valor)
            v.destroy()
            raiz.update()
            obs[cara] = o
    finally:
        ca.limpiar_valores_dinamicos()
        dec.limpiar()
        raiz.destroy()

    destino.write_text(json.dumps(obs, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(json.dumps(obs, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[9])
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
