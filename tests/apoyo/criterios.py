"""
tests/apoyo/criterios.py
========================
Dos gestores de contexto para probar el ESTADO de un criterio, y una razon
para que existan.

Por que existe
--------------
Hasta S20 buena parte de los criterios que gobiernan el nivel de PERFIL
estaban vacios en `criterios_adoptados.py`, y una veintena de tests se apoyaba
en ese vacio para comprobar la unica cosa que de verdad querian comprobar: que
la etapa que los consume SE DETIENE y no rellena nada. La comprobacion era
correcta y la premisa era temporal. Al cerrarse el nivel de perfil los
criterios quedaron declarados, y esos tests empezaron a fallar por la razon
equivocada: no porque el bloqueo se hubiera roto, sino porque ya no habia
vacio que probar.

`sin_valor` devuelve el vacio DURANTE el test. Asi el test sigue probando lo
suyo -- que un criterio sin valor detiene el calculo con
`CriterioPendienteError` -- y deja de depender de que el expediente siga
incompleto. La propiedad que fija es permanente; la que fijaba antes caducaba
en cuanto el proyecto avanzara.

Por que NO se usa `quitar_valor_dinamico`
-----------------------------------------
Porque hace otra cosa: retira una declaracion DE LA CORRIDA y deja al
descubierto la del archivo. Cuando el archivo tenia None eso bastaba; ahora
descubre justamente el valor que el test necesita que no este.

Por que `con_valor` sustituye el `Criterio` entero
--------------------------------------------------
`criterios_adoptados.establecer_valor_dinamico` -- la via de la GUI y de la
CLI -- pasa por `_verificar_criterio`, que exige que el valor caiga dentro de
la ventana de sensibilidad declarada. Es una guardia que no se debe ablandar:
un valor fuera de su propia ventana es una contradiccion que la memoria no
puede defender. Pero un CASO PATRON no es este expediente -- es un cruce
sintetico construido para que un error de formula no pueda pasar
desapercibido -- y sus entradas se eligen por poder de discriminacion, no por
plausibilidad de obra. Para esos casos se sustituye el objeto entero, con su
ventana, y se dice en el sitio por que.

Los dos restauran SIEMPRE, tambien si el test falla: un criterio que se queda
alterado contamina las pruebas que corran despues, y ese efecto de orden es
de los que aparecen semanas mas tarde y en otro archivo.
"""

from contextlib import contextmanager
from dataclasses import replace

import criterios_adoptados as ca


@contextmanager
def sin_valor(clave: str):
    """
    Deja `clave` sin valor mientras dure el bloque, por las DOS vias.

    Retira la declaracion de la corrida (la que pone `conftest`, si la hay) y
    ademas vacia la del archivo. Con una sola de las dos no basta: la de la
    corrida tapa a la del archivo, y la del archivo es la que hoy tiene el
    valor.
    """
    original = ca.CRITERIOS[clave]
    dinamico = ca.valores_dinamicos().get(clave, _SIN_DECLARAR)
    ca.quitar_valor_dinamico(clave)
    ca.CRITERIOS[clave] = replace(original, valor=None)
    try:
        yield
    finally:
        ca.CRITERIOS[clave] = original
        if dinamico is not _SIN_DECLARAR:
            ca.establecer_valor_dinamico(clave, dinamico)


@contextmanager
def con_valor(clave: str, valor, *, motivo: str):
    """
    Impone `valor` a `clave` mientras dure el bloque, SIN su ventana.

    `motivo` es obligatorio y no decorativo: esta funcion esquiva la guardia
    de sensibilidad, y quien la use tiene que decir por que el valor cae fuera
    de la ventana del expediente. Si el valor SI cae dentro, no hace falta
    esto: `establecer_valor_dinamico` es la via correcta y la que ejercita la
    guardia de paso.
    """
    if not motivo.strip():
        raise ValueError(
            "con_valor exige `motivo`: esquivar la guardia de sensibilidad "
            "sin decir por que es como no tenerla")
    original = ca.CRITERIOS[clave]
    dinamico = ca.valores_dinamicos().get(clave, _SIN_DECLARAR)
    ca.quitar_valor_dinamico(clave)
    ca.CRITERIOS[clave] = replace(original, valor=valor, sensibilidad=None,
                                  justificacion=motivo)
    try:
        yield valor
    finally:
        ca.CRITERIOS[clave] = original
        if dinamico is not _SIN_DECLARAR:
            ca.establecer_valor_dinamico(clave, dinamico)


# Centinela: `None` es un valor legitimo de un criterio y no puede significar
# "no habia declaracion de corrida".
_SIN_DECLARAR = object()
