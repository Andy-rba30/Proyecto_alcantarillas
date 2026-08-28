"""
Las tablas normativas, transcritas COMPLETAS.

QUE ES «COMPLETA» AQUI. Todas las columnas que la fuente imprime, todas sus
filas, todas sus notas al pie, todos sus modificadores y el texto que las
introduce. Que el calculo consuma una fila de tres no poda la transcripcion:
lo declara `uso`, y esa es la diferencia entre una tabla completa de uso
parcial y una tabla podada (§4 del diseño). Una tabla podada no deja ver de
que se eligio una fila.

LOS TRES EJES DE «PARCIAL», que aqui se ven en acto:

  A · `alcance`   que parte de la tabla IMPRESA esta en el registro.
                  `Acotada` exige razon y donde leer lo que falta. ES un
                  defecto si la razon falta.
  B · `uso`       que parte de lo transcrito CONSUME el calculo.
                  NUNCA es un defecto: es informacion. `NoUsada` exige
                  `por_que_no`; `PendienteDeCondicion` bloquea.
  C · `lagunas`   que parte del dominio deja sin cubrir LA FUENTE MISMA.
                  Tampoco es un defecto: es un hecho del documento.

LOS LITERALES VAN CON SUS TILDES Y CON SUS ERRATAS (T21). Es la unica zona
del repositorio donde esa regla manda sobre la costumbre de escribir sin
tildes: un `Verbatim` de-acentuado no se puede volver a encontrar en el PDF.
"""

from __future__ import annotations

from typing import Dict

from .esquema import (
    Acotada,
    CeldaSinValor,
    ColumnaDeTabla,
    CondicionAplicacion,
    ConjuntoDeMaximos,
    CorrespondenciaDeTablas,
    Efecto,
    FilaDeTabla,
    Integra,
    Laguna,
    Modificador,
    NoUsada,
    NotaAlPie,
    OrdenDeAplicacion,
    PendienteDeCondicion,
    PorCriterio,
    PorDatoDeSitio,
    QuePasaFuera,
    TablaNormativa,
    TramoDeModificador,
    Usada,
    Verbatim,
)
from . import citas as _c

_TODAS = []


def _tabla(**kw) -> TablaNormativa:
    t = TablaNormativa(**kw)
    _TODAS.append(t)
    return t


