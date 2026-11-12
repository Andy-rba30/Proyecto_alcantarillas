"""
M7_geometria.py
================
Fase 7 de la hoja de ruta: compatibilidad geometrica. Dos piezas que la hoja
separa a proposito, y que este modulo mantiene separadas:

    7.A  Tamizado previo    fija la cota de rasante UNA sola vez, como el
                            MAXIMO de las dos condiciones, antes del perfil
                            longitudinal.
    7.B  Verificacion final por punto  longitud, esviaje, pendiente y cotas
                            de entrada y salida, con la rasante ya congelada.

7.A -- el tamizado
------------------
    cota rasante >= max( cota clave + h_rec + e_paq ,
                         cota entrada + HW + resguardo(CBR) + e_paq )

    cota clave  = cota de fondo de la entrada + D + espesor de pared. Es la
                  clave FISICA, la superficie exterior del tubo, que es desde
                  donde EG-2013 508.07 mide el relleno (MAT-D4). La calcula
                  `M5_verificaciones.cota_clave`, no este modulo
    h_rec       = relleno minimo sobre la clave, calculado como el MAYOR de
                  dos minimos (`altura_recubrimiento`): el de EG-2013, que
                  solo existe para HDPE (0.30 m, Subseccion 508.07, pag. 984,
                  [N]), y la cobertura minima de la Tabla 12.6.6.3-1 de AASHTO
                  LRFD ([C], 'cobertura_minima_aashto'), que depende del
                  diametro EXTERIOR y de la condicion de pavimento. Ya NO es
                  un escalar de 0.30 m para los tres materiales: ese numero
                  quedaba 5 mm bajo el piso de 12 in de la tabla y hasta un
                  20 % bajo el Bc/8 que gobierna en diametros grandes
                  (NOR-VAC-01)
    e_paq       = cota de rasante - cota de subrasante     (Sec. 1.1)
    HW          = carga a la entrada, en metros sobre el fondo de la entrada
                  (Sec. 4.2 / 4.3), convertida a cota aqui
    resguardo   = tabla de Sec. 5.1 segun el CBR de subrasante, aplicada al
                  HW POR ANALOGIA ('resguardo_HW_subrasante', [N->])

Sec. 7.A manda correr el tamizado "con el diametro maximo supuesto **antes**
de definir el perfil longitudinal", y por eso la `seccion` es un argumento
explicito y no un valor que este modulo elija.

    ADVERTENCIA que hay que declarar en la memoria: el diametro maximo NO es
    conservador para las dos condiciones a la vez. Un D mayor sube la clave
    (empeora la primera) pero baja el HW (mejora la segunda). Correr 7.A con
    D_max deja la condicion de RESGUARDO evaluada con el HW mas favorable, de
    modo que el punto que la Fase 4 acabe resolviendo con un diametro menor
    tendra un HW mayor que el del tamizado. Esa es exactamente la razon de que
    7.B exista y se corra por punto con el D ADOPTADO: el tamizado fija la
    rasante, la verificacion final comprueba que el diametro realmente
    adoptado sigue cabiendo debajo. Cuando no cabe, 7.B no calla: devuelve
    "no factible -> subir rasante X cm".

7.B -- la verificacion final
----------------------------
    longitud   = (ancho de plataforma + proyeccion de taludes) / cos(esviaje)
    pendiente  = la MISMA con que corrio el diseño hidraulico,
                 `ResultadoHidraulico.S`; V2 nunca la restringe (Sec. 5.2)
    cota salida = cota de entrada - S * longitud

DESDE T-6 (cadena T, 2026-11-11) LA «PROYECCION DE TALUDES» TIENE METODO
DECLARADO, y la primera linea de arriba dejo de bastar. El criterio [A]
'metodo_longitud_conducto' elige entre dos:

    por_extremo          cada talud baja desde el borde de la plataforma
                         hasta el FONDO del conducto en SU extremo, y la
                         salida queda S*L mas baja que la entrada (HDS-5
                         3a ed., num. 2.2.4 b. y Figura 2.4, pag. impresa
                         2.8):
                             L = [ancho + talud * (H_entrada + H_salida0)]
                                 / [cos(esviaje) - talud * S]
                         Es el valor del archivo.
    terraplen_simetrico  los dos taludes bajan la altura del eje, rasante -
                         terreno: la formula anterior, conservada como caso
                         particular (INF-3.3.3 la señalo).

La longitud se resuelve UNA vez, antes de la Fase 4 (`longitud_del_conducto`),
y 7.B recibe ese mismo objeto. Y 7.B dejo de ser un parrafo en la memoria:
emite los pasos 7.B.1 (pendiente adoptada, con su origen), 7.B.2 (factor de
esviaje), 7.B.3 (longitud), 7.B.4 (caida y cota de salida) y 7.B.5 (encaje de
la seccion adoptada: longitud entre cabezales a la clave, HDS-5 num. 3.3.5).

LA PENDIENTE NO SE ELIGE DOS VECES (MAT-D9). Sec. 7.B dice que la pendiente de
la alcantarilla es la del cauce, y esa sigue siendo la regla del proyecto: el
valor por defecto lo pone la Fase 4, que resuelve `punto.exigir("S_cauce")`
cuando nadie declara otra cosa. Lo que este modulo YA NO hace es volver a
resolverla por su cuenta. Lo hacia -- `S = punto.exigir("S_cauce")` si el
llamador no pasaba nada -- y el llamador de produccion (`servicio._fase_7`) no
pasaba nada, de modo que el punto que declaraba su pendiente aparte
('S_conducto' de la CLI, la via de Sec. 2.3 para la Familia B y la C) quedaba
con DOS pendientes: el HW y las velocidades calculados con la declarada, y la
caida y la cota de salida con la del cauce. Ninguna de las dos era visible en
el informe como distinta de la otra. Ahora la pendiente viaja dentro del
resultado hidraulico, que es la salida de quien la resolvio, y 7.B la lee de
ahi: si el proyecto quiere cambiarla, se cambia en la Fase 4 y las dos cosas
se mueven juntas.

DESDE T-6 QUIEN LA RESUELVE ES `pendiente_adoptada`, una vez y ANTES de la
Fase 4, con su ORIGEN: la declarada (`S_conducto`), el extremo de la banda
adoptada cuando la pendiente del cauce lo traspasa (los dos criterios de T-2,
leidos con `M5.limites_de_pendiente()`), o la del cauce. `servicio` pasa ese
mismo valor a la longitud, al TW por cota, a MD y a 7.B. El reparto con V10
-- este modulo ACOTA la pendiente del cauce y lo avisa; V10 JUZGA la que
quedo y solo puede incumplirse con una declarada -- y lo que cada extremo
trae consigo (una caida o un disipador que el programa no dimensiona; una
salida bajo el cauce natural) estan en el docstring de esa funcion y en
`aviso_de_pendiente`.

El 1/cos(esviaje) no es un coeficiente adoptado: es la identidad geometrica
del cruce oblicuo -- el eje del conducto es la hipotenusa del ancho que
atraviesa -- del mismo orden que el T = D*sen(theta/2) de `modelos.SeccionCircular.ancho_superficial_en_llenado`.
A 0 grados vale 1 y el conducto es perpendicular a la via.

La proyeccion de taludes SI es un vacio: Sec. 7.B pide sumarla pero no da la
inclinacion del talud y Sec. 1.2 no la trae como columna. Se detiene en el
criterio 'talud_terraplen' [A], vacio a proposito (ver su justificacion en
criterios_adoptados.py). Mientras ese criterio siga vacio,
`longitud_conducto()` y `compatibilidad_geometrica()` se detienen con
CriterioPendienteError para CUALQUIER punto.

7.A YA NO CORRE SOLO, que es lo que este parrafo decia antes. El tamizado
necesita hoy otros dos criterios, y los dos estan vacios a proposito:

    'espesor_pared_conducto'  donde esta la clave fisica, y el Bc que entra en
                              la cobertura minima del concreto (MAT-D3/D4)
    'condicion_pavimento'     que fila de la Tabla 12.6.6.3-1 aplica a esta
                              via (NOR-VAC-01)

Que 7.A funcionase "hoy mismo" era el sintoma, no la virtud: funcionaba
porque medía la clave desde el punto equivocado y comparaba contra un numero
que ninguna tabla sostiene. Un tamizado que se detiene diciendo que le falta
el espesor de pared es mas util que uno que devuelve una rasante 33 % corta.

EL ACOPLAMIENTO CIRCULAR (Sec. 7.B lo declara; aqui se corta)
--------------------------------------------------------------
La hoja de ruta escribe el lazo asi:

    rasante -> paquete estructural -> subrasante -> CBR -> resguardo -> V4
            -> rasante

y hay que leerlo eslabon por eslabon para ver por que es un lazo de verdad y
no una cadena:

  1. rasante -> paquete. La cota de rasante es la superficie de rodadura. Bajo
     ella va el paquete estructural (Sec. 1.5), cuyo espesor e_paq es un dato
     de la seccion tipica.
  2. paquete -> subrasante. La subrasante es lo que queda al restar el
     paquete: cota subrasante = cota rasante - e_paq (Sec. 1.1). Mover la
     rasante mueve la subrasante.
  3. subrasante -> CBR. El CBR de diseño es el del suelo QUE QUEDA a nivel de
     subrasante; es el dato de calicata que define la calidad de ese apoyo.
  4. CBR -> resguardo. La tabla de Sec. 5.1 (Manual de Suelos, num. 4.5.4)
     entrega 0.60 / 0.80 / 1.00 / 1.20 m segun el tramo de CBR.
  5. resguardo -> V4. La verificacion V4 exige
     cota de entrada + HW <= cota de subrasante - resguardo(CBR). Los DOS
     terminos son niveles: HW es una carga sobre el fondo de la entrada y no
     se puede comparar con una cota sin sumarle esa cota (MAT-O5).
  6. V4 -> rasante. Cuando V4 no cumple, Sec. 5.1 lista las salidas:
     subdrenes, capas drenantes o **elevar la rasante** -- "lo que alimenta
     7.A". Y elevar la rasante vuelve al eslabon 1.

Iterar ese lazo dentro del bucle de diseño seria un solver implicito: cada
subida de rasante cambiaria la subrasante, y con ella -- en el caso general --
el suelo que queda arriba, su CBR, su resguardo y otra vez la condicion de V4.
Sec. 7.A lo corta de raiz: se fija la rasante UNA vez y se congela.

Que hace falta para que cortarlo sea legitimo y no una simplificacion tapada:

  - e_paq es INVARIANTE frente a la rasante. Es el espesor del paquete, un
    dato de la seccion transversal del proyecto, no una elevacion: subir la
    rasante sube la subrasante exactamente lo mismo. El eslabon 1->2 es una
    relacion afin de pendiente 1, no una realimentacion.
  - el CBR es un DATO MEDIDO del punto (columna del CSV, Sec. 1.2), no una
    funcion de la cota. A nivel de perfil -- que es el nivel de este estudio,
    Sec. 1.4 -- el cuerpo del terraplen se construye con material de cantera
    controlado, de modo que subir la rasante no cambia el CBR de diseño de la
    subrasante. Los eslabones 3 y 4 quedan constantes.
  - por lo tanto el resguardo es constante frente a la rasante, y la condicion
    de V4 se puede escribir como una cota inferior CERRADA sobre la rasante:

        cota entrada + HW <= (cota rasante - e_paq) - resguardo
        cota rasante >= cota entrada + HW + resguardo + e_paq

    que es, literalmente, la segunda linea del maximo de 7.A. El lazo se
    resuelve de una sola pasada, sin iterar.

Lo que el corte NO cubre, y hay que decirlo en la memoria: el eslabon 3
supone que el suelo a nivel de subrasante sigue siendo el mismo al subir la
rasante. Si el expediente detecta que un punto cambia de material de
subrasante con la elevacion, el CBR deja de ser constante, el lazo vuelve a
cerrarse y la rasante de ese punto se fija con el CBR del nivel FINAL, no con
el de la calicata original.

Coherencia con V4 (M5)
----------------------
La segunda condicion de 7.A y la verificacion V4 son la MISMA desigualdad
escrita al reves: V4 pregunta si el HW cabe bajo la subrasante que hay, y 7.A
pregunta que rasante hace falta para que quepa. Por eso este modulo no
reimplementa ninguna de las dos piezas que comparten:

    modulos.M5_verificaciones.cota_de_entrada         la cota a la que se
                                                      refiere el HW (la fija
                                                      el criterio declarado
                                                      'origen_cota_fondo_entrada')
    modulos.M5_verificaciones.cota_clave              la clave fisica, con el
                                                      espesor de pared
    modulos.M5_verificaciones.resguardo_por_cbr       la tabla de Sec. 5.1

`cota_clave` entro en esta lista al corregirse MAT-D4: estaba definida a la
vez aqui y dentro de `v7_flotacion`, y las dos copias calculaban
cota_entrada + D. Dos copias del mismo defecto es exactamente lo que esta
seccion existe para evitar.

Si M7 eligiera su propia cota de entrada o copiara la tabla, la rasante se
fijaria contra una condicion y V4 se verificaria contra otra, y el
acoplamiento seguiria abierto por la puerta de atras.

Por que 7.B trae dos verificaciones con umbral y un aviso
----------------------------------------------------------
De los cinco puntos que Sec. 7.B enumera, tres son CALCULOS y no chequeos
(longitud, esviaje y pendiente: la hoja fija como se obtienen, no un umbral
que puedan incumplir) y viajan como campos y como pasos de
`CompatibilidadGeometrica`. Los dos que si tienen umbral son:

    G1  rasante congelada        cota de rasante >= la minima de 7.A
    G2  entrega al receptor      cota de salida >= cota de fondo del receptor
                                 + 'desnivel_minimo_entrega_m'

y desde T-6 hay una tercera fila que NO es un umbral de aceptacion:

    G3  esviaje (AVISO)          esviaje <= 'esviaje_max_grados'; `cumple`
                                 es True siempre, y por encima del maximo el
                                 paso lleva veredicto INDICADOR

G2 ES UNA INTERPRETACION CON CRITERIO DECLARADO. Sec. 7.B pide las cotas de
entrada y salida "amarradas al perfil del cauce y a la cota de fondo del
receptor", y la lectura minima de ese amarre es que la salida no quede
enterrada bajo el fondo del cuerpo receptor. Hasta T-6 este parrafo decia que
G2 «no lleva ningun parametro adoptado» y que un desnivel minimo de entrega
«no se exige aqui» porque la hoja de ruta no lo da. La hoja de ruta lo declara
criterio desde T-0 y T-6 lo creo: 'desnivel_minimo_entrega_m' [A], con valor
0.0 m -- que es exactamente la comparacion anterior -- y ventana hasta 0.30
m. Ninguna fuente da el numero (el num. 4.1.1.3.3 del Manual exige cuidar la
pendiente y no habla de la entrega), y por eso es [A].

Excepciones
-----------
    CriterioPendienteError   'origen_cota_fondo_entrada' (bloquea toda
                             conversion de HW a cota, o sea 7.A entero y las
                             cotas de 7.B, para cualquier material);
                             'espesor_pared_conducto' (bloquea la clave fisica
                             y con ella 7.A entero, para los tres materiales);
                             'condicion_pavimento' (bloquea el recubrimiento
                             minimo, tambien para los tres);
                             'talud_terraplen' (bloquea la longitud de 7.B).
                             Desde T-6 tambien 'metodo_longitud_conducto',
                             'desnivel_minimo_entrega_m' y
                             'esviaje_max_grados', los tres con valor de
                             archivo.
    DisenoNoFactibleError    lo lanzan `TamizadoRasante.exigir_factible()` y
                             `CompatibilidadGeometrica.exigir_factible()`, con
                             `delta_rasante_m` cargado. NUNCA una excepcion
                             generica: el "no factible" de Sec. 7.B viaja con
                             su numero, y por defecto ni siquiera viaja como
                             excepcion -- `tamizado_rasante()` DEVUELVE el
                             delta en `delta_rasante_cm` y quien quiera la
                             excepcion la pide.
    DatoInvalidoError        el paquete estructural no es positivo (la
                             subrasante no queda bajo la rasante, Sec. 1.5),
                             el esviaje no admite cruce, o -- en la longitud
                             por extremo -- la pendiente alcanza a la del
                             talud vista sobre el eje del conducto, o un
                             borde de la plataforma queda bajo el fondo.
    DatoFaltanteError        'S_cauce', cuando la longitud por extremo
                             necesita la pendiente y el punto no trae ni la
                             del cauce ni una declarada.

Uso
---
    from src.modulos.M7_geometria import tamizado_rasante, compatibilidad_geometrica

    # 7.A, antes del perfil longitudinal, con el diametro maximo supuesto
    tamizado = tamizado_rasante(punto=punto, material=hdpe,
                                seccion=SeccionCircular(D=hdpe.D_max),
                                HW=0.95)   # D_max: tope de CATALOGO
    tamizado.cota_rasante_min          # msnm - la rasante que hay que fijar
    tamizado.delta_rasante_cm          # cm  - cuanto falta subir; 0.0 si cabe
    print(tamizado.mensaje)            # "no factible -> subir rasante 18.0 cm"

    # 7.B, por punto, con la seccion que la Fase 4 adopto. La pendiente NO
    # es argumento: sale de `resultado.S`, la que uso el diseño (MAT-D9)
    geometria = compatibilidad_geometrica(punto=punto, material=material,
                                          seccion=resultado_punto.seccion,
                                          resultado=resultado_punto.resultado_hidraulico)
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from src import criterios_adoptados as ca
from src.dominios import ESVIAJE_MAX, S_CAUCE_MAX
from src.modelos import (CIFRAS_FINA, CIFRAS_MAGNITUD,
                     CompatibilidadGeometrica,
                     CondicionRasante,
                     DatoInvalidoError, EleccionDeProyecto, FormaSeccion,
                     LimiteNumericoError, LongitudConducto,
                     Magnitud, Material, MetodoLongitud, OrigenPendiente,
                     PendienteAdoptada, Seccion,
                     exigir_seccion_coherente,
                     PuntoCritico, ResultadoHidraulico, TamizadoRasante,
                     TipoDeVeredicto, Umbral, Veredicto, Verificacion, paso)
from src.modulos.M2_material import espesor_pared
from src.modulos.M5_verificaciones import (CRITERIO_PENDIENTE_MAXIMA,
                                       CRITERIO_PENDIENTE_MINIMA,
                                       CRITERIO_REGIMEN_V2B,
                                       CRITERIO_RESGUARDO, cota_clave,
                                       cota_de_entrada,
                                       limites_de_pendiente,
                                       resguardo_por_cbr)
from src.tolerancias import COS_ESVIAJE_MIN, TOL_UMBRAL_NORMATIVO
from src.normativa import registro as _registro

NUMERAL_7A = "Sec. 7.A"
NUMERAL_7B = "Sec. 7.B"
# El recubrimiento NO sale solo de EG-2013, y decir que si es la atribucion
# falsa que NOR-VAC-01 denuncia: el EG-2013 fija la altura minima de relleno
# unicamente para HDPE. Este string es lo que M11 imprime en la columna
# "numeral" de la fila G1, o sea lo unico que el revisor ve de esa
# verificacion, y con la version anterior una fila de CONCRETO decia
# "recubrimiento EG-2013" al lado de criterio_aplicado = cobertura_minima_aashto.
# EL NUMERAL DE G1 NO PUEDE SER UNA CONSTANTE, y serlo fue el hallazgo 1 de la
# auditoria adversarial de C7. Es lo UNICO que M11 imprime en la columna
# «numeral» de la fila G1 -- o sea lo unico que el revisor ve de esa
# verificacion --, y la constante nombraba la Tabla 12.6.6.3-1 de AASHTO para
# TODOS los materiales. Para un marco esa tabla no tiene fila: C7 abrio
# 'cobertura_minima_cajon' justamente por eso, arreglo el `criterio_aplicado`
# y DEJO ESTE CANAL DICIENDO LO CONTRARIO. Un vacio declarado con una cita
# falsa al lado es peor que el vacio solo.
NUMERAL_G1_CIRCULAR = ("Sec. 7.A (recubrimiento: el mayor entre EG-2013 "
                       "508.07 -- solo HDPE -- y AASHTO LRFD Art. 12.6.6.3, "
                       "Tabla 12.6.6.3-1 / resguardo Sec. 5.1)")
NUMERAL_G1_CAJON = ("Sec. 7.A (cobertura: SIN numeral -- la Tabla 12.6.6.3-1 "
                    "de AASHTO no tiene fila de cajon de concreto y el "
                    "EG-2013 solo fija altura de relleno para HDPE --, "
                    "declarada en el criterio 'cobertura_minima_cajon' [A] / "
                    "resguardo Sec. 5.1)")


def numeral_g1(material: Material) -> str:
    """
    El numeral que la fila G1 imprime, que NO es el mismo en un marco.

    Ver el comentario de arriba: la constante unica atribuia a todo material
    la Tabla 12.6.6.3-1, y un marco no tiene fila en ella.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return NUMERAL_G1_CAJON
    return NUMERAL_G1_CIRCULAR
