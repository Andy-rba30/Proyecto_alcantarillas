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
de definir el perfil longitudinal", y por eso `D_supuesto` es un argumento
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

LA PENDIENTE NO SE ELIGE DOS VECES (MAT-D9). Sec. 7.B dice que la pendiente de
la alcantarilla es la del cauce, y esa sigue siendo la regla del proyecto: el
valor por defecto lo pone la Fase 4, que resuelve `punto.exigir("S_cauce")`
cuando nadie declara otra cosa. Lo que este modulo YA NO hace es volver a
resolverla por su cuenta. Lo hacia -- `S = punto.exigir("S_cauce")` si el
llamador no pasaba nada -- y el llamador de produccion (`cli._fase_7`) no
pasaba nada, de modo que el punto que declaraba su pendiente aparte
('S_conducto' de la CLI, la via de Sec. 2.3 para la Familia B y la C) quedaba
con DOS pendientes: el HW y las velocidades calculados con la declarada, y la
caida y la cota de salida con la del cauce. Ninguna de las dos era visible en
el informe como distinta de la otra. Ahora la pendiente viaja dentro del
resultado hidraulico, que es la salida de quien la resolvio, y 7.B la lee de
ahi: si el proyecto quiere cambiarla, se cambia en la Fase 4 y las dos cosas
se mueven juntas.

El 1/cos(esviaje) no es un coeficiente adoptado: es la identidad geometrica
del cruce oblicuo -- el eje del conducto es la hipotenusa del ancho que
atraviesa -- del mismo orden que el T = D*sen(theta/2) de `modelos.Geometria`.
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

    modulos.M5_verificaciones.cota_entrada_supuesta   la cota a la que se
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

Por que 7.B solo trae dos verificaciones
-----------------------------------------
De los cinco puntos que Sec. 7.B enumera, tres son CALCULOS y no chequeos
(longitud, esviaje y pendiente: la hoja fija como se obtienen, no un umbral
que puedan incumplir) y viajan como campos de `CompatibilidadGeometrica`. Los
dos que si tienen umbral son:

    G1  rasante congelada        cota de rasante >= la minima de 7.A
    G2  cota de salida           cota de salida >= cota de fondo del receptor

G2 es una INTERPRETACION declarada, no un criterio con fuente propia: Sec.
7.B pide las cotas de entrada y salida "amarradas al perfil del cauce y a la
cota de fondo del receptor", y la lectura minima de ese amarre es que la
salida no quede enterrada bajo el fondo del cuerpo receptor. No lleva ningun
parametro adoptado -- compara dos elevaciones del expediente y nada mas -- y
por eso no crea criterio. Un desnivel MINIMO de entrega sobre ese fondo si
seria un criterio, la hoja de ruta no lo da, y por lo tanto no se exige aqui.

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
    DisenoNoFactibleError    lo lanzan `TamizadoRasante.exigir_factible()` y
                             `CompatibilidadGeometrica.exigir_factible()`, con
                             `delta_rasante_m` cargado. NUNCA una excepcion
                             generica: el "no factible" de Sec. 7.B viaja con
                             su numero, y por defecto ni siquiera viaja como
                             excepcion -- `tamizado_rasante()` DEVUELVE el
                             delta en `delta_rasante_cm` y quien quiera la
                             excepcion la pide.
    DatoInvalidoError        el paquete estructural no es positivo (la
                             subrasante no queda bajo la rasante, Sec. 1.5) o
                             el esviaje no admite cruce.

Uso
---
    from modulos.M7_geometria import tamizado_rasante, compatibilidad_geometrica

    # 7.A, antes del perfil longitudinal, con el diametro maximo supuesto
    tamizado = tamizado_rasante(punto=punto, material=hdpe,
                                D_supuesto=hdpe.D_max, HW=0.95)   # D_max: tope de CATALOGO
    tamizado.cota_rasante_min          # msnm - la rasante que hay que fijar
    tamizado.delta_rasante_cm          # cm  - cuanto falta subir; 0.0 si cabe
    print(tamizado.mensaje)            # "no factible -> subir rasante 18.0 cm"

    # 7.B, por punto, con el diametro que la Fase 4 adopto. La pendiente NO
    # es argumento: sale de `resultado.S`, la que uso el diseño (MAT-D9)
    geometria = compatibilidad_geometrica(punto=punto, material=material,
                                          D=resultado_punto.D,
                                          resultado=resultado_punto.resultado_hidraulico)
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

