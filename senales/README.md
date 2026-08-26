# Graficación de señales y transformaciones

**`transformaciones.m`** — la actividad. Grafica x(t) y nueve transformaciones
en amplitud y en tiempo, cada una definida con una función anónima `@(t)...`
(el equivalente en MATLAB a una lambda). Se abre en MATLAB y se pulsa Run.

Extras, no hacen falta para la entrega:
- `transformacion_interactiva.m` — la misma idea pero pidiendo A, a, b y B por
  teclado o con deslizadores, y explicando en palabras qué operación hace.
- `transformaciones.py` — la misma actividad en Python.

## Las transformaciones

Todas salen de `y(t) = A*x(a*t + b) + B`:

| | qué cambia | ejemplo |
|---|---|---|
| `A` | amplitud | `2*x(t)` amplifica · `-x(t)` la invierte |
| `B` | nivel | `x(t)+1` la sube |
| `b` | corrimiento | `x(t-2)` retarda · `x(t+2)` adelanta |
| `a` | escala de tiempo | `x(2t)` comprime · `x(t/2)` ensancha · `x(-t)` refleja |

Dos detalles que conviene tener claros:

- `x(t-2)` mueve la señal hacia la **derecha**, aunque el signo sea negativo.
- El eje vertical está fijo en `±2.2` a propósito. Si se deja en automático,
  `2*x(t)` se ve idéntica al original porque la curva siempre llena el recuadro.

Para cambiar de señal se editan dos líneas: `nombre` y la anónima `x`.
