"""
ML_licuefaccion.py
==================
Fase 0-bis de la hoja de ruta: la evaluacion de licuefaccion, como RESULTADO
DECLARADO del estudio de mecanica de suelos (VE-5, lote catlic; decision del
dueño adoptada en el censo de pendientes del 2026-11-20, item 6).

Que hace
--------
Este modulo NO calcula el potencial de licuacion --la calculadora CSR/CRR de
Seed e Idriss / NCEER que E.050 38.5 nombra queda fuera del alcance--. Hace
tres cosas, por punto y a nivel de EXPEDIENTE (la corrida de perfil lo difiere
entero: la Fase 0-bis, punto 3, dice que a nivel de perfil se declara el
condicionante y se remite la solucion al expediente):

    1. Decide si AASHTO LRFD 10.5.4.2 (pag. impresa 10-34, PDF 1323) EXIGE la
       evaluacion: «A liquefaction assessment shall be conducted for Seismic
       Zones 3 and 4 if both of the following conditions are present»:
       el nivel freatico en los 50.0 ft superiores y suelo con las
       caracteristicas del numeral. La zona es el [S] 'zona_sismica_aashto'
       (sin leer, NO se supone 1 ni 2: hoja de ruta Sec. 9.2, nota VE3-20); el
       NF es la columna `NF_profundidad_m` del punto; la condicion de suelo
       solo la puede descartar el EMS ((N1)60, q_c1N o V_s1), y mientras no
       la descarte se PRESUME, con el perfil presunto de E.030
       ('PERFIL_SUELO_PRESUNTO') dicho al lado.

    2. Exige el RESULTADO del EMS donde la evaluacion es exigible: E.050
       38.3 (pag. 51) pone el analisis en el EMS, a cargo de su PR --«el PR
       debe incluir en su EMS un análisis determinístico y probabilístico del
       Potencial de Licuación de la zona»--. Sin el dato `licuefaccion_ems`
       del punto (o de `globales`), `DatoFaltanteError`: el expediente no
       cierra.

    3. Contrasta el resultado declarado con lo que el proyecto adopta: la
       demanda sismica ('demanda_sismica_licuefaccion', Tr = 1000 años, v8
       Sec. 0.6) y la magnitud ('Mw_licuefaccion', v8 Sec. 0.6: sin ella la
       evaluacion no es ejecutable); y un resultado «licua» sin medida de
       mitigacion es `DatoFaltanteError` sobre la mitigacion. Una mitigacion
       declarada se imprime y NO se verifica.

Decisiones de VE-5 (decision pendiente de Fable, tomadas del lado seguro):
    * el dato es POR PUNTO, con `globales` admitido (el 38.3 habla del
      potencial «de la zona»; el NF y el suelo varian por cruce): el del punto
      gana;
    * la magnitud del EMS no puede ser MENOR que la adoptada: una M_w mayor
      baja el factor de escala de magnitud y es el lado seguro;
    * el periodo de retorno del EMS no puede ser menor que el adoptado.

Y la clase de sitio MEDIDA (item 4 de la Sec. 5 del censo, VE-5)
-----------------------------------------------------------------
La v8 (Sec. 0.5 y Fase 0-bis, punto 2) pone juntas las dos preguntas que
solo el EMS cierra: la licuefaccion y la clase de sitio de AASHTO. Mientras
'clase_sitio' [S] siga sin valor, nada cambia --la cadena sismica lee las
filas declaradas en 'F_pga' [A], y M9 no se toca--. Cuando el EMS la DECLARA,
`contrastar_clase_sitio` la contrasta con esas filas: la fila F exige el
procedimiento especifico de sitio (AASHTO 3.10.2, «shall»: metodo no
evaluable); una clase fuera de las filas declaradas deja a 'F_pga' sin
sostener (dato invalido); una clase dentro de varias filas se AVISA, con el
factor medido al lado de la envolvente.

Excepciones
-----------
    DatoFaltanteError         falta el resultado del EMS donde se exige, o la
                              mitigacion de un suelo que licua.
    DatoInvalidoError         el resultado declarado mal formado (al cargar),
                              una zona fuera de 1 a 4, un Tr o una M_w por
                              debajo de lo adoptado.
    CriterioPendienteError    'Mw_licuefaccion' sin declarar cuando el EMS
                              trae su resultado (no hay contra que
                              contrastarlo).
"""

from __future__ import annotations

import math
import numbers
from typing import Any, Optional, Tuple

