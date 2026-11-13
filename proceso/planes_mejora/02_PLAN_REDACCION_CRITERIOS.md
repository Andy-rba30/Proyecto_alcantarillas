# Plan R — Redacción de criterios: estilo sin migración de esquema

**Sustituye a:** `02_PLAN_CRITERIOS_Y_TEXTOS.md`.
**Qué cambió en la revisión:** tu diagnóstico del texto de `F_pga` era bueno
(narración en vez de descripción, énfasis retórico, cuatro funciones en un
párrafo), pero la solución propuesta —migrar 69 criterios a una ficha de ocho
campos— ataca el esquema cuando el problema es la **redacción**. La mitad de
los ocho campos ya existe con otro nombre y más rigor: «qué dice la fuente» es
el `Verbatim` de la `Cita` (verificado contra el PDF), la «interpretación» es
el tipo `Interpretacion` del registro (que exige declarar hechos en contra),
la «sensibilidad» es un campo real de `Criterio`, y «quién lo consume» se
deriva. Migrar el esquema para ganar dos campos es riesgo alto y retorno bajo,
y arriesga exactamente lo que tu propio plan temía: perder información en la
migración.

**También se corrige una premisa.** Tu plan pedía textos «válidos para
cualquier proyecto, sin un solo dato de otro proyecto». Este repositorio es el
expediente de UNA obra (vía de evitamiento, La Unión, Piura), y la taxonomía
de la casa dice que un `[A]` **se defiende con su sensibilidad en esta obra**
(«la fila D daría 1.1 y la envolvente subiría 10 %» es una defensa legítima).
Lo que está mal no es que el dato del corredor exista: es (a) que esté
**mezclado** con lo que dice la fuente, como si fuera norma — eso es
NOR-HID-04 —, y (b) el **registro**: bitácora, primera persona, mayúsculas de
alegato. Las reglas de estilo de abajo atacan (a) y (b) y dejan en paz la
defensa por sensibilidad.

---

## R1 · El linter de estilo (`tests/test_estilo_criterios.py`)

Se conservan tus reglas buenas, adaptadas al esquema real, y se les da la
forma de la casa: **trinquete decreciente** (como `MAX_REFERENCIAS_DE_PROSA`
en `test_manifiesto_citas.py`), porque un linter que nace en rojo sobre 69
textos existentes o se apaga o bloquea todo.

| Regla | Falla cuando (en `justificacion` o `concepto` de un `Criterio`) | Nota |
|---|---|---|
| E1 | Verbos de bitácora: `antes se`, `se corrigió`, `se detectó`, `en la versión anterior`, referencias a sesiones (`S12`, `C2`) o a hallazgos (`SIS-`, `NOR-`, `MAT-`) como narración | La historia vive en git y en `decisiones_diferidas.md` |
| E2 | Primera persona: `decidimos`, `adoptamos`, `creo` | Impersonal siempre |
| E3 | Mayúsculas enfáticas: 2+ palabras seguidas todas en mayúscula que no sean siglas (lista blanca derivada: siglas ya presentes en el repo — AASHTO, TMC, HDPE, PGA, CBR, FEN, LRFD, MTC, WSDOT, HDS…) | La lista blanca vive junto al test y crece con justificación |
| E4 | Referencias al código como argumento normativo: `porque M9 lo espera`, `para que brentq` | El código no es fuente |
| E5 | Un texto que transcribe entre comillas una frase de la fuente en lugar de citar por `cita_id` | Ya es regla de la casa («ningún texto literal se transcribe dos veces», `Registro.textos_literales()`); aquí se extiende a los criterios |
| E6 | Magnitud sin unidad SI en el texto | |
| E7 | Fechas de calendario dentro de la justificación | |

**Lo que NO se prohíbe** (diferencia deliberada con tu R7): números y
resultados de esta obra dentro de la defensa de sensibilidad. Sí se exige que
estén presentados como sensibilidad («si se leyera la columna anterior…»),
no como contenido de la norma.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. Los 69 criterios de
src/criterios_adoptados.py llevan su texto en los campos `justificacion` y
`concepto` del dataclass Criterio. NO vas a cambiar el esquema ni ningún
valor: esta sesión solo construye el linter y mide.

Tarea:
1. Escribe tests/test_estilo_criterios.py con las reglas E1–E7 del plan
   (docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md si está en el repo; si
   no, las reglas van también al docstring del test). Cada regla con mensaje
   que nombre CLAVE, CAMPO y QUÉ corregir.
