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
                       uso=Usada(por=("M1.Clasificacion",))),
        ColumnaDeTabla(id="riesgo",
                       etiqueta_literal="RIESGO ADMISIBLE (**) ( %)",
                       unidad="%", uso=Usada(por=("M1.periodo_retorno_de",))),
        # La vida util NO es una columna impresa: la fuente la pone en la nota
        # (**). Se transcribe como columna derivada de la nota y se dice que
        # lo es, porque el calculo la necesita fila a fila y buscar «n = 25»
        # como celda en el PDF no la encontraria.
        ColumnaDeTabla(id="vida_util_anios",
                       etiqueta_literal="(**) Vida Útil considerado (n)",
                       unidad="años",
                       uso=Usada(por=("M1.periodo_retorno_de",))),
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
                    uso=Usada(por=("M1.periodo_retorno_de",))),
        FilaDeTabla(id="MC_HHD.T02#quebrada_menor",
                    etiqueta_literal=("Alcantarillas de paso quebradas "
                                      "menores y descarga de agua de cunetas"),
                    valores={"obra": ("Alcantarillas de paso quebradas "
                                      "menores y descarga de agua de cunetas"),
                             "riesgo": 35, "vida_util_anios": 15},
                    llamadas_a_nota=("(**)",),
                    uso=Usada(por=("M1.periodo_retorno_de",))),
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
                       unidad="", uso=Usada(por=("M2.materiales_candidatos",))),
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
            uso=Usada(por=("M2._MANNING_CLAVE",))),
        FilaDeTabla(
            id="MC_HHD.T09#concreto_tubo_recto",
            jerarquia=("A.CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO",
                       "A.2 NO METÁLICOS", "a. Concreto"),
            etiqueta_literal="tubo recto y libre de basuras",
            valores={"minimo": 0.010, "normal": 0.011, "maximo": 0.013},
            uso=Usada(por=("M2._MANNING_CLAVE",
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
                       uso=Usada(por=("M2.materiales_candidatos",))),
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
# EL CONSUMIDOR QUE NO EXISTE, declarado como lo que es. Estas filas y estas
# dos columnas decian `Usada(por=("MD.densidad_de_calicatas",))`, y ese simbolo
# NO EXISTE en ningun modulo: es exactamente la misma clase de defecto que el
# cluster persigue -- una afirmacion comprobable que nadie comprobaba --,
# cometida al escribir el registro. `CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`
# estan en `constantes_normativas.CONSTANTES_DE_REFERENCIA`, que es la lista de
# lo que el proyecto declara SIN consumidor de calculo, y ahi es donde la
# transcripcion tiene que apuntar. El test T24 impide que vuelva a pasar.
_REFERENCIA_C41 = NoUsada(por_que_no=(
    "gobierna la CAMPAÑA DE CAMPO -- cuantas calicatas hay que abrir --, no "
    "el dimensionamiento de la alcantarilla. Llega al expediente como "
    "`CALICATAS_POR_KM` y `CALICATAS_POR_SENTIDO`, las dos declaradas en "
    "`constantes_normativas.CONSTANTES_DE_REFERENCIA`: se transcriben para "
    "que la memoria pueda imprimirlas y para que la cita sea verificable, no "
    "porque entren en formula"))

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
                       uso=_REFERENCIA_C41),
        ColumnaDeTabla(id="por_sentido",
                       etiqueta_literal="x sentido",
                       unidad="",
                       uso=_REFERENCIA_C41),
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
            uso=_REFERENCIA_C41),
        FilaDeTabla(
            id="MS.C41#segunda_clase",
            etiqueta_literal=("Carreteras de Segunda Clase: carreteras con un "
                              "IMDA entre 2000-401 veh/día, de una calzada de "
                              "dos carriles."),
            valores={"profundidad_m": 1.50, "calicatas_por_km": 3,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=_REFERENCIA_C41),
        FilaDeTabla(
            id="MS.C41#tercera_clase",
            etiqueta_literal=("Carreteras de Tercera Clase: carreteras con un "
                              "IMDA entre 400-201 veh/día, de una calzada de "
                              "dos carriles."),
            valores={"profundidad_m": 1.50, "calicatas_por_km": 2,
                     "por_sentido": False,
                     "observacion": ("Las calicatas se  ubicarán "
                                     "longitudinalmente y en forma alternada")},
            uso=_REFERENCIA_C41),
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
            uso=_REFERENCIA_C41),
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
            # NO LA CIERRA NADIE, Y ESO SE ESCRIBE. `quien_lo_cierra=None` era
            # la unica laguna del registro sin cerrador nombrado, y «None» no
            # distingue «nadie la cierra» de «se me olvido decirlo». Aqui el
            # que la cierra ES el dato de sitio: hasta que `carriles_por_sentido`
            # se declare, la lectura de la columna se detiene, y si el dato
            # llegase con 5 o mas la tabla no tiene fila y hay que ir a la
            # fuente, no extrapolar.
            quien_lo_cierra="datos_sitio['carriles_por_sentido']",
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
# E.060 — Tabla 4.2, requisitos para condiciones especiales de exposicion
# ===========================================================================
# LAS DOS TABLAS DE DURABILIDAD SE LEEN JUNTAS, y esa es la primera cosa que
# faltaba (NOR-E060-05, NOR-E060-06). La 4.2 y la 4.4 llevan las dos, al pie,
# la MISMA nota marcada con asterisco desde sus columnas de a/c y de f'c. No
# es un adorno de imprenta: es la regla que decide que se especifica cuando el
# sitio tiene sulfatos Y cloruros a la vez, que es precisamente el caso de un
# corredor costero con freatico somero.
_NOTA_COMUN_4_2_4_4 = NotaAlPie(marca="*", texto=Verbatim(
    texto=("Cuando se utilicen las Tablas 4.2 y 4.4 simultáneamente, se debe "
           "utilizar la menor relación máxima agua-material cementante "
           "aplicable y el mayor f’c mínimo."),
    pagina_pdf=37))

