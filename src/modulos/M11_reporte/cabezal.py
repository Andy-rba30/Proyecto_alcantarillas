# -*- coding: utf-8 -*-
"""
M11_reporte.cabezal
===================
Submodulo de Fase 11 (`M11_reporte`): bloque `cabezal` (D3).
"""

from __future__ import annotations

from typing import (
    Any,
    List,
    Tuple,
)
from src.constantes_normativas import FISURACION_FRACCION_FR
from src.modelos import MURO_ALERO

from src.modulos.M11_reporte._base import (
    FMT_2,
    VACIO,
    _esc,
    _num,
)
from src.modulos.M11_reporte.tablas_diseno import (
    _fila,
    _td,
)
from src.modulos.M11_reporte.trazas import (
    TITULO_TRAZA_VERIFICACIONES,
)
from src.modulos.M11_reporte.pasos import (
    NoAplica,
    bloque_pasos,
    desarrollo_de_verificaciones,
)

TITULO_TRAZA_CABEZAL = ("Desarrollo de la Fase 9 del punto: embocadura, "
                        "geometria de los cabezales y aleros")


def traza_cabezal(informe: Any) -> Tuple[Any, ...]:
    """
    --- T-7a --- Los `PasoDeMemoria` de la Fase 9 del punto (embocadura,
    coronacion, desplante, aleros, losa, longitud entre cabezales), en su
    orden. Los emite `M9.cabezal_del_punto`; aqui solo se enumeran. Los de
    las verificaciones CB1-CB5 no estan aqui: cuelgan de su `Verificacion`
    y salen con el desarrollo de las verificaciones.
    """
    cabezal = getattr(informe, "cabezal", None)
    return () if cabezal is None else tuple(cabezal.pasos)