import criterios_adoptados as ca
from dominios import ESVIAJE_MAX
from modelos import (CIFRAS_MAGNITUD, CompatibilidadGeometrica,
                     CondicionRasante,
                     DatoInvalidoError, EleccionDeProyecto, LimiteNumericoError,
                     Magnitud, Material,
                     PuntoCritico, ResultadoHidraulico, TamizadoRasante,
                     TipoDeVeredicto, Umbral, Veredicto, Verificacion, paso)
from modulos.M2_material import diametro_exterior, espesor_pared
from modulos.M5_verificaciones import (CRITERIO_RESGUARDO, cota_clave,
                                       cota_entrada_supuesta,
                                       resguardo_por_cbr)
from tolerancias import TOL_UMBRAL_NORMATIVO

NUMERAL_7A = "Sec. 7.A"
NUMERAL_7B = "Sec. 7.B"
# El recubrimiento NO sale solo de EG-2013, y decir que si es la atribucion
# falsa que NOR-VAC-01 denuncia: el EG-2013 fija la altura minima de relleno
# unicamente para HDPE. Este string es lo que M11 imprime en la columna
# "numeral" de la fila G1, o sea lo unico que el revisor ve de esa
# verificacion, y con la version anterior una fila de CONCRETO decia
# "recubrimiento EG-2013" al lado de criterio_aplicado = cobertura_minima_aashto.
NUMERAL_G1 = ("Sec. 7.A (recubrimiento: el mayor entre EG-2013 508.07 -- solo "
              "HDPE -- y AASHTO LRFD Art. 12.6.6.3, Tabla 12.6.6.3-1 / "
              "resguardo Sec. 5.1)")
NUMERAL_G2 = "Sec. 7.B (cotas amarradas al fondo del receptor)"

CRITERIO_TALUD = "talud_terraplen"
CRITERIO_COBERTURA_AASHTO = "cobertura_minima_aashto"
CRITERIO_CONDICION_PAVIMENTO = "condicion_pavimento"

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
# `cota_entrada_supuesta` y `resguardo_por_cbr`, por la razon que el docstring
# del modulo ya da para esas dos -- V7 y 7.A tienen que medir la clave desde
# la misma referencia o el acoplamiento sigue abierto por la puerta de atras.
# Estaba definida en los dos sitios, y las dos copias arrastraban el mismo
# defecto: la calculaban como cota_entrada + D, sin espesor de pared (MAT-D4).


def cobertura_minima_aashto(*, material: Material, D: float) -> float:
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
    terminos iguales es uno solo. Ver la nota del criterio: para una seccion
    no circular la reduccion deja de valer.

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

    Se detiene tambien en 'espesor_pared_conducto' cuando la fila usa Bc.
    """
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

    # El D exterior se pide SOLO si la fila lo usa. La fila del concreto
    # (Bc) lo necesita y por lo tanto se detiene en 'espesor_pared_conducto';
    # las del metal (S) y el termoplastico (ID) no, y exigirselo seria
    # inventarles una dependencia que la tabla no tiene. Quien SI la tiene
    # siempre es la cota de clave, que es otra cosa y esta en M5.
    if _DIAMETRO_DE_LA_FILA[fila["sobre"]] == "D_ext":
        D_fila = diametro_exterior(material=material, D=D)
    else:
        D_fila = D

    candidatos = [fila["piso_m"]]
    if fila["divisor"] is not None:
        candidatos.append(D_fila / fila["divisor"])
    return max(candidatos)


def altura_recubrimiento(*, material: Material, D: float) -> float:
    """
    h_rec: relleno minimo sobre la clave hasta la subrasante, m (Sec. 7.A).

        h_rec = max( minimo de EG-2013 , cobertura minima de AASHTO )

    REGLA DEL MAYOR, la misma que Sec. 0.2 ya aplica al recubrimiento de
    concreto entre AASHTO y E.060. Los dos minimos regulan lo mismo desde dos
    corpus distintos y ninguno deroga al otro: EG-2013 es norma peruana
    vigente [N] y AASHTO LRFD es el cuerpo que Sec. 0.2 adopta de extremo a
    extremo, cubriendo con [C] el vacio que el corpus peruano deja.

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
    aashto = cobertura_minima_aashto(material=material, D=D)
    if material.h_relleno_min_eg2013 is None:
        return aashto
    return max(material.h_relleno_min_eg2013, aashto)