from src import criterios_adoptados as ca
from src import datos_sitio as ds
from src.constantes_normativas import (PROF_NF_LICUEFACCION_PIE,
                                       PROF_NF_LICUEFACCION_SI,
                                       ZONA_SISMICA_LICUEFACCION_A_CONSIDERAR,
                                       ZONAS_SISMICAS_AASHTO,
                                       ZONAS_SISMICAS_EXIGEN_LICUEFACCION)
from src.constantes_normativas import F_PGA_EXIGE_ESTUDIO_DE_SITIO, F_PGA_TABLA
from src.modelos import (CIFRAS_FACTOR, CIFRAS_MAGNITUD, DatoFaltanteError,
                         DatoInvalidoError, EstadoDeVerificacion, Magnitud,
                         MetodoNoEvaluableError,
                         ReferenciaNormativa, TipoDeVeredicto, Umbral,
                         Verificacion, Veredicto, paso)
from src.modulos import M9_cabezal as M9
from src.tolerancias import TOL_UMBRAL_NORMATIVO

CLAVE_LICUEFACCION_EMS = "licuefaccion_ems"
RESULTADO_NO_LICUA = "no_licua"
RESULTADO_LICUA = "licua"
RESULTADOS = (RESULTADO_NO_LICUA, RESULTADO_LICUA)
CAMPOS_DE_TRAZA = ("documento", "fecha", "metodo")
CAMPO_MITIGACION = "mitigacion"
CAMPO_MW = "Mw"
CAMPO_TR = "periodo_retorno_anios"
CAMPOS = ("resultado", CAMPO_MW, CAMPO_TR, CAMPO_MITIGACION) + CAMPOS_DE_TRAZA

CRITERIO_MW = "Mw_licuefaccion"
CRITERIO_TR = "demanda_sismica_licuefaccion"
CRITERIO_PERFIL = "PERFIL_SUELO_PRESUNTO"
DATO_ZONA = "zona_sismica_aashto"
PERFIL_LICUABLE_E030 = "S5"

CODIGO_LICUEFACCION = "0B.1"
CITA_AASHTO = "AASHTO_LRFD_9.10.5.4.2"
CITA_E050 = "E050.38.3"
NUMERAL_LICUEFACCION = ReferenciaNormativa(
    seccion_hoja_ruta="Fase 0-bis",
    numeral_norma="AASHTO LRFD 9a ed., 10.5.4.2, pag. impresa 10-34; RNE "
                  "E.050, Art. 38.3, pag. 51",
)
ETAPA_LICUEFACCION = ("evaluacion de licuefaccion (Fase 0-bis; AASHTO "
                      "10.5.4.2, E.050 38.3)")


# ===========================================================================
# La puerta: el resultado declarado, al cargar
# ===========================================================================

def _texto(campo: str, valor: Any, *, vacio_admitido: bool = False) -> str:
    if not isinstance(valor, str) or (not vacio_admitido and not valor.strip()):
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.{campo}", valor=valor,
            motivo="tiene que ser un texto"
                   + ("" if vacio_admitido else " no vacio"))
    return valor.strip()


def validar_licuefaccion_declarada(bruto: Any) -> dict:
    """
    Forma y dominio del dato `licuefaccion_ems` (E.050 38.3: el resultado
    del analisis del EMS), al CARGAR `--datos-externos`:

        {"resultado": "no_licua" | "licua",
         "Mw": <real > 0>, "periodo_retorno_anios": <entero > 0>,
         "mitigacion": "<texto; obligatorio si licua>",
         "documento": "...", "fecha": "...", "metodo": "..."}

    La mitigacion de un suelo que licua puede faltar AQUI: su ausencia no es
    un dato mal escrito sino uno que falta, y la detiene la Fase 0-bis como
    bloqueo del expediente (`evaluar_licuefaccion`).
    """
    if not isinstance(bruto, dict):
        raise DatoInvalidoError(
            CLAVE_LICUEFACCION_EMS, valor=bruto,
            motivo="es un objeto con " + ", ".join(CAMPOS))
    sobran = sorted(set(bruto) - set(CAMPOS))
    if sobran:
        raise DatoInvalidoError(
            CLAVE_LICUEFACCION_EMS, valor=", ".join(sobran),
            motivo="campos no reconocidos; los admitidos son "
                   + ", ".join(CAMPOS))
    resultado = bruto.get("resultado")
    if resultado not in RESULTADOS:
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.resultado", valor=resultado,
            motivo="es " + " o ".join(RESULTADOS))
    Mw = bruto.get(CAMPO_MW)
    if isinstance(Mw, bool) or not isinstance(Mw, numbers.Real) \
            or not (math.isfinite(Mw) and Mw > 0):
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.{CAMPO_MW}", valor=Mw,
            motivo="la magnitud con que el EMS evaluo es un real finito "
                   "positivo")
    Tr = bruto.get(CAMPO_TR)
    if isinstance(Tr, bool) or not isinstance(Tr, int) or not Tr > 0:
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.{CAMPO_TR}", valor=Tr,
            motivo="el periodo de retorno del sismo con que el EMS evaluo es "
                   "un entero positivo, en años")
    normal = {"resultado": resultado, CAMPO_MW: float(Mw), CAMPO_TR: Tr,
              CAMPO_MITIGACION: _texto(CAMPO_MITIGACION,
                                       bruto.get(CAMPO_MITIGACION, ""),
                                       vacio_admitido=True)}
    for campo in CAMPOS_DE_TRAZA:
        normal[campo] = _texto(campo, bruto.get(campo))
    return normal


