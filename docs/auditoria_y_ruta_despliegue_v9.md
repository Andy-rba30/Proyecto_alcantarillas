# Auditoría del estado actual y ruta de cierre para despliegue

*Documento de trabajo. Reemplaza a la versión anterior de esta guía.*

---

## 0. Lo que no se pudo auditar

**El archivo `memoria_alcantarillas.html` que se subió es la plantilla, no el reporte generado.**
Contiene 19 marcadores `%%` sin sustituir (`%%proyecto`, `%%version_hoja_ruta`,
`%%bloque_criterios`…). Es `src/plantillas/memoria_alcantarillas.html`, no la salida de M11.

Para auditar el reporte real hace falta:

```bash
python cli.py tests/ejemplo_puntos.csv --html
```

y localizar el archivo **de salida** (no el de plantilla). La revisión del producto final —
separación de bloques, si algún `[A]` se lee como `[N]`, claridad del bloqueo de C-01 — queda
pendiente de eso.

Lo que sí se puede decir de la plantilla: su estructura es correcta. Los cuatro bloques están
en el orden debido, el encabezado de trazabilidad tiene los siete campos, la nota que explica
por qué los pendientes van separados está redactada con precisión, y el comentario de cabecera
documenta el propio bug del `%%` que la regla atrapó. La plantilla no es el problema.

---

## 1. El hallazgo que define en qué estado está el proyecto

**25 de los 31 criterios `[A]` están sin valor.** Invocar cualquiera lanza
`CriterioPendienteError` y detiene el cálculo.

Consecuencia directa, verificable en la propia corrida: **hoy el programa no puede completar el
diseño de ningún punto crítico.** No por un defecto — por diseño. La arquitectura de gobierno de
criterios está haciendo exactamente lo que se construyó para hacer: negarse a producir un número
que no puede sostener.

Esto obliga a separar dos cosas que se confunden al hablar de "listo para desplegar":

| | Estado |
|---|---|
| **El software como herramienta** | Terminado. 13 módulos, 743 passed + 1 skipped (744 collected), GUI, exportación con trazabilidad |
| **El expediente como cálculo de ingeniería** | Bloqueado. Faltan 25 decisiones y datos que ninguna línea de código puede inventar |

Desplegar hoy es correcto y útil — la herramienta funciona. Lo que no existe todavía es un
diseño terminado que exportar con ella. Las secciones 3 a 5 son la ruta para cerrar eso.

---

## 2. Defectos reales encontrados en la auditoría

### 2.1 Ruptura de trazabilidad: el repo tiene la v7, no la v8

`CLAUDE.md` declara: *"Fuente normativa única: docs/hoja_de_ruta_alcantarillas_v7.md"*, y el repo
solo contiene la v7 — así lo reportó la sesión de la Parte 14.

Pero `ke_entrada` (el vacío del coeficiente de pérdida de entrada, descubierto durante la Parte 0)
se documentó en la **v8**, que nunca entró al repo. Resultado: **hay un criterio en el código cuya
justificación normativa no está en el documento que el propio proyecto declara como fuente de
verdad.** Es exactamente el tipo de deriva silenciosa que el sistema de trazabilidad existe para
impedir.

**Corrección:** subir la v8 a `docs/`, borrar la v7 del repo (M11 hace glob sobre
`hoja_de_ruta_alcantarillas_v*.md` y se detiene con `ValueError` si encuentra dos), y actualizar la
referencia en `CLAUDE.md`. Cambia el SHA-1 del encabezado de trazabilidad, que es justamente lo
que debe pasar.

### 2.2 `constantes_normativas.py` se contradice a sí mismo

Su docstring admite solo `[N]` **"con numeral verificado"**. Nueve entradas no tienen numeral:

`G`, `COMPACTACION_CORONA`, `COMPACTACION_CUERPO`, `CALICATAS_POR_KM`, `ESPACIAMIENTO_PERFIL_KM`,
`SPT_ESPACIAMIENTO`, `K_FRICCION_SI`, `h_o`, `Ks`, `D_MAX`/`D_PASO`.

*(Corrección respecto de una versión anterior de este documento: `ZONA_SISMICA_LA_UNION` y
`Z_E030` sí tienen numeral correcto — Anexo II y Art. 11.1 de E.030. Su problema no es falta de
numeral, es de clasificación: son dato de proyecto etiquetado como si fuera constante universal.
Se resuelven en la Etapa A.05, con el mismo tratamiento `[S]` que `PGA_roca_B`, no aquí.)*

El manifiesto ya las detectó y las marcó ⚠ — eso habla bien del proceso. Pero siguen ahí, con
etiqueta `[N]`, sosteniendo cálculos. Dos se pueden cerrar hoy con lo que ya se extrajo de las
normas en su momento:

| Constante | Numeral que le corresponde |
|---|---|
| `COMPACTACION_CORONA` / `COMPACTACION_CUERPO` | Manual de Suelos, num. 3.2.1, 3.2.2, 3.3 y 9.1(1) |
| `CALICATAS_POR_KM` / `ESPACIAMIENTO_PERFIL_KM` | Manual de Suelos, num. 4.2, Cuadro 4.1 |

Las otras cinco son de naturaleza distinta y se tratan en 2.3 y en la verificación de NotebookLM.

### 2.3 `G = 9.8` atribuido al Manual de Hidrología — y dos valores de *g* conviviendo

Dos problemas encadenados:

**El primero es de categoría.** La aceleración de la gravedad es una constante física, no una
exigencia normativa. Atribuirla a un manual vial peruano es un error de tipo: si mañana alguien
verifica ese "numeral" contra el PDF, no va a encontrar nada, y va a concluir —erróneamente— que
hay una cita inventada.

**El segundo es de consistencia.** `G = 9.8` m/s² convive con `GAMMA_AGUA_KN_M3 = 9.81` kN/m³.
Pero γ_agua = ρ·g = 1000 × g, así que 9.81 kN/m³ implica g = 9.81 m/s². **El proyecto usa dos
valores distintos de la misma constante física en dos módulos distintos.** La magnitud del error
es despreciable (0.1 %), pero un revisor que lo note tiene razón en preguntarlo.

**Resolución sugerida:** `G = 9.8` sí tiene fundamento como valor **prescrito para la fórmula de
Laushey** — el Manual la enuncia con esa constante y la constante 3.1 está calibrada con ella. Lo
correcto es acotarlo: `G_LAUSHEY = 9.8` con su numeral (4.1.1.3.7 c), usado solo en M6, y una
constante física `G = 9.81` para todo lo demás, fuera del archivo de constantes normativas
(pertenece a la misma categoría que las tolerancias: no responde "¿qué exige la norma?").

### 2.4 `NF_profundidad_m = 1.4` está etiquetado `[N]` y no lo es

Es un **dato de sitio** que viene del EMS, no una exigencia normativa. Su propia justificación lo
delata: cita secciones de la hoja de ruta, no un numeral de norma. Ningún manual del MTC dice que
el nivel freático de La Unión esté a 1.4 m — lo dice tu estudio de suelos.

Que esté como `[N]` significa que la memoria de cálculo lo va a presentar como respaldado por norma,
cuando su respaldo real es un ensayo de campo. La etiqueta correcta es `[A]` con
`reemplazado_por` = el EMS definitivo, o mejor aún: **debería ser una columna del CSV**, porque el
NF varía a lo largo de 5 km y hoy está congelado como constante única para todos los puntos.

---

## 3. El vacío normativo genuino que descubrió la implementación

Este es el hallazgo más valioso de toda la construcción, y no lo detectó ninguna de las ocho
versiones de la hoja de ruta:

> **`umbral_area_quebrada_importante_ha` = None — bloquea el TR de toda la Familia A.**
>
> El Manual de Hidrología entrega R y n para "quebradas importantes" y para "quebradas menores"
> (Tabla N° 02, num. 3.6), pero **nunca define dónde está la frontera entre ambas**. No hay umbral
> de área, de longitud de cauce ni de caudal.

La consecuencia práctica es directa: el TR de tus alcantarillas de paso es 71 años o 35 años según
una clasificación que la norma exige pero no define. Es una diferencia del doble en el periodo de
retorno, decidida por un criterio que hoy no tiene fuente.

Lo mismo ocurre, con menor impacto, con **`TR_evento_extremo`** (V8): el Manual pide verificar
ante evento extremo pero no fija el TR de esa verificación.

Ambos van a la verificación de NotebookLM como **afirmación negativa a confirmar** — no para
buscar el numeral, sino para confirmar que efectivamente no existe. Si se confirma, se convierten
en `[A]` con justificación explícita, y esa justificación es material de defensa en la
sustentación: *"la norma exige clasificar sin dar el criterio de clasificación; se adopta X por
las siguientes razones"*.

---

## 4. Ruta de cierre — qué hacer, en orden

### Etapa A.0 · Diagnóstico: dato de proyecto disfrazado de constante universal

**Nuevo tipo de defecto, distinto al que atrapó el manifiesto de citas.** Ese manifiesto verifica
si el numeral citado existe y dice lo que el código afirma. Este diagnóstico pregunta algo
distinto: **aunque el numeral sea real y la cita sea fiel, ¿el valor que cuelga de él es portable
a otro proyecto, o es un hecho de ubicación/suelo/ensayo específico de este expediente?**

El patrón ya apareció dos veces sin que se buscara sistemáticamente: `ZONA_SISMICA_LA_UNION` y
`Z_E030` citan correctamente E.030, pero "La Unión está en Zona 4" es un hecho de dónde está este
proyecto — en otra provincia sería otra zona. Lo mismo con `NF_profundidad_m` (§2.4): el numeral
que lo sostiene no es un numeral, es tu EMS. Antes de aplicar la Etapa A, conviene encontrar
**todos** los casos de este tipo, no solo los que se detectaron por accidente.

**Prompt para Claude Code:**

> "Audita `constantes_normativas.py`, `criterios_adoptados.py` y los docstrings de
> `src/modulos/*.py` buscando un defecto de clasificación distinto al que ya corrigió el
> manifiesto de citas: variables etiquetadas `[N]` que citan un numeral real y verificable de la
> norma, pero cuyo VALOR depende de una característica propia de este proyecto (ubicación
> geográfica, perfil de suelo del EMS, resultado de un ensayo) y no de la norma en sí.
>
> El criterio de diagnóstico es este: para cada variable etiquetada `[N]`, pregúntate —
> *"si este software se usara para diseñar una alcantarilla en otra vía, en otra provincia, con
> otro suelo, ¿este valor seguiría siendo el mismo?"*. Si la respuesta es NO porque depende de
> dónde está o qué características tiene ESTE proyecto, la variable está mal clasificada, aunque
> el numeral que cita sea correcto y verificable.
>
> Ejemplo ya confirmado en la auditoría (no lo reproceses, solo úsalo como patrón):
> `ZONA_SISMICA_LA_UNION` y `Z_E030` citan E.030 correctamente, pero "La Unión está en Zona 4" es
> un hecho de ubicación de este proyecto, no una constante universal — en otra provincia sería
> otra zona. Aplica exactamente esta misma lógica a TODAS las demás variables del archivo, sin
> asumir que son las únicas dos.
>
> Para cada variable que cumpla el criterio, genera una tabla con columnas: **Variable** |
> **Archivo:línea actual** | **Etiqueta actual** | **Numeral que cita** | **Por qué es dato de
> proyecto y no constante universal** | **Etiqueta correcta según la taxonomía de CLAUDE.md**
> (revisa ahí qué significa exactamente `[N→]` antes de proponerlo — si encaja con "valor resuelto
> al aplicar una tabla normativa a una condición específica de este proyecto", ese es candidato
> natural; si no encaja, dilo y propone qué hacer) | **Ubicación correcta sugerida** (¿debe seguir
> en `constantes_normativas.py` con otra etiqueta, moverse a un archivo de datos de proyecto, o
> convertirse en columna del CSV como se decidió para `NF_profundidad_m`?).
>
> No corrijas nada todavía — este es un manifiesto de diagnóstico, igual que el de citas. Si
> encuentras un caso ambiguo, inclúyelo en la tabla con una columna adicional
> `DUDA: [explica la ambigüedad]` en vez de decidir por tu cuenta.
>
> Guarda el resultado en `docs/manifiesto_datos_proyecto_vs_constantes.md`."

> **Estado: completado.** El manifiesto encontró 4 casos (más allá de `ZONA_SISMICA_LA_UNION`/
> `Z_E030`, ya confirmados antes): `PERFIL_SUELO_PRESUNTO` (referencia muerta, fácil), `PGA_roca_B`
> (el de mayor impacto — alimenta la cadena sísmica de todos los puntos), `factor_muro` (caso
> limpio, mismo patrón que `F_pga`) y `NF_profundidad_m` (confirma lo ya señalado en §2.4). Tres de
> los cuatro quedaron marcados `DUDA` porque ninguna de las cuatro etiquetas existentes describe
> con precisión "un hecho de sitio, obtenido con un procedimiento normativo real, que nadie eligió
> — se leyó o se midió". La resolución de esa duda está en la Etapa A.05.

### Etapa A.05 · Decisión de taxonomía: quinta etiqueta `[S]`

**Se resuelve que sí hace falta.** `[A]` no encaja para un dato que no tiene margen de elección:
nadie "adopta" dónde está el nivel freático, se mide; nadie "adopta" el PGA de un punto, se lee en
un mapa en una coordenada fija. Forzarlos a `[A]` los hace ver como criterio de ingeniería
discutible cuando en realidad son procedimiento normativo aplicado a un hecho de sitio — y el
campo `sensibilidad`, obligatorio para `[A]`, no tiene sentido para una medición de campo.

**Definición de la nueva etiqueta:**

> **`[S]` — Dato de sitio.** Obtenido mediante un procedimiento normativo real (mapa, ensayo,
> medición de campo) aplicado a las coordenadas o condiciones de este proyecto. No es elección del
> proyectista ni analogía: es un hecho determinado, no portable a otro proyecto. En vez de
> `sensibilidad`, declara **trazabilidad obligatoria**: el procedimiento exacto, la fuente, y si el
> dato aplica a todo el corredor o varía punto a punto.

**Prompt para Claude Code — implementa la etiqueta y las cuatro correcciones en la misma sesión**
(están acopladas: no se puede retaguetar sin que la etiqueta exista primero):

