"""
constantes_normativas.py
========================
Anexo B de docs/hoja_de_ruta_alcantarillas_v7.md, copiado literalmente.

Solo constantes [N] con numeral verificado. Todo [N->], [C] y [A] vive en
`criterios_adoptados.py`. No agregar aqui ningun valor que no venga con su
numeral: si falta, se declara alla como criterio adoptado, no aqui.

Unidades: SI (m, m3/s, m/s, MPa donde se indica, mm en recubrimientos).

ADVERTENCIA DE DOBLE DEFINICION
-------------------------------
Tres bloques de este anexo tienen un homologo en `criterios_adoptados.py`,
porque la hoja de ruta los incluyo aqui aun siendo [C]:

    D_INICIO / D_PASO / D_MAX   <->  criterio "diametros_normalizados"
    HDS5_INLET                  <->  criterio "hds5_embocadura_hdpe" (HDPE)
    H_RELLENO_MIN               <->  criterio "h_relleno_min_concreto_tmc"

La inconsistencia Clase D/F que motivo la v5 fue exactamente esto: el mismo
parametro definido en dos lugares (Sec. 0.7). Para el CALCULO, la fuente unica
es `criterios_adoptados.py`; lo de aqui queda como referencia trazable del
Anexo B. Ningun modulo debe leer los tres bloques citados desde este archivo.
"""

# ================= Manual de Hidrologia (RD 20-2011-MTC/14) =================
LUZ_MAX_ALCANTARILLA = 6.0          # m; >= 6.0 -> puente (4.1.1.3.1 / 4.1.1.5.1)
DIAMETRO_MIN = 0.90                 # m (4.1.1.3.4 a)
DIAMETRO_MIN_SELVA_ALTA = 1.22      # m = 48"; NO aplica en costa (4.1.1.3.7 a)
Y_SOBRE_D_MAX = 0.75                # borde libre >= 25% (4.1.1.3.7 b)
V_MIN = 0.25                        # m/s (4.1.1.3.6)
LAUSHEY_K = 3.1                     # d50 = V^2/(3.1*g), metrico (4.1.1.3.7 c)
G = 9.8                             # m/s2

RIESGO_ADMISIBLE = {                # Tabla N 02, num. 3.6
    "quebrada_importante": {"R": 0.30, "n": 25},   # -> TR = 71 anios
    "quebrada_menor":      {"R": 0.35, "n": 15},   # -> TR = 35 anios
}
# TR = 1 / (1 - (1-R)**(1/n))       # sin piso normativo

MANNING = {                         # Tabla N 09: (n_min, n_max)
    "metal_corrugado": (0.021, 0.030),
    "concreto_recto":  (0.010, 0.013),
    "madera_duelas":   (0.010, 0.014),
    # HDPE no listado -> criterios_adoptados.valor("n_manning_hdpe")
}
# n_max -> capacidad y tirante ; n_min -> velocidad y socavacion

V_MAX = {                           # Tabla N 10
    "concreto":            (3.0, 6.0),
    "ladrillo_c_concreto": (2.5, 3.5),
    "mamposteria_piedra":  (2.0, 2.0),
    # TMC y HDPE no listados -> criterios_adoptados
}

LONG_MAX_CUNETA = {"seca": 250.0, "muy_lluviosa": 200.0}   # m (4.1.2.1 d)

# ================= HDS-5 (FHWA) 3a ed., abril 2012 =========================
# Apendice A, Tabla A.1, pag. A.8
KU_METRICO = 1.811                  # q* = KU*Q/(A*D**0.5)
Q_LIM_NO_SUMERGIDO = 3.5
Q_LIM_SUMERGIDO    = 4.0            # entre ambos: interpolacion lineal

HDS5_INLET = {   # cartas por forma/material; dentro de cada una, por borde
    "circular_concreto_square_edge_headwall": {"K": 0.0098, "M": 2.00,
                                               "c": 0.0398, "Y": 0.67, "Ks": -0.5},
    "circular_cmp_headwall":                  {"K": 0.0078, "M": 2.00,
                                               "c": 0.0379, "Y": 0.69, "Ks": -0.5},
    "circular_cmp_mitered":                   {"K": 0.0210, "M": 1.33,
                                               "c": 0.0463, "Y": 0.75, "Ks":  0.7},
}
# Ks NO figura en la Tabla A.1: proviene de la formulacion (-0.5 / +0.7). No omitir.
# HDPE -> criterios_adoptados.valor("hds5_embocadura_hdpe")

# ================= Control de salida (SI) ==================================
K_FRICCION_SI = 19.62               # H = (1 + ke + 19.62*n^2*L/R^(4/3)) * V^2/(2g)
                                    # OJO: 29 es el valor ingles.
                                    # TEST UNITARIO OBLIGATORIO.
