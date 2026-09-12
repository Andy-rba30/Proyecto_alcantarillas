"""
tests/test_estilo_criterios.py — linter de estilo de los criterios (plan R1)
============================================================================
Vigila la REDACCION de los campos `justificacion` y `concepto` de los 69
criterios de src/criterios_adoptados.py, con las siete reglas E1–E7 de
docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md (§R1):

    E1  Verbos de bitacora ("decia", "venia", "version anterior") y
        referencias a sesiones (S14, C5) o hallazgos (SIS-, NOR-, MAT-)
        como narracion. La historia vive en git y en decisiones_diferidas.md.
    E2  Primera persona ("decidimos", "adoptamos", "creo"). Impersonal siempre.
    E3  Mayusculas enfaticas: 2+ palabras seguidas todas en mayuscula que no
        sean siglas. La lista blanca se DERIVA de fuentes.py y
        constantes_normativas.py y crece solo con justificacion en comentario.
    E4  Referencias al codigo como argumento normativo ("porque M9 lo
        espera", "para que brentq"). El codigo no es fuente.
    E5  Transcripcion entre comillas de una frase de la fuente en vez de
        citar por cita_id. Es la regla de la casa «ningun texto literal se
        transcribe dos veces», extendida a los criterios.
    E6  Magnitud dimensional sin unidad SI en el texto.
    E7  Fechas de calendario dentro de la justificacion.

Lo que NO se prohibe (deliberado, del plan R): numeros y resultados de ESTA
obra dentro de la defensa de sensibilidad. Este repositorio es el expediente
de una obra (via de evitamiento, La Union, Piura) y un [A] se defiende con su
sensibilidad en esta obra. Lo que las reglas atacan es el REGISTRO (bitacora,
enfasis de alegato) y la MEZCLA de lo que dice la fuente con lo que hace el
proyecto (NOR-HID-04), no la defensa por sensibilidad.

Forma de TRINQUETE, calcada de MAX_REFERENCIAS_DE_PROSA en
tests/test_manifiesto_citas.py: el linter nace sobre 69 textos existentes y
un linter que nace en rojo o se apaga o bloquea todo. Cada regla lleva su
censo medido (clave -> numero de violaciones hoy) y el test exige IGUALDAD
exacta: una violacion nueva falla (en clave limpia o en clave ya censada), y
una clave que el censo da por sucia y ya esta limpia tambien falla, para que
el censo baje con la limpieza y solo pueda decrecer. Subir un numero del
censo es admitir un texto nuevo con el defecto: no se hace.

Los detectores son PROXIES mecanicos y estan calibrados para ALTA PRECISION,
no para cobertura: un texto que pasa no esta certificado limpio (E6 en
particular solo ve decimales junto a un sustantivo dimensional), pero un
texto que falla, falla por algo real. Por eso los censos se fijaron
inspeccionando cada hallazgo a mano, no a granel.
"""

import ast
import re
from pathlib import Path

import criterios_adoptados as ca

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"

# Los dos campos de prosa que el plan R1 manda vigilar. `fuente`,
# `trazabilidad` y demas quedan fuera A PROPOSITO: la cita con numeral y
# pagina vive en `fuente` y alli los numeros y las mayusculas de rotulo son
# el contenido, no un vicio de registro.
CAMPOS = ("justificacion", "concepto")


def _textos():
    """(clave, campo, texto) de los dos campos de prosa de cada criterio."""
    return [(clave, campo, getattr(criterio, campo) or "")
            for clave, criterio in ca.CRITERIOS.items()
            for campo in CAMPOS]


# ---------------------------------------------------------------------------
# Comillas: lo citado no es prosa del autor
# ---------------------------------------------------------------------------
# E3 no debe contar como "enfasis" las mayusculas DENTRO de una cita («TW SE
# CALCULA, NO SE MIDE» trae las mayusculas de la fuente, no del redactor), y
# E5 necesita exactamente esos tramos. El lookbehind excluye el apostrofo
# interno de simbolos como f'c o B'c, que rompia el apareado de comillas.