def _bloque_cabezal(informe: Any) -> str:
    """
    --- T-7a --- La Fase 9 del PUNTO en la memoria (INF-4.2, INF-4.3): la
    embocadura y, cuando la corrida la alcanzo, la tabla de geometria de los
    dos cabezales -- dimension por dimension, con su valor, su ORIGEN
    («propuesta por regla» o «declarada») y la regla --, la longitud entre
    cabezales y el desarrollo de sus pasos. Formato, no calculo: todo viene
    del objeto que M9 emitio.
    """
    partes: List[str] = []
    e = getattr(informe, "embocadura", None)
    c = getattr(informe, "cabezal", None)
    # SIN CABEZAL NO HAY BLOQUE: la embocadura de un punto que no llego a la
    # Fase 9 ya la imprime la proteccion de entrada (paso 6.9) cuando el
    # punto dimensiona, y la llevan la CLI y el JSON siempre. Repetirla en la
    # memoria de cada punto sin dimensionar solo engordaba el expediente
    # (techo de paginas por punto de `test_ext8`).
    if c is None:
        # --- T-10 --- El punto DIMENSIONADO que no llega a la Fase 9 (una
        # corrida de perfil) tiene embocadura resuelta antes de la Fase 4:
        # la CLI y el JSON la publican con su regla y sus criterios, y la
        # memoria solo la nombraba en el paso 6.9. Una linea, no un bloque.
        if e is None or not getattr(informe, "dimensionado", False):
            return ""
        return ("<h4>Fase 9 &mdash; Embocadura del punto</h4>"
                + _linea_embocadura(informe, e, con_coherencia=True))
    if e is not None:
        partes.append(_linea_embocadura(informe, e))
        # La coherencia del marco con el cabezal va en el paso 9.0.0, que la
        # emite M9: no es una nota aparte ni un aviso (correcciones de T-7a).
    for g in c.geometrias:
        filas = [_fila(["<th>Dimension</th>", "<th>Valor</th>",
                        "<th>Origen</th>", "<th>Regla</th>"])]
        for d in g.dimensiones:
            filas.append(_fila([
                _td(_esc(d.nombre)),
                _td(f"{_num(d.valor)} {_esc(d.unidad)}", "num"),
                _td(_esc(d.origen)),
                _td(_esc(d.regla) + (f" (<code>{_esc(d.criterio)}</code>)"
                                     if d.criterio else ""))]))
        partes.append(
            f"<p><b>Cabezal de {_esc(g.extremo)}:</b> {_esc(g.tipo)}; "
            f"coronacion {_num(g.cota_coronacion)} msnm, desplante "
            f"{_num(g.cota_desplante)} msnm.</p>"
            '<table class="compacta">' + "".join(filas) + "</table>")
    if c.longitud_entre_cabezales is not None:
        partes.append(
            f"<p>Longitud entre cabezales "
            f"{_num(c.longitud_entre_cabezales, FMT_2)} m entre las caras "
            "interiores de los muros, y "
            f"{_num(c.longitud_metrado, FMT_2)} m de metrado del barril "
            "(paso 9.0.5): el diseño hidraulico sigue con la longitud "
            "aproximada de 7.B.</p>")
    else:
        partes.append(
            '<div class="nota"><p>Longitud entre cabezales: no se calcula ('
            + _esc(c.motivo_sin_longitud) + ").</p></div>")
    # --- T-7b --- La estabilidad de cada cabezal: la tabla de cargas SIN
    # FACTORAR con sus brazos y la de combinaciones de los dos marcos. Solo
    # formato: cargas, brazos, momentos y resultantes vienen del objeto que
    # M9 emitio (`EstabilidadDelCabezal`). Las seis filas E1 a E3 de cada
    # condicion estan en la tabla de verificaciones del punto y su
    # desarrollo en los pasos de abajo.
    # --- VE-7 (ficha VE7-01) --- y la de los aleros como muro (la franja
    # del arranque), con la misma tabla y su propio rotulo.
    for est in (tuple(getattr(c, "estabilidad", ()))
                + tuple(getattr(c, "estabilidad_aleros", ()))):
        filas = [_fila(["<th>Carga</th>", "<th>Que es</th>",
                        "<th>V (kN/m)</th>", "<th>x (m)</th>",
                        "<th>H (kN/m)</th>", "<th>z (m)</th>",
                        "<th>M respecto de la punta (kN&middot;m/m)</th>"])]
        for q in est.cargas:
            filas.append(_fila([
                _td(f"<code>{_esc(q.codigo)}</code>"), _td(_esc(q.descripcion)),
                _td(_num(q.V, FMT_2), "num"), _td(_num(q.x, FMT_2), "num"),
                _td(_num(q.H, FMT_2), "num"), _td(_num(q.z, FMT_2), "num"),
                _td(_num(q.momento, FMT_2), "num")]))
        combos = [_fila(["<th>Marco</th>", "<th>Combinacion</th>",
                         "<th>Para</th>", "<th>N (kN/m)</th>",
                         "<th>H (kN/m)</th>",
                         "<th>M estabilizante</th>", "<th>M volcante</th>",
                         "<th>e (m)</th>"])]
        for k in est.combinaciones:
            # --- T-10 --- la excentricidad de la resultante, que el JSON ya
            # publicaba: la calcula y la publica (o no, sin carga vertical)
            # `CombinacionDeEstabilidad.excentricidad_publicable`, no esta capa.
            combos.append(_fila([
                _td(_esc(k.marco)), _td(_esc(k.nombre)), _td(_esc(k.para)),
                _td(_num(k.N, FMT_2), "num"), _td(_num(k.H, FMT_2), "num"),
                _td(_num(k.M_estabilizante, FMT_2), "num"),
                _td(_num(k.M_volcante, FMT_2), "num"),
                _td(_num(k.excentricidad_publicable), "num")]))
        partes.append(
            f"<p><b>Estabilidad del "
            + ("alero del " if getattr(est, "muro", "") == MURO_ALERO else "")
            + f"cabezal de {_esc(est.extremo)}"
            + (f" (franja a {getattr(est, 'fraccion_alero', 0) or 0:g}·L, "
               "como muro)"
               if getattr(est, "muro", "") == MURO_ALERO else "") + ", "
            f"condicion {_esc(est.condicion.value)}</b> (regla de marco "
            f"<code>{_esc(est.regla_de_marco)}</code> [A]; empuje: "
            f"{_esc(getattr(est, 'metodo_empuje', ''))}; regimen "
            f"<code>{_esc(getattr(est, 'regimen', ''))}</code> [A]). Cargas sin "
            "factorar, por metro de muro; x desde la arista de la punta y z "
            "desde la base de la zapata; momento positivo si estabiliza.</p>"
            '<table class="compacta">' + "".join(filas) + "</table>"
            '<table class="compacta">' + "".join(combos) + "</table>"
            + _tabla_solicitaciones(est))
        if est.pendientes and est.condicion.value == "estatico":
            partes.append(
                '<div class="nota"><p><b>Sin evaluar:</b> '
                + " ".join(f"{_esc(cod)}: {_esc(motivo)}."
                           for cod, motivo in est.pendientes)
                + "</p></div>")
    # (Correcciones de T-7b, H8.) Un cabezal con SOLO UNA condicion
    # evaluada no se lee como completo: el aviso que M9 emite
    # (`integrar_estabilidad`) se imprime tambien aqui, junto a su tabla.
    for aviso in (a for a in getattr(c, "avisos", ())
                  if "se evaluo SOLO en la condicion" in a):
        partes.append('<div class="nota aviso"><p><b>Incompleta:</b> '
                      + _esc(aviso) + "</p></div>")
    if getattr(c, "estabilidad", ()):
        partes.append(
            '<div class="nota"><p>Las verificaciones E1 a E3 de cada '
            "condicion estan en la tabla de verificaciones del punto, una "
            "fila por marco: las del marco que rige deciden y las del otro "
            "informan. Los dos marcos no se cruzan: el LRFD compara cargas "
            "factoradas con resistencias minoradas y el ASD cargas de "
            "servicio con factores de seguridad. El armado no se verifica "
            "en este bloque.</p></div>")
    else:
        partes.append(
            '<div class="nota"><p>La estabilidad del cabezal (E1 a E3) NO '
            "se evaluo en esta corrida: el motivo esta en los bloqueos del "
            "punto. La geometria es un predimensionamiento, y las "
            "verificaciones CB de la tabla del punto solo comprueban que "
            "remate al conducto y que lo declarado no quede bajo los minimos "
            "con numero. El armado no se verifica en este bloque.</p></div>")
    for armado in getattr(c, "armado", ()):
        partes.append(_bloque_armado(armado))
    return ("<h4>Fase 9 &mdash; Cabezal y aleros del punto</h4>"
            + "".join(partes) + _traza_cabezal_sin_repetir(informe))


