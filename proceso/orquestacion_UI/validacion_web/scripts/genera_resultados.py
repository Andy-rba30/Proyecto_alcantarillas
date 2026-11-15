"""Genera /tmp/validacion_web/resultados.json y las tablas Markdown del INFORME a partir
de los JSON/memorias que la app escribio (CLI) y del recalculo a mano independiente."""
import json, sys, math
sys.path.insert(0, '/tmp/validacion_web/scripts')
from conv import FT, a_ft
from memoria_txt import texto
import re
W = '/tmp/validacion_web'
EJ = {e['id']: e for e in json.load(open('/tmp/ejemplos_web/ejemplos.json'))}
MANO = json.load(open(f'{W}/recalculo_mano.json'))
filas = []
def fila(ejemplo, magnitud, pub, app, unidad, tol_pct, metodo_fuente, clasif='', causa='', mano=None, nota=''):
    d = None if (pub is None or app is None) else 100 * (app - pub) / pub
    if d is None: ver = 'no comparable'
    elif abs(d) <= tol_pct: ver = 'dentro de tolerancia'
    else: ver = 'FUERA de tolerancia'
    filas.append(dict(ejemplo=ejemplo, magnitud=magnitud, unidad=unidad, publicado=pub, app=app,
                      diferencia_pct=None if d is None else round(d, 2), tolerancia_pct=tol_pct,
                      metodo_fuente=metodo_fuente, veredicto=ver, clasificacion=clasif if ver != 'dentro de tolerancia' else (clasif or '-'),
                      causa=causa, recalculo_mano=mano, nota=nota))
# ---------------- TDOT EX2 ----------------
cj = json.load(open(f'{W}/casos/TDOT_EX2/base/salida/cli.informe.json'))
pts = {p['id']: p['diseno'] for p in cj['puntos']}
for f in EJ['TDOT-EX2-circ-HY8']['resultados_publicados']['tabla_por_caudal']:
    pid = f"Q{f['Q_cfs']:04.1f}cfs".replace('.', 'p'); a = pts[pid]; q = f['Q_cfs']
    e = f'TDOT-EX2 Q={q:g} cfs'
    fila(e, 'HW control de entrada (sobre invert)', f['HW_inlet_ctrl_depth_ft'], a_ft(a['HW_entrada_m']), 'ft', 3, 'HY-8',
         '(c) metodo' if abs(a_ft(a['HW_entrada_m']) / f['HW_inlet_ctrl_depth_ft'] - 1) > 0.005 else '',
         'HY-8 ajusta polinomios a los nomogramas; la app usa las ecuaciones del Apendice A de HDS-5 3a ed.',
         mano=(f"HDS-5 Forma 1 a mano: {MANO['EX2_Q25_HW_entrada_HDS5_ft'][0]:.3f} ft" if q == 25 else None))
    fila(e, 'control gobernante', None, None, '-', 0, 'HY-8', '', f"HY-8: tipo 1-S2n (entrada); app: {a['control_gobernante']}")
    filas[-1]['publicado'] = 'entrada (1-S2n)'; filas[-1]['app'] = a['control_gobernante']; filas[-1]['veredicto'] = 'coincide' if a['control_gobernante'] == 'entrada' else 'NO coincide'
    for mag, pubv, appv in (('tirante normal (n=0.013)', f['normal_ft'], a_ft(a['y_normal_m'])),
                            ('tirante critico', f['critico_ft'], a_ft(a['y_critico_m'])),
                            ('TW (Manning en el cauce trapezoidal)', f['TW_ft'], a_ft(a['TW_m'])),
                            ('tirante a la salida', f['profundidad_salida_ft'], a_ft(a['y_salida_m'])),
                            ('velocidad de salida (app: V con n_max=0.013)', f['V_salida_fps'], a['V_sedimentacion_m_s'] / FT)):
        cl, ca_, mn = '', '', None
        if q == 2.5 and mag.startswith('tirante normal'):
            cl = '(b) fuente'; ca_ = 'el tirante normal de HY-8 no satisface Manning con sus propios datos'
            mn = f"Manning a mano D=3 ft, n=0.013, S=0.005: yn={MANO['EX2_Q2.5_yn_n0.013_ft']:.3f} ft; el 0.444 de HY-8 da Q={MANO['EX2_Q2.5_Q_que_da_yn_HY8_0.444_ft']:.3f} cfs, no 2.5"
        if q == 2.5 and mag.startswith('tirante critico'):
            cl = '(b) fuente'; ca_ = 'el critico de HY-8 no satisface Q^2/g = A^3/T'
            mn = f"critico exacto a mano: {MANO['EX2_Q2.5_yc_exacto_ft']:.3f} ft; el 0.470 de HY-8 corresponde a Q={MANO['EX2_Q2.5_Q_que_da_yc_HY8_0.470_ft']:.3f} cfs"
        fila(e, mag, pubv, appv, 'ft' if 'velocidad' not in mag else 'ft/s', 3, 'HY-8', cl, ca_, mn)
    fila(e, 'velocidad de salida que usa la proteccion (n_min=0.010)', f['V_salida_fps'], a['V_salida_m_s'] / FT, 'ft/s', 3, 'HY-8',
         '(c) metodo', 'regla de doble n del programa: V_salida = V(n_min) sobre la geometria de n_max (modelos.TiranteNormal; HDS-5 3.3.2 con el techo conservador); V_salida/V_HY8 = n_max/n_min = 1.30',
         mano='0.013/0.010 = 1.30 = cociente medido')
