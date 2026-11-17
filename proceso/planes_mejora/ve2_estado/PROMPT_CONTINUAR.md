# Prompt para terminar e integrar VE-2 desde otra cuenta

La sesión orquestadora se detuvo el 2026-11-17 por cuota (96 % semanal). Pega el bloque
`text` en una sesión nueva sobre `Andy-rba30/Proyecto_alcantarillas`. Cuando termine,
lanza la revisión con `PROMPT_REVISION_FABLE.md` en OTRA sesión (el revisor no debe ser el
mismo que integró).

```text
Retoma VE-2 del repositorio Andy-rba30/Proyecto_alcantarillas. Lee enteros CLAUDE.md, proceso/reglas_de_correccion_de_auditorias.md, el bloque «### VE-2» de proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md, y proceso/planes_mejora/ve2_estado/LEEME.md y preambulo.md (entorno: python3.12 con tkinter, xvfb, pip install -r requirements.txt PyMuPDF "pillow<13"; clona Andy-rba30/Normas y export NORMAS_DIR). Trabaja en la rama claude/elegant-rubin-4ax72s (git fetch origin claude/elegant-rubin-4ax72s); main está en 72a8d01 y NO se toca hasta que la revisión con Fable apruebe.

Estado de las cuatro partes (parches en proceso/planes_mejora/ve2_estado/, todos contra 72a8d01):
- (b) TERMINADA: b_velocidad_erosion.commit.patch (git am; 1 commit; suite 7293/10/7303).
- (a) y (g) TERMINADAS: a_g_materiales.commit.patch (git am; 2 commits; suite 6778/10/6788).
- (c1) terminada y (c2) A MEDIAS: c_flotacion_v7.wip.patch (diff de trabajo que incluye el commit de c1 y lo que había de c2 cuando se detuvo; el agente esperaba el resultado de su suite completa). Termina el paso 13 del prompt.
- (e) y (f) terminadas y (d) A MEDIAS: e_f_d_hidrologia.wip.patch (incluye los commits de e y f; se detuvo agregando el barrido de sensibilidad de factor_intervalo_fijo_p24). Termina los pasos 11 y 12.
Aplica cada parte en una rama propia desde 72a8d01, en este orden de integración: (b) → (a, g) → (c) → (e, f, d). Lo a medias se trata como BORRADOR: revísalo contra el prompt, completa los tests en rojo que falten y no lo des por bueno por estar escrito.

Al integrar en claude/elegant-rubin-4ax72s: los recuentos de criterios (141 + los nuevos de cada parte) se suman en tests y en CLAUDE.md («N desde VE-2» donde hoy dice «141 desde …»); la línea base y los documentos generados se REGENERAN sobre el conjunto con sus comandos (CLAUDE.md, «Tests»), y sólo (b) mueve números; las fichas de docs/decisiones_diferidas.md se conservan todas; abre la ficha VE2-01 con lo que sigue mal en la hoja de ruta (doble n rotulada «Regla [N]» en §4.1, fila V7 sin decir que el nivel de agua de diseño lo fija el Propietario, la §1.2 de VE1-01). Corre la suite en un clon LIMPIO fuera del repo (un checkout con worktrees dentro hace fallar test_los_imports_relativos_solo_viven_en_src_normativa) y en una exportación (git archive HEAD); fila del par en proceso/bitacora_conteos_y_entorno.md. Commit final «validacion(VE-2): integración — VE1-02 (a) a (g)» y push a claude/elegant-rubin-4ax72s. Informe breve: commits, par de la suite, números movidos, lo diferido.
```
