"""
M5_verificaciones.py
=====================
Fase 5 de la hoja de ruta: las DOCE verificaciones de la tabla principal
(V1 a V10; once hasta T-2, que sumo V10), cada una como funcion propia que devuelve un `Verificacion` (nunca
un bool desnudo), mas `verificar()`, el agregado que MD.py llama con la firma
que declara su Protocol `Verificador`.

    V1  Borde libre               y/D <= adoptado (0.75 por     [N] verificar, 4.1.1.3.7 b)
                                  defecto; [A] 'borde_libre_y_sobre_d_max')
                                  (RECOMENDACION aplicada como umbral duro)
    V2  Velocidad minima          V >= adoptado (0.25 m/s por    [N] verificar, 4.1.1.3.6
                                  defecto; [A] 'velocidad_minima_autolimpieza_m_s')
                                  (RECOMENDACION aplicada como umbral duro;
                                  se evalua con la rama n_max, la estimacion
                                  BAJA de velocidad -- ver `v2_velocidad_minima`)
    V2b Sedimentacion/colmatacion S_conducto >= S_cauce   [C] HDS-5 num. 5.3.3
                                  + acceso de mantenimiento    [N] 4.1.1.3.7 d) + [A]
                                  (INDICADOR, aplicado con el regimen de
                                  'regimen_v2b' [A]: con aviso desde T-2,
                                  umbral duro hasta entonces; el
                                  segundo indicador del numeral queda
                                  declarado pendiente -- ver
                                  `v2b_sedimentacion`)
    V3  Velocidad maxima          concreto: fila de la Tabla N 10 [N]
                                  TMC / HDPE: 'v_max_tmc' / 'v_max_hdpe',
                                  CERRADOS con valor 4.572 m/s     [C]
    V4  Carga a la entrada HW     cota entrada + HW <= cota subrasante
                                  - resguardo(CBR)                       [N->]
    V5  Remanso aguas arriba      metodo DECLARABLE ('remanso_derecho_via',
                                  sin valor de archivo): embalse a nivel
                                  contra el ancho del derecho de via (T-7b) [A]
    V6  Material solido de arrastre  seccion unica (cumple por construccion)
    V7  Flotacion del conducto    equilibrio LRFD de factores de carga
                                  (Fase 8, M8_estructural); pendiente en
                                  'factores_carga_aashto' o
                                  'peso_especifico_relleno_kn_m3'              [A]
    V8  Evento extremo (FEN)      TR y umbral DECLARABLES, sin valor de
                                  archivo: nivel del embalse con el caudal
                                  del evento contra el borde de la
                                  plataforma (T-7b)                       [A]
    V9  Disponibilidad de diametro  D <= tope de M2                        [C]
    V10 Pendiente del conducto    S_min <= S_conducto <= S_max              [A]
                                  ('pendiente_minima_conducto' y
                                  'pendiente_maxima_conducto'; T-2)

Por que ya son DOCE funciones para las DOCE filas de la tabla de Fase 5
----------------------------------------------------------------------
La tabla de Fase 5 de la hoja de ruta lista doce verificaciones -- V1, V2,
**V2b**, V3, V4, **V4b**, V5, V6, V7, V8, V9 y, desde T-2, **V10** (la
pendiente del conducto, que entro a la tabla y al modulo en el mismo
cambio) -- y este modulo implementa las DOCE. Las dos que faltaban de las
once primeras se cablearon en sesiones distintas y por la misma
regla: cuando se pudo sostener el umbral con su fuente, no antes.

**V2b - sedimentacion / colmatacion. IMPLEMENTADA desde S20**
(`v2b_sedimentacion`, en `verificar()`). Hasta entonces no existia en ninguna
linea de codigo (SIS-A-13, MAT-O15) y en su lugar habia una CONSTANCIA de
diferimiento: un parrafo que la memoria imprimia y que nadie tenia que
responder. Lo que la desbloqueo fue encontrar la fuente que este repositorio
ya tenia y no habia leido: el **HDS-5 3.a ed., num. 5.3.3 «Sedimentation»,
pag. impresa 5.11**, que nombra los indicadores de colmatacion en terminos de
dos numeros que el calculo ya tiene -- la pendiente del barril frente a la
del cauce natural --. La fila es [N] + [A] en la hoja de ruta y esa
estructura se conserva entera: el indicador de pendiente es la mitad
evaluable y el ACCESO DE MANTENIMIENTO es la mitad [A], que entra por el
criterio 'acceso_mantenimiento_v2b' y **detiene la corrida mientras siga
vacio**. Ya no es un parrafo: es una pregunta que el expediente tiene que
contestar.

De los dos indicadores del numeral se evalua UNO. El segundo -- «roughness
greater than the channel» -- exige el n de Manning del CAUCE NATURAL, que no
es columna de Sec. 1.2; queda declarado en la `verificacion_pendiente` del
criterio y la memoria lo imprime en la propia fila. Ver el docstring de la
funcion.

**V4b - relacion HW/D. IMPLEMENTADA desde S14** (`v4b_relacion_hw_d`, en
`verificar()`). Se cableo cuando se pudo y no antes: el conflicto #1 de la
matriz de auditorias lo prohibia expresamente mientras la ETIQUETA del
criterio siguiera abierta, porque implementar el chequeo sin saber de donde
salia el 1.5 habria convertido una cita mal leida en un umbral que rechaza
diametros. Lo que estaba abierto se cerro contra el PDF (C06): el rango
1.0-1.5 no es un criterio que el HDS-5 fije, sino la practica que su
Sec. 2.2.5 d) "Agency Constraints" DESCRIBE de las agencias viales
estadounidenses, y 1.5 es su extremo superior, el menos restrictivo. Por eso
el criterio dejo de ser [C] -- vacio cubierto por fuente tecnica -- y paso a
[A]: es una adopcion del proyectista sobre una banda de practica ajena, con
su rango de sensibilidad. Ver `criterios_adoptados.CRITERIOS['HW_D_max']`,
que lleva la cita y el texto literal.

Es un cambio de COMPORTAMIENTO -- un punto que hoy pasa puede dejar de
pasar -- y por eso se hizo aparte de la reetiquetacion y no en el mismo paso.
El HW que se divide entre D es el del control GOBERNANTE, no el del control
de entrada: lo que la fuente acota es el embalse que la obra produce. La
razon completa esta en el docstring de la funcion.

Los dos docstrings que afirmaban que M5 ya ejecutaba V4b -- en
`modulos.M4_control` y en `modelos.ControlEntrada` -- se habian corregido
junto con la reetiquetacion, cuando la afirmacion era falsa. Hoy vuelven a
poder decir que la verificacion existe, y lo dicen con la precision que
entonces faltaba: cual es el HW que compara.

Se dice con los dos numeros -- once filas, diez funciones -- porque la
diferencia importa: contarla mal (decir "las once") tapa justamente la que
sigue abierta.
Es la misma via documental que Fase 8 ya usa para el item 5 (rigidez de
anillo, pandeo y costura): se declara diferido con su motivo, no se calcula
un numero que nadie pidio.

Lo que NO se rellena en silencio
---------------------------------
V5 y V8 enuncian un REQUISITO en la hoja de ruta pero no entregan la formula,
el metodo o el dato con que evaluarlo (ver el detalle en cada funcion).
Rellenarlos con un supuesto no declarado es exactamente lo que CLAUDE.md
prohibe como "el peor error posible en este proyecto": cada uno se detiene
con `CriterioPendienteError` desde un criterio nuevo en
`criterios_adoptados.py` ('remanso_derecho_via', 'TR_evento_extremo'), con su
justificacion y lo que falta para resolverlo.

TW -- Sec. 1.3 ("TW se calcula, no se mide"): lo resuelve M3, no este modulo
---------------------------------------------------------------------------
El TW que consume la Fase 4 sale del procedimiento de Sec. 1.3, implementado
en `M3_hidraulica.tw_seccion_1_3` (SIS-B-04) y orquestado por
`servicio._resolver_tw`. Son CUATRO VIAS en orden de precedencia, y la via
por la que salio queda escrita en `TWDeterminado.via` y en el paso F1.TW de
la memoria:

    1. declarado a mano (`--tw` / `TW_m` de --datos-externos);
    2. la columna `cota_TW` del CSV, que es el paso 2 resuelto fuera: se
       resta la cota de fondo de la salida;
    3. la columna `Q_receptor_m3s` + el criterio [A] 'seccion_receptor':
       Manning en la seccion trapecial del receptor (pasos 1 y 2);
    4. sin caudal documentado, los dos escenarios acotados del paso 3
       --salida libre y receptor a seccion llena, con 'seccion_receptor'--,
       y gobierna el mayor.

El criterio 'TW_receptor' (Tablero 3.1) sigue existiendo como ULTIMA puerta
--`CriterioPendienteError`, nunca un relleno silencioso-- para el punto que
no puede recorrer ninguna de las cuatro (`servicio.tw_sin_via_de_sec_1_3`).
M5 no interviene: V4 y V4b reciben el HW que M4 calculo con ese TW.

    ESTE APARTADO SE TITULABA «diferido y declarado» Y DECIA LO CONTRARIO
    HASTA T-0 (INF-5.1.4): que el procedimiento de tres pasos «no esta
    implementado en ningun modulo», que «un CSV que traiga 'Q_receptor_m3s'
    y 'cota_TW' llenos sigue exigiendo el TW declarado» y que «ningun modulo
    lee esas dos columnas». Fue cierto hasta S20, que escribio
    `tw_seccion_1_3`; desde entonces las dos columnas son las vias 2 y 3.
    Lo que sigue sin ser columna de Sec. 1.2 es la SECCION del receptor:
    es el criterio [A] 'seccion_receptor', una adopcion con ventana y no una
    medicion, y cuando el TW sale por la via 4 esa adopcion puede decidir
    el diametro (INFORME §3.2, fila «Tailwater»; lo trata T-2).

V7 SI tiene formula y metodo -- Fase 8, item 3 de la hoja de ruta, y
`modulos.M8_estructural` la implementa completa ("tuberia vacia, NF en su cota
mas alta"). Ya NO como un factor de seguridad global ΣW >= FS*U, sino como el
equilibrio de factores de carga que corresponde al marco LRFD de Sec. 0.2:

    gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

Lo que sigue pendiente son dos DATOS puntuales del procedimiento, no el
procedimiento: el peso especifico del relleno
('peso_especifico_relleno_kn_m3') y la eleccion de fila de gamma_p
('factores_carga_aashto', el mismo criterio del que come M9; los gamma en si
son [N] y estan en constantes_normativas). Ver el docstring de `v7_flotacion`
mas abajo.

Consecuencia practica: mientras 'remanso_derecho_via', 'TR_evento_extremo',
'acceso_mantenimiento_v2b' y los dos criterios de V7 sigan vacios,
`verificar()` (y por lo tanto `MD.disenar_punto` / `MD.disenar_lote`) se
detiene con `CriterioPendienteError` para CUALQUIER punto. No es un defecto
de este modulo: es la misma regla que ya aplica a 'TW_receptor' o
'v_max_tmc' -- un vacio real bloquea el calculo, no lo esconde. Las doce
funciones individuales (v1_borde_libre, ..., v10_pendiente_conducto) SI
son utilizables una por una hoy mismo; es el AGREGADO el que hereda el
bloqueo de las pendientes.

V4 -- la cota de entrada es un DATO MEDIDO O UN CRITERIO DECLARADO
----------------------------------------------------------------------------
`modelos.ResultadoHidraulico` documenta que HW es una carga en metros SOBRE
EL FONDO DE LA ENTRADA, y que la conversion a cota (msnm) exige la cota de esa
entrada.

ESA COTA LLEGA HOY POR DOS VIAS, y el orden entre ellas no es negociable:

  1. MEDIDA, por la columna `cota_fondo_entrada` del CSV (Sec. 1.2):
     nivelacion del fondo del cauce en el cruce. Cuando viene, MANDA, y el
     criterio ni siquiera se invoca. En un PASO DE CANAL es la unica lectura
     correcta -- el canal atraviesa la via y continua, y el invert se hereda
     del fondo del canal, no se adopta.
  2. ADOPTADA, por la regla que el proyectista declara en
     'origen_cota_fondo_entrada' (`criterios_adoptados.py`), cuando la
     columna va vacia. Mientras nadie declare ninguna, V4, V7 y el tamizado
     7.A se detienen con `CriterioPendienteError` como cualquier otro vacio.

Las reglas implementadas son dos (`ORIGENES_COTA_ENTRADA`): 'cota_terreno'
-- adoptar el terreno natural del cruce -- y 'cota_fondo_entrada', que EXIGE
el dato medido y se detiene con `DatoFaltanteError` si no esta, en vez de caer
en silencio al terreno. El alcance de la primera, su direccion de
conservadurismo y lo que la sustituye estan escritos en la justificacion del
criterio.

POR QUE IMPORTA EL ORDEN, medido en este corredor: con 'cota_terreno' el
invert queda a la cota del TERRENO NATURAL, o sea por encima del fondo del
canal en toda la profundidad de la seccion (entre 0.30 y 0.95 m en los cinco
cruces). HW se mide sobre el invert, de modo que ese desfase se propaga
entero a V4, a V7 y al tamizado de 7.A.

QUE CAMBIO Y POR QUE: hasta la correccion de SIS-A-01/SIS-A-04 este modulo
adoptaba `punto.cota_terreno` por su cuenta, con la eleccion explicada solo
aqui -- sin entrada en `criterios_adoptados.py`, sin fila en el Anexo A y sin
que la memoria marcara el numero como adoptado. Un docstring no es una
declaracion: no lo lee el revisor de la memoria, no entra en
`criterios_usados()` y no se puede cambiar sin tocar el codigo. La eleccion
gobierna V4, V7 y la rasante de 7.A/M7-M8, o sea el resultado de la obra, y
por eso vive donde vive el resto de lo que el proyectista decide.

La lectura vive en `cota_de_entrada()`, publica, porque M7 (tamizado de
7.A) convierte el MISMO HW a cota para fijar la rasante minima: las dos
tienen que leer la misma referencia o el acoplamiento circular que 7.A dice
cortar sigue abierto. Lo mismo vale para `resguardo_por_cbr()`, que es la
segunda condicion del tamizado.

Excepciones
-----------
    CriterioPendienteError   V4, V7 y todo consumidor de
                             `cota_de_entrada`
                             ('origen_cota_fondo_entrada'); V5
                             ('remanso_derecho_via'); V7
                             ('peso_especifico_relleno_kn_m3' o
                             'factores_carga_aashto'); V8
                             ('TR_evento_extremo'). V3 en TMC/HDPE ya NO:
                             'v_max_tmc' y 'v_max_hdpe' tienen valor.
    DatoInvalidoError        el 'material' de V3 no es de TipoMaterial (no
                             deberia llegar aqui: M2 ya lo valido antes); en
                             V7, la clave del conducto queda a nivel de la
                             subrasante o por encima (no hay relleno que
                             pesar); la regla declarada en
                             'origen_cota_fondo_entrada' no es una de las
                             implementadas.

Uso
---
    from src.modulos.M5_verificaciones import verificar

    verificaciones = verificar(punto=punto, material=material,
                               seccion=seccion,
                               resultado=resultado_hidraulico)

LA SECCION ENTERA Y NO UN `D`, desde C7: V7 pesa el volumen desplazado, y ahi
un prisma y un cilindro dejan de parecerse. Este bloque seguia escribiendo
`D=D` -- la firma anterior -- despues de que C7i la cambiara, y lo encontro la
auditoria adversarial de esa sesion.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from src import criterios_adoptados as ca
from src.constantes_normativas import (BORDE_LIBRE_BADEN_RANGO_M,
                                   RESGUARDO_NAPA_SUBRASANTE,
                                   UMBRALES_POR_CODIGO, V_MIN,
                                   Y_SOBRE_D_MAX, caracter_del_umbral)
from src.modelos import (DatosDeExpediente, DerechoDeViaDelPunto,
                     EventoExtremoDelPunto, LimiteNumericoError,
                     METODO_REMANSO_COTA_AFECTACION,
                     METODO_REMANSO_EMBALSE_A_NIVEL,
                     METODO_REMANSO_PERFIL_PASO_A_PASO, METODOS_DE_REMANSO,
                     MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO,
                     MOTIVO_METODO_NO_EVALUABLE_REMANSO,
                     UMBRAL_V8_SIN_DESBORDE, UMBRALES_V8)
from src.modelos import (CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD,
                     CIFRAS_PORCENTAJE, ControlGobernante, CotaDeEntrada,
                     DatoFaltanteError, DatoInvalidoError, EleccionDeProyecto,
                     ErrorProyecto, EstadoDeVerificacion, Familia, FormaSeccion,
                     Magnitud, Material, MetodoNoEvaluableError,
                     PuntoCritico, ReferenciaNormativa, RegimenBarril,
                     ResultadoHidraulico,
                     Seccion, SeccionRectangular,
                     TipoMaterial, TipoDeVeredicto, Umbral, Veredicto,
                     Verificacion, eleccion,
                     exigir_seccion_coherente, paso)
from src.modulos.M2_material import (CRITERIO_D_MAX_NORMA,
                                 CRITERIO_N_CELDAS_CAJON,
                                 CRITERIO_SECCIONES_CAJON, CRITERIO_V_MAX,
                                 espesor_pared,
                                 numero_de_celdas,
                                 procedencia_del_espesor)
from src.modulos.M8_estructural import (CRITERIO_FACTORES_CARGA,
                                    empuje_flotacion_kn_m,
                                    factores_carga_flotacion,
                                    filas_ev_de_la_tabla,
                                    peso_relleno_kn_m,
                                    verificaciones_estructurales)
from src.tolerancias import TOL_UMBRAL_NORMATIVO

# DE DONDE SALEN EL TIRANTE Y LA VELOCIDAD QUE V1 Y V2 COMPARAN, dicho una
# vez (EXT-3; EXT-M-01, v8 §4.1; E-A). Tres regimenes y no dos: LLENO (TW >=
# D: el tirante es D y la velocidad Q_celda/A_llena), UNIFORME (parcialmente
# lleno bajo control de ENTRADA: los numeros de M3 valen) y PERFIL
# (parcialmente lleno bajo control de SALIDA: el control esta aguas abajo, la
# lamina sube desde max(y_c, TW) hacia la entrada y el tirante maximo y la
# velocidad minima del barril salen del perfil de la lamina de agua que M4
# resuelve por paso directo desde E-A, `ResultadoHidraulico.perfil`, paso
# 4.3c/4.3d). Hasta E-A el tercero no existia y las dos verificaciones lo
# decian con `MetodoNoEvaluableError`, que la corrida convierte en Bloqueo:
# diferible a nivel de perfil, no de expediente. Esa excepcion queda como el
# FALLBACK de un resultado que no trae perfil --M4 lo llena siempre; solo un
# `ResultadoHidraulico` armado a mano puede venir sin el-- y no se inventa un
# criterio de llenado para cerrarla.
PROCEDIMIENTO_PERFIL_LAMINA = (
    "el perfil de la lamina de agua a lo largo del conducto (HDS-5 Section "
    "3.5), que desde E-A calcula `M4.perfil_lamina` y viaja en "
    "`ResultadoHidraulico.perfil`: este resultado no lo trae")
MOTIVO_V1_V2_PENDIENTES = (
    "bajo control de SALIDA con el barril PARCIALMENTE LLENO el tirante y la "
    "velocidad dentro del conducto no son los del flujo uniforme de Manning "
    "y no se conocen sin el perfil de la lamina; no se inventa un criterio "
    "de llenado (v8 §4.1)")

REGIMEN_LLENO = "lleno"
REGIMEN_UNIFORME = "uniforme"
REGIMEN_PERFIL = "perfil"


def _regimen_de_v1_v2(codigo: str, resultado: ResultadoHidraulico,
                      id_punto: Optional[str]) -> str:
    """
    `REGIMEN_LLENO` si el barril va LLENO, `REGIMEN_UNIFORME` si va
    parcialmente lleno bajo control de ENTRADA (los numeros de M3 valen),
    `REGIMEN_PERFIL` si va parcialmente lleno bajo control de SALIDA con el
    perfil de la lamina en el resultado (E-A), y `MetodoNoEvaluableError` si
    va parcialmente lleno bajo control de SALIDA sin perfil. Es la UNICA
    bifurcacion por regimen de V1 y V2, y por eso esta escrita una vez.
    """
    if resultado.regimen_barril is RegimenBarril.LLENO:
        return REGIMEN_LLENO
    # --- T-2 --- (INF-5.1.6) EL BARRIL HORIZONTAL VA SIEMPRE POR EL PERFIL,
    # tambien cuando el mayor HW es el de la entrada: con S = 0 no hay
    # tirante normal ni velocidad uniforme que comparar (`y_normal` es None),
    # y la lamina dentro del conducto es la que sube desde la salida (H2).
    if (resultado.control_gobernante is ControlGobernante.SALIDA
            or resultado.sin_tirante_normal):
        if resultado.perfil is None:
            raise MetodoNoEvaluableError(
                que=codigo, procedimiento=PROCEDIMIENTO_PERFIL_LAMINA,
                motivo=MOTIVO_V1_V2_PENDIENTES, id_punto=id_punto)
        return REGIMEN_PERFIL
    return REGIMEN_UNIFORME

# Los TRES numerales de las verificaciones hidraulicas se escriben largos, y
# por el mismo motivo: son lo UNICO que la memoria imprime de cada
# verificacion (M11 los vuelca en la columna "numeral"), de modo que el
# sustento tiene que viajar aqui dentro o el revisor no lo ve. El titulo de la
# tabla, la pagina y el CARACTER de la frase vivian solo en el comentario de
# constantes_normativas y en docs/manifiesto_citas.md, que no van al
# expediente.
#
# V1 iba pelado -- "4.1.1.3.7 b)" -- y eso era un trato asimetrico sin
# fundamento (MAT-O13, NOR-HID-10): el 0.75 de V1 y el 0.25 de V2 salen del
# MISMO tipo de frase ("se recomienda") del mismo apartado 4.1.1.3, y solo V2
# llevaba el matiz. Un revisor que viera "recomienda, no prohibe" en V2 y un
# numeral desnudo en V1 leeria que el borde libre es exigencia y el piso de
# velocidad no, cuando la fuente los escribe igual.
NUMERAL_V1 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.7 b) "Borde libre", '
              'pag. impresa 79. El numeral RECOMIENDA este borde libre ("Se '
              'recomienda que el diseño hidraulico considere como minimo el '
              '25 % de la altura, diametro o flecha de la estructura"), no lo '
              'prohibe: aqui se aplica como umbral duro por decision '
              'conservadora del proyecto, igual que el piso de V2')
# V2 y V3 salen ademas del MISMO numeral -- 4.1.1.3.6 -- y de paginas
# contiguas: la Tabla Nº 10 esta en la 76 y el parrafo que la sigue termina en
# la 77. Lo que separa un piso de un techo no es el numero: es el titulo de la
# tabla y ese parrafo.
NUMERAL_V2 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.6, parrafo '
              'inmediatamente posterior a la Tabla Nº 10: arranca en la pag. '
              'impresa 76 y el valor se imprime en la 77. El numeral '
              'RECOMIENDA este minimo ("recomendandose que la velocidad '
              'minima sea igual a 0.25 m/s"), no lo prohibe: aqui se aplica '
              'como umbral duro por decision conservadora del proyecto. Se '
              'evalua con la velocidad de la rama de n MAXIMO -- la '
              'estimacion baja --, que es el extremo conservador para un piso')
NUMERAL_V3 = ('MC-HHD (RD 20-2011-MTC/14), Tabla Nº 10 "Velocidades maximas '
              'admisibles (m/s) en conductos revestidos", num. 4.1.1.3.6, '
              'pag. impresa 76; fuente de la tabla: HCANALES, Maximo Villon B. '
              'Los DOS numeros de cada fila son MAXIMOS -- lo dice el titulo --, '
              'de modo que se verifica solo el superior y el piso lo pone V2. '
              'Que el rango recorra la calidad del revestimiento es '
              'INTERPRETACION DEL PROYECTISTA y no del Manual: se declara '
              'aparte, en el bloque "Umbrales normativos y su caracter" de '
              'esta memoria. Se '
              'evalua con la velocidad de la rama de n MINIMO -- la estimacion '
              'alta --, que es el extremo conservador para un techo')
NUMERAL_V4 = ReferenciaNormativa(
    seccion_hoja_ruta="Sec. 5.1",
    numeral_norma="Manual de Suelos, Geologia, Geotecnia y Pavimentos (MTC), "
                  "num. 4.5.4 y 9.1(3)",
)
# V4b NO tiene numeral normativo, y el rotulo lo dice: el HDS-5 describe la
# banda de practica de las agencias de EE. UU., no la prescribe, y el MTC no
# fija HW/D alguno (NOR-HDS-02). Escribir aqui "HDS-5 num. 2.2.5 d)" a secas
# haria pasar por exigencia lo que la memoria tiene que presentar como
# adopcion del proyectista.
NUMERAL_V4B = ("Fase 5, V4b -- adopcion del proyectista ('HW_D_max' [A]). "
               "NO es exigencia: el HDS-5, num. 2.2.5 d) 'Agency "
               "Constraints', pag. impresa 2.10, DESCRIBE la banda 1.0-1.5 "
               "que imponen las agencias viales de EE. UU., y el MTC no fija "
               "HW/D alguno")

# V2b lleva numeral y pagina porque la mitad evaluable SI los tiene desde
# S20 -- el HDS-5 3.a ed. num. 5.3.3 --, y lleva ademas el matiz por la misma
# razon que V1 y V2: la fuente nombra un INDICADOR y el proyecto decide como
# lo aplica. Desde PF-4 esa decision es el criterio [A] `regimen_v2b` y el
# numeral lo nombra en vez de llamarla «decision conservadora del proyecto»,
# que era la frase con que un [A] vivia cableado y sin ficha. Un numeral
# pelado haria pasar por exigencia lo que la fuente escribe como sintoma.
NUMERAL_V2B = ('HDS-5 3.a ed. (FHWA-HIF-12-026), num. 5.3.3 "Sedimentation", '
               'pag. impresa 5.11. El numeral NO fija un umbral: nombra dos '
               'INDICADORES ("barrel slope less than the natural channel and '
               'roughness greater than the channel are key indicators of '
               'potential problems"). Aqui se evalua el PRIMERO, y como se '
               "aplica lo declara el criterio 'regimen_v2b' [A] (umbral duro "
               'que detiene el punto, o indicador con aviso que no descarta '
               'el diametro); el segundo '
               'exige el n de Manning del cauce natural, que no es columna de '
               'Sec. 1.2, y queda declarado pendiente. La otra mitad de la '
               'fila V2b de la hoja de ruta -- el acceso de mantenimiento en '
               'planos -- entra por el criterio '
               "'acceso_mantenimiento_v2b' [A]")
# VC1 NO ES UN NUMERAL DEL MTC Y EL ROTULO TIENE QUE DECIRLO. El requisito lo
# fija la Sec. 2.3 de la hoja de ruta, en prosa; el Manual no fija borde libre
# para un canal (verificado por ausencia sobre sus 225 paginas). Lo unico que
# viene de un numeral es el par de valores, y viene de uno cuyo objeto es un
# BADEN. Escribir aqui «num. 4.1.1.4.1 e)» a secas haria pasar por exigencia
# sobre un canal lo que la fuente recomienda sobre otra obra -- que es el
# mismo defecto que NUMERAL_V4B evita con el HDS-5.
NUMERAL_VC1 = ("Sec. 2.3 (requisito de la Familia C: «No puede alterar la "
               "rasante hidraulica ni el borde libre del canal»). El Manual "
               "de Hidrologia NO fija borde libre para un canal: sus dos "
               "apartados de «Borde libre» son de alcantarillas "
               "(num. 4.1.1.3.7 b) y de badenes (num. 4.1.1.4.1 e). El "
               "resguardo de 0.30-0.50 m que este umbral usa sale del "
               "SEGUNDO, pag. impresa 85, donde el Manual lo RECOMIENDA para "
               "un baden y lo mide contra la superficie de rodadura; "
               "aplicarlo a la coronacion de un canal es analogia declarada "
               "del proyectista, y elegir el 0.50 dentro de la banda es una "
               "segunda decision suya. Las dos van en el criterio "
               "'borde_libre_canal_m' [A]")
NUMERAL_V5 = "Fase 5, V5 (DG-2018 + Ley 29338)"
NUMERAL_V6 = "3.1"
NUMERAL_V7 = ("Fase 5, V7 (subpresion: Manual de Puentes num. 2.4.3.8.2; "
              "equilibrio de factores de carga: Manual de Puentes Tablas "
              "2.4.5.3.1-1 y 2.4.5.3.1-2, pag. impresa 143, con la fila de "
              "gamma_p elegida por estructura en 'factores_carga_aashto'; "
              "procedimiento: Fase 8, item 3)")
NUMERAL_V8 = "Fase 5, V8"
NUMERAL_V9 = "Sec. 3.2 (V9, nuevo en v7)"
# --- T-2 --- V10 lleva su sustento LARGO, como V1, V2 y V2b, y por la misma
# razon: es lo unico que la tabla de verificaciones imprime. Los dos limites
# son adopciones [A]; lo que las fuentes dicen --y lo que NO dicen-- va aqui.
NUMERAL_V10 = ('MC-HHD (RD 20-2011-MTC/14), num. 4.1.1.3.3 "Pendiente '
               'longitudinal", pag. impresa 71: exige que la pendiente no '
               'altere "desmesuradamente" la erosion y la sedimentacion, SIN '
               'fijar cifra. La banda es adopcion del proyectista '
               "('pendiente_minima_conducto' y 'pendiente_maxima_conducto' "
               '[A]) sobre lo que el HDS-5 3.a ed. describe: admite el barril '
               'horizontal (num. 3.3.4, pag. impresa 3.25) y dice que la '
               'mayoria de las alcantarillas se construyen por debajo del '
               '10 %, sin medidas estructurales especiales (num. 5.4.4, pag. '
               'impresa 5.16)')

CRITERIO_RESGUARDO = "resguardo_HW_subrasante"
CRITERIO_REMANSO = "remanso_derecho_via"
CRITERIO_EVENTO_EXTREMO = "TR_evento_extremo"
# --- T-7b --- el umbral con que V8 juzga el «no colapso».
CRITERIO_UMBRAL_V8 = "umbral_no_colapso_evento_extremo"
# La mitad [A] de la fila V2b: el acceso de mantenimiento en planos.
CRITERIO_ACCESO_MANTENIMIENTO = "acceso_mantenimiento_v2b"
# El REGIMEN con que se aplica la mitad evaluable de V2b (PF-4): umbral duro
# que detiene el punto, o indicador con aviso que no descarta el diametro.
# Las dos opciones se leen de la ficha (`sensibilidad`), que es el conjunto
# cerrado; aqui se nombran para la guardia de segunda linea y los veredictos.
CRITERIO_REGIMEN_V2B = "regimen_v2b"
REGIMEN_V2B_UMBRAL_DURO = "umbral_duro"
REGIMEN_V2B_INDICADOR_CON_AVISO = "indicador_con_aviso"
REGIMENES_V2B = (REGIMEN_V2B_UMBRAL_DURO, REGIMEN_V2B_INDICADOR_CON_AVISO)
# La regla con la que se obtiene la cota de fondo de entrada (V4, V7 y 7.A).
CRITERIO_ORIGEN_COTA_ENTRADA = "origen_cota_fondo_entrada"
# El resguardo bajo la coronacion del canal que VC1 no deja invadir. Es de
# CORREDOR y no columna: no se mide, se adopta (ver su ficha).
CRITERIO_BORDE_LIBRE_CANAL = "borde_libre_canal_m"
# Reglas IMPLEMENTADAS: clave = valor que el proyectista declara en el
# criterio, valor = campo de `PuntoCritico` del que sale la cota. No hay
# aritmetica ninguna aqui -- cada regla es la lectura de una columna que el
# CSV ya trae -- y por eso la tabla no contiene ningun valor de proyecto:
# contiene el nombre de la columna que la declaracion elige.
# LAS REGLAS IMPLEMENTADAS para obtener el invert cuando NO viene medido.
# Clave: lo que el proyectista declara en 'origen_cota_fondo_entrada'. Valor:
# el campo de `PuntoCritico` del que se lee.
#
# SON DOS DESDE QUE EL CSV TRAE `cota_fondo_entrada`, y la segunda no es una
# regla mas: es la puerta por la que el DATO MEDIDO entra al mismo mecanismo.
# Declararla explicitamente --- en vez de dejar que la precedencia de
# `cota_de_entrada` sea el unico sitio donde el dato existe --- es lo que
# permite al proyectista PEDIRLA a proposito y que la corrida se detenga con
# `DatoFaltanteError` si la columna va vacia, en vez de caer en silencio a la
# regla del terreno. Las dos lecturas son legitimas y no son la misma:
#
#   'cota_fondo_entrada'  «usa el fondo medido, y si no esta, parate»
#   (sin declarar nada)   «usa el medido si esta; si no, la regla de abajo»
ORIGENES_COTA_ENTRADA = {
    "cota_terreno": "cota_terreno",
    "cota_fondo_entrada": "cota_fondo_entrada",
}
# Techo OPCIONAL del concreto. Se lee con `valor_si_declarado`, no con
# `valor`: sin declarar no bloquea nada y V3 usa el maximo [N] de la tabla.
CRITERIO_V_MAX_CONCRETO = "v_max_concreto_eleccion"
# C05 (PC-24): el valor que V1 y V2 aplican como umbral duro es una ADOPCION
# [A] --- las dos cifras llegan con «se recomienda» --- y vive en
# criterios_adoptados.py con el valor recomendado por defecto. La cifra de la
# fuente sigue siendo [N] en constantes_normativas.py (Y_SOBRE_D_MAX, V_MIN):
# tabla y eleccion separadas. El contrato es el de
# 'riesgo_admisible_propietario' en M1: solo se puede ENDURECER.
CRITERIO_BORDE_LIBRE = "borde_libre_y_sobre_d_max"
CRITERIO_V_MIN = "velocidad_minima_autolimpieza_m_s"

# --- T-2 --- (cadena T, 2026-11-11) -----------------------------------------
# LA LECTURA DEL BORDE LIBRE CUANDO EL BARRIL VA LLENO POR EL RECEPTOR
# (INF-3.2.6), y LA BANDA DE PENDIENTE DEL CONDUCTO (INF-3.2.7). Los tres son
# criterios [A] de perfil con ventana; las fichas dicen que sostiene cada
# valor. `limites_de_pendiente()` es la lectura UNICA de la banda: la usa V10
# aqui y la usa M7 (`pendiente_adoptada`, desde T-6) para decir si la
# pendiente adoptada la gobierna la minima o la maxima.
CRITERIO_BORDE_LIBRE_BAJO_TW = "borde_libre_bajo_tw_ahogante"
LECTURA_TW_NO_CUMPLE = "no_cumple"
LECTURA_TW_AVISO = "aviso"
LECTURAS_BAJO_TW = (LECTURA_TW_NO_CUMPLE, LECTURA_TW_AVISO)
CRITERIO_PENDIENTE_MINIMA = "pendiente_minima_conducto"
CRITERIO_PENDIENTE_MAXIMA = "pendiente_maxima_conducto"


def _lectura_bajo_tw_ahogante() -> str:
    """
    La lectura declarada en 'borde_libre_bajo_tw_ahogante', validada como
    segunda linea (la puerta ya exige la categoria): forma MAT-D13.
    """
    lectura = ca.valor(CRITERIO_BORDE_LIBRE_BAJO_TW)   # CriterioPendienteError
    if not (isinstance(lectura, str) and lectura in LECTURAS_BAJO_TW):
        raise DatoInvalidoError(
            campo=CRITERIO_BORDE_LIBRE_BAJO_TW, valor=lectura,
            motivo=(f"'{CRITERIO_BORDE_LIBRE_BAJO_TW}' vale {lectura!r} y las "
                    f"unicas opciones son "
                    f"{', '.join(map(repr, LECTURAS_BAJO_TW))}: es un "
                    "conjunto cerrado"))
    return lectura


def limites_de_pendiente() -> Tuple[float, float]:
    """
    (S_min, S_max): la banda de pendiente del conducto que el proyecto
    adopta, de los criterios [A] 'pendiente_minima_conducto' y
    'pendiente_maxima_conducto' (Manual num. 4.1.1.3.3, sin cifra; HDS-5 num.
    3.3.4 y 5.4.4).

    Es la lectura unica de la banda, con su guardia cruzada: una minima mayor
    que la maxima no deja pendiente admisible y es un par de declaraciones
    que se contradicen, no un dato del punto. Forma MAT-D13: condicion en
    positivo y negada, mensaje con el PAR culpable.
    """
    s_min = float(ca.valor(CRITERIO_PENDIENTE_MINIMA))
    s_max = float(ca.valor(CRITERIO_PENDIENTE_MAXIMA))
    if not s_min >= 0:
        raise DatoInvalidoError(
            CRITERIO_PENDIENTE_MINIMA, valor=s_min,
            motivo="la pendiente minima del conducto no puede ser negativa: "
                   "0 es el barril horizontal, y la pendiente adversa no se "
                   "admite")
    if not s_min <= s_max:
        raise DatoInvalidoError(
            CRITERIO_PENDIENTE_MAXIMA, valor=s_max,
            motivo=f"la banda de pendiente del conducto queda vacia con el "
                   f"par ('{CRITERIO_PENDIENTE_MINIMA}' = {s_min}, "
                   f"'{CRITERIO_PENDIENTE_MAXIMA}' = {s_max}): la minima "
                   "supera a la maxima y ninguna pendiente cumpliria V10")
    return s_min, s_max


def _umbral_adoptado_v1() -> float:
    """
    El y/D maximo que V1 aplica: el criterio [A] 'borde_libre_y_sobre_d_max',
    que solo puede endurecer el 0.75 de la recomendacion (num. 4.1.1.3.7 b)).
    Forma MAT-D13: condicion en positivo y negada, par culpable nombrado.
    """
    adoptado = float(ca.valor(CRITERIO_BORDE_LIBRE))
    if not adoptado <= Y_SOBRE_D_MAX + TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            CRITERIO_BORDE_LIBRE, valor=adoptado,
            motivo=f"el Manual recomienda como minimo el 25 % de borde libre, "
                   f"o sea y/D <= {Y_SOBRE_D_MAX}; el proyecto puede exigir "
                   f"MAS borde libre (un y/D menor) pero no menos: {adoptado} "
                   "relaja la recomendacion en vez de adoptarla, y eso no es "
                   "una decision del proyectista sino salirse de lo que la "
                   "fuente concede",
        )
    return adoptado


def _umbral_adoptado_v2() -> float:
    """
    El piso de velocidad que V2 aplica: el criterio [A]
    'velocidad_minima_autolimpieza_m_s', que solo puede endurecer los
    0.25 m/s de la recomendacion (num. 4.1.1.3.6).
    """
    adoptado = float(ca.valor(CRITERIO_V_MIN))
    if not adoptado >= V_MIN - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            CRITERIO_V_MIN, valor=adoptado,
            motivo=f"el Manual recomienda una velocidad minima de {V_MIN} m/s; "
                   f"el proyecto puede exigir un piso MAYOR pero no menor: "
                   f"{adoptado} m/s relaja la recomendacion en vez de "
                   "adoptarla, y eso no es una decision del proyectista sino "
                   "salirse de lo que la fuente concede",
        )
    return adoptado


# ---------------------------------------------------------------------------
# Filas de Fase 5 que este modulo no evalua: desde S20, ninguna
# ---------------------------------------------------------------------------

CLAVE_HW_D_MAX = "HW_D_max"


def verificaciones_no_evaluadas() -> Tuple[str, ...]:
    """
    Las filas de la tabla de Fase 5 que este modulo NO implementa como
    verificacion. Desde S20 la tupla esta VACIA: se evaluan todas (once
    entonces, doce desde T-2).

    Misma forma y mismo proposito que
    `M8_estructural.verificacion_diferida_estructural`: lo que queda fuera del
    alcance del script no se calcula ni se aproxima, se declara con su
    fundamento para que la memoria lo imprima. Un requisito que desaparece sin
    dejar rastro es lo que este proyecto persigue.

    POR QUE SIGUE EXISTIENDO UNA FUNCION QUE HOY DEVUELVE (). Porque su forma
    es la del CONJUNTO de filas diferidas, no la de la fila que en un momento
    dado lo este. Ya paso dos veces: contenia dos constancias (V2b y V4b),
    quedo con una al cablearse V4b en S14, y quedo con ninguna al cablearse
    V2b en S20. El dia que otra se difiera entra aqui sin tocar a ningun
    llamador, y mientras tanto M11 imprime la afirmacion positiva -- que
    ninguna queda sin evaluar --, que es informacion y no un hueco.

    QUE PASO CON LA CONSTANCIA DE V2b, para que nadie la busque. No se
    BORRO: se CONVIRTIO. Su mitad evaluable es hoy `v2b_sedimentacion`, con
    el numeral 5.3.3 del HDS-5 que la sostiene; su mitad de expediente -- el
    acceso de mantenimiento en planos -- es hoy el criterio
    'acceso_mantenimiento_v2b', que DETIENE la corrida mientras siga vacio en
    vez de imprimir un parrafo que nadie tiene que contestar. La obligacion
    no se relajo: se endurecio.

    El nombre era `verificacion_diferida_v2b` y se renombro al incorporar la
    de V4b: una funcion que devolvia dos constancias no podia llamarse por una
    sola de ellas. El nombre plural se conserva por lo mismo que la tupla.
    """
    return ()


# ---------------------------------------------------------------------------
# La traza de la memoria: como este modulo la emite
# ---------------------------------------------------------------------------
# Cada verificacion devuelve su `Verificacion` COMO SIEMPRE y ademas el
# `PasoDeMemoria` que la explica. No es informacion nueva: es la que la
# funcion ya tenia delante -- de donde salio cada numero, contra que se
# compara, con que margen -- y que hasta S18 se perdia al devolver solo el
# veredicto, obligando a M11 a reconstruirla desde los resultados (SIS-A-07).
#
# `_umbral_de` arma el `Umbral` desde `UMBRALES_DE_VERIFICACION`, que es donde
# viven el caracter de la fuente y lo que el proyecto hace con el. NO se
# escriben aqui: la memoria y el codigo tienen que citar el mismo objeto o
# divergen, que es literalmente NOR-MEM-01.

# codigo de verificacion -> id de la cita del registro que fija SU umbral. Es
# la cita que lleva el NUMERO, que no siempre es la primera del bloque: la de
# V2 es la segunda mitad del parrafo ("recomendandose que la velocidad minima
# sea igual a 0.25 m/s"), porque la primera obliga a verificar y no dice
# cuanto.
CITA_DEL_UMBRAL = {
    "V1": "MC_HHD.4.1.1.3.7b",
    "V2": "MC_HHD.4.1.1.3.6#VMIN",
    # V2b: la cita que lleva la COMPARACION, no la que da la contracara.
    "V2b": "HDS5_3ED.5.3.3#INDICADORES",
    "V3": "MC_HHD.4.1.1.3.6#T10",
    "V4": "MS.4.5.4",
    # VC1: la cita que lleva el NUMERO es la del rango, no la que obliga a
    # dejar borde libre -- mismo reparto que en V2. Y aqui importa el doble,
    # porque la que obliga es EXIGENCIA: anclarle el umbral a ella haria que
    # la memoria imprimiera el 0.50 con caracter de exigencia sobre un canal,
    # cuando la fuente lo recomienda sobre un baden.
    "VC1": "MC_HHD.4.1.1.4.1e#RANGO",
    "V7": "MP.T2.4.5.3.1-2",
    # --- T-2 --- V10: la cita que lleva el NUMERO de la banda (el 10 %). La
    # del Manual obliga a estudiar la pendiente y no dice cuanto.
    "V10": "HDS5_3ED.5.4.4#PENDIENTE_10",
}


def _umbral_de(codigo: str, *, valor, unidad: str,
               descripcion: str, criterio: str = None) -> Umbral:
    """
    El `Umbral` de una verificacion, con su caracter y su aplicacion leidos de
    `UMBRALES_DE_VERIFICACION` y no reescritos aqui.
    """
    u = UMBRALES_POR_CODIGO[codigo]
    return Umbral(descripcion=descripcion, valor=valor, unidad=unidad,
                  cita_id=CITA_DEL_UMBRAL[codigo],
                  caracter=caracter_del_umbral(u),
                  aplicacion=u["aplicacion"],
                  criterio_aplicado=criterio)


def _veredicto(cumple: bool, margen: float, unidad: str,
               explicacion: str) -> Veredicto:
    return Veredicto(
        tipo=TipoDeVeredicto.CUMPLE if cumple else TipoDeVeredicto.NO_CUMPLE,
        margen=margen, unidad=unidad, explicacion=explicacion)


# ---------------------------------------------------------------------------
# La advertencia de alcance de la Familia C, junto al numero (§15.6.3)
# ---------------------------------------------------------------------------
# LA DECLARACION ENTERA NO VIVE AQUI, y es deliberado: vive en
# `cli.DECLARACION_ALCANCE_FAMILIA_C` y sale UNA VEZ por punto en el bloque de
# alcance de la memoria. Lo que sale aqui es la mitad que aquel bloque no
# puede dar -- el aviso PEGADO AL NUMERO que se acaba de calcular --, y es la
# leccion de NOR-HDS-05: un aviso que no señala el punto afectado es el «nadie
# se entera». Repetir la declaracion entera en cada paso seria el defecto
# contrario, y por eso esta nota REMITE a ella en vez de transcribirla.
#
# `contra` es lo que hace util a esta nota y no un adorno: el argumento de
# §15.6.2 es que la sustitucion NO es conservadora porque los umbrales que si
# se evaluan MIDEN CONTRA OTRA COTA. Nombrar en cada verificacion contra que
# mide ESA es lo que convierte el argumento general en una lectura del numero
# que el revisor tiene delante.
# REESCRITA AL IMPLEMENTARSE VC1, Y ESE ES EL PUNTO. La redaccion anterior
# decia, palabra por palabra, que el requisito de la Sec. 2.3 «NO se evalua en
# esta corrida» y que la verificacion que lo evaluaria «necesita el nivel de
# agua de diseño del canal y su borde libre, que no son columna de la Sec. 1.2
# ni los aporta ningun tablero». Las dos mitades dejaron de ser ciertas: VC1
# existe y se evalua, y la columna `cota_coronacion_canal` es de la Sec. 1.2.
#
# DEJARLA MINTIENDO HABRIA SIDO PEOR QUE NO HABERLA ESCRITO, y es SIS-A-03: un
# texto de alcance que describe un estado del programa que ya no existe se lee
# con la autoridad de una declaracion y desinforma con ella. Tampoco se BORRA,
# que es el otro extremo: la mitad del requisito que sigue sin evaluarse
# necesita seguir dicha, y ahora se puede decir con precision cual es.
NOTA_ALCANCE_FAMILIA_C = (
    "ALCANCE (Familia C -- cruce de canal o dren): ESTE umbral mide contra "
    "{contra}, no contra el canal. Contra el canal mide VC1, que SI se evalua "
    "en esta corrida: es la verificacion del requisito de la Sec. 2.3 y "
    "compara el nivel que el agua alcanza a la entrada con la coronacion del "
    "canal menos su borde libre. Cumplir ESTE umbral sigue sin decir nada "
    "sobre la admisibilidad de la obra COMO CRUCE DE CANAL: eso lo dice VC1, "
    "y hay que leer las dos filas. LO QUE VC1 TAMPOCO CIERRA, y queda "
    "declarado: la Sec. 2.3 pide dos cosas -- no alterar la rasante "
    "hidraulica NI el borde libre -- y VC1 cierra la segunda. La primera "
    "exige el tirante normal del canal en la seccion del cruce (su geometria "
    "trapecial y su n de Manning, que no son columna de la Sec. 1.2) y la "
    "extension aguas arriba del remanso. Ver el bloque «Alcance declarado de "
    "la corrida», etapa «VC1»."
)

# LA MISMA ADVERTENCIA, DICHA DESDE DENTRO DE VC1. No es la de arriba con otro
# texto: aquella avisa al lector de un umbral que NO mira el canal de que
# existe otro que si; esta avisa al lector del que SI mira el canal de hasta
# donde llega. Un paso que acredita media Sec. 2.3 y se imprime como si
# acreditara la Sec. 2.3 entera es la forma de NOR-MEM-01 --- cierto sobre el
# codigo, falso sobre el producto --- aplicada al veredicto mas importante de
# esta familia.
NOTA_VC1_LO_QUE_NO_MIDE = (
    "QUE ACREDITA ESTE VEREDICTO Y QUE NO. La Sec. 2.3 pide dos cosas al "
    "cruce de canal: que no altere la RASANTE HIDRAULICA del canal y que no "
    "altere su BORDE LIBRE. VC1 verifica la segunda: el agua embalsada no "
    "invade el resguardo bajo la coronacion. NO verifica la primera: acota el "
    "nivel que el agua alcanza, no mide en cuanto la obra levanta el pelo de "
    "agua respecto del que el canal tendria sin ella, de modo que un punto "
    "puede cumplir VC1 con holgura y aun asi haber subido la rasante "
    "hidraulica del canal en una fraccion apreciable de su calado. Cerrar esa "
    "mitad exige dos cosas que esta corrida no tiene: el tirante normal del "
    "canal en la seccion del cruce -- que necesita su geometria trapecial "
    "(ancho de solera y talud) y su n de Manning, ninguno de los dos columna "
    "de la Sec. 1.2 -- y la extension aguas arriba del remanso, que VC1 "
    "tampoco acota: mide en LA SECCION DEL CRUCE. "
    "EL BORDE LIBRE ADOPTADO NO ES EL DEL CANAL: es el que el proyecto adopta "
    "por analogia con el de un baden. El del propio canal lo fija quien lo "
    "opera (ANA / Junta de Usuarios), y si ese fuera mayor que el adoptado, "
    "esta verificacion seria menos exigente que el proyecto del canal."
)


def _nota_de_alcance(punto: PuntoCritico, contra: str) -> str:
    """La nota de §15.6.3 si el punto es de Familia C; cadena vacia si no."""
    if punto.familia is not Familia.C:
        return ""
    return NOTA_ALCANCE_FAMILIA_C.format(contra=contra)


def _magnitud_de_llenado(material: Material) -> Tuple[str, str, str]:
    """
    Contra que dimension se mide el llenado del barril: simbolo, nombre y
    PROCEDENCIA, elegidos por la forma de la seccion.

    NO ES COSMETICA. El num. 4.1.1.3.7 b) no escribe «D»: escribe «el 25 % de
    la altura, diametro o flecha de la estructura», y esa enumeracion de tres
    magnitudes es lo que hace que el numeral cubra al marco SIN ANALOGIA
    NINGUNA -- por eso V1 sigue siendo [N] puro tambien para el cajon --. Lo
    que cambia con la forma es cual de las tres se sustituye, y la memoria
    tiene que decir cual, porque «D = 1.50 m» al lado de un cajon de 2.00 x
    1.50 es un numero que el revisor no puede ubicar.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return ("H", "la altura interior de la celda",
                "altura interior H de la seccion adoptada por el bucle de "
                "diseño (MD), de la progresion que el expediente declara en "
                "'secciones_cajon_normalizadas'")
    return ("D", "el diametro interior",
            "diametro adoptado por el bucle de diseño (MD), de la serie "
            "normalizada")


