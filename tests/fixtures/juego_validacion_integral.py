"""
DATOS DE PRUEBA, NO DEL PROYECTO.
=================================

tests/fixtures/juego_validacion_integral.py -- el JUEGO DE DATOS DE PRUEBA
de la validacion integral de las tres familias (T-11 de la cadena T).

NINGUN VALOR DE ESTE ARCHIVO ES DEL PROYECTO. Ninguno es una medicion, un
ensayo, un levantamiento ni una decision del Propietario: son valores
PLAUSIBLES (orden de magnitud) puestos para que la corrida de expediente de
`tests/ejemplo_puntos.csv` recorra el programa de punta a punta, y cada uno
lleva al lado la linea que dice por que es plausible y de donde se tomo.
Donde ya existia un dato de prueba en el repositorio (los de T-7b y T-7c
para el cabezal, los de T-8 para la Fase 6, la guia de perfil, la linea
base de la Familia C), se REUTILIZA y se dice de donde viene.

COMO ENTRA AL PROGRAMA: SOLO POR LAS PUERTAS DE ENTRADA. Este modulo no es
leido por ningun modulo de `src/`: `tests/apoyo/validacion_integral.py` lo
MATERIALIZA en los archivos que la CLI lee (una copia de
`tests/ejemplo_puntos.csv` con las celdas de abajo, el JSON de
`--datos-externos`, el JSON de `--datos-sitio`) y en los `--declarar` de la
corrida, y los pasa por la misma puerta que un usuario: la CLI en
subproceso, o `servicio.correr` con las mismas guardias
(`cargar_datos_externos`, `cargar_datos_sitio`, `establecer_valor_dinamico`).
**Nada de aqui se escribe en `criterios_adoptados.py`, `datos_sitio.py` ni
`constantes_normativas.py`**: los vacios de esos archivos son decisiones del
proyecto y siguen vacios (PRECISIONES_T-11, punto 1).

Por que un modulo de Python y no cuatro archivos sueltos: la cabecera
«DATOS DE PRUEBA, NO DEL PROYECTO» tiene que ir en CADA archivo, y ni el
CSV de puntos (`M0_carga` no admite lineas de comentario) ni un JSON de
datos externos (la seccion desconocida es `DatoInvalidoError`) la admiten.
Aqui va una vez y vale para todo el juego; los archivos materializados se
escriben en un directorio temporal, SALVO los de la tercera corrida de
referencia del indice de formulas (la variante `caudal_calculado`), que
`tests/apoyo/validacion_integral.py::escribir_corrida_de_referencia` escribe
y versiona en `tests/fixtures/corridas_de_referencia/hidrologia_calculada/`
con un `LEEME.md` rotulado: tres de esos seis archivos (el CSV de puntos y
los dos JSON) no admiten la cabecera (corregido en las correcciones de T-11,
H12: decia que nunca se versionaban).

Lo que el juego deja fuera A PROPOSITO esta en `OMITIDAS_A_PROPOSITO`, con
su razon: es lo unico que un bloqueo de la corrida completa puede nombrar
como causa (PRECISIONES_T-11: «nunca un criterio vacio»).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

RAIZ = Path(__file__).resolve().parents[2]

ROTULO = "DATOS DE PRUEBA, NO DEL PROYECTO"

# El CSV de partida: el fixture de siempre, sin tocar. Las celdas de abajo se
# escriben sobre una COPIA.
CSV_BASE = RAIZ / "tests" / "ejemplo_puntos.csv"

# ---------------------------------------------------------------------------
# 1. Celdas del CSV que el fixture deja vacias (copia del CSV)
# ---------------------------------------------------------------------------
# (id, columna) -> texto de la celda.
CELDAS: Dict[Tuple[str, str], str] = {
    # Freatico a 3.0 m bajo el terreno del cruce en los cuatro puntos: orden
    # de magnitud de un aluvial costero en estiaje (2 a 5 m). T-7b uso 2.0 m
    # para A-01; con 2.0 m el desplante de los cabezales de SALIDA, que baja
    # con la hoya de socavacion, queda bajo el agua y la condicion sismica
    # es «metodo no evaluable» (variante `freatico_a_2m`, que el documento
    # de validacion imprime): se elige 3.0 m para que la corrida completa
    # evalue los dos marcos y se DICE.
    ("A-01", "NF_profundidad_m"): "3.0",
    ("A-02", "NF_profundidad_m"): "3.0",
    ("B-01", "NF_profundidad_m"): "3.0",
    ("C-01", "NF_profundidad_m"): "3.0",
    # La coronacion del canal de C-01: la de la guia de perfil y de la
    # corrida 6 de la linea base (38.30 msnm: 1.40 m sobre el terreno del
    # cruce, un canal en terraplen). Sin ella VC1 no se evalua.
    ("C-01", "cota_coronacion_canal"): "38.30",
}

# ---------------------------------------------------------------------------
# 2. `--datos-externos`
# ---------------------------------------------------------------------------
EXTERNOS: Dict[str, Any] = {
    "globales": {
        # Luz del cruce de 3.0 m: la de la corrida de punta a punta de T-7b
        # y T-7c (la guia usa 2.75 m); bajo el umbral de 6.0 m, alcantarilla.
        "luz_m": 3.0,
        # TW de 0.30 m sobre el fondo de la salida: el de la guia de perfil y
        # de la linea base. B-01 corre CON ESTE TW y no con el de 1.00 m de
        # la linea base, con el que no dimensiona (V2): variante
        # `B01_tw_de_la_linea_base`.
        "TW_m": 0.3,
        # Bombeo de 2 %: el de un pavimento asfaltico en la Tabla 304.03 del
        # DG-2018 (rango 2.0-2.5 %). Sin el, la plataforma se toma horizontal
        # y se avisa.
        "bombeo": 0.02,
        # El acceso de mantenimiento que pide `acceso_mantenimiento_v2b`.
        "acceso_mantenimiento_previsto": True,
        # Quebradas y drenes costeros: llevan agua solo en avenidas.
        "regimen_flujo_descarga": "intermitente",
        # Derecho de via de 20 m: el minimo de la Tabla 304.09 del DG-2018
        # para carretera de segunda clase (la clase de via de prueba del
        # sitio). Solo lo lee V5 con el metodo `embalse_a_nivel`; con el
        # metodo declarado abajo (`cota_de_afectacion`) no se lee, y se pone
        # para que la ventana de `remanso_derecho_via` se pueda barrer.
        "ancho_derecho_via_m": 20.0,
        # Ensayos de durabilidad (corregido en las correcciones de T-11, H6
        # de su auditoria: decia «suelo NO agresivo» y el programa lo
        # califica de agresivo para el acero). Sulfatos de 500 ppm en el
        # suelo (0.05 % en peso) y 100 ppm en el agua: «insignificante» PARA
        # EL CONCRETO por la Tabla 4.4 de E.060 (pag. impresa 38: 0,0 <=
        # SO4 < 0,1 % en el suelo, 0 <= SO4 < 150 ppm en el agua, sin
        # requisito), pero AGRESIVO PARA EL ACERO GALVANIZADO por el umbral
        # de AASHTO LRFD 11.10.6.4.2a (pag. impresa 11-89: «Sulfates <= 200
        # ppm») que `suelo_agresivo_acero_lrfd` aplica por analogia: la TMC
        # sigue candidata con aviso (`suelo_agresivo_lrfd_sobre_tmc` =
        # 'aviso'); con 'excluye' sale (variante
        # `v_max_concreto_3_con_tmc_excluida`). Cloruros bajo los 100 ppm
        # del mismo umbral, pH neutro, resistividad sobre 3000 ohm·cm,
        # abrasion baja. Con cloruros, A7 del cabezal no cumple con el f'c
        # de archivo: variante `agua_con_cloruros`. El dato NO se cambia.
        "sulfatos_suelo_ppm": 500,
        "sulfatos_agua_ppm": 100,
        "cloruros_ppm": 50,
        "pH": 7.5,
        "resistividad_ohm_cm": 3500,
        "abrasion": "poco_abrasivo",
    },
    "puntos": {
        "A-01": {
            # V5 por la cota de afectacion: la de T-7b (44.00 msnm, 1.90 m
            # sobre el terreno del cruce y 0.20 m bajo la rasante).
            "cota_afectacion_aguas_arriba_msnm": 44.00,
            # V8: los de T-7b (Q del evento extremo 1.3 m3/s = 1.11 veces el
            # de diseño; TW del receptor 0.50 m en ese evento).
            "Q_evento_extremo_m3s": 1.3,
            "TW_evento_extremo_m": 0.5,
            # Fase 6: los de `DATOS_T8` de tests/test_t8_proteccion.py (grava
            # gruesa en el cauce; lecho no cohesivo de grava arenosa bien
            # graduada, D84 30 mm, D16 2 mm, 8 % de finos; pico de 60 min).
            "tipo_terreno_receptor": "graduado_grava_gruesa",
            "tipo_terreno_entrada": "graduado_grava_gruesa",
            "material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.03,
                                      "D16_m": 0.002, "pasa_200_pct": 8},
            "duracion_caudal_pico_min": 60,
        },
        "A-02": {
            # La misma regla que A-01: 1.90 m sobre el terreno del cruce.
            "cota_afectacion_aguas_arriba_msnm": 41.75,
            # La misma proporcion que A-01 (1.11 veces el de diseño).
            "Q_evento_extremo_m3s": 0.53,
            "TW_evento_extremo_m": 0.5,
            # Fase 6: los de `DATOS_T8` (grava con piedras mayores de 20 cm
            # y una profundidad de socavacion de un estudio, 0.80 m, que es
            # la via del dato declarado: gana sobre la estimada).
            "tipo_terreno_receptor": "graduado_grava_a_piedras_mayor_20cm",
            "tipo_terreno_entrada": "graduado_grava_a_piedras_mayor_20cm",
            "profundidad_socavacion_estimada_m": 0.8,
        },
        "B-01": {
            # La misma regla que A-01 y A-02.
            "cota_afectacion_aguas_arriba_msnm": 40.30,
            "Q_evento_extremo_m3s": 0.106,
            "TW_evento_extremo_m": 0.5,
            # Fase 10: cuneta al 1 % (dentro de 0.5-2 % del num. 4.1.2 c));
            # faja tributaria de 7.0 m (semiplataforma de 4.80 m, berma y
            # talud de corte); el tramo empieza en 2+300, a 150 m de la obra,
            # bajo los 200 m de `long_max_cuneta`. Sin el inicio declarado el
            # tramo empieza en A-02 (530 m) y VB1 no cumple: variante
            # `B01_sin_inicio_de_tramo`, que es el caso de la linea base.
            "S_cuneta": 0.01,
            "ancho_tributario_m": 7.0,
            "inicio_tramo_cuneta_km": 2.3,
            # Fase 6: arena del SUCS 'SM' de la fila B-01; la fila granular
            # mas cercana de la Tabla N 11 es la arena fina no coloidal.
            # Lecho de arena limosa: D84 2 mm, D16 0.1 mm, 20 % de finos.
            "tipo_terreno_receptor": "arena_fina_no_coloidal",
            "tipo_terreno_entrada": "arena_fina_no_coloidal",
            "material_lecho_salida": {"tipo": "no_cohesivo", "D84_m": 0.002,
                                      "D16_m": 0.0001, "pasa_200_pct": 20},
        },
        "C-01": {
            # El caudal y las pendientes de C-01 de la linea base
            # (`entradas_ampliadas.json`): 0.85 m3/s del canal; el conducto
            # mas tendido (0.004) que el canal (0.006), como alli.
            "Q_m3s": 0.85,
            "S_conducto": 0.004,
            "S_cauce": 0.006,
            # V8 tambien se exige en la Familia C: 1.0 m3/s (1.18 veces el
            # de diseño del canal) con 0.60 m de tirante.
            "Q_evento_extremo_m3s": 1.0,
            "TW_evento_extremo_m": 0.6,
            # TW de C-01 = el tirante normal del canal que este mismo juego
            # declara abajo (correcciones de T-11, H7 de su auditoria: el TW
            # global de 0.30 m era menor). A mano, b 1.0, z 1.5, S 0.006,
            # n 0.025: con y = 0.41 m, A = (1.0 + 1.5·0.41)·0.41 = 0.662 m2,
            # P = 1.0 + 2·0.41·(1 + 1.5^2)^0.5 = 2.478 m, R = 0.267 m y
            # Q = A·R^(2/3)·S^(1/2)/n = 0.662·0.415·0.0775/0.025 = 0.85
            # m3/s, el caudal del canal. Ni la seccion ni el HW de salida se
            # mueven mas que en la cuarta cifra (el TW sigue bajo y_c).
            "TW_m": 0.41,
            # La seccion del MISMO canal: solera de 1.0 m, talud 1.5:1,
            # pendiente del canal, n de 0.025 (tierra) y 2.10 m de fondo
            # (36.20) a coronacion (38.30).
            "seccion_receptor_medida": {"b_m": 1.0, "z_HV": 1.5, "S": 0.006,
                                        "n": 0.025, "altura_total_m": 2.1},
            # Canal en limo ('ML'): la fila de la Tabla N 11 mas cercana es
            # la arcilla limosa no coloidal. La socavacion la da un estudio
            # del canal (0.50 m); con el lecho cohesivo estimado la hoya
            # baja 1.93 m y el cabezal de salida queda fuera de los metodos
            # implementados (variante `C01_lecho_cohesivo`).
            "tipo_terreno_receptor": "arcilla_limosa_no_coloidal",
            "tipo_terreno_entrada": "arcilla_limosa_no_coloidal",
            "profundidad_socavacion_estimada_m": 0.5,
        },
    },
}

# ---------------------------------------------------------------------------
# 3. `--datos-sitio` (los [S] de corredor que `datos_sitio.py` deja vacios)
# ---------------------------------------------------------------------------
FECHA = "2026-11-13"
_TRAZ = f"{ROTULO}: valor de prueba de la validacion integral (T-11)"

SITIO: Dict[str, Dict[str, Any]] = {
    # Los dos de la sobrecarga viva: los de T-7b/T-7c (muro paralelo al
    # trafico, trasdos a 1.60 m del borde de calzada).
    "orientacion_muro_respecto_al_trafico": {
        "valor": "paralelo_al_trafico", "trazabilidad": _TRAZ, "fecha": FECHA},
    "distancia_borde_calzada_al_trasdos_m": {
        "valor": 1.6, "trazabilidad": _TRAZ, "fecha": FECHA},
    # Calzada de dos carriles, uno por sentido.
    "carriles_por_sentido": {
        "valor": 1, "trazabilidad": _TRAZ, "fecha": FECHA},
    # Una fila de la Tabla 304.09 (la de los 20 m del derecho de via).
    "clase_de_via": {
        "valor": "carretera_segunda_clase", "trazabilidad": _TRAZ,
        "fecha": FECHA},
    "existe_informacion_secundaria_tramo": {
        "valor": "no", "trazabilidad": _TRAZ, "fecha": FECHA},
}

# ---------------------------------------------------------------------------
# 4. `--cuencas` / `--estacion`: los sinteticos de T-1, que ya llevan su
#    rotulo. Con `Q_m3s` lleno en el CSV, el caudal DECLARADO gana y la Fase
#    1-bis solo imprime su contraste; la variante `caudal_calculado` vacia
#    las tres celdas y deja que el programa lo calcule.
# ---------------------------------------------------------------------------
CUENCAS = RAIZ / "tests" / "fixtures" / "hidrologia" / "cuencas_prueba.csv"
ESTACION = RAIZ / "tests" / "fixtures" / "hidrologia" / "estacion_prueba.csv"

# ---------------------------------------------------------------------------
# 5. `--declarar`: los CRITERIOS que el archivo deja sin valor a proposito,
#    y las decisiones de proyectista o Propietario que la corrida necesita
# ---------------------------------------------------------------------------
DECLARACIONES: Dict[str, Any] = {
    # V5 y V8 (decisiones del proyectista y del Propietario): las de T-7b.
    "remanso_derecho_via": "cota_de_afectacion",
    "TR_evento_extremo": 500.0,
    "umbral_no_colapso_evento_extremo": "sin_desborde_de_la_plataforma",
    # Geotecnia del cabezal (ensayos del EMS): los de T-7b. Relleno de
    # trasdos granular, phi 34 grados (ventana 30-38); fundacion no cohesiva
    # phi 32 grados, gamma 18 kN/m3; gamma saturado del relleno 20 kN/m3.
    "phi_relleno_trasdos": 34.0,
    "c_phi_fundacion": {"cohesivo": False, "c_kpa": 0.0, "phi_grados": 32.0,
                        "gamma_kn_m3": 18.0},
    "peso_especifico_saturado_relleno_kn_m3": 20.0,
    # Decisiones de proyectista y Propietario que T-7b declaro en su corrida
    # de punta a punta (el archivo tiene otro valor; se declaran porque son
    # de quien hace los planos): trasdos con filtro y lloraderos, y muro que
    # admite el desplazamiento bajo sismo.
    "drenaje_trasdos": "drenado",
    "factor_muro_eleccion": "reduccion_por_desplazamiento",
    # Armado del cabezal: acero sin recubrir (la columna que mas
    # recubrimiento pide, la del conftest) y la Clase 2 de exposicion de
    # 5.6.7 (subestructura en el cauce: la que T-7c recomendo).
    "categoria_refuerzo_aashto": "A",
    "clase_exposicion_fisuracion_cabezal": "clase_2",
    # Analisis quimico del EMS, coherente con los ensayos de durabilidad de
    # arriba (500 ppm = 0.05 % de sulfato en suelo; 100 ppm en agua; sin
    # cloruros, sin congelamiento, sin exigencia de baja permeabilidad).
    "exposicion_quimica_ems": {
        "so4_suelo_pct": 0.05,
        "so4_agua_ppm": 100.0,
        "tabla_4_2": {"baja_permeabilidad": False,
                      "congelamiento_deshielo": False,
                      "cloruros": False},
    },
    # Tratamiento FEN de la serie sintetica: la serie completa (lo mas
    # conservador por construccion). Solo rige el caudal CALCULADO.
    "homogeneidad_serie_fen": "serie_completa",
}

# Por que el juego PISA un valor de archivo (correcciones de T-11, H2): las
# dos son decisiones del Propietario y del proyectista que el dueño CONFIRMO
# con su valor de archivo el 2026-11-13; el juego las cambia para que la
# validacion recorra la cadena sismica y el caso drenado, que con los
# valores de archivo no se ejercitan. Por eso la corrida TITULAR es la
# variante `decisiones_de_archivo` y el juego tal como esta es la variante
# que ejercita esas dos ramas. Un test exige que esta tabla nombre
# exactamente las claves de `DECLARACIONES` cuyo criterio tiene valor de
# archivo.
PISA_EL_ARCHIVO_PORQUE: Dict[str, str] = {
    "drenaje_trasdos": (
        "con 'sin_drenaje' el relleno se calcula saturado y la condicion "
        "sismica del cabezal es «metodo no evaluable» (ficha T7B-05): "
        "'drenado' deja evaluar la cadena sismica entera"),
    "factor_muro_eleccion": (
        "'reduccion_por_desplazamiento' (k_h = 0.5·k_h0) es la otra rama de "
        "la eleccion del Propietario: con el relleno drenado ejercita el "
        "empuje sismico reducido"),
}

# ---------------------------------------------------------------------------
# 6. Lo que el juego deja fuera A PROPOSITO, con su razon
# ---------------------------------------------------------------------------
OMITIDAS_A_PROPOSITO: Dict[str, str] = {
    "longitud_m": ("la longitud la calcula 7.B por extremo; declararla "
                   "sustituiria el calculo que la validacion quiere ver"),
    "L_hidraulico_m": ("la longitud por capacidad de la cuneta la calcula "
                       "la Fase 10 con S_cuneta y el ancho tributario"),
    "S_conducto (A-01, A-02, B-01)": ("el conducto sigue la pendiente del "
                                      "cauce, que es el caso normal"),
    "categoria_tr": "la fila de la Tabla N 02 la decide area_ha",
    "peralte": ("excluyente con el bombeo: los cuatro cruces se suponen en "
                "tangente"),
    "cota_fondo_entrada": ("es una MEDICION en el cauce que el juego no "
                           "inventa: rige `origen_cota_fondo_entrada` y la "
                           "memoria avisa que es una adopcion"),
    "cabezal_declarado": ("la geometria del cabezal la propone la regla de "
                          "T-7a; que no pase E3 ni E1 con ella es un "
                          "RESULTADO (la zapata no se itera por decision "
                          "del dueño), y la variante "
                          "`zapata_declarada_3m` muestra el otro lado"),
    "suelo_fundacion": ("la fundacion entra por el criterio de corredor "
                        "`c_phi_fundacion`; el dato por punto ganaria"),
    "Q_receptor_m3s / cota_TW": ("el TW entra declarado (vía 1), que manda "
                                 "sobre las otras tres"),
    "perfil_hdpe_fabricante": ("dato del fabricante de un tubo: ningun "
                               "punto adopta HDPE (el concreto es el primer "
                               "candidato) y el juego no inventa un "
                               "producto"),
    "D_max_catalogo / v_max_concreto_eleccion / riesgo_admisible_propietario"
    " / pendiente_relleno_trasdos_i / friccion_muro_suelo_delta": (
        "criterios [A] OPCIONALES: sin declararlos rige una regla escrita en "
        "su ficha, no un bloqueo"),
}

# ---------------------------------------------------------------------------
# 7. Variantes: el juego con UNA entrada cambiada, para ver el otro lado de
#    cada decision que el juego tomo. Cada una es (que dice, cambios).
#    Los cambios se aplican sobre una copia del juego:
#      ("celda", id, columna, texto o None)
#      ("externo", id o "globales", clave, valor o None)
#      ("declarar", clave, valor o None)
#      ("csv_caudal_vacio", (ids...))
# ---------------------------------------------------------------------------
VARIANTES: Dict[str, Tuple[str, Tuple[Tuple[Any, ...], ...]]] = {
    # LA CORRIDA TITULAR de la validacion (correcciones de T-11, H2 de su
    # auditoria; resolucion del orquestador aceptada por el dueño el
    # 2026-11-13): el juego con las DOS DECISIONES DE ARCHIVO que el dueño
    # confirmo el 2026-11-13 --`drenaje_trasdos` = 'sin_drenaje' y
    # `factor_muro_eleccion` = 'sin_reduccion'--, que el juego pisa para
    # ejercitar la cadena sismica y el caso drenado (ver
    # `PISA_EL_ARCHIVO_PORQUE`). Con el relleno sin drenaje el agua llega al
    # plano de empuje y el peso especifico SATURADO del relleno, que es un
    # ensayo del EMS sin valor de archivo, se pide: el juego lo declara por
    # la puerta de los ensayos (`--declarar`) con 20 kN/m3 --relleno granular
    # compactado: gamma_sat = gamma_d + n·gamma_w ≈ 17.5 + 0.25·9.81 = 20.0
    # kN/m3; el rango usual de un granular saturado es 19 a 22 kN/m3--. No es
    # un dato del sitio.
    "decisiones_de_archivo": (
        "Las dos decisiones de ARCHIVO que el juego pisa (`drenaje_trasdos` = "
        "'sin_drenaje', `factor_muro_eleccion` = 'sin_reduccion'), con el "
        "gamma saturado del relleno de prueba (20 kN/m³) que el relleno sin "
        "drenaje pide: la corrida TITULAR de §2",
        (("declarar", "drenaje_trasdos", None),
         ("declarar", "factor_muro_eleccion", None),
         ("declarar", "peso_especifico_saturado_relleno_kn_m3", 20.0))),
    "B01_tw_de_la_linea_base": (
        "B-01 con el TW de 1.00 m de la linea base (el caso por defecto que "
        "el dueño decidio dejar)",
        (("externo", "B-01", "TW_m", 1.0),)),
    "B01_sin_inicio_de_tramo": (
        "B-01 sin `inicio_tramo_cuneta_km`: el tramo empieza en A-02 "
        "(530 m), el caso de la linea base",
        (("externo", "B-01", "inicio_tramo_cuneta_km", None),)),
    "freatico_a_2m": (
        "Freatico a 2.0 m (el de T-7b) en los cuatro puntos",
        tuple(("celda", i, "NF_profundidad_m", "2.0")
              for i in ("A-01", "A-02", "B-01", "C-01"))),
    "agua_con_cloruros": (
        "Analisis quimico con cloruros (la fila de cloruros de la Tabla 4.2 "
        "de E.060), como en el conftest",
        (("declarar", "exposicion_quimica_ems", {
            "so4_suelo_pct": 0.05, "so4_agua_ppm": 100.0,
            "tabla_4_2": {"baja_permeabilidad": False,
                          "congelamiento_deshielo": False,
                          "cloruros": True}}),)),
    "sin_socavacion_A01": (
        "A-01 sin lecho declarado: la hoya no se estima y el desplante de "
        "salida queda en el minimo de E.050",
        (("externo", "A-01", "material_lecho_salida", None),)),
    "C01_lecho_cohesivo": (
        "C-01 con lecho cohesivo estimado (IP 8, Sv 25 kPa, 60 % de finos) "
        "en vez de la socavacion de un estudio",
        (("externo", "C-01", "profundidad_socavacion_estimada_m", None),
         ("externo", "C-01", "material_lecho_salida",
          {"tipo": "cohesivo", "IP": 8, "Sv_Pa": 25000, "pasa_200_pct": 60}))),
    "zapata_declarada_3m": (
        "A-01 con la zapata de sus dos cabezales declarada de 3.00 m de "
        "ancho (`cabezal_declarado`, la prueba de T-7b)",
        (("externo", "A-01", "cabezal_declarado", {"ancho_zapata_m": 3.0}),)),
    "drenaje_de_archivo": (
        "Trasdos sin drenaje (el valor de archivo de `drenaje_trasdos`)",
        (("declarar", "drenaje_trasdos", None),)),
    "caudal_calculado": (
        "A-01, A-02 y B-01 con `Q_m3s` vacio: el caudal lo calcula la Fase "
        "1-bis con las cuencas y la serie sinteticas de T-1",
        (("csv_caudal_vacio", ("A-01", "A-02", "B-01")),)),
    # La condicional que el juego completo no dispara (contrato §7): el
    # tratamiento FEN solo lo lee el caudal CALCULADO.
    # El fondo de entrada de C-01 en el canal (correcciones de T-11, H7):
    # sin el dato, la regla de archivo (`origen_cota_fondo_entrada` =
    # 'cota_terreno') pone la entrada en el terreno del cruce (36.90 msnm),
    # 0.70 m sobre el fondo del canal (36.20), y la salida queda colgada
    # sobre el canal (VC2). 36.30 msnm es la cota que, con la pendiente del
    # conducto (0.004) y la longitud que 7.B da con la entrada en el canal
    # (23.79 m: el terraplen es mas alto y la longitud crece), deja la
    # salida 5 mm sobre el fondo del canal: 36.30 - 0.004 · 23.79 = 36.205,
    # dentro de la tolerancia de `desajuste_empalme_canal_m` (0.010 m). El
    # auditor de T-11 probo 36.284 (= 36.20 + 0.004 · 21.0, con la longitud
    # de la entrada en el terreno): la salida quedaba 11 mm BAJO el canal y
    # VC2 seguia avisando.
    "C01_fondo_en_el_canal": (
        "C-01 con la cota de fondo de entrada en el canal (36.30 msnm: la "
        "salida queda a 5 mm sobre el fondo del canal, 36.20) en vez de la "
        "regla de archivo, que la pone en el terreno del cruce",
        (("celda", "C-01", "cota_fondo_entrada", "36.30"),)),
    # El resultado de la tesis que `v_max_concreto_eleccion` = 3.0 m/s da en
    # A-01 (TMC de 1.20 m) depende de otro [A]: con
    # `suelo_agresivo_lrfd_sobre_tmc` = 'excluye' (dentro de su ventana) el
    # TMC sale por los sulfatos del juego (correcciones de T-11, H6).
    "v_max_concreto_3_con_tmc_excluida": (
        "`v_max_concreto_eleccion` = 3.0 m/s (extremo inferior de la Tabla N "
        "10) con `suelo_agresivo_lrfd_sobre_tmc` = 'excluye': el TMC al que "
        "A-01 pasaria queda fuera por los sulfatos del juego",
        (("declarar", "v_max_concreto_eleccion", 3.0),
         ("declarar", "suelo_agresivo_lrfd_sobre_tmc", "excluye"))),
    "caudal_calculado_sin_fen": (
        "La variante `caudal_calculado` sin declarar `homogeneidad_serie_fen`"
        " (el tratamiento de los años FEN que solo el caudal calculado lee)",
        (("csv_caudal_vacio", ("A-01", "A-02", "B-01")),
         ("declarar", "homogeneidad_serie_fen", None))),
}