_COMILLA_LATINA = re.compile(r"«([^»]{1,600})»")
_COMILLA_SIMPLE = re.compile(r"(?<![A-Za-z])'([^']{1,600}?)'")


def _tramos_citados(texto):
    """Los tramos entrecomillados de un texto, con sus posiciones."""
    tramos = []
    for regex in (_COMILLA_LATINA, _COMILLA_SIMPLE):
        for m in regex.finditer(texto):
            tramos.append((m.start(), m.end(), m.group(1)))
    return tramos


def _sin_citas(texto):
    """El texto con los tramos entrecomillados en blanco (mismo largo)."""
    resultado = list(texto)
    for ini, fin, _ in _tramos_citados(texto):
        for i in range(ini, fin):
            resultado[i] = " "
    return "".join(resultado)


# ---------------------------------------------------------------------------
# E3 — lista blanca de siglas, DERIVADA y no mantenida a mano
# ---------------------------------------------------------------------------

# Palabras castellanas que la derivacion arrastra desde los NOMBRES de las
# constantes (F_PGA_TABLA aporta PGA pero tambien TABLA) y que no son siglas:
# escribirlas en mayuscula seguida es enfasis, no cita. Cada exclusion es una
# palabra del diccionario, no una sigla; si una sigla nueva colisionara con
# una palabra, se saca de aqui con su justificacion.
_PALABRAS_COLADAS = frozenset({
    "ALTERNATIVOS", "ANOMALIA", "BADEN", "COHERENCIA", "CORROSION", "CORTE",
    "CUANTIA", "DECIRSE", "ESTRICTA", "EXTREMA", "FRICCION", "HIDRAULICO",
    "HOMONIMIAS", "INCLUSIVE", "INDETERMINADA", "INICIO", "LEJOS",
    "PARTICIPA", "REMEDIOS", "REMITIDA", "SALVEDAD", "SUPUESTA", "TRANSICION",
    "VIVIENDA",  # del designador "RM ...-VIVIENDA"; suelta es palabra, no sigla
})

# Siglas que el barrido inicial encontro en los textos y la derivacion no
# alcanza (no figuran en los campos de Fuente ni en nombres de constantes, o
# su minuscula aparece como identificador en el corpus). Una por linea, con
# su razon: es la via de crecimiento que el plan R1 autoriza.
SIGLAS_JUSTIFICADAS = frozenset({
    "TMC",    # tuberia metalica corrugada; su minuscula existe como sufijo de simbolo (v_max_tmc)
    "HDPE",   # polietileno de alta densidad; material de la Fase 2
    "FEN",    # Fenomeno El Niño; serie hidrologica de Piura
    "WSDOT",  # Washington State DOT, fuente citada sin PDF en normas/
    "CSV",    # el formato del archivo de puntos (Sec. 1.2)
    "PDF",    # el soporte de las fuentes primarias en normas/
    "EMS",    # estudio de mecanica de suelos (E.050)
    "EH", "EV", "EQ", "LL", "DC",  # cargas AASHTO: empujes, sismo, viva, propia
    "TW",     # tailwater; HW ya sale derivada
    "SPT",    # ensayo de penetracion estandar (E.050); minuscula colisiona en el corpus
})


