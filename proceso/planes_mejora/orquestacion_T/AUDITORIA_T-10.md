# AUDITORÍA ADVERSARIAL CORTA de T-10 (FASE A): memoria M11 completa

Auditado sobre `/home/user/wt/T-10`, árbol `3f1ee53` frente a la base `2265d90`. Solo lectura: no edité el repo ni hice commits. **No creé `AUDITORIA_T-10.md`**: una regla del entorno me prohíbe escribir archivos de informe, así que el informe completo va aquí.

## Resumen

**Veredicto: AJUSTADO.**

**¿Cambió algún cálculo?: no.** Lo comprobé por el diff de `M5`, `M7`, `servicio` y `cli`, con el comparador de E-B y con un diff crudo del JSON, en la línea base y en las dos corridas de referencia ejecutadas con el código base y con la rama. Lo único que se mueve es `V4b/V6/V9.veredicto`, que pasa de None a `'cumple'`. `estado` y `cumple` no cambian, el RESUMEN de la CLI es idéntico, los CSV de resumen y `memoria_punto_cajon.html` son idénticos byte a byte, y todos los números del cabezal y del armado coinciden.

Hallazgos: 2 MEDIA, 5 BAJA.

Los dos más graves:
- **H1 (MEDIA).** El censo «por clave» en realidad busca texto libre en todo el bloque, con 2, 3 o 4 decimales. «0.40» aparece 99 veces en A-01. Cuatro mutantes sobreviven a todo `test_t10_memoria.py`: quitar la última fila de la tabla de armado, vaciar la columna de excentricidad, imprimir el valor en vez de la ventana en el anexo A.4 e imprimir K_A = K_AE.
- **H2 (MEDIA).** El paso 7.B.3b atribuye su fórmula de reparto a HDS-5 núm. 2.2.4 b. (pág. 2.8) mediante `formula_cita_id`, y no lleva la nota del 7.B.3 que aclara que el álgebra es del proyecto. La memoria afirma más de lo que dice la fuente.

## Hallazgos

