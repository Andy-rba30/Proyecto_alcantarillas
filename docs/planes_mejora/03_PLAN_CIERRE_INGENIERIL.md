# Plan I — Cierre ingenieril: lo que de verdad queda abierto

**Sustituye a:** `03_PLAN_AUDITORIA_INGENIERIL.md`.
**Qué cambió en la revisión:** tu plan proponía re-auditar «240 fórmulas» y
cerrar «48 defectos + 8 patrones». Esos números son de una foto vieja. El
tracker real (`docs/auditorias/matriz_cruzada_auditorias.xlsx`, hoja
`Hallazgos`, 237 filas) dice hoy: **220 Cerrado · 6 Cerrado parcial · 10 sin
acción · 1 verificado**. Las 174 verificaciones contra fuente primaria del
motor hidráulico son precisamente lo que la regla de la casa dice **no tocar
sin un test que falle antes**. Y dos de tus tickets eran la corrección
ingenua que la matriz de conflictos prohíbe (V4b — conflicto #1, ya resuelto
en S14 tal como el conflicto mandaba; `v_max` — cerrado con guardia que impide
volver al símbolo retirado).

Lo que queda abierto de verdad, medido:

1. **Los 6 «Cerrado parcial»** del tracker (I1).
2. **Las 10 discrepancias vivas** de `src/normativa/discrepancias.py` (I2).
3. **Los residuos de la Familia C** anotados en la bitácora de
   `docs/ruta_familia_c.md` §16 (I3).
4. Dos guardias nuevas de tu plan que valen la pena, en versión honesta:
   índice de fórmulas **generado** y chequeo dimensional **piloto** (I4,
   opcional).

De tu §A.2 (las diez preguntas de procedimiento): siete están respondidas por
la auditoría matemática cerrada y por el diseño vigente (control
entrada/salida con gobernante, TW que se detiene si falta, bucle de
materiales aislado, `DisenoNoFactibleError` con delta de rasante). Las que
siguen vivas quedan absorbidas: la 3.ª condición de `h_o` con barril
parcialmente lleno es NOR-HDS-05 (I1), y la coherencia de la cadena sísmica
con los parámetros de sitio quedó resuelta en S13 con la premisa de Clase de
Sitio (su discrepancia está en I2 si sigue viva).

---

## I1 · Los seis «Cerrado parcial»

Qué queda en cada uno, según el propio tracker:

| ID | Qué queda | ¿Accionable hoy? |
|---|---|---|
| `SIS-F-01` (GRAVE) | El código que construye widgets no se ejecuta en la suite | **Sí** — `CLAUDE.md` documenta que `python3-tk` + `xvfb-run` funcionan en el contenedor; ya hay 3 tests de ventana real |
| `NOR-PRO-04` (ALTA) | (1) transcribir Tabla 1 de ASTM A760 / Tabla 6 de AASHTO M 36; (2) calibre TMC por cobertura | (1) **Sí**, por método IMAGEN (los PDF no dan texto); (2) **No** — ASTM A796 no está en `normas/` (gabinete) |
| `SIS-F-13` (MENOR) | Casos patrón de M2, M8, M10 | **No** sin fuente externa — el conflicto #7 prohíbe inventar dorados. Gabinete: series de diámetros de M170M/M36/M294 |
| `NOR-E060-02` (ALTA) | `predimensionamiento_cabezal` sin declarar; `diseno_flexion_corte` lanza `NotImplementedError` | Parcial — es contrato de expediente; verificar que la detención sea ruidosa y declarada, no implementarlo |
| `NOR-HDS-05` (ALTA) | Procedimiento de barril parcialmente lleno (3.ª condición de `h_o`) | Parcial — evaluar si el Cap. III del HDS-5 (que SÍ está en `normas/`) da el procedimiento transcribible |
| `NOR-ANA-03` (MEDIA) | Detalle constructivo de embocadura HDPE | **No** — contenido de planos, no de software |

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md, incluida la sección
«Reglas de corrección de hallazgos»: ficha completa de cada ID antes de
tocar, hoja Conflictos vinculante, anclar por símbolo, actualizar el tracker
(openpyxl está PREAUTORIZADO para eso). Plan mode: sí.