2. Forma de trinquete, calcada de MAX_REFERENCIAS_DE_PROSA en
   tests/test_manifiesto_citas.py: mide las violaciones actuales por regla,
   fija el censo como constante (p. ej. VIOLACIONES_E1 = {...claves...}), y
   el test falla si aparece una violación NUEVA o si el censo dice que una
   clave está limpia y no lo está. El censo solo puede decrecer.
3. La lista blanca de siglas para E3 se construye derivándola de las siglas
   que ya aparecen en fuentes.py y constantes_normativas.py, más las que el
   barrido inicial justifique una a una en comentario.
4. Deja en el resumen de cierre la tabla: regla → número de criterios
   afectados → los cinco peores ejemplos, para que R2 priorice.

Regla dura: si al leer textos encuentras un VALOR que te parece mal, no lo
toques ni lo anotes en un archivo nuevo: los defectos de valor se registran
como Discrepancia en src/normativa/discrepancias.py si son contra una fuente,
o se mencionan en el resumen de cierre para decisión del dueño.

Cierre: suite en verde (el linter nace en verde por el trinquete); commit
«criterios(R1): linter de estilo E1–E7 con censo trinquete»; entrega en
origin/main; conteo como par passed+skipped=collected desde origin/main, con
el entorno.
```

---

## R2 · Reescritura por lotes, con el valor congelado

Dos lotes por `nivel` (36 de perfil, 33 de expediente), no por fase: el nivel
ya está medido por corridas y agrupa mejor el vocabulario compartido. La
estructura interna del texto reescrito sigue tu orden de lectura, pero **como
convención de redacción dentro de `justificacion`**, no como campos nuevos:

> qué decide → qué dice la fuente (por referencia a su `cita_id`, no
> transcrita) → qué no resuelve la fuente → qué se adopta y bajo qué regla →
> sensibilidad (aquí sí, con los números de esta obra si los hay).

### Prompt (uno por lote; cambia solo el lote)

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md. Existe
tests/test_estilo_criterios.py (R1) con censo trinquete de violaciones.
Esta sesión reescribe la REDACCIÓN de los criterios del lote
[LOTE 1: nivel == "perfil" | LOTE 2: nivel == "expediente"] de
src/criterios_adoptados.py. La redacción, no los valores.

Antes de empezar, congela la referencia: script corto que vuelque
{clave: (valor, etiqueta, nivel, opcional, resolucion)} de ca.CRITERIOS a un
archivo temporal FUERA del repo (p. ej. /tmp/censo_pre_R2.json).

Para cada criterio del lote cuyo texto viole alguna regla E1–E7 o mezcle
registro (norma revuelta con adopción):
1. Reescribe `justificacion` con el orden: qué decide → qué dice la fuente
   (referida por su cita del registro, no transcrita — regla E5) → qué no
   resuelve → qué se adopta y con qué regla general → sensibilidad (los
   números de esta obra van aquí y solo aquí, presentados como sensibilidad).
   Presente de indicativo, impersonal, unidades SI.
2. Si el texto contiene una decisión con historia que valga conservar
   (un enfoque descartado y por qué), esa historia va a
   docs/decisiones_diferidas.md con el formato del archivo (símbolo + qué se
   difirió + por qué), no se borra ni se queda en la justificación.
3. Actualiza el censo del trinquete: la clave sale del censo de la regla que
   limpiaste. El censo solo baja.

Reglas duras:
- NINGÚN cambio en `valor`, `etiqueta`, `nivel`, `opcional`, `resolucion`,
  `sensibilidad` (la tupla numérica) ni `fuente`. Al terminar, contrasta
  ca.CRITERIOS contra /tmp/censo_pre_R2.json: cualquier diferencia aborta el
  commit. Deja el resultado de esa comparación en el resumen de cierre.
- Si al reescribir descubres que un valor o una cita está mal: NO lo
  corrijas. Regístralo como Discrepancia en src/normativa/discrepancias.py
  (si es contra una fuente, con la cita que lo sostiene) o menciónalo en el
  cierre para decisión del dueño. Reescritura y corrección nunca en el mismo
  commit — es la regla 2 de tu propio plan original, y es correcta.
- No toques criterios fuera del lote.

Cierre: suite en verde (incluido el linter con su censo reducido); commit
«criterios(R2a|R2b): reescritura de estilo del lote <perfil|expediente>, sin
cambios de valor»; entrega en origin/main; conteo como par desde
origin/main, con el entorno.
```

