"""
Fichas de criterios adoptados del dominio: metrados.
"""

from typing import Dict
from src.constantes_normativas import SOBREANCHO_MAX_ENCOFRADO_EG2013_M
from src.modelos import Libre
from src.criterios._base import (
    Criterio,
    FORMA_CATEGORIA,
    FORMA_FLOAT,
    NIVEL_EXPEDIENTE,
)


CRITERIOS: Dict[str, Criterio] = {

    # =======================================================================
    # --- VE-5 (lote «met», item 8 del censo) --- Fase 11, entregable 8: los
    # metrados referidos al EG-2013. Los consume `M12_metrados` a nivel de
    # EXPEDIENTE (el metrado lee el cabezal, que la corrida de perfil
    # difiere). Ningun factor de desperdicio ni de esponjamiento: el EG-2013
    # los pone en el precio, no en la cantidad (503.12, 503.13, 501.09).
    # =======================================================================
    "sobreancho_excavacion_estructuras_m": Criterio(
        # OPCIONAL: la norma fija el defecto (cero) y el permiso (hasta
        # 45 cm), y el proyecto solo decide si hace falta encofrar.
        valor=None,
        opcional=True,
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        no_negativo=True,
        concepto="Sobreancho de la excavacion de las zapatas de los "
                 "cabezales y aleros (y de la zanja de un marco) fuera de "
                 "sus caras, en m, cuando el cimiento se vacia con encofrado",
        justificacion="Decide, solo si se declara, el volumen de excavacion "
                      "de los cimientos: cada zapata se excava con el "
                      "sobreancho a cada lado. Sin declararlo rige la regla "
                      "general del EG-2013 501.04, caras verticales conforme "
                      "a las dimensiones de la estructura (cita "
                      "EG2013.501.04#CARAS): sobreancho cero. Si el cimiento "
                      "necesita encofrado, la misma subseccion permite "
                      "extender la excavacion hasta 45 cm fuera de las caras "
                      "verticales del pie de la zapata (cita "
                      "EG2013.501.04#ENCOFRADO), que es el techo de la "
                      "ventana. No se aplica a la zanja de un tubo, cuyo "
                      "ancho total fija su Seccion (506.06, 507.05, 508.04)",
        fuente="EG-2013 501.04, pag. impresa 886 (PDF 894): «caras "
               "verticales conforme a las dimensiones de la estructura» "
               "(defecto, cero) y «se podrá extender hasta 45 cm» con "
               "encofrado (citas EG2013.501.04#CARAS y "
               "EG2013.501.04#ENCOFRADO)",
        sensibilidad=(0.0, SOBREANCHO_MAX_ENCOFRADO_EG2013_M),
        reemplazado_por="Las lineas de excavacion de los planos del "
                        "expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, si el cimiento se vacia con "
                        "encofrado; sin declararlo, cero",
            dominio="m, 0 a 0.45",
        ),
    ),

    "incremento_acero_por_despiece": Criterio(
        valor=None,                 # VACIO: lo fija el despiece de los planos
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_FLOAT,
        no_negativo=True,
        concepto="Fraccion que se suma al peso de las barras del cabezal "
                 "medidas dentro de cada elemento por los anclajes, ganchos, "
                 "dobleces y empalmes que el despiece de los planos indique "
                 "(0.10 = 10 %)",
        justificacion="Decide el metrado del acero de refuerzo de los "
                      "cabezales (partida 504.A). El EG-2013 mide el acero "
                      "por el peso de las barras con sus tamaños y longitudes "
                      "reales (504.10, cita "
                      "EG2013.504.10), y esas longitudes son las del "
                      "despiece de los planos (504.03), con los empalmes "
                      "que el Proyecto indique y sin los adicionales. El "
                      "programa entrega la barra y el espaciamiento de cada "
                      "cara, no el despiece: el peso de las barras dentro de "
                      "cada elemento es exacto, y lo que agregan los "
                      "anclajes y empalmes depende del detalle que ningun "
                      "numeral del repositorio fija. No es un desperdicio "
                      "--que el EG-2013 pone en el precio, 504.11--: es "
                      "acero colocado. Sin declararlo, el renglon del acero "
                      "se detiene",
        fuente="PENDIENTE - EG-2013 504.10 (pag. impresa 946) mide las "
               "longitudes del despiece; ninguna fuente del repositorio fija "
               "cuanto agregan los anclajes y empalmes de un cabezal",
        reemplazado_por="El peso del despiece de los planos de los cabezales",
        resolucion=Libre(
            que_lo_fija="el proyectista, con el despiece de los planos o una "
                        "estimacion declarada de anclajes y empalmes",
            dominio="fraccion >= 0",
        ),
    ),

    "clase_concreto_losa_entrega": Criterio(
        valor=None,                 # VACIO: la losa no tiene diseño estructural
        nivel=NIVEL_EXPEDIENTE,
        etiqueta="A",
        forma=FORMA_CATEGORIA,
        sensibilidad=("C", "D", "E", "F", "G"),
        concepto="Clase de concreto de la Tabla 503-07 del EG-2013 de la "
                 "losa de entrega (zampeado) y su dentellon",
        justificacion="Decide la partida 503.A de la losa de entrega y del "
                      "dentellon de cada cabezal. Su geometria la propone la "
                      "Fase 9 (T-7a), pero ninguna fase la diseña "
                      "estructuralmente ni le fija un material: la Lamina "
                      "Nº 04 del Manual la dibuja sin especificarlo y la "
                      "ficha T8-03 lo deja abierto. La ventana son las "
                      "clases de concreto reforzado, simple y ciclopeo de la "
                      "tabla (cita EG2013.503.04#T503_07); el pre y "
                      "postensado (A y B) no aplica a un zampeado. Sin "
                      "declararla, el renglon de la losa se detiene",
        fuente="PENDIENTE - EG-2013 503.04, Tabla 503-07, pag. impresa 912 "
               "(PDF 920): las clases; cual es la de la losa es del "
               "proyecto",
        reemplazado_por="La especificacion de la losa de entrega en los "
                        "planos del expediente",
        resolucion=Libre(
            que_lo_fija="el proyectista, con la especificacion del zampeado",
            dominio="una de las clases de la ventana",
        ),
    ),
}