> "Implementa la quinta etiqueta `[S]` (Dato de sitio) según esta definición: [pega la definición
> de arriba]. Cambios necesarios:
>
> (1) Actualiza el docstring de `criterios_adoptados.py:22-28` con las cinco etiquetas.
> (2) Actualiza `CLAUDE.md` — la taxonomía de etiquetas ahora tiene cinco valores, no cuatro.
> (3) En el template de M11 (`memoria_alcantarillas.html`): añade `.et-S` al CSS (sugiero un tono
> distinto de N, N→, C y A — es una categoría propia, no una variante de ninguna de las otras
> cuatro) y su entrada en la leyenda de etiquetas de la Sección 3.
> (4) En `reporte_criterios()`, añade `S` al diccionario `_ORDEN`, entre `N→` y `C`.
> (5) Reemplaza el campo `sensibilidad` por `trazabilidad` (string) para los criterios `[S]` —
> mantén `sensibilidad` como estaba para `[A]`, `[S]` no lo usa.
> (6) Crea `src/datos_sitio.py`, paralelo a `tolerancias.py`/`dominios.py` pero de naturaleza
> distinta: no son valores no-de-proyecto, son datos de sitio válidos para todo el corredor (a
> diferencia de una columna del CSV, que varía punto a punto). Documenta la distinción en su
> docstring.
>
> Ahora las cuatro correcciones del manifiesto:
>
> (a) `PERFIL_SUELO_PRESUNTO`: mover de `constantes_normativas.py` a `criterios_adoptados.py`,
> junto a `clase_sitio`, mismo `reemplazado_por` = 'Ensayo SPT'. Es referencia muerta hoy (no la
> usa ningún módulo) — verifícalo y déjalo documentado como tal.
>
> (b) `PGA_roca_B`: antes de decidir su ubicación, verifica en el mapa del Apéndice A3 si la curva
> de isoaceleración cambia dentro de los 5 km del corredor. Si no cambia apreciablemente: etiqueta
> `[S]`, mover a `src/datos_sitio.py` como dato de todo el proyecto, con trazabilidad = coordenadas
> exactas de lectura. Si sí cambia: columna del CSV en su lugar, mismo tratamiento que
> `NF_profundidad_m`.
>
> (c) `factor_muro`: separar en dos. `FACTOR_MURO_TABLA = {'rigido': 1.0, 'desplazable': 0.5}` a
> `constantes_normativas.py`, etiqueta `[N]`, numeral 2.8.1.1.14.2. La elección de cuál fila aplica
> a este cabezal queda en `criterios_adoptados.py` como `factor_muro_eleccion`, etiqueta `[A]`,
> sensibilidad `(0.5, 1.0)`, con la justificación ya escrita hoy ('cabezal empotrado, sin
> desplazamiento admisible garantizado'). Mismo patrón exacto que ya tiene `F_pga`.
>
> (d) `NF_profundidad_m`: etiqueta `[S]`, se convierte en columna del CSV. Actualiza `modelos.py`
> (`PuntoCritico`), `M0_carga.py` (`COLUMNAS`) y cualquier módulo que hoy lo invoque desde
> `criterios_adoptados`. Con un solo valor en `tests/ejemplo_puntos.csv` hoy, decide si repites
> 1.4 en las cuatro filas o declaras que varía — lo segundo es más honesto si no tienes evidencia
> de que sea uniforme en todo el tramo.
>
> (e) `ZONA_SISMICA_LA_UNION` y `Z_E030`: mismo tratamiento que (b) — son la lectura de un mapa de
> zonificación en las coordenadas de este proyecto. Etiqueta `[S]`, mover de
> `constantes_normativas.py` a `src/datos_sitio.py`, trazabilidad = Anexo II y Art. 11.1 de E.030
> más la ubicación exacta consultada. Recuerda que el propio proyecto ya decidió que estos dos
> valores **no gobiernan** el diseño del cabezal (Sec. 0.4 de la hoja de ruta) — quedan como
> referencia, así que el cambio es solo de clasificación, no de uso.
>
> Regenera `docs/manifiesto_citas.md` y `docs/manifiesto_datos_proyecto_vs_constantes.md` al final
> para reflejar el estado nuevo, y corre la suite completa."

**Gate:** las cinco etiquetas documentadas en los tres lugares que las citan (docstring, CLAUDE.md,
template HTML); `factor_muro_eleccion` sigue exactamente el patrón de `F_pga`; `NF_profundidad_m`
ya no existe en `criterios_adoptados.py`; suite en verde.

> **Estado: completado.** Las seis correcciones se aplicaron (a-e, más `ZONA_SISMICA_LA_UNION` que
> se sumó a la lista sin necesidad de otra sesión). Dos decisiones de valor, no solo de forma:
> `PGA_roca_B` no pudo cerrarse contra evidencia — el mapa del Apéndice A3 no está en el repo y la
> coordenada de lectura nunca se registró, así que se aplicó la rama que no exige inventar un dato
> (dato de todo el proyecto, no columna del CSV), con la trazabilidad declarando explícitamente que
> la comprobación de los 5 km sigue sin resolverse. Y `criterios_adoptados.py` quedó sin ningún
> criterio `[N]` — invariante nueva, con test propio: si alguna vez aparece un `[N]` ahí, es
> sospechoso por definición, porque ese archivo es para `[N→]`, `[S]`, `[C]` y `[A]`, no para
> universales verificados (eso vive en `constantes_normativas.py`).
>
> **Pendiente real que queda de A.05:** la comprobación del mapa de isoaceleración (¿varía dentro
> de los 5 km?) no se resolvió, se evitó. Si en algún momento consigues el PDF del Apéndice A3 y
> puedes leer la coordenada real de cada punto crítico, esa es la ocasión de decidir si `PGA_roca_B`
> se queda en `datos_sitio.py` o pasa a columna del CSV — no antes.

### Etapa A · Cierre de trazabilidad restante (una sesión corta, ~15 min)

Con A.05 hecho, solo quedan tres ítems del alcance original de esta etapa — los otros dos
(`NF_profundidad_m`, regenerar manifiestos) ya los resolvió A.05:

> "Tres correcciones de trazabilidad:
> (1) `CLAUDE.md` sigue nombrando `docs/hoja_de_ruta_alcantarillas_v7.md` como fuente normativa
> única, pero ese archivo ya no existe (está la v8). Actualiza la referencia y confirma que el glob
> de M11 (`hoja_de_ruta_alcantarillas_v*.md`) sigue encontrando una sola hoja.
> (2) Cierra los numerales faltantes que sí los tienen: `COMPACTACION_CORONA`/`COMPACTACION_CUERPO`
> → Manual de Suelos num. 3.2.1, 3.2.2, 3.3 y 9.1(1); `CALICATAS_POR_KM`/`ESPACIAMIENTO_PERFIL_KM`
> → Manual de Suelos num. 4.2, Cuadro 4.1.
> (3) Separa `G`: crea `G_LAUSHEY = 9.8` con numeral 4.1.1.3.7 c), usado solo en M6. Mueve la
> constante física `G = 9.81` fuera de `constantes_normativas.py` — hoy conviven g=9.8 (en G) y
> γ_agua=9.81 (que implica g=9.81): dos valores de la misma constante en el proyecto.
> Corre la suite completa al final."

> "Cinco correcciones de trazabilidad:
> (1) La hoja de ruta del repo es la v7; la v8 (que documenta `ke_entrada`) nunca se subió. Voy a
> subir `docs/hoja_de_ruta_alcantarillas_v8.md` — bórrala v7 del repo y actualiza la referencia en
> `CLAUDE.md`. Verifica que el glob de M11 detecte una sola hoja.
> (2) Cierra los numerales faltantes de `constantes_normativas.py` que sí los tienen:
> `ZONA_SISMICA_LA_UNION` → E.030 Anexo II; `Z_E030` → E.030 Art. 11.1 Tabla N° 1;
> `COMPACTACION_CORONA`/`COMPACTACION_CUERPO` → Manual de Suelos num. 3.2.1/3.2.2/3.3/9.1(1);
> `CALICATAS_POR_KM`/`ESPACIAMIENTO_PERFIL_KM` → Manual de Suelos num. 4.2, Cuadro 4.1.
> (3) Separa `G`: crea `G_LAUSHEY = 9.8` con numeral 4.1.1.3.7 c) usado solo en M6, y mueve la
> constante física `G = 9.81` fuera de `constantes_normativas.py` (misma categoría que
> `tolerancias.py`: no responde a qué exige la norma). Hoy conviven g=9.8 y γ_agua=9.81, que
> implica g=9.81 — dos valores de la misma constante.
> (4) `NF_profundidad_m` está como `[N]` y es un dato de sitio del EMS, no una exigencia
> normativa. Reetiquétalo `[A]` con `reemplazado_por` = EMS definitivo, y añade una nota de que
> debería migrar a columna del CSV porque el NF varía a lo largo de los 5 km.
> (5) Regenera `docs/manifiesto_citas.md` con todo lo anterior aplicado."

