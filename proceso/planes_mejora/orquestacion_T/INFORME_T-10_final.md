# INFORME T-10 · FINAL — memoria M11 completa: correcciones de la auditoría e integración

- **Commit en `origin/main`: `14f6138f6763d7fa3f9e56054b281316ff6809ce`** (un solo commit `tesis(T-10): memoria M11 completa — … — INF-3.4.7, INF-4.7, INF-5.1.10 (cerrados)`, padre `2265d90`, avance rápido). `origin/main == HEAD` confirmado. La rama `tesis/T-10` no se pudo reescribir sin forzar: el mismo commit está en la rama nueva **`tesis/T-10-final`**.
- Sin cambios de cálculo. M11 sólo formatea (test por AST).

## 1. Par de la suite (medido sobre el árbol integrado)

| Configuración | passed | skipped | collected |
|---|---|---|---|
| PyMuPDF sí · Tk no · **con** `NORMAS_DIR` (MEDIDO) | **6337** | 23 | **6360** |
| PyMuPDF sí · Tk no · **sin** `NORMAS_DIR` (MEDIDO) | 6319 | 41 | 6360 |
| sí · sí / no · sí / no · no | 6350 / 6206 / 6193 (derivados, no medidos: el contenedor no tiene tkinter) | 10 / 154 / 167 | 6360 |

Base `2265d90`: 6287 / 23 / 6310 (sin `NORMAS_DIR`: 6269 / 41). **+50 netos**: 43 de `tests/test_t10_memoria.py` (33 de la FASE A + 10 de las correcciones), +8 anclajes en `test_decisiones_diferidas` (T10-01..08), −1 en `test_guardias_de_la_suite` (`M11_reporte.verificaciones_publicadas` sale del censo de públicas sin referencia). Ninguno `pdf`, Tk ni `NORMAS_DIR`. `--collect-only -m pdf`: 145, sin cambio.

## 2. IDs (canónicos)

| ID | Estado | Nota |
|---|---|---|
| `INF-3.4.7` | **Cerrado** (T-10) | La Fase 9 del punto y del proyecto, entera, en la memoria HTML. |
| `INF-4.7` | **Cerrado** (T-10), con salvedad | Tabla estática/sísmica, fórmulas sustituidas, FS/φR vs ΣγQ, geometría, solicitaciones, armado en tabla. Sin «referencia al plano»: el programa no produce planos. |
| `INF-5.1.10` | Cerrado por T-0; **NOTA** de T-10 | Lo que T-0 dejó a T-10 (ficha T0-02): índice regenerado con corridas que dimensionan; la fila 4.4 cita HDS-5 núm. 3.3.5. Responsable «Claude Code (cadena T, T-0) → Claude Code (cadena T, T-10)». El canónico `INF-5.1.9` (`sucs_fundacion`) no se tocó. |

Tracker `.xlsx` actualizado (Estado / Responsable / Commit); `LO_QUE_ESCRIBIO_CADA_PROMPT` gana la fila `"T-10": {Cerrado: {INF-3.4.7, INF-4.7}}` (INF-5.1.10 sigue en la de T-0: una fila no figura en dos prompts).

## 3. Hallazgo por hallazgo (AUDITORIA_T-10.md: AJUSTADO, 2 MEDIA y 5 BAJA)

- **H1 (MEDIA) — CERRADO.** El censo buscaba cada número en todo el bloque. Ahora cada entrada de `tabla[]` y `secciones[]` del armado se compara con SU fila (por elemento/posición, formato de M11), cada `combinaciones[].excentricidad` en su columna, cada solicitación en su fila, el bloque del proyecto se imprime en tablas con la clave en la primera columna (cabezales, K_AE/K_A, recubrimientos, cuantías, eslabones) y se censa por clave, y el anexo A.4 exige la ventana de cada clave en su fila. Tests `test_h1_*` (5). Mutantes M-A, M-E, M-L y M-M **muertos** (medido sobre una copia del árbol).
- **H2 (MEDIA) — CERRADO.** El paso 7.B.3b ya no lleva `formula_cita_id`; HDS5_3ED.2.2.4#LONGITUD queda en `citas_textuales` como contexto, y la nota es la del 7.B.3 (`M7.NOTA_ALGEBRA_DE_LA_LONGITUD`) más la del reparto. `test_t6_geometria` ajustado; `test_h2_*`.
- **H3 (BAJA-MEDIA) — CERRADO.** `test_traza_punto` y `test_indice_formulas` vuelven a ejercitar el hueco con una entrada de prueba en `SIN_FUNDAMENTO` por `monkeypatch`. Mutante M-N **muerto**.
- **H4 (BAJA) — CERRADO.** Docstrings y comentarios reescritos (M5, `modelos.Verificacion.paso`, `traza_punto`, `indice_formulas`, `M11._paso_ausente`, cabecera de `UMBRALES_DE_VERIFICACION`).
- **H5 (BAJA) — CERRADO.** V4b sin «que es más exigente» (aplicación: «No sustituye a V5…»); el rótulo de la frase del anexo sigue al carácter de la cita (`M11.ROTULO_DE_LA_FRASE_POR_CARACTER`: DEFINICIÓN «describe»); la elección de V4b se imprime como ventana. `test_h5_*`.
- **H6 (BAJA) — CERRADO.** Test con la V8 acotada de `test_t7_verificacion`: su aviso sale UNA vez en el HTML.
- **H7 (BAJA) — CERRADO.** La regla N > 0 vive en el dato (`CombinacionDeEstabilidad.excentricidad_publicable`), que leen la CLI/JSON y M11; «0.8·f_r» de `FISURACION_FRACCION_FR` y el piso de 1.0 in de `RECUBRIMIENTO_MP_PISO_MM`. `test_h7_*`.