# ---------------- TDOT EX1 ----------------
d1 = json.load(open(f'{W}/casos/TDOT_EX1/base/salida/cli.informe.json'))['puntos'][0]['diseno']
HWo = d1['perfil_HW_aproximado_m']; H = HWo - d1['h_o_m'] + 0.005 * 33.528
e = 'TDOT-EX1 Q=25 cfs (a mano)'
fila(e, 'HW control de entrada', 2.37, a_ft(d1['HW_entrada_m']), 'ft', 5, 'nomograma HDS-5 (lectura HW/D=0.79)', '', '', mano=f"{MANO['EX2_Q25_HW_entrada_HDS5_ft'][0]:.3f} ft (ec. HDS-5)")
fila(e, 'd_c', 1.61, a_ft(d1['y_critico_m']), 'ft', 2, 'Tabla 6A-7', '', '', mano=f"{MANO['EX2_Q25_yc_ft']:.3f} ft")
fila(e, 'h_o = max(TW, (dc+D)/2)', 2.3, a_ft(d1['h_o_m']), 'ft', 2, 'a mano', '', '', mano=f"{MANO['EX1_ho_ft']:.3f} ft")
fila(e, 'H (perdidas, n real y L real)', 0.45, a_ft(H), 'ft', 5, 'nomograma (n=0.012, L ajustada)', '', 'la app usa n=0.013 y L=110 ft (HDS-5 3a ed.); TDOT ajusta L por n', mano=f"{MANO['EX1_H_ft']:.3f} ft")
fila(e, 'HW control de salida (aproximacion H+ho-SL)', 343.45 - 341.25, a_ft(HWo), 'ft', 5, 'a mano', '', 'la app la calcula y la descarta (HW/D<0.75, HDS-5 3.3.3): rige el perfil, que no alcanza la entrada; mismo control final', mano=f"{MANO['EX1_HWo_ft']:.3f} ft")
fila(e, 'tirante normal a la salida do', 1.55, a_ft(d1['y_normal_m']), 'ft', 2, 'Tabla 6A-11', '', '', mano=f"{MANO['EX2_Q25_yn_ft']:.3f} ft")
fila(e, 'velocidad de salida (app: V con n_max)', 6.78, d1['V_sedimentacion_m_s'] / FT, 'ft/s', 2, 'a mano', '', '', mano=f"{MANO['EX1_V_salida_normal_ft_s']:.3f} ft/s")
fila(e, 'control gobernante', None, None, '-', 0, 'a mano'); filas[-1].update(publicado='entrada', app=d1['control_gobernante'], veredicto='coincide' if d1['control_gobernante'] == 'entrada' else 'NO coincide')
# ---------------- TDOT EX4 ----------------
t = texto(f'{W}/casos/TDOT_EX4/base/salida/memoria.html')
res = re.findall(r'Resultado (HW_entrada|y_c|y_normal|V_sedimentacion|TW) = (-?[0-9.]+)', t)
blocks = []; cur = {}
for k, v in res:
    if k in cur: blocks.append(cur); cur = {}
    cur[k] = float(v)
