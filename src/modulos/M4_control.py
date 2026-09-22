"""
M4_control.py
=============
Fases 4.2 y 4.3 de la hoja de ruta: control de entrada (HDS-5) y control de
salida. Tres piezas independientes y una regla de comparacion:

    1. tirante_critico(Q, D)        Sec. 4.2.1 - segundo Brent, sobre
                                    Q^2*T/(g*A^3) = 1
    2. control_entrada(...)         Sec. 4.2 - HDS-5, Tabla A.1, tres ramas
    3. control_salida(...)          Sec. 4.3 - HW = H + h_o - S*L
    4. hw_gobernante(...)           el mayor de las dos, CON su etiqueta

Las tres primeras son independientes entre si salvo por una dependencia real
de la fisica: tanto la Forma 1 del control de entrada (que necesita H_c) como
el h_o del control de salida (que necesita y_c) se apoyan en el tirante
critico. Por eso las dos aceptan un `TiranteCritico` ya resuelto como
argumento opcional: la pieza 1 se prueba sola, y las piezas 2 y 3 se prueban
solas inyectandole el critico que uno quiera, sin tener que resolver Brent
dentro del test.

Lo que M4 NO hace
-----------------
M4 no resuelve el tirante normal (eso es M3, Sec. 4.1), no elige material ni
diametro (M2), y no verifica nada: que HW quede bajo la subrasante con su
resguardo (V4) es verificacion de la Fase 5 y la hace M5 con el HW que este
modulo entrega. M4 tampoco decide de donde sale el TW: lo recibe como dato.
El TW del cuerpo receptor es el criterio pendiente 'TW_receptor' (ANA / Junta
de Usuarios) y quien lo resuelva debe declararlo, no este modulo.

    V4b (la relacion HW/D) LA VERIFICA M5 DESDE S14, y conviene decir con
    que numero: `M5.v4b_relacion_hw_d` divide entre D el HW del control
    GOBERNANTE -- `ResultadoHidraulico.HW` --, no el HWi/D que este modulo
    calcula. Los dos son "HW/D" y no son el mismo: el de aqui es la salida
    adimensional de las ecuaciones de la Tabla A.1, valida solo si el control
    de entrada gobierna; lo que V4b acota es el embalse que la obra produce,
    que es el mayor de los dos controles.

    Este parrafo tuvo las dos afirmaciones falsas, en este orden. Primero
    decia que "HW/D <= 1.5 (V4b) ... son verificaciones de la Fase 5 y las
    hace M5" cuando M5 no la implementaba (SIS-A-02, MAT-D2). Corregido eso,
    decia que lo que M4 entregaba para el cableado futuro era
    `ControlEntrada.HW_sobre_D`, y tampoco: ese campo no es el argumento del
    chequeo, por la razon del parrafo anterior. El umbral es [A] y no [C]
    -- el rango 1.0-1.5 es una encuesta de practica de agencias
    estadounidenses que el HDS-5 describe, no un criterio que el manual fije
    (NOR-HDS-02) --, y esa reetiquetacion es lo que permitio cablearlo
    (conflicto #1 de la matriz de auditorias).

Los dos solvers de Brent (Sec. 4.2.1)
--------------------------------------
La hoja de ruta lo dice expresamente: "M4 requiere dos solvers, no uno". El
primero es el de M3 (tirante normal por Manning); el segundo es el de aqui:

    Q^2 * T / (g * A^3) = 1        con T = D*sen(theta/2)

Es otra ecuacion, no otra forma de la misma. El tirante normal depende de n y
de S; el critico NO depende de ninguno de los dos -- solo de Q y de la
geometria. De ahi que `TiranteCritico.V` si sea Q/A_c y no viole la regla de
doble n: no hay dos rugosidades entre las que elegir porque no hay rugosidad.

La ecuacion se resuelve en la forma equivalente A^3/T = Q^2/g (ver
`_residuo_critico`: la forma literal divide entre A^3 y ahi hay una division
por cero exacta en el borde vacio del intervalo). Asi escrita es monotona
creciente en theta sobre (0, 2*pi), de -Q^2/g en la seccion vacia a
+infinito en la llena: existe una unica raiz para todo Q > 0, de modo que --
a diferencia de `M3.tirante_normal` -- aqui no hay caso "sin solucion". Si Q
es enorme, el tirante critico simplemente se acerca a D, y quien decide que
eso es inadmisible es V1 (y/D <= 0.75), no este solver.

Control de entrada (Sec. 4.2)
------------------------------
    q* = Ku*Q / (A_llena * D^0.5)        Ku = 1.811 (SI)

    q* <= 3.5   HWi/D = H_c/D + K*(q*)^M + Ks*S      (Forma 1, ec. A.1)
                HWi/D = K*(q*)^M                     (Forma 2, ec. A.2)
    q* >= 4.0   HWi/D = c*(q*)^2 + Y + Ks*S          (sumergido, ec. A.3)
    entre ambos: interpolacion lineal

LA RAMA NO SUMERGIDA TIENE DOS FORMAS y las decide la carta, no el
proyectista: es la columna «Equation Form» de la Tabla A.1. La Forma 2 NO
lleva Ks*S ni H_c/D. La sumergida es UNA sola y comun a las dos.

CUIDADO CON LA PALABRA «FORMA» EN ESTE MODULO, porque nombra dos cosas y este
docstring las confundia: la FORMA DE ECUACION (1 o 2, del num. A.2.1) y las
RAMAS del regimen (no sumergida / sumergida). Se leia «las dos formas» donde
queria decir «las dos ramas», y esa colision -- que §15.8 denuncia contra la
hoja de ruta v8 como defecto D-9 -- estaba tambien aqui.

La interpolacion se hace entre el valor que da la RAMA NO SUMERGIDA evaluada
en q* = 3.5 y el que da la SUMERGIDA evaluada en q* = 4.0 -- no entre las dos
ramas evaluadas en el q* real. Las dos ecuaciones son ajustes validos solo
dentro de su rango; extrapolarlas al interior de la zona de transicion, que
es justamente donde ninguna de las dos vale, seria usarlas fuera de su
dominio. Asi la curva HWi/D(q*) queda continua en los dos extremos.

    Y «EVALUADA EN q* = 3.5» ES EVALUADA PARA EL CAUDAL DE q* = 3.5 (EXT-M-04,
    v8 §4.2 enmendada en EXT-0). La ec. (A.1) lleva H_c/D, y el H_c que
    entra en el extremo inferior es el del caudal que corresponde a ese
    q*, Q_lo = 3.5 * A_llena * sqrt(D) / Ku, no el del caudal real del
    punto. Hasta EXT-2 se usaba el H_c del caudal real: el extremo
    inferior se movia con q*, y lo que la memoria imprimia como «recta»
    era una curva (incrementos de 20.8 a 5.6 mm por paso de q* en CP-5;
    +1.9 % de HW, del lado conservador). Solo afecta a la Forma 1 -- la
    (A.2) no lleva H_c -- y solo al interior de la ventana: en q* = 3.5 el
    caudal real ES Q_lo y en q* = 4.0 el extremo superior no lleva H_c, de
    modo que la continuidad en los bordes no cambia. El caso patron CP-5T
    fija el punto medio, 1.107921425 m, calculado a mano.

    LA INTERPOLACION LINEAL NO ES EL METODO DEL HDS-5. Es una SIMPLIFICACION
    ADOPTADA, declarada como criterio [C] en 'metodo_transicion_hds5'. HDS-5
    no interpola: en la zona 3.5 < q* < 4.0 traza una curva TANGENTE a las
    dos ramas, un empalme empirico ajustado sobre sus datos de laboratorio
    del que no publica ecuacion cerrada. Quien prescribe la recta es Sec. 4.2
    de la hoja de ruta, no la fuente primaria. La distincion importa para la
    memoria: lo que se cita como HDS-5 son las DOS ECUACIONES y sus
    constantes de la Tabla A.1; el puente entre ellas es del proyecto y se
    defiende como tal. El error queda acotado -- la recta coincide con cada
    rama en su borde de validez, asi que solo se separa de la curva original
    en el interior de una ventana de q* de 0.5 de ancho -- y acotado no es lo
    mismo que normativo. `control_entrada()` invoca el criterio al entrar en
    esa rama, de modo que M11 lo imprime unicamente cuando algun punto del
    corredor cae realmente en la transicion.

La transicion bajo FORMA 2 puede decrecer con el caudal
-------------------------------------------------------
No es un fallo de implementacion: sale de combinar (A.2) + (A.3) + la recta
[C]. Con Forma 1 los DOS extremos de la recta llevan Ks*S y el termino SE
CANCELA en la diferencia, de modo que su pendiente no depende de S. Con Forma
2 el extremo inferior lo pierde, y la diferencia pasa a depender de S. Sobre
la Carta 9 escala 1 (K=0.510, M=0.667, c=0.0309, Y=0.80, Ks=-0.5) el umbral
exacto es

    S* = (c*4^2 + Y - K*3.5^M) / |Ks| = 0.236495 m/m

y por encima de esa pendiente la recta BAJA al subir q*: con D = 0.90 m y
S = 0.30, un q* de 3.50 da HW = 1.0585 m y uno de 4.00 da 1.0300 m -- 28.6 mm
MENOS de carga con 14 % MAS de caudal, y del lado no conservador --. No lo
atrapa nadie: `_resolver_hw_fuera_de_rango` solo mira el signo, y aqui el numero
es positivo.

Lo encontro la auditoria de C3 y queda DECLARADO, no corregido: corregirlo
seria sustituir el metodo de transicion adoptado, que es el criterio [C]
`metodo_transicion_hds5`, y eso no es de esta sesion. Una S de ese orden en
una alcantarilla es rarisima -- las del corredor van de 0.006 a 0.008 --, pero
rarisima no es imposible y `dominios.S_CAUCE_MAX` admite hasta 1.0. El caso
patron CP5D_FORMA2_TRANSICION_NO_MONOTONA lo fija.


El termino K_s*S tiene un limite, y el limite es fisico
-------------------------------------------------------
La correccion por pendiente K_s*S es una recta sin tope: con K_s = -0.5, basta
una S grande y un Q chico para que las dos RAMAS que lo llevan -- la no
sumergida de Forma 1 y la sumergida -- devuelvan HWi/D NEGATIVO --
una carga de agua bajo el fondo del conducto, que no existe (MAT-D10). El
umbral del signo, para la Forma 1, es S > 2*(H_c/D + K*(q*)^M): con
D = 0.90 m, Q = 0.05 m3/s y la carta de concreto vale S > 0.3770624, y hasta
esta correccion el diseño se ACEPTABA entero con HW = -0.010 m, o sea con V4
y el tamizado de 7.A evaluados 0.18 m del lado no conservador.

`control_entrada()` ya no devuelve ese numero. Hasta PF-1, cuando HWi/D salia
<= 0 lanzaba `DisenoNoFactibleError` con el motivo entero: un rechazo, no un
piso, porque un piso exige decidir QUE carga se adopta en su lugar -- la
lectura fisica seria HW ~ H_c, la energia especifica critica -- y ese valor no
lo fija ni la hoja de ruta ni el HDS-5, de modo que adoptarlo EN EL CODIGO
seria rellenar un vacio en silencio. Ese argumento sigue en pie y por eso el
codigo sigue sin adoptar nada por su cuenta. Lo que PC-03 midio es que el
rechazo era DEFINITIVO y MUDO, y que la constitucion tiene una regla para
este vacio que no es descartar: desde PF-1 el caso lo resuelve el criterio
[A] de perfil `hw_entrada_fuera_de_rango` (`_resolver_hw_fuera_de_rango`):
sin declarar, `CriterioPendienteError` con el par (Q, S) y S*, visible en la
pestaña 4; «energia_critica», HW = H_c con el `PisoDeCargaEntrada` que la
memoria imprime; «descartar», la conducta anterior. S* lo publica
`pendiente_limite_de_signo`.

CUANTO DE MAT-D10 CIERRA ESTE RECHAZO, dicho con numeros porque callarlo lo
haria parecer mas de lo que es. Cierra el SIGNO y poco mas. Justo por debajo
del umbral el diseño se sigue aceptando: con S = 0.37706 sale HW = +1e-6 m, y
V4 y el tamizado de 7.A quedan evaluados 0.1695 m del lado no conservador --
el 94 % de los 0.1798 m de error que la ficha denuncia. De esos 0.1798 m el
rechazo retira 0.0103, o sea el 5.7 %. Y en el corredor de este expediente
(S_cauce = 0.006-0.008) no se dispara nunca: en D = 0.90 hace falta S > 0.27,
y ademas con Q = 0.025 m3/s.

Es lo que se puede hacer sin fuente. Acotar el rango de validez ENTERO de la
correccion -- la recta deja de representar al HDS-5 bastante antes de cruzar
el cero -- exige una pendiente maxima que ni la hoja de ruta ni el manual
escriben, y ponerla aqui seria inventarla. Queda abierto y escrito: el
rechazo protege contra lo imposible, no contra lo extrapolado.

K_s: no esta en la Tabla A.1
-----------------------------
Las cinco constantes de la Tabla A.1 son K, M, c e Y... y cuatro no son cinco.
K_s (-0.5 sin inglete, +0.7 con inglete) NO figura en esa tabla: proviene de
la formulacion de las ecuaciones y hay que traerlo aparte. Omitirlo es un
error silencioso, del mismo genero que el 29 imperial del control de salida:
con S = 0.005 y Ks = -0.5 el termino vale -0.0025 en HWi/D, unos 2 mm en un
tubo de 0.90 m -- invisible en una revision a ojo y sistematicamente sesgado.
Por eso `modelos.ConstantesHDS5` lo declara como campo obligatorio: no se
puede construir la carta sin el, y `constantes_normativas.HDS5_INLET` y el
criterio 'hds5_embocadura_hdpe' lo traen los cuatro.

Control de salida (Sec. 4.3)
-----------------------------
    HW = H + h_o - S*L
    H  = (1 + ke + 19.63*n^2*L/R^(4/3)) * V^2/(2g)
    h_o = max(TW, (y_c + D)/2)

19.63 es el valor SI (`constantes_normativas.K_FRICCION_SI`). El 29 de la
literatura FHWA es del sistema ingles y no falla ruidosamente en metrico:
devuelve numeros plausibles y equivocados -- con los datos de CP-8, 0.5455 m
en vez de 0.4977 m, un 9.6 % de diferencia. La guardia es
`test_constante_friccion_es_SI_no_imperial` (tests/test_M4_control.py), que
contrasta contra CP-8 y contra el valor que saldria con 29.

    DE DONDE SALE EL 19.63, y por que se parece tanto a 2*g. Es la cifra que
    el HDS-5 escribe como conversion SI de su K = 29: fuente primaria
    transcrita. El parecido con 2*g NO es una coincidencia, y este docstring
    afirmaba que si lo era (MAT-D12, MAT-X5). La relacion es exacta y se
    comprueba con dos multiplicaciones:

        K = 2*g / phi^2      phi = factor de unidades de Manning
                             (1.486 en el sistema ingles, 1 en SI)

        ingles:  2 * 32.2 / 1.486^2   = 29.164  -> el 29 que imprime HDS-5
        SI:      2 * 9.81456          = 19.629  -> el 19.63 que imprime HDS-5

    o sea que en SI la constante ES 2*g, y lo unico que separa al 19.63 del
    19.62 es CUAL g: HDS-5 trabaja con g = 32.2 ft/s^2, que son 9.81456 m/s^2,
    y el proyecto usa `constantes_fisicas.G` = 9.81. Decir "coincidencia"
    ocultaba justamente eso -- que los dos numeros son el mismo concepto
    redondeado en dos sistemas --, y una razon falsa para un numero correcto
    es el mismo defecto que un numero inventado, en la otra direccion.

    Se conserva el 19.63 transcrito, no el 2*G derivado: el valor es de la
    fuente primaria y las tres auditorias coinciden en que el codigo tiene
    razon. Lo que la diferencia introduce esta acotado y se dice: el cociente
    19.63/19.62 vale 1.0005, de modo que afecta al termino de FRICCION en un
    +0.05 %: unas 950 veces menos que el +47.7 % que produce usar el 29
    imperial sobre ese mismo termino (el 9.6 % de arriba es sobre H, en
    CP-8), que es el error que esta constante existe para atrapar.

    Sigue en pie, y no dependia de aquella nota, que la gravedad de este
    modulo es `constantes_fisicas.G` = 9.81 y no
    `constantes_normativas.G_LAUSHEY` = 9.8, que la Sec. 4.1.1.3.7 c) fija
    SOLO para la formula de Laushey de M6. Son dos constantes con dos
    origenes y el proyecto las mantiene separadas a proposito.

h_o TIENE NUMERAL Y TIENE CONDICION DE USO, y hasta esta correccion el
modulo no traia ninguna de las dos (NOR-HDS-05). Es el num. 3.3.3 "Outlet
Control", pag. impresa 3.24 de la 3a ed., y alli mismo dice que la
aproximacion "can only be used if the barrel flows full for most of its
length" y que "it should not be used if the inlet is not submerged". Este
modulo la aplica SIEMPRE, tambien cuando el barril no llena, porque
comprobarlo exige un perfil de la lamina de agua que el script no calcula.
No se disimula: el texto literal y su condicion viven en
`constantes_normativas.H_O_NUMERAL` / `H_O_CONDICION_TEXTO`, entran en
`UMBRALES_DE_VERIFICACION` -- uno de los bloques que M11 imprime sin depender
de ningun resultado, junto al de alcance y al de acotaciones -- y la
verificacion pendiente esta declarada en el criterio
'geometria_control_salida', que presupone exactamente lo mismo.

De las tres condiciones que HDS-5 le pone a h_o, DOS se evaluan punto por
punto -- los limites HW/D < 0.75 ("should not be used") y HW/D < 1.2
("caution should be used"), en `control_salida()` --, y la tercera, que el
barril fluya lleno, no: exige un perfil de la lamina de agua que este script
no calcula. Declarar las tres sin evaluar ninguna, pudiendo evaluar dos, era
extender a toda la nota una imposibilidad que solo vale para una, y dejaba la
memoria avisando de que "algun punto podria estar fuera de rango" sin decir
cual lo esta.

Y DESDE EXT-3 EL LIMITE DE 0.75 NO ES UN AVISO (EXT-M-02, v8 §4.3 enmendada en
EXT-0). Cuando el control de salida gobierna y HW/D cae bajo 0.75 el metodo
aproximado NO esta definido para ese punto: el HW que sale no es un resultado
sino un numero fuera del dominio del metodo. Este modulo sigue sin lanzar --
calcula, marca `h_o_fuera_de_rango` y juzga el paso F4.HO como DIFERIDO con
el motivo «metodo no evaluable» -- y quien convierte la bandera en `Bloqueo`
es la corrida (`servicio.correr_punto`), leyendo el MISMO campo que el paso juzga:
diferible a nivel de perfil, no a nivel de expediente. Nunca es un
`Verificacion(cumple=False)`: subir de diametro solo baja HW/D (0.589 ->
0.526 medido) y recorrer el catalogo hasta `DisenoNoFactibleError` seria
rechazar por una condicion que ningun diametro puede cumplir.

Regimen del barril y velocidad de salida (HDS-5 3.1.6; EXT-3)
--------------------------------------------------------------
`resolver_control()` emite ademas COMO fluye el barril y con que velocidad
sale el agua, porque las dos cosas deciden verificaciones que hasta EXT-3 se
hacian siempre con el flujo uniforme de M3 (EXT-M-01, PC-04):

    LLENO               TW >= D: el TW llena el barril hasta la clave. V1 y V2
                        se comparan con D y con Q_celda/A_llena.
    PARCIALMENTE LLENO  en otro caso. Bajo control de ENTRADA el tirante es
                        el normal (M3); bajo control de SALIDA no se conoce
                        sin el perfil de la lamina y V1/V2 quedan pendientes.

    V_salida            control de SALIDA: Q_celda / A(min(D, max(TW, y_c)))
                        -- tirante critico, TW o seccion entera, segun el TW
                        (pag. impresa 3.18) --, sin n.
                        control de ENTRADA: la del tirante normal (pag. 3.24),
                        rama n_min: techo conservador para el d50 de M6.

Ver `regimen_del_barril`, `velocidad_de_salida` y el paso F4.REGIMEN.

De donde salen V y R en esa ecuacion: la hoja de ruta escribe la formula pero
no dice a que seccion pertenecen, y la eleccion mueve el resultado (R = D/4 =
0.225 m a seccion llena frente a R = 0.2715 m con y/D = 0.75, en un tubo de
0.90 m). No se rellena en silencio: esta declarado en el criterio
'geometria_control_salida' [C] = seccion llena, con su justificacion. Si se
cambia ese criterio, cambia el calculo sin tocar este archivo.

Cual gobierna
-------------
El HW de diseno es el MAYOR de los dos: cada control es una restriccion
independiente y la que exige mas carga es la que manda. `hw_gobernante()`
devuelve el par (HW, ControlGobernante) y `resolver_control()` lo deja
asentado en `ResultadoHidraulico.control_gobernante`, junto a los dos HW por
separado. Nunca se devuelve el maximo a secas: un HW sin la etiqueta de que
control lo produjo no le dice al revisor si el remedio es la embocadura o el
nivel del receptor.

Excepciones
-----------
    DatoInvalidoError        Q, D, S, L, n o TW no son fisicamente validos
                             para plantear el problema.
    DisenoNoFactibleError    la combinacion Q/D/S lleva la Forma 1 fuera de
                             rango y devuelve HWi/D <= 0 (ver mas arriba). No
                             es un dato invalido: el dato esta bien y lo que
                             no cierra es el metodo sobre esa combinacion.
    CriterioPendienteError   llega desde 'ke_entrada' o
                             'geometria_control_salida' si alguno se vacia.

Uso
---
    from src.modulos.M4_control import (tirante_critico, control_entrada,
                                    control_salida, hw_gobernante,
                                    resolver_control)

    critico = tirante_critico(Q=1.0, D=0.90)
    entrada = control_entrada(Q=1.0, D=0.90, S=0.005, hds5=concreto.hds5)
    salida  = control_salida(Q=1.0, D=0.90, S=0.005, L=20.0, TW=0.30,
                             n=concreto.n_para_capacidad)
    HW, control = hw_gobernante(entrada, salida)
"""

from __future__ import annotations

import math
import numbers
from typing import NamedTuple, Optional, Tuple

# EL RESOLUTOR SE IMPORTA EN EL PUNTO DE USO (EXT-8, PC-10): `scipy.optimize`
# costaba 230-310 ms en CADA `import cli`, tambien en una corrida que no
# llega a resolver nada (--criterios, la ayuda, la GUI al abrirse). Es el
# mismo `brentq` de siempre --- la referencia del docstring de modulo sigue
# valiendo --- traido la primera vez que hace falta; el segundo import es una
# busqueda en `sys.modules`.

