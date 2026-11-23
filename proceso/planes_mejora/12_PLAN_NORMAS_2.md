# Plan de integración de `normas_2/` (decidido 2026-11-23)

Material de proceso (`proceso/`), no del entregable. El dueño subió al
repositorio de normas (`Andy-rba30/Normas`, commit `ce4c90e`) una carpeta
`normas_2/` con 23 archivos. Esta sesión la revisó sin integrarla. Las
carpetas que ya existían (`normas/`, `ejemplos_resueltos/`) quedaron
idénticas: se comprobó con los hashes de árbol frente al commit anterior,
`991e2de`.

**Decisión del dueño:** después del fast-forward de `main` y de la auditoría
de Fable, hacer N1, N2 y N3 de abajo. El resto queda en el repositorio de
normas como contraste, sin integrarse.

## Reglas para integrar una norma

- La app solo lee la subcarpeta `normas/` de `NORMAS_DIR`
  (`src/normativa/fuentes.py::directorios_de_normas`). Un PDF que se integra
  pasa a `normas/` del repositorio de normas, con su `Fuente` en
  `src/normativa/fuentes.py` (sha1, páginas, paginación) y sus `Cita`
  verificadas contra la página impresa.
- `tests/test_ext6_registro_normativo.py` (PC-23) exige que todo PDF de
  `normas/` sea una fuente presente o esté censado en
  `PRESENTES_SIN_REGISTRAR`. Lo que se queda en `normas_2/` no lo ve.
- Siete PDF son escaneados, sin capa de texto: M 170M-95, M 259M-95,
  M 273M-95, M 288-96, Manual de Puentes 2018, Kramer y Chow. Se verifican
  renderizando la página (`python -m src.normativa.extraccion`).
- `HDMcombined 882025.pdf` (Caltrans HDM 2025, 110 MB) está en Git LFS. La
  vía anónima del contenedor sólo baja el puntero.
- Toda duda, al consultor Fable. Su dictamen va en el commit y en la ficha.
- Se regeneran los documentos generados y la suite completa con
  `NORMAS_DIR` se corre al cerrar.

## N1 · Manual de Puentes 2018 (RD 19-2018-MTC/14)

- El registro (`fuentes.MP`) cita la edición 2016 (RD 041-2016-MTC/14) y la
  marca derogada por la RD 19-2018-MTC/14. Su `pendiente_gabinete` dice:
  «conseguir la edicion 2018 y medir que numerales de los citados
  cambiaron; leer el regimen transitorio de la RD 19-2018-MTC/14».
- Archivo: `normas_2/Manual de Puentes MTC 2018 (PGA).pdf`, 634 páginas,
  escaneado.
- Las 29 citas `MP` que hay que contrastar (de `docs/trazabilidad.csv`):
  - capítulo 2: 2.1.4.3.9, 2.3.1.1.12.3, 2.3.2.5, 2.4.2.1 (Tabla
    2.4.2.1-1), 2.4.2.2, 2.4.3.2.2.2/.3/.5/.6, 2.4.3.3.2, 2.4.3.8.1,
    2.4.3.8.2, 2.4.3.11.2, 2.4.3.11.2.1.1 (fila F y excepciones), Tabla
    2.4.3.11.2.1.2-1 (F_pga), 2.4.4.1.3, 2.4.4.1.5.3, 2.4.5.2, 2.4.5.3.1
    (Tablas 2.4.5.3.1-1 y -2), 2.8.1.1.14.1, 2.8.1.1.14.2.1, Tabla
    2.9.1.5.5.3-1;
  - el resto: A.11.3.1 (K_AE), Figura 1.10-a, Glosario (obras de arte
    menores) e Introducción (LRFD 2014).
- Leer además el PGA de roca del corredor en los mapas de la edición 2018.
  Es el `[S]` `datos_sitio['PGA_roca_B']`, y la fuente ausente
  `APENDICE_A3_MP` remite a la de 2016.
- Resultado esperado: la cita apunta a la edición vigente con su página, o
  se declara la discrepancia en el punto de uso y en la ficha.

## N2 · Marco legal

- `fuentes.LEY_29338` y `fuentes.RNGIV` son hoy `_ausente`. Los archivos:
  `normas_2/ley_29338.pdf` (con texto), `normas_2/4773151-d-s-n-001-2010-ag.pdf`
  (reglamento de la Ley 29338, con texto) y `normas_2/DS 034-2008-MTC (SPIJ).pdf`
  (Reglamento Nacional de Gestión de Infraestructura Vial, con texto).
- Pasan a fuentes presentes, con las citas que la memoria usa: faja
  marginal y autorización de obras en cauces del ANA (comentario en
  `src/servicio.py`, «se apoyaria en la Ley 29338 y la DG-2018, fuentes
  ausentes»).

## N3 · HEC-11 (SI), filtro granular bajo el enrocado

- Archivo: `normas_2/hec11si.pdf` (Design of Riprap Revetment, versión
  métrica, 193 páginas).
- Cierra las fichas que piden «HEC-11 … para el filtro granular»
  (`docs/decisiones_diferidas.md`, alrededor de las líneas 4929, 8981 y
  9019 a la fecha de este plan).

## Lo que queda sin integrar, y por qué

| Archivo | Motivo |
|---|---|
| AASHTO LRFD 10.ª ed. (2024) | El proyecto cita la 9.ª (191 citas). Cambiar de edición obligaría a reverificarlas todas. Sirve para detectar numerales que cambiaron. |
| AASHTO M 259M-95, M 273M-95, ASTM C1433-08 | Norma de producto del cajón prefabricado. La app diseña el marco vaciado en sitio. |
| ASTM A798-13, AASHTO M 288-96 | Instalación de TMC y geotextiles. Se integran cuando una ficha lo pida. |
| AASHTO M 294-17, ASTM A760-15 y A796-15a | Ediciones más nuevas de fuentes registradas: sirven de contraste. |
| AASHTO M 170M-95, M 36M-91 | Ediciones más antiguas. La M 170M-95 podría dejar leer la Clase IV, como contraste declarado. |
| Caltrans Corrosion Guidelines 2021 | Durabilidad. Fuente `[C]` si una ficha lo pide. |
| FHWA GEC 3 (NHI-11-032), HEC-22 4.ª ed. | Sismo geotécnico y drenaje urbano. Fuentes `[C]` de apoyo. |
| Kramer, Chow, Aparicio | Libros de texto. Fuentes secundarias. |

Aparte de la app: el repositorio de normas es **público** y lleva PDF con
copyright (AASHTO, ASTM). Su README recomienda que sea privado.
