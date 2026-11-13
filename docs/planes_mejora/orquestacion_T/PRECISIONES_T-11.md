# Precisiones del orquestador para T-11 (validación integral de las tres familias) — cuarta sesión

Base: `origin/main` con T-10 integrado (el orquestador te da el SHA). T-11 VALIDA: no cambia cálculo. **Si la validación destapa
un defecto de cálculo, de fórmula o de cita, NO lo arregles tú: déjalo reproducido en un test `xfail(strict=True)` con su
evidencia, sigue con el resto y repórtalo** (lo corrige otro agente). Lo que sí arreglas: plomería de integración (una excepción
fuera de `ErrorProyecto`, un bloqueo que debía ser dato faltante y sale como criterio vacío por un cableado, un texto), con test.
Después de ti un auditor adversarial revisará sobre todo tus JUICIOS (qué comparas con qué, por qué un punto llega o no llega,
si el censo dice la verdad): déjalos escritos y auditables.

- **Punto 1 (corrida de punta a punta a expediente).** El juego de datos NUEVO vive en `tests/fixtures/` con la cabecera
  «DATOS DE PRUEBA, NO DEL PROYECTO» en CADA archivo y entra SÓLO por las puertas de entrada: `--datos-externos`, `--datos-sitio`
  (sitio.json), `--cuencas` / `--estacion` (los sintéticos de `tests/fixtures/hidrologia/` valen), una copia del CSV para las
  celdas que son columna (p. ej. `cota_coronacion_canal` de C-01, como la corrida 6 de la línea base) y `--declarar` / sesión
  para los CRITERIOS que el dueño dejó sin valor a propósito (`remanso_derecho_via`, `TR_evento_extremo`,
  `umbral_no_colapso_evento_extremo`, `clase_exposicion_fisuracion_cabezal`, `homogeneidad_serie_fen`, los geotécnicos de ensayo,
  `perfil_hdpe_fabricante`…). **NUNCA se escribe un valor de prueba en `criterios_adoptados.py`, `datos_sitio.py` ni
  `constantes_normativas.py`**: esos vacíos son decisiones del proyecto y siguen vacíos. Reutiliza los datos de prueba que ya
  existen (los de T-7b/T-7c para el cabezal, `tests/fixtures/entradas_ampliadas.json`, la guía) antes de inventar otros; cada
  valor nuevo lleva una línea que diga por qué es plausible (orden de magnitud), sin presentarlo como dato del sitio.
  La frase del prompt «nunca un criterio vacío» se lee así: con el juego de prueba COMPLETO, las tres familias llegan a la
  Fase 11 con diseño, o con un bloqueo cuya causa es una entrada que el propio juego deja fuera A PROPÓSITO (dilo); y SIN el
  juego (corrida por defecto), cada bloqueo se clasifica en la lista: entrada del proyecto que falta / criterio que el Propietario
  debe declarar / método diferido con ficha. Ningún `NotImplementedError`, `AssertionError` ni excepción fuera de `ErrorProyecto`
  en ninguna de las dos (test que lo fije, corriendo las dos). Entrega la LISTA EXACTA de lo que sigue requiriendo entrada del
  proyecto, cruzada con `docs/contrato_entradas.md` (deben decir lo mismo; si no, corrige el contrato).
  Familia B: B-01 con TW = 1.00 m no dimensiona (V2) y VB1 no cumple por los 530 m (decisión del dueño: se deja): en tu juego de
  prueba decide con qué TW y qué `inicio_tramo_cuneta_km` corre, y dilo; no escondas el caso por defecto.
  El cabezal de la regla NO pasa E3 estático ni E1 sísmico con los datos de prueba (sensibles a dos [A]; iteración de zapata
  diferida por el dueño): es un RESULTADO, no un fallo de T-11; preséntalo así, con la sensibilidad.
- **Punto 2 (validación externa).** La tabla de HDS-5 ya existe en tests (`CP_HDS5_DG1`, T-2): llévala a un documento
  `docs/validacion_hds5.md` GENERADO desde los mismos casos (con test de sincronía, como la guía), con la tolerancia de lectura y
  las casillas fuera censadas con su causa; añade, si están publicados en los PDF de `normas/` y verificados por página, los
  ejemplos resueltos que otros prompts usaron como oráculo (HEC-14 del apron y de socavación, T-8). HY-8 NO está en el entorno:
  `docs/validacion_hy8.md` con el procedimiento exacto para que el autor lo corra (qué entradas de cada punto, qué salida comparar,
  qué tolerancia), sin afirmar ningún resultado de HY-8.
- **Punto 3 (sensibilidad).** Con `--barrido` (PF-3), una clave a la vez, sobre el fixture: los [A] que gobiernan el diámetro
  (`HW_D_max`, `borde_libre_bajo_tw_ahogante`, `seccion_receptor`, `v_max_*`, y los que tú identifiques midiendo: `regimen_v2b`,
  `hw_entrada_fuera_de_rango`, `n_manning_cajon`…) y los del cabezal (`factor_muro_eleccion`, `gamma_EQ`,
  `fraccion_delta_sobre_phi_trasdos`, `fila_phi_estabilidad_cabezal`, `factores_inclinacion_carga_portante`,
  `regla_pendiente_relleno_trasdos`, `regimen_resistencia_elementos_cabezal`, el η del cruce). El anexo `docs/` se GENERA con un
  script de `tests/apoyo/` y un test de sincronía (o lleva la huella de la corrida y un test que la compare): un anexo escrito a
  mano se desincroniza. Di qué [A] mueven un diámetro o un veredicto dentro de su ventana y cuáles no.
- **Punto 4 (censo final).** Además de lo que el prompt pide: (i) hoja `Hallazgos`: lista de TODO `INF-` que no esté cerrado, con
  su razón y quién lo destraba (incluidos los cuatro que ningún prompt nombraba: `INF-5.1.3`, `INF-5.1.8`, `INF-5.1.9`,
  `INF-5.1.16`: di su estado real); (ii) `docs/decisiones_diferidas.md` y la memoria dicen como ALCANCE DECLARADO lo que el dueño
  decidió dejar fuera (armado de la sección del marco de la Familia C; cabezal paralelo a la vía del marco; iteración del ancho
  de zapata; V7 del marco sin peso propio; Figuras 3.3–3.4 de HEC-14 y `max(V_c, V_erosion)` en M4 para un prompt posterior a la
  cadena; el escalón de 11 mm de E-A en HW/D = 1.2, ficha T7V-01); (iii) la hidrología calculada entra al índice de fórmulas con
  una corrida de prueba (pregunta 3 de T-10); (iv) `SIN_CONSUMIDOR_Y_SIN_MEDIDA` y `M9.FUNCIONES_SIN_CONSUMIDOR` al día.
- **Punto 5**: `docs/linea_base.md` y la tabla de `CLAUDE.md` los escribes al INTEGRAR (FASE B), no en FASE A.
- PARADA (c): ningún diámetro, sección, material ni HW del fixture se mueve; T-11 no cambia valores de archivo.
