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
CAMINOS DE CODIGO. CUATRO cosas de las de abajo son decisiones que le tocan a
C5 y que aqui se toman SOLO para poder correr:

  * LA FILA DE LA TABLA N 09. Se usa `concreto_afinado` (0.011-0.014). La
    regla vinculante #6 dice que al marco le falta la FILA, no el grupo, y que
    su n sale de un criterio [N->] que hay que redactar. Ese criterio es de
    C5. Aqui no se declara ninguno: se leen dos numeros de una fila
    transcrita para tener un n con que correr.
  * LA CARTA DE HDS-5. Se usa `cajon_concreto_aleta_45_d043` -- Carta 9
    escala 1, Forma 2, la misma que el caso patron CP5D --. Cual carta le toca
    a la embocadura de la Sec. 9.1 es la decision que C5 empareja con
    `embocadura_cajon`.
  * `ke_entrada`. Vale 0.5 y su cita es del bloque «Pipe, Concrete» de la
    Tabla C.2. Para esta embocadura el numero del cajon COINCIDE y la cita no:
    es la regla vinculante #11, y abrirla es de C5. Esta corrida la consume
    tal cual esta, y por eso su control de SALIDA no es defendible como
    diseño. Como oraculo de diff sirve igual: lo que se vigila es que el
    numero no se mueva sin que nadie lo mire.
  * `geometria_control_salida`. LO ENCONTRO LA AUDITORIA DE C4 instrumentando
    `criterios_adoptados.valor`: esta corrida invoca DOS criterios, no uno, y
    este banner solo nombraba el otro. Es un `[C]` de nivel de perfil que
    elige la seccion de referencia del control de salida --"seccion llena"--
    y TODA su justificacion esta escrita sobre un tubo: razona con
    R = D/4 = 0.225 m frente a R = 0.2715 m del tirante normal, que en un
    marco no existen. Esta corrida es lo primero del repositorio que lo aplica
    a una seccion no circular, donde la diferencia entre las dos R no es el
    ~20 % de aquel razonamiento sino el 40 % que §16.8 mide. Elegir la seccion
    de referencia del marco es de C5, igual que `ke_entrada`.

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

from constantes_normativas import HDS5_INLET, MANNING                # noqa: E402
from modelos import (ConstantesHDS5, Material, SeccionRectangular,   # noqa: E402
                     TipoMaterial)
from modulos import M11_reporte as M11                               # noqa: E402
from modulos.M3_hidraulica import resolver_manning                   # noqa: E402
from modulos.M4_control import (control_entrada, control_salida,      # noqa: E402
                                resolver_control, tirante_critico)

# --- el punto, entero y en un solo sitio ------------------------------------
B = 2.00        # m   ancho interior de UNA celda (§4.1 del plan: "marco 2.00 x 1.50 m")
H = 1.50        # m   altura interior
Q = 6.00        # m3/s
S = 0.004       # m/m la misma pendiente que `entradas_ampliadas.json` declara para C-01
L = 20.00       # m   la longitud de CP-8
TW = 0.30       # m   el mismo TW del fixture ampliado
CARTA = "cajon_concreto_aleta_45_d043"
FILA_N = "concreto_afinado"

# Elegido para que el punto caiga donde se quiere mirar, y se dice cual es cada
# cosa: y/H = 0.694 (dentro del 0.75 de V1), regimen SUBCRITICO (y_n = 1.040 m
# frente a y_c = 0.972 m) y q* = 2.957, o sea la rama NO SUMERGIDA -- la unica
# en que la ec. (A.2) se aplica pura, sin interpolar con la (A.3) --. Es
# justamente la rama en que cablear `forma = 1` cambia el numero.

_n_min, _n_max = MANNING[FILA_N]

MARCO = Material(
    tipo=TipoMaterial.CONCRETO_REFORZADO,
    nombre="marco de concreto armado (FIXTURE, no es un material del catalogo)",
    n_min=_n_min,
    n_max=_n_max,
    D_max=H,
    D_max_de_catalogo="fixture: sin catalogo de marcos hasta C5",
    norma_producto="fixture: el marco es VACIADO IN SITU (§14.1), sin norma de producto",
    hds5=ConstantesHDS5.desde_dict(HDS5_INLET[CARTA]),
    fila_manning=FILA_N,
    v_max_tabla10=None,
    v_max_adoptado=None,
    h_relleno_min_eg2013=None,
    espesor_pared=None,
    seccion_eg2013="fixture",
)


def main() -> None:
    seccion = SeccionRectangular(B, H)
    normal = resolver_manning(seccion=seccion, Q=Q, S=S, material=MARCO)
    if normal is None:
        raise SystemExit(
            f"el fixture dejo de transportar su caudal: {seccion.etiqueta()} "
            f"con Q = {Q} m3/s y S = {S} no tiene tirante normal")
    resultado = resolver_control(seccion=seccion, Q=Q, S=S, L=L, TW=TW,
                                 material=MARCO, normal=normal)

    print("<!-- FIXTURE de la linea base: NO es un diseño. Ver el docstring "
          "de tests/linea_base_familia_c/punto_cajon.py -->")
    print(f"<h2>Punto de cajon &mdash; {seccion.etiqueta()}</h2>")
    print("<pre>")
    print(f"seccion            {seccion.etiqueta()}")
    print(f"carta HDS-5        {CARTA}  (Equation Form {MARCO.hds5.forma})")
    print(f"fila Tabla N 09    {FILA_N}  n = {MARCO.n_min} .. {MARCO.n_max}")
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
    entrada = control_entrada(Q, seccion, S, MARCO.hds5, critico)
    salida = control_salida(Q, seccion, S, L, TW,
                            MARCO.n_para_capacidad, critico=critico)
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
