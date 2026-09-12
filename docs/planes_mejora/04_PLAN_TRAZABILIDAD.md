# Plan T — Trazabilidad normativa: lo poco que faltaba, sin duplicar el registro

**Sustituye a:** `04_PLAN_TRAZABILIDAD_NORMATIVA.md`.
**Qué cambió en la revisión:** este era el plan más desactualizado de los
cuatro — casi todo su contenido existe, construido en S11–S12 con más detalle
del que pedía: `Fuente` con SHA-1 y desfase de paginación **medidos**, `Cita`
con `Verbatim` verificado contra el PDF (116 citas, 0 pendientes), carácter en
cinco valores, `Interpretacion` que exige hechos en contra, 18 tablas
transcritas completas con notas, modificadores y uso por celda,
`CorrespondenciaDeTablas.regla_al_cruzar`, 63 tests de guardia, y el
manifiesto **generado** (`docs/manifiesto_registro_normativo.md`) que es tu
«matriz de trazabilidad» con otro nombre. Tu `registro.yaml` habría sido un
duplicado del código; tus linters N1–N10 ya son invariantes del esquema.

Queda vivo, medido sobre el árbol real:

1. **Vigencia de ediciones** — el único campo de tu esquema que de verdad no
   existe. `Fuente` tiene `edicion`, `anio`, `resolucion`, `reemplaza_a`,
   `convive_con`, pero nadie ha confirmado contra el emisor que las ediciones
   citadas sigan vigentes (T1).
2. **Dos trinquetes que hay que bajar:** 9 `partes_sin_cita_transcrita` en
   discrepancias, y el triage de las 37 `elecciones_pendientes` (celdas y
   filas de tablas bloqueadas por condición) (T2).
3. **(Opcional) el export tabular para revisor externo**, generado — la única
   pieza de tu §5 que el manifiesto no da: filtrar y ordenar (T3).

---

## T1 · Vigencia de las ediciones citadas

Trabajo mitad de gabinete, mitad de registro. La sesión **no** cambia de
edición por su cuenta: si aparece una edición posterior, la decisión de
regirse por la nueva o por la vigente al inicio del proyecto es del
proyectista, y se registra como tal (tu propio plan lo decía bien en su §9, y
se conserva).

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md.
src/normativa/fuentes.py declara 13 fuentes presentes (con edicion, anio,
resolucion) y 13 ausentes. Nadie ha verificado que las ediciones citadas
sigan vigentes. Tienes acceso web (WebSearch/WebFetch); si la red no lo
permite, haz lo que puedas y reporta el resto como gabinete.

Tarea:
1. Para cada fuente PRESENTE peruana (MC_HHD, MP, MS, EG2013, E030, E050,
   E060): busca en el emisor oficial (MTC, SENCICO/Ministerio de Vivienda)
   si la edición/resolución citada sigue vigente o hay posterior. Para las
   de EE.UU. (HDS5_3ED, AASHTO_LRFD_9, M170M, M36, A760): edición vigente
   del emisor.
2. Registra el resultado EN EL REGISTRO, no en un documento aparte:
   - vigente confirmada → completa el campo nota de la Fuente con
     «vigencia confirmada <fecha>, <cómo>»;
   - edición posterior detectada → NO cambies la edición citada. Registra
     una Discrepancia (partes: lo que el proyecto cita vs lo que el emisor
     publica hoy) o usa reemplaza_a/convive_con si el esquema ya lo modela —
     decide leyendo esquema.py, y si el esquema necesita un campo nuevo para
     esto, propónlo en el cierre en vez de forzarlo.
   - El criterio de QUÉ edición rige el expediente, si aparece el caso, es
     del proyectista: déjalo como pendiente declarable por la vía que el
     proyecto ya usa (criterio con valor None), no lo decidas.
3. Nada de esto toca valores de cálculo ni citas verificadas: una cita
   contra la edición 2016 sigue siendo válida contra ese PDF (el SHA-1 la
   ancla). La vigencia es un metadato de la fuente, no de la cita.
4. Deja en el cierre la tabla fuente → estado (confirmada / posterior
   detectada / no determinable en línea → gabinete).

