"""
criterios_adoptados.py
======================
Fuente unica de verdad para todo parametro que NO sea una exigencia normativa
verificada. Ningun otro modulo del script debe declarar estos valores.

Regla de uso
------------
    from criterios_adoptados import valor, reporte_criterios

    Fpga = valor("F_pga")          # registra el uso automaticamente
    ...
    print(reporte_criterios())     # M11 lo imprime al final del reporte

Un criterio con valor None lanza CriterioPendienteError (modelos.py) y detiene
el calculo. Nunca devuelve un default. Para saber que falta ANTES de correr,
sin provocar la excepcion, se consulta criterios_sin_valor().

Al cambiar un criterio (por ejemplo, cuando llegue el SPT), se modifica UNA
linea de este archivo y todos los modulos se recalculan sin contradicciones.

Etiquetas
---------
    N    Exigencia normativa peruana vigente, numeral verificado
    N->  Valor normativo aplicado POR ANALOGIA. Requiere declaracion expresa
    S    Dato de sitio. Obtenido mediante un procedimiento normativo real
         (mapa, ensayo, medicion de campo) aplicado a las coordenadas o
         condiciones de ESTE proyecto. No es eleccion del proyectista ni
         analogia: es un hecho determinado, no portable a otro proyecto. En
         vez de sensibilidad declara TRAZABILIDAD obligatoria: el
         procedimiento exacto, la fuente, y si el dato aplica a todo el
         corredor o varia punto a punto
    C    Vacio normativo cubierto con fuente tecnica reconocida (FHWA, AASHTO)
    A    Sin norma ni fuente unica. Adopcion declarada + sensibilidad obligatoria

Las cinco se leen de mas determinado a mas elegido. [S] se lee entre [N->] y
[C] por lo mismo: el procedimiento que lo produce es normativo y propio (no
prestado, no ajeno), y lo unico local es la lectura.

Donde vive cada [S]
-------------------
Un dato de sitio unico para todo el corredor vive en `datos_sitio.py`
(PGA_roca_B, la zonificacion de E.030). Uno que varia punto a punto es una
columna del CSV (NF_profundidad_m, cbr_subrasante). Aqui solo quedan los [S]
que ademas siguen sujetos a un ensayo pendiente y por eso comparten tablero
con los criterios adoptados.
"""

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Optional, Tuple, Dict, List, Set

from modelos import CriterioPendienteError


# ---------------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Criterio:
    valor: Any
    etiqueta: str                              # "N", "N->", "S", "C", "A"
    concepto: str                              # que es
    justificacion: str                         # por que este valor
    fuente: str                                # de donde sale
    reemplazado_por: Optional[str] = None      # ensayo/dato que lo sustituye
    sensibilidad: Optional[Tuple] = None       # rango para analisis de sensibilidad -- SOLO [A]
    trazabilidad: Optional[str] = None         # como reproducir la lectura -- SOLO [S]
    verificacion_pendiente: Optional[str] = None   # lo que falta confirmar
    provisional: bool = False                  # valor de PRUEBA, no verificado

    # `provisional=True` marca un valor cargado para una corrida de prueba
    # integral: destraba el pipeline para ver que puntos completan diseno,
    # pero NO esta verificado contra norma ni ensayo y no puede ir a una
    # memoria de calculo. Existe para que ese valor NUNCA pueda pasar
    # inadvertido: reporte_criterios() y M11 lo imprimen con marca visible.
    # Ningun criterio del expediente lo lleva puesto -- si alguno aparece
    # con provisional=True en una revision, es que quedo residuo de una
    # prueba sin limpiar.

    # sensibilidad y trazabilidad no son dos nombres para lo mismo y no se
    # mezclan: un [A] se defiende mostrando cuanto cambiaria el resultado con
    # el otro extremo del rango, y un [S] no tiene rango que elegir -- se
    # defiende diciendo donde se leyo, para que el revisor repita la lectura.
    # `_coherencia_de_etiquetas()` lo verifica al importar el modulo.


_USADOS: Set[str] = set()

# ---------------------------------------------------------------------------
# Declaracion en caliente (solo para la corrida actual)
# ---------------------------------------------------------------------------
# La GUI (pestana "Criterios") permite declarar un valor para un criterio con
# valor=None SIN tocar este archivo. El override vive solo en memoria de
# proceso: se pierde al cerrar la GUI y nunca se confunde con un valor [N]/[C]
# transcrito de una norma. Reescribir este archivo es una accion aparte,
# explicita, ver `escribir_valor_en_archivo`.
_OVERRIDES: Dict[str, Any] = {}


def establecer_valor_dinamico(clave: str, valor_nuevo: Any) -> None:
    """Declara, solo para esta corrida, el valor de un criterio pendiente."""
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    _OVERRIDES[clave] = valor_nuevo


def quitar_valor_dinamico(clave: str) -> None:
    """Retira la declaracion en caliente de un criterio (vuelve a bloquear)."""
    _OVERRIDES.pop(clave, None)


def limpiar_valores_dinamicos() -> None:
    """Retira todas las declaraciones en caliente de la corrida."""
    _OVERRIDES.clear()


def valores_dinamicos() -> Dict[str, Any]:
    """Claves declaradas en caliente en esta corrida, sin registrar uso."""
    return dict(_OVERRIDES)


def valor(clave: str) -> Any:
    """Devuelve el valor del criterio y registra que fue usado."""
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    _USADOS.add(clave)
    if clave in _OVERRIDES:
        return _OVERRIDES[clave]
    c = CRITERIOS[clave]
    if c.valor is None:
        # Detiene el calculo. NUNCA se devuelve un default silencioso: la GUI
        # muestra "falta declarar: <clave>" y el usuario resuelve el vacio.
        raise CriterioPendienteError(clave, concepto=c.concepto, fuente=c.fuente)
    return c.valor


def valor_si_declarado(clave: str) -> Optional[Any]:
    """
    El valor del criterio, o None si sigue sin declarar. NO lanza
    CriterioPendienteError.

    Es la lectura para los criterios OPCIONALES: los que refinan un valor que
    la norma ya fija, en vez de cubrir un vacio. Un criterio de vacio se lee
    con `valor()` y detiene el calculo mientras este vacio; uno opcional se
    lee con esta, y quien la llama aplica el valor normativo por defecto.
    Confundirlas en cualquiera de los dos sentidos es grave: `valor()` sobre
    un opcional bloquea un calculo que la norma sabe resolver, y esta sobre
    uno de vacio rellena el vacio en silencio, que es el peor error del
    proyecto.

    Un criterio sin valor no se registra como usado: no se aplico a nada y no
    hay uso que declarar en M11. En cuanto reciba valor -- en el archivo o en
    caliente -- empieza a devolverlo Y a registrarse.
    """
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    if clave in _OVERRIDES:
        _USADOS.add(clave)
        return _OVERRIDES[clave]
    if CRITERIOS[clave].valor is None:
        return None
    return valor(clave)


def criterio(clave: str) -> Criterio:
    """Devuelve el objeto completo, sin registrar uso (para reportes)."""
    return CRITERIOS[clave]


def criterios_sin_valor() -> List[str]:
    """
    Claves cuyo valor es None y sin declaracion en caliente: vacios que
    detienen el calculo si se invocan. M11 los imprime en bloque aparte
    (Sec. 0.7) y la GUI los usa para avisar antes de correr, no despues de
    la excepcion.
    """
    return sorted(
        k for k, c in CRITERIOS.items()
        if c.valor is None and k not in _OVERRIDES
    )


def escribir_valor_en_archivo(clave: str, valor_nuevo: Any,
                              ruta: Optional[str] = None) -> None:
    """
    Reescribe, EN EL ARCHIVO FUENTE, el ``valor=None`` del criterio `clave`
    por `valor_nuevo`. Accion permanente y distinta de
    `establecer_valor_dinamico`: se usa solo cuando el usuario confirma de
    forma explicita que quiere dejar de tratar el criterio como pendiente
    (la GUI pide confirmacion aparte antes de llamarla). No toca ningun otro
    campo del Criterio (etiqueta, justificacion, fuente, sensibilidad): esos
    se revisan y editan a mano, porque describen POR QUE se adopto el valor.
    """
    import re

    if clave not in CRITERIOS:
        raise KeyError(f"'{clave}' no esta declarado en criterios_adoptados.py.")

    ruta_archivo = ruta or __file__
    texto = Path(ruta_archivo).read_text(encoding="utf-8")

    patron = re.compile(
        r'("' + re.escape(clave) + r'":\s*Criterio\(\s*\n\s*valor=)([^,\n]*)(,)'
    )
    texto_nuevo, n = patron.subn(
        lambda m: m.group(1) + repr(valor_nuevo) + m.group(3), texto, count=1,
    )
    if n == 0:
        raise ValueError(
            f"No se encontro el bloque 'valor=' de '{clave}' en {ruta_archivo}. "
            "No se modifico el archivo."
        )
    Path(ruta_archivo).write_text(texto_nuevo, encoding="utf-8")

    # El archivo ya quedo escrito; se refleja tambien en memoria para que el
    # resto de esta sesion (GUI o CLI en curso) vea el valor definitivo sin
    # tener que reiniciar el proceso, y se retira el override en caliente:
    # ya no hace falta, el valor "real" es ahora este.
    CRITERIOS[clave] = replace(CRITERIOS[clave], valor=valor_nuevo)
    _OVERRIDES.pop(clave, None)


def criterios_usados() -> List[str]:
    """
    Claves que el calculo invoco, en orden alfabetico. Es la misma informacion
    que `reporte_criterios(solo_usados=True)` imprime como texto, expuesta como
    lista para el consumidor que arma su propio bloque (cli.py la vuelca al
    JSON). Existe para que nadie tenga que leer `_USADOS` desde fuera.
    """
    return sorted(_USADOS)


# ---------------------------------------------------------------------------
# CRITERIOS ADOPTADOS
# ---------------------------------------------------------------------------