def _siglas_derivadas():
    """
    Siglas presentes en el repo, leidas de donde ya estan escritas:

    1. Los campos id / titulo / emisor / resolucion de cada `Fuente` de
       src/normativa/fuentes.py (AASHTO, LRFD, ASTM, MTC, RD...).
    2. Los fragmentos en mayuscula de los NOMBRES de asignacion de nivel de
       modulo de src/constantes_normativas.py (PGA, CBR, HDS...).

    Filtro: un token cuya forma minuscula aparece como palabra suelta en el
    texto de esos dos archivos es prosa, no sigla (TABLA, FILA, POR...). Las
    castellanas que sobreviven al filtro estan censadas en _PALABRAS_COLADAS.
    """
    texto_fuentes = (SRC / "normativa" / "fuentes.py").read_text(encoding="utf-8")
    texto_constantes = (SRC / "constantes_normativas.py").read_text(encoding="utf-8")

    candidatas = set()
    for nodo in ast.walk(ast.parse(texto_fuentes)):
        if isinstance(nodo, ast.Call) and getattr(nodo.func, "id", "") == "Fuente":
            for kw in nodo.keywords:
                if kw.arg in ("id", "titulo", "emisor", "resolucion") and \
                        isinstance(kw.value, ast.Constant) and \
                        isinstance(kw.value.value, str):
                    candidatas |= set(re.findall(r"[A-Z]{2,}", kw.value.value))
    for nodo in ast.parse(texto_constantes).body:
        objetivos = []
        if isinstance(nodo, ast.Assign):
            objetivos = [t for t in nodo.targets if isinstance(t, ast.Name)]
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            objetivos = [nodo.target]
        for objetivo in objetivos:
            candidatas |= set(re.findall(r"[A-Z]{2,}", objetivo.id))

    corpus = texto_fuentes + texto_constantes
    return {t for t in candidatas
            if not re.search(rf"\b{re.escape(t.lower())}\b", corpus)}


def _siglas():
    return (_siglas_derivadas() - _PALABRAS_COLADAS) | SIGLAS_JUSTIFICADAS


# ---------------------------------------------------------------------------
# Detectores. Cada uno devuelve {clave: [(campo, fragmento), ...]}
# ---------------------------------------------------------------------------

def _acumular(hallazgos, clave, campo, fragmento):
    hallazgos.setdefault(clave, []).append((campo, fragmento))


# E1: la historia del texto no va en el texto. Los patrones de sesion evitan
# dos vecinos legitimos medidos en el barrido inicial: S0–S5 son perfiles de
# suelo de E.030 (por eso la S exige DOS digitos: las sesiones de un digito
# quedan fuera a proposito, antes que confundir un perfil con una sesion), y
# `C3` aparece como comentario AASHTO (C3.4.1) y como norma ASTM (C76).
_E1_PATRONES = (
    re.compile(r"\bantes se\b", re.IGNORECASE),
    re.compile(r"\bse corrigi[oó]\b", re.IGNORECASE),
    re.compile(r"\bse detect[oó]\b", re.IGNORECASE),
    re.compile(r"\bversi[oó]n anterior\b", re.IGNORECASE),
    re.compile(r"\bredacci[oó]n anterior\b", re.IGNORECASE),
    re.compile(r"\bdec[ií]a\b", re.IGNORECASE),
    re.compile(r"\bven[ií]a\b", re.IGNORECASE),
    re.compile(r"\bS\d{2,}\b"),
    re.compile(r"(?<!ASTM )\bC\d{1,3}[a-z]?\b(?!\.\d)"),
    re.compile(r"\b(?:SIS|NOR|MAT)-[A-Z0-9]+(?:-[A-Z0-9]+)*\b"),
)


def _viola_e1():
    hallazgos = {}
    for clave, campo, texto in _textos():
        for patron in _E1_PATRONES:
            for m in patron.finditer(texto):
                _acumular(hallazgos, clave, campo, m.group(0))
    return hallazgos