Cierre: suite en verde; commit «trazabilidad(T1): vigencia de ediciones
verificada y registrada — <n> confirmadas, <n> con posterior, <n> a
gabinete»; entrega en origin/main; conteo como par
passed+skipped=collected desde origin/main, con el entorno.
```

---

## T2 · Bajar los dos trinquetes del registro

- `Registro.partes_sin_cita_transcrita()` → **9** partes de discrepancias que
  afirman «la parte X dice tal cosa» sin la cita transcrita que lo pruebe.
  Es un trinquete: solo puede bajar.
- `Registro.elecciones_pendientes()` → **37** filas/columnas de tablas
  bloqueadas por `PendienteDeCondicion` (las 15 filas de cajón de
  `HDS5_3ED.TA1` por `COND-EMBOCADURA-CAJON`, las columnas de `MP.TFPGA` por
  `COND-CLASE-DE-SITIO`, las de `T5.10.1-1` por `COND-CATEGORIA-REFUERZO`…).
  No todas son «trabajo»: muchas esperan una elección del proyectista o un
  dato de sitio. Lo que falta es el **triage escrito**: cuáles se destraban
  con trabajo de citas, cuáles con una declaración, cuáles con un ensayo.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. Dos vistas del
registro miden deuda de trazabilidad: partes_sin_cita_transcrita() (hoy ~9)
y elecciones_pendientes() (hoy ~37). Mide ambas antes de empezar.

Tarea 1 — las partes sin cita transcrita:
Para cada parte de Discrepancia sin cita: transcribe la cita que la sostiene
(Verbatim + página, verificada con verificador-normativo; método IMAGEN si
la fuente no da texto). Si la fuente que la sostiene está AUSENTE de
normas/, la parte no puede transcribirse: déjalo dicho en la discrepancia y
répórtalo en el cierre — no inventes el texto. Objetivo: el trinquete baja
todo lo que las fuentes presentes permitan.

Tarea 2 — triage de elecciones_pendientes:
Para cada PendienteDeCondicion, clasifica QUÉ lo destraba:
  (a) una declaración del proyectista (criterio existente — nómbralo);
  (b) un dato de sitio o ensayo (nómbralo);
  (c) trabajo de citas/transcripción posible hoy (hazlo en esta sesión si
      cabe, con verificador-normativo);
  (d) una fuente ausente (nómbrala).
El triage NO va a un documento nuevo: revisa si CondicionAplicacion ya tiene
dónde decirlo (resuelve: PorCriterio/PorDatoDeSitio/NoEvaluable ya apunta la
dirección); lo que falte de completar, complétalo en los objetos. En el
cierre, la tabla condición → clase → qué la destraba.

Regla dura: cero elecciones tomadas. Este trabajo deja los vacíos mejor
señalizados, no los rellena.

Cierre: suite en verde; commit «trazabilidad(T2): partes transcritas y
triage de elecciones pendientes — trinquetes <antes>→<después>»; entrega en
origin/main; conteo como par desde origin/main, con el entorno.
```

---

## T3 · (Opcional) Export tabular para revisor externo

Lo único de tu matriz §5 que el manifiesto generado no da: una vista
**filtrable** (CSV) para que un revisor —persona o IA— haga «dame todas las
exigencias con verificación por imagen» sin leer Markdown. Se genera del
`Registro`, con orden determinista y sello, como todo documento generado de
la casa.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. El manifiesto del
registro ya se genera (normativa/manifiesto.py) con test de sincronía. Esta
sesión añade una vista CSV, también generada — nunca editada a mano.

Tarea: generador docs/trazabilidad.csv (función en normativa/manifiesto.py,
mismo patrón): una fila por Cita, con columnas
  cita_id, fuente_id, norma, edicion, numeral, titulo_numeral,
  pagina_impresa, pagina_pdf, caracter, metodo_verificacion,
  fecha_verificacion, tiene_interpretacion, discrepancias_que_la_tocan,
  consumidores_declarados.
Orden determinista (fuente_id, numeral, cita_id) para diffs legibles.
Primera línea de comentario con el sello: fecha, commit, alcance y el par de
la suite. Test de sincronía calcado del existente. Añade la regeneración al
mismo flujo que regenera el manifiesto.

Cierre: suite en verde; commit «trazabilidad(T3): export CSV generado del
registro»; entrega en origin/main; conteo como par desde origin/main, con el
entorno.
```

---

## Fuera de alcance del plan T

- `registro.yaml` o cualquier segundo registro paralelo al código.
- Redistribuir PDFs (igual que en tu plan).
- Opinión legal sobre qué marco normativo aplica: la vigencia se documenta,
  la elección de marco es del proyectista y se declara como criterio (esto se
  conserva literal de tu plan, que aquí estaba bien).
- Conseguir las fuentes ausentes (gabinete; la lista con qué desbloquea cada
  una ya está en `FUENTES_AUSENTES` y en la deuda §15).