from src import criterios_adoptados as ca
from src.constantes_fisicas import G
from src.constantes_normativas import (FORMA_1, FORMA_2, K_MANNING_SI,
                                   H_O_HW_SOBRE_D_CAUTELA,
                                   H_O_HW_SOBRE_D_MIN, KE_CAJON_C2,
                                   KE_HDS5_C2, KU_SI,
                                   K_FRICCION_SI, Q_LIM_NO_SUMERGIDO,
                                   Q_LIM_SUMERGIDO)
from src.modelos import (CriterioPendienteError, PisoDeCargaEntrada,
                         CIFRAS_FACTOR, CIFRAS_FINA, CIFRAS_MAGNITUD,
                     FormaSeccion, Geometria, Seccion,
                     ConstantesHDS5,
                     ControlEntrada, ControlGobernante,
                     ControlSalida, DatoInvalidoError, DisenoNoFactibleError,
                     LimiteNumericoError, Magnitud, Material,
                     MOTIVO_METODO_NO_EVALUABLE, PerfilLamina, RegimenBarril,
                     RegimenEntrada,
                     ResultadoHidraulico, TiranteCritico, TipoDePerfil,
                     TipoDeVeredicto,
                     TiranteNormal, TransicionEntrada, Umbral, Veredicto, paso)
from src.modulos.M2_material import CRITERIO_N_CELDAS_CAJON, numero_de_celdas
from src.modulos.M3_hidraulica import geometria, resolver_manning
from src.tolerancias import (PASOS_PERFIL_LAMINA, TOL_ASINTOTA_PERFIL,
                             TOL_BRENT, TOL_UMBRAL_NORMATIVO)

NUMERAL_CRITICO = "4.2.1"
NUMERAL_ENTRADA = "4.2"
NUMERAL_SALIDA = "4.3"

CRITERIO_KE = "ke_entrada"
# EL ke DEL MARCO ES OTRO CRITERIO, no el mismo con otro valor (regla
# vinculante #11 de la Familia C). La Tabla C.2 tiene familia propia para el
# cajon -- «Box, Reinforced Concrete», siete filas bajo cuatro rotulos de
# agrupacion -- y la trampa es que para la embocadura a ras sin aletas el
# numero COINCIDE con el del tubo: 0.5 en las dos. El valor acertaria por
# casualidad y la cita seria falsa, que es el precedente NOR-HID-01.
CRITERIO_KE_CAJON = "ke_entrada_cajon"
CRITERIO_GEOMETRIA_SALIDA = "geometria_control_salida"
CRITERIO_TRANSICION = "metodo_transicion_hds5"
# EL VACIO DE PC-03 (PF-1): que se adopta cuando la correccion por pendiente
# deja la carga a la entrada en cero o bajo cero. Ver
# `_resolver_hw_fuera_de_rango` y `pendiente_limite_de_signo`.
CRITERIO_HW_FUERA_DE_RANGO = "hw_entrada_fuera_de_rango"
PISO_ENERGIA_CRITICA = "energia_critica"
PISO_DESCARTAR = "descartar"
CRITERIO_FRACCION_LLENA = "fraccion_llena_mayor_parte"   # E-A, paso 4.3c

# EL BRACKET DE THETA SE FUE A `SeccionCircular.bracket_llenado()` en C1,
# igual que en M3: es la seccion la que sabe sobre que parametro se la
# recorre. M4 lo pide y no lo construye.


# ---------------------------------------------------------------------------
# Validacion de entrada
# ---------------------------------------------------------------------------

def _validar_positivo(nombre: str, dato: float, motivo: str) -> None:
    # Forma MAT-D13 (PC-05): la condicion se escribe EN POSITIVO Y NEGADA.
    # `if dato <= 0` era permeable a NaN -- falso frente a `<=` igual que
    # frente a `>` -- y un NaN por la API interna salia como ValueError de
    # brentq, fuera de ErrorProyecto. Un `inf` pasa aqui a proposito: es
    # positivo, y quien lo detiene es la guardia de finitud a la SALIDA.
    if not dato > 0:
        raise DatoInvalidoError(nombre, valor=dato, motivo=motivo)


def _validar_ke(ke: object, campo: str) -> float:
    """
    Un coeficiente de perdida de entrada: real, no bool, finito y `not ke >= 0`
    (EXT-V-02, PC-02). La Tabla C.2 del HDS-5 recorre 0.2 a 0.9; el cero es
    una embocadura sin perdida y se admite; un ke negativo RESTA carga --
    `--declarar ke_entrada=-50` daba HW_salida = -7.668 m con el punto
    dimensionado y cero incumplidas -- y no es un coeficiente. 'texto',
    True y [1, 2] salian como TypeError, fuera de ErrorProyecto.
    """
    if not isinstance(ke, numbers.Real) or isinstance(ke, bool):
        raise DatoInvalidoError(
            campo, valor=ke,
            motivo=f"el coeficiente de perdida de entrada ke tiene que ser un "
                   f"numero real; lo declarado ({ke!r}) no lo es. La Tabla "
                   "C.2 del HDS-5 lo tabula entre 0.2 y 0.9")
    if not math.isfinite(ke):
        raise DatoInvalidoError(
            campo, valor=ke,
            motivo="el coeficiente de perdida de entrada ke no es finito")
    if not ke >= 0:
        raise DatoInvalidoError(
            campo, valor=ke,
            motivo=f"el coeficiente de perdida de entrada ke no puede ser "
                   f"negativo ({ke!r}): restaria carga en vez de perderla y "
                   "bajaria el HW de salida. La Tabla C.2 del HDS-5 lo "
                   "tabula entre 0.2 y 0.9; el cero es una embocadura sin "
                   "perdida. La condicion se escribe negada (`not ke >= 0`) "
                   "para que un NaN caiga del lado seguro (MAT-D13)")
    return float(ke)


def _validar_Q_D(Q: float, seccion: Seccion) -> None:
    _validar_positivo("Q", Q, "el caudal debe ser positivo")
    # EL NOMBRE DEL DATO LO PONE LA SECCION (anotacion A-4 de §16.4, cerrada
    # en C4). Aqui estaba escrita la SEGUNDA copia de la pareja
    # ("D", "el diametro debe ser positivo") -- la primera vivia en
    # `M3._validar_parametros` -- y las dos se imprimen, en la memoria y en el
    # JSON. La circular sigue diciendo exactamente eso; un marco dice "B" y
    # "H", que es como se llaman sus datos. La razon completa esta en M3.
    seccion.exigir_dimensiones_positivas()


# ---------------------------------------------------------------------------
# Pieza 1 - Tirante critico (Sec. 4.2.1)
# ---------------------------------------------------------------------------

def area_llena(seccion: Seccion) -> float:
    """
    Area de la seccion LLENA. La usan q* (Sec. 4.2) y el control de salida
    (Sec. 4.3).

    La formula ya no vive aqui: la aporta la seccion, que es quien sabe su
    forma. En la circular sigue siendo pi*D^2/4, identica al ultimo bit.
    """
    return seccion.area_llena


def radio_hidraulico_lleno(seccion: Seccion) -> float:
    """
    Radio hidraulico de la seccion LLENA (Sec. 4.3). Igual que arriba: lo
    aporta la seccion. En la circular sigue siendo D/4.
    """
    return seccion.radio_hidraulico_lleno


def _residuo_critico(seccion: Seccion, theta: float, Q: float) -> float:
    """
    Residuo de la ecuacion del tirante critico (Sec. 4.2.1), escrito como

        A^3/T - Q^2/g = 0

    que es la MISMA ecuacion que Q^2*T/(g*A^3) = 1 multiplicada por A^3/T.

    La reescritura no es cosmetica, es numerica: la forma literal de la hoja
    de ruta divide entre A^3, y en el extremo inferior del intervalo de Brent
    (theta = 1e-9 rad) el area vale CERO en aritmetica de doble precision --
    no un numero muy chico: cero exacto, porque theta - sen(theta) ~ theta^3/6
    ~ 1.7e-28 queda por debajo del ultimo bit de theta y la resta se cancela
    entera. Evaluar el residuo literal ahi es una division por cero, no una
    tendencia a infinito. Multiplicando por A^3/T la singularidad desaparece
    (T no se anula en ese extremo) y el residuo queda monotono CRECIENTE, de
    -Q^2/g en la seccion vacia a +infinito en la llena. La raiz es la misma.
    """
    geom = geometria(seccion, theta)
    # Q^2 DESBORDA ANTES QUE NADA MAS DE ESTA LINEA (MAT-O18, mitad alcanzable).
    # `Q_m3s` no tiene techo en dominios.py -- y no se le puede inventar uno,
    # igual que a las cotas de 7.B --, de modo que un Q >= ~1.34e154 llega
    # entero desde un CSV que pasa las tres validaciones de M0 y `Q ** 2`
    # lanza OverflowError. Medido: Q = 1e154 todavia cae como
    # DatoInvalidoError por la guarda de bracket de `tirante_critico`, y
    # Q = 1e155 revienta AQUI, en crudo, fuera de ErrorProyecto.
    #
    # La ficha de MAT-O18 lo situaba en q*^2 y lo clasificaba "solo alcanzable
    # inyectando": las dos cosas son falsas. Esta en `Q ** 2` de este residuo,
    # y se alcanza desde el CSV. Es la TERCERA correccion a esa ficha; S16 ya
    # habia encontrado dos.
    #
    # `float.__pow__` lanza OverflowError donde `Q * Q` daria `inf`: se atrapa
    # y se traduce, en vez de reescribir la potencia, porque el numero no
    # existe de las dos formas y lo que hay que arreglar es el dato.
    try:
        q_al_cuadrado = Q ** 2  # literal-ok: exponente de Q^2 = g*A^3/T, Sec. 4.2.1
    except OverflowError:
        raise LimiteNumericoError(
            "Q", valor=Q,
            motivo=f"Q^2 no cabe en doble precision (Q = {Q!r} m3/s), y sin "
                   f"Q^2 no hay residuo de {NUMERAL_CRITICO} que resolver. No "
                   f"es un caudal fuera de rango -- 'Q_m3s' solo exige ser "
                   f"positivo, y ponerle un techo seria inventar un valor de "
                   f"proyecto --, es un caudal cuyo cuadrado no es "
                   f"representable. Revisa si la celda perdio el separador "
                   f"decimal o vino en otra unidad",
        ) from None
    return geom.A ** 3 / geom.T - q_al_cuadrado / G  # literal-ok: A^3/T = Q^2/g, Sec. 4.2.1


def _critico_por_brent(Q: float, seccion: Seccion) -> Geometria:
    """
    La via de siempre: Brent sobre el parametro propio de la seccion.

    Es el cuerpo que `tirante_critico` tenia entero hasta C4, letra por letra
    y con sus dos guardias. Se separo para que la seccion que SI despeja el
    critico no tenga que pasar por aqui, no para cambiarlo: la circular
    recorre exactamente el mismo codigo y converge al mismo bit.

    SUS DOS MENSAJES SIGUEN NOMBRANDO «theta», «(0, 2*pi)» y «D», y no es un
    descuido del renombre: la UNICA seccion que llega hasta aqui es la que NO
    despeja su critico, y hoy esa es la circular. Los dos textos se imprimen
    --`servicio._bloqueo` los publica-- y generalizarlos sin una segunda forma sin
    solucion cerrada seria cambiar salida por una hipotesis. Quien traiga una
    tercera forma sin despeje tiene que generalizarlos con ella delante; lo
    encontro la auditoria de C4 y queda dicho aqui, que es donde se lee.
    """

    def f(theta: float) -> float:
        return _residuo_critico(seccion, theta, Q)

    llenado_min, llenado_max = seccion.bracket_llenado()
    f_min, f_max = f(llenado_min), f(llenado_max)
    if not (f_min < 0 < f_max):
        # Inalcanzable con aritmetica finita para un Q y un D de proyecto: se
        # deja como guarda explicita en vez de dejar que brentq lance
        # ValueError, que la GUI no sabria clasificar (ErrorProyecto o crash).
        raise DatoInvalidoError(
            "Q", valor=Q,
            motivo=f"el residuo de {NUMERAL_CRITICO} no cambia de signo en "
                   f"(0, 2*pi) para D={seccion.altura}: no hay tirante critico que "
                   f"resolver",
        )

    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    theta_critico = brentq(f, llenado_min, llenado_max, xtol=TOL_BRENT)
    geom = geometria(seccion, theta_critico)
    # SIS-G-02. LA GUARDA DE ARRIBA PROTEGE EL BRACKET DE BRENT, NO ESTA
    # DIVISION. Son dos cosas distintas y hasta aqui solo estaba la primera:
    # el residuo cruza el cero limpiamente, brentq converge, y el theta al que
    # converge puede estar POR DEBAJO del umbral en que el area se cancela.
    #
    # El umbral esta MEDIDO, no supuesto: A = (D^2/8)(theta - sen theta) vale
    # exactamente 0.0 para theta <= 2.149e-08, porque theta - sen(theta) ~
    # theta^3/6 cae bajo el ultimo bit de theta y la resta se cancela entera.
    # Con D = 0.90 m eso lo produce un Q de 1e-33 (Q = 1e-32 todavia da
    # theta = 2.979e-08 y area positiva), y sin esta guarda la division
    # siguiente lanzaba ZeroDivisionError en crudo, fuera de ErrorProyecto.
    #
    # ES LA MISMA CANCELACION QUE `_residuo_critico` YA ESQUIVA, y ahi esta lo
    # llamativo: el modulo la conocia y se defendia de ella EN EL RESIDUO --
    # por eso lo escribe como A^3/T y no dividiendo entre A^3 --, pero no en
    # la division de despues del solver.
    #
    # La condicion va EN POSITIVO Y NEGADA (`not geom.A > 0`, no
    # `geom.A <= 0`) siguiendo la plantilla de MAT-D13: un NaN es falso frente
    # a `<=` igual que frente a `>`, y escrita del otro modo se colaria.
    if not geom.A > 0:
        raise LimiteNumericoError(
            "Q", valor=Q, motivo=(
                f"el par (Q = {Q!r} m3/s, D = {seccion.altura!r} m) degenera: "
                f"el tirante "
                f"critico existe -- Brent converge a theta = "
                f"{theta_critico!r} rad -- pero a ese theta el area de la "
                f"seccion se anula en doble precision, porque "
                f"theta - sen(theta) queda por debajo del ultimo bit de theta "
                f"y la resta se cancela entera (ocurre desde "
                f"theta <= 2.149e-08). Sin area no hay velocidad critica que "
                f"calcular. No es un caudal fuera de rango: 'Q_m3s' solo "
                f"exige ser positivo. Revisa si la celda perdio digitos o si "
                f"el caudal vino en otra unidad"
            ),
        )
    return geom


def _critico_cerrado(Q: float, seccion: Seccion, llenado: float) -> Geometria:
    """
    La via de la solucion cerrada, con la guardia que la cerrada NO retira.

    La seccion ya devolvio su parametro propio en estado critico y ya guardo
    su propia aritmetica (desborde de q^2, y_c no finito, y_c nulo). Lo que
    queda es lo que no puede guardar sola: que el AREA construida con ese
    tirante sea utilizable. Es alcanzable y esta medido -- con B = Q = 5e-324
    el tirante critico vale 0.4671363512679737 m y el area B*y_c se anula en
    doble precision --, y sin esta guardia la division de `tirante_critico`
    lanzaria ZeroDivisionError en crudo, fuera de `ErrorProyecto`.

    Condicion en positivo y negada (plantilla de MAT-D13) y mensaje que nombra
    al PAR, no a un solo dato: ninguno de los dos esta fuera de rango.
    """
    geom = geometria(seccion, llenado)
    if not geom.A > 0:
        raise LimiteNumericoError(
            "Q", valor=Q, motivo=(
                f"el par (Q = {Q!r} m3/s, seccion {seccion.etiqueta()}) "
                f"degenera: el tirante critico sale de la solucion cerrada "
                f"con un valor positivo -- {geom.y!r} m -- y aun asi el area "
                f"de la seccion a ese tirante se anula en doble precision. "
                f"Sin area no hay velocidad critica que calcular. Cada dato "
                f"cumple su rango por separado; lo que no cabe es la "
                f"operacion que los combina"),
        )
    return geom


def tirante_critico(Q: float, seccion: Seccion) -> TiranteCritico:
    """
    Tirante critico de la seccion (Sec. 4.2.1), por la via que la seccion
    tenga: cerrada si la despeja, y Brent si no.

        Q^2 * T / (g * A^3) = 1

    LA SECCION DECIDE, Y M4 NO PREGUNTA DE QUE FORMA ES. `llenado_critico_
    cerrado` devuelve `None` cuando la ecuacion es trascendente en el
    parametro propio --la circular, donde A = (D^2/8)(theta - sen theta) y
    T = D*sen(theta/2)-- y devuelve el valor cuando se despeja --el marco,
    donde T = B es constante y y_c = (q^2/g)^(1/3) con q = Q/B--. Un
    `isinstance` aqui seria la forma de la seccion cableada en el modulo de
    calculo, que es justo lo que C1 retiro.

    Devuelve `TiranteCritico` con la geometria critica, la velocidad critica
    V_c = Q/A_c y la energia especifica critica H_c = y_c + V_c^2/(2g), que es
    lo que consume la Forma 1 del control de entrada. `cerrado` dice por cual
    de las dos vias se resolvio: lo necesita la traza de la memoria, que tiene
    que imprimir la formula que de verdad se uso.

    Por la via de Brent siempre existe solucion para Q > 0 (el residuo cruza
    el cero una sola vez sobre el intervalo), de modo que esta funcion no
    tiene el caso "None" de `M3.tirante_normal`: un Q desmedido no deja al
    solver sin raiz, solo acerca y_c a D, y eso lo juzga V1 (y/D <= 0.75), no
    este solver.
    """
    _validar_Q_D(Q, seccion)
    llenado_cerrado = seccion.llenado_critico_cerrado(Q, G)
    if llenado_cerrado is None:
        geom = _critico_por_brent(Q, seccion)
    else:
        geom = _critico_cerrado(Q, seccion, llenado_cerrado)
    V_c = Q / geom.A
    return TiranteCritico(
        geometria=geom,
        V=V_c,
        H_c=geom.y + V_c ** 2 / (2 * G),
        cerrado=llenado_cerrado is not None,
    )


# ---------------------------------------------------------------------------
# Pieza 2 - Control de entrada, HDS-5 (Sec. 4.2)
# ---------------------------------------------------------------------------

def caudal_adimensional(Q: float, seccion: Seccion) -> float:
    """
    q* = Ku*Q / (A_llena * D^0.5), con Ku = 1.811 (SI), Sec. 4.2.

    El area es la de la seccion LLENA, no la del tirante: q* es un caudal
    adimensional de la abertura, no del flujo (asi lo fija el caso patron
    CP-5, que da A_llena = pi*D^2/4 = 0.63617 m2 para D = 0.90 m).
    """
    _validar_Q_D(Q, seccion)
    return KU_SI * Q / (seccion.area_llena * math.sqrt(seccion.altura))


def _hw_sobre_D_no_sumergido(q_estrella: float, H_c: float, seccion: Seccion,
                             S: float, hds5: ConstantesHDS5) -> float:
    """
    HWi/D no sumergido, num. A.2.1 de HDS-5 (q* <= 3.5). DOS FORMAS:

        Forma 1   HWi/D = H_c/D + K*(q*)^M + Ks*S          ec. (A.1)
        Forma 2   HWi/D = K*(q*)^M                         ec. (A.2)

    LA FORMA 2 NO LLEVA EL TERMINO Ks*S. Verificado en esta sesion contra
    `normas/hif12026.pdf`, pag. impresa A.2 (PDF 191): la ec. (A.2) se imprime
    como HWi/D = K[Ku*Q/(A*D^0.5)]^M y ahi termina. El contraste esta en la
    MISMA pagina y es lo que cierra la lectura: la ec. (A.3), sumergida, si
    escribe «+ Y + Ks*S», y la (A.1) de la pagina anterior tambien lleva su
    «+ Ks*S». No es que la (A.2) lo omita por brevedad: es que no lo tiene.

    Cual de las dos se usa NO LO ELIGE EL PROYECTISTA: lo fija la carta de la
    Tabla A.1 a la que pertenece la seccion, en su columna «Equation Form».
    El propio num. A.2.1 explica por que hay dos -- «Form (1) is based on the
    specific head at critical depth... Form (2) is an exponential equation
    similar to a weir equation... Form (2) is easier to apply and is the only
    documented form of equation for some of the inlet control equations» --.

    LO QUE EL NUM. A.3 **NO** DICE, y esta redaccion llego a decir que si:
    NO prohibe cruzar coeficientes entre FORMAS DE ECUACION. Lo que prohibe es
    cruzarlos entre FORMAS GEOMETRICAS -- «rectangular (box) shapes» frente a
    «nonrectangular» --, que es otra cosa. La Tabla A.1 lo demuestra sola:
    forma y geometria son ORTOGONALES en ella; «Rect. Box Concrete» aparece
    con Forma 1 y con Forma 2, y «Circular» tambien. Quien dice que constante
    va con que ecuacion es la COLUMNA «Equation Form», fila por fila, y nada
    mas.

    POR QUE IMPORTA, CON EL NUMERO -- y son DOS errores distintos, con
    direccion distinta, que este docstring confundia hasta D9:

    (1) Copiar la ec. (A.1) ENTERA y cambiarle las constantes por las de una
    carta de Forma 2 arrastra H_c/D y Ks*S, y el que domina es H_c/D: el HW
    sale MAYOR que el real (+91 % medido en I3 sobre el marco de la linea
    base, 2.00 x 1.50 m, Q = 6 m3/s, S = 0.004, Carta 10 escala 1: 3.047 m
    frente a 1.592 m), o sea sobrediseño y falsos no-factibles. Es el error
    que `DIS-HR-FORMAS-HDS5` registro contra la v8 y que F4.FORMA_HDS5
    describe.

    (2) Sumar SOLO el Ks*S a la ec. (A.2) -- la mutacion que la primera
    redaccion de `modelos.ConstantesHDS5` habia escrito --: con Ks = -0.5 ese
    termino RESTA y el HW sale MENOR que el real, del lado NO conservador.
    Medido sobre la Carta 9 escala 1 (K = 0.510, M = 0.667) con un cajon de
    2.00 x 2.00 m, Q = 8 m3/s y S = 0.03: 1.910 m contra 1.880 m, 30 mm, y la
    diferencia crece lineal con la pendiente. El caso patron
    CP5D_FORMA2_KS_ESPUREO fija este segundo para que un regreso rompa un
    test. Ninguna guardia de signo detecta a ninguno de los dos: el resultado
    sigue siendo positivo y plausible.
    """
    directo = hds5.K * q_estrella ** hds5.M
    if hds5.forma == FORMA_2:
        return directo
    if hds5.forma != FORMA_1:
        raise DatoInvalidoError(
            "forma", valor=hds5.forma,
            motivo=("la columna «Equation Form» de la Tabla A.1 solo toma los "
                    "valores 1 y 2, y HDS-5 no define ninguna tercera forma "
                    "de la ecuacion no sumergida. Una carta con otra forma no "
                    "es una carta de esta tabla"))
    return H_c / seccion.altura + directo + hds5.Ks * S


