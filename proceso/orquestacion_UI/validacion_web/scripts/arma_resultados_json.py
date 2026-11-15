import json
W = '/tmp/validacion_web'
filas = json.load(open(f'{W}/resultados_filas.json'))
gui = {c: json.load(open(f'{W}/gui/{c}/recorrido_ventana.json')) for c in ('tdot_ex2', 'hidro', 'wisdot')}
res = {
 'meta': {'programa': '/home/user/val_web', 'commit': '2d37c2c7298aabf1fec8602eddf745fa70994cc2', 'arbol_limpio': True,
          'fecha': '2026-11-15', 'entorno': 'Python 3.12.3, ttkbootstrap 2.2.1, weasyprint 69.0, numpy 2.2.3, scipy 1.15.2, xvfb-run; NORMAS_DIR=/home/user/andy-rba30/normas',
          'conversiones': {'1 ft': '0.3048 m (exacto)', '1 ft3/s': '0.028316846592 m3/s (exacto, 0.3048^3)', '1 in': '0.0254 m',
                           '341.25 ft': '104.013 m', '340.70 ft': '103.84536 m', '345.32 ft': '105.253536 m', '110 ft': '33.528 m', '3 ft (36 in)': '0.9144 m', '1.8 ft': '0.54864 m',
                           '25 cfs': '0.707921 m3/s', '69.2 cfs': '1.959526 m3/s', '90 cfs': '2.548516 m3/s'},
          'alcance_de_las_corridas': 'perfil (hidraulica y verificaciones; Fases 8 y 9 diferidas, sin relacion con lo comparado)'},
 'casos': {
  'TDOT_EX2': {'fuente': 'TDOT Drainage Manual cap. 6, Ej. 2 (HY-8), pp. 6-81 a 6-90', 'dir': f'{W}/casos/TDOT_EX2',
               'variantes': {'base': 'rasante de PRUEBA +1.25 m', 'alt': 'todos los datos de prueba movidos (area, terreno, paquete, CBR, SUCS, luz, altura del cauce, rasante +2.25 m)',
                             'publicada': 'rasante publicada 345.32 ft: el 36 in no pasa V7 (y V4 a 25 cfs) y el punto se detiene en el defecto D1'},
               'declaraciones': f'{W}/casos/TDOT_EX2/declaraciones_base.txt', 'resultado': '10/10 puntos dimensionados en base y alt (concreto 0.9144 m), expediente de perfil cerrado (rc=0)'},
  'TDOT_EX1': {'fuente': 'TDOT cap. 6, Ej. 1 (a mano, nomogramas), pp. 6-73 a 6-80', 'dir': f'{W}/casos/TDOT_EX1', 'resultado': 'dimensionado, control de entrada, rc=0'},
  'TDOT_EX4': {'fuente': 'TDOT cap. 6, Ej. 4 (HY-8), pp. 6-94 a 6-101', 'dir': f'{W}/casos/TDOT_EX4',
               'resultado': 'el 36 in de concreto queda DESCARTADO (V3: V(n_min) > 6 m/s; V4b: HW/D 1.93 > 1.5) en todos los caudales: el HW se lee del escalon descartado. TDOT tambien lo rechaza (rebose). Con la progresion por defecto la app elige TMC 1.20 m'},
  'HIDRO_UPAO_UNC': {'fuente': 'UPAO La Jalca (Gumbel p. 94, Tinas p. 267, cuneta 1 pp. 107-108) y UNC Cocahuayco (Tc, C p. 51, Tabla 15)', 'dir': f'{W}/casos/HIDRO_UPAO_UNC',
                     'resultado': 'TINAS (55.911 km2) detenida: MetodoNoEvaluableError del racional (A >= 10 km2); los demas calculan Q'},
  'UNC_ALC36': {'fuente': 'UNC Cocahuayco pp. 90-91 (metodo de French)', 'dir': f'{W}/casos/UNC_ALC36', 'resultado': 'TMC 0.90 m dimensionado (concreto excluido por V3 declarando v_max_concreto_eleccion=3.0)'},
  'UPAO_MANNING': {'fuente': 'UPAO La Jalca pp. 121-123 (5 de 46 filas)', 'dir': f'{W}/casos/UPAO_MANNING', 'resultado': '2/5 dimensionados; 3 no factibles por V3 (velocidad maxima) en los tres materiales'},
  'OBRA_DALE': {'fuente': 'FHWA-RD-01-095 (obra real, ensayo de modelo)', 'dir': f'{W}/casos/OBRA_DALE', 'resultado': 'no factible (D > 2.70 m, V3); contraste solo cualitativo'},
  'OBRA_WISDOT': {'fuente': 'WisDOT STH 32, proyecto 9190-26(27)-00, reporte HY-8 (9 cruces, 18 caudales)', 'dir': f'{W}/casos/OBRA_WISDOT',
                  'resultado': '12 de 18 escalones con hidraulica: control coincide en 12/12, HW gobernante dentro de +-1 % de HY-8 en los 12 (salida por el remanso de la app incluida); 6 escalones sin hidraulica: con n = 0.013 no existe tirante normal (Q > Q pico) y la app descarta el escalon sin calcular HW; ademas solo C9 pasa todas las verificaciones de la app (V4/V4b/V7 con cotas de prueba)',
                  'contraste': f'{W}/casos/OBRA_WISDOT/contraste.json'},
  'OBRA_TU107': {'fuente': 'Tesis UNTumbes 2026, via TU-107 Bocapan-Tamarindo: 41 cuencas, serie Canaveral', 'dir': f'{W}/casos/OBRA_TU107',
                 'resultado': '34 de 41 cuencas con Q calculado; 5 detenidas por A >= 10 km2 (la tesis tambien cambia de metodo) y 2 por Tc de Temez < 0.25 h (C-20, C-27; la tesis lo aplica fuera de rango). P24 LN2P y K-S identicos a la tesis sin el 1.13; Tc Temez dentro de +-5 %; I y Q por Dick-Peschke ~1.5-2.4 veces los de la tesis; con la Tabla N 04 (solo Tc >= 1 h, 6 cuencas) de -0.3 % a -9.8 %. La app ajusta la serie sospechosa (729 mm/24 h, filas repetidas) sin avisar de su magnitud',
                 'contraste': f'{W}/casos/OBRA_TU107/contraste.json',
                 'nota_extraccion': 'en /tmp/ejemplos_web/obras_reales/obras.json las columnas tc_temez_h y tc_bransby_h estan INVERTIDAS respecto del PDF (Tabla 27, pag. 65: 1a columna Bransby-Williams, 2a Temez); se uso la del PDF'},
  'OBRA_TU107_05': {'resultado': 'NO CORRIDA: solo capacidad a seccion llena con Manning, sin HW/ke/L/TW; no hay magnitud HDS-5 que comparar'},
  'OBRA_QUERARI_06': {'resultado': 'NO CORRIDA: puente (Mac-Math, no racional) e inconsistencias internas graves de la fuente (serie 45-185 mm contra P24(T=2) = 36 mm)'},
  'OBRA_MNDOT': {'fuente': 'MnDOT 2021-29', 'resultado': 'NO CORRIDA: cajones multicelda sin HW, cotas ni TW publicados; nada que comparar'}},
 'contraste': filas,
 'invariancia_datos_de_prueba': json.load(open(f'{W}/invariancia.json')),
 'ventana_real': {c: {k: g.get(k) for k in ('examinar', 'campos_pestana_1', 'declaraciones', 'informe', 'segundos_ejecucion', 'json_exportado',
                                         'json_igual_a_la_cli_sin_hora', 'n_diferencias', 'comparador', 'dialogos', 'sesion_guardada')}
                  | {'pestana_3': {p: {kk: vv for kk, vv in v.items() if kk != 'texto'} for p, v in g['pestana_3_detalle'].items()},
                     'cli_desde_la_sesion_de_la_ventana': 'REPRODUCE (mismo JSON sin la hora)'} for c, g in gui.items()},
 'defectos_candidatos': [
  {'id': 'D1', 'titulo': 'La progresion de diametros declarada se redondea a 2 decimales y luego se rechaza a si misma',
   'archivo_linea': '/home/user/val_web/src/modulos/M2_material.py:973 (siguiente = round(inicio + (n + 1) * paso, 2)) y :966 (guardia que lo rechaza)',
   'reproduccion': f'{W}/defectos/D1_progresion_redondeo (repro_minima.py y la corrida CLI de un punto)',
   'efecto': 'con diametros_normalizados = {inicio 0.9144, paso 0.1524} (la serie de 6 in que la propia ficha del criterio cita) el 2o escalon es 1.07 m y no 1.0668 m (pide la fila de espesor 1070 y no 1067) y el 3o levanta DatoInvalidoError «no pertenece a la progresion»: los tres materiales salen «no evaluable» y el punto DisenoNoFactibleError aunque un diametro mayor cumpliria',
   'severidad': 'media (solo con progresion declarada no multiplo de 0.01 m; la de archivo 0.90/0.15 no lo dispara)'},
  {'id': 'D2', 'titulo': 'V7 (flotacion) no lee NF_profundidad_m, y el contrato de entradas dice que si y que sin el dato V7 queda pendiente',
   'archivo_linea': '/home/user/val_web/docs/contrato_entradas.md:71 frente a src/modulos/M5_verificaciones.py:3058 (U = empuje_flotacion_kn_m(...), sin NF) y src/modulos/M8_estructural.py:304',
   'reproduccion': f'{W}/defectos/O2_NF_y_V7 (mismo punto sin NF y con NF = 10 m: V7 identico, U = 9.623 kN/m, y descarta el 36 in)',
   'efecto': 'un NF medido profundo nunca alivia V7; sin NF V7 no queda pendiente sino que se evalua con el conducto sumergido y puede descartar diametros. El calculo es del lado seguro; lo que no cuadra es la documentacion (contrato y texto de ayuda del pre-vuelo) con el codigo',
   'severidad': 'baja (documentacion/coherencia; lado conservador)'}],
}
json.dump(res, open(f'{W}/resultados.json', 'w'), indent=1, ensure_ascii=False)
print('ok', len(filas))
