# Estado de las ramas del repositorio (2026-10-09)

**Respuesta corta: sí, `main` tiene la versión más actualizada del código.**
Hay 25 ramas en el remoto y 24 están completamente contenidas en `main`
(0 commits por delante). La única excepción es una rama de hoy con un solo
archivo de documentación, no código.

## Estado de `main`

| Dato | Valor |
|---|---|
| Último commit | `c2262a2` — gui(rediseño 4), 2026-09-22 |
| Commits totales | 449 |
| Rama local de esta sesión (`claude/charming-ptolemy-rk3y0q`) | idéntica a `main` |

## La única rama con trabajo no fusionado

- **`claude/laughing-volta-ubcdsj`**, commit `077056f` de hoy
  (2026-10-09 16:10 UTC): 1 commit adelante y 0 atrás de `main`.
- Añade solo `respuesta_datos_cruces.md` en la raíz del repositorio
  (92 líneas): una respuesta sobre qué columnas del CSV cubre una tabla de
  seis cruces de canal y cuáles faltan.
- No toca `src/`, `gui/`, `tests/` ni `docs/`. Es un borrador de ayuda al
  usuario generado en otra sesión, no una versión del software.

## Las otras 23 ramas (todas fusionadas)

| Rama | Adelante | Atrás | Fecha |
|---|---|---|---|
| archivo/expediente-2026-09-21 | 0 | 35 | 2026-09-21 |
| claude/blissful-wright-trtcxh | 0 | 38 | 2026-09-21 |
| claude/bold-hypatia-kici5k | 0 | 16 | 2026-09-21 |
| claude/dreamy-turing-wt1yd9 | 0 | 50 | 2026-09-20 |
| claude/eloquent-pasteur-kwwmop | 0 | 35 | 2026-09-21 |
| claude/exciting-bell-zbjgw8 | 0 | 42 | 2026-09-21 |
| claude/ext-4-deuda-tecnica-szclb3 | 0 | 56 | 2026-09-20 |
| claude/festive-cray-ft8ibd | 0 | 62 | 2026-09-20 |
| claude/festive-euler-wlva7n | 0 | 5 | 2026-09-22 |
| claude/funny-franklin-nhh2es | 0 | 40 | 2026-09-21 |
| claude/gallant-dirac-3mt6jo | 0 | 54 | 2026-09-20 |
| claude/gifted-keller-z060ct | 0 | 52 | 2026-09-20 |
| claude/guia-perfil-tesista-xvk30j | 0 | 12 | 2026-09-21 |
| claude/indice-formulas-dimensional-i0hffh | 0 | 91 | 2026-09-14 |
| claude/inspiring-lamport-1c7ghw | 0 | 46 | 2026-09-21 |
| claude/kind-cori-74qchh | 0 | 64 | 2026-09-20 |
| claude/magical-cray-x96fow | 0 | 83 | 2026-09-14 |
| claude/magical-heisenberg-yv9a9j | 0 | 68 | 2026-09-20 |
| claude/modest-hypatia-87ubz8 | 0 | 89 | 2026-09-14 |
| claude/peaceful-keller-f8kfzj | 0 | 59 | 2026-09-20 |
| claude/sweet-ptolemy-mintvw | 0 | 19 | 2026-09-21 |
| claude/tkinter-gui-visual-redesign-6p8fwx | 0 | 0 | 2026-09-22 |
| claude/zen-euler-6i4q2w | 0 | 66 | 2026-09-20 |

Son las ramas de cierre de cada sesión (EXT-0 a EXT-11, E-A, E-B, PF-3 a
PF-6, I4, T3, PD, el cierre C10/C05/C09/C11/C14 y el rediseño de la GUI).
Todas están en `main` y son candidatas a borrarse. No se borró ninguna.

## Nota sobre la medición

El contenedor arrancó con un clon superficial de 50 commits, y con eso
varias ramas aparentaban tener cientos de commits «adelante». Se trajo el
historial completo (`git fetch --unshallow`) antes de contar, y con el
historial entero esos conteos bajaron a cero.

## Opciones

1. Fusionar `claude/laughing-volta-ubcdsj` a `main` para incorporar el
   documento de cruces.
2. Dejarlo fuera, o moverlo a `docs/` antes de fusionar.
