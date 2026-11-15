"""
src/
====
El paquete del calculador: UN solo nombre importable (`src`), desde
EXT-9 (PC-08). Todo import de un modulo de este arbol se escribe
`from src... import ...`; la forma plana (`import criterios_adoptados`)
creaba un segundo modulo con su propio estado cuando `src/` estaba en
`sys.path` sin ser paquete. `tests/test_ext9_paquete_servicio.py` lo vigila.
"""
