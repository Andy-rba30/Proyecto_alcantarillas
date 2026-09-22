"""
tests/test_ext11_mutacion.py
============================
La mutacion MEDIDA de EXT-11 (propuesta 4 del dictamen): el arnes
`tests/apoyo/mutacion.py` probandose a si mismo, y el CENSO de los mutantes
que sobreviven a toda la suite objetivo con la razon de cada uno, anclado
al codigo para que no se vuelva una lista muerta.

Como se midio (2026-09-21, sobre el arbol de EXT-11, en serie con tres
trabajadores; `python3 -m tests.apoyo.mutacion --segunda-vuelta`):

  679 mutantes en 6 modulos (M3, M4, M5, MD enteros; `_par_de_manning`,
  `numero_de_celdas`, `catalogo`, `n_manning_hdpe` y `_fila_manning_de_cajon`
  de M2; las tres propiedades del par de n de `Material`).
  PRIMERA VUELTA (los diez `OBJETIVOS`, ~2 s por mutante): 568/679 muertos,
  score 0.8365. SEGUNDA VUELTA (linea base, cierre de perfil, CLI) sobre los
  111 vivos: 65 mueren, 46 sobreviven a todo; tres mas murieron con la
  segunda tanda de «Lo que la MUTACION enseño» (remedidos funcion por
  funcion con el arnes): 43 censados abajo (42 desde E-A, que retiro la
  entrada de `_exigir_regimen_evaluable` al desaparecer la funcion).
  E-A (2026-09-21) REMIDIO con `--funcion` las once funciones del perfil
  de la lamina (M4: perfil_lamina, _pendiente_friccion,
  _pendiente_friccion_llena, _llenado_de_tirante,
  _llenado_donde_Sf_iguala_S, _energia_especifica, hw_gobernante,
  resolver_control; M5: _regimen_de_v1_v2, v1_borde_libre,
  v2_velocidad_minima), con `tests/test_ea_perfil_lamina.py` sumado a
  los OBJETIVOS: 242 mutantes, 212 muertos en la primera vuelta (score
  0.876), 5 mas en la segunda, 25 vivos; uno era un hueco real
  (`V_entrada_m_s` del retorno UNIFORME) y se cerro con una asercion en
  el dorado de flujo uniforme; los otros 24 son los cuatro ya censados
  (hw_gobernante x2, V1, V2) y 20 nuevos: 62 censados en total.
  SIN `tests/test_ext11_propiedades.py` (los otros nueve objetivos, misma
  corrida): 504/679, score 0.7423. Sesenta y cuatro mutantes mueren SOLO por
  las propiedades y sus tandas: el receptor trapecial de la Sec. 1.3 (31:
  `tirante_normal_trapecial`, `caudal_manning_trapecial`, `area_` y
  `perimetro_trapecial`, `tw_seccion_1_3`), V3 y su paso (11), la
  progresion del catalogo (`_mismo_escalon`, 4), `_regimen` (2), el par de
  Manning (2) y las guardias de entrada. Sin las propiedades ni esas tandas,
  sobre los ocho objetivos que existian antes de EXT-11, la medida inicial
  fue 489/679 (0.7202).

Que es un superviviente CON RAZON. De cada mutante que sobrevive a las dos
vueltas se dice por que, y las razones son de cinco clases:

  equivalente   el mutante produce el mismo programa: `<=` frente a `<`
                cuando la banda TOL_UMBRAL_NORMATIVO ya cubre la igualdad,
                una guardia que el codigo anterior hace inalcanzable, un
                `return None` donde solo se lee la falsedad, un argumento
                por defecto que nadie usa;
  banda         el signo o el sentido de la banda TOL_UMBRAL_NORMATIVO (1e-9):
                el mutante solo se distingue con un valor a menos de 2·TOL
                del umbral. La banda existe para que la igualdad en punto
                flotante cuente como cumplimiento; donde el umbral es un
                escalar de entrada (V1, V2, V3, V9, el CBR) el test P8 fija
                la lectura inclusiva, y donde exige cotas o pesos al pelo
                (V4, V4b, VC1, V7, el regimen del barril) no se fijo;
  borde         una desigualdad estricta de la FUENTE en su valor exacto
                (HW/D = 0.75 de HDS-5 pag. 3.24): el caso es de medida
                nula y construirlo exige invertir el control de salida;
  memoria       solo cambia el TEXTO de un paso de memoria, no un numero.
                Ninguna entrada de hoy es de esta clase: las que lo
                parecian eran numeros y se cerraron con tests;
  fuera         el camino no lo recorre ningun test ni la linea base porque
                el expediente no puede llegar a el todavia (`M5.verificar`
                entero: V5 vacia), y esta escrito donde se prueba;
  hueco         un hueco REAL de la suite: no queda ninguno, porque cada
                hueco que la mutacion encontro se cerro con un test en
                `tests/test_ext11_propiedades.py` («Lo que la MUTACION
                enseño», dos tandas) y se remidio con el arnes.

El censo se comprueba en las dos direcciones: cada entrada tiene que seguir
siendo un mutante que `generar` produce sobre el codigo de hoy (anclaje por
modulo, funcion, operador y fragmento), y NO se comprueba aqui que siga
sobreviviendo --- eso cuesta minutos y se mide con el arnes; lo que se fija
es que la lista describa codigo que existe.
"""