# ---------------------------------------------------------------------------
# V1 - Borde libre (Sec. 4.1.1.3.7 b)
# ---------------------------------------------------------------------------

def v1_borde_libre(*, D: float, material: Material, punto: PuntoCritico,
                  resultado: ResultadoHidraulico) -> Verificacion:
    """
    y/D <= 0.75: minimo 25 % de borde libre sobre el tirante normal.

    `D` ES LA ALTURA INTERIOR DEL BARRIL, cualquiera que sea su forma, y por
    eso esta funcion sirve al marco sin analogia: el numeral escribe "el 25 %
    de la altura, diametro o flecha de la estructura" -- las tres magnitudes
    en la misma oracion --, de modo que un cajon esta cubierto por el TEXTO y
    no por extension. Lo unico que cambia es COMO SE LLAMA la dimension que se
    sustituye, y eso lo resuelve `_magnitud_de_llenado` a partir de
    `material.forma`. `material` y `punto` entraron en la firma en C5 por esto
    y por la nota de alcance; hasta entonces V1 no necesitaba saber nada del
    punto.

    Texto que lo sustenta, literal (MC-HHD, RD 20-2011-MTC/14,
    num. 4.1.1.3.7 b) "Borde libre", pag. impresa 79):

        "Se recomienda que el diseño hidráulico considere como mínimo el 25 %
        de la altura, diámetro o flecha de la estructura."

    ES UNA RECOMENDACION, IGUAL QUE EL PISO DE V2, y esta funcion la aplica
    igualmente como umbral duro (`y/D <= y_sobre_D_max` decide `cumple`, con
    el 0.75 recomendado por defecto en 'borde_libre_y_sobre_d_max'), que es la
    lectura conservadora y la que el proyecto adopta. El matiz viaja en
    `NUMERAL_V1`, que es lo unico que la memoria imprime de V1. Hasta esta
    correccion `NUMERAL_V1` era el numeral desnudo mientras `NUMERAL_V2` si
    llevaba el matiz: dos frases del mismo apartado presentadas con distinta
    fuerza normativa, sin nada en la fuente que lo justificara (MAT-O13,
    NOR-HID-10).

    EL TIRANTE QUE SE COMPARA ES EL DEL REGIMEN DEL BARRIL (EXT-3; EXT-M-01,
    v8 §1.3 y §4.1 enmendadas en EXT-0), y solo en flujo uniforme es
    `y_normal`:

      * barril LLENO (TW >= D, `ResultadoHidraulico.regimen_barril`): el
        tirante es D entero, y/D = 1. Aqui el veredicto no se
        apoya en la recomendacion del 25 % sino en la exigencia del mismo
        parrafo --«las alcantarillas no deben ser diseñadas para trabajar a
        seccion llena» (pag. impresa 79, `MC_HHD.4.1.1.3.7b#LLENA`)--, que
        viaja como cita textual del paso. Hasta EXT-3 esta funcion media el
        tirante normal tambien ahi y daba [OK] con y/D = 0.135 sobre un
        barril que la misma memoria decia ahogado.
        DESDE T-2 (INF-3.2.6) ESE CASO TIENE NOMBRE Y CRITERIO: es el barril
        lleno POR EL NIVEL DEL RECEPTOR, y lo que V1 hace lo declara el [A]
        'borde_libre_bajo_tw_ahogante'. «no_cumple» (valor del archivo, la
        conducta de EXT-3): NO CUMPLE. «aviso»: el borde libre se juzga con
        el tirante PROPIO del caudal de diseño --`y_normal`--; si lo
        conserva, `cumple=True` con veredicto INDICADOR y el diametro no se
        descarta; si no, NO CUMPLE igual. La memoria imprime cual aplico.
        EL MISMO CRITERIO GOBIERNA EL TRAMO ANTERIOR, cuando el TW queda
        entre el llenado admisible y la clave (0.75·D < TW < D) y es el
        tirante maximo del perfil: el borde libre lo toma el receptor igual
        que con el barril lleno, y la lectura no puede cambiar al cruzar
        TW = D. Bajo «no_cumple» nada se mueve (V1 ya no cumplia ahi, por el
        tirante maximo del perfil); bajo «aviso» la lectura es continua y
        monotona en el TW.
        Y el otro caso, el barril lleno POR EL CAUDAL DE DISEÑO (la lamina
        del perfil toca la clave con TW < D), NO CUMPLE siempre, con la
        misma cita, sin que el criterio intervenga.
      * parcialmente lleno bajo control de ENTRADA: `y_normal`, resuelto con
        n_max (rama de capacidad): mas rugosidad da mas tirante para el mismo
        Q, o sea el extremo conservador para una verificacion de borde libre.
      * parcialmente lleno bajo control de SALIDA: el tirante dentro del
        conducto no es el uniforme --el control esta aguas abajo-- y desde
        E-A sale del perfil de la lamina de agua: `perfil.y_max_m`, el
        tirante MAXIMO a lo largo del barril (M4, paso 4.3c/4.3d), con n_max.
        Hasta E-A esta funcion lo decia con `MetodoNoEvaluableError`, que
        queda como fallback de un resultado sin perfil (ver
        `_regimen_de_v1_v2`). No inventa un criterio de llenado.
      * barril HORIZONTAL (S = 0; T-2, INF-5.1.6): no hay tirante normal, y
        el tirante es el maximo del perfil cualquiera que sea el control que
        da la mayor carga.
    """
    simbolo, nombre, procedencia = _magnitud_de_llenado(material)
    regimen = _regimen_de_v1_v2("V1", resultado, punto.id)
    lleno = regimen == REGIMEN_LLENO
    y_sobre_D_max = _umbral_adoptado_v1()
    lleno_por_caudal = False
    if lleno:
        y = D
        procedencia_y = (
            "tirante del REGIMEN del barril (M4, paso 4.3b): la seccion va "
            "LLENA porque el TW alcanza la clave, y el tirante es la altura "
            "interior entera. NO es el tirante normal de Manning, que aqui "
            "no describe el flujo")
        citas_de_regimen = ("MC_HHD.4.1.1.3.7b#LLENA",)
    elif regimen == REGIMEN_PERFIL:
        y = resultado.perfil.y_max_m
        lleno_por_caudal = not y < D - TOL_UMBRAL_NORMATIVO
        procedencia_y = (
            "tirante MAXIMO del perfil de la lamina de agua (M4, paso 4.3c/"
            "4.3d, con n_max): "
            + ("el barril es HORIZONTAL (S = 0) y no tiene tirante normal, "
               "de modo que la lamina dentro del conducto es la que sube "
               "desde max(y_c, TW) hacia la entrada"
               if resultado.sin_tirante_normal else
               "el barril va parcialmente lleno bajo control "
               "de SALIDA, el control esta aguas abajo y la lamina sube desde "
               "max(y_c, TW) hacia la entrada, de modo que el tirante uniforme "
               "de Manning no describe el flujo")
            + "; el borde libre se juzga donde menos hay")
        # LLENO POR EL CAUDAL DE DISEÑO: la lamina toca la clave con el TW
        # por debajo de ella. Es el caso que la frase prohibitiva del
        # numeral describe sin matiz, y se cita.
        citas_de_regimen = (("MC_HHD.4.1.1.3.7b#LLENA",) if lleno_por_caudal
                            else ())
    else:
        y = resultado.y_normal
        procedencia_y = (
            "M3, tirante normal por Manning con la rama de n MAXIMO (mas "
            "rugosidad da mas tirante para el mismo Q: el extremo conservador "
            "para un borde libre); vale porque el barril va parcialmente "
            "lleno bajo control de ENTRADA, en regimen uniforme (M4, paso 4.3b)")
        citas_de_regimen = ()
    simbolo_y = {REGIMEN_LLENO: "y", REGIMEN_PERFIL: "y_max",
                 REGIMEN_UNIFORME: "y_normal"}[regimen]
    y_sobre_D = y / D
    cumple = y_sobre_D <= y_sobre_D_max + TOL_UMBRAL_NORMATIVO

    # --- T-2 --- (INF-3.2.6) QUIEN LE QUITA EL BORDE LIBRE AL BARRIL: el
    # caudal de diseño o el nivel del receptor. V1 separa los dos casos:
    #   * por el CAUDAL DE DISEÑO (la lamina toca la clave con el TW por
    #     debajo, o el tirante propio del caudal ya supera el llenado
    #     admisible): no cumple siempre, y ningun criterio interviene;
    #   * por el NIVEL DEL RECEPTOR: el TW queda por encima del llenado
    #     admisible (TW/D > y/D maximo) y es el quien fija el tirante maximo
    #     dentro del barril. Lo que V1 hace ahi lo declara el criterio [A]
    #     'borde_libre_bajo_tw_ahogante'.
    # EL CASO DEL RECEPTOR ES UNO SOLO A LO LARGO DE TODO EL TW, y no solo
    # con el regimen LLENO (TW >= D). La primera redaccion de T-2 lo
    # reconocia solo ahi, y el auditor adversarial midio la consecuencia en
    # A-02 (Q = 0.48 m3/s, S = 0.008): bajo «aviso», con TW = 0.80 y 0.89 m
    # el Ø 0.90 no pasaba; con TW = 0.90 pasaba; y con TW = 1.00 pasaba el
    # Ø 0.90 y fallaba el Ø 1.05. Mas ahogamiento era mas permisivo y el
    # tubo chico pasaba donde el grande no: una lectura discontinua en el TW
    # no sirve para barrer la sensibilidad. La condicion es ahora la misma
    # con el barril lleno y con el TW entre el llenado admisible y la clave:
    # el tirante maximo no supera al TW (lo fija el receptor, no el caudal).
    # EL BARRIL HORIZONTAL entra al caso por el TW solo: sobre un fondo plano
    # la lamina sube siempre hacia la entrada (H2) y el tirante maximo queda
    # por encima del TW, pero no hay tirante normal con que decir cuanto de
    # ese llenado es del caudal. Se reconoce el caso para DECIRLO: bajo
    # «aviso» no cumple igual, y la memoria explica por que.
    TW = resultado.TW_m
    remansado_por_receptor = (
        regimen == REGIMEN_PERFIL and not lleno_por_caudal
        and TW is not None
        and not TW / D <= y_sobre_D_max + TOL_UMBRAL_NORMATIVO
        and (not y > TW + TOL_UMBRAL_NORMATIVO
             or resultado.sin_tirante_normal))
    por_receptor = lleno or remansado_por_receptor
    lectura_tw = _lectura_bajo_tw_ahogante() if por_receptor else None
    aviso_por_tw = False
    sustitucion_extra: Tuple[Magnitud, ...] = ()
    elecciones: Tuple[EleccionDeProyecto, ...] = ()
    if por_receptor:
        # EL TIRANTE PROPIO DEL CAUDAL DE DISEÑO, que es lo que el diametro
        # puede resolver: el normal de Manning. En un barril horizontal no
        # existe, y entonces no hay con que separar los dos casos.
        y_propio = resultado.y_normal
        propio_cumple = (y_propio is not None and
                         y_propio / D <= y_sobre_D_max + TOL_UMBRAL_NORMATIVO)
        aviso_por_tw = lectura_tw == LECTURA_TW_AVISO and propio_cumple
        sustitucion_extra = (
            Magnitud("TW", TW if TW is not None
                     else "no informado", "m" if TW is not None
                     else "",
                     "tirante del receptor sobre el fondo de la salida, el "
                     "del paso 4.3: "
                     + ("alcanza o supera la clave del barril, y "
                        "por eso el regimen es LLENO POR EL NIVEL DEL "
                        "RECEPTOR, no por el caudal de diseño"
                        if lleno else
                        "queda por encima del llenado admisible y por debajo "
                        "de la clave, y es el tirante maximo dentro del "
                        "barril: el borde libre lo toma EL NIVEL DEL "
                        "RECEPTOR, no el caudal de diseño"),
                     cifras=CIFRAS_MAGNITUD if TW is not None
                     else None),
            (Magnitud("y_normal", y_propio, "m",
                      "tirante que el caudal de diseño tendria SIN el "
                      "remanso del receptor (M3, Manning con n_max): es "
                      "el llenado que depende del diametro, y el que se juzga "
                      "contra el borde libre cuando la lectura adoptada es "
                      "«aviso»", cifras=CIFRAS_MAGNITUD)
             if y_propio is not None else
             Magnitud("y_normal", "no existe (S = 0)", "",
                      "barril horizontal: no hay tirante normal con que "
                      "separar el llenado propio del caudal del remanso "
                      "del receptor, y V1 no cumple bajo las dos lecturas",
                      cifras=None)),
        )
        elecciones = (EleccionDeProyecto(
            que_se_adopto="lectura del borde libre cuando lo toma el nivel "
                          "del receptor (TW por encima del llenado "
                          "admisible, llegue o no a la clave)",
            valor=str(lectura_tw),
            entre=tuple(str(v) for v in
                        (ca.criterio(CRITERIO_BORDE_LIBRE_BAJO_TW).sensibilidad
                         or ())),
            de_donde=f"el criterio '{CRITERIO_BORDE_LIBRE_BAJO_TW}' [A]: el "
                     "numeral prohibe DISEÑAR para seccion llena y "
                     "recomienda un borde libre, y no distingue lo que "
                     "produce el caudal de lo que produce el receptor",
            por_que="«no_cumple» es la lectura literal: el riesgo de "
                    "obstruccion que el Manual invoca existe igual con el "
                    "barril remansado. «aviso» lee que la regla es sobre "
                    "el diseño del conducto: si con su propio caudal conserva "
                    "el borde libre, el remanso se declara y no descarta "
                    "el diametro, porque ningun diametro menor que el TW lo "
                    "resuelve. La eleccion y su consecuencia estan en la "
                    "ficha del criterio",
            cita_id="MC_HHD.4.1.1.3.7b#LLENA",
            clave_criterio=CRITERIO_BORDE_LIBRE_BAJO_TW),)
    umbral = _umbral_de(
        "V1", valor=y_sobre_D_max, unidad="",
        descripcion=f"y/{simbolo} maximo admisible (borde libre >= "
                    f"{1 - y_sobre_D_max:.0%} de {nombre})".replace("% de", " % de"),
        criterio=CRITERIO_BORDE_LIBRE)
    nota = (
        "El numeral RECOMIENDA este borde libre; aqui se aplica como umbral "
        f"duro por decision del proyecto, declarada en el criterio [A] "
        f"'{CRITERIO_BORDE_LIBRE}' (por defecto el 0.75 recomendado; solo "
        "se puede endurecer). La fuente no escribe "
        f"el 0.75 ni la razon y/{simbolo}: escribe «el 25 % de la altura, "
        "diametro o flecha de la estructura», y en esta seccion la magnitud "
        f"que corresponde de las tres es {nombre}.")
    if por_receptor:
        nota += (
            " CASO APLICADO: "
            + (f"barril LLENO POR EL NIVEL DEL RECEPTOR (TW >= {simbolo})"
               if lleno else
               "BORDE LIBRE TOMADO POR EL NIVEL DEL RECEPTOR (el TW queda "
               f"entre el llenado admisible y {nombre}"
               + (": el barril es horizontal y la lamina sube desde el hacia "
                  "la entrada)" if resultado.sin_tirante_normal else
                  ", y es el tirante maximo dentro del barril)"))
            + ", no por el caudal de diseño. Lo que V1 hace ahi lo "
            f"declara el criterio [A] '{CRITERIO_BORDE_LIBRE_BAJO_TW}', que "
            f"en esta corrida vale «{lectura_tw}»: "
            + (("NO CUMPLE, por la exigencia de la pag. impresa 79 leida al "
                "pie de la letra." if lleno else
                "NO CUMPLE: el borde libre se mide con el tirante del barril, "
                "venga de donde venga.")
               if lectura_tw == LECTURA_TW_NO_CUMPLE else
               "el borde libre se juzga con el tirante propio del caudal de "
               "diseño (y_normal); "
               + ("lo conserva, de modo que el remanso queda como AVISO "
                  "y no descarta el diametro."
                  if aviso_por_tw else
                  "NO lo conserva (o no existe, en un barril horizontal), de "
                  "modo que V1 NO CUMPLE igual."))
            + " El TW y su via estan en el paso 1.3; si sale de la seccion "
              "ADOPTADA del receptor, es esa adopcion la que decide.")
    elif lleno_por_caudal:
        nota += (
            " CASO APLICADO: barril LLENO POR EL CAUDAL DE DISEÑO -- la "
            "lamina toca la clave con el TW por debajo de ella --: NO CUMPLE "
            "por la exigencia de la pag. impresa 79, y el criterio "
            f"'{CRITERIO_BORDE_LIBRE_BAJO_TW}' no interviene.")
    de_alcance = _nota_de_alcance(
        punto, "la altura interior del propio barril")
    if aviso_por_tw:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.INDICADOR,
            margen=y_sobre_D_max - y_sobre_D, unidad="",
            explicacion=(
                ("el barril va LLENO POR EL NIVEL DEL RECEPTOR (TW >= D) y no "
                 "tiene borde libre durante la avenida"
                 if lleno else
                 "el NIVEL DEL RECEPTOR deja al barril con menos borde libre "
                 "del recomendado durante la avenida (TW por encima del "
                 "llenado admisible)")
                + "; con su propio caudal lo conservaria. Bajo "
                "borde_libre_bajo_tw_ahogante = aviso "
                "el diametro NO se descarta: ninguno menor que el TW lo "
                "resuelve, y lo que lo resuelve es la cota de la salida o la "
                "rasante. Queda como aviso: riesgo de obstruccion con el "
                "receptor en ese nivel"))
    else:
        veredicto = _veredicto(
            cumple, y_sobre_D_max - y_sobre_D, "",
            "margen de borde libre por encima del minimo adoptado"
            if cumple else
            "el barril va LLENO POR EL NIVEL DEL RECEPTOR (TW >= D): no hay "
            "borde libre, y la fuente prohibe diseñar para seccion llena "
            "(pag. impresa 79)"
            if lleno else
            "el barril va LLENO POR EL CAUDAL DE DISEÑO: la lamina toca la "
            "clave, y la fuente lo prohibe expresamente (pag. impresa 79)"
            if lleno_por_caudal else
            "el NIVEL DEL RECEPTOR deja al barril con menos borde libre del "
            "recomendado (TW por encima del llenado admisible)"
            if remansado_por_receptor else
            "el conducto trabaja con menos borde libre del recomendado")
    return Verificacion(
        cumple=cumple or aviso_por_tw,
        numeral=NUMERAL_V1,
        valor_obtenido=y_sobre_D,
        valor_admisible=y_sobre_D_max,
        criterio_aplicado=CRITERIO_BORDE_LIBRE,   # la adopcion, [A] (C05)
        codigo="V1",
        paso=paso(
            "F5.V1",
            codigo="V1",
            que="Borde libre: relacion de llenado del conducto",
            formula=f"y/{simbolo} <= {y_sobre_D_max:g}, el umbral adoptado en "
                    f"'{CRITERIO_BORDE_LIBRE}' (por defecto 0.75 = 1 - 0.25, "
                    f"el 25 % que el numeral escribe como borde libre minimo; "
                    f"solo se puede endurecer) y {simbolo} es {nombre}, una "
                    f"de las tres magnitudes que el numeral enumera",
            formula_cita_id="MC_HHD.4.1.1.3.7b",
            citas_textuales=citas_de_regimen,
            sustitucion=(
                Magnitud(simbolo_y, y, "m",
                         procedencia_y, cifras=CIFRAS_MAGNITUD),
                Magnitud(simbolo, D, "m", procedencia, cifras=CIFRAS_FACTOR))
            + sustitucion_extra,
            resultado=Magnitud(f"y/{simbolo}", y_sobre_D, "",
                               f"{simbolo_y} / {simbolo}, "
                               f"calculado en esta verificacion",
                               cifras=CIFRAS_MAGNITUD),
            umbral=umbral,
            veredicto=veredicto,
            elecciones=elecciones,
            nota_del_proyecto=f"{nota} {de_alcance}".strip(),
        ),
    )