# ===========================================================================
# La Fase 0-bis de un punto
# ===========================================================================

def _zona_leida() -> Optional[int]:
    """
    La zona sismica de AASHTO si el [S] tiene lectura (la registra como
    usada), o None si sigue sin leer. NO es un valor por defecto: sin lectura
    la funcion que llama no supone zona 1 ni 2 y lo dice en su bloqueo.
    """
    if ds.dato_efectivo(DATO_ZONA).valor is None:
        return None
    zona = ds.valor(DATO_ZONA)
    if zona not in ZONAS_SISMICAS_AASHTO:
        raise DatoInvalidoError(
            DATO_ZONA, valor=zona,
            motivo="AASHTO 3.10.6 asigna una de las cuatro zonas sismicas "
                   "(1 a 4) de la Tabla 3.10.6-1")
    return zona


def _no_aplica(id_punto: str, motivo: str, avisos: Tuple[str, ...],
               sustitucion: Tuple[Magnitud, ...]) -> Verificacion:
    p = paso(
        "F0.LICUEFACCION", codigo=CODIGO_LICUEFACCION,
        que="Evaluacion de licuefaccion del punto (AASHTO 10.5.4.2)",
        formula="exigible si zona sismica en {3, 4} y NF <= 50.0 ft y suelo "
                "con las caracteristicas del numeral",
        formula_cita_id=CITA_AASHTO,
        citas_textuales=(CITA_AASHTO, CITA_E050),
        sustitucion=sustitucion,
        resultado=Magnitud("evaluacion", "no exigida por 10.5.4.2", "",
                           motivo, cifras=None),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion=motivo))
    return Verificacion(
        cumple=True, numeral=NUMERAL_LICUEFACCION, valor_obtenido=None,
        valor_admisible=None, criterio_aplicado=None,
        codigo=CODIGO_LICUEFACCION, paso=p,
        estado=EstadoDeVerificacion.NO_APLICA, motivo_no_aplica=motivo,
        avisos=avisos)