Tarea: trabajar los 6 hallazgos en estado «Cerrado parcial» de la hoja
Hallazgos de docs/auditorias/matriz_cruzada_auditorias.xlsx. Para cada uno,
lee su ficha en docs/auditorias/*.md y decide: accionable en esta sesión /
bloqueado por fuente ausente (gabinete) / contrato de expediente. Luego:

1. SIS-F-01 — accionable: amplía los tests de ventana real
   (tests/test_gui_contrato.py, patrón _interprete_con_ventana) para que la
   construcción de widgets de gui/app.py y gui/ventana_normativa.py se
   ejecute al menos una vez bajo Tk real (smoke: construir la app, poblar
   las 4 pestañas con tests/ejemplo_puntos.csv, abrir y cerrar la ventana
   normativa de un criterio de_tabla). CLAUDE.md documenta cómo conseguir
   Tk en el contenedor (apt-get install -y python3-tk; python3.12 -m pip
   install numpy scipy ttkbootstrap --break-system-packages; xvfb-run).
   Recuerda: estos tests se SALTAN sin entorno gráfico — deben quedar en la
   clase de saltos ya documentada, sin romper el par collected.
2. NOR-PRO-04(1) — accionable: transcribe la Tabla 1 de ASTM A760 y la
   Tabla 6 de AASHTO M 36 como TablaNormativa en src/normativa/tablas.py.
   Ambas fuentes están declaradas con texto_extraible=False: la verificación
   es por método IMAGEN (renderizar_pagina), como ya hacen 5 citas del
   registro. Lanza verificador-normativo sobre cada transcripción. La parte
   (2) del hallazgo queda declarada como bloqueada por ASTM A796 ausente
   (ya censada en FUENTES_AUSENTES).
3. NOR-HDS-05 — evalúa: abre el Cap. III del HDS-5 (normas/, fuente
   HDS5_3ED) y decide si el procedimiento de barril parcialmente lleno es
   transcribible como cita+fundamento para la 3.ª condición de h_o. Si sí,
   deja ESCRITO el paquete (numeral, páginas, qué habría que implementar en
   M4/M5) sin implementarlo — la implementación es sesión propia, con plan
   mode, porque toca el motor validado. Si no, documenta por qué en la
   ficha del hallazgo.
4. NOR-E060-02 y NOR-ANA-03 — verifica que su estado parcial esté declarado
   donde corresponde (detención ruidosa de diseno_flexion_corte; entrada en
   docs/decisiones_diferidas.md si falta) y déjalos en parcial con la razón
   escrita en el tracker.
5. SIS-F-13 — no fabricar dorados (conflicto #7). Confirma que la exención
   de M2/M8/M10 sigue censada en la guardia de casos patrón y en
   decisiones_diferidas.md, y que la lista de qué fuente externa
   desbloquearía cada uno esté completa (M170M/M36/M294 para M2).
6. Actualiza Estado/Responsable/Commit en el .xlsx para lo que cambie de
   estado (pip install openpyxl --break-system-packages está preautorizado).

Antes de cerrar cualquiera de los seis, lanza auditor-adversarial sobre la
corrección y di explícitamente si cierra, cierra en parte o no cierra la
ficha — regla 3 de CLAUDE.md.

Cierre: suite en verde; commit «cierre(I1): trabajo sobre los 6 Cerrado
parcial — <IDs con cambio de estado>»; entrega en origin/main; conteo como
par passed+skipped=collected desde origin/main, con el entorno (aquí importa
doble: si conseguiste Tk, repórtalo como columna nueva de la tabla de
CLAUDE.md).
```

---

## I2 · Las diez discrepancias vivas

`src/normativa/discrepancias.py` declara 23 `Discrepancia`; 10 están vivas
(`ABIERTA` o `ABIERTA_CONTRA_HOJA_DE_RUTA`). Una discrepancia
`ABIERTA_CONTRA_HOJA_DE_RUTA` significa que **la hoja de ruta v8 sigue mal**
y quien la lea sin leer el código diseñará con el valor equivocado — la
constitución obliga a mantener eso dicho hasta corregir la v8. El precedente
de corrección existe (conflicto #6: la v8 se editó a 19.63 en sus cuatro
menciones).

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md: la fuente primaria
(PDF en normas/) gana sobre la hoja de ruta SOLO con verificación de
numeral + página + texto literal, y ganar por esa vía obliga a tres cosas
(declarar en el punto de uso, reportar contra la hoja de ruta, dejar dicho
que sigue mal mientras no se corrija). Plan mode: sí.

Tarea: recorrer las discrepancias vivas de src/normativa/discrepancias.py
(Registro.discrepancias_abiertas(); hoy ~10, mide) y, una por una:

1. Clasifícala: (a) resoluble corrigiendo la hoja de ruta v8; (b) resoluble
   corrigiendo código/registro; (c) irresoluble hoy (fuente ausente o
   decisión del proyectista).
2. Para las (a): prepara la edición EXACTA de
   docs/hoja_de_ruta_alcantarillas_v8.md — qué línea, qué texto entra, qué
   cita la sostiene — y APLÍCALA solo si la discrepancia ya está verificada
   contra fuente primaria por el registro (verificado con método declarado).
   Si la verificación no existe, primero verificador-normativo; sin
   verificación no se toca la v8. Al aplicar, actualiza el estado de la
   Discrepancia (RESUELTA) y revisa si M11 imprimía la advertencia asociada.
   OJO: no renombres el archivo — M11 lo localiza por patrón y exige
   exactamente uno.
3. Para las (b): mismo protocolo, con auditor-adversarial antes de cerrar.
4. Para las (c): confirma que el estado y el efecto de seguir la otra parte
   (efecto_si_se_sigue_la_otra) estén completos, y que la memoria las siga
   imprimiendo (tests/test_canal_discrepancias.py cubre el canal — extiende
   si añades casos).
5. La errata de K_AE (DIS-MP-KAE-SIGNO) es ERRATA_DE_IMPRENTA resuelta: es
   la trampa señalada en la hoja de ruta de correcciones §14 — NO
   «corrijas» el código contra el literal del Manual bajo ninguna
   circunstancia.

Ningún valor de cálculo cambia en esta sesión salvo que una discrepancia
verificada lo exija; en ese caso, dilo en el plan ANTES de tocarlo y hazlo
en commit separado dentro de la sesión, con su caso patrón ajustado y la
justificación en el mensaje.

Cierre: suite en verde; commit «cierre(I2): discrepancias vivas —
<resueltas>/<declaradas>»; entrega en origin/main; conteo como par desde
origin/main, con el entorno.
```

---

## I3 · Residuos de la Familia C

La bitácora (`docs/ruta_familia_c.md` §16) deja tres abiertos tras la sesión
C2: el defecto **D-9** contra la v8 (las dos formas de la ecuación de control
de entrada de HDS-5), **`ke_entrada` del cajón heredando el 0.5 de tubo**
(remitido a una futura C5), y la **página impresa A.8 de la Tabla A.1
inferida, no leída**. Además, 5 de los 9 criterios de perfil sin valor son
del cajón (`embocadura_cajon`, `ke_entrada_cajon`, `n_manning_cajon`,
`secciones_cajon_normalizadas`, `n_celdas_cajon`…): son elecciones del
proyectista y **no se rellenan** — pero su ficha debe estar completa para
declararlos desde la GUI.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md y, para todo lo de
Familia C, docs/ruta_familia_c.md (sus §6 reglas vinculantes y §16 bitácora).
Plan mode: sí.

Tarea, en este orden:
1. Página A.8: verifica con verificador-normativo la página impresa real de
   la Tabla A.1 del HDS-5 (fuente HDS5_3ED, ya en normas/) y corrige la cita
   si la inferencia estaba mal; deja el método de verificación registrado.
2. D-9 (dos formas de la ecuación de control de entrada): lee el estado en
   §15/§16 de ruta_familia_c.md. Si es discrepancia contra la v8 aún no
   registrada en src/normativa/discrepancias.py, regístrala con sus partes y
   citas (eso la mete al canal que M11 imprime). Su corrección de la v8
   sigue el protocolo del plan I2 — si I2 ya corrió, aplícala aquí con el
   mismo protocolo; si no, déjala registrada y viva.
3. ke_entrada_cajon: NO elijas el valor (es elección del proyectista). Lo
   que sí: confirma que el criterio esté completo como ficha declarable
   (concepto, fuente candidata con cita de la tabla de ke del HDS-5 si
   aplica, sensibilidad, resolucion, nivel) para que se pueda declarar desde
   la ventana normativa; y que mientras esté vacío, el punto de cajón se
   detenga o difiera con Bloqueo declarado, no con default silencioso
   (verifica contra el comportamiento real corriendo el pipeline con
   tests/linea_base_familia_c/).
4. Recorre los otros criterios de perfil sin valor del cajón
   (ca.criterios_de_perfil_sin_valor(), hoy 9 — mide) con el mismo criterio
   de completitud de ficha. Registra en el cierre cuáles quedaron
   declarables y cuáles esperan un dato que este software no produce.

Regla dura: cero valores inventados. Un vacío que necesita al proyectista se
queda vacío, declarado y declarable — es la regla más importante de
CLAUDE.md.

Cierre: suite en verde; commit «cierre(I3): residuos de Familia C — A.8
verificada, D-9 registrada, fichas del cajón declarables»; entrega en
origin/main; conteo como par desde origin/main, con el entorno. Actualiza la
bitácora §16 de ruta_familia_c.md con una entrada de esta sesión.
```

---

## I4 · (Opcional) Índice de fórmulas generado + chequeo dimensional piloto

Dos ideas de tu plan que sobreviven, en versión honesta:

- **Tu `matriz_formulas.csv` escrita a mano** se convierte en un **índice
  generado**: una corrida de referencia emite los `PasoDeMemoria`, y de ahí
  sale (módulo, función, fórmula, `formula_cita_id`, variables con
  procedencia). Generado como el manifiesto del registro, con test de
  sincronía — nunca mantenido a mano.
- **Tu chequeo dimensional de «todas las fórmulas»** se recorta a un
  **piloto** sobre la cadena hidráulica (M3–M5), que es donde viven los
  coeficientes dependientes de unidades. Si el piloto encuentra algo, se
  amplía; si no encuentra nada en la cadena más densa, el retorno del barrido
  total es dudoso y se declara la decisión en `decisiones_diferidas.md`.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. Los PasoDeMemoria de
una corrida llevan fórmula, cita y sustitución con procedencia; el manifiesto
del registro se GENERA (normativa/manifiesto.py::indice_del_registro) con
test de sincronía. Sesión opcional de guardias nuevas; ningún valor cambia.

Tarea 1 — índice de fórmulas generado:
- Añade a normativa/manifiesto.py (o hermano) un generador que, a partir de
  los PasoDeMemoria de una corrida de referencia sobre
  tests/ejemplo_puntos.csv a --alcance expediente, produzca
  docs/indice_formulas.md: una fila por paso con fase, módulo emisor,
  fórmula, cita (numeral + página), y variables con su etiqueta de
  procedencia. Cabecera con fecha, commit y el par de la suite — como pide
  la regla de sellos. Test de sincronía calcado del
  test_el_indice_del_registro_esta_sincronizado.
- Las verificaciones sin paso aparecen como los HuecoDeVerificacion que ya
  son, no se omiten.

Tarea 2 — chequeo dimensional piloto (M3, M4, M5):
- Para cada PasoDeMemoria emitido por esos módulos en la corrida de
  referencia, verifica que las unidades declaradas en la sustitución sean
  consistentes con la unidad del resultado, usando un mapa de dimensiones
  por unidad SI (m, m2, m3/s, m/s, Pa, kN…) que vive en el test, no en src/.
- Constantes con sufijo _SI: verifica que cada una la use una fórmula cuya
  sustitución quede dimensionalmente cerrada con el comentario imperial que
  la acompaña. Reporta, no corrijas: cualquier inconsistencia es un
  candidato a Discrepancia o a hallazgo, y su corrección es sesión aparte
  (tocaría el motor validado — regla: test que falle antes).
- Si el piloto sale limpio, registra en docs/decisiones_diferidas.md la
  decisión de no extender el barrido, con el argumento medido.

Cierre: suite en verde; commit «guardias(I4): índice de fórmulas generado y
chequeo dimensional piloto M3–M5»; entrega en origin/main; conteo como par
desde origin/main, con el entorno.
```

---

## Fuera de alcance del plan I

- Re-verificar las 174 fórmulas confirmadas contra fuente primaria (regla:
  no tocar el motor validado sin un test que falle antes).
- Implementar el diseño estructural del pórtico / flexión-corte del cabezal
  (contrato de expediente, detención ruidosa ya declarada).
- Conseguir las fuentes ausentes (gabinete del dueño; A796 y M294 son las dos
  que más desbloquean — quedó dicho en la deuda §15).
- Optimizar rendimiento; familias o materiales nuevos.
