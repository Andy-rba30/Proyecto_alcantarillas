# Precisiones del orquestador para T-7a (cabezal: geometría por punto y aleros)

- IDs canónicos: `INF-4.1`, `INF-4.2`, `INF-4.3` y **`INF-5.1.15`** (lo que el prompt llama `INF-5.1.12`; el `INF-5.1.12` canónico
  es M10, de T-9: NO lo cierres). Hoja `Hallazgos` sólo lectura en FASE A (`tests/apoyo/tracker.py`).
- Ya en `main` y debes CONSUMIR: filas de aleros de las Tablas A.1 y C.2 (T-2); `M6.socavacion_salida` y el dato externo de
  profundidad de socavación (T-8, HEC-14 cap. 5) para el desplante; `M6.proteccion_entrada` (T-8, ficha T8-03: declara el
  revestimiento sin dimensiones porque ninguna fuente se las da → tu punto 5, losa/zampeado y dentellón, es GEOMETRÍA DECLARADA [A]
  y enlaza con esa ficha); la longitud por extremo y la ficha T6-01 de T-6 (la longitud ENTRE CABEZALES a la clave se cierra
  cuando exista la coronación del cabezal: te toca cerrarla o decir por qué no); `EstabilidadCabezal`, Ka de Coulomb y lo de EXT-7 en M9.
- **T-7b y T-7c vienen después y son de otro agente**: tú NO decides el marco de estabilidad (LRFD/ASD: ya decidido por el dueño,
  `<SP>/orq/../orq/DICTAMEN` no hace falta), ni ensamblas cargas, ni armas. Deja `GeometriaCabezal`, `Aleros` y las funciones de
  predimensionado con interfaz limpia para T-7b. La Fase 9 es de nivel EXPEDIENTE: no la hagas correr a perfil.
- El «PDF de VARIOS» (pp. 42, 18) NO está en la sesión: no lo cites con página; si usas una regla suya, es [A] «práctica, no
  verificada en esta sesión». Toda regla de predimensionado del prompt (H/8–H/6, 0.4–0.7·H, H/12–H/10, D_f ≥ 0.80 m, ciclópeo hasta
  2.0 m, 45°/30°/60°, H_f 0.30–0.50, 1.0–1.5·D, 0.20–0.30 m) es [A] con ventana salvo que encuentres el numeral real (E.050
  profundidad mínima de cimentación, E.060 cap. 14 espesores mínimos, EG-2013 Sec. 500, AASHTO 11.6.1.x, Láminas del MTC leídas
  por imagen): verifícalo en el PDF antes de etiquetar [N]/[C]. Si la fuente contradice la cifra del prompt, gana la fuente.
- **PARADA (c) — coherencia embocadura ↔ ke ↔ carta**: implementa el mecanismo (si la embocadura adoptada es con aleros, ke y la
  carta de control de entrada pasan a las filas de aleros y M4 recalcula; test: cambiar α no puede dejar ke intacto donde la fuente
  distingue). Pero el valor de archivo de la embocadura NO puede mover ningún diámetro ni sección ya dimensionados (A-01, A-02
  concreto Ø 0.90; B-01; C-01 marco 1.20 × 0.90 donde dimensiona). Comprueba en la fuente qué filas distingue HDS-5 para TUBO con
  cabezal y aleros (Tabla C.2: «headwall or headwall and wingwalls») frente a CAJÓN (cartas 8–13): si para el tubo la fila es la
  misma, nada se mueve y lo dices; si adoptar `angulo_aletas` por defecto cambia HW de algún punto, mide antes/después: HW que cambia
  sin mover diámetro = movimiento declarado con su causa; diámetro/sección que cambia = NO lo actives por defecto y devuelve la pregunta.
- Dimensiones pisadas por `--datos-externos`: validación de forma y dominio (`dominios.py`), nunca valor por defecto silencioso; la
  memoria imprime «propuesta por regla» o «declarada» por dimensión.
- T-3 (Familia C) trabaja a la vez en `/home/user/wt/T-3` y toca `embocadura_cajon`/`ke_entrada_cajon`: tú NO les des valor de
  archivo; tu mecanismo debe funcionar con el criterio declarado o vacío.
- Zonas calientes: `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py` (`correr_cabezal`),
  `M11_reporte.py`, `normativa/{citas,tablas,fundamentos}.py`, `decisiones_diferidas.md`, v8 §9, `CLAUDE.md`,
  `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`. Bloques `# --- T-7a ---` al final de sección. Tu módulo: `src/modulos/M9_cabezal.py`.
