"""
El registro: la vista unica sobre fuentes, citas, tablas y discrepancias.

Es lo que consumen `constantes_normativas.py`, la guardia de
`tests/test_normativa_*.py` y el generador del manifiesto. Nadie mas conoce
la estructura interna de los modulos de datos.

REGLA DE DEPENDENCIAS (§3 del diseño), que hay que respetar para no crear un
ciclo:

    normativa/  <-  constantes_normativas.py  <-  criterios_adoptados.py
                                              <-  modulos M0..M11

Nadie de la izquierda importa nada de la derecha. De ahi la consecuencia que
gobierna todo el esquema: el registro conoce la CLAVE del criterio que
resuelve una condicion, nunca el objeto `Criterio`. La resolucion es tardia y
la hace el consumidor.
"""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional, Tuple

from .esquema import (
    Cita,
    CondicionAplicacion,
    CorrespondenciaDeTablas,
    Discrepancia,
    EstadoDiscrepancia,
    Fuente,
    Fundamento,
    Modificador,
    PendienteDeCondicion,
    TablaNormativa,
    Usada,
    esta_por_transcribir,
)


class Registro:
    """
    Indice de todo lo declarado. Se construye una vez al importar
    `src.normativa` y no se muta despues: un registro que cambia en caliente
    no se puede firmar.
    """

    def __init__(self,
                 fuentes: Dict[str, Fuente],
                 fuentes_ausentes: Dict[str, Fuente],
                 catalogos: Dict[str, object],
                 citas: Dict[str, Cita],
                 tablas: Dict[str, TablaNormativa],
                 discrepancias: Dict[str, Discrepancia],
                 correspondencias: Dict[str, CorrespondenciaDeTablas],
                 fundamentos: Dict[str, Fundamento]):
        self._fuentes = dict(fuentes)
        self._ausentes = dict(fuentes_ausentes)
        self._catalogos = dict(catalogos)
        self._citas = dict(citas)
        self._tablas = dict(tablas)
        self._discrepancias = dict(discrepancias)
        self._correspondencias = dict(correspondencias)
        self._fundamentos = dict(fundamentos)

    # -- acceso -------------------------------------------------------------
    def fuente(self, id_: str) -> Fuente:
        if id_ in self._fuentes:
            return self._fuentes[id_]
        if id_ in self._ausentes:
            return self._ausentes[id_]
        if id_ in self._catalogos:
            raise KeyError(
                f"«{id_}» es un Catalogo, no una Fuente: un tope de catalogo "
                "no tiene numeral y no puede sostener una cita (T1)")
        raise KeyError(f"no hay fuente «{id_}»")

    def cita(self, id_: str) -> Cita:
        try:
            return self._citas[id_]
        except KeyError:
            raise KeyError(f"no hay cita «{id_}» en el registro") from None

    def tabla(self, id_: str) -> TablaNormativa:
        try:
            return self._tablas[id_]
        except KeyError:
            raise KeyError(f"no hay tabla «{id_}» en el registro") from None

    def discrepancia(self, id_: str) -> Discrepancia:
        return self._discrepancias[id_]

    def correspondencia(self, id_: str) -> CorrespondenciaDeTablas:
        return self._correspondencias[id_]

    # -- colecciones --------------------------------------------------------
    @property
    def fuentes(self) -> Tuple[Fuente, ...]:
        return tuple(self._fuentes.values())

    @property
    def fuentes_ausentes(self) -> Tuple[Fuente, ...]:
        return tuple(self._ausentes.values())

    @property
    def catalogos(self) -> Tuple[object, ...]:
        return tuple(self._catalogos.values())

    @property
    def citas(self) -> Tuple[Cita, ...]:
        return tuple(self._citas.values())

    @property
    def tablas(self) -> Tuple[TablaNormativa, ...]:
        return tuple(self._tablas.values())

    @property
    def discrepancias(self) -> Tuple[Discrepancia, ...]:
        return tuple(self._discrepancias.values())

    @property
    def correspondencias(self) -> Tuple[CorrespondenciaDeTablas, ...]:
        return tuple(self._correspondencias.values())

    @property
    def fundamentos(self) -> Tuple[Fundamento, ...]:
        return tuple(self._fundamentos.values())

    def ids_de_fuente(self) -> Tuple[str, ...]:
        return tuple(self._fuentes) + tuple(self._ausentes)

    # -- vistas que la guardia y la ventana necesitan ------------------------
    def citas_de(self, fuente_id: str) -> Tuple[Cita, ...]:
        return tuple(c for c in self._citas.values() if c.fuente_id == fuente_id)

    def citas_sin_verificar(self) -> Tuple[Cita, ...]:
        return tuple(c for c in self._citas.values() if c.verificado is None)

    def citas_con_pendientes(self) -> Tuple[Cita, ...]:
        return tuple(c for c in self._citas.values() if c.tiene_pendientes)

    def cuenta_por_transcribir(self) -> int:
        """
        El trinquete de T22: este numero solo puede DECRECER. La migracion a
        medias es un estado legitimo; la migracion a medias invisible, no.
        """
        return sum(len(c.campos_pendientes) for c in self._citas.values())

    def discrepancias_abiertas(self) -> Tuple[Discrepancia, ...]:
        """
        Las que `CLAUDE.md` obliga a seguir declarando mientras nadie corrija
        la hoja de ruta. M11 las imprime; el test T20 comprueba que estan.
        """
        return tuple(d for d in self._discrepancias.values()
                     if d.estado in (EstadoDiscrepancia.ABIERTA_CONTRA_HOJA_DE_RUTA,
                                     EstadoDiscrepancia.ABIERTA))

    def condiciones(self) -> Iterator[Tuple[str, CondicionAplicacion]]:
        for c in self._citas.values():
            for cond in c.condiciones:
                yield (f"cita:{c.id}", cond)
        for t in self._tablas.values():
            for fila in t.filas:
                for cond in fila.condiciones:
                    yield (f"tabla:{t.id}#{fila.id}", cond)
            for m in t.modificadores:
                for tramo in m.tramos:
                    yield (f"modificador:{m.id}", tramo.condicion)

    def condicion(self, id_: str) -> Optional[CondicionAplicacion]:
        for _, cond in self.condiciones():
            if cond.id == id_:
                return cond
        return None

    def modificadores(self) -> Tuple[Modificador, ...]:
        return tuple(m for t in self._tablas.values() for m in t.modificadores)

    def elecciones_pendientes(self) -> Tuple[Tuple[str, str], ...]:
        """
        Las columnas y filas que la ventana pinta como «eleccion pendiente» y
        que detienen el calculo (D4). No es lo mismo que `NoUsada`: alli la
        decision esta tomada, aqui falta un dato.
        """
        salida: List[Tuple[str, str]] = []
        for t in self._tablas.values():
            for c in t.columnas:
                if isinstance(c.uso, PendienteDeCondicion):
                    salida.append((f"{t.id}:columna:{c.id}", c.uso.condicion_id))
            for f in t.filas:
                if isinstance(f.uso, PendienteDeCondicion):
                    salida.append((f"{t.id}:fila:{f.id}", f.uso.condicion_id))
        return tuple(salida)

    def consumidores_declarados(self) -> Tuple[str, ...]:
        vistos = set()
        for t in self._tablas.values():
            for elemento in (*t.columnas, *t.filas):
                if isinstance(elemento.uso, Usada):
                    vistos.update(elemento.uso.por)
        return tuple(sorted(vistos))

    # -- integridad referencial (T4) ----------------------------------------
    def problemas_de_integridad(self) -> Tuple[str, ...]:
        """
        Todo id referenciado existe. Es la version moderna de la referencia
        `archivo:linea` rota: un id que apunta a nada.
        """
        fallos: List[str] = []
        ids_cita = set(self._citas)
        ids_tabla = set(self._tablas)
        ids_fuente = set(self._fuentes) | set(self._ausentes)
        ids_catalogo = set(self._catalogos)
        ids_condicion = {cond.id for _, cond in self.condiciones()}

        for c in self._citas.values():
            if c.fuente_id in ids_catalogo:
                fallos.append(
                    f"cita {c.id}: su fuente «{c.fuente_id}» es un Catalogo (T1)")
            elif c.fuente_id not in ids_fuente:
                fallos.append(
                    f"cita {c.id}: fuente «{c.fuente_id}» no existe")
            for otro in c.corresponde_en:
                if otro not in ids_cita:
                    fallos.append(
                        f"cita {c.id}: `corresponde_en` apunta a «{otro}», "
                        "que no existe")
            for cond in c.condiciones:
                if cond.cita_id and cond.cita_id not in ids_cita:
                    fallos.append(
                        f"condicion {cond.id}: cita «{cond.cita_id}» no existe")

        for t in self._tablas.values():
            if t.cita_id not in ids_cita:
                fallos.append(f"tabla {t.id}: cita «{t.cita_id}» no existe")
            for errata in t.erratas:
                if errata not in self._discrepancias:
                    fallos.append(
                        f"tabla {t.id}: errata «{errata}» no es una Discrepancia")
            for m in t.modificadores:
                if m.cita_id not in ids_cita:
                    fallos.append(
                        f"modificador {m.id}: cita «{m.cita_id}» no existe")
                for extremo, nombre in ((m.piso, "piso"), (m.tope, "tope")):
                    if extremo is not None and extremo[1] not in ids_cita:
                        fallos.append(
                            f"modificador {m.id}: el {nombre} cita "
                            f"«{extremo[1]}», que no existe")
            for elemento in (*t.columnas, *t.filas):
                uso = elemento.uso
                if isinstance(uso, PendienteDeCondicion) and \
                        uso.condicion_id not in ids_condicion:
                    fallos.append(
                        f"tabla {t.id}: `PendienteDeCondicion` apunta a la "
                        f"condicion «{uso.condicion_id}», que no existe")

        for corr in self._correspondencias.values():
            for lado in (corr.tabla_a, corr.tabla_b):
                if lado not in ids_tabla:
                    fallos.append(
                        f"correspondencia {corr.id}: tabla «{lado}» no existe")

        for f in self._fundamentos.values():
            for cita_id in f.citas:
                if cita_id not in ids_cita:
                    fallos.append(
                        f"fundamento {f.id}: cita «{cita_id}» no existe")

        for f in self._fuentes.values():
            for otra in f.convive_con:
                if otra not in ids_fuente:
                    fallos.append(
                        f"fuente {f.id}: `convive_con` apunta a «{otra}», "
                        "que no existe")

        # Citas huerfanas: nadie las referencia y no sostienen ninguna tabla.
        referenciadas = {t.cita_id for t in self._tablas.values()}
        referenciadas |= {m.cita_id for m in self.modificadores()}
        referenciadas |= {cond.cita_id for _, cond in self.condiciones()}
        referenciadas |= {cid for f in self._fundamentos.values() for cid in f.citas}
        referenciadas |= {cid for c in self._citas.values()
                          for cid in c.corresponde_en}
        referenciadas |= {p.cita_id for d in self._discrepancias.values()
                          for p in d.partes if p.cita_id}
        for m in self.modificadores():
            for extremo in (m.piso, m.tope):
                if extremo is not None:
                    referenciadas.add(extremo[1])
        for t in self._tablas.values():
            for a in t.afirmaciones_negativas:
                if a.cita_id:
                    referenciadas.add(a.cita_id)
            for fila in t.filas:
                for celda in fila.valores.values():
                    cita_id = getattr(celda, "cita_id", None)
                    if cita_id:
                        referenciadas.add(cita_id)
        self._referenciadas = referenciadas
        return tuple(fallos)

    def citas_referenciadas(self) -> frozenset:
        self.problemas_de_integridad()
        return frozenset(self._referenciadas)


def construir() -> Registro:
    """
    Arma el registro. Import diferido a proposito: `citas.py` y `tablas.py`
    importan `esquema` y `fuentes`, y si `registro` los importara arriba
    tendriamos un ciclo en cuanto uno de ellos quisiera consultar el registro.
    """
    from . import citas as _citas
    from . import discrepancias as _discrepancias
    from . import fuentes as _fuentes
    from . import tablas as _tablas

    return Registro(
        fuentes=_fuentes.FUENTES,
        fuentes_ausentes=_fuentes.FUENTES_AUSENTES,
        catalogos=_fuentes.CATALOGOS,
        citas=_citas.CITAS,
        tablas=_tablas.TABLAS,
        discrepancias=_discrepancias.DISCREPANCIAS,
        correspondencias=_tablas.CORRESPONDENCIAS,
        fundamentos=_citas.FUNDAMENTOS,
    )