import ast
import textwrap
from pathlib import Path

import pytest

from tests.apoyo import mutacion

RAIZ = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# El censo: (modulo, funcion, operador, original -> mutado): razon
# ---------------------------------------------------------------------------
SUPERVIVIENTES_CON_RAZON = {
    "src/modulos/M3_hidraulica.py::tirante_normal::booleano::f_min > 0 or f_max < 0 -> f_min > 0 and f_max < 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::comparacion::f_min > 0 -> f_min >= 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::comparacion::f_max < 0 -> f_max <= 0":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal::constante::0 -> 1":
        "equivalente: la guardia del corchete es inalcanzable tras `not Q < Q_lleno` (PC-06): con 0 < Q < Q_lleno, f(min) < 0 y f(max) > 0 siempre; se conserva como defensa de Brent",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::1.0 -> 2.0":
        "equivalente: semilla y factor de duplicacion del corchete; cualquier valor > 0 encuentra la misma raiz (Brent con el mismo xtol)",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::comparacion::f(y_hi) > 0 -> f(y_hi) >= 0":
        "equivalente: `f(y_hi) >= 0` frente a `> 0` difiere solo si el corchete cae EXACTAMENTE en la raiz, de medida nula",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::2 -> 3":
        "equivalente: semilla y factor de duplicacion del corchete; cualquier valor > 0 encuentra la misma raiz (Brent con el mismo xtol)",
    "src/modulos/M3_hidraulica.py::tirante_normal_trapecial::constante::0 -> 1 #2":
        "equivalente: `f(y_hi) > 1` en vez de `> 0` solo duplica el corchete una vez mas antes de Brent; la raiz es la misma",
    "src/modulos/M3_hidraulica.py::tw_seccion_1_3::aritmetico::cota_fondo_salida + gobernante -> cota_fondo_salida - gobernante #2":
        "equivalente: es el `cota_agua` que la via de escenarios pasa a `_paso_tw`, y ese argumento no llega a ningun campo del paso por esa via (la cota que si se publica, `cota_TW_msnm`, la fija test_la_cota_de_agua_del_TW...)",
    "src/modulos/M4_control.py::_resolver_hw_fuera_de_rango::comparacion::HW_sobre_D > 0 -> HW_sobre_D >= 0":
        "equivalente: HW/D exactamente 0.0 (una lamina en el fondo) es de medida nula; el mutante solo cambia si un caudal produce ese cero exacto",
    "src/modulos/M4_control.py::control_salida::comparacion::TW > h_o_geometrico -> TW >= h_o_geometrico":
        "equivalente: con TW == h_o_geometrico las dos ramas devuelven el mismo h_o; el mutante solo cambia el rotulo `ahogado_por_TW` en la igualdad exacta",
    "src/modulos/M4_control.py::control_salida::comparacion::HW_sobre_D < H_O_HW_SOBRE_D_MIN -> HW_sobre_D <= H_O_HW_SOBRE_D_MIN":
        "borde: HW/D exactamente igual a 0.75 (o a 1.2, la cautela) de HDS-5 pag. 3.24; la lectura (0.75 usable) no se fija por test porque construir HW/D = 0.75 exacto exige invertir el control de salida, y el caso es de medida nula",
    "src/modulos/M4_control.py::control_salida::comparacion::HW_sobre_D < H_O_HW_SOBRE_D_CAUTELA -> HW_sobre_D <= H_O_HW_SOBRE_D_CAUTELA":
        "borde: HW/D exactamente igual a 0.75 (o a 1.2, la cautela) de HDS-5 pag. 3.24; la lectura (0.75 usable) no se fija por test porque construir HW/D = 0.75 exacto exige invertir el control de salida, y el caso es de medida nula",
    "src/modulos/M4_control.py::hw_gobernante::comparacion::HW_salida > entrada.HW + TOL_UMBRAL_NORMATIVO -> HW_salida >= entrada.HW + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::hw_gobernante::aritmetico::entrada.HW + TOL_UMBRAL_NORMATIVO -> entrada.HW - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M4_control.py::regimen_del_barril::comparacion::TW < seccion.altura - TOL_UMBRAL_NORMATIVO -> TW <= seccion.altura - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::y_salida < D - TOL_UMBRAL_NORMATIVO -> y_salida <= D - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::TW > critico.y_c -> TW >= critico.y_c":
        "equivalente: con TW == y_c el tirante de salida es el mismo por `min(D, max(TW, y_c))`; solo cambia el texto del caso",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::A > 0 -> A >= 0":
        "equivalente: A = A(y_salida) con y_salida >= y_c > 0 nunca es cero; la guardia es defensiva",
    "src/modulos/M4_control.py::velocidad_de_salida::comparacion::TW < seccion.altura - TOL_UMBRAL_NORMATIVO -> TW <= seccion.altura - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M4_control.py::velocidad_de_salida::aritmetico::seccion.altura - TOL_UMBRAL_NORMATIVO -> seccion.altura + TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M4_control.py::_pasos_hidraulicos::constante::1 -> 2":
        "equivalente: el valor por defecto `celdas=1` nunca se usa, `resolver_control` pasa siempre `celdas` explicito",
    # E-A retiro la entrada `_exigir_regimen_evaluable::retorno_none` (return
    # False -> return None): la funcion paso a `_regimen_de_v1_v2`, que
    # devuelve uno de tres rotulos y no un booleano, y ese mutante ya no se
    # genera. Los mutantes nuevos del perfil se remidieron con el arnes al
    # cierre de E-A (ver la ficha EA-06 en docs/decisiones_diferidas.md).
    # --- E-A: el perfil de la lamina (M4.perfil_lamina y sus auxiliares),
    # medido el 2026-09-21 con `--funcion` sobre las once funciones tocadas:
    # 242 mutantes, 212 muertos en la primera vuelta (87.6 %), 5 mas en la
    # segunda, 25 vivos; el unico hueco real (V_entrada_m_s del retorno
    # UNIFORME) se cerro con una asercion y quedan los 24 de abajo, mas los
    # cuatro que ya estaban censados (hw_gobernante x2, V1, V2). ------------
    "src/modulos/M4_control.py::_llenado_donde_Sf_iguala_S::comparacion::f_a * f_b < 0 -> f_a * f_b <= 0":
        "borde: solo se distingue si la raiz de Sf = S cae EXACTAMENTE en un extremo del corchete (f = 0 en punto flotante), de medida nula; entonces Brent devuelve ese extremo y el perfil es el mismo",
    "src/modulos/M4_control.py::_llenado_donde_Sf_iguala_S::aritmetico::f_a * f_b -> f_a / f_b":
        "equivalente: el signo del cociente es el del producto salvo con f_b = 0, que es el borde de arriba",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::HW_aproximado / D < H_O_HW_SOBRE_D_MIN -> HW_aproximado / D <= H_O_HW_SOBRE_D_MIN":
        "borde: HW/D exactamente 0.75 (HDS-5 pag. 3.24), de medida nula; el mismo borde que `control_salida` lleva censado",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::HW_aproximado / D < H_O_HW_SOBRE_D_CAUTELA -> HW_aproximado / D <= H_O_HW_SOBRE_D_CAUTELA":
        "borde: HW/D exactamente 1.2 (HDS-5 pag. 3.24), de medida nula; el mismo borde que `control_salida` lleva censado",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::TW < D - TOL_UMBRAL_NORMATIVO -> TW <= D - TOL_UMBRAL_NORMATIVO":
        "borde: un TW a exactamente D - 1e-9 (el borde de la banda que `regimen_del_barril` comparte), de medida nula",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::TW > D -> TW >= D":
        "equivalente: con TW == D las dos ramas dan h_salida = D",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::pendiente_linea < 0 -> pendiente_linea <= 0":
        "borde: Sf_llena exactamente igual a S (linea llena horizontal), de medida nula; el original la declara llena hasta la entrada y el mutante dividiria por cero en x_corte",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::x_corte < L -> x_corte <= L":
        "borde: la linea llena corta la clave EXACTAMENTE en la entrada (x_corte == L), de medida nula: llena hasta la entrada y lamina libre de longitud cero publican los mismos numeros",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::TW > y_c -> TW >= y_c":
        "equivalente: con TW == y_c el llenado del TW por Brent es el llenado de y_c (a TOL_BRENT), y la frontera max(y_c, TW) es la misma",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::f_salida < 0 -> f_salida <= 0":
        "borde: Sf exactamente igual a S en la frontera (f_salida == 0.0 en punto flotante), de medida nula; la rama M1/S1 encontraria la raiz en la propia frontera y el retorno UNIFORME a TOL es el mismo",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::f_salida > 0 -> f_salida >= 0":
        "borde: el mismo f_salida == 0.0 exacto de arriba, que solo llega a esta rama tras fallar `< 0`",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::g0.y > y_c + TOL_UMBRAL_NORMATIVO -> g0.y >= y_c + TOL_UMBRAL_NORMATIVO":
        "borde: una frontera a exactamente y_c + 1e-9 m, de medida nula (S1 de longitud cero frente a una S1 de un escalon de 1e-9 m)",
    "src/modulos/M4_control.py::perfil_lamina::aritmetico::y_c + TOL_UMBRAL_NORMATIVO -> y_c - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con una frontera a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9 m) de y_c; la banda existe para que y_c calculado por Brent cuente como y_c",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::abs(g0.y - y_asintota) <= TOL_UMBRAL_NORMATIVO -> abs(g0.y - y_asintota) < TOL_UMBRAL_NORMATIVO":
        "borde: una frontera a exactamente 1e-9 m de la asintota, de medida nula",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::abs(denominador) > TOL_ASINTOTA_PERFIL * S -> abs(denominador) >= TOL_ASINTOTA_PERFIL * S":
        "borde: |S - Sf_medio| exactamente igual a 1e-12·S, de medida nula",
    "src/modulos/M4_control.py::perfil_lamina::aritmetico::TOL_ASINTOTA_PERFIL * S -> TOL_ASINTOTA_PERFIL / S":
        "banda: el freno de la escalera pasa de 1e-12·S a 1e-12/S (1e-15 frente a 1e-9 con S = 0.001) y ninguna estacion de la suite cae entre los dos: acercarse tanto a la asintota exige del orden de 1e9 escalones; fijarlo pediria un caso al pelo sobre la tolerancia numerica, que no mueve ninguna magnitud",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::dx >= 0 -> dx > 0":
        "borde: dx exactamente 0.0 (dos escalones consecutivos con la misma energia especifica), de medida nula; el mutante lo trataria como avance negativo",
    "src/modulos/M4_control.py::perfil_lamina::comparacion::x + dx < L -> x + dx <= L":
        "borde: un escalon que termina EXACTAMENTE en la entrada (x + dx == L), de medida nula: el cruce por Brent devuelve el mismo llenado que el escalon",
    "src/modulos/M4_control.py::perfil_lamina::aritmetico::longitud_llena / L -> longitud_llena * L #3":
        "equivalente: en el retorno UNIFORME a TOL `longitud_llena` es 0 (la rama sumergida deja la frontera en la clave, y una asintota a menos de 1e-9 m de la clave es el borde), y 0/L = 0·L",
    "src/modulos/M4_control.py::perfil_lamina::aritmetico::longitud_llena / L -> longitud_llena * L #5":
        "equivalente: la S1 de longitud cero exige g0.y <= y_c + TOL, y tras un tramo lleno g0.y es D > y_c: solo se llega sin tramo lleno, con `longitud_llena` = 0, y 0/L = 0·L",
    "src/modulos/M5_verificaciones.py::v1_borde_libre::comparacion::y_sobre_D <= y_sobre_D_max + TOL_UMBRAL_NORMATIVO -> y_sobre_D < y_sobre_D_max + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v2_velocidad_minima::comparacion::V >= v_min - TOL_UMBRAL_NORMATIVO -> V > v_min - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v2b_sedimentacion::comparacion::resultado.S >= S_cauce - TOL_UMBRAL_NORMATIVO -> resultado.S > S_cauce - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v3_velocidad_maxima::comparacion::resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO -> resultado.V_erosion < v_max + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v3_velocidad_maxima::comparacion::resultado.V_erosion <= v_max + TOL_UMBRAL_NORMATIVO -> resultado.V_erosion < v_max + TOL_UMBRAL_NORMATIVO #2":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::altura_relleno_sobre_clave::comparacion::altura <= TOL_UMBRAL_NORMATIVO -> altura < TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::resguardo_por_cbr::comparacion::cbr < cbr_max -> cbr <= cbr_max":
        "equivalente: la tabla RESGUARDO_NAPA_SUBRASANTE va en orden descendente y la fila cuyo CBR_min es el borde se encuentra antes que la que lo tiene por CBR_max; `<=` en el techo nunca decide (test_el_resguardo_por_cbr... fija la lectura [min, max))",
    "src/modulos/M5_verificaciones.py::v4_carga_entrada::comparacion::HW_cota <= admisible + TOL_UMBRAL_NORMATIVO -> HW_cota < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v4_carga_entrada::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v4b_relacion_hw_d::comparacion::HW_sobre_D <= admisible + TOL_UMBRAL_NORMATIVO -> HW_sobre_D < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v4b_relacion_hw_d::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::vc1_borde_libre_canal::comparacion::HW_cota <= admisible + TOL_UMBRAL_NORMATIVO -> HW_cota < admisible + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::vc1_borde_libre_canal::aritmetico::admisible + TOL_UMBRAL_NORMATIVO -> admisible - TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v7_flotacion::comparacion::estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO -> estabilizante > desestabilizante - TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::v7_flotacion::aritmetico::desestabilizante - TOL_UMBRAL_NORMATIVO -> desestabilizante + TOL_UMBRAL_NORMATIVO":
        "banda: solo se distingue con un valor a menos de 2·TOL_UMBRAL_NORMATIVO (1e-9) del umbral; la banda existe para que la igualdad en punto flotante cuente como cumplimiento",
    "src/modulos/M5_verificaciones.py::v9_disponibilidad_diametro::comparacion::D <= material.D_max + TOL_UMBRAL_NORMATIVO -> D < material.D_max + TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/M5_verificaciones.py::verificar::retorno_none::return tuple(hechas) -> return None":
        "fuera: ningun test llega al final de `M5.verificar` (la Fase 5 de expediente) porque V5 esta vacia y detiene antes; la de perfil corre por `servicio._verificador_perfil` (ficha EXT-11-04)",
    "src/modulos/MD.py::_mismo_escalon::comparacion::abs(a.altura - b.altura) > TOL_UMBRAL_NORMATIVO -> abs(a.altura - b.altura) >= TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
    "src/modulos/MD.py::_mismo_escalon::retorno_none::return False -> return None":
        "equivalente: `return None` es tan falso como `return False` para `any(...)` en `_exigir_progreso`",
    "src/modulos/MD.py::_mismo_escalon::comparacion::abs(ancho_a - ancho_b) <= TOL_UMBRAL_NORMATIVO -> abs(ancho_a - ancho_b) < TOL_UMBRAL_NORMATIVO":
        "equivalente: `<=`/`>=` frente a `<`/`>` con la banda TOL_UMBRAL_NORMATIVO solo difieren en la igualdad exacta umbral ± 1e-9, de medida nula en punto flotante",
}