# ---------------------------------------------------------------------------
# V2 - Velocidad minima (Sec. 4.1.1.3.6)
# ---------------------------------------------------------------------------

def v2_velocidad_minima(*, resultado: ResultadoHidraulico) -> Verificacion:
    """
    V >= 0.25 m/s. Sec. 5.2 de la hoja de ruta ya advierte que este piso casi
    nunca gobierna (se necesitaria una pendiente ~0.00006 para violarlo); la
    verificacion se calcula igual, sin dar por hecho el resultado.

    Texto que lo sustenta, literal (MC-HHD, RD 20-2011-MTC/14, num. 4.1.1.3.6,
    pag. 76, parrafo inmediatamente posterior a la Tabla Nº 10):

        "Se deberá verificar que la velocidad mínima del flujo dentro del
        conducto no produzca sedimentación que pueda incidir en una reducción
        de su capacidad hidráulica, recomendándose que la velocidad mínima sea
        igual a 0.25 m/s."

    DOS COSAS QUE ESE TEXTO FIJA Y QUE HAY QUE LEER JUNTAS:

    (1) El 0.25 es una RECOMENDACION, no una prohibicion -- el numeral dice
        "recomendandose". Esta funcion lo aplica igualmente como umbral duro
        (`V >= v_min` decide `cumple`, con los 0.25 m/s recomendados por
        defecto en 'velocidad_minima_autolimpieza_m_s'), que es la lectura
        conservadora y es la
        que el proyecto adopta. Pero el matiz no puede quedarse en el codigo:
        `NUMERAL_V2` lo lleva escrito, de modo que la memoria lo imprime junto
        al resultado y un revisor que vea un punto rechazado por V2 sepa que
        esta ante una recomendacion incumplida y no ante una infraccion. Y no
        viaja solo por ahi: `constantes_normativas.UMBRALES_DE_VERIFICACION`
        lo lleva al bloque que M11 imprime SIEMPRE, tambien cuando ningun
        punto llego a evaluarse (NOR-MEM-01).

    (2) La RAZON del minimo es la sedimentacion que reduce la capacidad
        hidraulica, no el desgaste. Es lo que separa a V2 de V3: el piso lo
        pone la sedimentacion y vale para todos los materiales por igual; el
        techo lo pone la abrasion del revestimiento y cambia con el material.
        Por eso los dos numeros de la Tabla Nº 10 son maximos y ninguno es
        este piso (ver `v3_velocidad_maxima`).

    QUE VELOCIDAD SE COMPARA, Y POR QUE NO ES LA MISMA QUE EN V3 (MAT-D1)
    ---------------------------------------------------------------------
    `resultado.V_sedimentacion`: la de la rama de n MAXIMO, que es la
    estimacion BAJA de velocidad. No `V_erosion`, que es la alta y la que
    consume V3.

    La regla de doble n (Sec. 4.1 de la hoja de ruta) asigna n minimo a
    "velocidad MAXIMA y socavacion". V2 no esta en esa lista, y no por olvido:
    un piso y un techo tienen extremos conservadores OPUESTOS. Contra un techo
    hay que suponer la velocidad mas alta que el rango de n admite; contra un
    piso, la mas baja. Verificar el piso con la estimacion alta es declarar
    "cumple" en el caso en que el conducto sedimenta.

    Hasta esta correccion V2 leia la rama n_min y el defecto era medible: con
    D = 0.90 m, y/D = 0.75 y S = 5e-5, la rama n_max da 0.228 m/s -- por
    debajo del piso -- y la n_min 0.297 m/s, de modo que el punto pasaba. La
    ventana permisiva completa es S entre 3.55e-5 y 6.01e-5, por debajo de
    cualquier pendiente constructiva, asi que ningun diseño real quedo
    afectado; lo que estaba invertido era el conservadurismo. El fixture CP-3
    ya modelaba el umbral de V2 con n = 0.013 (n_max): el repositorio se
    contradecia a si mismo.

    Y TODO LO ANTERIOR VALE PARA EL FLUJO UNIFORME (EXT-3; EXT-M-01, v8 §4.1
    enmendada en EXT-0). La velocidad que se compara es la de la SECCION
    EFECTIVA del regimen del barril:

      * barril LLENO (TW >= D): `ResultadoHidraulico.V_llena_m_s` =
        Q_celda / A_llena, que M4 calcula sin n --a seccion llena no hay
        tirante que resolver, y por eso no hay dos ramas entre las que
        elegir--. Es el caso (a) del dictamen: 0.05 m3/s en un tubo de 0.90 m
        ahogado da 0.0786 m/s < 0.25, y esta funcion decia [OK] con los 0.974
        m/s del flujo uniforme.
      * parcialmente lleno bajo control de ENTRADA: `V_sedimentacion`, como
        arriba.
      * parcialmente lleno bajo control de SALIDA: desde E-A la velocidad
        MINIMA del perfil de la lamina de agua, `perfil.V_min_m_s` =
        Q_celda / A(y_max) (M4, paso 4.3c/4.3d), con n_max, que es el lado
        conservador de un piso. Hasta E-A, `MetodoNoEvaluableError`, que
        queda como fallback de un resultado sin perfil (ver
        `_regimen_de_v1_v2`).
    """
    regimen = _regimen_de_v1_v2("V2", resultado, None)
    lleno = regimen == REGIMEN_LLENO
    if lleno:
        if resultado.V_llena_m_s is None:
            raise ValueError(
                "el ResultadoHidraulico dice regimen LLENO y no trae "
                "V_llena_m_s: M4.resolver_control la llena siempre, asi que "
                "esto es un fallo de programa, no del expediente")
        V = resultado.V_llena_m_s
        simbolo_V = "V_llena"
        procedencia_V = (
            "M4 (paso 4.3b): Q_celda / A_llena, la velocidad del regimen "
            "LLENO porque el TW alcanza la clave del barril (HDS-5 3.1.6, "
            "pag. impresa 3.18). No lleva n de Manning: a seccion llena no "
            "hay tirante que resolver ni dos ramas entre las que elegir, y "
            "la velocidad uniforme de M3 no describe este flujo")
    elif regimen == REGIMEN_PERFIL:
        V = resultado.perfil.V_min_m_s
        simbolo_V = "V_min"
        procedencia_V = (
            "M4 (paso 4.3c/4.3d): Q_celda / A(y_max), la velocidad MINIMA del "
            "perfil de la lamina de agua, con n_max. "
            + ("El barril es HORIZONTAL (S = 0): no hay velocidad uniforme, "
               "y el piso de autolimpieza se juzga donde la velocidad es "
               "menor" if resultado.sin_tirante_normal else
               "El barril va parcialmente "
               "lleno bajo control de SALIDA y el control esta aguas abajo: la "
               "velocidad uniforme de M3 no describe este flujo, y el piso de "
               "autolimpieza se juzga donde la velocidad es menor"))
    else:
        V = resultado.V_sedimentacion
        simbolo_V = "V_sedimentacion"
        procedencia_V = (
            "M3, velocidad de la rama de n MAXIMO -- la estimacion BAJA de "
            "velocidad, que es el extremo conservador contra un PISO. No es "
            "la de V3, que verifica un techo y usa la rama opuesta (MAT-D1). "
            "Vale porque el barril va parcialmente lleno bajo control de "
            "ENTRADA, en regimen uniforme (M4, paso 4.3b)")
    v_min = _umbral_adoptado_v2()
    cumple = V >= v_min - TOL_UMBRAL_NORMATIVO
    umbral = _umbral_de("V2", valor=v_min, unidad="m/s",
                        descripcion="velocidad minima de autolimpieza",
                        criterio=CRITERIO_V_MIN)
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V2,
        valor_obtenido=V,
        valor_admisible=v_min,
        criterio_aplicado=CRITERIO_V_MIN,        # la adopcion, [A] (C05)
        codigo="V2",
        paso=paso(
            "F5.V2",
            codigo="V2",
            que="Velocidad minima: comprobacion de autolimpieza",
            formula=f"V >= {v_min:g} m/s, el piso adoptado en "
                    f"'{CRITERIO_V_MIN}' (por defecto los 0.25 m/s que el "
                    "numeral recomienda; solo se puede endurecer)",
            formula_cita_id="MC_HHD.4.1.1.3.6#VMIN",
            # LAS DOS MITADES DEL PARRAFO, y en este orden: primero la que
            # obliga a verificar, despues la que recomienda el valor. Leida
            # sola, la segunda hace parecer opcional lo que el Manual manda.
            citas_textuales=("MC_HHD.4.1.1.3.6#VMIN_INICIO",),
            sustitucion=(
                Magnitud(simbolo_V, V, "m/s", procedencia_V,
                         cifras=CIFRAS_MAGNITUD),),
            resultado=Magnitud(simbolo_V, V,
                               "m/s", "la misma velocidad, contrastada contra "
                               "el piso", cifras=CIFRAS_MAGNITUD),
            umbral=umbral,
            veredicto=_veredicto(
                cumple, V - v_min, "m/s",
                "por encima del piso de autolimpieza" if cumple else
                "por debajo del piso: el conducto puede sedimentar y perder "
                "capacidad hidraulica"),
            nota_del_proyecto=(
                "La oracion del Manual dice dos cosas con fuerza distinta: "
                "«se debera verificar» (EXIGENCIA de comprobar) y "
                "«recomendandose que la velocidad minima sea igual a 0.25 "
                "m/s» (RECOMENDACION sobre el valor). El proyecto cumple la "
                "primera y aplica la segunda como umbral duro, por decision "
                "conservadora propia."),
        ),
    )