def evaluar_licuefaccion(*, id_punto: str,
                         NF_profundidad_m: Optional[float],
                         declarada: Optional[dict]) -> Verificacion:
    """
    La Fase 0-bis del punto. AASHTO LRFD 9a ed., 10.5.4.2 (pag. impresa
    10-34) decide si la evaluacion es exigible; RNE E.050 Art. 38.3 (pag. 51)
    la pone en el EMS. Ver el docstring del modulo.

    `declarada` es el `licuefaccion_ems` validado del punto (o de
    `globales`), o None. `NF_profundidad_m` es la columna del CSV (m bajo el
    terreno), o None si el punto no la trae.
    """
    if declarada is not None:
        return _contrastar_declarada(id_punto, declarada)

    zona = _zona_leida()
    sustitucion = [
        Magnitud("zona", "sin leer" if zona is None else zona, "",
                 f"dato de sitio [S] '{DATO_ZONA}' (AASHTO 3.10.6)",
                 cifras=None),
        Magnitud("NF", "sin dato" if NF_profundidad_m is None
                 else NF_profundidad_m, "" if NF_profundidad_m is None else "m",
                 "columna NF_profundidad_m del punto",
                 cifras=None if NF_profundidad_m is None else CIFRAS_MAGNITUD),
    ]
    if zona is not None and zona not in ZONAS_SISMICAS_EXIGEN_LICUEFACCION:
        avisos: Tuple[str, ...] = ()
        if zona == ZONA_SISMICA_LICUEFACCION_A_CONSIDERAR:
            avisos = (f"licuefaccion: en la Zona sismica "
                      f"{ZONA_SISMICA_LICUEFACCION_A_CONSIDERAR} AASHTO "
                      "10.5.4.2 pide considerarla («should also be "
                      "considered») si hay arenas sueltas a muy sueltas "
                      "saturadas que afecten la estabilidad de la obra; no la "
                      "exige y el expediente no se detiene",)
        return _no_aplica(
            id_punto, f"Zona sismica {zona}: AASHTO 10.5.4.2 exige la "
            "evaluacion solo en las zonas 3 y 4", avisos, tuple(sustitucion))
    if NF_profundidad_m is not None and \
            not NF_profundidad_m <= PROF_NF_LICUEFACCION_SI + TOL_UMBRAL_NORMATIVO:
        return _no_aplica(
            id_punto, f"nivel freatico a {NF_profundidad_m:.2f} m, bajo los "
            f"{PROF_NF_LICUEFACCION_PIE:g} ft ({PROF_NF_LICUEFACCION_SI:.2f} m) "
            "de AASHTO 10.5.4.2", (), tuple(sustitucion))

    perfil = ca.valor(CRITERIO_PERFIL)
    Tr = ca.valor(CRITERIO_TR)
    por_que_zona = ("la zona sismica de AASHTO no esta leida "
                    f"('{DATO_ZONA}' sin valor) y la hoja de ruta (Sec. 9.2, "
                    "nota VE3-20) no admite suponerla 1 ni 2"
                    if zona is None else f"Zona sismica {zona}")
    por_que_nf = ("el punto no trae NF_profundidad_m y no se puede descartar "
                  "que el nivel freatico quede en los 50 ft superiores"
                  if NF_profundidad_m is None else
                  f"NF a {NF_profundidad_m:.2f} m, dentro de los "
                  f"{PROF_NF_LICUEFACCION_PIE:g} ft "
                  f"({PROF_NF_LICUEFACCION_SI:.2f} m)")
    por_que_suelo = ("la condicion de suelo ((N1)60, q_c1N o V_s1) solo la "
                     "puede descartar el EMS y se presume"
                     + (f"; el perfil presunto de E.030 es "
                        f"{PERFIL_LICUABLE_E030} «suelos potencialmente "
                        "licuables»" if perfil == PERFIL_LICUABLE_E030 else
                        f"; el perfil presunto de E.030 es {perfil}"))
    raise DatoFaltanteError(
        CLAVE_LICUEFACCION_EMS,
        detalle=(f"AASHTO 10.5.4.2 exige evaluar la licuefaccion ({por_que_zona}; "
                 f"{por_que_nf}; {por_que_suelo}) y E.050 38.3 pone ese "
                 "analisis en el EMS. Declarar el resultado del EMS en "
                 f"--datos-externos, clave '{CLAVE_LICUEFACCION_EMS}' "
                 "(resultado no_licua o licua, Mw, periodo_retorno_anios, "
                 "mitigacion si licua, documento, fecha y metodo), evaluado "
                 f"con a_max de Tr >= {Tr} años ('{CRITERIO_TR}') y la M_w "
                 f"que el proyecto adopte ('{CRITERIO_MW}')"
                 + ("" if zona is not None else
                    f"; o leer y declarar '{DATO_ZONA}' por sesion si la "
                    "obra esta en las zonas 1 o 2")))