def _linea_embocadura(informe: Any, e: Any, *,
                      con_coherencia: bool = False) -> str:
    """
    La embocadura del punto en una linea, con su regla y sus criterios. La
    coherencia del marco con el cabezal la lleva el paso 9.0.0 cuando hay
    cabezal (correcciones de T-7a); sin cabezal (perfil) va en la linea.
    """
    angulo = ("sin aleros" if e.angulo_aletas is None else
              f"aleros a {_num(e.angulo_aletas, FMT_2)} grados con la "
              "pared del barril")
    coherencia = (getattr(informe, "coherencia_embocadura", None)
                  if con_coherencia else None)
    return (f"<p><b>Embocadura del punto:</b> {_esc(e.tipo)} ({angulo}; "
            f"{_esc(e.regla)}), criterios <code>{_esc(e.criterio_tipo)}</code>"
            + (f" y <code>{_esc(e.criterio_angulo)}</code>"
               if e.criterio_angulo else "") + " [A]."
            + (f" {_esc(coherencia)}." if coherencia else "") + "</p>")


def _tabla_solicitaciones(est: Any) -> str:
    """
    --- T-10 --- Las solicitaciones FACTORADAS por elemento del ensamble de
    estabilidad (`EstabilidadDelCabezal.solicitaciones`, marco LRFD): las
    que el JSON publicaba y la memoria no. Son las que recibe el armado de
    T-7c; aqui solo se ponen en tabla, con el coeficiente de empuje con que
    salieron y la nota de M9.
    """
    if not getattr(est, "solicitaciones", ()):
        return ""
    filas = [_fila(["<th>Elemento</th>", "<th>Seccion</th>",
                    "<th>Combinacion</th>", "<th>V_u (kN/m)</th>",
                    "<th>M_u (kN&middot;m/m)</th>", "<th>Empuje</th>",
                    "<th>Nota</th>"])]
    for sol in est.solicitaciones:
        empuje = (f"{_esc(sol.coeficiente_de_empuje)} = "
                  f"{_num(sol.K_empuje)}" if sol.K_empuje is not None
                  else _esc(sol.coeficiente_de_empuje))
        filas.append(_fila([
            _td(_esc(sol.elemento)), _td(_esc(sol.seccion)),
            _td(_esc(sol.combinacion)), _td(_num(sol.V_u, FMT_2), "num"),
            _td(_num(sol.M_u, FMT_2), "num"), _td(empuje),
            _td(_esc(sol.nota))]))
    return ("<p>Solicitaciones factoradas por elemento (marco LRFD), por "
            "metro de muro: las que recibe el armado.</p>"
            '<table class="compacta">' + "".join(filas) + "</table>")