# ---------------------------------------------------------------------------
# V2b - Sedimentacion / colmatacion (HDS-5 3.a ed., num. 5.3.3)
# ---------------------------------------------------------------------------

def v2b_sedimentacion(*, punto: PuntoCritico,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    S_conducto >= S_cauce, el indicador de sedimentacion del HDS-5, aplicado
    con el regimen declarado en 'regimen_v2b', mas el acceso de
    mantenimiento declarado en 'acceso_mantenimiento_v2b'.

    POR QUE ESTA FILA EXISTE SI YA ESTA V2. Porque V2 pone un piso de
    VELOCIDAD en el caudal de DISEÑO, y la colmatacion de una alcantarilla en
    una llanura de riego no la produce la avenida: la producen los caudales
    bajos y frecuentes sobre un conducto tendido mas plano que el cauce que lo
    alimenta. Un punto puede cumplir V2 con holgura y colmatarse igual. El
    HDS-5 3.a ed. lo nombra con todas las letras (num. 5.3.3 «Sedimentation»,
    pag. impresa 5.11):

        "Therefore, barrel slope less than the natural channel and roughness
        greater than the channel are key indicators of potential problems at
        culvert sites."

    y da la contracara en la misma pagina:

        "Culverts which are located on and aligned with the natural channel
        generally do not have a sedimentation problem."

    DE LOS DOS INDICADORES SE EVALUA UNO, Y HAY QUE DECIR CUAL Y POR QUE. El
    primero -- pendiente del barril frente a la del cauce -- son dos numeros
    que este calculo ya tiene: `resultado.S` es la pendiente CON QUE CORRIO EL
    DISEÑO y `punto.S_cauce` la del cauce natural (Sec. 1.5). El segundo --
    rugosidad del barril frente a la del cauce -- exige el n de Manning del
    CAUCE NATURAL, que no es columna de Sec. 1.2 y que la hoja de ruta no
    fija: no se aproxima con el n del conducto ni con un valor de practica,
    se declara pendiente en `acceso_mantenimiento_v2b.verificacion_pendiente`
    y en `regimen_v2b.verificacion_pendiente`, y la memoria lo imprime en la
    propia fila. Media verificacion declarada es defendible; media
    verificacion callada no.

    ES UN INDICADOR, Y COMO SE APLICA LO DECLARA UN CRITERIO (PF-4). La
    fuente escribe «are key indicators of potential problems», no «shall»:
    ni umbral ni consecuencia. Hasta PF-4 este modulo lo aplicaba como umbral
    duro «por decision conservadora del proyecto», que es un [A] cableado y
    sin ficha; desde PF-4 el regimen sale de `ca.valor(CRITERIO_REGIMEN_V2B)`
    y se imprime como eleccion del paso, con su Fundamento
    (`F5.V2b.REGIMEN`, verbo DEFINE, el unico que el caracter DEFINICION de
    la cita sostiene):

        umbral_duro          el indicador disparado deja `cumple=False` y MD
                             descarta la seccion (conducta de S20; valor del
                             archivo entre PF-4 y T-2).
        indicador_con_aviso  la comparacion es LA MISMA (mismos numeros, el
                             mismo margen) y `cumple=True` siempre: el paso
                             lleva veredicto INDICADOR cuando se dispara,
                             CUMPLE cuando no, y el diametro no se descarta.
                             Valor del archivo desde T-2: es aplicar la
                             fuente como esta escrita, y lo unico coherente
                             con admitir el barril horizontal (INF-5.1.6).

    El matiz viaja ademas en `NUMERAL_V2B` y en `UMBRALES_DE_VERIFICACION`,
    que es lo que M11 imprime siempre.

    POR QUE CASI NUNCA GOBIERNA EN ESTE CORREDOR, y se dice para que nadie lo
    lea como una verificacion decorativa: Sec. 7.B fija que la alcantarilla
    sigue la pendiente del cauce, de modo que `S_conducto = S_cauce` salvo que
    el punto declare `S_conducto` aparte. La fila existe para el punto que SI
    lo declara -- una entrada deprimida, un conducto tendido mas plano para
    ganar recubrimiento, o un cruce de canal cuya pendiente la fija el canal
    -- que es exactamente el caso que el HDS-5 describe como «built with an
    upstream depression» y del que dice «Sedimentation is the likely result».

    LA MITAD [A] DEL ACCESO DETIENE, y esa es la diferencia con lo que habia
    antes. Hasta S20 la obligacion de prever el acceso de limpieza viajaba
    como un texto en `verificaciones_no_evaluadas()`: un parrafo que la
    memoria imprimia y que nadie tenia que responder. Ahora es un criterio
    sin valor, de modo que la corrida se detiene con `CriterioPendienteError`
    hasta que el proyectista declare como se limpia cada punto (SIS-A-13,
    MAT-O15).
    """
    # `exigir` y no `punto.S_cauce`: sin la pendiente del cauce el indicador
    # no tiene contra que comparar, y el revisor tiene que AÑADIR el dato
    # (DatoFaltanteError, no Invalido). MD descarta el material con la causa
    # citada entera, no mata el punto.
    S_cauce = punto.exigir("S_cauce")
    acceso = ca.valor(CRITERIO_ACCESO_MANTENIMIENTO)   # CriterioPendienteError
    regimen = _regimen_v2b()                           # CriterioPendienteError
    # LA COMPARACION NO CAMBIA CON EL REGIMEN, y la linea se conserva tal cual
    # porque el censo de mutacion (`tests/test_ext11_mutacion.py`) la nombra.
    cumple = resultado.S >= S_cauce - TOL_UMBRAL_NORMATIVO
    disparado = not cumple
    aviso = regimen == REGIMEN_V2B_INDICADOR_CON_AVISO
    umbral = _umbral_de(
        "V2b", valor=S_cauce, unidad="m/m",
        descripcion="pendiente del cauce natural: el conducto no se tiende "
                    "mas plano que ella",
        criterio=CRITERIO_ACCESO_MANTENIMIENTO)
    margen = resultado.S - S_cauce
    if not disparado:
        veredicto = _veredicto(
            True, margen, "m/m",
            "el conducto no queda mas plano que el cauce que lo alimenta: el "
            "indicador de sedimentacion del num. 5.3.3 no se dispara")
    elif aviso:
        veredicto = Veredicto(
            tipo=TipoDeVeredicto.INDICADOR, margen=margen, unidad="m/m",
            explicacion=(
                "el conducto queda MAS PLANO que el cauce natural, que es el "
                "indicador de colmatacion del num. 5.3.3; el HDS-5 lo llama "
                "«built with an upstream depression» y dice que la "
                "sedimentacion es el resultado probable. Bajo regimen_v2b = "
                "indicador_con_aviso el punto NO se detiene: el indicador "
                "queda como aviso de mantenimiento junto al acceso de "
                "limpieza declarado, y la seccion no se descarta por el"))
    else:
        veredicto = _veredicto(
            False, margen, "m/m",
            "el conducto queda MAS PLANO que el cauce natural, que es el "
            "indicador de colmatacion del num. 5.3.3; el HDS-5 lo llama "
            "«built with an upstream depression» y dice que la "
            "sedimentacion es el resultado probable. Bajo regimen_v2b = "
            "umbral_duro la seccion se descarta")
    return Verificacion(
        cumple=cumple or aviso,
        numeral=NUMERAL_V2B,
        valor_obtenido=resultado.S,
        valor_admisible=S_cauce,
        criterio_aplicado=CRITERIO_ACCESO_MANTENIMIENTO,
        codigo="V2b",
        paso=paso(
            "F5.V2b",
            codigo="V2b",
            que="Sedimentacion / colmatacion: indicador de pendiente y "
                "acceso de mantenimiento",
            formula="S_conducto >= S_cauce",
            formula_cita_id="HDS5_3ED.5.3.3#INDICADORES",
            # --- T-2 --- La tercera es la EXIGENCIA [N] de la otra mitad de
            # la fila: el num. 4.1.1.3.7 d) «Mantenimiento y limpieza». El
            # dispositivo de acceso sigue siendo el [A] de abajo.
            citas_textuales=("HDS5_3ED.5.3.3#INDICADORES",
                             "HDS5_3ED.5.3.3#ALINEADO",
                             "MC_HHD.4.1.1.3.7d"),
            sustitucion=(
                Magnitud("S_conducto", resultado.S, "m/m",
                         "pendiente CON QUE CORRIO EL DISEÑO (paso 7.B.1: "
                         "cauce, extremo de la banda o `S_conducto` "
                         "declarada)",
                         cifras=CIFRAS_FINA),
                Magnitud("S_cauce", S_cauce, "m/m",
                         "pendiente del CAUCE NATURAL, columna del CSV "
                         "(Sec. 1.5: no es la de la alcantarilla)",
                         cifras=CIFRAS_FINA)),
            resultado=Magnitud("S_conducto - S_cauce", margen,
                               "m/m",
                               "diferencia de pendientes: negativa es el "
                               "indicador que el HDS-5 nombra",
                               cifras=CIFRAS_FINA),
            umbral=umbral,
            veredicto=veredicto,
            elecciones=(
                EleccionDeProyecto(
                    que_se_adopto="regimen con que se aplica el indicador "
                                  "de pendiente del num. 5.3.3",
                    valor=str(regimen),
                    entre=tuple(str(v) for v in
                                ca.criterio(CRITERIO_REGIMEN_V2B).sensibilidad),
                    de_donde="el criterio 'regimen_v2b' [A]: la fuente "
                             "define el indicador y no dice que hacer "
                             "cuando se dispara",
                    por_que="la fuente escribe «are key indicators of "
                            "potential problems», sin umbral ni «shall»: "
                            "convertir el indicador en condicion de "
                            "aceptacion (umbral_duro) o dejarlo como aviso "
                            "que no descarta el diametro "
                            "(indicador_con_aviso) es una eleccion del "
                            "proyectista, y hasta PF-4 vivia cableada aqui "
                            "como «decision conservadora del proyecto»",
                    clave_criterio=CRITERIO_REGIMEN_V2B,
                    fundamento_id="F5.V2b.REGIMEN"),
                EleccionDeProyecto(
                    que_se_adopto="dispositivo de acceso de mantenimiento para "
                                  "limpieza del conducto",
                    valor=str(acceso),
                    entre=tuple(str(v) for v in
                                ca.criterio(CRITERIO_ACCESO_MANTENIMIENTO)
                                  .sensibilidad),
                    de_donde="el criterio 'acceso_mantenimiento_v2b' [A]: "
                             "ninguna norma de normas/ prescribe el dispositivo",
                    por_que="la fila V2b de la hoja de ruta es [N] + [A], y esta "
                            "es la mitad [A]. La mitad [N] es la exigencia del "
                            "num. 4.1.1.3.7 d) del Manual -- las dimensiones "
                            "deben permitir el mantenimiento y la limpieza --, "
                            "que no dice CON QUE se entra. El indicador de "
                            "pendiente dice si "
                            "el punto TIENDE a colmatarse; el acceso dice si se "
                            "va a poder limpiar cuando lo haga. El diametro "
                            "minimo de 0.90 m garantiza que una persona quepa, "
                            "no que pueda entrar",
                    clave_criterio=CRITERIO_ACCESO_MANTENIMIENTO),),
            nota_del_proyecto=(
                "SE EVALUA UNO DE LOS DOS INDICADORES DEL NUMERAL. El "
                "segundo -- «roughness greater than the channel» -- exige el "
                "n de Manning del cauce natural, que no es columna de "
                "Sec. 1.2 ni lo fija la hoja de ruta. No se aproxima: queda "
                "declarado como pendiente. Y el caracter de la fuente es "
                "INDICADOR («are key indicators of potential problems»), no "
                "exigencia: como se aplica lo declara el criterio "
                "'regimen_v2b' [A] -- en esta corrida, "
                + ("como INDICADOR CON AVISO, que se evalua igual y no "
                   "descarta el diametro; es el valor del archivo desde T-2."
                   if aviso else
                   "como UMBRAL DURO, que detiene el punto cuando se "
                   "dispara; es la lectura mas conservadora, declarada para "
                   "esta corrida.")),
        ),
    )


def _regimen_v2b() -> str:
    """
    El regimen declarado en 'regimen_v2b', validado como segunda linea.

    La puerta (`_verificar_criterio`, forma `categoria`) ya rechaza lo que no
    esta en el conjunto cerrado; esta guardia existe para el valor que la
    burle (`con_valor` en tests, o una edicion del archivo), en forma MAT-D13:
    condicion en positivo y negada, mensaje que nombra el dato.
    """
    regimen = ca.valor(CRITERIO_REGIMEN_V2B)          # CriterioPendienteError
    if not (isinstance(regimen, str) and regimen in REGIMENES_V2B):
        raise DatoInvalidoError(
            campo=CRITERIO_REGIMEN_V2B,
            valor=regimen,
            motivo=(f"'{CRITERIO_REGIMEN_V2B}' vale {regimen!r} y las unicas "
                    f"opciones son {', '.join(map(repr, REGIMENES_V2B))}: el "
                    "regimen de V2b es un conjunto cerrado"))
    return regimen


# ---------------------------------------------------------------------------
# V3 - Velocidad maxima (Tabla N 10 / vacios PPI-FHWA)
# ---------------------------------------------------------------------------

def _velocidad_de_v3(resultado: ResultadoHidraulico) -> Magnitud:
    """
    La velocidad que V3 compara contra el techo, con su procedencia.

    En flujo uniforme es `V_erosion`, la rama de n MINIMO (la estimacion
    ALTA: el extremo conservador contra un techo). --- T-2 --- EN UN BARRIL
    HORIZONTAL (S = 0, INF-5.1.6) no hay velocidad uniforme: la mayor del
    barril es la de la seccion de SALIDA, porque sobre un fondo horizontal
    la lamina es subcritica y baja hacia la salida (perfil H2), donde pasa
    por min(D, max(TW, y_c)). Es `ResultadoHidraulico.V_salida` (HDS-5 num.
    3.1.6, pag. impresa 3.18), que no lleva n. No se le busca un sustituto
    con Manning, que ahi no tiene solucion.
    """
    if not resultado.sin_tirante_normal:
        return Magnitud(
            "V_erosion", resultado.V_erosion, "m/s",
            "M3, velocidad de la rama de n MINIMO -- la estimacion "
            "ALTA de velocidad, que es el extremo conservador contra "
            "un TECHO. No es la de V2, que verifica un piso y usa la "
            "rama opuesta", cifras=CIFRAS_MAGNITUD)
    if resultado.V_salida is None:
        raise MetodoNoEvaluableError(
            que="V3",
            procedimiento="la velocidad a la salida de HDS-5 3.1.6, que "
                          "`M4.resolver_control` emite en "
                          "`ResultadoHidraulico.V_salida`: este resultado no "
                          "la trae",
            motivo="el barril es horizontal (S = 0), no hay velocidad "
                   "uniforme de Manning, y la maxima del conducto es la de "
                   "la seccion de salida")
    return Magnitud(
        "V_salida", resultado.V_salida.valor, "m/s",
        "M4 (paso 4.3b): Q_celda / A(min(D, max(TW, y_c))), la velocidad de "
        "la seccion de SALIDA (HDS-5 num. 3.1.6). El barril es HORIZONTAL "
        "(S = 0): no hay velocidad uniforme, la lamina baja hacia la salida "
        "y esa es la velocidad MAXIMA del conducto. No lleva n de Manning",
        cifras=CIFRAS_MAGNITUD)


def _paso_v3(*, resultado: ResultadoHidraulico, v_max: float,
             clave, cumple: bool, material: Material, de_tabla: bool):
    """
    El paso de memoria de V3, comun a sus dos ramas.

    LA ELECCION SE IMPRIME, que es la regla R1: el techo de un material de la
    Tabla Nº 10 sale de una FILA, y la fila tiene alternativas -- las otras
    filas de la tabla, y en el concreto ademas el segundo numero de la propia
    fila. Sin decir entre que se eligio, «6.0 m/s» y «6.0 m/s porque es el
    mayor de la fila Concreto, descartando 3.0» son la misma linea en la
    pagina y no son la misma decision.
    """
    elecciones = []
    if de_tabla:
        fila = ", ".join(f"{v}" for v in material.v_max_tabla10)
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="techo de velocidad del revestimiento",
            valor=f"{v_max} m/s",
            entre=tuple(f"{v} m/s" for v in material.v_max_tabla10),
            de_donde=f"la fila «{material.nombre}» de la Tabla Nº 10 "
                     f"({fila} m/s)",
            por_que="los DOS numeros de la fila son MAXIMOS -- lo dice el "
                    "titulo de la tabla --, de modo que se verifica contra el "
                    "mayor y el menor NO es un piso. El piso de velocidad es "
                    "V2 y sale de otro parrafo",
            cita_id="MC_HHD.4.1.1.3.6#T10"))
        if clave is not None:
            elecciones.append(EleccionDeProyecto(
                que_se_adopto="techo mas conservador dentro de la fila",
                valor=f"{v_max} m/s",
                entre=tuple(f"{v} m/s" for v in material.v_max_tabla10),
                de_donde="el criterio adoptado 'v_max_concreto_eleccion'",
                por_que="el proyectista bajo el techo dentro de la fila del "
                        "concreto. Esa posibilidad se apoya en una "
                        "INTERPRETACION del proyectista -- que el par recorra "
                        "la calidad del acabado --, no en el Manual: se "
                        "declara aparte, en el bloque de umbrales",
                clave_criterio=clave))
    elif clave is not None:
        # LA ETIQUETA SE LEE DE LA FICHA, no se escribe aqui (T-4, INF-3.2.4).
        # Este texto decia «[C], con fuente WSDOT» para los dos materiales, y
        # desde T-4 es cierto solo para el HDPE: la fuente PROHIBE el
        # termoplastico en abrasion severa (§8-3.3), y para el metal no fija
        # limite --pide mas calibre o solera de concreto--, de modo que el
        # techo del TMC es una adopcion [A] con ventana. Imprimir la misma
        # frase para los dos volveria a presentar como limite de la fuente lo
        # que el proyecto eligio.
        ficha = ca.criterio(clave)
        if ficha.etiqueta == "C":
            de_donde = (f"el criterio adoptado '{clave}' [C], con fuente "
                        "WSDOT Hydraulics Manual, §8-3.3 y Table 8-4")
            por_que = ("la Tabla Nº 10 NO lista este material: no tiene fila. "
                       "El vacio esta verificado (afirmacion negativa del "
                       "registro) y se cubre con fuente tecnica reconocida, "
                       "que es lo que la etiqueta [C] declara: la fuente no "
                       "admite tuberia termoplastica en abrasion severa, y "
                       "el umbral de velocidad de ese nivel es el que se "
                       "adopta como techo")
            entre = ()
        else:
            de_donde = (f"el criterio adoptado '{clave}' [{ficha.etiqueta}], "
                        "una adopcion del proyecto con ventana de "
                        "sensibilidad: ninguna fuente fija este valor como "
                        "limite del material")
            por_que = ("la Tabla Nº 10 NO lista este material: no tiene fila. "
                       "Para la tuberia metalica la fuente tecnica consultada "
                       "no prohibe ninguna velocidad --pide aumentar el "
                       "espesor o revestir la solera segun el nivel de "
                       "abrasion--, de modo que el techo es una eleccion del "
                       "proyecto y se defiende con su ventana. Lo que V3 "
                       "admite por debajo del techo no sustituye la "
                       "proteccion contra la abrasion que el sitio exija")
            entre = (tuple(f"{v} m/s" for v in ficha.sensibilidad)
                     if isinstance(ficha.sensibilidad, tuple) else ())
        elecciones.append(EleccionDeProyecto(
            que_se_adopto="techo de velocidad",
            valor=f"{v_max} m/s",
            entre=entre,
            de_donde=de_donde,
            por_que=por_que,
            clave_criterio=clave))
    return paso(
        "F5.V3",
        codigo="V3",
        que="Velocidad maxima: comprobacion contra el techo del revestimiento",
        formula="V <= v_max del revestimiento",
        formula_cita_id="MC_HHD.4.1.1.3.6#T10",
        sustitucion=(_velocidad_de_v3(resultado),),
        resultado=Magnitud(_velocidad_de_v3(resultado).simbolo,
                           _velocidad_de_v3(resultado).valor, "m/s",
                           "la misma velocidad, contrastada contra el techo",
                           cifras=CIFRAS_MAGNITUD),
        umbral=_umbral_de("V3", valor=v_max, unidad="m/s",
                          descripcion=f"velocidad maxima admisible de "
                                      f"«{material.nombre}»",
                          criterio=clave),
        veredicto=_veredicto(
            cumple, v_max - _velocidad_de_v3(resultado).valor, "m/s",
            "por debajo del maximo admisible del revestimiento" if cumple else
            "por encima del maximo: el flujo abrasiona el revestimiento"),
        elecciones=tuple(elecciones),
    )


def v3_velocidad_maxima(*, material: Material,
                        resultado: ResultadoHidraulico) -> Verificacion:
    """
    V3 verifica UN SOLO extremo: el techo. V <= v_max.

    Materiales de la Tabla N 10 (concreto, ladrillo con concreto, mamposteria
    de piedra y concreto): M2 trae la fila literal en
    `material.v_max_tabla10`, y TODOS sus valores son velocidades MAXIMAS --
    la tabla se titula "Velocidades maximas admisibles (m/s) en conductos
    revestidos" (num. 4.1.1.3.6, pag. impresa 76), su unica columna de valores
    se rotula "VELOCIDAD (M/S)", y el piso esta aparte en el parrafo
    siguiente. El extremo inferior no es un minimo; exigirlo como tal era leer
    la tabla al reves.

    QUE DICE LA FUENTE Y QUE PONE EL PROYECTO (NOR-HID-04). Que los dos
    numeros sean maximos lo dice el titulo. Que el rango "recorra la calidad
    del revestimiento" -- el superior para el mejor acabado, el inferior para
    el mas pobre -- NO lo dice el Manual en ninguna parte: es interpretacion
    del proyectista, esta declarada como tal en
    `constantes_normativas.TABLA_10_INTERPRETACION_PROYECTO`, y es la que
    sostiene que 'v_max_concreto_eleccion' pueda bajar el techo dentro de la
    fila. Se dice aparte y no pegado a la cita porque en contra de esa lectura
    juegan dos hechos de la propia fuente: la frase que introduce la tabla
    habla de "un rango, cuyos limites se describen a continuacion", y la fila
    de mamposteria trae un solo valor.

    Ese error tenia consecuencia real: rechazaba por V3 un conducto de
    concreto a 1.5 m/s, que es una velocidad perfectamente admisible y que
    cumple de sobra el unico piso que la norma fija. Porque el piso existe y
    es otro: **V2**, autolimpieza, V >= 0.25 m/s, declarado aparte en la misma
    pagina y aplicable a todos los materiales por igual. Un segundo piso, mas
    alto y por material, no lo respalda ningun numeral.

    Se toma el valor MAYOR de la fila como admisible. Bajo la interpretacion
    del proyecto es el techo del revestimiento de mejor calidad; bajo lo que
    la fuente sostiene sin mas, es simplemente la mayor de las velocidades que
    la tabla admite para ese revestimiento, y verificar contra ella es la
    lectura minima que no inventa un piso.

    Techo mas conservador, OPCIONAL. Para el concreto, el proyectista puede
    declarar 'v_max_concreto_eleccion' y bajar ese techo -- hasta 3.0 m/s, el
    maximo del acabado mas pobre -- si las condiciones del acabado de ESTA
    obra lo ameritan. Se lee con `ca.valor_si_declarado`, NO con `ca.valor`:
    es un criterio opcional que refina un valor que la norma ya fija, no un
    vacio que la norma deje abierto. Sin declarar devuelve None, V3 aplica el
    6.0 de la tabla y el criterio no entra en la memoria. Leerlo con
    `ca.valor` bloquearia el concreto por un criterio que nadie tiene
    obligacion de declarar.

    `criterio_aplicado` distingue las dos procedencias, que es lo que un
    revisor necesita: None cuando el umbral es el [N] de la tabla, y la clave
    del criterio cuando el proyectista lo bajo.

    TMC y HDPE: la Tabla N 10 no los cubre (Tablero 1.3). El valor sale de
    `criterios_adoptados.valor('v_max_tmc' | 'v_max_hdpe')`, hoy 4.572 m/s los
    dos -- la conversion exacta de 15 ft/s, que antes se escribia redondeada
    a 4.6 y quedaba 0.6 % POR ENCIMA del techo declarado duro (MAT-O14) --.

    LOS DOS NUMEROS COINCIDEN Y NO SON LA MISMA COSA (T-4, INF-3.2.4), y la
    asimetria es deliberada:

      * 'v_max_hdpe' es [C]. WSDOT Hydraulics Manual M 23-03.12, §8-3.3, no
        admite tuberia termoplastica en condiciones severamente abrasivas, y
        su Table 8-4 pone el nivel severo por encima de 15 ft/s. La
        prohibicion sale del §8-3.3; de la tabla sale solo el umbral.
      * 'v_max_tmc' es [A], con ventana (3.048, 4.572) m/s. Para el metal la
        misma tabla NO prohibe: pide mas calibre o solera de concreto. El
        techo del TMC es una adopcion del proyecto.

    Y LO QUE V3 NO HACE: no CLASIFICA el sitio. Al HDPE le aplica como techo
    el umbral de velocidad del nivel severo --tomar la velocidad sola como
    suficiente es una lectura del proyecto, declarada como `Interpretacion`
    de la tabla: la Table 8-4 define cada nivel tambien por la carga de fondo
    y su nota dice que no hace falta que concurran todas las condiciones--.
    El NIVEL de abrasion del sitio es otro dato, de campo y opcional, y quien
    lo aplica es la matriz de durabilidad de M2 (`M2.matriz_durabilidad`),
    que excluye el HDPE en el nivel severo aunque la velocidad sea menor.

    Se leen con `ca.valor`, no con `ca.valor_si_declarado`: no son
    opcionales -- si alguien los vaciara, V3 debe detenerse y no caer a un
    techo inventado, porque para estos materiales no hay ningun valor
    normativo de respaldo al que volver. Son un techo escalar, de modo que
    esta rama no cambia.
    """
    if material.tipo in CRITERIO_V_MAX:
        clave = CRITERIO_V_MAX[material.tipo]
        v_max = ca.valor(clave)     # CriterioPendienteError mientras falte
        V = _velocidad_de_v3(resultado).valor   # V_erosion; V_salida si S = 0
        cumple = V <= v_max + TOL_UMBRAL_NORMATIVO
        return Verificacion(
            cumple=cumple,
            numeral=NUMERAL_V3,
            valor_obtenido=V,
            valor_admisible=v_max,
            criterio_aplicado=clave,
            codigo="V3",
            paso=_paso_v3(resultado=resultado, v_max=v_max, clave=clave,
                          cumple=cumple, material=material, de_tabla=False),
        )

    # Solo el techo: los valores de la fila de la Tabla N 10 son todos
    # MAXIMOS, no un piso y un techo (ver el docstring). Se toma el mayor; los
    # demas no se verifican. `max()` y no un desempaquetado de dos: la fila de
    # la mamposteria trae UN solo valor y escribirla como (2.0, 2.0) inventaba
    # un par que la fuente no imprime (NOR-HID-07).
    v_max = max(material.v_max_tabla10)
    clave = None

    if material.tipo is TipoMaterial.CONCRETO_REFORZADO:
        adoptado = ca.valor_si_declarado(CRITERIO_V_MAX_CONCRETO)
        if adoptado is not None:
            v_max = adoptado
            clave = CRITERIO_V_MAX_CONCRETO

    V = _velocidad_de_v3(resultado).valor       # V_erosion; V_salida si S = 0
    cumple = V <= v_max + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V3,
        valor_obtenido=V,
        valor_admisible=v_max,
        criterio_aplicado=clave,   # None = [N] puro de la Tabla N 10
        codigo="V3",
        paso=_paso_v3(resultado=resultado, v_max=v_max, clave=clave,
                      cumple=cumple, material=material, de_tabla=True),
    )


# ---------------------------------------------------------------------------
# V4 - Carga a la entrada HW (Sec. 5.1, resguardo por analogia [N->])
# ---------------------------------------------------------------------------

def cota_de_entrada(punto: PuntoCritico) -> CotaDeEntrada:
    """
    Cota del fondo de la entrada, msnm, CON SU PROCEDENCIA (Sec. 7.B).

    EL DATO MEDIDO MANDA SOBRE LA REGLA, y ese es todo el orden de esta
    funcion. Si la fila trae `cota_fondo_entrada`, se devuelve esa y el
    criterio 'origen_cota_fondo_entrada' NI SIQUIERA SE INVOCA --- no aparece
    en `criterios_usados()`, porque esta corrida no lo uso ---. Solo cuando la
    columna va vacia se aplica la regla que el proyectista declaro, y si no
    declaro ninguna, la etapa se detiene con `CriterioPendienteError` como se
    detenia antes. NO hay valor por defecto en ninguno de los dos escalones.

    La precedencia no es una comodidad: la escribe el `reemplazado_por` del
    propio criterio --- «un dato medido no se sustituye por una regla
    adoptada» ---, y antes de que la columna existiera ya estaba anunciada en
    el mensaje de error de esta misma funcion.

    LA EXCEPCION AL ORDEN, y es deliberada: si el proyectista declara
    EXPRESAMENTE la regla `'cota_fondo_entrada'`, esta pidiendo el dato medido
    a proposito, y entonces una columna vacia es un `DatoFaltanteError` en vez
    de una caida silenciosa a la regla del terreno. Pedir el dato y recibir
    otra cosa sin enterarse es justo lo que este proyecto persigue.

    POR QUE SE LLAMA ASI Y NO `cota_entrada_supuesta`, que es como se llamaba.
    Porque desde que la columna existe el nombre MIENTE la mitad de las veces:
    una cota medida no es una cota supuesta, y la diferencia es exactamente la
    que el revisor pregunta. Es la leccion de `ResultadoPunto.D` aplicada a un
    nombre en vez de a un campo.

    Es publica y con nombre propio porque V4 no es su unico consumidor: el
    tamizado de 7.A (M7) convierte el mismo HW a cota para fijar la rasante
    minima. Si cada modulo eligiera su propia cota de entrada, V4 y 7.A
    quedarian evaluando dos condiciones distintas y el acoplamiento circular
    que 7.A dice cortar seguiria abierto: la rasante se fijaria contra una
    referencia y se verificaria contra otra.
    """
    medida = punto.cota_fondo_entrada
    if medida is not None:
        return CotaDeEntrada(
            valor=medida, medida=True,
            procedencia="columna cota_fondo_entrada del CSV (Sec. 1.2): "
                        "nivelacion del fondo del cauce en el cruce. Es un "
                        "dato MEDIDO y no una regla, de modo que el criterio "
                        f"'{CRITERIO_ORIGEN_COTA_ENTRADA}' no se aplica en "
                        "este punto")

    origen = ca.valor(CRITERIO_ORIGEN_COTA_ENTRADA)
    if origen not in ORIGENES_COTA_ENTRADA:
        raise DatoInvalidoError(
            CRITERIO_ORIGEN_COTA_ENTRADA, valor=origen,
            motivo="la regla declarada tiene que ser una de las "
                   f"implementadas: {sorted(ORIGENES_COTA_ENTRADA)}",
        )
    campo = ORIGENES_COTA_ENTRADA[origen]
    valor = getattr(punto, campo)
    if valor is None:
        # Solo puede pasar con `origen == 'cota_fondo_entrada'`: el
        # proyectista pidio el dato medido y la fila no lo trae. Es
        # `DatoFaltanteError` --- el revisor tiene que AÑADIR algo --- y no
        # una caida a la regla del terreno.
        raise DatoFaltanteError(
            campo, id_punto=punto.id,
            detalle=f"el criterio '{CRITERIO_ORIGEN_COTA_ENTRADA}' declara "
                    f"'{origen}', o sea que pide la cota de fondo de entrada "
                    "MEDIDA, y esta fila la deja vacia. O se mide y se llena "
                    "la columna, o se declara otra regla: el programa no "
                    "elige por el proyectista",
        )
    return CotaDeEntrada(
        valor=valor, medida=False,
        procedencia=f"regla '{origen}' declarada en el criterio "
                    f"'{CRITERIO_ORIGEN_COTA_ENTRADA}' [A]; el codigo NO la "
                    "elige. La fila no trae cota de fondo de entrada medida",
        # La regla viaja con la cota (PC-07): el JSON la publicaba leyendo el
        # registro global al exportar, y una declaracion posterior cambiaba
        # la regla impresa al lado de una cota que no cambio.
        regla=origen)


def cota_clave(*, punto: PuntoCritico, material: Material,
               seccion: Seccion) -> float:
    """
    Cota de la clave FISICA del conducto, msnm (Sec. 7.A):

        cota clave = cota de fondo de la entrada
                     + altura interior + espesor de pared

    RECIBE LA SECCION Y NO UN ESCALAR DESDE C8. La altura interior de un tubo
    es su diametro y la de un marco es la H de su celda, y con un `D: float`
    la funcion tenia que confiar en que el llamador hubiera puesto la altura
    correcta -- que es la suposicion de forma que la Familia C persigue.

    El espesor de pared entra UNA vez y no dos: la cota de entrada es el
    invert INTERIOR -- la superficie por donde corre el agua -- de modo que la
    superficie exterior superior queda a D_int + t sobre ella, no a D_ext.

    POR QUE NO ES cota_entrada + D, que es lo que este proyecto calculaba
    (MAT-D4): EG-2013 Subseccion 508.07 (pag. impresa 984) mide el relleno
    minimo "desde la clave de la tuberia hasta el nivel de la subrasante", y
    la clave de la tuberia es su superficie EXTERIOR. Con la clave calculada
    sobre el diametro interior, la rasante minima de 7.A sale corta justo en
    t: una rasante fijada en ese minimo deja ~0.20 m reales de recubrimiento
    donde EG-2013 exige 0.30 (deficit del 33 % para D = 0.90 m de concreto).

    Es publica y vive AQUI, junto a `cota_de_entrada`, por la misma
    razon que ella: la usan V7 (para pesar el relleno real sobre la clave) y
    el tamizado de 7.A (para fijar la rasante), y si cada modulo la
    recalculase por su cuenta las dos condiciones se separarian. Estaba
    duplicada -- M7.cota_clave y una linea suelta dentro de `v7_flotacion` --
    y las dos copias tenian el mismo error.

    Se detiene con `CriterioPendienteError` en 'origen_cota_fondo_entrada'
    (la cota de entrada) o en 'espesor_pared_conducto' (el espesor).
    """
    altura = seccion.altura
    return cota_de_entrada(punto).valor + altura + espesor_pared(material,
                                                                 altura)


def altura_relleno_sobre_clave(*, punto: PuntoCritico, material: Material,
                               seccion: Seccion) -> float:
    """
    Altura REAL de relleno sobre la clave fisica del conducto, m:

        altura = cota de subrasante - cota de clave

    Es el relleno que de verdad hay encima -- no el minimo de Sec. 7.A, que es
    un piso admisible y otra cosa --, y lo consumen dos etapas distintas: V7,
    que lo pesa como EV para la flotacion, y la Fase 8, que con el entra a la
    tabla de clases o calibres de la norma de producto (items 1-2).

    LA GUARDA ES PARTE DE LA MAGNITUD, y por eso vive aqui y no en cada
    consumidor. Una altura nula o negativa significa que la clave queda a
    nivel de la subrasante o por encima: no es un relleno pequeño sino un
    punto cuyas cotas no se sostienen, y el numero que saldria de restarlas no
    tiene sentido fisico en ninguna de las dos etapas. Sale como
    `DatoInvalidoError` sobre 'cota_subrasante' -- el revisor tiene que
    CORREGIR una cota, no añadir un dato (CLAUDE.md) --, que es la excepcion
    que la Fase 5 ya lanzaba.

    POR QUE SE EXTRAJO (SIS-A-21). La resta estaba escrita dos veces: dentro
    de `v7_flotacion`, con la guarda, y en `servicio._fase_8`, sin ella. La segunda
    copia no hacia daño HOY -- la Fase 8 se detiene antes, en el tope de
    'clases_producto_por_relleno' -- y esa es exactamente la forma en que una
    guarda desaparece sin que nadie lo note: el dia en que ese criterio se
    declare y la tabla se transcriba, la Fase 8 entraria a la norma de
    producto con una altura negativa y elegiria una clase contra un numero sin
    sentido. Escrita una vez, la guarda no se puede olvidar en una de las dos.

    Se detiene con `CriterioPendienteError` en lo mismo que `cota_clave`:
    'origen_cota_fondo_entrada' y 'espesor_pared_conducto'.
    """
    clave = cota_clave(punto=punto, material=material, seccion=seccion)
    altura = punto.cota_subrasante - clave
    if altura <= TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "cota_subrasante", valor=punto.cota_subrasante, id_punto=punto.id,
            # El motivo NO cita numeral de fase: la misma magnitud la
            # consumen V7 (Fase 5) y la norma de producto (Fase 8), y una
            # excepcion que nombrase una sola mandaria al revisor a la etapa
            # equivocada la mitad de las veces. Quien la atrapa ya sabe en que
            # etapa esta -- `servicio._etapa` la anota con su fase.
            motivo="la clave del conducto queda a nivel de la subrasante o "
                   f"por encima ({altura:+.3f} m de relleno): no hay relleno "
                   "sobre la clave que pesar ni con que entrar a la tabla de "
                   "la norma de producto",
        )
    return altura


def resguardo_por_cbr(cbr: float) -> float:
    """
    Resguardo de Sec. 5.1 segun el CBR de subrasante (Manual de Suelos, num.
    4.5.4): busca en `RESGUARDO_NAPA_SUBRASANTE` [N] la fila cuyo rango
    [CBR_min, CBR_max) contiene el dato, con los extremos None como
    ilimitados. Recorre las cuatro filas de la tabla, exhaustivas por
    construccion (cubren todo el dominio fisico del CBR).

    Publica por el mismo motivo que `cota_de_entrada`: la segunda
    condicion del tamizado de 7.A (M7) es la misma tabla aplicada al mismo
    CBR, y duplicarla alli seria abrir la puerta a que las dos se separen.
    """
    for cbr_min, cbr_max, resguardo in RESGUARDO_NAPA_SUBRASANTE:
        piso = cbr_min is None or cbr >= cbr_min
        techo = cbr_max is None or cbr < cbr_max
        if piso and techo:
            return resguardo
    raise ValueError(
        f"CBR = {cbr} no cae en ninguna fila de RESGUARDO_NAPA_SUBRASANTE: "
        "la tabla deberia ser exhaustiva sobre el dominio fisico del dato"
    )


def _banda(inf, sup) -> str:
    """La fila de la tabla de resguardo, escrita como la lee un revisor."""
    if inf is None:
        return f"< {sup} %"
    if sup is None:
        return f">= {inf} %"
    return f"{inf}-{sup} %"


def v4_carga_entrada(*, punto: PuntoCritico,
                     resultado: ResultadoHidraulico) -> Verificacion:
    """
    cota de entrada + HW <= cota de subrasante - resguardo(CBR), Sec. 5.1.

    LOS DOS TERMINOS SON NIVELES, y por eso la desigualdad lleva el sumando
    `cota de entrada` que la hoja de ruta v8 omitia (MAT-O5): HW es una carga
    en metros sobre el fondo de la entrada, no una cota, y compararla con una
    cota msnm sin ese sumando se cumple siempre. El codigo nunca lo omitio
    -- ver `HW_cota` mas abajo --; era la hoja la que estaba mal, y se
    corrigio alli. El numeral tambien compara niveles: "El nivel superior de
    la sub rasante debe quedar encima del nivel de la napa freatica como
    minimo a 0.60 m ..." (Manual de Suelos, num. 4.5.4, pag. impresa 42).

    El resguardo sale
    del criterio 'resguardo_HW_subrasante' [N->] (analogia declarada al nivel
    freatico, no un valor puntual: la tabla de CBR vive en
    `constantes_normativas.RESGUARDO_NAPA_SUBRASANTE`, [N] por numeral, y es
    la aplicacion de ESA tabla al HW lo que Sec. 5.1 etiqueta [N->]).

    `HW` es una carga en metros sobre el fondo de la entrada (Sec. 4.2/4.3);
    convertirla a cota exige la cota de esa entrada. Este modulo NO la elige:
    la pide a `cota_de_entrada`, que devuelve el fondo MEDIDO cuando la fila
    lo trae y, si no, aplica la regla que el proyectista declaro en
    'origen_cota_fondo_entrada' [A] -- ver "V4 -- la cota de entrada es un
    DATO MEDIDO O UN CRITERIO DECLARADO" en el docstring del modulo. La
    `Magnitud` de la sustitucion dice cual de las dos fue, que es lo primero
    que el revisor pregunta. Este parrafo decia "este modulo adopta
    `punto.cota_terreno`", que es lo que hacia ANTES de SIS-A-01/SIS-A-04 y
    dejo de ser cierto entonces: 'cota_terreno' es hoy una de las reglas
    admisibles del criterio, no una eleccion del codigo.
    """
    ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico
    resguardo_m = resguardo_por_cbr(punto.cbr_subrasante)

    entrada = cota_de_entrada(punto)   # MEDIDA o regla; ver su docstring
    HW_cota = entrada.valor + resultado.HW
    admisible = punto.cota_subrasante - resguardo_m

    cumple = HW_cota <= admisible + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V4,
        valor_obtenido=HW_cota,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_RESGUARDO,   # su etiqueta en ca.criterio() es "N->"
        codigo="V4",
        paso=paso(
            "F5.V4",
            codigo="V4",
            que="Carga a la entrada: el agua embalsada frente a la subrasante",
            formula="cota_entrada + HW <= cota_subrasante - resguardo(CBR)",
            formula_cita_id="MS.4.5.4",
            sustitucion=(
                # LA PROCEDENCIA LA TRAE EL PROPIO VALOR, y por eso ya no
                # esta escrita a mano aqui: dice MEDIDA o dice que regla se
                # aplico. Es la diferencia entre un dato y una eleccion, y es
                # lo primero que el revisor pregunta de esta cota.
                Magnitud("cota_entrada", entrada.valor, "msnm",
                         entrada.procedencia, cifras=CIFRAS_MAGNITUD),
                Magnitud("HW", resultado.HW, "m",
                         "M4, carga a la entrada del control que GOBIERNA "
                         "(entrada o salida, el mayor de los dos)", cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_subrasante", punto.cota_subrasante, "msnm",
                         "columna cota_subrasante del CSV (Sec. 1.2)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("CBR", punto.cbr_subrasante, "%",
                         "columna cbr_subrasante del CSV (Sec. 1.2)",
                         cifras=CIFRAS_PORCENTAJE),
                Magnitud("resguardo", resguardo_m, "m",
                         "tabla del num. 4.5.4 del Manual de Suelos, entrando "
                         "con el CBR de la fila", cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("cota alcanzada por el agua", HW_cota, "msnm",
                               "cota_entrada + HW", cifras=CIFRAS_MAGNITUD),
            umbral=_umbral_de(
                "V4", valor=admisible, unidad="msnm",
                descripcion="cota maxima que el agua puede alcanzar "
                            "(subrasante menos resguardo)",
                criterio=CRITERIO_RESGUARDO),
            veredicto=_veredicto(
                cumple, admisible - HW_cota, "m",
                "el agua queda por debajo de la subrasante con su resguardo"
                if cumple else
                "el agua embalsada invade el resguardo bajo la subrasante"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="resguardo bajo la subrasante",
                valor=f"{resguardo_m} m",
                entre=tuple(f"{resguardo} m (CBR {_banda(inf, sup)})"
                            for inf, sup, resguardo in
                            RESGUARDO_NAPA_SUBRASANTE),
                de_donde="la tabla de resguardo por CBR del num. 4.5.4 del "
                         "Manual de Suelos",
                por_que=f"es la fila que corresponde al CBR "
                        f"{punto.cbr_subrasante} % de ESTE punto. La tabla es "
                        "normativa; extenderla del nivel freatico a la carga "
                        "de una avenida es la ANALOGIA que el criterio "
                        "'resguardo_HW_subrasante' declara como [N->]",
                cita_id="MS.4.5.4",
                clave_criterio=CRITERIO_RESGUARDO),),
            # V4 es la SEGUNDA de las dos verificaciones que pueden llevar la
            # advertencia de §15.6.3, y no la que aquel apartado nombra. La
            # que nombra -- V4b -- no emite `PasoDeMemoria`: su `Fundamento`
            # esta censado en `normativa.fundamentos.SIN_FUNDAMENTO` porque el
            # rango HW/D 1.0-1.5 lo DESCRIBE el HDS-5 y no lo prescribe, y
            # darle una cita para poder colgarle la nota seria convertir en
            # exigencia una adopcion del proyectista. V4 sirve mejor al
            # argumento: es LA verificacion que mide contra la subrasante de
            # la VIA, que es justamente la cota que §15.6.2 contrapone a la
            # del canal.
            nota_del_proyecto=_nota_de_alcance(
                punto, "la subrasante de la VIA, con su resguardo por CBR"),
        ),
    )


# ---------------------------------------------------------------------------
# V4b - Relacion HW/D (adopcion del proyectista sobre la banda del HDS-5)
# ---------------------------------------------------------------------------

def v4b_relacion_hw_d(*, D: float,
                      resultado: ResultadoHidraulico) -> Verificacion:
    """
    HW/D <= 'HW_D_max', Fase 5 fila V4b.

    CUAL HW SE DIVIDE ENTRE D, que es la unica decision de esta funcion y la
    que decide si el chequeo sirve. Se usa `resultado.HW` -- la carga del
    control que GOBIERNA --, no el HWi/D del control de entrada. Lo que la
    fuente acota es "the headwater produced by a culvert": el embalse real
    aguas arriba, que es el mayor de los dos controles. Tomar el de entrada
    cuando gobierna el de salida daria un numero menor que el embalse que la
    obra produce, y un umbral que se relaja solo cuando el agua sube mas es
    la direccion insegura exacta que este proyecto persigue.

    Es una consecuencia que hay que dejar escrita porque contradice una
    prediccion del propio repositorio: el docstring de
    `modelos.ControlEntrada.HW_sobre_D` decia que ese campo "sera el
    argumento del chequeo el dia que se cablee" (SIS-B-02). No lo es, por lo
    anterior, y ese docstring se corrigio en la misma pasada.

    DE DONDE SALE EL UMBRAL, y por que es [A] y no [N] ni [C]. El HDS-5 no
    prescribe HW/D alguno: su num. 2.2.5 d) "Agency Constraints" (pag.
    impresa 2.10) DESCRIBE lo que imponen las agencias viales
    estadounidenses -- "The allowable HW/D ratio varies throughout the
    country, but commonly ranges from 1.0 to 1.5" -- y en el Peru la agencia
    es el MTC, que no fija ninguno (NOR-HDS-02). Elegir un numero dentro de
    esa banda ajena es adopcion del proyectista, y por eso el criterio lleva
    su rango de sensibilidad y esta funcion lo declara en
    `criterio_aplicado`.

    POR QUE SE CABLEA AHORA Y NO ANTES. El conflicto #1 de la matriz de
    auditorias lo prohibia expresamente mientras la ETIQUETA del criterio
    estuviese abierta: implementar el chequeo antes de saber de donde sale el
    1.5 habria convertido una cita mal leida en un umbral que rechaza
    diametros. Cerrada la procedencia (C06), el cableado es lo que quedaba
    (MAT-D2, SIS-A-02, SIS-B-02).

    NO SUSTITUYE A V5. El control real del embalse aguas arriba es V5
    -- remanso dentro del derecho de via --, que es la que protege a
    terceros y que sigue deteniendose por falta de dato. V4b es un tope de
    practica, mas laxo, y cumplirlo no dice nada sobre V5.
    """
    HW_sobre_D = resultado.HW / D
    admisible = ca.valor(CLAVE_HW_D_MAX)
    return Verificacion(
        cumple=HW_sobre_D <= admisible + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V4B,
        valor_obtenido=HW_sobre_D,
        valor_admisible=admisible,
        criterio_aplicado=CLAVE_HW_D_MAX,
        codigo="V4b",
    )


# ---------------------------------------------------------------------------
# V5 - Remanso aguas arriba (DG-2018 + Ley 29338)
# ---------------------------------------------------------------------------

def v5_remanso(*, punto: PuntoCritico,
               resultado: ResultadoHidraulico,
               derecho_de_via: Optional[DerechoDeViaDelPunto] = None
               ) -> Verificacion:
    """
    V5: el embalse que la obra forma aguas arriba queda dentro del derecho de
    via, sin afectar a terceros ni a la faja marginal (Fase 5, fila V5).

    --- T-7b --- (PUNTO 0, decision del dueño del 2026-11-13). TIENE METODO,
    y es DECLARABLE: el criterio 'remanso_derecho_via' [A] elige como se mide
    la extension del embalse, y no tiene valor de archivo. Se detiene, por
    separado y nunca con un fallo de programa:

      * criterio SIN valor      -> `CriterioPendienteError` (como siempre: sin
                                   declarar nada, ningun resultado cambia);
      * sin `ancho_derecho_via_m` -> `DatoFaltanteError`: el ancho de la faja
                                   de ESTE cruce es un dato externo por punto
                                   (lo fija la resolucion que aprueba el
                                   derecho de via del tramo) y no tiene valor
                                   por defecto;
      * metodo «perfil de remanso paso a paso» -> `MetodoNoEvaluableError`:
                                   esta nombrado y no implementado.

    DOS METODOS IMPLEMENTADOS (correcciones de T-7b, H2):

      * «cota_de_afectacion» (`_v5_cota_de_afectacion`), el que la FUENTE
        sostiene: la cota del embalse de diseño (solera de entrada + HW de
        M4) no supera la cota de afectacion aguas arriba, dato externo por
        punto (`cota_afectacion_aguas_arriba_msnm`). HDS-5 num. 2.2.5: «The
        design headwater should not exceed the allowable headwater», y la
        cota admisible puede ser «the flood damage elevation of an upstream
        building or another upstream road crossing». Sin el dato,
        `DatoFaltanteError`. Puede fallar de verdad.
      * «embalse_a_nivel», el de abajo, con un defecto que se DICE: el plano
        horizontal corta el FONDO, de modo que la distancia incluye el tramo
        natural del cauce y, como medida de lo que la obra añade, es una
        cota superior; con los anchos normativos solo cumple en cauces de
        pendiente fuerte.

    EL METODO «embalse_a_nivel», con todos sus supuestos, que viajan en el
    paso de la memoria:

        x_embalse = HW / S_cauce
        d         = (semilongitud de entrada + x_embalse) · cos(esviaje)
        cumple    si  d <= ancho_derecho_via / 2

      1. El embalse es un PLANO HORIZONTAL a la cota de la carga de diseño
         de M4 (la del control que gobierna). El HDS-5 identifica esa carga
         con la profundidad del embalse aguas arriba (num. 2.2.5); no da el
         metodo de su extension, que es del proyecto.
      2. El fondo del cauce sube aguas arriba de la boca con la pendiente
         `S_cauce` del CSV, en la direccion del eje del conducto: el plano lo
         corta a HW / S_cauce de la boca. No hay topografia del cauce ni
         lateral: NO se mide si el agua se extiende a lo ancho.
      3. La boca queda a la semilongitud de entrada de 7.B del eje de la
         via, medida sobre el eje del conducto; el esviaje proyecta la suma
         sobre la normal a la via.
      4. El dato es el ancho TOTAL de la faja, y se toma SIMETRICA respecto
         del eje de la via: la mitad queda del lado de aguas arriba.
      5. NO ES LA CURVA DE REMANSO. En un cauce de pendiente suave el perfil
         real (M1) se prolonga mas alla de ese punto, con tirantes mayores
         que el normal: la distancia es una cota INFERIOR de la extension
         del remanso. En uno de pendiente fuerte el embalse termina en un
         resalto y el plano es su cota superior. El programa no conoce la
         seccion del cauce de aproximacion y NO clasifica su regimen: el
         paso lo dice en vez de presumir el lado.

    Con `S_cauce` nula el plano horizontal no corta el fondo y no hay
    extension finita: `MetodoNoEvaluableError`, nunca una cifra.

    LO QUE EL DG-2018 SI DA Y LO QUE NO: el requisito juridico --el derecho
    de via es bien de dominio publico (304.07.01) y su ancho minimo es el de
    la Tabla 304.09 por clase de carretera, incrementado en 5.00 m en el
    caso del borde mas alejado de las obras de drenaje (304.07.02)--. NO da
    condicion hidraulica alguna. El piso de la tabla es un CONTRASTE del
    dato declarado, que el servicio imprime como aviso; no lo sustituye.

    NO SE INVOCA EN LA FAMILIA C, y no por falta de datos: por no aplicar
    (ver `_remanso_o_cruce_de_canal`); la sustituye VC1.
    """
    metodo = ca.valor(CRITERIO_REMANSO)     # CriterioPendienteError: sin metodo
    if metodo not in METODOS_DE_REMANSO:
        raise DatoInvalidoError(
            CRITERIO_REMANSO, valor=metodo, id_punto=punto.id,
            motivo="el criterio elige el METODO de V5; se espera uno de: "
                   + ", ".join(METODOS_DE_REMANSO))
    if metodo == METODO_REMANSO_PERFIL_PASO_A_PASO:
        raise MetodoNoEvaluableError(
            "V5", "perfil de remanso paso a paso aguas arriba del embalse",
            "el metodo declarado en 'remanso_derecho_via' no esta "
            "implementado: exige la seccion y la topografia del cauce de "
            "aproximacion. Los metodos implementados son "
            f"'{METODO_REMANSO_EMBALSE_A_NIVEL}' y "
            f"'{METODO_REMANSO_COTA_AFECTACION}'",
            id_punto=punto.id, rotulo=MOTIVO_METODO_NO_EVALUABLE_REMANSO)
    if metodo == METODO_REMANSO_COTA_AFECTACION:
        return _v5_cota_de_afectacion(punto=punto, resultado=resultado,
                                      derecho_de_via=derecho_de_via)
    if derecho_de_via is None or derecho_de_via.ancho_m is None:
        raise DatoFaltanteError(
            "ancho_derecho_via_m",
            id_punto=punto.id,
            detalle=(
                f"el criterio '{CRITERIO_REMANSO}' esta declarado "
                f"('{metodo}'), pero V5 no puede resolverse sin el ancho del "
                "derecho de via de este cruce: no es columna de Sec. 1.2 y "
                "no tiene valor por defecto. Declarar `ancho_derecho_via_m` "
                "(m, ancho total de la faja) por --datos-externos, con la "
                "resolucion que aprueba el derecho de via del tramo"
            ),
        )

    ancho = derecho_de_via.ancho_m
    semilongitud = derecho_de_via.semilongitud_entrada_m
    S = punto.exigir("S_cauce")
    HW = resultado.HW
    for nombre, x in (("ancho_derecho_via_m", ancho), ("S_cauce", S),
                      ("HW", HW), ("semilongitud de entrada", semilongitud)):
        if isinstance(x, bool) or not isinstance(x, (int, float)) \
                or not math.isfinite(x):
            raise DatoInvalidoError(
                nombre, valor=x, id_punto=punto.id,
                motivo="V5 (embalse a nivel) necesita un numero finito")
    if not ancho > 0:
        raise DatoInvalidoError(
            "ancho_derecho_via_m", valor=ancho, id_punto=punto.id,
            motivo="el ancho del derecho de via tiene que ser positivo")
    if not (HW >= 0 and semilongitud >= 0):
        raise DatoInvalidoError(
            "HW", valor=(HW, semilongitud), id_punto=punto.id,
            motivo="la carga de diseño y la semilongitud de entrada no "
                   "pueden ser negativas")
    # Forma MAT-D13: la condicion en positivo y negada (un NaN es falso
    # frente a `>` igual que frente a `<=`), y el mensaje nombra al par.
    if not S > 0:
        raise MetodoNoEvaluableError(
            "V5", "perfil de remanso paso a paso",
            f"con pendiente de cauce S_cauce = {S!r} el plano horizontal a "
            f"la cota de la carga (HW = {HW:.3f} m) no corta el fondo del "
            "cauce aguas arriba: el embalse a nivel no tiene extension "
            "finita y el metodo no da cifra",
            id_punto=punto.id, rotulo=MOTIVO_METODO_NO_EVALUABLE_REMANSO)
    x_embalse = HW / S
    coseno = math.cos(math.radians(punto.esviaje_grados))
    d = (semilongitud + x_embalse) * coseno
    if not math.isfinite(d):
        raise LimiteNumericoError(
            "extension del embalse", valor=d, id_punto=punto.id,
            motivo=f"HW = {HW!r} m entre S_cauce = {S!r} no cabe en un "
                   "numero finito")
    medio = ancho / 2
    cumple = d <= medio + TOL_UMBRAL_NORMATIVO
    piso = derecho_de_via.piso_dg2018_m
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V5,
        valor_obtenido=d,
        valor_admisible=medio,
        criterio_aplicado=CRITERIO_REMANSO,
        codigo="V5",
        paso=paso(
            "F5.V5", codigo="V5",
            que="V5: extension del embalse aguas arriba frente al derecho "
                "de via (metodo del embalse a nivel)",
            formula=("x_embalse = HW / S_cauce;  d = (L_boca + x_embalse) · "
                     "cos(esviaje)  <=  ancho_derecho_via / 2"),
            sustitucion=(
                Magnitud("HW", HW, "m",
                         "carga de diseño de M4, la del control que "
                         f"gobierna ({resultado.control_gobernante.value}): "
                         "cota del embalse sobre la solera de entrada",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("S_cauce", S, "m/m",
                         "pendiente del cauce (columna S_cauce o el dato "
                         "que la completa): se supone la del fondo aguas "
                         "arriba de la boca, en la direccion del eje",
                         cifras=CIFRAS_FINA),
                Magnitud("x_embalse", x_embalse, "m",
                         "distancia, sobre el eje, de la boca al punto en "
                         "que el plano horizontal corta el fondo",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("L_boca", semilongitud, "m",
                         derecho_de_via.origen_semilongitud,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("esviaje", punto.esviaje_grados, "grados",
                         "columna esviaje_grados: proyecta la distancia "
                         "sobre la normal a la via",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("ancho_derecho_via", ancho, "m",
                         derecho_de_via.origen_ancho,
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "d", d, "m",
                "distancia del extremo aguas arriba del embalse al eje de "
                "la via, medida normal a ella", cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="mitad del ancho declarado del derecho de via "
                            "(faja simetrica respecto del eje)",
                valor=medio, unidad="m", cita_id="DG2018.304.07.01",
                caracter="DEFINICION",
                aplicacion="umbral del proyecto: la fuente define la faja "
                           "y no enuncia condicion hidraulica; el metodo es "
                           f"'{CRITERIO_REMANSO}' [A]",
                criterio_aplicado=CRITERIO_REMANSO),
            veredicto=_veredicto(
                cumple, medio - d, "m",
                ("el embalse a nivel queda dentro de la faja" if cumple else
                 "el embalse a nivel sale de la faja del derecho de via: "
                 "hace falta una seccion mayor (menos carga), o el perfil "
                 "de remanso sobre la topografia del cauce")),
            citas_textuales=("HDS5_3ED.2.2.5#EMBALSE", "DG2018.304.07.02"),
            nota_del_proyecto=(
                "SUPUESTOS DEL METODO (criterio 'remanso_derecho_via' = "
                f"'{metodo}', [A]): (1) el embalse es un plano horizontal a "
                "la cota de la carga de diseño; (2) el fondo del cauce sube "
                "aguas arriba con la pendiente del CSV, en la direccion del "
                "eje del conducto, sin topografia del cauce ni lateral: no "
                "se mide si el agua se extiende a lo ancho; (3) el dato es "
                "el ancho total de la faja y se toma simetrica respecto del "
                "eje de la via; (4) NO es la curva de remanso: en un cauce "
                "de pendiente suave el perfil real se prolonga mas alla, "
                "con tirantes mayores que el normal, y esta distancia es "
                "una cota INFERIOR de la extension del remanso; en uno de "
                "pendiente fuerte el embalse termina en un resalto y el "
                "plano es su cota superior. El programa no conoce la "
                "seccion del cauce de aproximacion y no clasifica su "
                "regimen. (5) EL PLANO CORTA EL FONDO, y por eso d INCLUYE "
                "el tramo en que el cauce ya llevaria agua sin la obra (su "
                "tirante natural): como medida de lo que la OBRA añade al "
                "embalse es una cota SUPERIOR -- una obra que no eleva el "
                "nivel tambien da d > 0 --, y con los anchos de la Tabla "
                "304.09 del DG-2018 (16 a 40 m) solo cumple en cauces de "
                "pendiente fuerte. Restar el tirante natural, (HW - y_n) / "
                "S_cauce, exige la seccion del cauce de aproximacion, que no "
                "es dato de entrada (diferido, ficha T7B-01). El metodo que "
                "la fuente sostiene es el de COTA ('cota_de_afectacion'). "
                + ("Piso del DG-2018 para el ancho: "
                   f"{piso:.2f} m ({derecho_de_via.origen_piso})."
                   if piso is not None else
                   "Piso del DG-2018 para el ancho: no contrastado ("
                   f"{derecho_de_via.origen_piso}).")
                + " La faja marginal (Ley 29338) no se evalua: la ley no "
                "esta en normas/.")),
    )


def _v5_cota_de_afectacion(*, punto: PuntoCritico,
                           resultado: ResultadoHidraulico,
                           derecho_de_via: Optional[DerechoDeViaDelPunto]
                           ) -> Verificacion:
    """
    V5 con el metodo «cota_de_afectacion» (correcciones de T-7b, H2):

        cota_embalse = cota de entrada + HW  <=  cota de afectacion aguas arriba

    La fuente (HDS-5 num. 2.2.5, pags. impresas 2.9 y 2.10) plantea la
    carga admisible como un NIVEL: «The design headwater should not exceed
    the allowable headwater» (cita HDS5_3ED.2.2.5#NO_EXCEDER, RECOMENDACION)
    y la cota admisible puede ser «the flood damage elevation of an upstream
    building or another upstream road crossing» (cita
    HDS5_3ED.2.2.5a#COTA_DE_DANO, PERMISO). Que ESA cota sea la del terreno
    o del bien a proteger en el limite del derecho de via aguas arriba es
    eleccion del proyecto ('remanso_derecho_via' [A]); el dato es de la
    topografia del cruce (`cota_afectacion_aguas_arriba_msnm`, por punto,
    sin valor por defecto: sin el, `DatoFaltanteError`).

    LO QUE NO MIDE: si el embalse rebasa esa cota en otro punto del limite
    (la topografia lateral) ni la curva de remanso; compara la carga de
    diseño de M4 en la boca, que es el nivel MAS ALTO del embalse a nivel.
    """
    if derecho_de_via is None or derecho_de_via.cota_afectacion_msnm is None:
        raise DatoFaltanteError(
            "cota_afectacion_aguas_arriba_msnm",
            id_punto=punto.id,
            detalle=(
                f"el criterio '{CRITERIO_REMANSO}' declara el metodo "
                f"'{METODO_REMANSO_COTA_AFECTACION}', y V5 compara la cota "
                "del embalse de diseño con la cota de afectacion aguas "
                "arriba de este cruce: la del terreno o del bien a proteger "
                "en el limite del derecho de via, de la topografia. No es "
                "columna de Sec. 1.2 y no tiene valor por defecto: declarar "
                "`cota_afectacion_aguas_arriba_msnm` (msnm) por "
                "--datos-externos"),
        )
    cota_af = derecho_de_via.cota_afectacion_msnm
    entrada = cota_de_entrada(punto)
    HW = resultado.HW
    for nombre, x in (("cota_afectacion_aguas_arriba_msnm", cota_af),
                      ("HW", HW), ("cota de entrada", entrada.valor)):
        if isinstance(x, bool) or not isinstance(x, (int, float)) \
                or not math.isfinite(x):
            raise DatoInvalidoError(
                nombre, valor=x, id_punto=punto.id,
                motivo="V5 (cota de afectacion) necesita un numero finito")
    if not HW >= 0:
        raise DatoInvalidoError("HW", valor=HW, id_punto=punto.id,
                                motivo="la carga de diseño no puede ser "
                                       "negativa")
    cota_embalse = entrada.valor + HW
    cumple = cota_embalse <= cota_af + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V5,
        valor_obtenido=cota_embalse,
        valor_admisible=cota_af,
        criterio_aplicado=CRITERIO_REMANSO,
        codigo="V5",
        paso=paso(
            "F5.V5", codigo="V5",
            que="V5: cota del embalse de diseño frente a la cota de "
                "afectacion aguas arriba (metodo de cota)",
            formula="cota de entrada + HW  <=  cota de afectacion aguas arriba",
            sustitucion=(
                Magnitud("cota_entrada", entrada.valor, "msnm",
                         entrada.procedencia, cifras=CIFRAS_MAGNITUD),
                Magnitud("HW", HW, "m",
                         "carga de diseño de M4, la del control que "
                         f"gobierna ({resultado.control_gobernante.value})",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_afectacion", cota_af, "msnm",
                         derecho_de_via.origen_cota_afectacion,
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "cota_embalse", cota_embalse, "msnm",
                "cota de entrada + HW: nivel del embalse de diseño en la "
                "boca", cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="cota del terreno o del bien a proteger en el "
                            "limite del derecho de via aguas arriba",
                valor=cota_af, unidad="msnm",
                cita_id="HDS5_3ED.2.2.5a#COTA_DE_DANO",
                caracter="PERMISO",
                aplicacion="umbral del proyecto: la fuente admite una cota "
                           "de daño aguas arriba como cota admisible; que "
                           "sea la del limite del derecho de via lo elige "
                           f"'{CRITERIO_REMANSO}' [A]",
                criterio_aplicado=CRITERIO_REMANSO),
            veredicto=_veredicto(
                cumple, cota_af - cota_embalse, "m",
                ("el embalse de diseño no alcanza la cota de afectacion "
                 "aguas arriba" if cumple else
                 "el embalse de diseño supera la cota de afectacion aguas "
                 "arriba: hace falta una seccion mayor (menos carga) o "
                 "proteger lo que se afecta")),
            citas_textuales=("HDS5_3ED.2.2.5#NO_EXCEDER",
                             "HDS5_3ED.2.2.5#EMBALSE"),
            nota_del_proyecto=(
                f"Metodo '{METODO_REMANSO_COTA_AFECTACION}' "
                f"('{CRITERIO_REMANSO}', [A]): es el criterio de NIVEL que "
                "el HDS-5 num. 2.2.5 sostiene, sin ninguna longitud. Compara "
                "el nivel mas alto del embalse (en la boca) con la cota del "
                "dato; no mide la topografia lateral ni la curva de "
                "remanso. El inciso b. del mismo numeral trae otro criterio "
                "de nivel -- el AUMENTO admisible sobre el nivel sin la "
                "obra -- que exige el perfil del cauce y no esta "
                "implementado.")),
    )


# ---------------------------------------------------------------------------
# VC1 - Cruce de canal: borde libre del canal (Sec. 2.3)
# ---------------------------------------------------------------------------

def vc1_borde_libre_canal(*, punto: PuntoCritico,
                          resultado: ResultadoHidraulico) -> Verificacion:
    """
    cota de entrada + HW <= cota de coronacion del canal - borde libre, Sec. 2.3.

    LA VERIFICACION QUE DE VERDAD GOBIERNA A LA FAMILIA C, y hasta esta sesion
    no existia. La Sec. 2.3 le da a esta familia un solo requisito --- «No
    puede alterar la rasante hidraulica ni el borde libre del canal» --- y
    ninguna verificacion lo evaluaba: §13 de `docs/ruta_familia_c.md` lo
    llevaba declarado como deuda porque faltaba el dato. El dato llego
    (levantamiento propio de los seis cruces) y con el la columna
    `cota_coronacion_canal`.

    POR QUE NO LA SUSTITUYE NINGUNA DE LAS QUE YA HABIA. Las tres que miden
    algo parecido miden contra OTRA cota:

        V1   el llenado DENTRO del barril      (y <= 0.75 H)
        V4   la subrasante de la VIA           (con su resguardo por CBR)
        V4b  la carga relativa a la seccion    (HW/D)

    Las tres pueden cumplirse con el canal desbordado, porque ninguna mira el
    canal. En un paso de canal el agua que la alcantarilla embalsa no se
    extiende sobre el terreno: sube dentro de un cauce confinado, y si llega a
    la coronacion desborda sobre parcela de tercero ANTES de entrar al
    conducto. VC1 es mas exigente que V1 y no la sustituye: son dos umbrales
    sobre magnitudes distintas.

    QUE MITAD DE LA SEC. 2.3 CIERRA, Y QUE MITAD NO. Cierra la del BORDE
    LIBRE: el agua no invade el resguardo bajo la coronacion. NO cierra la de
    la RASANTE HIDRAULICA: acota el nivel que el agua alcanza, no mide en
    cuanto la obra LEVANTA el pelo de agua del canal respecto del que tendria
    sin ella. Un HW justo bajo el umbral puede ser una alteracion grande de la
    rasante hidraulica y VC1 lo da por bueno. Medir la otra mitad exige el
    tirante normal del canal en la seccion del cruce --- o sea su geometria
    trapecial (b, z) y su n de Manning, que no son columna de Sec. 1.2 --- y
    ademas la extension aguas arriba del remanso. Queda declarado, no cerrado
    en silencio: es lo que imprime la nota de alcance de esta familia.

    LOS DOS TERMINOS SON NIVELES, igual que en V4 y por la misma razon: HW es
    una carga en metros sobre el fondo de la entrada, no una cota. La cota de
    entrada la resuelve `cota_de_entrada`, que en un paso de canal es la
    nivelacion del fondo DEL CANAL en el cruce.

    EL BORDE LIBRE NO ES [N]. Sale del criterio 'borde_libre_canal_m' [A]: el
    Manual no fija borde libre para un canal --- verificado por ausencia sobre
    sus 225 paginas, `citas.SIN_BORDE_LIBRE_DE_CANAL` --- y el par 0.30-0.50 m
    que el proyecto adopta es el del num. 4.1.1.4.1 e), cuyo objeto es un
    BADEN y cuyo datum superior es la superficie de rodadura. La analogia y la
    eleccion dentro de la banda son del proyectista y viajan en el criterio.

    Se detiene sin veredicto en dos sitios, y ninguno es un fallo de programa:

    - Criterio SIN declarar -> `CriterioPendienteError` (la lanza `ca.valor`).
    - Columna vacia         -> `DatoFaltanteError`. El revisor tiene que
      CONSEGUIR la cota, no decidirla: no hay regla que la sustituya.
    """
    borde_libre = ca.valor(CRITERIO_BORDE_LIBRE_CANAL)
    coronacion = punto.cota_coronacion_canal
    if coronacion is None:
        raise DatoFaltanteError(
            "cota_coronacion_canal", id_punto=punto.id,
            detalle=(
                "VC1 mide contra la coronacion del canal y esta fila la deja "
                "vacia. Sale del levantamiento topografico del cruce --- "
                "seccion transversal del canal con su fondo y sus dos "
                "coronaciones --- y NO hay regla declarada que la sustituya: "
                "ni el terreno natural ni la rasante son el labio del canal. "
                "Sin ella el requisito de la Sec. 2.3 no se puede evaluar, y "
                "el programa no lo da por cumplido"
            ),
        )

    entrada = cota_de_entrada(punto)
    HW_cota = entrada.valor + resultado.HW
    admisible = coronacion - borde_libre

    cumple = HW_cota <= admisible + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_VC1,
        valor_obtenido=HW_cota,
        valor_admisible=admisible,
        criterio_aplicado=CRITERIO_BORDE_LIBRE_CANAL,
        codigo="VC1",
        paso=paso(
            "F5.VC1",
            codigo="VC1",
            que="Cruce de canal: el agua embalsada frente a la coronacion "
                "del canal",
            formula="cota_entrada + HW <= cota_coronacion_canal - "
                    "borde_libre_canal",
            # LA CITA DE LA FORMULA ES LA DEL BORDE LIBRE, que es lo unico de
            # la desigualdad que sale de una fuente. La desigualdad entera no
            # la escribe ningun numeral: la escribe la Sec. 2.3 de la hoja de
            # ruta como REQUISITO, en prosa y sin formula. Es el mismo reparto
            # que V7 --- fuente para las partes, proyecto para el ensamblaje
            # --- y por eso la separacion va tambien en la nota.
            formula_cita_id="MC_HHD.4.1.1.4.1e",
            sustitucion=(
                Magnitud("cota_entrada", entrada.valor, "msnm",
                         entrada.procedencia, cifras=CIFRAS_MAGNITUD),
                Magnitud("HW", resultado.HW, "m",
                         "M4, carga a la entrada del control que GOBIERNA "
                         "(entrada o salida, el mayor de los dos)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_coronacion_canal", coronacion, "msnm",
                         "columna cota_coronacion_canal del CSV: "
                         "levantamiento topografico del cruce. Dato de sitio "
                         "[S], medido punto a punto",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("borde_libre_canal", borde_libre, "m",
                         f"criterio '{CRITERIO_BORDE_LIBRE_CANAL}' [A]: "
                         "adopcion del proyectista dentro de la banda "
                         "0.30-0.50 m que el num. 4.1.1.4.1 e) recomienda "
                         "PARA UN BADEN. No es un valor normativo del canal",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("cota alcanzada por el agua", HW_cota, "msnm",
                               "cota_entrada + HW", cifras=CIFRAS_MAGNITUD),
            umbral=_umbral_de(
                "VC1", valor=admisible, unidad="msnm",
                descripcion="cota maxima que el agua puede alcanzar en el "
                            "canal (coronacion menos borde libre)",
                criterio=CRITERIO_BORDE_LIBRE_CANAL),
            veredicto=_veredicto(
                cumple, admisible - HW_cota, "m",
                "el agua queda bajo la coronacion del canal con su borde "
                "libre"
                if cumple else
                "el agua embalsada invade el borde libre del canal: desborda "
                "sobre las parcelas colindantes antes de entrar al conducto"),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="borde libre del canal",
                valor=f"{borde_libre} m",
                entre=tuple(f"{v} m" for v in BORDE_LIBRE_BADEN_RANGO_M),
                de_donde="la banda que el num. 4.1.1.4.1 e) del Manual "
                         "recomienda, en texto corrido y sin tabla, PARA UN "
                         "BADEN",
                por_que="es el extremo SUPERIOR de la banda, y aqui el "
                        "extremo superior es el conservador: el borde libre "
                        "se resta de la coronacion, de modo que subirlo baja "
                        "la cota admisible y endurece la verificacion. El "
                        "Manual no da regla para elegir dentro de la banda ni "
                        "fija borde libre alguno para un canal, y por eso "
                        "esto es una eleccion del proyectista y no una "
                        "lectura de la fuente",
                cita_id="MC_HHD.4.1.1.4.1e#RANGO",
                clave_criterio=CRITERIO_BORDE_LIBRE_CANAL),),
            nota_del_proyecto=NOTA_VC1_LO_QUE_NO_MIDE,
        ),
    )


# ---------------------------------------------------------------------------
# V6 - Material solido de arrastre (Sec. 3.1)
# ---------------------------------------------------------------------------

def v6_material_solido_arrastre(*, material: Material,
                                seccion: Optional[Seccion] = None,
                                Q: Optional[float] = None) -> Verificacion:
    """
    Con palizada: seccion unica mayor, nunca multiple (Sec. 3.1).

    --- T-3 --- (cadena T, INF-0.4) CON N > 1 LA FILA DICE QUE SE RECHAZA, y
    no solo cuantas celdas: el reparto Q/N que MD ya hace (EXT-2), el tabique
    entre celdas y el ancho exterior total del marco multicelda. El veredicto
    NO cambia -- la multicelda sigue sin aceptarse mientras no haya un dato
    de sitio sobre la capacidad de arrastre del cauce (ficha EXT-2-01) --:
    lo que cambia es que el revisor ve que obra se rechazo. La SEPARACION
    entre celdas de un marco VACIADO IN SITU (§14.1 de la ruta de la Familia
    C) es el tabique, del espesor 'espesor_pared_cajon': el marco es
    monolitico. La regla de separacion del num. 4.1.1.3.4 a) -- la mitad del
    diametro, entre 0.40 y 1.00 m, medida entre superficies externas -- es
    de TUBERIAS y su razon es compactar el relleno entre ellas, que en un
    marco monolitico no existe; la fila la nombra para decir por que no la
    aplica (cita `MC_HHD.4.1.1.3.4a#SEPARACION`). `seccion` y `Q` son
    opcionales: sin ellos la fila es la de antes.

    LO QUE C5 CAMBIO, Y NO ES EL VEREDICTO SINO DE QUE DEPENDE. Este
    docstring decia que "el catalogo de M2 y el bucle de MD solo ofrecen
    conductos circulares de UNA seccion" y que "el diseño multiceldular es
    Familia C ... y queda fuera del alcance de M2/MD". Las dos frases dejaron
    de ser ciertas en esta misma sesion: M2 devuelve candidato de marco y MD
    reparte el caudal entre celdas. La verificacion sigue valiendo
    trivialmente, pero ya NO por una incapacidad del programa: vale porque el
    expediente declara UNA celda en el criterio 'n_celdas_cajon', y el dia que
    declare mas de una este veredicto se pone en NO CUMPLE por si solo. Un
    veredicto que dependia de lo que el codigo no sabia hacer era el peor
    lugar donde tenerlo: se habria vuelto falso en silencio.

    NO LLEVA `PasoDeMemoria`, y la razon esta censada en
    `normativa.fundamentos.SIN_FUNDAMENTO` bajo F5.V6: la fila V6 de la Fase 5
    de la v8 lleva etiqueta [N] y NINGUN numeral, y su enunciado sale de una
    frase del num. 4.1.1.3.4 a) que RECOMIENDA -- el literal esta en el
    registro, en `MC_HHD.4.1.1.3.4a#MULTIPLES`, y no se transcribe aqui: una
    segunda copia a mano diverge de su `Verbatim` sin que nada avise, que es
    NOR-MEM-01 --. El fundamento
    que si existe es F3.CELDAS, con verbo RECOMIENDA, y funda el paso que
    ADOPTA el numero de celdas -- que es donde esta la decision --. V6 solo
    la comprueba.

    EL CONDUCTO CIRCULAR NO CONSULTA EL CRITERIO, y es la misma regla que
    `M4.caudal_por_celda` (desde EXT-2; antes `MD._caudal_por_barril`): un
    tubo es una celda por construccion de su
    catalogo, y leer alli 'n_celdas_cajon' registraria como usado un criterio
    del marco en una corrida que no tiene ninguno.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        # Por `MD.numero_de_celdas` y no por `ca.valor` a secas: el numero que
        # V6 verifica tiene que ser EL MISMO que reparte el caudal, con la
        # misma guardia. Dos lecturas con dos guardias distintas es como
        # divergen los numeros -- un 2.5 declarado pasaba por una y no por la
        # otra --.
        celdas = numero_de_celdas(material)
        procedencia = f"criterio '{CRITERIO_N_CELDAS_CAJON}' [A]"
        criterio = CRITERIO_N_CELDAS_CAJON
    else:
        celdas = 1
        procedencia = ("por construccion del catalogo circular de la Sec. "
                       "3.2: un tubo es un solo barril")
        criterio = None
    obtenido = f"{celdas} celda(s) -- {procedencia}"
    if celdas > 1 and isinstance(seccion, SeccionRectangular):
        t = espesor_pared(material, seccion.altura)
        ancho = seccion.ancho_exterior_de_celdas(t, celdas)
        reparto = ("" if Q is None else
                   f"; Q/N = {Q / celdas:.3f} m3/s por celda (EXT-2)")
        obtenido += (
            f"{reparto}; tabique entre celdas t = {t:.2f} m (marco "
            f"monolitico vaciado in situ: la separacion de tubos del num. "
            f"4.1.1.3.4 a) -- D/2 entre 0.40 y 1.00 m, entre superficies "
            f"externas -- es de TUBERIAS con relleno entre ellas); ancho "
            f"exterior total {ancho:.2f} m. No se acepta mientras no haya "
            f"dato de arrastre del cauce (ficha EXT-2-01)")
    return Verificacion(
        cumple=celdas == 1,
        numeral=NUMERAL_V6,
        valor_obtenido=obtenido,
        valor_admisible="sección única con palizada",
        criterio_aplicado=criterio,
        codigo="V6",
    )