### Etapa B · Verificación normativa con NotebookLM (trabajo tuyo, fuera de Claude Code)

Sube los PDF (los enlaces están en `notebooklm_extraccion_normativa.md`) y corre **un prompt por
bloque del manifiesto**:

```
Voy a darte afirmaciones que un software de ingeniería hace sobre este documento
normativo. Para cada una, dime si el numeral citado dice lo que la afirmación
sostiene, con página y cita textual corta. Responde SOLO con una etiqueta por fila:

CONFIRMADO — el numeral existe y dice lo que la afirmación sostiene
DISCREPANCIA — el numeral existe pero dice algo distinto (explica la diferencia)
NO ENCONTRADO — el numeral no existe o no pude ubicarlo

No completes ni corrijas la afirmación tú mismo. Si dudas, usa NO ENCONTRADO en vez
de adivinar.

Afirmaciones a verificar:
[pega el bloque del manifiesto correspondiente]
```

**Prioridad de bloques** (no hace falta hacerlos todos de golpe):

| Orden | Bloque | Por qué primero |
|---|---|---|
| 1 | §1 Manual de Hidrología | 30 citas, gobierna Fases 2 a 6, y contiene las dos afirmaciones negativas críticas (§3) |
| 2 | §4 E.050 | 16 citas, toda la tabla de factores de seguridad de la Fase 9 |
| 3 | §3 Manual de Puentes | 20 citas, incluye el PGA y la cadena sísmica |
| 4 | §7 HDS-5 | Incluye `Ks`, que el propio código declara que no está en la Tabla A.1 |
| 5 | §2, §5, §6 | Manual de Suelos, E.060, EG-2013 |
| 6 | §9 Normas de producto | `D_MAX` lleva "VERIFICAR" escrito en el código y sus topes descartan materiales enteros |

**Además de las filas del manifiesto, incluye estas tres preguntas explícitas — cada una en el
prompt del bloque que le corresponde, no en uno genérico:**

**Dentro del prompt de §1 (Manual de Hidrología), añade:**

1. *"¿El Manual define en algún lugar el umbral que separa 'quebrada importante' de 'quebrada
   menor' — por área, longitud de cauce o caudal? Si no lo define, dilo expresamente."*
2. *"¿El Manual fija un periodo de retorno para la verificación ante evento extremo, distinto del
   TR de diseño?"*

**Dentro del prompt de §7 (HDS-5), añade:**

3. *"¿De dónde sale el coeficiente Ks (−0.5 sin inglete, +0.7 con inglete)? ¿Está en el Apéndice
   A, en el cuerpo del capítulo, o en otro lugar del documento?"*

Van con esos bloques y no con otros porque las preguntas 1 y 2 solo tienen sentido con la Tabla
N° 02 (R y n) delante — es ahí donde falta el criterio de clasificación — y la pregunta 3 solo se
puede responder con la Tabla A.1 de HDS-5 a la vista, que es donde el propio código declara no
haber encontrado a Ks.

> **Estado: 7 de 9 bloques verificados.** Faltan **Manual de Puentes** (§3, 20 citas, incluye la
> cadena sísmica completa) y **AASHTO LRFD** (§8, los 9 criterios de la Etapa C.2) — se subieron sin
> contenido legible, hay que reintentarlos. Los hallazgos de los 7 bloques cerrados están abajo.

### Resultado de la Etapa B — hallazgos de los 7 bloques verificados

Los siete reportes son de calidad alta y en su mayoría confirman lo que ya estaba en el código.
Lo que sigue es lo que **sí requiere una corrección**, ordenado por severidad. Los detalles menores
de formato (una página mal citada, una nota que precisa una palabra) no están aquí — están en el
prompt de cierre.

#### Crítico — verificar antes que nada

**`CUANTIA_MIN_MURO` puede estar declarada pero no aplicada.** El verificador de E.060 marcó esto
como discrepancia grave: 0.0020 (horizontal) y 0.0015 (vertical) no son informativas, son **piso
obligatorio** del refuerzo (Art. 14.3.1), y bajo cortante alto suben a 0.0025 (Art. 11.10.10.2,
aplicable a muros con responsabilidad sísmica vía Art. 21.9.4.1). La hoja de ruta v7/v8, en §9.4,
las describe como *"referencia de cuantías mínimas... como contraste"* — esa palabra, "contraste",
es la señal de alarma: si M9 solo las imprime en el reporte sin forzar
`ρ_diseño ≥ max(ρ_calculado, ρ_mínimo)` en el cálculo real de refuerzo, el software puede estar
generando una cuantía insuficiente sin que ninguna verificación lo detecte. **Esto no se resuelve
en el chat — se verifica leyendo `M9_cabezal.py`.** Va primero en el prompt de cierre.

#### Alto — decisiones de metodología, no solo de cita

**Corrección a mí mismo: `K_FRICCION_SI` debería ser 19.63, no 19.62.** Hace unas sesiones celebré
que 2×9.81 = 19.62 coincidiera "elegantemente" con la constante — la presenté como si esa
coincidencia explicara su origen. El verificador de HDS-5 encontró el texto exacto:
*"KU = 29 in English Units (19.63 in SI)"* — **el propio documento fija 19.63 como la conversión
de su constante 29**, no 19.62. La diferencia es de 0.05 %, irrelevante en magnitud, pero la
"elegancia" que atribuí a 2×g era una coincidencia numérica sin respaldo en la fuente, y hay una
fuente primaria que sí lo fija. Corregir a 19.63, y quitar la justificación "= 2×g" — no es de
donde sale el número.

**La transición del HDS-5 no es interpolación lineal.** Toda la arquitectura de M4 (y el caso
patrón CP-5) asume interpolación lineal entre q\*=3.5 y q\*=4.0. El verificador encontró que el
propio HDS-5 dice que esa zona se resuelve *"empirically by drawing a curve between and tangent
to..."* — con curvas tangentes, no con una recta. Dos caminos, ninguno automático:
(a) declarar la interpolación lineal como simplificación adoptada **[C]**, con justificación
explícita de por qué es razonable en una zona angosta; o (b) implementar el método real. Dado el
nivel de perfil del proyecto, (a) es defendible — pero tiene que decirse, no dejarse como si fuera
el método literal del HDS-5.

**`clase_sitio` puede estar confundiendo dos ensayos con requisitos de profundidad distintos.**
El SPT de 15 m / cada 1 m (E.050 Art. 38) es para **licuefacción**. La clasificación de sitio
AASHTO/E.030 (Clase F, la que motiva la excepción de periodo corto) requiere caracterizar **los
primeros 30 m**, con parámetros distintos (N̄60, Vs30 o Su). Son ensayos relacionados pero no
intercambiables: un SPT de 15 m resuelve la pregunta de licuefacción y **no necessarily** resuelve
la de clasificación de sitio. Si `criterios_adoptados.py` dice `reemplazado_por='Ensayo SPT'` sin
distinguir la profundidad exigida para cada propósito, hay que separarlo en dos.

**`CALICATAS_POR_KM` no aplica el multiplicador "por sentido" en autopistas/duales.** Bajo, porque
tu vía no es autopista ni dual — pero es un error real de la constante que vale la pena cerrar
ahora que se sabe, antes de que el proyecto crezca o se reutilice el código.

#### Positivo — pendientes que este trabajo cerró solo

- **`ke_entrada`**: cita exacta, Apéndice C, Tabla C.2, pág. C.2. Ya no queda "verificación
  pendiente" en ese criterio.