TITULO_ARMADO = "Armado del cabezal de {extremo} ({tipo})"


def _bloque_armado(a: Any) -> str:
    """
    --- T-10 --- El armado de UN cabezal maquetado como TABLA (hasta T-10
    salia solo como pasos: INFORME_T-7c §9). Dos tablas, las dos con los
    numeros que M9 emitio en `ArmadoDelCabezal`: la de secciones criticas
    (la solicitacion que rige, los tres aceros, el adoptado, la barra, la
    resistencia, la fisuracion de 5.6.7 y el contraste de E.060, que
    informa) y la tabla de armado por elemento y posicion (T-7c punto 4).
    Las verificaciones A1 a A8 / C1 a C8 estan en la tabla del punto y su
    desarrollo en sus pasos.
    """
    partes = [f"<p><b>{_esc(TITULO_ARMADO.format(extremo=a.extremo, tipo=a.tipo))}"
              f"</b>: regimen <code>{_esc(a.regimen)}</code> [A]; f'c "
              f"{_num(a.fc_mpa, FMT_2)} MPa; f_y {_num(a.fy_mpa, FMT_2)} MPa; "
              "Evento Extremo I "
              + ("evaluado" if a.sismico else "NO evaluado (ver avisos)")
              + ".</p>"]
    if a.secciones:
        filas = [_fila(["<th>Seccion</th>", "<th>Cara</th>",
                        "<th>Espesor / d (m)</th>",
                        "<th>Recubrimiento (mm)</th>",
                        "<th>Rige la flexion</th>",
                        "<th>M_u (kN&middot;m/m) [cede / reposo]; V_u "
                        "(kN/m) [cede]</th>",
                        "<th>As resist. / min. flex. / min. constr. "
                        "(mm&sup2;/m)</th>",
                        "<th>As adoptado (mm&sup2;/m), gobierna</th>",
                        "<th>Barra, s_max</th>",
                        "<th>M_r, V_r (kN&middot;m/m, kN/m)</th>",
                        "<th>5.6.7: f_ss (MPa), s clase 1 / 2 (m)</th>",
                        "<th>E.060 (contraste): M_u, V_u, As</th>"])]
        for sec in a.secciones:
            rf = sec.rige_flexion
            fis = sec.s_fisuracion or {}
            filas.append(_fila([
                _td(f"{_esc(sec.elemento)}: {_esc(sec.seccion)}"),
                _td(_esc(sec.cara)),
                _td(f"{_num(sec.espesor)} / {_num(sec.d)}", "num"),
                _td(f"{_num(sec.recubrimiento_mm, FMT_2)}<br>"
                    f"<small>{_esc(sec.origen_recubrimiento)}</small>"),
                _td(_esc(rf.combinacion)),
                _td(f"{_num(rf.M_u, FMT_2)} [{_num(rf.M_u_cedente, FMT_2)} / "
                    f"{_num(rf.M_u_reposo, FMT_2)}]<br><small>V_u "
                    f"{_num(sec.rige_cortante.V_u, FMT_2)} ["
                    f"{_num(sec.rige_cortante.V_u_cedente, FMT_2)}] "
                    f"({_esc(sec.rige_cortante.combinacion)})</small>",
                    "num"),
                _td(f"{_num(sec.As_resistencia, FMT_2)} / "
                    f"{_num(sec.As_minimo_flexion, FMT_2)} / "
                    f"{_num(sec.As_minimo_constructivo, FMT_2)}", "num"),
                _td(f"{_num(sec.As_adoptado, FMT_2)}, {_esc(sec.gobierna)}"),
                _td((_esc(sec.barra.texto) if sec.barra is not None
                     else "sin barra del catalogo")
                    + f"; s_max {_num(sec.s_max)} m "
                    f"<small>({_esc(sec.origen_s_max)})</small>"),
                _td(f"{_num(sec.M_r, FMT_2)}, {_num(sec.V_r, FMT_2)}", "num"),
                _td((f"{_num(sec.f_ss, FMT_2)}; "
                     f"{_num(fis.get('clase_1'))} / {_num(fis.get('clase_2'))}")
                    if sec.fisuracion_aplica else
                    (f"no aplica (traccion bajo "
                     f"{_num(FISURACION_FRACCION_FR, FMT_2)}&middot;f_r; f_ss "
                     f"{_num(sec.f_ss, FMT_2)})"
                     if sec.fisuracion_aplica is False else VACIO)),
                _td(f"{_num(sec.M_u_e060, FMT_2)}, {_num(sec.V_u_e060, FMT_2)}, "
                    f"{_num(sec.As_e060, FMT_2)}", "num")]))
        partes.append('<table class="compacta">' + "".join(filas) + "</table>")
    if a.tabla:
        filas = [_fila(["<th>Elemento</th>", "<th>Posicion</th>",
                        "<th>As requerido</th>", "<th>As minimo</th>",
                        "<th>As adoptado</th>", "<th>Gobierna</th>",
                        "<th>Barra (&Oslash; mm)</th>",
                        "<th>As provisto</th>", "<th>s_max (m)</th>"])]
        for f in a.tabla:
            barra = (f"{_esc(f.barra.texto)} ({_num(f.barra.diametro_mm, FMT_2)})"
                     if f.barra is not None else "sin barra del catalogo")
            filas.append(_fila([
                _td(_esc(f.elemento)), _td(_esc(f.posicion)),
                _td(_num(f.As_requerido, FMT_2), "num"),
                _td(f"{_num(f.As_minimo, FMT_2)} "
                    f"<small>({_esc(f.origen_minimo)})</small>", "num"),
                _td(_num(f.As_adoptado, FMT_2), "num"),
                _td(_esc(f.gobierna)), _td(barra),
                _td(_num(f.barra.As_provisto if f.barra is not None else None,
                         FMT_2), "num"),
                _td(_num(f.s_max), "num")]))
        partes.append("<p>Tabla de armado por elemento y posicion "
                      "(mm&sup2;/m; T-7c punto 4):</p>"
                      '<table class="compacta">' + "".join(filas) + "</table>")
    return "".join(partes)


