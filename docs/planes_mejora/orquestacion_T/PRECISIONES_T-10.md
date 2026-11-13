# Precisiones del orquestador para T-10 (memoria M11 completa) — cuarta sesión

Base: `origin/main` con T-7c integrado (el orquestador te da el SHA). SIN CAMBIOS DE CÁLCULO: si para imprimir algo hace falta
un número que ningún módulo emite, el módulo de cálculo lo EMITE como `PasoDeMemoria` (sin cambiar ningún resultado) y M11 lo
formatea; M11 no hace aritmética sobre magnitudes (test por AST). Lee `ORQ/ORQUESTACION.md` (con su ENMIENDA DE LA CUARTA SESIÓN),
los informes finales de los prompts que alimentan la memoria (`ORQ/INFORME_T-3_final.md`, `-T-5_final`, `-T-7a_final`,
`-T-7b_final`, `-T-7c_final`, `-T-8_correcciones`, `-T-9_final`: mira en cada uno qué pasos y datos emite y qué dejó «para
T-10») y la sección «Cuarta sesión» de `ORQ/DECISIONES_DUENO_2026-11-12.md`.

- **IDs canónicos** (el número del INFORME, no el del prompt): «INF-3.4 "memoria"» es la fila **`INF-3.4.7`**; `INF-4.7`; y lo
  que el prompt llama `INF-5.1.9` es **`INF-5.1.10`** (la cita del control gobernante y el índice de fórmulas; T-0 ya corrigió la
  cita: a ti te toca que el índice regenerado la muestre en una corrida que dimensione). El `INF-5.1.9` canónico es
  `sucs_fundacion` (lo cerró T-4): NO lo toques. Hoja `Hallazgos` sólo lectura hasta la integración.
- **Punto 1 (secciones)**: muchas ya existen porque cada prompt imprimió lo suyo. Tu trabajo es el CENSO: recorre la memoria de
  una corrida que dimensione los cuatro puntos y de una de expediente con los datos de prueba del cabezal (los de T-7b/T-7c,
  rotulados) y lista, fase por fase, qué resultado del JSON/CLI NO tiene paso con fórmula sustituida en el HTML (el prompt nombra
  L, caída, cota de salida, G2, V4b, V6, V9; añade lo que encuentres de la hidrología, Fase 8, Fase 9 —geometría, aleros, tabla
  de cargas con brazos y momentos, e, q, φR frente a ΣγQ y FS del marco ASD en paralelo, armado por elemento—, protección y
  espaciamiento). Lo que falte se cierra emitiendo el paso desde el módulo. Test que lo fije: todo valor que la CLI/JSON publica
  de un punto dimensionado aparece en su bloque del HTML (por clave, no por texto libre).
- **Punto 2**: la cadena sísmica y cualquier otro bloque que CLI/JSON imprimen y el HTML no: una sola fuente (el dato del
  informe), tres vistas.
- **Punto 3 (índice de fórmulas)**: la corrida de referencia debe dimensionar los cuatro puntos. Usa los datos externos que YA
  existen en `tests/` (la corrida de la guía de perfil; `tests/fixtures/`), rotulados como de prueba; NO inventes valores nuevos
  de entradas. B-01 dimensiona en la corrida de la guía (no con TW = 1.00 m). Para la Fase 9 (expediente), los datos de prueba de
  T-7b/T-7c. Di qué corrida usa el índice y por qué.
- **Punto 4 (anexo de sensibilidad)**: todo [A] nuevo de T-1…T-9 con ventana y en el anexo; un test lo fija por barrido de
  `criterios_adoptados` (etiqueta [A] con valor ⇒ `sensibilidad` no vacía y aparece cuando se usó). No ejecutes barridos PF-3
  dentro de la memoria: el anexo imprime la ventana y la resolución, no recalcula.
- **Punto 5 (tamaño)**: hoy la memoria mide ≈ 114 KB y 32 páginas por punto (techos de `tests/test_ext8_*`), lejos del objetivo
  de EXT-8 (< 15 KB / 10 páginas, que ya entonces no se alcanzó: ficha EXT-8-01). No recortes contenido sustentado para cumplir
  una cifra: MIDE por fase cuánto pesa cada bloque, quita lo que esté repetido (citas y fichas impresas más de una vez, pasos
  idénticos por punto que puedan ir una vez en un anexo común con ancla), y documenta en una ficha por qué el objetivo no es
  alcanzable sin perder sustento, con la medida antes/después. Los techos se REMIDEN y se dicen; no se relajan a ojo.
- **Avisos**: todo aviso de `InformePunto.avisos()` sale en las tres vistas; los veredictos INDICADOR se pintan como aviso; las
  verificaciones «no evaluadas» / «método no evaluable» / «espera dato» se distinguen de CUMPLE y de NO CUMPLE también en el HTML.
- **Lo que el dueño decidió y la memoria debe decir como ALCANCE DECLARADO (no como omisión)**: el armado de la SECCIÓN del
  marco de la Familia C no se diseña (basta el dimensionamiento; T-5 entrega la demanda); el cabezal paralelo a la vía del marco
  está diferido; la iteración del ancho de zapata está diferida al EMS real; V7 del marco no pesa el concreto (ficha T3-08);
  las Figuras 3.3–3.4 de HEC-14 se digitalizarán después de la cadena.
- **GUI**: no la amplíes (sin Tk en el contenedor no se puede probar la ventana real); si un exportador de la GUI comparte código
  con lo que tocas, que siga funcionando (tests de contrato por AST).
- PARADA (c): ningún diámetro, sección, material ni HW se mueve; la línea base cambia sólo por FORMATO (clasificado con el
  comparador de E-B y `diff`). Las memorias HTML de la línea base se regeneran.