### Aceptación (tras los dos lotes)

- [ ] Censo del trinquete en cero para E1–E4 y E7 (E5/E6 pueden conservar
      excepciones justificadas una a una).
- [ ] `{clave: valor}` idéntico antes y después, verificado por el volcado.
- [ ] La historia con valor quedó en `decisiones_diferidas.md`, no borrada.
- [ ] Un ingeniero externo lee tres criterios al azar y explica qué decide
      cada uno (prueba manual del dueño — conservada de tu plan).

---

## R3 · La Nota 1 de F_pga — tu nota ingenieril, ahora verificable barato

Tu plan dejó una observación valiosa: si la Nota 1 de la tabla de F_pga manda
interpolar linealmente entre los valores rotulados, los rótulos extremos son
**puntos tabulados** del dominio de interpolación, y `limite_inclusive` podría
ser lectura directa de la nota — bajando el criterio de `[A]` a `[N]` o
`[N→]`. En tu plan eso costaba una verificación incierta; hoy es barato: la
tabla `MP.TFPGA` está transcrita **completa en `src/normativa/tablas.py`, con
sus 2 notas al pie como `Verbatim` verificados contra el PDF del Manual de
Puentes**.

### Prompt

```
Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md, en particular la
jerarquía de fuentes (hoja de ruta > conocimiento previo; fuente primaria en
normas/ > hoja de ruta, solo con verificación de numeral + página + texto
literal) y la taxonomía de etiquetas. Plan mode: sí — decide antes de tocar.

Objeto: el criterio de lectura de columna extrema de F_pga en
src/criterios_adoptados.py (localízalo por clave; contiene «F_pga» y
«extrema» o similar) y la tabla MP.TFPGA de src/normativa/tablas.py, cuyas
notas al pie ya están transcritas como Verbatim verificados.

Tarea:
1. Lanza el subagente verificador-normativo sobre la Nota 1 de la tabla de
   F_pga del Manual de Puentes: texto literal, numeral, página. Pregunta
   concreta: ¿el texto de la nota sostiene que los valores rotulados son los
   puntos entre los que se interpola, y que fuera del intervalo rotulado el
   factor queda definido por la columna extrema? ¿O la nota calla sobre el
   caso «PGA exactamente igual al rótulo extremo»?
2. Con la respuesta:
   a. Si la nota RESUELVE el caso: la lectura deja de ser elección. Sigue el
      protocolo de la fuente primaria si hay discrepancia con la hoja de
      ruta (declarar en el punto de uso con la cita; reportar el defecto
      contra la hoja de ruta; dejar dicho que sigue mal mientras no se
      corrija). Reetiqueta el criterio a lo que corresponda ([N] si es
      lectura directa del texto, [N→] si es analogía), ajusta su
      justificacion (estilo del plan R), conserva la cita con su Verbatim, y
      revisa qué guardias dependen de la etiqueta ([A] de perfil exige
      sensibilidad y resolucion — _verificar_nivel).
   b. Si la nota NO lo resuelve: el criterio queda [A] como está, y lo que
      se gana es dejar ESCRITO en su justificación que la nota fue
      verificada y qué dice y qué calla — con AfirmacionNegativa del
      registro si corresponde (que_no_dice + ambito_barrido), que es
      exactamente el tipo que existe para esto.
3. Lanza auditor-adversarial sobre tu conclusión antes de commitear.

Regla dura: no cambies el VALOR adoptado (limite_inclusive) en ningún caso;
esta sesión decide su etiqueta y su sustento, no su contenido.

Cierre: suite en verde; commit «criterios(R3): verificación de la Nota 1 de
F_pga y reetiquetado si corresponde — <resultado>»; entrega en origin/main;
conteo como par desde origin/main, con el entorno. Si reetiquetaste, di
explícitamente en el cierre cuál de las tres obligaciones de la fuente
primaria ejecutaste y dónde.
```

---

## Fuera de alcance del plan R

- Cambiar valores adoptados (si aparecen mal, van como `Discrepancia` o a
  decisión del dueño).
- Migrar el esquema de `Criterio`. Si tras R2 sobrevive una necesidad real de
  un campo (p. ej. `que_no_resuelve` estructurado), se propone entonces, con
  los textos ya limpios como evidencia — no antes.
- Tocar la hoja de ruta v8 (eso es del plan I, con su protocolo).