NUMERAL_G2 = ("Sec. 7.B (cotas amarradas al fondo del receptor; desnivel "
              "de entrega: criterio 'desnivel_minimo_entrega_m' [A])")

# LOS DOS MINIMOS QUE COMPITEN EN h_rec, con nombre, porque G1 tiene que
# decir CUAL gano y no solo enunciar la regla. Hasta C7 el paso escribia «el
# MAYOR entre el minimo de la EG-2013 y la cobertura minima de AASHTO» y se
# quedaba ahi: el revisor leia la regla y no el resultado de aplicarla, que es
# el dato que necesita para saber que mover si el punto no cabe.
MINIMO_EG2013 = "EG-2013 508.07"
MINIMO_AASHTO = "AASHTO LRFD Tabla 12.6.6.3-1"
# Y LA TERCERA, que la auditoria adversarial de C7 encontro ausente: en un
# marco no gobierna ninguna de las dos anteriores porque ninguna lo alcanza.
# Sin esta etiqueta, `altura_recubrimiento` devolvia para el marco la frase
# «AQUI GOBIERNA AASHTO LRFD Tabla 12.6.6.3-1», que es la cita falsa que
# 'cobertura_minima_cajon' existe para no tener que hacer -- y la introdujo el
# propio C7i al anadir el par.
MINIMO_CAJON_DECLARADO = "el criterio 'cobertura_minima_cajon' [A]"

CRITERIO_TALUD = "talud_terraplen"
CRITERIO_COBERTURA_AASHTO = "cobertura_minima_aashto"
CRITERIO_COBERTURA_CAJON = "cobertura_minima_cajon"
CRITERIO_CONDICION_PAVIMENTO = "condicion_pavimento"

# --- T-6 --- Las claves que 7.B lee desde T-6.
CRITERIO_METODO_LONGITUD = "metodo_longitud_conducto"
CRITERIO_DESNIVEL_ENTREGA = "desnivel_minimo_entrega_m"
CRITERIO_ESVIAJE_MAX = "esviaje_max_grados"
# LA BANDA DE PENDIENTE ES DE T-2 Y AQUI NO SE VUELVE A LEER. Los criterios
# 'pendiente_minima_conducto' y 'pendiente_maxima_conducto' los creo T-2 con
# su lectura unica, `M5.limites_de_pendiente()` -- que trae la guardia cruzada
# de la banda vacia --, y con la verificacion que los aplica (V10). Este
# modulo importa de M5 las dos claves y la funcion: `pendiente_adoptada` dice
# cual de los origenes gobierna y no tiene una segunda lectura de la banda.
# Hasta integrar T-6 despues de T-2 esto era una lectura por clave que podia
# no encontrarla (FASE A en paralelo); ya no hace falta.

NUMERAL_G3 = ("Sec. 7.B (esviaje del cruce frente al maximo adoptado: HDS-5 "
              "num. 5.4.2, por analogia; AVISO, el esviaje es dato de "
              "entrada)")
METODOS_DE_LONGITUD = (MetodoLongitud.TERRAPLEN_SIMETRICO.value,
                       MetodoLongitud.POR_EXTREMO.value)

# Claves de la fila de 'cobertura_minima_aashto'. Los nombres reproducen la
# nomenclatura del propio Art. 12.6.6.3 (S, Bc, ID) y no se reescriben aqui:
# el criterio es la transcripcion y este modulo solo la lee.
_DIAMETRO_DE_LA_FILA = {
    "exterior": "D_ext",     # Bc, "outside diameter or width of the structure"
    "interior": "D_int",     # ID, "inside diameter"
    "nominal": "D_int",      # S, "diameter of pipe" -- el nominal del catalogo,
                             # que en este proyecto es el interior (Sec. 3.2)
}


# ---------------------------------------------------------------------------
# Piezas de 7.A
# ---------------------------------------------------------------------------

def espesor_paquete(punto: PuntoCritico) -> float:
    """
    e_paq = cota de rasante - cota de subrasante, m (Sec. 1.1).

    Es el termino que aparece en las DOS condiciones de 7.A, y el que hace
    que el acoplamiento circular se pueda cortar de una sola pasada: no es una
    elevacion sino un espesor de la seccion tipica, invariante frente a la
    rasante (ver el docstring del modulo).

    M0 ya rechaza la fila cuya subrasante no queda bajo la rasante (Sec. 1.5).
    Se vuelve a exigir aqui porque M7 tambien se llama con puntos armados a
    mano, y un e_paq nulo o negativo no da un tamizado conservador: da uno sin
    sentido fisico.
    """
    e_paq = punto.cota_rasante - punto.cota_subrasante
    if e_paq <= TOL_UMBRAL_NORMATIVO:
        raise DatoInvalidoError(
            "cota_subrasante", valor=punto.cota_subrasante, id_punto=punto.id,
            motivo=f"el espesor del paquete estructural sale {e_paq:+.3f} m: "
                   f"la subrasante tiene que quedar bajo la rasante "
                   f"({punto.cota_rasante}) y su separacion es el paquete "
                   "(Sec. 1.5), termino de las dos condiciones de 7.A",
        )
    return e_paq


# `cota_clave` NO se define aqui: se importa de M5_verificaciones, junto a
# `cota_de_entrada` y `resguardo_por_cbr`, por la razon que el docstring
# del modulo ya da para esas dos -- V7 y 7.A tienen que medir la clave desde
# la misma referencia o el acoplamiento sigue abierto por la puerta de atras.
# Estaba definida en los dos sitios, y las dos copias arrastraban el mismo
# defecto: la calculaban como cota_entrada + D, sin espesor de pared (MAT-D4).


def _cobertura_declarada_del_cajon() -> float:
    """
    La cobertura minima del marco, m: la que el proyectista DECLARO, porque no
    hay tabla de la que leerla.

    Se detiene con `CriterioPendienteError` mientras 'cobertura_minima_cajon'
    siga vacio -- que es lo correcto: el revisor tiene que DECIDIR, no
    conseguir un dato --. Su ficha lleva las tres lecturas candidatas con su
    consecuencia, y la `AfirmacionNegativa` SIN_CAJON_DE_CONCRETO_T12663 fija
    el barrido que sostiene el vacio.

    LA GUARDA ES DE LIMITE Y NO DE DOMINIO, en la forma de MAT-D13: umbral
    MEDIDO -- una cobertura negativa no es "un dato raro", es una cota de
    clave por encima de la subrasante --, condicion escrita en positivo y
    negada, y mensaje que nombra la clave culpable. Cero SI es admisible: es
    la unica rama que AASHTO cubre expresamente para un cajon, y la ficha del
    criterio dice con que exigencia estructural viene.
    """
    h = ca.valor(CRITERIO_COBERTURA_CAJON)      # CriterioPendienteError si falta
    if not h >= 0.0:
        raise DatoInvalidoError(
            CRITERIO_COBERTURA_CAJON, valor=h,
            motivo="la cobertura minima de un marco no puede ser negativa: "
                   "seria una clave por encima de la subrasante. El cero SI "
                   "es declarable -- AASHTO lo cubre expresamente, a cambio "
                   "de disenar la losa superior para carga vehicular directa "
                   "--, y por eso el limite es el cero y no un piso positivo",
        )
    return float(h)


def cobertura_minima_aashto(*, material: Material, seccion: Seccion) -> float:
    """
    Cobertura minima sobre la clave, m, segun la Tabla 12.6.6.3-1 de AASHTO
    LRFD 9a ed. (Art. 12.6.6.3 "Minimum Cover", pag. 12-22), para el material
    y el diametro dados.

        cobertura = max( D_de_la_fila / divisor , piso de la fila )

    Las tres filas son homogeneas -- los divisores son adimensionales -- de
    modo que no hay ninguna conversion de unidades que hacer. El "or B'c/8,
    whichever is greater" de la fila del concreto tampoco aparece aqui: B'c es
    la "out-to-out vertical rise of pipe" del propio articulo, que en un
    conducto CIRCULAR es el diametro exterior, o sea Bc. El maximo de dos
    terminos iguales es uno solo.

    Y ESTA FUNCION NO ATIENDE AL CAJON, que es distinto de "todavia no lo
    atiende". Este parrafo remitia a "la nota del criterio: para una seccion
    no circular la reduccion deja de valer", dando por hecho que el marco
    entraba por aqui con el segundo termino. C7 lo verifico contra AASHTO y no
    es asi: las dos filas de concreto de la Tabla 12.6.6.3-1 dicen
    "Reinforced Concrete PIPE" y no hay fila de cajon de concreto. La
    cobertura minima del marco sale de `cobertura_minima_cajon`, que es un
    vacio declarado, no de esta tabla.

    LA BIFURCACION ES POR FORMA Y NO POR MATERIAL, por lo mismo que en
    `M8._elemento_de`: un marco de concreto y un tubo de concreto comparten
    `TipoMaterial`, de modo que indexar la tabla por material no los separa.
    Hasta C7 no se separaban, y el marco recibia la fila del tubo -- y encima
    con la dimension equivocada dentro, porque `D` en un marco vale la ALTURA
    y el "diametro exterior" la convertia en H + 2t, que es B'c y no Bc
    (esa funcion la retiro C8 por esto mismo). Medido:
    para un marco de 3.00 x 1.50 m con t = 0.15 salia 0.3048 m, el piso de la
    fila del tubo, SIN QUE EL ANCHO ENTRARA EN EL CALCULO -- B no es argumento
    de esta funcion --. Ese es el motivo de que la respuesta no sea traer un
    termino mas sino detenerse: no hay fila que aplicar.

    QUE DIAMETRO ENTRA lo dice la nomenclatura del articulo, y no es el mismo
    en las tres filas: Bc ("outside diameter or width of the structure") en el
    concreto reforzado, S ("diameter of pipe") en el metal corrugado e ID
    ("inside diameter") en el termoplastico. La distincion importa: en un tubo
    de concreto de D = 2.40 m con t = 0.15 m, Bc/8 da 0.34 m y (D_int)/8 daria
    0.30 -- justo el numero equivocado que este proyecto tenia.

    QUE FILA APLICA lo decide 'condicion_pavimento' [A], hoy SIN VALOR: la
    llamada se detiene con `CriterioPendienteError` hasta que se declare. No
    se adopta el extremo mas exigente "por si acaso" porque no hay uno solo --
    en concreto la fila de pavimento rigido pide MENOS que las otras dos -- y
    porque adoptarlo moveria la rasante de todos los puntos sin declararlo.

    Se detiene tambien en 'espesor_pared_conducto' cuando la fila usa Bc, y en
    'cobertura_minima_cajon' cuando la seccion es rectangular.
    """
    exigir_seccion_coherente(material, seccion)
    if material.forma is FormaSeccion.RECTANGULAR:
        return _cobertura_declarada_del_cajon()
    tabla = ca.valor(CRITERIO_COBERTURA_AASHTO)
    condicion = ca.valor(CRITERIO_CONDICION_PAVIMENTO)   # CriterioPendienteError
    filas = tabla[material.tipo.value]
    if condicion not in filas:
        raise DatoInvalidoError(
            CRITERIO_CONDICION_PAVIMENTO, valor=condicion,
            motivo="la condicion de pavimento declarada tiene que ser una de "
                   f"las filas transcritas de la Tabla 12.6.6.3-1: "
                   f"{sorted(filas)}",
        )
    fila = filas[condicion]

    # El ancho exterior se pide SOLO si la fila lo usa. La fila del concreto
    # (Bc) lo necesita y por lo tanto se detiene en 'espesor_pared_conducto';
    # las del metal (S) y el termoplastico (ID) no, y exigirselo seria
    # inventarles una dependencia que la tabla no tiene. Quien SI la tiene
    # siempre es la cota de clave, que es otra cosa y esta en M5.
    #
    # QUE `Bc` SALGA DE LA SECCION, y no de un "diametro exterior", es lo que hace
    # correcta la ranura de Bc en vez de dejarla a la coincidencia: Bc es la
    # dimension HORIZONTAL, y un `D + 2t` solo la da porque en un
    # circulo ancho y canto coinciden.
    #
    # SOLO LA RAMA DE Bc SE DESACOPLA, y decirlo entero importa porque el
    # parrafo anterior decia «ya no depende de esa coincidencia» a secas y eso
    # es falso para las otras dos filas: `S` es «diameter of pipe» e `ID` el
    # diametro interior, y las dos siguen leyendo la dimension VERTICAL
    # (`seccion.altura`). No es un defecto: esas dos filas son de conducto
    # CIRCULAR -- metal corrugado y termoplastico --, donde vertical y
    # horizontal son el mismo numero por geometria, y el marco sale antes de
    # llegar aqui. Pero la frase que lo cubria todo era mas ancha que el
    # arreglo, y lo midio la auditoria adversarial de C7.
    if _DIAMETRO_DE_LA_FILA[fila["sobre"]] == "D_ext":
        D_fila = seccion.ancho_exterior(espesor_pared(material,
                                                      seccion.altura))
    else:
        D_fila = seccion.altura

    candidatos = [fila["piso_m"]]
    if fila["divisor"] is not None:
        candidatos.append(D_fila / fila["divisor"])
    return max(candidatos)