T_E060_4_2 = _tabla(
    id="E060.T4.2",
    cita_id="E060.T4.2",
    titulo_literal="TABLA 4.2 REQUISITOS PARA CONDICIONES ESPECIALES DE EXPOSICIÓN",
    texto_previo=Verbatim(
        texto=("Los concretos expuestos a las condiciones especiales de "
               "exposición señaladas en la Tabla 4.2 deben cumplir con las "
               "relaciones máximas agua-material cementante y con la "
               "resistencia mínima f’c señaladas en ésta."),
        pagina_pdf=37),
    columnas=(
        ColumnaDeTabla(id="condicion",
                       etiqueta_literal="Condición de la exposición",
                       unidad="",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-EXPOSICION-QUIMICA-EMS")),
        ColumnaDeTabla(id="a_c_max",
                       etiqueta_literal=("Relación máxima agua - material "
                                         "cementante (en peso) para concretos "
                                         "de peso normal *"),
                       unidad="",
                       uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        ColumnaDeTabla(id="fc_min_MPa",
                       etiqueta_literal=("f’c mínimo (MPa) para concretos de "
                                         "peso normal o con agregados "
                                         "ligeros*"),
                       unidad="MPa",
                       uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
    ),
    filas=(
        FilaDeTabla(
            id="E060.T4.2#baja_permeabilidad",
            etiqueta_literal=("Concreto que se pretende tenga baja "
                              "permeabilidad en exposición al agua."),
            valores={"a_c_max": 0.50, "fc_min_MPa": 28},
            llamadas_a_nota=("*",),
            uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        FilaDeTabla(
            id="E060.T4.2#congelamiento_deshielo",
            etiqueta_literal=("Concreto expuesto a ciclos de congelamiento y "
                              "deshielo en condición húmeda o a productos "
                              "químicos descongelantes."),
            valores={"a_c_max": 0.45, "fc_min_MPa": 31},
            llamadas_a_nota=("*",),
            uso=NoUsada(por_que_no=("La Union, Piura, esta a nivel del mar en "
                                    "costa desertica: no hay ciclos de "
                                    "congelamiento y deshielo ni se emplean "
                                    "productos descongelantes"))),
        FilaDeTabla(
            id="E060.T4.2#cloruros",
            etiqueta_literal=("Para proteger de la corrosión el refuerzo de "
                              "acero cuando el concreto está expuesto a "
                              "cloruros provenientes de productos "
                              "descongelantes, sal, agua salobre, agua de mar "
                              "o a salpicaduras del mismo origen."),
            valores={"a_c_max": 0.40, "fc_min_MPa": 35},
            llamadas_a_nota=("*",),
            uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
    ),
    notas_al_pie=(_NOTA_COMUN_4_2_4_4,),
    alcance=Integra(),
    vistas_de_calculo=("EXPOSICION_ESPECIAL",),
)


# ===========================================================================
# E.060 — Tabla 4.4, concreto expuesto a soluciones de sulfatos
# ===========================================================================
# DOS ESCALAS PARALELAS, no una: la tabla clasifica por sulfato soluble en el
# SUELO (porcentaje en peso) o por sulfato en el AGUA (ppm). La transcripcion
# anterior llevaba solo la del suelo, de modo que un expediente con analisis
# de agua -- lo esperable con ANA de por medio -- no podia clasificarse.
T_E060_4_4 = _tabla(
    id="E060.T4.4",
    cita_id="E060.T4.4",
    titulo_literal=("TABLA 4.4 REQUISITOS PARA CONCRETO EXPUESTO A SOLUCIONES "
                    "DE SULFATOS"),
    columnas=(
        ColumnaDeTabla(id="exposicion",
                       etiqueta_literal="Exposición a sulfatos", unidad="",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-EXPOSICION-QUIMICA-EMS")),
        ColumnaDeTabla(id="so4_suelo_pct",
                       etiqueta_literal=("Sulfato soluble en agua (SO4) "
                                         "presente en el suelo, porcentaje en "
                                         "peso"),
                       unidad="% en peso",
                       uso=Usada(por=("M9.clase_exposicion_sulfatos",))),
        ColumnaDeTabla(id="so4_agua_ppm",
                       etiqueta_literal="Sulfato (SO4) en el agua, ppm",
                       unidad="ppm",
                       uso=Usada(por=("M9.clase_exposicion_sulfatos",))),
        ColumnaDeTabla(id="cementos", etiqueta_literal="Tipo de Cemento",
                       unidad="",
                       uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        ColumnaDeTabla(id="a_c_max",
                       etiqueta_literal=("Relación máxima agua - material "
                                         "cementante (en peso) para concretos "
                                         "de peso normal*"),
                       unidad="",
                       uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        ColumnaDeTabla(id="fc_min_MPa",
                       etiqueta_literal=("f’c mínimo (MPa) para concretos de "
                                         "peso normal y ligero*"),
                       unidad="MPa",
                       uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
    ),
    filas=(
        FilaDeTabla(
            id="E060.T4.4#insignificante", etiqueta_literal="Insignificante",
            valores={"so4_suelo_pct": "0,0 ≤ SO4 < 0,1",
                     "so4_agua_ppm": "0 ≤ SO4< 150",
                     "cementos": CeldaSinValor.NO_IMPRESO,
                     "a_c_max": CeldaSinValor.NO_IMPRESO,
                     "fc_min_MPa": CeldaSinValor.NO_IMPRESO},
            uso=Usada(por=("M9.clase_exposicion_sulfatos",))),
        FilaDeTabla(
            id="E060.T4.4#moderada", etiqueta_literal="Moderada**",
            valores={"so4_suelo_pct": "0,1 ≤ SO4 < 0,2",
                     "so4_agua_ppm": "150 ≤ SO4 < 1500",
                     "cementos": ("II, IP(MS), IS(MS), P(MS), I(PM)(MS), "
                                  "I(SM)(MS)"),
                     "a_c_max": 0.50, "fc_min_MPa": 28},
            llamadas_a_nota=("**", "*"),
            uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        FilaDeTabla(
            id="E060.T4.4#severa", etiqueta_literal="Severa",
            valores={"so4_suelo_pct": "0,2 ≤ SO4 < 2,0",
                     "so4_agua_ppm": "1500 ≤ SO4 < 10000",
                     "cementos": "V", "a_c_max": 0.45, "fc_min_MPa": 31},
            llamadas_a_nota=("*",),
            uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
        FilaDeTabla(
            id="E060.T4.4#muy_severa", etiqueta_literal="Muy severa",
            valores={"so4_suelo_pct": "2,0 < SO4",
                     "so4_agua_ppm": "10000 < SO4",
                     "cementos": "Tipo V más puzolana***",
                     "a_c_max": 0.45, "fc_min_MPa": 31},
            llamadas_a_nota=("***", "*"),
            uso=Usada(por=("M9.requisitos_durabilidad_concreto",))),
    ),
    notas_al_pie=(
        _NOTA_COMUN_4_2_4_4,
        NotaAlPie(marca="**", texto=Verbatim(
            texto=("Se considera el caso del agua de mar como exposición "
                   "moderada."),
            pagina_pdf=38)),
        NotaAlPie(marca="***", texto=Verbatim(
            texto=("Puzolana que se ha comprobado por medio de ensayos, o por "
                   "experiencia, que mejora la resistencia a sulfatos cuando "
                   "se usa en concretos que contienen cemento tipo V."),
            pagina_pdf=38)),
    ),
    lagunas=(
        Laguna(
            que_no_cubre=("el punto SO4 = 2,0 % exacto en la escala del suelo "
                          "-- y 10 000 ppm exacto en la del agua --. "
                          "VERIFICADO SOBRE LA IMAGEN RENDERIZADA: la fila "
                          "severa se imprime «0,2 ≤ SO4 < 2,0», con cota "
                          "superior ESTRICTA, y la muy severa «2,0 < SO4», "
                          "con cota inferior ESTRICTA y sin «≤». El valor "
                          "exacto no cae en ninguna de las dos"),
            con_que_regla=("la hoja de ruta lo cierra: su Sec. 3.3 escribe la "
                           "fila severa como «0.20 - 2.00» y la muy severa "
                           "como «> 2.00», de modo que el punto exacto queda "
                           "en SEVERA. Se sigue esa lectura y no la mas "
                           "exigente porque la fuente primaria no la "
                           "contradice: calla. Y la unica diferencia practica "
                           "entre las dos filas es el cemento (V frente a V "
                           "mas puzolana): la a/c y el f'c son los mismos, de "
                           "modo que el recubrimiento no cambia por este "
                           "borde"),
            quien_lo_cierra="hoja_de_ruta §3.3",
            si_nadie_lo_cierra=Efecto.BLOQUEA),
    ),
    erratas=("DIS-E060-BORDE-2-0",),
    alcance=Integra(),
    vistas_de_calculo=("SULFATOS",),
)


# ===========================================================================
# E.060 Art. 7.7.1 — el lado peruano de la regla del recubrimiento mayor
# ===========================================================================
# NO ES UNA TABLA IMPRESA: el articulo lo escribe como lista con incisos. Se
# modela como tabla porque el calculo la consume como tal y porque asi la
# ventana puede pintarla junto a su homologa de AASHTO, que si es tabla; el
# `alcance` declara que solo se transcriben los tres incisos que este
# expediente puede alcanzar.
T_E060_7_7_1 = _tabla(
    id="E060.T7.7.1",
    cita_id="E060.7.7.1",
    titulo_literal="7.7.1 Concreto construido en sitio (no preesforzado)",
    texto_previo=Verbatim(
        texto=("Debe proporcionarse el siguiente recubrimiento mínimo de "
               "concreto al refuerzo, excepto cuando se requieran "
               "recubrimientos mayores según 7.7.5.1 ó se requiera protección "
               "especial contra el fuego"),
        pagina_pdf=54),
    columnas=(
        ColumnaDeTabla(id="situacion", etiqueta_literal="Situación",
                       unidad="", uso=Usada(por=("M9.recubrimiento_de_diseno",))),
        ColumnaDeTabla(id="recubrimiento_mm",
                       etiqueta_literal="Recubrimiento mínimo", unidad="mm",
                       uso=Usada(por=("M9.recubrimiento_de_diseno",))),
    ),
    filas=(
        FilaDeTabla(
            id="E060.T7.7.1#contra_suelo",
            jerarquia=("(a)",),
            etiqueta_literal=("Concreto colocado contra el suelo y expuesto "
                              "permanentemente a él"),
            valores={"recubrimiento_mm": 70},
            uso=Usada(por=("M9.recubrimiento_de_diseno",))),
        FilaDeTabla(
            id="E060.T7.7.1#suelo_intemperie_ge_3_4",
            jerarquia=("(b)", "Concreto en contacto permanente con el suelo o "
                              "la intemperie"),
            etiqueta_literal="Barras de 3/4” y mayores",
            valores={"recubrimiento_mm": 50},
            uso=Usada(por=("M9.recubrimiento_de_diseno",))),
        FilaDeTabla(
            id="E060.T7.7.1#suelo_intemperie_le_5_8",
            jerarquia=("(b)", "Concreto en contacto permanente con el suelo o "
                              "la intemperie"),
            etiqueta_literal=("Barras de 5/8” y menores, mallas "
                              "electrosoldadas"),
            valores={"recubrimiento_mm": 40},
            uso=Usada(por=("M9.recubrimiento_de_diseno",))),
    ),
    alcance=Acotada(
        razon=("el inciso (c) del articulo -- «Concreto no expuesto a la "
               "intemperie ni en contacto con el suelo» -- describe elementos "
               "interiores de edificacion (losas, muros, viguetas, vigas y "
               "columnas, cascaras y losas plegadas). Un cabezal de "
               "alcantarilla esta, por definicion, contra el suelo o a la "
               "intemperie: ninguna de sus siete filas puede aplicarle"),
        que_queda_fuera=("(c) Concreto no expuesto a la intemperie ni en "
                         "contacto con el suelo: losas, muros y viguetas "
                         "(40 y 20 mm), vigas y columnas (40 mm), y cascaras "
                         "y losas plegadas (20, 15 y 15 mm)"),
        donde_leerlo="E.060, Art. 7.7.1 (c), pag. impresa 54"),
    vistas_de_calculo=("RECUBRIMIENTO",),
)


# ===========================================================================
# EG-2013 — Tabla 503-07, clases de concreto estructural
# ===========================================================================
# DOS columnas, no tres: «Clase» y «Resistencia minima a la compresion a 28
# dias». El USO no es una columna -- es encabezado de grupo dentro de la
# primera --, y la tabla no lleva ninguna nota al pie.
T_EG_503_07 = _tabla(
    id="EG2013.T503-07",
    cita_id="EG2013.503.04#T503_07",
    titulo_literal="Tabla 503-07 Clases de concreto estructural",
    texto_previo=Verbatim(
        texto=("Para su empleo en las distintas clases de obra y de acuerdo "
               "con su resistencia mínima a la compresión, determinada según "
               "la norma MTC E 704, se establecen las siguientes clases de "
               "concreto, indicadas en la Tabla 503-07."),
        pagina_pdf=919),
    columnas=(
        ColumnaDeTabla(id="clase", etiqueta_literal="Clase", unidad="",
                       uso=Usada(por=("M9.verificar_ciclopeo",))),
        ColumnaDeTabla(id="fc_MPa",
                       etiqueta_literal=("Resistencia mínima a la compresión "
                                         "a 28 días"),
                       unidad="MPa",
                       uso=Usada(por=("M9.verificar_ciclopeo",))),
    ),
    filas=(
        FilaDeTabla(id="EG2013.T503-07#A", etiqueta_literal="A",
                    jerarquia=("Concreto pre y post tensado",),
                    valores={"fc_MPa": 35.0},
                    uso=NoUsada(por_que_no="ningun elemento de este proyecto se pre o postensa")),
        FilaDeTabla(id="EG2013.T503-07#B", etiqueta_literal="B",
                    jerarquia=("Concreto pre y post tensado",),
                    valores={"fc_MPa": 32.0},
                    uso=NoUsada(por_que_no="idem")),
        FilaDeTabla(id="EG2013.T503-07#C", etiqueta_literal="C",
                    jerarquia=("Concreto reforzado",),
                    valores={"fc_MPa": 28.0},
                    uso=NoUsada(por_que_no=("el f'c del cabezal lo fija la "
                                            "durabilidad, no esta escala de "
                                            "clases; se transcribe porque es "
                                            "la que hay que mirar si el "
                                            "expediente especifica por clase"))),
        FilaDeTabla(id="EG2013.T503-07#D", etiqueta_literal="D",
                    jerarquia=("Concreto reforzado",),
                    valores={"fc_MPa": 21.0},
                    uso=NoUsada(por_que_no="idem")),
        FilaDeTabla(id="EG2013.T503-07#E", etiqueta_literal="E",
                    jerarquia=("Concreto reforzado",),
                    valores={"fc_MPa": 17.5},
                    uso=NoUsada(por_que_no="idem")),
        FilaDeTabla(id="EG2013.T503-07#F", etiqueta_literal="F",
                    jerarquia=("Concreto simple",),
                    valores={"fc_MPa": 14.0},
                    uso=Usada(por=("M9.verificar_ciclopeo",))),
        FilaDeTabla(id="EG2013.T503-07#G", etiqueta_literal="G",
                    jerarquia=("Concreto ciclópeo",),
                    valores={"fc_MPa": 14.0},
                    llamadas_a_nota=(),
                    uso=Usada(por=("M9.verificar_ciclopeo",))),
    ),
    notas_al_pie=(),
    erratas=("DIS-HR-CICLOPEO",),
    alcance=Integra(),
    vistas_de_calculo=("CLASES_CONCRETO_EG2013_MPA",),
)


# ===========================================================================
# Manual de Puentes — Tabla 2.4.5.3.1-2, factores de carga permanente gamma_p
# ===========================================================================
# LAS DIECIOCHO FILAS CON VALOR, aunque el calculo use cinco. Es la regla dura
# del proyecto: la tabla se transcribe entera y la eleccion se declara aparte,
# porque una tabla podada no deja ver de que se eligio una fila.
#
# LAS DOS COLUMNAS SE ESCRIBEN COMO LAS IMPRIME EL MANUAL, y no son iguales:
# «Maximo» va SIN tilde en el original y «Mínimo» CON ella. Es errata de la
# fuente, no de esta transcripcion, y por eso la primera no se «arregla». Si
# aqui se quitaran las dos tildes, la nota de erratas estaria atribuyendo al
# Manual una falta que seria del codigo.
#
# LA CELDA «N/A» NO ES «no declarado» NI «falta el dato»: la fuente dice
# expresamente que esa fila no tiene ese extremo. Tiene nombre propio para que
# ningun consumidor la lea como un cero, un uno o una omision -- y para que
# pedirla sea un error del expediente y no un KeyError. Existe por MAT-D15 /
# NOR-AAS-04: el criterio afirmaba que la fuente no declara minimo para EH en
# reposo, y lo declara (0.90); el N/A pertenece a la fila SIGUIENTE, «AEP Para
# paredes ancladas». Un corrimiento de una fila entre dos que comparten el
# maximo 1.35.
_USO_GAMMA_P = {
    "EH_activa": Usada(por=("M9.empujes_trasdos",)),
    "EV_muros_y_estribos_de_retencion": Usada(por=("M9.verificar_estabilidad",)),
    "EV_estructura_rigida_enterrada": Usada(por=("M8.factores_carga_flotacion",)),
    "EV_flexibles_alcantarillas_termoplasticas": Usada(por=("M8.factores_carga_flotacion",)),
    "EV_flexibles_cajon_metalico_plancha_fibra_vidrio": Usada(por=("M8.factores_carga_flotacion",)),
    "ES_carga_superficial_en_el_terreno": Usada(por=("M9.empujes_trasdos",)),
}
_NO_USADA_GAMMA_P = NoUsada(por_que_no=(
    "la fila describe un tipo de carga o de fundacion que este expediente no "
    "tiene -- pilotes, downdrag, superficie de rodadura, muros MSE, suelo "
    "claveteado, esfuerzos residuales --. Se transcribe porque es lo que deja "
    "ver de que se eligio la fila que si se usa: sin las dieciocho, «EV: "
    "Estructura rigida enterrada» seria un numero sin alternativas visibles"))

_FILAS_GAMMA_P = (
    FilaDeTabla(
        id="MP.TGAMMA_P#DC_componentes_y_auxiliares",
        etiqueta_literal='DC: Componentes y Auxiliares.',
        valores={"maximo": 1.25, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("DC_componentes_y_auxiliares", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#DC_resistencia_IV_solamente",
        etiqueta_literal='DC: Resistencia IV Solamente.',
        valores={"maximo": 1.5, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("DC_resistencia_IV_solamente", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#DD_pilotes_metodo_tomlinson",
        jerarquia=('DD: Downdrag',),
        etiqueta_literal='Pilotes, α Método de Tomlinson.',
        valores={"maximo": 1.4, "minimo": 0.25},
        uso=_USO_GAMMA_P.get("DD_pilotes_metodo_tomlinson", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#DD_pilotes_metodo_lambda",
        jerarquia=('DD: Downdrag',),
        etiqueta_literal='Pilotes, λ Método.',
        valores={"maximo": 1.05, "minimo": 0.3},
        uso=_USO_GAMMA_P.get("DD_pilotes_metodo_lambda", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#DD_pilotes_perforados_oneill_reese",
        jerarquia=('DD: Downdrag',),
        etiqueta_literal='Pilotes Perforados, (Drilled Shaft) Método de O’Neill and Reese (1999).',
        valores={"maximo": 1.25, "minimo": 0.35},
        uso=_USO_GAMMA_P.get("DD_pilotes_perforados_oneill_reese", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#DW_superficie_de_rodadura_y_accesorios",
        etiqueta_literal='DW: Superficie de rodadura y accesorios.',
        valores={"maximo": 1.5, "minimo": 0.65},
        uso=_USO_GAMMA_P.get("DW_superficie_de_rodadura_y_accesorios", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EH_activa",
        jerarquia=('EH: Presión Horizontal de la tierra.',),
        etiqueta_literal='Activa.',
        valores={"maximo": 1.5, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EH_activa", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EH_en_reposo",
        jerarquia=('EH: Presión Horizontal de la tierra.',),
        etiqueta_literal='En reposo.',
        valores={"maximo": 1.35, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EH_en_reposo", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EH_AEP_paredes_ancladas",
        jerarquia=('EH: Presión Horizontal de la tierra.',),
        etiqueta_literal='AEP Para paredes ancladas.',
        valores={"maximo": 1.35, "minimo": CeldaSinValor.NO_APLICA},
        uso=_USO_GAMMA_P.get("EH_AEP_paredes_ancladas", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EL_esfuerzos_residuales",
        etiqueta_literal='EL: Esfuerzos residuales acumulados resultantes del proceso constructivo, (Locked-in construction Stresses.)',
        valores={"maximo": 1.0, "minimo": 1.0},
        uso=_USO_GAMMA_P.get("EL_esfuerzos_residuales", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_estabilidad_global",
        jerarquia=('EV: Presion vertical de la tierra',),
        etiqueta_literal='Estabilidad global.',
        valores={"maximo": 1.0, "minimo": CeldaSinValor.NO_APLICA},
        uso=_USO_GAMMA_P.get("EV_estabilidad_global", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_muros_y_estribos_de_retencion",
        jerarquia=('EV: Presion vertical de la tierra',),
        etiqueta_literal='Muros y estribos de retención.',
        valores={"maximo": 1.35, "minimo": 1.0},
        uso=_USO_GAMMA_P.get("EV_muros_y_estribos_de_retencion", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_estructura_rigida_enterrada",
        jerarquia=('EV: Presion vertical de la tierra',),
        etiqueta_literal='Estructura rígida enterrada.',
        valores={"maximo": 1.3, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EV_estructura_rigida_enterrada", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_porticos_rigidos",
        jerarquia=('EV: Presion vertical de la tierra',),
        etiqueta_literal='Pórticos rígidos.',
        valores={"maximo": 1.35, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EV_porticos_rigidos", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_flexibles_cajon_metalico_plancha_fibra_vidrio",
        jerarquia=('EV: Presion vertical de la tierra', 'Estructuras flexible enterradas'),
        etiqueta_literal='o Alcantarillas cajón metálicas, plancas estructurales con corrugaciones y alcantarillas de fibra de vidrio.',
        valores={"maximo": 1.5, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EV_flexibles_cajon_metalico_plancha_fibra_vidrio", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_flexibles_alcantarillas_termoplasticas",
        jerarquia=('EV: Presion vertical de la tierra', 'Estructuras flexible enterradas'),
        etiqueta_literal='o Alcantarillas termoplásticas.',
        valores={"maximo": 1.3, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EV_flexibles_alcantarillas_termoplasticas", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#EV_flexibles_entre_otros",
        jerarquia=('EV: Presion vertical de la tierra', 'Estructuras flexible enterradas'),
        etiqueta_literal='o Entre otros.',
        valores={"maximo": 1.95, "minimo": 0.9},
        uso=_USO_GAMMA_P.get("EV_flexibles_entre_otros", _NO_USADA_GAMMA_P)),
    FilaDeTabla(
        id="MP.TGAMMA_P#ES_carga_superficial_en_el_terreno",
        etiqueta_literal='ES: Carga superficial(Sobrecarga) en el terreno',
        valores={"maximo": 1.5, "minimo": 0.75},
        uso=_USO_GAMMA_P.get("ES_carga_superficial_en_el_terreno", _NO_USADA_GAMMA_P)),
)

T_MP_GAMMA_P = _tabla(
    id="MP.TGAMMA_P",
    cita_id="MP.T2.4.5.3.1-2",
    titulo_literal="Tabla 2.4.5.3.1-2 Factores de carga para cargas permanentes, γp",
    columnas=(
        ColumnaDeTabla(id="tipo_de_carga",
                       etiqueta_literal=("Tipo de Carga, Tipo de Fundaciones, "
                                         "y Métodos Usados para Fuerza de "
                                         "Arrastre Hacia Abajo (Downdrag)"),
                       unidad="",
                       uso=Usada(por=("M8.factores_carga_flotacion", "M9.verificar_estabilidad"))),
        # «Maximo» SIN tilde y «Mínimo» CON ella: asi lo imprime el Manual.
        ColumnaDeTabla(id="maximo", etiqueta_literal="Maximo", unidad="",
                       uso=Usada(por=("M9.verificar_estabilidad",))),
        ColumnaDeTabla(id="minimo", etiqueta_literal="Mínimo", unidad="",
                       uso=Usada(por=("M8.factores_carga_flotacion",))),
    ),
    filas=_FILAS_GAMMA_P,
    fuente_declarada_por_la_tabla="",
    erratas=("DIS-MP-ERRATAS-GAMMA-P",),
    alcance=Integra(),
    vistas_de_calculo=("TABLA_GAMMA_P_FILAS",),
)


# ===========================================================================
# Manual de Puentes — Tabla 2.4.5.3.1-1, combinaciones de carga
# ===========================================================================
# PARCIAL POR FILAS, COMPLETA POR COLUMNAS, y las dos mitades de esa frase
# salen de campos distintos: `alcance = Acotada` dice lo primero con su razon,
# y las catorce columnas transcritas dicen lo segundo. Las otras diez filas de
# la tabla -- Resistencia II a V, Evento Extremo II, Servicio II a IV y Fatiga
# I y II -- no estan porque ninguna fase del proyecto las evalua: no es una
# tabla podada, es que la Sec. 9.2 elige TRES combinaciones y estas son esas.
#
# LA CELDA «--» ES LA FUENTE DICIENDO QUE AHI NO HAY FACTOR, no un cero.
# Y donde la columna de cargas permanentes remite a la Tabla -2, la celda lo
# dice con un marcador propio en vez de con un numero inventado.
#
# EVENTO EXTREMO I LLEVA 1.00 EN LAS PERMANENTES, NO gamma_p, y no es un error
# de transcripcion: lo dicen las dos fuentes, y el comentario C3.4.1 de AASHTO
# explica por que ("Prior to 2015, these Specifications used a value for
# gamma_p greater than 1.0. This practice went against the intended philosophy
# behind the Extreme Event Limit State", pag. impresa 3-10).

_FILAS_COMBINACIONES = (
    FilaDeTabla(
        id="MP.TCOMB#Resistencia_I",
        etiqueta_literal='Resistencia I',
        valores={"permanentes": CeldaSinValor.REMITE_A_OTRA_TABLA, "LS": 1.75, "WA": '1.0 / 1.0', "WS": CeldaSinValor.NO_PARTICIPA, "WL": CeldaSinValor.NO_PARTICIPA, "FR": 1.0, "TU": '0.5 / 1.2', "TG": 'gamma_TG', "SE": 'gamma_SE', "EQ": CeldaSinValor.NO_PARTICIPA, "BL": CeldaSinValor.NO_PARTICIPA, "IC": CeldaSinValor.NO_PARTICIPA, "CT": CeldaSinValor.NO_PARTICIPA, "CV": CeldaSinValor.NO_PARTICIPA},
        uso=Usada(por=("M8.factores_carga_flotacion", "M9.combinaciones"))),
    FilaDeTabla(
        id="MP.TCOMB#Servicio_I",
        etiqueta_literal='Servicio I',
        valores={"permanentes": '1.0 / 1.0', "LS": 1.0, "WA": '1.0 / 1.0', "WS": 0.3, "WL": 1.0, "FR": 1.0, "TU": '1.0 / 1.2', "TG": 'gamma_TG', "SE": 'gamma_SE', "EQ": CeldaSinValor.NO_PARTICIPA, "BL": CeldaSinValor.NO_PARTICIPA, "IC": CeldaSinValor.NO_PARTICIPA, "CT": CeldaSinValor.NO_PARTICIPA, "CV": CeldaSinValor.NO_PARTICIPA},
        uso=Usada(por=("M8.factores_carga_flotacion", "M9.combinaciones"))),
    FilaDeTabla(
        id="MP.TCOMB#Evento_Extremo_I",
        etiqueta_literal='Evento Extremo I',
        valores={"permanentes": '1.0 / 1.0', "LS": 'gamma_EQ', "WA": '1.0 / 1.0', "WS": CeldaSinValor.NO_PARTICIPA, "WL": CeldaSinValor.NO_PARTICIPA, "FR": 1.0, "TU": CeldaSinValor.NO_PARTICIPA, "TG": CeldaSinValor.NO_PARTICIPA, "SE": CeldaSinValor.NO_PARTICIPA, "EQ": '1.0 / 1.0', "BL": CeldaSinValor.NO_PARTICIPA, "IC": CeldaSinValor.NO_PARTICIPA, "CT": CeldaSinValor.NO_PARTICIPA, "CV": CeldaSinValor.NO_PARTICIPA},
        uso=Usada(por=("M8.factores_carga_flotacion", "M9.combinaciones"))),
)


T_MP_COMBINACIONES = _tabla(
    id="MP.TCOMB",
    cita_id="MP.T2.4.5.3.1-1",
    titulo_literal="Tabla 2.4.5.3.1-1 Combinaciones de Carga y Factores de Carga",
    columnas=tuple(
        ColumnaDeTabla(id=cid, etiqueta_literal=etiqueta, unidad="",
                       uso=uso)
        for cid, etiqueta, uso in (
            ("permanentes", "DC DD DW EH EV ES EL PS CR SH",
             Usada(por=("M8.factores_carga_flotacion", "M9.combinaciones"))),
            ("LS", "LL IM CE BR PL LS", Usada(por=("M9.empujes_trasdos",))),
            ("WA", "WA", Usada(por=("M8.factores_carga_flotacion",))),
            ("WS", "WS", NoUsada(por_que_no="ninguna fase evalua viento sobre la estructura")),
            ("WL", "WL", NoUsada(por_que_no="ninguna fase evalua viento sobre la carga viva")),
            ("FR", "FR", NoUsada(por_que_no="ninguna fase evalua friccion")),
            ("TU", "TU", NoUsada(por_que_no="ninguna fase evalua temperatura uniforme")),
            ("TG", "TG", NoUsada(por_que_no="ninguna fase evalua gradiente termico")),
            ("SE", "SE", NoUsada(por_que_no="ninguna fase evalua asentamiento diferencial")),
            ("EQ", "EQ", Usada(por=("M9.demanda_sismica_cabezal",))),
            ("BL", "BL", NoUsada(por_que_no="ninguna fase evalua explosion")),
            ("IC", "IC", NoUsada(por_que_no="ninguna fase evalua carga de hielo")),
            ("CT", "CT", NoUsada(por_que_no="ninguna fase evalua colision de vehiculo")),
            ("CV", "CV", NoUsada(por_que_no="ninguna fase evalua colision de embarcacion")),
        )),
    filas=_FILAS_COMBINACIONES,
    notas_al_pie=(
        NotaAlPie(marca="", texto=Verbatim(
            texto=("Usar solamente uno de los indicados en estas columnas en "
                   "cada combinación"),
            pagina_pdf=144)),
    ),
    alcance=Acotada(
        razon=("la Sec. 9.2 de la hoja de ruta nombra TRES combinaciones "
               "-- Resistencia I, Servicio I y Evento Extremo I -- y ninguna "
               "fase del proyecto evalua las otras diez"),
        que_queda_fuera=("Resistencia II, III, IV y V; Evento Extremo II; "
                         "Servicio II, III y IV; Fatiga I y Fatiga II"),
        donde_leerlo=("Manual de Puentes, num. 2.4.5.3.1, Tabla 2.4.5.3.1-1, "
                      "pag. impresa 143 (PDF 144)")),
    vistas_de_calculo=("TABLA_COMBINACIONES_FILAS",),
)


# ===========================================================================
# Manual de Puentes — Tabla 2.9.1.5.5.3-1, recubrimiento de concreto
# ===========================================================================
# LO QUE EL TITULO DE LA TABLA DICE Y NADIE HABIA LEIDO -- y es la clave de
# todo el cluster C07 --: «Recubrimiento para las armaduras principales de
# aceros NO PROTEGIDAS». La tabla peruana tiene UNA sola columna porque cubre
# UNA sola categoria de acero: la no protegida, que la 9a ed. de AASHTO llama
# Categoria A. El acero epoxico o galvanizado el Manual lo trata en un numeral
# aparte, el 2.9.1.5.5.4 «Recubrimiento Protector». De modo que los 3.0 in de
# «ubicaciones costeras» NO son «el recubrimiento de AASHTO»: son el del acero
# SIN recubrir, y con acero protegido la tabla de la 9a ed. baja a 2.0 in.
#
# Los valores se transcriben en mm -- la unidad en que este proyecto
# especifica recubrimientos, porque E.060 Art. 7.7.1 esta escrito en mm -- con
# la pulgada de la fuente al lado. 1 in = 25.4 mm exacto: 3.0 in son 76.2 mm y
# no 75 (MAT-D16).
_USO_RECUB = {
    "vaciado_contra_suelo": Usada(por=("M9._recubrimiento_aashto_detallado",)),
    "costera": Usada(por=("M9._recubrimiento_aashto_detallado",)),
    "exterior_no_superior": Usada(por=("M9._recubrimiento_aashto_detallado",)),
}
_NO_USADA_RECUB = NoUsada(por_que_no=(
    "la fila describe un elemento que este expediente no tiene -- pilotes, "
    "pilares, tableros, paneles prefabricados, alcantarillas cajon "
    "prefabricadas -- o una exposicion que no le aplica. Se transcribe entera "
    "porque es lo que deja ver que las tres filas que si se usan son las que "
    "corresponden a un cabezal vaciado contra el suelo en ubicacion costera"))




_FILAS_RECUBRIMIENTO_MP = (
    FilaDeTabla(
        id="MP.TRECUB#agua_salada",
        etiqueta_literal='Exposición directa al agua salada',
        valores={"recubrimiento_mm": 101.6, "recubrimiento_in": 4.0},
        uso=_USO_RECUB.get("agua_salada", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#vaciado_contra_suelo",
        etiqueta_literal='Vaciado del concreto contra el suelo',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("vaciado_contra_suelo", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#costera",
        etiqueta_literal='Ubicaciones costeras',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("costera", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#sales_anticongelantes",
        etiqueta_literal='sales_anticongelantes',
        valores={"recubrimiento_mm": 63.5, "recubrimiento_in": 2.5},
        uso=_USO_RECUB.get("sales_anticongelantes", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#tableros_neumaticos_clavos",
        etiqueta_literal='tableros_neumaticos_clavos',
        valores={"recubrimiento_mm": 63.5, "recubrimiento_in": 2.5},
        uso=_USO_RECUB.get("tableros_neumaticos_clavos", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#exterior_no_superior",
        etiqueta_literal='exterior_no_superior',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("exterior_no_superior", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#interior_hasta_n11",
        etiqueta_literal='interior_hasta_n11',
        valores={"recubrimiento_mm": 38.1, "recubrimiento_in": 1.5},
        uso=_USO_RECUB.get("interior_hasta_n11", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#interior_n14_n18",
        etiqueta_literal='interior_n14_n18',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("interior_n14_n18", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#losa_in_situ_inferior_hasta_n11",
        etiqueta_literal='losa_in_situ_inferior_hasta_n11',
        valores={"recubrimiento_mm": 25.4, "recubrimiento_in": 1.0},
        uso=_USO_RECUB.get("losa_in_situ_inferior_hasta_n11", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#losa_in_situ_inferior_n14_n18",
        etiqueta_literal='losa_in_situ_inferior_n14_n18',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("losa_in_situ_inferior_n14_n18", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#paneles_prefabricados_encofrados",
        etiqueta_literal='paneles_prefabricados_encofrados',
        valores={"recubrimiento_mm": 20.32, "recubrimiento_in": 0.8},
        uso=_USO_RECUB.get("paneles_prefabricados_encofrados", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_prefabricado_no_corrosivo",
        etiqueta_literal='pilar_prefabricado_no_corrosivo',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("pilar_prefabricado_no_corrosivo", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_prefabricado_corrosivo",
        etiqueta_literal='pilar_prefabricado_corrosivo',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("pilar_prefabricado_corrosivo", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilote_prefabricado_pretensado",
        etiqueta_literal='pilote_prefabricado_pretensado',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("pilote_prefabricado_pretensado", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_in_situ_no_corrosivo",
        etiqueta_literal='pilar_in_situ_no_corrosivo',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("pilar_in_situ_no_corrosivo", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_in_situ_corrosivo_general",
        etiqueta_literal='pilar_in_situ_corrosivo_general',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("pilar_in_situ_corrosivo_general", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_in_situ_corrosivo_protegida",
        etiqueta_literal='pilar_in_situ_corrosivo_protegida',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("pilar_in_situ_corrosivo_protegida", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_in_situ_cascaras",
        etiqueta_literal='pilar_in_situ_cascaras',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("pilar_in_situ_cascaras", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#pilar_in_situ_tremie_o_lechada",
        etiqueta_literal='pilar_in_situ_tremie_o_lechada',
        valores={"recubrimiento_mm": 76.2, "recubrimiento_in": 3.0},
        uso=_USO_RECUB.get("pilar_in_situ_tremie_o_lechada", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#alcantarilla_cajon_prefab_losa_de_rodadura",
        etiqueta_literal='alcantarilla_cajon_prefab_losa_de_rodadura',
        valores={"recubrimiento_mm": 63.5, "recubrimiento_in": 2.5},
        uso=_USO_RECUB.get("alcantarilla_cajon_prefab_losa_de_rodadura", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#alcantarilla_cajon_prefab_losa_menos_2_pies",
        etiqueta_literal='Alcantarillas de cajón de concreto prefabricados: forjados con inferior a 2 pies de relleno que no se utilicen como una superficie de conducción',
        valores={"recubrimiento_mm": 50.8, "recubrimiento_in": 2.0},
        uso=_USO_RECUB.get("alcantarilla_cajon_prefab_losa_menos_2_pies", _NO_USADA_RECUB)),
    FilaDeTabla(
        id="MP.TRECUB#alcantarilla_cajon_prefab_otros_miembros",
        etiqueta_literal='alcantarilla_cajon_prefab_otros_miembros',
        valores={"recubrimiento_mm": 25.4, "recubrimiento_in": 1.0},
        uso=_USO_RECUB.get("alcantarilla_cajon_prefab_otros_miembros", _NO_USADA_RECUB)),
)

T_MP_RECUBRIMIENTO = _tabla(
    id="MP.TRECUB",
    cita_id="MP.T2.9.1.5.5.3-1",
    titulo_literal=("Tabla 2.9.1.5.5.3-1 Recubrimiento para las armaduras "
                    "principales de aceros no protegidas"),
    columnas=(
        ColumnaDeTabla(id="situacion", etiqueta_literal="Situación", unidad="",
                       uso=Usada(por=("M9._recubrimiento_aashto_detallado",))),
        ColumnaDeTabla(id="recubrimiento_in",
                       etiqueta_literal="Recubrimiento (in.)", unidad="in",
                       uso=NoUsada(por_que_no=(
                           "el calculo opera en SI y consume la columna en "
                           "mm; la pulgada se transcribe porque es la unidad "
                           "en que la fuente lo imprime y sin ella no se "
                           "puede comprobar la conversion"))),
        ColumnaDeTabla(id="recubrimiento_mm",
                       etiqueta_literal="Recubrimiento (mm)", unidad="mm",
                       uso=Usada(por=("M9._recubrimiento_aashto_detallado",))),
    ),
    filas=_FILAS_RECUBRIMIENTO_MP,
    modificadores=(
        Modificador(
            id="MOD-RECUB-AC",
            cita_id="MP.T2.9.1.5.5.3-1",
            concepto="factor por relación agua-cemento",
            texto=Verbatim(texto="Para W/C <= 0.40", pagina_pdf=378),
            sobre_que=("multiplica el recubrimiento de cualquier fila de esta "
                       "tabla"),
            orden=OrdenDeAplicacion.ANTES_DE_CRUZAR_FUENTES,
            tramos=(
                TramoDeModificador(
                    condicion=CondicionAplicacion(
                        id="COND-AC-BAJA",
                        texto=Verbatim(texto="Para W/C <= 0.40",
                                       pagina_pdf=378),
                        cita_id="MP.T2.9.1.5.5.3-1",
                        resuelve=PorCriterio(clave="exposicion_quimica_ems")),
                    factor=0.8, etiqueta_literal="Para W/C <= 0.40 ... 0.8"),
                TramoDeModificador(
                    condicion=CondicionAplicacion(
                        id="COND-AC-ALTA",
                        texto=Verbatim(texto="Para W/C >= 0.50",
                                       pagina_pdf=378),
                        cita_id="MP.T2.9.1.5.5.3-1",
                        resuelve=PorCriterio(clave="exposicion_quimica_ems")),
                    factor=1.2, etiqueta_literal="Para W/C >= 0.50 ... 1.2"),
            ),
            piso=(25.4, "MP.T2.9.1.5.5.3-1"),
            lagunas=(
                Laguna(
                    que_no_cubre=("la banda 0.40 < W/C < 0.50. El Manual "
                                  "imprime SOLO DOS viñetas y AASHTO tres: el "
                                  "tramo intermedio, con factor 1.0, esta en "
                                  "el Art. 5.10.1 de AASHTO (pag. impresa "
                                  "5-167) y el corpus peruano no lo trae"),
                    con_que_regla=("un criterio [C], no copiando el 1.0 de la "
                                   "otra fuente hacia adentro de la "
                                   "transcripcion peruana. LA BANDA ES "
                                   "ALCANZABLE en este expediente: con "
                                   "sulfatos severos y sin cloruros la a/c "
                                   "maxima resulta 0.45"),
                    quien_lo_cierra=("criterios_adoptados["
                                     "'factor_recubrimiento_banda_intermedia_ac']"),
                    si_nadie_lo_cierra=Efecto.BLOQUEA),
            ),
        ),
    ),
    alcance=Integra(),
    vistas_de_calculo=("RECUBRIMIENTO_MP_MM",),
)


# ===========================================================================
# Manual de Puentes — Tabla 2.4.3.11.2.1.2-1, factor de sitio F_pga
# ===========================================================================
# LA TABLA ENTERA -- sus seis filas y sus cinco columnas --, no las tres que
# el calculo consume. Y TRES DE SUS RASGOS SOLO SE VEN RENDERIZANDO, que es
# por lo que su cita lleva `metodo = IMAGEN`:
#
#   1. El «1» del encabezado superior es la llamada a la Nota 1, no un
#      exponente.
#   2. Los dos rotulos extremos son DESIGUALDADES ESTRICTAS -- «PGA < 0.10» y
#      «PGA > 0.50» --, y el `>` de la ultima no sobrevive a la extraccion de
#      texto plano.
#   3. El asterisco de la fila F remite a la Nota 2 y NO es un cero ni un
#      olvido: es la fuente diciendo que ahi no hay factor.
#
# QUE HACER CON UN PGA DE EXACTAMENTE 0.50 -- leer esa columna o interpolar
# contra la anterior -- LA TABLA NO LO RESUELVE, y el PGA de este proyecto cae
# justo sobre ese borde. Es laguna de la fuente, no del registro
# (NOR-PUE-11), y la cierra el criterio, no un `>=` del codigo.
_NO = NoUsada(por_que_no=(
    "la fila describe una clase de sitio que este expediente no se atribuye. "
    "Se transcribe entera porque es lo que deja ver que el salto de la "
    "clase D a la E dobla el factor a PGA bajo y lo invierte a PGA alto"))

_FILAS_F_PGA = (
    FilaDeTabla(
        id="MP.TFPGA#A",
        etiqueta_literal="A",
        valores={"pga_lt_0_10": 0.8, "pga_0_20": 0.8, "pga_0_30": 0.8, "pga_0_40": 0.8, "pga_gt_0_50": 0.8},
        uso=Usada(por=("M9.f_pga",))),
    FilaDeTabla(
        id="MP.TFPGA#B",
        etiqueta_literal="B",
        valores={"pga_lt_0_10": 1.0, "pga_0_20": 1.0, "pga_0_30": 1.0, "pga_0_40": 1.0, "pga_gt_0_50": 1.0},
        uso=Usada(por=("M9.f_pga",))),
    FilaDeTabla(
        id="MP.TFPGA#C",
        etiqueta_literal="C",
        valores={"pga_lt_0_10": 1.2, "pga_0_20": 1.2, "pga_0_30": 1.1, "pga_0_40": 1.0, "pga_gt_0_50": 1.0},
        uso=Usada(por=("M9.f_pga",))),
    FilaDeTabla(
        id="MP.TFPGA#D",
        etiqueta_literal="D",
        valores={"pga_lt_0_10": 1.6, "pga_0_20": 1.4, "pga_0_30": 1.2, "pga_0_40": 1.1, "pga_gt_0_50": 1.0},
        uso=Usada(por=("M9.f_pga",))),
    FilaDeTabla(
        id="MP.TFPGA#E",
        etiqueta_literal="E",
        valores={"pga_lt_0_10": 2.5, "pga_0_20": 1.7, "pga_0_30": 1.2, "pga_0_40": 0.9, "pga_gt_0_50": 0.9},
        uso=PendienteDeCondicion(condicion_id="COND-CLASE-DE-SITIO")),
    FilaDeTabla(
        id="MP.TFPGA#F",
        etiqueta_literal="F",
        valores={"pga_lt_0_10": CeldaSinValor.EXIGE_ESTUDIO, "pga_0_20": CeldaSinValor.EXIGE_ESTUDIO, "pga_0_30": CeldaSinValor.EXIGE_ESTUDIO, "pga_0_40": CeldaSinValor.EXIGE_ESTUDIO, "pga_gt_0_50": CeldaSinValor.EXIGE_ESTUDIO},
        llamadas_a_nota=("2",),
        uso=PendienteDeCondicion(condicion_id="COND-CLASE-DE-SITIO")),
)

T_MP_F_PGA = _tabla(
    id="MP.TFPGA",
    cita_id="MP.T2.4.3.11.2.1.2-1",
    titulo_literal=("Tabla 2.4.3.11.2.1.2-1 Valores de Factor de Sitio, F_pga "
                    "En Periodo-Cero en el Espectro de Aceleracion"),
    encabezados_superiores=("Coeficiente Aceleracion Pico del Terreno (PGA)1",),
    columnas=(
        ColumnaDeTabla(id="clase_de_sitio",
                       etiqueta_literal="Clase de Sitio", unidad="",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CLASE-DE-SITIO")),
        ColumnaDeTabla(id="pga_lt_0_10", etiqueta_literal="PGA < 0.10",
                       unidad="g", uso=Usada(por=("M9.f_pga",))),
        ColumnaDeTabla(id="pga_0_20", etiqueta_literal="PGA = 0.20",
                       unidad="g", uso=Usada(por=("M9.f_pga",))),
        ColumnaDeTabla(id="pga_0_30", etiqueta_literal="PGA = 0.30",
                       unidad="g", uso=Usada(por=("M9.f_pga",))),
        ColumnaDeTabla(id="pga_0_40", etiqueta_literal="PGA = 0.40",
                       unidad="g", uso=Usada(por=("M9.f_pga",))),
        ColumnaDeTabla(id="pga_gt_0_50", etiqueta_literal="PGA > 0.50",
                       unidad="g", uso=Usada(por=("M9.f_pga",))),
    ),
    filas=_FILAS_F_PGA,
    notas_al_pie=(
        NotaAlPie(marca="1", texto=Verbatim(
            texto=("Usar linea recta de interpolacion para valores "
                   "intermedios de PGA."),
            pagina_pdf=124)),
        NotaAlPie(marca="2", texto=Verbatim(
            texto=("Llevar a cabo investigaciones geotecnicas especificas del "
                   "sitio y analisis de respuesta dinamica de sitio, para "
                   "todos los sitios en sitio clase F"),
            pagina_pdf=124)),
    ),
    lagunas=(
        Laguna(
            que_no_cubre=("un PGA de EXACTAMENTE 0.50. La ultima columna se "
                          "rotula «PGA > 0.50», desigualdad estricta, y la "
                          "anterior es «PGA = 0.40»: la tabla no dice si el "
                          "borde se lee en la ultima columna o se interpola "
                          "contra la anterior. EL PGA DE ESTE PROYECTO CAE "
                          "JUSTO AHI, de modo que no es un caso teorico"),
            con_que_regla=("un criterio [A] declarado, no un `>=` del codigo: "
                           "la decision es del proyectista porque la fuente "
                           "no la toma"),
            quien_lo_cierra=("criterios_adoptados["
                             "'F_pga_lectura_columna_extrema']"),
            si_nadie_lo_cierra=Efecto.BLOQUEA),
    ),
    alcance=Integra(),
    vistas_de_calculo=("F_PGA_TABLA",),
)


# ===========================================================================
# HDS-5 — Tabla A.1, constantes de las ecuaciones de control de entrada
# ===========================================================================
# ACOTADA A LAS TRES CARTAS DEL CATALOGO, y con la razon. De sus NUEVE
# columnas impresas, cuatro son constantes de la ecuacion (K, M, c, Y) y las
# otras cinco identifican la carta; de ahi que el repositorio afirmara que la
# tabla «contiene solo K, M, c e Y» -- cierto en cuanto a CONSTANTES DE
# ECUACION, que es lo que NOR-HDS-03 discutia: no hay columna K_u ni columna
# K_s, y esos dos viven en la lista de variables del num. A.2.1.
#
# ERRATA DE LA PROPIA FUENTE, hallada al verificar: el titulo dice «for Charts
# in Appendix G» y en esta 3a edicion NO EXISTE un Apendice G -- las cartas
# estan en el Apendice C --. Se transcribe como lo imprime, con la
# advertencia, para que quien lo busque lo encuentre.
T_HDS5_A1 = _tabla(
    id="HDS5_3ED.TA1",
    cita_id="HDS5_3ED.TA.1",
    titulo_literal=("Table A.1.  Constants for Inlet Control Equations for "
                    "Charts in Appendix G."),
    columnas=(
        ColumnaDeTabla(id="chart_no", etiqueta_literal="Chart No", unidad="",
                       uso=Usada(por=("M2.materiales_candidatos",))),
        ColumnaDeTabla(id="shape_and_material",
                       etiqueta_literal="Shape and Material", unidad="",
                       uso=Usada(por=("M2.materiales_candidatos",))),
        ColumnaDeTabla(id="nomograph_scale",
                       etiqueta_literal="Nomograph Scale", unidad="",
                       uso=NoUsada(por_que_no=(
                           "identifica la escala del nomograma impreso; este "
                           "programa resuelve las ecuaciones y no lee "
                           "nomogramas"))),
        ColumnaDeTabla(id="inlet_configuration",
                       etiqueta_literal="Inlet Configuration", unidad="",
                       uso=Usada(por=("criterios_adoptados['ke_entrada']",))),
        ColumnaDeTabla(id="equation_form",
                       etiqueta_literal="Equation Form", unidad="",
                       uso=NoUsada(por_que_no=(
                           "las tres filas del catalogo son Form 1 y M4 "
                           "implementa esa forma; se transcribe porque una "
                           "carta de Form 2 usaria otra ecuacion y sin esta "
                           "columna eso no se veria"))),
        ColumnaDeTabla(id="K", etiqueta_literal="Unsubmerged K", unidad="",
                       uso=Usada(por=("M4.control_entrada",))),
        ColumnaDeTabla(id="M", etiqueta_literal="Unsubmerged M", unidad="",
                       uso=Usada(por=("M4.control_entrada",))),
        ColumnaDeTabla(id="c", etiqueta_literal="Submerged c", unidad="",
                       uso=Usada(por=("M4.control_entrada",))),
        ColumnaDeTabla(id="Y", etiqueta_literal="Submerged Y", unidad="",
                       uso=Usada(por=("M4.control_entrada",))),
        ColumnaDeTabla(id="references", etiqueta_literal="References",
                       unidad="",
                       uso=NoUsada(por_que_no=(
                           "son las referencias bibliograficas de cada carta "
                           "(Bossy 1963, FHWA 1974, NBS 5th, HEC 13); no "
                           "entran en ninguna formula"))),
    ),
    filas=(
        FilaDeTabla(
            id="HDS5_3ED.TA1#circular_concreto_square_edge_headwall",
            etiqueta_literal="Square edge w/headwall",
            jerarquia=("1", "Circular Concrete"),
            valores={"chart_no": 1, "shape_and_material": "Circular Concrete",
                     "nomograph_scale": 1,
                     "inlet_configuration": "Square edge w/headwall",
                     "equation_form": 1, "K": 0.0098, "M": 2.00,
                     "c": 0.0398, "Y": 0.67, "references": "1, 2"},
            uso=Usada(por=("M4.control_entrada",))),
        FilaDeTabla(
            id="HDS5_3ED.TA1#circular_cmp_headwall",
            etiqueta_literal="Headwall",
            jerarquia=("2", "Circular CM"),
            valores={"chart_no": 2, "shape_and_material": "Circular CM",
                     "nomograph_scale": 1, "inlet_configuration": "Headwall",
                     "equation_form": 1, "K": 0.0078, "M": 2.00,
                     "c": 0.0379, "Y": 0.69, "references": "1, 2"},
            uso=Usada(por=("M4.control_entrada",))),
        FilaDeTabla(
            id="HDS5_3ED.TA1#circular_cmp_mitered",
            etiqueta_literal="Mitered to slope",
            jerarquia=("2", "Circular CM"),
            valores={"chart_no": 2, "shape_and_material": "Circular CM",
                     "nomograph_scale": 2,
                     "inlet_configuration": "Mitered to slope",
                     "equation_form": 1, "K": 0.0210, "M": 1.33,
                     "c": 0.0463, "Y": 0.75, "references": "1, 2"},
            uso=NoUsada(por_que_no=(
                "este proyecto adopta la embocadura a ras del muro (square "
                "edge with headwall); la de inglete se transcribe porque es "
                "la alternativa que el criterio 'embocadura' podria elegir, y "
                "porque su Ks de +0.7 es el que se confunde con el ke de 0.7 "
                "de la Tabla C.2 -- dos coeficientes distintos con el mismo "
                "numero"))),
    ),
    notas_al_pie=(
        NotaAlPie(marca="¹²³⁴", texto=Verbatim(
            texto="Bossy 1963", pagina_pdf=197)),
    ),
    alcance=Acotada(
        razon=("la tabla cubre todas las cartas del Apendice C -- cajon, "
               "eliptica, arco, pipe-arch, long span -- y el catalogo de "
               "conductos de la Sec. 3.2 de este proyecto ofrece solo seccion "
               "CIRCULAR en concreto, TMC y HDPE. Las filas de otras formas "
               "no pueden aplicarse a ningun punto del corredor"),
        que_queda_fuera=("las cartas de secciones cajon, eliptica, "
                         "pipe-arch, arco y long span, y las demas "
                         "configuraciones de borde de las circulares"),
        donde_leerlo="HDS-5 3a ed., Tabla A.1, pag. impresa A.8 (PDF 197)"),
    erratas=("DIS-HDS5-APENDICE-G",),
    vistas_de_calculo=("HDS5_INLET",),
)


# ===========================================================================
# HDS-5 — Tabla C.2, coeficientes de perdida de entrada (ke)
# ===========================================================================
# ACOTADA a la familia que el catalogo puede alcanzar. Y con una precision que
# la verificacion destapo: EL VALOR 0.5 APARECE SIETE VECES EN LA TABLA, en
# siete filas distintas. Cualquier codigo que diga «ke = 0.5 = tubo de
# concreto con cabezal» tiene que precisar el BORDE: es «Square-edge» bajo
# «Headwall or headwall and wingwalls», no «Socket end of pipe», que da 0.2.
T_HDS5_C2 = _tabla(
    id="HDS5_3ED.TC2",
    cita_id="HDS5_3ED.TC.2",
    titulo_literal="Table C.2.  Entrance Loss Coefficients.",
    texto_previo=Verbatim(
        texto="Outlet Control, Full or Partly Full Entrance Head Loss",
        pagina_pdf=216),
    columnas=(
        ColumnaDeTabla(id="tipo_y_borde",
                       etiqueta_literal=("Type of Structure and Design of "
                                         "Entrance"),
                       unidad="",
                       uso=Usada(por=("criterios_adoptados['ke_entrada']",))),
        ColumnaDeTabla(id="ke", etiqueta_literal="Coefficient Ke", unidad="",
                       uso=Usada(por=("M4.control_salida",))),
    ),
    filas=(
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_socket_projecting",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Projecting from fill, socket end (groove-end)",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="este proyecto no proyecta tubo saliente del relleno")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_sq_projecting",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Projecting from fill, sq. cut end",
            valores={"ke": 0.5},
            uso=NoUsada(por_que_no="idem")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_headwall_socket",
            jerarquia=("Pipe, Concrete", "Headwall or headwall and wingwalls"),
            etiqueta_literal="Socket end of pipe (groove-end",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no=(
                "el catalogo no ofrece tubo de campana; se transcribe porque "
                "es la fila HERMANA de la que el proyecto usa y la que "
                "explica que el 0.5 no es «el de concreto con cabezal» sino "
                "el del borde a escuadra"))),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_headwall_square_edge",
            jerarquia=("Pipe, Concrete", "Headwall or headwall and wingwalls"),
            etiqueta_literal="Square-edge",
            valores={"ke": 0.5},
            uso=Usada(por=("criterios_adoptados['ke_entrada']",))),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_rounded",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Rounded (radius = D/12",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="el catalogo no ofrece borde redondeado")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_mitered",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Mitered to conform to fill slope",
            valores={"ke": 0.7},
            uso=NoUsada(por_que_no=(
                "alternativa no adoptada. Se transcribe porque su 0.7 es el "
                "que se confunde con el Ks de +0.7 del control de ENTRADA: "
                "dos coeficientes distintos, con el mismo numero y la misma "
                "condicion (inglete), y sin relacion entre si"))),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_end_section",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="*End-Section conforming to fill slope",
            valores={"ke": 0.5},
            llamadas_a_nota=("*",),
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_beveled",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Beveled edges, 33.7⁰ or 45⁰ bevels",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#concreto_tapered",
            jerarquia=("Pipe, Concrete",),
            etiqueta_literal="Side- or slope-tapered inlet",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_projecting",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal="Projecting from fill (no headwall)",
            valores={"ke": 0.9},
            uso=NoUsada(por_que_no="este proyecto no proyecta tubo saliente")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_headwall_square_edge",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal="Headwall or headwall and wingwalls square-edge",
            valores={"ke": 0.5},
            uso=Usada(por=("criterios_adoptados['ke_entrada']",))),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_mitered",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal=("Mitered to conform to fill slope, paved or "
                              "unpaved slope"),
            valores={"ke": 0.7},
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_end_section",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal="*End-Section conforming to fill slope",
            valores={"ke": 0.5},
            llamadas_a_nota=("*",),
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_beveled",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal="Beveled edges, 33.7⁰ or 45⁰ bevels",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="alternativa no adoptada")),
        FilaDeTabla(
            id="HDS5_3ED.TC2#cm_tapered",
            jerarquia=("Pipe. or Pipe-Arch. Corrugated Metal",),
            etiqueta_literal="Side- or slope-tapered inlet",
            valores={"ke": 0.2},
            uso=NoUsada(por_que_no="alternativa no adoptada")),
    ),
    notas_al_pie=(
        NotaAlPie(marca="*", texto=Verbatim(
            texto=("Note: \"End Sections conforming to fill slope,\" made of "
                   "either metal or concrete, are the sections commonly "
                   "available from manufacturers.  From limited hydraulic "
                   "tests they are equivalent in operation to a headwall in "
                   "both inlet and outlet control."),
            pagina_pdf=216)),
    ),
    alcance=Acotada(
        razon=("la tabla trae ademas la familia «Box, Reinforced Concrete» "
               "con sus once filas de aletas y bordes, y el catalogo de "
               "conductos de la Sec. 3.2 no ofrece seccion cajon: ninguna de "
               "esas filas puede aplicarse a un punto de este corredor"),
        que_queda_fuera=("«Box, Reinforced Concrete»: Headwall parallel to "
                         "embankment (no wingwalls), Wingwalls at 30° to 75° "
                         "to barrel, Wingwall at 10° to 25° to barrel y "
                         "Wingwalls parallel (extension of sides), con sus "
                         "sub-bordes"),
        donde_leerlo="HDS-5 3a ed., Tabla C.2, pag. impresa C.6 (PDF 216)"),
    vistas_de_calculo=(),
)


# ===========================================================================
# AASHTO LRFD 9a ed. — Tabla 12.6.6.3-1, cobertura minima
# ===========================================================================
# LA TABLA QUE EL EXPEDIENTE CREIA QUE ERA OTRA. La justificacion del criterio
# 'condicion_pavimento' la describe como si «separase» tres condiciones de
# pavimento, y no lo hace: sus columnas son «Type», «Condition» y «Minimum
# Cover*», y las condiciones de pavimento son VALORES de la segunda columna
# que solo aparecen en 2 de los 13 tipos. Los otros once llevan un em-dash
# IMPRESO -- no una celda vacia -- y su cobertura no depende del pavimento.
#
# Que el repositorio ya calculaba bien no vuelve inocua la descripcion: quien
# la lea sin abrir el PDF buscara tres columnas que no existen. Por eso la
# transcripcion completa entra aqui, con los trece tipos y las catorce filas,
# y no solo los tres materiales del catalogo.
#
# CUATRO CELDAS NO CONTIENEN UN NUMERO SINO UN REENVIO a otro articulo o a
# otra tabla. Se transcriben como el texto que son: convertirlas en numero
# seria una interpretacion, y es justo lo que este cluster existe para
# impedir. Se marcan con `CeldaSinValor.REMITE_A_OTRA_TABLA`.
#
# LA TABLA ES IMPERIAL DE PUNTA A PUNTA -- ni una columna SI, ni un valor
# entre parentesis -- y ADEMAS DIMENSIONALMENTE MIXTA POR DISEÑO DE LA NORMA:
# el propio Art. 12.6.6.3 define S e ID en PULGADAS y Bc y B'c en PIES, de
# modo que «S/8» sale en pulgadas y «Bc/8» en PIES, y las dos se comparan
# contra el mismo «>= 12.0 in.». No es una errata: es como esta escrita. Las
# formulas del proyecto son adimensionales en el divisor y homogeneas con el
# diametro de entrada, que es lo unico que las salva de esa mezcla.
# NI DOS NI TRES: DEPENDE DEL MATERIAL, y por eso el criterio no puede tener
# una sola forma. Para el CONCRETO la tabla mete «bajo area no pavimentada» y
# «sobre pavimento flexible» en la MISMA celda, de modo que las tres opciones
# de 'condicion_pavimento' son dos filas. Para el HDPE separa «unpaved» de
# «paved» -- sin distinguir flexible de rigido --, y las tres opciones vuelven
# a ser dos, pero AGRUPADAS AL REVES. Para el metal corrugado son una sola.
# Colapsar el criterio a las dos filas del concreto romperia el HDPE, y al
# reves. No es laguna de la fuente: la fuente cubre su dominio entero. Es una
# diferencia de granularidad, y esta escrita aqui porque leerla al reves es
# justo lo que hace falta para calcular de menos.
_TIPO_FUERA = NoUsada(por_que_no=(
    "el catalogo de conductos de la Sec. 3.2 no ofrece esta forma ni este "
    "material. Se transcribe porque sin las trece filas no se ve que la "
    "columna «Condition» esta vacia -- em-dash impreso -- en once de ellas, "
    "que es exactamente lo que el expediente leia al reves"))

_FILAS_COBERTURA = (
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#cmp",
        etiqueta_literal="Corrugated Metal Pipe",
        valores={"condicion": "—", "cobertura": "S/8 ≥ 12.0 in."},
        uso=Usada(por=("criterios_adoptados['cobertura_minima_aashto']",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#spiral_acero",
        jerarquia=("Spiral Rib Metal Pipe",),
        etiqueta_literal="Steel Conduit",
        valores={"condicion": "Steel Conduit", "cobertura": "S/4 ≥ 12.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#spiral_alum_le48",
        jerarquia=("Spiral Rib Metal Pipe",),
        etiqueta_literal="Aluminum Conduit where S ≤ 48.0 in.",
        valores={"condicion": "Aluminum Conduit where S ≤ 48.0 in.",
                 "cobertura": "S/2 ≥ 12.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#spiral_alum_gt48",
        jerarquia=("Spiral Rib Metal Pipe",),
        etiqueta_literal="Aluminum Conduit where S > 48.0 in.",
        valores={"condicion": "Aluminum Conduit where S > 48.0 in.",
                 "cobertura": "S/2.75 ≥ 24.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#structural_plate",
        etiqueta_literal="Structural Plate Pipe Structures",
        valores={"condicion": "—", "cobertura": "S/8 ≥ 12.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#long_span",
        etiqueta_literal="Long-Span Structural Plate Pipe Structures",
        valores={"condicion": "—",
                 "cobertura": CeldaSinValor.REMITE_A_OTRA_TABLA},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#box",
        etiqueta_literal="Structural Plate Box Structures",
        valores={"condicion": "—",
                 "cobertura": CeldaSinValor.REMITE_A_OTRA_TABLA},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#deep_corrugated",
        etiqueta_literal="Deep Corrugated Structural Plate Structures",
        valores={"condicion": "—",
                 "cobertura": CeldaSinValor.REMITE_A_OTRA_TABLA},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#fiberglass",
        etiqueta_literal="Fiberglass Pipe",
        valores={"condicion": "—", "cobertura": "12.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#termo_no_pavimentado",
        jerarquia=("Thermoplastic Pipe",),
        etiqueta_literal="Under unpaved areas",
        valores={"condicion": "Under unpaved areas",
                 "cobertura": "ID/8 ≥ 12.0 in."},
        uso=Usada(por=("criterios_adoptados['cobertura_minima_aashto']",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#termo_pavimentado",
        jerarquia=("Thermoplastic Pipe",),
        etiqueta_literal="Under paved roads",
        valores={"condicion": "Under paved roads",
                 "cobertura": "ID/2 ≥ 24.0 in."},
        uso=Usada(por=("criterios_adoptados['cobertura_minima_aashto']",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#steel_reinforced_termo",
        etiqueta_literal="Steel-Reinforced Thermoplastic Culverts",
        valores={"condicion": "—", "cobertura": "S/5 ≥ 12.0 in."},
        uso=_TIPO_FUERA),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#rcp_no_rigido",
        jerarquia=("Reinforced Concrete Pipe",),
        etiqueta_literal=("Under unpaved areas or top of flexible pavement"),
        valores={"condicion": ("Under unpaved areas or top of flexible "
                               "pavement"),
                 "cobertura": ("Bc/8 or B'c/8, whichever is greater, "
                               "≥ 12.0 in.")},
        uso=Usada(por=("criterios_adoptados['cobertura_minima_aashto']",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T12.6.6.3-1#rcp_rigido",
        jerarquia=("Reinforced Concrete Pipe",),
        etiqueta_literal="Under bottom of rigid pavement",
        valores={"condicion": "Under bottom of rigid pavement",
                 "cobertura": "9.0 in."},
        uso=Usada(por=("criterios_adoptados['cobertura_minima_aashto']",))),
)

T_COBERTURA_MINIMA = _tabla(
    id="AASHTO_LRFD_9.T12.6.6.3-1",
    cita_id="AASHTO_LRFD_9.T12.6.6.3-1",
    titulo_literal="Table 12.6.6.3-1—Minimum Cover",
    texto_previo=Verbatim(
        texto=("The minimum cover, including a well-compacted granular "
               "subbase and base course, shall not be less than that "
               "specified in Table 12.6.6.3-1"),
        pagina_pdf=1659),
    columnas=(
        ColumnaDeTabla(id="tipo", etiqueta_literal="Type", unidad="",
                       uso=Usada(por=(
                           "criterios_adoptados['cobertura_minima_aashto']",))),
        # LA COLUMNA QUE EL EXPEDIENTE CREIA QUE ERAN TRES COLUMNAS.
        ColumnaDeTabla(id="condicion", etiqueta_literal="Condition", unidad="",
                       uso=Usada(por=("criterios_adoptados["
                                      "'condicion_pavimento']",))),
        ColumnaDeTabla(id="cobertura", etiqueta_literal="Minimum Cover*",
                       unidad="in / ft (ver la nota de unidades mixtas)",
                       uso=Usada(por=(
                           "criterios_adoptados['cobertura_minima_aashto']",))),
    ),
    filas=_FILAS_COBERTURA,
    notas_al_pie=(
        NotaAlPie(marca="*", texto=Verbatim(
            texto=("Minimum cover taken from top of rigid pavement or bottom "
                   "of flexible pavement"),
            pagina_pdf=1660)),
    ),
    alcance=Integra(),
    vistas_de_calculo=("cobertura_minima_aashto",),
)


# ===========================================================================
# AASHTO LRFD 9a ed. — Tabla 5.10.1-1, recubrimiento minimo
# ===========================================================================
# LA OTRA MITAD DEL CRUCE. La Tabla 2.9.1.5.5.3-1 del Manual de Puentes es
# esta misma tabla traducida, con UNA sola columna -- la de acero no
# protegido, que aqui es la Categoria A --, y `M9._recubrimiento_aashto_
# detallado` las cruza con la regla del mayor de Sec. 0.2. Ese cruce se hacia
# con `situacion in RECUBRIMIENTO_MP_MM` y SE SALTABA SIN AVISAR en las ocho
# filas de la familia de pilotes; la correspondencia declarada de mas abajo,
# guardada por T19, es lo que lo impide.
#
# LA TABLA IMPRIME PULGADAS Y NADA MAS. La unidad se declara UNA VEZ, en el
# titulo -- «(in.)» --, y las celdas van sin simbolo; el unico numero del
# cuerpo que no es una pulgada es el «2.0 ft» del rotulo de relleno. Los mm
# son CONVERSION DEL PROYECTO (1 in = 25.4 mm exacto), no valor de la fuente,
# y por eso las dos columnas viven juntas en cada fila: sin la pulgada al lado
# no se puede comprobar la conversion, y ahi es donde nacio el «75 mm» que el
# expediente arrastro (3.0 in son 76.2, no 75).
#
# NO TIENE NI UNA LLAMADA: ni asterisco, ni superindice, ni cruz, ni en el
# titulo ni en ninguna celda. Lo que hay bajo la tabla son tres renglones
# corridos que DEFINEN las categorias, sin marca que los ate a nada, y por eso
# entran como notas de marca vacia -- que es lo que la pagina hace.
#
# QUE DECIDE ENTRE «Noncorrosive» Y «Corrosive», y donde vive: la definicion
# («greater than or equal to 500 ppm of chlorides»…) esta en el COMENTARIO
# C5.10.1, columna derecha de la pag. impresa 5-168, NO en el articulado. Es
# un dato de categoria, no de numero, y se declara porque tratar un comentario
# como exigencia es el mismo genero de defecto que este cluster persigue. No
# afecta a este expediente: sus dos filas usadas estan fuera de la familia de
# pilotes.
# LA CONDICION QUE NADIE HABIA DECLARADO (NOR-AAS-01). La tabla tiene tres
# columnas y el expediente leia una sola: los 3.0 in de «Coastal» son de la
# Categoria A, y con B o C la tabla baja a 2.0 in = 50.8 mm, con lo que la
# regla del mayor de Sec. 0.2 la pasaria a ganar E.060. Cual de las tres
# aplica no lo dice ninguna norma -- lo dice la especificacion del acero de
# este expediente --, y por eso el criterio esta VACIO y bloquea.
_COND_CATEGORIA_REFUERZO = CondicionAplicacion(
    id="COND-CATEGORIA-REFUERZO",
    texto=Verbatim(
        texto=("Category A—Uncoated reinforcing steel meeting AASHTO "
               "M 31M/M 31"),
        pagina_pdf=528),
    cita_id="AASHTO_LRFD_9.T5.10.1-1",
    resuelve=PorCriterio(clave="categoria_refuerzo_aashto"),
)

_NO_USADA_AASHTO = NoUsada(por_que_no=(
    "el emparejamiento 'situacion_recubrimiento_aashto' no lleva ninguna "
    "condicion de E.060 a esta fila. Se transcribe entera porque es lo que "
    "deja ver que hay TRES columnas y que la eleccion de categoria puede "
    "invertir quien gobierna el recubrimiento"))

_FILAS_RECUB_AASHTO = (
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#agua_salada",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Direct exposure to salt water",
        valores={"cat_a_in": 4.0, "cat_b_in": 2.5, "cat_c_in": 2.5,
                 "cat_a_mm": 101.6, "cat_b_mm": 63.5,
                 "cat_c_mm": 63.5},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#vaciado_contra_suelo",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Cast against earth",
        valores={"cat_a_in": 3.0, "cat_b_in": 2.0, "cat_c_in": 2.0,
                 "cat_a_mm": 76.2, "cat_b_mm": 50.8,
                 "cat_c_mm": 50.8},
        condiciones=(_COND_CATEGORIA_REFUERZO,),
        uso=Usada(por=("M9._recubrimiento_aashto_detallado",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#costera",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Coastal",
        valores={"cat_a_in": 3.0, "cat_b_in": 2.0, "cat_c_in": 2.0,
                 "cat_a_mm": 76.2, "cat_b_mm": 50.8,
                 "cat_c_mm": 50.8},
        condiciones=(_COND_CATEGORIA_REFUERZO,),
        uso=Usada(por=("M9._recubrimiento_aashto_detallado",))),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#sales_anticongelantes",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Exposure to deicing salts",
        valores={"cat_a_in": 2.5, "cat_b_in": 2.0, "cat_c_in": 1.5,
                 "cat_a_mm": 63.5, "cat_b_mm": 50.8,
                 "cat_c_mm": 38.1},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#tableros_neumaticos_clavos",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Deck surfaces subject to tire stud or chain wear",
        valores={"cat_a_in": 2.5, "cat_b_in": 2.5, "cat_c_in": 2.0,
                 "cat_a_mm": 63.5, "cat_b_mm": 63.5,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#exterior_no_superior",
        jerarquia=("Severe to Moderate Exposure",),
        etiqueta_literal="Other than noted above",
        valores={"cat_a_in": 2.0, "cat_b_in": 2.0, "cat_c_in": 1.5,
                 "cat_a_mm": 50.8, "cat_b_mm": 50.8,
                 "cat_c_mm": 38.1},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#interior_hasta_n11",
        jerarquia=("Limited Exposure", "Other than noted below"),
        etiqueta_literal="Up to No. 11 bar",
        valores={"cat_a_in": 1.5, "cat_b_in": 1.0, "cat_c_in": 1.0,
                 "cat_a_mm": 38.1, "cat_b_mm": 25.4,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#interior_n14_n18",
        jerarquia=("Limited Exposure", "Other than noted below"),
        etiqueta_literal="No. 14 and No. 18 bars",
        valores={"cat_a_in": 2.0, "cat_b_in": 2.0, "cat_c_in": 2.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 50.8,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#losa_in_situ_inferior_hasta_n11",
        jerarquia=("Limited Exposure", "Bottom of cast-in-place slabs"),
        etiqueta_literal="Up to No. 11 bar",
        valores={"cat_a_in": 1.0, "cat_b_in": 1.0, "cat_c_in": 1.0,
                 "cat_a_mm": 25.4, "cat_b_mm": 25.4,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#losa_in_situ_inferior_n14_n18",
        jerarquia=("Limited Exposure", "Bottom of cast-in-place slabs"),
        etiqueta_literal="No. 14 and No. 18 bars",
        valores={"cat_a_in": 2.0, "cat_b_in": 2.0, "cat_c_in": 2.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 50.8,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#paneles_prefabricados_encofrados",
        jerarquia=("Limited Exposure",),
        etiqueta_literal="Precast soffit form panels",
        valores={"cat_a_in": 0.8, "cat_b_in": 0.8, "cat_c_in": 0.8,
                 "cat_a_mm": 20.32, "cat_b_mm": 20.32,
                 "cat_c_mm": 20.32},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_prefab_armado_no_corrosivo",
        jerarquia=("Piling", "Precast reinforced piles"),
        etiqueta_literal="Noncorrosive environments",
        valores={"cat_a_in": 2.0, "cat_b_in": 1.5, "cat_c_in": 1.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 38.1,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_prefab_armado_corrosivo",
        jerarquia=("Piling", "Precast reinforced piles"),
        etiqueta_literal="Corrosive environments",
        valores={"cat_a_in": 3.0, "cat_b_in": 2.5, "cat_c_in": 2.0,
                 "cat_a_mm": 76.2, "cat_b_mm": 63.5,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_prefab_pretensado",
        jerarquia=("Piling",),
        etiqueta_literal="Precast prestressed piles",
        valores={"cat_a_in": 2.0, "cat_b_in": 1.0, "cat_c_in": 1.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 25.4,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_in_situ_no_corrosivo",
        jerarquia=("Piling", "Cast-in-place piles"),
        etiqueta_literal="Noncorrosive environments",
        valores={"cat_a_in": 2.0, "cat_b_in": 1.5, "cat_c_in": 1.5,
                 "cat_a_mm": 50.8, "cat_b_mm": 38.1,
                 "cat_c_mm": 38.1},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_in_situ_corrosivo",
        jerarquia=("Piling", "Cast-in-place piles"),
        etiqueta_literal="Corrosive environments",
        valores={"cat_a_in": 3.0, "cat_b_in": 2.5, "cat_c_in": 2.0,
                 "cat_a_mm": 76.2, "cat_b_mm": 63.5,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_in_situ_cascaras",
        jerarquia=("Piling", "Cast-in-place piles"),
        etiqueta_literal="Shells",
        valores={"cat_a_in": 2.0, "cat_b_in": 1.5, "cat_c_in": 1.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 38.1,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#pilote_in_situ_tremie_o_lechada",
        jerarquia=("Piling", "Cast-in-place piles"),
        etiqueta_literal="Auger-cast, tremie concrete, or slurry construction",
        valores={"cat_a_in": 3.0, "cat_b_in": 2.5, "cat_c_in": 2.0,
                 "cat_a_mm": 76.2, "cat_b_mm": 63.5,
                 "cat_c_mm": 50.8},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#alcantarilla_cajon_prefab_losa_de_rodadura",
        jerarquia=("Precast Culverts",),
        etiqueta_literal="Top slabs used as a driving surface",
        valores={"cat_a_in": 2.5, "cat_b_in": 2.0, "cat_c_in": 1.5,
                 "cat_a_mm": 63.5, "cat_b_mm": 50.8,
                 "cat_c_mm": 38.1},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#alcantarilla_cajon_prefab_losa_menos_2_pies",
        jerarquia=("Precast Culverts",),
        etiqueta_literal="Top slabs with less than 2.0 ft of fill",
        valores={"cat_a_in": 2.0, "cat_b_in": 1.5, "cat_c_in": 1.0,
                 "cat_a_mm": 50.8, "cat_b_mm": 38.1,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
    FilaDeTabla(
        id="AASHTO_LRFD_9.T5.10.1-1#alcantarilla_cajon_prefab_otros_miembros",
        jerarquia=("Precast Culverts",),
        etiqueta_literal="All other members",
        valores={"cat_a_in": 1.0, "cat_b_in": 1.0, "cat_c_in": 1.0,
                 "cat_a_mm": 25.4, "cat_b_mm": 25.4,
                 "cat_c_mm": 25.4},
        uso=_NO_USADA_AASHTO),
)

T_AASHTO_RECUBRIMIENTO = _tabla(
    id="AASHTO_LRFD_9.T5.10.1-1",
    cita_id="AASHTO_LRFD_9.T5.10.1-1",
    titulo_literal=("Table 5.10.1-1—Minimum Cover for Main Reinforcing Steel "
                    "(in.)"),
    encabezados_superiores=("Reinforcing Material Category",),
    texto_previo=Verbatim(
        texto=("Cover for prestressing and reinforcing steel shall not be "
               "less than that specified in Table 5.10.1-1 and modified for "
               "W/CM ratio."),
        pagina_pdf=526),
    columnas=(
        ColumnaDeTabla(id="situacion", etiqueta_literal="Situation", unidad="",
                       uso=Usada(por=(
                           "M9._recubrimiento_aashto_detallado",))),
        ColumnaDeTabla(id="cat_a_in", etiqueta_literal="A", unidad="in",
                       uso=NoUsada(por_que_no=(
                           "el calculo opera en SI y consume la columna en "
                           "mm; la pulgada es la unidad IMPRESA y sin ella la "
                           "conversion no se puede comprobar"))),
        ColumnaDeTabla(id="cat_b_in", etiqueta_literal="B", unidad="in",
                       uso=NoUsada(por_que_no="idem cat_a_in")),
        ColumnaDeTabla(id="cat_c_in", etiqueta_literal="C", unidad="in",
                       uso=NoUsada(por_que_no="idem cat_a_in")),
        # LAS TRES COLUMNAS EN mm NO ESTAN IMPRESAS: son la conversion del
        # proyecto, declarada como tal. Van en la tabla y no en el consumidor
        # para que la conversion ocurra UNA vez y se pueda auditar contra la
        # pulgada de al lado.
        ColumnaDeTabla(id="cat_a_mm",
                       etiqueta_literal="A (conversion del proyecto)",
                       unidad="mm",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CATEGORIA-REFUERZO")),
        ColumnaDeTabla(id="cat_b_mm",
                       etiqueta_literal="B (conversion del proyecto)",
                       unidad="mm",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CATEGORIA-REFUERZO")),
        ColumnaDeTabla(id="cat_c_mm",
                       etiqueta_literal="C (conversion del proyecto)",
                       unidad="mm",
                       uso=PendienteDeCondicion(
                           condicion_id="COND-CATEGORIA-REFUERZO")),
    ),
    filas=_FILAS_RECUB_AASHTO,
    notas_al_pie=(
        NotaAlPie(marca="", texto=Verbatim(
            texto=("Category A—Uncoated reinforcing steel meeting AASHTO "
                   "M 31M/M 31"),
            pagina_pdf=528)),
        NotaAlPie(marca="", texto=Verbatim(
            texto=("Category B—Epoxy coated or galvanized meeting ASTM "
                   "A775/A775M"),
            pagina_pdf=528)),
        NotaAlPie(marca="", texto=Verbatim(
            texto="Category C—Materials meeting AASHTO M 334M/M 334",
            pagina_pdf=528)),
    ),
    modificadores=(),
    alcance=Integra(),
    vistas_de_calculo=("tabla_recubrimiento_aashto_mm",),
)


# ===========================================================================
# La correspondencia entre el piso peruano y la tabla de AASHTO
# ===========================================================================
CORR_RECUBRIMIENTO = CorrespondenciaDeTablas(
    id="CORR-RECUBRIMIENTO",
    tabla_a="AASHTO_LRFD_9.T5.10.1-1",
    tabla_b="MP.TRECUB",
    pares={
        "agua_salada": ("agua_salada",),
        "alcantarilla_cajon_prefab_losa_de_rodadura": ("alcantarilla_cajon_prefab_losa_de_rodadura",),
        "alcantarilla_cajon_prefab_losa_menos_2_pies": ("alcantarilla_cajon_prefab_losa_menos_2_pies",),
        "alcantarilla_cajon_prefab_otros_miembros": ("alcantarilla_cajon_prefab_otros_miembros",),
        "costera": ("costera",),
        "exterior_no_superior": ("exterior_no_superior",),
        "interior_hasta_n11": ("interior_hasta_n11",),
        "interior_n14_n18": ("interior_n14_n18",),
        "losa_in_situ_inferior_hasta_n11": ("losa_in_situ_inferior_hasta_n11",),
        "losa_in_situ_inferior_n14_n18": ("losa_in_situ_inferior_n14_n18",),
        "paneles_prefabricados_encofrados": ("paneles_prefabricados_encofrados",),
        "pilote_in_situ_cascaras": ("pilar_in_situ_cascaras",),
        "pilote_in_situ_corrosivo": ("pilar_in_situ_corrosivo_general", "pilar_in_situ_corrosivo_protegida"),
        "pilote_in_situ_no_corrosivo": ("pilar_in_situ_no_corrosivo",),
        "pilote_in_situ_tremie_o_lechada": ("pilar_in_situ_tremie_o_lechada",),
        "pilote_prefab_armado_corrosivo": ("pilar_prefabricado_corrosivo",),
        "pilote_prefab_armado_no_corrosivo": ("pilar_prefabricado_no_corrosivo",),
        "pilote_prefab_pretensado": ("pilote_prefabricado_pretensado",),
        "sales_anticongelantes": ("sales_anticongelantes",),
        "tableros_neumaticos_clavos": ("tableros_neumaticos_clavos",),
        "vaciado_contra_suelo": ("vaciado_contra_suelo",),
    },
    regla_al_cruzar=(
        "Sec. 0.2, regla del conflicto: RIGE EL MAYOR. Se compara la columna "
        "de la Categoria A de AASHTO -- la de acero NO protegido -- contra la "
        "columna unica del Manual, que es la misma. Con categoria B o C el "
        "corpus peruano no tabula y el valor sale de AASHTO como [C], sin "
        "cruce que hacer. Cuando el Manual parte en dos una fila de AASHTO se "
        "toma el MAYOR de las dos subfilas, que es lo que hace la misma regla "
        "cuando una fuente detalla mas que la otra."),
    diferencias_declaradas=(
        "El Manual traduce «shafts» por «Pilares» donde la transcripcion de "
        "AASHTO dice «pilote»: las ocho filas de la familia de pilotes NO se "
        "cruzan por nombre de clave, y ahi estaba el defecto -- `situacion in "
        "RECUBRIMIENTO_MP_MM` daba False y el cruce se saltaba SIN AVISAR.",
        "El Manual PARTE EN DOS la fila «Cast-in-place piles / Corrosive "
        "environments»: «En general» y «Armadura protegida». Del lado de "
        "AASHTO es una sola, y las dos subfilas traen el mismo 3.0 in.",
        "AASHTO imprime TRES columnas de categoria de material y el Manual "
        "UNA, la de aceros no protegidos, que corresponde a la Categoria A. "
        "No es una diferencia de valores: es que el Manual cubre una sola de "
        "las tres.",
        "AASHTO imprime PULGADAS y nada mas; los mm de las dos "
        "transcripciones son conversion, exacta (1 in = 25.4 mm) pero del "
        "proyecto. De redondearla mal salio el «75 mm» que el expediente "
        "arrastro por 3.0 in = 76.2 mm.",
    ),
)

CORRESPONDENCIAS: Dict[str, CorrespondenciaDeTablas] = {
    c.id: c for c in (CORR_RECUBRIMIENTO,)
}

TABLAS: Dict[str, TablaNormativa] = {t.id: t for t in _TODAS}