# ---------------------------------------------------------------------------
# V7 - Flotacion del conducto (Manual de Puentes num. 2.4.3.8.2 + Fase 8.3)
# ---------------------------------------------------------------------------

def v7_flotacion(*, punto: PuntoCritico, material: Material,
                 seccion: Seccion,
                 resultado: ResultadoHidraulico) -> Verificacion:
    """
    Flotacion del conducto por EQUILIBRIO DE FACTORES DE CARGA LRFD, tuberia
    vacia y NF en su cota mas alta (Fase 5, fila V7):

        gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U

    Se minoran las cargas que estabilizan -- peso propio del conducto (DC) y
    peso del relleno sobre la clave (EV), con sus gamma MINIMOS de la Tabla
    2.4.5.3.1-2 -- y se mayora la subpresion, que desestabiliza (WA, Tabla
    2.4.5.3.1-1). Para un conducto enterrado es la forma
    0.90*(DC + EV) >= 1.00*U.

    CON UN MARCO ESTA VERIFICACION YA CORRE SIN SUPONER LA FORMA, y hasta C7
    no. Este parrafo declaraba TRES defectos abiertos --C5 los abrio al hacer
    que la Familia C llegase hasta aqui-- y los tres se cerraron en C7. Se
    deja el censo, con lo que cerro cada uno, porque un defecto declarado que
    desaparece del docstring sin decir como se cerro es indistinguible de uno
    que se borro:

      1. CERRADO (C7, punto 2). `M8.empuje_flotacion_kn_m` y
         `M8.peso_relleno_kn_m` recibian `D_exterior` y calculaban sobre
         pi*D^2/4, o sea un CILINDRO. Hoy reciben la `Seccion` y piden
         `area_exterior` y `ancho_exterior`, que el protocolo implementa en
         las dos formas. Medido en el caso patron CP10: sobre un marco de
         2.00 x 1.50 con t = 0.15 la U del prisma es 40.61 kN/m y la del
         cilindro circunscrito 24.96, o sea que V7 sobreestimaba la seguridad
         un 27 %, en la direccion insegura.
      2. CERRADO (C7, punto 1). `M2.espesor_pared` indexaba por DIAMETRO
         DESIGNADO en milimetros, que es la columna «Wall Thickness» de una
         norma de TUBERIA donde un marco vaciado in situ no tiene fila. Hoy
         el marco lee 'espesor_pared_cajon', criterio [A] de perfil sin valor,
         y se detiene con `CriterioPendienteError` hasta que se declare.
      3. CERRADO (C7, punto 3). `M8.factores_carga_flotacion` indexaba
         `factores_carga_aashto` por `material.tipo.value`, de modo que un
         marco recibia la fila del TUBO -- «Estructura rigida enterrada» -- y
         no la suya, «Porticos rigidos». Hoy discrimina por FORMA
         (`M8._elemento_de`). El minimo de las dos filas es 0.90 y por eso el
         NUMERO no cambiaba: lo que salia mal era la FILA que la memoria
         imprime, o sea una cita falsa sobre un valor correcto (precedente
         NOR-HID-01).

    LO QUE SIGUE SIN CERRARSE, para que no se lea como que todo lo del marco
    esta hecho: `cota_clave` y `altura_relleno_sobre_clave` siguen recibiendo
    un escalar `D`, y esta funcion se lo da como `seccion.altura`. Es correcto
    -- la clave es la generatriz superior y se apila sobre la altura INTERIOR,
    que en un marco es H -- y aun asi es el ultimo sitio de la cadena de V7
    donde viaja un numero en vez de una seccion. Va con `ResultadoPunto.D`,
    que el brief de C7 reserva a C8.

    EL gamma DE EV DEPENDE DEL MATERIAL, y por eso esta funcion le pasa el
    suyo a `factores_carga_flotacion`. La Tabla 2.4.5.3.1-2 desglosa el
    empuje vertical de tierra por TIPO DE ESTRUCTURA: el tubo de concreto es
    "Estructura rigida enterrada", el HDPE una "Alcantarilla termoplastica" y
    el TMC una estructura flexible de la subfila "Entre otros". Los tres
    minimos valen 0.90 y el numero de V7 no cambia por esto; lo que cambia es
    que la fila de la que sale queda dicha, en vez de heredarse de un par
    unico que no era ninguna fila de la tabla (MAT-D8, NOR-PUE-03).

    NO es un FS global. La fila V7 de la hoja de ruta lo enuncia como
    ΣW >= FS*U, que es lenguaje de tension admisible; Sec. 0.2 adopta AASHTO
    LRFD de extremo a extremo, y verificar una demanda LRFD contra un FS
    clasico es la misma incoherencia carga-resistencia que esa seccion declara
    resuelta. El criterio 'FS_flotacion' que sostenia el umbral se retiro: en
    LRFD el margen lo hacen los propios gamma, y conservar ademas un FS seria
    contar dos veces el mismo margen. Ver "Por que V7 ya no usa un factor de
    seguridad global" en el docstring de `modulos.M8_estructural`.

    El procedimiento esta completo en `modulos.M8_estructural` (Fase 8, item
    3); esta funcion solo arma la altura de relleno del punto y ensambla el
    resultado.

    La altura de relleno sobre la clave es la REAL del punto -- cota de
    subrasante menos la cota de la clave -- no el minimo de Sec. 7.A: V7 pesa
    el relleno que de verdad hay encima, no un piso admisible. No la resta
    aqui: la pide a `altura_relleno_sobre_clave`, que es la misma que consume
    la Fase 8 y trae la guarda de cotas incoherentes con ella (SIS-A-21). Esa
    funcion usa la misma `cota_clave` que el tamizado de 7.A, que a su vez usa
    la misma cota de entrada que V4 (`cota_de_entrada`, el dato medido o la regla
    declarada en 'origen_cota_fondo_entrada'), para no evaluar la flotacion
    contra una referencia distinta de la que fija la rasante. Esa clave es la
    FISICA: lleva el espesor de pared, y por eso V7 se detiene tambien en
    'espesor_pared_conducto' (MAT-D4).

    U y EV se calculan sobre el diametro EXTERIOR, no sobre el interior. El
    num. 2.4.3.8.2 define la subpresion sobre el volumen desplazado, que es el
    exterior; con t = 0.100 m en un tubo de concreto de D = 0.90 m
    (D_ext = 1.10 m) usar el interior la subestimaba un 33.1 %, y el docstring
    de M8 declaraba esa aproximacion "del lado conservador" cuando es
    exactamente la contraria (MAT-D3).

    DC = 0: no suma el peso propio del conducto (ver "Por que el peso propio
    del conducto no entra en V7" en el docstring de M8_estructural). Omitirlo
    es conservador, reduce el lado estabilizante en vez de inflarlo.

    Se detiene en 'peso_especifico_relleno_kn_m3' (el termino EV) o en
    'factores_carga_aashto' (la eleccion de fila de gamma_p), los dos vacios
    que le faltan al procedimiento -- no en un vacio de METODO: ver el
    docstring del modulo.
    """
    exigir_seccion_coherente(material, seccion)
    D = seccion.altura
    altura_relleno = altura_relleno_sobre_clave(punto=punto, material=material,
                                                seccion=seccion)

    t = espesor_pared(material, D)
    U = empuje_flotacion_kn_m(seccion=seccion, espesor=t)
    EV = peso_relleno_kn_m(seccion=seccion, espesor=t,
                           altura_relleno=altura_relleno)
    DC = 0.0                 # peso propio omitido, del lado conservador
    g = factores_carga_flotacion(material=material)   # CriterioPendienteError si EV no se detuvo antes

    estabilizante = g.gamma_DC * DC + g.gamma_EV * EV
    desestabilizante = g.gamma_WA * U

    # DE DONDE SALIO t, dicho en el paso (T-4, INF-5.1.17). Hasta T-4 el TMC
    # y el HDPE no llegaban aqui --no tenian espesor--, y cuando el unico
    # material era el concreto bastaba la ficha del criterio. Con tres
    # origenes distintos, V7 dice cual es el del material que juzga.
    texto_t, cita_t, clave_t = procedencia_del_espesor(material)
    eleccion_t = eleccion(
        "F3.D_EXTERIOR",
        que_se_adopto="espesor que separa el diametro hidraulico del "
                      "exterior",
        valor=f"t = {t:.5g} m",
        entre=(),
        de_donde=texto_t,
        cita_id=cita_t,
        clave_criterio=clave_t)

    cumple = estabilizante >= desestabilizante - TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V7,
        valor_obtenido=estabilizante,
        valor_admisible=desestabilizante,
        criterio_aplicado=CRITERIO_FACTORES_CARGA,
        codigo="V7",
        paso=paso(
            "F5.V7",
            codigo="V7",
            que="Flotacion: equilibrio del conducto vacio bajo el freatico",
            formula="gamma_DC_min*DC + gamma_EV_min*EV >= gamma_WA*U",
            formula_cita_id="MP.T2.4.5.3.1-2",
            # LAS DOS FRASES QUE DISCUTEN EL EXTREMO DE gamma_EV, LITERALES Y
            # JUNTAS, bajo «Lo que dice la fuente». Una autoriza minorar y la
            # otra manda mayorar, y las dos son `shall`: quien defienda esta
            # memoria en una sustentacion tiene que poder verlas ahi y no
            # descubrirlas leyendo el PDF. Cual sigue el proyecto y por que lo
            # dice el `por_que` de F5.V7, que M11 imprime en otro bloque --
            # NOR-HID-04: lo que la fuente DICE y lo que el proyecto LEE no se
            # pegan --. La discrepancia entera esta en
            # DIS-AASHTO-GAMMA-EV-12.6.1, estado ABIERTA.
            citas_textuales=("MP.2.4.5.3.1#MINIMO",
                             "AASHTO_LRFD_9.12.6.1#GAMMA_EV_MAX"),
            sustitucion=(
                Magnitud("Bc", seccion.ancho_exterior(t), "m",
                         "ancho EXTERIOR en planta (Art. 12.6.6.3 de AASHTO: "
                         "«outside diameter or width of the structure»). Es "
                         "el ancho del prisma de relleno", cifras=CIFRAS_MAGNITUD),
                Magnitud("B'c", seccion.canto_exterior(t), "m",
                         "canto EXTERIOR («out-to-out vertical rise»). En un "
                         "marco NO coincide con Bc; en una circular si, y esa "
                         "coincidencia es la que oculto el defecto hasta C7",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("altura_relleno", altura_relleno, "m",
                         "cota de subrasante menos cota de clave FISICA del "
                         "punto: el relleno que de verdad hay encima, no el "
                         "minimo admisible de 7.A", cifras=CIFRAS_MAGNITUD),
                Magnitud("U", U, "kN/m",
                         "subpresion sobre el conducto vacio "
                         "(num. 2.4.3.8.2 del Manual de Puentes)", cifras=CIFRAS_MAGNITUD),
                Magnitud("EV", EV, "kN/m",
                         "peso del relleno sobre la clave", cifras=CIFRAS_MAGNITUD),
                Magnitud("DC", DC, "kN/m",
                         "peso propio del conducto, OMITIDO a proposito: "
                         "reduce el lado estabilizante y es del lado "
                         "conservador", cifras=CIFRAS_MAGNITUD),
                Magnitud("gamma_EV_min", g.gamma_EV, "",
                         "minimo de la fila de gamma_p que describe a este "
                         "material en la Tabla 2.4.5.3.1-2", cifras=CIFRAS_FACTOR),
                Magnitud("gamma_WA", g.gamma_WA, "",
                         "factor de la carga de agua, Tabla 2.4.5.3.1-1",
                         cifras=CIFRAS_FACTOR)),
            resultado=Magnitud("accion estabilizante", estabilizante, "kN/m",
                               "gamma_DC*DC + gamma_EV*EV", cifras=CIFRAS_MAGNITUD),
            umbral=_umbral_de(
                "V7", valor=desestabilizante, unidad="kN/m",
                descripcion="accion desestabilizante mayorada (gamma_WA*U)",
                criterio=CRITERIO_FACTORES_CARGA),
            veredicto=_veredicto(
                cumple, estabilizante - desestabilizante, "kN/m",
                "el conducto vacio no flota" if cumple else
                "la subpresion supera lo que lo sujeta: el conducto flota"),
            elecciones=(eleccion(
                "F5.V7_FILA",
                que_se_adopto="fila de gamma_p que describe a esta estructura",
                valor=f"«{g.fila_gamma_EV}» -> gamma_EV min = {g.gamma_EV}",
                entre=filas_ev_de_la_tabla(),
                de_donde="la Tabla 2.4.5.3.1-2 del Manual de Puentes "
                         "(= 3.4.1-2 de AASHTO LRFD), pag. impresa 143",
                cita_id="MP.T2.4.5.3.1-2",
                clave_criterio=CRITERIO_FACTORES_CARGA), eleccion_t),
        ),
    )