def altura_recubrimiento(*, material: Material,
                         seccion: Seccion) -> Tuple[float, str]:
    """
    h_rec: relleno minimo sobre la clave hasta la subrasante, m (Sec. 7.A), y
    CUAL DE LOS DOS MINIMOS GANO.

        h_rec = max( minimo de EG-2013 , cobertura minima de AASHTO )

    REGLA DEL MAYOR, la misma que Sec. 0.2 ya aplica al recubrimiento de
    concreto entre AASHTO y E.060. Los dos minimos regulan lo mismo desde dos
    corpus distintos y ninguno deroga al otro: EG-2013 es norma peruana
    vigente [N] y AASHTO LRFD es el cuerpo que Sec. 0.2 adopta de extremo a
    extremo, cubriendo con [C] el vacio que el corpus peruano deja.

    DEVUELVE EL PAR, Y ESA ES LA MITAD QUE FALTABA. Un `max()` sin decir cual
    gano publica la REGLA y esconde el RESULTADO DE APLICARLA, que es el dato
    que el revisor necesita: si el punto no cabe por 5 cm, mover el espesor de
    pared solo sirve si quien manda es AASHTO, y no sirve de nada si manda el
    0.30 m de EG-2013, que es una constante. Hasta C7 el paso de G1 escribia
    «el MAYOR entre...» y ahi se quedaba. El nombre del ganador sale de las
    constantes MINIMO_EG2013 / MINIMO_AASHTO y no se escribe suelto en cada
    sitio, para que la memoria no pueda llamarlos de dos maneras.

    EL EMPATE SE ADJUDICA A AASHTO, y es una decision, no un descuido del
    `>`: es el unico de los dos que depende de la geometria del conducto, de
    modo que en un empate senala la variable que SI se puede mover.

    Y NO ES LA MISMA REGLA CON QUE EL TAMIZADO DESEMPATA, que es lo que este
    parrafo decia -- «es la misma regla ... y por la misma razon» -- y es
    FALSO: `tamizado_rasante` desempata al reves y lo dice, «se declara
    gobernante el RECUBRIMIENTO, por ser LA QUE NO DEPENDE DEL CALCULO
    HIDRAULICO ... ante la duda se senala LA MAS ESTABLE». Alli se prefiere la
    condicion ESTABLE; aqui, la MOVIBLE. Los dos criterios son defendibles y
    son OPUESTOS, y presentarlos como el mismo era inventar una coherencia que
    no existe. Lo encontro la auditoria adversarial de C7. Se dejan los dos
    como estan -- cambiarlos moveria numeros por una razon de estilo -- y se
    dice que difieren.

    QUE CAMBIO Y POR QUE (NOR-VAC-01, MAT-D4, conflicto #5 del plan de
    correcciones). Esta funcion devolvia `material.h_relleno_min`: 0.30 m para
    los tres materiales -- [N] de EG-2013 en HDPE y adoptado por analogia en
    concreto y TMC. Ese numero estaba mal por DOS motivos que se acumulaban
    sobre el mismo valor, y corregir uno solo lo dejaba corto igual:

      (1) EL NUMERO. La Tabla 12.6.6.3-1 pone un piso de 12.0 in = 0.3048 m
          para concreto y para metal, de modo que 0.30 m quedaba 5 mm por
          debajo; y en diametros grandes no gobierna el piso sino Bc/8, que
          para un tubo de concreto de 2.40 m da ~0.36 m, un 20 % mas.
      (2) EL PUNTO DESDE DONDE SE MIDE. La clave se calculaba sobre el
          diametro interior, sin espesor de pared, de modo que la rasante
          minima salia corta ademas en t. Ver `M5_verificaciones.cota_clave`.

    El vacio que la analogia cubria no era un vacio: la busqueda se declaro
    cerrada tras agotar tres fuentes y la cuarta -- AASHTO LRFD Sec. 12 --
    estaba en normas/ y es la que el propio proyecto adopta. El criterio
    'h_relleno_min_concreto_tmc' se retiro.

    LO QUE NO ES UNIFORME, Y HAY QUE DECIRLO. "El numero era corto" vale en
    ocho de las nueve combinaciones material x condicion, no en las nueve. En
    CONCRETO bajo PAVIMENTO RIGIDO la tabla pide 9.0 in = 0.2286 m, que es
    MENOS que el 0.30 m retirado. Frente al estado anterior, el balance de la
    correccion en esa casilla es exactamente `t - 0.0714 m`: con el espesor
    de la corrida de pruebas (t = 0.100) la rasante minima sube 0.029 m, pero
    con un t declarado por debajo de 0.0714 m BAJARIA. No es un descuido: son
    dos cambios independientes -- el umbral y el punto desde donde se mide --
    y en esa casilla apuntan en sentidos opuestos. Quien declare
    'espesor_pared_conducto' por debajo de ese valor para concreto tiene que
    saber que esta relajando la exigencia respecto de lo que el expediente
    venia aplicando, y decirlo en la memoria.

    Se detiene con `CriterioPendienteError` en 'condicion_pavimento' (que fila
    de la tabla) y en 'espesor_pared_conducto' (el Bc del concreto).
    """
    aashto = cobertura_minima_aashto(material=material, seccion=seccion)
    if material.forma is FormaSeccion.RECTANGULAR:
        # NO ES «el mayor entre dos»: no hay dos. Ni la tabla de AASHTO ni el
        # EG-2013 alcanzan a un marco, de modo que el numero sale entero del
        # criterio declarado y la memoria tiene que decir ESO y no otra cosa.
        return aashto, (f"{MINIMO_CAJON_DECLARADO} ({aashto:.3f} m): ni la "
                        f"Tabla 12.6.6.3-1 de AASHTO --sin fila de cajon de "
                        f"concreto-- ni el EG-2013 --que solo fija altura de "
                        f"relleno para HDPE-- alcanzan a un marco, de modo "
                        f"que aqui no hay dos minimos que comparar")
    eg2013 = material.h_relleno_min_eg2013
    if eg2013 is None:
        return aashto, (f"{MINIMO_AASHTO} ({aashto:.3f} m); {MINIMO_EG2013} "
                        "no fija minimo de relleno para este material")
    if eg2013 > aashto:
        return eg2013, (f"{MINIMO_EG2013} ({eg2013:.3f} m), sobre "
                        f"{MINIMO_AASHTO} ({aashto:.3f} m)")
    return aashto, (f"{MINIMO_AASHTO} ({aashto:.3f} m), sobre "
                    f"{MINIMO_EG2013} ({eg2013:.3f} m)")


def criterio_recubrimiento(material: Material) -> Optional[str]:
    """
    Clave del criterio del que sale h_rec: 'cobertura_minima_aashto' en las
    secciones circulares y 'cobertura_minima_cajon' en el marco.

    QUE DEVUELVA CLAVES DISTINTAS ES EL PUNTO, no un detalle: esta clave es la
    que viaja a `Verificacion.criterio_aplicado` de G1 y la que M11 imprime.
    Con una sola clave, la memoria de un marco habria dicho que su h_rec sale
    de la Tabla 12.6.6.3-1 de AASHTO -- que no tiene fila de cajon de
    concreto: ver la `AfirmacionNegativa` SIN_CAJON_DE_CONCRETO_T12663 --, que
    es la cita falsa que este proyecto persigue.

    Devolvia None en HDPE -- donde el 0.30 m se leia como [N] puro de EG-2013
    -- y 'h_relleno_min_concreto_tmc' en los otros dos. Ahora la tabla de
    AASHTO entra en los TRES materiales, de modo que en los tres hay un
    criterio [C] que declarar; en HDPE ademas compite con el minimo [N] de
    EG-2013 y puede ganarlo cualquiera de los dos segun el diametro y la
    condicion de pavimento.

    Se conserva la firma Optional -- y la funcion, en vez de una constante --
    porque el dia en que un material tenga h_rec gobernado solo por EG-2013 no
    habra criterio adoptado que declarar, y la `Verificacion` de G1 tiene que
    poder decirlo. `Material` guarda los valores pero no su procedencia.
    """
    if material.forma is FormaSeccion.RECTANGULAR:
        return CRITERIO_COBERTURA_CAJON
    return CRITERIO_COBERTURA_AASHTO


# ---------------------------------------------------------------------------
# 7.A - Tamizado previo: la cota de rasante minima
# ---------------------------------------------------------------------------

def tamizado_rasante(*, punto: PuntoCritico, material: Material,
                     seccion: Seccion, HW: float) -> TamizadoRasante:
    """
    Tamizado de Sec. 7.A: cota de rasante minima como MAXIMO de las dos
    condiciones, y el delta que le falta a la rasante del CSV para alcanzarla.

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             cota entrada + HW + resguardo(CBR) + e_paq )

    Argumentos
    ----------
    seccion         la seccion del tamizado. Sec. 7.A manda correrlo con la
                    MAXIMA supuesta antes de definir el perfil; en 7.B se
                    vuelve a correr con la adoptada. Es explicita porque la
                    eleccion se declara en la memoria: ver la ADVERTENCIA del
                    docstring del modulo, la seccion maxima no es conservadora
                    para las dos condiciones a la vez.
                    ES LA SECCION Y NO UN `D` DESDE C7: con un escalar, la
                    unica dimension que llegaba a 7.A era la vertical, y en un
                    marco la cobertura minima se lee sobre la HORIZONTAL. El
                    escalar no lo dejaba ver -- en un circulo las dos
                    coinciden --, que es como un marco acabo recibiendo la
                    cobertura de la fila del tubo calculada sobre su canto.
    HW          m   carga a la entrada SOBRE EL FONDO DE LA ENTRADA (Sec. 4.2
                    / 4.3), no una cota. La convierte a cota este modulo, con
                    la misma referencia que usa V4.

    NO lanza excepcion cuando el punto no alcanza: devuelve el resultado con
    `factible=False` y el delta cargado (`delta_rasante_m`, `delta_rasante_cm`
    y `mensaje`), que es lo que Sec. 7.B pide -- "el chequeo devuelve 'no
    factible -> subir rasante X cm', nunca un resultado silencioso". Quien
    necesite abortar llama a `TamizadoRasante.exigir_factible()`, que lanza
    `DisenoNoFactibleError` CON el delta dentro.

    Empate entre las dos condiciones: se declara gobernante el RECUBRIMIENTO,
    por ser la que no depende del calculo hidraulico. La cota devuelta es la
    misma en cualquier caso; lo que cambia es que variable hay que mover, y
    ante la duda se señala la mas estable.
    """
    e_paq = espesor_paquete(punto)
    h_rec, minimo_que_gobierna = altura_recubrimiento(material=material,
                                                      seccion=seccion)
    cota_entrada = cota_de_entrada(punto)
    entrada = cota_entrada.valor
    altura = seccion.altura
    clave = cota_clave(punto=punto, material=material, seccion=seccion)
    t_pared = espesor_pared(material, altura)
    Bc = seccion.ancho_exterior(t_pared)

    ca.valor(CRITERIO_RESGUARDO)      # registra el uso; "segun_CBR" no es numerico
    resguardo = resguardo_por_cbr(punto.cbr_subrasante)

    por_recubrimiento = clave + h_rec + e_paq
    por_resguardo = entrada + HW + resguardo + e_paq

    cota_min = max(por_recubrimiento, por_resguardo)
    if por_resguardo > por_recubrimiento + TOL_UMBRAL_NORMATIVO:
        condicion = CondicionRasante.RESGUARDO
    else:
        condicion = CondicionRasante.RECUBRIMIENTO

    faltante = cota_min - punto.cota_rasante
    factible = faltante <= TOL_UMBRAL_NORMATIVO

    return TamizadoRasante(
        cota_rasante_min=cota_min,
        cota_rasante_actual=punto.cota_rasante,
        cota_por_recubrimiento=por_recubrimiento,
        cota_por_resguardo=por_resguardo,
        condicion_gobernante=condicion,
        cota_entrada=entrada,
        cota_clave=clave,
        altura_supuesta=altura,
        espesor_pared=t_pared,
        ancho_exterior=Bc,
        HW=HW,
        h_recubrimiento=h_rec,
        espesor_paquete=e_paq,
        resguardo=resguardo,
        factible=factible,
        delta_rasante_m=0.0 if factible else faltante,
        criterio_recubrimiento=criterio_recubrimiento(material),
        numeral_g1=numeral_g1(material),
        minimo_que_gobierna=minimo_que_gobierna,
        criterio_resguardo=CRITERIO_RESGUARDO,
        id_punto=punto.id,
        numeral=NUMERAL_7A,
        # T-6 (INF-5.1.18): las dos condiciones se levantan sobre la cota de
        # entrada. Si es el terreno adoptado y no el fondo medido, la rasante
        # minima y su delta son PROVISIONALES y el objeto lo dice.
        provisional=bool(cota_entrada.aviso),
        aviso=cota_entrada.aviso,
    )


