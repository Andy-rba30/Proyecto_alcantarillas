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
    C    Vacio normativo cubierto con fuente tecnica reconocida (FHWA, AASHTO)
    A    Sin norma ni fuente unica. Adopcion declarada + sensibilidad obligatoria
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple, Dict, List, Set

from modelos import CriterioPendienteError


# ---------------------------------------------------------------------------
# Estructura
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Criterio:
    valor: Any
    etiqueta: str                              # "N", "N->", "C", "A"
    concepto: str                              # que es
    justificacion: str                         # por que este valor
    fuente: str                                # de donde sale
    reemplazado_por: Optional[str] = None      # ensayo/dato que lo sustituye
    sensibilidad: Optional[Tuple] = None       # rango para analisis de sensibilidad
    verificacion_pendiente: Optional[str] = None   # lo que falta confirmar


_USADOS: Set[str] = set()


def valor(clave: str) -> Any:
    """Devuelve el valor del criterio y registra que fue usado."""
    if clave not in CRITERIOS:
        raise KeyError(
            f"'{clave}' no esta declarado en criterios_adoptados.py. "
            "Ningun parametro no normativo puede usarse sin declararse aqui."
        )
    _USADOS.add(clave)
    c = CRITERIOS[clave]
    if c.valor is None:
        # Detiene el calculo. NUNCA se devuelve un default silencioso: la GUI
        # muestra "falta declarar: <clave>" y el usuario resuelve el vacio.
        raise CriterioPendienteError(clave, concepto=c.concepto, fuente=c.fuente)
    return c.valor


def criterio(clave: str) -> Criterio:
    """Devuelve el objeto completo, sin registrar uso (para reportes)."""
    return CRITERIOS[clave]


def criterios_sin_valor() -> List[str]:
    """
    Claves cuyo valor es None: vacios que detienen el calculo si se invocan.
    M11 los imprime en bloque aparte (Sec. 0.7) y la GUI los usa para avisar
    antes de correr, no despues de la excepcion.
    """
    return sorted(k for k, c in CRITERIOS.items() if c.valor is None)


# ---------------------------------------------------------------------------
# CRITERIOS ADOPTADOS
# ---------------------------------------------------------------------------