blocks.append(cur)
j4 = json.load(open(f'{W}/casos/TDOT_EX4/base/salida/cli.informe.json'))
hwd = {p['id']: float(p['iteraciones'][0]['motivo'].rsplit('obtenido', 1)[1].split('frente')[0]) for p in j4['puntos']}
tw = {p['id']: p['datos_declarados']['TW_m']['valor'] for p in j4['puntos']}
e = 'TDOT-EX4 (S=3 %, entrada cuadrada)'
fila(e + ' Q=69.2 cfs', 'HW control de entrada (rebose: 347.00-341.25)', 5.75, hwd['EX4-Q69p2'] * 3.0, 'ft', 3, 'HY-8 (caudal de inicio del rebose, «about 69.2 cfs»)', '', 'el 36 in queda descartado por la app (V3 y V4b); el HW se lee del escalon descartado (motivo V4b y memoria)', mano=f"{MANO['EX4_Q69.2_HW_entrada_ft'][0]:.3f} ft (HDS-5 sumergida)")
fila(e + ' Q=72 cfs', 'TW (Tabla 3 de HY-8)', 1.81, a_ft(tw['EX4-Q72']), 'ft', 3, 'HY-8')
fila(e + ' Q=90 cfs', 'TW', 2.005, a_ft(tw['EX4-Q90']), 'ft', 3, 'HY-8')
b90 = blocks[2]
fila(e + ' Q=90 cfs', 'tirante critico', 2.967, a_ft(b90['y_c']), 'ft', 3, 'HY-8', '(b) fuente', 'HY-8 se desvia del critico exacto cuando dc/D -> 1', mano=f"critico exacto a mano: {MANO['EX4_Q90_yc_exacto_ft']:.3f} ft")
fila(e + ' Q=90 cfs', 'tirante normal', 1.883, a_ft(b90['y_normal']), 'ft', 3, 'HY-8 (corrida slope-tapered, n=0.012)', '(c) norma', 'HY-8 usa n=0.012; la app el n_max de la Tabla N 09 del Manual (0.013)', mano=f"Manning a mano: n=0.012 -> {MANO['EX4_Q90_yn_n0.012_ft']:.3f} ft; n=0.013 -> {MANO['EX4_Q90_yn_n0.013_ft']:.3f} ft")
fila(e + ' Q=90 cfs', 'velocidad de salida (app: V con n_max)', 17.29, b90['V_sedimentacion'] / FT, 'ft/s', 3, 'HY-8', '(c) metodo', 'la app toma la velocidad al tirante normal (HDS-5 3.3.2, pag. 3.24) y n=0.013; HY-8 calcula la curva S2 (tirante 2.072 ft > normal en 110 ft)', mano=f"a mano: V(yn, n=0.013)={MANO['EX4_Q90_V_normal_n0.013_ft_s']:.2f} ft/s; V(2.072 ft)={MANO['EX4_Q90_V_a_2.072ft_HY8_ft_s']:.2f} ft/s")
# ---------------- HIDROLOGIA ----------------
def caud(r):
    return {p['id']: (p['caudal'] or {}, p) for p in json.load(open(r))['puntos']}