def _contrastar_declarada(id_punto: str, declarada: dict) -> Verificacion:
    """El resultado del EMS contra lo que el proyecto adopta (v8 Sec. 0.6)."""
    Tr_adoptado = ca.valor(CRITERIO_TR)
    Tr = declarada[CAMPO_TR]
    if not Tr >= Tr_adoptado:
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.{CAMPO_TR}", valor=Tr,
            id_punto=id_punto,
            motivo=f"el EMS evaluo con un sismo de Tr = {Tr} años y el "
                   f"proyecto exige Tr = {Tr_adoptado} años al suelo "
                   f"('{CRITERIO_TR}', hoja de ruta Sec. 0.6): la evaluacion "
                   "no usa la demanda del expediente")
    Mw_adoptada = ca.valor(CRITERIO_MW)
    Mw = declarada[CAMPO_MW]
    if not Mw >= Mw_adoptada - TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            f"{CLAVE_LICUEFACCION_EMS}.{CAMPO_MW}", valor=Mw,
            id_punto=id_punto,
            motivo=f"el EMS evaluo con M_w = {Mw:g}, menor que la M_w = "
                   f"{Mw_adoptada:g} que el proyecto adopta ('{CRITERIO_MW}'): "
                   "una magnitud menor sube el factor de escala de magnitud "
                   "y no es el lado seguro")
    licua = declarada["resultado"] == RESULTADO_LICUA
    if licua and not declarada[CAMPO_MITIGACION]:
        raise DatoFaltanteError(
            f"{CLAVE_LICUEFACCION_EMS}.{CAMPO_MITIGACION}",
            detalle=("el EMS declara que el suelo LICUA y no declara la "
                     "medida de mitigacion; AASHTO 10.5.4.2 manda evaluar la "
                     "perdida de resistencia, el asentamiento y el flujo o "
                     "desplazamiento lateral, y la Fase 0-bis de la hoja de "
                     "ruta remite la solucion al mejoramiento del terreno: el "
                     "expediente no se cierra sin ella"))
    traza = (f"{declarada['documento']} ({declarada['fecha']}; "
             f"{declarada['metodo']})")
    avisos: Tuple[str, ...] = ()
    if licua:
        avisos = (f"licuefaccion: el EMS declara que el suelo LICUA ({traza}); "
                  f"mitigacion declarada: {declarada[CAMPO_MITIGACION]}. El "
                  "programa no la verifica",)
    explicacion = ("resultado del EMS declarado y contrastado con la demanda "
                   "y la magnitud adoptadas"
                   + ("; licua, con medida de mitigacion declarada"
                      if licua else ""))
    p = paso(
        "F0.LICUEFACCION", codigo=CODIGO_LICUEFACCION,
        que="Evaluacion de licuefaccion del punto: resultado declarado del EMS",
        formula="Tr_EMS >= Tr adoptado ; M_w EMS >= M_w adoptada ; si licua, "
                "medida de mitigacion declarada",
        formula_cita_id=CITA_E050,
        citas_textuales=(CITA_AASHTO, CITA_E050),
        sustitucion=(
            Magnitud("resultado", declarada["resultado"], "",
                     f"dato externo '{CLAVE_LICUEFACCION_EMS}': {traza}",
                     cifras=None),
            Magnitud("Tr_EMS", Tr, "años", "periodo de retorno del a_max del "
                     "EMS", cifras=None),
            Magnitud("Tr", Tr_adoptado, "años", f"criterio '{CRITERIO_TR}' [A]",
                     cifras=None),
            Magnitud("Mw_EMS", Mw, "", "magnitud con que evaluo el EMS",
                     cifras=CIFRAS_FACTOR),
            Magnitud("Mw", Mw_adoptada, "", f"criterio '{CRITERIO_MW}' [A]",
                     cifras=CIFRAS_FACTOR)),
        resultado=Magnitud("licuefaccion", declarada["resultado"], "",
                           traza, cifras=None),
        umbral=Umbral(
            descripcion="demanda sismica que el proyecto exige al suelo "
                        "(Tr del a_max) y magnitud adoptada",
            valor=f"Tr >= {Tr_adoptado} años ; M_w >= {Mw_adoptada:g}",
            unidad="", cita_id=CITA_AASHTO,
            caracter="EXIGENCIA de la evaluacion («A liquefaction assessment "
                     "shall be conducted»); la fuente no fija ni el Tr ni la "
                     "M_w con que se evalua",
            aplicacion="Umbral del proyecto: Tr y M_w son adopciones [A] "
                       "(hoja de ruta Sec. 0.6) y el EMS no puede evaluar por "
                       "debajo de ellas",
            criterio_aplicado=CRITERIO_TR),
        veredicto=Veredicto(tipo=TipoDeVeredicto.CUMPLE,
                            explicacion=explicacion),
        nota_del_proyecto=(
            "El programa no calcula el potencial de licuacion (la calculadora "
            "CSR/CRR esta fuera del alcance): exige el resultado del EMS, que "
            "E.050 38.3 pone a cargo de su PR, y lo contrasta con lo que el "
            "expediente adopta. Una mitigacion declarada no se verifica."))
    return Verificacion(
        cumple=True, numeral=NUMERAL_LICUEFACCION,
        valor_obtenido=declarada["resultado"],
        valor_admisible=f"Tr >= {Tr_adoptado} años, M_w >= {Mw_adoptada:g}",
        criterio_aplicado=CRITERIO_MW, codigo=CODIGO_LICUEFACCION, paso=p,
        avisos=avisos)