Decisiones del dueño aplicadas en las fichas: techos aceptados (T10-01), V9 sin veredicto para catálogo/marco aceptado (T10-03), tercera corrida con hidrología → T-11 (T10-02). Ficha nueva T10-08 con las correcciones. Parte renumerada a **LIII**.

## 4. Tamaño final por punto (método de `test_ext8`, con las declaraciones de la suite)

Expediente: **107.04 KB y 31.00 páginas por punto** (base `2265d90`: 113.99 KB / 32.33). Techos `KB_POR_PUNTO_MAX` 114.5 → **107.5**, `PAGINAS_POR_PUNTO_MAX` 33 → **31.5**. Un punto: 119 páginas (104 en la base; lo fijo crece). Perfil, sin techo: 141.16 KB por punto (149.96 en la base). El objetivo de EXT-8 (< 15 KB, < 10 pág.) sigue sin alcanzarse (T10-01).

## 5. Línea base (comparador de E-B contra `2265d90`)

`informe_expediente.json` e `informe_rama_error.json` IGUALES; `informe_familia_c.json` 8 y `informe_perfil_ancho.json` 6 diferencias, todas `V4b/V6/V9.veredicto` None → 'cumple'; 0 no comparables; `alcance.declarado` nuevo en los cuatro JSON; cinco líneas de alcance en los cinco `cli_*.txt`; formato en las tres memorias de la CLI. `memoria_punto_cajon.html` y los dos CSV de resumen idénticos byte a byte. Las correcciones H1–H7 sólo movieron las tres memorias (formato).

**Diámetros, secciones, materiales y HW movidos: ninguno.**

## 6. Censos y generados

141 criterios / 20 sin valor (sin mover); citas 506 → 507 (`HDS5_3ED.2.2.5d#AGENCIAS`); tres fundamentos (`F5.V4b`, `F5.V6`, `F5.V9`); `SIN_FUNDAMENTO` vacío; ninguna marca `literal-ok` nueva. Generados resellados con el par medido (`indice_formulas.md`, `manifiesto_citas.md`, `manifiesto_registro_normativo.md`, `trazabilidad.csv`). `CLAUDE.md`: párrafo de T-10, `collected` 6360, tabla de pares, cadena de totales, recuento de `pdf` (145) y la nota de las dos corridas de referencia del índice.

## 7. Diferidos (Parte LIII)

T10-01 tamaño (objetivo de EXT-8 no alcanzado; formato impreso resumido por decidir) · T10-02 hidrología calculada fuera del índice (→ T-11) · T10-03 V9 sin juicio con tope [A] · T10-04 tres textos con otra vista · T10-05 alcance declarado · T10-06 el anexo no recalcula (el barrido sigue siendo PF-3) · T10-07 aceptación no escrita en rojo primero · T10-08 correcciones de la auditoría.

## 8. Lo que T-11 y T-12 deben saber

- **T-11**: añadir la corrida con la hidrología de prueba (`tests/fixtures/hidrologia/`) como tercera entrada de `indice_formulas.CORRIDAS_DE_REFERENCIA` (ficha T10-02) y regenerar `docs/indice_formulas.md`; `test_dimensional_piloto` conserva su corrida propia y no debe migrarse sin remedir su censo. Todo paso nuevo que emita un módulo entra en la memoria por `bloque_pasos` sin tocar M11; todo número nuevo del JSON tiene que aparecer en su FILA (el censo por clave de `test_t10_memoria` lo pide), y todo texto nuevo del JSON que la memoria no lleve rompe el censo de textos.
- **T-12**: el formato impreso (memoria por punto + anexo digital, págs. 110–122 del PDF guía) es decisión pendiente del dueño (T10-01); los techos de `test_ext8` están pegados a la medida y cualquier crecimiento los rompe a propósito. `modelos.ALCANCE_DECLARADO` es la lista de lo que el expediente declara no hacer: si T-12 cierra alguna de esas fichas, hay que quitar su entrada.
- Push de la rama: `tesis/T-10` en el remoto sigue en `3f1ee53` (historia de la FASE A); el commit integrado está en `main` y en `tesis/T-10-final`.