def g1_rasante_congelada(tamizado: TamizadoRasante) -> Verificacion:
    """
    G1: la rasante del expediente alcanza la minima del tamizado de 7.A.

    Es la unica de las dos verificaciones de 7.B que no necesita la longitud
    del conducto, y por lo tanto la unica evaluable sin 'talud_terraplen'.
    El criterio
    aplicado es el de la condicion que gobierna: 'resguardo_HW_subrasante'
    [N->] si manda la carga a la entrada, y si manda el recubrimiento, el que
    `criterio_recubrimiento` devuelva -- 'cobertura_minima_aashto' [C] en los
    tres materiales del catalogo CIRCULAR, porque la Tabla 12.6.6.3-1 entra en
    los tres, y 'cobertura_minima_cajon' [A] en un marco, que no tiene fila en
    esa tabla.

    ESTE PARRAFO DECIA «en los tres materiales» A SECAS y era falso desde que
    C7 abrio el vacio del cajon: lo encontro la auditoria adversarial de esa
    sesion, junto con los otros dos canales por los que la memoria de un marco
    seguia nombrando la tabla del tubo (el `numeral`, hoy `numeral_g1`, y la
    procedencia de la magnitud `h_rec`).

    Sigue sin necesitar 'talud_terraplen' -- solo lee campos de
    `TamizadoRasante`, y el tamizado nunca llama a `proyeccion_taludes` --,
    pero eso ya no la hace evaluable "hoy mismo": el tamizado que la alimenta
    se detiene ahora en 'espesor_pared_conducto' y en 'condicion_pavimento'.
    Lo que cambio no es esta funcion sino lo que hay que declarar antes de
    llegar a ella.
    """
    manda_recubrimiento = (tamizado.condicion_gobernante
                           is CondicionRasante.RECUBRIMIENTO)
    return Verificacion(
        cumple=tamizado.factible,
        numeral=tamizado.numeral_g1,
        valor_obtenido=tamizado.cota_rasante_actual,
        valor_admisible=tamizado.cota_rasante_min,
        criterio_aplicado=tamizado.criterio_gobernante,
        codigo="G1",
        paso=paso(
            "F7.RELLENO",
            codigo="G1",
            que="Rasante minima: la que el conducto exige bajo la via",
            formula="cota_rasante_min = max(cota_clave + h_rec + e_paquete, "
                    "cota_entrada + HW + resguardo + e_paquete)",
            formula_cita_id="AASHTO_LRFD_9.12.6.6.3#COBERTURA",
            citas_textuales=("AASHTO_LRFD_9.12.6.6.3#COBERTURA",
                             "EG2013.508.07#RELLENO_MIN"),
            sustitucion=(
                Magnitud("cota_clave", tamizado.cota_clave, "msnm",
                         "cota de entrada + D + espesor de pared: es la clave "
                         "FISICA, la exterior. Medirla sobre el diametro "
                         "interior dejaba la rasante minima corta en t "
                         "(MAT-D3, MAT-D4)", cifras=CIFRAS_MAGNITUD),
                Magnitud("h_rec", tamizado.h_recubrimiento, "m",
                         "relleno minimo sobre la clave: el MAYOR entre el "
                         "minimo de la EG-2013 y la cobertura minima de la "
                         "Tabla 12.6.6.3-1 de AASHTO. AQUI GOBIERNA "
                         f"{tamizado.minimo_que_gobierna}",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("e_paquete", tamizado.espesor_paquete, "m",
                         "cota de rasante menos cota de subrasante del CSV",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("resguardo", tamizado.resguardo, "m",
                         "tabla de resguardo por CBR del Manual de Suelos, la "
                         "misma que consume V4", cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud("cota_rasante_min", tamizado.cota_rasante_min,
                               "msnm",
                               f"gobierna la condicion "
                               f"{tamizado.condicion_gobernante.value}",
                               cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="cota de rasante minima que el conducto exige",
                valor=tamizado.cota_rasante_min, unidad="msnm",
                cita_id="AASHTO_LRFD_9.12.6.6.3#COBERTURA",
                caracter="EXIGENCIA",
                aplicacion="REGLA DEL MAYOR entre la EG-2013 y AASHTO, la "
                           "misma que la Sec. 0.2 aplica al recubrimiento de "
                           "concreto: los dos minimos regulan lo mismo desde "
                           "dos corpus y ninguno deroga al otro. Cumplir el "
                           "menor dejaria el otro incumplido.",
                criterio_aplicado=tamizado.criterio_gobernante),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if tamizado.factible
                      else TipoDeVeredicto.NO_CUMPLE),
                margen=(tamizado.cota_rasante_actual
                        - tamizado.cota_rasante_min),
                unidad="m",
                explicacion=(
                    "la rasante del expediente ya alcanza la minima"
                    if tamizado.factible else
                    f"no factible: hay que subir la rasante "
                    f"{tamizado.delta_rasante_m:.3f} m")),
            elecciones=(EleccionDeProyecto(
                que_se_adopto="condicion que gobierna la rasante minima",
                valor=tamizado.condicion_gobernante.value,
                entre=(f"recubrimiento: {tamizado.cota_por_recubrimiento:.3f} "
                       "msnm",
                       f"resguardo bajo subrasante: "
                       f"{tamizado.cota_por_resguardo:.3f} msnm"),
                de_donde="las dos condiciones de la Sec. 7.A, evaluadas para "
                         "este punto",
                por_que=("manda el RECUBRIMIENTO: el conducto necesita mas "
                         "relleno encima del que el agua necesita por debajo"
                         if manda_recubrimiento else
                         "manda el RESGUARDO: la carga a la entrada exige mas "
                         "rasante que la cobertura del conducto"),
                clave_criterio=tamizado.criterio_gobernante or ""),),
            nota_del_proyecto=(
                f"AVISO: {tamizado.aviso}. La cota de clave y la cota de "
                "entrada de las dos condiciones salen de esa adopcion, de "
                "modo que la rasante minima y el delta de rasante de este "
                "paso son PROVISIONALES: con el fondo medido bajo el "
                "terreno, las dos condiciones bajan lo mismo que el fondo."
                if tamizado.provisional else ""),
        ),
    )


# ---------------------------------------------------------------------------
# Piezas de 7.B: longitud, esviaje y cotas
# ---------------------------------------------------------------------------

def factor_esviaje(punto: PuntoCritico) -> float:
    """
    1 / cos(esviaje): cuanto alarga el cruce oblicuo la longitud del conducto
    (Sec. 7.B, "afectada por esviaje").

    Identidad geometrica, no coeficiente adoptado: el eje del conducto es la
    hipotenusa del ancho que atraviesa. Vale 1 en el cruce perpendicular.
    A 90 grados el conducto seria paralelo a la via y no habria cruce que
    resolver -- `dominios.ESVIAJE_MAX`, que M0 ya exige a la entrada.

    LA ASINTOTA NO ESTA ACOTADA, Y SE DECLARA (MAT-O18). El dominio es
    abierto en 90 grados, no cerrado, de modo que un esviaje que M0 acepta
    puede estar arbitrariamente cerca del limite: con 89.9999 grados el
    factor vale 5.7e5 y `longitud_conducto` devuelve del orden de 1e6 m; con
    89.9 grados, 573 y 10 313 m sobre A-01. La ficha MAT-O18 lo clasifica
    como "no alcanzable desde el CSV validado", y eso es INEXACTO: M0 valida
    `0 <= esviaje < 90` y esos valores pasan.

    ESTA FUNCION NO PONE COTA DE CORDURA, y la razon cambio de redaccion en
    T-6. Hasta entonces este parrafo decia que elegir un maximo -- 45, 60
    grados -- «seria inventar un valor normativo». Sigue siendo cierto que
    ninguna fuente fija un esviaje maximo del BARRIL (ni la Sec. 7.B ni
    EG-2013), y por eso el numero no se escribe AQUI ni detiene el calculo;
    lo que T-6 hizo es lo que el parrafo ya señalaba como camino: adoptarlo
    como criterio [A] con su ventana ('esviaje_max_grados', 45 grados, por
    analogia con el maximo practico del esviaje de embocadura del HDS-5), que
    no es un valor normativo sino una adopcion declarada, y aplicarlo como
    AVISO. La longitud de un esviaje absurdo sigue viendose en la memoria.

    Y ESE CAMINO EXISTE DESDE EL CIERRE DE C10 (PC-32): el criterio [A]
    'esviaje_max_grados' de criterios_adoptados.py. Hasta T-6 era opcional y,
    declarado, un esviaje que lo superase salia de AQUI como
    `DatoInvalidoError`. DESDE T-6 TIENE VALOR (45 grados, por analogia con
    el maximo practico del esviaje de embocadura del HDS-5 num. 5.4.2) Y NO
    SE APLICA EN ESTA FUNCION: el esviaje es un dato de entrada medido, y un
    dato que supera una adopcion del proyecto se SEÑALA en vez de rechazarse.
    El aviso lo emite `g3_esviaje` (verificacion G3 de 7.B, veredicto
    INDICADOR); esta funcion calcula el factor para todo esviaje del dominio.

    LO QUE SI TIENE ES UNA GUARDIA DE SALIDA NUMERICA (PC-32, EXT-1), y
    conviene no confundirla con la cota anterior: por debajo de
    `tolerancias.COS_ESVIAJE_MIN` -- cos(theta) ~ 3.5e-7, o sea theta por
    encima de 89.99998 grados -- el redondeo del angulo en doble precision
    mueve el factor mas que TOL_UMBRAL_NORMATIVO en relativo, y el numero ya
    no esta determinado por el dato. Ahi sale `LimiteNumericoError` con el
    umbral nombrado (patron SIS-G-01). El umbral se DERIVA de epsilon y de la
    tolerancia del proyecto, no se elige: es la frontera exacta entre una
    tolerancia y un valor de proyecto. El 89.9 del dictamen (10 313 m) queda
    del lado que pasa, a proposito, por el parrafo anterior.
    """
    # EL DOMINIO ES EL DE M0, [0, ESVIAJE_MAX), Y NO UN SUPERCONJUNTO (T-6,
    # auditor adversarial). Esta guarda admitia (-ESVIAJE_MAX, ESVIAJE_MAX) y
    # se apoyaba en que M0 rechaza el negativo al cargar (SIS-B-23): cierto
    # para un punto que viene del CSV, falso para quien llama a M7 con un
    # `PuntoCritico` armado a mano -- medido: -89 grados daba factor 57.3,
    # 3301 m de conducto y G3 en «cumple» --. Un esviaje es el angulo con la
    # normal a la via, sin signo. Forma MAT-D13: condicion en positivo y
    # negada, para que un NaN tampoco pase.
    if not (0 <= punto.esviaje_grados < ESVIAJE_MAX):
        raise DatoInvalidoError(
            "esviaje_grados", valor=punto.esviaje_grados, id_punto=punto.id,
            motivo=f"el esviaje va de 0 (cruce perpendicular) a {ESVIAJE_MAX} "
                   "grados, donde el conducto seria paralelo a la via y la "
                   "longitud de 7.B no estaria definida; es el angulo con la "
                   "normal al eje de la via y no lleva signo",
        )
    # --- T-6 --- EL TOPE YA NO SE APLICA AQUI. Desde el cierre de C10 esta
    # funcion detenia con `DatoInvalidoError` todo esviaje sobre
    # 'esviaje_max_grados' cuando el criterio estaba declarado. T-6 le da
    # valor al criterio (45 grados) y cambia lo que hace: el esviaje es un
    # DATO DE ENTRADA y superarlo es un AVISO que emite `g3_esviaje`, no un
    # rechazo. El factor se calcula igual por encima del maximo.
    coseno = math.cos(math.radians(punto.esviaje_grados))
    if not coseno > COS_ESVIAJE_MIN:
        # GUARDIA DE SALIDA CON UMBRAL NOMBRADO (PC-32, patron SIS-G-01). El
        # dato cumple su dominio -- M0 admite todo esviaje < 90 -- y es la
        # aritmetica 1/cos la que deja de estar determinada: por debajo de
        # `tolerancias.COS_ESVIAJE_MIN` el redondeo del angulo mueve el
        # factor mas de TOL_UMBRAL_NORMATIVO en relativo. Es un limite
        # NUMERICO y no una cota de cordura: 89.9 grados sigue pasando, y por
        # que se explica en el docstring (MAT-O18) y en tolerancias.py.
        raise LimiteNumericoError(
            "esviaje_grados", valor=punto.esviaje_grados, id_punto=punto.id,
            motivo=f"1/cos(esviaje) no esta determinado en doble precision: "
                   f"cos({punto.esviaje_grados!r} grados) = {coseno!r} queda "
                   f"por debajo de COS_ESVIAJE_MIN = {COS_ESVIAJE_MIN!r} "
                   "(tolerancias.py), de modo que el ultimo bit del angulo "
                   "mueve la longitud de 7.B mas que la tolerancia con que "
                   "el proyecto compara umbrales. No es un esviaje fuera de "
                   f"rango -- el dominio es abierto en {ESVIAJE_MAX} grados "
                   "y ninguna norma de normas/ fija un maximo constructivo "
                   "--, es un cruce cuya longitud no se puede calcular con "
                   "este dato",
        )
    return 1.0 / coseno


def _exigir_finito(campo: str, valor: float, punto: PuntoCritico) -> float:
    """
    Devuelve `valor` si es finito; si no, LimiteNumericoError (SIS-G-01).

    ES UNA GUARDA DE SALIDA, Y AHI ESTA LA GRACIA. La de ENTRADA ya existe y
    esta cerrada por los dos lados: `M0_carga._a_float` rechaza 'inf' y 'nan'
    en cualquier celda del CSV (MAT-D14) y `criterios_adoptados.
    _verificar_finitud` los rechaza en cualquier criterio declarado. Lo que
    ninguna de las dos puede cerrar es que una ARITMETICA entre numeros
    finitos desborde: 2 * 1.5 * 1e308 no es un dato mal declarado, es una
    multiplicacion que no cabe en un double.

    POR QUE NO SE CIERRA PONIENDOLE TECHO A LA COTA, que es el remedio que
    parece obvio: porque ese techo seria un VALOR DE PROYECTO inventado --
    "una rasante no pasa de N msnm" no lo dice ninguna norma, no lo dice la
    hoja de ruta, y CLAUDE.md lo prohibe expresamente. `dominios.py` acota lo
    que un dato PUEDE SER (un CBR sobre 100 esta en otra escala; un esviaje de
    120 grados no existe); la altura de una rasante no tiene un limite de esa
    naturaleza. Por eso la guarda va donde el problema aparece de verdad -- la
    salida del calculo -- y no donde seria comodo ponerla.

    Se aplica a las cuatro salidas de 7.B que se MIDIERON capaces de desbordar
    desde un CSV que pasa las tres validaciones de M0: `altura_terraplen` (una
    resta de cotas de signo opuesto), `proyeccion_taludes`, `longitud_conducto`
    y `cota_salida`. Las tres ultimas heredan el desborde de la primera y
    ademas lo pueden producir por su cuenta.

    QUE UNA GUARDA INTERNA DISPARE ANTES QUE LA EXTERNA ES LO QUE SE BUSCA, no
    un solapamiento: `longitud_conducto` llama a `proyeccion_taludes`, que ya
    esta guardada, de modo que el error nombra la magnitud concreta que
    desbordo en vez de la que la contiene.

    NO HAY GUARDA EQUIVALENTE EN M9, y es deliberado: `verificar_volteo` y
    `verificar_deslizamiento` devuelven `math.inf` A PROPOSITO como FS cuando
    la solicitacion es nula -- "no vuelca" no es un numero grande, es la
    ausencia del momento volcante --, y un barrido que prohibiera todo
    no-finito en la salida de todo el calculo mataria ese caso legitimo. Son
    los dos unicos productores deliberados de `inf` del repositorio.
    """
    if not math.isfinite(valor):
        raise LimiteNumericoError(
            campo, valor=valor, id_punto=punto.id,
            motivo=f"el calculo de 7.B desbordo la doble precision partiendo "
                   f"de datos que SI son finitos (cota de rasante "
                   f"{punto.cota_rasante!r}, cota de terreno "
                   f"{punto.cota_terreno!r}, ancho de plataforma "
                   f"{punto.ancho_plataforma!r}). No es un dato fuera de "
                   f"rango -- ninguna cota tiene techo en dominios.py, y no "
                   f"se le puede inventar uno --, es que la aritmetica entre "
                   f"ellos no cabe en un numero. Sin esta guarda el valor "
                   f"seguiria hasta la memoria y el informe imprimiria un "
                   f"diagnostico entero construido sobre un 'inf'"
        )
    return valor


def altura_terraplen(punto: PuntoCritico) -> float:
    """
    Altura del terraplen en el cruce, m: cota de rasante - cota de terreno.

    Es el brazo vertical del talud. No es la altura de relleno sobre la clave
    (esa es h_rec + el diametro y sale de la subrasante): son dos alturas
    distintas y confundirlas alarga el conducto.
    """
    return _exigir_finito("altura_terraplen",
                          punto.cota_rasante - punto.cota_terreno, punto)


def proyeccion_taludes(punto: PuntoCritico) -> float:
    """
    Proyeccion horizontal de los taludes del terraplen, m (Sec. 7.B).

        proyeccion = 2 * talud * altura de terraplen

    El 2 son los DOS taludes, uno a cada lado de la plataforma, con la misma
    altura: el CSV entrega una sola cota de terreno por punto (Sec. 1.2) y por
    lo tanto lo unico que se puede calcular es el terraplen simetrico. Si la
    seccion del punto es asimetrica, la longitud se mide sobre la seccion
    transversal y se pasa a `compatibilidad_geometrica` como dato.

    El talud sale del criterio 'talud_terraplen' [A], hoy VACIO: Sec. 7.B pide
    sumar esta proyeccion pero no da la inclinacion, y Sec. 1.2 no la trae
    como columna. La llamada se detiene con CriterioPendienteError hasta que
    se declare.
    """
    talud = ca.valor(CRITERIO_TALUD)      # CriterioPendienteError mientras falte
    return _exigir_finito("proyeccion_taludes",
                          2 * talud * altura_terraplen(punto), punto)


# ---------------------------------------------------------------------------
# --- T-6 --- Pendiente adoptada, longitud por extremo y pasos de 7.B
# (INF-3.3.3, INF-5.1.18, INF-3.2.7)
# ---------------------------------------------------------------------------

def _caracter_de(cita_id: str) -> str:
    """El caracter de una cita, leido del registro y no escrito a mano."""
    return _registro.construir().cita(cita_id).caracter.value.upper()


def pendiente_adoptada(punto: PuntoCritico,
                       S_declarada: Optional[float] = None
                       ) -> PendienteAdoptada:
    """
    La pendiente del conducto con su ORIGEN (Sec. 7.B; T-6 punto 5).

    Tres origenes, en este orden:

      1. DECLARADA   el punto trae `S_conducto` (dato externo). Es una
                     decision del expediente para ese punto y el calculo no
                     la pisa: si queda fuera de la banda adoptada, quien lo
                     dice es V10 (`M5.v10_pendiente_conducto`).
      2. MINIMA o    la pendiente del CAUCE queda bajo
         MAXIMA      'pendiente_minima_conducto' o sobre
                     'pendiente_maxima_conducto' y gobierna el extremo de la
                     banda, leida de `M5.limites_de_pendiente()`.
      3. CAUCE       `S_cauce`, la regla de Sec. 7.B: el conducto sigue al
                     cauce. Es lo que el HDS-5 num. 5.3.3 asocia a la
                     ausencia de problemas de sedimentacion.

    EL REPARTO CON V10, que hay que decir porque las dos piezas leen la misma
    banda: ESTA funcion acota la pendiente del CAUCE --el dato que nadie
    eligio-- y lo declara con su origen y un aviso (`aviso_de_pendiente`);
    V10 JUZGA la pendiente con que corrio el diseño, y como aqui la del cauce
    ya sale dentro de la banda, V10 solo puede incumplirse con una pendiente
    DECLARADA. Las dos usan la misma tolerancia (`TOL_UMBRAL_NORMATIVO`), de
    modo que el extremo adoptado aqui cumple alli. Lo que el extremo trae
    consigo no lo resuelve este modulo, y por eso se avisa:

      MAXIMA  el conducto queda MAS TENDIDO que su cauce. El desnivel que el
              barril no baja, (S_cauce - S_conducto) * L, hay que resolverlo
              con una estructura de caida o de disipacion en un extremo, que
              este calculo no dimensiona; y V2b compara S_conducto con
              S_cauce y lo juzga segun 'regimen_v2b' (indicador con aviso, o
              umbral duro: entonces el punto no dimensiona).
      MINIMA  el conducto CAE MAS que su cauce: la salida queda
              (S_conducto - S_cauce) * L bajo el cauce natural, y G2 la juzga
              contra el fondo del receptor.

    ES EL UNICO SITIO DONDE SE RESUELVE (MAT-D9: la pendiente no se elige dos
    veces). `servicio` la llama antes de la Fase 4 y pasa el MISMO valor a la
    longitud, al TW, a MD y a 7.B.

    El Manual del MTC exige cuidar la pendiente y no da ninguna cifra (num.
    4.1.1.3.3, pag. impresa 71): los dos extremos son criterios [A].

    Excepciones: `DatoFaltanteError('S_cauce')` si no hay ni declaracion ni
    pendiente de cauce; `DatoInvalidoError` si la pendiente no es un numero
    finito y no negativo (segunda linea: M0 y la carga de datos externos ya
    lo exigen) o si la banda adoptada queda vacia (de
    `M5.limites_de_pendiente`).
    """
    if S_declarada is not None:
        if not (S_declarada >= 0 and math.isfinite(S_declarada)):
            raise DatoInvalidoError(
                "S_conducto", valor=S_declarada, id_punto=punto.id,
                motivo="la pendiente declarada del conducto tiene que ser un "
                       "numero finito y no negativo (0 es el barril "
                       "horizontal); la pendiente adversa no se admite")
        return PendienteAdoptada(
            valor=S_declarada, origen=OrigenPendiente.DECLARADA,
            S_cauce=punto.S_cauce, S_declarada=S_declarada,
            S_minima=None, S_maxima=None,
            procedencia="dato externo `S_conducto` declarado para este "
                        "punto: no es la pendiente del cauce, y la banda de "
                        "pendiente adoptada no la sustituye (la juzga V10)")
    S_cauce = punto.exigir("S_cauce")
    if not (S_cauce > 0 and math.isfinite(S_cauce)):
        raise DatoInvalidoError(
            "S_cauce", valor=S_cauce, id_punto=punto.id,
            motivo="la pendiente del cauce tiene que ser un numero finito y "
                   "positivo para adoptarla como pendiente del conducto; un "
                   "barril horizontal se declara con `S_conducto` = 0, no "
                   "con la pendiente del cauce")
    S_min, S_max = limites_de_pendiente()
    if not S_cauce >= S_min - TOL_UMBRAL_NORMATIVO:
        return PendienteAdoptada(
            valor=S_min, origen=OrigenPendiente.MINIMA, S_cauce=S_cauce,
            S_declarada=None, S_minima=S_min, S_maxima=S_max,
            procedencia=f"criterio '{CRITERIO_PENDIENTE_MINIMA}': la "
                        f"pendiente del cauce ({S_cauce!r}) queda por debajo "
                        "y gobierna el minimo adoptado")
    if not S_cauce <= S_max + TOL_UMBRAL_NORMATIVO:
        return PendienteAdoptada(
            valor=S_max, origen=OrigenPendiente.MAXIMA, S_cauce=S_cauce,
            S_declarada=None, S_minima=S_min, S_maxima=S_max,
            procedencia=f"criterio '{CRITERIO_PENDIENTE_MAXIMA}': la "
                        f"pendiente del cauce ({S_cauce!r}) lo supera y "
                        "gobierna el maximo adoptado")
    return PendienteAdoptada(
        valor=S_cauce, origen=OrigenPendiente.CAUCE, S_cauce=S_cauce,
        S_declarada=None, S_minima=S_min, S_maxima=S_max,
        procedencia="pendiente del cauce (`S_cauce`): el conducto sigue al "
                    "cauce, que es la regla de la Sec. 7.B")


def desnivel_frente_al_cauce(pendiente: PendienteAdoptada,
                             longitud: float) -> Optional[float]:
    """
    (S_cauce - S_conducto) * L, en metros: lo que el cauce baja a lo largo
    del conducto y el barril no (positivo: conducto mas tendido que el
    cauce), o lo que el barril baja de mas (negativo). None si el punto no
    tiene pendiente de cauce con que comparar (Sec. 7.B).

    Es la magnitud de obra que trae consigo una pendiente que no es la del
    cauce, y la que imprimen el paso 7.B.4 y `aviso_de_pendiente`.
    """
    if pendiente.S_cauce is None:
        return None
    return (pendiente.S_cauce - pendiente.valor) * longitud


def aviso_de_pendiente(pendiente: PendienteAdoptada,
                       longitud: Optional[float] = None) -> str:
    """
    El AVISO de una pendiente que gobierna un extremo de la banda adoptada, o
    "" si el origen es el cauce o la declaracion (Sec. 7.B; T-6).

    Una pendiente declarada no avisa aqui: es una decision del expediente y
    la juzgan V10 (banda) y V2b (frente al cauce), cada una en su fila. Con
    `longitud` el aviso lleva el desnivel en metros; sin ella, la expresion.
    """
    if pendiente.origen not in (OrigenPendiente.MINIMA, OrigenPendiente.MAXIMA):
        return ""
    desnivel = (None if longitud is None
                else desnivel_frente_al_cauce(pendiente, longitud))
    if pendiente.origen is OrigenPendiente.MAXIMA:
        cuanto = ("(S_cauce - S_conducto) x L" if desnivel is None
                  else f"{desnivel:.2f} m en este punto")
        return (
            f"pendiente del conducto limitada al maximo adoptado "
            f"({pendiente.valor:g} m/m, criterio "
            f"'{CRITERIO_PENDIENTE_MAXIMA}'): la del cauce es "
            f"{pendiente.S_cauce:g} m/m. El conducto queda mas tendido que "
            f"su cauce y el desnivel que el barril no baja, {cuanto}, "
            "requiere una estructura de caida o de disipacion en un extremo "
            "que este calculo no dimensiona; V2b juzga la sedimentacion "
            f"segun '{CRITERIO_REGIMEN_V2B}'")
    cuanto = ("(S_conducto - S_cauce) x L" if desnivel is None
              else f"{-desnivel:.2f} m en este punto")
    return (
        f"pendiente del conducto elevada al minimo adoptado "
        f"({pendiente.valor:g} m/m, criterio "
        f"'{CRITERIO_PENDIENTE_MINIMA}'): la del cauce es "
        f"{pendiente.S_cauce:g} m/m. El conducto cae mas que su cauce y la "
        f"salida queda {cuanto} por debajo del cauce natural; G2 la juzga "
        "contra el fondo del receptor")


def _pendiente_del_diseno(punto: PuntoCritico, S: float) -> PendienteAdoptada:
    """
    El origen de una pendiente que llega ya resuelta en el resultado
    hidraulico, cuando quien llama a 7.B no trae el `PendienteAdoptada`.

    No vuelve a elegir: `S` es la del diseño. Solo la rotula comparandola con
    lo que `pendiente_adoptada` resolveria sin declaracion; si coincide tiene
    ese origen, y si no, fue declarada.
    """
    if punto.S_cauce is not None:
        sin_declarar = pendiente_adoptada(punto)
        if abs(sin_declarar.valor - S) <= TOL_UMBRAL_NORMATIVO:
            return sin_declarar
    return pendiente_adoptada(punto, S_declarada=S)


def paso_pendiente(pendiente: PendienteAdoptada):
    """El `PasoDeMemoria` 7.B.1: la pendiente adoptada y de donde sale."""
    sustitucion = []
    if pendiente.S_cauce is not None:
        sustitucion.append(Magnitud(
            "S_cauce", pendiente.S_cauce, "m/m",
            "pendiente del cauce natural en el cruce (columna del CSV o dato "
            "de tablero)", cifras=CIFRAS_FINA))
    if pendiente.S_declarada is not None:
        sustitucion.append(Magnitud(
            "S_conducto declarada", pendiente.S_declarada, "m/m",
            "dato externo `S_conducto` del punto", cifras=CIFRAS_FINA))
    for simbolo, valor, clave in (
            ("S_minima", pendiente.S_minima, CRITERIO_PENDIENTE_MINIMA),
            ("S_maxima", pendiente.S_maxima, CRITERIO_PENDIENTE_MAXIMA)):
        if valor is not None:
            sustitucion.append(Magnitud(
                simbolo, valor, "m/m", f"criterio '{clave}' [A]",
                cifras=CIFRAS_FINA))
    formula = {
        OrigenPendiente.CAUCE: "S_conducto = S_cauce",
        OrigenPendiente.DECLARADA: "S_conducto = S declarada para el punto",
        OrigenPendiente.MINIMA: "S_conducto = S_minima  (S_cauce < S_minima)",
        OrigenPendiente.MAXIMA: "S_conducto = S_maxima  (S_cauce > S_maxima)",
    }[pendiente.origen]
    aviso = aviso_de_pendiente(pendiente)
    return paso(
        "F7.PENDIENTE",
        codigo="7.B.1",
        que="Pendiente adoptada del conducto",
        formula=formula,
        formula_cita_id="MC_HHD.4.1.1.3.3",
        citas_textuales=("MC_HHD.4.1.1.3.3", "HDS5_3ED.5.3.3#ALINEADO"),
        sustitucion=tuple(sustitucion),
        resultado=Magnitud("S_conducto", pendiente.valor, "m/m",
                           pendiente.procedencia, cifras=CIFRAS_FINA),
        elecciones=(EleccionDeProyecto(
            que_se_adopto="origen de la pendiente del conducto",
            valor=pendiente.origen.value,
            entre=tuple(o.value for o in OrigenPendiente),
            de_donde="la regla de la Sec. 7.B (el conducto sigue al cauce), "
                     "la declaracion del punto y los limites de pendiente "
                     "adoptados por el proyecto",
            por_que=pendiente.procedencia),),
        nota_del_proyecto=(
            "La fuente exige cuidar la pendiente y no da cifra: ni minima, "
            "ni maxima. Es la MISMA pendiente con que corre el diseño "
            "hidraulico (Fase 4), el TW por cota y la caida de 7.B."
            + (" La banda (S_minima, S_maxima) es la de V10, leida una "
               "sola vez: aqui acota la pendiente del CAUCE, y V10 juzga la "
               "pendiente con que corrio el diseño."
               if pendiente.origen is not OrigenPendiente.DECLARADA else
               " La pendiente DECLARADA no se acota aqui: V10 la juzga "
               "contra la banda adoptada y V2b contra la del cauce.")
            + (f" AVISO: {aviso}." if aviso else "")),
    )


def _procedencia_de_la_entrada(entrada) -> str:
    """
    De donde sale la cota de entrada, en una linea: la procedencia completa
    ya la imprime el paso G1 y el parrafo de la Fase 7, y repetirla entera en
    cada sustitucion engorda la memoria sin decir nada nuevo.
    """
    if entrada.medida:
        return "MEDIDA: columna cota_fondo_entrada del CSV"
    return (f"ADOPTADA: regla '{entrada.regla}' del criterio "
            "'origen_cota_fondo_entrada' [A], no medida")


def _metodo_longitud() -> MetodoLongitud:
    """
    El metodo declarado en 'metodo_longitud_conducto', validado como segunda
    linea (la puerta ya rechaza lo que no esta en la ventana; forma MAT-D13).
    """
    metodo = ca.valor(CRITERIO_METODO_LONGITUD)
    if not (isinstance(metodo, str) and metodo in METODOS_DE_LONGITUD):
        raise DatoInvalidoError(
            CRITERIO_METODO_LONGITUD, valor=metodo,
            motivo=f"'{CRITERIO_METODO_LONGITUD}' vale {metodo!r} y las "
                   f"unicas opciones son "
                   f"{', '.join(map(repr, METODOS_DE_LONGITUD))}")
    return MetodoLongitud(metodo)


def _paso_factor(punto: PuntoCritico, factor: float):
    """El `PasoDeMemoria` 7.B.2: el factor de esviaje."""
    return paso(
        "F7.ESVIAJE",
        codigo="7.B.2",
        que="Factor de esviaje del cruce",
        formula="factor = 1 / cos(esviaje)",
        formula_cita_id="HDS5_3ED.5.4.1#ESVIAJE",
        citas_textuales=("HDS5_3ED.5.4.1#ESVIAJE", "MC_HHD.4.1.1.3.2"),
        sustitucion=(Magnitud(
            "esviaje", punto.esviaje_grados, "grados",
            "columna esviaje_grados del CSV: angulo entre el eje del "
            "conducto y la NORMAL al eje de la via (0 = cruce perpendicular)",
            cifras=CIFRAS_MAGNITUD),),
        resultado=Magnitud(
            "factor", factor, "-",
            "identidad geometrica del cruce oblicuo: el eje del conducto es "
            "la hipotenusa del ancho que atraviesa", cifras=CIFRAS_FINA),
    )


def _eleccion_de_metodo(metodo: MetodoLongitud) -> EleccionDeProyecto:
    return EleccionDeProyecto(
        que_se_adopto="metodo de calculo de la longitud del conducto",
        valor=metodo.value,
        entre=tuple(str(v) for v in
                    ca.criterio(CRITERIO_METODO_LONGITUD).sensibilidad),
        de_donde=f"el criterio '{CRITERIO_METODO_LONGITUD}' [A]",
        por_que=("la fuente describe superponer el conducto a la seccion "
                 "transversal del cruce, con un talud a cada lado y la "
                 "salida mas baja que la entrada; que cada talud baje hasta "
                 "el FONDO -- como si el barril no tuviera altura -- es "
                 "eleccion del proyecto, porque la seccion aun no se conoce, "
                 "y da la cota superior de la longitud"
                 if metodo is MetodoLongitud.POR_EXTREMO else
                 "los dos taludes bajan la altura del eje (rasante - "
                 "terreno): es la formula anterior a T-6, caso particular "
                 "del metodo por extremo"),
        clave_criterio=CRITERIO_METODO_LONGITUD)


def _exigir_dato_transversal(clave: str, valor: Optional[float],
                             punto: PuntoCritico) -> float:
    """
    Bombeo o peralte como numero valido. None es «no declarado» y vale 0.

    Es la SEGUNDA linea: `servicio._numero_externo` ya valida lo que entra
    por el JSON, pero esta funcion la alcanza tambien quien llama a M7
    directamente (medido por el auditor de T-6: bombeo = -0.5 daba 28.93 m de
    conducto sin excepcion). Finito, en m/m -- un valor absoluto >= 1 delata
    un porcentaje, el mismo techo de escritura de las pendientes -- y, para
    el bombeo, no negativo: un bombeo negativo no existe; una plataforma que
    sube hacia un borde y baja hacia el otro es un peralte.
    """
    if valor is None:
        return 0.0      # plataforma horizontal: el caso particular
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) \
            or not math.isfinite(valor):
        raise DatoInvalidoError(
            clave, valor=valor, id_punto=punto.id,
            motivo="la pendiente transversal de la plataforma es un numero "
                   "finito en m/m (0.02 = 2 %)")
    if not abs(valor) < S_CAUCE_MAX:
        raise DatoInvalidoError(
            clave, valor=valor, id_punto=punto.id,
            motivo="una pendiente transversal en m/m (0.02 = 2 %): un valor "
                   f"absoluto >= {S_CAUCE_MAX} delata un dato en PORCENTAJE")
    if clave == "bombeo" and not valor >= 0:
        raise DatoInvalidoError(
            clave, valor=valor, id_punto=punto.id,
            motivo="el bombeo es una pendiente transversal no negativa (baja "
                   "los dos bordes de la plataforma); si un borde sube y el "
                   "otro baja, el dato es `peralte`, que si lleva signo")
    return float(valor)


def exigir_transversales_compatibles(bombeo: Optional[float],
                                     peralte: Optional[float],
                                     id_punto: Optional[str] = None) -> None:
    """
    `bombeo` y `peralte` son EXCLUYENTES en un mismo punto.

    Una seccion transversal tiene bombeo O peralte: el DG-2018 pide el bombeo
    «en tramos en tangente o en curvas en contraperalte» (num. 304.05, pag.
    impresa 195) y define el peralte como la inclinacion de la carretera «en
    los tramos de curva» (num. 304.06, pag. impresa 196). Una plataforma
    peraltada tiene una sola agua. Sumarlos -- lo que el calculo hacia hasta
    la auditoria de T-6: A-01 con bombeo 0.02 y peralte 0.04 daba 18.467 m
    donde el peralte solo da 18.869 -- baja los dos bordes de una seccion que
    ya no tiene bombeo. `DatoInvalidoError` que nombra el PAR: el revisor
    tiene que corregir uno de los dos. Un valor declarado en cero no cuenta:
    `bombeo = 0` junto a un peralte es la forma de decir «aqui no hay bombeo»
    cuando el bombeo viene declarado para todos los puntos.
    """
    hay_bombeo = bombeo is not None and abs(bombeo) > 0
    hay_peralte = peralte is not None and abs(peralte) > 0
    if hay_bombeo and hay_peralte:
        raise DatoInvalidoError(
            "bombeo y peralte", valor=(bombeo, peralte), id_punto=id_punto,
            motivo=f"el punto declara a la vez bombeo ({bombeo!r}) y peralte "
                   f"({peralte!r}), y una seccion transversal tiene uno u "
                   "otro: bombeo en tangente (DG-2018 num. 304.05), peralte "
                   "en curva (num. 304.06). Si el bombeo viene declarado "
                   "para todos los puntos, el punto en curva lo anula "
                   "declarando `bombeo` = 0 junto a su `peralte`")


def _transversales_validas(punto: PuntoCritico, bombeo: Optional[float],
                           peralte: Optional[float]) -> Tuple[float, float]:
    """(bombeo, peralte) validados y compatibles; None vale 0."""
    b = _exigir_dato_transversal("bombeo", bombeo, punto)
    pe = _exigir_dato_transversal("peralte", peralte, punto)
    exigir_transversales_compatibles(bombeo, peralte, punto.id)
    return b, pe


def _aviso_transversal_descartada(bombeo: Optional[float],
                                  peralte: Optional[float],
                                  motivo: str) -> Tuple[str, ...]:
    """
    El aviso de una pendiente transversal DECLARADA que el calculo no usa. Un
    dato del expediente que se descarta sin decirlo deja a quien lo escribio
    mirando una longitud calculada con otra seccion.
    """
    declarados = [f"{nombre} = {valor:g}"
                  for nombre, valor in (("bombeo", bombeo), ("peralte", peralte))
                  if valor is not None]
    if not declarados:
        return ()
    return (f"pendiente transversal declarada y NO aplicada "
            f"({', '.join(declarados)}): {motivo}",)


def longitud_del_conducto(punto: PuntoCritico, *,
                          pendiente: Optional[PendienteAdoptada] = None,
                          bombeo: Optional[float] = None,
                          peralte: Optional[float] = None
                          ) -> LongitudConducto:
    """
    Longitud del conducto de Sec. 7.B, con el metodo declarado en
    'metodo_longitud_conducto' [A] y los pasos que la explican.

    POR EXTREMO (HDS-5 3a ed., num. 2.2.4 b. y Figura 2.4, pag. impresa 2.8):
    el conducto se superpone a la seccion transversal DEL CRUCE (esviada). A
    cada lado, el talud del terraplen baja desde el borde de la plataforma
    hasta el fondo del conducto en ese extremo:

        proyeccion_entrada = talud * (cota_borde_entrada - cota_entrada)
        proyeccion_salida  = talud * (cota_borde_salida - cota_salida)
        cota_salida        = cota_entrada - S * L
        L * cos(esviaje)   = ancho + proyeccion_entrada + proyeccion_salida

    y despejando L, que aparece en los dos miembros:

        L = [ancho + talud * (H_entrada + H_salida0)]
            / [cos(esviaje) - talud * S]

    con H_entrada = cota_borde_entrada - cota_entrada y H_salida0 =
    cota_borde_salida - cota_entrada (la altura del borde de salida sobre el
    fondo de la ENTRADA; la caida esta en el denominador). El borde de la
    plataforma es la rasante del eje, corregida cuando la seccion tipica lo
    da (datos externos opcionales, DG-2018 num. 304.05 y 304.06):

        cota_borde_entrada = cota_rasante + (peralte - bombeo) * ancho / 2
        cota_borde_salida  = cota_rasante - (peralte + bombeo) * ancho / 2

    `bombeo` >= 0 baja los dos bordes; `peralte` > 0 sube el de la entrada y
    baja el de la salida (giro alrededor del eje), de modo que no cambia la
    suma de las dos proyecciones -- ni L -- y si lo que cada talud recorre.

    MEDIR AL FONDO ES ELECCION DEL PROYECTO, NO DE LA FUENTE. El HDS-5
    describe superponer el barril ESTIMADO a la seccion transversal y llama
    aproximada a la longitud que resulta (num. 2.2.4 b.); su Figura 2.4
    dibuja los taludes muriendo en la cara SUPERIOR del barril, y la Lamina
    N 01 a) del Manual del MTC, en la coronacion de los cabezales. Aqui el
    talud baja hasta el fondo -- un barril de altura cero -- porque esta
    longitud se necesita ANTES de conocer la seccion (num. 3.1.4, pag.
    impresa 3.9: «an approximation of barrel length is usually necessary to
    begin the design process»). Es la COTA SUPERIOR de la longitud, y no es
    el lado seguro por construccion: alargar el conducto suma friccion y
    resta caida, y con la pendiente de A-01 el HW de salida BAJA (0.9925 m
    con la longitud al fondo, 1.0002 m con la longitud a la clave). La
    longitud a la clave de la seccion adoptada la da `longitud_a_la_clave`,
    despues del diseño.

    CON EL FONDO DE ENTRADA ADOPTADO IGUAL AL TERRENO hay un sesgo que el paso
    declara: 'cota_terreno' es la cota del terreno EN EL EJE, y este metodo
    ancla ahi la ENTRADA y carga toda la caida aguas abajo. Con
    `cota_fondo_entrada` medida en el cauce es exacto.

    TERRAPLEN SIMETRICO: L = (ancho + 2 * talud * H_eje) / cos(esviaje), con
    H_eje = cota de rasante - cota de TERRENO. Es la formula anterior a T-6 y
    el caso particular de la de arriba con el fondo de entrada en el
    terreno, sin bombeo y sin la caida en la proyeccion de salida. No lee la
    pendiente ni los datos transversales.

    `pendiente` es la que resolvio `pendiente_adoptada`; si no se pasa y el
    metodo la necesita, se resuelve aqui con esa misma funcion.

    Excepciones: `CriterioPendienteError` ('talud_terraplen', el metodo, o
    la regla de la cota de entrada); `DatoFaltanteError('S_cauce')`;
    `DatoInvalidoError` si un borde de la plataforma queda a la cota del
    fondo o por debajo, o si talud * S alcanza a cos(esviaje) -- el talud no
    llegaria nunca a encontrar un conducto que baja mas rapido que el --;
    `LimiteNumericoError` en las guardias de salida (SIS-G-01, PC-32).
    """
    metodo = _metodo_longitud()
    talud = ca.valor(CRITERIO_TALUD)
    factor = factor_esviaje(punto)
    ancho = punto.ancho_plataforma
    eleccion = _eleccion_de_metodo(metodo)

    if metodo is MetodoLongitud.TERRAPLEN_SIMETRICO:
        _transversales_validas(punto, bombeo, peralte)
        descartada = _aviso_transversal_descartada(
            bombeo, peralte,
            "el metodo terraplen_simetrico toma la plataforma horizontal y "
            "no lee el bombeo ni el peralte")
        altura = altura_terraplen(punto)
        proyeccion = proyeccion_taludes(punto)
        longitud = _exigir_finito("longitud_conducto",
                                  (ancho + proyeccion) * factor, punto)
        paso_longitud = paso(
            "F7.LONGITUD",
            codigo="7.B.3",
            que="Longitud del conducto (terraplen simetrico)",
            formula="L = (ancho + 2 * talud * H_eje) * factor",
            formula_cita_id="HDS5_3ED.2.2.4#LONGITUD",
            citas_textuales=("HDS5_3ED.2.2.4#LONGITUD",
                             "DG2018.304.10#T304.11"),
            sustitucion=(
                Magnitud("ancho", ancho, "m",
                         "columna ancho_plataforma del CSV",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("talud", talud, "H:V",
                         f"criterio '{CRITERIO_TALUD}' [A]",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("H_eje", altura, "m",
                         "cota de rasante - cota de terreno del CSV: la "
                         "MISMA altura para los dos taludes",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("factor", factor, "-", "paso 7.B.2",
                         cifras=CIFRAS_FINA)),
            resultado=Magnitud("L", longitud, "m",
                               "longitud APROXIMADA del conducto para el "
                               "diseño hidraulico y para 7.B",
                               cifras=CIFRAS_MAGNITUD),
            elecciones=(eleccion,),
            nota_del_proyecto=(
                "Caso particular del metodo por extremo: supone el fondo de "
                "la entrada en el terreno del eje, la plataforma horizontal "
                "y la misma altura de talud en la salida que en la entrada, "
                "aunque la salida quede S*L mas baja. No usa la cota de "
                "fondo medida ni el bombeo o el peralte aunque se declaren."
                + "".join(f" AVISO: {a}." for a in descartada)),
        )
        semi = longitud / 2
        return LongitudConducto(
            longitud=longitud, metodo=metodo, factor_esviaje=factor,
            talud=talud, S=None, bombeo=None, peralte=None,
            cota_borde_entrada=punto.cota_rasante,
            cota_borde_salida=punto.cota_rasante,
            cota_referencia_entrada=punto.cota_terreno,
            cota_referencia_salida=punto.cota_terreno,
            altura_entrada=altura, altura_salida=altura,
            proyeccion_entrada=proyeccion / 2,
            proyeccion_salida=proyeccion / 2,
            proyeccion_taludes=proyeccion,
            semilongitud_entrada=semi, semilongitud_salida=semi,
            pasos=(_paso_factor(punto, factor), paso_longitud),
            avisos=descartada)

    # --- por extremo --------------------------------------------------------
    if pendiente is None:
        pendiente = pendiente_adoptada(punto)
    S = pendiente.valor
    b, pe = _transversales_validas(punto, bombeo, peralte)
    entrada = cota_de_entrada(punto)
    semiancho = ancho / 2
    borde_e = punto.cota_rasante + (pe - b) * semiancho
    borde_s = punto.cota_rasante - (pe + b) * semiancho
    H_e = _exigir_finito("altura_terraplen", borde_e - entrada.valor, punto)
    H_s0 = _exigir_finito("altura_terraplen", borde_s - entrada.valor, punto)
    coseno = 1.0 / factor
    denominador = coseno - talud * S
    if not denominador > 0:
        # EL ERROR ES DEL PAR, no de la pendiente sola: el mismo S tiene
        # longitud con un esviaje menor. El campo y el motivo nombran los dos.
        raise DatoInvalidoError(
            "esviaje_grados y S_conducto",
            valor=(punto.esviaje_grados, S), id_punto=punto.id,
            motivo=f"con talud {talud!r} H:V y esviaje "
                   f"{punto.esviaje_grados!r} grados, la pendiente del "
                   f"conducto ({S!r}) hace talud*S = {talud * S!r} >= "
                   f"cos(esviaje) = {coseno!r}: el conducto baja mas rapido "
                   "que el talud visto sobre su eje y el talud de salida no "
                   "lo alcanza nunca. La longitud de 7.B no esta definida "
                   "con este par (esviaje, pendiente) para ese talud: o el "
                   "esviaje es menor, o la pendiente lo es")
    if not denominador > COS_ESVIAJE_MIN:
        raise LimiteNumericoError(
            "longitud_conducto", valor=denominador, id_punto=punto.id,
            motivo=f"cos(esviaje) - talud*S = {denominador!r} queda por "
                   f"debajo de COS_ESVIAJE_MIN = {COS_ESVIAJE_MIN!r} "
                   "(tolerancias.py): la diferencia entre el coseno y "
                   "talud*S ya no esta determinada en doble precision y la "
                   "longitud de 7.B tampoco")
    # La guarda INTERNA nombra la magnitud que desborda de verdad (SIS-G-01):
    # el producto del talud por las alturas, antes que la longitud que lo
    # contiene.
    proyeccion_sin_caida = _exigir_finito("proyeccion_taludes",
                                          talud * (H_e + H_s0), punto)
    longitud = _exigir_finito(
        "longitud_conducto",
        (ancho + proyeccion_sin_caida) / denominador, punto)
    caida = S * longitud
    H_s = H_s0 + caida
    for lado, altura, borde in (("entrada", H_e, borde_e),
                                ("salida", H_s, borde_s)):
        if not altura > TOL_UMBRAL_NORMATIVO:
            raise DatoInvalidoError(
                "cota_rasante", valor=punto.cota_rasante, id_punto=punto.id,
                motivo=f"el borde de la plataforma del lado de la {lado} "
                       f"({borde:.3f} msnm, con bombeo {b!r} y peralte "
                       f"{pe!r}) no queda por encima del fondo del conducto "
                       f"en ese extremo ({altura:+.3f} m): no hay talud de "
                       "terraplen que proyectar")
    proy_e = talud * H_e
    proy_s = talud * H_s
    proyeccion = _exigir_finito("proyeccion_taludes", proy_e + proy_s, punto)
    # EL SESGO DEL FONDO ADOPTADO, dicho con su numero (auditor de T-6).
    # 'cota_terreno' es el terreno EN EL EJE (docs/contrato_entradas.md). Con
    # el fondo adoptado igual a ella, este metodo pone esa cota en la ENTRADA
    # y carga toda la caida aguas abajo; un lecho de pendiente S que pasara
    # por esa cota en el eje tendria la entrada mas alta y daria la longitud
    # de abajo. No se cambia el calculo -- el perfil adoptado ya tenia ese
    # sesgo en la cota de salida, y con el fondo MEDIDO es exacto --: se dice.
    nota_del_eje = ""
    if entrada.aviso:
        L_por_el_eje = ((semiancho + talud * H_e) / (coseno + talud * S)
                        + (semiancho + talud * H_s0) / denominador)
        nota_del_eje = (
            " El fondo de la entrada es ADOPTADO igual al terreno, que es la "
            "cota del terreno en el EJE de la via: el metodo ancla ahi la "
            "entrada y carga toda la caida aguas abajo. Para un lecho de "
            "pendiente S que pasara por esa cota en el eje la longitud seria "
            f"{L_por_el_eje:.3f} m ({longitud - L_por_el_eje:+.3f} m de "
            "diferencia), que desaparece al medir `cota_fondo_entrada` en el "
            "cauce.")
    # LA PLATAFORMA HORIZONTAL SE AVISA: sin bombeo ni peralte declarados los
    # dos bordes se toman a la cota de rasante, y el bombeo que toda calzada
    # tiene (DG-2018 num. 304.05) acorta la longitud. La sensibilidad se da
    # por punto: talud * ancho / (cos - talud*S) metros por unidad de
    # pendiente transversal, que son los mismos centimetros por cada 1 %.
    # EL AVISO DEL FONDO ADOPTADO VIAJA CON LA LONGITUD QUE LO CONSUMIO: este
    # metodo ancla los dos taludes al fondo de la entrada, y si ese fondo es
    # el terreno del eje la longitud lo hereda. Va aqui y no solo en 7.B para
    # que lo lleve tambien el punto que no dimensiona, cuya longitud ya entro
    # al control de salida de cada escalon (`InformePunto.avisos`).
    avisos: Tuple[str, ...] = (entrada.aviso,) if entrada.aviso else ()
    if bombeo is None and peralte is None:
        avisos += (
            "plataforma tomada horizontal: no se declaro `bombeo` ni "
            "`peralte`. Declarar el bombeo de la seccion tipica: cada 1 % "
            f"acorta la longitud {talud * ancho / denominador:.1f} cm en "
            "este punto",)
    # Lo que la formula anterior a T-6 daria con los mismos datos: se imprime
    # junto al resultado para que la diferencia se vea (y se pueda defender).
    L_simetrica = (ancho + 2 * talud * (punto.cota_rasante
                                        - punto.cota_terreno)) * factor
    sustitucion = [
        Magnitud("ancho", ancho, "m", "columna ancho_plataforma del CSV",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("talud", talud, "H:V", f"criterio '{CRITERIO_TALUD}' [A]",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("cota_entrada", entrada.valor, "msnm",
                 _procedencia_de_la_entrada(entrada),
                 cifras=CIFRAS_MAGNITUD),
    ]
    if bombeo is not None:
        sustitucion.append(Magnitud(
            "bombeo", b, "m/m", "dato externo `bombeo` (seccion tipica; "
            "DG-2018 num. 304.05)", cifras=CIFRAS_FINA))
    if peralte is not None:
        sustitucion.append(Magnitud(
            "peralte", pe, "m/m", "dato externo `peralte` (seccion tipica; "
            "DG-2018 num. 304.06): positivo sube el borde de la entrada",
            cifras=CIFRAS_FINA))
    procedencia_borde = (
        "cota de rasante, corregida por la pendiente transversal declarada "
        "sobre medio ancho"
        if bombeo is not None or peralte is not None else
        "cota de rasante: plataforma horizontal, sin bombeo ni peralte "
        "declarados")
    sustitucion += [
        Magnitud("cota_borde_entrada", borde_e, "msnm", procedencia_borde,
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("cota_borde_salida", borde_s, "msnm", procedencia_borde,
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("H_entrada", H_e, "m",
                 "cota_borde_entrada - cota_entrada", cifras=CIFRAS_MAGNITUD),
        Magnitud("H_salida0", H_s0, "m",
                 "cota_borde_salida - cota_entrada; la caida S*L hasta el "
                 "fondo de la salida esta en el denominador",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("cos(esviaje)", coseno, "-", "1 / factor del paso 7.B.2",
                 cifras=CIFRAS_FINA),
        Magnitud("S", S, "m/m", "pendiente adoptada del conducto "
                 f"(origen: {pendiente.origen.value})", cifras=CIFRAS_FINA),
    ]
    paso_longitud = paso(
        "F7.LONGITUD",
        codigo="7.B.3",
        que="Longitud del conducto (por extremo)",
        formula="L = [ancho + talud * (H_entrada + H_salida0)] "
                "/ [cos(esviaje) - talud * S]",
        formula_cita_id="HDS5_3ED.2.2.4#LONGITUD",
        citas_textuales=("HDS5_3ED.2.2.4#LONGITUD", "HDS5_3ED.3.1.4#LONGITUD",
                         "DG2018.304.10#T304.11")
        + (("DG2018.304.05#BOMBEO",) if bombeo is not None else ())
        + (("DG2018.304.06#PERALTE",) if peralte is not None else ()),
        sustitucion=tuple(sustitucion),
        resultado=Magnitud("L", longitud, "m",
                           "longitud APROXIMADA del conducto, medida al "
                           "fondo en cada extremo: la del diseño hidraulico "
                           "y la de 7.B", cifras=CIFRAS_MAGNITUD),
        elecciones=(eleccion,),
        nota_del_proyecto=(
            "La fuente describe superponer el barril estimado a la seccion "
            "transversal del cruce y llama aproximada a la longitud que "
            "resulta; la expresion cerrada es su algebra y la hace el "
            "proyecto. Que el talud baje hasta el FONDO es eleccion del "
            "proyecto (la seccion aun no se conoce): da la cota superior de "
            "la longitud, y no es el lado seguro por construccion, porque "
            "alargar el conducto suma friccion y resta caida. El talud de la "
            f"entrada proyecta {proy_e:.3f} m y el de la salida "
            f"{proy_s:.3f} m (la salida queda {caida:.3f} m mas baja). Con "
            "el metodo del terraplen simetrico -- la formula anterior, caso "
            f"particular de esta -- la longitud seria {L_simetrica:.3f} m."
            + nota_del_eje
            + "".join(f" AVISO: {a}." for a in avisos)),
    )
    semi_e = (semiancho + proy_e) * factor
    return LongitudConducto(
        longitud=longitud, metodo=metodo, factor_esviaje=factor,
        talud=talud, S=S, bombeo=bombeo, peralte=peralte,
        cota_borde_entrada=borde_e, cota_borde_salida=borde_s,
        cota_referencia_entrada=entrada.valor,
        cota_referencia_salida=entrada.valor - caida,
        altura_entrada=H_e, altura_salida=H_s,
        proyeccion_entrada=proy_e, proyeccion_salida=proy_s,
        proyeccion_taludes=proyeccion,
        semilongitud_entrada=semi_e,
        semilongitud_salida=longitud - semi_e,
        pasos=(_paso_factor(punto, factor), paso_longitud),
        avisos=avisos)


def longitud_declarada(punto: PuntoCritico, longitud: float,
                       origen: str = "dato externo `longitud_m`", *,
                       bombeo: Optional[float] = None,
                       peralte: Optional[float] = None
                       ) -> LongitudConducto:
    """
    La longitud que el expediente DECLARA (`longitud_m`), envuelta en el
    mismo tipo que la calculada para que 7.B y la memoria digan de donde
    salio. No calcula: la proyeccion de taludes es la que esa longitud
    IMPLICA, no un calculo independiente.

    `bombeo` y `peralte`, si el punto los declara, se validan igual y NO se
    usan: una longitud declarada ya trae dentro la seccion con que se midio.
    Que se descartan lo dicen el paso y un aviso.
    """
    _transversales_validas(punto, bombeo, peralte)
    descartada = _aviso_transversal_descartada(
        bombeo, peralte,
        "la longitud del punto es DECLARADA (`longitud_m`) y no se calcula")
    factor = factor_esviaje(punto)
    proyeccion = longitud / factor - punto.ancho_plataforma
    paso_longitud = paso(
        "F7.LONGITUD",
        codigo="7.B.3",
        que="Longitud del conducto (declarada)",
        formula="L = longitud declarada por el expediente",
        formula_cita_id="HDS5_3ED.2.2.4#LONGITUD",
        citas_textuales=("HDS5_3ED.2.2.4#LONGITUD",),
        sustitucion=(
            Magnitud("longitud_m", longitud, "m", origen,
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("factor", factor, "-", "paso 7.B.2",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("L", longitud, "m",
                           "longitud DECLARADA: no la calcula este modulo",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            "Un dato medido sobre la seccion transversal no se sustituye por "
            "un metodo: 'metodo_longitud_conducto' no se aplica en este "
            f"punto. Esta longitud implica {proyeccion:.3f} m de proyeccion "
            "de taludes (L / factor - ancho de plataforma)."
            + "".join(f" AVISO: {a}." for a in descartada)),
    )
    return LongitudConducto(
        longitud=longitud, metodo=MetodoLongitud.DECLARADA,
        factor_esviaje=factor, talud=None, S=None, bombeo=None, peralte=None,
        cota_borde_entrada=None, cota_borde_salida=None,
        cota_referencia_entrada=None, cota_referencia_salida=None,
        altura_entrada=None, altura_salida=None,
        proyeccion_entrada=None, proyeccion_salida=None,
        proyeccion_taludes=proyeccion,
        semilongitud_entrada=None, semilongitud_salida=None,
        pasos=(_paso_factor(punto, factor), paso_longitud),
        avisos=descartada)


def longitud_conducto(punto: PuntoCritico, *,
                      pendiente: Optional[PendienteAdoptada] = None,
                      bombeo: Optional[float] = None,
                      peralte: Optional[float] = None) -> float:
    """
    Longitud del conducto, m (Sec. 7.B): el escalar de
    `longitud_del_conducto`, que es quien la calcula con el metodo declarado
    en 'metodo_longitud_conducto' [A] y emite sus pasos. Se conserva para los
    consumidores que solo necesitan el numero.

    Se detiene con CriterioPendienteError mientras 'talud_terraplen' siga
    vacio (ver `proyeccion_taludes`).
    """
    return longitud_del_conducto(punto, pendiente=pendiente, bombeo=bombeo,
                                 peralte=peralte).longitud


def _clave_sobre_el_fondo(punto: PuntoCritico, material: Material,
                          seccion: Seccion) -> float:
    """
    Altura de la clave FISICA sobre el fondo de la entrada, m.

    No se recalcula aqui: es `M5.cota_clave` menos la cota de entrada, la
    MISMA clave que usan 7.A y V7 (MAT-D4). Si la definicion de la clave
    cambia para una forma -- el marco con su espesor de losa --, el encaje la
    hereda sin tocar este modulo.
    """
    return (cota_clave(punto=punto, material=material, seccion=seccion)
            - cota_de_entrada(punto).valor)


def longitud_a_la_clave(*, punto: PuntoCritico, material: Material,
                        seccion: Seccion,
                        longitud: LongitudConducto) -> Optional[float]:
    """
    Longitud entre cabezales con el talud muriendo en la CLAVE exterior de
    la seccion adoptada en cada extremo, m. None cuando no aplica.

    Es el ENCAJE que el HDS-5 manda hacer despues del diseño (num. 3.3.5,
    pag. impresa 3.25: «Once the barrel is selected it must be fitted into
    the roadway cross section ... the length should be close to the
    approximate length, and the headwalls and wingwalls must be
    dimensioned»). Con muro de cabecera el talud no baja hasta el fondo sino
    hasta la coronacion del muro, que como minimo esta a la clave exterior:

        c = cota de clave - cota de entrada        (la clave FISICA, MAT-D4:
                                                    altura interior + pared)
        L_clave = [ancho + talud * (H_entrada + H_salida0 - 2 c)]
                  / [cos(esviaje) - talud * S]

    Es la COTA SUPERIOR de la longitud entre cabezales (la clave es el
    minimo de la coronacion del muro, y un cabezal mas alto que la clave
    acorta mas: 0.30 m sobre la clave en A-01 dan 13.42 m contra 14.68) y NO
    sustituye a la longitud del diseño: la
    friccion, la caida y la cota de salida se quedan con la aproximada, que
    es la que uso la Fase 4. La definitiva -- que es la de construccion y
    metrado -- la fija el cabezal por punto, cuando exista su coronacion.

    Solo aplica al metodo por extremo: en el terraplen simetrico la
    referencia es el terreno y no el conducto, y una longitud declarada no
    se recalcula.
    """
    if longitud.metodo is not MetodoLongitud.POR_EXTREMO:
        return None
    c = _clave_sobre_el_fondo(punto, material, seccion)
    denominador = 1.0 / longitud.factor_esviaje - longitud.talud * longitud.S
    H0 = (longitud.altura_entrada
          + (longitud.cota_borde_salida - longitud.cota_referencia_entrada))
    return _exigir_finito(
        "longitud_conducto",
        (punto.ancho_plataforma + longitud.talud * (H0 - 2 * c))
        / denominador, punto)


def _paso_encaje(*, punto: PuntoCritico, material: Material,
                 seccion: Seccion,
                 longitud: LongitudConducto, L_clave: float):
    """El `PasoDeMemoria` 7.B.5: la seccion adoptada encajada en el cruce."""
    c = _clave_sobre_el_fondo(punto, material, seccion)
    diferencia = longitud.longitud - L_clave
    return paso(
        "F7.ENCAJE",
        codigo="7.B.5",
        que="Encaje de la seccion adoptada: longitud entre cabezales a la "
            "clave",
        formula="L_clave = [ancho + talud * (H_entrada + H_salida0 - 2 * c)] "
                "/ [cos(esviaje) - talud * S],  c = altura interior + "
                "espesor de pared",
        formula_cita_id="HDS5_3ED.3.3.5#ENCAJE",
        citas_textuales=("HDS5_3ED.3.3.5#ENCAJE", "HDS5_3ED.3.1.4#LONGITUD"),
        sustitucion=(
            Magnitud("c", c, "m",
                     f"altura interior de la seccion adoptada "
                     f"({seccion.etiqueta()}) mas el espesor de pared: la "
                     "clave EXTERIOR sobre el fondo", cifras=CIFRAS_MAGNITUD),
            Magnitud("L", longitud.longitud, "m",
                     "longitud aproximada del paso 7.B.3, medida al fondo",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("L_clave", L_clave, "m",
                           "longitud entre cabezales si el talud muere en la "
                           "clave exterior en los dos extremos",
                           cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=(
            f"La longitud a la clave es {diferencia:.3f} m menor que la "
            f"aproximada ({diferencia / longitud.longitud:.1%}). La fuente "
            "pide que la longitud real quede «close to the approximate "
            "length» y no da tolerancia: el proyecto no inventa una y deja "
            "las dos a la vista. El diseño hidraulico, la caida y la cota "
            "de salida usan la APROXIMADA (al fondo); la longitud entre "
            "cabezales definitiva la fija la coronacion del muro de "
            "cabecera, que este paso supone en la clave -- su minimo --."),
    )


def cota_salida(*, punto: PuntoCritico, longitud: float, S: float) -> float:
    """
    Cota del fondo de la salida, msnm: cota de entrada - S * longitud.

    La pendiente es la del CAUCE (Sec. 7.B y Sec. 1.5): la alcantarilla sigue
    el cauce natural, y V2 nunca la restringe (Sec. 5.2). La restriccion real
    es constructiva y de cota del receptor, que es lo que verifica G2.

    `S` es argumento y no se resuelve aqui: quien llama desde 7.B pasa
    `ResultadoHidraulico.S`, la del diseño. Esta funcion es una identidad
    geometrica sobre la pendiente que reciba, y no le corresponde decidir
    cual es (MAT-D9).
    """
    return _exigir_finito("cota_salida",
                          cota_de_entrada(punto).valor - S * longitud, punto)


def _paso_cota_salida(*, punto: PuntoCritico, longitud: float, S: float,
                      caida: float, salida: float,
                      pendiente: PendienteAdoptada):
    """El `PasoDeMemoria` 7.B.4: la caida y la cota de fondo de la salida."""
    entrada = cota_de_entrada(punto)
    # Cuando gobierna un extremo de la banda, el conducto ya no sigue al
    # cauce y la salida queda a otra cota que la del cauce natural: el
    # desnivel se imprime con su numero, que es la magnitud de obra.
    aviso = aviso_de_pendiente(pendiente, longitud)
    desnivel = ()
    if aviso:
        desnivel = (Magnitud(
            "(S_cauce - S) * L", desnivel_frente_al_cauce(pendiente, longitud),
            "m", "desnivel entre la salida del conducto y el cauce natural "
            "a esa distancia: positivo, la salida queda sobre el cauce "
            "(conducto mas tendido); negativo, por debajo",
            cifras=CIFRAS_MAGNITUD),)
    return paso(
        "F7.COTA_SALIDA",
        codigo="7.B.4",
        que="Caida del conducto y cota de fondo de la salida",
        formula="caida = S * L ;  cota_salida = cota_entrada - caida",
        formula_cita_id="HDS5_3ED.2.2.4#LONGITUD",
        citas_textuales=("HDS5_3ED.2.2.4#LONGITUD", "MC_HHD.LAMINA_01"),
        sustitucion=(
            Magnitud("cota_entrada", entrada.valor, "msnm",
                     _procedencia_de_la_entrada(entrada),
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("S", S, "m/m",
                     f"paso 7.B.1 (origen: {pendiente.origen.value})",
                     cifras=CIFRAS_FINA),
            Magnitud("L", longitud, "m", "paso 7.B.3",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("caida", caida, "m", "S * L", cifras=CIFRAS_MAGNITUD),
            *desnivel),
        resultado=Magnitud("cota_salida", salida, "msnm",
                           "cota de fondo de la salida: la que se amarra al "
                           "receptor en G2", cifras=CIFRAS_MAGNITUD),
        nota_del_proyecto=" ".join(nota for nota in (
            f"AVISO: {entrada.aviso}. La cota de salida hereda esa adopcion "
            "entera: si el fondo real de la entrada esta bajo el terreno, la "
            "salida baja lo mismo." if entrada.aviso else "",
            f"AVISO: {aviso}." if aviso else "") if nota),
    )


def g2_cota_salida(*, punto: PuntoCritico, cota_salida_m: float) -> Verificacion:
    """
    G2: la salida entrega sobre el fondo del cuerpo receptor, con el desnivel
    minimo adoptado.

        cota_salida >= cota_fondo_receptor + desnivel_minimo_entrega_m

    El amarre lo pide la Sec. 7.B («cotas amarradas al perfil del cauce y a
    la cota de fondo del receptor») y lo sostiene el Manual del MTC, que
    exige que la pendiente de la alcantarilla no altere la erosion y la
    sedimentacion (num. 4.1.1.3.3, pag. impresa 71). NINGUNA de las dos
    fuentes da el desnivel: es el criterio [A] 'desnivel_minimo_entrega_m',
    que en el archivo vale 0.0 -- la entrega a nivel, la conducta de esta
    verificacion hasta T-6, cuando comparaba las dos cotas sin criterio --.

    Si falla, subir la rasante NO lo arregla: se corrige con la pendiente, con
    la longitud o con la cota del receptor. Por eso
    `CompatibilidadGeometrica.exigir_factible()` no le adjunta delta.
    """
    desnivel = ca.valor(CRITERIO_DESNIVEL_ENTREGA)
    if isinstance(desnivel, bool) or not isinstance(desnivel, (int, float)) \
            or not desnivel >= 0:
        raise DatoInvalidoError(
            CRITERIO_DESNIVEL_ENTREGA, valor=desnivel, id_punto=punto.id,
            motivo="el desnivel minimo de entrega es una altura en metros, "
                   "no negativa (0 = entrega a nivel del fondo del receptor)")
    cota_minima = punto.cota_fondo_receptor + desnivel
    cumple = cota_salida_m >= cota_minima - TOL_UMBRAL_NORMATIVO
    margen = cota_salida_m - cota_minima
    # LA CITA DEL UMBRAL ES LA LAMINA, NO EL NUMERAL DE LA PENDIENTE (auditor
    # de T-6). El num. 4.1.1.3.3 es una EXIGENCIA sobre la pendiente y no
    # habla de la entrega: tomar de el el «caracter en la fuente» de un
    # numero [A] imprimia EXIGENCIA encima de una adopcion. La Lamina N 01
    # TIPIFICA (DEFINICION) las ubicaciones de la salida respecto del cauce
    # -- a) a nivel, c) y d) sobre el -- y es lo unico que la fuente dice de
    # la entrega; no acota el desnivel.
    cita = "MC_HHD.LAMINA_01"
    return Verificacion(
        cumple=cumple,
        numeral=NUMERAL_G2,
        valor_obtenido=cota_salida_m,
        valor_admisible=cota_minima,
        criterio_aplicado=CRITERIO_DESNIVEL_ENTREGA,
        codigo="G2",
        paso=paso(
            "F7.ENTREGA",
            codigo="G2",
            que="Entrega al cuerpo receptor",
            formula="cota_salida >= cota_fondo_receptor + desnivel_minimo",
            formula_cita_id=cita,
            citas_textuales=(cita, "MC_HHD.4.1.1.3.3"),
            sustitucion=(
                Magnitud("cota_salida", cota_salida_m, "msnm", "paso 7.B.4",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("cota_fondo_receptor", punto.cota_fondo_receptor,
                         "msnm", "columna cota_fondo_receptor del CSV",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("desnivel_minimo", desnivel, "m",
                         f"criterio '{CRITERIO_DESNIVEL_ENTREGA}' [A]",
                         cifras=CIFRAS_MAGNITUD)),
            resultado=Magnitud(
                "cota_salida - cota_fondo_receptor",
                cota_salida_m - punto.cota_fondo_receptor, "m",
                "desnivel de entrega que resulta: lo que la salida queda "
                "sobre el fondo del receptor", cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="cota minima de la salida: fondo del receptor "
                            "mas el desnivel de entrega adoptado",
                valor=cota_minima, unidad="msnm", cita_id=cita,
                caracter=_caracter_de(cita),
                aplicacion="ADOPCION DEL PROYECTO, SIN CIFRA DE FUENTE: la "
                           "lamina tipifica donde puede quedar la salida "
                           "respecto del cauce (a nivel, o sobre el con "
                           "proteccion) y no acota ningun desnivel; el "
                           "numeral de la pendiente (4.1.1.3.3) exige cuidar "
                           "la erosion y la sedimentacion y no habla de la "
                           "entrega. Contrastar la cota de salida con el "
                           "fondo del receptor es lectura del proyecto, y el "
                           "numero tambien: el desnivel del criterio [A], "
                           "que en 0.0 exige solo que la salida no quede "
                           "enterrada bajo el fondo del receptor.",
                criterio_aplicado=CRITERIO_DESNIVEL_ENTREGA),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if cumple
                      else TipoDeVeredicto.NO_CUMPLE),
                margen=margen, unidad="m",
                explicacion=(
                    "la salida entrega sobre el fondo del receptor con el "
                    "desnivel adoptado" if cumple else
                    "la salida queda por debajo de la cota minima de "
                    "entrega: se corrige con la pendiente, con la longitud "
                    "o con la cota del receptor, no subiendo la rasante")),
            nota_del_proyecto=(
                "El remanso del receptor no se cubre con este desnivel: "
                "entra al control de salida por el TW de la Sec. 1.3. Un "
                "desnivel mayor no es conservador sin mas: una salida "
                "elevada descarga en caida y exige proteccion (Lamina N 01, "
                "ubicaciones c y d)."),
        ),
    )


def g3_esviaje(punto: PuntoCritico) -> Verificacion:
    """
    G3: el esviaje del cruce frente al maximo que el proyecto adopta
    ('esviaje_max_grados' [A]). ES UN AVISO Y NUNCA BLOQUEA.

    `cumple` es True siempre: el esviaje es un dato de entrada medido y el
    calculo no lo rechaza por superar una adopcion. Cuando lo supera, el paso
    lleva veredicto INDICADOR -- que la memoria pinta como aviso -- y dice
    que hacer: revisar el cruce en planta y, si procede, acondicionar el
    cauce (Manual del MTC, num. 4.1.1.3.2). El maximo se apoya POR ANALOGIA
    en el maximo practico del esviaje de EMBOCADURA del HDS-5 (num. 5.4.2,
    pag. impresa 5.13), que coincide con el del barril cuando el cabezal va
    paralelo a la via.
    """
    maximo = ca.valor(CRITERIO_ESVIAJE_MAX)
    esviaje = punto.esviaje_grados
    dentro = esviaje <= maximo + TOL_UMBRAL_NORMATIVO
    cita = "HDS5_3ED.5.4.2#MAXIMO_PRACTICO"
    factor = factor_esviaje(punto)
    return Verificacion(
        cumple=True,
        numeral=NUMERAL_G3,
        valor_obtenido=esviaje,
        valor_admisible=maximo,
        criterio_aplicado=CRITERIO_ESVIAJE_MAX,
        codigo="G3",
        paso=paso(
            "F7.ESVIAJE_MAX",
            codigo="G3",
            que="Esviaje del cruce frente al maximo adoptado (aviso)",
            formula="esviaje <= esviaje_max",
            formula_cita_id=cita,
            citas_textuales=(cita, "MC_HHD.4.1.1.3.2"),
            sustitucion=(
                Magnitud("esviaje", esviaje, "grados",
                         "columna esviaje_grados del CSV (dato de entrada)",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("factor", factor, "-",
                         "paso 7.B.2: cuanto alarga este esviaje el conducto",
                         cifras=CIFRAS_FINA)),
            resultado=Magnitud("esviaje_max - esviaje", maximo - esviaje,
                               "grados", "holgura frente al maximo adoptado",
                               cifras=CIFRAS_MAGNITUD),
            umbral=Umbral(
                descripcion="esviaje maximo que el proyecto adopta sin "
                            "revision en planta",
                valor=maximo, unidad="grados", cita_id=cita,
                caracter=_caracter_de(cita),
                aplicacion="POR ANALOGIA y como AVISO: la fuente describe un "
                           "maximo practico del esviaje de la EMBOCADURA, "
                           "que es el del barril cuando el cabezal va "
                           "paralelo a la via. El proyecto no lo aplica como "
                           "limite: el esviaje es dato de entrada, y por "
                           "encima del maximo el punto se señala y sigue.",
                criterio_aplicado=CRITERIO_ESVIAJE_MAX),
            veredicto=Veredicto(
                tipo=(TipoDeVeredicto.CUMPLE if dentro
                      else TipoDeVeredicto.INDICADOR),
                margen=maximo - esviaje, unidad="grados",
                explicacion=(
                    "el esviaje no supera el maximo adoptado" if dentro else
                    "el esviaje SUPERA el maximo adoptado: el conducto se "
                    f"alarga {factor:.2f} veces respecto del cruce a "
                    "escuadra. Revisar el cruce en planta -- y la convencion "
                    "del angulo, que se mide desde la NORMAL al eje -- y, si "
                    "procede, acondicionar el cauce a la entrada y a la "
                    "salida. El punto NO se detiene por esto")),
        ),
    )


# ---------------------------------------------------------------------------
# 7.B - Verificacion final por punto
# ---------------------------------------------------------------------------

def compatibilidad_geometrica(*, punto: PuntoCritico, material: Material,
                              seccion: Seccion,
                              resultado: ResultadoHidraulico,
                              longitud: Optional[float] = None,
                              longitud_calculada: Optional[LongitudConducto] = None,
                              pendiente: Optional[PendienteAdoptada] = None,
                              bombeo: Optional[float] = None,
                              peralte: Optional[float] = None
                              ) -> CompatibilidadGeometrica:
    """
    Verificacion final de Sec. 7.B para un punto, con el diametro que la
    Fase 4 adopto: rehace el tamizado de 7.A con ESE diametro y su HW real,
    calcula longitud, esviaje, pendiente y cotas, y devuelve las tres
    verificaciones (G1 y G2 con umbral; G3, el aviso de esviaje).

    Argumentos
    ----------
    seccion           la seccion adoptada (no la supuesta de 7.A). Era un
                      escalar `D` hasta C7: ver el argumento homonimo de
                      `tamizado_rasante`, que es a donde viaja.
    resultado         salida de la Fase 4. De aqui salen las DOS magnitudes
                      del diseño que 7.B necesita y no puede volver a elegir:
                      el HW del control que gobierna
                      (`ResultadoHidraulico.HW`, en metros sobre el fondo de
                      la entrada) y la pendiente con que se resolvio
                      (`ResultadoHidraulico.S`). La pendiente por eso no es
                      argumento de esta funcion: ver "LA PENDIENTE NO SE
                      ELIGE DOS VECES" en el docstring del modulo (MAT-D9).
    longitud    m     longitud DECLARADA del conducto (dato del expediente).
                      Si no se pasa, la calcula `longitud_del_conducto` con
                      el metodo de 'metodo_longitud_conducto'. En el caso
                      declarado `proyeccion_taludes` sale despejada de la
                      longitud dada, y es lo que esa longitud implica -- no
                      un calculo independiente.
    longitud_calculada  la `LongitudConducto` que ya se resolvio ANTES de la
                      Fase 4 (T-6). Es la via de produccion: `servicio` la
                      calcula una vez, se la da a MD como L y la pasa aqui,
                      para que la longitud de 7.B sea LA MISMA del diseño.
                      Excluye a `longitud`.
    pendiente         el `PendienteAdoptada` que resolvio la pendiente del
                      diseño, para imprimir su ORIGEN. Si no se pasa, se
                      rotula comparando `resultado.S` con la del cauce. Tiene
                      que valer `resultado.S`: si no, es un fallo de programa.
    bombeo, peralte   pendiente transversal de la plataforma (datos externos
                      opcionales, excluyentes entre si); solo se usan si la
                      longitud se calcula aqui. Con una longitud declarada
                      se validan y se AVISA que no se aplican.

    Devuelve el resultado tambien cuando NO cumple: `factible` es False y
    `delta_rasante_cm` trae el numero de Sec. 7.B. La excepcion, si se quiere,
    se pide con `CompatibilidadGeometrica.exigir_factible()` y sale como
    `DisenoNoFactibleError` con el delta, nunca generica.
    """
    S = resultado.S          # la del diseno, no una nueva eleccion (MAT-D9)
    if pendiente is None:
        pendiente = _pendiente_del_diseno(punto, S)
    elif abs(pendiente.valor - S) > TOL_UMBRAL_NORMATIVO:
        raise ValueError(
            f"7.B de {punto.id}: la pendiente adoptada ({pendiente.valor!r}) "
            f"no es la del resultado hidraulico ({S!r}). La pendiente no se "
            "elige dos veces (MAT-D9)")
    if longitud_calculada is not None and longitud is not None:
        raise ValueError(
            "compatibilidad_geometrica: `longitud` (declarada) y "
            "`longitud_calculada` se excluyen; es una u otra")
    if longitud_calculada is None:
        if longitud is None:
            longitud_calculada = longitud_del_conducto(
                punto, pendiente=pendiente, bombeo=bombeo, peralte=peralte)
        else:
            longitud_calculada = longitud_declarada(
                punto, longitud, bombeo=bombeo, peralte=peralte)
    longitud = longitud_calculada.longitud
    factor = longitud_calculada.factor_esviaje
    proyeccion = longitud_calculada.proyeccion_taludes

    tamizado = tamizado_rasante(punto=punto, material=material,
                                seccion=seccion, HW=resultado.HW)

    entrada = cota_de_entrada(punto)
    caida = S * longitud
    salida = cota_salida(punto=punto, longitud=longitud, S=S)

    pasos = [paso_pendiente(pendiente), *longitud_calculada.pasos,
             _paso_cota_salida(punto=punto, longitud=longitud, S=S,
                               caida=caida, salida=salida,
                               pendiente=pendiente)]
    L_clave = longitud_a_la_clave(punto=punto, material=material,
                                  seccion=seccion,
                                  longitud=longitud_calculada)
    if L_clave is not None:
        pasos.append(_paso_encaje(punto=punto, material=material,
                                  seccion=seccion,
                                  longitud=longitud_calculada,
                                  L_clave=L_clave))

    verificaciones: Tuple[Verificacion, ...] = (
        g1_rasante_congelada(tamizado),
        g2_cota_salida(punto=punto, cota_salida_m=salida),
        g3_esviaje(punto),
    )
    # LOS AVISOS DE 7.B, en el orden del calculo: el fondo de entrada
    # adoptado, la pendiente que gobierna un extremo de la banda y los de la
    # longitud. EL DE ESVIAJE NO VA AQUI: G3 es una verificacion con veredicto
    # INDICADOR y viaja por la via de todas las que lo llevan
    # (`InformePunto.con_aviso`), que es la que cuentan el RESUMEN, la CLI y
    # el JSON. Repetirlo en esta lista lo imprimia dos veces.
    avisos = []
    for aviso in (entrada.aviso, aviso_de_pendiente(pendiente, longitud),
                  *longitud_calculada.avisos):
        if aviso and aviso not in avisos:
            avisos.append(aviso)

    return CompatibilidadGeometrica(
        punto=punto,
        # LA SECCION, y ya no el escalar `D` que C7 dejo declarado como deuda
        # de C8 por ser "de la misma familia que `ResultadoPunto.D`". Va la
        # seccion entera por la misma razon que alli: de `0.90` no se recupera
        # si la luz era 1.20 o 2.00 m.
        seccion=seccion,
        tamizado=tamizado,
        longitud=longitud,
        proyeccion_taludes=proyeccion,
        factor_esviaje=factor,
        altura_terraplen=altura_terraplen(punto),
        S_conducto=S,
        cota_entrada=entrada,
        cota_salida=salida,
        caida=caida,
        verificaciones=verificaciones,
        numeral=NUMERAL_7B,
        pasos=tuple(pasos),
        longitud_calculada=longitud_calculada,
        pendiente=pendiente,
        longitud_a_la_clave=L_clave,
        desnivel_entrega=salida - punto.cota_fondo_receptor,
        avisos=tuple(avisos),
    )