def _clave(modulo, funcion, operador, original, mutado):
    return f"{modulo}::{funcion}::{operador}::{original} -> {mutado}"


@pytest.fixture(scope="module")
def mutantes_de_hoy():
    """{clave: Mutante} de todo lo que el arnes genera sobre el arbol actual."""
    salida = {}
    for modulo, funciones in mutacion.MODULOS_DE_EXT11.items():
        for m, _ in mutacion.generar(modulo, funciones):
            salida.setdefault(m.clave, m)
    return salida


def test_cada_superviviente_del_censo_sigue_siendo_un_mutante_del_codigo(mutantes_de_hoy):
    huerfanos = [c for c in SUPERVIVIENTES_CON_RAZON if c not in mutantes_de_hoy]
    assert not huerfanos, (
        "entradas de SUPERVIVIENTES_CON_RAZON que el arnes ya no genera "
        "(cambio el codigo que anclan): actualiza o retira estas\n  "
        + "\n  ".join(huerfanos))


def test_cada_razon_del_censo_es_de_una_de_las_clases_declaradas():
    clases = ("equivalente", "banda", "borde", "memoria", "fuera")
    for clave, razon in SUPERVIVIENTES_CON_RAZON.items():
        assert razon.split(":")[0] in clases, f"{clave}: «{razon[:60]}»"
    assert not any(r.startswith("hueco") for r in SUPERVIVIENTES_CON_RAZON.values()), (
        "un hueco real no se censa: se cierra con un test")