def _hw_sobre_D_sumergido(q_estrella: float, S: float,
                          hds5: ConstantesHDS5) -> float:
    """
    HWi/D = c*(q*)^2 + Y + Ks*S, regimen sumergido (q* >= 4.0), ec. (A.3).

    NO SE BIFURCA POR FORMA, y esa es una lectura de la fuente y no un olvido:
    la division en dos formas la hace el num. A.2.1, que es el de las
    ecuaciones NO SUMERGIDAS. La sumergida es el num. A.2.2 y tiene UNA sola
    ecuacion, la (A.3), cuyo encabezado remite a las variables de A.2.1 sin
    distinguir forma; y la Tabla A.1 da c e Y para TODAS sus cartas, sean de
    Forma 1 o de Forma 2. Verificado en la pag. impresa A.2 (PDF 191).

    Y esta si lleva Ks*S -- comprobado en la misma pagina, no deducido de que
    lo lleve la (A.1) --: es la confusion numeral/pagina que NOR-HDS-01 ya
    cerro una vez y que C2 volvio a encontrar al citar el num. A.3.
    """
    return hds5.c * q_estrella ** 2 + hds5.Y + hds5.Ks * S


def _regimen(q_estrella: float) -> RegimenEntrada:
    """Rama de Sec. 4.2 segun q*, con los limites [N] 3.5 y 4.0."""
    if q_estrella <= Q_LIM_NO_SUMERGIDO:
        return RegimenEntrada.NO_SUMERGIDO
    if q_estrella >= Q_LIM_SUMERGIDO:
        return RegimenEntrada.SUMERGIDO
    return RegimenEntrada.TRANSICION


def pendiente_limite_de_signo(Q: float, seccion: Seccion, hds5: ConstantesHDS5,
                              critico: Optional[TiranteCritico] = None
                              ) -> Optional[float]:
    """
    S*: la pendiente a partir de la cual la ecuacion de control de entrada
    deja de entregar carga para este Q y esta seccion (MAT-D10, PC-03).

    HWi/D es lineal en S en cada rama --- pendiente Ks en la (A.1) y la
    (A.3), 0 en la (A.2), y peso*Ks en la recta de transicion bajo Forma 2
    ---, de modo que S* = X/(-m), con X el HWi/D sin el termino de pendiente
    y m la pendiente de la rama. Para la Forma 1 no sumergida es el
    S* = 2*(H_c/D + K*(q*)^M) que el docstring del modulo escribe con
    Ks = -0.5. Devuelve None cuando la rama no decrece con S (Forma 2 no
    sumergida, o una carta con Ks >= 0): ahi no hay limite que citar, y no
    se devuelve `inf` porque el censo de los dos `inf` deliberados del
    repositorio no admite un tercero.

    S* NO CRECE CON D BAJO FORMA 1: bajan H_c/D y q* a la vez con Ks*S fijo,
    de modo que si la carta se cae en el diametro minimo del catalogo ninguno
    mayor la levanta, y por eso descartar el material entero bajo «descartar»
    es correcto para las tres cartas circulares del catalogo, que son Forma 1
    (`tests/test_pf1_hw_fuera_de_rango.py` y P9 lo fijan). BAJO FORMA 2 NO
    ES UNA PROPIEDAD GENERAL, y lo midio el auditor adversarial de PF-1: al
    crecer D el q* baja y la rama pasa a la no sumergida de la (A.2), que no
    lleva Ks*S, de modo que S* pasa a None --- la carta deja de poder caerse
    ---. Lo que acota el alcance de todo esto es el dominio del dato: con
    S <= `dominios.S_CAUCE_MAX` (1.0) solo la Forma 1 no sumergida puede
    dispararse, porque en la rama sumergida y en la transicion S* vale al
    menos (c*4^2 + Y)/|Ks| ~ 2.6 para toda carta transcrita.
    """
    _validar_Q_D(Q, seccion)
    if critico is None:
        critico = tirante_critico(Q, seccion)
    q_estrella = caudal_adimensional(Q, seccion)
    sin_pendiente, _, _, m = _hw_sobre_D_y_pendiente(
        q_estrella, critico, seccion, S=0, hds5=hds5)
    if not m < 0:
        return None
    return sin_pendiente / (-m)


def _hw_sobre_D_y_pendiente(q_estrella: float, critico: TiranteCritico,
                            seccion: Seccion, S: float, hds5: ConstantesHDS5
                            ) -> Tuple[float, RegimenEntrada,
                                       Optional[TransicionEntrada], float]:
    """
    (HWi/D, rama, recta de transicion o None, dHWi/D / dS) para un q* y una
    S. Es el cuerpo de las tres ramas de `control_entrada`, separado para que
    `pendiente_limite_de_signo` evalue las MISMAS ecuaciones --- con S = 0,
    que aqui se admite porque la positividad de S la exige `control_entrada`
    y no las ecuaciones ---. La cuarta salida es la pendiente de la rama en
    S, que es lo unico que S* necesita ademas del numero.
    """
    regimen = _regimen(q_estrella)
    transicion = None
    if regimen is RegimenEntrada.NO_SUMERGIDO:
        HW_sobre_D = _hw_sobre_D_no_sumergido(q_estrella, critico.H_c, seccion, S, hds5)
        m = hds5.Ks if hds5.forma == FORMA_1 else 0
    elif regimen is RegimenEntrada.SUMERGIDO:
        HW_sobre_D = _hw_sobre_D_sumergido(q_estrella, S, hds5)
        m = hds5.Ks
    else:
        # Interpolacion lineal entre los EXTREMOS del rango de validez de cada
        # forma, no entre las dos formas evaluadas en el q* real: dentro de la
        # transicion ninguna de las dos ecuaciones vale, y extrapolarlas seria
        # usarlas fuera de su dominio de ajuste. Asi la curva empalma continua
        # en q* = 3.5 y en q* = 4.0.
        #
        # El criterio se invoca AQUI y no al entrar en la funcion: asi M11
        # declara la simplificacion solo si algun punto cae de verdad en la
        # transicion, y no en las corridas donde todos los q* quedan fuera.
        metodo = ca.valor(CRITERIO_TRANSICION)
        if metodo != "interpolacion_lineal_entre_extremos":
            raise DatoInvalidoError(
                CRITERIO_TRANSICION, valor=metodo,
                motivo="M4 solo implementa la recta entre los extremos de "
                       "validez. Reproducir la curva tangente del HDS-5 exige "
                       "programar otro procedimiento, no cambiar este valor",
            )
        # EL EXTREMO INFERIOR ES EL DE Q_lo, EL CAUDAL DE q* = 3.5 (EXT-M-04),
        # y bajo Forma 1 se evalua con el H_c de ESE caudal: es lo que hace
        # que los dos extremos sean fijos para un D, una S y una carta, y
        # que la recta sea una recta. Bajo Forma 2 la (A.2) no lleva H_c y
        # no hay segundo critico que resolver.
        Q_lo = Q_LIM_NO_SUMERGIDO * seccion.area_llena * math.sqrt(seccion.altura) / KU_SI
        H_c_lo = (tirante_critico(Q_lo, seccion).H_c
                  if hds5.forma == FORMA_1 else None)
        extremo_inferior = _hw_sobre_D_no_sumergido(
            Q_LIM_NO_SUMERGIDO, H_c_lo, seccion, S, hds5)
        extremo_superior = _hw_sobre_D_sumergido(Q_LIM_SUMERGIDO, S, hds5)
        peso = ((q_estrella - Q_LIM_NO_SUMERGIDO)
                / (Q_LIM_SUMERGIDO - Q_LIM_NO_SUMERGIDO))
        HW_sobre_D = extremo_inferior + peso * (extremo_superior - extremo_inferior)
        transicion = TransicionEntrada(
            Q_lo=Q_lo, H_c_lo=H_c_lo,
            HW_lo=extremo_inferior * seccion.altura,
            HW_hi=extremo_superior * seccion.altura,
            peso=peso)
        # Bajo Forma 1 los dos extremos llevan Ks*S y la recta hereda la
        # pendiente entera; bajo Forma 2 solo el superior, y la hereda por
        # su peso.
        m = hds5.Ks if hds5.forma == FORMA_1 else peso * hds5.Ks
    return HW_sobre_D, regimen, transicion, m


def _resolver_hw_fuera_de_rango(HW_sobre_D: float, m: float, *, Q: float,
                                S: float, seccion: Seccion, q_estrella: float,
                                hds5: ConstantesHDS5, critico: TiranteCritico
                                ) -> Tuple[float, Optional[PisoDeCargaEntrada]]:
    """
    Resuelve el HWi/D que la correccion por pendiente Ks*S deja en cero o
    bajo cero (MAT-D10): una lamina de agua por debajo del fondo del
    conducto, que no existe. Sec. 4.2 no acota ese termino, la recta no
    tiene tope, y ni la hoja de ruta ni el HDS-5 dicen que hacer ahi.

    HASTA PF-1 ESTO ERA `_exigir_hw_no_negativo` Y LANZABA
    `DisenoNoFactibleError`, con un argumento que sigue siendo cierto en su
    mitad: el dato no esta mal (una pendiente medida en campo no se
    «corrige»: no es DatoInvalidoError) y adoptar un piso EN EL CODIGO seria
    rellenar un vacio en silencio. Lo que el argumento no decia es que la
    constitucion tiene una regla para ese vacio, y no es descartar: es la
    entrada con valor=None, etiqueta [A] y la excepcion que detiene el
    calculo hasta que el proyectista declare. PC-03 lo midio por el otro
    lado: el descarte era DEFINITIVO --- un cruce trivialmente factible salia
    como no factible --- y MUDO --- el Bloqueo viajaba con `criterio=None` y
    `M11.criterios_bloqueantes` lo saltaba ---. La clase elegida y por que no
    es `MetodoNoEvaluableError` estan en la ficha PF-1-01.

    LA HOJA DE RUTA DECIA OTRA COSA Y SE ENMENDO EN PF-1: la nota de MAT-D10
    de la v8 §4.2 escribia «`M4.control_entrada()` rechaza ese resultado con
    `DisenoNoFactibleError`. Es un rechazo, no un piso», que era la conducta
    hasta PF-1; la enmienda (nota «Corregido (PF-1, PC-03)» en esa seccion)
    describe la de ahora. No es una discrepancia normativa --- HDS-5 no dice
    nada del caso --- sino la descripcion del software en la hoja, y por
    eso se enmienda la hoja y no se abre una `DIS-*`.

    EL PISO ACOTA EL SIGNO, NO IMPONE H_c COMO MINIMO: por debajo de S* la
    ecuacion puede devolver una carga positiva menor que H_c (con D = 0.90 y
    Q = 0.05: HW = 0.035 m a S = 0.30 frente a H_c = 0.169 m) y se acepta tal
    cual, como antes de PF-1; el criterio solo gobierna el caso en que la
    ecuacion no entrega carga. Por eso la carga NO es continua en S*, y la
    ficha del criterio lo dice en su `justificacion`.

    Tres salidas, las tres con el par (Q, S) culpable y el S* de la carta:
      * sin declarar        -> CriterioPendienteError sobre
                               `hw_entrada_fuera_de_rango` (Bloqueo con criterio,
                               visible en la pestaña 4);
      * «energia_critica»   -> HW = H_c, la energia especifica critica del paso
                               4.2.1, y el `PisoDeCargaEntrada` que la memoria
                               imprime con el HWi/D que la ecuacion devolvio;
      * «descartar»         -> DisenoNoFactibleError, la conducta anterior, y
                               `MD.disenar_material` descarta el material entero
                               --- con razon: HWi/D decrece con D, ver
                               `pendiente_limite_de_signo` ---.

    La comparacion se escribe en positivo y negada (forma MAT-D13): un NaN
    tampoco pasa.
    """
    if HW_sobre_D > 0:
        return HW_sobre_D, None
    S_limite = S - HW_sobre_D / m if m < 0 else None
    caso = (f"D={seccion.altura} m (altura del barril), Q={Q} m3/s (por "
            f"barril), S={S} m/m, q*={q_estrella:.5f}: "
            f"la correccion por pendiente Ks*S (Ks={hds5.Ks}) devuelve "
            f"HWi/D={HW_sobre_D:.5f}, una carga a la entrada nula o negativa; "
            f"la ecuacion deja de entregar carga desde S*="
            + (f"{S_limite:.5f} m/m" if S_limite is not None else "(sin limite)"))
    try:
        adoptado = ca.valor(CRITERIO_HW_FUERA_DE_RANGO)
    except CriterioPendienteError as exc:
        raise CriterioPendienteError(
            exc.clave, concepto=exc.concepto,
            fuente=f"{exc.fuente}. Caso: {caso}") from None
    if adoptado == PISO_ENERGIA_CRITICA:
        return critico.H_c / seccion.altura, PisoDeCargaEntrada(
            criterio=CRITERIO_HW_FUERA_DE_RANGO, adoptado=adoptado,
            HW_sobre_D_formula=HW_sobre_D, S_limite=S_limite)
    if adoptado == PISO_DESCARTAR:
        raise DisenoNoFactibleError(
            motivo=f"control de entrada ({NUMERAL_ENTRADA}): {caso}. El HDS-5 "
                   f"formula esa correccion para pendientes de alcantarilla "
                   f"corrientes y aqui quedo extrapolada fuera de rango; "
                   f"'{CRITERIO_HW_FUERA_DE_RANGO}' esta declarado "
                   f"«{PISO_DESCARTAR}», de modo que no se adopta ningun piso "
                   f"y esta combinacion se descarta. Lo que la resolveria es "
                   f"un procedimiento valido para pendientes de ese orden, no "
                   f"otro diametro: HWi/D decrece al crecer D",
        )
    # Segunda linea (EXT-5): la puerta ya rechaza lo que no es del conjunto
    # cerrado, y esto defiende lo que llegue por otra via.
    raise DatoInvalidoError(
        CRITERIO_HW_FUERA_DE_RANGO, valor=adoptado,
        motivo=f"solo admite «{PISO_ENERGIA_CRITICA}» o «{PISO_DESCARTAR}»")


def control_entrada(Q: float, seccion: Seccion, S: float, hds5: ConstantesHDS5,
                    critico: Optional[TiranteCritico] = None) -> ControlEntrada:
    """
    Carga a la entrada bajo control de entrada (Sec. 4.2), HDS-5, Tabla A.1.

    Tres ramas segun el caudal adimensional q* = Ku*Q/(A_llena*D^0.5), y la
    primera tiene DOS FORMAS segun la carta (columna «Equation Form»):

        q* <= 3.5   HWi/D = H_c/D + K*(q*)^M + Ks*S    (Forma 1, ec. A.1)
                    HWi/D = K*(q*)^M                   (Forma 2, ec. A.2)
        q* >= 4.0   HWi/D = c*(q*)^2 + Y + Ks*S        (sumergido, ec. A.3;
                                                        comun a las dos formas)
        3.5 < q* < 4.0   interpolacion lineal entre el valor de la primera en
                    q* = 3.5 -- para el caudal Q_lo de ese q*, y bajo Forma 1
                    con H_c(Q_lo) -- y el de la segunda en q* = 4.0

    La tercera rama NO reproduce el HDS-5: la curva tangente del HDS-5 se
    sustituye por una recta, y esa sustitucion es el criterio [C]
    'metodo_transicion_hds5', que se invoca al entrar en la rama (ver el
    docstring del modulo). Las dos ramas extremas si son las ecuaciones
    literales de HDS-5 -- pero de su num. A.2, ecs. (A.1) a (A.3), pags.
    impresas A.1-A.2, NO de la Tabla A.1 (NOR-HDS-03): de esa tabla, que esta
    en la pag. A.8, salen unicamente las constantes K, M, c e Y de cada
    carta.

    El termino Ks*S no se omite DONDE LA ECUACION LO TIENE, que desde C3 no
    es en todas partes: la (A.1) y la (A.3) lo llevan, y la (A.2) NO. Este
    parrafo decia «no se omite» a secas, y era cierto hasta que existio la
    Forma 2 -- en cuya rama no sumergida se omite, y DEBE omitirse --. Ks
    sigue siendo campo obligatorio de `ConstantesHDS5`, porque una carta sin
    el no se puede armar y porque la rama sumergida lo usa siempre, sea cual
    sea la forma.

    `critico` es opcional: si no se pasa, se resuelve aqui con la pieza 1. Se
    admite inyectarlo para no repetir Brent cuando el orquestador ya lo tiene
    (y para poder probar esta pieza sin depender de la anterior).
    """
    _validar_Q_D(Q, seccion)
    _validar_positivo("S", S, "la pendiente del conducto debe ser positiva")

    if critico is None:
        critico = tirante_critico(Q, seccion)

    q_estrella = caudal_adimensional(Q, seccion)
    HW_sobre_D, regimen, transicion, m = _hw_sobre_D_y_pendiente(
        q_estrella, critico, seccion, S, hds5)

    # Una sola vez, despues de las tres ramas, porque la resolucion es la
    # misma. Bajo Forma 2 no sumergida no puede dispararse -- K*(q*)^M > 0
    # siempre para q* > 0 --; en las demas ramas el termino Ks*S entra, y de
    # ahi puede venir el numero negativo. Ver `_resolver_hw_fuera_de_rango`
    # y el docstring del modulo.
    HW_sobre_D, piso = _resolver_hw_fuera_de_rango(
        HW_sobre_D, m, Q=Q, S=S, seccion=seccion, q_estrella=q_estrella,
        hds5=hds5, critico=critico)

    return ControlEntrada(
        HW=HW_sobre_D * seccion.altura,
        HW_sobre_D=HW_sobre_D,
        q_estrella=q_estrella,
        regimen=regimen,
        critico=critico,
        constantes=hds5,
        transicion=transicion,
        piso=piso,
    )


# ---------------------------------------------------------------------------
# Pieza 3 - Control de salida (Sec. 4.3)
# ---------------------------------------------------------------------------

def _fila_del_ke_numerico(criterio_ke: str) -> Optional[str]:
    """
    La clave de fila de la Tabla C.2 de la que sale el ke NUMERICO, o None.

    Declarado en caliente: la fila que `declarar_desde_tabla` registro en
    la procedencia (una declaracion sin procedencia --- `--declarar`,
    `establecer_valor_dinamico` a secas --- no nombra fila y no se le
    inventa). Del archivo: `DeTabla.fila_id` de la resolucion del criterio.
    El import es perezoso porque `declaracion` importa la ventana normativa
    y el censo, que M4 no necesita para calcular.
    """
    if ca.declarado_en_caliente(criterio_ke):
        from src import declaracion as _dec
        procedencia = _dec.procedencia_de(criterio_ke)
        if procedencia is None or not procedencia.filas:
            return None
        return procedencia.filas[0]
    resolucion = ca.CRITERIOS[criterio_ke].resolucion
    return getattr(resolucion, "fila_id", None)


def ke_declarado(criterio_ke: str = CRITERIO_KE
                 ) -> Tuple[str, str, str, float]:
    """
    (fila, agrupacion, bloque, ke) del criterio de perdida de entrada.

    EL BLOQUE VIAJA CON LOS OTROS DOS y no se deduce despues: es lo que
    permite que la memoria diga de que familia de la Tabla C.2 salio el
    coeficiente sin que ningun modulo lo escriba a mano.

    DOS CRITERIOS, DOS FORMAS DE DECLARACION, y la asimetria es deliberada
    (esta razonada en `constantes_normativas.KE_HDS5_C2`):

      * 'ke_entrada' (tubo) declara UN NUMERO, y desde el cierre de C5-02
        los tres rotulos salen de la fila de la que ese numero sale
        (`_fila_del_ke_numerico`): vacios solo si el numero no es la celda
        de ninguna fila nombrada (un ke declarado a secas, o uno que
        «DIFIERE de la celda»).
      * 'ke_entrada_cajon' declara LA CLAVE DE UNA FILA de la Tabla C.2. Se
        declara asi porque en el bloque «Box, Reinforced Concrete» el numero
        NO identifica la fila -- el 0.2 esta en tres, el 0.5 en dos, y tres
        filas comparten el rotulo «Square-edged at crown» --, de modo que un
        numero suelto dejaria a la memoria sin poder decir de donde salio.

    Una clave que no este en la tabla es `DatoInvalidoError` y no un
    `KeyError`: quien la escribio fue el expediente, no el programa.

    SE VALIDA CONTRA EL BLOQUE, NO CONTRA LA TABLA, y la diferencia la
    encontro la auditoria adversarial de C5 midiendo esta misma funcion: con
    `KE_HDS5_C2` entera como dominio, declarar
    «concreto_headwall_square_edge» -- fila del bloque «Pipe, Concrete» --
    devolvia ke = 0.5 sin quejarse, y la memoria lo imprimia como fila de
    cajon. Es NOR-HID-01 exacto, cometido por la guardia escrita para
    cerrarlo, y con el numero que la regla vinculante #11 avisa que coincide.
    El dominio del criterio son las SIETE de `KE_CAJON_C2`.
    """
    valor = ca.valor(criterio_ke)
    if criterio_ke != CRITERIO_KE_CAJON:
        # El NUMERO declarado se valida aqui, en el consumidor: la ventana del
        # criterio defiende la puerta de declaracion y esta guardia defiende
        # lo que llegue por cualquier otra via (EXT-V-02).
        ke = _validar_ke(valor, criterio_ke)
        # Y LA FILA VIAJA CON EL NUMERO (C5-02, cierre del 2026-09-22). El
        # tubo sigue declarando un numero --- es el unico criterio `float`
        # resuelto `de_tabla`, y sobre el se sostienen el editor de E-B, el
        # barrido de PF-3 y `declarar_desde_tabla` ---, pero el numero SALE
        # de una fila: la del archivo esta en `DeTabla.fila_id` de su
        # resolucion, y la de una declaracion en caliente en la procedencia
        # que `declarar_desde_tabla` registro. Los tres rotulos se imprimen
        # SOLO si el numero es la celda de esa fila: un 0.7 declarado sobre
        # la fila del 0.5 «DIFIERE de la celda» (EXT-1) y no puede citarla.
        fila_id = _fila_del_ke_numerico(criterio_ke)
        if fila_id is None:
            return "", "", "", ke
        f = KE_HDS5_C2.get(fila_id)
        if f is None or f["bloque"].startswith("Box"):
            raise DatoInvalidoError(
                criterio_ke, valor=fila_id,
                motivo="la fila de la que se declara el ke del TUBO tiene "
                       "que ser de un bloque «Pipe» de la Tabla C.2 del "
                       f"HDS-5; «{fila_id}» es del bloque "
                       f"«{f['bloque'] if f else 'desconocido'}» (un cajon, "
                       "o una fila que la tabla no tiene). Es la simetrica "
                       "de NOR-HID-01: el numero puede coincidir y la cita "
                       "seria falsa",
            )
        if not abs(f["ke"] - ke) <= TOL_UMBRAL_NORMATIVO:
            return "", "", "", ke
        return f["fila"], f["agrupacion"], f["bloque"], ke
    if not isinstance(valor, str) or valor not in KE_CAJON_C2:
        raise DatoInvalidoError(
            criterio_ke, valor=valor,
            motivo="se espera la CLAVE de una fila del bloque «Box, "
                   "Reinforced Concrete» de la Tabla C.2 del HDS-5, no un "
                   "coeficiente ni una fila de otro bloque: en ese bloque el "
                   "numero no identifica la fila, y el num. A.3 prohibe "
                   "cruzar coeficientes entre geometrias. Claves admitidas: "
                   + ", ".join(sorted(KE_CAJON_C2)),
        )
    fila = KE_HDS5_C2[valor]
    return fila["fila"], fila["agrupacion"], fila["bloque"], fila["ke"]


