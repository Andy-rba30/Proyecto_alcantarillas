# Cadena de prompts EXT — corrección y evolución tras la auditoría externa del 2026-09-19

**Fuente:** `06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md` (bloque 4, pasos 0–11), que a su
vez integra el informe de auditoría externa (22 hallazgos), sus dos planes (P00–P19 y
E00–E25) y lo medido en la revisión (35 puntos ciegos, 35 refutaciones, 2 evaluaciones
de plan, crítico). Todo lo que estos prompts piden está reproducido sobre `5196dd2`
y anclado por símbolo.

**Cómo ejecutar la cadena.** Un prompt por sesión de Claude Code, en el orden dado.
Cada sesión termina con el ritual de cierre (abajo). No se avanza al siguiente si la
suite no está en verde y el trabajo no está en `origin/main`. Los prompts E-A y E-B
del final son evolución: solo después de cerrar EXT-0 a EXT-11.

**Serie de commits:** `ext(EXT-n): <resumen> — <IDs cerrados>`. Los IDs son los de la
auditoría externa con prefijo `EXT-` (`EXT-A-01`, `EXT-M-03`…) y los `PC-nn` del
dictamen; nunca los prefijos desnudos `A-`/`M-`/`V-`/`G-`, que colisionan con la
auditoría de Sistema.

---

## Reglas comunes (incluidas por referencia en todos los prompts)

- Lee `CLAUDE.md` entero antes de tocar nada. Las cinco etiquetas, los tres archivos
  de valores, `DatoInvalidoError` vs `DatoFaltanteError` vs `LimiteNumericoError`,
  «la memoria la emite el cálculo», «ningún texto literal se transcribe dos veces».
- **La hoja de ruta v8 es la fuente de verdad y la fuente primaria (PDF en `normas/`)
  gana solo con verificación.** Si un cambio contradice la v8, primero se enmienda la
  v8 (EXT-0 lo hace para todo lo conocido); en el punto de uso se declara la
  discrepancia con cita de página; el defecto se reporta contra la hoja.
- **Imports planos.** Los módulos se importan como los importa `conftest.py`
  (`import criterios_adoptados as ca`, `from modulos import M4_control`), nunca
  `src.modulos.X`: `src/` no es paquete y esa vía crea un segundo módulo con otro
  estado (PC-08). Las rutas `src/modulos/X.py` de este documento son rutas de archivo.
- **Un cluster entero por commit; un commit por sesión.** Antes de tocar un objeto,
  consulta la hoja `Conflictos` del tracker (8 filas vinculantes, §6 de
  `hoja_de_ruta_correcciones_v12.md`) y `docs/decisiones_diferidas.md`.
- **Tests primero, en rojo, como aceptación**: `pytest.mark.xfail(strict=True)` con la
  expectativa del invariante o de la fuente, nunca con la salida actual como oráculo.
  Al corregir, quitar el `xfail`. La suite no usa `xfail` hoy: introdúcelo así.
- **Guardias con la forma MAT-D13**: condición en positivo y negada (`not x > 0`),
  umbral nombrado (nunca `!= 0` ni `==` entre floats), mensaje que nombra el dato o el
  par culpable. Rechazo en la puerta de declaración = `ValueError` (contrato SIS-E-05);
  rechazo en el consumidor = `DatoInvalidoError`.
- **No inventes valores**: si falta un criterio o un procedimiento, entrada con
  `valor=None`, etiqueta `[A]`, `nivel`, `sensibilidad` si es de perfil, y
  `CriterioPendienteError`. Ningún literal nuevo fuera de `constantes_normativas.py`,
  `criterios_adoptados.py` y `datos_sitio.py` (`tests/test_sin_literales.py` lo
  rechaza; `# literal-ok: <razón>` solo para fórmulas transcritas).
- **Ritual de cierre** (obligatorio): (1) suite entera verde, `passed + skipped =
  collected` (hoy 1982); (2) regenerar los cuatro documentos generados si tocaste
  citas, criterios, memoria o pasos: `python3 -m src.normativa.manifiesto --escribir
  --suite "<par>"` y `python3 src/indice_formulas.py --escribir --suite "<par>"`;
  (3) actualizar Estado/Responsable/Commit en la hoja `Hallazgos` de
  `docs/auditorias/matriz_cruzada_auditorias.xlsx` (openpyxl preautorizado); (4)
  registrar en `docs/decisiones_diferidas.md` lo que se difiera, con símbolo; (5)
  fusionar a `main`, empujar, medir el par sobre `origin/main` y escribirlo en el
  commit; (6) si el par cambió, actualizar la tabla de cuatro entornos de `CLAUDE.md`.
- Al terminar, devuelve: qué IDs cerraste (entero / en parte / no), qué tests nuevos
  hay, qué números de la línea base se movieron y por qué, y qué quedó diferido.
  Detente ahí; no ejecutes el prompt siguiente.

---

## EXT-0 · Gobernanza y hoja de ruta (documental, sin código)

