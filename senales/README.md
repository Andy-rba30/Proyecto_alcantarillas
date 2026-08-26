# Graficación de señales y transformaciones

- **`transformaciones.py`** — la actividad en Python. Grafica x(t) y sus
  transformaciones en amplitud y en tiempo, cada una definida con una lambda.
  Se ejecuta con `python transformaciones.py` (necesita `numpy` y `matplotlib`).
- `transformacion_senales.m` — versión anterior en MATLAB, interactiva.

## Las transformaciones, en una línea

Todas salen de `y(t) = A*x(a*t + b) + B`:

| | qué cambia | ejemplo |
|---|---|---|
| `A` | amplitud | `2*x(t)` amplifica · `-x(t)` la invierte |
| `B` | nivel | `x(t) + 1` la sube |
| `b` | corrimiento | `x(t-2)` retarda · `x(t+2)` adelanta |
| `a` | escala de tiempo | `x(2t)` comprime · `x(t/2)` ensancha · `x(-t)` refleja |

Ojo con el signo: `x(t-2)` mueve la señal hacia la **derecha**, no hacia la
izquierda; el `-2` se compensa avanzando en t.

Para cambiar de señal se edita una sola línea: la lambda `x` (y `nombre`).