h1 = caud(f'{W}/casos/HIDRO_UPAO_UNC/base/salida/cli_TR100_50.informe.json')
h5 = caud(f'{W}/casos/HIDRO_UPAO_UNC/base/salida/cli_TR500_100.informe.json')
g = EJ['UPAO-JALCA-Gumbel-Pd']['resultados_publicados']['XT_prima_mm']
fila('UPAO Gumbel (serie 17 anios)', "P24(TR=50) X'T", g['50'], h1['UNC-A2'][0]['P24_TR_mm'], 'mm', 0.5, 'Gumbel momentos', '', '', mano=f"{MANO['UPAO_XT_50']:.4f}")
fila('UPAO Gumbel (serie 17 anios)', "P24(TR=100) X'T", g['100'], h1['TINAS-T-DIAG'][0]['P24_TR_mm'], 'mm', 0.5, 'Gumbel momentos', '', '', mano=f"{MANO['UPAO_XT_100']:.4f}")
fila('UPAO Gumbel (serie 17 anios)', "P24(TR=500) X'T", g['500'], h5['TINAS-T-DIAG'][0]['P24_TR_mm'], 'mm', 0.5, 'Gumbel momentos', '', '', mano=f"{MANO['UPAO_XT_500']:.4f}")
fila('UPAO Gumbel (serie 17 anios)', 'P24(TR=100) con factor 1.13 (XT)', 69.48, h1['TINAS-T-DIAG'][0]['P24_TR_mm'], 'mm', 0.5, 'Gumbel x 1.13 (intervalo fijo)', '(c) metodo', 'la app no aplica el factor 1.13: el Manual de Hidrologia del MTC no lo trae (buscado en el PDF: ninguna ocurrencia de «1.13» ni de «intervalo fijo»)', mano='61.489 x 1.13 = 69.48')
fila('UPAO Tinas (Temez)', 'Tc Temez', 3.95, h1['TINAS-T-DIAG'][0]['tc_min'] / 60, 'h', 1, 'ec. (30) del Manual', '', 'leido en la fila de DIAGNOSTICO (area de prueba 9.5 km2; Tc no depende del area)', mano=f"{MANO['UPAO_Tinas_Tc_temez_h']:.4f} h")
fila('UPAO Tinas (Temez)', 'K uniformidad', 1.28, h1['TINAS-T-DIAG'][0]['K_uniformidad'], '-', 1, 'ec. (31)', '', '', mano=f"{MANO['UPAO_Tinas_K']:.4f}")
fila('UPAO Tinas (Temez)', 'I de diseno', 11.51, h1['TINAS-T-DIAG'][0]['I_mm_h'], 'mm/h', 3, 'ec. (32)-(34) del Manual (KA, P corregida, I de Temez con 11) y P24 x 1.13', '(c) metodo',
     'la app usa Dick-Peschke sobre P24 sin 1.13 y sin KA (uso hibrido declarado, ficha T1-08); la tesis el metodo racional modificado completo',
     mano=f"ec. 34 a mano: {MANO['UPAO_Tinas_I_temez_ec34']:.3f} mm/h (reproduce la tesis); Dick-Peschke a mano con P24=61.49: {MANO['UPAO_Tinas_I_dick_peschke_sin_1.13']:.3f} (= app)")
fila('UPAO Tinas (Temez)', 'C', 0.32, None, '-', 0, 'ec. (35) con CN=72', '(c) metodo', 'la app toma C de la Tabla N 08 (cobertura/suelo/pendiente, no publicados por la tesis): no se compara', mano=f"ec. 35 a mano: {MANO['UPAO_Tinas_C_ec35']:.4f}")
c = h1['TINAS'][1]
fila('UPAO Tinas (Temez)', 'Q de diseno (area real 55.911 km2)', 74.03, None, 'm3/s', 0, 'racional modificado', '(c) metodo / alcance',
     'la app se DETIENE: MetodoNoEvaluableError «el Manual situa el metodo racional en cuencas de area menor de 10 km2 (num. 3.12.2) y la cuenca tiene 55.911 km2»; el racional modificado (valido hasta 770 km2, num. 3.12.2.1) no esta implementado (ficha T1-08)')