# ===========================================================================
# Manual de Hidrologia — Tabla Nº 02, riesgo admisible
# ===========================================================================
# INTEGRA: seis filas, ni una mas. Confirmado sobre la pagina renderizada (el
# recuadro cierra tras «Defensas Ribereñas»).
#
# SOBRE LAS «CUATRO NOTAS». La pagina imprime DOS marcadores -- (*) y (**) --
# y ocho renglones bajo ellos; los dos ultimos («Se tendrá en cuenta…» y «El
# Propietario…») no llevan marcador propio y quedan sangrados bajo el bloque
# (**). Agruparlos en cuatro es del proyecto; el contenido es literal. Aqui se
# transcriben con la marca que la pagina les da, y los dos sin marca la llevan
# vacia -- que es exactamente lo que la fuente hace.
T02 = _tabla(
    id="MC_HHD.T02",
    cita_id="MC_HHD.3.6",
    titulo_literal=("TABLA Nº 02: VALORES  MAXIMOS RECOMENDADOS DE RIESGO "
                    "ADMISIBLE DE OBRAS DE DRENAJE"),
    texto_previo=Verbatim(
        texto=("De acuerdo a los valores presentados en la Tabla Nº 01 se "
               "recomienda utilizar como máximo, los siguientes valores de "
               "riesgo admisible de obras  de drenaje:"),
        pagina_pdf=28),
    columnas=(
        ColumnaDeTabla(id="obra", etiqueta_literal="TIPO DE OBRA", unidad="",
                       uso=Usada(por=("M1.clasificacion",))),
        ColumnaDeTabla(id="riesgo",
                       etiqueta_literal="RIESGO ADMISIBLE (**) ( %)",
                       unidad="%", uso=Usada(por=("M1.periodo_de_retorno",))),
        # La vida util NO es una columna impresa: la fuente la pone en la nota
        # (**). Se transcribe como columna derivada de la nota y se dice que
        # lo es, porque el calculo la necesita fila a fila y buscar «n = 25»
        # como celda en el PDF no la encontraria.
        ColumnaDeTabla(id="vida_util_anios",
                       etiqueta_literal="(**) Vida Útil considerado (n)",
                       unidad="años",
                       uso=Usada(por=("M1.periodo_de_retorno",))),
    ),
    filas=(
        FilaDeTabla(id="MC_HHD.T02#puentes", etiqueta_literal="Puentes (*)",
                    valores={"obra": "Puentes (*)", "riesgo": 25,
                             "vida_util_anios": 40},
                    llamadas_a_nota=("(*)", "(**)"),
                    uso=NoUsada(por_que_no=("este proyecto dimensiona "
                                            "alcantarillas; una luz >= 6.0 m "
                                            "sale del alcance por el num. "
                                            "4.1.1.5.1"))),
        FilaDeTabla(id="MC_HHD.T02#quebrada_importante",
                    etiqueta_literal=("Alcantarillas de paso de quebradas "
                                      "importantes y badenes"),
                    valores={"obra": ("Alcantarillas de paso de quebradas "
                                      "importantes y badenes"),
                             "riesgo": 30, "vida_util_anios": 25},
                    llamadas_a_nota=("(**)",),
                    uso=Usada(por=("M1.periodo_de_retorno",))),
        FilaDeTabla(id="MC_HHD.T02#quebrada_menor",
                    etiqueta_literal=("Alcantarillas de paso quebradas "
                                      "menores y descarga de agua de cunetas"),
                    valores={"obra": ("Alcantarillas de paso quebradas "
                                      "menores y descarga de agua de cunetas"),
                             "riesgo": 35, "vida_util_anios": 15},
                    llamadas_a_nota=("(**)",),
                    uso=Usada(por=("M1.periodo_de_retorno",))),
        FilaDeTabla(id="MC_HHD.T02#drenaje_plataforma",
                    etiqueta_literal="Drenaje de la plataforma (a nivel longitudinal)",
                    valores={"obra": "Drenaje de la plataforma (a nivel longitudinal)",
                             "riesgo": 40, "vida_util_anios": 15},
                    llamadas_a_nota=("(**)",),
                    uso=NoUsada(por_que_no=("la Fase 2 dimensiona el conducto "
                                            "del cruce, no el drenaje "
                                            "longitudinal de la plataforma. "
                                            "Se transcribe porque es lo que "
                                            "deja ver que la alcantarilla de "
                                            "cuneta NO usa esta fila sino la "
                                            "de quebrada menor"))),
        FilaDeTabla(id="MC_HHD.T02#subdrenes", etiqueta_literal="Subdrenes",
                    valores={"obra": "Subdrenes", "riesgo": 40,
                             "vida_util_anios": 15},
                    llamadas_a_nota=("(**)",),
                    uso=NoUsada(por_que_no="ninguna fase dimensiona subdrenes")),
        FilaDeTabla(id="MC_HHD.T02#defensas_riberenas",
                    etiqueta_literal="Defensas Ribereñas",
                    valores={"obra": "Defensas Ribereñas", "riesgo": 25,
                             "vida_util_anios": 40},
                    llamadas_a_nota=("(**)",),
                    uso=NoUsada(por_que_no="ninguna fase dimensiona defensas ribereñas")),
    ),
    notas_al_pie=(
        NotaAlPie(marca="(*)", texto=Verbatim(
            texto=("(*)   - Para obtención de la luz y nivel de aguas máximas "
                   "extraordinarias. - Se recomienda un período de retorno T "
                   "de 500 años para el cálculo de socavación."),
            pagina_pdf=28)),
        NotaAlPie(marca="(**)", texto=Verbatim(
            texto=("(**) - Vida Útil considerado (n) • Puentes y Defensas "
                   "Ribereñas n= 40 años. •  Alcantarillas de quebradas "
                   "importantes n= 25 años. •  Alcantarillas de quebradas "
                   "menores n= 15 años. • Drenaje de plataforma y Sub-drenes "
                   "n= 15 años."),
            pagina_pdf=28)),
        NotaAlPie(marca="", texto=Verbatim(
            texto=("Se tendrá en cuenta,  la importancia y la vida útil de la "
                   "obra a diseñarse."),
            pagina_pdf=28)),
        NotaAlPie(marca="", texto=Verbatim(
            texto=("El Propietario de una Obra es el que define el riesgo "
                   "admisible de falla y la vida útil de las obras."),
            pagina_pdf=28)),
    ),
    fuente_declarada_por_la_tabla="",   # la Tabla Nº 02 NO declara fuente; el
                                        # «Fuente: MONSALVE, 1999.» de la
                                        # misma pagina es de la Tabla Nº 01
    alcance=Integra(),
    vistas_de_calculo=("TABLA_02_FILAS", "RIESGO_ADMISIBLE"),
)