- **`HW_D_max`**: confirmado como rango típico 1.0–1.5 (Sec. 2.2.5, pág. 2.14). También cierra.
- **`umbral_area_quebrada_importante_ha`**: confirmado formalmente que el Manual **no** lo define
  — la Tabla N° 02 da R y n por categoría pero no la regla de asignación física. Ya no es una
  sospecha, es un vacío normativo confirmado con evidencia citable. Listo para cerrarse como
  `[A]` en la Etapa C.1 con esta cita como justificación.
- **Hallazgo con valor propio, no pedido**: el **Art. 7.3 de E.030** es la base legal explícita de
  por qué el proyecto usa el Manual de Puentes en vez de E.030 directamente para el cabezal —
  *"mientras no se cuente con normas nacionales específicas para estructuras tales como... puentes...
  se deben utilizar los valores... amplificados... sustentado por el proyectista"*. Como el MTC sí
  tiene esa norma sectorial (el Manual de Puentes), el proyecto está exactamente en el supuesto que
  el propio Art. 7.3 contempla. Esto no estaba citado en ningún lado de la hoja de ruta — conviene
  agregarlo a §0.2 como el respaldo legal de la Vía 1.

#### Matizado — hallazgo real, pero presentado con más alarma de la que corresponde

El verificador de E.030 califica el `PERFIL_SUELO_PRESUNTO` inerte como *"violación crítica de
seguridad"*. El hallazgo de fondo es correcto (está inerte, ya lo sabíamos desde el manifiesto de
datos de proyecto), pero la calificación de "crítico" no tiene el contexto completo: la Fase 0-bis
de la hoja de ruta ya declara la licuefacción como *"el condicionante técnico no resuelto"* del
proyecto y exige el SPT antes del expediente — no es un descuido, es una decisión de alcance de
perfil ya documentada. Vale la pena, eso sí, la mejora que sugiere: una advertencia activa en la
interfaz si se detecta suelo licuable sin SPT, en vez de solo quedar como referencia muerta en el
código. Baja prioridad, no urgente.

Igual de matizado el riesgo de "La Unión" homónima entre departamentos — válido como
consideración si este software se reutiliza algún día para otro proyecto, pero hoy
`ZONA_SISMICA_LA_UNION` es una constante fija para *este* expediente, no una función que busque
distritos por nombre. No es un defecto activo.

### Prompt de cierre — Etapa B, primera tanda (7 de 9 bloques)

> "Verificación normativa externa encontró correcciones reales. En orden de prioridad:
>
> (1) **Verifica primero, no asumas:** abre `M9_cabezal.py` y confirma si `CUANTIA_MIN_MURO` se
> usa como piso obligatorio en el cálculo de refuerzo (`ρ_diseño = max(ρ_calculado, ρ_mínimo)`) o
> solo se imprime en el reporte como referencia. Si es lo segundo, corrígelo — es un mínimo
> normativo obligatorio (E.060 Art. 14.3.1), no informativo. Añade el escalón a 0.0025 bajo
> cortante alto (Art. 11.10.10.2) si el módulo ya calcula cortante; si no lo calcula, decláralo
> como pendiente explícito, no lo omitas en silencio.
>
> (2) `K_FRICCION_SI`: cambiar de 19.62 a **19.63** — es el valor que el propio HDS-5 declara como
> conversión de su constante K=29. Quita cualquier justificación basada en "2×g" — era una
> coincidencia numérica sin respaldo en la fuente primaria, no el origen real de la constante.
> Actualiza los valores dorados de `casos_patron.py` (CP-8) con el nuevo K_FRICCION_SI.
>
> (3) La transición del HDS-5 (3.5 < q\* < 4.0): declara explícitamente en el docstring de M4 que
> la interpolación lineal es una **simplificación adoptada `[C]`**, no el método literal del
> HDS-5 (que usa curvas tangentes empíricas). Añade la entrada correspondiente a
> `criterios_adoptados.py` con esta justificación.
>
> (4) Separa `clase_sitio` en dos requisitos de profundidad: el SPT de licuefacción (15 m, E.050
> Art. 38) y la caracterización de sitio para la Clase F/excepción de periodo corto (30 m, criterio
> AASHTO/E.030). Actualiza `reemplazado_por` en ambos criterios para que cada uno pida la
> profundidad que le corresponde.
>
> (5) `CALICATAS_POR_KM`: agrega el multiplicador "por sentido" para autopistas y duales (Manual
> de Suelos, Cuadro 4.1).
>
> (6) Cierra las citas que ya quedaron confirmadas con evidencia nueva: `ke_entrada` (Apéndice C,
> Tabla C.2, pág. C.2), `HW_D_max` (Sec. 2.2.5, pág. 2.14, rango 1.0–1.5). Quita cualquier
> `verificacion_pendiente` que les quedara.
>
> (7) Formaliza `umbral_area_quebrada_importante_ha` como `[A]` con esta justificación: el Manual
> de Hidrología (Tabla N° 02) da R y n por categoría pero no fija ninguna regla de asignación física
> (área, caudal o longitud) para clasificar una quebrada. Cita textual disponible si la necesitas.
>
> (8) Corrige el patrón sistémico de citas compuestas: constantes como `NUMERAL_V4`, `NUMERAL_9_1`,
> `NUMERAL_8_1` y `NUMERAL_FASE_10` mezclan en un mismo string la sección interna de la hoja de
> ruta ('Sec. 9.1', '5.1', 'Fase 10') con el numeral real de la norma. Un verificador externo
> interpretó el string completo como si fuera la cita, y en el caso de `NUMERAL_8_1` el resultado
> es peor: cita una 'Sección 500' y una 'Sec. 8.1' que **no existen** en EG-2013 — error que viene
> de una simplificación mía en una versión temprana de la hoja de ruta, nunca corregida. Separa
> cada una de estas constantes en dos campos: `seccion_hoja_ruta` (navegación interna) y
> `numeral_norma` (la cita real, verificable). Para EG-2013 en particular, ninguna referencia debe
> decir 'Sección 500' — usa 'Capítulo V, Sección 502' para rellenos generales, o la sección
> específica de cada material (505/506/507/508) según corresponda.
>
> (9) Renombra `SUBSECCION` a `SECCION` en `constantes_normativas.py` — 505/506/507/508 son
> Secciones completas del EG-2013, no subsecciones.
>
> Corre la suite completa al final."

**Gate:** ítem (1) resuelto con evidencia (no una suposición); `K_FRICCION_SI = 19.63` propagado a
`casos_patron.py`; `clase_sitio` separado en dos profundidades; el patrón de citas compuestas
corregido al menos en los 4 casos confirmados; suite en verde.

### Resultado de la Etapa B — segunda tanda: Manual de Puentes y AASHTO LRFD 9ª Ed. (2020)

**Estado: los 9 bloques de la Etapa B están verificados.** Los dos que faltaban llegaron completos.
Uno de los hallazgos no es una cita mal puesta — es una pieza central de la arquitectura sísmica
que estaba apoyada en algo que no existe.

#### Crítico — la excepción de periodo corto para Clase F no existe en AASHTO LRFD

Desde la v5/v6, `§0.5` de la hoja de ruta y el criterio `clase_sitio` se apoyan en una supuesta
excepción de AASHTO LRFD Art. 3.10.3.1 que permitiría, para estructuras de periodo fundamental
corto, clasificar un sitio Clase F como si no fuera licuable y usar factores de sitio tabulados.
La v7 ya marcaba esto como "verificación pendiente" — **ahora está resuelta, y el resultado es que
la excepción no existe**:

> *"Ni en el articulado 3.10.3.1, ni en la Tabla 3.10.3.1-1, ni en el Comentario C3.10.3.1 se exime
> de realizar el estudio dinámico específico de sitio basándose en que la estructura posee un
> periodo fundamental corto."*