filas[-1]['app'] = 'detenida (MetodoNoEvaluableError)'
fila('UPAO Tinas (Kirpich)', 'Tc Kirpich', 93.07, h1['TINAS-K-DIAG'][0]['tc_min'], 'min', 1, 'Kirpich', '', 'fila de diagnostico', mano=f"{MANO['UPAO_Tinas_Tc_kirpich_min']:.3f} min")
fila('UPAO cuneta 1 (Kirpich)', 'Tc Kirpich', 1.05, h1['CUNETA1'][0]['tc_min'], 'min', 1, 'Kirpich', '', '', mano=f"{MANO['UPAO_cuneta1_Tc_kirpich_min']:.4f} min")
fila('UPAO cuneta 1 (Kirpich)', 'I de diseno', 109.84, h1['CUNETA1'][0]['I_mm_h'], 'mm/h', 3, 'IDF propia K T^m/t^n con TR=10 y t=1.05 min', '(c) norma / metodo',
     'TR=10 no se puede: la Tabla N 02 da como minimo TR 35 en cunetas (R=0.35, n=15) y la app solo deja endurecerlo; ademas la app aplica la duracion minima de 5 min [C] y Dick-Peschke, no la IDF de la tesis')
for pid, nom, tc_pub_min in (('UNC-CAJ', 'Cajahuache', 97.75), ('UNC-A1', 'A1', 38.23), ('UNC-A2', 'A2', 34.35)):
    fila(f'UNC Cocahuayco {nom}', 'Tc Temez', tc_pub_min, h1[pid][0]['tc_min'], 'min', 1, 'Temez', '', '', mano=f"{MANO['UNC_' + nom + '_Tc_temez_h'] * 60:.2f} min")
    fila(f'UNC Cocahuayco {nom}', 'C (Tabla N 08: pastos, semipermeable, pendiente media)', 0.45, h1[pid][0]['C'], '-', 0.5, 'Tabla N 08', '', '')
fila('UNC Cocahuayco A1', 'I de diseno', 39.61, None, 'mm/h', 3, 'IILA zona 17, TR 15', '(b) fuente + (c)', 'la tesis dice I15 = 120.01 mm/h en el texto y usa 39.61 en la Tabla 15; ademas TR 15 e IILA no son el TR de la Tabla N 02 ni la serie de la app (serie de PRUEBA): no comparable')
filas[-1]['nota'] = f"la app, con la serie UPAO de PRUEBA y TR 100, da I = {h1['UNC-A1'][0]['I_mm_h']:.2f} mm/h (no se compara)"
# ---------------- UNC alcantarilla 36 in (French) ----------------
u = {p['id']: p['diseno'] for p in json.load(open(f'{W}/casos/UNC_ALC36/base/salida/cli.informe.json'))['puntos']}
fila('UNC alcantarilla 36 in (TMC)', 'tirante critico yc (Q=0.79)', 0.51, u['UNC36-Q0p79']['y_critico_m'], 'm', 5, 'lectura de grafico (French)', '', 'la app da el critico exacto (0.523 m)')
fila('UNC alcantarilla 36 in (TMC)', 'HW (Y1) a Q=0.80', 0.80, u['UNC36-Q0p80']['HW_entrada_m'], 'm', 10, 'French (orificio con Cd=0.89, flujo tipo 1)', '(c) metodo', 'HDS-5 control de entrada, carta CMP con muro, frente al metodo de French; los dos dan control de entrada (flujo tipo 1)')
# ---------------- UPAO Manning ----------------
m = {p['id']: p for p in json.load(open(f'{W}/casos/UPAO_MANNING/base/salida/cli.informe.json'))['puntos']}
for pid, dp in (('ALC01', '24 in (0.61 m)'), ('ALC13', '24 in'), ('ALC40', '36 in (0.91 m)'), ('ALC44', '36 in'), ('ALC46', '24 in')):
    p = m[pid]; app = (f"{p['diseno']['material']} {p['diseno']['seccion']}" if p['dimensionado'] else 'no factible (V3 en los tres materiales)')
    fila(f'UPAO alcantarilla {pid[3:]}', 'diametro comercial', None, None, '-', 0, 'Manning y/D=0.75, n=0.024, sin verificaciones', '(c) norma', 'minimo de 0.90 m del Manual num. 4.1.1.3.4 a) adoptado sin condicion; V3 (Tabla N 10) con n_min; pendiente del conducto acotada a 10 % [A] (la tesis publica S de 0.21 a 0.39 sin unidad: (b) fuente)')
    filas[-1].update(publicado=dp, app=app, veredicto='difiere')