# E2: solo formas inequivocas. Los textos del repo van sin tildes, asi que
# "adopto"/"considero" pueden ser terceras personas del pasado ("adoptó") y
# NO se patrullan; "se creo" (por "se creó") tampoco.
_E2_PATRONES = (
    re.compile(r"\bdecidimos\b", re.IGNORECASE),
    re.compile(r"\badoptamos\b", re.IGNORECASE),
    re.compile(r"\belegimos\b", re.IGNORECASE),
    re.compile(r"\bpreferimos\b", re.IGNORECASE),
    re.compile(r"\btomamos\b", re.IGNORECASE),
    re.compile(r"\busamos\b", re.IGNORECASE),
    re.compile(r"\bcreemos\b", re.IGNORECASE),
    re.compile(r"\bconsideramos\b", re.IGNORECASE),
    re.compile(r"(?<!se )\bcreo\b", re.IGNORECASE),
    re.compile(r"\bnuestr[oa]s?\b", re.IGNORECASE),
    re.compile(r"\bnosotros\b", re.IGNORECASE),
)


def _viola_e2():
    hallazgos = {}
    for clave, campo, texto in _textos():
        for patron in _E2_PATRONES:
            for m in patron.finditer(texto):
                _acumular(hallazgos, clave, campo, m.group(0))
    return hallazgos


# E3: dos o mas palabras seguidas todas en mayuscula que no sean todas
# siglas. Se evalua sobre el texto SIN los tramos citados: las mayusculas de
# una cita son de la fuente. Una racha es limpia solo si CADA palabra esta en
# la lista blanca ("AASHTO LRFD" pasa; "CSV NO" no pasa, porque el enfasis
# esta en el NO).
_E3_RACHA = re.compile(
    r"\b[A-ZÁÉÍÓÚÜÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{2,}\b)+")


def _viola_e3():
    siglas = _siglas()
    hallazgos = {}
    for clave, campo, texto in _textos():
        for m in _E3_RACHA.finditer(_sin_citas(texto)):
            palabras = m.group(0).split()
            if all(p in siglas for p in palabras):
                continue
            _acumular(hallazgos, clave, campo, m.group(0))
    return hallazgos


# E4: un conector causal seguido de un simbolo de codigo. "porque M9 lo
# espera" justifica el valor con el codigo, y el codigo no es fuente. Hoy el
# censo esta vacio: la regla existe para que siga asi.
_E4 = re.compile(
    r"\b(?:porque|para que|ya que|puesto que)\s+(?:el |la |los |las |un |una )?"
    r"`?(?:M\d+\b|brentq\b|scipy\b|numpy\b|[a-z_]+_[a-z_]+\(\))",
    re.IGNORECASE)


def _viola_e4():
    hallazgos = {}
    for clave, campo, texto in _textos():
        for m in _E4.finditer(texto):
            _acumular(hallazgos, clave, campo, m.group(0))
    return hallazgos


# E5: una cita entrecomillada de seis o mas palabras es una transcripcion, y
# las transcripciones divergen sin avisar (dos de las seis del reporte ya
# habian divergido cuando se cerro NOR-MEM-01). El umbral de seis palabras
# deja pasar los rotulos cortos de fila ('Muros y estribos de retencion') y
# retiene las frases: es la calibracion del barrido inicial, no un dogma.
_E5_MIN_PALABRAS = 6


def _viola_e5():
    hallazgos = {}
    for clave, campo, texto in _textos():
        for _, _, fragmento in _tramos_citados(texto):
            limpio = fragmento.strip()
            if len(limpio.split()) >= _E5_MIN_PALABRAS:
                _acumular(hallazgos, clave, campo, limpio[:70])
    return hallazgos


# E6: un decimal pegado a un sustantivo dimensional y sin unidad a la vista.
# Detector de alta precision y baja cobertura A PROPOSITO: un factor
# adimensional (F_pga = 1.0, ke = 0.5) no lleva unidad y no debe caer aqui,
# asi que solo se mira el decimal cuya clausula nombra una magnitud fisica.
_E6_TRIGGER = re.compile(
    r"\b(?:cotas?|alturas?|profundidad|espesor|diametros?|radio|anchos?|"
    r"longitud|luz|recubrimiento|cobertura|velocidad|caudal|freatico|"
    r"rasante|resguardo|borde libre|peso especifico|densidad|presion|"
    r"marco de|tubo de)\b", re.IGNORECASE)