CRITERIOS: Dict[str, Criterio] = {

    # ----------------------- SISMO: cadena unica -------------------------
    # Se define UNA vez y se propaga a toda verificacion de estabilidad.

    "PGA_roca_B": Criterio(
        valor=0.50,
        etiqueta="N",
        concepto="Aceleracion pico del terreno en roca Clase B, Tr = 1000 anios",
        justificacion="Lectura directa del mapa de isoaceleraciones sobre las "
                      "coordenadas del distrito de La Union, Piura",
        fuente="Manual de Puentes MTC, Apendice A3, mapa 'Isoaceleraciones "
               "Espectrales Suelo Tipo B, AASHTO 2014 (Roca). Periodo estructural "
               "0.0 seg (PGA)' - descartados los mapas de Ss y S1",
        verificacion_pendiente="Registrar en la memoria las coordenadas o la curva "
                               "de isoaceleracion sobre la que se hizo la lectura "
                               "(trazabilidad; las curvas varian dentro del dpto.)",
    ),

    "clase_sitio": Criterio(
        valor="F_con_excepcion_periodo_corto",
        etiqueta="C",
        concepto="Clase de sitio sismica AASHTO",
        justificacion="El sitio es Clase F por susceptibilidad a licuefaccion "
                      "(arenas saturadas, NF a 1.4 m). Se invoca la excepcion "
                      "para estructuras de periodo fundamental corto (<= 0.5 s), "
                      "que permite clasificar como si los suelos no licuaran, "
                      "quedando los efectos de licuefaccion excluidos del alcance "
                      "y remitidos al estudio geotecnico del expediente",
        fuente="AASHTO LRFD Art. 3.10.3.1 (el Manual de Puentes no tipifica "
               "excepciones para Clase F en su Tabla 2.4.3.11.2.1.2-1)",
        reemplazado_por="Ensayo SPT: perforaciones >= 15 m, ensayos cada 1 m "
                        "(E.050 Art. 38) -> N_barra o Vs30 -> clase definitiva",
        verificacion_pendiente="Precisar si en tu edicion de AASHTO la excepcion "
                               "esta en el ARTICULADO 3.10.3.1 o en el COMENTARIO "
                               "C3.10.3.1 / nota a la tabla, y citarla como tal",
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

    "factor_muro": Criterio(
        valor=1.0,
        etiqueta="N",
        concepto="Factor de reduccion del coeficiente sismico por desplazamiento",
        justificacion="El cabezal esta empotrado en el terraplen y no tiene "
                      "desplazamiento lateral admisible garantizado de 25-50 mm. "
                      "Se adopta el caso de muro rigido, sin reduccion",
        fuente="Manual de Puentes, numeral 2.8.1.1.14.2",
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
        justificacion="La Tabla N 02 (num. 3.6) entrega las dos filas con su R y "
                      "su n, pero NO entrega la regla para decidir cual le toca a "
                      "un cauce dado, y Sec. 2.3 se limita a decir que la Familia "
                      "A lleva 'TR 71 o 35 anios'. El vacio no es menor: entre una "
                      "fila y la otra el TR se duplica, y con el sube la intensidad "
                      "de la IDF y el Q de diseno de todos los puntos de paso. Se "
                      "elige el AREA DE CUENCA como descriptor porque es el unico "
                      "dato del CSV que Sec. 1.1 califica expresamente de 'solo "
                      "clasificador': no entra en ninguna formula y existe "
                      "justamente para esto. Lo que falta es el umbral. "
                      "ALTERNATIVA sin este criterio: clasificar cauce por cauce y "
                      "pasar la categoria explicita a M1, que la acepta como "
                      "argumento; entonces la eleccion se documenta punto por "
                      "punto en la memoria en vez de por regla",
        fuente="PENDIENTE - el Manual MTC no define 'quebrada importante' ni "
               "'quebrada menor' por umbral de area, longitud ni caudal",
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
        valor=None,                 # VACIO: la Tabla N 10 da un RANGO, no un valor
        etiqueta="A",
        concepto="Velocidad maxima admisible adoptada para el concreto, dentro "
                 "del rango 3.0-6.0 m/s de la Tabla N 10",
        justificacion="Regla de coherencia de la hoja de ruta: cuando una tabla "
                      "normativa aporta los valores pero la ELECCION entre ellos "
                      "es del proyectista, se desdobla - la tabla es [N] y la "
                      "eleccion es [A]. V3 necesita UN numero. La lectura "
                      "conservadora es el extremo inferior (3.0 m/s), pero "
                      "adoptarla en silencio seria rellenar el vacio sin "
                      "declararlo. Se deja sin valor a proposito: escribe aqui "
                      "el numero que vas a defender en la memoria",
        fuente="Manual MTC, Tabla N 10 (num. 4.1.1.3.6) - el rango es [N]; la "
               "eleccion dentro del rango no esta normada",
        sensibilidad=(3.0, 6.0),
    ),

    "ke_entrada": Criterio(
        valor=0.5,
        etiqueta="C",
        concepto="Coeficiente de perdida de carga en la embocadura (ke)",
        justificacion="La ecuacion de control de salida de la hoja de ruta, "
                      "H = (1 + ke + 19.62*n^2*L/R^(4/3))*V^2/(2g), contiene ke "
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
        fuente="HDS-5 (FHWA) 3a ed., abril 2012 / tablas de coeficiente de "
               "perdida de entrada para embocadura square edge with headwall",
        reemplazado_por="Fila de HDS-5 que corresponda si cambia el detalle de "
                        "embocadura del cabezal (Tablero 2.3)",
        verificacion_pendiente="El ke debe moverse junto con el detalle de "
                               "embocadura (Tablero 2.3) y con las constantes "
                               "HDS-5 de Sec. 4.2: cambiar el detalle obliga a "
                               "cambiar los tres",
    ),

    "geometria_control_salida": Criterio(
        valor="seccion_llena",
        etiqueta="C",
        concepto="Seccion de referencia de la que se toman V y R en la ecuacion "
                 "de control de salida H = (1 + ke + 19.62*n^2*L/R^(4/3))*V^2/(2g)",
        justificacion="Sec. 4.3 escribe la ecuacion pero NO dice a que seccion "
                      "pertenecen V y R, y la eleccion no es cosmetica: con la "
                      "seccion llena de un tubo de 0.90 m, R = D/4 = 0.225 m; con "
                      "el tirante normal de y/D = 0.75, R = 0.2715 m. La misma "
                      "formula da dos H distintas. Se adopta la SECCION LLENA "
                      "(A = pi*D^2/4, R = D/4, V = Q/A) porque es la seccion para "
                      "la que HDS-5 deriva esa expresion: los tres sumandos "
                      "(1 = carga de velocidad, ke = perdida de entrada, "
                      "19.62*n^2*L/R^(4/3) = perdida por friccion) son las "
                      "perdidas de un barril trabajando LLENO, que es el caso de "
                      "control de salida por definicion. Aplicarla sobre la "
                      "geometria del tirante normal mezcla dos regimenes. "
                      "TRAZABILIDAD: el caso patron CP-8 de "
                      "tests/fixtures/casos_patron.py alimenta la formula con "
                      "R = 0.27152 y V = 2.2807, que son los de la seccion "
                      "parcialmente llena de CP-2. CP-8 no contradice esto: es un "
                      "caso patron de la CONSTANTE 19.62 frente al 29 imperial, y "
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
        justificacion="El Manual MTC no define HW/D. Se adopta el rango corriente "
                      "de la practica FHWA. El control gobernante del embalse es "
                      "la verificacion V5 (remanso dentro del derecho de via)",
        fuente="HDS-5 (FHWA), practica corriente",
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
}


# ---------------------------------------------------------------------------
# Reporte para el modulo M11
# ---------------------------------------------------------------------------

_ORDEN = {"N": 0, "N->": 1, "C": 2, "A": 3}


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
        out.append(f"[{c.etiqueta}] {k} = {c.valor!r}")
        out.append(f"     Concepto      : {c.concepto}")
        out.append(f"     Justificacion : {c.justificacion}")
        out.append(f"     Fuente        : {c.fuente}")
        if c.reemplazado_por:
            out.append(f"     Se sustituye por: {c.reemplazado_por}")
        if c.sensibilidad:
            out.append(f"     Sensibilidad  : {c.sensibilidad}")
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
    # Demostracion: cadena sismica completa desde una sola fuente
    A_s = valor("PGA_roca_B") * valor("F_pga")
    k_h = valor("factor_muro") * A_s
    valor("clase_sitio")

    print(f"A_s = {A_s:.2f} g")
    print(f"k_h = {k_h:.2f}")
    print(f"k_v = {valor('k_v'):.2f}\n")
    print(reporte_criterios())