El reporte identifica de dónde probablemente vino la confusión: esa excepción **sí existe en ASCE
7 y en el IBC** (normas de edificaciones de EE.UU.), no en AASHTO. Y cita el mandato real de
AASHTO, sin excepciones, para Clase F:

> *"Site-specific geotechnical investigation and dynamic site response analysis should be
> performed for all sites in Site Class F."* (Nota 2, Tablas 3.10.3.2-1, -2 y -3)

**Esto no invalida la decisión de usar F_pga = 1.0 — invalida la justificación con la que se
presentó.** Decir en la memoria *"nos acogemos a la excepción de periodo corto de AASHTO"* sería
citar una disposición que no existe, y es exactamente el tipo de error que un jurado con AASHTO a
mano detecta de inmediato. La corrección no es abandonar el valor adoptado — es **dejar de
llamarlo excepción normativa y declararlo lo que es: una aproximación de perfil, adoptada a falta
del estudio de sitio que AASHTO exige sin excepción**, con ese estudio remitido al expediente
técnico junto al SPT que ya estaba pendiente por la Fase 0-bis.

**Redacción de reemplazo para la memoria** (sustituye al párrafo de la excepción en §0.5):

> *"El sitio clasifica como Clase de Sitio F por susceptibilidad a licuefacción. AASHTO LRFD
> (Art. 3.10.3.1 y Comentario C3.10.3.1) no contempla ninguna excepción a esta clasificación por
> periodo estructural corto: exige, sin excepciones, investigación geotécnica específica y análisis
> de respuesta dinámica de sitio para todo sitio Clase F (Nota 2, Tablas 3.10.3.2-1 a -3). A nivel
> de perfil, y sin el estudio de sitio específico que la norma exige, se adopta F_pga = 1.0 como
> aproximación conservadora dentro del marco tabulado, dejando expresamente declarado que esta
> adopción no satisface el requisito normativo pleno y que el estudio de respuesta de sitio queda
> diferido al expediente técnico, junto con el ensayo SPT que determina la clasificación real del
> perfil."*

Esto reclasifica el criterio: de "[C] excepción normativa aplicada" pasa a "**[A] aproximación de
perfil, declarada, con el requisito normativo pendiente explícito**" — más débil en apariencia,
pero honesto, y una adopción declarada correctamente defendida vale más en sustentación que una
cita que no resiste que la verifiquen.

#### Alto — corrección de metodología, no solo de cita

**`FS_flotacion` no debería ser un factor de seguridad clásico.** El reporte de AASHTO es tajante:
*"La Sección 12 NO desarrolla un procedimiento ni exige un factor de seguridad por flotación...
no existe... una verificación simplificada tipo ASD."* AASHTO LRFD resuelve la flotación en el
Art. 3.7.2 mediante equilibrio de factores de carga, no mediante un FS:

$$\sum \gamma_{i,\min} Q_{\text{estabilizante}} \ge \gamma_{\text{desestabilizante}} \cdot U$$

con γ_DC,mín = 0.90, γ_EV,mín = 0.90 (Tabla 3.4.1-2) y γ = 1.00 para la subpresión U (Tabla
3.4.1-1). La verificación V7 de la hoja de ruta está formulada como *"ΣW ≥ FS·U"* — hay que
cambiar la lógica, no solo la cita: la mención de un FS clásico de flotación (1.5, 1.25) es de
manuales viales empíricos, no de AASHTO LRFD, y mezclarlos sería inconsistente con la Vía 1
(AASHTO de extremo a extremo) que el propio proyecto adoptó en §0.2.

**`GAMMA_AGUA_KN_M3 = 9.81` cita mal el numeral 2.4.3.8.2** — el numeral define el concepto de
subpresión, no fija ningún valor numérico del peso específico del agua. 9.81 kN/m³ es ρ·g, una
constante física, no un valor normativo del Manual de Puentes. Mismo tratamiento que ya se le dio
a `G`: sacarla de `constantes_normativas.py` (que exige numeral verificado) y moverla a
`constantes_fisicas.py`, idealmente derivada como `GAMMA_AGUA = RHO_AGUA * G` en vez de un litearl
independiente — así un cambio futuro en G no puede dejar a las dos constantes inconsistentes entre
sí, que es el mismo tipo de error que motivó separar G de G_LAUSHEY hace varias sesiones.