def perdida_carga(V: float, R: float, n: float, L: float,
                  ke: Optional[float] = None,
                  criterio_ke: str = CRITERIO_KE) -> float:
    """
    H = (1 + ke + K_friccion*n^2*L/R^(4/3)) * V^2/(2g), Sec. 4.3, en SI.

    K_friccion es `constantes_normativas.K_FRICCION_SI` = 19.63, la
    conversion SI que HDS-5 declara para su K = 29 del sistema ingles. Usar
    el 29 en metrico no falla ruidosamente: devuelve numeros plausibles y
    equivocados. Ver CP-8 y `test_constante_friccion_es_SI_no_imperial`.

    Los tres sumandos del parentesis son, en orden: carga de velocidad,
    perdida de entrada y perdida por friccion. `ke` sale del criterio
    'ke_entrada' [C] (0.5 para tubo a ras del muro) si no se pasa explicito.

    Toma V y R como argumentos sueltos, sin decidir de que seccion salen: esa
    decision es del criterio 'geometria_control_salida' y la aplica
    `control_salida()`. Asi esta funcion es exactamente la ecuacion de
    Sec. 4.3 y nada mas, que es lo que contrasta CP-8.
    """
    _validar_positivo("V", V, "la velocidad debe ser positiva")
    _validar_positivo("R", R, "el radio hidraulico debe ser positivo")
    _validar_positivo("n", n, "el coeficiente de Manning debe ser positivo")
    _validar_positivo("L", L, "la longitud del conducto debe ser positiva")

    if ke is None:
        # Se desempaqueta por posicion y no por indice: los tres rotulos no
        # los usa esta funcion -- son de la memoria, y los guarda
        # `control_salida` --, y un `[3]` suelto es un literal sin nombre.
        *_, ke = ke_declarado(criterio_ke)
    ke = _validar_ke(ke, "ke")

    friccion = K_FRICCION_SI * n ** 2 * L / R ** (4 / 3)  # literal-ok: exponente 4/3 de Sec. 4.3
    return (1 + ke + friccion) * V ** 2 / (2 * G)


def _geometria_de_referencia(Q: float, seccion: Seccion) -> Tuple[float, float]:
    """
    (V, R) de la seccion con la que se evalua Sec. 4.3, segun el criterio
    'geometria_control_salida' [C]. Hoy: seccion LLENA.

    NI A NI R SE ESCRIBEN AQUI, y desde C5 este docstring tampoco los escribe:
    decia "V = Q/(pi*D^2/4), R = D/4", que es la aritmetica de un tubo y de
    ningun marco (para el de 2.00 x 1.50 m el R lleno es B*H/(2*(B+H)) =
    0.4286 m, no H/4). Los dos salen de la seccion -- `area_llena` y
    `radio_hidraulico_lleno` --, que es exactamente lo que permite que el
    mismo criterio gobierne las dos formas. Ver la justificacion completa en
    criterios_adoptados.py.
    """
    seleccion = ca.valor(CRITERIO_GEOMETRIA_SALIDA)
    if seleccion != "seccion_llena":
        raise DatoInvalidoError(
            CRITERIO_GEOMETRIA_SALIDA, valor=seleccion,
            motivo="M4 solo implementa la seccion llena de Sec. 4.3. Una "
                   "seccion de referencia distinta exige programar el "
                   "procedimiento de barril parcialmente lleno de HDS-5",
        )
    A = seccion.area_llena
    return Q / A, seccion.radio_hidraulico_lleno


def control_salida(Q: float, seccion: Seccion, S: float, L: float, TW: float,
                   n: float, ke: Optional[float] = None,
                   critico: Optional[TiranteCritico] = None,
                   criterio_ke: str = CRITERIO_KE) -> ControlSalida:
    """
    Carga a la entrada bajo control de salida (Sec. 4.3):

        HW = H + h_o - S*L
        H  = (1 + ke + 19.63*n^2*L/R^(4/3)) * V^2/(2g)
        h_o = max(TW, (y_c + D)/2)

    `TW` es el tirante en el cuerpo receptor durante la avenida, en metros
    sobre el fondo de la SALIDA (no una cota): quien lo calcula es el modulo
    que resuelva Manning en el receptor, y mientras el criterio 'TW_receptor'
    siga vacio, quien lo pasa debe declarar con que escenario lo obtuvo. Se
    admite TW = 0 (salida libre); un TW negativo es DatoInvalidoError.

    `n` es el de la rama de CAPACIDAD (n_max, Sec. 4.1): HW es una carga, y la
    regla de doble n manda el n mayor -- mas friccion, mas H, mas remanso --
    del lado conservador de la inundacion. `resolver_control()` lo toma solo
    de `material.n_para_capacidad`; aqui se recibe explicito para poder
    probar la pieza aislada.

    El resultado puede salir negativo en un conducto largo y empinado, donde
    S*L supera a H + h_o. No es un error: significa que el control de salida
    no impone carga alguna a la entrada, y por eso siempre pierde frente al
    control de entrada en `hw_gobernante()`.
    """
    _validar_Q_D(Q, seccion)
    _validar_positivo("S", S, "la pendiente del conducto debe ser positiva")
    _validar_positivo("L", L, "la longitud del conducto debe ser positiva")
    # `not TW >= 0` y no `TW < 0` (PC-05, forma MAT-D13): un TW = NaN pasaba
    # y HW salia NaN.
    if not TW >= 0:
        raise DatoInvalidoError("TW", valor=TW,
                                motivo="el tirante en el receptor no puede ser "
                                       "negativo (TW = 0 es salida libre)")

    if critico is None:
        critico = tirante_critico(Q, seccion)

    V, R = _geometria_de_referencia(Q, seccion)
    # Se resuelve UNA vez y se guarda: el numero que entra en H y el que la
    # memoria imprime tienen que ser el mismo objeto, no dos lecturas.
    ke_fila, ke_agrupacion, ke_bloque, ke_valor = ke_declarado(criterio_ke)
    if ke is not None:
        # `ke` explicito es la via de los tests de la pieza aislada y de CP-8:
        # gana sobre el criterio y se declara como lo que es, sin procedencia
        # de tabla.
        ke_valor, ke_fila, ke_agrupacion, ke_bloque = ke, "", "", ""
    H = perdida_carga(V=V, R=R, n=n, L=L, ke=ke_valor)

    h_o_geometrico = (critico.y_c + seccion.altura) / 2
    h_o = max(TW, h_o_geometrico)
    caida = S * L
    HW = H + h_o - caida
    if not math.isfinite(HW):
        # GUARDIA DE FINITUD A LA SALIDA (PC-05, patron SIS-G-01). Cada dato
        # paso su validacion -- un L o un TW infinitos son positivos -- y es
        # la aritmetica que los combina la que no cabe: H crece con L, h_o
        # con TW, y la resta H + h_o - S*L puede dar inf o nan. El mensaje
        # nombra el PAR, como MAT-D13: no hay umbral que reparta la culpa.
        raise LimiteNumericoError(
            "HW", valor=HW,
            motivo=f"el control de salida (Sec. 4.3) no da una carga finita "
                   f"con el par (L = {L!r} m, TW = {TW!r} m): H = {H!r}, "
                   f"h_o = {h_o!r}, S*L = {caida!r}. Cada dato cumple su "
                   "validacion por separado; lo que no cabe en un numero es "
                   "la operacion que los combina. Sin esta guardia el HW "
                   "seguiria hasta la memoria y el informe imprimiria un "
                   "diagnostico entero sobre un numero que no lo es",
        )

    # Las dos condiciones de uso que HDS-5 pone a h_o y que SI se pueden
    # evaluar (num. 3.3.3, pag. impresa 3.24; NOR-HDS-05). No lanzan AQUI: la
    # pieza calcula y marca; la de 0.75 la convierte en `Bloqueo` «metodo no
    # evaluable» la corrida, leyendo la bandera ya filtrada por control
    # gobernante que `resolver_control` deja en `ResultadoHidraulico` (EXT-3).
    # Ver `constantes_normativas.H_O_CONDICION_APLICACION`.
    HW_sobre_D = HW / seccion.altura

    return ControlSalida(
        HW=HW,
        H=H,
        h_o=h_o,
        TW=TW,
        caida=caida,
        V=V,
        R=R,
        ahogado_por_TW=TW > h_o_geometrico,
        critico=critico,
        ke=ke_valor,
        ke_criterio="" if ke is not None else criterio_ke,
        ke_fila=ke_fila,
        ke_agrupacion=ke_agrupacion,
        ke_bloque=ke_bloque,
        HW_sobre_D=HW_sobre_D,
        h_o_fuera_de_rango=HW_sobre_D < H_O_HW_SOBRE_D_MIN,
        h_o_requiere_cautela=HW_sobre_D < H_O_HW_SOBRE_D_CAUTELA,
    )


# ---------------------------------------------------------------------------
# Pieza 4 - Cual de los dos gobierna
# ---------------------------------------------------------------------------

def _procedencia_ke(salida: ControlSalida) -> str:
    """
    De donde salio el ke que entro en H, escrito para el revisor.

    TRES REDACCIONES Y NO DOS, porque hay tres situaciones reales: el ke que
    llega por una clave de fila de la Tabla C.2 (el marco), el que llega como
    numero declarado en un criterio (el tubo) y el que llega explicito por
    argumento (los casos patron y los tests de la pieza suelta). Confundir el
    tercero con el segundo pondria en la memoria una cita de criterio que la
    corrida no leyo.
    """
    if not salida.ke_criterio:
        return ("coeficiente pasado explicito a `control_salida`: esta "
                "corrida NO lo leyo de ningun criterio")
    if not salida.ke_fila:
        # Dos casos reales y un solo texto que no miente en ninguno: el ke
        # se declaro nombrando una fila cuya celda NO es este numero (la
        # nota que `declarar_desde_tabla` exige va en el bloque 3), o se
        # declaro sin nombrar fila (`--declarar`, `establecer_valor_dinamico`)
        # y entonces no hay procedencia registrada que citar: se dice.
        return (f"criterio '{salida.ke_criterio}', declarado como NUMERO sin "
                "fila de la Tabla C.2 que lo respalde: o la fila nombrada al "
                "declararlo tiene otra celda (la nota que lo explica esta en "
                "el bloque 3 de esta memoria), o se declaro sin nombrar fila "
                "y esta memoria no tiene procedencia que citar")
    # EL BLOQUE SE LEE DE LA TABLA, NO SE CABLEA. Esta linea decia
    # «del bloque «Box, Reinforced Concrete»» como literal, de modo que
    # imprimia esa procedencia CUALQUIERA que fuese la fila declarada -- y
    # `ke_declarado` aceptaba entonces filas de tubo (ver su docstring) --.
    # Un texto de procedencia que no puede desmentirse no es una procedencia.
    return (f"criterio '{salida.ke_criterio}': fila «{salida.ke_fila}» bajo "
            f"el rotulo de agrupacion «{salida.ke_agrupacion}» del bloque "
            f"«{salida.ke_bloque}» de la Tabla C.2 del HDS-5 (pag. "
            f"impresa C.6). Los dos rotulos van juntos a proposito: tres "
            f"filas del bloque se imprimen con el mismo texto y distinto "
            f"coeficiente")


def criterio_ke_de(material: Material) -> str:
    """
    Cual de los dos criterios de ke le toca a este material (regla #11).

    NO ES GEOMETRIA, y por eso no rompe la ceguera de forma que C1 y C4
    dejaron: M4 no calcula nada distinto segun la respuesta -- la ecuacion de
    `perdida_carga` es la misma -- ni le pregunta a la seccion por sus
    dimensiones. Lo que elige es DE QUE FILA DE QUE TABLA sale un coeficiente
    declarado, y esa eleccion la manda la familia del catalogo: la Tabla C.2
    de HDS-5 tiene bloques separados para «Pipe, Concrete» y para «Box,
    Reinforced Concrete», y el num. A.3 prohibe cruzarlos.

    LA TRAMPA, POR SI ALGUIEN PIENSA EN SIMPLIFICARLO: para la embocadura que
    la Sec. 9.1 adopta -- cabezal a ras, sin aletas -- las dos filas valen
    0.5. Un `ke` unico daria el mismo numero y la cita seria falsa, y como
    acierta por casualidad no fallaria nunca de forma ruidosa. En cuanto la
    embocadura declare aletas deja de coincidir: 0.4, 0.5 o 0.7 segun el
    angulo.
    """
    return (CRITERIO_KE_CAJON if material.forma is FormaSeccion.RECTANGULAR
            else CRITERIO_KE)


def hw_gobernante(entrada: ControlEntrada, salida: ControlSalida,
                  perfil: Optional[PerfilLamina] = None
                  ) -> Tuple[float, ControlGobernante]:
    """
    HW de diseno y control que lo produce (Sec. 4.2 y 4.3): el MAYOR de los
    dos. Cada control es una restriccion independiente sobre la misma
    estructura y la que exige mas carga es la que manda.

    Devuelve el par, nunca el maximo a secas: los dos numeros pueden estar a
    centimetros y el remedio de cada caso es distinto -- si gobierna la
    entrada se trabaja la embocadura o el diametro; si gobierna la salida,
    el problema esta aguas abajo (TW del receptor) y agrandar el tubo puede
    no mover el HW.

    Empate: se devuelve ENTRADA cuando la diferencia cae dentro de
    TOL_UMBRAL_NORMATIVO. No es una decision de calculo -- el HW es el mismo
    numero por ambos caminos, hasta la millonesima de milimetro -- sino la
    etiqueta con la que se reporta ese numero.

    CON `perfil` (E-A) EL HW DE SALIDA QUE COMPITE ES EL EFECTIVO
    (`PerfilLamina.HW_efectivo_m`): la aproximacion de la Sec. 4.3 mientras
    HW_aprox/D >= 0.75 --la pag. 3.12 del HDS-5 la avala hasta ahi-- y el
    remanso por debajo, donde la fuente dice que la aproximacion «should not
    be used» y que «backwater calculations are required». Y cuando bajo 0.75
    el remanso NO alcanza la entrada --la S1 corta y_c antes, o tiene
    longitud cero en un barril supercritico con TW <= y_c-- el control de
    salida no impone carga alguna y gobierna la ENTRADA (Section 3.5.1: la S1
    se usa «if the S1 curve extends to the face of the culvert»). Es lo que
    deshace la circularidad de la aproximacion: hasta E-A el caso (b) del
    dictamen se clasificaba como control de salida con un h_o que la fuente
    prohibe usar ahi. Sin `perfil` --la pieza aislada y los tests de antes
    de E-A-- compara la aproximacion, como siempre.
    """
    HW_salida = salida.HW if perfil is None else perfil.HW_efectivo_m
    if HW_salida is not None and HW_salida > entrada.HW + TOL_UMBRAL_NORMATIVO:
        return HW_salida, ControlGobernante.SALIDA
    return entrada.HW, ControlGobernante.ENTRADA


# ---------------------------------------------------------------------------
# Pieza 5 - Regimen del barril y velocidad de salida (HDS-5 3.1.6; EXT-3)
# ---------------------------------------------------------------------------

class _RegimenYSalida(NamedTuple):
    """Lo que la pieza 5 entrega a `ResultadoHidraulico` y al paso F4.REGIMEN."""
    regimen: RegimenBarril
    V_llena: float          # m/s - Q_celda / A_llena
    y_salida: float         # m   - tirante con que se midio V_salida
    V_salida: Magnitud      # m/s - con su procedencia


def regimen_del_barril(TW: float, seccion: Seccion) -> RegimenBarril:
    """
    LLENO si la salida esta sumergida, TW >= D; PARCIALMENTE_LLENO si no
    (v8 §1.3 y §4.1, enmendadas en EXT-0; HDS-5 3.1.6, pag. impresa 3.18:
    «Total barrel area is used when the tailwater exceeds the top of the
    barrel»).

    La v8 escribe «TW >= D, o HW >= D con la salida sumergida»: la segunda
    clausula esta contenida en la primera (salida sumergida ES TW >= D), y por
    eso aqui hay una condicion y no dos. Lo que NO hace esta funcion es decir
    cuanto llena un barril con TW < D: eso exige el perfil de la lamina de agua
    (HDS-5 3.1.4, tipos 6 y 7) y se declara pendiente, no se estima. Forma
    MAT-D13: condicion en positivo y negada, con tolerancia nombrada.

    NO MIRA EL CONTROL, Y ESO ES UNA DISCREPANCIA DECLARADA CON LA FUENTE
    PRIMARIA (HDS-5 3.1.3, pag. impresa 3.2, `HDS5_3ED.3.1.3#SUMERGENCIA`):
    bajo control de ENTRADA la sumergencia de la salida «does not assure
    outlet control», el tramo de aguas arriba es supercritico y un resalto
    llena el barril hacia la salida. LLENO aqui significa lo que V1 y V2
    necesitan --la salida y el tramo aguas abajo del resalto van llenos, sin
    borde libre y a la velocidad Q/A_llena, la menor del barril--, no «flujo a
    presion en toda la longitud», que es lo que la v8 §1.3 dice a secas y por
    lo que el defecto queda reportado contra ella (`modelos.RegimenBarril`).
    """
    if not TW < seccion.altura - TOL_UMBRAL_NORMATIVO:
        return RegimenBarril.LLENO
    return RegimenBarril.PARCIALMENTE_LLENO


def velocidad_de_salida(*, Q_celda: float, seccion: Seccion, TW: float,
                        critico: TiranteCritico, normal: TiranteNormal,
                        control: ControlGobernante) -> Tuple[Magnitud, float]:
    """
    (V_salida, y_salida) por HDS-5 3.1.6: la velocidad a la SALIDA del
    conducto, que es la que dimensiona la proteccion de la Fase 6 (PC-04).

    Control de SALIDA (pag. impresa 3.18): el area es la de la seccion al
    tirante que fija el TW -- el critico si TW < y_c, el TW si y_c <= TW < D,
    la seccion entera si TW >= D --, o sea min(D, max(TW, y_c)). No lleva n:
    es Q entre un area, y por eso no entra en la regla de doble n.

    Control de ENTRADA (pag. impresa 3.24, «The velocity at normal depth is
    assumed to be the outlet velocity»): la del tirante normal. De sus dos
    ramas se toma la de n MINIMO, `V_erosion`, la estimacion ALTA: d50 crece
    con V^2 y el techo es el lado conservador de una proteccion. Es lo que M6
    recibia siempre hasta EXT-3, tambien bajo control de salida, donde en
    pendiente suave con salida libre la velocidad a y_c es MAYOR (1.508 vs
    1.184 m/s en el caso del dictamen) y la piedra salia chica.
    """
    if control is ControlGobernante.ENTRADA:
        salida_llena = ("" if TW < seccion.altura - TOL_UMBRAL_NORMATIVO else
                        ". Con el TW sobre la clave la seccion de SALIDA va "
                        "llena tras el resalto (HDS-5 3.1.3, Fig. 3.1C/D) y la "
                        "velocidad real alli seria Q_celda/A_llena, menor: se "
                        "conserva la del tirante normal como techo declarado, "
                        "porque el 3.1.6 no da la regla para ese caso y d50 "
                        "crece con V^2")
        return Magnitud(
            "V_salida", normal.V_erosion, "m/s",
            "HDS-5 num. 3.3.2 (pag. impresa 3.24) y 3.1.6: bajo control de "
            "ENTRADA la velocidad a la salida es la del tirante normal. De las "
            "dos ramas de n (Sec. 4.1) se toma la de n MINIMO, V_erosion, la "
            "estimacion ALTA: es el techo conservador para un d50 que crece "
            "con el cuadrado de V" + salida_llena,
            cifras=CIFRAS_MAGNITUD), normal.geometria.y
    D = seccion.altura
    y_salida = min(D, max(TW, critico.y_c))
    # LAS TRES AREAS, Y DE DONDE SALE CADA UNA (regla vinculante #12 de
    # ruta_familia_c.md §6): la seccion entera y la critica ya estan resueltas
    # por la via canonica --`area_llena` y `critico.geometria.A`, que es la
    # misma A con que M4 formo H_c-- y NO se recalculan desde el tirante. Solo
    # el TW es un tirante SIN `Geometria` --es un dato del receptor, no la
    # salida de un solver--, y ese es el unico caso en que se lee `area(TW)`
    # por la via por tirante. Esta censado en
    # `tests/test_seccion_rectangular.py::CENSO_VIA_POR_TIRANTE`.
    if not y_salida < D - TOL_UMBRAL_NORMATIVO:
        y_salida = D
        A = seccion.area_llena
        caso = ("el TW supera la clave del barril, de modo que el area es la "
                "SECCION ENTERA (tercera vineta de la pag. 3.18): V = "
                "Q_celda / A_llena")
    elif TW > critico.y_c:
        A = seccion.area(y_salida)
        caso = ("el TW esta entre el tirante critico y la clave, de modo que "
                "el tirante a la salida es el TW (segunda vineta de la pag. "
                "3.18): V = Q_celda / A(TW)")
    else:
        A = critico.geometria.A
        caso = ("el TW queda bajo el tirante critico, de modo que el agua pasa "
                "por y_c a la salida (primera vineta de la pag. 3.18): V = "
                "Q_celda / A(y_c), con el area critica que el paso 4.2 ya "
                "resolvio")
    if not A > 0:
        # Forma MAT-D13: umbral en positivo y negado; el par culpable.
        raise LimiteNumericoError(
            "A_salida", valor=A,
            motivo=f"el area de la seccion al tirante de salida "
                   f"(y_salida = {y_salida!r} m, con TW = {TW!r} m y "
                   f"y_c = {critico.y_c!r} m) no es positiva y la velocidad "
                   "de salida de HDS-5 3.1.6 no se puede formar")
    return Magnitud(
        "V_salida", Q_celda / A, "m/s",
        f"HDS-5 num. 3.1.6 (pag. impresa 3.18): bajo control de SALIDA el "
        f"area de la velocidad de salida la fija el TW; aqui {caso}. No lleva "
        f"n de Manning: es un caudal entre un area, y por eso no entra en la "
        f"regla de doble n",
        cifras=CIFRAS_MAGNITUD), y_salida