### H1 · MEDIA · El censo JSON↔HTML no es «por clave» y deja vivos mutantes reales
- **Qué pasa.** `test_todo_numero_del_json_de_un_punto_dimensionado_esta_en_su_bloque` recorre las claves del JSON, pero da por bueno cualquier formato (`_formatos`: `.2f`, `.3f`, `.4f`) que aparezca en cualquier lugar del texto plano del punto, enlaces incluidos. El test de textos hace lo mismo con subcadenas.
- **Colisiones medidas.** En A-01 (expediente) las excentricidades a 2 decimales aparecen entre 2 y 99 veces fuera de su columna.
- **Mutantes que sobreviven a los 33 tests.** Script en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-10-aud/mutar.py`, que corre sobre una copia del árbol:
  - M-A: `for f in a.tabla:` → `a.tabla[:-1]` en `M11._bloque_armado`. Sobrevive porque «aleros: armadura horizontal» y 300.00 aparecen en otros sitios.
  - M-E: la columna `e (m)` de `_bloque_cabezal` vacía.
  - M-L: el anexo A.4 imprime `c.valor` en vez de `c.sensibilidad` (en `anexo_sensibilidad`).
  - M-M: `K_A` se imprime con el valor de `K_AE` (en `bloque_cabezal_proyecto`).
- **El bloque de proyecto no está censado.** De `cabezal` solo se comprueban la cadena y las notas; recubrimientos, cuantías, Mononobe-Okabe y `por_punto` no se comprueban.
- **Mutantes que sí mueren:** quitar 7.B.3b, quitar las filas del CSV, vaciar el alcance de la norma de producto, quitar `origen_aporte`, quitar un aviso, quitar las solicitaciones, quitar el rótulo de bloqueo.
- **Por qué importa.** Contradice PRECISIONES («por clave, no por texto libre») y la ficha T10-04.
- **Corrección.** Comparar cada entrada de `cabezal.armado[].tabla[]` y `secciones[]` con su fila, localizada por `elemento`/`posicion`, usando el `FMT` con que M11 la imprime. Fijar `combinaciones[].excentricidad` en su columna. En el anexo, exigir `_valor_legible(c.sensibilidad)` en la fila de cada clave. Censar los números de `bloque_cabezal_proyecto`.

### H2 · MEDIA · La fórmula del 7.B.3b se atribuye a HDS-5 2.2.4 b.
- En `M7_geometria.longitud_del_conducto`, `paso_reparto` lleva `formula_cita_id="HDS5_3ED.2.2.4#LONGITUD"`, una cita con carácter APROXIMACIÓN («…culvert length are approximate…»), y no tiene `nota_del_proyecto`.
- La memoria imprime «H_salida = H_salida0 + S·L ; … L_salida = L − L_entrada — núm. 2.2.4 b. · pág. impresa 2.8». HDS-5 no escribe esa fórmula.
- El 7.B.3 sí aclara: «la expresion cerrada es su algebra y la hace el proyecto». Es la misma clase de defecto que INF-5.1.10.
- **Corrección.** Quitar `formula_cita_id` del 7.B.3b, o ponerle la misma nota del proyecto que al 7.B.3.

### H3 · BAJA-MEDIA · Al vaciar `SIN_FUNDAMENTO`, el camino del hueco de `traza_punto` quedó sin ejercitar
- `test_indice_formulas.py::test_hueco_censado_construye_la_misma_ficha_que_la_traza` recorre ahora un censo vacío. Se volvió vacuo **sin declararse**: no está entre los seis tests reescritos.
- El bucle de `test_traza_punto::test_las_verificaciones_sin_paso_llegan_como_hueco_censado` también es vacuo.
- Mutante M-N, un `raise` dentro de `traza_punto._hueco`: sobrevive a `test_traza_punto`, `test_indice_formulas`, `test_memoria_sustentada`, `test_t10_memoria` y `test_cierre_c10` (104 passed).
- **Corrección.** Aplicar a esos dos tests el mismo `monkeypatch` de `F.SIN_FUNDAMENTO` con una entrada de prueba que ya usa `test_memoria_sustentada`.

### H4 · BAJA · Docstrings y comentarios que ahora contradicen el código
- `M5.v6_material_solido_arrastre`: «NO LLEVA `PasoDeMemoria`… censada en SIN_FUNDAMENTO bajo F5.V6».
- Comentario en `M5.v4_carga_entrada`: «La que nombra -- V4b -- no emite `PasoDeMemoria`».
- `modelos.Verificacion.paso`: «V4b, V5, V6, V8 y V9» como censadas.
- Docstring del módulo `traza_punto`: «(V4b, V5, V6, V8, V9)».
- Docstring de `indice_formulas`: «(V4b en esta corrida)».
- Comentario T-10 en `UMBRALES_DE_VERIFICACION` («NINGUNA cita fija el numero»): es falso para V9 del tubo, donde la cita sí fija el número.
- **Corrección.** Reescribirlos en el mismo commit. Es la clase de defecto SIS-A-03.

### H5 · BAJA · El umbral de V4b se imprime con más fuerza de la que tiene
- En el anexo, el umbral 1.5 aparece bajo «Frase que lo fija: núm. 2.2.5 d.». Esa frase describe la práctica de agencias de EE. UU. y no fija el 1.5. Va contra el espíritu del conflicto #1 y de NOR-HDS-02.
- El texto añade «V5, que es mas exigente», algo que el cálculo no establece.
- La elección imprime «Elegido entre: 1.2, 1.5» para lo que es una ventana, no dos opciones.
- Verifiqué la cita nueva contra el PDF y es literal: hif12026, PDF 72, pág. impresa 2.10, ítem d.
- **Corrección.** En `UMBRALES_DE_VERIFICACION` V4b, quitar «que es mas exigente». En `M11.anexo_referencias`, poner un rótulo según el carácter (DEFINICIÓN → «frase que describe»). En la `EleccionDeProyecto` de V4b, escribir `entre` como ventana.

### H6 · BAJA · Los `Verificacion.avisos` de `2265d90` no se ejercitan
- Ninguna de las dos corridas produce un aviso de V8 (medido: 0 por punto). La afirmación del informe «el test de avisos en tres vistas lo cubre» es vacía para ellos.
- El mecanismo sí está bien: `servicio.InformePunto.avisos` los incluye y `_avisos_que_faltan` los imprime si no salieron.
- **Corrección.** Un test con la V8 acotada de `test_t7_verificacion` que compruebe que su aviso sale una vez en el HTML.

### H7 · BAJA · Textos de presentación duplicados
- La regla `k.N > 0` de la excentricidad está escrita dos veces, en `cli` y en `M11._bloque_cabezal`. Lo correcto sería que viviera en `CombinacionDeEstabilidad`.
- «0.8·f_r» (en `_bloque_armado`) y «piso de 1.0 in», copiado de la CLI, son cifras escritas en el texto. Si cambian `FISURACION_FRACCION_FR` o `RECUBRIMIENTO_MP_PISO_MM`, el texto se queda desfasado.

## Comprobado y no refutado

1. **Cálculo.** La rama no cambia ningún valor, condición ni orden de evaluación:
   - `cumple` es la misma expresión en V4b, V6 y V9.
   - `_veredicto` solo da CUMPLE o NO_CUMPLE, coherente con `estado` (lo exige `Verificacion.__post_init__`).
   - V9 sin umbral (marco o catálogo) da `veredicto` None y el `estado` sale de `cumple`.
   - No hay excepciones nuevas: los Magnitud tienen procedencia y todas las citas existen.
   - El 7.B.3b no tiene veredicto, así que no cuenta en `con_aviso` ni en los indicadores.
   - El comparador da IGUALES en `informe_expediente` e `informe_rama_error`. En `familia_c` (8), `perfil_ancho` (6), `perfil_guia` (11) y `expediente_cabezal` (3), todas las diferencias son de veredicto. Más `alcance.declarado`, que el comparador no mira.
   - Los dos CSV y la memoria del cajón son idénticos. En la CLI solo se añaden las líneas del alcance.
   - Recomputé a mano el 7.B.3b de A-01: L = 18.0/0.9539 = 18.870; H_s = 2.213; proyección = 8.626; L_entrada = 9.318; L_salida = 9.551. Coincide.
2. **M11.**
   - No hay operaciones aritméticas nuevas. La única comparación es el `k.N > 0` de presentación.
   - Las lecturas de `ca` son estáticas y están en `LECTURAS_ESTATICAS`.
   - `M2.alcance_norma_producto_de` es pura.
   - `_YaImpreso` es estado de presentación (ContextVar) y solo actúa dentro de `memoria_html_por_partes`.
3. **Anclas y sustento.**
   - Anclas rotas: 17 → 0 en perfil y 15 → 0 en expediente.
   - Ningún `id` de cita, fundamento o umbral se pierde, y ningún literal «…» se pierde.
   - Ningún código de paso distinto desaparece: solo se sustituyen los tres huecos.
   - A-01 pasa de 216 a 167 pasos por la deduplicación de objetos idénticos del armado.
   - Los techos (107.5 KB y 31.5 páginas) quedan pegados a la medida y el dueño los aceptó.
4. **Alcance declarado.** Coincide con las fichas T5-07, T7A-03, T7B-09, T3-08 y T8-08 y con las decisiones del dueño (cuarta sesión). DC = 0 en V7 es efectivamente del lado seguro. No hay verbos de obligación nuevos.
5. **Índice de fórmulas.** Las dos corridas usan datos de prueba ya existentes, y los tests los comparan con la guía y con T-7c. `n_celdas_cajon` = 1 en el archivo equivale al `--declarar` de la guía. La fila 4.4 cita «núm. 3.3.5 · pág. impresa 3.25». No hay entradas inventadas.
6. **Conflictos.** El #1 (V4b) se respeta en lo esencial: carácter DEFINICIÓN y verbo DEFINE, `[A]` intacto; el matiz es H5. El #8 (Clase F) no se toca: la memoria imprime las filas C, D y E que la CLI ya publicaba.

Scripts y salidas de esta auditoría en `/tmp/claude-0/-home-user-Proyecto-alcantarillas/1cd08434-aed4-5109-98e7-ccedca5437f0/scratchpad/T-10-aud/`:
- `mutar.py`: aplica un mutante sobre la copia del árbol, corre los tests y lo revierte.
- `correr.py` y `memoria.py`: corren las corridas de referencia con el código base y con la rama, y generan su JSON y su memoria.
- `jdiff.py`: diff crudo entre dos JSON.
- HTML y JSON generados: `main-*` y `T-10-*`.