```text
Ejecuta únicamente EXT-0 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Lee antes docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md entero: es la especificación de esta cadena.

1. Tracker. Da de alta en la hoja Hallazgos del .xlsx los 22 hallazgos de la auditoría externa con prefijo EXT- (EXT-A-01 … EXT-G-03) y los 35 puntos ciegos PC-01 … PC-35 del dictamen, con severidad reevaluada, cluster, vínculo a los vecinos ya cerrados (NOR-HDS-05, SIS-A-18, SIS-B-22, C5-02, MAT-O10, MAT-D1, R95-031) y Estado «Abierto». Cruza además docs/auditorias/temario_refutar_95.json y temario_refutar_48.json contra la hoja: todo ítem con severidad ALTA/CRÍTICA cuyo hallazgo_id no tenga fila de estado recibe una fila propia (empieza por R95-031 / H-13, la cuantía vertical de E.060 11.10.10.3).

2. Hoja de ruta v8 (docs/hoja_de_ruta_alcantarillas_v8.md). Enmienda, con nota de corrección al estilo de las de D9 y citando la página del PDF verificada en el dictamen: §1.3 («V4 y V4b, las únicas que dependen del TW» es falso bajo TW ahogante); §4.1 y las filas V1/V2 de la tabla de Fase 5 (el tirante y la velocidad que se comparan salen del régimen del barril, no del uniforme; V1 y V2 son [N] en el deber de verificar y [A] en el valor 0.75 / 0.25 m/s aplicado como umbral duro, porque la fuente dice «se recomienda», MC-HHD págs. impresas 76-77 y 79); §4.3 (transcribir completa la frase de HDS-5 pág. 3.24 que hoy está elidida sin marcar: «If a more accurate headwater is necessary, backwater calculations (Section 3.5) should be used…», y decidir por escrito que HW/D < 0.75 bajo control de salida es «método no evaluable» diferible en perfil y no en expediente, no un aviso); §4.2 (la rama no sumergida en q* = 3.5 se evalúa con el H_c del caudal que corresponde a q* = 3.5); §9.2 (el empuje estático usa el Ka de Coulomb de MP 2.4.4.1.5.3, pág. impresa 136, que se reduce a tan²(45−φ/2) con ángulos nulos); §9.4 (añadir 11.10.10.2 y 11.10.10.3 con la ec. 11-32 y su tope, pág. 104, y la pregunta de aplicabilidad del §11.10.2, cortante en el plano); fila V5 (de «[N] DG-2018 + Ley 29338» a: requisito jurídico [N] con DG-2018 §304.07.02 y Tabla 304.09 + método hidráulico [A] + dato de sitio [S] ancho_derecho_via_m); «pág. 75» → 76-77 en V2; «pág. 178» → 179 en §espaciamiento; y el «+9.6 %» de fricción reescrito como «×1.477 sobre el término (+47.7 %), que en CP-8 sube H de 0.4977 a 0.5455 m (+9.6 %)» también en la línea 527.

3. Constantes de texto que repiten la v8: corrige H_O_CONDICION_TEXTO (frase elidida) y anota en el bloque de H_O_CONDICION_APLICACION que «M5 no cambia» era falso (M-01 lo refuta).

4. Reabre con el argumento nuevo las fichas NOR-HDS-05 (bloqueo vs aviso), C5-02 (pasa de limpieza a defecto por V-02), SIS-B-22 (abrir sesión es el caso de uso de limpiar_valores_dinamicos) y NOR-HID-02 (cierre incompleto: NUMERAL_FASE_10 sigue en 178), en el tracker y en decisiones_diferidas.md.

5. Registra en decisiones_diferidas.md la decisión «un expediente por repositorio; multi-obra es requisito de producto» (V-01) y la de mantener las seis fichas de ayuda externa vacías o llenarlas (G-03), con su argumento.

No toques código ni tests. Regenera los manifiestos si alguna cita cambió. Ritual de cierre.
```

## EXT-1 · Guardias locales sin cambio de contrato (cluster «entradas»)