_E6_DECIMAL = re.compile(r"\d+\.\d+")
# El decimal esta cubierto si lo sigue una unidad, directamente o al cierre
# de una enumeracion corta ("entre 0.30 y 0.95 m", "2.00 x 1.50 m").
_E6_CUBIERTO = re.compile(
    r"^(?:\s*(?:[xy×,]|y|a|-|–)\s*\d+(?:[.,]\d+)?)*\s*"
    r"(?:m3/s|m³/s|m/s|mm|cm|km|m2|m²|m3|m³|kN/m3|kN/m³|"
    r"kN/m|kN|kPa|MPa|Pa\b|kg/cm2|kg/cm²|kcf|grados?|anios|años|"
    r"ha\b|in\b|ft\b|%|°|m\b|s\b)")
# Contexto de cita o de numeral: "Sec. 4.2", "Tabla 4.4", "§15.1", "3.10.3.1".
_E6_ES_NUMERAL = re.compile(
    r"(?:Art|num|Sec|Tabla|Tablas|Tablero|pag|pags|Nota|ed|Fig|"
    r"Subsecci?on(?:es)?|Apendice|paso|cluster|CP|fila|version|N)"
    r"\W{0,4}$", re.IGNORECASE)


def _viola_e6():
    hallazgos = {}
    for clave, campo, texto in _textos():
        for m in _E6_DECIMAL.finditer(texto):
            ini, fin = m.start(), m.end()
            if re.search(r"\d\.\d+\.|\.\d+-\d|\d-\d",
                         texto[max(0, ini - 2):fin + 2]):
                continue                      # cadena de numeral o tabla
            antes = texto[max(0, ini - 50):ini]
            if "§" in antes[-4:] or _E6_ES_NUMERAL.search(antes):
                continue                      # es una cita, no una magnitud
            if re.search(r"[=*/^<>+]\s{0,2}$", antes) or \
                    re.match(r"[*/^]", texto[fin:fin + 1]):
                continue                      # expresion matematica
            clausula = re.split(r"[.;:]", antes)[-1]
            if not _E6_TRIGGER.search(clausula[-45:]):
                continue                      # sin magnitud fisica a la vista
            if _E6_CUBIERTO.search(texto[fin:fin + 26]):
                continue                      # la unidad esta
            _acumular(hallazgos, clave, campo, texto[max(0, ini - 25):fin + 12])
    return hallazgos


# E7: fechas de calendario en la justificacion. Un año suelto se tolera solo
# como parte de un designador de norma (EG-2013, RM 183-2026), de una edicion
# ("9a ed. (2020)") o de la serie de eventos FEN, que es dato hidrologico de
# esta obra y no bitacora.
_E7_FECHA = re.compile(
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|"
    r"\b(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
    r"setiembre|octubre|noviembre|diciembre)\b|"
    r"\b(?:19|20)\d{2}\b", re.IGNORECASE)
_E7_EXENTO_ANTES = re.compile(
    r"(?:[A-Z]{1,4}-|(?:RM|RD|DS|NTP)\s+[\d.]+[-/]|ed\.\s*\(|edicion\s+)$")
_E7_EXENTO_DESPUES = re.compile(r"^\s*paginas\b")
# Los tres megaeventos FEN de la serie de Piura (dato de la serie, no fecha
# de bitacora); solo exentos en la clave que analiza esa serie.
_E7_ANIOS_FEN = ("homogeneidad_serie_fen", frozenset({"1983", "1998", "2017"}))


def _viola_e7():
    hallazgos = {}
    for clave, criterio in ca.CRITERIOS.items():
        texto = criterio.justificacion or ""
        for m in _E7_FECHA.finditer(texto):
            fecha = m.group(0)
            if _E7_EXENTO_ANTES.search(texto[max(0, m.start() - 12):m.start()]):
                continue
            if _E7_EXENTO_DESPUES.search(texto[m.end():m.end() + 12]):
                continue
            if clave == _E7_ANIOS_FEN[0] and fecha in _E7_ANIOS_FEN[1]:
                continue
            _acumular(hallazgos, clave, "justificacion", fecha)
    return hallazgos


