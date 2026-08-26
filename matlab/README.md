# transformacion_senales.m

Versión ergonómica del script de transformación de señales

    y(t) = A * x(a*t + b) + B

Es **un solo archivo**. Ábrelo en MATLAB y pulsa **Run** (o escribe
`transformacion_senales` en la Command Window). No hay que editar el código.

## Qué se arregló respecto a la versión anterior

| Problema | Cómo queda ahora |
|---|---|
| "Pide raro los coeficientes": cuatro `input()` seguidos, sin valor por defecto, y si pulsabas Enter devolvía `[]` y el script reventaba o graficaba vacío | Cada coeficiente muestra su valor entre corchetes; **Enter lo deja como está**. Acepta `3/4`, `pi/2`, `-0.5`. Si escribes cualquier otra cosa lo dice y vuelve a preguntar, no se cae. También puedes escribir los cuatro de una vez: `2 -1 3 -1` |
| "No dice qué operación hace, solo la gráfica" | Escribe la fórmula ya con los números puestos (`y(t) = 2*x(-t + 3) - 1`) y **enumera en palabras cada operación en su orden**: corrimiento, reflexión, compresión/expansión, amplificación/atenuación, corrimiento vertical. Sale en la Command Window **y dentro de la propia figura**, en un recuadro |
| Había que editar el código para cambiar la señal | Menú con 6 señales típicas + opción de escribir la tuya (avisa si te olvidas de los puntos `.*` `./` `.^`) |
| El eje fijo `-5..5` cortaba la señal al correrla o ensancharla | El eje de tiempo se calcula para que entren la original **y** la transformada |
| `a = 0` producía una gráfica sin sentido | Se rechaza con una explicación |
| Un solo intento por ejecución | Al terminar: `Enter` para otra transformación, `c` para cambiar de señal, `q` para salir |

## Los dos modos

1. **Guiado** — escribes `A`, `a`, `b`, `B` y obtienes la explicación escrita
   más la gráfica (original arriba, comparación abajo, resumen en el recuadro).
2. **Interactivo** — cuatro deslizadores; la gráfica, el título con la fórmula
   y la lista de operaciones se actualizan solos mientras los mueves. El eje
   vertical es fijo a propósito: si se reajustara solo, el cambio de amplitud
   no se vería.

## Los cuatro coeficientes

| | qué hace | neutro | ejemplos |
|---|---|---|---|
| `A` | amplitud | `1` | `2` el doble · `0.5` la mitad · `-1` la invierte arriba/abajo |
| `a` | escala de tiempo | `1` | `2` la comprime · `0.5` la ensancha · `-1` la espeja |
| `b` | corrimiento en el tiempo | `0` | `+2` dos a la izquierda · `-2` dos a la derecha |
| `B` | nivel | `0` | `+1` la sube · `-1` la baja |

## El detalle del orden (por eso el programa lo avisa)

En `y(t) = A*x(a*t + b) + B` el orden en que se aplican las operaciones cambia
cuánto vale el corrimiento:

- Si **corres primero y escalas después**, el corrimiento es `b`.
- Si **escalas primero y corres después**, el corrimiento es `b/a`.

El programa usa el primer orden y, cuando `a ≠ 1` y `b ≠ 0`, imprime también
`b/a` para que no te confundas. Como comprobación numérica dice dónde acaba lo
que en `x(t)` ocurría en `t = 0`: en `t = -b/a`.
