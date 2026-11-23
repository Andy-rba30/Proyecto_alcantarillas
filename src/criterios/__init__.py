"""
Fichas de criterios adoptados divididas por dominio (bloque D2).
Cada modulo expone su dict `CRITERIOS` respetando el orden original.
"""

from pathlib import Path
from typing import Dict, Tuple

from src.criterios._base import Criterio
from src.criterios import sismo
from src.criterios import hidrologia
from src.criterios import hidraulica
from src.criterios import verificaciones
from src.criterios import geotecnia
from src.criterios import conducto
from src.criterios import proteccion
from src.criterios import cabezal_base
from src.criterios import cabezal_calculo
from src.criterios import metrados

_DIR = Path(__file__).resolve().parent

MODULOS_DE_FICHAS: Tuple[Tuple[Path, Dict[str, Criterio]], ...] = (
    (_DIR / "sismo.py", sismo.CRITERIOS),
    (_DIR / "hidrologia.py", hidrologia.CRITERIOS),
    (_DIR / "hidraulica.py", hidraulica.CRITERIOS),
    (_DIR / "verificaciones.py", verificaciones.CRITERIOS),
    (_DIR / "geotecnia.py", geotecnia.CRITERIOS),
    (_DIR / "conducto.py", conducto.CRITERIOS),
    (_DIR / "proteccion.py", proteccion.CRITERIOS),
    (_DIR / "cabezal_base.py", cabezal_base.CRITERIOS),
    (_DIR / "cabezal_calculo.py", cabezal_calculo.CRITERIOS),
    (_DIR / "metrados.py", metrados.CRITERIOS),
)

ARCHIVOS_DE_FICHAS: Tuple[Path, ...] = (
    _DIR / "__init__.py",
    _DIR / "_base.py",
    *(ruta for ruta, _ in MODULOS_DE_FICHAS),
)

CRITERIOS_DE_FICHAS: Dict[str, Criterio] = {}
ORIGEN_POR_CLAVE: Dict[str, Path] = {}
for _ruta, _fichas in MODULOS_DE_FICHAS:
    for _clave, _criterio in _fichas.items():
        if _clave in CRITERIOS_DE_FICHAS:
            raise ValueError(f"Criterio duplicado en src/criterios: {_clave!r}")
        CRITERIOS_DE_FICHAS[_clave] = _criterio
        ORIGEN_POR_CLAVE[_clave] = _ruta
