# Encargo T-8 (protección de entrada y salida) — MODO PARALELO, FASE A — CONTINUACIÓN

Worktree `/home/user/wt/T-8`, rama `tesis/T-8` (base `ad5cb97` = T-0 + T-2; `origin/main` ya va por delante: se rebasa en FASE B).
**Otro agente empezó este prompt y fue pausado**: la rama tiene commits WIP y hay 3 archivos sin commit
(`src/normativa/fundamentos.py`, `src/variables_entrada.py`, `tests/test_normativa.py`). Empieza por `git log --oneline ad5cb97..HEAD`,
`git diff ad5cb97 HEAD --stat` y `git status`/`git diff` para entender QUÉ está hecho y qué falta (su último paso anunciado era
«parchear M11»); no rehagas lo hecho: revísalo con ojo crítico, complétalo y ciérralo. No toques otros worktrees ni
`/home/user/proyecto_alcantarillas` (checkout de `main`).

PRIMERO lee entero `/tmp/claude-0/-home-user/8c9a9d01-15e4-5a10-91d4-d894b414664c/scratchpad/ORQUESTACION.md` (rutas, entorno con
`NORMAS_DIR`, reglas no negociables, paradas, decisiones del dueño, LECCIONES de las auditorías, FASE A/FASE B, commit e informe).
Después, en el worktree: `CLAUDE.md` ENTERO, la nota del orquestador y la §2 de `docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`,
`docs/contrato_entradas.md`, y del INFORME (`/home/user/andy-rba30/cotas-esviaje-alcantarillas/INFORME_evaluacion_app_alcantarillas_vs_PDF.md`) §0, §2, §3.3, §5.1.

## El prompt, tal cual (bloque T-8 de la cadena)

```text
Ejecuta únicamente T-8 de CADENA_PROMPTS_tesis_app_alcantarillas.md y aplica sus reglas comunes. Cierra INF-3.3 "protección" e INF-5.1.11 (M6 sin protección de entrada). Fuentes: manual MTC 4.1.1.3.7 c) ec. (49) Laushey y Láminas 04–05; HDS-5 §3.1.6 (velocidad de salida) y §5.x (scour, referencia a HEC-14); HEC-14 (hec14.pdf, ya en Normas): cap. 10 (riprap aprons y riprap basins), cap. 4–5 (velocidad de salida y disipadores internos), cap. 3 (socavación a la salida); cada fórmula transcrita con página verificada.

1. Salida: conserva Laushey (d50) y añade: Froude a la salida; longitud y d50 del apron por HEC-14 cap. 10 (Froude a la salida, TW/D), con la Lámina 05 del MTC como contraste; espesor 1.5–2.0·d50 [C/A]; filtro (geotextil o granular) como requisito declarado [N] de EG-2013 si lo trae, o [A]; velocidad admisible del cauce receptor (manual MTC Tabla 11 por tipo de terreno, entrada [S] tipo_terreno_receptor) con aviso cuando V_salida la supera y cálculo del d50 solo entonces.

2. Entrada: protección de taludes del terraplén y zampeado/caja según tipo de embocadura (T-7a); emboquillado de piedra como [A] de catálogo con cita a las Láminas.

3. Socavación local a la salida (HEC-14 cap. 3, método de la hoya de socavación) como estimación para la profundidad de desplante del cabezal (T-7a punto 2); el dato externo "profundidad de socavación estimada" gana si viene.

4. M6 pasa a llamarse de verdad "protección de entrada y salida"; todas las magnitudes con PasoDeMemoria y fórmula sustituida.

Ritual de cierre.
```

## Precisiones del orquestador

- IDs canónicos: lo que el prompt llama `INF-5.1.11` es **`INF-5.1.13`**; «INF-3.3 protección» es la fila `INF-3.3.k` que T-0 te asigna
  (hoja `Hallazgos`, sólo lectura en FASE A; `tests/apoyo/tracker.py`).
- **ERRATA DE LA CADENA (verificada por T-0 contra `hec14.pdf`): en HEC-14 (FHWA-NHI-06-086, 3.ª ed., 2006) la socavación a la
  salida es el CAPÍTULO 5, no el 3; la velocidad de salida es el cap. 3; los disipadores internos el cap. 7.** Verifica el índice y cita
  por el capítulo REAL; riprap apron / riprap basin donde estén de verdad (cap. 10). Gana la fuente; declara la discrepancia.
- Dorados: al menos un ejemplo numérico RESUELTO de HEC-14 para el apron y uno para la hoya de socavación (con página), más uno a mano
  por fórmula con la aritmética escrita. Coeficientes empíricos dependientes de unidades con sufijo `_SI` y el valor inglés en comentario.
  Rangos de validez transcritos; fuera de rango: lo que la fuente diga (describe población → aviso/criterio; prohíbe → no evaluable).
- **Entradas que no se inventan** (opcionales, sin valor por defecto): `tipo_terreno_receptor`, propiedades del lecho que el método de
  socavación pida (d50/d84, cohesión/IP…), duración del caudal. Sin el dato → `DatoFaltanteError` claro o «no evaluado» con aviso, nunca
  un suelo supuesto. Lo que M6 hace hoy (d50 de Laushey, espesor 1.75·d50, longitud 5.0 m) debe dar los MISMOS números en el fixture:
  lo nuevo va al lado; sin `tipo_terreno_receptor` se conserva la conducta de hoy y se avisa.
- Punto 2 depende de T-7a (no existe aún): implementa contra la embocadura de hoy (`square edge w/ headwall`) con la interfaz lista;
  lo que no cierre sin T-7a, ficha diferida. Punto 3: función pública que T-7a consumirá (socavación estimada por punto con su
  PasoDeMemoria) + dato externo `profundidad_socavacion_estimada_m` que gana si viene.
- Láminas 04–05 del MTC: son figuras, por imagen; cita sólo lo que digan. EG-2013 sobre filtro/geotextil/emboquillado: numeral real o nada.
- Con `S_conducto = 0` (T-2) `V_erosion`/`y_normal` son `None`: M6 lee `V_salida`; Froude con tirante y velocidad de SALIDA de M4.
- PARADA (c): nada debe mover un diámetro; compruébalo contra la línea base y dilo.
- `tests/test_t0_gobernanza.py` exige que HEC-14 siga sin citas: te toca actualizarlo (conflicto probable al integrar: T-1 y T-4 lo tocaron por WSDOT).
- Zonas calientes: `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`, `M11_reporte.py`,
  `normativa/{citas,tablas,fundamentos}.py`, `decisiones_diferidas.md` (Partes XLI–XLIV ocupadas: rótulo provisional), v8, `CLAUDE.md`.
  Bloques `# --- T-8 ---` al final de sección; no reordenes nada ajeno. Tu módulo: `src/modulos/M6_proteccion.py`.

Al terminar la FASE A (suite entera verde en tu rama con `NORMAS_DIR`, commits intermedios frecuentes —puede haber cortes por límite de
uso—, SIN tocar xlsx / tabla de CLAUDE.md / `verificar_sesion.py`, SIN fusionar ni empujar, NUNCA `git stash`), devuelve el informe con
el formato de ORQUESTACION.md, con las filas del tracker para la integración. No ejecutes ningún otro prompt.
