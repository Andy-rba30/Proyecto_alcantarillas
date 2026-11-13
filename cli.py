"""
cli.py
======
Linea de comandos del expediente: corre el pipeline completo sobre el CSV de
puntos criticos de Sec. 1.2 y vuelca el resultado a stdout mas un JSON.

    M0 -> M1 -> MD (M2/M3/M4/M5) -> M6 -> M7 -> M8 -> M9 -> M10

DESDE EXT-9 ESTE ARCHIVO ES UN ADAPTADOR. La orquestacion --- el alcance y lo
que difiere, la carga de datos externos, las estructuras del informe, las
fases, `correr` y el contexto de la corrida --- vive en `src/servicio.py`, y
aqui quedan las tres puertas que la presentan: `argparse` (`main`), el
volcado a JSON (`informe_json`) y el volcado a texto (`volcar`), mas la
sesion serializada y `--declarar`. Lo que la GUI y la suite leen de `cli`
se sigue leyendo de aqui, reexportado del servicio como el MISMO objeto
(ver el bloque de imports). El docstring que sigue describe lo que la CLI
reporta y acepta, que no cambio.

Uso
---
    python cli.py tests/ejemplo_puntos.csv --luz 2.0 --json salida.json

Que reporta por punto
---------------------
    material y SECCION adoptada (Fase 4) -- un diametro en un tubo, el par
    B x H en un marco: lo nombra la propia seccion (`Seccion.etiqueta`)
    control gobernante (entrada / salida) y la hidraulica que lo sostiene
    verificaciones con su numeral: la luz de Sec. 2.1, V1-V9 de la Fase 5 y
        G1/G2 de Sec. 7.B (y G3, el aviso de esviaje, desde T-6), cada una
        con valor obtenido, admisible y el criterio adoptado del que sale el
        umbral
    los criterios pendientes que bloquearon una etapa, con el concepto y la
        fuente que los resolveria

Datos que NO estan en el CSV
----------------------------
DOS CLASES DE CLAVE, Y NINGUN CONTEO ESCRITO A MANO. Este bloque las enumera
y no las cuenta, a proposito: un numero escrito aqui envejece con la clave
siguiente, y ya envejecio dos veces -- la historia esta en §16.11-bis de
`docs/ruta_familia_c.md`, no aqui, porque contarla en el propio parrafo vuelve
a dejar el numero escrito --. La cuenta que no envejece es
`len(CLAVES_EXTERNAS)`, y `test_cli` contrasta esta lista contra ella.

NO TODAS SON AJENAS AL CSV, aunque el titulo del bloque lo sugiera: `Q_m3s` y
`S_cauce` SI son columnas de Sec. 1.2. Las dos clases son estas, y la
diferencia importa porque se corrigen en sitios distintos:

  (a) MAGNITUDES QUE NO SON COLUMNA. `luz_m`, `TW_m`, `longitud_m`,
      `S_conducto`, `L_hidraulico_m` y `categoria_tr`. Sec. 1.2 no las trae y
      ningun numeral las deduce. Y, desde T-2, dos que no son un numero
      suelto y solo entran por el JSON: `seccion_receptor_medida` (la seccion
      levantada del receptor, un objeto con b_m, z_HV, S, n y altura_total_m,
      que gana sobre la adoptada del criterio 'seccion_receptor') y
      `acceso_mantenimiento_previsto` (booleano: si los planos preven el
      acceso de limpieza del num. 4.1.1.3.7 d)). Las dos son opcionales.
      Desde T-6 tambien `bombeo` y `peralte`, la pendiente transversal de la
      plataforma en el cruce: opcionales, excluyentes entre si, y sin ellas
      la longitud por extremo toma la plataforma horizontal y lo avisa.
      Y, desde T-8, las de la Fase 6, tambien opcionales y por punto o
      globales: `tipo_terreno_receptor` y `tipo_terreno_entrada` (fila de
      la Tabla N 11 del Manual: el material del cauce a la salida y a la
      entrada), `regimen_flujo_descarga` (su columna: intermitente o
      permanente), `material_lecho_salida` (objeto del EMS con el suelo del
      lecho: tipo, D84_m y D16_m o IP y Sv_Pa, y pasa_200_pct),
      `duracion_caudal_pico_min` (minutos, del estudio hidrologico) y
      `profundidad_socavacion_estimada_m` (de un estudio del cauce; gana
      sobre la hoya que estima el programa).
      Y, desde T-9, las tres de la cuneta de la Fase 10 (Familia B), solo
      por el JSON: `ancho_tributario_m` (ancho de la faja que drena a la
      cuneta), `S_cuneta` (pendiente longitudinal de la cuneta) y
      `inicio_tramo_cuneta_km` (progresiva donde empieza el tramo que
      descarga en el alivio, el extremo de VB1).
  (b) COLUMNAS QUE UNA FAMILIA DEJA VACIAS POR TABLERO. `Q_m3s` y `S_cauce`.
      La columna existe y para la Familia C va vacia a proposito
      (`M0_carga._VACIAS_FAMILIA_C`): su valor no lo tiene quien escribe el
      CSV sino el Tablero 3.1 (ANA / Junta de Usuarios del Bajo Piura), que la
      Sec. 2.3 de la hoja de ruta nombra como el que bloquea la familia
      entera. La clave es el vehiculo por el que ese dato entra el dia que el
      tablero lo entrega. `S_conducto` esta en la clase (a) y no en esta, y
      conviene decirlo porque se confunde: no es ninguna columna, es la
      pendiente del CONDUCTO cuando difiere de la del cauce.

Entran declaradas por quien corre el calculo -- por bandera o por el JSON de
`--datos-externos` -- y el informe registra de donde salio cada una, igual que
MD recibe L y TW en vez de derivarlos:

    luz_m           m     luz del cruce, de la topografia o del QGIS. Sin ella
                          no se puede aplicar el umbral binario de Sec. 2.1 y
                          el punto no se disena: un cruce de 6 m o mas es
                          PUENTE y esta fuera de alcance (Sec. 3.1).
    TW_m            m     tirante en el receptor sobre el fondo de la SALIDA.
                          Si no se declara se pide a `criterios_adoptados`
                          ('TW_receptor'), que hoy es un vacio.
    longitud_m      m     longitud del conducto. Si no se declara la calcula
                          M7 (7.B), que exige 'talud_terraplen'.
    Q_m3s, S_conducto     caudal y pendiente cuando no son los de la columna:
                          Sec. 2.3 dice que el caudal de la Familia B es el
                          del drenaje longitudinal y el de la C el del canal.
    S_cauce         m/m   pendiente del CAUCE NATURAL, para el punto cuya
                          columna va vacia. En un cruce de canal el "cauce" es
                          el canal y su pendiente la da el Tablero 3.1, no
                          quien escribe el CSV. NO ES `S_conducto` y no se
                          sustituye por ella: `S_conducto` es la pendiente con
                          que se tiende el barril y esta es la del cauce que
                          lo alimenta; V2b compara UNA CONTRA OTRA (indicador
                          de sedimentacion del HDS-5, num. 5.3.3), de modo que
                          igualarlas convertiria la verificacion en una
                          tautologia. Sin ella, V2b se detiene con
                          `DatoFaltanteError('S_cauce')` y el material entero
                          queda no evaluable; la Fase 4 no se detiene, porque
                          la pendiente del diseno la aporta `S_conducto`.
    L_hidraulico_m  m     longitud a la que la cuneta agota su capacidad, para
                          la Fase 10 (Familia B). Declarada GANA; sin ella la
                          calcula M10 (T-9) con los datos de abajo y los
                          criterios de la cuneta ('seccion_cuneta', con el
                          minimo muy lluvioso de la Tabla Nº 34, y
                          'revestimiento_cuneta').
    ancho_tributario_m, S_cuneta
                    m, m/m ancho de la faja que drena a la cuneta y pendiente
                          longitudinal de la cuneta (trazo). Con S_cuneta se
                          verifica VB2 (aporte contra capacidad). Sin los que
                          hagan falta y sin L_hidraulico_m, la Fase 10 del
                          punto se detiene (con el tramo conocido y el caudal
                          declarado basta S_cuneta).
    inicio_tramo_cuneta_km
                    km    progresiva donde empieza, del lado de progresivas
                          menores, el tramo de cuneta que descarga en el
                          alivio: extremo de VB1; gana sobre la obra anterior
                          (B, o A por 'obras_familia_a_extremo_de_cuneta').
                          Sin el y sin obra anterior, VB1 no se evalua y es
                          un bloqueo del punto.
    bombeo, peralte m/m   pendiente transversal de la plataforma en el cruce,
                          de la seccion tipica (DG-2018 num. 304.05 y 304.06;
                          0.02 = 2 %). OPCIONALES y solo por el JSON: afinan
                          la longitud por extremo de 7.B. `bombeo` >= 0 baja
                          los dos bordes; `peralte` lleva signo, positivo
                          sube el borde del lado de la entrada. SON
                          EXCLUYENTES en un mismo punto (una seccion tiene
                          bombeo o peralte): los dos distintos de cero son
                          `DatoInvalidoError`. Sin ellos la plataforma se
                          toma horizontal, y la memoria lo avisa.
    categoria_tr          fila de la Tabla N 02 del punto ('quebrada_importante'
                          o 'quebrada_menor'). Sec. 2.2 la declara cauce por
                          cauce y el Manual no da un umbral para deducirla; sin
                          ella la Familia A se detiene en
                          'umbral_area_quebrada_importante_ha'.
    tipo_terreno_receptor, tipo_terreno_entrada, regimen_flujo_descarga
                          fila y columna de la Tabla N 11 del Manual para el
                          cauce de salida y el de entrada. Sin ellas la Fase 6
                          dimensiona el enrocado como antes de T-8 y AVISA que
                          no comparo con la velocidad admisible del terreno.
    material_lecho_salida suelo del lecho a la salida (EMS). Sin el, la hoya
                          de socavacion de HEC-14 Cap. 5 no se estima y el
                          filtro no elige columna de EG-2013; la corrida avisa.
    duracion_caudal_pico_min  min. Sin ella rige el criterio
                          'duracion_caudal_pico_socavacion_min'.
    profundidad_socavacion_estimada_m  m. Admite 0; si falta, la estimada.

Ninguna tiene valor por defecto. Sin declararla, la etapa que la
necesita queda bloqueada y el informe lo dice; no se sustituye por un numero
plausible.

Y UNA TERCERA CLASE DESDE T-4, QUE NO ES DE `CLAVES_EXTERNAS`: LOS ENSAYOS DE
DURABILIDAD (Sec. 3.3 y 3.4 de la hoja de ruta). Entran por el mismo JSON de
`--datos-externos` -- en `globales` para todo el sitio, en `puntos` para una
calicata, que pisa al del sitio -- y no tienen bandera. Son OPCIONALES: su
ausencia no bloquea ninguna etapa, y por eso viven en
`servicio.CLAVES_DE_DURABILIDAD` y no en la tupla de arriba, cuyas claves son
datos que alguna etapa exige. Tampoco tienen valor por defecto:

    sulfatos_suelo_ppm   ppm   sulfato (SO4) en el suelo; la Tabla 4.4 de
                               E.060 lo lee en % en peso (1 % = 10 000 ppm).
    sulfatos_agua_ppm    ppm   sulfato en el agua: la otra escala de la tabla.
    cloruros_ppm         ppm   cloruros; la norma no da umbral: solo avisa.
    pH                   -     pH del suelo o del agua.
    resistividad_ohm_cm  ohm-cm
    abrasion             texto nivel de abrasion del sitio, uno de los cuatro
                               de la Table 8-4 del WSDOT Hydraulics Manual
                               (`no_abrasivo`, `poco_abrasivo`,
                               `moderadamente_abrasivo`,
                               `severamente_abrasivo`). Es un dato de campo:
                               no se deduce de la velocidad.

Con ellos `M2.matriz_durabilidad` filtra los materiales candidatos del punto
(pH y resistividad excluyen la TMC; la abrasion severa, el HDPE; los sulfatos
exigen al concreto su cemento) y el informe lo imprime con sus citas. Sin
ninguno, la matriz no actua y cada punto dice «durabilidad: sin ensayos,
matriz no aplicada».

Que hace con un criterio pendiente
----------------------------------
Lo registra como bloqueo de la etapa donde salto -- con clave, concepto y
fuente -- sigue con las etapas que no dependen de el, y al final los agrupa en
un bloque aparte con las fases y los puntos que bloquearon (Sec. 0.7). Nunca
sustituye por un defecto ni convierte el vacio en un incumplimiento: un
criterio sin valor es un calculo que todavia no se puede completar, no una
verificacion que falla.

Como declarar uno sin tocar el archivo: `--declarar CLAVE=VALOR`, repetible.
Es la MISMA via que la pestana "Criterios" de la GUI --
`criterios_adoptados.establecer_valor_dinamico`, que somete el valor a la
guardia del archivo -- y vale solo para esa corrida:
`criterios_adoptados.py` no se modifica. La memoria imprime esos valores con
su procedencia ("declarado para esta corrida, no en archivo") y los lista
aparte, para que nadie los lea como transcritos de una norma.

Misma via NO es misma politica, y conviene saberlo: la GUI solo ofrece el
boton para los criterios VACIOS (y para retirar lo que ella misma declaro),
mientras que `--declarar` acepta cualquier clave declarada, incluidas las que
ya traen valor en el archivo. Es deliberado -- una corrida de sensibilidad
consiste justamente en mover un valor que ya existe -- y no abre un agujero:
el valor pasa por la misma guardia, la memoria lo marca como declarado para
la corrida y dice ademas QUE valor trae el archivo, de modo que sustituir un
valor transcrito queda a la vista en el entregable. Lo que no se puede por
ninguna de las dos vias es declarar `None` -- ni la cadena vacia
(`--declarar CLAVE=` se rechaza): retirar una declaracion es otra operacion, y
aqui consiste en no pasar la bandera.

Solo se atrapa `ErrorProyecto` (criterio pendiente, dato faltante, dato
invalido, diseno no factible): es un problema del expediente y va al informe.
Un fallo de programa (ImportError, AssertionError) se propaga con su traza,
porque significa que un modulo esta incompleto.

Codigos de salida
-----------------
    0   el expediente cerro AL ALCANCE DECLARADO (--alcance, por defecto
        "expediente"): todos los puntos dimensionados, sin bloqueos y con
        todas las verificaciones cumpliendo. Lo diferido por alcance no
        cuenta como bloqueo, pero queda impreso con su fundamento
    1   el expediente esta incompleto: hay bloqueos, puntos sin dimensionar o
        verificaciones incumplidas. Es el resultado normal mientras el
        Tablero 3 siga abierto
    2   no se pudo correr: el CSV o el JSON de datos externos no se pueden
        leer o no tienen la forma esperada
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Los modulos del calculador se importan del paquete `src` (EXT-9, PC-08):
# esta CLI vive en la raiz del repositorio y la raiz la pone el interprete
# (`python cli.py`, `python -m cli`), no un `sys.path.insert`. Antes de EXT-9
# este archivo insertaba `src/` en el path e importaba por nombre plano, y
# esa doble via era la que permitia dos copias del mismo modulo con dos
# estados (`_OVERRIDES`, `_USADOS`) en un proceso mixto.
from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src import declaracion as _declaracion
from src import comparador as _comparador
from src import sesion as _sesion
from src.constantes_normativas import H_O_HW_SOBRE_D_MIN
from src.modelos import (Bloqueo, Clasificacion, CompatibilidadGeometrica,
                         ContextoCorrida, ErrorProyecto, Espaciamiento,
                         EstadoDeVerificacion,
                         PasoDiseno, PerfilLamina, ProteccionSalida,
                         ResultadoPunto, TipoDeVeredicto, Verificacion)
from src.modelos import (ORIGEN_DIMENSION_DECLARADA,   # --- T-7a ---
                         ORIGEN_DIMENSION_DERIVADA)
from src.modulos import M2_material as M2
from src.modulos import M5_verificaciones as M5
from src.modulos.M8_estructural import (CODIGO_PASO_HMAX_TIPO4,
                                        verificacion_diferida_estructural)
# La agregacion de criterios bloqueantes y el armado de la memoria son de la
# Fase 11: viven en M11 y aqui solo se usan. `CriterioBloqueante` se
# reexporta porque el JSON y el volcado de texto de esta CLI lo siguen
# publicando con el mismo nombre.
from src.modulos.M11_reporte import (CriterioBloqueante,  # noqa: F401
                                     DIR_PLANTILLAS, NOMBRE_PLANTILLA,
                                     NOMBRE_PLANTILLA_PERFIL,
                                     cargar_plantilla, criterios_bloqueantes,
                                     exportar_csv, exportar_html, exportar_pdf,
                                     marcadores_de_la_memoria, memoria_html)

# ===========================================================================
# El servicio de calculo (EXT-9, E01): la orquestacion vive en src/servicio.py
# ===========================================================================
# Esta CLI es un ADAPTADOR: argparse, el volcado a JSON y el volcado a texto.
# Lo que corre el expediente --- el alcance y lo que difiere, la carga de
# datos externos, las estructuras del informe, las fases, `correr` y el
# contexto de la corrida --- esta en `src/servicio.py` y se importa de alli.
#
# DOS GRUPOS, Y EL SEGUNDO ES UN CONTRATO. El primero es lo que este archivo
# usa. El segundo son REEXPORTACIONES: los atributos que `gui/app.py` lee
# como `cli.X` y los privados que la suite lee como `cli._x`
# (`_verificador_perfil`, `_etapa`, `_numero_externo`, `_fase_*`, `_bloqueo`,
# `_dato_externo`, `_compuerta_metodo_h_o`, `_DOMINIO_DE_CLAVE`, ...). Son
# el MISMO objeto que el del servicio --- no una copia; un test lo fija por
# identidad ---, y se retiran solo cuando los archivos de tests que los leen
# migren al servicio (ficha EXT-9-01 de `docs/decisiones_diferidas.md`).
# Patchear una funcion que el servicio LLAMA (`disenar_punto`,
# `cadena_sismica`, `seleccionar_clase_calibre`) se hace sobre `servicio`,
# que es donde se resuelve el nombre: en EXT-9 los tres sitios de la suite
# que lo hacian sobre `cli` migraron.
from src.servicio import (ALCANCE_EXPEDIENTE, ALCANCE_PERFIL, DECIMALES_FACTOR,
                          ETAPA_DURABILIDAD,
                          FASE_CABEZAL, DatoDeclarado, Informe, InformeCabezal,
                          InformePunto, _fmt, advertencia_de_corredor_de,
                          cargar_datos_externos, cargar_datos_sitio,
                          cargar_hidrologia, correr)
from src.servicio import (  # noqa: F401  (reexportaciones: contrato GUI/suite)
    CLAVES_DE_DURABILIDAD, CLAVES_EXTERNAS, DatosExternos, FAMILIAS_QUE_USAN,
    FASE_ESTRUCTURAL,
    MODULOS_DIFERIDOS_POR_ALCANCE, NOTA_ESTABILIDAD_CABEZAL,
    VERIFICACIONES_DIFERIDAS_POR_ALCANCE, _DOMINIO_DE_CLAVE,
    _avisar_ids_desconocidos, _bloqueo, _compuerta_metodo_h_o, _dato_externo,
    _etapa, _fase_10, _fase_6, _fase_8, _numero_externo, _verificador_perfil,
    capturar_contexto, familias_del_csv, familias_que_usan, puntos_por_familia)

# Presentacion. Ninguno entra en un calculo: mueven columnas de texto.
ANCHO = 78          # literal-ok: ancho de la caja de texto del volcado a consola
SANGRIA = "  "
# El segundo nivel de sangria del volcado. Se escribia `SANGRIA * 4` en seis
# sitios -- un literal por sitio, y ademas ilegible: son cuatro sangrias, no
# cuatro espacios. Es formato de consola, no un valor de proyecto.
SANGRIA_DETALLE = SANGRIA * 4   # literal-ok: nivel de sangria del volcado
# La pendiente se imprime con mas decimales que el resto: S = 0.005 m/m con
# los tres decimales por defecto se veria como 0.005 y con dos como 0.01.
DECIMALES_PENDIENTE = 4         # literal-ok: decimales del volcado de S
MARCA_CUMPLE = "[OK]"
MARCA_INCUMPLE = "[NO]"
# El indicador disparado bajo `regimen_v2b` = indicador_con_aviso (PF-4): la
# verificacion no detiene el punto (`cumple` True) y no es un [OK]; la marca
# se lee del veredicto del paso, como hace M11.
MARCA_INDICADOR = "[AVISO]"
# C10 (PC-27): la fila que no se evaluo no es [OK]. El estado es la fuente y
# este adaptador de texto es una vista mas; hasta C10 leia `cumple` a secas.
MARCA_NO_APLICA = "[N/A]"

# ===========================================================================
# Volcado a JSON
# ===========================================================================

def _num(valor: Any) -> Any:
    """
    Un float no finito no es JSON valido. Sale como texto para que el archivo
    se pueda leer siempre y el problema quede visible en el propio campo.
    """
    if isinstance(valor, float) and not math.isfinite(valor):
        return repr(valor)
    return valor


def _veredicto_de(v: Verificacion) -> Optional[str]:
    """El tipo de veredicto del paso de la verificacion, o None sin paso."""
    if v.paso is None or v.paso.veredicto is None:
        return None
    return v.paso.veredicto.tipo.value


def _verificacion_json(fase: str, v: Verificacion) -> Dict[str, Any]:
    # `veredicto` entra en PF-4: `cumple` dice si el punto se detiene y el
    # veredicto dice que juzgo la memoria. Bajo `regimen_v2b` =
    # indicador_con_aviso las dos cosas difieren a proposito (cumple=True,
    # veredicto «indicador»), y un JSON con solo `cumple` lo perderia --
    # el «fuera de dominio» que solo existia en el HTML es PC-27.
    # `estado` (PC-27, cierre): LA fuente; `cumple` y `veredicto` son sus
    # vistas y se conservan porque el JSON los publica desde EXT-3 / PF-4.
    return {"fase": fase, "codigo": v.codigo, "numeral": v.numeral,
            "estado": v.estado.value,
            "cumple": v.cumple, "veredicto": _veredicto_de(v),
            "valor_obtenido": _num(v.valor_obtenido),
            "valor_admisible": _num(v.valor_admisible),
            "criterio_aplicado": v.criterio_aplicado}


def _paso_json(paso: PasoDiseno) -> Dict[str, Any]:
    return {"material": paso.material,
            "seccion": paso.seccion.etiqueta(),
            "aceptado": paso.aceptado, "motivo": paso.motivo,
            "incumplidas": [v.codigo or v.numeral for v in paso.incumplidas]}


def _dato_json(dato: Optional[DatoDeclarado]) -> Optional[Dict[str, Any]]:
    if dato is None:
        return None
    return {"valor": _num(dato.valor), "origen": dato.origen}


def _seccion_receptor_json(tw) -> Optional[Dict[str, Any]]:
    """
    --- T-2 --- La seccion del receptor con que corrio Sec. 1.3 y de donde
    salio (medida o adoptada), o None si la via del TW no usa seccion
    (declarado, `cota_TW`) o el TW no llego a determinarse.
    """
    if tw is None or tw.seccion is None:
        return None
    sec = tw.seccion
    return {"origen": tw.origen_seccion, "via": tw.via.value,
            "b_m": _num(sec.b_m), "z_HV": _num(sec.z_HV), "S": _num(sec.S),
            "n": _num(sec.n), "altura_total_m": _num(sec.altura_total_m)}


def _bloqueo_json(bloqueo: Bloqueo) -> Dict[str, Any]:
    return {"fase": bloqueo.fase, "etapa": bloqueo.etapa,
            "tipo": bloqueo.tipo.value,
            "criterio": bloqueo.criterio, "etiqueta": bloqueo.etiqueta,
            "concepto": bloqueo.concepto, "fuente": bloqueo.fuente,
            "campo": bloqueo.campo,
            "delta_rasante_m": _num(bloqueo.delta_rasante_m),
            "diferido_por_alcance": bloqueo.diferido_por_alcance,
            "mensaje": bloqueo.mensaje}


def _clasificacion_json(c: Clasificacion) -> Dict[str, Any]:
    tr = c.periodo_retorno
    return {"luz_m": _num(c.luz_m), "denominacion": c.denominacion.value,
            "numeral_luz": c.verificacion_luz.numeral,
            "familia": c.perfil.familia.value,
            "origen_del_caudal": c.perfil.origen_del_caudal,
            "TR_procede": tr.procede,
            "TR_anios": tr.anios,
            "TR_categoria": None if tr.categoria is None else tr.categoria.value,
            "TR_numeral": tr.numeral, "TR_fundamento": tr.fundamento,
            "datos_pendientes": list(c.datos_pendientes)}


# Las claves del bloque `diseno` del JSON, escritas una vez para que el
# contrato con el tablero externo sea legible sin correr nada. Desde EXT-6
# lleva `alcance_norma_producto` (EXT-N-03): lo que la norma de producto dice
# cubrir en su clausula 1.1 o, para el marco, por que no la hay. Que la tupla
# y el diccionario de `_diseno_json` coincidan lo comprueba un test sobre el
# AST (tests/test_ext6_registro_normativo.py), no una guardia en la ruta de
# exportacion: un desajuste es un defecto del programa, no del expediente.
CLAVES_DISENO_JSON = (
    "material", "tipo", "norma_producto", "alcance_norma_producto",
    "seccion_eg2013", "n_min", "n_max", "seccion", "dimension_max_catalogo_m",
    # T-4: el criterio que fijo ese tope (serie de la norma, corrugacion,
    # disponibilidad declarada o serie del marco).
    "dimension_max_criterio",
    "control_gobernante", "Q_m3s", "S_m_m", "V_erosion_m_s",
    "V_sedimentacion_m_s", "y_normal_m", "y_critico_m", "HW_entrada_m",
    "HW_salida_m", "HW_gobernante_m", "Q_celda_m3s", "numero_celdas",
    "regimen_barril", "V_llena_m_s", "V_salida_m_s", "V_salida_procedencia",
    "y_salida_m", "h_o_m", "TW_m", "ahogado_por_TW", "HW_sobre_D_salida",
    "h_o_fuera_de_rango", "h_o_requiere_cautela",
    # EL PERFIL DE LA LAMINA (E-A): las dos salidas --la fraccion de longitud
    # a seccion llena y el HW por remanso-- con el rotulo del perfil, si
    # alcanza la entrada, si sustituye a la aproximacion, y el tirante
    # maximo y la velocidad minima que V1 y V2 compararon.
    "perfil_tipo", "perfil_alcanza_entrada", "perfil_HW_remanso_m",
    "perfil_HW_aproximado_m", "perfil_sustituye_aproximacion",
    "perfil_y_entrada_m", "perfil_y_max_m", "perfil_V_min_m_s",
    "perfil_fraccion_llena", "perfil_longitud_llena_m",
    "perfil_y_asintota_m", "perfil_comprobacion_manda",
    # EL PISO DE LA CARGA A LA ENTRADA (PF-1, PC-03): que opcion del criterio
    # `hw_entrada_fuera_de_rango` se adopto (None cuando la ecuacion entrego
    # carga por si sola, que es todo el corredor), el HW/D que la ecuacion
    # devolvio y el S* de la carta. Sin esto el JSON decia HW_entrada_m = H_c
    # como si fuera la ecuacion y el comparador no distinguia los dos casos.
    "hw_entrada_piso", "hw_entrada_HW_sobre_D_formula", "hw_entrada_S_limite_m_m",
)


def _diseno_json(resultado: ResultadoPunto) -> Dict[str, Any]:
    material, hidraulica = resultado.material, resultado.resultado_hidraulico
    perfil = hidraulica.perfil
    return {"material": material.nombre, "tipo": material.tipo.value,
            "norma_producto": material.norma_producto,
            "alcance_norma_producto": M2.alcance_norma_producto_de(
                material.tipo, material.forma),
            "seccion_eg2013": material.seccion_eg2013,
            "n_min": _num(material.n_min), "n_max": _num(material.n_max),
            "seccion": resultado.seccion.etiqueta(),
            "dimension_max_catalogo_m": _num(material.D_max),
            # --- T-4 --- De donde salio ese tope: la serie de la norma de
            # producto, la corrugacion adoptada (TMC), la disponibilidad
            # declarada o la serie del marco. Sin esta clave el numero de
            # arriba no dice si lo fija una norma o una eleccion.
            "dimension_max_criterio": material.D_max_criterio,
            "control_gobernante": hidraulica.control_gobernante.value,
            # Q y S son los del DISEÑO, no los de la columna del CSV: la
            # Familia B y la C traen su propio caudal (Sec. 2.3) y el punto que
            # no sigue el cauce declara su pendiente. La pendiente sale tambien
            # en el bloque de geometria, y ahora es forzosamente la misma: las
            # dos leen `ResultadoHidraulico.S` (MAT-D9). Aqui va ademas porque
            # el bloque de geometria no existe si la Fase 7 quedo bloqueada.
            "Q_m3s": _num(hidraulica.Q),
            "S_m_m": _num(hidraulica.S),
            # Dos claves y no una "V_m_s": la velocidad de la rama n_min
            # (techos: V3, d50) y la de la rama n_max (piso: V2) son numeros
            # distintos, y una sola clave obligaba a adivinar cual (MAT-D1).
            "V_erosion_m_s": _num(hidraulica.V_erosion),
            "V_sedimentacion_m_s": _num(hidraulica.V_sedimentacion),
            "y_normal_m": _num(hidraulica.y_normal),
            "y_critico_m": _num(hidraulica.y_critico),
            "HW_entrada_m": _num(hidraulica.HW_entrada),
            "HW_salida_m": _num(hidraulica.HW_salida),
            "HW_gobernante_m": _num(hidraulica.HW),
            # EL CAUDAL CON QUE M4 RESOLVIO DE VERDAD y cuantos barriles lo
            # reciben (EXT-2-02): Q_m3s sigue siendo el del punto.
            "Q_celda_m3s": _num(hidraulica.Q_celda_m3s),
            "numero_celdas": hidraulica.numero_celdas,
            # EL REGIMEN DEL BARRIL Y LA VELOCIDAD DE SALIDA (EXT-3; EXT-M-01,
            # PC-04): lo que V1/V2 compararon y lo que recibio la Fase 6, con
            # la procedencia que M4 escribio.
            "regimen_barril": hidraulica.regimen_barril.value,
            "V_llena_m_s": _num(hidraulica.V_llena_m_s),
            "V_salida_m_s": (None if hidraulica.V_salida is None
                             else _num(hidraulica.V_salida.valor)),
            "V_salida_procedencia": (None if hidraulica.V_salida is None
                                     else hidraulica.V_salida.procedencia),
            "y_salida_m": _num(hidraulica.y_salida_m),
            # EL BLOQUE h_o ENTERO (SIS-B-18, mitad JSON): los dos numeros que
            # producen la rama, la rama, el cociente que las dos condiciones
            # de uso acotan y las dos banderas, ya filtradas por control
            # gobernante en M4. Hasta EXT-3 no llegaba ninguna pieza.
            "h_o_m": _num(hidraulica.h_o_m),
            "TW_m": _num(hidraulica.TW_m),
            "ahogado_por_TW": hidraulica.ahogado_por_TW,
            "HW_sobre_D_salida": _num(hidraulica.HW_sobre_D_salida),
            "h_o_fuera_de_rango": hidraulica.h_o_fuera_de_rango,
            "h_o_requiere_cautela": hidraulica.h_o_requiere_cautela,
            # EL PERFIL DE LA LAMINA (E-A): las dos salidas del paso 4.3c/4.3d
            # y lo que V1/V2 compararon. Las claves van LITERALES aqui, y no
            # por desempaquetado, porque el test de EXT-6 lee el contrato del
            # AST de este dict. `None` en cada una si el resultado no trae
            # perfil, que M4 no produce (`_campo_del_perfil`).
            "perfil_tipo": _campo_del_perfil(perfil, lambda p: p.tipo.value),
            "perfil_alcanza_entrada": _campo_del_perfil(
                perfil, lambda p: p.alcanza_entrada),
            "perfil_HW_remanso_m": _campo_del_perfil(
                perfil, lambda p: _num(p.HW_remanso_m)),
            "perfil_HW_aproximado_m": _campo_del_perfil(
                perfil, lambda p: _num(p.HW_aproximado_m)),
            "perfil_sustituye_aproximacion": _campo_del_perfil(
                perfil, lambda p: p.sustituye_aproximacion),
            "perfil_y_entrada_m": _campo_del_perfil(
                perfil, lambda p: _num(p.y_entrada_m)),
            "perfil_y_max_m": _campo_del_perfil(perfil, lambda p: _num(p.y_max_m)),
            "perfil_V_min_m_s": _campo_del_perfil(
                perfil, lambda p: _num(p.V_min_m_s)),
            "perfil_fraccion_llena": _campo_del_perfil(
                perfil, lambda p: _num(p.fraccion_llena)),
            "perfil_longitud_llena_m": _campo_del_perfil(
                perfil, lambda p: _num(p.longitud_llena_m)),
            "perfil_y_asintota_m": _campo_del_perfil(
                perfil, lambda p: _num(p.y_asintota_m)),
            "perfil_comprobacion_manda": _campo_del_perfil(
                perfil, lambda p: p.comprobacion_manda),
            "hw_entrada_piso": (None if hidraulica.piso_hw_entrada is None
                                else hidraulica.piso_hw_entrada.adoptado),
            "hw_entrada_HW_sobre_D_formula": (
                None if hidraulica.piso_hw_entrada is None
                else _num(hidraulica.piso_hw_entrada.HW_sobre_D_formula)),
            "hw_entrada_S_limite_m_m": (
                None if hidraulica.piso_hw_entrada is None
                or hidraulica.piso_hw_entrada.S_limite is None
                else _num(hidraulica.piso_hw_entrada.S_limite)),
}


def _campo_del_perfil(perfil: Optional[PerfilLamina], lector) -> Any:
    """Un campo del perfil para el JSON, o None si el resultado no lo trae."""
    return None if perfil is None else lector(perfil)


def _lineas_fase_6(informe: InformePunto) -> List[str]:
    """
    --- T-8 --- Lo que la Fase 6 añade al d50: el Froude de la salida, el
    apron de HEC-14, la proteccion de la entrada y la profundidad de
    socavacion para el desplante. Los avisos de la fase no van aqui: salen
    con los del punto (`InformePunto.avisos`).
    """
    out: List[str] = []
    p = informe.proteccion
    if p.froude is not None:
        regimen = {True: "supercritico", False: "subcritico o critico",
                   None: "regimen no determinado"}[p.froude.supercritico]
        out.append(f"{SANGRIA_DETALLE}Froude de HEC-14 a la salida: Fr_e = "
                   f"{_fmt(p.froude.Fr)} (ye = "
                   f"{_fmt(p.froude.y_equivalente)} m, HEC-14 num. 10.1.1); "
                   f"{regimen} por el tirante contra el critico")
    a = p.apron
    if a is not None:
        geometria = ("fuera de la Tabla 10.1" if a.clase is None else
                     f"clase {a.clase}, L = {_fmt(a.longitud)} m, e = "
                     f"{_fmt(a.espesor)} m, ancho final "
                     f"{_fmt(a.ancho_final)} m")
        out.append(f"{SANGRIA_DETALLE}apron de HEC-14: D50 = "
                   f"{_fmt(a.D50_requerido)} m, {geometria} (Sec. 10.2)")
    e = informe.proteccion_entrada
    if e is not None:
        velocidad = ("sin velocidad publicada" if e.V_entrada is None
                     else f"V en la boca = {_fmt(e.V_entrada)} m/s")
        out.append(f"{SANGRIA_DETALLE}entrada: {velocidad}; revestimiento "
                   f"adoptado: {e.revestimiento} (criterio "
                   f"{e.criterio_revestimiento})")
    s = informe.socavacion
    if s is not None:
        valor = (s.origen if s.profundidad_para_desplante is None
                 else f"{_fmt(s.profundidad_para_desplante)} m ({s.origen}), "
                      f"medida desde {s.referencia}"
                      + ("" if s.cota_fondo_de_la_hoya is None else
                         f": fondo de la hoya a "
                         f"{_fmt(s.cota_fondo_de_la_hoya)} msnm"))
        out.append(f"{SANGRIA_DETALLE}socavacion a la salida para el "
                   f"desplante: {valor}")
    return out


def _proteccion_json(p: ProteccionSalida) -> Dict[str, Any]:
    # La clave dice QUE velocidad es, como en el bloque de hidraulica: desde
    # EXT-3 el d50 de Laushey se calcula con la velocidad de SALIDA de HDS-5
    # 3.1.6 (`ResultadoHidraulico.V_salida`), que bajo control de entrada
    # coincide con `V_erosion` y bajo control de salida no. La clave se
    # llamaba "V_erosion_m_s" y habria seguido diciendo una rama que ya no es
    # la que entra: es la ambiguedad que MAT-D1 vino a quitar, al reves.
    salida = {"numeral": p.numeral, "V_salida_m_s": _num(p.V),
              "d50_m": _num(p.d50),
              "espesor_m": _num(p.espesor), "longitud_m": _num(p.longitud),
              "criterio_espesor": p.criterio_espesor,
              "criterio_longitud": p.criterio_longitud,
              "advertencias": list(p.advertencias)}
    # --- T-8 --- Lo que la Fase 6 añade a Laushey. `d50_m`, `espesor_m` y
    # `longitud_m` son los que RIGEN por la regla declarada y llevan siempre
    # numero; `d50_laushey_m` es el del Manual, rija o no. `requerida` es lo
    # que INFORMA el contraste con la Tabla Nº 11: true si la velocidad de
    # salida supera la admisible, false si no la supera (el terreno la
    # resistiria segun la tabla; la proteccion se mantiene igual) y null si
    # el punto no declaro el terreno o si el contraste no concluye
    # (`velocidad_admisible.concluyente` false).
    salida["d50_laushey_m"] = _num(p.d50_laushey)
    salida["rige_la_envolvente"] = p.rige_la_envolvente
    salida["requerida"] = p.requerida
    salida["froude_salida"] = None if p.froude is None else {
        "Fr": _num(p.froude.Fr), "y_equivalente_m": _num(p.froude.y_equivalente),
        "area_m2": _num(p.froude.A), "supercritico": p.froude.supercritico,
        "seccion_llena": p.froude.seccion_llena}
    salida["velocidad_admisible"] = _admisible_json(p.velocidad_admisible)
    a = p.apron
    salida["apron_hec14"] = None if a is None else {
        "D50_requerido_m": _num(a.D50_requerido), "D_m": _num(a.D),
        "D_de_calculo_m": _num(a.D_de_calculo),
        "ajustado_por_supercritico": a.ajustado_por_supercritico,
        "TW_m": _num(a.TW), "TW_de_calculo_m": _num(a.TW_de_calculo),
        "TW_acotado": a.TW_acotado, "clase": a.clase,
        "D50_clase_m": _num(a.D50_clase), "longitud_m": _num(a.longitud),
        "espesor_m": _num(a.espesor), "ancho_final_m": _num(a.ancho_final)}
    c = p.clase_de_la_piedra
    salida["clase_hec14_de_la_piedra"] = None if c is None else {
        "d50_m": _num(c.d50_de_partida), "clase": c.clase,
        "D50_clase_m": _num(c.D50_clase), "longitud_m": _num(c.longitud),
        "espesor_m": _num(c.espesor), "ancho_final_m": _num(c.ancho_final)}
    salida["regla_espesor_longitud"] = p.regla_espesor_longitud
    salida["espesor_adoptado_m"] = _num(p.espesor_adoptado)
    salida["longitud_adoptada_m"] = _num(p.longitud_adoptada)
    f = p.filtro
    salida["filtro"] = None if f is None else {
        "requisito": f.texto, "clase_geotextil": f.clase_geotextil,
        "pasa_200_pct": _num(f.pasa_200_pct), "columna_tabla_511_06": f.columna,
        "permitividad_min_s1": _num(f.permitividad_min_s1),
        "abertura_aparente_max_mm": _num(f.abertura_aparente_max_mm),
        "citas": list(f.citas)}
    return salida


def _admisible_json(v) -> Optional[Dict[str, Any]]:
    """--- T-8 --- La comparacion con la Tabla Nº 11, o null si no se hizo."""
    if v is None:
        return None
    return {"tipo_terreno": v.tipo_terreno, "regimen_flujo": v.regimen_flujo,
            "V_m_s": _num(v.V), "V_admisible_m_s": _num(v.V_admisible),
            "supera": v.supera, "concluyente": v.concluyente}


def _proteccion_entrada_json(p) -> Dict[str, Any]:
    """--- T-8 --- La proteccion de la ENTRADA (INF-5.1.13)."""
    return {"tipo_embocadura": p.tipo_embocadura,
            "V_entrada_m_s": _num(p.V_entrada),
            "revestimiento": p.revestimiento,
            "criterio_revestimiento": p.criterio_revestimiento,
            "elementos": list(p.elementos), "requerida": p.requerida,
            "velocidad_admisible": _admisible_json(p.velocidad_admisible)}


def _socavacion_json(s) -> Dict[str, Any]:
    """
    --- T-8 --- La profundidad de socavacion a la salida que se entrega al
    desplante del cabezal, con su origen, y la hoya estimada si la hay.
    """
    e = s.estimada
    return {"profundidad_para_desplante_m": _num(s.profundidad_para_desplante),
            "origen": s.origen, "declarada_m": _num(s.declarada_m),
            "referencia": s.referencia,
            "cota_referencia_msnm": _num(s.cota_referencia),
            "cota_fondo_de_la_hoya_msnm": _num(s.cota_fondo_de_la_hoya),
            "motivo_no_estimada": s.motivo_no_estimada,
            "hoya_estimada": None if e is None else {
                "metodo": e.metodo, "profundidad_m": _num(e.profundidad),
                "ancho_m": _num(e.ancho), "longitud_m": _num(e.longitud),
                "distancia_al_maximo_m": _num(e.distancia_al_maximo),
                "duracion_min": _num(e.duracion_min),
                "origen_duracion": e.origen_duracion,
                "duracion_por_criterio": e.duracion_por_criterio,
                "duracion_acotada": e.duracion_acotada,
                "duracion_alternativa_min": _num(e.duracion_alternativa_min),
                "profundidad_alternativa_m": _num(e.profundidad_alternativa),
                "Cs": _num(e.Cs), "Ch": _num(e.Ch)}}


def _geometria_t6_json(g: CompatibilidadGeometrica) -> Dict[str, Any]:
    """
    Lo que T-6 añade al bloque `geometria` del JSON: el metodo de la
    longitud con las alturas de terraplen POR EXTREMO (lo que el cabezal por
    punto leera), el origen de la pendiente, la longitud a la clave, el
    desnivel de entrega y los avisos. Todo sale del objeto de 7.B.
    """
    lc, pend = g.longitud_calculada, g.pendiente
    longitud = None if lc is None else {
        "metodo": lc.metodo.value,
        "talud_H_V": _num(lc.talud),
        "bombeo_m_m": _num(lc.bombeo), "peralte_m_m": _num(lc.peralte),
        "cota_borde_entrada_msnm": _num(lc.cota_borde_entrada),
        "cota_borde_salida_msnm": _num(lc.cota_borde_salida),
        "altura_terraplen_entrada_m": _num(lc.altura_entrada),
        "altura_terraplen_salida_m": _num(lc.altura_salida),
        "proyeccion_talud_entrada_m": _num(lc.proyeccion_entrada),
        "proyeccion_talud_salida_m": _num(lc.proyeccion_salida),
        "semilongitud_entrada_m": _num(lc.semilongitud_entrada),
        "semilongitud_salida_m": _num(lc.semilongitud_salida),
    }
    pendiente = None if pend is None else {
        "origen": pend.origen.value,
        "S_cauce": _num(pend.S_cauce),
        "S_declarada": _num(pend.S_declarada),
        "S_minima": _num(pend.S_minima), "S_maxima": _num(pend.S_maxima),
        "procedencia": pend.procedencia,
    }
    return {"longitud_calculo": longitud,
            "S_conducto_origen": pendiente,
            "longitud_a_la_clave_m": _num(g.longitud_a_la_clave),
            "desnivel_entrega_m": _num(g.desnivel_entrega),
            "avisos": list(g.avisos)}


def _geometria_t3_json(g: CompatibilidadGeometrica) -> Dict[str, Any]:
    """
    --- T-3 --- Lo que T-3 añade al bloque `geometria` del JSON: la geometria
    del marco (None para un tubo) y el remanso aguas arriba del canal (None
    fuera de la Familia C). Todo sale del objeto de 7.B; nada se recalcula.
    """
    m, r = g.geometria_marco, g.remanso_canal
    marco = None if m is None else {
        "B_m": _num(m.B_m), "H_m": _num(m.H_m), "celdas": m.celdas,
        "espesor_m": _num(m.espesor_m), "tabique_m": _num(m.tabique_m),
        "ancho_exterior_m": _num(m.ancho_exterior_m),
        "canto_exterior_m": _num(m.canto_exterior_m),
        "cota_fondo_interior_msnm": _num(m.cota_fondo_interior_msnm),
        "cota_clave_interior_msnm": _num(m.cota_clave_interior_msnm),
        "cota_clave_exterior_msnm": _num(m.cota_clave_exterior_msnm),
        "cota_base_exterior_msnm": _num(m.cota_base_exterior_msnm),
        "relleno_sobre_losa_m": _num(m.relleno_sobre_losa_m),
    }
    remanso = None if r is None else {
        "evaluado": r.evaluado,
        "seccion_origen": r.seccion_origen,
        "Q_canal_m3s": _num(r.Q_canal_m3s), "S_canal": _num(r.S_canal),
        "y_normal_canal_m": _num(r.y_normal_canal_m),
        "HW_m": _num(r.HW_m),
        "cota_lamina_entrada_msnm": _num(r.cota_lamina_entrada_msnm),
        "sobreelevacion_m": _num(r.sobreelevacion_m),
        "longitud_minima_m": _num(r.longitud_minima_m),
        # --- T-3 (auditoria, H2 y H3) --- si la cuenta concluye, el tirante
        # critico del canal y, si no concluye, por que.
        "concluye": r.concluye,
        "y_critico_canal_m": _num(r.y_critico_canal_m),
        "motivo_no_concluye": r.motivo_no_concluye,
        "aviso": r.aviso,
    }
    return {"geometria_marco": marco, "remanso_canal": remanso}


def _geometria_json(g: CompatibilidadGeometrica) -> Dict[str, Any]:
    t = g.tamizado
    return {"numeral": g.numeral, "longitud_m": _num(g.longitud),
            "proyeccion_taludes_m": _num(g.proyeccion_taludes),
            "factor_esviaje": _num(g.factor_esviaje),
            "altura_terraplen_m": _num(g.altura_terraplen),
            "S_conducto": _num(g.S_conducto),
            "cota_entrada_msnm": _num(g.cota_entrada.valor),
            # MEDIDA o ADOPTADA. Es la diferencia entre un dato y una
            # eleccion, y el JSON la lleva porque la GUI y cualquier
            # consumidor externo la necesitan igual que la memoria (SIS-A-04).
            #
            # UNA SOLA CLAVE, Y TODO SALE DE `g.cota_entrada` (PC-07). Hasta
            # EXT-4 la clave estaba DUPLICADA en este literal: el rotulo de
            # arriba nacia pisado por un dict que decia `adoptada: True`
            # siempre --- tambien para una cota MEDIDA --- y cuya `regla` se
            # leia del registro global AL EXPORTAR, de modo que declarar
            # despues de correr cambiaba la regla impresa al lado de una
            # cota que no cambio. La regla que produjo el numero viaja ahora
            # con el numero (`CotaDeEntrada.regla`).
            "cota_entrada_origen": {
                "rotulo": g.cota_entrada.rotulo,
                "adoptada": not g.cota_entrada.medida,
                "criterio": M5.CRITERIO_ORIGEN_COTA_ENTRADA,
                "regla": g.cota_entrada.regla,
                "procedencia": g.cota_entrada.procedencia,
                "nota": ("cota MEDIDA: columna cota_fondo_entrada del CSV; "
                         "el criterio no se aplico en este punto"
                         if g.cota_entrada.medida else
                         "no es cota medida: sale de la regla declarada en "
                         "ese criterio mientras el expediente no entregue la "
                         "cota de invert de entrada por punto"),
            },
            "cota_salida_msnm": _num(g.cota_salida), "caida_m": _num(g.caida),
            # --- T-6 --- como salio L, de donde sale la pendiente, el
            # encaje a la clave, el desnivel de entrega y los avisos de 7.B.
            **_geometria_t6_json(g),
            # --- T-3 --- la geometria del marco y el remanso del canal.
            **_geometria_t3_json(g),
            "factible": g.factible,
            "delta_rasante_cm": _num(g.delta_rasante_cm),
            "tamizado": {"provisional": t.provisional,    # T-6
                         "cota_rasante_min_msnm": _num(t.cota_rasante_min),
                         "cota_rasante_actual_msnm": _num(t.cota_rasante_actual),
                         "cota_por_recubrimiento_msnm": _num(t.cota_por_recubrimiento),
                         "cota_por_resguardo_msnm": _num(t.cota_por_resguardo),
                         "condicion_gobernante": t.condicion_gobernante.value,
                         "criterio_gobernante": t.criterio_gobernante,
                         "mensaje": t.mensaje}}


def _espaciamiento_json(e: Espaciamiento) -> Dict[str, Any]:
    salida: Dict[str, Any] = {
        "numeral": e.numeral, "L_normativo_m": _num(e.L_normativo),
        "L_hidraulico_m": _num(e.L_hidraulico),
        "espaciamiento_max_m": _num(e.espaciamiento_max),
        "gobierna": e.gobierna.value,
        "criterio_normativo": e.criterio_normativo,
        # --- T-9 --- de donde salio L_hidraulico: declarado o calculado, y
        # con que cuneta y que escorrentia cuando se calculo.
        "origen_L_hidraulico": e.origen_L_hidraulico,
        "longitud_hidraulica": None}
    lh = e.longitud_hidraulica
    if lh is not None:
        c = lh.capacidad
        salida["longitud_hidraulica"] = {
            "profundidad_m": _num(c.profundidad_m),
            "ancho_m": _num(c.ancho_m),
            "talud_interior_HV": _num(c.talud_interior_HV),
            "talud_exterior_HV": _num(c.talud_exterior_HV),
            "borde_libre_m": _num(c.borde_libre_m),
            "revestimiento": c.revestimiento, "n": _num(c.n),
            "v_limite_m_s": _num(c.v_limite_m_s), "S_cuneta": _num(c.S),
            "Q_llena_m3s": _num(c.Q_llena_m3s),
            "V_llena_m_s": _num(c.V_llena_m_s),
            "Q_velocidad_m3s": _num(c.Q_velocidad_m3s),
            "Q_admisible_m3s": _num(c.Q_admisible_m3s),
            "gobierna_capacidad": c.gobierna,
            "escorrentia_m3s_km2": _num(lh.escorrentia_m3s_km2),
            "origen_escorrentia": lh.origen_escorrentia,
            "ancho_tributario_m": _num(lh.ancho_tributario_m),
            "q_por_metro_m3s_m": _num(lh.q_por_metro_m3s_m),
            "L_hidraulico_m": _num(lh.L_hidraulico),
            # --- T-9 (correcciones, H1) --- como se repartio el aporte: con
            # el tramo (Q / s) o con el area (q · b), y la longitud que el
            # area implica.
            "metodo_aporte": lh.metodo_aporte,
            "Q_aporte_m3s": _num(lh.Q_aporte_m3s),
            "longitud_tramo_m": _num(lh.longitud_tramo_m),
            "s_implicita_m": _num(lh.s_implicita_m)}
    return salida


def _aporte_alivio_json(a: Any) -> Optional[Dict[str, Any]]:
    """--- T-9 (correcciones, H1) --- VB2 (la verificacion va con las demas)."""
    if a is None:
        return None
    c = a.capacidad
    return {"Q_aporte_m3s": _num(a.Q_aporte_m3s),
            "origen_aporte": a.origen_aporte,
            "evaluada": a.verificacion is not None,
            "aviso": a.aviso or None,
            "capacidad": None if c is None else {
                "profundidad_m": _num(c.profundidad_m),
                "ancho_m": _num(c.ancho_m),
                "talud_interior_HV": _num(c.talud_interior_HV),
                "talud_exterior_HV": _num(c.talud_exterior_HV),
                "borde_libre_m": _num(c.borde_libre_m),
                "revestimiento": c.revestimiento, "n": _num(c.n),
                "v_limite_m_s": _num(c.v_limite_m_s), "S_cuneta": _num(c.S),
                "Q_llena_m3s": _num(c.Q_llena_m3s),
                "Q_velocidad_m3s": _num(c.Q_velocidad_m3s),
                "Q_admisible_m3s": _num(c.Q_admisible_m3s),
                "gobierna_capacidad": c.gobierna}}


def _tramo_alivio_json(t: Any) -> Optional[Dict[str, Any]]:
    """--- T-9 --- El tramo de cuneta de VB1 (la verificacion va con las demas)."""
    if t is None:
        return None
    return {"extremo": t.extremo, "origen_extremo": t.origen_extremo,
            "progresiva_km": _num(t.progresiva_km),
            "progresiva_extremo_km": _num(t.progresiva_extremo_km),
            "longitud_m": _num(t.longitud_m),
            "evaluada": t.verificacion is not None,
            "aviso": t.aviso or None,
            # --- T-9 (correcciones, H2 y H3) --- el dato que destraba VB1
            # sin evaluar (es un bloqueo del punto) y los huecos de cuneta
            # que VB1 no mira.
            "falta": t.falta or None,
            "huecos": list(t.avisos)}


def _caudal_json(c: Any) -> Dict[str, Any]:
    """El caudal de diseño de un punto y de donde salio (T-1, Fase 1-bis)."""
    salida: Dict[str, Any] = {
        "Q_m3s": _num(c.Q_m3s), "origen": c.origen, "leyenda": c.leyenda,
        "de_donde": c.de_donde,
        "area_km2": _num(c.area_km2),
        "q_especifico_m3s_km2": _num(c.q_especifico_m3s_km2),
        "lamina_equivalente_mm_h": _num(c.lamina_equivalente_mm_h),
        "tratamiento_fen": c.tratamiento_fen,
        "avisos": list(c.avisos),
        "pasos": [p.codigo for p in c.pasos]}
    if c.calculado:
        salida.update({
            "TR_anios": c.TR_anios, "metodo_tc": c.metodo_tc,
            "tc_min": _num(c.tc_min),
            "duracion_min": _num(c.duracion_min),
            "I_mm_h": _num(c.I_mm_h), "C": _num(c.C),
            "K_uniformidad": _num(c.K_uniformidad),
            "P24_TR_mm": _num(c.P24_TR_mm), "distribucion": c.distribucion,
            "ajustes": [{"distribucion": a.distribucion, "n": a.n,
                         "D": _num(a.D), "d_critico": _num(a.d_critico),
                         "alfa": a.alfa, "acepta": a.acepta,
                         "P_TR_mm": _num(a.P_TR_mm)} for a in c.ajustes]})
    return salida


def _durabilidad_json(dictamen) -> Optional[Dict[str, Any]]:
    """
    El dictamen de la matriz de durabilidad del punto (Sec. 3.3; T-4). None
    solo cuando la etapa se bloqueo, y entonces el bloqueo esta en la lista
    del punto. `aplicada: false` es el caso sin ensayos: la matriz no actuo y
    `resumen` lo dice con el texto de `modelos.DURABILIDAD_SIN_ENSAYOS`.
    """
    if dictamen is None:
        return None
    ensayos = dictamen.ensayos
    return {
        "aplicada": dictamen.aplicada,
        "resumen": dictamen.resumen,
        "ensayos": ({} if ensayos is None else {
            clave: {"valor": getattr(ensayos, clave),
                    "origen": ensayos.origen_de(clave)}
            for clave in ensayos.declarados}),
        "materiales_excluidos": [t.value for t in dictamen.excluidos],
        "suelo_fundacion": dictamen.suelo_fundacion,
        "reglas": [{"ensayo": r.ensayo,
                    "material": None if r.material is None else r.material.value,
                    "efecto": r.efecto.value, "texto": r.texto,
                    "citas": list(r.cita_ids),
                    "criterio": r.criterio or None}
                   for r in dictamen.reglas],
    }


def _lineas_durabilidad(informe: InformePunto) -> List[str]:
    """
    Las lineas de la Sec. 3.3 en el volcado de texto. La primera va SIEMPRE
    --con ensayos o sin ellos--, porque «no se aplico» es un hecho del
    expediente que el lector tiene que ver en cada punto, no deducir de que
    falte un bloque.
    """
    d = informe.durabilidad
    if d is None:
        # Dos casos distintos: la etapa se bloqueo, y se dice; o el punto no
        # llego a la Fase 3 (se detuvo en la Fase 2), y no hay nada que decir.
        if any(b.etapa == ETAPA_DURABILIDAD for b in informe.bloqueos):
            return [f"{SANGRIA}Sec. 3.3 durabilidad: no evaluada (ver "
                    "bloqueos)"]
        return []
    out = [f"{SANGRIA}Sec. 3.3 {d.resumen}"]
    out.extend(f"{SANGRIA}        [{r.efecto.value}] "
               f"{'general' if r.material is None else r.material.value}: "
               f"{r.texto}" for r in d.reglas)
    if not any(r.ensayo == "sucs_fundacion" for r in d.reglas):
        out.append(f"{SANGRIA}        {d.suelo_fundacion}")
    return out


def _punto_json(informe: InformePunto) -> Dict[str, Any]:
    punto = informe.punto
    salida: Dict[str, Any] = {
        "id": punto.id, "progresiva": punto.progresiva_display,
        "familia": punto.familia.value,
        "pendientes_externos": list(punto.pendientes_externos),
        "dimensionado": informe.dimensionado,
        # `S_cauce` ENTRO AQUI POR LA AUDITORIA ADVERSARIAL DE C6. C6 añadio
        # la fila a la memoria HTML y no a este JSON, de modo que el
        # artefacto legible por MAQUINA -- que es ademas el de la linea base
        # -- declaraba `S_cauce` en `datos_pendientes` sobre una corrida que
        # la habia usado, y no publicaba nada que lo contradijera. Publicar
        # la trazabilidad en un solo formato es publicarla a medias.
        "datos_declarados": {"luz_m": _dato_json(informe.luz),
                             "categoria_tr": _dato_json(informe.categoria_tr),
                             "longitud_m": _dato_json(informe.longitud),
                             "TW_m": _dato_json(informe.tw),
                             "S_cauce": _dato_json(informe.s_cauce),
                             # --- T-2 --- el booleano opcional del acceso de
                             # mantenimiento (num. 4.1.1.3.7 d)), o null.
                             "acceso_mantenimiento_previsto":
                                 _dato_json(informe.acceso_mantenimiento)},
        # --- T-2 --- (INF-3.2.8) CON QUE SECCION DEL RECEPTOR SE OBTUVO EL
        # TW, cuando la via la usa: la geometria y si es MEDIDA o ADOPTADA.
        # Y los avisos del punto, con el mismo texto que la memoria.
        "tw_seccion_receptor": _seccion_receptor_json(informe.tw_sec13),
        "avisos": list(informe.avisos()),
        "clasificacion": (None if informe.clasificacion is None
                          else _clasificacion_json(informe.clasificacion)),
        # EL CAUDAL DE DISEÑO CON SU ORIGEN (T-1): declarado por el estudio
        # hidrologico o calculado por la Fase 1-bis. None en la Familia C y
        # cuando el calculo se detuvo (el bloqueo dice por que).
        "caudal": (None if informe.caudal is None
                   else _caudal_json(informe.caudal)),
        "durabilidad": _durabilidad_json(informe.durabilidad),
        "diseno": (None if not informe.dimensionado
                   else _diseno_json(informe.resultado)),
        "proteccion_salida": (None if informe.proteccion is None
                              else _proteccion_json(informe.proteccion)),
        # --- T-8 --- las otras dos piezas de la Fase 6.
        "proteccion_entrada": (
            None if informe.proteccion_entrada is None
            else _proteccion_entrada_json(informe.proteccion_entrada)),
        "socavacion_salida": (None if informe.socavacion is None
                              else _socavacion_json(informe.socavacion)),
        "geometria": (None if informe.geometria is None
                      else _geometria_json(informe.geometria)),
        # --- T-7a --- la embocadura del punto y, a expediente, sus cabezales.
        "cabezal": _cabezal_del_punto_json(informe),
        "estructural": None,
        "espaciamiento_alivio": (None if informe.espaciamiento is None
                                 else _espaciamiento_json(informe.espaciamiento)),
        "tramo_alivio": _tramo_alivio_json(informe.tramo_alivio),
        "aporte_alivio": _aporte_alivio_json(informe.aporte_alivio),
        "iteraciones": [_paso_json(p) for p in informe.traza],
        "verificaciones": [_verificacion_json(fase, v)
                           for fase, v in informe.verificaciones()],
        # Las filas de la tabla de Fase 5 que no se evaluan viajan con el
        # punto igual que la constancia del item 5 de Fase 8: contar menos
        # verificaciones de las ONCE que la hoja de ruta lista no puede
        # quedar como un ejercicio de resta del lector (SIS-A-13 / MAT-O15).
        # Desde S20 la lista esta VACIA -- V4b se cableo en S14 y V2b en S20
        # --, y la clave se conserva por lo mismo que la funcion: su forma es
        # la del conjunto, no la de su contenido de hoy.
        "verificaciones_no_evaluadas": list(M5.verificaciones_no_evaluadas()),
        "bloqueos": [_bloqueo_json(b) for b in informe.bloqueos],
    }
    # --- T-5 --- La Fase 8: lo que eligio y su relleno maximo (los dos
    # alcances, conducto circular dimensionado), la demanda del marco y la
    # cama de apoyo (expediente), y lo que sigue sin verificarse. Las
    # verificaciones F8.* viajan en `verificaciones`, con la fase del diseño.
    if informe.estructural is not None or informe.cama_apoyo is not None:
        salida["estructural"] = _estructural_json(informe)
    return salida


def _estructural_json(informe: InformePunto) -> Dict[str, Any]:
    """--- T-5 --- El bloque `estructural` del punto (INF-3.3.5)."""
    r = informe.estructural
    bloque: Dict[str, Any] = {
        "material": None if r is None else r.material,
        "seleccion": None if r is None else (r.seleccion or None),
        "H_relleno_m": None if r is None else _num(r.H_relleno_m),
        "e_paquete_m": None if r is None else _num(r.e_paquete_m),
        "H_total_m": None if r is None else _num(r.H_total_m),
        "relleno_maximo_m": (None if r is None or r.relleno_maximo_m is None
                             else _num(r.relleno_maximo_m)),
        "avisos": [] if r is None else list(r.avisos),
        "pasos": [] if r is None else [
            {"codigo": p.codigo, "que": p.que,
             "resultado": {"simbolo": p.resultado.simbolo,
                           "valor": _num(p.resultado.valor),
                           "unidad": p.resultado.unidad}}
            for p in r.pasos],
        "demanda_marco": (None if r is None or r.demanda_marco is None else {
            "F_e": _num(r.demanda_marco.F_e),
            "w_tierra_kPa": _num(r.demanda_marco.w_tierra_kPa),
            "w_viva_kPa": _num(r.demanda_marco.w_viva_kPa),
            "w_u_kPa": _num(r.demanda_marco.w_u_kPa),
            "luz_m": _num(r.demanda_marco.luz_m),
            "M_ref_kNm_m": _num(r.demanda_marco.M_u_referencia_kNm_m)}),
        "cama_apoyo": None, "sujecion_relleno_lateral": None, "numeral": None,
        # Lo que no se verifica DEL CONDUCTO DE ESTE PUNTO; la lista de
        # todos los materiales solo cuando el punto trae la cama y no el
        # conducto (auditoria de T-5).
        "verificacion_diferida": list(
            r.diferido if r is not None and r.diferido
            else verificacion_diferida_estructural()),
    }
    if informe.cama_apoyo is not None:
        bloque.update({
            "cama_apoyo": informe.cama_apoyo.cama_apoyo,
            "sujecion_relleno_lateral": informe.cama_apoyo.sujecion_relleno_lateral,
            "numeral": informe.cama_apoyo.numeral})
    return bloque


def _cabezal_json(informe: InformeCabezal) -> Dict[str, Any]:
    cadena = informe.cadena
    return {
        # Cada paso viaja con su etiqueta, su origen y LA CONDICION que su
        # fuente le pone. Sin esos tres campos el JSON daba siete numeros y
        # nada mas: no se podia ver de que filas de la tabla salio F_pga, en
        # que rama de k_h0 cayo la cimentacion ni que regimen de k_v rige, que
        # es justamente lo que hay que revisar de una cadena sismica -- el
        # numero se comprueba solo, el supuesto no se ve.
        "cadena_sismica": (None if cadena is None else {
            "numeral": cadena.numeral, "PGA": _num(cadena.PGA),
            "F_pga": _num(cadena.F_pga), "A_s": _num(cadena.A_s),
            "k_h0": _num(cadena.k_h0), "factor_muro": _num(cadena.factor_muro),
            "k_h": _num(cadena.k_h), "k_v": _num(cadena.k_v),
            "clases_de_sitio": list(cadena.clases_de_sitio),
            "cimentacion_en_roca": cadena.cimentacion_en_roca,
            "pasos": [{"simbolo": p.simbolo, "valor": _num(p.valor),
                       "concepto": p.concepto, "etiqueta": p.etiqueta,
                       "origen": p.origen, "criterio": p.criterio,
                       "condicion": p.condicion} for p in cadena.pasos]}),
        "mononobe_okabe": (None if informe.mononobe_okabe is None else {
            "K_AE": _num(informe.mononobe_okabe.K_AE),
            "K_A": _num(informe.mononobe_okabe.K_A)}),
        # --- T-7a --- la geometria es POR PUNTO: aqui solo la suma.
        "por_punto": [{"punto": c.id_punto, "entrada": c.entrada.tipo,
                       "salida": c.salida.tipo,
                       "H_c_entrada_m": _num(c.entrada.altura_total),
                       "H_c_salida_m": _num(c.salida.altura_total)}
                      for c in informe.por_punto],
        "recubrimientos": [{"condicion": r.condicion,
                            "e060_mm": _num(r.e060_mm),
                            "aashto_mm": _num(r.aashto_mm),
                            "adoptado_mm": _num(r.adoptado_mm),
                            "origen": r.origen, "numeral": r.numeral,
                            "situacion": r.situacion,
                            "categoria": r.categoria,
                            "tabulado_mm": _num(r.tabulado_mm),
                            "factor_ac": _num(r.factor_ac),
                            "piso_aplicado": r.piso_aplicado,
                            "corpus_tabla": r.corpus_tabla,
                            "origen_factor": r.origen_factor,
                            "durabilidad": (
                                None if r.requisitos is None else {
                                    "a_c_max": _num(r.requisitos.a_c_max),
                                    "fc_min_MPa": _num(r.requisitos.fc_min_MPa),
                                    "clase_sulfatos": r.requisitos.clase_sulfatos,
                                    "gobierna_a_c": r.requisitos.gobierna_a_c,
                                    "gobierna_fc": r.requisitos.gobierna_fc,
                                    "cementos_admisibles":
                                        list(r.requisitos.cementos_admisibles),
                                    "numeral": r.requisitos.numeral})}
                           for r in informe.recubrimientos],
        "cuantias_minimas": {k: _num(v) for k, v in informe.cuantias.items()},
        "notas": list(informe.notas),
        "bloqueos": [_bloqueo_json(b) for b in informe.bloqueos],
    }


def informe_json(informe: Informe) -> Dict[str, Any]:
    """
    El expediente completo como dict listo para `json.dump`.

    Todo lo que es ESTADO --- usos, valores efectivos, declarados, huellas ---
    sale de `informe.contexto` (EXT-4): el JSON describe la corrida que hizo
    el informe, no el proceso en el momento de exportar.
    """
    bloqueantes = criterios_bloqueantes(informe)
    contexto = ContextoCorrida.de(informe)
    salida = _informe_json_base(informe, bloqueantes, contexto)
    if informe.hidrologia is not None:
        # Solo cuando la corrida trajo --cuencas y --estacion (T-1): de que
        # archivos salieron las entradas de la Fase 1-bis.
        salida["expediente"]["hidrologia"] = {
            "cuencas": informe.hidrologia.origen_cuencas,
            "estacion": informe.hidrologia.origen_estacion,
            "obras_con_cuenca": sorted(informe.hidrologia.cuencas),
            "estaciones": sorted(informe.hidrologia.estaciones)}
    return salida


def _informe_json_base(informe: Informe, bloqueantes: Any,
                       contexto: Any) -> Dict[str, Any]:
    """El dict del expediente, sin el bloque opcional de la hidrologia."""
    return {
        "expediente": {
            "csv": str(informe.csv), "generado_utc": informe.generado,
            # Las dos huellas de la corrida, las MISMAS que imprime la
            # memoria: la del CSV es de los bytes que M0 leyo (PC-09).
            "csv_sha1": contexto.csv_sha1,
            "criterios_sha1": contexto.criterios_sha1,
            # El corredor para el que se leyeron los [S] de esta corrida, y
            # de que archivo salio (EXT-V-01). La advertencia de corredor NO
            # va aqui: depende del nombre del proyecto, que es presentacion.
            "corredor_del_proyecto": {
                "valor": contexto.dato_efectivo("corredor_del_proyecto").valor,
                "origen": contexto.dato_efectivo("corredor_del_proyecto").origen},
            "puntos": len(informe.puntos),
            "dimensionados": informe.dimensionados,
            "cerrado": informe.cerrado},
        # Constancia del alcance de la corrida (no cosmetica: es la
        # declaracion que la memoria necesita). "cerrado" de arriba se lee AL
        # ALCANCE declarado aqui: lo diferido no cuenta como bloqueo, pero
        # queda listado entero, con su fundamento, en "diferidos".
        "alcance": {
            "nivel": informe.alcance,
            "diferidos": [{"punto": id_punto, **_bloqueo_json(b)}
                          for id_punto, b in informe.diferidos()]},
        "puntos": [_punto_json(p) for p in informe.puntos],
        "cabezal": _cabezal_json(informe.cabezal),
        "datos_sitio": {
            # Valor, trazabilidad, fecha y ORIGEN de la corrida (EXT-10),
            # leidos de la foto: un [S] declarado por sesion viaja con el
            # archivo del que salio, y el del repositorio con el suyo.
            "usados": [{"clave": k, "etiqueta": ds.dato(k).etiqueta,
                        "valor": _num(contexto.dato_efectivo(k).valor),
                        "concepto": ds.dato(k).concepto,
                        "trazabilidad": contexto.dato_efectivo(k).trazabilidad,
                        "ambito": ds.dato(k).ambito,
                        "origen": contexto.dato_efectivo(k).origen,
                        "fecha": contexto.dato_efectivo(k).fecha,
                        "declarado_en_caliente":
                            contexto.dato_efectivo(k).declarado_en_caliente}
                       for k in contexto.datos_usados],
            "sin_valor_declarados": list(contexto.datos_sin_valor),
            "declarados_en_caliente": list(contexto.datos_declarados_en_caliente),
            "trazabilidad_incompleta": ds.datos_con_verificacion_pendiente()},
        "criterios": {
            # Valor EFECTIVO y procedencia: el JSON es el otro reporte de la
            # corrida y tenia el mismo defecto que la memoria HTML -- leia el
            # valor del ARCHIVO, de modo que un criterio declarado en
            # caliente viajaba con "valor": null mientras gobernaba el
            # calculo (SIS-A-01). Y desde EXT-4 el valor efectivo es el DE LA
            # CORRIDA, no el del proceso al exportar (EXT-A-01).
            "usados": [{"clave": k,
                        "etiqueta": ca.criterio(k).etiqueta,
                        "valor": _num(contexto.valor_efectivo(k)),
                        "declarado_en_caliente": contexto.declarado_en_caliente(k),
                        "concepto": ca.criterio(k).concepto}
                       for k in contexto.criterios_usados],
            "sin_valor_declarados": list(contexto.criterios_sin_valor),
            "declarados_en_caliente": list(contexto.declarados_en_caliente),
            # Hermano de `trazabilidad_incompleta` de los datos de sitio: sin
            # el, un consumidor del JSON veia que datos de sitio quedaban sin
            # cerrar documentalmente y no veia que criterios (SIS-D-07).
            "verificacion_pendiente": list(
                contexto.criterios_con_verificacion_pendiente),
            "sin_consumidor": ca.criterios_sin_consumidor(),
            "bloquearon": [{"clave": c.clave, "etiqueta": c.etiqueta,
                            "concepto": c.concepto, "fuente": c.fuente,
                            "reemplazado_por": c.reemplazado_por,
                            "fases": list(c.fases), "etapas": list(c.etapas),
                            "puntos": list(c.puntos),
                            # True cuando TODO lo que este criterio detuvo
                            # estaba diferido por alcance (EXT-G-02): no
                            # bloquea el cierre de esta corrida.
                            "diferido": c.diferido,
                            # QUIEN lo fija y CON QUE evidencia (E-B, E13
                            # reducido), derivados de la ficha: las mismas
                            # dos columnas que la pestaña 4 y el anticipo.
                            "responsable": c.responsable,
                            "evidencia": c.evidencia}
                           for c in bloqueantes]},
    }


# ===========================================================================
# Volcado a stdout
# ===========================================================================

def _titulo(texto: str, marca: str = "=") -> List[str]:
    return [marca * ANCHO, texto, marca * ANCHO]


def _lineas_verificaciones(informe: InformePunto) -> List[str]:
    filas = informe.verificaciones()
    if not filas:
        return []
    out = [f"{SANGRIA}Verificaciones:"]
    for fase, v in filas:
        if v.estado is EstadoDeVerificacion.NO_APLICA:
            marca = MARCA_NO_APLICA
        elif _veredicto_de(v) == TipoDeVeredicto.INDICADOR.value:
            marca = MARCA_INDICADOR
        else:
            marca = MARCA_CUMPLE if v.cumple else MARCA_INCUMPLE
        codigo = v.codigo or fase.split(" - ")[0]
        out.append(f"{SANGRIA * 2}{marca} {codigo:<4} {v.numeral:<28} "
                   f"obtenido {_fmt(v.valor_obtenido)} | admisible "
                   f"{_fmt(v.valor_admisible)}")
        if v.estado is EstadoDeVerificacion.NO_APLICA:
            out.append(f"{SANGRIA_DETALLE}no aplica: {v.motivo_no_aplica}")
        if v.criterio_aplicado:
            # Consulta tolerante: una clave que no este en CRITERIOS se imprime
            # tal cual, sin etiqueta. Un desajuste de nombre es un problema de
            # reporte y no puede tumbar la memoria del punto.
            declarado = ca.CRITERIOS.get(v.criterio_aplicado)
            etiqueta = f" [{declarado.etiqueta}]" if declarado is not None else ""
            out.append(f"{SANGRIA_DETALLE}umbral del criterio "
                       f"'{v.criterio_aplicado}'{etiqueta}")
    return out


def _lineas_bloqueos(bloqueos: Sequence[Bloqueo]) -> List[str]:
    if not bloqueos:
        return []
    out = [f"{SANGRIA}Bloqueos:"]
    for b in bloqueos:
        out.append(f"{SANGRIA * 2}[{b.tipo.value}] {b.fase} -> {b.etapa}")
        if b.criterio:
            out.append(f"{SANGRIA_DETALLE}falta declarar: {b.criterio} "
                       f"[{b.etiqueta}] - {b.concepto}")
            out.append(f"{SANGRIA_DETALLE}fuente: {b.fuente}")
        else:
            out.append(f"{SANGRIA_DETALLE}{b.mensaje}")
    return out


def _lineas_punto(informe: InformePunto) -> List[str]:
    punto = informe.punto
    out = ["-" * ANCHO,
           f"{punto.id}  |  progresiva {punto.progresiva_display}  |  "
           f"Familia {punto.familia.value}",
           "-" * ANCHO]

    if informe.clasificacion is not None:
        c = informe.clasificacion
        tr = (f"TR {c.periodo_retorno.anios} anios"
              if c.periodo_retorno.anios is not None
              else "TR no procede (ver fundamento en el JSON)")
        out.append(f"{SANGRIA}Fase 2  {c.denominacion.value} "
                   f"(luz {_fmt(c.luz_m)} m, num. {c.verificacion_luz.numeral}) "
                   f"| {tr}")

    if informe.caudal is not None:
        c = informe.caudal
        especifico = ("" if c.q_especifico_m3s_km2 is None else
                      f" | Q/A = {_fmt(c.q_especifico_m3s_km2)} m3/s por km2 "
                      f"(C*I = {_fmt(c.lamina_equivalente_mm_h, DECIMALES_FACTOR)} mm/h)")
        out.append(f"{SANGRIA}Fase 1b {c.leyenda}: Q = {_fmt(c.Q_m3s)} m3/s"
                   f"{especifico}")
        if c.calculado:
            out.append(f"{SANGRIA}        Hidrologia: TR {c.TR_anios} anios, "
                       f"P24 = {_fmt(c.P24_TR_mm, DECIMALES_FACTOR)} mm "
                       f"({c.distribucion}; FEN: {c.tratamiento_fen}), "
                       f"tc = {_fmt(c.tc_min, DECIMALES_FACTOR)} min, "
                       f"I = {_fmt(c.I_mm_h, DECIMALES_FACTOR)} mm/h, "
                       f"C = {_fmt(c.C, DECIMALES_FACTOR)}, "
                       f"A = {_fmt(c.area_km2)} km2")
        # Los avisos de la Fase 1-bis NO se imprimen aqui: salen con los
        # demas del punto, por `InformePunto.avisos()` (T-2), una sola vez.
    out.extend(_lineas_durabilidad(informe))

    if informe.dimensionado:
        r = informe.resultado
        h = r.resultado_hidraulico
        out.append(f"{SANGRIA}Fase 4  Material : {r.material.nombre} "
                   f"({r.material.norma_producto})")
        out.append(f"{SANGRIA}        Seccion  : "
                   f"{r.seccion.etiqueta()} (interior)")
        out.append(f"{SANGRIA}        Control  : {h.control_gobernante.value} "
                   f"(HW = {_fmt(h.HW)} m; entrada {_fmt(h.HW_entrada)} / "
                   f"salida {_fmt(h.HW_salida)})")
        if h.sin_tirante_normal:
            # --- T-2 --- Barril horizontal (S = 0): no hay tirante normal ni
            # velocidades de Manning que imprimir, y se dice (INF-5.1.6).
            out.append(f"{SANGRIA}        Hidraulica: BARRIL HORIZONTAL, sin "
                       f"tirante normal ni velocidad uniforme (HDS-5 3.3.4); "
                       f"y_c = {_fmt(h.y_critico)} m, "
                       f"Q = {_fmt(h.Q)} m3/s, S = "
                       f"{_fmt(h.S, DECIMALES_PENDIENTE)} m/m")
        else:
            out.append(f"{SANGRIA}        Hidraulica: y_n = {_fmt(h.y_normal)} m, "
                       f"y_c = {_fmt(h.y_critico)} m, "
                       f"V_erosion = {_fmt(h.V_erosion)} m/s (n min), "
                       f"V_sedimentacion = {_fmt(h.V_sedimentacion)} m/s (n max), "
                       f"Q = {_fmt(h.Q)} m3/s, S = {_fmt(h.S, DECIMALES_PENDIENTE)} m/m")
        out.append(f"{SANGRIA}        Longitud : L = {_fmt(informe.longitud.valor)} m "
                   f"({informe.longitud.origen}) | TW = "
                   f"{_fmt(informe.tw.valor)} m ({informe.tw.origen})")
        # EL REGIMEN Y EL BLOQUE h_o (EXT-3; SIS-B-18): lo que V1/V2
        # compararon, lo que recibio la Fase 6 y las dos condiciones de uso
        # de la aproximacion, dichas en el punto.
        v_sal = ("sin emitir" if h.V_salida is None
                 else f"{_fmt(h.V_salida.valor)} m/s")
        out.append(f"{SANGRIA}        Regimen  : {h.regimen_barril.value} | "
                   f"V_llena = {_fmt(h.V_llena_m_s)} m/s | "
                   f"V_salida = {v_sal} (HDS-5 3.1.6, y_salida = "
                   f"{_fmt(h.y_salida_m)} m)")
        # HW/D_salida es el de la APROXIMACION del paso 4.3 (el cociente que
        # las dos condiciones juzgan); que se use o no lo dice la linea del
        # perfil (E-A). `usa fuera de rango` es la bandera de la compuerta.
        out.append(f"{SANGRIA}        h_o      : {_fmt(h.h_o_m)} m "
                   f"({'manda TW: salida ahogada' if h.ahogado_por_TW else 'manda (y_c + D)/2'}; "
                   f"TW = {_fmt(h.TW_m)} m) | HW_aprox/D = "
                   f"{_fmt(h.HW_sobre_D_salida)} | usa la aproximacion fuera de "
                   f"rango (< {_fmt(H_O_HW_SOBRE_D_MIN, DECIMALES_FACTOR)}): "
                   f"{'si' if h.h_o_fuera_de_rango else 'no'} | cautela: "
                   f"{'si' if h.h_o_requiere_cautela else 'no'}")
        # EL PERFIL DE LA LAMINA (E-A): las dos salidas del paso 4.3c/4.3d.
        if h.perfil is not None:
            pf = h.perfil
            remanso = ("no alcanza la entrada" if not pf.alcanza_entrada
                       else f"{_fmt(pf.HW_remanso_m)} m")
            papel = ("sustituye a la aproximacion (HW_aprox/D < 0.75)"
                     if pf.sustituye_aproximacion
                     else "manda: la comprobacion pide mas carga que la aproximacion"
                     if pf.comprobacion_manda
                     else "comprueba la aproximacion, que sigue siendo la carga")
            out.append(f"{SANGRIA}        Perfil   : {pf.tipo.value} | lleno en "
                       f"{_fmt(pf.longitud_llena_m)} m de {_fmt(informe.longitud.valor)} m "
                       f"(fraccion {_fmt(pf.fraccion_llena)}) | HW por remanso = "
                       f"{remanso} ({papel}) | y_max = {_fmt(pf.y_max_m)} m, "
                       f"V_min = {_fmt(pf.V_min_m_s)} m/s")
    else:
        out.append(f"{SANGRIA}Fase 4  sin dimensionar")

    # LA PENDIENTE DEL CAUCE, JUSTO ENCIMA DE LA VERIFICACION QUE LA CONSUME.
    # Va aqui y no dentro de la rama de `dimensionado` porque el punto que se
    # detiene antes tambien la declaro, y porque V2b es lo siguiente que se
    # imprime. La segunda auditoria de C6 midio que este volcado -- que es
    # linea base como los otros dos -- publicaba `longitud` y `tw` CON su
    # procedencia y `s_cauce` no: dos formatos de tres, sobre el argumento de
    # que publicarla en uno solo es publicarla a medias.
    if informe.s_cauce is not None:
        out.append(f"{SANGRIA}        S_cauce  : "
                   f"{_fmt(informe.s_cauce.valor, DECIMALES_PENDIENTE)} m/m "
                   f"({informe.s_cauce.origen})")

    out.extend(_lineas_verificaciones(informe))

    if informe.proteccion is not None:
        p = informe.proteccion
        if p.rige_la_envolvente:
            # LA LINEA SEPARA LOS ORIGENES (H1 de la segunda auditoria de
            # T-8): con la envolvente, el espesor y la longitud salen de la
            # Tabla 10.1 de HEC-14 y no del numeral del Manual, que solo da
            # el d50 de Laushey.
            out.append(f"{SANGRIA}Fase 6  d50 = {_fmt(p.d50_laushey)} m "
                       f"(num. {p.numeral}); rige la envolvente con HEC-14: "
                       f"d50 {_fmt(p.d50)} m, espesor {_fmt(p.espesor)} m, "
                       f"longitud {_fmt(p.longitud)} m (Ec. 10.4 y Tabla "
                       "10.1)")
        else:
            out.append(f"{SANGRIA}Fase 6  d50 = {_fmt(p.d50)} m, espesor "
                       f"{_fmt(p.espesor)} m, longitud {_fmt(p.longitud)} m "
                       f"(num. {p.numeral})")
        for advertencia in p.advertencias:
            out.append(f"{SANGRIA_DETALLE}aviso: {advertencia}")
        out.extend(_lineas_fase_6(informe))
    if informe.geometria is not None:
        g = informe.geometria
        # La cota de entrada NO es un dato del CSV: sale de la regla que el
        # proyectista declaro en 'origen_cota_fondo_entrada'. Va marcada en
        # las TRES salidas (texto, JSON y HTML) y no solo en la memoria: la
        # GUI pinta el detalle del punto con estas mismas lineas, y un numero
        # en msnm sin marca se lee como cota levantada en campo (SIS-A-04).
        # LA MARCA DICE CUAL DE LAS DOS FUE, y ya no afirma «ADOPTADA»
        # siempre: desde que el CSV trae `cota_fondo_entrada`, la cota puede
        # venir MEDIDA, y decir que se adopto seria falso justo en el punto
        # donde el dato es mejor.
        out.append(f"{SANGRIA}Fase 7  L = {_fmt(g.longitud)} m, cota entrada "
                   f"{_fmt(g.cota_entrada.valor)} "
                   f"({g.cota_entrada.rotulo}) "
                   f"/ salida {_fmt(g.cota_salida)} msnm")
        out.append(f"{SANGRIA_DETALLE}cota de entrada: "
                   f"{g.cota_entrada.procedencia}")
        # --- T-6 --- el metodo de L, la pendiente con su origen, el encaje
        # a la clave, con las mismas palabras del objeto de 7.B.
        if g.longitud_calculada is not None:
            detalle = f"longitud: metodo {g.longitud_calculada.metodo.value}"
            if g.longitud_a_la_clave is not None:
                detalle += (f"; entre cabezales a la clave "
                            f"{_fmt(g.longitud_a_la_clave)} m")
            out.append(f"{SANGRIA_DETALLE}{detalle}")
        if g.pendiente is not None:
            out.append(f"{SANGRIA_DETALLE}pendiente: S = "
                       f"{_fmt(g.S_conducto, DECIMALES_PENDIENTE)} m/m "
                       f"({g.pendiente.origen.value}); caida "
                       f"{_fmt(g.caida)} m")
        # --- T-3 --- la geometria del marco, con las palabras del objeto.
        m = g.geometria_marco
        if m is not None:
            out.append(f"{SANGRIA_DETALLE}marco: {m.celdas} celda(s), "
                       f"t = {_fmt(m.espesor_m)} m; exterior "
                       f"{_fmt(m.ancho_exterior_m)} x "
                       f"{_fmt(m.canto_exterior_m)} m; clave exterior "
                       f"{_fmt(m.cota_clave_exterior_msnm)} msnm; relleno "
                       f"sobre la losa {_fmt(m.relleno_sobre_losa_m)} m")
        # Los avisos de 7.B NO se imprimen aqui: salen con los demas del
        # punto, por `InformePunto.avisos()`, una sola vez (y tambien cuando
        # el punto no dimensiona).
        out.append(f"{SANGRIA_DETALLE}{g.tamizado.mensaje}")
    # --- T-5 --- La Fase 8 del conducto: lo elegido y su relleno maximo, o
    # la demanda del marco; los avisos salen con los del punto.
    r = informe.estructural
    if r is not None and r.demanda_marco is not None:
        out.append(f"{SANGRIA}Fase 8  marco: diseño del portico diferido al "
                   f"expediente; demanda M_ref = "
                   f"{_fmt(r.demanda_marco.M_u_referencia_kNm_m)} kN.m/m")
    elif r is not None:
        maximo = ("-" if r.relleno_maximo_m is None
                  else f"{_fmt(r.relleno_maximo_m)} m")
        # El contraste con la instalacion Tipo 4 del tubo de concreto (no
        # rige), leido del paso que M8 emite: la CLI no calcula.
        tipo4 = next((p for p in r.pasos
                      if p.codigo == CODIGO_PASO_HMAX_TIPO4), None)
        contraste = ("" if tipo4 is None else
                     f" (con instalacion Tipo 4: {_fmt(tipo4.resultado.valor)} m)")
        out.append(f"{SANGRIA}Fase 8  {r.seleccion or 'ninguna cumple'}; "
                   f"relleno {_fmt(r.H_relleno_m)} m + paquete "
                   f"{_fmt(r.e_paquete_m)} m; relleno maximo {maximo}"
                   f"{contraste}")
    if informe.cama_apoyo is not None:
        out.append(f"{SANGRIA}Fase 8  cama: {informe.cama_apoyo.cama_apoyo} "
                   f"(num. {informe.cama_apoyo.numeral})")
    out.extend(_lineas_cabezal_del_punto(informe))
    if informe.espaciamiento is not None:
        e = informe.espaciamiento
        out.append(f"{SANGRIA}Fase 10 espaciamiento max = "
                   f"{_fmt(e.espaciamiento_max)} m (gobierna {e.gobierna.value}; "
                   f"normativo {_fmt(e.L_normativo)} / hidraulico "
                   f"{_fmt(e.L_hidraulico)}, {e.origen_L_hidraulico})")
        # --- T-9 --- con la longitud calculada, como se repartio el aporte.
        lh = e.longitud_hidraulica
        if lh is not None:
            out.append(f"{SANGRIA_DETALLE}{lh.metodo_aporte}: q' = "
                       f"{lh.q_por_metro_m3s_m:.3e} m3/s por m; "
                       f"L_hidraulico = {_fmt(lh.L_hidraulico)} m")
    # --- T-9 (correcciones, H1) --- la cuneta y su capacidad, de la que VB2
    # juzga el aporte (la verificacion sale en la tabla de arriba).
    aporte = informe.aporte_alivio
    if aporte is not None and aporte.capacidad is not None:
        c = aporte.capacidad
        out.append(f"{SANGRIA}Fase 10 cuneta {_fmt(c.profundidad_m)} x "
                   f"{_fmt(c.ancho_m)} m ({c.revestimiento}, S = "
                   f"{_fmt(c.S, DECIMALES_PENDIENTE)} m/m): Q_adm = "
                   f"{_fmt(c.Q_admisible_m3s, DECIMALES_PENDIENTE)} m3/s "
                   f"({c.gobierna}); Q de aporte = "
                   f"{_fmt(aporte.Q_aporte_m3s, DECIMALES_PENDIENTE)} m3/s")
    # --- T-9 --- el tramo de VB1 (la verificacion sale en la tabla de arriba;
    # el tramo sin evaluar sale en los avisos).
    tramo = informe.tramo_alivio
    if tramo is not None and tramo.longitud_m is not None:
        out.append(f"{SANGRIA}Fase 10 tramo de cuneta (VB1): "
                   f"{_fmt(tramo.longitud_m)} m desde {tramo.extremo} "
                   f"({tramo.origen_extremo})")

    # --- T-2 --- Los avisos del punto (TW con la seccion adoptada del
    # receptor, acceso de mantenimiento declarado como no previsto) y la
    # declaracion del acceso cuando si esta previsto. Van tambien cuando el
    # punto no dimensiona: el TW adoptado puede ser justamente el motivo.
    acceso = informe.acceso_mantenimiento
    if acceso is not None and acceso.valor is True:
        out.append(f"{SANGRIA}Acceso de mantenimiento: previsto en los planos "
                   f"({acceso.origen}; exigencia del num. 4.1.1.3.7 d))")
    for aviso in informe.avisos():
        out.append(f"{SANGRIA}aviso: {aviso}")

    out.extend(_lineas_bloqueos(informe.bloqueos))
    return out


def _lineas_cabezal_del_punto(informe: InformePunto) -> List[str]:
    """
    --- T-7a --- La Fase 9 del punto: la embocadura (siempre que se
    resolvio) y, a expediente, los dos cabezales con su geometria resumida.
    La tabla completa, dimension por dimension con su origen, va en el JSON
    y en la memoria; aqui, una linea por cabezal.
    """
    out: List[str] = []
    e = informe.embocadura
    if e is not None:
        angulo = ("sin aleros" if e.angulo_aletas is None
                  else f"aleros a {_fmt(e.angulo_aletas, 1)} grados con la "
                       "pared del barril")
        # La coherencia del marco con el cabezal, cuando la hubo, va en la
        # MISMA linea y sin texto propio: es un dato del punto (el JSON lleva
        # la nota entera), no un aviso, y con las filas de 30 a 75 grados
        # se cumple siempre (correcciones de T-7a).
        coherente = ("; coherente con la embocadura del marco"
                     if informe.coherencia_embocadura else "")
        out.append(f"{SANGRIA}Embocadura: {e.tipo} ({angulo}; {e.regla})"
                   f"{coherente}")
    c = informe.cabezal
    if c is None:
        return out
    for g in c.geometrias:
        aleros = ("sin aleros" if g.aleros is None else
                  f"aleros {_fmt(g.aleros.angulo_grados, 1)} grados x "
                  f"{_fmt(g.aleros.longitud_corto, 2)} / "
                  f"{_fmt(g.aleros.longitud_largo, 2)} m (corto / largo)")
        out.append(
            f"{SANGRIA}Fase 9  cabezal de {g.extremo}: {g.tipo}, H_c = "
            f"{_fmt(g.altura_total, 2)} m (corona {_fmt(g.cota_coronacion)} / "
            f"desplante {_fmt(g.cota_desplante)} msnm, D_f = "
            f"{_fmt(g.D_f, 2)} m), L_c = {_fmt(g.longitud, 2)} m, zapata "
            f"B = {_fmt(g.B, 2)} x {_fmt(g.espesor_zapata, 2)} m, pantalla "
            f"{_fmt(g.espesor_corona, 2)} m, {aleros}, losa "
            f"{_fmt(g.losa.longitud, 2)} x {_fmt(g.losa.espesor, 2)} m con "
            f"dentellon de {_fmt(g.losa.profundidad_dentellon, 2)} m")
        declaradas = [d.nombre for d in g.dimensiones
                      if d.origen == ORIGEN_DIMENSION_DECLARADA]
        derivadas = [d.nombre for d in g.dimensiones
                     if d.origen == ORIGEN_DIMENSION_DERIVADA]
        out.append(f"{SANGRIA_DETALLE}dimensiones: "
                   + ("todas propuestas por regla"
                      if not declaradas and not derivadas else
                      ("declaradas " + ", ".join(declaradas) + "; "
                       if declaradas else "")
                      + ("derivadas de las declaradas " + ", ".join(derivadas)
                         + "; " if derivadas else "")
                      + "el resto propuestas por regla"))
    if c.longitud_entre_cabezales is not None:
        out.append(f"{SANGRIA_DETALLE}longitud entre cabezales "
                   f"{_fmt(c.longitud_entre_cabezales)} m entre trasdos, "
                   f"{_fmt(c.longitud_metrado)} m de metrado (el diseño "
                   "hidraulico sigue con la aproximada de 7.B)")
    else:
        out.append(f"{SANGRIA_DETALLE}longitud entre cabezales: no se "
                   f"calcula ({c.motivo_sin_longitud})")
    return out


def _cabezal_del_punto_json(informe: InformePunto) -> Optional[Dict[str, Any]]:
    """--- T-7a --- La embocadura y el cabezal del punto, para el JSON."""
    e = informe.embocadura
    if e is None and informe.cabezal is None:
        return None
    salida: Dict[str, Any] = {
        # Los criterios que la decidieron, SIN el vacio del angulo cuando
        # el cabezal es recto (correcciones de T-7a, H9).
        "embocadura": (None if e is None else {
            "tipo": e.tipo, "angulo_aletas_grados": _num(e.angulo_aletas),
            "regla": e.regla,
            "criterios": [x for x in (e.criterio_tipo, e.criterio_angulo)
                          if x]}),
        "coherencia_embocadura_marco": informe.coherencia_embocadura,
        "cabezales": None,
    }
    c = informe.cabezal
    if c is None:
        return salida

    def _geom(g) -> Dict[str, Any]:
        return {
            "extremo": g.extremo, "tipo": g.tipo,
            "cota_coronacion_msnm": _num(g.cota_coronacion),
            "cota_desplante_msnm": _num(g.cota_desplante),
            "H_c_m": _num(g.altura_total), "H_sobre_zapata_m": _num(g.H),
            "D_f_m": _num(g.D_f), "L_c_m": _num(g.longitud),
            "B_m": _num(g.B), "espesor_zapata_m": _num(g.espesor_zapata),
            "ancho_punta_m": _num(g.ancho_punta),
            "ancho_talon_m": _num(g.ancho_talon),
            "espesor_corona_m": _num(g.espesor_corona),
            "espesor_base_muro_m": _num(g.espesor_base_muro),
            "beta_grados": _num(g.beta_grados),
            "aleros": (None if g.aleros is None else {
                "angulo_grados": _num(g.aleros.angulo_grados),
                "angulo_largo_grados": _num(g.aleros.angulo_largo_grados),
                "esviaje_grados": _num(g.aleros.esviaje_grados),
                "longitud_corto_m": _num(g.aleros.longitud_corto),
                "longitud_largo_m": _num(g.aleros.longitud_largo),
                "altura_inicial_m": _num(g.aleros.altura_inicial),
                "altura_final_m": _num(g.aleros.altura_final),
                "espesor_m": _num(g.aleros.espesor),
                "ancho_zapata_m": _num(g.aleros.ancho_zapata),
                "espesor_zapata_m": _num(g.aleros.espesor_zapata)}),
            "losa": (None if g.losa is None else {
                "longitud_m": _num(g.losa.longitud),
                "espesor_m": _num(g.losa.espesor),
                "profundidad_dentellon_m": _num(g.losa.profundidad_dentellon),
                "ancho_dentellon_m": _num(g.losa.ancho_dentellon),
                "cota_terreno_msnm": _num(g.losa.cota_terreno),
                "cota_base_dentellon_msnm": _num(g.losa.cota_base_dentellon)}),
            "dimensiones": [{"nombre": d.nombre, "valor": _num(d.valor),
                             "unidad": d.unidad, "origen": d.origen,
                             "regla": d.regla, "criterio": d.criterio}
                            for d in g.dimensiones]}

    salida["cabezales"] = [_geom(g) for g in c.geometrias]
    salida["longitud_entre_cabezales_m"] = _num(c.longitud_entre_cabezales)
    salida["longitud_metrado_m"] = _num(c.longitud_metrado)
    salida["motivo_sin_longitud_entre_cabezales"] = c.motivo_sin_longitud
    return salida


def _lineas_cabezal(informe: InformeCabezal) -> List[str]:
    out = _titulo(f"{FASE_CABEZAL} - del proyecto, no del punto", "-")
    # --- T-7a --- la geometria es POR PUNTO (va en cada punto); aqui, la
    # suma: cuantos cabezales se propusieron.
    if informe.por_punto:
        out.append(f"{SANGRIA}Cabezales por punto: "
                   + ", ".join(f"{c.id_punto} ({c.entrada.tipo} / "
                               f"{c.salida.tipo})" for c in informe.por_punto)
                   + " -- la geometria de cada uno va con su punto")
    if informe.cadena is not None:
        c = informe.cadena
        out.append(f"{SANGRIA}Cadena sismica (num. {c.numeral}): "
                   f"PGA {_fmt(c.PGA, 2)} g -> A_s {_fmt(c.A_s, 2)} g -> "
                   f"k_h {_fmt(c.k_h, 2)} | k_v {_fmt(c.k_v, 2)}")
        # La condicion de cada eslabon, debajo del resumen: es lo que separa
        # una cadena revisable de siete numeros que coinciden por casualidad.
        for paso in c.pasos:
            if paso.condicion:
                out.append(f"{SANGRIA * 2}{paso.simbolo} "
                           f"[{paso.etiqueta}]: {paso.condicion}")
    for r in informe.recubrimientos:
        out.append(f"{SANGRIA}Recubrimiento '{r.condicion}': "
                   f"{_fmt(r.adoptado_mm, 1)} mm (gobierna {r.origen}, "
                   f"{r.numeral})")
        # La cadena del lado AASHTO, debajo del resultado: sin ella el numero
        # vuelve a ser un valor que hay que creer. Es la misma razon por la
        # que la cadena sismica imprime la condicion de cada eslabon.
        out.append(f"{SANGRIA * 2}lado AASHTO: fila '{r.situacion}', "
                   f"categoria de acero '{r.categoria}' -> "
                   f"{_fmt(r.tabulado_mm, 1)} mm de tabla x {r.factor_ac} "
                   f"por relacion a/c = {_fmt(r.aashto_mm, 1)} mm"
                   + (" (piso de 1.0 in aplicado)" if r.piso_aplicado else "")
                   + f"; {r.corpus_tabla}")
        # DE DONDE SALE EL FACTOR, no solo cuanto vale. Un 1.2 puede ser "la
        # a/c maxima es 0.50 o mas" o "no hay a/c contra la que evaluarlo y se
        # toma el mas exigente": son dos situaciones distintas del expediente
        # y la memoria tiene que poder distinguirlas sin abrir el codigo.
        out.append(f"{SANGRIA * 2}factor por a/c: {r.origen_factor}")
        if r.requisitos is not None:
            out.append(
                f"{SANGRIA * 2}durabilidad del concreto: a/c maxima "
                f"{r.requisitos.a_c_max} (gobierna {r.requisitos.gobierna_a_c}), "
                f"f'c minimo {r.requisitos.fc_min_MPa} MPa "
                f"(gobierna {r.requisitos.gobierna_fc}); exposicion a "
                f"sulfatos '{r.requisitos.clase_sulfatos}'")
    for direccion, cuantia in informe.cuantias.items():
        out.append(f"{SANGRIA}Cuantia minima {direccion}: {cuantia}")
    for nota in informe.notas:
        out.append(f"{SANGRIA * 2}nota: {nota}")
    out.extend(_lineas_bloqueos(informe.bloqueos))
    return out


def _lineas_criterios_bloqueantes(informe: Informe) -> List[str]:
    bloqueantes = criterios_bloqueantes(informe)
    out = _titulo("CRITERIOS PENDIENTES QUE BLOQUEARON UNA ETAPA")
    if not bloqueantes:
        out.append("Ninguno: ningun criterio sin valor se invoco en esta corrida.")
        return out
    for c in bloqueantes:
        puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
        out.append(f"[{c.etiqueta}] {c.clave}")
        out.append(f"{SANGRIA}Concepto : {c.concepto}")
        out.append(f"{SANGRIA}Fuente   : {c.fuente}")
        if c.reemplazado_por:
            out.append(f"{SANGRIA}Lo resuelve: {c.reemplazado_por}")
        out.append(f"{SANGRIA}Bloqueo  : {'; '.join(c.etapas)}")
        out.append(f"{SANGRIA}Puntos   : {puntos}")
        if c.diferido:
            out.append(f"{SANGRIA}Diferido : por alcance; no cuenta para el "
                       "cierre de esta corrida (ver ALCANCE DE LA CORRIDA)")
        out.append("")
    return out


def _lineas_alcance(informe: Informe) -> List[str]:
    """
    La declaracion de alcance de la corrida. En alcance de expediente basta
    la linea; en alcance de perfil se lista TODO lo diferido con su
    fundamento: es la constancia que la memoria de tesis necesita para que
    "cerrado" no se lea como "expediente completo".
    """
    out = _titulo("ALCANCE DE LA CORRIDA")
    out.append(f"Alcance declarado: {informe.alcance} (bandera --alcance; "
               f"por defecto {ALCANCE_EXPEDIENTE})")
    diferidos = informe.diferidos()
    if not diferidos:
        out.append("Ninguna etapa diferida por alcance: la corrida ejecuto "
                   "el pipeline completo.")
        return out
    out.append("Diferido al expediente por alcance (registrado con su "
               "fundamento; NO cuenta como bloqueo para el cierre):")
    for id_punto, b in diferidos:
        donde = id_punto if id_punto is not None else "proyecto"
        out.append(f"{SANGRIA}[{donde}] {b.fase}")
        out.append(f"{SANGRIA * 2}{b.etapa}")
        if b.criterio:
            out.append(f"{SANGRIA * 2}falta declarar: {b.criterio} "
                       f"[{b.etiqueta}] - {b.concepto}")
            out.append(f"{SANGRIA * 2}fuente: {b.fuente}")
        else:
            out.append(f"{SANGRIA * 2}{b.mensaje}")
    return out


def _lineas_resumen(informe: Informe) -> List[str]:
    # Las cifras salen de `Informe.resumen`, la misma que leen la GUI y la
    # memoria (EXT-G-02): aqui no se cuenta nada.
    r = informe.resumen()
    out = _titulo("RESUMEN")
    out.append(f"CSV                     : {informe.csv}")
    out.append(f"Alcance de la corrida   : {informe.alcance}")
    out.append(f"Puntos del expediente   : {r.puntos}")
    out.append(f"Puntos dimensionados    : {r.dimensionados}")
    out.append(f"Verificaciones incumplidas: {r.incumplidas}")
    # T-2: las que salieron como INDICADOR (`[AVISO]` en la tabla del punto)
    # no son incumplidas, y se cuentan aparte para que el 0 de arriba no las
    # calle.
    out.append(f"Verificaciones con aviso: {r.con_aviso}")
    out.append(f"Etapas bloqueadas       : {r.bloqueadas}")
    if r.diferidas:
        out.append(f"Diferidas por alcance   : {r.diferidas} (ver ALCANCE DE "
                   "LA CORRIDA; no cuentan para el cierre)")
    out.append(f"Expediente cerrado      : {'si' if r.cerrado else 'no'}")
    if not informe.cerrado:
        out.append("")
        if r.bloqueadas or not r.incumplidas:
            out.append("El expediente NO cierra. Mientras un criterio siga sin "
                       "valor, la etapa que lo invoca se detiene: no se "
                       "sustituye por un defecto (Sec. 0.7).")
        else:
            # --- T-9 (correcciones) --- Sin etapas bloqueadas, lo que impide
            # el cierre son verificaciones que se evaluaron y no cumplen (VB1
            # de B-01 en la guia, por ejemplo): la frase de los criterios sin
            # valor no era la razon.
            out.append("El expediente NO cierra: hay verificaciones "
                       "incumplidas (marcadas [NO] en el bloque de su punto). "
                       "Se resuelven en el diseño o con los datos del "
                       "proyecto que las sostienen, no con un defecto.")
    return out


def volcar(informe: Informe, con_criterios: bool = False) -> str:
    """El informe completo como texto, en el orden en que se lee la memoria."""
    lineas = _titulo("EXPEDIENTE DE ALCANTARILLAS - "
                     "M0 -> M1 -> MD -> M6 -> M7 -> M8 -> M9 -> M10")
    lineas.append(f"CSV: {informe.csv}    generado (UTC): {informe.generado}")
    lineas.append("")
    for punto in informe.puntos:
        lineas.extend(_lineas_punto(punto))
        lineas.append("")
    lineas.extend(_lineas_cabezal(informe.cabezal))
    lineas.append("")
    lineas.extend(_lineas_alcance(informe))
    lineas.append("")
    lineas.extend(_lineas_criterios_bloqueantes(informe))
    lineas.extend(_lineas_resumen(informe))
    if con_criterios:
        # La foto de la corrida, no el registro vivo del proceso (EXT-4).
        contexto = ContextoCorrida.de(informe)
        lineas.append("")
        lineas.append(ds.reporte_datos_sitio(solo_usados=True,
                                             usados=contexto.datos_usados,
                                             efectivos=contexto.datos_efectivos,
                                             sin_valor=contexto.datos_sin_valor))
        lineas.append("")
        lineas.append(ca.reporte_criterios(solo_usados=True, contexto=contexto))
    return "\n".join(lineas)


# ===========================================================================
# Entrada
# ===========================================================================

def plantilla_por_alcance(alcance: str,
                          forzada: Optional[Path] = None) -> Path:
    """
    Que plantilla de M11 usa la memoria: la explicita si se paso --plantilla,
    y si no la que corresponde al alcance de la corrida.

    El alcance elige el DEFECTO, no una obligacion: la de perfil y la de
    expediente comparten el contrato de marcadores, de modo que cualquiera de
    las dos se puede forzar sobre cualquier corrida. Una memoria de perfil
    impresa con la plantilla de expediente sigue siendo correcta -- solo trae
    ademas el volcado de Tableros 1-2-3 -- y esa combinacion tiene su uso al
    revisar que quedo fuera.
    """
    if forzada is not None:
        return Path(forzada)
    nombre = (NOMBRE_PLANTILLA_PERFIL if alcance == ALCANCE_PERFIL
              else NOMBRE_PLANTILLA)
    return DIR_PLANTILLAS / nombre


# ---------------------------------------------------------------------------
# Progreso por stdout y sesion serializada (EXT-8, PC-11)
# ---------------------------------------------------------------------------
# La GUI exporta el PDF en un SUBPROCESO que corre esta CLI, y lee su avance
# de stdout: una linea por punto de la memoria y una por etapa, con este
# prefijo delante para distinguirlas del volcado. Solo salen con `--progreso`;
# sin la bandera la salida de la CLI es la de siempre (la linea base de la
# Familia C la fija).
PREFIJO_PROGRESO = "progreso:"


def _informar_progreso(etapa: str, hecho: int, total: int) -> None:
    print(f"{PREFIJO_PROGRESO} {hecho}/{total} {etapa}", flush=True)


@dataclass(frozen=True)
class SesionSerializada:
    """
    Lo que una sesion de la ventana (`gui/app.py::guardar_sesion`, formato
    `sesion.FORMATO_SESION`) le dice a la CLI: de que obra es la corrida.

    `banderas` ya viene traducida a las claves de `cargar_datos_externos`
    (`sesion.banderas_de_externos`), y `criterios` es el bloque tal cual,
    que `aplicar_sesion_serializada` repone por `declaracion.restaurar_sesion`
    --- el MISMO camino con guardia que «Cargar sesion» en la ventana ---.
    """
    proyecto: str
    csv: Optional[Path]
    datos_externos: Optional[Path]
    banderas: Dict[str, Optional[str]]
    alcance: Optional[str]
    criterios: Optional[Dict[str, Any]]
    formato_version: int
    # Formato 3 (EXT-10, E04): identidad, la ruta del sitio.json, los [S]
    # declarados por sesion, las corridas embebidas y los avisos de la
    # migracion explicita con que se leyo. `nombre` es el del archivo, que
    # es el origen que la memoria imprime para un [S] repuesto de aqui.
    id: str = ""
    datos_sitio: Optional[Path] = None
    sitio: Optional[Dict[str, Any]] = None
    corridas: Tuple[Dict[str, Any], ...] = ()
    csv_sha1: str = ""
    avisos: Tuple[str, ...] = ()
    nombre: str = ""


def cargar_sesion_serializada(ruta: Path) -> SesionSerializada:
    """
    Lee una sesion de la ventana y la valida ENTERA antes de devolverla
    (`sesion.errores_de_sesion`, PC-16). Una sesion deformada es
    `ValueError` con la lista de defectos; un archivo ilegible sale como lo
    que es (OSError, UnicodeDecodeError, JSONDecodeError), fuera de
    ErrorProyecto, igual que el CSV.

    Desde EXT-10 la MIGRACION ES EXPLICITA: lo crudo se valida, se lleva al
    formato actual con `sesion.migrar_a_actual` (v1 o v2 se completan y
    dicen que se completaron; una version desconocida es `ValueError`), y
    se vuelve a validar lo migrado. Los avisos viajan en `avisos`.
    """
    data = json.loads(Path(ruta).read_text(encoding="utf-8"))
    errores = _sesion.errores_de_sesion(data)
    if errores:
        raise ValueError(
            f"la sesion «{Path(ruta).name}» no se puede aplicar: "
            + "; ".join(errores))
    data, avisos = _sesion.migrar_a_actual(data)
    errores = _sesion.errores_de_sesion(data)
    if errores:
        raise ValueError(
            f"la sesion «{Path(ruta).name}» no se puede aplicar tras migrarla: "
            + "; ".join(errores))
    alcance = data.get("alcance") or None
    if alcance is not None and alcance not in (ALCANCE_PERFIL, ALCANCE_EXPEDIENTE):
        raise ValueError(
            f"la sesion «{Path(ruta).name}» trae un alcance desconocido: "
            f"{alcance!r} (admitidos: {ALCANCE_PERFIL}, {ALCANCE_EXPEDIENTE})")
    return SesionSerializada(
        proyecto=str(data.get("proyecto", "") or ""),
        csv=Path(data["csv"]) if data.get("csv") else None,
        datos_externos=(Path(data["datos_externos"])
                        if data.get("datos_externos") else None),
        banderas=_sesion.banderas_de_externos(data.get("externos", {}) or {}),
        alcance=alcance,
        criterios=data.get("criterios"),
        formato_version=int(data.get("formato_version", 1)),
        id=str(data.get("id", "") or ""),
        datos_sitio=Path(data["datos_sitio"]) if data.get("datos_sitio") else None,
        sitio=data.get("sitio"),
        corridas=tuple(data.get("corridas") or ()),
        csv_sha1=str(data.get("csv_sha1", "") or ""),
        avisos=tuple(avisos),
        nombre=Path(ruta).name)


def aplicar_sesion_serializada(sesion: SesionSerializada):
    """
    Repone los criterios de la sesion en ESTE proceso, sustituyendo lo que
    hubiera declarado (`restaurar_sesion(sustituir=True)`: abrir una obra no
    hereda las decisiones de otra, EXT-A-02). Devuelve el
    `ResultadoDeRestauracion` con lo restaurado, lo rechazado y lo retirado,
    para que `main` lo diga.
    """
    return _declaracion.restaurar_sesion(sesion.criterios or {}, sustituir=True)


def aplicar_sitio_de_sesion(sesion: SesionSerializada):
    """
    Repone los datos de sitio [S] del bloque `sitio` de la sesion (EXT-10),
    sustituyendo lo que otra obra hubiera declarado, con la sesion como
    origen. Hermana de `aplicar_sesion_serializada`, y aparte de ella para
    no cambiar su contrato. Devuelve el `ResultadoDeRestauracion`.
    """
    return _declaracion.restaurar_datos_de_sitio(
        sesion.sitio or {"valores": {}}, sustituir=True,
        origen=f"sesion {sesion.nombre}")


def _comparar_con_la_corrida_embebida(informe: Informe,
                                      sesion: SesionSerializada) -> Optional[str]:
    """
    Si la sesion trae embebida una corrida del MISMO CSV y alcance, dice si
    esta corrida la REPRODUCE (salvo la marca de tiempo) o DIFIERE de ella.
    Es lo que las corridas embebidas de E04 permiten afirmar; nunca detiene
    nada, y mientras el hijo del PDF recalcule (ficha EXT-8-02) es la unica
    equivalencia que se mide sobre la sesion misma.
    """
    contexto = ContextoCorrida.de(informe)
    candidatas = [c for c in sesion.corridas
                  if isinstance(c, dict) and c.get("csv_sha1") == contexto.csv_sha1
                  and c.get("alcance") == informe.alcance
                  and isinstance(c.get("informe_json"), dict)]
    if not candidatas:
        return None
    guardada = candidatas[-1]
    propia = json.loads(json.dumps(informe_json(informe), ensure_ascii=False,
                                   allow_nan=False))
    # LA MISMA COMPARACION QUE `--comparar` (E-B, E14): `comparador.comparar`
    # normaliza --- sin la marca de tiempo y sin las RUTAS de origen de los
    # [S], que no dicen nada del calculo y con las que dos maquinas dirian
    # DIFIERE sobre la misma obra --- y compara por identidad de punto con
    # las tolerancias nombradas. Hasta E-B esto comparaba dos dicts con `==`
    # por su cuenta: dos definiciones de «la misma corrida».
    igual = _comparador.comparar(propia, guardada["informe_json"]).iguales
    cuando = guardada.get("generado_utc", "?")
    if igual:
        return (f"Esta corrida REPRODUCE la guardada en la sesion el {cuando} "
                f"(mismo JSON; {_comparador.descripcion_de_lo_omitido()})")
    return (f"Esta corrida DIFIERE de la guardada en la sesion el {cuando}: "
            "el expediente, los criterios o los datos de sitio cambiaron "
            "desde entonces; revise antes de dar la memoria por vigente")


def _bandera_explicita(argv: Optional[Sequence[str]], nombre: str) -> bool:
    """Si `nombre` (p. ej. `--alcance`) vino escrito en la linea de comandos."""
    tokens = list(sys.argv[1:] if argv is None else argv)
    return any(t == nombre or t.startswith(nombre + "=") for t in tokens)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cli.py",
        # Sin abreviaturas (EXT-8): `--sesion` promete que una bandera
        # ESCRITA gana a lo que la sesion trae, y eso se decide mirando la
        # linea de comandos (`_bandera_explicita`); con `--alc expediente`
        # admitido, la bandera escrita perderia (auditoria adversarial).
        allow_abbrev=False,
        description="Corre el pipeline de alcantarillas (M0 a M10) sobre el "
                    "CSV de puntos criticos de Sec. 1.2.",
        epilog="Los datos que no son columna de Sec. 1.2 (luz, TW, longitud, "
               "Q/S de Familias B y C, L_hidraulico) se declaran con las "
               "banderas o con --datos-externos. No tienen valor por defecto. "
               "Los datos de sitio [S] de OTRA obra (PGA, corredor...) se "
               "declaran con --datos-sitio, con trazabilidad y fecha; sin "
               "el gobiernan los de datos_sitio.py, la obra del repositorio.")
    p.add_argument("csv", type=Path, nargs="?", default=None,
                   help="ruta del CSV de puntos criticos (se puede omitir "
                        "con --sesion, que lo trae)")
    p.add_argument("--comparar", nargs=2, type=Path, metavar=("A.json", "B.json"),
                   dest="comparar",
                   help="compara dos volcados informe_json por identidad de punto "
                        "(src/comparador.py) y termina: 0 iguales, 1 difieren, 2 "
                        "no se pudo leer. No corre el pipeline")
    p.add_argument("--prevuelo", action="store_true", dest="prevuelo",
                   help="imprime el anticipo entero (criterios vacios que el "
                        "alcance puede invocar, contraste del CSV, lo que el "
                        "alcance difiere y los datos que faltan punto a punto) "
                        "y termina SIN correr el pipeline: 0 si nada detiene "
                        "una etapa, 1 si algo lo hace (PF-2). Es una "
                        "estimacion: la lista definitiva la da la corrida")
    p.add_argument("--sesion", type=Path, dest="sesion",
                   help="sesion guardada por la ventana (JSON): repone el "
                        "proyecto, el CSV, los datos externos, el alcance y "
                        "los criterios declarados con su procedencia, por "
                        "el mismo camino con guardia que «Cargar sesion». "
                        "Una bandera escrita aqui gana a lo que la sesion "
                        "trae; --declarar compone encima")
    p.add_argument("--progreso", action="store_true",
                   help=f"imprime en stdout una linea «{PREFIJO_PROGRESO} "
                        "hecho/total etapa» por punto de la memoria y por "
                        "etapa de la exportacion (es lo que la ventana lee "
                        "del subproceso que escribe el PDF)")
    p.add_argument("--json", type=Path, dest="json_salida",
                   help="ruta del JSON de salida (por defecto, junto al CSV "
                        "como <csv>.informe.json)")
    p.add_argument("--datos-externos", type=Path, dest="datos_externos",
                   help="JSON con los datos declarados, globales y por punto")
    p.add_argument("--cuencas", type=Path, dest="cuencas",
                   help="CSV de cuencas, una fila por obra (id, area_km2, "
                        "L_cauce_m, S_cauce_cuenca, S_terreno, cobertura, "
                        "suelo, estacion, metodo_tc; segun el metodo, "
                        "H_desnivel_m, ajuste_kirpich y CN). Con --estacion, el "
                        "programa calcula el caudal de los puntos de Familia "
                        "A y B que traigan Q_m3s vacio (Fase 1-bis). Si "
                        "Q_m3s viene lleno, gana el declarado")
    p.add_argument("--estacion", type=Path, dest="estacion",
                   help="CSV de la serie de precipitacion maxima en 24 h "
                        "(estacion, anio, p24_mm, fen). La columna fen dice, "
                        "anio por anio y sin celdas vacias, cuales son del "
                        "fenomeno El Nino; como se tratan "
                        "se declara con --declarar homogeneidad_serie_fen=...")
    p.add_argument("--datos-sitio", type=Path, dest="datos_sitio",
                   help="JSON con los datos de sitio [S] de la obra que se "
                        "calcula (EXT-10): por clave, {valor, trazabilidad, "
                        "fecha}. Se declaran SOLO para esta corrida por la "
                        "misma guardia que datos_sitio.py, que no se toca; "
                        "la memoria imprime de que archivo salio cada [S]. "
                        "Una bandera escrita gana al bloque 'sitio' de "
                        "--sesion")
    p.add_argument("--declarar", action="append", default=[],
                   metavar="CLAVE=VALOR", dest="declaraciones",
                   help="declara un criterio de criterios_adoptados.py SOLO "
                        "para esta corrida (repetible). Es la misma via que "
                        "la GUI: el archivo no se toca y la memoria imprime "
                        "el valor marcado como declarado para la corrida")
    p.add_argument("--barrido", action="append", default=[],
                   metavar="CLAVE=v1,v2,v3", dest="barridos",
                   help="barrido de sensibilidad (PF-3): corre el pipeline una "
                        "vez por valor con el criterio declarado a ese valor, "
                        "compara cada corrida con la del primer valor y "
                        "escribe la tabla; repetible, UNA clave a la vez (nunca "
                        "el producto cartesiano). Cada valor pasa la misma "
                        "puerta que una declaracion: fuera de la ventana de "
                        "sensibilidad no corre nada. La coma SEPARA valores "
                        "(3,5 son dos valores; un par se escribe con parentesis). "
                        "Con --barrido no se arma memoria y --json recibe el "
                        "barrido, no el expediente")
    p.add_argument("--barrido-nota", default="", dest="barrido_nota",
                   metavar="TEXTO",
                   help="nota de procedencia de los valores barridos (la que "
                        "un criterio de tabla exige cuando el valor no "
                        "proviene de una fila); vale para todos los --barrido "
                        "de la invocacion")
    p.add_argument("--barrido-fila", default="", dest="barrido_fila",
                   metavar="FILA",
                   help="fila de la tabla de la que provienen los valores "
                        "barridos, cuando la hay; vale para todos los "
                        "--barrido de la invocacion, de modo que dos claves de "
                        "tablas distintas con fila se barren en dos invocaciones")
    p.add_argument("--luz", type=float, help="luz del cruce, m (Sec. 2.1)")
    p.add_argument("--tw", type=float, dest="TW",
                   help="tirante en el receptor sobre el fondo de la salida, m")
    p.add_argument("--longitud", type=float,
                   help="longitud del conducto, m (si no, la calcula 7.B)")
    p.add_argument("--l-hidraulico", type=float, dest="l_hidraulico",
                   help="longitud por capacidad de la cuneta, m (Fase 10)")
    p.add_argument("--categoria-tr", dest="categoria_tr",
                   help="fila de la Tabla N 02: quebrada_importante o "
                        "quebrada_menor (Sec. 2.2, Familia A)")
    p.add_argument("--criterios", action="store_true",
                   help="imprime tambien la declaracion completa de los "
                        "datos de sitio [S] y de los criterios usados "
                        "(reporte_datos_sitio + reporte_criterios)")
    p.add_argument("--html", type=Path, dest="html_salida",
                   help="escribe la memoria de calculo de la Fase 11 (M11) "
                        "en esa ruta, como HTML")
    p.add_argument("--pdf", type=Path, dest="pdf_salida",
                   help="escribe la memoria en PDF con weasyprint; si no esta "
                        "instalado, deja el HTML y lo abre en el navegador "
                        "para Ctrl+P (misma via que legacy/Tc.py)")
    p.add_argument("--csv-resumen", type=Path, dest="csv_resumen_salida",
                   help="escribe el cuadro resumen de la Fase 11 (entregable "
                        "3) en esa ruta, como CSV")
    p.add_argument("--proyecto", default="",
                   help="nombre del proyecto que encabeza la memoria")
    p.add_argument("--plantilla", type=Path, dest="plantilla",
                   help="fuerza la plantilla HTML de la memoria (M11). Por "
                        f"defecto, '{NOMBRE_PLANTILLA_PERFIL}' con --alcance "
                        f"perfil y '{NOMBRE_PLANTILLA}' con --alcance "
                        "expediente. Las dos aceptan cualquier corrida")
    p.add_argument("--alcance", choices=(ALCANCE_PERFIL, ALCANCE_EXPEDIENTE),
                   default=ALCANCE_EXPEDIENTE,
                   help="alcance de la corrida. 'expediente' (defecto): el "
                        "pipeline completo, como siempre. 'perfil': V5 y V8 "
                        "se intentan pero su fallo se difiere al expediente, "
                        "y las Fases 8 y 9 no se ejecutan; todo lo diferido "
                        "queda registrado con su fundamento y no cuenta para "
                        "el cierre")
    return p


def declarar_criterios(declaraciones: Sequence[str]) -> List[str]:
    """
    Aplica las declaraciones `CLAVE=VALOR` de `--declarar` a la corrida.

    Pasa por `criterios_adoptados.establecer_valor_dinamico`, el UNICO camino
    de declaracion en caliente, que a su vez somete el valor a la misma
    guardia que el archivo (`_verificar_criterio`): un valor fuera del rango
    de sensibilidad se rechaza aqui y la corrida no empieza.

    El texto se interpreta con `ast.literal_eval` -- 1.5, (0.010, 0.013),
    'cota_terreno' -- y lo que no sea un literal de Python se toma como
    cadena, que es lo que declara un criterio categorico. No hay conversion
    de unidades ni default: lo que el usuario escribe es lo que se declara.
    """
    aplicadas = []
    for declaracion in declaraciones:
        clave, sep, texto = declaracion.partition("=")
        if not sep or not clave.strip():
            raise ValueError(
                f"--declarar {declaracion!r} no tiene la forma CLAVE=VALOR")
        clave, texto = clave.strip(), texto.strip()
        if not texto:
            # Sin esto, `ast.literal_eval("")` lanza SyntaxError, el texto cae
            # al respaldo y se declara la CADENA VACIA: un valor que nadie
            # quiso declarar entrando por la puerta de una errata.
            raise ValueError(
                f"--declarar {declaracion!r} no trae valor. Para retirar una "
                "declaracion no se declara vacio: se omite la bandera")
        try:
            valor_nuevo = ast.literal_eval(texto)
        except (ValueError, SyntaxError):
            # 'nan', 'inf', '-inf' e 'Infinity' NO son literales de Python:
            # `literal_eval` los rechaza y caian a este respaldo COMO CADENA,
            # por debajo de la guardia de finitud de criterios_adoptados, que
            # solo recorre numeros. Y la cadena no se queda quieta:
            # `M9_cabezal.cuantia_de_diseno` -- y cualquier consumidor que
            # haga float() sobre un criterio numerico -- la devuelve al
            # calculo convertida en el mismo nan que se rechazo, y la memoria
            # sale con `cuantia_adoptada = nan` y un gobernante declarado.
            # El respaldo a texto existe para los criterios CATEGORICOS
            # ('cota_terreno', 'flexible', 'A'), no para un numero disfrazado.
            if _parece_numero_no_finito(texto):
                raise ValueError(
                    f"--declarar {declaracion!r} no es un numero declarable: "
                    f"{texto!r} no es un literal de Python, entraria como "
                    "TEXTO y el primer consumidor que haga float() lo "
                    "devolveria al calculo como infinito o NaN"
                ) from None
            valor_nuevo = texto
        if isinstance(valor_nuevo, tuple) and not _escrita_como_tupla(texto):
            # `0,5` es una coma DECIMAL para quien la teclea y la tupla (0, 5)
            # para `ast.literal_eval` (PC-34). Con 'HW_D_max' la ventana lo
            # rechazaba; con un criterio sin ventana la tupla entraba en
            # silencio. Una tupla se declara con sus parentesis: (0.010, 0.013).
            raise ValueError(
                f"--declarar {declaracion!r}: {texto!r} se leeria como la "
                f"TUPLA {valor_nuevo!r}, no como un numero. Si es un decimal, "
                "el separador es el punto (0.5); si de verdad es una tupla, "
                "escribela con parentesis: (0.010, 0.013). La coma sin "
                "parentesis no declara nada"
            )
        ca.establecer_valor_dinamico(clave, valor_nuevo)
        aplicadas.append(clave)
    return aplicadas


def _escrita_como_tupla(texto: str) -> bool:
    """El texto lleva sus parentesis: una tupla escrita como tupla."""
    return texto.startswith("(") and texto.endswith(")")


def _parece_numero_no_finito(texto: str) -> bool:
    """
    El texto se lee como un numero y ese numero no es finito.

    Es la puerta que `ast.literal_eval` deja abierta: 'nan' e 'inf' no son
    literales de Python -- son NOMBRES --, de modo que literal_eval los
    rechaza y el respaldo a cadena los dejaba pasar como texto.
    """
    try:
        return not math.isfinite(float(texto))
    except (TypeError, ValueError, OverflowError):
        return False


def _aplicar_datos_de_sitio(args, sesion: Optional[SesionSerializada]):
    """
    Que datos de sitio gobiernan esta corrida, en orden de precedencia:
    `--datos-sitio` escrito > ruta `datos_sitio` de la sesion > bloque
    `sitio` de la sesion > nada (gobierna `datos_sitio.py`). Es LA MISMA
    regla que la ventana aplica al ejecutar (el campo de la pestaña 1 gana
    al bloque de la sesion abierta): la auditoria adversarial de EXT-10
    midio que con la regla anterior (bloque > ruta) las dos puertas
    calculaban obras distintas sobre la misma sesion si el sitio.json
    cambiaba tras guardar. Cuando la ruta gana y la sesion traia ademas un
    bloque, `main` lo dice. Devuelve `(resultado, aviso)`.
    """
    if args.datos_sitio is not None:
        return cargar_datos_sitio(args.datos_sitio), None
    if sesion is None:
        return None, None
    if sesion.datos_sitio is not None:
        aviso = None
        if sesion.sitio and sesion.sitio.get("valores"):
            aviso = (f"La sesion trae la ruta {sesion.datos_sitio} y ademas un "
                     "bloque 'sitio': gobierna la ruta (se relee el archivo), "
                     "como en la ventana; el bloque se ignora")
        return cargar_datos_sitio(sesion.datos_sitio), aviso
    return aplicar_sitio_de_sesion(sesion), None


def _literal_declarado(texto: str, bandera: str) -> Any:
    """
    Un valor tecleado en la linea de comandos, con la lectura de `--declarar`:
    `ast.literal_eval`, texto para lo que no es literal (un criterio
    categorico), y el rechazo de 'nan'/'inf' disfrazados de texto.
    """
    try:
        return ast.literal_eval(texto)
    except (ValueError, SyntaxError):
        if _parece_numero_no_finito(texto):
            raise ValueError(
                f"{bandera}: {texto!r} no es un numero declarable: no es un "
                "literal de Python, entraria como TEXTO y el primer consumidor "
                "que haga float() lo devolveria al calculo como infinito o NaN"
            ) from None
        return texto


def valores_del_barrido(barrido: str) -> Tuple[str, Tuple[Any, ...]]:
    """
    `CLAVE=v1,v2,v3` de `--barrido` como (clave, valores). Los valores se
    leen JUNTOS como una tupla de literales de Python, de modo que un par
    se escribe con sus parentesis --- `(0.010, 0.013),(0.012, 0.015)` --- y
    la coma sin parentesis separa valores (no es decimal: PC-34). Lo que no
    es un literal se lee como texto, valor a valor, con el mismo respaldo
    que `--declarar`.
    """
    clave, sep, texto = barrido.partition("=")
    clave, texto = clave.strip(), texto.strip()
    if not sep or not clave:
        raise ValueError(f"--barrido {barrido!r} no tiene la forma CLAVE=v1,v2,v3")
    if not texto:
        raise ValueError(f"--barrido {barrido!r} no trae ningun valor")
    try:
        valores = ast.literal_eval(f"({texto},)")
    except (ValueError, SyntaxError):
        trozos = [trozo.strip() for trozo in texto.split(",")]
        if any(not trozo for trozo in trozos):
            raise ValueError(
                f"--barrido {barrido!r} trae un valor vacio (dos comas seguidas, "
                "o una coma al final): cada coma separa un valor") from None
        valores = tuple(_literal_declarado(trozo, f"--barrido {barrido!r}")
                        for trozo in trozos)
    return clave, tuple(valores)


# Las banderas que un barrido no aplica: el barrido no es un expediente y no
# arma memoria ni cuadro (PF-3). Se AVISA, porque callarlas era escribir
# nada con codigo 0 (auditor adversarial de PF-3).
_BANDERAS_QUE_EL_BARRIDO_NO_APLICA = (("html_salida", "--html"), ("pdf_salida", "--pdf"),
                                      ("csv_resumen_salida", "--csv-resumen"),
                                      ("criterios", "--criterios"), ("progreso", "--progreso"))


def _barrer_desde_cli(args, externos: DatosExternos) -> int:
    """
    Los barridos de `--barrido`, uno tras otro y cada uno sobre el mismo
    estado de entrada (lo que `--sesion`, `--datos-sitio` y `--declarar`
    dejaron declarado). Imprime la tabla de cada uno y escribe UN JSON con
    todos (`{"barridos": [...]}`) en `--json` o junto al CSV. Devuelve 0, o
    2 si algun valor no pasa la puerta o una corrida se detiene en un error
    del expediente: la puerta se cierra ANTES de la primera corrida, de modo
    que un valor fuera de la ventana no deja ninguna corrida hecha.
    """
    from src import barrido as _barrido
    ignoradas = [bandera for campo, bandera in _BANDERAS_QUE_EL_BARRIDO_NO_APLICA
                 if getattr(args, campo)]
    if ignoradas:
        print("Con --barrido no se escribe memoria ni cuadro: se ignoran "
              + ", ".join(ignoradas), file=sys.stderr)
    # LA PUERTA DE TODOS LOS BARRIDOS ANTES DE LA PRIMERA CORRIDA: con dos
    # --barrido, el segundo que no pasara la puerta se descubria despues de
    # correr el primero entero (auditor adversarial de PF-3).
    barridos = []
    try:
        for texto in args.barridos:
            clave, valores = valores_del_barrido(texto)
            _barrido.verificar_valores(clave, valores, fila=args.barrido_fila,
                                       nota=args.barrido_nota)
            barridos.append((texto, clave, valores))
    except KeyError as exc:
        print(f"No se pudo barrer: la clave {exc} no existe en criterios_adoptados.py",
              file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"No se pudo barrer: {exc}", file=sys.stderr)
        return 2
    volcados = []
    for texto, clave, valores in barridos:
        try:
            resultado = _barrido.barrer(
                args.csv, externos, args.alcance, clave, valores,
                fila=args.barrido_fila, nota=args.barrido_nota,
                hidrologia=cargar_hidrologia(args.cuencas, args.estacion),
                volcar=informe_json)
        except ErrorProyecto as exc:
            print(f"El barrido de {texto!r} se detuvo en el expediente: {exc}",
                  file=sys.stderr)
            return 2
        print("\n".join(_barrido.lineas_de_la_tabla(resultado)))
        print()
        volcados.append(_barrido.volcado_del_barrido(resultado))
    destino = args.json_salida or args.csv.with_suffix(".barrido.json")
    _sesion.escribir_json_atomico(destino, {"barridos": volcados})
    print(f"JSON del barrido: {destino}")
    return 0


def _prevuelo(ruta_csv: Path, externos: DatosExternos, alcance: str,
              hidrologia: Any = None) -> int:
    """
    Imprime los cuatro bloques del anticipo de la pestaña 1 y devuelve 0 si
    ninguna falta estimada detiene una etapa, 1 si alguna lo hace. No corre
    el pipeline ni carga los puntos: es la MISMA estimacion que la ventana
    pinta antes de ejecutar, y la lista definitiva la da la corrida.
    """
    from src import anticipo as _antc
    print(_antc.AVISO_DEL_ANTICIPO)
    print("\n== Criterios vacios que el alcance puede invocar ==")
    vacios = _antc.criterios_vacios_alcanzables(alcance)
    for c in vacios:
        print(f"  {c.clave}: {c.concepto} [{c.responsable}]")
    if not vacios:
        print("  ninguno")
    print("\n== Columnas del CSV ==")
    contraste = _antc.contraste_de_cabecera(ruta_csv)
    for linea in _antc.lineas_del_contraste(contraste):
        print(f"  {linea}")
    print("\n== Lo que este alcance difiere ==")
    for linea in _antc.lineas_de_diferimientos(_antc.diferimientos_del_alcance(alcance)):
        print(f"  {linea}")
    print("\n== Datos que faltan, punto a punto ==")
    # LAS DOS ENTRADAS DE LA HIDROLOGIA (T-1, auditoria): con --cuencas y
    # --estacion el pre-vuelo las CARGA --un archivo mal escrito sale aqui--
    # y deja de llamar falta a un Q_m3s vacio que la corrida va a calcular;
    # lo que NO hace es calcularlo, y lo dice en vez de callarlo.
    calculables = (frozenset() if hidrologia is None
                   else hidrologia.ids_calculables())
    estimado = _antc.datos_faltantes_por_punto(
        ruta_csv, externos, alcance, ids_con_caudal_calculable=calculables)
    for linea in _antc.lineas_del_prevuelo(estimado):
        print(f"  {linea}")
    if hidrologia is not None:
        print("\n  Aviso: --cuencas y --estacion se cargaron y se validaron, "
              "pero el pre-vuelo NO calcula la hidrologia. Un Q_m3s vacio con "
              "cuenca y estacion figura como «" + _antc.ETAPA_DEPENDE_DE_LA_HIDROLOGIA
              + "»: la corrida puede detenerlo por un criterio sin declarar "
              "o por un metodo no evaluable.")
    # EL CODIGO DE SALIDA LEE LOS DOS BLOQUES QUE DETIENEN (auditor
    # adversarial de PF-2): una cabecera incompleta o una columna que no
    # admite vacio detienen la carga igual que una falta por punto, y salir
    # con 0 mientras la misma pantalla lo imprime seria contradecirse.
    detiene_la_carga = bool(contraste.faltan) or any(
        not c.admite_vacio for c in contraste.con_vacios)
    return 1 if detiene_la_carga or any(e.detiene for e in estimado) else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)

    # COMPARAR DOS VOLCADOS Y SALIR (E-B, E14): ningun otro argumento se
    # lee y el pipeline no corre. El comparador no importa el motor.
    if args.comparar is not None:
        return _comparador.main([str(r) for r in args.comparar])

    # LA SESION SERIALIZADA VA PRIMERO (EXT-8, PC-11): repone los criterios
    # con su procedencia y rellena lo que la linea de comandos no trajo. Una
    # bandera escrita gana; `--declarar` compone encima (por eso va despues).
    sesion: Optional[SesionSerializada] = None
    if args.sesion is not None:
        try:
            sesion = cargar_sesion_serializada(args.sesion)
            restauracion = aplicar_sesion_serializada(sesion)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"No se pudo leer la sesion: {exc}", file=sys.stderr)
            return 2
        except (ValueError, KeyError) as exc:
            print(f"No se pudo aplicar la sesion: {exc}", file=sys.stderr)
            return 2
        for aviso in sesion.avisos:
            print(f"Sesion migrada: {aviso}")
        if sesion.id:
            print(f"Sesion {sesion.id} ({sesion.nombre})")
        if restauracion.restaurados:
            print("Criterios restaurados de la sesion SOLO para esta corrida: "
                  + ", ".join(restauracion.restaurados)
                  + " (criterios_adoptados.py no se modifico)")
        for clave, motivo in restauracion.rechazados:
            print(f"NO se restauro {clave}: {motivo}", file=sys.stderr)
        if not _bandera_explicita(argv, "--proyecto"):
            args.proyecto = sesion.proyecto
        if args.csv is None:
            args.csv = sesion.csv
        if args.datos_externos is None:
            args.datos_externos = sesion.datos_externos
        if sesion.alcance is not None and not _bandera_explicita(argv, "--alcance"):
            args.alcance = sesion.alcance
    if args.csv is None:
        parser.error("hace falta el CSV de puntos criticos, o una --sesion que lo traiga")
    if args.prevuelo and args.barridos:
        parser.error("--prevuelo y --barrido no se combinan: el pre-vuelo no corre "
                     "y el barrido corre una vez por valor")

    # LOS DATOS DE SITIO DE LA OBRA (EXT-10): la bandera escrita gana al
    # bloque `sitio` de la sesion; sin bandera se aplica el bloque, y si la
    # sesion no trae bloque pero si la ruta del sitio.json, se lee la ruta.
    # Va ANTES de --declarar y de correr, y en su propio `try` con el mismo
    # brazo que --declarar: es una declaracion, y su rechazo es ValueError.
    try:
        sitio, aviso_sitio = _aplicar_datos_de_sitio(args, sesion)
    except (ValueError, KeyError) as exc:
        print(f"No se pudo declarar el dato de sitio: {exc}", file=sys.stderr)
        return 2
    if aviso_sitio:
        print(aviso_sitio)
    if sitio is not None and sitio.restaurados:
        print("Datos de sitio [S] declarados SOLO para esta corrida desde "
              f"{ds.origen_de(sitio.restaurados[0])}: "
              + ", ".join(sitio.restaurados)
              + " (datos_sitio.py no se modifico)")
    if sitio is not None:
        for clave, motivo in sitio.rechazados:
            print(f"NO se restauro el dato de sitio {clave}: {motivo}",
                  file=sys.stderr)

    try:
        declaradas = declarar_criterios(args.declaraciones)
    except (ValueError, KeyError) as exc:
        print(f"No se pudo declarar el criterio: {exc}", file=sys.stderr)
        return 2
    for clave in declaradas:
        print(f"Criterio declarado SOLO para esta corrida: {clave} = "
              f"{ca.valores_dinamicos()[clave]!r} "
              "(criterios_adoptados.py no se modifico)")

    plantilla = plantilla_por_alcance(args.alcance, args.plantilla)
    if args.html_salida is not None or args.pdf_salida is not None:
        # LA PLANTILLA SE COMPRUEBA ANTES DE CORRER NADA (PC-35): una ruta
        # inexistente o una hoja sin los marcadores del contrato terminaba
        # con traceback desnudo (FileNotFoundError / ValueError) DESPUES de
        # haber escrito el JSON: salida parcial sin ErrorProyecto. Ahora se
        # rechaza aqui, sin JSON a medias, con el mismo codigo de salida
        # que cualquier otra entrada que no se puede leer.
        try:
            _exigir_plantilla_valida(plantilla)
        except (FileNotFoundError, ValueError) as exc:
            print(f"No se puede usar la plantilla: {exc}", file=sys.stderr)
            return 2

    banderas = {"luz_m": args.luz, "TW_m": args.TW,
                "longitud_m": args.longitud,
                "L_hidraulico_m": args.l_hidraulico,
                "categoria_tr": args.categoria_tr}
    if sesion is not None:
        # Lo que la linea de comandos no trajo lo pone la sesion, campo a
        # campo: son las MISMAS claves (`sesion.banderas_de_externos`).
        for clave, valor in sesion.banderas.items():
            if banderas.get(clave) is None:
                banderas[clave] = valor
    progreso = _informar_progreso if args.progreso else None
    try:
        externos = cargar_datos_externos(args.datos_externos, banderas)
        if args.prevuelo:
            # EL PRE-VUELO Y SALIR (PF-2): nada de lo de abajo corre. Los
            # cuatro bloques los produce `src/anticipo.py`; aqui se imprimen.
            return _prevuelo(args.csv, externos, args.alcance,
                             cargar_hidrologia(args.cuencas, args.estacion))
        if args.barridos:
            # EL BARRIDO Y SALIR (PF-3): el expediente no se corre ni se
            # exporta; el barrido es un anexo de la tesis, no una memoria.
            return _barrer_desde_cli(args, externos)
        # LAS DOS ENTRADAS DE LA FASE 1-bis (T-1): se cargan aqui, dentro
        # del mismo `try`, porque un CSV de cuencas mal escrito es un
        # expediente que no se puede cargar, igual que el de puntos.
        hidrologia = cargar_hidrologia(args.cuencas, args.estacion)
        informe = correr(args.csv, externos, alcance=args.alcance,
                         hidrologia=hidrologia)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        # UnicodeDecodeError es subclase de ValueError y no entra sola: un CSV
        # guardado en ANSI por Excel -- con las eñes del castellano -- salia
        # con traza en vez de decir que el archivo no esta en UTF-8. Las dos
        # puertas del pipeline tienen que fallar igual (SIS-E-01), y el test
        # de simetria de tests/test_gui_contrato.py lo exige.
        print(f"No se pudo leer la entrada: {exc}", file=sys.stderr)
        return 2
    except ErrorProyecto as exc:
        # Un fallo de carga: sin puntos no hay expediente que informar.
        print(f"El expediente no se puede cargar: {exc}", file=sys.stderr)
        return 2

    print(volcar(informe, con_criterios=args.criterios))

    # La advertencia de corredor (EXT-V-01) y, si la sesion trae la corrida
    # embebida, si esta la reproduce (E04). Ninguna detiene nada.
    advertencia = advertencia_de_corredor_de(args.proyecto, ContextoCorrida.de(informe))
    if advertencia:
        print(f"\n{advertencia}")
    if sesion is not None:
        comparacion = _comparar_con_la_corrida_embebida(informe, sesion)
        if comparacion:
            print(f"\n{comparacion}")

    # LA MEMORIA SE ARMA ANTES DE ESCRIBIR EL JSON (PC-35): si la plantilla
    # no imprime un bloque que esta corrida SI produjo (`ValueError` del
    # contrato de marcadores, SIS-B-06), o si algun bloque de la memoria se
    # detiene en un `ErrorProyecto`, se sale aqui sin dejar ninguna salida
    # a medias. Lo que se escribe despues es lo que ya esta en memoria.
    try:
        if args.html_salida is not None or args.pdf_salida is not None:
            memoria_html(informe, proyecto=args.proyecto,
                         ruta_plantilla=plantilla)
    except (FileNotFoundError, ValueError, ErrorProyecto) as exc:
        print(f"No se pudo armar la memoria con la plantilla "
              f"«{plantilla.name}»: {exc}", file=sys.stderr)
        return 2

    destino = args.json_salida or args.csv.with_suffix(".informe.json")
    # Escritura atomica (E04): nunca un JSON a medias en disco.
    _sesion.escribir_json_atomico(destino, informe_json(informe))
    print(f"\nJSON del expediente: {destino}")

    if args.html_salida is not None:
        ruta = exportar_html(informe, args.html_salida,
                             proyecto=args.proyecto,
                             ruta_plantilla=plantilla, progreso=progreso)
        print(f"Memoria de calculo (HTML): {ruta}")
        print(f"Plantilla usada          : {plantilla.name}")

    if args.pdf_salida is not None:
        salida = exportar_pdf(informe, args.pdf_salida,
                              proyecto=args.proyecto,
                              ruta_plantilla=plantilla, progreso=progreso)
        print(salida.mensaje)

    if args.csv_resumen_salida is not None:
        ruta = exportar_csv(informe, args.csv_resumen_salida)
        print(f"Cuadro resumen (CSV): {ruta}")

    return 0 if informe.cerrado else 1


def _exigir_plantilla_valida(plantilla: Path) -> None:
    """
    La plantilla existe y pide SOLO marcadores del contrato de M11, y al
    menos uno (PC-35).

    `M11.cargar_plantilla` ya lanza FileNotFoundError si no existe; aqui se
    añade la mitad que faltaba antes de correr: una hoja sin marcadores -- o
    con uno que M11 no entrega -- no puede imprimir la memoria, y
    `substitute` lo diria con KeyError/ValueError despues de escribir el
    JSON. La otra direccion del contrato (un bloque que la corrida produce y
    la hoja no imprime) solo se puede comprobar con la corrida hecha, y la
    comprueba `memoria_html` antes de que `main` escriba nada.
    """
    hoja = cargar_plantilla(plantilla)
    pedidos = {m.group("named") or m.group("braced")
               for m in hoja.pattern.finditer(hoja.template)}
    pedidos.discard(None)
    if not pedidos:
        raise ValueError(
            f"la plantilla «{plantilla.name}» no tiene ningun marcador "
            f"{hoja.delimiter}nombre: no puede imprimir la memoria. Los "
            f"marcadores del contrato son {sorted(marcadores_de_la_memoria())}")
    desconocidos = sorted(pedidos - set(marcadores_de_la_memoria()))
    if desconocidos:
        raise ValueError(
            f"la plantilla «{plantilla.name}» pide marcadores que M11 no "
            f"entrega: {desconocidos}. Los del contrato son "
            f"{sorted(marcadores_de_la_memoria())}")


if __name__ == "__main__":
    sys.exit(main())
