# Precisiones del orquestador para T-3 (Familia C: el marco se dimensiona)

- ID canónico: lo que el prompt llama «INF-3.x Familia C no se dimensiona» es **`INF-0.4`**; los criterios del cajón son del cluster
  de criterios vacíos (mira la hoja `Hallazgos` con `tests/apoyo/tracker.py`, sólo lectura en FASE A, y di qué filas tocas).
- Lo que ya existe y debes CONSUMIR, no re-transcribir: T-2 dejó en `constantes_normativas`/registro las 26 filas de la Tabla A.1
  y las de ke de la Tabla C.2 (cajón con aleros incluidas) y la sección medida del receptor (`seccion_receptor_medida`, dato externo);
  EXT-2 el reparto multicelda (`HDS5_3ED.5.4.3#REPARTO`); E-A el perfil de la lámina; T-6 la geometría por extremo; T-4
  `D_max_norma_producto`. `docs/ruta_familia_c.md` entera es lectura obligada. `docs/guia_perfil.md` y `tests/test_guia_perfil.py`
  declaran HOY en caliente los siete criterios del cajón: al darles valor de archivo esos tests y la guía cambian de contrato
  (reescríbelos sin perder lo que medían; la guía se regenera con `python -m tests.apoyo.guia_perfil`).
- **PARADA (c)**: C-01 es marco **1.20 × 0.90** donde hoy dimensiona (con los criterios declarados en caliente en la guía/tests y en
  la línea base). Con valor de archivo, C-01 pasará de «bloqueado por criterio» a dimensionado en la corrida por defecto: eso es
  movimiento DECLARADO (dilo con B×H y HW). Pero si la progresión que el prompt propone (anchos 1.00–4.00 paso 0.50, alturas
  1.00–3.00 paso 0.25) NO contiene 1.20 × 0.90 o hace que alguna corrida que hoy fija una sección adopte otra, NO cambies lo que
  esas corridas fijan: deja la progresión del prompt como valor de archivo SÓLO si ninguna sección ya fijada se mueve; si se
  movería, implementa todo, deja el valor de archivo que NO mueve nada (o el criterio sin valor si no hay tal) y devuelve la
  pregunta con el antes/después. A-01, A-02 (concreto Ø 0.90) y B-01 no pueden cambiar en nada.
- Cada valor que des a un criterio: fila de tabla nombrada por clave (nunca número suelto), cita verificada contra el PDF, y
  [A] con ventana donde la fuente no fija cifra. «práctica EG-2013» o «catálogo constructivo» sin numeral real NO es cita: [A]
  declarado. AASHTO LRFD 12.11 / 12.6.6.3 (cobertura), manual MTC 4.1.1.3.4 (múltiples, separación), E.060 (espesores mínimos):
  numeral y página reales o nada. Si `embocadura_cajon` con aleros da distinto HW que «square edge headwall 90°», deja el de hoy
  (lo cambiará T-7a con coherencia ke↔carta).
- M8: T-5 (Fase 8 real, AASHTO 12.11 para el marco) está en la rama `tesis/T-5` (worktree `/home/user/wt/T-5`, sólo lectura) y se
  integra ANTES que tú: no implementes cargas del marco en M8; limítate a que la geometría del marco (H, B, espesores, cota de
  clave) quede disponible en `modelos.py`/M7 para quien la consuma, y mira cómo T-5 lee hoy la sección para no chocar.
- VC2 y el remanso aguas arriba del canal: con dato → verificación / aviso; sin dato → «no evaluado» con aviso, nunca un supuesto.
- Zonas calientes (conflictos al integrar): `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`,
  `M11_reporte.py`, `normativa/{citas,tablas,fundamentos}.py`, `decisiones_diferidas.md`, v8, `CLAUDE.md`,
  `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`. Bloques `# --- T-3 ---` al final de sección; no reordenes nada ajeno.