CRITERIOS: Dict[str, Criterio] = {

    # ----------------------- SISMO: cadena unica -------------------------
    # Se define UNA vez y se propaga a toda verificacion de estabilidad.

    # 'PGA_roca_B' ya no vive aqui: es un dato de sitio [S] -- la lectura de un
    # mapa normativo sobre las coordenadas de esta obra, unica para todo el
    # corredor -- y vive en `datos_sitio.py`. No se declara en dos sitios: la
    # cadena sismica de M9 lo lee de alla.

    "PERFIL_SUELO_PRESUNTO": Criterio(
        valor="S5",
        etiqueta="S",
        concepto="Perfil de suelo de E.030 presunto para el sitio (S0-S5)",
        justificacion="El Art. 14.6 de E.030 define el ESQUEMA de perfiles "
                      "S0-S5 y sus umbrales; que letra le toca a este sitio es "
                      "el resultado de aplicar ese esquema a las condiciones "
                      "de la llanura del Bajo Piura (arenas saturadas, NF "
                      "somero, suelos potencialmente licuables), no una "
                      "exigencia normativa con valor fijo. En otra via con "
                      "otro suelo el mismo articulo da otra letra. El nombre "
                      "de la variable lo venia admitiendo desde el principio: "
                      "PRESUNTO es una presuncion de expediente",
        fuente="E.030 (RM 183-2026-VIVIENDA), Art. 14.6 - suelos "
               "potencialmente licuables",
        reemplazado_por="Ensayo SPT DE LICUEFACCION: perforaciones de al menos "
                        "15 m de profundidad con ensayo cada 1.00 m (E.050 "
                        "Art. 38). Es la profundidad que cierra ESTE criterio "
                        "-- la presuncion de suelo licuable del Art. 14.6 -- y "
                        "no la del criterio 'clase_sitio', que necesita 30 m",
        trazabilidad="Clasificacion del Art. 14.6 de E.030 aplicada a la "
                     "caracterizacion geotecnica disponible del corredor "
                     "(llanura del Bajo Piura, distrito de La Union), sin "
                     "ensayo que la cierre. Ambito: todo el corredor mientras "
                     "sea presuncion; con SPT pasa a ser dato por calicata y "
                     "entonces le corresponde una columna del CSV, no esta "
                     "entrada. REFERENCIA MUERTA HOY: ningun modulo de "
                     "src/modulos/ lo invoca -- la clase de sitio que si entra "
                     "en el calculo es la de AASHTO, criterio 'clase_sitio'. "
                     "Se conserva declarado, y no borrado, porque es la "
                     "presuncion geotecnica sobre la que se apoyan tanto "
                     "'clase_sitio' como la hipotesis de licuefaccion de "
                     "Sec. 0.5",
        verificacion_pendiente="Al llegar el SPT, confirmar el perfil y "
                               "decidir si es unico para el tramo o varia por "
                               "calicata; si varia, no se corrige el valor: se "
                               "convierte en columna del CSV",
    ),

    "clase_sitio": Criterio(
        valor="F_con_factores_tabulados_por_adopcion",
        etiqueta="A",
        concepto="Clase de sitio sismica AASHTO y base sobre la que se toman "
                 "los factores de sitio de la cadena sismica",
        justificacion="El sitio es Clase F por susceptibilidad a licuefaccion "
                      "(arenas saturadas, NF a 1.4 m); esa parte no cambia. "
                      "LO QUE CAMBIA ES QUE LA DISPENSA POR PERIODO CORTO NO "
                      "EXISTE. Se verifico contra AASHTO LRFD Bridge Design "
                      "Specifications, 9a edicion (2020): no esta en el "
                      "Art. 3.10.3.1, no esta en su comentario C3.10.3.1, y "
                      "no esta en ninguna tabla ni nota de tabla de clases de "
                      "sitio. AASHTO exige, de forma incondicional, un estudio de "
                      "respuesta de sitio especifico para la Clase F. La "
                      "redaccion anterior de este criterio y de Sec. 0.5 "
                      "atribuia a AASHTO una dispensa por periodo "
                      "fundamental T <= 0.5 s que AASHTO no concede: no fue "
                      "un vacio rellenado en silencio, fue una autorizacion "
                      "normativa inventada, que es peor, porque un vacio se "
                      "ve y una cita falsa se cree. "
                      "CONSECUENCIA SOBRE LA ETIQUETA: deja de ser [C]. Un "
                      "[C] es un vacio normativo CUBIERTO con fuente tecnica "
                      "reconocida, y aqui no hay fuente que cubra nada -- la "
                      "que se citaba no dice lo que se le hacia decir. Pasa a "
                      "[A]: seguir el calculo con los factores de sitio "
                      "tabulados, mientras no exista el estudio de respuesta "
                      "de sitio, es una ADOPCION DECLARADA DEL PROYECTISTA y "
                      "no un permiso de la norma. La memoria lo dice con esas "
                      "palabras; no hay forma honesta de escribirlo mas "
                      "corto. "
                      "ALCANCE, ahora sin coartada: los factores tabulados "
                      "permiten DIMENSIONAR el elemento; no evaluan el riesgo "
                      "de licuefaccion (Fase 0-bis), y los efectos de la "
                      "licuefaccion -- asentamiento, desplazamiento lateral, "
                      "perdida de capacidad portante -- quedan fuera del "
                      "alcance del script y remitidos al estudio geotecnico "
                      "del expediente. Un analisis de respuesta especifica de "
                      "sitio puede arrojar valores MAYORES que los tabulados: "
                      "la adopcion no es conservadora por construccion, y por "
                      "eso es [A] y no [N->]",
        fuente="NINGUNA autoriza la adopcion. AASHTO LRFD 9a ed. (2020), "
               "Art. 3.10.3.1 y C3.10.3.1: la Clase F exige estudio de "
               "respuesta de sitio especifico, sin dispensa alguna por periodo "
               "corto. El Manual de Puentes tampoco tipifica dispensas "
               "para Clase F en su Tabla 2.4.3.11.2.1.2-1. La adopcion es "
               "del proyectista y se declara como tal",
        reemplazado_por="CARACTERIZACION DE SITIO SOBRE LOS 30 m SUPERIORES: "
                        "Vs30, o N_barra promediado en esos 30 m, con el que "
                        "se lee la clase de sitio. Los 30 m son parte de la "
                        "DEFINICION de la clase (AASHTO LRFD Art. 3.10.3.1, "
                        "coherente con el perfil de E.030): una clase de sitio "
                        "leida sobre menos profundidad no es la misma "
                        "variable. "
                        "NO LO CIERRA el SPT de 15 m de E.050 Art. 38: ese "
                        "ensayo responde a la pregunta de licuefaccion "
                        "(criterio PERFIL_SUELO_PRESUNTO) y se detiene a mitad "
                        "de la columna que esta clase necesita. Este criterio "
                        "decia antes '>= 15 m -> N_barra o Vs30', que mezclaba "
                        "las dos profundidades y daba por cerrada con 15 m una "
                        "lectura que exige 30. Son dos requisitos de campana "
                        "distintos y conviene pedirlos juntos al programar la "
                        "campana geotecnica",
        verificacion_pendiente="La verificacion que este campo pedia -- si la "
                               "dispensa estaba en articulado o en comentario "
                               "-- YA SE HIZO y la respuesta fue que no esta "
                               "en ninguno de los dos. Lo que queda pendiente "
                               "es otra cosa: mientras la adopcion siga en "
                               "pie, la memoria debe declararla como decision "
                               "del proyectista contra una exigencia expresa "
                               "de AASHTO, y el expediente debe programar el "
                               "estudio de respuesta de sitio especifico. No "
                               "se cita AASHTO como respaldo de la adopcion",
    ),

    "F_pga": Criterio(
        valor=1.0,
        etiqueta="A",
        concepto="Factor de sitio para la aceleracion pico",
        justificacion="Sin SPT no hay clase de sitio definitiva. Para PGA >= 0.50 "
                      "los factores convergen: 1.0 para clases C y D, 0.9 para E. "
                      "Se adopta 1.0 por ser conservador o exacto frente a las "
                      "tres clases plausibles; incertidumbre asociada <= 10%",
        fuente="Tabla 2.4.3.11.2.1.2-1 del Manual de Puentes (valores [N]: C=1.0, D=1.0, E=0.9 para PGA>=0.50). La ELECCION es [A]",
        reemplazado_por="Clase de sitio definitiva desde SPT",
        sensibilidad=(0.9, 1.0),
    ),

    "factor_muro_eleccion": Criterio(
        valor=1.0,
        etiqueta="A",
        concepto="Factor de reduccion del coeficiente sismico por "
                 "desplazamiento: fila elegida de la tabla del numeral",
        justificacion="El cabezal esta empotrado en el terraplen y no tiene "
                      "desplazamiento lateral admisible garantizado de 25-50 mm. "
                      "Se adopta el caso de muro rigido, sin reduccion",
        fuente="Tabla FACTOR_MURO_TABLA del Manual de Puentes num. 2.8.1.1.14.2 "
               "(valores [N]: rigido = 1.0, desplazable = 0.5). La ELECCION de "
               "la fila es [A]",
        reemplazado_por="Diseno de detalle del cabezal que garantice (o "
                        "descarte) un desplazamiento admisible de 25-50 mm",
        sensibilidad=(0.5, 1.0),
    ),

    "k_v": Criterio(
        valor=0.0,
        etiqueta="A",
        concepto="Coeficiente sismico vertical para Mononobe-Okabe",
        justificacion="Adopcion habitual en analisis pseudo-estatico de muros de "
                      "contencion de baja altura",
        fuente="Practica corriente; no fijado por el Manual de Puentes",
        sensibilidad=(0.0, 0.5),   # 0.5*k_h como escenario alterno
    ),

    # Los cuatro angulos que Sec. 9.2 exige ADEMAS de la cadena sismica para
    # cerrar Mononobe-Okabe: "se requieren ademas phi del relleno, pendiente
    # del relleno (i), inclinacion del muro (beta) y friccion muro-suelo
    # (delta)". El primero ya esta declarado abajo como 'phi_relleno_trasdos'
    # (bloque GEOTECNIA), porque no es solo del sismo: gobierna tambien el Ka
    # estatico. Los otros tres viven aqui.

    "pendiente_relleno_trasdos_i": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Inclinacion de la superficie del relleno del trasdos sobre "
                 "la horizontal (i), en grados, para Mononobe-Okabe",
        justificacion="Sec. 9.2 la exige por su nombre y no la entrega, y "
                      "Sec. 1.2 no trae ninguna columna de geometria del "
                      "cabezal ni del terraplen sobre el trasdos. No se "
                      "puede deducir del CSV: la altura de terraplen del "
                      "punto (cota_rasante - cota_terreno) es un desnivel, "
                      "no la pendiente de la superficie contra el muro. "
                      "Adoptar i = 0 en silencio parece inocuo y no lo es: "
                      "en Mononobe-Okabe i entra en sen(phi - psi - i), y "
                      "con psi = 26.6 grados (k_h = 0.50) el radicando se "
                      "anula para phi - i cerca de psi -- es decir, unos "
                      "pocos grados de relleno inclinado pueden llevar el "
                      "empuje sismico al infinito. Es el parametro con la "
                      "sensibilidad mas violenta de toda la Fase 9",
        fuente="PENDIENTE - seccion tipica del expediente vial sobre el "
               "cabezal (DG-2018) o el detalle de coronacion del terraplen",
        reemplazado_por="Geometria medida sobre la seccion transversal del "
                        "punto de cruce",
        sensibilidad=(0.0, 10.0),   # grados; horizontal frente a talud suave
        verificacion_pendiente="Declarar si el relleno corona horizontal "
                               "contra el muro (i = 0) o continua con el "
                               "talud del terraplen: son dos detalles "
                               "constructivos distintos, no un matiz",
    ),

    "inclinacion_muro_beta": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Inclinacion del paramento interior (trasdos) del cabezal "
                 "respecto de la VERTICAL (beta), en grados, positiva cuando "
                 "el muro se aleja del relleno",
        justificacion="Es geometria del cabezal, y Sec. 9 no lo dimensiona: "
                      "la hoja de ruta fija el detalle de EMBOCADURA (tubo a "
                      "ras del muro, square edge, Sec. 9.1 y Tablero 2.3) "
                      "pero no el talud del paramento. Un cabezal de "
                      "paramento vertical (beta = 0) y uno con talud de "
                      "1:10 dan K_AE distintos, y el signo de beta se presta "
                      "a error: se declara con la convencion de "
                      "Mononobe-Okabe, no con la del plano",
        fuente="PENDIENTE - predimensionamiento del cabezal; ver el criterio "
               "'predimensionamiento_cabezal', del que este angulo es parte",
        reemplazado_por="Plano de encofrado del cabezal del expediente",
        sensibilidad=(0.0, 10.0),   # grados
    ),

    "friccion_muro_suelo_delta": Criterio(
        valor=None,                 # VACIO: bloquea K_AE y el Ka de Coulomb
        etiqueta="A",
        concepto="Angulo de friccion entre el paramento del muro y el relleno "
                 "(delta), en grados, para Mononobe-Okabe",
        justificacion="Sec. 9.2 lo exige por su nombre y no lo entrega. La "
                      "practica corriente lo liga a phi del relleno (del "
                      "orden de phi/2 a 2*phi/3 en concreto contra suelo "
                      "granular), pero la hoja de ruta no fija esa fraccion "
                      "y adoptarla en silencio moveria a la vez el empuje "
                      "estatico y el sismico. Ademas no es conservador por "
                      "un lado solo: un delta alto reduce K_AE (favorable "
                      "para el empuje) y a la vez inclina la resultante, "
                      "cambiando el reparto entre deslizamiento y volteo",
        fuente="PENDIENTE - se declara como fraccion de 'phi_relleno_trasdos' "
               "con la fuente tecnica que la sostenga, o se mide",
        reemplazado_por="Ensayo de interfase concreto-relleno, o adopcion "
                        "declarada como fraccion de phi con su fuente",
        sensibilidad=(0.0, 22.7),   # grados; delta=0 (conservador) a 2*phi/3 con phi=34
        verificacion_pendiente="Declararlo como FRACCION de phi y no como "
                               "angulo suelto, para que al ajustar "
                               "'phi_relleno_trasdos' no queden incoherentes",
    ),

    "punto_aplicacion_incremento_sismico": Criterio(
        valor=None,                 # VACIO: bloquea el momento de volteo sismico
        etiqueta="A",
        concepto="Altura de aplicacion del incremento sismico de empuje "
                 "(P_AE - P_A), como fraccion de la altura H del muro",
        justificacion="Mononobe-Okabe entrega el empuje TOTAL, no su punto de "
                      "aplicacion. El empuje estatico si lo tiene sin "
                      "adoptar nada: su distribucion es triangular y la "
                      "resultante cae en H/3, que es el centroide del "
                      "triangulo, no un criterio. El INCREMENTO sismico no es "
                      "triangular y su altura de aplicacion es una convencion "
                      "de la literatura (Seed-Whitman la sitea del orden de "
                      "0.6H); la hoja de ruta no la fija. Sin ella no hay "
                      "brazo, y sin brazo no hay momento de volteo sismico: "
                      "la fila 'volteo / sismico' de la tabla de Sec. 9.3 no "
                      "se puede evaluar",
        fuente="PENDIENTE - Sec. 9.2 entrega K_AE y se detiene ahi. "
               "Seed-Whitman (0.6H) o AASHTO LRFD Sec. 11, declarado con su "
               "fuente en la memoria",
        reemplazado_por="Convencion adoptada y escrita en la memoria de calculo",
        sensibilidad=(0.333, 0.6),   # H/3 (empuje total en el centroide) a 0.6H
    ),

    # ----------------------- HIDROLOGIA -----------------------------------

    "homogeneidad_serie_fen": Criterio(
        valor=None,                 # VACIO: bloquea el Q de diseno de TODOS los puntos
        etiqueta="A",
        concepto="Tratamiento de la poblacion mixta de la serie de precipitacion "
                 "maxima anual (anios FEN frente a anios neutros)",
        justificacion="La serie de Piura no es de poblacion unica: 1983, 1998 y "
                      "2017 no pertenecen estadisticamente a la misma poblacion "
                      "que los anios neutros. Si la serie los CONTIENE, el ajuste "
                      "K-S puede estar dominado por dos o tres outliers y hay que "
                      "reportar el ajuste con y sin ellos y adoptar el mas "
                      "conservador. Si NO los contiene, el Q de diseno esta "
                      "subestimado de forma grave y es una limitacion central",
        fuente="PENDIENTE - Fase 1-bis de la hoja de ruta. Requiere la serie "
               "SENAMHI con su longitud de registro, estacion y anios faltantes",
        reemplazado_por="Analisis de homogeneidad sobre la serie SENAMHI completa",
        verificacion_pendiente="Tablero 3.2: verificar si la serie contiene 1983, "
                               "1998 y 2017. Va ANTES de la Fase 4",
    ),

    "umbral_area_quebrada_importante_ha": Criterio(
        valor=None,                 # VACIO: bloquea el TR de toda la Familia A
        etiqueta="A",
        concepto="Area de cuenca a partir de la cual el cauce de un punto de "
                 "Familia A se clasifica como 'quebrada importante' (TR 71) en "
                 "vez de 'quebrada menor' (TR 35) en la Tabla N 02",
        justificacion="FORMALIZADO COMO [A] TRAS VERIFICACION EXTERNA DEL "
                      "MANUAL. Lo que la Tabla N 02 (num. 3.6) del Manual de "
                      "Hidrologia entrega son las dos filas con su riesgo "
                      "admisible R y su vida util n, y de ahi sale el TR de "
                      "cada categoria. Lo que NO entrega -- ni esa tabla ni "
                      "ningun otro apartado del Manual -- es una REGLA DE "
                      "ASIGNACION FISICA que diga cuando un cauce cae en una "
                      "categoria o en la otra: no hay umbral de area, ni de "
                      "caudal, ni de longitud, ni de orden de cauce. El "
                      "Manual nombra las categorias y las tarifa; no las "
                      "define. Sec. 2.3 de la hoja de ruta hereda el hueco y "
                      "se limita a decir que la Familia A lleva 'TR 71 o 35 "
                      "anios'. "
                      "Por eso es [A] y no [C]: un [C] necesitaria una fuente "
                      "tecnica reconocida que SI fije el criterio, y aqui no "
                      "la hay -- el vacio esta en la norma y no se cubre "
                      "prestandolo de otra. Y no es menor: entre una fila y "
                      "la otra el TR se duplica, y con el suben la intensidad "
                      "de la IDF y el Q de diseno de todos los puntos de "
                      "paso. "
                      "Se elige el AREA DE CUENCA como descriptor porque es "
                      "el unico dato del CSV que Sec. 1.1 califica "
                      "expresamente de 'solo clasificador': no entra en "
                      "ninguna formula y existe justamente para esto. Elegir "
                      "el descriptor tambien es parte de la adopcion -- el "
                      "Manual tampoco dice que haya que clasificar por area. "
                      "Lo que falta es el umbral. "
                      "ALTERNATIVA sin este criterio: clasificar cauce por "
                      "cauce y pasar la categoria explicita a M1, que la "
                      "acepta como argumento; entonces la eleccion se "
                      "documenta punto por punto en la memoria en vez de por "
                      "regla",
        fuente="PENDIENTE - Manual de Hidrologia, Hidraulica y Drenaje (MTC), "
               "Tabla N 02 (num. 3.6): da R y n por categoria de cauce y NO "
               "define 'quebrada importante' ni 'quebrada menor' por umbral "
               "de area, longitud ni caudal. Verificado contra el texto",
        reemplazado_por="Clasificacion del cauce documentada punto por punto "
                        "(categoria explicita a M1), o umbral tomado de un "
                        "estudio hidrologico de la cuenca del Bajo Piura",
        verificacion_pendiente="Si se adopta un umbral, declarar en la memoria "
                               "que puntos quedan a cada lado y correr la "
                               "sensibilidad del Q con TR 71 y TR 35: es la "
                               "misma alcantarilla con dos caudales de diseno",
    ),

    # ----------------------- HIDRAULICA: vacios ---------------------------

    "hds5_embocadura_hdpe": Criterio(
        valor={"K": 0.0098, "M": 2.00, "c": 0.0398, "Y": 0.67, "Ks": -0.5},
        etiqueta="C",
        concepto="Constantes de control de entrada HDS-5 para tuberia HDPE",
        justificacion="La Tabla A.1 se organiza en cartas por forma/material y, "
                      "dentro de cada carta, por configuracion de borde: la misma "
                      "'square edge w/headwall' tiene K=0.0098 en concreto y "
                      "K=0.0078 en metal corrugado. Esa diferencia responde al "
                      "PERFIL DE PARED EN LA BOCA (lisa vs corrugada), no a la "
                      "friccion del barril. El HDPE de interior liso cortado a ras "
                      "del muro presenta en la boca pared lisa y borde cuadrado: "
                      "misma condicion de entrada que el concreto",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice A, Tabla A.1, pag. A.8",
        verificacion_pendiente="Confirmar que el detalle constructivo enrasa el "
                               "tubo en la cara del cabezal. Si aloja campana o "
                               "sobresale, corresponde otra fila de la tabla",
    ),

    "metodo_transicion_hds5": Criterio(
        valor="interpolacion_lineal_entre_extremos",
        etiqueta="C",
        concepto="Metodo con que se cubre la zona de transicion del control de "
                 "entrada de HDS-5, 3.5 < q* < 4.0",
        justificacion="Sec. 4.2 de la hoja de ruta resuelve la transicion con "
                      "'interpolar linealmente', y eso es lo que M4 implementa: "
                      "una recta entre la forma NO SUMERGIDA evaluada en "
                      "q* = 3.5 y la SUMERGIDA evaluada en q* = 4.0. Lo que se "
                      "declara aqui es que ESO NO ES EL METODO DEL HDS-5. "
                      "HDS-5 no interpola linealmente: en la zona de transicion "
                      "traza a mano una curva TANGENTE a las dos ramas, un "
                      "empalme empirico ajustado sobre los datos de laboratorio "
                      "del que no publica ecuacion cerrada. La recta es una "
                      "SIMPLIFICACION ADOPTADA de ese empalme, no una "
                      "transcripcion de la fuente primaria, y por eso es [C] y "
                      "no [N]: la fuente tecnica reconocida existe (HDS-5) pero "
                      "el procedimiento programable no sale de ella. "
                      "Que la recta empalme continua en los dos extremos "
                      "(coincide con cada rama en su borde de validez) hace el "
                      "error acotado y del orden del espesor de la propia "
                      "curva de HDS-5, no lo convierte en el metodo del HDS-5. "
                      "ALCANCE: solo afecta a los puntos cuyo q* cae dentro de "
                      "la ventana 3.5-4.0; fuera de ella rigen las dos "
                      "ecuaciones tal cual las escribe la tabla",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. IV y Apendice A "
               "(curva de transicion tangente, sin ecuacion publicada). La "
               "interpolacion lineal la prescribe Sec. 4.2 de la hoja de ruta, "
               "no HDS-5",
        reemplazado_por="Lectura directa de la carta de HDS-5 en la zona de "
                        "transicion, o el procedimiento tangente si el "
                        "expediente exige reproducir la curva original",
        verificacion_pendiente="Declarar en la memoria que puntos del corredor "
                               "caen con q* entre 3.5 y 4.0: si ninguno lo hace, "
                               "esta simplificacion no toca ningun resultado y "
                               "basta con dejarla enunciada",
    ),

    "n_manning_hdpe": Criterio(
        valor=(0.010, 0.013),       # RANGO (n_min, n_max), no valor puntual
        etiqueta="A",
        concepto="Coeficiente de rugosidad de Manning para HDPE de interior liso",
        justificacion="La Tabla N 09 del Manual MTC no lista HDPE. Se adopta el "
                      "RANGO COMPLETO del concreto por analogia. Un valor puntual "
                      "(p.ej. 0.012) romperia la regla de doble n: n_max para "
                      "capacidad y n_min para velocidad y socavacion. Con un solo "
                      "numero, una de las dos verificaciones deja de ser conservadora",
        fuente="Analogia a Tabla N 09 (concreto, tubo recto)",
        reemplazado_por="Ficha tecnica del producto seleccionado",
        sensibilidad=(0.010, 0.013),
        verificacion_pendiente="Confirmar que el HDPE especificado es de INTERIOR "
                               "LISO. El de interior corrugado tiene n del orden de "
                               "0.018-0.025 y la analogia seria gruesamente insegura",
    ),

    "v_max_hdpe": Criterio(
        valor=None,                 # VACIO
        etiqueta="C",               # Anexo A y Sec. 0.1: la fuente (PPI/FHWA)
                                    # es tecnica reconocida, no una adopcion libre
        concepto="Velocidad maxima admisible en HDPE",
        justificacion="La Tabla N 10 del Manual MTC no cubre materiales flexibles",
        fuente="PENDIENTE - fuente identificada: Plastics Pipe Institute (PPI) "
               "y FHWA. Falta EXTRAER los valores numericos",
        reemplazado_por="Valor numerico de PPI/FHWA o ficha tecnica",
    ),

    "v_max_tmc": Criterio(
        valor=None,                 # VACIO
        etiqueta="C",               # idem v_max_hdpe: Anexo A lo etiqueta [C]
        concepto="Velocidad maxima admisible en TMC",
        justificacion="La Tabla N 10 del Manual MTC no cubre materiales flexibles",
        fuente="PENDIENTE - fuente identificada: Plastics Pipe Institute (PPI) "
               "y FHWA. Falta EXTRAER los valores numericos",
        reemplazado_por="Valor numerico de PPI/FHWA o ficha tecnica",
    ),

    "v_max_concreto_eleccion": Criterio(
        valor=None,                 # OPCIONAL: sin valor, V3 usa el techo [N]
        etiqueta="A",
        concepto="Techo de velocidad adoptado para el concreto, mas "
                 "conservador que el maximo normativo de 6.0 m/s",
        justificacion="OPCIONAL, no un vacio: sin valor el calculo NO se "
                      "detiene, V3 aplica el techo normativo de 6.0 m/s y la "
                      "memoria no declara este criterio. Es la unica entrada "
                      "de este archivo que se lee con "
                      "`valor_si_declarado()` en vez de `valor()`. "
                      "La Tabla N 10 se titula 'Velocidades maximas "
                      "admisibles en conductos revestidos' (num. 4.1.1.3.6, "
                      "pag. 76): sus dos numeros son MAXIMOS segun la calidad "
                      "del revestimiento, y 6.0 m/s es el techo del acabado "
                      "de mejor calidad. Un concreto de acabado corriente "
                      "admite menos, y bajar el techo hasta 3.0 m/s -- el "
                      "maximo del acabado mas pobre -- es una decision "
                      "defendible del proyectista sobre las condiciones de "
                      "ESTA obra, no una exigencia del numeral: por eso [A]. "
                      "CORRIGE la redaccion anterior, que lo planteaba como "
                      "'elegir un valor dentro del rango' dando por hecho que "
                      "3.0 era un PISO a decidir. No lo es: el piso de "
                      "velocidad es V2 (0.25 m/s, misma pagina) y vale para "
                      "todos los materiales. Con aquella lectura, V3 rechazaba "
                      "conductos de concreto perfectamente admisibles",
        fuente="Manual MTC, Tabla N 10 (num. 4.1.1.3.6, pag. 76) - los "
               "maximos son [N]; adoptar uno mas conservador que el techo de "
               "la tabla no esta normado y es del proyectista",
        sensibilidad=(3.0, 6.0),
    ),

    "ke_entrada": Criterio(
        valor=0.5,
        etiqueta="C",
        concepto="Coeficiente de perdida de carga en la embocadura (ke)",
        justificacion="La ecuacion de control de salida de la hoja de ruta, "
                      "H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g), contiene ke "
                      "pero ningun apartado de la hoja le asigna valor. El "
                      "Manual MTC no desarrolla el control de salida, de modo "
                      "que el dato sale de HDS-5, en la fila que corresponde a "
                      "la embocadura ya adoptada por diseno: tubo a ras del "
                      "muro (square edge with headwall). "
                      "TRAZABILIDAD: este 0.5 ya estaba en uso como dato fijo "
                      "en el caso patron CP-8 de tests/fixtures/casos_patron.py "
                      "('ke': 0.5), donde entra en el calculo de H sin declarar "
                      "de donde salia. Queda trazado aqui: el fixture y el "
                      "calculo leen ahora el mismo origen, y si el valor cambia, "
                      "cambia en un solo sitio",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Apendice C, Tabla C.2, "
               "pag. C.2 - coeficientes de perdida de entrada; fila 'square "
               "edge with headwall', ke = 0.5. CITA CERRADA por verificacion "
               "externa contra el documento: antes se citaba el manual sin "
               "apendice, tabla ni pagina, y lo que quedaba pendiente era "
               "exactamente eso",
        reemplazado_por="Fila de HDS-5 que corresponda si cambia el detalle de "
                        "embocadura del cabezal (Tablero 2.3). La Tabla C.2 "
                        "trae las demas configuraciones de borde",
    ),

    "geometria_control_salida": Criterio(
        valor="seccion_llena",
        etiqueta="C",
        concepto="Seccion de referencia de la que se toman V y R en la ecuacion "
                 "de control de salida H = (1 + ke + 19.63*n^2*L/R^(4/3))*V^2/(2g)",
        justificacion="Sec. 4.3 escribe la ecuacion pero NO dice a que seccion "
                      "pertenecen V y R, y la eleccion no es cosmetica: con la "
                      "seccion llena de un tubo de 0.90 m, R = D/4 = 0.225 m; con "
                      "el tirante normal de y/D = 0.75, R = 0.2715 m. La misma "
                      "formula da dos H distintas. Se adopta la SECCION LLENA "
                      "(A = pi*D^2/4, R = D/4, V = Q/A) porque es la seccion para "
                      "la que HDS-5 deriva esa expresion: los tres sumandos "
                      "(1 = carga de velocidad, ke = perdida de entrada, "
                      "19.63*n^2*L/R^(4/3) = perdida por friccion) son las "
                      "perdidas de un barril trabajando LLENO, que es el caso de "
                      "control de salida por definicion. Aplicarla sobre la "
                      "geometria del tirante normal mezcla dos regimenes. "
                      "TRAZABILIDAD: el caso patron CP-8 de "
                      "tests/fixtures/casos_patron.py alimenta la formula con "
                      "R = 0.27152 y V = 2.2807, que son los de la seccion "
                      "parcialmente llena de CP-2. CP-8 no contradice esto: es un "
                      "caso patron de la CONSTANTE SI (19.63) frente al 29 imperial, "
                      "y "
                      "para eso da V y R como datos sueltos, no como la geometria "
                      "de un control de salida real",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Cap. III - control de salida a "
               "seccion llena. Sec. 4.3 de la hoja de ruta cita la ecuacion sin "
               "definir la seccion",
        reemplazado_por="Procedimiento de barril parcialmente lleno de HDS-5 "
                        "(longitud de la seccion llena, Cap. III) si el "
                        "expediente lo exige",
        verificacion_pendiente="Con TW bajo y pendiente pronunciada el barril "
                               "puede no llegar a llenarse y el control de salida "
                               "no gobierna igualmente; verificar que el punto "
                               "donde el control de salida GOBIERNE sea uno donde "
                               "la hipotesis de seccion llena tenga sentido fisico",
    ),

    "HW_D_max": Criterio(
        valor=1.5,
        etiqueta="C",
        concepto="Relacion maxima de carga a la entrada sobre diametro",
        justificacion="El Manual MTC no define HW/D. Se adopta el extremo "
                      "superior del rango que HDS-5 da para el diseno "
                      "corriente, 1.0-1.5. El control gobernante del embalse "
                      "sigue siendo la verificacion V5 (remanso dentro del "
                      "derecho de via). "
                      "SOBRE LA SENSIBILIDAD: la banda declarada es "
                      "(1.2, 1.5), no el rango completo (1.0, 1.5) de la "
                      "fuente. Se conserva a proposito -- es la banda que el "
                      "proyecto considera defendible para este corredor -- y "
                      "se deja dicho que es un SUBRANGO, para que nadie la "
                      "confunda con lo que dice HDS-5",
        fuente="HDS-5 (FHWA) 3a ed., abril 2012, Sec. 2.2.5, pag. 2.14 - "
               "rango de HW/D de 1.0 a 1.5 para el diseno corriente. CITA "
               "CERRADA por verificacion externa contra el documento: antes "
               "decia solo 'practica corriente', sin seccion ni pagina",
        sensibilidad=(1.2, 1.5),
    ),

    "resguardo_HW_subrasante": Criterio(
        valor="segun_CBR",          # 0.60 / 0.80 / 1.00 / 1.20 m
        etiqueta="N->",
        concepto="Resguardo entre nivel de agua a la entrada y subrasante",
        justificacion="El numeral 4.5.4 regula la separacion frente al NIVEL "
                      "FREATICO, no frente a un nivel transitorio de avenida. Se "
                      "aplica POR ANALOGIA por ser el unico parametro normativo "
                      "nacional que protege la subrasante de la saturacion. La "
                      "analogia es conservadora y debe declararse en la memoria",
        fuente="Manual de Suelos MTC, numeral 4.5.4 y 9.1(3)",
    ),

    "TW_receptor": Criterio(
        valor=None,                 # VACIO hasta obtener Q del receptor
        etiqueta="A",
        concepto="Nivel de agua en el cuerpo receptor durante la avenida",
        justificacion="No se mide: se calcula con Manning en el receptor usando "
                      "su propio caudal de diseno. Sin ese dato se adoptan dos "
                      "escenarios acotados (salida libre / seccion llena)",
        fuente="PENDIENTE: ANA / Junta de Usuarios del Bajo Piura",
        reemplazado_por="Caudal de diseno documentado del dren o canal receptor",
    ),

    "long_max_cuneta": Criterio(
        valor=200.0,
        etiqueta="A",
        concepto="Longitud maxima de cuneta -> espaciamiento de alcantarillas de alivio",
        justificacion="El Manual fija 250 m para region seca y 200 m para region "
                      "muy lluviosa. El regimen normal de Piura es arido, pero el "
                      "evento de diseno relevante es el FEN, durante el cual la "
                      "zona se comporta como region muy lluviosa. Se adopta 200 m",
        fuente="Manual MTC, numeral 4.1.2.1 d), pag. 178",
        sensibilidad=(200.0, 250.0),
    ),

    # ----------------------- FASE 5: VACIOS DE VERIFICACION ---------------
    # Tres filas de la tabla de Fase 5 (V5, V7, V8) enuncian el REQUISITO
    # pero no entregan la formula ni el dato con que M5 pueda evaluarlo.
    # Cada uno se detiene aqui, no en M5, para que quede escrito por que
    # falta y que lo resolveria -- nunca un valor supuesto en silencio.
    #
    # V7 ya NO es de esta clase: Fase 8 (M8_estructural.py) implementa el
    # procedimiento completo, y desde la correccion del marco LRFD es un
    # equilibrio de factores de carga, no un FS global. Lo que sigue faltando
    # son dos datos puntuales del procedimiento -- 'peso_especifico_relleno_kn_m3'
    # (mas abajo, seccion de Fase 8) y 'factores_carga_aashto' (seccion de
    # Fase 9, compartido con M9) -- no la formula ni el metodo, que ya estan
    # escritos.

    "remanso_derecho_via": Criterio(
        valor=None,                 # VACIO: bloquea V5 para todo punto
        etiqueta="A",
        concepto="Extension del remanso aguas arriba de la alcantarilla y "
                 "ancho de derecho de via disponible en el punto, para V5 "
                 "(embalse dentro del derecho de via, sin afectar terceros "
                 "ni la faja marginal)",
        justificacion="Sec. 4.2 y el DG-2018 exigen la condicion pero no dan "
                      "metodo: la hoja de ruta no entrega un procedimiento de "
                      "perfil de remanso (curva de remanso aguas arriba del "
                      "embalse) ni el dato de ancho de derecho de via por "
                      "punto -- este ultimo tampoco es columna del CSV "
                      "(Sec. 1.2). Sin el metodo Y el dato, V5 no tiene con "
                      "que comparar el HW calculado por M4",
        fuente="PENDIENTE - Manual de Diseño Geometrico DG-2018 + Ley 29338 "
               "(Fase 5, V5). Requiere perfil de remanso (paso a paso o "
               "HEC-RAS) y el ancho de derecho de via del expediente vial",
        reemplazado_por="Perfil de remanso calculado aguas arriba del punto "
                        "y ancho de derecho de via declarado por punto",
        verificacion_pendiente="Definir si el ancho de derecho de via es un "
                               "dato por punto (nueva columna del CSV) o un "
                               "criterio unico del tramo",
    ),

    "TR_evento_extremo": Criterio(
        valor=None,                 # VACIO: bloquea V8 para todo punto
        etiqueta="A",
        concepto="Periodo de retorno del evento extremo de V8 y el umbral "
                 "que define 'la via no colapsa aunque desborde'",
        justificacion="Sec. 5 (V8) exige verificar el punto a un TR MAYOR "
                      "que el de diseno y confirmar que la via no colapsa "
                      "aunque desborde, pero la hoja de ruta no fija ese TR "
                      "mayor ni un umbral cuantitativo de 'colapso' (p.ej. "
                      "HW sobre la corona del terraplen). Sin el TR no hay "
                      "Q que correr por M3/M4 aparte del Q de diseno, y sin "
                      "el umbral no hay con que comparar el HW resultante",
        fuente="PENDIENTE - Fase 5, V8 de la hoja de ruta: '[N] verificacion, "
               "no diseño', sin numeral que fije el TR ni el umbral",
        reemplazado_por="TR del evento extremo (p.ej. el de la serie FEN de "
                        "la Fase 1-bis) y definicion tecnica de colapso de "
                        "la via, ambos declarados en la memoria",
    ),

    # ----------------------- GEOTECNIA -----------------------------------

    "phi_relleno_trasdos": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Angulo de friccion interna del material de cantera del trasdos",
        justificacion="Estimado por correlacion desde granulometria y grado de "
                      "compactacion especificado",
        fuente="PENDIENTE",
        reemplazado_por="Ensayo de corte directo sobre el material de cantera",
        sensibilidad=(30.0, 38.0),
    ),

    "c_phi_fundacion": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Parametros de resistencia del suelo de fundacion",
        justificacion="Correlacion desde clasificacion SUCS de calicatas. E.050 "
                      "Art. 20 obliga a usar solo uno: phi=0 en cohesivos, "
                      "c=0 en friccionantes",
        fuente="PENDIENTE",
        reemplazado_por="Corte directo o SPT",
    ),

    "capacidad_portante_adm": Criterio(
        valor=None,                 # completar
        etiqueta="A",
        concepto="Capacidad portante admisible del terreno de fundacion",
        justificacion="Derivada de c_phi_fundacion, que es a su vez adoptado",
        fuente="PENDIENTE",
        reemplazado_por="EMS conforme a E.050",
    ),

    "Mw_licuefaccion": Criterio(
        valor=None,                 # VACIO: bloquea la evaluacion de licuefaccion
        etiqueta="A",
        concepto="Magnitud sismica para el factor de escala de magnitud (MSF)",
        justificacion="El procedimiento simplificado de evaluacion de licuefaccion "
                      "no se alimenta solo de a_max: requiere Mw para el MSF. El "
                      "mapa de PGA no la entrega",
        fuente="PENDIENTE: desagregacion del peligro sismico o adopcion justificada "
               "del sismo de diseno de la subduccion del norte peruano",
        reemplazado_por="Estudio de peligro sismico especifico",
    ),

    "demanda_sismica_licuefaccion": Criterio(
        valor=1000,                 # anios
        etiqueta="A",
        concepto="Periodo de retorno para la evaluacion de licuefaccion",
        justificacion="Se descarta el sismo de 475 anios de E.030. Al tratarse de "
                      "infraestructura vial regida por el Manual de Puentes, se "
                      "exige al suelo la misma demanda que a la estructura que "
                      "soporta. Un terreno evaluado a 475 anios bajo una estructura "
                      "disenada a 1000 es incoherencia de niveles de seguridad",
        fuente="Coherencia con el marco del Manual de Puentes",
        sensibilidad=(475, 1000),
    ),

    "diametros_normalizados": Criterio(
        valor={"inicio": 0.90, "paso": 0.15,
               "max": {"concreto_reforzado": 2.70, "tmc": 2.10, "hdpe": 1.50}},
        etiqueta="C",
        concepto="Progresion de diametros y topes por material",
        justificacion="Neutralidad comercial exigible en obra publica: no se usan "
                      "catalogos de proveedor. El paso de 0.15 m reproduce las "
                      "series de 6 pulgadas (ASTM/AASHTO) y de 150 mm (M294) con "
                      "error despreciable. Usar 0.90 en vez de 0.9144 subestima el "
                      "area ~3%, del lado de la seguridad",
        fuente="ASTM C76/AASHTO M170; AASHTO M36/ASTM A760; AASHTO M294",
        verificacion_pendiente="Confirmar los topes superiores contra el texto de "
                               "cada norma de producto. El de HDPE (~1.50 m) es el "
                               "mas restrictivo y puede descartar el material",
    ),

    "h_relleno_min_concreto_tmc": Criterio(
        valor=None,                 # VACIO: bloquea el tamizado 7.A en concreto y TMC
        etiqueta="C",
        concepto="Altura minima de relleno sobre la clave para concreto y TMC",
        justificacion="EG-2013 fija 0.30 m para HDPE/PAD (508.07/508.08) pero "
                      "NO fija el valor para concreto ni TMC: remite al Proyecto "
                      "y a la norma de producto. El tamizado previo de 7.A no "
                      "puede fijar la rasante sin este dato, porque la cota de "
                      "rasante depende de cota clave + h_rec + espesor del paquete",
        fuente="PENDIENTE - AASHTO M-170M (clases I a V) para concreto; "
               "ASTM A-807 / AASHTO M36 para TMC. Falta EXTRAER el valor por "
               "clase o calibre y altura de relleno",
        reemplazado_por="Tabla de alturas admisibles de la norma de producto "
                        "para la clase o calibre seleccionado en la Fase 8",
        verificacion_pendiente="Nota constructiva [N] que si es firme: el equipo "
                               "pesado no circula sobre el conducto antes de que "
                               "el relleno alcance 0.30 m (Sec. 7.A)",
    ),

    # ----------------------- FASE 8: ESTRUCTURAL DEL CONDUCTO -------------
    # Seleccion de clase/calibre por norma de producto (items 1-2) y V7 -
    # flotacion (item 3). El resto de Fase 8 (item 5: rigidez de anillo,
    # pandeo, costura) NO se calcula por decision expresa de la hoja de
    # ruta -- se difiere al expediente tecnico, ver
    # M8_estructural.verificacion_diferida_estructural().

    # 'NF_profundidad_m' ya no vive aqui: es un dato de sitio [S] que se mide
    # en cada cruce, no una exigencia normativa, y por eso es COLUMNA DEL CSV
    # (ver modelos.PuntoCritico y M0_carga.COLUMNAS). El 1.4 m que este
    # criterio declaraba era la caracterizacion general de la llanura del Bajo
    # Piura, y su propia `verificacion_pendiente` ya avisaba de que podia no
    # ser uniforme dentro del tramo; repetirlo en las cuatro filas del CSV
    # habria fingido cuatro mediciones donde hubo una descripcion de zona.

    "clases_producto_por_relleno": Criterio(
        valor=None,                 # VACIO: bloquea la seleccion de Fase 8, items 1-2
        etiqueta="C",
        concepto="Tabla de clase (concreto, AASHTO M-170M I-V) o calibre "
                 "(TMC, ASTM A-807/AASHTO M36) admisible segun la altura de "
                 "relleno sobre la clave, para Fase 8 items 1-2: seleccionar "
                 "la clase/calibre por altura real y verificar que esa "
                 "altura cae en el rango admisible de la clase elegida",
        justificacion="Ninguna de las dos tablas (AASHTO M-170M clases I-V "
                      "por diametro y altura de relleno; ASTM A-807/AASHTO "
                      "M36 calibre por altura) esta transcrita en la hoja de "
                      "ruta -- es el MISMO vacio de norma de producto ya "
                      "declarado en 'h_relleno_min_concreto_tmc' (Sec. 7.A), "
                      "pero alli solo hacia falta un minimo escalar y aqui "
                      "hace falta la tabla completa de clases con su rango "
                      "admisible. HDPE (AASHTO M294) no tiene tabla de clase "
                      "por altura: su seleccion depende de un calculo de "
                      "rigidez de anillo que Fase 8, item 5, difiere "
                      "expresamente al expediente tecnico",
        fuente="PENDIENTE - AASHTO M-170M (clases I-V, concreto); "
              "ASTM A-807 / AASHTO M36 (calibre por altura, TMC). Falta "
              "EXTRAER la tabla completa (clase o calibre x diametro x "
              "rango de altura de relleno)",
        reemplazado_por="Tabla de clase/calibre por altura de relleno de la "
                        "norma de producto, extraida y transcrita con su "
                        "numeral",
    ),

    # 'FS_flotacion' SE RETIRO. Declaraba el factor de seguridad global de
    # ΣW >= FS*U, que es lenguaje de TENSION ADMISIBLE, y V7 se reescribio
    # como el equilibrio de factores de carga que corresponde al marco LRFD
    # que adopta Sec. 0.2:
    #
    #     gamma_DC_min * DC + gamma_EV_min * EV  >=  gamma_WA * U
    #
    # No se le redefinio el contenido porque en LRFD no queda nada que
    # represente: el margen entre estabilizante y desestabilizante lo hacen
    # ahora los propios gamma, y conservar ademas un FS seria contar dos veces
    # el mismo margen. Los gamma NO son un criterio nuevo: salen de
    # 'factores_carga_aashto', mas abajo, el mismo del que come M9 (Sec. 9.2).
    # Que Fase 8 y Fase 9 lean la misma declaracion es lo que impide que el
    # expediente termine con dos juegos de factores de carga distintos.

    "peso_especifico_relleno_kn_m3": Criterio(
        valor=None,                 # VACIO: bloquea el termino Sigma W de V7
        etiqueta="A",
        concepto="Peso especifico del material de relleno sobre la clave, "
                 "para el termino ΣW de V7 (peso del prisma de relleno que "
                 "se opone a la flotacion)",
        justificacion="Ni la hoja de ruta ni el CSV (Sec. 1.2) traen el "
                      "peso especifico del material de relleno: depende de "
                      "la cantera que finalmente se especifique. V7 lo "
                      "necesita para pesar el prisma de relleno sobre la "
                      "clave (ancho D, altura la del punto -- ver "
                      "M8_estructural.peso_relleno_kn_m). El peso propio del "
                      "conducto NO se suma: omitirlo es conservador (reduce "
                      "ΣW) y evita depender del espesor de pared que "
                      "'clases_producto_por_relleno' todavia no resuelve",
        fuente="PENDIENTE - ensayo de peso especifico del material de "
              "cantera propuesto, o valor de practica corriente declarado "
              "con su fuente en la memoria",
        reemplazado_por="Peso especifico medido del material de relleno "
                        "efectivamente especificado en el proyecto",
        sensibilidad=(17.0, 20.0),   # kN/m3, rango corriente de rellenos compactados
    ),

    # ----------------------- FASE 7: COMPATIBILIDAD GEOMETRICA ------------
    # 7.A queda resuelto con lo ya declarado (h_relleno_min_concreto_tmc para
    # el recubrimiento y resguardo_HW_subrasante para la carga a la entrada).
    # Lo que 7.B abre es la LONGITUD del conducto.

    "talud_terraplen": Criterio(
        valor=None,                 # VACIO: bloquea la longitud del conducto en 7.B
        etiqueta="A",
        concepto="Inclinacion del talud del terraplen en el punto de cruce, "
                 "como proyeccion horizontal por unidad de altura (H:V), para "
                 "la 'proyeccion de taludes' que Sec. 7.B suma al ancho de "
                 "plataforma al calcular la longitud del conducto",
        justificacion="Sec. 7.B define la longitud como 'ancho de plataforma + "
                      "proyeccion de taludes, afectada por esviaje', pero no "
                      "entrega la inclinacion del talud ni una regla para "
                      "deducirla, y Sec. 1.2 no la trae como columna: el unico "
                      "dato de seccion transversal que llega por punto es el "
                      "ancho de plataforma. El vacio no se puede tapar con lo "
                      "que ya esta en el CSV -- la altura de terraplen del "
                      "punto (cota_rasante - cota_terreno) da el BRAZO "
                      "VERTICAL del talud, no su inclinacion -- y sin longitud "
                      "no hay caida S*L ni cota de salida que amarrar al fondo "
                      "del receptor, que es la otra mitad de 7.B. Adoptar en "
                      "silencio un 1.5:1 de practica corriente moveria la "
                      "longitud, la caida y la cota de salida de todos los "
                      "puntos sin que nadie pueda rastrear de donde salio",
        fuente="PENDIENTE - Manual de Diseño Geometrico DG-2018 y la seccion "
               "tipica del proyecto, que fijan el talud del terraplen segun su "
               "altura y el material del cuerpo",
        reemplazado_por="Talud de la seccion tipica del expediente vial, o la "
                        "longitud medida directamente sobre la seccion "
                        "transversal de cada punto",
        verificacion_pendiente="Declarar si el talud es unico para el tramo o "
                               "varia por punto con la altura de terraplen. M7 "
                               "lo aplica hoy a los DOS taludes con la misma "
                               "altura (terraplen simetrico sobre el terreno "
                               "natural del cruce), que es lo unico que el CSV "
                               "permite calcular: si la seccion es asimetrica, "
                               "la longitud se mide y no se deduce",
    ),

    # ----------------------- PROTECCION Y DETALLE -------------------------

    "espesor_proteccion_salida": Criterio(
        valor=1.75,                 # multiplicador de d50
        etiqueta="A",
        concepto="Espesor de la capa de proteccion, como multiplo de d50",
        justificacion="El Manual solo entrega d50 (Laushey). El espesor, la "
                      "longitud y la granulometria completa no estan normados. "
                      "Se adopta el rango corriente 1.5-2.0 d50",
        fuente="Practica corriente de diseno de enrocado",
        sensibilidad=(1.5, 2.0),
    ),

    "longitud_proteccion_salida": Criterio(
        valor=None,                 # VACIO: completa el diseno de la Fase 6
        etiqueta="A",
        concepto="Longitud de la proteccion aguas abajo de la salida",
        justificacion="Laushey (num. 4.1.1.3.7 c) entrega d50 y nada mas. La "
                      "hoja de ruta declara expresamente que el espesor, la "
                      "LONGITUD aguas abajo, la granulometria completa y el "
                      "filtro quedan fuera de la norma. Sin filtro el enrocado "
                      "se socava por debajo y falla: la longitud sola no basta, "
                      "pero sin ella no hay pieza que dimensionar",
        fuente="PENDIENTE - Sec. 6 de la hoja de ruta la marca [A] sin valor. "
               "Practica corriente de diseno de enrocado o HEC-14",
        reemplazado_por="Diseno de disipador o transicion del expediente",
        verificacion_pendiente="Con pendientes bajas los d50 son de 3-13 cm y lo "
                               "probable es que gobierne el emboquillado de piedra "
                               "por razones constructivas, no el enrocado",
    ),

    "angulo_aletas": Criterio(
        valor=None,                 # completar segun esviaje
        etiqueta="A",
        concepto="Angulo de las aletas del cabezal",
        justificacion="Ajustado al esviaje del cauce en cada punto",
        fuente="Practica corriente; no fijado por el Manual",
    ),

    # ----------------------- FASE 9: CABEZAL Y ALETAS ---------------------
    # Sec. 9.2 nombra las combinaciones y la cadena sismica; Sec. 9.3 da los
    # FS; Sec. 9.4 remite el diseno a AASHTO LRFD Sec. 5. Lo que NO transcribe
    # son las tablas numericas de esas tres remisiones. Cada vacio se declara
    # aqui en vez de rellenarse con el valor "de siempre".

    "factores_carga_aashto": Criterio(
        valor={
            "Resistencia I": {
                "DC": {"max": 1.25, "min": 0.90},
                "EV": {"max": 1.35, "min": 0.90},
                "EH": {"max": 1.50, "min": 0.90},        # empuje ACTIVO -- caso de diseno del proyecto
                "EH_en_reposo": {"max": 1.35},           # informativo: el proyecto disena con empuje activo, no en reposo
                "LS": 1.75,
                "WA": {"max": 1.00, "min": 1.00},
            },
            "Servicio I": {
                "DC": {"max": 1.00, "min": 1.00},
                "EV": {"max": 1.00, "min": 1.00},
                "EH": {"max": 1.00, "min": 1.00},
                "LS": 1.00,
                "WA": {"max": 1.00, "min": 1.00},
            },
            "Evento Extremo I": {
                "DC": {"max": 1.00, "min": 1.00},
                "EV": {"max": 1.00, "min": 1.00},
                "EH": {"max": 1.00, "min": 1.00},
                "LS": "gamma_EQ",   # 0.50 o 0.00 -- a criterio del propietario, ver verificacion_pendiente
                "WA": {"max": 1.00, "min": 1.00},
                "EQ": {"max": 1.00, "min": 1.00},
            },
        },
        etiqueta="C",
        concepto="Factores gamma de las tres combinaciones de Sec. 9.2 "
                 "(Resistencia I, Servicio I, Evento Extremo I) por tipo de "
                 "carga: DC, EV, EH, LS, WA, EQ, con sus maximos y minimos",
        justificacion="Sec. 9.2 NOMBRA las tres combinaciones con numeral "
                      "(2.4.5.3, AASHTO LRFD Sec. 3.4.1) pero no transcribia "
                      "la Tabla 3.4.1-1 ni la 3.4.1-2. Sin los factores, una "
                      "combinacion es una lista de cargas, no una demanda. "
                      "CERRADO por verificacion externa contra la fuente: "
                      "los factores de EH y EV son DOBLES (gamma maximo y "
                      "minimo) y cual de los dos gobierna depende de si la "
                      "carga estabiliza o desestabiliza cada verificacion -- "
                      "escribir 1.35 para el empuje de tierras en todas las "
                      "filas habria sido el error clasico y da del lado "
                      "inseguro en volteo; la tabla fuente da EV minimo "
                      "0.90, no 1.00. La Tabla 3.4.1-2 ademas distingue EH "
                      "activo (1.50/0.90) de EH en reposo (1.35, sin minimo "
                      "declarado por la fuente): el proyecto disena con "
                      "empuje ACTIVO (Mononobe-Okabe/Coulomb, ver "
                      "'inclinacion_muro_beta' y companeros), asi que 'EH' "
                      "es el activo y 'EH_en_reposo' queda solo como dato "
                      "informativo de la tabla. Evento Extremo I lleva "
                      "gamma_EQ en la carga LS, que la propia AASHTO deja a "
                      "criterio del propietario (0.50 o 0.00): no se fija "
                      "aqui un numero, se declara la eleccion pendiente",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tablas "
               "3.4.1-1 (pag. 3-14) y 3.4.1-2 (pag. 3-18); transcritas "
               "tambien en Manual de Puentes MTC, pags. 143 y 146",
        verificacion_pendiente="gamma_EQ (carga LS de Evento Extremo I) "
                               "queda a criterio del propietario del "
                               "proyecto (0.50 o 0.00, AASHTO LRFD "
                               "C3.4.1): declarar en la memoria cual se "
                               "adopta y por que, antes de evaluar esa "
                               "combinacion",
    ),

    "peso_especifico_concreto_kn_m3": Criterio(
        valor=23.56,                # kN/m3, concreto armado (0.150 kcf)
        etiqueta="C",
        concepto="Peso especifico del concreto armado del cabezal, kN/m3",
        justificacion="Es el peso propio (carga DC) que resiste el volteo y "
                      "el deslizamiento de Sec. 9.3: sin el no hay momento "
                      "estabilizante ni fuerza normal en la base. CERRADO "
                      "por verificacion externa: AASHTO LRFD Tabla 3.5.1-1 "
                      "+ Comentario C3.5.1 dan 0.150 kcf (concreto normal "
                      "armado) = 23.56 kN/m3. El valor cae dentro del rango "
                      "de practica corriente (23.5-24.5 kN/m3) que este "
                      "criterio manejaba antes de tener cita directa, pero "
                      "no se adopta el redondeo regional de 24.0: ese numero "
                      "no tiene fuente propia y 23.56 si la tiene",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tabla "
               "3.5.1-1 + Comentario C3.5.1, pag. 3-21 (0.150 kcf, concreto "
               "normal armado)",
    ),

    "predimensionamiento_cabezal": Criterio(
        valor=None,                 # VACIO: bloquea la estabilidad automatica
        etiqueta="A",
        concepto="Geometria del cabezal (altura H sobre zapata, ancho de "
                 "zapata B, profundidad de desplante D_f, espesor de la "
                 "pantalla en corona y en su arranque, espesor de zapata e "
                 "inclinacion beta del trasdos), en m",
        justificacion="Sec. 9.1 fija QUE es el cabezal (Sec. 503, concreto "
                      "estructural) y COMO es su embocadura (tubo a ras, "
                      "square edge, amarrada a las constantes HDS-5 de "
                      "Sec. 4.2), pero no lo dimensiona, y Sec. 1.2 no trae "
                      "ninguna columna con su geometria. Sin H no hay empuje, "
                      "sin B no hay momento estabilizante ni presion de "
                      "contacto, sin D_f no hay confinamiento. Las funciones "
                      "de M9 aceptan la geometria como argumento explicito "
                      "para poder tantear; lo que este vacio bloquea es que "
                      "el cabezal se dimensione SOLO, sin que nadie declare "
                      "de donde salieron las dimensiones",
        fuente="PENDIENTE - predimensionamiento del proyectista, o plano tipo "
               "de cabezal del expediente vial",
        reemplazado_por="Plano de encofrado del cabezal, acotado",
        verificacion_pendiente="La geometria tiene que ser COMPATIBLE con el "
                               "diametro adoptado en la Fase 4 y con la "
                               "altura de terraplen de la Fase 7: un cabezal "
                               "declarado aparte del conducto que remata es "
                               "una incoherencia de expediente",
    ),

    "N_cq_N_gammaq_meyerhof": Criterio(
        valor=None,                 # VACIO: bloquea la capacidad portante en talud
        etiqueta="A",
        concepto="Factores de capacidad de carga N_cq y N_gamma_q para zapata "
                 "proxima a talud (Meyerhof 1957), leidos de las figuras "
                 "2.8.1.3.1.2c-1 y -2 del Manual de Puentes",
        justificacion="Sec. 9.3 es taxativa en que el cabezal se apoya en el "
                      "BORDE DEL TERRAPLEN y no en terreno horizontal, y en "
                      "que la penalizacion es severa por perdida de "
                      "confinamiento: N_q = 0.0 (eso si es un numero y esta "
                      "en constantes_normativas), y N_c y N_gamma se "
                      "REEMPLAZAN por N_cq y N_gamma_q. Pero esos dos salen "
                      "de FIGURAS, no de una formula ni de una tabla: "
                      "dependen de la distancia de la zapata al borde, de la "
                      "altura del talud y de su inclinacion, y no hay forma "
                      "de transcribirlos sin leer los abacos para la "
                      "geometria concreta de cada punto. Usar N_c y N_gamma "
                      "de terreno horizontal aqui seria exactamente la "
                      "sobrestimacion que la hoja de ruta advierte",
        fuente="PENDIENTE - Manual de Puentes num. 2.8.1.3.1.2c, figuras "
               "2.8.1.3.1.2c-1 y 2.8.1.3.1.2c-2 (Meyerhof 1957), pags. 272-273",
        reemplazado_por="Lectura de los abacos para la geometria real de cada "
                        "cabezal, adjuntada a la memoria",
        verificacion_pendiente="E.050 Art. 30.1-30.2 exige ADEMAS la "
                               "verificacion por inclinacion de la superficie "
                               "y de la base, y el analisis de estabilidad "
                               "global del talud con la estructura "
                               "cargandolo: son dos comprobaciones, no una "
                               "(Sec. 9.3, 'doble verificacion')",
    ),

    "metodo_estabilidad_global": Criterio(
        valor=None,                 # VACIO: bloquea las filas E4 y E5 de Sec. 9.3
        etiqueta="A",
        concepto="Metodo de analisis de estabilidad global del muro y del "
                 "talud que lo soporta (equilibrio limite: Bishop "
                 "simplificado, Spencer, Morgenstern-Price...)",
        justificacion="La tabla de Sec. 9.3 exige FS = 1.50 estatico y 1.25 "
                      "sismico para la estabilidad global del muro "
                      "(39.13.6 b) y para la del talud (Art. 30.3), pero un "
                      "FS de estabilidad global no se calcula con una "
                      "formula cerrada: sale de un analisis de superficies "
                      "de falla que exige el perfil estratigrafico completo, "
                      "la geometria del terraplen y un metodo declarado. "
                      "Ninguna de las tres cosas esta en el alcance del CSV "
                      "de Sec. 1.2. El FS existe y esta transcrito; lo que "
                      "falta es con que producir el valor a comparar",
        fuente="PENDIENTE - E.050 Art. 30.3 y num. 39.13.6 b) fijan el "
               "umbral, no el metodo. El analisis es del EMS del expediente",
        reemplazado_por="Analisis de estabilidad de taludes del estudio "
                        "geotecnico, con su metodo y sus superficies criticas",
    ),

    "recubrimiento_aashto_mm": Criterio(
        valor={"contra_suelo": 75.0, "suelo_intemperie_ge_3_4": 75.0,
              "suelo_intemperie_le_5_8": 75.0},
        etiqueta="C",
        concepto="Recubrimiento minimo del refuerzo exigido por AASHTO LRFD, "
                 "en mm, por condicion de exposicion, para compararlo con el "
                 "de E.060 Art. 7.7.1",
        justificacion="Sec. 0.2 fija la regla de conflicto: 'rige el "
                      "recubrimiento MAYOR entre AASHTO y E.060'. CERRADO "
                      "por verificacion externa: AASHTO LRFD Tabla 5.10.1-1 "
                      "no organiza el recubrimiento por diametro de barra "
                      "como E.060 (>= 3/4\" / <= 5/8\") -- lo organiza por "
                      "severidad de EXPOSICION. La Union (Piura) es corredor "
                      "costero, y la categoria de exposicion aplicable de "
                      "AASHTO es 'ambiente costero' = 75 mm, uniforme sin "
                      "importar el diametro de barra. Como 75 > 70 "
                      "(contra_suelo de E.060) y 75 > 50 y 75 > 40 (los dos "
                      "casos de intemperie de E.060), AASHTO gobierna en los "
                      "tres casos por la regla del mayor: no son tres "
                      "lecturas distintas de AASHTO, es el mismo valor de "
                      "exposicion costera aplicado a los tres casos de "
                      "E.060, declarado explicito en las tres claves para "
                      "que la memoria muestre la comparacion caso por caso",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., Tabla "
               "5.10.1-1, pag. 5-169, categoria de exposicion 'ambiente "
               "costero'",
        verificacion_pendiente="Con NF a 1.4 m y suelos salinos, E.060 "
                               "Art. 7.7.5.1 (ambiente corrosivo, 'aumentar "
                               "adecuadamente') es directamente invocable "
                               "(Sec. 3.3): el aumento se declara aparte, "
                               "porque el articulo no fija cuanto",
    ),

    "cortante_alto_muro_e060_art_11_10_10_2": Criterio(
        valor=None,                 # VACIO: bloquea el escalon de rho a 0.0025
        etiqueta="A",
        concepto="Si el muro del cabezal esta en la condicion de CORTANTE "
                 "ALTO de E.060 Art. 11.10.10.2, que escalona la cuantia "
                 "horizontal minima de 0.0020 a 0.0025",
        justificacion="E.060 no tiene un solo minimo de cuantia horizontal "
                      "de muro: tiene dos. El Art. 14.3.1 fija 0.0020, y el "
                      "Art. 11.10.10.2 lo sube a 0.0025 cuando la demanda de "
                      "cortante supera el umbral que ese articulo define "
                      "(del orden de Vu > 0.5*phi*Vc). Aplicar solo el "
                      "0.0020 sin comprobar el otro es quedarse con el "
                      "minimo mas bajo de los dos por omision. "
                      "POR QUE NO SE RESUELVE AQUI Y NO SE RELLENA: el "
                      "disparador es una DEMANDA DE CORTANTE, y M9 no "
                      "calcula cortante -- el diseno por flexion y corte "
                      "esta bloqueado entero en "
                      "'procedimiento_flexion_corte_aashto_sec5', que es de "
                      "AASHTO LRFD Sec. 5 por la Via 1 de Sec. 0.2. Sin Vu "
                      "no hay forma de contestar si el muro esta o no en esa "
                      "condicion, y contestar 'no' por defecto seria elegir "
                      "el minimo mas bajo en silencio, que es exactamente el "
                      "error que este archivo existe para impedir. "
                      "Se declara VACIO y `M9.cuantia_de_diseno` lo exige a "
                      "quien la llame: o se declara aqui, o el calculo se "
                      "detiene. "
                      "NOTA DE TAXONOMIA: el 0.0025 en si es [N] "
                      "-- articulo peruano vigente -- y su sitio natural "
                      "seria constantes_normativas.py. No esta alli porque "
                      "la hoja de ruta no transcribe el Art. 11.10.10.2: "
                      "solo cita el 14.3.1. Mientras la hoja de ruta no lo "
                      "recoja, el numero viaja en esta justificacion y no "
                      "como constante [N], para no crear una cita normativa "
                      "que la fuente de verdad del proyecto no respalda. "
                      "Ademas, la Via 1 de Sec. 0.2 abre una pregunta previa "
                      "que tambien hay que contestar en la memoria: si el "
                      "diseno estructural es de AASHTO, cual de los dos "
                      "minimos de E.060 se importa y con que argumento",
        fuente="PENDIENTE - E.060 Art. 11.10.10.2 (cuantia horizontal "
               "minima en muros con cortante alto). Verificar numeral y "
               "pagina contra el texto de E.060 antes de darle valor, y "
               "recoger el articulo en la hoja de ruta",
        reemplazado_por="Demanda de cortante Vu del cabezal, salida del "
                        "diseno de 'procedimiento_flexion_corte_aashto_sec5', "
                        "contrastada contra el umbral del Art. 11.10.10.2",
        verificacion_pendiente="Al cerrarlo, declarar en la memoria las dos "
                               "cosas por separado: el valor de Vu con que se "
                               "decidio, y si el minimo aplicado es el 0.0020 "
                               "del Art. 14.3.1 o el 0.0025 del "
                               "Art. 11.10.10.2",
    ),

    "procedimiento_flexion_corte_aashto_sec5": Criterio(
        valor={
            "phi_flexion": 0.90,
            "phi_corte": 0.90,
            "modelo_corte": "MCFT_seccional_directo_no_iterativo "
                            "(AASHTO LRFD 9a ed., 2020)",
            "beta": "4.8 / (1 + 750*epsilon_s)",
            "theta_grados": "29 + 3500*epsilon_s",
            "Vc_kN": "0.0316*beta*lambda*raiz(f_c_prima)*bv*dv",
            "Vs_kN": "(Vu/phi) - Vc - Vp",
            "espaciamiento_s_m": "Av*fy*dv*cot(theta) / Vs",
            "dv_m": "max(de - a/2, 0.9*de, 0.72*h)",
        },
        etiqueta="C",
        concepto="Procedimiento de diseno por flexion y corte de AASHTO LRFD "
                 "Seccion 5: factores de resistencia phi, limites de refuerzo "
                 "y modelo de corte (MCFT / beta-theta) aplicables",
        justificacion="Sec. 9.4 remite el diseno a 'AASHTO LRFD Seccion 5' y "
                      "no transcribia nada de esa seccion, en coherencia con "
                      "la Via 1 de Sec. 0.2 (AASHTO de extremo a extremo, "
                      "E.060 solo para durabilidad y recubrimientos). "
                      "Mezclarlo con las expresiones de E.060 -- que si "
                      "estan a mano y que muchos usarian por costumbre -- "
                      "romperia justamente la consistencia carga-resistencia "
                      "que Sec. 0.2 declara RESUELTA: no se pueden combinar "
                      "demandas mayoradas por AASHTO con resistencias "
                      "reducidas por E.060. CERRADO por verificacion "
                      "externa: Art. 5.5.4.2 da phi = 0.90 para flexion y "
                      "para corte; Arts. 5.7.3.4.2, 5.7.3.3 y 5.7.2.8 dan el "
                      "Modelo Seccional MCFT en su procedimiento directo no "
                      "iterativo de la 9a ed. (2020), con beta, theta, Vc, "
                      "Vs y dv en forma cerrada. Las cuantias minimas de "
                      "E.060 Art. 14.3.1 que M9 aplica son un PISO "
                      "OBLIGATORIO sobre el resultado de este procedimiento "
                      "-- rho_diseno = max(rho_calculado, rho_minimo) -- no "
                      "una nota de referencia: el rho que salga de AASHTO "
                      "entra por `M9.cuantia_de_diseno` y el minimo lo "
                      "levanta si hace falta. Cerrar este dato declara el "
                      "PROCEDIMIENTO citado y disponible; el ENSAMBLE "
                      "completo (iterar epsilon_s, resolver Vs y el "
                      "espaciamiento para un momento y un cortante dados) "
                      "sigue sin implementarse en `M9.diseno_flexion_corte` "
                      "-- es una tarea de implementacion aparte, mas grande "
                      "que transcribir un dato, y no se acomete aqui",
        fuente="AASHTO LRFD Bridge Design Specifications, 9a ed., "
               "Arts. 5.5.4.2 (pag. 5-32) y 5.7.3.4.2 / 5.7.3.3 / 5.7.2.8 "
               "(pags. 5-70 a 5-243)",
    ),
}