# ---------------------------------------------------------------------------
# El arnes probandose a si mismo
# ---------------------------------------------------------------------------

def _generar_sobre(codigo: str, tmp_path, funciones=None, operadores=mutacion.OPERADORES):
    ruta = tmp_path / "modulo_de_prueba.py"
    ruta.write_text(textwrap.dedent(codigo), encoding="utf-8")
    original = mutacion.RAIZ
    mutacion.RAIZ = tmp_path
    try:
        return mutacion.generar("modulo_de_prueba.py", funciones, operadores)
    finally:
        mutacion.RAIZ = original


def test_el_generador_produce_los_ocho_operadores_y_ninguno_mas(tmp_path):
    codigo = '''
        def f(material, normal, x, y):
            """docstring con 3 numeros: 1 + 2."""
            if x > 0 and not y:
                return material.n_min * normal.V_erosion + 2
            return None
    '''
    mutantes = _generar_sobre(codigo, tmp_path)
    operadores = {m.operador for m, _ in mutantes}
    assert operadores == set(mutacion.OPERADORES)
    fragmentos = {(m.operador, m.original, m.mutado) for m, _ in mutantes}
    assert ("par_n", "material.n_min", "material.n_max") in fragmentos
    assert ("par_v", "normal.V_erosion", "normal.V_sedimentacion") in fragmentos
    # Los fragmentos son texto de `ast.unparse`, y su forma exacta (los
    # parentesis de `not`) cambia entre versiones: se comparan tras la
    # misma ida y vuelta por el AST, no contra un texto escrito a mano.
    def _normal(expr):
        return ast.unparse(ast.parse(expr, mode="eval"))
    condiciones = {(m.original, m.mutado) for m, _ in mutantes if m.operador == "condicion"}
    assert {(_normal(o[3:-1]), _normal(mu[3:-1])) for o, mu in condiciones} == {
        (_normal("x > 0 and not y"), _normal("not (x > 0 and not y)"))}
    assert ("retorno_none", "return material.n_min * normal.V_erosion + 2",
            "return None") in fragmentos
    # El docstring no se muta, y `return None` no se muta a si mismo.
    assert not any("docstring" in m.original for m, _ in mutantes)
    assert not any(m.original == "return None" for m, _ in mutantes)