```text
Ejecuta únicamente EXT-1 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra en un solo commit: EXT-A-03, EXT-V-03, EXT-V-06, EXT-V-04, EXT-V-05, EXT-V-02, PC-01, PC-02, PC-05, PC-28, PC-32, PC-33, PC-34, PC-35. Ningún número de la línea base debe moverse.

Escribe primero los tests de aceptación en rojo (xfail strict) y luego corrige:

- M2_material.progresion_de_cajon: rechazar con DatoInvalidoError(CRITERIO_SECCIONES_CAJON, …) todo par (B,H) que coincida con uno anterior dentro de TOL_UMBRAL_NORMATIVO (adyacente, no adyacente y casi-duplicado 5e-10). MD.disenar_material: guardia de progreso (si siguiente_seccion devuelve _misma_seccion que la actual o ya visitada, ErrorProyecto, nunca bucle). No cambies la API por valor ni ordenes la serie.
- M2_material.espesor_pared: un validador único para las dos ramas (Real y no bool, finito, `not t > 0` → DatoInvalidoError con el campo de cada forma; `return float(t)`), conservando el orden Pendiente → Faltante material → Faltante fila → Inválido. Parametriza -0.1, 0, True, -0.0, inf.
- M1_clasificacion._riesgo_del_propietario: validar Mapping exterior, claves de fila ∈ CategoriaTR, campos ∈ {R, n}, reales finitos no bool; clave desconocida o errata → DatoInvalidoError con ruta (hoy se ignora en silencio y la memoria imprime «DECLARADOS POR EL PROPIETARIO» con los valores por defecto).
- criterios_adoptados: (a) rechazar en establecer_valor_dinamico toda escritura sobre un criterio con resolucion Derivada (ValueError, «se deriva de <de>; edite sus entradas»), y actualizar el docstring «DE CUALQUIER CRITERIO» y el test «mismo rasero por los tres caminos»; (b) sensibilidad estructurada {campo: (min, max)} para criterios de valor dict (empieza por seccion_receptor): exigir dict, rechazar claves desconocidas y faltantes, _es_real por campo, rango por campo; (c) para pares (min, max) exigir len == 2 y orden (n_manning_hdpe: hoy (0.013, 0.010) pasa y aprueba un HDPE que el par nominal descarta); (d) modelos.Material.__post_init__ con `not n_min <= n_max` → DatoInvalidoError; M2.catalogo convierte forma mala del par en DatoInvalidoError (hoy un escalar tumba la corrida entera).
- M4_control.perdida_carga y ke_declarado: ke real, finito, `not ke >= 0` → DatoInvalidoError (Tabla C.2: 0.2–0.9). Dar a ke_entrada, v_max_tmc y v_max_hdpe la ventana de la tabla de la que salen, para que _verificar_sensibilidad los cubra. En declaracion.declarar_desde_tabla, cuando se nombra una fila y una columna con celda escalar, guardar valor_de_la_celda en Procedencia y, si valor != celda, exigir nota o rechazar; M11 imprime «DIFIERE de la celda (0.5)» en vez de «proviene de esa fila». Ejecuta C5-02 (ke_entrada como clave de fila de KE_HDS5_C2, como ke_entrada_cajon) si cabe en la sesión; si no, déjalo declarado para EXT-6.
- M3._validar_parametros y M4._validar_positivo a la forma MAT-D13; control_salida valida `not TW >= 0` y guardia de finitud a la salida (LimiteNumericoError nombrando el par).
- MD.disenar_punto: acumular DatoFaltanteError de todos los candidatos y relanzar el primero (con campo) en vez de DisenoNoFactibleError con campo=None.
- M7: guardia de salida en factor_esviaje / longitud_conducto (LimiteNumericoError con umbral nombrado; 89.9° da 10 313 m hoy). cli._numero_externo: excluir bool. cli.declarar_criterios: «0,5» no puede declarar la tupla (0, 5) en silencio. cli --plantilla inexistente o sin marcadores: ErrorProyecto o FileNotFoundError capturado, sin dejar el JSON a medias.

Ritual de cierre. Reporta por ID.
```

## EXT-2 · Multicelda y transición (cluster hidráulico A)

```text
Ejecuta únicamente EXT-2 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-M-03, EXT-M-04, PC-06 y PC-19 en un commit. Prerrequisito: EXT-0 (v8 §4.2 enmendada).

Tests de aceptación en rojo primero: (a) MD.disenar_material con marco 2.00×1.50, N=3, Q=9, S=0.004, L=24, TW=0 produce HW_salida 1.045982117 m y control de salida, y `resultado.Q_celda_m3s == 3.0`, `Q == 9.0`; mutación que devuelva Q total a resolver_control debe romperlo (monkeypatch registrando el Q recibido). (b) control_entrada Forma 1 con D=0.90, S=0.005, concreto, q*=3.75 → HW = 1.107921425 m (media exacta de los extremos); linealidad (segundas diferencias nulas en la ventana); continuidad en 3.5 y 4.0 se conserva. (c) tirante_normal del marco 2.00×1.50 con Q=8.0 m³/s → None (hoy devuelve y/H = 0.85 en la banda 7.70–9.64 donde el marco va a presión).

Corrección: MD pasa Q_barril a resolver_control (mejor: el reparto dentro de M4 con celdas=numero_de_celdas(material), para cerrar también el camino normal is None). ResultadoHidraulico gana Q_celda_m3s y numero_celdas con default (Q sigue siendo el total: sus tres lectores lo imprimen como caudal del punto); PasoDeMemoria del reparto colgado del paso «Número de celdas» (F3.CELDAS existe); el paso de Manning imprime el Q con que M3 resolvió de verdad; cita HDS-5 §5.4.3 (PDF 151) al registro como sostén de la regla vinculante #3. V6 sigue rechazando N > 1 hasta que exista test multicelda de punta a punta: cámbiala solo en el mismo commit que este contrato.
Transición: Q_lo = Q_LIM_NO_SUMERGIDO·A_llena·√D/Ku, H_c_lo = tirante_critico(Q_lo).H_c, solo Forma 1; reescribir test_la_interpolacion_reproduce_la_recta_entre_los_dos_extremos con H_c(Q_lo); llevar al paso F4.CONTROL los dos extremos y Q_lo/H_c_lo; dorado 1.107921425 en casos_patron (CP5) calculado a mano; precisar la justificacion de metodo_transicion_hds5. tirante_normal: comparar con Q_lleno (radio_hidraulico_lleno) en las dos formas y devolver None si Q >= Q_lleno.

Regenera la línea base de Familia C con regenerar.sh y declara archivo por archivo qué se movió (A-01: −0.306 mm de HW_entrada); añade a entradas_ampliadas.json una fila con TW > D y a punto_cajon.py n_celdas_cajon = 3, y anota en el README las mutaciones que la línea base no ve. Ritual de cierre.
```