# ---------------------------------------------------------------------------
# Coherencia de las etiquetas
# ---------------------------------------------------------------------------

ETIQUETAS_VALIDAS = ("N", "N->", "S", "C", "A")


def _coherencia_de_etiquetas() -> None:
    """
    Verifica al importar que ninguna entrada mezcle los dos modos de defensa.

    Es una guardia de arquitectura, no una validacion de dato: si falla, el
    archivo esta mal escrito y ninguna corrida deberia empezar. Un [S] sin
    trazabilidad seria un hecho de sitio que el revisor no puede reproducir, y
    un [S] con sensibilidad seria un hecho al que se le ofrece un rango de
    valores alternativos, que es justo lo que un hecho no tiene.
    """
    for clave, c in CRITERIOS.items():
        if c.etiqueta not in ETIQUETAS_VALIDAS:
            raise ValueError(
                f"'{clave}' lleva la etiqueta {c.etiqueta!r}, que no es de la "
                f"convencion {ETIQUETAS_VALIDAS}"
            )
        if c.etiqueta == "S":
            if not c.trazabilidad:
                raise ValueError(
                    f"'{clave}' es [S] y no declara trazabilidad. Un dato de "
                    "sitio se defiende diciendo como reproducir la lectura"
                )
            if c.sensibilidad:
                raise ValueError(
                    f"'{clave}' es [S] y declara sensibilidad. Un hecho de "
                    "sitio no tiene rango que elegir: si lo tuviera, seria [A]"
                )
        elif c.trazabilidad:
            raise ValueError(
                f"'{clave}' no es [S] y declara trazabilidad. El campo es "
                "exclusivo de los datos de sitio"
            )