# ---------------- Obra real Dale ----------------
t = texto(f'{W}/casos/OBRA_DALE/salida/memoria_solo_concreto.html')
hw = [float(x) for x in re.findall(r'Resultado HW_entrada = ([0-9.]+)', t)]
fila('OBRA REAL Dale Blvd Q=1000 cfs', 'HW (energia, sobre invert de entrada)', 231.16 - 218.93, a_ft(hw[0]), 'ft', 10, 'ensayo de modelo fisico 1:12', '(c) configuracion', 'dos diametros en serie y entrada acampanada a 45 grados: fuera de HDS-5 y de la app; la app (concreto, borde cuadrado, solo el tubo de 9.5 ft) ademas lo descarta por D > 2.70 m (V9) y V3')
fila('OBRA REAL Dale Blvd Q=1500 cfs', 'HW (energia, sobre invert de entrada)', 237.33 - 218.93, a_ft(hw[1]), 'ft', 10, 'ensayo de modelo fisico 1:12', '(c) configuracion', 'idem')

# ---------------- OBRA REAL WisDOT STH 32 (HY-8) ----------------
wi = json.load(open(f'{W}/casos/OBRA_WISDOT/contraste.json'))
for f in wi:
    H, Ap, M = f['HY8'], f['app'], f['mano']; e = f"OBRA REAL WisDOT {f['id']} (Q={f['Q_cfs']:g} cfs, D={f['D_ft']} ft)"
    if Ap['HWi'] is None:
        fila(e, 'HW gobernante', H['HW_gob'], None, 'ft', 3, 'HY-8 (n=0.012)', '(c) norma',
             'la app descarta el escalon SIN hidraulica: «no transporta Q en flujo libre con n = 0.013» (con el n_max de la Tabla N 09 no existe tirante normal: Q > Q pico de la seccion parcial); HY-8 corre con n = 0.012',
             mano=f"tirante normal a mano con n=0.013: {'no existe' if M['yn_n0013_ft'] is None else round(M['yn_n0013_ft'],3)}; con n=0.012: {'no existe' if M['yn_n0012_ft'] is None else round(M['yn_n0012_ft'],3)} ft; HW entrada HDS-5 a mano {M['HW_entrada_HDS5_ft']:.3f} ft")
        filas[-1]['app'] = 'sin hidraulica (no transporta Q en flujo libre con n=0.013)'
        continue
    fila(e, 'control gobernante', None, None, '-', 0, 'HY-8'); filas[-1].update(publicado=f"{H['control']} ({H['tipo']})", app=Ap['control'], veredicto='coincide' if Ap['control'] == H['control'] else 'NO coincide')
    fila(e, 'HW control de entrada', H['HWi'], Ap['HWi'], 'ft', 3, 'HY-8', '', '', mano=f"{M['HW_entrada_HDS5_ft']:.3f} ft ({M['regimen']})")
    fila(e, 'HW gobernante (sobre invert)', H['HW_gob'], Ap['HW_gob'], 'ft', 3, 'HY-8', '',
         'bajo control de salida la app usa el remanso (HDS-5 3.3.3: HW/D < 1.2) con n=0.013' if Ap['control'] == 'salida' else '',
         mano=(f"aproximacion H+ho-SL a mano: n=0.012 {M['HWo_aprox_n0012_ft']:.3f}, n=0.013 {M['HWo_aprox_n0013_ft']:.3f} ft" if Ap['control'] == 'salida' else None))
    fila(e, 'tirante critico', H['yc'], Ap['yc'], 'ft', 3, 'HY-8', '', '', mano=f"{M['yc_ft']:.3f} ft")
    fila(e, 'tirante normal', H['yn'], Ap['yn'], 'ft', 3, 'HY-8 (n=0.012)', '(c) norma', 'la app usa n_max = 0.013 de la Tabla N 09 (no declarable); HY-8 n = 0.012',
         mano=f"Manning a mano n=0.012: {M['yn_n0012_ft']:.3f} ft; n=0.013: {M['yn_n0013_ft']:.3f} ft")
    tw_rel = H['TW'] + ({'WI-C2-Qd': 0.40, 'WI-C2-Qm': 0.40}.get(f['id'], 0.0))
    fila(e, 'TW (sobre el invert de SALIDA)', tw_rel, Ap['TW'], 'ft', 3, 'HY-8 (profundidad en el canal + desnivel canal-salida)', '', 'C2: el canal esta 0.40 ft sobre el invert de salida; HY-8 da la profundidad en el canal, la app la referida al fondo de la salida' if f['id'].startswith('WI-C2') else '')
    fila(e, 'velocidad de salida', H['V'], Ap['V_salida'], 'ft/s', 3, 'HY-8', '(c) metodo' if Ap['control'] == 'entrada' else '',
         'bajo control de ENTRADA la app da V al tirante normal con n_min (techo conservador) y HY-8 al tirante de la curva S2' if Ap['control'] == 'entrada' else 'bajo control de salida ambos usan Q/A(yc)')