## EXT-3 · Régimen del barril y dominio del método (cluster C06)

```text
Ejecuta únicamente EXT-3 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-M-01, EXT-M-02, PC-04, PC-27 (mitad compuerta) y la mitad JSON de SIS-B-18 en un commit. Prerrequisitos: EXT-0 (v8 §1.3/§4.1/§4.3 enmendadas, NOR-HDS-05 reabierta) y EXT-2. Usa plan mode: es la sesión más delicada de la cadena.

Tests de aceptación en rojo: (a) caso ahogado D=0.90, Q=0.05, S=0.005, L=20, TW=1.2, concreto: V2 no cumple (velocidad en el conducto lleno Q/A_llena = 0.0786 m/s < 0.25) y V1 no cumple (sección llena, MC-HHD pág. 79); el punto no sale «dimensionado» sin bloqueo. (b) caso Q=0.3, TW=0: HW/D_salida = 0.589 < 0.75 → el punto no cierra como «sí» en expediente; en perfil queda diferido con motivo «método no evaluable (HDS-5 3.24, Sección 3.5)»; nunca DisenoNoFactibleError ni Verificacion(cumple=False) (subir D solo empeora HW/D). (c) caso subcrítico con salida libre (Q=0.3, S=0.001): la velocidad que recibe M6 es la de salida por HDS-5 3.1.6 (1.508 m/s), no V_erosion (1.184). (d) el bloque h_o entero (HW_sobre_D_salida, h_o, TW, ahogado_por_TW, banderas) aparece en informe_json y en cli.volcar.

Corrección: M4.resolver_control emite el régimen del barril (lleno cuando TW ≥ D o HW ≥ D con salida sumergida; parcialmente lleno en otro caso) y la velocidad de salida por HDS-5 3.1.6 (área a min(D, max(TW, y_c))) como Magnitud con procedencia, sin tocar control_salida. M5: V2 compara la velocidad de la sección efectiva; V1 a sección llena no cumple con cita a pág. 79; bajo control de salida parcialmente lleno V1/V2 quedan pendientes por la vía Bloqueo (diferible en perfil, no en expediente) hasta el perfil de lámina: no inventes criterio de llenado. h_o fuera de rango → Bloqueo «método no evaluable» leído por cli._verificador_perfil / correr_punto; el PasoDeMemoria y la compuerta consumen el mismo objeto (SIS-A-07). M6.proteccion_salida recibe la velocidad de salida bajo control de salida y la de tirante normal bajo control de entrada. Mueve cli.Bloqueo a modelos.py con `tipo` como Enum.

Actualiza los tres tests del corredor (test_cierre_perfil, test_cli, test_gui_contrato: B-01 pasa a «dimensionado con HW no evaluable/diferido»), añade a casos_patron el dorado cerrado del régimen lleno (Q/A_llena es aritmética de la fuente, no un dorado inventado) y regenera la línea base declarando qué se movió (9 de 13 archivos). No implementes el perfil por paso directo aquí: déjalo como EXT-3b, sesión propia con plan mode, siguiendo el paquete I1 de H_O_CONDICION_APLICACION, con dorados solo de flujo uniforme y balance de energía (conflicto #7). Ritual de cierre.
```

## EXT-4 · Contexto de corrida y sesiones (cluster estado)

