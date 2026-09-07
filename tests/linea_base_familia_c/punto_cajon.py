"""
punto_cajon.py -- LA QUINTA CORRIDA DE LA LINEA BASE, y la unica que no es la CLI.

QUE CIERRA. `tests/test_linea_base.py` dejo declarado y medido su propio
punto ciego: de tres mutaciones ensayadas, la de cablear `forma = 1` en el
paso de memoria NO la ve, «porque HOY NINGUN PUNTO DEL FIXTURE USA FORMA 2:
las tres cartas circulares del catalogo son Forma 1, de modo que suponerla no
mueve un byte». Y termina: «El dia que C4 meta una seccion de cajon en el
fixture, la A pasara a ser visible tambien aqui». Este archivo es ese dia.

POR QUE NO ES LA CLI, QUE ES LO QUE HABRIA SIDO NATURAL. Porque la CLI todavia
no puede producir un cajon: `MD.disenar_material` construye
`SeccionCircular(D)` recorriendo la progresion de diametros de M2, y abrir ese
catalogo a la seccion rectangular es la sesion C5, no esta. El limite de
alcance de C4 lo dice con todas las letras -- «no abre el catalogo ni los
criterios del cajon» --. La alternativa era dejar la ceguera abierta una
sesion mas; esta corrida la cierra por el unico camino que no invade C5:
llamar a M3 y a M4 directamente, con la seccion que C4 SI trae.

=============================================================================
ESTO NO ES UN DISEÑO, Y NINGUN NUMERO DE AQUI ES UNA ADOPCION DEL PROYECTO
=============================================================================
Es un FIXTURE, de la misma naturaleza que `entradas_ampliadas.json` -- que
lleva escrita la misma advertencia -- y con la misma finalidad: EJERCITAR
CAMINOS DE CODIGO.

LAS CUATRO DECISIONES QUE C4 TOMO PRESTADAS ESTAN RESUELTAS, y no heredadas.
C4 escribio este driver antes de que existieran los criterios del cajon, de
modo que tuvo que inventarse un `Material` a mano -- con una fila de la Tabla
N 09, una carta de la Tabla A.1 y el `ke_entrada` del bloque de TUBO -- y
nombrar las cuatro como prestadas. C5 las cierra por donde correspondia:

  1. LA FILA DE LA TABLA N 09 es ahora el criterio 'n_manning_cajon' [N->],
     con su analogia declarada: el vacio es de FILA y no de grupo, y por eso
     la analogia se queda DENTRO del grupo A, que ya cubre al conducto
     cerrado. Aqui se DECLARA una de las dos filas de su ventana; no se
     inventa un rango.
  2. LA CARTA DE HDS-5 es ahora 'embocadura_cajon' [A]. Se declara la Carta 9
     escala 1 -- la misma que el caso patron CP5D --, que es de FORMA 2, que
     es lo que este artefacto existe para vigilar.
  3. `ke_entrada` YA NO SE USA: el marco lee 'ke_entrada_cajon', que sale del
     bloque «Box, Reinforced Concrete» de la Tabla C.2 y va emparejado con la
     embocadura declarada. La regla vinculante #11 queda cerrada, y con ella
     la trampa que la hacia peligrosa -- que el numero del tubo y el del cajon
     COINCIDEN para el cabezal a ras --.
  4. `geometria_control_salida` SIGUE INVOCANDOSE y ahora esta NOMBRADO. Es
     un [C] de perfil cuya justificacion razonaba con `R = D/4`, o sea sobre
     un tubo; C5 la reescribio para que cubra las dos formas y midio lo que
     cambia en un marco. La CONCLUSION no cambia -- se toma la seccion llena,
     porque es la seccion para la que HDS-5 deriva esa expresion -- y la
     MAGNITUD si: en un marco 2.00 x 1.50 la diferencia entre las dos R es del
     40 %, no del ~20 % del ejemplo circular.

LOS CUATRO CRITERIOS SE DECLARAN EN CALIENTE, por el mismo camino que usan la
GUI y la CLI (`establecer_valor_dinamico`), y por lo tanto atraviesan la misma
guardia que una declaracion real. Son VALORES DE LA CORRIDA DE PRUEBA -- la
memoria los imprime en el bloque "DECLARADOS SOLO PARA ESTA CORRIDA" -- y no
tocan `criterios_adoptados.py`: en el archivo los cinco siguen sin valor,
porque el num. 4.1.1.3.4 a) remite la seccion del cruce de canal a "cada
diseño particular" y el proyecto no puede escribirla.

El punto tampoco pasa por la Fase 5 ni por MD: no hay verificaciones, no hay
eleccion de material y no hay iteracion de catalogo. Es UNA combinacion,
resuelta una vez.

SALIDA. Un fragmento HTML con dos partes: un <pre> con los numeros que la
memoria no imprime (los HW de los dos controles, el que gobierna, las dos
velocidades) y los siete `PasoDeMemoria` que M3 y M4 emiten, pintados por el
MISMO `M11.bloque_pasos` que usa la memoria de produccion. Asi el oraculo
cubre las dos mitades: los numeros y las etiquetas.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _ruta in (RAIZ, RAIZ / "src"):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

import criterios_adoptados as ca                                    # noqa: E402
from modelos import (FormaSeccion, SeccionRectangular, TipoMaterial)  # noqa: E402
from modulos.M2_material import catalogo                             # noqa: E402
from modulos import M11_reporte as M11                               # noqa: E402
from modulos.M3_hidraulica import resolver_manning                   # noqa: E402
from modulos.M4_control import (control_entrada, control_salida,      # noqa: E402
                                criterio_ke_de,
                                resolver_control, tirante_critico)

# --- el punto, entero y en un solo sitio ------------------------------------
B = 2.00        # m   ancho interior de UNA celda (§4.1 del plan: "marco 2.00 x 1.50 m")
H = 1.50        # m   altura interior
Q = 6.00        # m3/s
S = 0.004       # m/m la misma pendiente que `entradas_ampliadas.json` declara para C-01
L = 20.00       # m   la longitud de CP-8
TW = 0.30       # m   el mismo TW del fixture ampliado
CARTA = "cajon_concreto_aleta_45_d043"   # Carta 9 escala 1, FORMA 2
FILA_N = "concreto_afinado"              # la unica subfila que no dice "tubo"
# La fila del bloque «Box, Reinforced Concrete» que corresponde a la carta
# declarada: aletas a 45 grados caen en «Wingwalls at 30 to 75 degrees to
# barrel», borde en escuadra -> ke = 0.4. NO es el 0.5 del tubo, y esa es
# exactamente la diferencia que la regla vinculante #11 existe para que se
# vea.
#
# SE DECLARA LA CLAVE DE LA FILA Y NO EL 0.4, que es lo que el criterio pide
# desde C5: en ese bloque el coeficiente no identifica la fila -- el 0.2 esta
# en tres y el 0.5 en dos --, de modo que un numero suelto dejaria a la
# memoria sin poder imprimir la condicion que lo justifica.
KE_CAJON = "cajon_aletas_30_75_escuadra"

# Elegido para que el punto caiga donde se quiere mirar, y se dice cual es cada
# cosa: y/H = 0.694 (dentro del 0.75 de V1), regimen SUBCRITICO (y_n = 1.040 m
# frente a y_c = 0.972 m) y q* = 2.957, o sea la rama NO SUMERGIDA -- la unica
# en que la ec. (A.2) se aplica pura, sin interpolar con la (A.3) --. Es
# justamente la rama en que cablear `forma = 1` cambia el numero.

# LOS CUATRO VALORES DE LA CORRIDA DE PRUEBA. Se declaran aqui, juntos, para
# que se lean de una vez y para que quede claro que son cuatro y no tres.
DECLARACIONES = {
    "embocadura_cajon": CARTA,
    "n_manning_cajon": FILA_N,
    # La progresion la lee la traza de Fase 3 que el catalogo emite (el paso
    # de `F3.SECCION_CANAL` publica la serie entera y el de
    # `F3.MANTENIMIENTO` su escalon mas chico). Se declara la serie que
    # CONTIENE la seccion de este fixture, para que el artefacto sea coherente
    # consigo mismo.
    "secciones_cajon_normalizadas": ((1.50, 1.20), (2.00, 1.50), (2.50, 2.00)),
    # UNA CELDA. Este driver no pasa por MD y por lo tanto no ejercita el
    # reparto Q/N -- con N = 1 daria el mismo numero de todos modos --, pero
    # se declara igual: un marco con la embocadura y el n declarados y sin
    # numero de celdas seria un expediente a medias, y lo que este artefacto
    # publica es una traza de memoria completa.
    "n_celdas_cajon": 1,
    "ke_entrada_cajon": KE_CAJON,
}


def _declarar():
    """
    Entra por `establecer_valor_dinamico`, que es la via de la GUI y de la
    CLI: lo que este fixture declara atraviesa la misma guardia
    (`_verificar_criterio`) que una declaracion del expediente.
    """
    for clave, valor in DECLARACIONES.items():
        ca.establecer_valor_dinamico(clave, valor)


def main() -> None:
    _declarar()
    marco = catalogo(TipoMaterial.CONCRETO_REFORZADO,
                     forma=FormaSeccion.RECTANGULAR)
    seccion = SeccionRectangular(B, H)
    normal = resolver_manning(seccion=seccion, Q=Q, S=S, material=marco)
    if normal is None:
        raise SystemExit(
            f"el fixture dejo de transportar su caudal: {seccion.etiqueta()} "
            f"con Q = {Q} m3/s y S = {S} no tiene tirante normal")
    resultado = resolver_control(seccion=seccion, Q=Q, S=S, L=L, TW=TW,
                                 material=marco, normal=normal)

    print("<!-- FIXTURE de la linea base: NO es un diseño. Ver el docstring "
          "de tests/linea_base_familia_c/punto_cajon.py -->")
    print(f"<h2>Punto de cajon &mdash; {seccion.etiqueta()}</h2>")
    print("<pre>")
    print(f"seccion            {seccion.etiqueta()}")
    print(f"carta HDS-5        {CARTA}  (Equation Form {marco.hds5.forma})")
    print(f"fila Tabla N 09    {FILA_N}  n = {marco.n_min} .. {marco.n_max}")
    print(f"Q                  {Q:.3f} m3/s")
    print(f"S                  {S:.4f} m/m")
    print(f"L                  {L:.3f} m")
    print(f"TW                 {TW:.3f} m")
    print(f"A_llena            {seccion.area_llena:.6f} m2")
    print(f"R_lleno            {seccion.radio_hidraulico_lleno:.6f} m")
    print(f"y_normal           {normal.geometria.y:.6f} m")
    print(f"y/H                {normal.geometria.y_sobre_D:.6f}")
    print(f"A                  {normal.geometria.A:.6f} m2")
    print(f"P                  {normal.geometria.P:.6f} m")
    print(f"R                  {normal.geometria.R:.6f} m")
    print(f"V_erosion          {normal.V_erosion:.6f} m/s")
    print(f"V_sedimentacion    {normal.V_sedimentacion:.6f} m/s")
    # Las tres piezas se vuelven a pedir para publicar lo que
    # `ResultadoHidraulico` no lleva -- la via del critico, q*, el regimen,
    # h_o --. Son deterministas y no dependen de nada resuelto antes: no hay
    # dos resultados posibles que puedan divergir.
    critico = tirante_critico(Q, seccion)
    entrada = control_entrada(Q, seccion, S, marco.hds5, critico)
    # `criterio_ke` EXPLICITO, y hace falta: su valor por defecto es
    # `CRITERIO_KE`, el del TUBO, de modo que este artefacto -- que es el del
    # CAJON -- registraba como usado el criterio de la otra forma. No mueve
    # ningun numero impreso (de esta llamada solo se publica `h_o`), y por eso
    # justamente habria pasado inadvertido. Lo midio la auditoria adversarial
    # de C5.
    salida = control_salida(Q, seccion, S, L, TW,
                            marco.n_para_capacidad, critico=critico,
                            criterio_ke=criterio_ke_de(marco))
    print(f"y_critico          {critico.y_c:.6f} m")
    print(f"critico cerrado    {critico.cerrado}")
    print(f"V_critica          {critico.V:.6f} m/s")
    print(f"H_c                {critico.H_c:.6f} m")
    print(f"q*                 {entrada.q_estrella:.6f}")
    print(f"regimen entrada    {entrada.regimen.value}")
    print(f"HW entrada         {resultado.HW_entrada:.6f} m")
    print(f"HW salida          {resultado.HW_salida:.6f} m")
    print(f"h_o                {salida.h_o:.6f} m")
    print(f"h_o fuera de rango {resultado.h_o_fuera_de_rango}")
    print(f"gobierna           {resultado.control_gobernante.value}")
    print(f"HW                 {resultado.HW:.6f} m")
    print("</pre>")
    print(M11.bloque_pasos(resultado.pasos, "Traza hidraulica del punto de cajon"))


if __name__ == "__main__":
    main()