_coherencia_de_etiquetas()


# ---------------------------------------------------------------------------
# Reporte para el modulo M11
# ---------------------------------------------------------------------------

# Orden de lectura, de mas determinado a mas elegido. [S] va entre [N->] y
# [C]: su procedimiento es normativo y propio del sitio, no prestado ni ajeno.
_ORDEN = {"N": 0, "N->": 1, "S": 2, "C": 3, "A": 4}


def reporte_criterios(solo_usados: bool = True) -> str:
    """
    Genera el bloque de declaracion de criterios para el reporte final.
    Con solo_usados=True lista unicamente los criterios que el calculo invoco.
    """
    claves = sorted(
        (_USADOS if solo_usados else set(CRITERIOS)),
        key=lambda k: (_ORDEN.get(CRITERIOS[k].etiqueta, 9), k),
    )
    if not claves:
        return "No se invoco ningun criterio adoptado."

    out = ["=" * 78,
           "DECLARACION DE CRITERIOS ADOPTADOS",
           "=" * 78, ""]

    for k in claves:
        c = CRITERIOS[k]
        valor_efectivo = _OVERRIDES.get(k, c.valor)
        marca_override = "  [declarado para esta corrida, no en archivo]" if k in _OVERRIDES else ""
        marca_prov = "  [PROVISIONAL: valor de prueba, NO verificado]" if c.provisional else ""
        out.append(f"[{c.etiqueta}] {k} = {valor_efectivo!r}{marca_override}{marca_prov}")
        out.append(f"     Concepto      : {c.concepto}")
        out.append(f"     Justificacion : {c.justificacion}")
        out.append(f"     Fuente        : {c.fuente}")
        if c.reemplazado_por:
            out.append(f"     Se sustituye por: {c.reemplazado_por}")
        if c.sensibilidad:
            out.append(f"     Sensibilidad  : {c.sensibilidad}")
        if c.trazabilidad:
            out.append(f"     Trazabilidad  : {c.trazabilidad}")
        if c.verificacion_pendiente:
            out.append(f"     >> VERIFICAR  : {c.verificacion_pendiente}")
        out.append("")

    pendientes = [k for k in claves if CRITERIOS[k].verificacion_pendiente]
    if pendientes:
        out.append("-" * 78)
        out.append("ADVERTENCIA: los siguientes criterios tienen verificaciones")
        out.append("pendientes y no deben citarse en la memoria hasta resolverlas:")
        for k in pendientes:
            out.append(f"  - {k}")
        out.append("-" * 78)

    sin_valor = criterios_sin_valor()
    if sin_valor:
        out.append("")
        out.append("-" * 78)
        out.append("VACIOS SIN VALOR: detienen el calculo en cuanto se invocan")
        out.append("(bloque aparte, Sec. 0.7 - no se sustituyen por defecto):")
        for k in sin_valor:
            out.append(f"  - [{CRITERIOS[k].etiqueta}] {k}: {CRITERIOS[k].concepto}")
        out.append("-" * 78)

    return "\n".join(out)


def parametros_sensibilizables() -> Dict[str, Tuple]:
    """Devuelve los criterios con rango declarado, para el analisis de sensibilidad."""
    return {k: c.sensibilidad for k, c in CRITERIOS.items() if c.sensibilidad}


if __name__ == "__main__":
    # Demostracion: cadena sismica completa desde una sola fuente. El PGA es
    # un dato de sitio [S] y entra desde datos_sitio.py, no desde aqui.
    import datos_sitio as ds

    A_s = ds.valor("PGA_roca_B") * valor("F_pga")
    k_h = valor("factor_muro_eleccion") * A_s
    valor("clase_sitio")

    print(f"A_s = {A_s:.2f} g")
    print(f"k_h = {k_h:.2f}")
    print(f"k_v = {valor('k_v'):.2f}\n")
    print(reporte_criterios())