def _regimen_y_salida(*, Q_celda: float, seccion: Seccion, TW: float,
                      critico: TiranteCritico, normal: TiranteNormal,
                      control: ControlGobernante) -> _RegimenYSalida:
    """La pieza 5 entera, resuelta UNA vez: el resultado y el paso la comparten."""
    V_salida, y_salida = velocidad_de_salida(
        Q_celda=Q_celda, seccion=seccion, TW=TW, critico=critico,
        normal=normal, control=control)
    return _RegimenYSalida(regimen=regimen_del_barril(TW, seccion),
                           V_llena=Q_celda / seccion.area_llena,
                           y_salida=y_salida, V_salida=V_salida)


# ---------------------------------------------------------------------------
# Pieza 6 - El perfil de la lamina de agua por paso directo (E-A; NOR-HDS-05)
# ---------------------------------------------------------------------------
# El procedimiento de barril parcialmente lleno del Cap. III del HDS-5, tal
# como la pag. impresa 3.12 (PDF 94) lo escribe y la Section 3.5.1 (PDF
# 118-120) lo reparte por tipos: el calculo de remanso arranca en la lamina
# de la salida --«critical depth at the culvert outlet or … the tailwater
# depth, whichever is higher»-- y avanza hacia la entrada; donde la lamina
# esta sobre la clave rige «a straight, full flow hydraulic grade line» con la
# pendiente de friccion de la Ec. 3.7; y en la entrada «the inlet losses and
# the velocity head are added to the elevation of the hydraulic grade line»
# para formar el HW. El paquete de implementacion (piezas 1 a 5) esta en el
# bloque que precede a `constantes_normativas.H_O_CONDICION_APLICACION`.
#
# SE INTEGRA SOBRE EL PARAMETRO PROPIO DE LA SECCION, no sobre el tirante
# (regla vinculante #12 de ruta_familia_c.md §6). La escalera recorre
# `llenado` --theta en la circular, el tirante en el marco-- y cada escalon
# pide su `Geometria` entera a `geometria_en`: A, P, R e y mutuamente
# consistentes, sin pasar por `theta_desde_tirante`, que en la circular esta
# mal condicionada en los extremos. El unico tirante que llega SIN
# `Geometria` es el TW, y su llenado se resuelve con Brent sobre
# `bracket_llenado()`, por la misma via canonica; ninguna de las tres
# funciones de esta pieza llama a `area(y)`, `perimetro(y)` ni
# `ancho_superficial(y)`, y `tests/test_ea_perfil_lamina.py` lo fija por AST
# junto al censo de `test_seccion_rectangular`.
#
# EL PASO DIRECTO, en una linea: entre dos escalones consecutivos de la
# escalera, con E = y + V²/2g y Sf la Ec. 3.7 en cada uno,
#
#     dx = (E_aguas_abajo - E_aguas_arriba) / (S - Sf_medio),   Sf_medio = (Sf_0 + Sf_1)/2
#
# con x medido desde la salida hacia aguas arriba. La direccion de la
# escalera la fija la clasificacion del perfil (HDS-5 3.5.1): en pendiente
# suave la lamina tiende a y_n --M1 bajando desde un TW > y_n, M2 subiendo
# desde max(y_c, TW) < y_n-- y la asintota se excluye; en pendiente
# pronunciada (y_n <= y_c) la lamina baja hacia y_c (S1) y, si lo alcanza
# antes de la entrada, el remanso NO llega y el control es de entrada. El
# cruce con x = L se resuelve DENTRO del escalon con Brent, para que el paso
# de la escalera no imponga su resolucion al tirante de la entrada.
#
# LO QUE NO HACE, dicho para que no se lea de mas: no situa el resalto
# hidraulico (HY-8 7.3 lo hace por momentum; aqui basta saber que la S1 no
# llega a la cara de entrada), no calcula perfiles S2 desde la entrada (bajo
# control de entrada el tramo supercritico se aproxima por el uniforme, como
# desde EXT-3) y no fabrica dorados: sus dos casos patron son limites de la
# propia formula (conflicto #7).

def _fmt_m(valor: Optional[float]) -> str:
    """Un numero del perfil en el texto de una procedencia, a las cifras de la memoria."""
    if valor is None:
        return "--"
    return f"{valor:.{CIFRAS_MAGNITUD}f}"


def _pendiente_friccion(g: Geometria, Q: float, n: float) -> float:
    """
    Sf de la Ec. 3.7 (HDS-5 pag. impresa 3.12): Sf = Ku·n²·V²/(R^(4/3)·2g),
    con Ku = `K_FRICCION_SI` = 19.63 y V = Q/A sobre la `Geometria` del
    escalon. Es el MISMO termino de friccion de `perdida_carga` (Sec. 4.3),
    escrito por unidad de longitud: asi el tramo lleno del perfil reproduce
    la formula cerrada del control de salida exactamente, y la fuente
    imprime R^1.33 donde la Sec. 4.3 y este modulo escriben R^(4/3).
    """
    V = Q / g.A
    return K_FRICCION_SI * n ** 2 * V ** 2 / (g.R ** (4 / 3) * 2 * G)  # literal-ok: exponente 4/3 de la Ec. 3.7 / Sec. 4.3


def _pendiente_friccion_llena(seccion: Seccion, Q: float, n: float) -> float:
    """
    La Ec. 3.7 a SECCION LLENA, con `area_llena` y `radio_hidraulico_lleno`:
    en el marco el R lleno lleva la losa superior en el perimetro
    (2B + 2H) y NO es el de `geometria_en(H)`, que es de lamina libre
    (B + 2H). Es la misma pareja con que `control_salida` forma H.
    """
    V = Q / seccion.area_llena
    return K_FRICCION_SI * n ** 2 * V ** 2 / (seccion.radio_hidraulico_lleno ** (4 / 3) * 2 * G)  # literal-ok: exponente 4/3 de la Ec. 3.7 / Sec. 4.3


def _energia_especifica(g: Geometria, Q: float) -> float:
    """E = y + V²/2g sobre la `Geometria` del escalon."""
    V = Q / g.A
    return g.y + V ** 2 / (2 * G)


def _llenado_de_tirante(seccion: Seccion, y: float) -> float:
    """
    El parametro propio de la seccion cuyo tirante es `y`, resuelto con
    Brent sobre `bracket_llenado()` y `geometria_en` (la via CANONICA de la
    regla #12), y no con la inversa cerrada de la forma. Lo necesita el TW,
    que es el unico tirante que entra al perfil sin `Geometria`: es un dato
    del receptor, no la salida de un solver. Quien llama garantiza
    y_c <= y < D, de modo que la raiz existe y esta lejos de los dos bordes.
    """
    llenado_min, llenado_max = seccion.bracket_llenado()
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    return brentq(lambda llenado: seccion.geometria_en(llenado).y - y,
                  llenado_min, llenado_max, xtol=TOL_BRENT)


def _llenado_donde_Sf_iguala_S(seccion: Seccion, Q: float, n: float, S: float,
                               llenado_a: float, llenado_b: float) -> Optional[float]:
    """
    El parametro propio en que la Ec. 3.7 da Sf = S dentro de [a, b] --la
    ASINTOTA del perfil con su propia ley de friccion--, o `None` si Sf - S
    no cambia de signo en el intervalo. Brent sobre `geometria_en` (via
    canonica). NO es el tirante normal de M3, y la diferencia esta medida
    (auditoria adversarial de E-A): Manning en M3 lleva `K_MANNING_SI` = 1 y
    la Ec. 3.7 lleva `K_FRICCION_SI`/(2g) = 19.63/19.62 = 1.00051, de modo que
    en y_n de Manning la pendiente de friccion del perfil vale 1.00051·S y la
    lamina que el paso directo integra tiende a un y_n' 0.05 % mas alto
    (0.07 mm en D = 0.90 con Q = 0.3 y S = 0.001). Clasificar el perfil
    contra y_n en vez de contra y_n' dejaba una banda de TW entre los dos en
    la que la escalera iba contra su propio perfil y lanzaba
    `LimiteNumericoError`; por eso la asintota se busca con la MISMA ley que
    integra, y y_n se imprime al lado, con su diferencia declarada.
    """
    def f(llenado: float) -> float:
        return _pendiente_friccion(seccion.geometria_en(llenado), Q, n) - S

    f_a, f_b = f(llenado_a), f(llenado_b)
    if not f_a * f_b < 0:
        return None
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    return brentq(f, llenado_a, llenado_b, xtol=TOL_BRENT)


def perfil_lamina(*, Q_celda: float, seccion: Seccion, S: float, L: float,
                  TW: float, n: float, ke: float, critico: TiranteCritico,
                  HW_aproximado: float,
                  rungs: int = PASOS_PERFIL_LAMINA) -> PerfilLamina:
    """
    El perfil de la lamina de agua desde la salida hacia la entrada, por paso
    directo (HDS-5 3.a ed., pag. impresa 3.12 / PDF 94; Section 3.5.1, PDF
    118-120; E-A). Ver el bloque de arriba para el metodo y sus limites.

    `n` es n_max --la regla de doble n manda el n mayor para una carga, y
    ademas da mas tirante y menos velocidad, el lado conservador de V1 y de
    V2-- y `ke` es el coeficiente con que `control_salida` formo H, para que
    el tramo lleno reproduzca HW = H + h_o - S·L exactamente. `HW_aproximado`
    es el HW de `control_salida`: decide `sustituye_aproximacion` (HW_aprox/D
    < 0.75, pag. 3.24 y 3.12) y `cautela_aproximacion` (< 1.2), y viaja en
    el resultado para que la memoria imprima los dos numeros juntos.

    LA CLASIFICACION NO LEE EL TIRANTE NORMAL DE M3: lee el SIGNO de
    Sf - S en la frontera de salida, con la misma Ec. 3.7 que integra
    (`_llenado_donde_Sf_iguala_S`). Con Sf(y_salida) < S la lamina baja
    aguas arriba hacia la raiz de Sf = S: si esa raiz esta por encima de y_c
    es una M1 (asintota, excluida); si no la hay por encima de y_c, es una
    S1 que termina en y_c (pendiente pronunciada). Con Sf(y_salida) > S la
    lamina sube hacia la raiz por encima (M2, asintota) o, si no la hay bajo
    la clave --Q por encima del caudal a seccion llena--, hasta la clave, y
    desde alli sigue la linea de energia llena (Fig. 3.7B). Asi el perfil no
    necesita `normal` y vale igual cuando M3 no tiene solucion.

    Devuelve un `PerfilLamina`; nunca `None`. Cuando el remanso no alcanza
    la entrada lo dice `alcanza_entrada=False` con `x_fin_remanso_m`.
    """
    _validar_Q_D(Q_celda, seccion)
    _validar_positivo("S", S, "la pendiente del conducto debe ser positiva")
    _validar_positivo("L", L, "la longitud del conducto debe ser positiva")
    _validar_positivo("n", n, "el coeficiente de Manning debe ser positivo")
    if not TW >= 0:
        raise DatoInvalidoError("TW", valor=TW,
                                motivo="el tirante en el receptor no puede ser "
                                       "negativo (TW = 0 es salida libre)")
    if not rungs >= 2:
        raise ValueError(f"perfil_lamina: la escalera necesita al menos dos "
                         f"escalones, no {rungs!r}")

    D = seccion.altura
    llenado_min, llenado_max = seccion.bracket_llenado()
    llenado_c = critico.geometria.llenado
    V_llena = Q_celda / seccion.area_llena
    Sf_llena = _pendiente_friccion_llena(seccion, Q_celda, n)
    y_c = critico.y_c
    sustituye = HW_aproximado / D < H_O_HW_SOBRE_D_MIN
    cautela = HW_aproximado / D < H_O_HW_SOBRE_D_CAUTELA
    y_salida = min(D, max(y_c, TW))

    def _hw(y_entrada: float, V_entrada: float) -> float:
        # HDS-5 pag. 3.12: las perdidas de entrada y la carga de velocidad se
        # suman a la linea de energia en la entrada.
        return y_entrada + (1 + ke) * V_entrada ** 2 / (2 * G)

    def _resultado(**kw) -> PerfilLamina:
        return PerfilLamina(y_salida_m=y_salida, n=n, ke=ke,
                            HW_aproximado_m=HW_aproximado,
                            sustituye_aproximacion=sustituye,
                            cautela_aproximacion=cautela, rungs=rungs, **kw)

    def _lleno_hasta_la_entrada(h_entrada: float, longitud_llena: float,
                                estaciones: Tuple[Tuple[float, float], ...],
                                y_max: float, V_min: float) -> PerfilLamina:
        if not math.isfinite(h_entrada):
            raise LimiteNumericoError(
                "h_entrada", valor=h_entrada,
                motivo=f"la linea de energia llena no da una carga finita en "
                       f"la entrada con el par (L = {L!r} m, TW = {TW!r} m): "
                       f"Sf_llena = {Sf_llena!r}, S = {S!r}")
        return _resultado(
            tipo=TipoDePerfil.LLENA, alcanza_entrada=True, x_fin_remanso_m=None,
            y_entrada_m=h_entrada, V_entrada_m_s=V_llena,
            HW_remanso_m=_hw(h_entrada, V_llena), y_asintota_m=None,
            longitud_llena_m=longitud_llena, fraccion_llena=longitud_llena / L,
            y_max_m=max(y_max, D), V_min_m_s=min(V_min, V_llena),
            estaciones=estaciones)

    # --- 1. Donde arranca la lamina libre --------------------------------
    x = 0.0
    longitud_llena = 0.0
    y_max = y_salida
    V_min = math.inf
    if not TW < D - TOL_UMBRAL_NORMATIVO:
        # Salida sumergida (el mismo umbral que `regimen_del_barril`): la
        # linea de energia llena arranca en el TW, sobre el fondo de la
        # salida, y cambia aguas arriba a razon de (Sf_llena - S). Un TW a
        # menos de TOL de la clave se toma como la clave: la banda de la
        # tolerancia no puede producir un tramo lleno negativo (auditoria
        # adversarial de E-A).
        h_salida = TW if TW > D else D
        pendiente_linea = Sf_llena - S
        if not pendiente_linea < 0:
            # La linea no baja de la clave: llena hasta la entrada.
            return _lleno_hasta_la_entrada(h_salida + pendiente_linea * L, L, (),
                                           D, V_llena)
        x_corte = (h_salida - D) / (S - Sf_llena)
        if not x_corte < L:
            return _lleno_hasta_la_entrada(h_salida + pendiente_linea * L, L, (),
                                           D, V_llena)
        longitud_llena = x_corte
        x = x_corte
        llenado_actual = llenado_max
        y_max = D
        V_min = V_llena
    elif TW > y_c:
        llenado_actual = _llenado_de_tirante(seccion, TW)
    else:
        llenado_actual = llenado_c

    g0 = seccion.geometria_en(llenado_actual)
    estaciones = [(x, g0.y)]
    y_max = max(y_max, g0.y)
    V_min = min(V_min, Q_celda / g0.A)

    # --- 2. Clasificacion por el signo de Sf - S en la frontera ------------
    f_salida = _pendiente_friccion(g0, Q_celda, n) - S
    y_asintota: Optional[float] = None
    if f_salida < 0:
        # La lamina BAJA aguas arriba, hacia la raiz de Sf = S si esta por
        # encima de y_c (M1) o hasta y_c si no (S1, pendiente pronunciada).
        raiz = _llenado_donde_Sf_iguala_S(seccion, Q_celda, n, S, llenado_c,
                                          llenado_actual)
        if raiz is None:
            if not g0.y > y_c + TOL_UMBRAL_NORMATIVO:
                # S1 de longitud cero: la frontera YA esta en y_c y el remanso
                # no remonta nada. Aguas arriba el flujo es supercritico
                # (control de entrada), aproximado por el uniforme como en
                # EXT-3; ese tramo no cambia y_max ni V_min, porque en
                # pendiente pronunciada y_n < y_c <= y_salida.
                return _resultado(
                    tipo=TipoDePerfil.S1, alcanza_entrada=False,
                    x_fin_remanso_m=x, y_entrada_m=None, V_entrada_m_s=None,
                    HW_remanso_m=None, y_asintota_m=None,
                    longitud_llena_m=longitud_llena,
                    fraccion_llena=longitud_llena / L, y_max_m=y_max,
                    V_min_m_s=V_min, estaciones=tuple(estaciones))
            objetivo, terminal, tipo = llenado_c, "critico", TipoDePerfil.S1
        else:
            objetivo, terminal, tipo = raiz, "", TipoDePerfil.M1
            y_asintota = seccion.geometria_en(raiz).y
    elif f_salida > 0:
        # La lamina SUBE aguas arriba: hacia la raiz de Sf = S bajo la clave
        # (M2) o, si no la hay, hasta la clave y desde alli llena (Fig. 3.7B).
        raiz = _llenado_donde_Sf_iguala_S(seccion, Q_celda, n, S, llenado_actual,
                                          llenado_max)
        if raiz is None:
            objetivo, terminal, tipo = llenado_max, "clave", TipoDePerfil.M2
        else:
            objetivo, terminal, tipo = raiz, "", TipoDePerfil.M2
            y_asintota = seccion.geometria_en(raiz).y
    else:
        objetivo, terminal, tipo = llenado_actual, "", TipoDePerfil.UNIFORME
        y_asintota = g0.y
    if y_asintota is not None and abs(g0.y - y_asintota) <= TOL_UMBRAL_NORMATIVO:
        # UNIFORME a la tolerancia del proyecto: nada mueve la lamina.
        return _resultado(
            tipo=TipoDePerfil.UNIFORME, alcanza_entrada=True, x_fin_remanso_m=None,
            y_entrada_m=g0.y, V_entrada_m_s=Q_celda / g0.A,
            HW_remanso_m=_hw(g0.y, Q_celda / g0.A), y_asintota_m=y_asintota,
            longitud_llena_m=longitud_llena, fraccion_llena=longitud_llena / L,
            y_max_m=y_max, V_min_m_s=V_min,
            estaciones=tuple(estaciones) + ((L, g0.y),))

    # --- 3. La escalera, escalon a escalon, aguas arriba ------------------
    E0, Sf0 = _energia_especifica(g0, Q_celda), _pendiente_friccion(g0, Q_celda, n)
    llenado_previo = llenado_actual
    from scipy.optimize import brentq   # perezoso: ver la nota junto a los imports
    y_entrada: Optional[float] = None
    for k in range(1, rungs + 1):
        if not terminal and k == rungs:
            break                       # la asintota se excluye
        llenado_k = llenado_actual + (objetivo - llenado_actual) * k / rungs
        g1 = seccion.geometria_en(llenado_k)
        E1 = _energia_especifica(g1, Q_celda)
        Sf1 = _pendiente_friccion(g1, Q_celda, n)
        denominador = S - (Sf0 + Sf1) / 2
        if not abs(denominador) > TOL_ASINTOTA_PERFIL * S:
            break                       # asintota alcanzada: plano desde aqui
        dx = (E0 - E1) / denominador
        if not dx >= 0:
            # Forma MAT-D13: umbral en positivo y negado; el par culpable. Un
            # dx negativo es una escalera que va contra su propio perfil, y
            # con la clasificacion de arriba --el signo de Sf - S con la
            # MISMA ley que integra-- no ocurre; si ocurre, la aritmetica no
            # cierra y no se publica un perfil sobre ella.
            raise LimiteNumericoError(
                "dx", valor=dx,
                motivo=f"el paso directo devolvio un avance negativo entre "
                       f"y = {g0.y!r} m y y = {g1.y!r} m (E_0 = {E0!r}, "
                       f"E_1 = {E1!r}, S - Sf_medio = {denominador!r}): la "
                       "escalera va contra el perfil que clasifico")
        if not x + dx < L:
            # Cruce con la entrada DENTRO del escalon: el llenado exacto.
            def resto(llenado: float) -> float:
                g = seccion.geometria_en(llenado)
                return ((E0 - _energia_especifica(g, Q_celda))
                        / (S - (Sf0 + _pendiente_friccion(g, Q_celda, n)) / 2)
                        - (L - x))
            a, b = sorted((llenado_previo, llenado_k))
            llenado_L = brentq(resto, a, b, xtol=TOL_BRENT)
            gL = seccion.geometria_en(llenado_L)
            estaciones.append((L, gL.y))
            y_max = max(y_max, gL.y)
            V_min = min(V_min, Q_celda / gL.A)
            y_entrada = gL.y
            V_entrada = Q_celda / gL.A
            break
        x += dx
        estaciones.append((x, g1.y))
        y_max = max(y_max, g1.y)
        V_min = min(V_min, Q_celda / g1.A)
        E0, Sf0, g0, llenado_previo = E1, Sf1, g1, llenado_k

    # --- 4. Como termino ----------------------------------------------------
    if y_entrada is None:
        if terminal == "critico":
            # La S1 corto y_c en x < L: el remanso no alcanza la entrada. El
            # tramo supercritico aguas arriba (y <= y_c < y_salida) no cambia
            # y_max ni V_min: los dos estan en la salida.
            return _resultado(
                tipo=tipo, alcanza_entrada=False, x_fin_remanso_m=x,
                y_entrada_m=None, V_entrada_m_s=None, HW_remanso_m=None,
                y_asintota_m=None, longitud_llena_m=longitud_llena,
                fraccion_llena=longitud_llena / L, y_max_m=y_max,
                V_min_m_s=V_min, estaciones=tuple(estaciones))
        if terminal == "clave":
            # La M2 corto la clave en x < L: linea llena hasta la entrada.
            return _lleno_hasta_la_entrada(
                D + (Sf_llena - S) * (L - x), longitud_llena + (L - x),
                tuple(estaciones), y_max, V_min)
        # Asintota alcanzada (o escalera agotada junto a ella): la lamina
        # esta en y_asintota a todos los efectos y sigue plana hasta L.
        y_entrada = g0.y
        V_entrada = Q_celda / g0.A
        estaciones.append((L, y_entrada))
    return _resultado(
        tipo=tipo, alcanza_entrada=True, x_fin_remanso_m=None,
        y_entrada_m=y_entrada, V_entrada_m_s=V_entrada,
        HW_remanso_m=_hw(y_entrada, V_entrada), y_asintota_m=y_asintota,
        longitud_llena_m=longitud_llena, fraccion_llena=longitud_llena / L,
        y_max_m=y_max, V_min_m_s=V_min, estaciones=tuple(estaciones))