def _traza_cabezal_sin_repetir(informe: Any) -> str:
    """
    --- T-10 --- El desarrollo de la Fase 9 SIN los pasos que ya salieron en
    «Desarrollo de cada verificacion»: los de las verificaciones del armado
    (A1 a A8, C1 a C8) cuelgan a la vez de su `Verificacion` y de
    `ArmadoDelCabezal.pasos`, y hasta T-10 la memoria los imprimia DOS veces
    (medido en A-01 a expediente: 50 pasos, 161 KB). Se excluyen por
    IDENTIDAD del objeto --- el mismo `PasoDeMemoria`, no uno parecido ---,
    como el paso 2.1 en EXT-8, y la remision dice donde estan.
    """
    ya_impresos = {id(paso) for _codigo, paso
                   in desarrollo_de_verificaciones(informe)
                   if paso is not None and not isinstance(paso, NoAplica)}
    pasos = traza_cabezal(informe)
    restantes = tuple(p for p in pasos if id(p) not in ya_impresos)
    remitidos = [p.codigo for p in pasos if id(p) in ya_impresos]
    remision = ""
    if remitidos:
        remision = ('<div class="nota"><p>Los pasos de '
                    + ", ".join(f"<code>{_esc(c)}</code>" for c in remitidos)
                    + f" se desarrollan una sola vez, en «"
                    f"{_esc(TITULO_TRAZA_VERIFICACIONES)}» de este punto: son "
                    "los de las verificaciones del armado.</p></div>")
    return bloque_pasos(restantes, TITULO_TRAZA_CABEZAL) + remision
