"""
proceso/tests/test_t12_proceso.py
=================================
La mitad de PROCESO de la aceptacion de T-12 (INF-5.2.2): lo que hay DENTRO
de `proceso/` despues del movimiento. La mitad del entregable --que el
material ya no esta en su sitio anterior, que `tests/` no lo lee, que
`git archive` lo excluye-- esta en `tests/test_t12_entregable.py`.

Se corre desde la raiz del repositorio:  python -m pytest proceso/tests
"""

import re
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
PROCESO = RAIZ / "proceso"
BASE = "f77c5d4"


def test_el_material_de_proceso_esta_en_proceso():
    for ruta in (PROCESO / ".claude" / "agents" / "verificador-normativo.md",
                 PROCESO / "planes_mejora" / "09_CADENA_PROMPTS_TESIS.md",
                 PROCESO / "auditorias" / "matriz_cruzada_auditorias.xlsx",
                 PROCESO / "auditorias" / "auditoria_sistema.md",
                 PROCESO / "auditorias" / "temario_refutar_95.json",
                 PROCESO / "verificar_sesion.py",
                 PROCESO / "hoja_de_ruta_correcciones_v12.md",
                 PROCESO / "auditoria_y_ruta_despliegue_v9.md",
                 PROCESO / "apoyo" / "tracker.py",
                 PROCESO / "tests" / "conftest.py",
                 PROCESO / "README.md"):
        assert ruta.exists(), ruta


def _de_la_base(ruta: str) -> str:
    hecho = subprocess.run(["git", "show", f"{BASE}:{ruta}"], cwd=RAIZ,
                           capture_output=True, text=True)
    if hecho.returncode != 0:
        pytest.skip(f"la base {BASE} no esta en este clon: {hecho.stderr.strip()}")
    return hecho.stdout


def _con_cifra(token: str) -> bool:
    return any(c.isdigit() for c in token)


def _es_subsecuencia_con_cifras_libres(base: list, hoy: list) -> tuple:
    """
    (True, None) si las palabras de `base` aparecen EN ORDEN en `hoy`,
    admitiendo palabras insertadas en cualquier sitio y que una palabra CON
    CIFRA de la base empareje con cualquier palabra con cifra (un conteo que
    se actualiza); (False, contexto) con las palabras donde se corta, si no.
    El emparejamiento voraz (la primera coincidencia) es optimo para una
    subsecuencia con cualquier predicado de emparejamiento.
    """
    j = 0
    for i, palabra in enumerate(base):
        while j < len(hoy) and not (
                hoy[j] == palabra or (_con_cifra(palabra) and _con_cifra(hoy[j]))):
            j += 1
        if j == len(hoy):
            return False, " ".join(base[max(0, i - 8):i + 8])
        j += 1
    return True, None


def test_las_reglas_de_correccion_se_movieron_enteras_sin_reescribir():
    """
    Las reglas de correccion de auditorias NO se actualizan con cada sesion:
    desde la linea de su titulo, el archivo es, byte a byte, la seccion de
    `CLAUDE.md` en la base de T-12.
    """
    base = _de_la_base("CLAUDE.md")
    i_reglas = base.index("## Reglas de corrección de hallazgos de auditoría")
    reglas = (PROCESO / "reglas_de_correccion_de_auditorias.md").read_text(encoding="utf-8")
    assert reglas[reglas.index("## Reglas de corrección"):] == \
        base[i_reglas:].rstrip("\n") + "\n"


def test_la_bitacora_conserva_su_texto_historico_y_admite_actualizarse():
    """
    LA FORMA ELEGIDA (H4 de la auditoria de T-12). La bitacora SE ACTUALIZA
    (la tabla de pares, el «collected» de hoy, la cadena de totales, el
    parrafo de cada prompt que integra), de modo que compararla byte a byte
    con la seccion movida --lo que hacia la FASE A-- la ponia en rojo en la
    primera actualizacion legitima. Lo que NO puede pasar es que el texto
    historico se pierda o se reescriba. Por eso: todas las palabras de la
    seccion «Cierre de tarea» de `CLAUDE.md` en `f77c5d4` tienen que seguir
    en la bitacora, EN ORDEN; se admite insertar texto en cualquier sitio y
    que una palabra con cifra (un conteo, un par) cambie de valor. Borrar o
    cambiar una palabra sin cifra la pone en rojo.
    """
    base = _de_la_base("CLAUDE.md")
    i_cierre = base.index("## Cierre de tarea: la entrega es `origin/main`")
    i_reglas = base.index("## Reglas de corrección de hallazgos de auditoría")
    historica = base[i_cierre:i_reglas].split()
    bitacora = (PROCESO / "bitacora_conteos_y_entorno.md").read_text(encoding="utf-8")
    hoy = bitacora[bitacora.index("## Cierre de tarea"):].split()
    conserva, donde = _es_subsecuencia_con_cifras_libres(historica, hoy)
    assert conserva, f"la bitacora perdio o reescribio texto historico cerca de: {donde}"
    assert "| PyMuPDF | Ventana Tk | `passed` | `skipped` |" in bitacora


def test_la_comprobacion_de_la_bitacora_no_es_vacua():
    """La forma de arriba detecta un borrado y una reescritura sin cifra."""
    base = "Una tarea no está terminada hasta que su trabajo está en main , hoy 6469".split()
    assert _es_subsecuencia_con_cifras_libres(
        base, ("Una tarea NUEVA no está terminada hasta que su trabajo está en "
               "main , hoy 6539").split())[0]
    assert not _es_subsecuencia_con_cifras_libres(
        base, "Una tarea no está terminada hasta que su trabajo está , hoy 6469".split())[0]
    assert not _es_subsecuencia_con_cifras_libres(
        base, ("Una tarea sí está terminada hasta que su trabajo está en main , "
               "hoy 6469").split())[0]


def test_verificar_sesion_corre_tambien_la_suite_de_proceso():
    """H4: nadie corria `proceso/tests`; el cierre de sesion la corre."""
    texto = (PROCESO / "verificar_sesion.py").read_text(encoding="utf-8")
    assert '"proceso/tests"' in texto


def test_el_readme_de_proceso_no_escribe_un_correo():
    texto = (PROCESO / "README.md").read_text(encoding="utf-8")
    assert not re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", texto)