# ===========================================================================
# Manual de Hidrologia — Tabla Nº 09, rugosidad de Manning
# ===========================================================================
# ACOTADA al grupo A, con su razon y con donde leer lo que falta.
#
# LA ERRATA DE COMPOSICION DEL BLOQUE A.2, hallada al verificar en S12 y que
# el repositorio venia corrigiendo EN SILENCIO. En la pagina impresa 75, la
# columna de valores del bloque A.2 esta desplazada UN RENGLON HACIA ARRIBA
# respecto de sus rotulos: `0.010 0.011 0.013` se imprime a la altura de
# «a. Concreto» -- que es un rotulo de categoria, sin valores propios, igual
# que «b. Acero» y «c. Metal corrugado» del bloque A.1, que SI quedan en
# blanco -- y `0.010 0.012 0.014` a la altura de «b. Madera».
#
# QUE LO DEMUESTRA, y no es preferencia de lectura:
#   1. Leida al pie de la letra, la pagina deja SIN VALOR a «Tubo con moldaje
#      madera en bruto» y a «c. Albañilería de piedra.», que son hojas de la
#      jerarquia y no rotulos: una tabla no deja sin numero a sus hojas.
#   2. Corriendo un renglon, las diez ternas encajan una a una con las diez
#      hojas, sin sobrar ni faltar.
#   3. Y coinciden fila por fila con la fuente que la propia tabla declara
#      -- «Hidráulica de Canales Abiertos, Ven Te Chow, 1983» --: culvert
#      straight and free of debris 0.010/0.011/0.013, with bends 0.011/0.013/
#      0.014, finished 0.011/0.012/0.014, sewer with manholes 0.013/0.015/
#      0.017, unfinished steel form 0.012/0.013/0.014, smooth wood form
#      0.012/0.014/0.016, rough plank form 0.015/0.017/0.020, wood stave
#      0.010/0.012/0.014, laminated treated 0.015/0.017/0.020.
#   4. El bloque A.1 de la MISMA tabla no tiene el desplazamiento, de modo
#      que es un descuido de composicion de A.2 y no la forma de la tabla.
#
# Se transcribe la lectura corregida Y se declara la errata: transcribir la
# alineacion impresa meteria en el calculo un n que la fuente de la tabla no
# asigna a esa fila, y corregirla sin decirlo es lo que este cluster
# persigue. La declaracion vive en `erratas` y en la nota de cada fila.
T09 = _tabla(
    id="MC_HHD.T09",
    cita_id="MC_HHD.4.1.1.3.6#T09",
    titulo_literal=("TABLA  Nº  09:  Valores del Coeficiente de Rugosidad de "
                    "Manning (n)"),
    texto_previo=Verbatim(
        texto="n : Coeficiente de Manning (Ver Tabla Nº 09)",
        pagina_pdf=77),
    columnas=(
        ColumnaDeTabla(id="tipo_de_canal", etiqueta_literal="TIPO DE CANAL",
                       unidad="", uso=Usada(por=("M2.material",))),
        ColumnaDeTabla(id="minimo", etiqueta_literal="MÍNIMO", unidad="",
                       uso=Usada(por=("M3.resolver_manning",))),
        # LA COLUMNA DEL CENTRO. Transcrita, no consumida, con su razon.
        # NO es PendienteDeCondicion: no falta ningun dato, la decision esta
        # tomada y razonada.
        ColumnaDeTabla(id="normal", etiqueta_literal="NORMAL", unidad="",
                       uso=NoUsada(por_que_no=(
                           "la regla de doble n (Sec. 4.1 de la hoja de ruta) "
                           "no pide el valor corriente sino los dos EXTREMOS "
                           "-- n maximo para capacidad y tirante, n minimo "
                           "para velocidad maxima y socavacion --, de modo "
                           "que cada verificacion se resuelve con el extremo "
                           "que la deja del lado seguro. El valor NORMAL "
                           "entraria en un calculo de un solo n, que es justo "
                           "lo que la regla prohibe"))),
        ColumnaDeTabla(id="maximo", etiqueta_literal="MÁXIMO", unidad="",
                       uso=Usada(por=("M3.resolver_manning",))),
    ),
    filas=(
        FilaDeTabla(
            id="MC_HHD.T09#metal_corrugado_subdren",
            jerarquia=("A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.1. METÁLICOS", "c. Metal corrugado"),
            etiqueta_literal="sub - dren",
            valores={"minimo": 0.017, "normal": 0.019, "maximo": 0.021},
            uso=NoUsada(por_que_no=("una alcantarilla es dren para aguas "
                                    "lluvias, no sub-dren "
                                    "(M2._MANNING_CLAVE)"))),
        FilaDeTabla(
            id="MC_HHD.T09#metal_corrugado_dren_aguas_lluvias",
            jerarquia=("A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.1. METÁLICOS", "c. Metal corrugado"),
            etiqueta_literal="dren para aguas lluvias",
            valores={"minimo": 0.021, "normal": 0.024, "maximo": 0.030},
            uso=Usada(por=("M2._MANNING_CLAVE['tmc']",))),
        FilaDeTabla(
            id="MC_HHD.T09#concreto_tubo_recto",
            jerarquia=("A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.2 NO METÁLICOS", "a. Concreto"),
            etiqueta_literal="tubo recto y libre de basuras",
            valores={"minimo": 0.010, "normal": 0.011, "maximo": 0.013},
            uso=Usada(por=("M2._MANNING_CLAVE['concreto']",
                           "criterios_adoptados['n_manning_hdpe']"))),
        FilaDeTabla(
            id="MC_HHD.T09#madera_duelas",
            jerarquia=("A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.2 NO METÁLICOS", "b. Madera"),
            etiqueta_literal="duelas",
            valores={"minimo": 0.010, "normal": 0.012, "maximo": 0.014},
            uso=NoUsada(por_que_no=("el catalogo de conductos de la Sec. 3.2 "
                                    "no ofrece madera"))),
    ),
    fuente_declarada_por_la_tabla=("Hidráulica de Canales Abiertos, Ven Te "
                                   "Chow, 1983."),
    erratas=("DIS-MCHHD-T09-A2-DESPLAZADA",),
    afirmaciones_negativas=(_c.SIN_HDPE_T09,),
    alcance=Acotada(
        razon=("el grupo A es el unico de la tabla que describe una "
               "alcantarilla; los grupos B (canales revestidos o "
               "desarmables), C (excavado o dragado) y D (corrientes "
               "naturales) describen el CAUCE, no el conducto, y ningun "
               "modulo dimensiona un cauce. Dentro del grupo A se transcriben "
               "las cuatro subfilas que el catalogo de la Sec. 3.2 puede "
               "alcanzar"),
        que_queda_fuera=("del grupo A: «a. Bronce Polido», «b. Acero» "
                         "(soldado, con remaches) y las seis subfilas "
                         "restantes de «a. Concreto» y «b. Madera», mas "
                         "«c. Albañilería de piedra.». Fuera del grupo A: "
                         "«B.CANALES REVESTIDOS», «C. EXCAVADO» y "
                         "«D. CORRIENTES NATURALES»"),
        donde_leerlo=("MC_HHD, num. 4.1.1.3.6, Tabla Nº 09: los grupos A, B y "
                      "C en la pag. impresa 75 (PDF 78) y el grupo D con la "
                      "linea de Fuente en la 76 (PDF 79)")),
    vistas_de_calculo=("TABLA_09_FILAS", "MANNING"),
)