# ---------------------------------------------------------------------------
# Los censos del trinquete — MEDIDOS sobre el arbol de R1, no opinados.
# Solo pueden decrecer: al limpiar una clave, su entrada se borra o baja.
# ---------------------------------------------------------------------------

# E1 — 63 violaciones en 25 claves. Lo mas cargado: factores_carga_aashto
# (13, narra el cluster C03 entero con sus cinco hallazgos), HW_D_max y
# D_max_catalogo (5 cada una).
VIOLACIONES_E1 = {
    "D_max_catalogo": 5,
    "HW_D_max": 5,
    "PERFIL_SUELO_PRESUNTO": 1,
    "acceso_mantenimiento_v2b": 3,
    "categoria_refuerzo_aashto": 1,
    "clase_sitio": 2,
    "clases_producto_por_relleno": 2,
    "cobertura_minima_aashto": 1,
    "cobertura_minima_cajon": 3,
    "condicion_pavimento": 1,
    "cortante_alto_muro_e060_art_11_10_10_2": 3,
    "diametros_normalizados": 3,
    "embocadura_cajon": 2,
    "espesor_pared_cajon": 1,
    "espesor_pared_conducto": 3,
    "exposicion_quimica_ems": 1,
    "factores_carga_aashto": 13,
    "geometria_control_salida": 2,
    "k_v": 1,
    "ke_entrada_cajon": 1,
    "origen_cota_fondo_entrada": 2,
    "resguardo_HW_subrasante": 2,
    "riesgo_admisible_propietario": 1,
    "secciones_cajon_normalizadas": 1,
    "v_max_concreto_eleccion": 3,
}

# E2 — nace limpio: ni una primera persona en los 69. La regla queda para
# que siga asi.
VIOLACIONES_E2 = {}

# E3 — la regla mas violada: 204 rachas de enfasis en 46 claves. Los textos
# usan mayusculas como titulos de seccion internos ('POR QUE NO SE
# SOSTIENE'), que es exactamente el registro de alegato que R2 va a
# reescribir.
VIOLACIONES_E3 = {
    "D_max_catalogo": 4,
    "F_pga": 11,
    "F_pga_lectura_columna_extrema": 1,
    "HW_D_max": 6,
    "N_cq_N_gammaq_meyerhof": 1,
    "TR_evento_extremo": 1,
    "acceso_mantenimiento_v2b": 6,
    "borde_libre_canal_m": 3,
    "categoria_refuerzo_aashto": 6,
    "clase_sitio": 10,
    "clases_producto_por_relleno": 3,
    "cobertura_minima_aashto": 7,
    "cobertura_minima_cajon": 7,
    "condicion_pavimento": 7,
    "cortante_alto_muro_e060_art_11_10_10_2": 6,
    "diametros_normalizados": 1,
    "embocadura_cajon": 7,
    "espesor_pared_cajon": 7,
    "espesor_pared_conducto": 7,
    "exposicion_quimica_ems": 2,
    "factor_muro_eleccion": 2,
    "factor_recubrimiento_banda_intermedia_ac": 3,
    "factores_carga_aashto": 12,
    "gamma_EQ": 2,
    "geometria_control_salida": 4,
    "h_eq_bajo_altura_tabulada": 3,
    "h_eq_banda_intermedia_borde": 3,
    "hds5_embocadura_hdpe": 1,
    "k_v": 2,
    "ke_entrada_cajon": 6,
    "metodo_transicion_hds5": 3,
    "n_celdas_cajon": 6,
    "n_manning_cajon": 6,
    "n_manning_hdpe": 1,
    "origen_cota_fondo_entrada": 11,
    "predimensionamiento_cabezal": 2,
    "procedimiento_flexion_corte_aashto_sec5": 1,
    "resguardo_HW_subrasante": 5,
    "riesgo_admisible_propietario": 3,
    "seccion_receptor": 6,
    "secciones_cajon_normalizadas": 5,
    "situacion_recubrimiento_aashto": 5,
    "tabla_recubrimiento_aashto_mm": 2,
    "talud_terraplen": 1,
    "umbral_area_quebrada_importante_ha": 4,
    "v_max_concreto_eleccion": 2,
}