**El PGA leído podría estar del lado no conservador.** El reporte encontró que las curvas de
isoaceleración en la franja costera de Piura van de **0.50 g a 0.54 g** (0.51 g "promedio
costero"). El proyecto adoptó 0.50 — el extremo *inferior* del rango, no el superior. Si la
coordenada exacta de La Unión cae más cerca de 0.54, el valor adoptado subestima la demanda
sísmica hasta en un 8 %. Esto refuerza —con evidencia nueva, no solo como formalidad— la
verificación pendiente que ya existía sobre registrar las coordenadas exactas de lectura. No se
puede cerrar sin el mapa y las coordenadas reales del punto.

#### Cierre de la Etapa C.2 — 6 de 9 criterios, con datos reales en mano

Los dos reportes entregan valores numéricos utilizables para seis de los nueve criterios que
dependían de AASHTO LRFD:

| Criterio | Valor que cierra el vacío | Fuente |
|---|---|---|
| `factores_carga_aashto` | DC 1.25/0.90, EV 1.35/0.90, EH 1.50/0.90 (activo) — tabla completa en el memo | Tabla 3.4.1-1/-2, transcrita también en el Manual de Puentes (págs. 143, 146) — puede citarse como `[N]` vía MTC, no hace falta AASHTO directo |
| `recubrimiento_aashto_mm` | 75 mm contra el suelo (Cat. A) — **mayor que los 70 mm de E.060**, así que ahora gobierna este valor por la regla "rige el mayor" de §9.4 | AASHTO Tabla 5.10.1-1, pág. 5-169 |
| `procedimiento_flexion_corte_aashto_sec5` | φ=0.90 flexión y corte; MCFT con β y θ analíticos (fórmulas completas en el memo) | Art. 5.5.4.2 y 5.7.3.4.2 |
| `peso_especifico_concreto_kn_m3` | 23.56 kN/m³ (AASHTO) — la práctica regional/MTC redondea a 24.0 kN/m³, ambos defendibles | Tabla 3.5.1-1 + Comentario C3.5.1 |
| `FS_flotacion` | Se cierra **cambiando el método**, no con un número — ver hallazgo de arriba | Art. 3.7.2 |
| `N_cq_N_gammaq_meyerhof` | Confirmado que `None` es correcto: salen de gráficos (Meyerhof 1957), no hay fórmula ni tabla discreta | Figuras 2.8.1.3.1.2c-1/-2 |

**Quedan 3 sin cerrar, y no los cierran estos documentos:** `clases_producto_por_relleno`
(necesita AASHTO M-170M, documento de producto distinto), `v_max_hdpe` y `v_max_tmc` (necesitan
PPI/FHWA). Son los de menor impacto de los nueve — quedan declarados `[A]`/`[C]` pendientes, sin
bloquear nada mientras el concreto siga siendo la opción por defecto en la matriz de decisión de
material.

### Prompt de cierre — Etapa B, segunda tanda (Manual de Puentes + AASHTO)

> "Cuatro correcciones, la primera es la más importante de todo este proyecto:
>
> (1) **Reescribe §0.5 y el criterio `clase_sitio`.** La excepción de periodo corto para Clase F
> NO EXISTE en AASHTO LRFD (verificado contra la 9ª edición, 2020: ni en el Art. 3.10.3.1, ni en su
> comentario C3.10.3.1, ni en ninguna tabla). AASHTO exige estudio de respuesta de sitio específico
> para Clase F sin excepciones. Cambia la etiqueta de `clase_sitio` de la que tenga ahora a `[A]`, y
> reemplaza su justificación por: [pega el párrafo de redacción de reemplazo de arriba]. Esto debe
> reflejarse igual en la memoria de cálculo — verifica que M11 no siga imprimiendo la palabra
> 'excepción' en ningún lado de la sección sísmica.
>
> (2) Reescribe V7 (flotación) para que use equilibrio de factores de carga LRFD en vez de un factor
> de seguridad clásico: `0.90·(DC + EV) ≥ 1.00·U`, con los factores de la Tabla 3.4.1-1/-2. Retira
> `FS_flotacion` de `criterios_adoptados.py` si ya no hace falta, o redefine qué representa.
>
> (3) Mueve `GAMMA_AGUA_KN_M3` de `constantes_normativas.py` a `constantes_fisicas.py`, derivada
> como `GAMMA_AGUA = RHO_AGUA * G` en vez de literal independiente — mismo criterio que ya se aplicó
> a G. Añade `RHO_AGUA = 1000` (kg/m³) si no existe.
>
> (4) Cierra los 5 criterios de la Etapa C.2 con los valores de la tabla de esta sección
> (`factores_carga_aashto`, `recubrimiento_aashto_mm`, `procedimiento_flexion_corte_aashto_sec5`,
> `peso_especifico_concreto_kn_m3`, `N_cq_N_gammaq_meyerhof` confirmado como `None` correcto). Para
> `recubrimiento_aashto_mm`, verifica que la regla 'rige el mayor entre AASHTO y E.060' en M9 ahora
> devuelva 75 mm y no 70 mm para concreto contra el suelo.
>
> No toques `clases_producto_por_relleno`, `v_max_hdpe` ni `v_max_tmc` — necesitan AASHTO M-170M y
> PPI/FHWA, documentos que no se han verificado todavía. Corre la suite completa al final."

**Gate:** ninguna mención de "excepción" sobrevive en el código ni en el HTML generado para la
sección sísmica; V7 usa equilibrio de cargas, no un FS; `GAMMA_AGUA` deriva de `G`; los 5 criterios
de C.2 tienen valor; suite en verde.

### Prompt de cierre — Etapa B, tercera tanda: los 4 datos de C.2 (sin criterio de por medio)

Estos cuatro no requieren ninguna decisión de ingeniería — son transcripción directa de valores ya
verificados contra AASHTO LRFD 9ª Ed. (2020). Van en un prompt aparte de los "criterios" de la
Etapa C.1 porque ahí sí hay juicio del proyectista; aquí no hay nada que decidir, solo que copiar
bien.

> "Cierra los cuatro datos de C.2 con estos valores, ya verificados — no hay decisión de ingeniería
> en ninguno, es transcripción directa:
>
> **(1) `factores_carga_aashto`** — Tabla 3.4.1-1 y 3.4.1-2, AASHTO LRFD 9ª Ed., págs. 3-14/3-18
> (también transcritas en Manual de Puentes MTC, págs. 143/146):
>
> | Carga | Resistencia I | Servicio I | Evento Extremo I |
> |---|---|---|---|
> | DC | máx 1.25 / mín 0.90 | 1.00 | 1.00 |
> | EV | máx 1.35 / mín 0.90 | 1.00 | 1.00 |
> | EH (activo) | máx 1.50 / mín 0.90 | 1.00 | 1.00 |
> | EH (en reposo) | máx 1.35 | — | — |
> | LS | 1.75 | 1.00 | γ_EQ (0.50 o 0.00, por proyecto) |
> | WA | 1.00 | 1.00 | 1.00 |
> | EQ | — | — | 1.00 |
>
> Nota: el valor de EV mínimo es 0.90 según la tabla fuente — no 1.00 como advertiste como
> posibilidad en tu mensaje anterior; la fuente verificada zanja la duda. Etiqueta `[N]`, citable
> vía Manual de Puentes MTC directamente (págs. 143/146), sin necesidad de AASHTO como fuente
> primaria si prefieres la cadena de citas más corta.
>
> **(2) `recubrimiento_aashto_mm`** — Tabla 5.10.1-1, AASHTO LRFD 9ª Ed., pág. 5-169, Categoría A
> (acero convencional). Aviso antes de mapear a las tres claves de E.060: **AASHTO no organiza su
> tabla por diámetro de barra como E.060** (≥3/4" / ≤5/8") — organiza por severidad de exposición.
> No fuerces una correspondencia 1:1 que no existe en la fuente. La resolución defendible: La Unión
> (Piura) es zona costera, así que la categoría de exposición aplicable de AASHTO es *"Ambiente
> costero"* = **75 mm**, uniforme, sin importar el diámetro de barra. Como 75 > 70 (contra_suelo de
> E.060) y 75 > 50 y 75 > 40 (los dos casos de intemperie de E.060), AASHTO gobierna en los tres por
> la regla del mayor — no hace falta forzar tres valores AASHTO distintos, uno solo (75 mm, por
> exposición costera) ya es mayor que los tres de E.060. Si prefieres declarar las tres claves
> explícitamente para que la memoria muestre la comparación caso por caso, usa 75 mm en las tres;
> documenta en el criterio que es el mismo valor fuente (exposición costera) aplicado a los tres
> casos de E.060, no tres lecturas distintas de AASHTO.
>
> **(3) `peso_especifico_concreto_kn_m3`** — Tabla 3.5.1-1 + Comentario C3.5.1, AASHTO LRFD 9ª Ed.,
> pág. 3-21: **23.56 kN/m³** (0.150 kcf, concreto armado). Cae dentro del rango de sensibilidad ya
> declarado (23.5–24.5). Usa este valor citado, no el redondeo de práctica regional a 24.0 — 23.56
> tiene fuente directa, 24.0 es convención sin cita propia.
>
> **(4) `procedimiento_flexion_corte_aashto_sec5`** — Arts. 5.5.4.2 y 5.7.3.4.2, AASHTO LRFD 9ª
> Ed., págs. 5-32 y 5-70/5-243:
> - φ = 0.90 para flexión y para corte
> - Modelo Seccional MCFT, procedimiento directo no iterativo (2020, 9ª ed.)
> - β = 4.8 / (1 + 750·εs) — Art. 5.7.3.4.2-1
> - θ = 29 + 3500·εs (grados) — Art. 5.7.3.4.2-3
> - Vc = 0.0316·β·λ·√f'c·bv·dv — Art. 5.7.3.3-3
> - Vs = (Vu/φ) − Vc − Vp — espaciamiento s = Av·fy·dv·cotθ / Vs — Art. 5.7.3.3-4
> - dv = max(de − a/2, 0.9·de, 0.72·h) — Art. 5.7.2.8
>
> Declara esto como el valor del criterio (deja de ser `None`, queda citado y trazable). **No
> implementes el cálculo completo de flexión/corte en M9 ahora si no estaba ya planeado en esta
> sesión** — eso es una tarea de ensamblaje aparte, más grande que cerrar un criterio; si
> `diseno_flexion_corte()` sigue siendo un tope como reportaste antes, que lo siga siendo, solo con
> la fórmula ya citada y disponible para cuando se implemente.
>
> Corre la suite completa al final."

**Gate:** los 4 criterios de C.2 sin `None`; `recubrimiento_aashto_mm` documentado con la
justificación de "exposición costera uniforme" en vez de tres lecturas forzadas; suite en verde.

### Etapa C · Cierre de los 25 criterios vacíos

Se cierran por vías distintas. Agrupados por lo que hace falta para resolverlos:

**C.1 — Se cierran con una decisión tuya y de tu asesor (11 criterios, una tarde)**