# ===========================================================================
# Manual de Hidrologia — Tabla Nº 10, velocidades maximas admisibles
# ===========================================================================
# INTEGRA y de uso PARCIAL, y no hay en el objeto nada que se parezca a un
# defecto: la ventana imprime «Tabla completa · el calculo usa 1 de 3 filas»
# con la razon a mano.
T10 = _tabla(
    id="MC_HHD.T10",
    cita_id="MC_HHD.4.1.1.3.6#T10",
    titulo_literal=("TABLA  Nº  10:    Velocidades máximas  admisibles (m/s)  "
                    "en conductos revestidos"),
    texto_previo=Verbatim(
        texto=("Se debe tener en cuenta la velocidad, parámetro que es "
               "necesario verificar de tal manera que se encuentre dentro de "
               "un rango, cuyos límites se describen a continuación."),
        pagina_pdf=79),
    columnas=(
        ColumnaDeTabla(id="revestimiento",
                       etiqueta_literal="TIPO DE REVESTIMIENTO", unidad="",
                       uso=Usada(por=("M2.material",))),
        ColumnaDeTabla(id="velocidad", etiqueta_literal="VELOCIDAD (M/S)",
                       unidad="m/s",
                       uso=Usada(por=("M5.v3_velocidad_maxima",))),
    ),
    filas=(
        FilaDeTabla(
            id="MC_HHD.T10#concreto", etiqueta_literal="Concreto",
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(3.0, 6.0), unidad="m/s",
                cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=Usada(por=("M5.v3_velocidad_maxima",))),
        FilaDeTabla(
            id="MC_HHD.T10#ladrillo_c_concreto",
            etiqueta_literal="Ladrillo con concreto",
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(2.5, 3.5), unidad="m/s",
                cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=NoUsada(por_que_no=("el catalogo de conductos de la Sec. 3.2 "
                                    "no ofrece ladrillo con concreto"))),
        FilaDeTabla(
            # UN solo valor. No es media fila ni un par al que le falte el
            # otro numero: es lo que la tabla imprime (NOR-HID-07). La tupla
            # de un elemento es la forma normal, no un caso especial.
            id="MC_HHD.T10#mamposteria_piedra",
            etiqueta_literal="Mampostería de piedra y concreto",
            valores={"velocidad": ConjuntoDeMaximos(
                valores=(2.0,), unidad="m/s",
                cita_id="MC_HHD.4.1.1.3.6#T10",
                que_pasa_fuera=QuePasaFuera.INCUMPLE_LA_NORMA)},
            uso=NoUsada(por_que_no=("el catalogo de conductos de la Sec. 3.2 "
                                    "no ofrece mamposteria de piedra"))),
    ),
    fuente_declarada_por_la_tabla="HCANALES, Máximo Villon B.",
    afirmaciones_negativas=(_c.SIN_TMC_NI_HDPE_T10,),
    interpretacion=_c.INTERPRETACION_T10,
    alcance=Integra(),
    vistas_de_calculo=("TABLA_10_FILAS", "V_MAX"),
)


