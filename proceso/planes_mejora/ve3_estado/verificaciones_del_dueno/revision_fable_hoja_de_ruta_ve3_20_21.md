# Revisión independiente (Fable) de las correcciones de la hoja de ruta VE3-20 y VE3-21

Fecha: 2026-11-20. Sesión `claude/cool-euler-tpoj7o`. Revisión de sólo lectura, encargada por la
sesión que escribió las correcciones, a un agente con el modelo Fable. No corrió la suite ni el
pipeline: lo que dice del código sale de leer los valores de archivo, `M9.factor_muro`, el informe
`sismo_cabezal_que_se_pasa.md` y `docs/validacion_integral.md`.

Qué se revisó: el diff de `docs/hoja_de_ruta_alcantarillas_v8.md` que el dueño aprobó el
2026-11-20: (a) Fase 9, viñeta «El agua una sola vez» y nota «Corregido (`VE3-21`)»
(`drenaje_trasdos` = `drenado` de archivo); (b) §9.2, cursiva tras la cadena sísmica y nota
«Corregido (`VE3-20`)» («No asumirlo en un cabezal empotrado en terraplén» → «No se asume de
archivo: se declara por obra»).

## Veredicto: integrar con correcciones

Las dos correcciones son correctas en el fondo y todas las citas literales existen en el PDF con
su numeral y página. Dos correcciones de redacción antes de integrar (H1, H2); el resto, menor.

## 1. Citas contra la fuente primaria (todas coinciden palabra por palabra, sin elisiones internas)

| Cita | Resultado |
|---|---|
| 11.6.6, pág. 11-35, PDF 1504, «Backfills behind abutments… water in the backfill» | Literal y completa; normativa («shall»). |
| C11.6.5.3, pág. 11-31, PDF 1500, «The time-averaged mean groundwater elevation should be used…» | Literal; comentario y «should» (ver H3). |
| 11.6.5.2.1, pág. 11-27, PDF 1496, «kh0 is the seismic horizontal acceleration coefficient assuming zero wall displacement occurs» | Literal (en la fuente, dentro de un paréntesis tras «where»). |
| 11.6.5.2.2, pág. 11-28, PDF 1497, «if the wall is free to move laterally… acceptable to the Owner» | Literal; «la autoriza» es fiel. |
| 11.5.4.2, pág. 11-9, PDF 1478, «As, is less than or equal to 0.4g» | Literal (ver H1 sobre el argumento). |
| C11.6.5.4, pág. 11-32, PDF 1501, «abutment walls with structural wing walls» | Literal; «pueden no ceder» traduce «may be nonyielding». |
| C11.6.6 (paráfrasis de los lloraderos) | Fiel a «Weep holes or geocomposite panel drains at the wall face do not assure fully drained conditions». |
| Manual de Puentes 2.8.1.1.14.2.2, pág. impresa 255 | Correcto (PDF 256; el encabezado del numeral está en la 254). |

## 2. Hallazgos y lo que hizo la sesión

- **H1 (medio-alto).** El punto (2) de la nota VE3-20 decía que la exención de 11.5.4.2 «no
  aplica» porque A_s = 0.50 g, pero la condición es disyuntiva (Zonas 1 a 3 **o** A_s ≤ 0.4 g):
  hay que decir además que la zona no es Zona 1 a 3, y la Zona 4 sólo está estimada (S_D1 ≈ 0.63
  a 0.72) con una lectura propia de S1 que no es dato [S]. **Corregido** en la nota y en la ficha
  VE3-20 («no puede invocarse… mientras no se confirme una Zona 1 a 3»).
- **H2 (medio).** El punto (3) atribuía al informe una medida de los cuatro puntos que el informe
  no hizo (midió A-01, con `sin_drenaje`), y «E1 y E3» era ambiguo. Con el drenado de archivo
  fallan E3 los ocho cabezales y además E1 los de salida (`docs/validacion_integral.md` §2,
  variante `decisiones_de_archivo`). **Corregido** con ese texto.
- **H3 (bajo-medio).** «el nivel medio que pide C11.6.5.3»: es un «should» de comentario, y la
  equivalencia con el freático del punto es lectura del proyecto. **Corregido** («que el proyecto
  toma como el nivel medio que C11.6.5.3 recomienda») en la nota y en la ficha VE3-21.
- **H4 (bajo).** Texto viejo en `tests/test_M9_cabezal.py:242` y «el lado conservador» sin su
  coste en la ficha de `factor_muro_eleccion`; la nota pedía dos justificaciones y la ficha
  tres. **Corregido** los tres.
- **H5 (bajo, preexistente).** La viñeta «Bajo sismo» de la Fase 9 seguía diciendo que con
  k_h = 0.50 la condición sísmica es no evaluable. **Marcada** como superada (cuña de tanteo de
  T-7b H4 y VE-3.14: da cifra y no cumple), con remisión a la nota VE3-20.
- **H6 (informativo).** El Manual traduce «kh0, será reducido» donde AASHTO dice «should be
  reduced»; la nota cita el Manual sólo como paralelo y no le atribuye verbo. Sin cambio.

## 3. Confirmado sin hallazgo

Valores de archivo (`drenaje_trasdos` = `drenado`, `factor_muro_eleccion` = `sin_reduccion`,
`regimen_resistencia_elementos_cabezal` = `no_cedente_k0`, `dimensionamiento_zapata_cabezal` paso
0.10 m y tope 1.5·H_c); la guardia de un solo régimen en `M9.factor_muro`; que con reducción +
cedente + drenado los ocho cabezales cumplen (`docs/validacion_integral.md`); que no queda otra
frase de la hoja de ruta con `sin_drenaje` de archivo ni que prohíba la reducción.