# E4 — nace limpio: nadie justifica hoy un valor con lo que el codigo
# espera. La regla queda de guardia.
VIOLACIONES_E4 = {}

# E5 — 46 transcripciones largas en 26 claves. Las peores: clase_sitio y
# cobertura_minima_cajon (4 cada una, citas en ingles de AASHTO que el
# registro deberia llevar como Verbatim).
VIOLACIONES_E5 = {
    "F_pga": 1,
    "HW_D_max": 2,
    "TR_evento_extremo": 1,
    "acceso_mantenimiento_v2b": 1,
    "categoria_refuerzo_aashto": 2,
    "clase_sitio": 4,
    "clases_producto_por_relleno": 1,
    "cobertura_minima_aashto": 2,
    "cobertura_minima_cajon": 4,
    "condicion_pavimento": 1,
    "cortante_alto_muro_e060_art_11_10_10_2": 3,
    "embocadura_cajon": 1,
    "espesor_pared_conducto": 1,
    "exposicion_quimica_ems": 1,
    "factor_muro_eleccion": 3,
    "factor_recubrimiento_banda_intermedia_ac": 1,
    "factores_carga_aashto": 3,
    "geometria_control_salida": 1,
    "n_manning_cajon": 1,
    "origen_cota_fondo_entrada": 1,
    "riesgo_admisible_propietario": 2,
    "seccion_receptor": 2,
    "situacion_recubrimiento_aashto": 2,
    "tabla_recubrimiento_aashto_mm": 1,
    "talud_terraplen": 1,
    "v_max_concreto_eleccion": 3,
}

# E6 — una sola magnitud sin unidad al alcance del detector: el 0.30 (m) que
# EG-2013 exige como recubrimiento, en espesor_pared_conducto.
VIOLACIONES_E6 = {
    "espesor_pared_conducto": 1,
}

# E7 — nace limpio: los años que sobreviven en las justificaciones son
# designadores de norma (EG-2013), ediciones («9a ed. (2020)») o la serie
# FEN de Piura, y las tres formas estan exentas con su razon.
VIOLACIONES_E7 = {}


# ---------------------------------------------------------------------------
# El contraste comun
# ---------------------------------------------------------------------------

_COMO_CORREGIR = {
    "E1": "quita la narracion de bitacora: la historia del texto vive en git "
          "y en docs/decisiones_diferidas.md, y el hallazgo se declara en el "
          "tracker, no en la justificacion",
    "E2": "reescribe en impersonal: 'se adopta', no 'adoptamos'",
    "E3": "quita el enfasis en mayusculas (o, si TODAS las palabras son "
          "siglas reales, añadelas a SIGLAS_JUSTIFICADAS con su razon)",
    "E4": "el codigo no es fuente: justifica el valor con su norma o su "
          "adopcion declarada, no con lo que un modulo espera",
    "E5": "no transcribas la frase: citala por su cita_id del registro "
          "(Registro.textos_literales() ya la verifica contra su pagina)",
    "E6": "añade la unidad SI a la magnitud (o presenta el numero como lo "
          "que es, si no es una magnitud dimensional)",
    "E7": "quita la fecha de calendario: si es historia, va en git; si es "
          "designador de norma o dato de serie, declaralo en las exenciones "
          "del detector con su razon",
}