# ===========================================================================
# Manual de Suelos — Cuadro 4.1, numero de calicatas
# ===========================================================================
# EL HALLAZGO DE C12, hecho estructura. El repositorio afirmaba que el Cuadro
# «da el 6 como alternativa SIN DECIR CUANDO APLICA CADA UNA» y que la fila
# dual dice «4 (o 6)». Verificado contra el PDF: las dos proposiciones son
# falsas. El Cuadro condiciona por CARRILES POR SENTIDO, con tres viñetas
# explicitas en cada una de las dos filas multicarril, y la cadena «4 (o 6)»
# no aparece en ninguna celda.
#
# Afirmar que la fuente calla donde habla es la forma INVERSA del defecto que
# este cluster persigue -- en vez de citar lo que no dice, negar lo que si
# dice --, y el resultado es igual de invisible: un vacio inventado que
# convierte en [A] lo que es [N].
#
# La celda no es un escalar: es una tabla de tres entradas dentro de la celda.
# Se modela como columna por numero de carriles por sentido, que es la
# variable que la propia celda nombra.
# La clase de via del corredor no esta cerrada: depende del IMDA del estudio
# de demanda, que este expediente todavia no tiene. La fila del Cuadro no se
# puede elegir sin ella, y elegirla a ojo seria decidir cuantas calicatas
# exige la norma.
_COND_CLASE_VIA = CondicionAplicacion(
    id="COND-CLASE-DE-VIA",
    texto=Verbatim(
        texto=("Autopistas: carreteras de IMDA mayor de 6000 veh/día, de "
               "calzadas separadas, cada una con dos o más carriles"),
        pagina_pdf=29),
    cita_id="MS.4.2#C41",
    resuelve=PorDatoDeSitio(clave="clase_de_via"),
)

_COND_CARRILES = CondicionAplicacion(
    id="COND-CARRILES-POR-SENTIDO",
    texto=Verbatim(
        texto=("Calzada 2 carriles por sentido: 4 calicatas x km x sentido / "
               "Calzada 3 carriles por sentido: 4 calicatas x km x sentido / "
               "Calzada 4 carriles por sentido: 6 calicatas x km x sentido"),
        pagina_pdf=29),
    cita_id="MS.4.2#C41",
    resuelve=PorDatoDeSitio(clave="carriles_por_sentido"),
    # D4: por defecto BLOQUEA, y aqui debe. El dato existe en el mundo -- lo
    # fija el diseño geometrico de la via --; lo que falta es traerlo.
)

