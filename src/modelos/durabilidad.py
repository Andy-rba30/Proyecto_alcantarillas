"""
src/modelos/durabilidad.py
==========================
Fase 3: la matriz de durabilidad (v8 3.3 y 3.4).

Parte del paquete `src.modelos` (D3, plan de mantenibilidad): los tipos se
mueven sin reescribir y `src.modelos` los reexporta con los mismos nombres.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from src.modelos.base import TipoMaterial

if TYPE_CHECKING:  # solo anotaciones (cadenas con `from __future__`)
    from src.modelos.memoria import PasoDeMemoria

# ===========================================================================
# --- T-4 --- Fase 3: la matriz de durabilidad (v8 §3.3 y §3.4)
# ===========================================================================
# Cuatro tipos, y los cuatro fluyen entre modulos: `servicio` arma los
# ensayos desde los datos externos, `M2.matriz_durabilidad` emite el
# dictamen, `MD.disenar_punto` lo recibe para filtrar los candidatos, y M11 y
# la CLI lo imprimen.

# La frase con que la memoria, el volcado de texto y el JSON dicen que la
# matriz no actuo. Escrita UNA vez: la cadena T la pide textual.
DURABILIDAD_SIN_ENSAYOS = "durabilidad: sin ensayos, matriz no aplicada"

# Las claves de los ensayos, que son a la vez las claves con que entran por
# `--datos-externos` (`servicio.CLAVES_DE_DURABILIDAD`) y los nombres de los
# campos de `EnsayosDurabilidad`.
ENSAYOS_DE_DURABILIDAD: Tuple[str, ...] = (
    "sulfatos_suelo_ppm", "sulfatos_agua_ppm", "cloruros_ppm", "pH",
    "resistividad_ohm_cm", "abrasion")


@dataclass(frozen=True)
class EnsayosDurabilidad:
    """
    Los ensayos de durabilidad de UN punto: dato de sitio [S] del EMS y del
    estudio de campo, por punto o comun al corredor.

    TODOS OPCIONALES Y SIN VALOR POR DEFECTO (docs/contrato_entradas.md): un
    campo en None es «no hay ensayo», nunca «el ensayo dio cero». Con los
    seis en None la matriz no actua.

    UNIDADES Y QUE MIDE CADA UNO, porque dos de ellos se confunden:

    sulfatos_suelo_ppm   sulfato soluble en agua presente en el SUELO, en
                         mg/kg (ppm en peso). E.060 Tabla 4.4 lo tabula en
                         porcentaje en peso: 1 % = 10 000 ppm.
    sulfatos_agua_ppm    sulfato (SO4) en el AGUA, en ppm. Es la otra escala
                         de la misma tabla, y NO es la misma magnitud: 1 500
                         ppm en el suelo es exposicion moderada y en el agua
                         es severa.
    cloruros_ppm         cloruros en el suelo o en el agua, ppm.
    pH                   del suelo o del agua; si hay los dos, el mas
                         alejado de 7.
    resistividad_ohm_cm  del suelo o del agua; si hay las dos, la menor.
    abrasion             nivel de abrasion del sitio: una de las claves de
                         `constantes_normativas.NIVELES_DE_ABRASION`.

    `origenes` lleva de donde salio cada dato declarado (el JSON del
    expediente, global o del punto), para que la memoria lo imprima.
    """

    sulfatos_suelo_ppm: Optional[float] = None
    sulfatos_agua_ppm: Optional[float] = None
    cloruros_ppm: Optional[float] = None
    pH: Optional[float] = None
    resistividad_ohm_cm: Optional[float] = None
    abrasion: Optional[str] = None
    origenes: Tuple[Tuple[str, str], ...] = ()

    @property
    def declarados(self) -> Tuple[str, ...]:
        """Las claves que SI traen ensayo, en el orden del contrato."""
        return tuple(clave for clave in ENSAYOS_DE_DURABILIDAD
                     if getattr(self, clave) is not None)

    @property
    def hay_ensayos(self) -> bool:
        return bool(self.declarados)

    def origen_de(self, clave: str) -> str:
        return dict(self.origenes).get(clave, "dato declarado del punto")


class EfectoDeDurabilidad(str, Enum):
    """
    Que hace una regla de la matriz con un material. TRES, y solo el primero
    cambia la lista de candidatos:

    EXCLUYE   el material sale de los candidatos del punto.
    EXIGE     el material sigue candidato CON un requisito de especificacion
              (tipo de cemento, proteccion de la tuberia) que la memoria
              deja escrito.
    AVISA     ni excluye ni exige: la fuente es cualitativa o recomienda, y
              la memoria lo imprime para que el proyectista decida.
    """

    EXCLUYE = "excluye"
    EXIGE = "exige"
    AVISA = "avisa"


@dataclass(frozen=True)
class ReglaDeDurabilidad:
    """
    UNA consecuencia de un ensayo sobre un material (o sobre el punto entero,
    con `material` en None): que ensayo la dispara, que efecto tiene, que
    hace el proyecto con ella y en que citas del registro se apoya.

    `texto` es lo que el proyecto HACE, en prosa propia: no entrecomilla la
    fuente. La frase de la fuente la imprime la memoria desde el registro,
    por `cita_ids`.
    """

    ensayo: str
    material: Optional[TipoMaterial]
    efecto: EfectoDeDurabilidad
    texto: str
    cita_ids: Tuple[str, ...]
    criterio: str = ""


@dataclass(frozen=True)
class DictamenDurabilidad:
    """
    Lo que la matriz de durabilidad dice de un punto.

    `aplicada` es False cuando el punto no trae NINGUN ensayo: entonces no
    hay reglas de ensayo ni pasos, los candidatos son los de la familia y la
    memoria imprime `DURABILIDAD_SIN_ENSAYOS`. El aviso del suelo de
    fundacion NO depende de los ensayos --lee una columna obligatoria del
    CSV-- y puede venir en `reglas` aunque `aplicada` sea False.

    `suelo_fundacion` es la linea que dice que se leyo de `sucs_fundacion` y
    contra que conjunto, se dispare o no el aviso.
    """

    aplicada: bool
    reglas: Tuple[ReglaDeDurabilidad, ...] = ()
    pasos: Tuple["PasoDeMemoria", ...] = ()
    ensayos: Optional[EnsayosDurabilidad] = None
    suelo_fundacion: str = ""

    @property
    def excluidos(self) -> Tuple[TipoMaterial, ...]:
        """Los materiales que la matriz saca de los candidatos, sin repetir."""
        vistos: list = []
        for regla in self.reglas:
            if regla.efecto is EfectoDeDurabilidad.EXCLUYE \
                    and regla.material is not None \
                    and regla.material not in vistos:
                vistos.append(regla.material)
        return tuple(vistos)

    def reglas_de(self, material: Optional[TipoMaterial]) -> Tuple[ReglaDeDurabilidad, ...]:
        return tuple(r for r in self.reglas if r.material is material)

    def motivo_de_exclusion(self, material: TipoMaterial) -> str:
        """Por que quedo fuera ese material, o cadena vacia si no quedo."""
        return "; ".join(r.texto for r in self.reglas
                         if r.material is material
                         and r.efecto is EfectoDeDurabilidad.EXCLUYE)

    @property
    def resumen(self) -> str:
        """La linea que encabeza el bloque de durabilidad del punto."""
        if not self.aplicada:
            return DURABILIDAD_SIN_ENSAYOS
        declarados = ", ".join(self.ensayos.declarados) if self.ensayos else ""
        fuera = ", ".join(m.value for m in self.excluidos) or "ninguno"
        return (f"durabilidad: matriz aplicada con {declarados}; materiales "
                f"excluidos: {fuera}")