def test_el_generador_no_toca_cadenas_ni_numeros_dentro_de_f_strings(tmp_path):
    codigo = '''
        def f(v):
            return f"{v:.3f} m/s (2 decimales)"
    '''
    mutantes = _generar_sobre(codigo, tmp_path, operadores=("constante",))
    assert mutantes == []


def test_cada_fuente_mutada_es_python_valido_y_difiere_del_original(tmp_path):
    codigo = '''
        def g(a, b):
            if a <= b:
                return (a + b) / 2
            return a ** 2
    '''
    mutantes = _generar_sobre(codigo, tmp_path)
    assert len(mutantes) >= 8
    original = ast.unparse(ast.parse(textwrap.dedent(codigo)))
    for m, fuente in mutantes:
        ast.parse(fuente)
        assert fuente != original, m.clave


def test_el_arnes_mata_de_verdad_un_mutante_conocido(tmp_path):
    """
    De punta a punta y en subproceso: el par de n intercambiado en
    `resolver_manning` muere contra las propiedades. Es el unico test de
    aqui que corre pytest dentro de pytest; cuesta unos segundos.
    """
    mutantes = [(m, f) for m, f in mutacion.generar(
        "src/modulos/M3_hidraulica.py", ("resolver_manning",), ("par_n",))]
    assert mutantes, "resolver_manning dejo de leer el par de n"
    resultados = mutacion.evaluar(mutantes[:1], ("tests/test_ext11_propiedades.py",),
                                  trabajadores=1)
    assert resultados[0]["veredicto"] == "muerto", resultados[0]