# ---------------------------------------------------------------------------
# La traza hidraulica de la memoria (§4.4)
# ---------------------------------------------------------------------------
# Los cuatro pasos que un revisor necesita leer de corrido para reconstruir el
# HW de un punto: el tirante normal, el tirante critico, cada control y la
# adopcion del que gobierna. Los emite ESTA funcion --- la que tiene los
# numeros delante --- y no M11, que solo los formatea.
#
# Ninguno de los cuatro lleva `umbral`: no verifican nada, calculan. Es para
# lo que existe `TipoDeVeredicto.SIN_VEREDICTO`; forzarles un "cumple"
# obligaria a inventarles un umbral, que es la cita falsa que este proyecto
# viene retirando. El unico que si juzga es el de h_o, y su umbral son las
# CONDICIONES DE USO que la propia fuente le pone (NOR-HDS-05).

def _pasos_hidraulicos(*, seccion, Q, S, L, TW, material, normal, critico, entrada,
                       salida, control, gobierna_salida,
                       Q_celda: Optional[float] = None, celdas: int = 1,
                       regimen: Optional[_RegimenYSalida] = None,
                       perfil: Optional[PerfilLamina] = None):
    """
    La traza de M3 + M4 para una combinacion, en orden de calculo.

    `Q` es el caudal del PUNTO y `Q_celda` el que M3 y M4 resolvieron de
    verdad (EXT-M-03); sin reparto valen lo mismo, y por eso `Q_celda` lleva
    default: los tests que llaman a esta funcion con una sola celda no
    tienen que saber que existe un reparto.

    `regimen` es la pieza 5 ya resuelta por `resolver_control` (EXT-3): el
    paso F4.REGIMEN imprime EL MISMO objeto que viaja en el resultado, no una
    segunda lectura. Si no llega --los tests de la traza suelta-- se resuelve
    aqui con la misma funcion, que es la unica que existe. `perfil` (E-A) es
    la pieza 6, con el mismo contrato.
    """
    if Q_celda is None:
        Q_celda = Q
    if regimen is None:
        regimen = _regimen_y_salida(Q_celda=Q_celda, seccion=seccion, TW=TW,
                                    critico=critico, normal=normal,
                                    control=control)
    if perfil is None:
        perfil = perfil_lamina(Q_celda=Q_celda, seccion=seccion, S=S, L=L, TW=TW,
                               n=material.n_para_capacidad, ke=salida.ke,
                               critico=critico, HW_aproximado=salida.HW)
    HW_salida_efectivo = (perfil.HW_efectivo_m if perfil.HW_efectivo_m is not None
                          else salida.HW)
    # EL PASO DEL REPARTO, y va PRIMERO y solo en el marco: es lo primero que
    # un revisor necesita para rehacer el tirante normal de la celda, y en la
    # circular no hay reparto que contar -- un tubo es una celda por
    # construccion del catalogo, sin criterio invocado, y un paso que dijera
    # «Q/1» estaria imprimiendo una decision que nadie tomo --. Cuelga del
    # MISMO fundamento que el paso «Numero de celdas» de M2 (F3.CELDAS): aquel
    # adopta N, este dice con que caudal quedo cada barril. Hasta EXT-2 la
    # memoria adoptaba N y nunca lo decia: imprimia Q = 9.0 junto a un y_n que
    # solo transporta 3.0.
    de_reparto = ()
    if material.forma is FormaSeccion.RECTANGULAR:
        de_reparto = (paso(
            "F3.CELDAS",
            codigo="3.3",
            que="Caudal que entra a cada celda del marco",
            formula="Q_celda = Q / N, con N celdas hidraulicamente iguales: los "
                    "coeficientes de HDS-5, el radio hidraulico y los dos "
                    "controles se resuelven POR BARRIL",
            formula_cita_id="HDS5_3ED.5.4.3#REPARTO",
            citas_textuales=("HDS5_3ED.5.4.3#REPARTO",),
            sustitucion=(
                Magnitud("Q", Q, "m3/s",
                         "caudal de diseño del PUNTO: la columna Q_m3s del CSV "
                         "en la Familia A, y el caudal declarado del drenaje "
                         "longitudinal o del canal en las B y C",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("N", celdas, "celdas",
                         f"adoptado en el criterio '{CRITERIO_N_CELDAS_CAJON}'; "
                         "es el mismo numero que V6 verifica", cifras=None)),
            resultado=Magnitud("Q_celda", Q_celda, "m3/s",
                               "caudal de UNA celda: es el Q con que se "
                               "resuelven los pasos 4.1 a 4.4 de abajo",
                               cifras=CIFRAS_MAGNITUD),
            veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                                explicacion="paso de calculo: no contrasta "
                                            "contra ningun umbral"),
            nota_del_proyecto=(
                "La fuente lo escribe como un SUPUESTO condicionado a barriles "
                "hidraulicamente identicos, que es lo que la seccion modela: "
                "una celda repetida N veces. Barriles distintos o con cotas "
                "distintas piden el procedimiento iterativo de HDS-5 Section "
                "3.5, que este proyecto no implementa."),
        ),)
    # EL PASO QUE DICE COMO SE CALCULAN A, P Y R, y va PRIMERO porque es el
    # que hace legible al siguiente: Manning define Q en funcion de A y de R,
    # y el num. 4.1.1.3.6 NO dice como se calcula ninguno de los dos. Ese
    # hueco lo llena la forma de la seccion, y hasta C4 la memoria lo daba por
    # sabido -- el paso de Manning afirmaba «A, P y R son los de la seccion
    # circular parcialmente llena» sin escribir ninguna de las tres formulas,
    # y con un marco esa frase habria sido ademas falsa --.
    #
    # LAS FORMULAS LAS PONE LA SECCION (`formula_geometria`), no este modulo:
    # es la misma razon por la que M4 no sabe de que forma es. Y los valores
    # que se sustituyen son los que el `Geometria` YA TRAE -- `g.A`, `g.P`,
    # `g.R`, `g.y` --: no se recalculan con `seccion.area(y)` ni con
    # `seccion.perimetro(y)`, que es exactamente lo que la regla vinculante
    # #12 existe para impedir.
    geometria_normal = normal.geometria
    # LA FILA DEL PASO 4.1 QUE ES LA ALTURA DEL BARRIL, para que los pasos 4.2
    # y 4.3 puedan apuntar a ella por su nombre: `magnitudes_de_forma()` la
    # pone la ULTIMA a proposito («D» en la circular, «H» en el marco), y el
    # auditor de PD midio que decir «el mismo D del paso 4.1» era falso para
    # el marco, cuyo paso 4.1 no imprime ninguna fila «D».
    fila_altura = seccion.magnitudes_de_forma()[-1].simbolo
    de_seccion = paso(
        "F4.SECCION",
        codigo="4.1",
        que="Area, perimetro mojado y radio hidraulico de la seccion, para el "
            "tirante de trabajo",
        formula=seccion.formula_geometria(),
        formula_cita_id="MC_HHD.4.1.1.3.6",
        sustitucion=seccion.magnitudes_de_forma() + (
            Magnitud("y", geometria_normal.y, "m",
                     "tirante normal, que es el que resuelve el paso "
                     "siguiente: Brent recorre ESTA misma seccion hasta que "
                     "Manning iguala el caudal de diseño",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("A", geometria_normal.A, "m2",
                     "area hidraulica a ese tirante; sale de la formula de "
                     "arriba y no se vuelve a calcular en ningun otro sitio",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("P", geometria_normal.P, "m",
                     "perimetro mojado a ese tirante, por la misma via",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("R", geometria_normal.R, "m",
                           "radio hidraulico A/P: es el unico de los tres que "
                           "entra en Manning, y con el la seccion queda "
                           "resuelta", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo: no contrasta contra "
                                        "ningun umbral"),
        nota_del_proyecto=(
            f"La seccion es «{seccion.etiqueta()}», la que esta corrida "
            f"esta resolviendo. El numeral prescribe Manning y "
            f"define A, P y R, y no fija la forma del conducto: por eso las "
            f"formulas de arriba no son una eleccion del proyecto sino la "
            f"geometria de la seccion adoptada, y por eso mismo cambian con "
            f"ella sin que cambie el procedimiento."),
    )

    de_manning = paso(
        "F4.MANNING",
        codigo="4.1",
        que="Tirante normal y velocidades en el conducto",
        formula="Q = (k_n/n) * A * R^(2/3) * S^(1/2), con k_n = K_MANNING_SI "
                "el coeficiente de unidades del SI, resuelta con Brent "
                "sobre el parametro de llenado de la seccion; A, P y R son "
                "los del paso anterior",
        formula_cita_id="MC_HHD.4.1.1.3.6",
        sustitucion=(
            # EL COEFICIENTE DE UNIDADES VA EN LA SUSTITUCION, y hasta PD no
            # iba: la formula no es homogenea, y el 1.0 que la cierra en SI
            # estaba implicito en el (1/n). Es una constante empirica
            # dependiente de unidades como KU_SI, y la memoria la imprime
            # con su unidad y su procedencia por la misma razon que imprime
            # Ku en q*. Vale 1.0: no mueve ningun numero.
            Magnitud("k_n", K_MANNING_SI, "m^(1/3)/s",
                     "coeficiente de unidades de Manning en SI, "
                     "constantes_normativas.K_MANNING_SI: es el que hace "
                     "homogenea la formula (1.486 ft^(1/3)/s en el sistema "
                     "ingles, que NO se usa: todo el calculo opera en SI). El "
                     "Manual escribe la ec. (47) en forma SI, sin coeficiente",
                     cifras=CIFRAS_FACTOR),
            # EL Q CON QUE M3 RESOLVIO DE VERDAD (EXT-M-03): el de la celda.
            # Sin reparto es el del punto, y la procedencia lo dice.
            Magnitud("Q", Q_celda, "m3/s",
                     (f"caudal de UNA celda, Q/N con N = {celdas} del paso "
                      f"del reparto: es el que transporta el tirante de "
                      f"abajo, no el caudal del punto ({Q:.{CIFRAS_MAGNITUD}f} "
                      f"m3/s)")
                     if celdas != 1 else
                     "caudal de diseño CON QUE CORRIO el punto: la columna "
                     "Q_m3s del CSV en la Familia A, y el caudal declarado "
                     "del drenaje longitudinal o del canal en las B y C",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("S", S, "m/m",
                     "pendiente con que corrio el diseño: la del cauce salvo "
                     "que el punto declare 'S_conducto'. Es la MISMA que usa "
                     "la Fase 7 (MAT-D9)", cifras=CIFRAS_FINA),
            *seccion.magnitudes_de_forma(),
            Magnitud("n_max", material.n_para_capacidad, "",
                     f"extremo superior del rango de la Tabla Nº 09 para "
                     f"«{material.nombre}»: rama de CAPACIDAD", cifras=CIFRAS_FINA),
            Magnitud("n_min", material.n_para_velocidad_maxima, "",
                     f"extremo inferior del mismo rango: rama de EROSION",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("y_normal", normal.geometria.y, "m",
                           "resuelto con n_max, que da mas tirante para el "
                           "mismo Q", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo: no contrasta contra "
                                        "ningun umbral"),
        nota_del_proyecto=(
            f"La seccion se resuelve DOS veces, una por extremo del rango de "
            f"n: V_erosion = {normal.V_erosion:.3f} m/s con n_min (estimacion "
            f"ALTA, para los techos: V3 y el d50 de la Fase 6) y "
            f"V_sedimentacion = {normal.V_sedimentacion:.3f} m/s con n_max "
            f"(estimacion BAJA, para el piso de V2). No hay una «la» "
            f"velocidad: un piso y un techo tienen extremos conservadores "
            f"opuestos."),
    )

    # SU FUNDAMENTO YA NO ES `F4.CONTROL`, Y NO ES UN CAMBIO COSMETICO. Ese
    # fundamento dice, literalmente, «Carga a la entrada HW por los dos
    # controles del HDS-5, entrada y salida, y adopcion del mayor»: describe
    # OTRO paso, y este lo tomaba prestado porque no habia uno propio. El
    # propio lo redacto CN en la §15.7 del plan de la Familia C -- `F4.YC_RECT`
    # --, y explica por que el critico se calcula: porque DOS pasos
    # posteriores lo consumen (la Forma 1 por H_c, y h_o del control de
    # salida). Vale para las dos formas, y por eso lo usan las dos.
    #
    # LA FORMULA SI DEPENDE DE LA VIA, y `critico.cerrado` es quien lo sabe.
    # Imprimir «resuelta con Brent» sobre un numero que salio de una formula
    # cerrada dejaria al revisor sin poder rehacerlo, que es exactamente el
    # defecto que C3 tuvo que corregir en el paso de la Forma 2.
    magnitudes_criticas = [
        Magnitud("Q", Q_celda, "m3/s",
                 "el mismo caudal del paso de Manning"
                 + (": el de UNA celda" if celdas != 1 else ""),
                 cifras=CIFRAS_MAGNITUD),
        *seccion.magnitudes_de_forma()]
    if critico.cerrado:
        magnitudes_criticas.append(
            Magnitud("T", critico.geometria.T, "m",
                     "ancho superficial en el estado critico. Es el que la "
                     "solucion cerrada divide (q = Q/T), y la solucion es "
                     "cerrada precisamente porque en esta forma NO depende "
                     "del tirante", cifras=CIFRAS_FACTOR))

    de_critico = paso(
        "F4.YC_RECT",
        codigo="4.2.1",
        que="Tirante critico de la seccion",
        formula=("y_c = (q^2/g)^(1/3) con q = Q/T: la solucion CERRADA de "
                 "Q^2/g = A^3/T cuando T no depende del tirante -- sin Brent"
                 if critico.cerrado else
                 "Q^2 / g = A^3 / T, resuelta con Brent sobre el parametro de "
                 "llenado de la seccion"),
        sustitucion=tuple(magnitudes_criticas),
        resultado=Magnitud("y_c", critico.y_c, "m",
                           "tirante critico; no depende de n",
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo"),
        # SE CONDICIONA POR FORMA, y antes no: la nota afirmaba sin matiz que
        # el critico entra «en la Forma 1 del control de entrada», y bajo
        # Forma 2 la ec. (A.2) NO usa H_c. Se imprimia igual en las dos.
        nota_del_proyecto=(
            ("Entra en las dos piezas siguientes: en la Forma 1 del control "
             "de entrada (por H_c) y en h_o del control de salida. Se "
             "resuelve UNA vez."
             if material.hds5.forma == FORMA_1 else
             "Esta carta es de FORMA 2 y su ecuacion de control de entrada "
             "-- la (A.2) -- NO usa H_c. El tirante critico se resuelve igual "
             "porque lo necesita h_o del control de salida, y solo para eso. "
             "Se resuelve UNA vez.")
            + (" La seccion despeja el critico y la solucion es EXACTA: no "
               "hay convergencia que pueda fallar."
               if critico.cerrado else
               " En esta forma la ecuacion es trascendente en el parametro de "
               "llenado y hace falta un segundo Brent, distinto del de "
               "Manning: no interviene ni n ni S.")
            # EL TECHO, IMPRESO SOLO CUANDO MUERDE. La comparacion es ciega a
            # la forma --`seccion.altura` es el contrato del protocolo-- y en
            # la circular no se dispara nunca, porque alli el tirante critico
            # se acerca a D sin alcanzarlo. Sin esta linea, un punto con el
            # critico topado imprimiria el numero topado sin decir que lo
            # esta, que es la mitad silenciosa del defecto.
            + (f" El tirante critico ALCANZA la altura interior del barril "
               f"({seccion.altura:.{CIFRAS_MAGNITUD}f} m) y queda topado ahi: "
               f"el HDS-5 (num. 3.3.3, pag. impresa 3.24) establece que el "
               f"tirante critico no puede exceder la altura interior, y sus "
               f"cartas del Apendice C lo acotan igual. Sin ese techo el "
               f"calculo daria un area critica MAYOR que la del barril "
               f"entero."
               if critico.y_c >= seccion.altura else "")),
    )

    # EL PASO QUE DICE QUE ECUACION SE USO, y va ANTES del control de entrada
    # porque es lo primero que un revisor necesita saber para poder rehacer el
    # numero: ver K y M sin saber en que ecuacion entraron no permite
    # reconstruir nada. Su `por_que` es `F4.FORMA_HDS5` TAL CUAL lo dejo C2 en
    # el registro, con sus tres citas ya verificadas -- no se redacta otra vez
    # aqui, que seria la segunda copia que NOR-MEM-01 persigue --.
    forma = material.hds5.forma
    de_forma = paso(
        "F4.FORMA_HDS5",
        codigo="4.2",
        que="Forma de la ecuacion de control de entrada del HDS-5",
        formula=("Forma 1: HW/D = H_c/D + K*(q*)^M + Ks*S, ec. (A.1)  |  "
                 "Forma 2: HW/D = K*(q*)^M, ec. (A.2), SIN el termino Ks*S"),
        formula_cita_id="HDS5_3ED.A.2",
        sustitucion=(
            Magnitud("Equation Form", forma, "",
                     "columna de la Tabla A.1 para la carta de esta "
                     "embocadura; no la elige el proyectista",
                     cifras=CIFRAS_FACTOR),
            Magnitud("K", material.hds5.K, "",
                     f"constante de la carta, ajustada a la Forma {forma}",
                     cifras=CIFRAS_FINA),
            Magnitud("M", material.hds5.M, "",
                     f"exponente de la carta, ajustado a la Forma {forma}",
                     cifras=CIFRAS_FINA)),
        resultado=Magnitud("forma aplicada", forma, "",
                           f"se resuelve con la ecuacion "
                           f"({'A.1' if forma == FORMA_1 else 'A.2'}) del "
                           f"num. A.2.1", cifras=CIFRAS_FACTOR),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo"),
        citas_textuales=("HDS5_3ED.A.3#FORMAS",),
        # AQUI VIVIO LA VIA 2 DEL CANAL DE DISCREPANCIAS, de I3 a D9: este
        # paso declaraba `discrepancias=("DIS-HR-FORMAS-HDS5",)` porque D-9
        # hablaba del NUMERO que este paso sustituye -- la forma de la
        # ecuacion, que la v8 rotulaba «Forma 1» sin decir que existiera la
        # 2 --, no de un texto que el paso entrecomille: el caso exacto para
        # el que `PasoDeMemoria.discrepancias` existe. D9 corrigio la v8 (los
        # cinco puntos de la bitacora §16.19 de ruta_familia_c.md), paso la
        # discrepancia a RESUELTA y retiro la tupla EN EL MISMO COMMIT, porque
        # la guardia de `paso()` no admite resueltas: quien abra hoy la v8
        # encuentra la Forma 2 escrita y no hay nada que defender. La via
        # queda censada sin usuario de produccion (ficha D9-01 de
        # docs/decisiones_diferidas.md y
        # `test_la_via_del_paso_quedo_sin_usuario_al_resolver_FORMAS`); el
        # `Fundamento` de este paso sigue citando TA.1, A.2 y A.3#FORMAS, y
        # por esa puerta (via 1) le seguiria llegando cualquier discrepancia
        # viva sobre esos numerales.
        nota_del_proyecto=(
            f"Esta corrida usa la FORMA {forma}. "
            + ("La Forma 1 lleva el termino de correccion por pendiente "
               "Ks*S; la Forma 2 no lo lleva, y por eso no aparece en la "
               "sustitucion del paso siguiente cuando gobierna la Forma 2."
               if forma == FORMA_1 else
               "La Forma 2 NO lleva el termino Ks*S: no se omite aqui, es "
               "que la ec. (A.2) no lo tiene. Ks sigue entrando en la rama "
               "SUMERGIDA, que es la ec. (A.3) y es comun a las dos formas.")),
    )

    # LA FORMULA Y LA SUSTITUCION DEPENDEN DE LA FORMA, y hasta que un auditor
    # lo vio NO era asi: bajo Forma 2 este paso imprimia la ec. (A.1) entera
    # -- con su H_c/D y su Ks*S -- y metia `Ks` en la sustitucion, para
    # explicar un numero que sale de la (A.2), que no tiene ninguno de los
    # dos. Es el MISMO defecto que esta sesion existe para impedir, mudado del
    # docstring al reporte; y el paso `de_forma`, unas lineas mas arriba,
    # PROMETIA POR ESCRITO que no pasaba.
    #
    # `Ks` entra en la sustitucion solo si el numero impreso lo contiene: en
    # Forma 1 siempre, y en Forma 2 solo cuando la rama es sumergida o de
    # transicion -- la (A.3) si lo lleva, y la recta lo hereda por su extremo
    # superior --.
    ks_participa = (material.hds5.forma == FORMA_1
                    or entrada.regimen is not RegimenEntrada.NO_SUMERGIDO)
    if material.hds5.forma == FORMA_1:
        _no_sumergida = "HW/D = H_c/D + K*(q*)^M + Ks*S, ec. (A.1)"
    else:
        _no_sumergida = "HW/D = K*(q*)^M, ec. (A.2) -- sin H_c/D y sin Ks*S"
    magnitudes = [
        Magnitud("q*", entrada.q_estrella, "",
                 "caudal adimensional Ku*Q/(A_llena*D^0.5); decide la "
                 "rama", cifras=CIFRAS_MAGNITUD)]
    if ks_participa:
        magnitudes.append(
            Magnitud("Ks", material.hds5.Ks, "",
                     "correccion por pendiente de la formulacion del HDS-5; "
                     "NO figura en la Tabla A.1", cifras=CIFRAS_FACTOR))
    # EL D QUE CIERRA LA DIMENSION, y hasta PD no estaba: las ecuaciones de
    # arriba dan HW/D, adimensional, y el resultado del paso es HW_entrada en
    # metros. Sin el D en la sustitucion el paso no cerraba por si solo (lo
    # midio el piloto dimensional de I4). Es `seccion.altura`, el mismo
    # numero con que `control_entrada` multiplica HW/D: no se recalcula.
    magnitudes.append(
        Magnitud("D", seccion.altura, "m",
                 f"altura interior del barril, el «D» de HDS-5, con que HW/D "
                 f"pasa a HW_entrada: es la fila «{fila_altura}» del paso 4.1"
                 + ("" if fila_altura == "D" else
                    " (la altura del marco; el diametro en la circular)"),
                 cifras=CIFRAS_FACTOR))
    # LOS DOS EXTREMOS DE LA RECTA, solo cuando la rama es la de transicion
    # (EXT-M-04): un HW «por la recta» sin los dos numeros entre los que se
    # interpolo no se puede rehacer. El inferior se evalua para Q_lo, el
    # caudal de q* = 3.5, y bajo Forma 1 con el H_c de ESE caudal.
    if entrada.transicion is not None:
        t = entrada.transicion
        magnitudes.append(
            Magnitud("Q_lo", t.Q_lo, "m3/s",
                     f"caudal que corresponde a q* = {Q_LIM_NO_SUMERGIDO}: "
                     f"{Q_LIM_NO_SUMERGIDO}*A_llena*D^0.5/Ku. El extremo "
                     "inferior de la recta es la rama no sumergida para ESTE "
                     "caudal, no para el del punto", cifras=CIFRAS_MAGNITUD))
        if t.H_c_lo is not None:
            magnitudes.append(
                Magnitud("H_c_lo", t.H_c_lo, "m",
                         "energia especifica critica de Q_lo, resuelta con el "
                         "mismo solver del paso 4.2.1: es el H_c que entra en "
                         "la ec. (A.1) del extremo inferior", cifras=CIFRAS_MAGNITUD))
        magnitudes.append(
            Magnitud("HW_lo", t.HW_lo, "m",
                     f"extremo inferior: la rama no sumergida en q* = "
                     f"{Q_LIM_NO_SUMERGIDO}, por D", cifras=CIFRAS_MAGNITUD))
        magnitudes.append(
            Magnitud("HW_hi", t.HW_hi, "m",
                     f"extremo superior: la ec. (A.3) en q* = "
                     f"{Q_LIM_SUMERGIDO}, por D", cifras=CIFRAS_MAGNITUD))

    # EL PISO ADOPTADO (PF-1, PC-03), solo cuando la ecuacion devolvio una
    # carga nula o negativa y el criterio `hw_entrada_fuera_de_rango` esta
    # declarado «energia_critica»: la memoria imprime lo que la ecuacion dio,
    # el S* de la carta y lo que se adopto en su lugar. Sin piso, nada de
    # esto aparece, que es el caso de todo el corredor del repositorio.
    piso = entrada.piso
    if piso is not None:
        magnitudes.append(
            Magnitud("HW/D_formula", piso.HW_sobre_D_formula, "",
                     "lo que la ecuacion de control de entrada devolvio con "
                     "la correccion por pendiente Ks*S: nulo o negativo, una "
                     "lamina bajo el fondo del conducto (MAT-D10)",
                     cifras=CIFRAS_MAGNITUD))
        if piso.S_limite is not None:
            magnitudes.append(
                Magnitud("S*", piso.S_limite, "m/m",
                         "pendiente desde la que la ecuacion deja de entregar "
                         "carga para este Q y este D: S* = X/(-Ks), con X el "
                         "HWi/D sin el termino de pendiente "
                         "(`pendiente_limite_de_signo`)", cifras=CIFRAS_MAGNITUD))
        magnitudes.append(
            Magnitud("H_c", entrada.critico.H_c, "m",
                     "energia especifica critica del paso 4.2.1, adoptada como "
                     f"piso de la carga por el criterio [A] '{piso.criterio}' "
                     f"= «{piso.adoptado}»", cifras=CIFRAS_MAGNITUD))
    nota_del_piso = ("" if piso is None else
                     f" LA CARGA IMPRESA ES UN PISO ADOPTADO, no la ecuacion: "
                     f"para este Q y este D la correccion por pendiente Ks*S "
                     f"dejo HW/D en {piso.HW_sobre_D_formula:.5f}, y el "
                     f"criterio [A] '{piso.criterio}' esta declarado "
                     f"«{piso.adoptado}», de modo que HW_entrada = H_c. Es una "
                     f"adopcion del proyectista sobre un vacio de HDS-5 (PC-03, "
                     f"PF-1): ni la hoja de ruta ni la fuente fijan que carga "
                     f"corresponde fuera del rango de la correccion.")

    de_entrada = paso(
        "F4.CONTROL",
        codigo="4.2",
        que="Carga a la entrada bajo CONTROL DE ENTRADA",
        formula=(f"no sumergido (q* <= {Q_LIM_NO_SUMERGIDO}): {_no_sumergida}"
                 f"  |  sumergido (q* >= {Q_LIM_SUMERGIDO}): "
                 f"HW/D = c*(q*)^2 + Y + Ks*S, ec. (A.3)  |  entre ambos, "
                 f"recta entre los extremos de validez"),
        formula_cita_id="HDS5_3ED.A.2",
        sustitucion=tuple(magnitudes),
        resultado=Magnitud("HW_entrada", entrada.HW, "m",
                           f"carga sobre el fondo de la entrada, regimen "
                           f"«{entrada.regimen.value}»"
                           + ("" if piso is None else
                              f"; PISO adoptado por '{piso.criterio}'"),
                           cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo"),
        nota_del_proyecto=(
            "Las constantes K, M, c e Y salen de la Tabla A.1, carta y "
            "escala de la embocadura adoptada; las ECUACIONES salen del num. "
            "A.2, no de esa tabla (NOR-HDS-03). "
            + ("Ks aparece en la sustitucion porque el numero de arriba lo "
               "contiene." if ks_participa else
               "Esta carta es de Forma 2 y la rama aplicada es la NO "
               "sumergida: el numero de arriba no lleva Ks*S, y por eso Ks "
               "no aparece en la sustitucion.")
            + nota_del_piso),
    )

    de_salida = paso(
        "F4.HO",
        codigo="4.3",
        que="Carga a la entrada bajo CONTROL DE SALIDA, y las condiciones de "
            "uso que la fuente pone a h_o",
        formula="HW = H + h_o - S*L, con h_o = max(TW, (y_c + D)/2)",
        formula_cita_id="HDS5_3ED.3.3.3#HO",
        citas_textuales=("HDS5_3ED.3.3.3#HO", "HDS5_3ED.3.3.3#HO_SUMERGIDA"),
        sustitucion=(
            Magnitud("H", salida.H, "m",
                     "perdida de carga en el barril, con n_max y la longitud "
                     "del conducto", cifras=CIFRAS_MAGNITUD),
            # ke ENTRA EN LA SUSTITUCION AUNQUE NO ESTE EN LA FORMULA DE
            # ARRIBA, y hace falta: es el unico sumando de H que sale de una
            # DECLARACION y no de la geometria, de modo que sin el la memoria
            # publicaba un H sin decir de donde venia su termino de entrada.
            # Con el marco la procedencia lleva ademas la fila Y su rotulo de
            # agrupacion, porque en el bloque «Box, Reinforced Concrete» tres
            # filas se rotulan igual y el numero no identifica ninguna.
            Magnitud("ke", salida.ke, "",
                     _procedencia_ke(salida), cifras=CIFRAS_FACTOR),
            Magnitud("TW", TW, "m",
                     "tirante en el receptor durante la avenida, sobre el "
                     "fondo de la SALIDA. No es una cota",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("(y_c + D)/2", (critico.y_c + seccion.altura) / 2, "m",
                     "aproximacion de la linea de energia del HDS-5",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("h_o", salida.h_o, "m",
                     "el mayor de los dos anteriores"
                     + (" (manda TW: la salida esta ahogada)"
                        if salida.ahogado_por_TW else
                        " (manda la aproximacion geometrica)"),
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("S*L", salida.caida, "m",
                     "caida del conducto entre entrada y salida",
                     cifras=CIFRAS_MAGNITUD),
            # LA MAGNITUD QUE EL UMBRAL JUZGA SE IMPRIME, y hasta PD no se
            # imprimia: el resultado del paso es HW_salida en metros y el
            # umbral de la fuente es sobre HW/D, adimensional, de modo que el
            # veredicto y su margen se calculaban sobre un numero que la
            # memoria no mostraba (lo midio el piloto dimensional de I4). Se
            # traen el D y el cociente ya calculado (`salida.HW_sobre_D`, el
            # mismo objeto que decide `h_o_fuera_de_rango`): no se recalcula
            # nada y no cambia que se compara ni el veredicto.
            Magnitud("D", seccion.altura, "m",
                     f"altura interior del barril, el «D» de HDS-5, con que "
                     f"HW_salida se lleva a HW/D para el umbral de abajo: es "
                     f"la fila «{fila_altura}» del paso 4.1"
                     + ("" if fila_altura == "D" else
                        f" (la altura del marco, que NO es la «{fila_altura}» "
                        "de perdida de carga de esta misma sustitucion)"),
                     cifras=CIFRAS_FACTOR),
            Magnitud("HW/D", salida.HW_sobre_D, "",
                     "HW_salida/D: la magnitud sobre la que se juzga el "
                     "umbral de abajo y sobre la que se calcula el margen del "
                     "veredicto; es el mismo cociente que decide si h_o esta "
                     "fuera de rango",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud("HW_salida", salida.HW, "m",
                           "carga sobre el fondo de la entrada",
                           cifras=CIFRAS_MAGNITUD),
        umbral=Umbral(
            descripcion="HW/D minimo (sobre el HW/D de la sustitucion) por "
                        "debajo del cual la fuente dice que la aproximacion "
                        "de h_o NO debe usarse",
            valor=H_O_HW_SOBRE_D_MIN, unidad="",
            cita_id="HDS5_3ED.3.3.3#HO_1_2D",
            caracter="EXIGENCIA sobre el USO de la aproximacion, no sobre el "
                     "diseño: la fuente no prohibe el conducto, dice que su "
                     "propio numero no es de fiar ahi",
            aplicacion="h_o se calcula SIEMPRE; los dos limites se evaluan "
                       "punto por punto y solo cuentan si el control de "
                       "SALIDA gobierna, que es como la fuente los escribe. "
                       "Bajo 0.75 la aproximacion NO se usa: el HW del punto "
                       "es el del remanso del paso 4.3d (pag. 3.12: «backwater "
                       "calculations are required»). La tercera condicion "
                       "--que el barril fluya lleno en la mayor parte de su "
                       "longitud-- se MIDE en el paso 4.3c con el perfil de "
                       "la lamina."),
        # NO_CUMPLE Y NO DIFERIDO bajo 0.75 desde E-A, y memoria y pipeline
        # dicen lo mismo (SIS-A-07): la condicion de uso de la aproximacion
        # NO se cumple y, en consecuencia, la aproximacion NO se usa --el HW
        # del punto es el del remanso (4.3d) o, si el remanso no alcanza la
        # entrada, gobierna la entrada--. Hasta E-A no habia remanso y el
        # paso decia DIFERIDO con el bloqueo «metodo no evaluable». La
        # bandera `ResultadoHidraulico.h_o_fuera_de_rango` que la compuerta
        # de `servicio` lee queda en False con perfil.
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.NO_CUMPLE
                  if (gobierna_salida and salida.h_o_fuera_de_rango)
                  else TipoDeVeredicto.CUMPLE if gobierna_salida
                  else TipoDeVeredicto.SIN_VEREDICTO),
            margen=salida.HW_sobre_D - H_O_HW_SOBRE_D_MIN,
            unidad="",
            explicacion=(
                ("gobierna el control de ENTRADA: el HW de salida no es la "
                 "carga de este punto y las condiciones de h_o no aplican, "
                 "que es como la fuente las condiciona"
                 + (". Y gobierna porque el remanso del paso 4.3d no alcanza "
                    "la entrada: la aproximacion de arriba esta ademas fuera "
                    "de su rango (HW/D < 0.75) y no compite"
                    if perfil.sustituye_aproximacion else ""))
                if not gobierna_salida else
                "HW/D por debajo de 0.75 bajo control de salida, donde la "
                "fuente dice que la aproximacion de h_o no debe usarse: el "
                "HW de arriba NO es la carga del punto sino un numero fuera "
                "del dominio del metodo, y la carga es la del REMANSO del "
                "paso 4.3d (pag. 3.12: «For lower headwaters, backwater "
                "calculations are required»)"
                if salida.h_o_fuera_de_rango else
                "HW/D por debajo de 1.2: la fuente pide cautela, el barril "
                "puede fluir parcialmente lleno; el remanso del paso 4.3d es "
                "la comprobacion que la fuente pide"
                if salida.h_o_requiere_cautela else
                "HW/D dentro del rango de validez que la fuente declara")),
        nota_del_proyecto=(
            "HABIA UNA CIRCULARIDAD, y el paso 4.3c/4.3d la deshace: el HW "
            "con que se evaluan los dos limites es el que produce la propia "
            "aproximacion, de modo que un h_o sobreestimado puede hacer que "
            "el control de salida gobierne un punto donde no gobernaria. "
            "Desde E-A, bajo 0.75 el remanso decide: si no alcanza la "
            "entrada, el control de salida no impone carga y gobierna la "
            "entrada."),
    )

    # EL PASO DEL REGIMEN (EXT-3), despues del control de salida porque
    # necesita saber cual gobierna y antes de la adopcion porque V1, V2 y la
    # Fase 6 leen de aqui. El `resultado` es EL MISMO objeto `Magnitud` que
    # viaja en `ResultadoHidraulico.V_salida`: una lectura, no dos.
    de_regimen = paso(
        "F4.REGIMEN",
        codigo="4.3b",
        que="Regimen del barril y velocidad a la salida (HDS-5 3.1.6)",
        formula="regimen = LLENO si TW >= D, PARCIALMENTE LLENO si no; "
                "V_salida = Q_celda / A(y_salida), con y_salida = "
                "min(D, max(TW, y_c)) bajo control de salida y y_salida = y_n "
                "bajo control de entrada",
        formula_cita_id="HDS5_3ED.3.1.6#V_SALIDA",
        citas_textuales=("HDS5_3ED.3.1.6#V_SALIDA", "HDS5_3ED.3.1.6#V_SALIDA_TW",
                         "HDS5_3ED.3.3.2#V_SALIDA_ENTRADA",
                         "HDS5_3ED.3.1.3#SUMERGENCIA"),
        sustitucion=(
            Magnitud("TW", TW, "m",
                     "tirante en el receptor sobre el fondo de la SALIDA, el "
                     "mismo del paso 4.3", cifras=CIFRAS_MAGNITUD),
            Magnitud("D", seccion.altura, "m",
                     f"altura interior del barril, la fila «{fila_altura}» "
                     f"del paso 4.1", cifras=CIFRAS_FACTOR),
            Magnitud("y_c", critico.y_c, "m", "tirante critico del paso 4.2",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("y_n", normal.geometria.y, "m",
                     "tirante normal del paso 4.1, con n_max",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("Q_celda", Q_celda, "m3/s",
                     "caudal de UNA celda, el mismo con que se resolvieron "
                     "los pasos 4.1 a 4.3", cifras=CIFRAS_MAGNITUD),
            Magnitud("regimen", regimen.regimen.value, "",
                     "LLENO cuando TW >= D: la salida esta sumergida y la "
                     "seccion de salida y el tramo aguas abajo van llenos, sin "
                     "borde libre y a Q_celda/A_llena; bajo control de ENTRADA "
                     "el tramo de aguas arriba sigue supercritico y un resalto "
                     "lo llena hacia la salida (HDS-5 3.1.3, pag. 3.2), de modo "
                     "que LLENO no significa presion en toda la longitud. "
                     "PARCIALMENTE LLENO en otro caso, y con TW < D esta "
                     "corrida NO estima cuanto llena: exige el perfil de la "
                     "lamina de agua",
                     cifras=None),
            Magnitud("V_llena", regimen.V_llena, "m/s",
                     "Q_celda / A_llena: la velocidad del regimen LLENO, sin n "
                     "porque a seccion llena no hay tirante que resolver. Es la "
                     "que V2 compara cuando el barril va lleno",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("y_salida", regimen.y_salida, "m",
                     "tirante con que se mide la velocidad a la salida: "
                     "min(D, max(TW, y_c)) bajo control de salida, y_n bajo "
                     "control de entrada", cifras=CIFRAS_MAGNITUD),
            Magnitud("control", control.value, "",
                     "el control que gobierna, del paso 4.4", cifras=None)),
        resultado=regimen.V_salida,
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="paso de calculo: no contrasta contra "
                                        "ningun umbral. Lo que juzga V1 y V2 "
                                        "esta en la Fase 5, y lo que recibe "
                                        "la Fase 6 es V_salida"),
        nota_del_proyecto=(
            "Bajo control de SALIDA con el barril PARCIALMENTE LLENO el "
            "tirante y la velocidad DENTRO del conducto no son los del flujo "
            "uniforme: salen del perfil de la lamina de agua del paso 4.3c "
            "(HDS-5 Section 3.5), y V1 y V2 comparan su tirante maximo y su "
            "velocidad minima. No se inventa un criterio de llenado. La "
            "velocidad A LA SALIDA es la de arriba."),
    )

    # LOS DOS PASOS DEL PERFIL (E-A, pieza 6): 4.3c mide la longitud a
    # seccion llena --y con ella juzga la primera condicion de uso de h_o,
    # que hasta E-A solo se declaraba-- y 4.3d da la carga a la entrada por
    # remanso, que bajo 0.75D sustituye a la aproximacion del paso 4.3 y por
    # encima la comprueba. Van despues del regimen y antes de la adopcion,
    # porque la adopcion lee el HW efectivo que 4.3d decide.
    citas_perfil = ("HDS5_3ED.3.1.4#REMANSO", "HDS5_3ED.3.1.4#EMPALME",
                    "HDS5_3ED.3.1.4#HW_REMANSO", "HDS5_3ED.3.1.4#0_75D",
                    "HDS5_3ED.3.5#PERFIL", "HDS5_3ED.3.5.1#S1",
                    "HDS5_3ED.3.5.1#TIPO7")
    usa_aproximacion = gobierna_salida and not perfil.sustituye_aproximacion
    mayor_parte = ca.valor(CRITERIO_FRACCION_LLENA)
    llena_la_mayor_parte = perfil.fraccion_llena > mayor_parte
    porcentaje_lleno = f"{perfil.fraccion_llena * 100:.{CIFRAS_FACTOR}f} %"  # literal-ok: 100 convierte la fraccion a porcentaje de presentacion
    de_lo_lleno = (
        f"el barril va a seccion llena en {_fmt_m(perfil.longitud_llena_m)} m "
        f"de {_fmt_m(L)} m ({porcentaje_lleno} de su longitud)")
    sustitucion_perfil = (
        Magnitud("y_salida", perfil.y_salida_m, "m",
                 "frontera aguas abajo del remanso: el mayor de y_c y TW, "
                 "acotado a D (pag. 3.12, «critical depth at the culvert "
                 "outlet or … the tailwater depth, whichever is higher»)",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("y_n", normal.geometria.y, "m",
                 "tirante normal del paso 4.1, con n_max (Manning con "
                 "K_MANNING_SI = 1)", cifras=CIFRAS_MAGNITUD),
        (Magnitud("y_n'", perfil.y_asintota_m, "m",
                  "la asintota del perfil: el tirante en que la Ec. 3.7 da "
                  "Sf = S con el mismo n. Queda un 0.05 % por encima de y_n "
                  "porque K_FRICCION_SI/(2g) = 19.63/19.62, y el perfil se "
                  "clasifica e integra contra el (M1 baja hacia el, M2 sube "
                  "hacia el)", cifras=CIFRAS_FINA)
         if perfil.y_asintota_m is not None else
         Magnitud("y_n'", "sin asintota bajo la clave", "",
                  "la Ec. 3.7 no da Sf = S entre la frontera y la clave: la "
                  "lamina termina en y_c (S1), en la clave (M2 que se "
                  "empalma con la linea llena) o va llena", cifras=None)),
        Magnitud("y_c", critico.y_c, "m",
                 "tirante critico del paso 4.2: el limite de la curva S1 y "
                 "la frontera con salida libre", cifras=CIFRAS_MAGNITUD),
        Magnitud("D", seccion.altura, "m",
                 f"altura interior del barril, la fila «{fila_altura}» del "
                 f"paso 4.1: la clave donde la lamina libre se empalma con "
                 f"la linea de energia llena", cifras=CIFRAS_FACTOR),
        Magnitud("n", perfil.n, "",
                 "n MAXIMO de la Tabla N 09 (paso 4.1), el mismo de la "
                 "friccion del paso 4.3: mas rugosidad da mas remanso, mas "
                 "tirante y menos velocidad, el lado conservador de la "
                 "carga, de V1 y de V2", cifras=CIFRAS_FINA),
        Magnitud("S", S, "m/m", "pendiente del conducto, la del paso 4.1",
                 cifras=CIFRAS_FINA),
        Magnitud("L", L, "m", "longitud del conducto, la del paso 4.3",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("ke", perfil.ke, "",
                 "el mismo coeficiente de perdida de entrada del paso 4.3",
                 cifras=CIFRAS_FACTOR),
        Magnitud("HW_aprox", perfil.HW_aproximado_m, "m",
                 "la carga del paso 4.3, por la aproximacion h_o = max(TW, "
                 "(y_c + D)/2)", cifras=CIFRAS_MAGNITUD),
        Magnitud("HW_aprox/D", salida.HW_sobre_D, "",
                 "el cociente que decide si la aproximacion se usa: por "
                 "debajo de 0.75 la sustituye el remanso",
                 cifras=CIFRAS_MAGNITUD),
        Magnitud("perfil", perfil.tipo.value, "",
                 "rotulo del perfil resuelto (HDS-5 Section 3.5.1): M1 baja "
                 "hacia y_n desde un TW alto, M2 sube hacia y_n, S1 baja "
                 "hacia y_c en pendiente pronunciada, uniforme si la "
                 "frontera es y_n, llena si la linea de energia llena "
                 "alcanza la entrada", cifras=None),
        Magnitud("escalones", perfil.rungs, "",
                 "escalones de la escalera del paso directo sobre el "
                 "parametro propio de la seccion (precision numerica, "
                 "tolerancias.PASOS_PERFIL_LAMINA)", cifras=None),
    )
    de_perfil = paso(
        "F4.PERFIL",
        codigo="4.3c",
        que="Perfil de la lamina de agua por paso directo: longitud a "
            "seccion llena, y la primera condicion de uso de h_o, MEDIDA",
        formula="desde y_salida = min(D, max(y_c, TW)) hacia la entrada, "
                "escalon a escalon: dx = (E_abajo - E_arriba) / (S - Sf_medio), "
                "con E = y + V^2/(2g) y Sf = Ku*n^2*V^2/(R^(4/3)*2g), Ec. 3.7; "
                "donde la lamina esta sobre la clave rige la linea de energia "
                "llena con Sf_llena. L_llena = longitud sobre la clave; "
                "fraccion_llena = L_llena / L",
        formula_cita_id="HDS5_3ED.3.1.4#REMANSO",
        citas_textuales=citas_perfil + ("HDS5_3ED.3.3.3#HO",),
        sustitucion=sustitucion_perfil,
        resultado=Magnitud("fraccion_llena", perfil.fraccion_llena, "",
                           f"longitud a seccion llena entre la longitud del "
                           f"conducto: {de_lo_lleno}. Es la primera de las "
                           "tres salidas del perfil que HDS-5 3.5.1 nombra "
                           "(«length of barrel flowing full»)",
                           cifras=CIFRAS_MAGNITUD),
        umbral=Umbral(
            descripcion="fraccion de la longitud a seccion llena por encima "
                        "de la cual el barril fluye lleno «for most of its "
                        "length» (lectura del proyecto: mas de la mitad, "
                        "citas.INTERPRETACION_MAYOR_PARTE; el numero es el "
                        f"criterio '{CRITERIO_FRACCION_LLENA}' [A])",
            valor=mayor_parte, unidad="",
            cita_id="HDS5_3ED.3.3.3#HO",
            criterio_aplicado=CRITERIO_FRACCION_LLENA,
            caracter="APROXIMACION con condicion de uso expresa («can only "
                     "be used if…»); la misma fuente la relaja en la pag. "
                     "3.12 hasta HW = 0.75D aun con el barril parcialmente "
                     "lleno en toda su longitud",
            aplicacion="Se MIDE siempre. Juzga solo cuando la aproximacion "
                       "del paso 4.3 es la carga del punto (control de "
                       "salida con HW/D >= 0.75); si no se cumple, el HW "
                       "sigue siendo el de la aproximacion --la pag. 3.12 la "
                       "avala hasta 0.75D-- y el remanso del paso 4.3d se "
                       "imprime como la comprobacion que la pag. 3.24 pide. "
                       "No rechaza el punto: es la condicion ideal de un "
                       "metodo, no una exigencia sobre el diseño (v8 §4.3)."),
        veredicto=Veredicto(
            tipo=(TipoDeVeredicto.SIN_VEREDICTO if not usa_aproximacion
                  else TipoDeVeredicto.CUMPLE if llena_la_mayor_parte
                  else TipoDeVeredicto.NO_CUMPLE),
            margen=perfil.fraccion_llena - mayor_parte,
            unidad="",
            explicacion=(
                (f"medido: {de_lo_lleno}. "
                 + ("gobierna el control de ENTRADA y las condiciones de uso "
                    "de h_o no aplican"
                    if not gobierna_salida else
                    "la aproximacion del paso 4.3 no se usa --HW/D < 0.75-- "
                    "y su condicion de uso no aplica: la carga del punto es "
                    "la del remanso del paso 4.3d"))
                if not usa_aproximacion else
                f"{de_lo_lleno}: la aproximacion h_o = (d_c + D)/2 se usa "
                "dentro de su primera condicion (barril lleno en la mayor "
                "parte de su longitud)"
                if llena_la_mayor_parte else
                f"{de_lo_lleno}: la aproximacion h_o = (d_c + D)/2 se usa "
                "FUERA de su primera condicion (pag. 3.24). El HW del punto "
                "sigue siendo el suyo porque la pag. 3.12 de la misma fuente "
                "da «adequate results» hasta HW = 0.75D aun con el barril "
                "parcialmente lleno en toda su longitud, y el remanso del "
                "paso 4.3d es la comprobacion que la fuente pide. No es un "
                "incumplimiento del diseño: es la condicion ideal de un "
                "metodo cuya validez la propia fuente extiende (v8 §4.3)")),
        nota_del_proyecto=(
            "Es el procedimiento de barril parcialmente lleno del Cap. III "
            "que hasta E-A este software no calculaba. LA ECUACION DEL PASO "
            "--dx = (E_abajo - E_arriba)/(S - Sf_medio)-- NO la escribe el "
            "HDS-5: es el balance de energia entre dos secciones del flujo "
            "gradualmente variado, que la fuente delega en el software de la "
            "Section 3.5; lo que la fuente escribe es de donde arranca el "
            "remanso, hacia donde avanza, la Ec. 3.7 y el empalme. Se integra "
            "sobre el parametro propio de la seccion (regla vinculante #12 de "
            "la Familia C) y no situa el resalto hidraulico: le basta saber si "
            "la curva S1 alcanza la cara de entrada (HDS-5 3.5.1)."),
    )
    if perfil.alcanza_entrada:
        resultado_remanso = Magnitud(
            "HW_remanso", perfil.HW_remanso_m, "m",
            f"y_entrada + (1 + ke)*V_entrada^2/(2g), con y_entrada = "
            f"{_fmt_m(perfil.y_entrada_m)} m y V_entrada = "
            f"{_fmt_m(perfil.V_entrada_m_s)} m/s del perfil"
            + (" (carga de presion: la linea de energia llena alcanza la "
               "entrada)" if perfil.tipo is TipoDePerfil.LLENA else ""),
            cifras=CIFRAS_MAGNITUD)
        explicacion_remanso = (
            "es la carga del punto bajo control de SALIDA: sustituye a la "
            "aproximacion del paso 4.3, fuera de su rango (HW/D < 0.75)"
            if gobierna_salida and perfil.sustituye_aproximacion else
            "es la carga del punto bajo control de SALIDA: la comprobacion "
            "que la pag. 3.24 pide en la banda de cautela da MAS carga que la "
            "aproximacion del paso 4.3, y del lado de la inundacion manda la "
            "mayor (v8 §4.3, nota de E-A)"
            if gobierna_salida and perfil.comprobacion_manda else
            "comprobacion del paso 4.3, que sigue siendo la carga del punto: "
            "la aproximacion esta dentro del rango que la pag. 3.12 avala y "
            "pide igual o mas carga que el remanso"
            if gobierna_salida else
            "no es la carga del punto: gobierna el control de ENTRADA"
            if not perfil.sustituye_aproximacion else
            "no es la carga del punto: gobierna el control de ENTRADA, cuyo "
            "HW supera al del remanso")
    else:
        resultado_remanso = Magnitud(
            "HW_remanso", "no alcanza la entrada", "",
            f"la curva S1 corta el tirante critico a x = "
            f"{_fmt_m(perfil.x_fin_remanso_m)} m de la salida, antes de la "
            f"entrada (L = {_fmt_m(L)} m): aguas arriba el flujo es "
            "supercritico y lo controla la entrada (HDS-5 3.5.1: la S1 se "
            "usa «if the S1 curve extends to the face of the culvert»)",
            cifras=None)
        explicacion_remanso = (
            "el control de salida no impone carga alguna en la entrada: "
            "gobierna el control de ENTRADA"
            + (". La aproximacion del paso 4.3 --que lo clasificaba como "
               "control de salida-- esta fuera de su rango y no compite: es "
               "la circularidad deshecha"
               if perfil.sustituye_aproximacion else
               ". La aproximacion del paso 4.3 sigue siendo la carga de "
               "control de salida que compite, dentro del rango que la pag. "
               "3.12 avala"))
    de_remanso = paso(
        "F4.PERFIL",
        codigo="4.3d",
        que="Carga a la entrada por remanso, HW_remanso, y el tirante maximo "
            "y la velocidad minima del barril que V1 y V2 comparan",
        formula="HW_remanso = y_entrada + (1 + ke)*V_entrada^2/(2g), con "
                "y_entrada el tirante (o la carga de presion) del perfil en "
                "x = L; y_max = tirante maximo del perfil; V_min = Q_celda / "
                "A(y_max)",
        formula_cita_id="HDS5_3ED.3.1.4#HW_REMANSO",
        citas_textuales=citas_perfil,
        sustitucion=(
            (Magnitud("y_entrada", perfil.y_entrada_m, "m",
                      "tirante (o carga de presion) del perfil en la entrada "
                      "(x = L)", cifras=CIFRAS_MAGNITUD)
             if perfil.alcanza_entrada else
             Magnitud("y_entrada", "no alcanza la entrada", "",
                      "el remanso termina antes de la entrada (ver el "
                      "resultado)", cifras=None)),
            Magnitud("ke", perfil.ke, "",
                     "el mismo coeficiente de perdida de entrada del paso 4.3",
                     cifras=CIFRAS_FACTOR),
            Magnitud("Q_celda", Q_celda, "m3/s",
                     "caudal de UNA celda, el mismo de los pasos 4.1 a 4.3",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("y_max", perfil.y_max_m, "m",
                     "tirante MAXIMO del perfil a lo largo del barril (D si "
                     "hay tramo lleno; incluye el tirante normal del tramo "
                     "supercritico aguas arriba de un resalto): el que V1 "
                     "compara bajo control de salida", cifras=CIFRAS_MAGNITUD),
            Magnitud("V_min", perfil.V_min_m_s, "m/s",
                     "Q_celda / A(y_max), la velocidad MINIMA del barril: la "
                     "que V2 compara bajo control de salida",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("alcanza_entrada", "si" if perfil.alcanza_entrada else "no",
                     "", "si el remanso llega a la cara de entrada (HDS-5 "
                     "3.5.1)", cifras=None)),
        resultado=resultado_remanso,
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion=explicacion_remanso),
        nota_del_proyecto=(
            "Las velocidades de aproximacion y de salida se toman nulas, como "
            "en el metodo manual (num. 3.3.3). Con la linea de energia llena "
            "de punta a punta este numero es exactamente el HW = H + h_o - "
            "S*L del paso 4.3 con h_o = TW."),
    )

    de_gobernante = paso(
        "F4.CONTROL",
        codigo="4.4",
        que="Cual de los dos controles gobierna",
        formula="HW = max(HW_entrada, HW_salida), con HW_salida el del remanso "
                "(4.3d) si HW_aprox/D < 0.75, el mayor de aproximacion y remanso "
                "si 0.75 <= HW_aprox/D < 1.2, y el de la aproximacion (4.3) si "
                "no; sin remanso que alcance la entrada bajo 0.75, gobierna la "
                "entrada",
        formula_cita_id="HDS5_3ED.A.2",
        citas_textuales=("HDS5_3ED.3.1.4#0_75D",),
        sustitucion=(
            Magnitud("HW_entrada", entrada.HW, "m", "pieza 4.2",
                     cifras=CIFRAS_MAGNITUD),
            Magnitud("HW_salida", HW_salida_efectivo, "m",
                     "pieza 4.3d, el remanso: sustituye a la aproximacion, "
                     "fuera de su rango"
                     if perfil.sustituye_aproximacion and perfil.alcanza_entrada
                     else "pieza 4.3, la aproximacion, fuera de su rango y sin "
                     "remanso que alcance la entrada: NO compite (4.3d)"
                     if perfil.sustituye_aproximacion
                     else "pieza 4.3d, el remanso: en la banda de cautela la "
                     "comprobacion pide mas carga que la aproximacion y manda"
                     if perfil.comprobacion_manda
                     else "pieza 4.3, la aproximacion, dentro del rango que la "
                     "pag. 3.12 avala; el remanso de 4.3d la comprueba",
                     cifras=CIFRAS_MAGNITUD)),
        resultado=Magnitud(
            "HW", HW_salida_efectivo if gobierna_salida else entrada.HW, "m",
            f"carga de diseño del punto; gobierna el control de "
            f"{control.value}", cifras=CIFRAS_MAGNITUD),
        veredicto=Veredicto(tipo=TipoDeVeredicto.SIN_VEREDICTO,
                            explicacion="adopcion, no verificacion"),
        nota_del_proyecto=(
            "Cada control es una restriccion independiente sobre la misma "
            "estructura y manda la que exige MAS carga. El par se conserva "
            "entero y no solo el maximo: si gobierna la entrada se trabaja la "
            "embocadura o el diametro; si gobierna la salida, el problema "
            "esta aguas abajo (TW del receptor) y agrandar el tubo puede no "
            "mover el HW."),
    )

    # LA TRAZA DE FASE 3 VA DELANTE, y no la emite M4: la trae el material.
    # M2 decide en Fase 3 que tipo de estructura, que progresion de secciones,
    # cuantas celdas y que fila de rugosidad, y emite un `PasoDeMemoria` por
    # cada una. Llegan por aqui porque este es el canal que M11 imprime bajo
    # «Fases 3 y 4»; abrir uno nuevo en el reporte es de otra sesion. En la
    # circular la tupla viene VACIA y no se mueve nada: el tubo no elige en
    # Fase 3 -- su fila y su carta son lectura directa de una tabla --.
    return material.pasos + de_reparto + (de_seccion, de_manning, de_critico,
                                          de_forma, de_entrada, de_salida,
                                          de_regimen, de_perfil, de_remanso,
                                          de_gobernante)


def caudal_por_celda(Q: float, material: Material) -> Tuple[float, int]:
    """
    (Q/N, N): el caudal que entra a UNA celda y cuantas hay (regla vinculante
    #3 de ruta_familia_c.md §6; HDS-5 num. 5.4.3, `HDS5_3ED.5.4.3#REPARTO`).

    VIVE EN M4 DESDE EXT-2, y antes era `MD._caudal_por_barril` (EXT-M-03).
    Con el reparto en el orquestador, M4 recibia el Q TOTAL y lo resolvia con
    un tirante normal que MD habia resuelto para Q/N: cinco cifras a nueve
    decimales, +113.8 % de HW y cambio de control en el marco de tres celdas.
    Y el camino `normal=None` de `resolver_control` -- Manning resuelto aqui
    -- ni siquiera repartia. Con el reparto DENTRO de la pieza que consume
    el caudal, los dos caminos reparten igual y MD solo lo pide para poder
    distinguir en el motivo el escalon que no transporta Q/N.

    LA CIRCULAR NO INVOCA NINGUN CRITERIO, y es deliberado: su catalogo no
    ofrece multibarril, N vale 1 por construccion del catalogo y no por una
    decision del proyectista. Invocar 'n_celdas_cajon' aqui la registraria
    como criterio USADO en toda corrida -- M11 imprime los usados -- y
    estaria diciendo que el tubo eligio tener una celda, que es falso.

    EL MARCO SI LO INVOCA, por `M2.numero_de_celdas`, que es la MISMA lectura
    con la MISMA guardia que usa V6: dos lecturas con dos guardias es como
    divergen los numeros.
    """
    if material.forma is not FormaSeccion.RECTANGULAR:
        return Q, 1
    celdas = numero_de_celdas(material)
    return Q / celdas, celdas


def resolver_control(seccion: Seccion, Q: float, S: float, L: float, TW: float,
                     material: Material,
                     normal: Optional[TiranteNormal] = None
                     ) -> Optional[ResultadoHidraulico]:
    """
    Resultado hidraulico completo de una combinacion punto/material/diametro:
    junta el tirante normal de M3 (Sec. 4.1) con las tres piezas de M4
    (Sec. 4.2 y 4.3) en un `ResultadoHidraulico`.

    `Q` ES EL CAUDAL DEL PUNTO, y lo que M3 y M4 resuelven es el de UNA
    celda, `caudal_por_celda(Q, material)` (EXT-M-03): con N celdas iguales
    cada barril recibe Q/N. El `ResultadoHidraulico` lleva los dos --`Q`
    total y `Q_celda_m3s`-- y el `PasoDeMemoria` del reparto. Si el
    orquestador inyecta `normal`, tiene que ser el tirante normal resuelto
    para Q/N: es el contrato de MD, que lo resuelve con el mismo
    `caudal_por_celda` para poder distinguir en el motivo el escalon que no
    transporta el caudal de la celda.

    Devuelve None si M3 no encuentra tirante normal para esa seccion y ese
    material -- el conducto no transporta Q/N en lamina libre, o va a
    presion --, con la misma lectura que en M3: no es un fallo, es "este
    material y esta seccion no alcanzan" y el orquestador de la Fase 4 pasa
    al siguiente escalon de M2.

    Reparto de rugosidades (regla de doble n, Sec. 4.1):
      - el tirante normal y la friccion del control de salida usan n_max
        (`material.n_para_capacidad`): conservador del lado de la inundacion;
      - las DOS velocidades que salen en `ResultadoHidraulico` viajan tal
        como las deja M3: `V_erosion` (n_min, estimacion alta) para los techos
        -- V3 y el d50 de Laushey -- y `V_sedimentacion` (n_max, estimacion
        baja) para el piso de autolimpieza de V2. M4 no elige entre ellas ni
        recalcula ninguna: solo las traslada;
      - el tirante critico no usa ninguno: no depende de n.

    El tirante critico se resuelve UNA vez y se inyecta en las dos piezas que
    lo necesitan (Forma 1 del control de entrada y h_o del control de salida).

    Y DESDE EXT-3 EMITE LA PIEZA 5 (EXT-M-01, PC-04): el regimen del barril
    (`regimen_del_barril`), la velocidad del regimen lleno y la velocidad a
    la salida por HDS-5 3.1.6 (`velocidad_de_salida`), como `Magnitud` con
    procedencia, mas el bloque h_o entero (h_o, TW, `ahogado_por_TW`) que
    hasta entonces se quedaba en `ControlSalida` (SIS-B-18). `control_salida`
    no cambia: la pieza 5 lee lo que aquella ya calculo.
    """
    Q_celda, celdas = caudal_por_celda(Q, material)
    if normal is None:
        normal = resolver_manning(seccion=seccion, Q=Q_celda, S=S,
                                  material=material)
    if normal is None:
        return None

    critico = tirante_critico(Q_celda, seccion)
    entrada = control_entrada(Q=Q_celda, seccion=seccion, S=S,
                              hds5=material.hds5, critico=critico)
    salida = control_salida(Q=Q_celda, seccion=seccion, S=S, L=L, TW=TW,
                            n=material.n_para_capacidad, critico=critico,
                            criterio_ke=criterio_ke_de(material))
    # LA PIEZA 6 (E-A): el perfil de la lamina, con el mismo n_max y el mismo
    # ke con que `control_salida` formo H. Decide, con `hw_gobernante`, cual
    # es el HW efectivo del control de salida y si ese control impone carga.
    perfil = perfil_lamina(Q_celda=Q_celda, seccion=seccion, S=S, L=L, TW=TW,
                           n=material.n_para_capacidad, ke=salida.ke,
                           critico=critico, HW_aproximado=salida.HW)
    _, control = hw_gobernante(entrada, salida, perfil)

    # HDS-5 escribe las dos condiciones de uso de h_o condicionadas a que el
    # control de salida GOBIERNE ("If outlet control governs and the headwater
    # depth ... is less than 1.2D"), y asi se propagan: si gobierna la entrada,
    # el HW de salida no es la carga del punto y no hay nada que advertir.
    gobierna_salida = control is ControlGobernante.SALIDA
    regimen = _regimen_y_salida(Q_celda=Q_celda, seccion=seccion, TW=TW,
                                critico=critico, normal=normal,
                                control=control)
    # EL HW DE SALIDA QUE SE PUBLICA es el efectivo (remanso bajo 0.75D,
    # aproximacion en el resto). Cuando el remanso no alcanza la entrada el
    # control de salida no impone carga y gobierna la entrada: se publica la
    # aproximacion, rotulada en el perfil como lo que es (fuera de rango y
    # sin remanso que la sustituya), para que el tipo siga llevando un
    # numero y la memoria pueda imprimir los dos.
    HW_salida_efectivo = (perfil.HW_efectivo_m if perfil.HW_efectivo_m is not None
                          else salida.HW)

    return ResultadoHidraulico(
        y_normal=normal.geometria.y,
        y_critico=critico.y_c,
        V_erosion=normal.V_erosion,
        V_sedimentacion=normal.V_sedimentacion,
        Q=Q,
        # Q y S salen en el resultado porque son los datos CON QUE SE
        # RESOLVIO, no los de la columna: la Familia B y la C traen su propio
        # caudal (Sec. 2.3) y el punto que no sigue el cauce declara su
        # pendiente. La Fase 7 los lee de aqui en vez de volver a elegirlos
        # (MAT-D9).
        S=S,
        HW_entrada=entrada.HW,
        # El piso adoptado por `hw_entrada_fuera_de_rango`, si lo hubo (PF-1):
        # el JSON y el comparador tienen que poder distinguir un punto cuyo
        # HW_entrada es H_c por adopcion de uno en que lo dio la ecuacion.
        piso_hw_entrada=entrada.piso,
        HW_salida=HW_salida_efectivo,
        control_gobernante=control,
        # «Este punto USA la aproximacion fuera de rango»: con perfil no
        # puede pasar --donde esta fuera de rango, no se usa-- y la bandera
        # queda en False. La compuerta de `servicio` la sigue leyendo para
        # el resultado sin perfil que M4 no produce (E-A).
        h_o_fuera_de_rango=(gobierna_salida and salida.h_o_fuera_de_rango
                            and not perfil.sustituye_aproximacion),
        h_o_requiere_cautela=gobierna_salida and salida.h_o_requiere_cautela,
        # El HW/D que esas dos banderas acotan, para que la memoria lo
        # imprima sin volver a dividir (C8, punto 2). Es el de SALIDA porque
        # es el que el num. 3.3.3 acota, y viaja siempre --- no solo cuando
        # gobierna la salida ---: las banderas ya llevan esa condicion. Y
        # SIGUE SIENDO EL DE LA APROXIMACION desde E-A (auditoria
        # adversarial): es el cociente que las dos banderas y la sustitucion
        # juzgan, y cambiarle la definicion bajo el mismo nombre era mezclar
        # el numero que se juzga con el que se publica. El HW efectivo viaja
        # en `HW_salida` y el remanso en `perfil`.
        HW_sobre_D_salida=salida.HW_sobre_D,
        Q_celda_m3s=Q_celda,
        numero_celdas=celdas,
        # La pieza 5 y el bloque h_o (EXT-3). `V_salida` es el MISMO objeto
        # que el paso F4.REGIMEN imprime como resultado.
        regimen_barril=regimen.regimen,
        V_llena_m_s=regimen.V_llena,
        V_salida=regimen.V_salida,
        y_salida_m=regimen.y_salida,
        h_o_m=salida.h_o,
        TW_m=salida.TW,
        ahogado_por_TW=salida.ahogado_por_TW,
        perfil=perfil,
        pasos=_pasos_hidraulicos(
            seccion=seccion, Q=Q, S=S, L=L, TW=TW, material=material, normal=normal,
            critico=critico, entrada=entrada, salida=salida, control=control,
            gobierna_salida=gobierna_salida, Q_celda=Q_celda, celdas=celdas,
            regimen=regimen, perfil=perfil),
    )