def criterio_recubrimiento(material: Material) -> Optional[str]:
    """
    Clave del criterio del que sale h_rec: hoy siempre
    'cobertura_minima_aashto'.

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
    return CRITERIO_COBERTURA_AASHTO


# ---------------------------------------------------------------------------
# 7.A - Tamizado previo: la cota de rasante minima
# ---------------------------------------------------------------------------

def tamizado_rasante(*, punto: PuntoCritico, material: Material,
                     D_supuesto: float, HW: float) -> TamizadoRasante:
    """
    Tamizado de Sec. 7.A: cota de rasante minima como MAXIMO de las dos
    condiciones, y el delta que le falta a la rasante del CSV para alcanzarla.

        cota rasante >= max( cota clave + h_rec + e_paq ,
                             cota entrada + HW + resguardo(CBR) + e_paq )

    Argumentos
    ----------
    D_supuesto  m   diametro del tamizado. Sec. 7.A manda correrlo con el
                    diametro MAXIMO supuesto antes de definir el perfil; en
                    7.B se vuelve a correr con el diametro adoptado. Es
                    explicito porque la eleccion se declara en la memoria: ver
                    la ADVERTENCIA del docstring del modulo, el D maximo no es
                    conservador para las dos condiciones a la vez.
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
    h_rec = altura_recubrimiento(material=material, D=D_supuesto)
    entrada = cota_entrada_supuesta(punto)
    clave = cota_clave(punto=punto, material=material, D=D_supuesto)
    t_pared = espesor_pared(material)
    D_ext = diametro_exterior(material=material, D=D_supuesto)

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
        D_supuesto=D_supuesto,
        espesor_pared=t_pared,
        D_exterior=D_ext,
        HW=HW,
        h_recubrimiento=h_rec,
        espesor_paquete=e_paq,
        resguardo=resguardo,
        factible=factible,
        delta_rasante_m=0.0 if factible else faltante,
        criterio_recubrimiento=criterio_recubrimiento(material),
        criterio_resguardo=CRITERIO_RESGUARDO,
        id_punto=punto.id,
        numeral=NUMERAL_7A,
    )


def g1_rasante_congelada(tamizado: TamizadoRasante) -> Verificacion:
    """
    G1: la rasante del expediente alcanza la minima del tamizado de 7.A.

    Es la unica de las dos verificaciones de 7.B que no necesita la longitud
    del conducto, y por lo tanto la unica evaluable sin 'talud_terraplen'.
    El criterio
    aplicado es el de la condicion que gobierna: 'resguardo_HW_subrasante'
    [N->] si manda la carga a la entrada, y 'cobertura_minima_aashto' [C] si
    manda el recubrimiento -- en los tres materiales, porque la Tabla
    12.6.6.3-1 entra en los tres (ver `criterio_recubrimiento`).

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
        numeral=NUMERAL_G1,
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
                         "Tabla 12.6.6.3-1 de AASHTO",
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
    puede estar arbitrariamente cerca del limite: con 89.999999999 grados el
    factor vale 5.73e10 y `longitud_conducto` devuelve del orden de 1e11 m.
    La ficha MAT-O18 lo clasifica como "no alcanzable desde el CSV validado",
    y eso es INEXACTO: M0 valida `0 <= esviaje < 90` y ese valor pasa.

    No se pone cota de cordura porque no hay ninguna que citar: ni la Sec.
    7.B ni EG-2013 fijan un esviaje maximo constructivo, y elegir uno --
    45, 60 grados -- seria inventar un valor normativo, que es lo que
    CLAUDE.md prohibe expresamente. Lo que corresponde es que el numero se
    VEA: una longitud de 1e11 m es absurda a simple vista en la memoria, y
    G2 la contrasta contra la cota del receptor. Si el proyecto quiere una
    cota, el camino es declararla como criterio [A] con su sensibilidad, no
    escribirla aqui.
    """
    if not (-ESVIAJE_MAX < punto.esviaje_grados < ESVIAJE_MAX):
        raise DatoInvalidoError(
            "esviaje_grados", valor=punto.esviaje_grados, id_punto=punto.id,
            motivo=f"el esviaje va de 0 (cruce perpendicular) a {ESVIAJE_MAX} "
                   "grados, donde el conducto seria paralelo a la via y la "
                   "longitud de 7.B no estaria definida",
        )
    return 1.0 / math.cos(math.radians(punto.esviaje_grados))


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