def test_el_arnes_se_niega_a_medir_sobre_una_linea_base_roja(tmp_path):
    """
    Un objetivo roto mataria a todos los mutantes y el score seria 1.0 sin
    medir nada: la corrida de referencia lo impide (auditoria de EXT-11).
    """
    roto = tmp_path / "test_roto.py"
    roto.write_text("def test_x():\n    assert False\n", encoding="utf-8")
    with pytest.raises(mutacion.LineaBaseRoja):
        mutacion.exigir_linea_base_verde(mutacion.RAIZ, (str(roto),))


def test_dos_mutaciones_identicas_en_la_misma_funcion_tienen_claves_distintas(mutantes_de_hoy):
    claves = set()
    repetidos = 0
    for modulo, funciones in mutacion.MODULOS_DE_EXT11.items():
        for m, _ in mutacion.generar(modulo, funciones):
            assert m.clave not in claves, m.clave
            claves.add(m.clave)
            repetidos += m.ordinal > 1
    assert repetidos > 0, "el ordinal existe porque hay fragmentos repetidos; hoy no hay ninguno"


def test_los_modulos_medidos_son_M3_M5_MD_y_el_par_de_n():
    modulos = set(mutacion.MODULOS_DE_EXT11)
    assert {"src/modulos/M3_hidraulica.py", "src/modulos/M4_control.py",
            "src/modulos/M5_verificaciones.py", "src/modulos/MD.py"} <= modulos
    assert set(mutacion.MODULOS_DE_EXT11["src/modelos.py"]) == {
        "n_para_capacidad", "n_para_velocidad_maxima", "n_para_velocidad_minima"}
    assert "_par_de_manning" in mutacion.MODULOS_DE_EXT11["src/modulos/M2_material.py"]
    assert "tests/test_ext11_propiedades.py" in mutacion.OBJETIVOS
