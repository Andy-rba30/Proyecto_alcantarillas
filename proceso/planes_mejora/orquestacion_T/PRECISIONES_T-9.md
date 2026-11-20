# Precisiones del orquestador para T-9 (espaciamiento de alivios con L hidráulico calculado)

- IDs canónicos: lo que el prompt llama `INF-5.1.11` («M10 no puede fallar») es **`INF-5.1.12`**; «INF-3.3 espaciamiento» es la
  fila `INF-3.3.k` que T-0 te asigna; y por decisión del dueño te tocan además **`INF-5.1.8`** (`area_ha` obligatoria en la
  Familia B sin consumidor: dale consumidor real —el área tributaria/contraste del caudal de la cuneta— o deja de exigirla,
  lo que la fuente y el contrato de entradas sostengan) y **cablear la aceptación de la Familia B**:
  `M1.PERFILES[Familia.B].verificaciones_aceptacion` = «V1 + V2 + V4 + V5 + espaciamiento de la Fase 10» (v8 §2.3, ficha T0-03),
  ahora que M10 tendrá una verificación que puede fallar. Hoja `Hallazgos` sólo lectura en FASE A.
- Ya en `main` y debes CONSUMIR (T-1): `MH_hidrologia.caudal_de_aporte_cuneta` (devuelve `PasoDeMemoria`; es TU enlace),
  `precipitacion_de_diseno` / puerta FEN (`homogeneidad_serie_fen`: ninguna lluvia de diseño sin pasar por ella),
  `duracion_minima_lluvia_min` [C], `coeficiente_escorrentia_superficie_vial` [C] (WSDOT Table 2-2), el único 0.278
  (`RACIONAL_COEFICIENTE_SI`). **`MH_hidrologia` sólo lo importa `src/servicio.py` (test por AST)**: M10 no puede importarlo; el
  servicio hace de puente (calcula el aporte y se lo pasa a M10, o le pasa la función). Lee la ficha T1-04 y las de T-1 sobre el enlace.
- Fuentes a verificar TÚ contra el PDF del manual MTC: 4.1.2.1 cunetas (sección típica y su tabla de dimensiones mínimas,
  longitud máxima de tramo «250 m / 200 m» con su texto literal y su carácter —¿exige o recomienda?—, velocidades admisibles por
  revestimiento, la ecuación de Manning que cite) y DG-2018 (bombeo, anchos; numerales reales). El TR de la cuneta («35 años» dice
  el prompt): verifícalo en la Tabla del manual (riesgo/vida útil) o es entrada/criterio declarado; no lo fijes de memoria.
- Entradas que NO se inventan: sección de cuneta ([A] de sección típica CON ventana y cita de la tabla de mínimos), ancho
  tributario (dato externo), pendiente longitudinal de la rasante (dato externo o derivada del perfil si el CSV la sostiene: di cómo),
  revestimiento. `L_hidraulico_m` declarado sigue aceptándose y GANA. Falta algo que se necesita → `DatoFaltanteError` con nombre,
  dentro de `_etapa` (bloqueo del punto/tramo), nunca corrida caída. El pre-vuelo (`anticipo.datos_faltantes_por_punto`) debe seguir
  diciendo la verdad sobre lo que detiene y lo que espera.
- Verificación por TRAMO entre obras B consecutivas (progresivas del CSV): con una sola obra B en el fixture (B-01) di qué se
  puede verificar y qué no (extremos del tramo: dato externo opcional, no supuesto); que pueda FALLAR de verdad (test con dos
  progresivas a mano), y el resultado en `InformePunto`/informe, CLI, JSON y memoria, con avisos por `avisos()`.
- **PARADA (c)**: B-01 hoy NO dimensiona en la corrida con TW = 1.00 m (V2 no cierra en ningún D) y donde dimensiona es Ø 0.90 /
  1.05 según la corrida de la línea base (míralo en `tests/linea_base_familia_c/README.md`). Cablear la aceptación de la Familia B
  cambia qué verificaciones deciden su diámetro: mide antes/después cada corrida de la línea base y de `docs/guia_perfil.md`.
  Si el diámetro o el «dimensionado» de B-01 (o de cualquier punto) cambia, NO lo actives por defecto: deja el cableado listo,
  el valor de hoy vigente, y devuelve la pregunta con el antes/después. A-01, A-02 y C-01 no pueden cambiar en nada.
- La Fase 10 es de nivel EXPEDIENTE hoy: decide con «Nivel de entrega» de CLAUDE.md (y dilo) si el espaciamiento entra a la
  aceptación a perfil o queda diferido con símbolo; no cambies el alcance de perfil sin medirlo (`tests/test_nivel_medido.py`).
- Zonas calientes: `criterios_adoptados.py`, `constantes_normativas.py`, `modelos.py`, `servicio.py`, `M11_reporte.py`,
  `normativa/{citas,tablas,fundamentos}.py`, `decisiones_diferidas.md`, v8, `CLAUDE.md`,
  `tests/test_t0_gobernanza.py::LO_QUE_ESCRIBIO_CADA_PROMPT`. Bloques `# --- T-9 ---` al final de sección. Tu módulo: `src/modulos/M10_espaciamiento.py` (o como se llame hoy).