def longitud_conducto(punto: PuntoCritico) -> float:
    """
    Longitud del conducto, m (Sec. 7.B):

        (ancho de plataforma + proyeccion de taludes) / cos(esviaje)

    Se detiene con CriterioPendienteError mientras 'talud_terraplen' siga
    vacio (ver `proyeccion_taludes`).
    """
    return _exigir_finito(
        "longitud_conducto",
        (punto.ancho_plataforma + proyeccion_taludes(punto)) * factor_esviaje(punto),
        punto)


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
                          cota_entrada_supuesta(punto) - S * longitud, punto)


def g2_cota_salida(*, punto: PuntoCritico, cota_salida_m: float) -> Verificacion:
    """
    G2: la cota de salida no queda bajo el fondo del cuerpo receptor.

    Interpretacion declarada del amarre que pide Sec. 7.B, sin parametro
    adoptado de por medio: compara dos elevaciones del expediente. Un desnivel
    minimo de entrega sobre ese fondo seria otro asunto, la hoja de ruta no lo
    fija y por eso no se exige aqui (ver el docstring del modulo).

    Si falla, subir la rasante NO lo arregla: se corrige con la pendiente, con
    la longitud o con la cota del receptor. Por eso
    `CompatibilidadGeometrica.exigir_factible()` no le adjunta delta.
    """
    return Verificacion(
        cumple=cota_salida_m >= punto.cota_fondo_receptor - TOL_UMBRAL_NORMATIVO,
        numeral=NUMERAL_G2,
        valor_obtenido=cota_salida_m,
        valor_admisible=punto.cota_fondo_receptor,
        criterio_aplicado=None,
        codigo="G2",
    )


# ---------------------------------------------------------------------------
# 7.B - Verificacion final por punto
# ---------------------------------------------------------------------------

def compatibilidad_geometrica(*, punto: PuntoCritico, material: Material,
                              D: float, resultado: ResultadoHidraulico,
                              longitud: Optional[float] = None
                              ) -> CompatibilidadGeometrica:
    """
    Verificacion final de Sec. 7.B para un punto, con el diametro que la
    Fase 4 adopto: rehace el tamizado de 7.A con ESE diametro y su HW real,
    calcula longitud, esviaje, pendiente y cotas, y devuelve las dos
    verificaciones con umbral (G1 y G2).

    Argumentos
    ----------
    D           m     diametro adoptado (no el supuesto de 7.A).
    resultado         salida de la Fase 4. De aqui salen las DOS magnitudes
                      del diseño que 7.B necesita y no puede volver a elegir:
                      el HW del control que gobierna
                      (`ResultadoHidraulico.HW`, en metros sobre el fondo de
                      la entrada) y la pendiente con que se resolvio
                      (`ResultadoHidraulico.S`). La pendiente por eso no es
                      argumento de esta funcion: ver "LA PENDIENTE NO SE
                      ELIGE DOS VECES" en el docstring del modulo (MAT-D9).
    longitud    m     longitud del conducto. Por defecto la calcula
                      `longitud_conducto`, que exige 'talud_terraplen'. Se
                      admite explicita para el punto cuya seccion transversal
                      es asimetrica o esta medida en planos: quien la pase
                      declara de donde la obtuvo, igual que MD con su L. En
                      ese caso `proyeccion_taludes` sale despejada de la
                      longitud dada, y es lo que esa longitud implica -- no un
                      calculo independiente.

    Devuelve el resultado tambien cuando NO cumple: `factible` es False y
    `delta_rasante_cm` trae el numero de Sec. 7.B. La excepcion, si se quiere,
    se pide con `CompatibilidadGeometrica.exigir_factible()` y sale como
    `DisenoNoFactibleError` con el delta, nunca generica.
    """
    S = resultado.S          # la del diseno, no una nueva eleccion (MAT-D9)
    factor = factor_esviaje(punto)
    if longitud is None:
        proyeccion = proyeccion_taludes(punto)      # exige 'talud_terraplen'
        longitud = (punto.ancho_plataforma + proyeccion) * factor
    else:
        proyeccion = longitud / factor - punto.ancho_plataforma

    tamizado = tamizado_rasante(punto=punto, material=material,
                                D_supuesto=D, HW=resultado.HW)

    entrada = cota_entrada_supuesta(punto)
    caida = S * longitud
    salida = cota_salida(punto=punto, longitud=longitud, S=S)

    verificaciones: Tuple[Verificacion, ...] = (
        g1_rasante_congelada(tamizado),
        g2_cota_salida(punto=punto, cota_salida_m=salida),
    )

    return CompatibilidadGeometrica(
        punto=punto,
        D=D,
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
    )