# ---------------- OBRA REAL TU-107 (Tumbes) ----------------
tu = json.load(open(f'{W}/casos/OBRA_TU107/contraste.json'))
M7 = tu['mano']
fila('OBRA REAL TU-107 (serie Canaveral, LN2P)', 'P24(T=35) sin factor', M7['P24_T35_publicados_log10'], tu['P24_app']['T35'], 'mm', 0.5, 'Log Normal 2P (media/desv log10 publicadas 2.117/0.389)', '', '', mano=f"de la serie: {M7['P24_T35_serie']:.2f} mm")
fila('OBRA REAL TU-107 (serie Canaveral, LN2P)', 'P24(T=35) con factor 1.13 (el de la tesis)', 1.13 * M7['P24_T35_publicados_log10'], tu['P24_app']['T35'], 'mm', 0.5, 'LN2P x 1.13', '(c) metodo', 'la app no aplica el factor 1.13 (no esta en el Manual)')
fila('OBRA REAL TU-107 (serie Canaveral, LN2P)', 'K-S Delta de la LN2P', 0.0535, [k for k in tu['KS_app'] if k[0] == 'lognormal_2p'][0][1], '-', 1, 'K-S', '', '')
fila('OBRA REAL TU-107 (serie Canaveral, LN2P)', 'P24(T=71) / tesis T=70 sin 1.13', M7['P24_T70_publicados_log10'], tu['P24_app']['T71'], 'mm', 1, 'LN2P', '(c) redondeo de TR', 'TR = 1/(1-(0.7)^(1/25)) = 70.59: la tesis lo TRUNCA a 70, la app lo REDONDEA a 71 (M1)', mano=f"T=71: {M7['P24_T71_serie']:.2f} mm")
for f in tu['filas']:
    e = f"OBRA REAL TU-107 {f['cuenca']} (A={f['A']} km2)"
    if f['bloqueo']:
        fila(e, 'Q de diseno', f['Q_tesis'], None, 'm3/s', 0, 'racional (A<10) o hidrograma unitario (A>10)', '(c) norma/alcance',
             f['bloqueo'][0])
        filas[-1].update(app='detenida (MetodoNoEvaluableError)', veredicto='no comparable')
        continue
    fila(e, 'Tc Temez', f['Tc_temez_pdf_h'], f['Tc_app_h'], 'h', 5, 'Temez (Tabla 27, 2a columna; S con 2 decimales)', '(b) fuente (redondeo de S)' if abs(f['Tc_app_h'] / f['Tc_temez_pdf_h'] - 1) > 0.05 else '', 'S publicada con 2 decimales; la tesis calculo con S de las cotas',
         mano=f"S publicada: {f['Tc_mano_S_publicada_h']:.3f} h; S = (cota max - cota min)/L: {f['Tc_mano_S_de_cotas_h']:.3f} h")
    fila(e, 'C (fila inferida de la Tabla N 08)', f['C_tesis'], f['C_app'], '-', 0.5, 'Tabla N 08', '', 'no es contraste independiente: la fila se infirio de las C publicadas')
    col = str(f['TR_tesis'])
    fila(e, f'I (TR {col}) app Dick-Peschke', f['I_tesis'], f['I_app_DP'], 'mm/h', 3, 'IDF propia I = 408.81 T^0.391 / t^0.5375 (Tabla 04 + regresion + 1.13)', '(c) metodo',
         'Dick-Peschke (valor de archivo de relacion_intensidad_duracion) da casi el doble que la Tabla N 04 en duraciones cortas; ademas sin 1.13 y con Tc de Temez solo (la tesis promedia Temez y Bransby-Williams)',
         mano=f"IDF de la tesis a mano: {f['I_mano_IDF_tesis']:.1f} mm/h (la fuente cuadra consigo misma)")
    fila(e, f'Q (TR {col}) app Dick-Peschke', f['Q_tesis'], f['Q_app_DP'], 'm3/s', 3, 'Q = C I A / 3.6', '(c) metodo', 'arrastra la I')
    if f['I_app_T04'] is not None:
        fila(e, f'I (TR {col}) app Tabla N 04', f['I_tesis'], f['I_app_T04'], 'mm/h', 3, 'IDF propia', '(c) metodo' if abs(f['I_app_T04'] / f['I_tesis'] - 1) > 0.03 else '',
             'misma relacion (Tabla N 04) pero la tesis multiplica por 1.13 y suaviza con su regresion potencial; TR 70 vs 71')
        fila(e, f'Q (TR {col}) app Tabla N 04', f['Q_tesis'], f['Q_app_T04'], 'm3/s', 3, 'Q = C I A / 3.6', '(c) metodo' if abs(f['Q_app_T04'] / f['Q_tesis'] - 1) > 0.03 else '', 'arrastra la I')