# ===========================================================================
# La clase de sitio medida frente a las filas de F_pga (VE-5, censo Sec. 5)
# ===========================================================================

CRITERIO_CLASE_SITIO = "clase_sitio"
DATO_PGA = "PGA_roca_B"
ETAPA_CLASE_SITIO = ("clase de sitio medida frente a las filas de 'F_pga' "
                     "(AASHTO 3.10.3.1 y 3.10.2)")
MOTIVO_METODO_NO_EVALUABLE_SITIO = (
    "método no evaluable (AASHTO 3.10.2, procedimiento específico de sitio)")


def contrastar_clase_sitio() -> Tuple[str, ...]:
    """
    La clase de sitio MEDIDA ('clase_sitio' [S]) contra las filas que
    'F_pga' [A] declara plausibles. AASHTO LRFD 9a ed., 3.10.3.1 (pag.
    impresa 3-101, cita AASHTO_LRFD_9.3.10.3.1): «Sites shall be classified
    by their stiffness...»; la fila es [A] SOLO mientras la clase falta (la
    ficha de 'F_pga' lo dice: la caracterizacion «deja una sola fila»).

    Sin clase declarada no hace nada y no la registra como usada (el [S]
    vacio se declara en el bloque de vacios, ver su `trazabilidad`). Con
    clase:
      * fila F: `MetodoNoEvaluableError` --la tabla no trae factor y el
        Art. 3.10.2 exige el procedimiento especifico de sitio («A
        Site-Specific Procedure shall be used»), que el programa no tiene--;
      * clase fuera de las filas de 'F_pga': `DatoInvalidoError` sobre
        'F_pga', que ya no describe al sitio medido;
      * clase dentro de varias filas: un AVISO con el factor medido y la
        envolvente que la cadena sismica sigue usando (del lado seguro);
      * 'F_pga' = la clase medida: nada que decir.
    Devuelve los avisos.
    """
    clase = ca.valor_si_declarado(CRITERIO_CLASE_SITIO)
    if clase is None:
        return ()
    if clase not in F_PGA_TABLA:
        raise DatoInvalidoError(
            CRITERIO_CLASE_SITIO, valor=clase,
            motivo="no es una clase de sitio de la Tabla 3.10.3.1-1 (A a F)")
    if F_PGA_EXIGE_ESTUDIO_DE_SITIO in F_PGA_TABLA[clase]:
        raise MetodoNoEvaluableError(
            que="factor de sitio de la cadena sismica",
            procedimiento="analisis de respuesta dinamica especifico del "
                          "sitio (AASHTO 3.10.2; Manual de Puentes "
                          "2.4.3.11.2)",
            motivo=f"la clase de sitio medida es {clase}: la Tabla "
                   "2.4.3.11.2.1.2-1 no trae factor para ella (Nota 2) y el "
                   "Art. 3.10.2 exige el procedimiento especifico de sitio "
                   "(«shall be used»), que este programa no implementa",
            rotulo=MOTIVO_METODO_NO_EVALUABLE_SITIO)
    filas = M9.clases_de_sitio_plausibles()
    if clase not in filas:
        raise DatoInvalidoError(
            M9.CRITERIO_F_PGA, valor=filas,
            motivo=f"la clase de sitio MEDIDA es {clase} ('{CRITERIO_CLASE_SITIO}') "
                   f"y no esta entre las filas que 'F_pga' declara "
                   f"plausibles ({', '.join(filas)}): con la clase medida la "
                   f"fila ya no es una eleccion. Declarar 'F_pga' = "
                   f"('{clase}',)")
    if len(filas) == 1:
        return ()
    PGA = ds.valor(DATO_PGA)
    lectura = ca.valor(M9.CRITERIO_F_PGA_LECTURA)
    medido = M9.factor_sitio_desde_tabla(clase=clase, PGA=PGA,
                                         lectura_extremos=lectura)
    envolvente = max(M9.factor_sitio_desde_tabla(clase=c, PGA=PGA,
                                                 lectura_extremos=lectura)
                     for c in filas)
    return (f"clase de sitio medida {clase}: F_pga = {medido:.2f} con su fila, "
            f"y la cadena sismica sigue con la envolvente de "
            f"{', '.join(filas)} ({envolvente:.2f}), del lado seguro. Con la "
            f"clase medida la fila deja de ser una eleccion: declarar 'F_pga' "
            f"= ('{clase}',)",)
