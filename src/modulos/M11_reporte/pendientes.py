# -*- coding: utf-8 -*-
"""
M11_reporte.pendientes
======================
Submodulo de Fase 11 (`M11_reporte`): bloque `pendientes` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    Sequence,
)
from src import criterios_adoptados as ca
from src.modelos import (
    ALCANCE_EXPEDIENTE,
    ALCANCE_PERFIL,
)

from src.modulos.M11_reporte._base import (
    _esc,
    _etiqueta_html,
    _md_inline,
    _valor_legible,
)
from src.modulos.M11_reporte.tableros import (
    CriterioBloqueante,
    Tablero,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.sitio_criterios import (
    _criterio_efectivo,
)

# ===========================================================================
# 4. Bloque aparte de pendientes (Tableros 1, 2 y 3)
# ===========================================================================

def _tabla_tablero(tablero: Tablero) -> str:
    """Un tablero de la hoja de ruta, tal cual lo publica."""
    encabezado = "".join(f"<th>{_md_inline(c)}</th>" for c in tablero.encabezados)
    filas = "".join(
        _fila([_td(_md_inline(celda)) for celda in fila])
        for fila in tablero.filas)
    return (f'<div class="tablero"><h3>Tablero {_esc(tablero.numero)} '
            f"&mdash; {_md_inline(tablero.titulo)}</h3>"
            f'<p class="glosa">{_md_inline(tablero.glosa)}</p>'
            f'<table class="ancha"><thead><tr>{encabezado}</tr></thead>'
            f"<tbody>{filas}</tbody></table></div>")


def bloque_pendientes(tableros: Sequence[Tablero],
                      bloqueantes: Sequence[CriterioBloqueante],
                      contexto: Any,
                      alcance: str = ALCANCE_EXPEDIENTE) -> str:
    """
    Bloque 5 del entregable: los pendientes de los Tableros 1, 2 y 3, mas los
    criterios que esta corrida dejo sin valor. Vacios, declarados, pisados y
    opcionales salen del `ContextoCorrida` (EXT-4).

    Va separado de la declaracion de criterios a proposito (ver el docstring
    del modulo). Se imprime siempre, incluso vacio de bloqueos: que una corrida
    no haya tropezado con un pendiente no significa que el pendiente no exista.

    EL VOLCADO DE LOS TABLEROS DEPENDE DEL ALCANCE, y es lo que cierra
    SIS-B-06. La plantilla de perfil se diseño sin ese volcado --- a nivel de
    perfil los Tableros 1-2-3 no son la lista de trabajo, y en su lugar va el
    bloque de alcance ---, y para conseguirlo simplemente OMITIA el marcador.
    Omitir un marcador no es una decision de contenido: `substitute` no se
    queja de un valor sobrante, de modo que forzar esa plantilla sobre una
    corrida de EXPEDIENTE tiraba 13 647 caracteres --- los criterios
    bloqueantes del expediente entre ellos --- sin decir nada. Y la propia CLI
    invita a esa combinacion: su docstring dice que las dos plantillas
    «comparten el contrato de marcadores» y su help remata con «las dos
    aceptan cualquier corrida».
    Ahora las dos plantillas imprimen el marcador --- el contrato es de verdad
    el que la CLI promete --- y quien decide que va dentro es el ALCANCE DE LA
    CORRIDA, que es de donde tenia que salir la decision desde el principio.
    """
    if alcance == ALCANCE_PERFIL:
        # A nivel de perfil los tableros no se vuelcan, y eso NO cambia:
        # cambia que ahora se dice, en el sitio donde estarian, en vez de
        # desaparecer con el marcador.
        partes = [
            '<div class="nota"><p>Esta es una corrida a <b>nivel de '
            "perfil</b>: el volcado de los Tableros 1, 2 y 3 de la hoja de "
            "ruta no se imprime, porque a este nivel la lista de trabajo es "
            "el bloque de alcance y no los tableros. Los criterios que "
            "<b>esta corrida</b> dejo sin valor si se listan abajo: son los "
            "que detuvieron una etapa de verdad.</p><p>Para el volcado "
            "completo de los tres tableros, correr con "
            "<code>--alcance expediente</code>.</p></div>"]
    else:
        partes = ["".join(_tabla_tablero(t) for t in tableros)]

    partes.append("<h3>Criterios declarados todavia sin valor</h3>")
    sin_valor = contexto.criterios_sin_valor
    if not sin_valor:
        partes.append("<p>Ninguno: todos los criterios de "
                      "<code>criterios_adoptados.py</code> tienen valor.</p>")
    else:
        partes.append(
            "<p>Estos criterios estan declarados pero vacios. Cualquier etapa "
            "que los invoque se detiene: no se sustituyen por un valor por "
            "defecto (Sec. 0.7).</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Concepto</th>", "<th>Que lo resuelve</th>"])]
        for clave in sin_valor:
            c = ca.criterio(clave)
            # `reemplazado_por` es el ensayo o dato que CIERRA el vacio. Sin
            # el, esta columna caia en `fuente`, que en un criterio vacio es
            # el ENUNCIADO del vacio ("Practica corriente; no fijado por el
            # Manual"): la memoria decia que lo que resuelve el hueco es la
            # descripcion del hueco. Ahora se dice que falta declararlo.
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_esc(c.concepto)),
                _td(_esc(c.reemplazado_por) if c.reemplazado_por else
                    '<span class="pendiente">sin declarar que lo resuelve '
                    "&mdash; el criterio no dice que ensayo o dato lo "
                    "cerraria</span>")]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    # DOS BLOQUES Y NO UNO, desde que la GUI permite PISAR un valor de archivo.
    # El parrafo de aqui abajo decia «no estan en criterios_adoptados.py» y «el
    # archivo no los tiene», y de un criterio pisado las dos frases son FALSAS:
    # el archivo SI lo tiene, y dice otra cosa. Un bloque que mezclara los dos
    # casos imprimiria esa mentira sobre la mitad de sus filas, que es
    # exactamente la clase de defecto que la memoria existe para no cometer.
    #
    # La diferencia tampoco es de matiz para quien lee: rellenar un vacio deja
    # el expediente donde estaba --- faltaba un numero y se puso ---, mientras
    # que pisar SUSTITUYE una decision transcrita que sigue en el archivo
    # diciendo otra cosa. Separarlos es lo que distingue tantear de falsear.
    pisados = list(contexto.pisados_en_caliente)
    rellenados = [c for c in contexto.declarados_en_caliente
                  if c not in pisados]

    partes.append("<h3>Criterios declarados solo para esta corrida</h3>")
    if not rellenados and not pisados:
        partes.append("<p>Ninguno: todo valor que entro en el calculo esta "
                      "transcrito en <code>criterios_adoptados.py</code>.</p>")
    if rellenados:
        # Ni vacios ni valores del archivo: la tercera categoria que faltaba.
        # `criterios_sin_valor()` los excluye -- correctamente, porque el
        # calculo tuvo valor con que correr -- y por eso, antes de esta
        # tabla, se caian de la memoria entre las dos sillas.
        partes.append(
            "<p>Estos criterios recibieron valor <b>al lanzar esta corrida</b> "
            "y no estan en <code>criterios_adoptados.py</code>. El calculo los "
            "uso; el archivo que el encabezado identifica por SHA-1, no los "
            "tiene. Mientras sigan asi, la memoria <b>no</b> los sostiene: "
            "para el expediente hay que escribirlos en el archivo con su "
            "justificacion y su fuente.</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Concepto</th>", "<th>Valor declarado</th>",
                        "<th>Que dice el archivo</th>"])]
        for clave in rellenados:
            c = ca.criterio(clave)
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_esc(c.concepto)),
                _td(_valor_legible(contexto.valor_efectivo(clave))),
                _td(_valor_legible(c.valor))]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    if pisados:
        partes.append("<h4>Valores del archivo PISADOS en esta corrida</h4>")
        partes.append(
            '<p class="pendiente">Estos criterios <b>si tienen valor</b> en '
            "<code>criterios_adoptados.py</code>, y esta corrida uso OTRO. El "
            "archivo que el encabezado identifica por SHA-1 sigue diciendo lo "
            "de la ultima columna: los numeros de esta memoria <b>no</b> se "
            "reproducen volviendo a correr el expediente tal como esta "
            "guardado. Es un TANTEO, valido para explorar y <b>no</b> para "
            "entregar: para que el expediente diga lo que esta memoria dice, "
            "el valor tiene que escribirse en el archivo, con su justificacion "
            "y su fuente revisadas.</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Concepto</th>", "<th>Valor usado en esta corrida</th>",
                        "<th>Valor que el archivo declara</th>"])]
        for clave in pisados:
            c = ca.criterio(clave)
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_esc(c.concepto)),
                _td(_valor_legible(contexto.valor_efectivo(clave))),
                _td('<span class="pendiente">'
                    + _valor_legible(c.valor) + "</span>")]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    opcionales = contexto.criterios_opcionales_sin_declarar
    if opcionales:
        # Salieron de la tabla de arriba porque no son vacios: su valor=None
        # no detiene nada, el calculo aplica el valor normativo por defecto.
        # Pero no pueden desaparecer de la memoria por eso: que el
        # refinamiento estuviera disponible y no se adoptara es una decision
        # del proyectista, y es distinto de no haberlo mirado.
        partes.append("<h3>Refinamiento opcional no adoptado</h3>")
        partes.append(
            "<p>Estos criterios estan declarados sin valor a proposito y "
            "<b>no bloquean nada</b>: refinan un valor que la norma ya fija, "
            "de modo que el calculo corre con el valor normativo por defecto. "
            "Nadie tiene obligacion de declararlos.</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Concepto</th>", "<th>Rango en que podria moverse</th>",
                        "<th>Norma que aporta el defecto</th>"])]
        for clave in opcionales:
            c = ca.criterio(clave)
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_esc(c.concepto)),
                _td(_esc(str(c.sensibilidad))),
                _td(_esc(c.fuente))]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    sin_consumidor = ca.criterios_sin_consumidor()
    if sin_consumidor:
        # Un criterio CON valor y sin invocacion no cae en ninguno de los
        # otros bloques (no esta usado, no esta vacio, no es opcional) y
        # desaparecia de la memoria sin dejar rastro. La razon de que nadie lo
        # invoque se escribe UNA vez, en el campo `sin_consumidor` del propio
        # criterio, y se imprime aqui.
        partes.append("<h3>Criterios declarados que ninguna etapa invoca</h3>")
        partes.append(
            "<p>Estan declarados y <b>ningun modulo de produccion los llama</b>. "
            "No es un olvido de cableado: cada uno dice por que, y el motivo "
            "es siempre el mismo tipo de cosa &mdash; su consumidor esta "
            "declarado fuera del alcance de esta corrida. Se imprimen para "
            "que el revisor no tenga que deducir de su ausencia si faltan o "
            "sobran.</p>")
        filas = [_fila(["<th>Criterio</th>", "<th>Etiqueta</th>",
                        "<th>Valor</th>", "<th>Por que nadie lo invoca</th>"])]
        for clave in sin_consumidor:
            c = _criterio_efectivo(clave, contexto)
            filas.append(_fila([
                _td(f"<code>{_esc(clave)}</code>"),
                _td(_etiqueta_html(c.etiqueta)),
                _td(_valor_legible(c.valor)),
                _td(_esc(c.sin_consumidor))]))
        partes.append('<table class="ancha">' + "".join(filas) + "</table>")

    partes.append("<h3>Criterios sin valor que bloquearon una etapa de esta "
                  "corrida</h3>")
    if not bloqueantes:
        partes.append("<p>Ninguno: ningun criterio sin valor se invoco en esta "
                      "corrida. No significa que no queden pendientes, sino "
                      "que los puntos calculados no dependian de ellos.</p>")
    else:
        for c in bloqueantes:
            puntos = ", ".join(c.puntos) if c.puntos else "proyecto (Fase 9)"
            partes.append(
                '<div class="bloqueo"><p>'
                f"{_etiqueta_html(c.etiqueta)} <code>{_esc(c.clave)}</code> "
                f"&mdash; {_esc(c.concepto)}<br>"
                f"<b>Fuente:</b> {_esc(c.fuente)}<br>"
                f"<b>Detuvo:</b> {_esc('; '.join(c.etapas))}<br>"
                f"<b>Puntos afectados:</b> {_esc(puntos)}"
                + (f"<br><b>Lo resuelve:</b> {_esc(c.reemplazado_por)}"
                   if c.reemplazado_por else "")
                # Lo diferido por alcance se dice en la ficha (EXT-G-02): el
                # criterio sigue pendiente, y NO cuenta para el cierre de
                # esta corrida.
                + ("<br><b>Diferido por alcance:</b> no cuenta para el "
                   "cierre de esta corrida; ver el bloque de alcance"
                   if c.diferido else "")
                + "</p></div>")
    return "".join(partes)


# ---------------------------------------------------------------------------
# Acotaciones: adopciones del proyectista sobre vacios normativos verificados
# ---------------------------------------------------------------------------

def acotaciones_declaradas(contexto: Any) -> list:
    """
    Criterios con valor que cubren un vacio normativo REGISTRADO. El valor
    efectivo es el del `ContextoCorrida` (EXT-4).

    Se leen del propio catalogo, no de la plantilla: cualquier adopcion futura
    del mismo caracter entra aqui sola con solo declarar `vacio_verificado`.
    """
    # Valor EFECTIVO: una adopcion sobre un vacio verificado que se declaro
    # en caliente cubre el vacio igual que si estuviera en el archivo, y tiene
    # que aparecer en este bloque -- con su marca de procedencia, que la pone
    # `bloque_acotaciones`. Leyendo `c.valor` se caia del bloque.
    return sorted(
        (k for k, c in ca.CRITERIOS.items()
         if c.vacio_verificado and contexto.valor_efectivo(k) is not None),
        key=lambda k: (ca.CRITERIOS[k].etiqueta, k))


def bloque_acotaciones(contexto: Any,
                       alcance: str = ALCANCE_EXPEDIENTE) -> str:
    """
    Bloque 6: lo que el proyectista adopto donde la norma no dice nada.

    Existe porque la tabla de criterios no basta para estas entradas. Un
    'D_max_catalogo = 2.10 m [A] ASTM A760' se leeria como una cita normativa
    corriente y ocultaria lo unico que el revisor necesita saber: que A760
    tabula hasta 3600 mm y que el tope lo pone el proyecto. Un valor adoptado
    sobre un vacio -- o sobre una disponibilidad -- se defiende con el
    razonamiento entero o no se defiende.

    El ejemplo que este docstring usaba, 'h_relleno_min_concreto_tmc = 0.30 m
    [N->] EG-2013 508.07', ya no existe: el criterio se retiro al cerrarse
    NOR-VAC-01. Servia para lo mismo -- el 508.07 habla de HDPE y no del
    material al que se le aplicaba -- y acabo demostrandolo por la via dura:
    aquel valor no solo se leia mal, ademas era corto.

    Por eso imprime las cinco piezas por separado -- que dice la norma, que NO
    dice, que se adopto, por que es conservador, que queda pendiente -- en vez
    de un parrafo unico donde las tres primeras se confunden.

    El tono cambia con el alcance y no por estilo: en una memoria de PERFIL la
    adopcion es una decision legitima del nivel de detalle que se esta
    entregando; en una de EXPEDIENTE es una brecha, porque el expediente es
    justamente donde esas verificaciones debian resolverse y no lo hicieron.
    """
    claves = acotaciones_declaradas(contexto)
    if not claves:
        return ('<div class="nota"><p>Ninguna: esta corrida no aplico ningun '
                "valor adoptado sobre un vacio normativo. Todo lo que entro "
                "en el calculo tiene norma que lo fija o ensayo que lo "
                "determina.</p></div>")

    de_expediente = alcance == ALCANCE_EXPEDIENTE
    partes = []
    if de_expediente:
        partes.append(
            '<div class="bloqueo"><p><b>BRECHA DE EXPEDIENTE.</b> Las '
            "adopciones de abajo se tomaron para destrabar el nivel de "
            "PERFIL. Esta es una memoria de EXPEDIENTE, que es donde las "
            "verificaciones por material debian resolverse: mientras sigan "
            "abiertas, cada una es una brecha del expediente y no una nota al "
            "pie. Ninguna puede citarse como valor verificado.</p></div>")
    else:
        partes.append(
            '<div class="nota"><p>Adopciones del proyectista sobre vacios '
            "normativos <b>verificados</b>: huecos donde la busqueda se agoto "
            "fuente por fuente y quedo registrada, no huecos que nadie miro. "
            "Son legitimas al nivel de perfil y <b>no sustituyen</b> la "
            "verificacion de expediente que cada una declara.</p></div>")

    for clave in claves:
        c = _criterio_efectivo(clave, contexto)
        marca = (' <b class="pendiente">[declarado para esta corrida, no en '
                 "archivo]</b>" if contexto.declarado_en_caliente(clave) else "")
        partes.append(
            f'<h3><code>{_esc(clave)}</code> = '
            f"{_valor_legible(c.valor)}{marca} &mdash; "
            f"{_etiqueta_html(c.etiqueta)}</h3>")
        partes.append(f"<p><b>Que es:</b> {_esc(c.concepto)}</p>")
        partes.append(
            f'<dl class="acotacion">'
            # El orden importa: primero lo que la norma dice y no dice, que es
            # el argumento; despues la busqueda, que es la prueba de que el
            # vacio es real. Al reves se lee como una excusa buscada a
            # posteriori.
            f"<dt>Que dice la norma, que NO dice, y por que la adopcion "
            f"es conservadora</dt><dd>{_esc(c.justificacion)}</dd>"
            f"<dt>Busqueda que agoto el vacio</dt><dd>{_esc(c.fuente)}</dd>"
            f"<dt>Registro completo de esa busqueda</dt>"
            f"<dd><code>docs/{_esc(c.vacio_verificado)}</code> &mdash; ahi "
            f"esta, fuente por fuente, que se busco y que se encontro</dd>"
            f"<dt>{'BRECHA: lo que el expediente debia resolver' if de_expediente else 'Queda pendiente para el expediente'}</dt>"
            f"<dd>{_esc(c.reemplazado_por)}</dd>"
            f"</dl>")
    return "".join(partes)