```text
Ejecuta únicamente EXT-4 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16 y la deuda de la suite (27 accesos a _USADOS) en un commit. Prerrequisito: EXT-0 (SIS-B-22 reabierta). No crees un objeto Proyecto.

Tests de aceptación en rojo: (a) dos corridas en el mismo proceso: la segunda, detenida en Fase 2, exporta 0 criterios usados; (b) declarar tras correr y serializar el mismo Informe da el mismo JSON/HTML (incluida la clave cota_entrada_origen de _geometria_json, hoy duplicada en el literal dict); (c) editar el CSV tras correr: el csv_sha1 exportado es el de la corrida; (d) A declara 2 claves → abrir sesión B vacía deja valores_dinamicos() == {} y procedencias() == {}; una clave de B sin procedencia no hereda la de A; (e) en la GUI (test sin Tk sobre la lógica, y el de ventana real si hay Tk): declarar, quitar, cargar sesión o una corrida fallida invalidan self.informe y apagan los exportadores con motivo; (f) «Etapas bloqueadas» de la GUI == la cuenta de la CLI sobre el mismo Informe.

Corrección: cli.correr vacía ca._USADOS y ds._USADOS al entrar (funciones públicas reiniciar_usos) y al salir captura Informe.contexto: ContextoCorrida (frozen, en modelos.py) con usados, valores efectivos copiados en profundidad, procedencias, declarados en caliente, pisados, csv_sha1 de los mismos bytes que leyó M0 y criterios_sha1. Los 39 sitios de exportación (11 en cli.informe_json/_geometria_json, 2 en cli.volcar, 24 en M11, trazabilidad) leen del contexto; amplía el test AST de M11 a «no llama ca./ds./_declaracion. salvo lecturas estáticas». Quita la lectura en caliente de cota_entrada_origen (el rótulo y la regla salen de g.cota_entrada). restaurar_sesion(estado, *, sustituir=True): candidato validado con _verificar_criterio en seco, luego limpiar_valores_dinamicos() + _PROCEDENCIAS.clear() y volcar solo lo aceptado; devolver retirados; sustituir=False es «Importar decisiones». gui.cargar_sesion valida el esquema entero (tipos de cada clave) antes de tocar un StringVar, repone a '' los externos ausentes, y root.report_callback_exception muestra diálogo. bloqueos_reales() en cli.Informe/InformePunto consumido por CLI y GUI; CriterioBloqueante con `diferido`. conftest: una fixture autouse que haga snapshot/restore de _OVERRIDES, _USADOS, ds._USADOS y _PROCEDENCIAS; retirar los 27 accesos privados de los 9 archivos. Reescribe el docstring de limpiar_valores_dinamicos (SIS-B-22) y la entrada SIS-A-18. Ritual de cierre.
```

## EXT-5 · Forma por criterio y parser GUI–GUI (cluster GUI)

```text
Ejecuta únicamente EXT-5 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-G-01, PC-13, PC-14 y la parte de forma de V-02/V-05/V-06 que EXT-1 haya dejado abierta, en un commit. Si hay red: apt-get install -y python3-tk xvfb para python3.12 y corre los tests de ventana real.

Tests de aceptación en rojo: (a) las dos ventanas devuelven int para '1' y '-3', float solo con separador decimal o exponente, list para '[[1.20, 0.90], [1.50, 1.20]]', ValueError para '[1.2, 0.9'; (b) tras declarar los siete criterios del cajón desde la ventana, C-01 no se bloquea en n_celdas_cajon (afirma cuál es su bloqueo real; hoy el test de ventana es ciego a esto); (c) una cadena no numérica para un criterio numérico sin rango se rechaza en la declaración, no en M2/M4 (hoy 53 de 70 claves aceptan 'cero' y la corrida revienta con TypeError); (d) 'nan' recibe el mismo veredicto al escribir y al declarar.

Corrección: campo Criterio.forma (int | float | str | par_ordenado | serie_de_pares | dict_con_campos | categoria) que _verificar_criterio exige también cuando sensibilidad no es numérica; un solo parser en gui/componentes.py::interpretar_texto_declarado que usan ExpedienteApp._interpretar_valor_declarado y VentanaNormativa._valor_tecleado (conserva la divergencia deliberada con la CLI y su test); política de coma/miles: rechazar '1.200,50'; validar_contra_rango con la forma MAT-D13 (`not x <= tope`); Derivada con cara de solo lectura también en la pestaña 2; ayuda de las seis claves externas derivada de variables_entrada si EXT-0 decidió llenarlas. Ritual de cierre.
```

## EXT-6 · Registro normativo (sesiones N3/N4)

