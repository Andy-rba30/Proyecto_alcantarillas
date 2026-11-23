# -*- coding: utf-8 -*-
"""
M9_cabezal.armado
=================
Submodulo de Fase 9 (`M9_cabezal`): bloque `armado` (D1).
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from dataclasses import (
    dataclass,
    replace as _reemplazar,
)
from src import criterios_adoptados as ca
from src.constantes_normativas import (
    FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO,
    REGIMEN_CORTANTE_EN_EL_PLANO,
)
from src.dominios import MILIMETROS_POR_METRO
from src.modelos import (
    ArmadoDeSeccion,
    ArmadoDelCabezal,
    CIFRAS_FINA,
    CIFRAS_MAGNITUD,
    CondicionAnalisis,
    CriterioPendienteError,
    DatoInvalidoError,
    ELEMENTO_ALEROS,
    ELEMENTO_PANTALLA,
    ELEMENTO_ZAPATA,
    ELEMENTO_ZAPATA_ALEROS,
    EntornoDelCabezal,
    ErrorProyecto,
    EstadoDeVerificacion,
    FilaDeArmado,
    GeometriaCabezal,
    MINIMOS_MAS_EXIGENTE,
    Magnitud,
    PasoDeMemoria,
    REGIMEN_RESISTENCIA_CEDENTE,
    REGIMEN_RESISTENCIA_K0,
    SECCION_ALERO,
    SECCION_ALERO_MITAD,
    SECCION_PANTALLA,
    SECCION_PUNTA,
    SECCION_TALON,
    SECCION_TALON_ALERO,
    Verificacion,
    paso,
)
from src.tolerancias import (
    FRACCIONES_DE_ESTABILIDAD_DEL_ALERO,
    TOL_UMBRAL_NORMATIVO,
)

from src.modulos.M9_cabezal._criterios import (
    CITAS_DE_ETA,
    CONDICION_RECUBRIMIENTO_ZAPATA,
    CRITERIO_CATALOGO_BARRAS,
    CRITERIO_EXPOSICION_QUIMICA,
    CRITERIO_FACTOR_MURO,
    CRITERIO_PERALTE_ZAPATA_ARMADA,
    CRITERIO_REGIMEN_CORTANTE,
    CRITERIO_REGIMEN_RESISTENCIA,
    ELEMENTOS_ARMADOS,
    FRACCION_ARRANQUE_ALERO,
    FRACCION_MITAD_ALERO,
    SUFIJO_ALERO,
    TIPO_GRAVEDAD,
    TIPO_VOLADIZO,
    _exigir_positivo,
    _finito,
    catalogo_de_barras,
    sufijo_de_la_franja,
)
from src.modulos.M9_cabezal.armado_secciones import (
    CRITERIO_FC_CABEZAL,
    CRITERIO_REGLA_MINIMOS,
    NUMERAL_9_4_ARMADO,
    _aviso_cabezal,
    _procedimiento,
    _regla_de_minimos,
    _verificacion_de_armado,
    acero_de_temperatura_aashto,
    acero_por_flexion,
    cuantia_vertical_ec_11_32,
    diseno_flexion_corte,
    espaciamiento_maximo_del_armado,
    materiales_del_armado,
    minimo_e060_por_cara,
    momento_de_agrietamiento,
    proponer_barra,
    solicitaciones_de_resistencia,
)
from src.modulos.M9_cabezal.durabilidad import (
    _minimo_de_cuantia_aplicable,
    recubrimiento_para_armar,
    requisitos_durabilidad_concreto,
)
from src.modulos.M9_cabezal.estabilidad import _eta_para_la_memoria

def _altura_y_longitud(entorno: EntornoDelCabezal) -> Tuple[float, float]:
    g = entorno.geometria
    hm = g.altura_total
    return hm, (g.longitud if g.longitud else hm)


def altura_del_fuste_del_alero(g: GeometriaCabezal, fraccion: float
                               ) -> float:
    """
    --- VE-7 --- La altura del fuste de la franja del alero a la `fraccion`
    de su longitud, sobre la zapata del alero: H_c - e_z,alero - Δ, con Δ =
    (h0 - H_f)·fraccion. Puede ser <= 0 (la franja no tiene fuste).
    """
    al = g.aleros
    bajada = max(al.altura_inicial - al.altura_final, 0.0) * fraccion
    return g.altura_total - al.espesor_zapata - bajada


def espesor_de_la_base_del_alero_de_gravedad(g: GeometriaCabezal,
                                             H_franja: float) -> float:
    """
    --- VE-7 (abierto (c)) --- El espesor en la base del fuste del alero de
    un cabezal de GRAVEDAD de altura `H_franja`: el del alero en la corona
    mas el ensanche del cabezal por metro de altura,

        e_base = e_alero + (e_base,cab - e_corona,cab)·H_franja / H_cab
    """
    return (g.aleros.espesor + (g.espesor_base_muro - g.espesor_corona)
            * H_franja / g.H)


def entorno_de_la_seccion_del_alero(entorno: EntornoDelCabezal,
                                    fraccion: float) -> EntornoDelCabezal:
    """
    El entorno del FUSTE de la franja del alero a la `fraccion` de su
    longitud (0 en el arranque, 1 en la punta): un muro en voladizo con

      bajada  Δ = (h0 - H_f)·fraccion, lo que la franja esta mas abajo que
              el arranque (el alero baja con el talud, `Aleros`)
      H       H_c - e_zapata del alero - Δ, sobre la zapata del alero
      fuste   el espesor del alero, uniforme
      zapata  la del alero (ancho y espesor de `Aleros`), TODA como talon:
              la franja no tiene punta (desde VE-7 su talon se arma y la
              franja del arranque se verifica como muro, ficha VE7-01) y
              el plano virtual queda en su
              extremo -- del lado de mas empuje con el plano virtual; con la
              cuña sobre la cara del fuste, la de archivo, no cambia nada --
      relleno la corona y el relleno retenido Δ mas abajo; el borde de la
              plataforma, el desplante, el freatico y el agua no se mueven:
              detras de la franja el relleno SUBE hasta la plataforma con el
              talud del terraplen entero (lado seguro: normal al alero sube
              menos, con el seno del angulo del alero con el talud)

    La sobrecarga viva, su orientacion y su distancia al borde son las del
    cabezal (lado seguro: la franja esta mas lejos de la via).
    """
    g = entorno.geometria
    al = g.aleros
    if al is None:
        raise DatoInvalidoError(
            "aleros", valor=None, id_punto=entorno.id_punto,
            motivo="el cabezal no tiene aleros: no hay seccion de alero")
    if not (_finito(fraccion) and 0 <= fraccion <= 1):
        raise DatoInvalidoError(
            "fraccion", valor=fraccion, id_punto=entorno.id_punto,
            motivo="la seccion del alero va de su arranque (0) a su punta "
                   "(1)")
    bajada = max(al.altura_inicial - al.altura_final, 0.0) * fraccion
    H = altura_del_fuste_del_alero(g, fraccion)
    if not H > 0:
        raise DatoInvalidoError(
            "aleros", valor=H, id_punto=entorno.id_punto,
            motivo=f"la franja del alero a {fraccion:g}·L no deja fuste "
                   "sobre su zapata")
    # --- VE-7 (dictamen Fable, abierto (c)) --- con el cabezal de GRAVEDAD
    # la franja es la seccion del cabezal cortada a su altura: corona del
    # espesor del alero, la base con el mismo ensanche por metro de altura
    # que el cabezal, y la punta del cabezal; el talon es lo que queda.
    if g.tipo == TIPO_GRAVEDAD:
        e_base = espesor_de_la_base_del_alero_de_gravedad(g, H)
        punta = g.ancho_punta
    else:
        e_base, punta = al.espesor, 0.0
    talon = al.ancho_zapata - punta - e_base
    if not talon >= 0:
        raise DatoInvalidoError(
            "aleros", valor=al.ancho_zapata, id_punto=entorno.id_punto,
            motivo=f"la zapata del alero ({al.ancho_zapata:.3f} m) no "
                   f"alcanza para su punta ({punta:.3f} m) y su fuste "
                   f"({e_base:.3f} m)")
    # --- VE-7 (dictamen Fable, abierto (b)) --- la longitud de la franja
    # es la del alero CORTO, no la del cabezal: es la L de la Tabla
    # 10.6.3.1.2a-3 que la estabilidad del alero lee
    # (`estabilidad_del_alero` contrasta ademas la zapata corrida).
    longitud = (al.longitud_corto if al.longitud_corto > TOL_UMBRAL_NORMATIVO
                else None)
    seccion = _reemplazar(
        g, H=H, B=al.ancho_zapata, espesor_zapata=al.espesor_zapata,
        espesor_corona=al.espesor, espesor_base_muro=e_base,
        ancho_punta=punta, ancho_talon=talon, longitud=longitud,
        cota_coronacion=g.cota_coronacion - bajada, aleros=None, losa=None,
        dimensiones=())
    return _reemplazar(entorno, geometria=seccion,
                       cota_relleno=entorno.cota_relleno - bajada)


def alero_verificable_como_muro(entorno: EntornoDelCabezal) -> bool:
    """--- VE-7 --- Si el cabezal tiene aleros (de voladizo o de gravedad)."""
    return entorno.geometria.aleros is not None


def fracciones_del_alero(entorno: EntornoDelCabezal
                         ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
    """
    (las fracciones de `FRACCIONES_DE_ESTABILIDAD_DEL_ALERO` cuya franja
    tiene fuste, las que no): una franja sin fuste no es un muro que
    verificar.
    """
    g = entorno.geometria
    con, sin = [], []
    for f in FRACCIONES_DE_ESTABILIDAD_DEL_ALERO:
        (con if altura_del_fuste_del_alero(g, f) > TOL_UMBRAL_NORMATIVO
         else sin).append(f)
    return tuple(con), tuple(sin)


def franja_del_alero(entorno: EntornoDelCabezal, fraccion: float
                     ) -> EntornoDelCabezal:
    """
    --- VE-7 --- La franja del alero a la `fraccion` de su longitud como
    muro: la seccion de `entorno_de_la_seccion_del_alero`, sin el FS
    declarado de E4 y E5 del cabezal (es del cabezal, no del alero).
    """
    if not alero_verificable_como_muro(entorno):
        raise DatoInvalidoError(
            "aleros", valor=None, id_punto=entorno.id_punto,
            motivo="el cabezal no tiene aleros que verificar como muro")
    return _reemplazar(entorno_de_la_seccion_del_alero(entorno, fraccion),
                       estabilidad_global=None)


def franja_del_arranque_del_alero(entorno: EntornoDelCabezal
                                  ) -> EntornoDelCabezal:
    """--- VE-7 --- La franja del arranque (`franja_del_alero` en 0)."""
    return franja_del_alero(entorno, FRACCION_ARRANQUE_ALERO)


@dataclass(frozen=True)
class _EntornoMinimo:
    """Lo unico que `fracciones_del_alero` lee de un entorno: su geometria."""

    geometria: GeometriaCabezal


def clave_del_talon_del_alero(fraccion: float) -> str:
    """--- VE-7 --- La clave de la seccion del talon de la zapata de los
    aleros en la franja a la `fraccion` de su longitud: `talon_alero` en el
    arranque, `talon_alero_25` ... `talon_alero_100` despues."""
    sufijo = sufijo_de_la_franja(fraccion)[len(SUFIJO_ALERO):]
    return SECCION_TALON_ALERO + sufijo.replace(".", "_")


def armar_elemento(entorno: EntornoDelCabezal, elemento: str,
                   solicitaciones: Optional[dict] = None
                   ) -> Tuple[ArmadoDeSeccion, ...]:
    """
    Las secciones criticas armadas de UN elemento de UN cabezal de voladizo
    armado:

      pantalla  su arranque sobre la zapata, con el espesor del arranque; la
                cara en traccion es el trasdos.
      zapata    la punta (traccion abajo) y el talon (traccion arriba), en
                la cara de la pantalla (AASHTO 5.12.8.4); la que no tiene
                vuelo no se arma.
      aleros    (VE-6) por sus PROPIAS secciones: el arranque (tramo de 0
                a L/2) y la mitad de su longitud (tramo de L/2 a L), cada
                una con las solicitaciones del fuste de su franja
                (`entorno_de_la_seccion_del_alero`), con el espesor del
                alero. Sin caida (h0 = H_f), solo el arranque.
      zapata de los aleros
                (VE-7, ficha VE7-01) su talon en la cara del alero, con las
                solicitaciones de la franja del arranque y el procedimiento
                de la zapata del cabezal.

    El servicio la llama una vez por elemento para que lo que un elemento
    no pueda evaluar quede como `Bloqueo` del punto y los otros dos sigan.
    """
    if elemento not in ELEMENTOS_ARMADOS:
        raise DatoInvalidoError("elemento", valor=elemento,
                                motivo="se espera uno de: "
                                       + ", ".join(ELEMENTOS_ARMADOS))
    g = entorno.geometria
    if g.tipo == TIPO_GRAVEDAD:
        raise DatoInvalidoError(
            "tipo", valor=g.tipo, id_punto=entorno.id_punto,
            motivo="el cabezal de gravedad en ciclopeo no se arma: su "
                   "verificacion es `verificar_cabezal_ciclopeo`")
    sol = (solicitaciones_de_resistencia(entorno) if solicitaciones is None
           else solicitaciones)
    hm, lm = _altura_y_longitud(entorno)
    comun = dict(regimen=sol["regimen"], sufijo=entorno.extremo[0],
                 id_punto=entorno.id_punto, hm=hm, lm=lm)
    servicio = sol.get("servicio", {})
    lugar = f"cabezal de {entorno.extremo}"
    piezas = []
    if elemento == ELEMENTO_PANTALLA:
        piezas.append(diseno_flexion_corte(
            solicitaciones=sol["secciones"][SECCION_PANTALLA],
            espesor=g.espesor_base_muro, elemento=ELEMENTO_PANTALLA,
            clave=SECCION_PANTALLA,
            seccion=f"arranque de la pantalla del {lugar}",
            cara="trasdos (contra el relleno), armadura vertical",
            ancho_seccion=min(g.H, lm),
            contraste_e060=sol["e060"].get(SECCION_PANTALLA),
            momento_servicio=servicio.get(SECCION_PANTALLA), **comun))
    elif elemento == ELEMENTO_ZAPATA:
        datos = sol["datos"]
        for clave, vuelo, cara in (
                (SECCION_PUNTA, datos["punta"],
                 "inferior (contra el terreno), armadura transversal"),
                (SECCION_TALON, datos["talon"],
                 "superior (bajo el relleno), armadura transversal")):
            if not vuelo > TOL_UMBRAL_NORMATIVO:
                continue
            if not sol["secciones"][clave]:
                continue
            piezas.append(diseno_flexion_corte(
                solicitaciones=sol["secciones"][clave],
                espesor=g.espesor_zapata, elemento=ELEMENTO_ZAPATA,
                clave=clave,
                seccion=f"{clave} de la zapata del {lugar}, en la cara de "
                        "la pantalla",
                cara=cara, es_zapata=True, vuelo=vuelo, ancho_seccion=g.B,
                contraste_e060=sol["e060"].get(clave),
                momento_servicio=servicio.get(clave), **comun))
    elif elemento == ELEMENTO_ZAPATA_ALEROS:
        # --- VE-7 (ficha VE7-01) --- el TALON de la zapata de los aleros,
        # en la cara del alero, en CADA franja que se verifica como muro
        # (dictamen Fable, abierto (a)), con sus solicitaciones y el
        # procedimiento de la zapata del cabezal: presion de contacto
        # lineal, el metodo del talon de 'momento_talon_cabezal' y las
        # mismas filas. La franja no tiene punta. La tabla adopta la de
        # mayor acero (`ensamblar_armado`).
        # Una franja cuyas solicitaciones no se pueden evaluar (su
        # estabilidad lleva el mismo `Bloqueo`) no detiene las demas; si no
        # se puede evaluar ninguna, se detiene con el primer motivo.
        if g.aleros is None:
            return ()
        fallida = None
        for fraccion in fracciones_del_alero(entorno)[0]:
            franja = franja_del_alero(entorno, fraccion)
            try:
                sol_f = solicitaciones_de_resistencia(franja)
            except ErrorProyecto:
                fallida = fraccion if fallida is None else fallida
                continue
            vuelo = sol_f["datos"]["talon"]
            if not (vuelo > TOL_UMBRAL_NORMATIVO
                    and sol_f["secciones"][SECCION_TALON]):
                continue
            piezas.append(diseno_flexion_corte(
                solicitaciones=sol_f["secciones"][SECCION_TALON],
                espesor=g.aleros.espesor_zapata,
                elemento=ELEMENTO_ZAPATA_ALEROS,
                clave=clave_del_talon_del_alero(fraccion),
                seccion=(f"talon de la zapata de los aleros del {lugar}, en "
                         f"la cara del alero (franja a {fraccion:g}·L)"),
                cara="superior (bajo el relleno), armadura transversal",
                es_zapata=True, vuelo=vuelo, ancho_seccion=franja.geometria.B,
                contraste_e060=sol_f["e060"].get(SECCION_TALON),
                momento_servicio=sol_f.get("servicio", {}).get(SECCION_TALON),
                **comun))
        if not piezas and fallida is not None:
            # ninguna franja evaluable: la primera que fallo se detiene
            # otra vez, con su propio motivo
            solicitaciones_de_resistencia(franja_del_alero(entorno, fallida))
    else:
        if g.aleros is None:
            return ()
        secciones = [(SECCION_ALERO, 0.0,
                      f"arranque de los aleros del {lugar} (su seccion mas "
                      "alta; arma el tramo de 0 a L/2)")]
        if g.aleros.altura_inicial > g.aleros.altura_final \
                + TOL_UMBRAL_NORMATIVO:
            secciones.append((
                SECCION_ALERO_MITAD, FRACCION_MITAD_ALERO,
                f"mitad de la longitud de los aleros del {lugar} (arma el "
                "tramo de L/2 a L)"))
        for clave, fraccion, rotulo in secciones:
            franja = entorno_de_la_seccion_del_alero(entorno, fraccion)
            sol_x = solicitaciones_de_resistencia(franja)
            # --- dictamen Fable de VE-6 --- el ancho de la seccion de la
            # mitad es la altura de SU franja; el del arranque, el de siempre.
            alto = (g.aleros.altura_inicial if clave == SECCION_ALERO
                    else franja.geometria.H)
            piezas.append(diseno_flexion_corte(
                solicitaciones=sol_x["secciones"][SECCION_PANTALLA],
                espesor=g.aleros.espesor, elemento=ELEMENTO_ALEROS,
                clave=clave, seccion=rotulo,
                cara="trasdos (contra el relleno), armadura vertical",
                ancho_seccion=min(alto, max(g.aleros.longitudes)),
                contraste_e060=sol_x["e060"].get(SECCION_PANTALLA),
                momento_servicio=sol_x.get("servicio", {}).get(
                    SECCION_PANTALLA), **comun))
    return tuple(piezas)


def _fila_de_reparto(*, elemento: str, posicion: str, es_zapata: bool,
                     direccion: str, espesor: float, ancho: float,
                     fy: float, regla: str, catalogo: dict,
                     hm: float, lm: float) -> FilaDeArmado:
    """Una fila de acero de REPARTO: solo minimo, por cara."""
    As = acero_de_temperatura_aashto(ancho=max(ancho, espesor),
                                     espesor=espesor, fy=fy)
    origen = "retraccion y temperatura (AASHTO 5.10.6)"
    if regla == MINIMOS_MAS_EXIGENTE:
        As_e, origen_e = minimo_e060_por_cara(
            es_zapata=es_zapata, direccion=direccion, espesor=espesor,
            hm=hm, lm=lm)
        if As_e > As:
            As, origen = As_e, origen_e
    s_max, _ = espaciamiento_maximo_del_armado(espesor=espesor, regla=regla)
    return FilaDeArmado(
        elemento=elemento, posicion=posicion, As_requerido=0.0,
        As_minimo=As, origen_minimo=origen, As_adoptado=As,
        gobierna="minimo constructivo: " + origen, s_max=s_max,
        barra=proponer_barra(As=As, s_max=s_max, catalogo=catalogo,
                             desde=catalogo["reparto"]))


def _fila_de_peralte_de_zapata(entorno: EntornoDelCabezal,
                               piezas: Sequence[ArmadoDeSeccion], *,
                               catalogo: dict, regla: str) -> Verificacion:
    """
    --- correcciones de T-7c (H4) --- La fila A8: la altura de la zapata
    medida sobre su refuerzo inferior frente a los 300 mm de E.060 15.7
    ('peralte_min_zapata_armada_m' [N→]), con el recubrimiento con que SE
    ARMA la cara inferior y la barra de la punta (o la minima principal si
    la punta no se armo). LA LECTURA QUE LA FILA USA es hasta el EJE de la
    capa inferior, que es el peralte efectivo; «medida sobre el refuerzo
    inferior» admite otras dos, y las dos se imprimen: hasta la cara
    INFERIOR de la barra (medio diametro mas: la menos exigente) y hasta
    su cara SUPERIOR (medio diametro menos: la mas exigente, la de «above
    bottom reinforcement»). No se itera: si no cumple, la fila lo dice.
    Decide con la regla del minimo mas exigente
    ('regla_minimos_constructivos_cabezal'); con «solo_aashto» informa,
    porque AASHTO no fija esa altura.

    --- verificacion de T-7 (punto 7) --- EL PISO DE T-7a SE CORRIGIO
    (`peralte_minimo_zapata`): con la zapata de REGLA esta fila cumple por
    construccion, porque el piso suma el mismo recubrimiento y medio
    diametro de la mayor barra del catalogo. Sigue pudiendo FALLAR con una
    zapata declarada mas delgada (`cabezal_declarado`). Y la nota decia que
    bastaba «bajar el recubrimiento con el dato de exposicion»: era falso
    --con la regla anterior, 0.37 m, ni las categorias B o C alcanzaban
    (0.2937 m)--.
    """
    g = entorno.geometria
    ext = entorno.extremo[0]
    punta = next((p for p in piezas if p.clave == SECCION_PUNTA), None)
    rec, origen_rec, _ = recubrimiento_para_armar(
        condicion=CONDICION_RECUBRIMIENTO_ZAPATA)
    if punta is not None and punta.barra is not None:
        diametro, barra = punta.barra.diametro_mm, punta.barra.texto
    else:
        diametro = dict((n, d) for d, _, n in catalogo["barras"])[
            catalogo["minima_principal"]]
        barra = (f"barra minima principal "
                 f"Ø {catalogo['minima_principal']}\" del catalogo")
    minimo = _exigir_positivo(
        CRITERIO_PERALTE_ZAPATA_ARMADA,
        ca.valor(CRITERIO_PERALTE_ZAPATA_ARMADA),
        "altura minima de la zapata armada sobre su refuerzo")
    altura = g.espesor_zapata - (rec + diametro / 2) / MILIMETROS_POR_METRO
    a_la_cara = g.espesor_zapata - rec / MILIMETROS_POR_METRO
    sobre_la_barra = g.espesor_zapata - (rec + diametro) / MILIMETROS_POR_METRO
    mag = lambda s, v, u, p, c=CIFRAS_MAGNITUD: Magnitud(s, v, u, p, cifras=c)  # noqa: E731
    return _verificacion_de_armado(
        fundamento="F9.ARM_PERALTE_ZAPATA", codigo=f"A8.zapata.{ext}",
        que=("A8, altura de la zapata sobre su refuerzo inferior: cabezal "
             f"de {entorno.extremo}"),
        formula="h_z - (recubrimiento inferior + diametro/2) >= 300 mm",
        sustitucion=(
            mag("h_z", g.espesor_zapata, "m", "espesor de la zapata (T-7a)"),
            mag("recubrimiento inferior", rec, "mm", origen_rec, 1),
            mag("diametro", diametro, "mm", barra, 1),
            mag("hasta la cara inferior de la barra", a_la_cara, "m",
                "otra lectura de «medida sobre el refuerzo inferior»: la "
                "menos exigente; no es la que la fila usa"),
            mag("hasta la cara superior de la barra", sobre_la_barra, "m",
                "la lectura mas exigente (el concreto por encima de la "
                "barra); no es la que la fila usa, y la zapata de regla no "
                "la garantiza"),
        ),
        resultado=mag("altura sobre el refuerzo", altura, "m",
                      "hasta el EJE de la capa inferior: la lectura que la "
                      "fila usa, la misma con que se fija el piso del "
                      "espesor de la zapata de regla"),
        descripcion_umbral="altura sobre el refuerzo inferior >= 300 mm",
        admisible=minimo, unidad="m", cita="E060.15.7#PERALTE",
        aplicacion=("minimo constructivo de E.060, por analogia [N→]; "
                    f"decide con '{CRITERIO_REGLA_MINIMOS}' = "
                    f"'{MINIMOS_MAS_EXIGENTE}'"),
        criterio=CRITERIO_PERALTE_ZAPATA_ARMADA,
        cumple=altura >= minimo - TOL_UMBRAL_NORMATIVO,
        margen=altura - minimo, decide=regla == MINIMOS_MAS_EXIGENTE,
        obtenido=altura,
        nota=("El espesor no se itera (la geometria lo propone y el "
              "armado lo arma). La zapata de REGLA cumple por construccion: "
              "su piso es 300 mm + el recubrimiento con que se arma + medio "
              "diametro de la mayor barra del catalogo. Si esta fila no "
              "cumple es porque el espesor se DECLARO por debajo de ese "
              "piso, y el remedio es engrosar la zapata: bajar el "
              "recubrimiento con el dato de exposicion no alcanza por si "
              "solo. La altura se lee hasta el eje de la capa inferior; con "
              "el recubrimiento de cota por falta de dato es la menor "
              "posible."),
        explicacion_falla=("la zapata no da 300 mm sobre su refuerzo "
                           "inferior con el recubrimiento con que se arma: "
                           "engrosarla"))


def _fila_de_durabilidad(entorno: EntornoDelCabezal, *, fc: float,
                         requisitos) -> Verificacion:
    """
    --- correcciones de T-7c (H7) --- La fila A7: el f'c de calculo
    ('fc_cabezal_mpa' [A]) frente al minimo por durabilidad de E.060
    (Tablas 4.2 y 4.4, con su nota al pie), cuando el analisis quimico del
    EMS esta declarado. DECIDE: la durabilidad es la excepcion de la §0.2
    de la hoja de ruta, en que E.060 rige. Sin el dato no hay fila y el
    ensamble lo avisa.
    """
    ext = entorno.extremo[0]
    minimo = requisitos.fc_min_MPa
    mag = lambda s, v, u, p, c=CIFRAS_MAGNITUD: Magnitud(s, v, u, p, cifras=c)  # noqa: E731
    return _verificacion_de_armado(
        fundamento="F9.ARM_DURABILIDAD", codigo=f"A7.concreto.{ext}",
        que=("A7, f'c de calculo frente al minimo por durabilidad: cabezal "
             f"de {entorno.extremo}"),
        formula="f'c >= f'c minimo (E.060 Tablas 4.2 y 4.4: el MAYOR de los "
                "aplicables)",
        sustitucion=(mag("f'c", fc, "MPa", f"'{CRITERIO_FC_CABEZAL}' [A]",
                         1),),
        resultado=mag("f'c", fc, "MPa", "especificado", 1),
        descripcion_umbral="f'c >= f'c minimo por durabilidad",
        admisible=minimo, unidad="MPa", cita="E060.T4.4",
        aplicacion=(f"exigencia de E.060 por la excepcion de durabilidad de "
                    f"la Sec. 0.2; gobierna {requisitos.gobierna_fc}"),
        criterio=CRITERIO_FC_CABEZAL,
        cumple=fc >= minimo - TOL_UMBRAL_NORMATIVO, margen=fc - minimo,
        decide=True, obtenido=fc,
        nota=("El minimo sale del analisis quimico del EMS "
              f"('{CRITERIO_EXPOSICION_QUIMICA}'); el f'c de calculo es un "
              "[A] y hay que subirlo si no llega."),
        explicacion_falla="el f'c de calculo es menor que el minimo por "
                          "durabilidad: subir 'fc_cabezal_mpa'",
        citas=("E060.T4.2", "E060.4.4.2"))


def _fila_de_durabilidad_no_aplica(entorno: EntornoDelCabezal, *, fc: float,
                                   requisitos) -> Verificacion:
    """
    --- T-11 (H10 de su auditoria) --- La fila A7 cuando el analisis quimico
    del EMS esta declarado y E.060 no fija f'c minimo: exposicion a sulfatos
    «insignificante» en la Tabla 4.4 (pag. impresa 38: «0,0 <= SO4 < 0,1» en
    el suelo y «0 <= SO4 < 150» ppm en el agua, sin requisito de f'c) y
    ninguna fila de la Tabla 4.2 aplicable. `EstadoDeVerificacion.NO_APLICA`
    con su razon (el estado que C10 abrio para esto): no juzga, no rellena
    un minimo y no cuenta como incumplida. Con un minimo aplicable la fila
    es `_fila_de_durabilidad`, que decide.
    """
    ext = entorno.extremo[0]
    return Verificacion(
        cumple=True, numeral=NUMERAL_9_4_ARMADO, valor_obtenido=fc,
        valor_admisible=None, criterio_aplicado=CRITERIO_FC_CABEZAL,
        codigo=f"A7.concreto.{ext}", estado=EstadoDeVerificacion.NO_APLICA,
        motivo_no_aplica=(
            f"A7 del cabezal de {entorno.extremo}: con el analisis quimico "
            f"declarado ('{CRITERIO_EXPOSICION_QUIMICA}') la exposicion a "
            f"sulfatos es «{requisitos.clase_sulfatos}» en la Tabla 4.4 de "
            "E.060, que en esa fila no fija f'c minimo, y ninguna fila de la "
            "Tabla 4.2 aplica: E.060 no impone un f'c minimo por "
            "durabilidad y no hay nada que juzgar. Rige el f'c de calculo "
            f"({fc:.1f} MPa, '{CRITERIO_FC_CABEZAL}' [A])"))


def ensamblar_armado(entorno: EntornoDelCabezal,
                     piezas: Sequence[ArmadoDeSeccion],
                     solicitaciones: Optional[dict] = None, *,
                     alero_verificado: bool = False
                     ) -> ArmadoDelCabezal:
    """
    El `ArmadoDelCabezal` de UN cabezal de voladizo armado a partir de sus
    secciones ya diseñadas: el paso del regimen (con que empuje se armo y
    cuanto da el otro), las secciones, la TABLA de armado por elemento -- el
    acero principal de cada seccion y el de reparto de cada elemento, con la
    barra y el espaciamiento propuestos -- y los avisos.

    Avisa, y no solo en una nota de paso: cuando el armado CAMBIA entre el
    empuje en reposo y el activo; cuando falta el Evento Extremo; cuando el
    recubrimiento es la cota por falta de dato; cuando el regimen de
    cortante «en el plano» esta declarado; lo que el armado no cubre; y que
    la geometria se arma tal como llega, pase o no su estabilidad.
    """
    g = entorno.geometria
    piezas = tuple(piezas)
    sol = (solicitaciones_de_resistencia(entorno) if solicitaciones is None
           else solicitaciones)
    mat = materiales_del_armado()
    regla = _regla_de_minimos()
    catalogo = catalogo_de_barras()
    regimen = sol["regimen"]
    quien = _aviso_cabezal(entorno)
    ext = entorno.extremo[0]
    hm, lm = _altura_y_longitud(entorno)
    K0, K_A = sol["K0"], sol["K_A"]
    avisos = list(sol["avisos"])
    for p in piezas:
        avisos.extend(a if a.startswith(quien) else f"{quien}: {a}"
                      for a in p.avisos)

    # --- el paso del regimen y el aviso de lo que cambia --------------------
    pantalla = next((p for p in piezas if p.clave == SECCION_PANTALLA), None)
    referencia = pantalla or (piezas[0] if piezas else None)
    estaticas = [] if referencia is None else [
        s for s in referencia.solicitaciones
        if s.condicion is CondicionAnalisis.ESTATICO]
    pasos: List[PasoDeMemoria] = []
    datos_e = sol.get("datos") or {}
    i_grados = (datos_e.get("angulos") or {}).get("i", 0.0)
    K0_talud = K0 * (1 + math.sin(math.radians(i_grados)))
    k_h_armado = sol.get("k_h_armado")
    k_h_estab = sol.get("k_h_estabilidad")
    if estaticas:
        s0 = max(estaticas, key=lambda s: s.M_u)
        M_rep = s0.M_u_reposo if s0.M_u_reposo is not None else 0.0
        pasos.append(paso(
            "F9.ARM_REGIMEN", codigo=f"9.4.r.{ext}",
            que=f"Empuje con que se arma el cabezal de {entorno.extremo}: "
                f"regimen «{regimen}»",
            formula="reposo: EH = (K0 / K_A)·P_A, horizontal, con gamma = "
                    "1.35; LS = K0·gamma·h_eq·h. Activo: el del ensamble de "
                    "estabilidad, con gamma = 1.50",
            sustitucion=(
                Magnitud("K_A", K_A, "", "del ensamble de estabilidad (cuña "
                         "de tanteo o Coulomb)", cifras=CIFRAS_FINA),
                Magnitud("K0", K0, "", "1 - sen(phi) (AASHTO 3.11.5.2-1, "
                         "terreno horizontal)", cifras=CIFRAS_FINA),
                Magnitud("K0 / K_A", K0 / K_A, "", "cociente con que se "
                         "escala el empuje del suelo", cifras=CIFRAS_FINA),
                Magnitud(f"M_u activo, {referencia.clave}", s0.M_u_cedente,
                         "kN·m/m", f"{s0.combinacion}, del ensamble de "
                         "T-7b", cifras=CIFRAS_MAGNITUD),
                Magnitud(f"M_u reposo, {referencia.clave}", M_rep, "kN·m/m",
                         "las mismas cargas con el empuje en reposo",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("K0·(1 + sen i)", K0_talud, "",
                         f"CONTRASTE de sensibilidad, no adoptado: el K0 "
                         f"con el relleno en talud de la practica "
                         f"geotecnica, con i = {i_grados:.2f} grados (la "
                         "pendiente equivalente del ensamble); AASHTO "
                         "3.11.5.2 da K0 solo con terreno horizontal y no "
                         f"trae esta formula. Seria un {K0_talud / K0 - 1:.0%}"
                         " mas de empuje en reposo", cifras=CIFRAS_FINA),
                Magnitud("k_h del armado", k_h_armado if k_h_armado
                         is not None else 0.0, "",
                         ("1.0·k_h0 (AASHTO 11.6.5.4, muro que no cede)"
                          if regimen == REGIMEN_RESISTENCIA_K0 else
                          "el de la cadena sismica (muro que cede)")
                         if k_h_armado is not None else
                         "el Evento Extremo I no entro al armado",
                         cifras=CIFRAS_FINA),
                Magnitud("k_h de la estabilidad", k_h_estab if k_h_estab
                         is not None else 0.0, "",
                         f"el de la cadena sismica ('{CRITERIO_FACTOR_MURO}'"
                         ")", cifras=CIFRAS_FINA),
            ) + _eta_para_la_memoria(CondicionAnalisis.ESTATICO)[0],
            resultado=Magnitud(f"M_u que rige, {referencia.clave}", s0.M_u,
                               "kN·m/m",
                               "el mayor de los dos" if regimen
                               == REGIMEN_RESISTENCIA_K0 else
                               "el del muro que cede",
                               cifras=CIFRAS_MAGNITUD),
            citas_textuales=("AASHTO_LRFD_9.C3.11.1#REPOSO",
                             "AASHTO_LRFD_9.C11.6.5.4#K0",
                             "AASHTO_LRFD_9.11.6.5.4#NO_CEDENTE",
                             "AASHTO_LRFD_9.C3.11.5.2#ACTIVO") + CITAS_DE_ETA,
            nota_del_proyecto=(
                _eta_para_la_memoria(CondicionAnalisis.ESTATICO)[1] + " El "
                "Evento Extremo I y el Servicio I del armado van con eta = "
                "1.00. " +
                "QUE SE ESCALA Y QUE NO: solo el empuje del suelo (EH) y el "
                "de la sobrecarga viva (LS) cambian de coeficiente; en "
                "reposo el empuje es horizontal y su componente vertical "
                "desaparece. El peso del concreto, el del relleno, el de la "
                "sobrecarga, el agua y la subpresion son los mismos. La "
                "estabilidad externa NO cambia: sigue con el muro que cede. "
                "El K0 es de terreno horizontal y el relleno sube detras "
                "del cabezal: por eso rige la mayor de las dos "
                "solicitaciones y no la de reposo a secas; la sensibilidad "
                "a un K0 con talud se imprime arriba y no se adopta. Bajo "
                "sismo, con el muro que no cede, el armado va con k_h = "
                "1.0·k_h0 (11.6.5.4), y la estabilidad tambien: un solo "
                "regimen, la reduccion de k_h solo con el armado que cede. Es "
                "una eleccion del proyecto "
                f"('{CRITERIO_REGIMEN_RESISTENCIA}' [A]).")))
    for p in piezas:
        otra = _armado_con_el_otro_regimen(p, regimen)
        if otra is not None:
            avisos.append(
                f"{quien}: el armado de {p.clave} CAMBIA con el regimen de "
                f"resistencia ('{CRITERIO_REGIMEN_RESISTENCIA}' [A]): con "
                f"«{regimen}» se adoptan {p.As_adoptado:.0f} mm2/m "
                f"({p.barra.texto if p.barra else 'sin barra del catalogo'}"
                f"); con «{otra[0]}» serian {otra[1]:.0f} mm2/m"
                + (f" ({otra[2].texto})" if otra[2] else ""))
    if not sol["sismico"]:
        pass            # el aviso ya viene en sol["avisos"]
    elif regimen == REGIMEN_RESISTENCIA_K0:
        avisos.append(
            f"{quien}: bajo sismo el armado usa el empuje del metodo del "
            "ensamble (cuña o Mononobe-Okabe) con k_h = 1.0·k_h0 (AASHTO "
            "11.6.5.4) y, en la pantalla y los aleros, la resultante del "
            "empuje total a h/2 si da mas cortante o momento (AASHTO "
            "C11.6.5.4). La fuente no da un coeficiente sismico de reposo y "
            "no se inventa")

    # --- la tabla de armado ---------------------------------------------------
    # --- VE-7 --- de los talones de la zapata de los aleros (uno por
    # franja) la tabla adopta el de MAYOR acero: es una sola zapata.
    talones = [p for p in piezas if p.elemento == ELEMENTO_ZAPATA_ALEROS]
    rige_talon = max(talones, key=lambda p: p.As_adoptado, default=None)
    tabla = [FilaDeArmado(
        elemento=p.elemento,
        posicion=f"{p.clave}: {p.cara}",
        As_requerido=p.As_resistencia,
        As_minimo=max(p.As_minimo_flexion, p.As_minimo_constructivo),
        origen_minimo=p.origen_minimo, As_adoptado=p.As_adoptado,
        gobierna=p.gobierna, s_max=p.s_max, barra=p.barra) for p in piezas
        if p.elemento != ELEMENTO_ZAPATA_ALEROS or p is rige_talon]
    comun = dict(fy=mat["fy"], regla=regla, catalogo=catalogo, hm=hm, lm=lm)
    claves = {p.clave for p in piezas}
    if SECCION_PANTALLA in claves:
        tabla.append(_fila_de_reparto(
            elemento=ELEMENTO_PANTALLA,
            posicion="pantalla: cara expuesta, armadura vertical",
            es_zapata=False, direccion="vertical",
            espesor=g.espesor_base_muro, ancho=min(g.H, lm), **comun))
        tabla.append(_fila_de_reparto(
            elemento=ELEMENTO_PANTALLA,
            posicion="pantalla: armadura horizontal, cada cara",
            es_zapata=False, direccion="horizontal",
            espesor=g.espesor_base_muro, ancho=min(g.H, lm), **comun))
    if claves & {SECCION_PUNTA, SECCION_TALON}:
        tabla.append(_fila_de_reparto(
            elemento=ELEMENTO_ZAPATA,
            posicion="zapata: armadura longitudinal (a lo largo del muro), "
                     "cada cara",
            es_zapata=True, direccion="reparto", espesor=g.espesor_zapata,
            ancho=g.B, **comun))
    if SECCION_ALERO in claves:
        # --- dictamen Fable de VE-6 --- lo que el armado del alero NO es.
        # --- VE-7 (ficha VE7-01) --- desde VE-7 el servicio verifica la
        # franja del arranque como muro (`estabilidad_del_alero`) y lo dice
        # con `alero_verificado`; el aviso queda para cuando no corrio (su
        # etapa se bloqueo, o una puerta de tanteo que no la corre).
        if not alero_verificado:
            avisos.append(
                f"{quien}: el alero esta ARMADO por sus secciones y no "
                "verificado como muro: su estabilidad (E1 a E3 de AASHTO "
                "11.6) no se evaluo en todas sus franjas y las dos "
                "condiciones (ver «Etapas bloqueadas»; ficha VE7-01)")
        tabla.append(_fila_de_reparto(
            elemento=ELEMENTO_ALEROS,
            posicion="aleros: armadura horizontal, cada cara",
            es_zapata=False, direccion="horizontal",
            espesor=g.aleros.espesor,
            ancho=min(g.aleros.altura_inicial, max(g.aleros.longitudes)),
            **comun))
    if rige_talon is not None:
        # --- VE-7 --- el reparto de la zapata de los aleros, como el de la
        # zapata del cabezal: a lo largo del alero, cada cara.
        tabla.append(_fila_de_reparto(
            elemento=ELEMENTO_ZAPATA_ALEROS,
            posicion="zapata de los aleros: armadura longitudinal (a lo "
                     "largo del alero), cada cara",
            es_zapata=True, direccion="reparto",
            espesor=g.aleros.espesor_zapata, ancho=g.aleros.ancho_zapata,
            **comun))
    sin_barra = [f.posicion for f in tabla if f.barra is None]
    if sin_barra:
        avisos.append(
            f"{quien}: ninguna barra del catalogo "
            f"('{CRITERIO_CATALOGO_BARRAS}' [A]) da el acero adoptado con "
            "un espaciamiento admisible en: " + "; ".join(sin_barra))
    de_zapata = [p for p in piezas if p.elemento == ELEMENTO_ZAPATA]
    if de_zapata:
        pasos.append(paso(
            "F9.ARM_ZAPATA", codigo=f"9.4.z.{ext}",
            que="Solicitaciones de la zapata en la cara de la pantalla: "
                f"cabezal de {entorno.extremo}",
            formula="punta: integral de la presion de contacto LINEAL y de "
                    "la subpresion, menos el peso propio. Talon: peso "
                    "entero de lo que tiene encima (relleno, sobrecarga, "
                    "componente vertical del empuje y peso propio)",
            sustitucion=tuple(
                Magnitud(f"M_u, {p.clave}", p.rige_flexion.M_u, "kN·m/m",
                         f"{p.rige_flexion.combinacion}; "
                         f"{p.rige_flexion.nota}", cifras=CIFRAS_MAGNITUD)
                for p in de_zapata) + tuple(
                Magnitud(f"V_u, {p.clave}", p.rige_cortante.V_u, "kN/m",
                         f"{p.rige_cortante.combinacion}",
                         cifras=CIFRAS_MAGNITUD) for p in de_zapata),
            resultado=Magnitud("secciones de la zapata", len(de_zapata), "",
                               "punta y talon, las que tienen vuelo"),
            citas_textuales=("AASHTO_LRFD_9.10.6.5#LINEAL",
                             "AASHTO_LRFD_9.11.6.1.2#TALON",
                             "AASHTO_LRFD_9.5.12.8.4#CARA"),
            nota_del_proyecto=(
                "La presion de contacto del DISEÑO ESTRUCTURAL es lineal "
                "(triangular o trapezoidal), no la uniforme sobre el ancho "
                "efectivo que la capacidad portante usa en E1. El cortante "
                "se toma en la cara de la pantalla tambien en la punta, "
                "donde la fuente permite tomarlo a d_v de ella: lado "
                "seguro. El talon con el metodo mas exacto se imprime en "
                "la procedencia y no rige.")))
    pasos_secciones = [x for p in piezas for x in p.pasos]
    pasos.extend(pasos_secciones)
    if tabla:
        pasos.append(paso(
            "F9.ARM_TABLA", codigo=f"9.4.t.{ext}",
            que=f"Tabla de armado del cabezal de {entorno.extremo}",
            formula="A_s adoptado = max(A_s requerido por resistencia, A_s "
                    "minimo); barra y espaciamiento propuestos del catalogo",
            sustitucion=tuple(
                Magnitud(f.posicion,
                         f"requerido {f.As_requerido:.0f}, minimo "
                         f"{f.As_minimo:.0f}, adoptado {f.As_adoptado:.0f} "
                         f"mm2/m -> " + (f"{f.barra.texto} "
                                         f"({f.barra.As_provisto:.0f} mm2/m)"
                                         if f.barra else
                                         "SIN BARRA DEL CATALOGO"),
                         "", f"gobierna: {f.gobierna}; s maximo "
                         f"{f.s_max:.3f} m") for f in tabla),
            resultado=Magnitud("filas de la tabla", len(tabla), "",
                               "una por posicion (cara y direccion) de cada "
                               "elemento"),
            citas_textuales=("AASHTO_LRFD_9.5.6.3.2.1#MR",
                             "AASHTO_LRFD_9.5.6.3.3#MINIMO",
                             "AASHTO_LRFD_9.5.10.6#TEMPERATURA"),
            nota_del_proyecto=(
                "Las barras y los espaciamientos son una PROPUESTA del "
                f"catalogo '{CRITERIO_CATALOGO_BARRAS}' [A]: lo que el "
                "plano lleve tiene que dar al menos el acero adoptado con "
                "un espaciamiento no mayor que el maximo. El acero de "
                "reparto es el minimo de cada cara: el mas exigente de "
                "AASHTO 5.10.6 y de E.060 "
                f"('{CRITERIO_REGLA_MINIMOS}' [A]).")))

    # --- el regimen de cortante de E.060 y lo que NO esta ---------------------
    if regla == MINIMOS_MAS_EXIGENTE and SECCION_PANTALLA in claves:
        en_el_plano = (ca.valor(CRITERIO_REGIMEN_CORTANTE)
                       == REGIMEN_CORTANTE_EN_EL_PLANO)
        rho_h, numeral_h, _, _ = _minimo_de_cuantia_aplicable(
            direccion="horizontal", cortante_alto=en_el_plano)
        rho_v, _, _, _ = _minimo_de_cuantia_aplicable(
            direccion="vertical", cortante_alto=en_el_plano)
        if en_el_plano:
            rho_v = cuantia_vertical_ec_11_32(hm=hm, lm=lm, rho_h=rho_h)
            avisos.append(
                f"{quien}: el regimen de cortante declarado es «en el "
                f"plano» ('{CRITERIO_REGIMEN_CORTANTE}'): se aplican los "
                f"pisos de E.060 11.10.10 (horizontal {rho_h:g}, vertical "
                f"{rho_v:g} por la ec. 11-32 con hm/lm = {hm / lm:.2f}). El "
                "programa NO modela ninguna carga en el plano del muro: el "
                "umbral de 11.10.7 no se evalua, y la cuantia horizontal "
                "requerida por 11.10.10.1 se toma igual a su piso")
        pasos.append(paso(
            "F9.ARM_CORTANTE_PLANO", codigo=f"9.4.p.{ext}",
            que="Cuantias minimas del muro segun el plano del cortante "
                f"(E.060 11.10, por analogia): cabezal de {entorno.extremo}",
            formula="perpendicular al plano: rho_h >= 0,0020 y rho_v >= "
                    "0,0015 (14.3.1). En el plano: rho_h >= 0,0025 y rho_v "
                    ">= 0,0025 + 0,5·(2,5 - hm/lm)·(rho_h - 0,0025) >= "
                    "0,0025 (ec. 11-32)",
            sustitucion=(
                Magnitud("regimen", ca.valor(CRITERIO_REGIMEN_CORTANTE), "",
                         f"'{CRITERIO_REGIMEN_CORTANTE}' [A]: el cortante "
                         "que el ensamble entrega es el del empuje, "
                         "perpendicular al plano"),
                Magnitud("hm", hm, "m", "altura total del muro",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("lm", lm, "m", "longitud del cabezal",
                         cifras=CIFRAS_MAGNITUD),
                Magnitud("rho_h", rho_h, "", numeral_h, cifras=CIFRAS_FINA),
            ),
            resultado=Magnitud("rho_v", rho_v, "",
                               "ec. (11-32) evaluada" if en_el_plano else
                               "14.3.1 (el regimen de 11.10.10 no rige)",
                               cifras=CIFRAS_FINA),
            citas_textuales=("E060.11.10.1", "E060.11.10.2",
                             "E060.11.10.10.2", "E060.11.10.10.3"),
            nota_del_proyecto=(
                "E.060 es norma de edificaciones y se aplica al cabezal por "
                "analogia: estas cuantias entran como minimo constructivo, "
                "junto al acero de temperatura de AASHTO 5.10.6, y rige el "
                "mayor.")))
    avisos.append(
        f"{quien}: el armado NO cubre el VANO del conducto -- la pantalla "
        f"de {g.longitud or lm:.2f} m es hueco en el ancho del barril, de "
        "modo que la sección llena es la de los machones a cada lado: el "
        "refuerzo de borde alrededor de la abertura (E.060 22.6.6.5 pide dos "
        "barras de 5/8\" en las aberturas de los muros de concreto simple; "
        "para el armado, por analogia) no se dimensiona --; ni la losa de "
        "entrega ni el dentellon, que la geometria del cabezal trae y no se "
        "arman; ni el desarrollo ni los empalmes de las barras (la zapata "
        "de los aleros se arma en el talon de la franja del arranque, "
        "VE-7). Arma la "
        "geometria que recibe sin iterarla: si el cabezal no pasa su "
        "estabilidad (filas E1 a E3), el armado es el de una geometria que "
        "todavia hay que ampliar")
    verificaciones_cabezal = [_fila_de_peralte_de_zapata(
        entorno, piezas, catalogo=catalogo, regla=regla)]
    try:
        requisitos = requisitos_durabilidad_concreto()
    except CriterioPendienteError:
        avisos.append(
            f"{quien}: el f'c de calculo ({mat['fc']:.1f} MPa, "
            f"'{CRITERIO_FC_CABEZAL}' [A]) NO se contrasto con el minimo "
            "por durabilidad de E.060 (Tablas 4.2 y 4.4): falta el analisis "
            f"quimico del EMS ('{CRITERIO_EXPOSICION_QUIMICA}'); con el, la "
            "fila A7 lo decide")
    else:
        if requisitos.fc_min_MPa is not None:
            verificaciones_cabezal.append(_fila_de_durabilidad(
                entorno, fc=mat["fc"], requisitos=requisitos))
        else:
            # --- T-11 (H10 de su auditoria) --- Con el analisis quimico
            # declarado y ningun minimo aplicable, la fila A7 EXISTE y dice
            # que no aplica, con la razon: hasta aqui no aparecia, y la
            # tabla de A1 a A8 no distinguia «evaluada, sin minimo» de «no
            # evaluada». No juzga nada ni rellena un minimo.
            verificaciones_cabezal.append(_fila_de_durabilidad_no_aplica(
                entorno, fc=mat["fc"], requisitos=requisitos))
    verificaciones = (tuple(v for p in piezas for v in p.verificaciones)
                      + tuple(verificaciones_cabezal))
    # Una fila NO_APLICA no tiene paso (PC-27): no hay nada que sustituir.
    pasos.extend(v.paso for v in verificaciones_cabezal if v.paso is not None)
    for v in verificaciones_cabezal:
        if v.estado not in (EstadoDeVerificacion.CUMPLE,
                            EstadoDeVerificacion.NO_APLICA):
            avisos.append(f"{quien}: {v.paso.que} -- "
                          f"{v.paso.veredicto.explicacion}")
    unicos = []
    for a in avisos:
        if a not in unicos:
            unicos.append(a)
    return ArmadoDelCabezal(
        id_punto=entorno.id_punto, extremo=entorno.extremo,
        tipo=g.tipo or TIPO_VOLADIZO, regimen=regimen, fc_mpa=mat["fc"],
        fy_mpa=mat["fy"], secciones=piezas, tabla=tuple(tabla),
        verificaciones=verificaciones, pasos=tuple(pasos),
        avisos=tuple(unicos), sismico=sol["sismico"], K0=K0, K_A=K_A)


def _armado_con_el_otro_regimen(p: ArmadoDeSeccion, regimen: str
                                ) -> Optional[tuple]:
    """
    Si la barra propuesta de la seccion cambia al armarla con el OTRO
    regimen, (nombre del otro regimen, acero adoptado, barra). None si no
    cambia o si no hay con que compararlo.
    """
    otro = (REGIMEN_RESISTENCIA_CEDENTE if regimen == REGIMEN_RESISTENCIA_K0
            else REGIMEN_RESISTENCIA_K0)
    if not any(s.M_u_reposo is not None for s in p.solicitaciones):
        return None
    mat = materiales_del_armado()
    As_otro, M_estatico = [], 0.0
    for s in p.solicitaciones:
        M = s.M_u_cedente if otro == REGIMEN_RESISTENCIA_CEDENTE else max(
            s.M_u_cedente, s.M_u_reposo if s.M_u_reposo is not None
            else s.M_u_cedente)
        M = max(M, 0.0)
        As = acero_por_flexion(M_u=M, d=p.d, fc=mat["fc"], fy=mat["fy"],
                               phi=s.phi_flexion)
        if As is None:
            return None
        As_otro.append(As)
        if s.condicion is CondicionAnalisis.ESTATICO:
            M_estatico = max(M_estatico, M)
    # El minimo de flexion de 5.6.3.3 tambien se mueve con el regimen: sale
    # del menor de 1.33·M_u (de Resistencia I) y M_cr.
    M_minimo = min(FACTOR_MOMENTO_REFUERZO_MINIMO_AASHTO * M_estatico,
                   momento_de_agrietamiento(espesor=p.espesor, fc=mat["fc"],
                                            gamma_3=mat["gamma_3"]))
    As_minf = acero_por_flexion(M_u=M_minimo, d=p.d, fc=mat["fc"],
                                fy=mat["fy"],
                                phi=_procedimiento()["phi_flexion"])
    if As_minf is None or p.barra is None:
        return None
    adoptado = max(max(As_otro), As_minf, p.As_minimo_constructivo)
    barra = proponer_barra(As=adoptado, s_max=p.s_max,
                           catalogo=catalogo_de_barras(),
                           desde=p.barra.designacion if otro
                           == REGIMEN_RESISTENCIA_K0
                           else catalogo_de_barras()["minima_principal"])
    if barra is not None and barra.designacion == p.barra.designacion \
            and abs(barra.espaciamiento - p.barra.espaciamiento) \
            <= TOL_UMBRAL_NORMATIVO:
        return None
    return otro, adoptado, barra