# ---------------------------------------------------------------------------
# V8 - Evento extremo / FEN (Fase 5, V8)
# ---------------------------------------------------------------------------

def v8_evento_extremo(*, punto: PuntoCritico,
                      resultado: ResultadoHidraulico,
                      material: Optional[Material] = None,
                      seccion: Optional[Seccion] = None,
                      evento: Optional[EventoExtremoDelPunto] = None
                      ) -> Verificacion:
    """
    V8: a un periodo de retorno mayor que el de diseño, la via no colapsa
    aunque desborde (Fase 5, fila V8).

    --- T-7b --- TIENE METODO Y UMBRAL DECLARABLES, con la misma decision que
    V5: nada tiene valor de archivo, y sin declarar V8 se detiene como
    siempre. Se detiene, en este orden y nunca con un fallo de programa:

      * 'TR_evento_extremo' sin valor -> `CriterioPendienteError`;
      * sin `Q_evento_extremo_m3s`     -> `DatoFaltanteError`: el caudal de
        ese periodo de retorno es un dato externo por punto (lo da el
        estudio hidrologico; la Fase 1-bis lo sabe calcular, y el enlace
        sigue diferido, ficha T1-03). El programa no lo escala del de
        diseño;
      * sin `TW_evento_extremo_m`      -> `DatoFaltanteError`: el tirante
        del receptor en ese evento. Usar el de diseño seria rellenar una
        entrada del lado NO conservador (el receptor sube con la avenida);
        admite 0, salida libre;
      * 'umbral_no_colapso_evento_extremo' sin valor ->
        `CriterioPendienteError`: la hoja de ruta no dice como se juzga el
        colapso;
      * el umbral declarado es el del desborde admitido, o la carga del
        evento no se puede evaluar ni a presion -> `MetodoNoEvaluableError`.

    EL METODO: el caudal del evento se corre por la MISMA seccion, material,
    pendiente y longitud del CANDIDATO (M3 y M4, que resuelve el servicio:
    `EventoExtremoDelPunto.resolver`) y da la carga HW_ext: en lamina libre
    con la hidraulica entera de M4 o, si el caudal no cabe en lamina libre,
    con el barril A PRESION (`M4.hidraulica_a_presion`: el control de
    entrada sumergido y el de salida a barril lleno, gobernando el mayor;
    correcciones de T-7b, H3). Y solo se evalua sobre el candidato que YA
    cumple todo lo anterior de la tabla (`verificar`): un V8 que no se puede
    evaluar no enmascara un V1 o un V5 incumplido. Con el umbral
    «sin_desborde_de_la_plataforma» se compara la cota del embalse (solera
    de entrada + HW_ext) con la cota a la que la plataforma desborda (su
    borde del lado de la entrada). Si no la alcanza, la via no desborda. Es
    la lectura MAS EXIGENTE de la fila, que admite el desborde: lo que el
    HDS-5 sostiene (num. 2.2.5 a.) es la cota de comparacion, no el
    periodo de retorno ni la definicion de colapso.
    """
    TR = ca.valor(CRITERIO_EVENTO_EXTREMO)   # CriterioPendienteError: sin TR
    if evento is None or evento.Q_m3s is None:
        raise DatoFaltanteError(
            "Q_evento_extremo_m3s",
            id_punto=punto.id,
            detalle=(
                f"el criterio '{CRITERIO_EVENTO_EXTREMO}' esta declarado, "
                "pero V8 no puede resolverse sin el CAUDAL que corresponde a "
                "ese periodo de retorno mayor: declarar "
                "`Q_evento_extremo_m3s` por --datos-externos, con el estudio "
                "hidrologico que lo da. El programa SABE calcularlo "
                "(`MH_hidrologia.caudal_de_diseno` admite cualquier periodo "
                "de retorno), pero ese enlace esta diferido (ficha T1-03 de "
                "docs/decisiones_diferidas.md), y no lo escala del de "
                "diseño"
            ),
        )
    if evento.TW_m is None:
        raise DatoFaltanteError(
            "TW_evento_extremo_m",
            id_punto=punto.id,
            detalle=(
                "V8 corre el caudal del evento extremo por la seccion "
                "adoptada y necesita el tirante del receptor EN ESE EVENTO "
                "(m sobre el fondo de la salida; 0 = salida libre): "
                "declarar `TW_evento_extremo_m` por --datos-externos. No se "
                "toma el de diseño: el receptor sube con la avenida y "
                "usarlo subestimaria la carga"
            ),
        )
    umbral_v8 = ca.valor(CRITERIO_UMBRAL_V8)   # CriterioPendienteError
    if umbral_v8 not in UMBRALES_V8:
        raise DatoInvalidoError(
            CRITERIO_UMBRAL_V8, valor=umbral_v8, id_punto=punto.id,
            motivo="se espera uno de: " + ", ".join(UMBRALES_V8))
    Q_ext = evento.Q_m3s
    if isinstance(Q_ext, bool) or not isinstance(Q_ext, (int, float)) \
            or not math.isfinite(Q_ext) or not Q_ext > 0:
        raise DatoInvalidoError(
            "Q_evento_extremo_m3s", valor=Q_ext, id_punto=punto.id,
            motivo="el caudal del evento extremo tiene que ser finito y "
                   "positivo")
    if not Q_ext >= resultado.Q - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "Q_evento_extremo_m3s", valor=Q_ext, id_punto=punto.id,
            motivo=f"el caudal del evento extremo ({Q_ext:.3f} m3/s) es "
                   f"menor que el de diseño ({resultado.Q:.3f} m3/s): V8 "
                   "verifica un periodo de retorno MAYOR")
    if umbral_v8 != UMBRAL_V8_SIN_DESBORDE:
        raise MetodoNoEvaluableError(
            "V8", "flujo sobre la plataforma (HDS-5 num. 3.1.5) y erosion "
            "del talud de aguas abajo",
            "el umbral declarado en 'umbral_no_colapso_evento_extremo' "
            "admite el desborde con el terraplen protegido, y juzgarlo "
            "exige repartir el caudal entre el conducto y la plataforma: no "
            "esta implementado",
            id_punto=punto.id, rotulo=MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO)
    if evento.resolver is None or material is None or seccion is None \
            or evento.cota_desborde is None:
        raise DatoFaltanteError(
            "cota_desborde", id_punto=punto.id,
            detalle="V8 necesita la seccion candidata, la hidraulica del "
                    "evento y la cota de desborde de la plataforma, que el "
                    "servicio le entrega; una llamada suelta a "
                    "`v8_evento_extremo` tiene que traerlas en `evento`")
    extremo = evento.resolver(seccion=seccion, material=material)
    if extremo is None:
        # El servicio resuelve SIEMPRE: en lamina libre o, si no cabe, con el
        # barril a presion (correcciones de T-7b, H3). Un resolver que no
        # devuelve nada es de una llamada suelta.
        raise MetodoNoEvaluableError(
            "V8", "carga del caudal del evento extremo",
            f"la seccion candidata ({seccion.etiqueta()}) no tiene carga "
            f"evaluada para el caudal del evento extremo ({Q_ext:.3f} m3/s)",
            id_punto=punto.id, rotulo=MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO)
    entrada = cota_de_entrada(punto)
    HW_ext = extremo.HW
    cota_embalse = entrada.valor + HW_ext
    cota_desborde = evento.cota_desborde
    if not (math.isfinite(cota_embalse) and math.isfinite(cota_desborde)):
        raise LimiteNumericoError(
            "cota del embalse del evento extremo", valor=cota_embalse,
            id_punto=punto.id,
            motivo="la cota del embalse o la de desborde no es finita")
    cumple = cota_embalse <= cota_desborde + TOL_UMBRAL_NORMATIVO
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V8,
        valor_obtenido=cota_embalse,
        valor_admisible=cota_desborde,
        criterio_aplicado=CRITERIO_UMBRAL_V8,
        codigo="V8",
        paso=paso(
            "F5.V8", codigo="V8",
            que="V8: nivel del embalse con el caudal del evento extremo "
                "frente a la cota de desborde de la plataforma",
            formula=("cota de entrada + HW(Q_ext)  <=  cota de desborde de "
                     "la plataforma"),
            sustitucion=(
                Magnitud("TR_ext", TR, "años",
                         f"criterio '{CRITERIO_EVENTO_EXTREMO}' [A], "
                         "declarado", cifras=CIFRAS_MAGNITUD),
                Magnitud("Q_ext", Q_ext, "m3/s", evento.origen,
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("Q_diseno", resultado.Q, "m3/s",
                         "caudal de diseño del punto", cifras=CIFRAS_MAGNITUD),
                Magnitud("TW_ext", evento.TW_m, "m",
                         "tirante del receptor en el evento extremo "
                         "(`TW_evento_extremo_m`, dato externo)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("HW_ext", HW_ext, "m",
                         "carga de M4 con Q_ext por la seccion candidata "
                         f"({seccion.etiqueta()}), "
                         f"{getattr(extremo, 'regimen', 'lamina libre')}, "
                         "control que gobierna: "
                         f"{extremo.control_gobernante.value}"
                         + (f" ({extremo.nota})" if getattr(extremo, "nota",
                                                            "") else ""),
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_entrada", entrada.valor, "msnm",
                         entrada.procedencia, cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "cota_embalse_ext", cota_embalse, "msnm",
                "cota de entrada + HW_ext", cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="cota de desborde de la plataforma ("
                            + evento.origen_cota_desborde + ")",
                valor=cota_desborde, unidad="msnm",
                cita_id="HDS5_3ED.2.2.5a#COTA_CRITICA",
                caracter="PERMISO",
                aplicacion="umbral del proyecto: la fuente admite esa cota "
                           "de comparacion y no define el colapso; criterio "
                           f"'{CRITERIO_UMBRAL_V8}' [A]",
                criterio_aplicado=CRITERIO_UMBRAL_V8),
            veredicto=_veredicto(
                cumple, cota_desborde - cota_embalse, "m",
                ("el evento extremo no desborda la plataforma" if cumple else
                 "el evento extremo desborda la plataforma por esta seccion "
                 "candidata: con el umbral declarado V8 no cumple; hace "
                 "falta una seccion mayor, o el analisis del flujo sobre la "
                 "via con el terraplen protegido")),
            nota_del_proyecto=(
                f"Umbral '{umbral_v8}' ('{CRITERIO_UMBRAL_V8}', [A]): es la "
                "lectura mas exigente de la fila V8, que admite el "
                "desborde. El periodo de retorno, el caudal y el tirante "
                "del receptor del evento son entradas del proyecto. La "
                "pendiente y la longitud son las del diseño. No se evalua "
                "la erosion del terraplen ni el sifonamiento por la carga "
                "sostenida.")),
    )


# ---------------------------------------------------------------------------
# V9 - Disponibilidad de diametro (Sec. 3.2, nuevo en v7)
# ---------------------------------------------------------------------------

def v9_disponibilidad_diametro(*, D: float, material: Material) -> Verificacion:
    """
    Disponibilidad de SECCION: la dimension requerida <= el tope de CATALOGO
    del material. El tope es `material.D_max`, que M2 resuelve -- V9 solo lo
    consulta, no lo recalcula.

    ES DISPONIBILIDAD DE SECCION Y NO DE DIAMETRO DESDE C5, y el nombre no
    cambio a proposito: `v9_disponibilidad_diametro` es el simbolo que
    nombran la Sec. 4.4 del plan, la fila V9 de la Fase 5 y los marcadores de
    las plantillas de M11, y renombrarlo por precision semantica habria
    costado arrastrar los cuatro sitios para no ganar ningun numero. Lo que si
    cambio es DE DONDE SALE EL TOPE, porque atribuirlo mal era una cita falsa:

      * circular: el tope lo resuelve `M2.tope_de_diametro` y se compara
        contra el diametro interior. Hasta T-4 salia del criterio
        'D_max_catalogo' [A]; desde T-4 sale de la norma de producto
        ('D_max_norma_producto' [C]: en concreto, el ultimo diametro con
        diseño estandar de M 170M, 2.70 m), del mayor diametro estandar
        de la corrugacion adoptada en TMC ('corrugacion_y_espesor_tmc' [A])
        o, si el proyectista la declara por debajo, de la disponibilidad
        ('D_max_catalogo' [A], opcional). `Material.D_max_criterio` dice
        cual de los tres goberno y esa es la clave que viaja en
        `criterio_aplicado`;
      * marco: el tope es la MAYOR altura interior de la progresion que el
        expediente declara en 'secciones_cajon_normalizadas' [A], y se compara
        contra la altura de la seccion adoptada. Atribuir el tope de un cajon
        a 'D_max_catalogo' -- cuyo valor es un diametro de tubo por material
        -- habria puesto en la memoria un numero verdadero bajo una
        procedencia falsa.

    LO QUE SIGUE DESCRIBE EL ESTADO ANTERIOR A T-4, y se conserva porque es
    el argumento por el que el tope dejo de ser una adopcion sin respaldo:
    «NO ES UN UMBRAL NORMATIVO EN NINGUNA DE LAS DOS FORMAS» era cierto del
    2.70 / 2.10 / 1.50 m de 'D_max_catalogo', y en el tubo ya no lo es del
    tope de la serie (INF-3.3.1). Para el marco sigue valiendo entero.

    NO ERA UN UMBRAL NORMATIVO EN NINGUNA DE LAS DOS FORMAS (NOR-PRO-01,
    NOR-PRO-02, MAT-O8). El tope circular se atribuia a ASTM C76/AASHTO M170,
    AASHTO M36/ASTM A760 y AASHTO M294, y ninguna de las dos primeras lo
    sostiene: A760 tabula diametros nominales hasta 3600 mm y M 170M igual.
    La tercera si termina donde el proyecto topa -- la serie de AASHTO
    M 294-11 acaba en 1500 mm, verificado en N2 sobre una traduccion no
    oficial sin firma --, y aun asi el tope del HDPE sigue siendo de
    catalogo: la eleccion es la misma para los tres materiales y este paso
    descarta por catalogo, no por norma. Es una
    adopcion del proyecto sobre la disponibilidad de mercado, y el tope del
    marco lo es todavia mas claramente: es la serie que el proyectista
    escribio. Por eso `criterio_aplicado` apunta al criterio y no a una norma:
    un punto rechazado por V9 no lo rechaza la norma.
    """
    de_cajon = material.forma is FormaSeccion.RECTANGULAR
    return Verificacion(
        cumple=D <= material.D_max + TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_V9,
        valor_obtenido=D,
        valor_admisible=material.D_max,
        criterio_aplicado=(CRITERIO_SECCIONES_CAJON if de_cajon
                           else material.D_max_criterio
                           or CRITERIO_D_MAX_NORMA),
        codigo="V9",
    )


# ---------------------------------------------------------------------------
# --- T-2 --- V10 - Pendiente del conducto dentro de la banda adoptada
# ---------------------------------------------------------------------------

def fase_8_estructural(*, punto: PuntoCritico, material: Material,
                       seccion: Seccion) -> Tuple[Verificacion, ...]:
    """
    --- T-5 --- Las verificaciones estructurales del conducto que deciden si
    el escalon EXISTE (INF-3.3.5): la clase del tubo de concreto, el area de
    pared con pandeo, la costura y el factor de flexibilidad del TMC, y el
    empuje, el pandeo y la deflexion del HDPE. Las calcula
    `M8.verificaciones_estructurales` con la altura REAL de relleno sobre la
    clave fisica (`altura_relleno_sobre_clave`, la misma de V7); el marco no
    aporta ninguna --su diseño se difiere al expediente--.

    Entran a la tabla de la Fase 5 DETRAS de V9 y con codigo «F8.*», como
    V7 --que es Fase 8, item 3-- ya entraba: no son filas de la tabla de la
    hoja de ruta sino de la Fase 8, que la corrida ensambla aqui porque
    deciden la aceptacion del escalon igual que una V.
    """
    altura = altura_relleno_sobre_clave(punto=punto, material=material,
                                        seccion=seccion)
    return verificaciones_estructurales(punto=punto, material=material,
                                        seccion=seccion, altura_relleno=altura)


def v10_pendiente_conducto(*, resultado: ResultadoHidraulico) -> Verificacion:
    """
    S_min <= S_conducto <= S_max, con la banda de los criterios [A]
    'pendiente_minima_conducto' y 'pendiente_maxima_conducto' (T-2,
    INF-3.2.7).

    QUE DICE LA FUENTE Y QUE NO. El Manual (num. 4.1.1.3.3 «Pendiente
    longitudinal», pag. impresa 71) exige que la pendiente de la
    alcantarilla no altere «desmesuradamente» la erosion y la sedimentacion
    y que sus cambios se estudien con cuidado; NO fija cifra, ni minima ni
    maxima. El HDS-5 admite el barril horizontal (num. 3.3.4, pag. impresa
    3.25) y DESCRIBE que la mayoria de las alcantarillas se construyen por
    debajo del 10 %, sin medidas estructurales especiales (num. 5.4.4, pag.
    impresa 5.16). De ahi la banda adoptada: 0.0 a 0.10, cada extremo con su
    ventana y su ficha. Es [A]: un punto rechazado por V10 no lo rechaza la
    norma, lo rechaza la banda que el proyecto adopto.

    LA PENDIENTE QUE SE JUZGA es `resultado.S`, la pendiente CON QUE CORRIO
    EL DISEÑO, que es la misma que usa la Fase 7 (MAT-D9). No se vuelve a
    elegir aqui: la resuelve `M7.pendiente_adoptada`, una vez y antes de la
    Fase 4, con su origen.

    EL REPARTO CON M7 (T-6), porque las dos piezas leen la misma banda con
    `limites_de_pendiente()`. M7 ACOTA la pendiente del CAUCE: si `S_cauce`
    cae fuera de la banda, el diseño corre con el extremo --origen «minima»
    o «maxima» del paso 7.B.1--, la corrida lo avisa y dice que trae consigo
    (una estructura de caida o disipacion, o una salida bajo el cauce
    natural). Esta verificacion JUZGA la pendiente que quedo, y como la del
    cauce ya llega dentro de la banda, en la corrida del servicio solo la
    incumple una pendiente DECLARADA (`S_conducto`), que M7 no pisa. Llamada
    directamente, o por `MD.disenar_punto` sin la pendiente resuelta, juzga
    la que reciba.

    NO DEPENDE DEL DIAMETRO, y hay que decirlo: si la pendiente cae fuera de
    la banda, ningun escalon del catalogo la cumple y el punto sale «no
    factible» con V10 incumplida en toda su progresion. El remedio no es
    otro tubo: es otra pendiente declarada (`S_conducto`) --o ninguna, y
    entonces rige la del cauce acotada por M7--, o declarar otra banda con
    su razon.

    NO SUSTITUYE A LAS QUE MIDEN EL EFECTO. La sedimentacion la juzgan V2
    (velocidad minima) y V2b (indicador de pendiente frente al cauce); la
    erosion, V3 (velocidad maxima) y la proteccion de la Fase 6. V10 acota
    la geometria; aquellas, lo que el agua hace con ella.
    """
    S = resultado.S
    s_min, s_max = limites_de_pendiente()
    sobre_la_minima = S >= s_min - TOL_UMBRAL_NORMATIVO
    bajo_la_maxima = S <= s_max + TOL_UMBRAL_NORMATIVO
    cumple = sobre_la_minima and bajo_la_maxima
    # EL EXTREMO QUE SE IMPRIME COMO ADMISIBLE es el que el punto incumple;
    # si cumple los dos, el maximo, que es el que tiene consecuencia de obra.
    gobierna_minima = not sobre_la_minima
    admisible = s_min if gobierna_minima else s_max
    criterio = (CRITERIO_PENDIENTE_MINIMA if gobierna_minima
                else CRITERIO_PENDIENTE_MAXIMA)
    margen = (S - s_min) if gobierna_minima else (s_max - S)
    umbral = _umbral_de(
        "V10", valor=admisible, unidad="m/m",
        descripcion=("pendiente minima adoptada del conducto"
                     if gobierna_minima else
                     "pendiente maxima adoptada del conducto: hasta ella la "
                     "fuente no pide medidas estructurales especiales"),
        criterio=criterio)

    def _eleccion(clave: str, que: str, valor: float, por_que: str,
                  cita: str) -> EleccionDeProyecto:
        return EleccionDeProyecto(
            que_se_adopto=que, valor=f"{valor:g} m/m",
            # La ventana es parte de la ficha, pero un caso patron puede
            # sustituir el criterio entero sin ella: entonces no hay «entre».
            entre=tuple(f"{v:g} m/m"
                        for v in (ca.criterio(clave).sensibilidad or ())),
            de_donde=f"el criterio '{clave}' [A]: ninguna fuente de normas/ "
                     "fija esta pendiente en cifras",
            por_que=por_que, cita_id=cita, clave_criterio=clave)

    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_V10,
        valor_obtenido=S,
        valor_admisible=admisible,
        criterio_aplicado=criterio,
        codigo="V10",
        paso=paso(
            "F5.V10",
            codigo="V10",
            que="Pendiente del conducto: dentro de la banda adoptada",
            formula="S_min <= S_conducto <= S_max",
            formula_cita_id="MC_HHD.4.1.1.3.3",
            citas_textuales=("MC_HHD.4.1.1.3.3", "HDS5_3ED.3.3.4#HORIZONTAL",
                             "HDS5_3ED.5.4.4#PENDIENTE_10"),
            sustitucion=(
                Magnitud("S_conducto", S, "m/m",
                         "pendiente CON QUE CORRIO EL DISEÑO (paso 7.B.1: "
                         "cauce, extremo de la banda o `S_conducto` "
                         "declarada)",
                         cifras=CIFRAS_FINA),
                Magnitud("S_min", s_min, "m/m",
                         f"criterio '{CRITERIO_PENDIENTE_MINIMA}' [A]",
                         cifras=CIFRAS_FINA),
                Magnitud("S_max", s_max, "m/m",
                         f"criterio '{CRITERIO_PENDIENTE_MAXIMA}' [A]",
                         cifras=CIFRAS_FINA)),
            resultado=Magnitud(
                "S_conducto - S_min" if gobierna_minima
                else "S_max - S_conducto", margen, "m/m",
                "holgura respecto del extremo de la banda que se imprime "
                "como admisible: negativa es fuera de la banda",
                cifras=CIFRAS_FINA),
            umbral=umbral,
            veredicto=_veredicto(
                cumple, margen, "m/m",
                "la pendiente del conducto esta dentro de la banda adoptada"
                if cumple else
                "el conducto queda MAS PLANO que la pendiente minima adoptada"
                if gobierna_minima else
                "el conducto queda MAS EMPINADO que la pendiente maxima "
                "adoptada: por encima de ella la fuente pide medidas "
                "estructurales que este calculo no dimensiona"),
            elecciones=(
                _eleccion(
                    CRITERIO_PENDIENTE_MINIMA,
                    "pendiente minima admitida en el conducto", s_min,
                    "el Manual no fija cifra y el HDS-5 admite el barril "
                    "horizontal; la sedimentacion la juzgan V2 y V2b, no "
                    "esta banda", "HDS5_3ED.3.3.4#HORIZONTAL"),
                _eleccion(
                    CRITERIO_PENDIENTE_MAXIMA,
                    "pendiente maxima admitida en el conducto", s_max,
                    "el HDS-5 describe que bajo el 10 % no se usan medidas "
                    "estructurales especiales; este programa no dimensiona "
                    "anclajes ni ataduras", "HDS5_3ED.5.4.4#PENDIENTE_10")),
            nota_del_proyecto=(
                "LA BANDA ES DEL PROYECTO, NO DE LA NORMA: el Manual exige "
                "estudiar la pendiente y no la acota en cifras. Esta "
                "verificacion no depende del diametro -- la pendiente es la "
                "misma en todo el catalogo --, de modo que incumplirla no se "
                "resuelve con otro tubo sino con otra pendiente del conducto "
                "(`S_conducto`) o con otra banda, declarada con su razon. "
                "La pendiente del CAUCE fuera de la banda la sustituye el "
                "extremo antes del diseño (paso 7.B.1): aqui solo incumple "
                "una declarada. Y no sustituye a V2, V2b y V3, que juzgan lo "
                "que el agua hace con esa pendiente."
                + (" EL BARRIL ES HORIZONTAL (S = 0): no hay tirante normal, "
                   "y el paso 4.1 dice de donde salen entonces el tirante y "
                   "la velocidad." if resultado.sin_tirante_normal else "")),
        ),
    )