```text
Ejecuta únicamente EXT-6 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-N-02, EXT-N-03, EXT-N-04, EXT-N-01, PC-23, PC-24, PC-25, PC-26, PC-30 y el resto de EXT-G-03 en un commit (o dos sesiones N3/N4 si no cabe). Usa el molde de docs/planes_mejora/prompt_N1_A796.md.

- DG-2018 como Fuente presente: sha1 96ea04423a7e0e7fc44b5cd5d8824d6166a8e816, 285 páginas, paginación MEDIDA (la PDF 199 imprime 198; no asumas Corrida(desfase=1) sin medir), marca de vigencia T1 (RD 03-2018-MTC/14 solo si la verificas), retirarla de FUENTES_AUSENTES; citas 304.07.01, 304.07.02 y Tabla 304.09 (anchos por clase; «+5.00 m del borde de las obras de drenaje») como piso [N] del ancho del derecho de vía; corregir SIN_FUNDAMENTO F5.V5, la ficha de talud_terraplen y la justificacion de remanso_derecho_via («Sec. 4.2 y el DG-2018 exigen la condición» no lo sostiene el texto). Decide si vuelve el RNGIV (DS 034-2008-MTC) borrado en 5196dd2, al que 304.07.01 remite.
- Manual de Seguridad Vial 2017 y Manual de Dispositivos (RD 016-2016-MTC/14): censo PRESENTES_SIN_REGISTRAR con motivo, y un test que liste normas/*.pdf y exija que cada archivo sea Fuente presente o esté censado (T17 solo vigila el sentido inverso).
- Citas nuevas: E.060 11.10.10.2 y 11.10.10.3 (PDF 104) y 11.10.1/11.10.2 (PDF 103); AASHTO M 170M §1.1 y Nota 1 (PDF 1); HDS-5 §5.4.3 (PDF 151) si EXT-2 no la registró. Registro de alcance también para M 36 y A760 (una sola cita cada una, de tablas).
- N-03: norma_producto por (material, forma): para RECTANGULAR un rótulo explícito «sin norma de producto: marco vaciado in situ (ruta_familia_c §14.1); diseño LRFD Sec. 5 y Art. 12.11; construcción EG-2013 503+504; M 259/M 273 ausentes» anclado en el registro (LRFD 12.4.2.4 pág. 12-8 y 12.11.1 pág. 12-68); adaptar cli._diseno_json, el resumen, los tres sitios de M11 y MD._motivo_descarte.
- N-01: partir edicion_que_rige_el_expediente en fuente legal (MP: opción «citada 2016» exige fecha de inicio del expediente y régimen transitorio con acto verificado) y fuentes técnicas; corregir «cuya edición no la manda nadie» (MP-2016 ancla LRFD 2014, PDF 44); Fuente.vigencia de T1-01 con acto_aprobatorio/derogado_por; el criterio sigue vacío y sin consumidor de cálculo.
- Textos: 178→179 en NUMERAL_FASE_10, Espaciamiento.numeral, long_max_cuneta.fuente y test que los compare con MC_HHD_CUNETA.pagina_impresa; F4.MANNING «una geometría con n_max y dos velocidades» (M3 no cambia); M1: la columna «TR de diseño» es de la tabla de la v8 §2.2, no de la Tabla N.º 02; fricción 47.7 %/9.6 % en citas, discrepancias y fuentes.

Regenera manifiesto_citas.md, manifiesto_registro_normativo.md y trazabilidad.csv con sello. Ritual de cierre.
```

## EXT-7 · Cabezal (cluster C07)

```text
Ejecuta únicamente EXT-7 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-M-05, EXT-M-06 y EXT-M-07 en un commit. Prerrequisito: EXT-0 (v8 §9.2/§9.4 enmendadas) y EXT-6 (citas de E.060 11.10.10.x). Nada se cablea a la CLI: M9.FUNCIONES_SIN_CONSUMIDOR y su test siguen vigilando.

- M-05: cuantia_de_diseno con direccion='vertical' y cortante_alto=True DETIENE con CriterioPendienteError leyendo un criterio nuevo (valor=None, [A], NIVEL_EXPEDIENTE, resolucion que nombre hm, lm y ρh requerido por 11.10.10.1) y un criterio de aplicabilidad del régimen de cortante en el plano (§11.10.2; un cabezal en voladizo trabaja perpendicular, §11.10.1 → §11.12): si no aplica, ni 11.10.10.2 ni .3 rigen. Ampliar verificar_cuantia con el mismo argumento; corregir el docstring que afirma lo contrario de la norma; test parametrizado en vertical. No implementes la ec. 11-32: faltan lm y Vu.
- M-06: empuje activo estático y sobrecarga con el Ka de Coulomb de MP 2.4.4.1.5.3 (existe como k_a_coulomb, se reduce a tan²(45−φ/2) con ángulos nulos, diff −5.6e-17), declarando la discrepancia con §9.2 en el punto de uso; conservar ka_rankine para el test límite; bloque de CP9_EMPUJE_TRASDOS con i, δ ≠ 0 dentro de las ventanas (con k_h = 0.5 M-O se agota antes de i = 10°: dilo en la sensibilidad). Alternativa mínima si no se quiere tocar el estático: guardia con umbral nombrado que detenga en condición SÍSMICA cuando |K_A_rankine − K_A_coulomb| supere la tolerancia.
- M-07: EstabilidadCabezal con `exigidas` (derivadas de las claves de constantes_normativas.FS, más E6 si se decide), `__post_init__` que rechace conjunto vacío o código fuera de exigidas (ValueError, patrón EmpujesTrasdos), `estabilidad_interna_cumple`, `estable` solo con todas las exigidas presentes y cumplidas, `pendientes`; verificar_estabilidad registra E4/E5 como pendientes en vez de omitirlas; reescribir los dos tests que asertan `estable` con tres ítems.

Ritual de cierre.
```

## EXT-8 · Rendimiento y GUI no bloqueante