def _contrastar(regla, censo, medido):
    """
    El trinquete: igualdad EXACTA entre lo medido y lo censado, con mensajes
    que nombran CLAVE, CAMPO y QUE corregir.
    """
    conteos = {clave: len(v) for clave, v in medido.items()}
    conteos = {k: n for k, n in conteos.items() if n}
    censo_vivo = {k: n for k, n in censo.items() if n}

    problemas = []
    for clave in sorted(set(conteos) | set(censo_vivo)):
        hay, censadas = conteos.get(clave, 0), censo_vivo.get(clave, 0)
        if hay > censadas:
            detalle = "; ".join(
                f"[{campo}] {fragmento!r}"
                for campo, fragmento in medido.get(clave, []))
            problemas.append(
                f"{regla} · '{clave}': {hay} violacion(es) y el censo admite "
                f"{censadas}. {detalle}. Correccion: {_COMO_CORREGIR[regla]}.")
        elif hay < censadas:
            problemas.append(
                f"{regla} · '{clave}': el censo la da por sucia con "
                f"{censadas} y hoy tiene {hay}. Baja su entrada en "
                f"VIOLACIONES_{regla} — el censo solo decrece, pero decrece "
                f"de verdad, no por olvido.")
    assert not problemas, (
        f"el estilo de los criterios se movio respecto del censo de "
        f"VIOLACIONES_{regla}:\n" + "\n".join(problemas))


def test_E1_sin_bitacora():
    _contrastar("E1", VIOLACIONES_E1, _viola_e1())


def test_E2_sin_primera_persona():
    _contrastar("E2", VIOLACIONES_E2, _viola_e2())


def test_E3_sin_mayusculas_enfaticas():
    _contrastar("E3", VIOLACIONES_E3, _viola_e3())


def test_E4_el_codigo_no_es_fuente():
    _contrastar("E4", VIOLACIONES_E4, _viola_e4())


def test_E5_sin_transcripciones():
    _contrastar("E5", VIOLACIONES_E5, _viola_e5())


def test_E6_magnitud_con_unidad():
    _contrastar("E6", VIOLACIONES_E6, _viola_e6())


def test_E7_sin_fechas_de_calendario():
    _contrastar("E7", VIOLACIONES_E7, _viola_e7())


def test_los_censos_solo_nombran_claves_reales():
    """
    Un censo con una clave que ya no existe (renombrada, retirada) es un
    censo muerto: nadie lo baja porque nada lo mide. Se detecta aqui.
    """
    for nombre, censo in (("E1", VIOLACIONES_E1), ("E2", VIOLACIONES_E2),
                          ("E3", VIOLACIONES_E3), ("E4", VIOLACIONES_E4),
                          ("E5", VIOLACIONES_E5), ("E6", VIOLACIONES_E6),
                          ("E7", VIOLACIONES_E7)):
        fantasmas = set(censo) - set(ca.CRITERIOS)
        assert not fantasmas, (
            f"VIOLACIONES_{nombre} censa claves que no existen en "
            f"criterios_adoptados.CRITERIOS: {sorted(fantasmas)}. "
            f"Renombra o retira esas entradas del censo.")


def test_la_lista_blanca_de_siglas_sigue_derivada():
    """
    Contrapeso de E3: que la derivacion siga produciendo las siglas
    estructurales (si fuentes.py o constantes_normativas.py cambian de forma
    y la derivacion se queda vacia, E3 empezaria a acusar 'AASHTO LRFD' como
    enfasis, que es exactamente el falso positivo que la lista evita).
    """
    derivadas = _siglas_derivadas()
    for sigla in ("AASHTO", "LRFD", "ASTM", "MTC", "HDS", "PGA", "CBR"):
        assert sigla in derivadas, (
            f"la derivacion de siglas ya no encuentra {sigla!r} en "
            f"fuentes.py / constantes_normativas.py: revisa "
            f"_siglas_derivadas() antes de que E3 acuse citas legitimas.")