# ---------------------------------------------------------------------------
# Agregado: la firma que llama MD.py
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# LA UNICA FILA DE LA FASE 5 QUE DEPENDE DE LA FAMILIA, y por que
# ---------------------------------------------------------------------------
# V5 SE DECLARA NO APLICABLE EN LA FAMILIA C, Y VC1 OCUPA SU SITIO. La decision
# es del proyecto y va sostenida aqui, en el sitio donde surte efecto.
#
# POR QUE NO APLICA, y no es que «no se pueda evaluar». V5 verifica que el
# embalse quede DENTRO DEL DERECHO DE VIA, sin invadir predio de tercero ni la
# faja marginal. Esa formulacion presupone agua que se EXTIENDE lateralmente
# sobre el terreno al remansarse contra el terraplen, y por eso el umbral es un
# ancho. En un paso de canal esa premisa es falsa: el agua sube DENTRO de un
# cauce confinado entre dos coronaciones, y su avance no es lateral sobre la
# plataforma sino vertical contra el labio del canal. Un ancho de derecho de
# via no acota nada ahi; lo que acota es la coronacion. Dejarla «pendiente para
# siempre» sostenia que faltaba un dato --- `ancho_derecho_via_m` --- para una
# comparacion que en esta familia no dice lo que hay que decir aunque el dato
# llegue.
#
# LA PREOCUPACION NO DESAPARECE: CAMBIA DE DIRECCION. Lo que V5 protege son
# los terceros, y en un cruce de canal los terceros siguen ahi --- las parcelas
# que el canal riega ---. Solo que se les llega por el canal y no por la
# plataforma, y esa es exactamente la comparacion que hace VC1. Por eso V5 no
# se declara «no aplicable» a secas sino SUSTITUIDA, con su sustituta corriendo
# en la misma posicion de la tabla y con veredicto real.
#
# LO QUE LA SUSTITUCION NO CUBRE, dicho aqui y en la memoria y no solo aqui:
# VC1 mide EN LA SECCION DEL CRUCE y no acota cuanto se extiende el remanso
# aguas arriba. Un tercero situado varios centenares de metros arriba, donde el
# canal tenga la coronacion mas baja, puede quedar afectado por un remanso que
# en el cruce cumple. V5 tampoco lo cubria --- su umbral era un ancho, no una
# longitud ---, de modo que la sustitucion no PIERDE alcance; pero decir que
# VC1 cierra el hueco entero seria falso, y se dice.
# DEVUELVE EL CODIGO ADEMAS DE LA PIEZA, y no es adorno. Hay DOS llamadores
# --- `verificar` aqui y `servicio._verificador_perfil` --- y no tratan igual lo que
# sale: para el de perfil, V5 es una verificacion DIFERIDA (su fallo se anota y
# el punto sigue dimensionandose) mientras que VC1 es OBLIGATORIA (su fallo
# bloquea el material). Si el llamador tuviera que deducir cual le toca
# mirando la familia por su cuenta, la regla viviria en dos sitios y podrian
# divergir: es exactamente lo que ya paso con la lista literal de
# `_verificador_perfil`, que se quedo sin VC1 mientras `verificar` ya lo
# corria, de modo que a `--alcance perfil` --- el alcance del entregable --- un
# cruce de canal seguia saliendo con V5 diferida y sin VC1 por ninguna parte.
def v5_no_aplica_en_canal(*, punto: PuntoCritico) -> Verificacion:
    """
    La fila V5 de la tabla de la Fase 5 en un punto de la Familia C: NO
    APLICA, y se dice con esas palabras (PC-27, cierre del 2026-09-22).

    Hasta aqui la fila no aparecia: VC1 ocupaba su posicion y el revisor que
    contara filas tenia que deducir que V5 se habia sustituido leyendo
    `_remanso_o_cruce_de_canal`. El estado NO_APLICA de
    `EstadoDeVerificacion` existe para esto: la verificacion existe en la
    tabla, en este punto no dice nada --- su umbral es un ANCHO sobre la
    plataforma y en un paso de canal el agua sube confinada entre las dos
    coronaciones ---, y quien la sustituye (VC1, con veredicto real) va en el
    motivo. No cuenta como incumplida ni como cumplida: `cumple=True` es la
    vista que el pipeline lee (no detiene el punto), y el JSON y la memoria
    llevan el estado.
    """
    if punto.familia is not Familia.C:
        raise ValueError(
            f"v5_no_aplica_en_canal es solo para la Familia C y el punto "
            f"{punto.id} es de la Familia {punto.familia.value}")
    return Verificacion(
        cumple=True,
        numeral=NUMERAL_V5,
        valor_obtenido=None,
        valor_admisible=None,
        criterio_aplicado=None,
        codigo="V5",
        estado=EstadoDeVerificacion.NO_APLICA,
        motivo_no_aplica=(
            "V5 verifica que el remanso no se extienda sobre la plataforma "
            "mas alla del derecho de via, y su umbral es un ANCHO; en un "
            "paso de canal (Familia C) el agua sube confinada entre las dos "
            "coronaciones del canal y ese ancho no acota nada. La SUSTITUYE "
            "VC1, que compara la cota del remanso contra la coronacion y "
            "corre en la misma posicion de la tabla con veredicto real; lo "
            "que VC1 no cubre (la extension del remanso aguas arriba) esta "
            "dicho en su propio paso"),
    )