# ho = max(TW, (yc + D)/2)

# ================= Diametros normalizados (ASTM / AASHTO) ==================
D_PASO = 0.15                       # m; reproduce las series de 6" y 150 mm
D_INICIO = 0.90                     # m; minimo normativo MTC
D_MAX = {                           # topes por norma de producto - VERIFICAR
    "concreto_reforzado": 2.70,     # ASTM C76 / AASHTO M170
    "tmc":                2.10,     # AASHTO M36 / ASTM A760
    "hdpe":               1.50,     # AASHTO M294  <- el mas restrictivo
}
# Sin tope, el solver puede converger a un diametro inexistente.
# Superado el tope: devolver "material descartado por diametro requerido".

# ================= Manual de Suelos (RD 10-2014-MTC/14) ====================
RESGUARDO_NAPA_SUBRASANTE = [       # (CBR_min, CBR_max, resguardo_m)  num. 4.5.4
    (20.0, None, 0.60), (6.0, 20.0, 0.80),
    (3.0, 6.0, 1.00),   (None, 3.0, 1.20),
]
# Su aplicacion al HW es POR ANALOGIA [N->] -> ver criterios_adoptados
CBR_MIN_SUBRASANTE = 6.0            # % (num. 3.3)
COMPACTACION_CORONA = 0.95          # 0.30 m superiores, capas de 0.15 m
COMPACTACION_CUERPO = 0.90          # capas de hasta 0.30 m

CALICATAS_POR_KM = {"autopista": 4, "dual": 4, "primera_clase": 4,
                    "segunda_clase": 3, "tercera_clase": 2, "bajo_volumen": 1}
ESPACIAMIENTO_PERFIL_KM = 4.0       # nivel perfil

# ================= EG-2013, Seccion 500 ====================================
H_RELLENO_MIN = {
    "hdpe":     0.30,               # m, clave a subrasante (508.07/508.08)
    "concreto": None,               # AASHTO M-170M (clases I a V)
    "tmc":      None,               # ASTM A-807 / AASHTO M36
}
SUBSECCION = {"concreto_simple": "505", "concreto_reforzado": "506",
              "tmc": "507", "hdpe": "508"}
SECCION_CABEZALES = "503"           # concreto estructural (+504 acero)

# ================= Manual de Puentes (RD 041-2016-MTC/14) ==================
SOBRECARGA_TRASDOS_H_EQ = 0.60      # m de relleno equivalente (2.1.4.3.9)
CARGA_VIVA = "HL-93"                # (2.4.3.2.2.1)
NQ_ZAPATA_EN_TALUD = 0.0            # (2.8.1.3.1.2c)
F_PGA_TABLA = {                     # Tabla 2.4.3.11.2.1.2-1, PGA >= 0.50
    "C": 1.0, "D": 1.0, "E": 0.9,
}
# PGA, F_pga elegido, factor de muro y k_v -> criterios_adoptados

# ================= E.050 (RM 406-2018-VIVIENDA) ============================
FS = {
    "capacidad_portante": {"estatico": 3.00, "sismico": 2.50},   # Art. 21
    "volteo":             {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "deslizamiento":      {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 a
    "estabilidad_global": {"estatico": 1.50, "sismico": 1.25},   # 39.13.6 b
    "talud":              {"estatico": 1.50, "sismico": 1.25},   # Art. 30.3
}
SPT_PROF_MIN = 15.0                 # m (Art. 38)
SPT_ESPACIAMIENTO = 1.0             # m entre ensayos

# ================= E.060 (durabilidad, excepcion declarada) ================
SULFATOS = [                        # Tabla 4.4: (SO4_min%, SO4_max%, cemento, a/c, f'c_MPa)
    (0.00, 0.10, None,               None, None),
    (0.10, 0.20, "II/IP(MS)/IS(MS)", 0.50, 28),
    (0.20, 2.00, "V",                0.45, 31),
    (2.00, None, "V + puzolana",     0.45, 31),
]
CLORUROS_EXTERNOS = {"a_c_max": 0.40, "fc_min_MPa": 35}   # Art. 4.2 / 4.4
RECUBRIMIENTO = {"contra_suelo": 70, "suelo_intemperie_ge_3_4": 50,
                 "suelo_intemperie_le_5_8": 40}           # Art. 7.7.1

# ================= E.030 (RM 183-2026-VIVIENDA) - solo referencia ==========
ZONA_SISMICA_LA_UNION = 4
Z_E030 = 0.45                       # Tr = 475 anios - NO se usa para el cabezal
PERFIL_SUELO_PRESUNTO = "S5"        # suelos potencialmente licuables (Art. 14.6)