json.dump(filas, open(f'{W}/resultados_filas.json', 'w'), indent=1, ensure_ascii=False)
def fmt(x):
    if x is None: return '—'
    if isinstance(x, float): return f'{x:.4g}' if abs(x) < 1000 else f'{x:.1f}'
    return str(x)
lin = ['| Ejemplo | Magnitud | Unid. | Publicado | App | Dif. % | Tol. % | Veredicto | Clasif. | Causa / recalculo a mano |', '|---|---|---|---|---|---|---|---|---|---|']
for f in filas:
    causa = '; '.join(x for x in (f['causa'], ('a mano: ' + f['recalculo_mano']) if f['recalculo_mano'] else '') if x)
    lin.append(f"| {f['ejemplo']} | {f['magnitud']} | {f['unidad']} | {fmt(f['publicado'])} | {fmt(f['app'])} | {fmt(f['diferencia_pct'])} | {f['tolerancia_pct']} | {f['veredicto']} | {f['clasificacion'] or '-'} | {causa} |")
open(f'{W}/tabla_contraste.md', 'w').write('\n'.join(lin) + '\n')
print(len(filas), 'filas;', sum(1 for f in filas if f['veredicto'] == 'FUERA de tolerancia'), 'fuera de tolerancia')
for f in filas:
    if f['veredicto'] == 'FUERA de tolerancia': print('  ', f['ejemplo'], f['magnitud'], f['diferencia_pct'], f['clasificacion'])
