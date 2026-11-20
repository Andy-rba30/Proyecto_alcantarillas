import sys, shlex
from pathlib import Path
from tests.apoyo import validacion_integral as V
d = Path(sys.argv[1])
e = V.materializar(V.juego_completo(), d)
print(" ".join(shlex.quote(a) for a in V.argumentos_cli(e)))