```text
Ejecuta únicamente EXT-8 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra PC-10, PC-11, PC-12 y PC-17 en un commit. Prerrequisito: EXT-4 (contexto de corrida).

Medido: la exportación PDF cuesta 11 s/287 MB (4 puntos), 69 s/1.29 GB (40), 360 s/5.7 GB (200), en el hilo de Tk; el cálculo cuesta 2 ms por punto; la memoria HTML pesa 67 KB por punto con 44 % de texto repetido.

- PDF fuera del hilo de Tk por SUBPROCESO (python3 cli.py --pdf con la sesión serializada y --declarar), no por hilo: aislamiento por proceso, progreso por líneas de stdout, cancelación terminando el proceso, botón apagado con motivo visible y estado terminal claro; conserva el contrato M11.WeasyHTML que la GUI sondea y los tests parchean. Documenta el límite medido en la ayuda del botón y ofrece la vía navegador por encima de un umbral de puntos.
- Memoria: retirar el doble renderizado del paso 2.1 (F2.LUZ) por punto; deduplicar los punteros; y, como decisión explícita frente al criterio de salida §4.4 de hoja_de_ruta_correcciones_v12.md, un anexo único de citas, umbrales y discrepancias con ancla por cita_id al que cada punto enlaza (los textos siguen saliendo de Registro.textos_literales()); construir por streaming. Objetivo: < 15 KB y < 10 páginas por punto, medido después, y solo entonces un test de tamaño por punto.
- Imports: weasyprint perezoso dentro de exportar_pdf (manteniendo el diagnóstico ImportError vs OSError y la sonda weasyprint_disponible), scipy.optimize en el punto de uso, VARIABLES de variables_entrada perezoso; test de presupuesto `import cli` < 0.3 s sin weasyprint, verificado con -X importtime.
- Accesibilidad mínima: rueda en X11/macOS (<Button-4>/<Button-5>, delta normalizado), motivo del botón apagado en un rótulo visible además del tooltip, Escape en las emergentes, Control-Return para ejecutar.

Ritual de cierre.
```

## EXT-9 · Paquete `src/` y servicio de cálculo (E01–E03 fundidas)

```text
Ejecuta únicamente EXT-9 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra PC-08 y las fases E01, E02, E03, E03a, E03b, E03c del plan de evolución en un commit (o dos sesiones si no cabe). Prerrequisitos: EXT-4 y EXT-8.

1. Guardia de identidad antes de mover nada: test que rechace por AST `import src.` fuera de src/normativa y que en subproceso importe cli y compruebe que ningún módulo de src/*.py vive bajo dos claves de sys.modules. Después convierte src/ en paquete real con un solo nombre y retira los cinco sys.path.insert (cli.py, gui/app.py, gui/ayuda_entrada.py, gui/ventana_normativa.py, src/indice_formulas.py) y el de conftest; un solo estilo de import en todo el repositorio; `python -m <paquete>.cli` y `python -m <paquete>.normativa.manifiesto` comparten convención. No crees subpaquetes nuevos (proyectos/, expediente/, hidraulica/…) en esta sesión.
2. Servicio de cálculo: mueve a un módulo propio las 23 funciones de orquestación (696 líneas), los 4 dataclasses (Bloqueo ya está en modelos.py desde EXT-3) y la carga de datos externos (153 líneas) de cli.py; JSON, texto y argparse quedan como adaptadores; cli conserva reexportaciones para los 21 atributos que usa gui/app.py y los 6 privados que usan los tests (_verificador_perfil, _etapa, _numero_externo, _fase_*, _bloqueo, _parser), y se retiran solo cuando los 11 archivos de tests migren. Importar y ejecutar el servicio no inicia CLI ni GUI. Equivalencia medida: mismas entradas resueltas, resultados y contexto por las dos puertas.
3. anticipo (2 atributos), ayuda_entrada (5) e indice_formulas (2) apuntan al servicio; no regeneres el índice de fórmulas aquí (es refactor de imports; el sello exige el par de origin/main).

Ritual de cierre.
```

## EXT-10 · Multi-obra como requisito (V-01, E04)

```text
Ejecuta únicamente EXT-10 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra EXT-V-01 y la fase E04 del plan de evolución en un commit. Prerrequisitos: EXT-4, EXT-9 y la decisión registrada en EXT-0. Usa plan mode.

Primero la enmienda constitucional, porque hoy el repositorio ES un expediente: CLAUDE.md (taxonomía [S]: dónde vive un [S] declarado por sesión) y v8 §0.7 («se declara una sola vez en criterios_adoptados.py»). Después: DatoSitio.nivel; datos_sitio.establecer_dato_dinamico(clave, valor, trazabilidad, fecha) que construya por dataclasses.replace (pasa _verificar_dato, exige trazabilidad no vacía, rechaza Derivada), con registro de uso; --datos-sitio sitio.json en la CLI, hermano de --datos-externos; la sesión (FORMATO_SESION = 3, migración explícita v2→v3, id, csv_sha1, informe_json embebido por corrida, escritura temporal + os.replace) es el único lugar del «proyecto actual»; la memoria imprime de qué archivo salió cada [S] y advierte si --proyecto no coincide con corredor_del_proyecto. Los valores de La Unión SIGUEN en datos_sitio.py y criterios_adoptados.py como valores de archivo (así test_cierre_perfil, test_nivel_medido y las líneas base siguen verdes); un proyecto nuevo se crea cargando una sesión vacía, no vaciando los archivos. Radio medido: la corrida de perfil no lee ningún [S]; la de expediente solo PGA_roca_B; 18 tests en 5 archivos, uno de ellos (test_M11_reporte, `assert c.clave in ca.CRITERIOS`) es un supuesto del test a corregir. Prueba dos obras distintas, una obra vacía y abrir B tras A. Ritual de cierre.
```