| Criterio | Qué decidir |
|---|---|
| `v_max_concreto_eleccion` | 3.0 m/s es la lectura conservadora del rango 3.0–6.0 |
| `talud_terraplen` | Sale de tu sección típica (DG-2018) |
| `pendiente_relleno_trasdos_i` | 0° si la coronación es horizontal |
| `inclinacion_muro_beta` | 0° si el muro es vertical |
| `friccion_muro_suelo_delta` | Habitual: 2/3 · φ del relleno |
| `punto_aplicacion_incremento_sismico` | 0.6H (Seed-Whitman) es la adopción corriente |
| `angulo_aletas` | Según esviaje de cada punto |
| `predimensionamiento_cabezal` | Geometría de partida para la iteración de estabilidad |
| `longitud_proteccion_salida` | Práctica de enrocado o HEC-14 |
| `TR_evento_extremo` | Tras confirmar en Etapa B que la norma no lo fija |
| `umbral_area_quebrada_importante_ha` | **El más importante.** Tras confirmar el vacío en Etapa B |

**C.2 — Se cierran extrayendo de un PDF (9 criterios, requiere AASHTO LRFD)**

`factores_carga_aashto` · `recubrimiento_aashto_mm` · `procedimiento_flexion_corte_aashto_sec5` ·
`peso_especifico_concreto_kn_m3` · `FS_flotacion` · `N_cq_N_gammaq_meyerhof` (figuras del Manual
de Puentes) · `clases_producto_por_relleno` (AASHTO M-170M) · `v_max_hdpe` y `v_max_tmc` (PPI/FHWA)
· `metodo_estabilidad_global`

> **Nota:** el bloque §8 del manifiesto observa que **ninguna cita a AASHTO LRFD lleva valor
> numérico transcrito** — las tablas quedaron todas sin extraer. Es el hueco más grande que queda
> y afecta a toda la Fase 9. Necesitas acceso al PDF de AASHTO LRFD, y **declarar qué edición**,
> porque los factores y la numeración de la Sec. 11 cambiaron entre ediciones.
>
> **Estado:** 6 de 9 verificados y con valor real (ver "Resultado de la Etapa B — segunda tanda"
> más arriba). Quedan `clases_producto_por_relleno`, `v_max_hdpe` y `v_max_tmc`, que necesitan
> AASHTO M-170M y PPI/FHWA — documentos aparte, no verificados todavía.

**C.3 — Dependen de datos externos (5 criterios, no se cierran ahora)**

`TW_receptor` (ANA / Junta de Usuarios) · `homogeneidad_serie_fen` (SENAMHI) ·
`c_phi_fundacion`, `capacidad_portante_adm`, `phi_relleno_trasdos`,
`peso_especifico_relleno_kn_m3` (ensayos) · `remanso_derecho_via` (requiere perfil de remanso)

Estos quedan como pendientes declarados del expediente. **La memoria de cálculo los va a imprimir
en el bloque 4 con su fundamento, que es exactamente lo correcto a nivel de perfil.**

### Etapa D · Primera corrida completa y revisión del producto

> **Estado: en curso.** `docs/manifiesto_citas.md` (Etapa B) quedó desactualizado tras cerrar los
> 4 datos de C.2 — pendiente de sincronizar, no bloquea nada. Datos de prueba: usar
> `tests/fixtures/datos_referenciales_prueba.md` (versión corregida, sin pisar los 6 criterios ya
> cerrados/retirados: `factores_carga_aashto`, `recubrimiento_aashto_mm`,
> `peso_especifico_concreto_kn_m3`, `procedimiento_flexion_corte_aashto_sec5`, `FS_flotacion`,
> `N_cq_N_gammaq_meyerhof`). Interfaz gráfica: `python gui/app.py` desde la raíz del repo.

**Antes de tener las decisiones reales de C.1/C.2 listas, vale la pena una corrida de prueba
integral con valores provisionales — es una buena forma de validar que el pipeline entero
funciona de punta a punta sin esperar a que las 25 decisiones estén cerradas de verdad.**

El riesgo no es hacerlo: es que un valor puesto "para que corra" se confunda después con una
decisión real y termine en una memoria de cálculo que vas a defender. Ninguna etiqueta de
`criterios_adoptados.py` distingue hoy "esto lo decidí" de "esto lo puse para probar" — las dos
se ven igual como `[A]` con `justificacion` y `valor`. Para que no se mezclen:

**Usa una rama de git aparte para la corrida de prueba.**

```bash
git checkout -b prueba-integral
```

En esa rama, rellena los 25 criterios con valores razonables — puedes usar directamente las
adopciones sugeridas de C.1 (§4, tabla) como punto de partida, y para C.2/C.3 cualquier valor
dentro del rango de `sensibilidad` declarado. Corre el pipeline completo, exporta el HTML, revisa
que M11 se comporte bien con un expediente que sí cierra. Cuando termines:

```bash
git checkout master        # vuelve a la rama real, con los 25 en None
git branch -D prueba-integral   # opcional: descarta la rama de prueba entera
```

**Nada de la rama de prueba llega a `master` a menos que tú lo decidas fila por fila.** Las
decisiones reales de la Etapa C se aplican directo en `master`, cada una con su fuente de verdad
correspondiente (Etapa B para C.2, tu criterio de ingeniería para C.1) — no como un arrastre de lo
que pusiste para probar.

**Alternativa si prefieres no usar ramas:** pide a Claude Code que añada un campo
`provisional: bool = False` a la dataclass `Criterio`, y que `reporte_criterios()` imprima un
aviso en rojo, imposible de pasar por alto, en cualquier fila con `provisional=True`. Es más
débil que la rama —depende de que alguien vea el aviso— pero sirve si de verdad quieres correr la
prueba sin salir de `master`.

Con la corrida de prueba (en la rama, o marcada como provisional) hecha, trae aquí:
- El **HTML generado** (no la plantilla)
- La salida del CLI mostrando qué puntos cerraron y cuáles quedaron bloqueados

Reviso el reporte como lo haría un jurado: si cada número lleva numeral o etiqueta, si los bloques
están separados, si algún `[A]` se lee como si fuera `[N]`, y si los bloqueos se explican con
claridad suficiente para defenderlos. Si detecto algo que parece un valor de prueba filtrado como
si fuera real, te lo señalo ahí — es exactamente el tipo de cosa que esta revisión existe para
atrapar antes de que llegue a la sustentación.

### Etapa E · Validación externa con HY-8

Sigue pendiente desde la Parte 6 de la guía de sesiones. Con al menos un punto ya cerrando el
diseño, corre 1–2 puntos en HY-8 y compara HW de entrada, HW de salida y control gobernante.
Discrepancia < 5 %, o explicada por escrito. Es el entregable 5 de la Fase 11 y va como anexo.

---

## 5. Lo que salió bien y conviene decirlo

El manifiesto es un documento de auditoría de calidad profesional. Tres cosas destacan:

- **El concepto de "afirmación negativa"** — inventariar no solo lo que la norma dice, sino lo que
  el código afirma que la norma *no* dice (que HDPE no está en la Tabla N° 09, que el Manual de
  Puentes no tipifica la Clase F). Esas afirmaciones son tan auditables como las positivas y casi
  nadie las documenta.
- **La §11**, separando las citas que parecen numerales normativos y son secciones de la hoja de
  ruta. Sin eso, alguien buscaría "num. 4.2.1" en el Manual del MTC y no lo encontraría nunca.
- **El matiz de §12** sobre los `[A]` que sí mencionan numeral: distinguir que la tabla subyacente
  es `[N]` y se verifica, mientras que la elección dentro de ella es `[A]` y se justifica. Es
  precisamente la distinción que costó varias versiones fijar.

Y el propio manifiesto encontró la contradicción de `constantes_normativas.py` consigo mismo
(§13, punto 1) antes de que la encontrara nadie más. Un inventario que detecta su propio defecto
de origen es un buen inventario.
