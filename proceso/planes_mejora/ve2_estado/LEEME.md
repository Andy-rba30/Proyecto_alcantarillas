# Estado de VE-2

Material de proceso, no del entregable. Reescrito el 2026-11-17, en las correcciones de la
revisión independiente (hallazgo B4): hasta entonces este archivo describía el estado de la
mañana del 17 —ningún agente había commiteado y el trabajo vivía en parches— y ya no era
cierto.

## Dónde está

| Paso | Dónde | Estado |
|---|---|---|
| Prompt VE-2 | `main` = `72a8d01`, `proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md` | escrito y aprobado por el dueño |
| Las cuatro partes, (b) → (a, g) → (c) → (e, f, d) | `claude/elegant-rubin-4ax72s`: `9a9b998`, `4c077c2`, `9fedc8d`, `2b9aa21`, `c250d06` | terminadas |
| Integración | `claude/elegant-rubin-4ax72s` = `8dd435e` («validacion(VE-2): integración — VE1-02 (a) a (g)») | suite 7425 / 10 / 7435 |
| Revisión independiente con Fable | `revision/ve2-fable` = `d9b59f9`, informe en `REVISION_FABLE.md` de esta carpeta | «integrar con correcciones»: un alto (A1), cuatro medios, cinco bajos |
| Correcciones de la revisión | rama `claude/youthful-shannon-rjzmuc`, desde `d9b59f9` | en curso |
| Verificación de las correcciones (Fable) y paso a `main` | — | pendiente |

`main` sigue en `72a8d01` hasta que la verificación apruebe.

Los cuatro parches con que se retomó VE-2 (`a_g_materiales.commit.patch`,
`b_velocidad_erosion.commit.patch`, `c_flotacion_v7.wip.patch`, `e_f_d_hidrologia.wip.patch`,
unas 13 700 líneas) se retiraron de esta carpeta: lo que tenían está en los commits de la
tabla, y los archivos siguen en la historia (`git show d9b59f9:proceso/planes_mejora/ve2_estado/<archivo>`).
Ningún test del entregable ni de proceso los leía.

## Los otros archivos de esta carpeta

- `REVISION_FABLE.md`: el informe de la revisión independiente (hallazgos, evidencia, par).
- `PROMPT_CONTINUAR.md` y `PROMPT_REVISION_FABLE.md`: los prompts con que se terminó la
  integración y se lanzó la revisión desde otra cuenta. Se conservan como constancia; los
  dos describen el estado anterior a `8dd435e`.
- `preambulo.md`: el contrato común que se dio a los agentes de las cuatro partes.
- `ejemplos_estructurales.md`: ejemplos resueltos para validar M8 y M9 (ver abajo).

## Entorno (medido)

`python3.12` con tkinter, `xvfb-run -a`, `pip install -r requirements.txt PyMuPDF "pillow<13"`,
y `NORMAS_DIR` = clon de `Andy-rba30/Normas`. La suite se mide en un clon limpio fuera del
repositorio: en un checkout con worktrees de agentes en `.claude/worktrees/`,
`test_los_imports_relativos_solo_viven_en_src_normativa` falla porque barre todo el árbol.

## Lo que sigue después de VE-2 (pedido del dueño, 2026-11-17)

1. **Validación externa de lo estructural**: M8 (cargas sobre el tubo, D-load de AASHTO
   M 170M, TMC y HDPE) y M9 (estabilidad y armado del cabezal, AASHTO LRFD y E.060) no se
   contrastaron contra ningún ejemplo publicado. Hace falta un `validacion_estructural.md`
   generado, como `validacion_hds5.md`, con ejemplos resueltos de AASHTO LRFD, de diseño de
   tubos de concreto y un cabezal calculado a mano o en otro software.
2. **El cabezal no queda diseñado**: la geometría que propone la regla de T-7a no pasa la
   estabilidad LRFD en los 8 cabezales de la validación integral y no se itera (ficha
   T7B-09). Verificarlo con datos reales y que el dueño decida si el programa dimensiona el
   cabezal o sólo verifica uno declarado.