C41 = _tabla(
    id="MS.C41",
    cita_id="MS.4.2#C41",
    titulo_literal="Cuadro 4.1 Número de Calicatas para Exploración de Suelos",
    texto_previo=Verbatim(
        texto=("el número mínimo de calicatas por kilómetro, estará de "
               "acuerdo al cuadro 4.1."),
        pagina_pdf=29),
    columnas=(
        ColumnaDeTabla(id="tipo_de_carretera",
                       etiqueta_literal="Tipo de Carretera", unidad="",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CLASE-DE-VIA")),
        ColumnaDeTabla(id="profundidad_m", etiqueta_literal="Profundidad (m)",
                       unidad="m",
                       uso=NoUsada(por_que_no=(
                           "gobierna la campaña de campo, no el "
                           "dimensionamiento de la alcantarilla. Se "
                           "transcribe porque NOR-SUE-04 la reclamaba: el "
                           "Cuadro SI fija la profundidad, en columna propia, "
                           "y el repositorio no la recogia"))),
        # La celda de «Número mínimo de Calicatas» es, en las dos filas
        # multicarril, una tabla de TRES entradas por carriles por sentido.
        # Se abre en tres columnas porque esa es la variable que la propia
        # celda nombra; aplastarlas en un escalar es lo que produjo el
        # hallazgo.
        ColumnaDeTabla(id="calicatas_2_carriles_por_sentido",
                       etiqueta_literal="Calzada 2 carriles por sentido",
                       unidad="calicatas x km x sentido",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CARRILES-POR-SENTIDO")),
        ColumnaDeTabla(id="calicatas_3_carriles_por_sentido",
                       etiqueta_literal="Calzada 3 carriles por sentido",
                       unidad="calicatas x km x sentido",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CARRILES-POR-SENTIDO")),
        ColumnaDeTabla(id="calicatas_4_carriles_por_sentido",
                       etiqueta_literal="Calzada 4 carriles por sentido",
                       unidad="calicatas x km x sentido",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CARRILES-POR-SENTIDO")),
        ColumnaDeTabla(id="calicatas_por_km",
                       etiqueta_literal="Número mínimo de Calicatas",
                       unidad="calicatas x km",
                       uso=Usada(por=("MD.densidad_de_calicatas",))),
        ColumnaDeTabla(id="por_sentido",
                       etiqueta_literal="x sentido",
                       unidad="",
                       uso=Usada(por=("MD.densidad_de_calicatas",))),
        ColumnaDeTabla(id="observacion", etiqueta_literal="Observación",
                       unidad="",
                       uso=NoUsada(por_que_no=("es la regla de UBICACION de "
                                               "las calicatas, no de "
                                               "densidad; ninguna fase la "
                                               "evalua"))),
    ),
    filas=(
        FilaDeTabla(
            id="MS.C41#autopista",
            etiqueta_literal=("Autopistas: carreteras de IMDA mayor de 6000 "
                              "veh/día, de calzadas separadas, cada una con "
                              "dos o más carriles"),
            valores={
                "profundidad_m": 1.50,
                "calicatas_2_carriles_por_sentido": 4,
                "calicatas_3_carriles_por_sentido": 4,
                "calicatas_4_carriles_por_sentido": 6,
                "calicatas_por_km": CeldaSinValor.REMITE_A_OTRA_TABLA,
                "por_sentido": True,
                "observacion": ("Las calicatas se  ubicarán longitudinalmente "
                                "y en forma alternada"),
            },
            condiciones=(_COND_CARRILES, _COND_CLASE_VIA),
            uso=PendienteDeCondicion(condicion_id="COND-CARRILES-POR-SENTIDO")),
        FilaDeTabla(
            id="MS.C41#dual",
            etiqueta_literal=("Carreteras Duales o Multicarril: carreteras de "
                              "IMDA entre 6000 y 4001  veh/dia, de calzadas "
                              "separadas, cada una con dos o más carriles"),
            valores={
                "profundidad_m": 1.50,
                "calicatas_2_carriles_por_sentido": 4,
                "calicatas_3_carriles_por_sentido": 4,
                "calicatas_4_carriles_por_sentido": 6,
                "calicatas_por_km": CeldaSinValor.REMITE_A_OTRA_TABLA,
                "por_sentido": True,
                "observacion": ("Las calicatas se  ubicarán longitudinalmente "
                                "y en forma alternada"),
            },
            condiciones=(_COND_CARRILES, _COND_CLASE_VIA),
            uso=PendienteDeCondicion(condicion_id="COND-CARRILES-POR-SENTIDO")),
        FilaDeTabla(
            id="MS.C41#primera_clase",
            etiqueta_literal=("Carreteras de Primera Clase: carreteras con un "
                              "IMDA entre 4000-2001 veh/día, de una calzada "
                              "de dos carriles."),
            valores={"profundidad_m": 1.50, "calicatas_por_km": 4,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=Usada(por=("MD.densidad_de_calicatas",))),
        FilaDeTabla(
            id="MS.C41#segunda_clase",
            etiqueta_literal=("Carreteras de Segunda Clase: carreteras con un "
                              "IMDA entre 2000-401 veh/día, de una calzada de "
                              "dos carriles."),
            valores={"profundidad_m": 1.50, "calicatas_por_km": 3,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=Usada(por=("MD.densidad_de_calicatas",))),
        FilaDeTabla(
            id="MS.C41#tercera_clase",
            etiqueta_literal=("Carreteras de Tercera Clase: carreteras con un "
                              "IMDA entre 400-201 veh/día, de una calzada de "
                              "dos carriles."),
            valores={"profundidad_m": 1.50, "calicatas_por_km": 2,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=Usada(por=("MD.densidad_de_calicatas",))),
        FilaDeTabla(
            id="MS.C41#bajo_volumen",
            etiqueta_literal=("Carreteras de Bajo Volumen de Tránsito: "
                              "carreteras con un IMDA ≤ 200 veh/día, de una "
                              "calzada."),
            # «1 calicata», en singular, tal como lo imprime.
            valores={"profundidad_m": 1.50, "calicatas_por_km": 1,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=Usada(por=("MD.densidad_de_calicatas",))),
    ),
    notas_al_pie=(
        NotaAlPie(marca="Fuente", texto=Verbatim(
            texto=("Fuente:  Elaboración Propia, teniendo en cuenta el Tipo de "
                   "Carretera establecido en la RD 037-2008-MTC/14 y el Manual "
                   "de Ensayo de Materiales del MTC"),
            pagina_pdf=29)),
    ),
    lagunas=(
        Laguna(
            que_no_cubre=("las calzadas de MAS de 4 carriles por sentido: el "
                          "Cuadro tabula 2, 3 y 4 y no dice que hacer con 5 "
                          "o mas"),
            con_que_regla=("ninguna. La fuente no extrapola ni dice que la "
                           "ultima fila se prolongue"),
            quien_lo_cierra=None,
            si_nadie_lo_cierra=Efecto.BLOQUEA),
    ),
    alcance=Integra(),
    vistas_de_calculo=("CALICATAS_POR_KM", "CALICATAS_POR_SENTIDO",
                       "CALICATAS_PROFUNDIDAD_M"),
)


# ===========================================================================
# AASHTO LRFD 9a ed. — las dos tablas de h_eq
# ===========================================================================
# LAS DOS SON BINOMIOS ACOPLADOS, no dos filas de un eje «orientacion». La
# Tabla -1 es de ESTRIBOS perpendiculares al trafico (su variable se llama
# literalmente «Abutment Height») y la -2 de MUROS DE CONTENCION paralelos.
# No hay tabla para «muro perpendicular» ni para «estribo paralelo», y el
# articulado NO contiene ninguna frase que reparta las dos: las cita juntas y
# sin condicionante. Quien reparte son los TITULOS y el comentario C3.11.6.4.
#
# Consecuencia, y es la que matiza el conflicto #4: aplicar la Tabla -1 a un
# cabezal de alcantarilla es ANALOGIA declarada ([N->]), no lectura directa.
#
# LAS UNIDADES SON PIES, y asi se transcriben: es lo que la fuente imprime.
# La conversion a SI vive en la vista de calculo, que es donde CLAUDE.md la
# pone («la conversion a unidades de presentacion ocurre solo en la capa de
# reporte, nunca en el calculo» -- aqui es al reves y por la misma razon: el
# calculo opera en SI y la transcripcion conserva la unidad de la fuente).
T_HEQ_ESTRIBO = _tabla(
    id="AASHTO_LRFD_9.T3.11.6.4-1",
    cita_id="AASHTO_LRFD_9.T3.11.6.4-1",
    titulo_literal=("Table 3.11.6.4-1—Equivalent Height of Soil for Vehicular "
                    "Loading on Abutments Perpendicular to Traffic"),
    columnas=(
        ColumnaDeTabla(id="altura_ft", etiqueta_literal="Abutment Height (ft)",
                       unidad="ft",
                       uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        ColumnaDeTabla(id="h_eq_ft", etiqueta_literal="heq (ft)", unidad="ft",
                       uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
    ),
    filas=(
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-1#5", etiqueta_literal="5.0",
                    valores={"altura_ft": 5.0, "h_eq_ft": 4.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-1#10", etiqueta_literal="10.0",
                    valores={"altura_ft": 10.0, "h_eq_ft": 3.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-1#20", etiqueta_literal="≥20.0",
                    valores={"altura_ft": 20.0, "h_eq_ft": 2.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
    ),
    notas_al_pie=(),      # la tabla NO imprime ninguna; verificado en imagen
    lagunas=(
        Laguna(
            que_no_cubre=("los muros de MENOS de 5.0 ft (1.524 m): la tabla "
                          "arranca en 5.0 y la interpolacion que la fuente "
                          "exige es «for intermediate wall heights», o sea "
                          "ENTRE filas. Por debajo de 5.0 no hay fila con que "
                          "interpolar y extrapolar no lo autoriza nadie"),
            con_que_regla=("el proyecto adopta el h_eq de la primera fila "
                           "(4.0 ft) para toda altura menor, que es el lado "
                           "conservador porque h_eq DECRECE con la altura"),
            quien_lo_cierra="criterios_adoptados['h_eq_bajo_altura_tabulada']",
            si_nadie_lo_cierra=Efecto.BLOQUEA),
    ),
    alcance=Integra(),
    vistas_de_calculo=("H_EQ_ESTRIBO_PERPENDICULAR_FT",),
)

T_HEQ_MURO = _tabla(
    id="AASHTO_LRFD_9.T3.11.6.4-2",
    cita_id="AASHTO_LRFD_9.T3.11.6.4-2",
    titulo_literal=("Table 3.11.6.4-2—Equivalent Height of Soil for Vehicular "
                    "Loading on Retaining Walls Parallel to Traffic"),
    encabezados_superiores=("heq (ft) Distance from wall backface to edge of "
                            "traffic",),
    columnas=(
        ColumnaDeTabla(id="altura_ft",
                       etiqueta_literal="Retaining Wall Height (ft)",
                       unidad="ft",
                       uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        ColumnaDeTabla(id="borde_0_0_ft", etiqueta_literal="0.0 ft",
                       unidad="ft",
                       uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        ColumnaDeTabla(id="borde_1_0_ft_o_mas",
                       etiqueta_literal="1.0 ft or Further", unidad="ft",
                       uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
    ),
    filas=(
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-2#5", etiqueta_literal="5.0",
                    valores={"altura_ft": 5.0, "borde_0_0_ft": 5.0,
                             "borde_1_0_ft_o_mas": 2.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-2#10", etiqueta_literal="10.0",
                    valores={"altura_ft": 10.0, "borde_0_0_ft": 3.5,
                             "borde_1_0_ft_o_mas": 2.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
        FilaDeTabla(id="AASHTO_LRFD_9.T3.11.6.4-2#20", etiqueta_literal="≥20.0",
                    valores={"altura_ft": 20.0, "borde_0_0_ft": 2.0,
                             "borde_1_0_ft_o_mas": 2.0},
                    uso=Usada(por=("M9.h_eq_sobrecarga_trasdos",))),
    ),
    notas_al_pie=(),      # ninguna; verificado en imagen
    lagunas=(
        Laguna(
            que_no_cubre=("la banda 0.0 ft < distancia < 1.0 ft. La fuente "
                          "manda interpolar «for intermediate wall HEIGHTS» "
                          "-- entre filas -- y NO autoriza interpolar entre "
                          "estas dos columnas"),
            con_que_regla=("el proyecto lee la columna «0.0 ft», que es el "
                           "lado conservador, para toda distancia menor de "
                           "1.0 ft"),
            quien_lo_cierra="criterios_adoptados['h_eq_banda_intermedia_borde']",
            si_nadie_lo_cierra=Efecto.BLOQUEA),
        Laguna(
            que_no_cubre="los muros de menos de 5.0 ft (1.524 m)",
            con_que_regla=("el h_eq de la primera fila para toda altura "
                           "menor: h_eq decrece con la altura y por debajo de "
                           "5.0 ft no hay fila con que interpolar"),
            quien_lo_cierra="criterios_adoptados['h_eq_bajo_altura_tabulada']",
            si_nadie_lo_cierra=Efecto.BLOQUEA),
    ),
    alcance=Integra(),
    vistas_de_calculo=("H_EQ_MURO_PARALELO_FT",),
)


# ===========================================================================
# La correspondencia entre el piso peruano y la tabla de AASHTO
# ===========================================================================
CORRESPONDENCIAS: Dict[str, CorrespondenciaDeTablas] = {}

TABLAS: Dict[str, TablaNormativa] = {t.id: t for t in _TODAS}