## EXT-11 · Propiedades, mutación e higiene de suite

```text
Ejecuta únicamente EXT-11 de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Cierra PC-18 (residuo), PC-20, PC-21, PC-22 y PC-29 en un commit. Consulta antes (regla de dependencias de CLAUDE.md) la incorporación de hypothesis y mutmut como dependencias de TEST en requirements-dev.txt, con la misma justificación que PyMuPDF; si no se aprueban, escribe las propiedades con pytest.parametrize sobre mallas.

Propiedades: Q = V_sedimentacion·A (n_max) en circular y rectangular; Q_total = N·Q_celda a través de MD→M4; V_erosion ≥ V_sedimentacion; continuidad y linealidad de la transición; monotonía de HW(Q) bajo control de entrada Forma 1; tirante_normal = None para Q ≥ Q_lleno; HW(N=3) ≠ HW(N=1). Mutación medida sobre M3–M5/MD y sobre el par (n_min, n_max): reporta el mutation score y fija en un censo lo que sobrevive con razón. Suite: test_anticipo y test_gui_contrato:592 al AST (getsource cuenta comentarios); guardia en test_guardias_de_la_suite contra `getsource(...).count(` / `in read_text()` sin ast.parse; corrida real en concreto para las Fases 6/7/8 de test_cli (hoy un stub HDPE que el producto no puede dimensionar); test_MD: sustituir el skip permanente por una simulación de ausencia real; compartir la corrida de la línea base entre sus dos tests y marcar test_bandera_pdf como lento; censo fijado de funciones públicas sin referencia en tests (16 hoy). Cruce automatizado de temario_refutar_*.json con la hoja Hallazgos como test. Ritual de cierre; actualiza la tabla de cuatro entornos de CLAUDE.md.
```

---

## Evolución (solo después de EXT-0 a EXT-11)

### E-A · Perfil de lámina por paso directo (H00–H02 = la sesión de NOR-HDS-05)

```text
Ejecuta únicamente E-A de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Sesión con plan mode. La especificación YA está escrita: el paquete de cinco piezas del bloque de comentario previo a constantes_normativas.H_O_CONDICION_APLICACION (Ec. 3.7 pág. 3.12/PDF 94; umbrales pág. 3.24/PDF 106; Sección 3.5 PDF 116–120; integrar en M4 desde la frontera max(y_c, TW) ≤ D hacia la entrada con empalme a línea de energía llena). Restricciones: regla vinculante #12 de ruta_familia_c.md §6 (la vía por tirante de Seccion no gana consumidores desde M3/M4 sin declararlos; integra en `llenado` vía geometria_en o declara el consumidor en el censo con su medición de condicionamiento); conflicto #7 (dorados solo con corrida externa citable: hasta entonces, límite de flujo uniforme y balance de energía); tipo nuevo en modelos.py (no ampliar ResultadoHidraulico a ciegas). Primera salida: fracción de longitud a sección llena, que vuelve MEDIDA la primera condición de h_o; segunda: HW por remanso bajo HW/D < 0.75, que deshace la circularidad que hoy clasifica como salida un barril supercrítico; con eso V1/V2 dejan de estar pendientes bajo control de salida parcialmente lleno (EXT-3). Cierra NOR-HDS-05 entera, regenera los cuatro generados con sello. Ritual de cierre.
```

### E-B · Editores tipados, comparador e histórico (E10, E14, E13 reducido, E21 acotado)

```text
Ejecuta únicamente E-B de docs/planes_mejora/07_CADENA_PROMPTS_EXT.md y aplica sus reglas comunes. Una sesión por letra si no cabe. (E10) Editores de escalares, pares, series de pares y dicts con campos sobre Criterio.forma de EXT-5 y CampoValidable, empezando por secciones_cajon_normalizadas y seccion_receptor; una selección normativa obtiene el valor de la tabla; una adopción distinta exige procedencia; aplicar es atómico. (E14) Comparador de dos informe_json por identidad de punto (reutiliza la comparación de test_linea_base), con tolerancias nombradas y «no comparable» para métodos distintos; nunca recalcula con el proyecto activo. (E13 reducido) Columna evidencia/responsable en la pestaña 4 y en el anticipo, que sigue siendo informativo (00_LEEME_DICTAMEN §3). (E21 acotado) Memoria con índice, traza con sha1, criterios usados del contexto, bloqueos y alcance; nada que no exista como objeto. Descartado con razón en el dictamen: E06/E07 (hilos), E09, E16, E17, E19, E20, E22–E25, H03, H05 sin HY-8, H06–H08, rutas G/B sin consulta de dependencias, S00–S07 y D00–D03 sin fuente. Ritual de cierre.
```
