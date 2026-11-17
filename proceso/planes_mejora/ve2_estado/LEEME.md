# Estado de VE-2 (para retomar en otra sesión)

Material de proceso, no del entregable. Lo dejó la sesión orquestadora el 2026-11-17 porque
el presupuesto de tokens de la sesión estaba sobre el 90 %.

## Dónde quedó

- `main` = `72a8d01`: VE-1 integrado y el prompt VE-2 en
  `proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md`.
- Suite de partida medida en un clon limpio de `72a8d01` (python 3.12 con tkinter, xvfb,
  `NORMAS_DIR` enlazado): **6739 passed, 10 skipped, 6749 collected**, igual que VE-1.
  Ojo: en el checkout principal `test_los_imports_relativos_solo_viven_en_src_normativa`
  falla mientras existan worktrees de agentes en `.claude/worktrees/` (el test barre todo el
  árbol); medir siempre en un clon limpio.
- VE-2 se repartió en cuatro agentes en paralelo, cada uno en su worktree, con el contrato
  común de abajo. **Ninguno había commiteado todavía** cuando se guardó este estado; sus
  cambios en curso están en los parches `*.wip.patch` de esta carpeta (diff contra
  `72a8d01`, incluidos los archivos nuevos). Son trabajo A MEDIAS: no se integran tal cual.

| Parche | Decisiones VE1-02 | Pasos del prompt | Mueve la línea base |
|---|---|---|---|
| `b_velocidad_erosion.wip.patch` | (b) | 1-5 | sí |
| `a_g_materiales.wip.patch` | (a), (g) | 7, 14 | no (valores de archivo) |
| `c_flotacion_v7.wip.patch` | (c1), (c2) | 6, 13 | no (valores de archivo) |
| `e_f_d_hidrologia.wip.patch` | (e), (f), (d) | 8, 10-12 | no (valores de archivo) |

## Cómo retomar

1. Entorno: `apt-get install -y python3-tk xvfb`; usar `python3.12` (el 3.13 del contenedor
   no trae tkinter) con `pip install --break-system-packages -r requirements.txt PyMuPDF` y
   `pillow<13` (ttkbootstrap); clonar `Andy-rba30/Normas` y `export NORMAS_DIR=<clon>`.
2. Si los agentes de la sesión anterior terminaron y sus ramas existen, integrar sus ramas.
   Si no, partir de `main`, aplicar el parche de la parte (`git apply --3way`) como
   BORRADOR y terminar los pasos del prompt VE-2 que falten (tests en rojo primero).
3. Integrar en orden de bloque: (b) → (c1, a, e) → (f, d) → (c2, g). Conflictos esperables
   y cómo se resuelven: los recuentos de criterios (141 + los nuevos) se suman; los
   documentos generados y la línea base se REGENERAN sobre el conjunto con sus comandos;
   fichas de `docs/decisiones_diferidas.md`, se conservan todas.
4. Revisión independiente con el modelo Fable (pedido del dueño) de lo más crítico: (b), (f),
   (c2)+(g) y la integración final. El revisor recibe el diff y el prompt, no las
   conclusiones del implementador; reverifica citas en el PDF y recalcula a mano la ALC46 de
   UPAO (V_erosion ≈ 5.81 m/s, Ø 0.90 m) y una cuenca de 55.9 km² por el racional modificado.
5. Después: ficha VE2-01 (lo que sigue mal en la hoja de ruta), CLAUDE.md («141 desde …» →
   «N desde VE-2»), fila del par en `proceso/bitacora_conteos_y_entorno.md`, suite en clon
   limpio y en exportación, y empujar a `main`.

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

## Contrato común que se dio a los agentes

Ver `preambulo.md` en esta carpeta.