def pieza_del_hueco_de_V5(*, punto: PuntoCritico,
                          resultado: ResultadoHidraulico,
                          derecho_de_via: Optional[DerechoDeViaDelPunto] = None):
    """
    (codigo, pieza) que ocupa la posicion de V5: VC1 en Familia C, V5 si no.
    `derecho_de_via` (T-7b) es lo que V5 necesita del punto y el servicio le
    entrega; la Familia C no lo usa.
    """
    if punto.familia is Familia.C:
        return "VC1", lambda: vc1_borde_libre_canal(punto=punto,
                                                    resultado=resultado)
    return "V5", lambda: v5_remanso(punto=punto, resultado=resultado,
                                    derecho_de_via=derecho_de_via)


def verificar(*, punto: PuntoCritico, material: Material,
             seccion: Seccion,
             resultado: ResultadoHidraulico,
             expediente: Optional[DatosDeExpediente] = None
             ) -> Tuple[Verificacion, ...]:
    """
    --- T-7b --- `expediente` son los datos de expediente que V5 y V8
    necesitan ademas del resultado (`DatosDeExpediente`: el derecho de via
    del punto y el evento extremo); los arma el servicio. Sin el, V5 y V8 se
    detienen donde siempre.


    Las doce verificaciones de la Fase 5, en el orden de la tabla salvo
    V10 (la pendiente del conducto, T-2), que la tabla lista al final y aqui
    se evalua detras de V4b para que V5 y V8 no la tapen. Y detras de V9,
    desde T-5, las de la Fase 8 del conducto (`fase_8_estructural`, codigos
    F8.*), solo si todo lo anterior cumple. Coincide
    con la firma de `modulos.MD.Verificador`: MD la importa como
    `modulos.M5_verificaciones.verificar` cuando no se le inyecta otra.

    UNA SOLA POSICION DEPENDE DE LA FAMILIA, y es la octava (la septima
    hasta T-2, que intercalo V10 detras de V4b): en la Familia C
    la ocupa VC1 (cruce de canal) y en las demas V5 (remanso en el derecho de
    via). El resto se evalua igual en las tres. La justificacion de esa
    sustitucion --- que V5 presupone agua extendiendose sobre la plataforma y
    en un paso de canal el agua sube confinada entre coronaciones --- esta en
    `_remanso_o_cruce_de_canal`, que es donde surte efecto. Es la UNICA
    bifurcacion por familia de este modulo, y deliberadamente no se despacha
    sobre `PerfilFamilia.verificaciones_aceptacion`: aquel campo es la huella
    de una frase de la Sec. 2.3, y convertirlo en filtro dejaria a la Familia
    A sin V3, V6, V7, V8 y V9, que es la lectura no conservadora que su propio
    docstring existe para no habilitar.

    Se detiene -- sin devolver nada -- en la primera de V3 (TMC/HDPE), V5,
    VC1, V7 o V8 que este pendiente: son excepciones, no verificaciones
    incumplidas, y el bucle de MD no debe tratarlas como un diametro rechazado
    sino como lo que son, un calculo que no puede completarse todavia. Desde
    EXT-3 tambien V1 y V2 se detienen asi, con `MetodoNoEvaluableError`,
    cuando el barril va parcialmente lleno bajo control de SALIDA: el tirante
    y la velocidad que comparan exigen el perfil de la lamina de agua. A
    nivel de expediente eso bloquea el punto; a nivel de perfil
    `servicio._verificador_perfil` lo difiere y sigue.

    PERO LO QUE YA SE VERIFICO NO SE TIRA. Al detenerse, la excepcion se lleva
    en `verificaciones_completadas` las que si se evaluaron, con su veredicto y
    con su `PasoDeMemoria`. En ESTE expediente eso no es un detalle: en las
    Familias A y B ninguna combinacion pasa de V5 --- `v5_remanso` se detiene
    siempre en `ancho_derecho_via_m` ---, de modo que sin esto el desarrollo de
    V1 a V4b, que si se calculo entero, no llegaba nunca a la memoria y el
    revisor solo veia «no dimensionado». Es la misma trampa de NOR-MEM-01:
    cierto sobre el codigo y falso sobre el producto. Escribirlo como una lista
    y no como una tupla literal es lo que permite conservarlas.
    """
    # LAS OTRAS TRES SIGUEN PIDIENDO LA ALTURA, y eso no es suponer una
    # forma: `Seccion.altura` es la altura interior de cualquiera de ellas --
    # el "D" de HDS-5, regla vinculante #4 --. Quien necesita mas que la
    # altura es V7, porque la subpresion actua sobre la superficie EXTERIOR y
    # ahi un prisma y un cilindro dejan de parecerse.
    D = seccion.altura
    hechas: list = []

    def pieza_v8():
        return v8_evento_extremo(
            punto=punto, resultado=resultado, material=material,
            seccion=seccion,
            evento=(None if expediente is None
                    else expediente.evento_extremo))

    piezas = (
        lambda: v1_borde_libre(D=D, material=material, punto=punto,
                               resultado=resultado),
        lambda: v2_velocidad_minima(resultado=resultado),
        lambda: v2b_sedimentacion(punto=punto, resultado=resultado),
        lambda: v3_velocidad_maxima(material=material, resultado=resultado),
        lambda: v4_carga_entrada(punto=punto, resultado=resultado),
        lambda: v4b_relacion_hw_d(D=D, resultado=resultado),
        # --- T-2 --- V10 VA ANTES DEL HUECO DE V5, y no al final de la
        # tabla. No depende del diametro, de la familia ni de ningun dato de
        # expediente --su banda son dos criterios con valor--, y detras de V5
        # y de V8 no llegaba a evaluarse en ninguna corrida de expediente del
        # repositorio: las dos se detienen por un criterio pendiente y esta
        # tupla se corta en la primera que se detiene. Lo midio el auditor
        # adversarial de T-2.
        lambda: v10_pendiente_conducto(resultado=resultado),
        pieza_del_hueco_de_V5(
            punto=punto, resultado=resultado,
            derecho_de_via=(None if expediente is None
                            else expediente.derecho_de_via))[1],
        lambda: v6_material_solido_arrastre(material=material,
                                            seccion=seccion,
                                            Q=resultado.Q),
        lambda: v7_flotacion(punto=punto, material=material,
                             seccion=seccion, resultado=resultado),
        pieza_v8,
        lambda: v9_disponibilidad_diametro(D=D, material=material),
    )
    for pieza in piezas:
        # --- correcciones de T-7b (H3) --- V8 SOLO SOBRE EL CANDIDATO QUE YA
        # CUMPLE LO ANTERIOR: corre un caudal mayor por la seccion candidata
        # y, si no pudiera evaluarse, enmascaraba el V1 o el V5 que de verdad
        # la descartan. Un candidato que ya incumple se rechaza igual, sin V8.
        if pieza is pieza_v8 and not all(v.cumple for v in hechas):
            continue
        try:
            hechas.append(pieza())
        except ErrorProyecto as exc:
            exc.verificaciones_completadas = tuple(hechas)
            raise
        # LA FILA SUSTITUIDA SE IMPRIME COMO «NO APLICA» (PC-27): en la
        # Familia C, detras de VC1 va la V5 que VC1 sustituye, con su motivo.
        if hechas[-1].codigo == "VC1":
            hechas.append(v5_no_aplica_en_canal(punto=punto))
    # --- T-5 --- LA FASE 8 DEL CONDUCTO, detras de la tabla y SOLO si todo
    # lo anterior cumple: un escalon que ya incumple una V se rechaza igual,
    # y evaluarle la Fase 8 dejaria que un dato estructural que falta tapara
    # el incumplimiento hidraulico que de verdad lo descarta.
    if all(v.cumple for v in hechas):
        try:
            hechas.extend(fase_8_estructural(punto=punto, material=material,
                                             seccion=seccion))
        except ErrorProyecto as exc:
            exc.verificaciones_completadas = tuple(hechas)
            # El escalon CUMPLE toda la tabla y lo unico que lo detiene es
            # lo que la Fase 8 no pudo evaluar: MD lo necesita para no
            # llamar «no factible» a un punto al que solo le falta un dato
            # (`MD.ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`).
            exc.escalon_cumple_lo_demas = True
            raise
    return tuple(hechas)
