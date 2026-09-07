# Parche v2 de `docs/ruta_familia_c.md` — consolidación de CN

**Por qué es un parche y no un archivo nuevo.** §15 la escribió la sesión CN y vive en
`claude/marco-concreto-normativa-jg9rlz` (SHA `e2da067`). Reemplazar el archivo entero la
borraría. Cada edición de abajo está anclada por su encabezado y por el texto que
sustituye.

**Orden.** Primero fusionar el PR #2. Después aplicar este parche en un commit aparte:
`familiaC(CP): consolidacion de CN — regla #11, regla #6 corregida, C5 punto 6`.

---

## E1 · §6, regla vinculante #6 — reescribir la justificación

CN acierta: la regla llegaba a la conclusión correcta por el camino equivocado. El vacío
es **de fila, no de grupo**, y eso hace la analogía **más estrecha** que la del HDPE, no
equivalente. Sustituir el párrafo entero de la regla #6 por:

> **#6 — La Tabla Nº 09 NO tiene fila de cajón, y el vacío es DE FILA, NO DE GRUPO.** El
> grupo «A. CONDUCTO CERRADO CON ESCURRIMIENTO PARCIALMENTE LLENO» ya cubre al marco por
> su propio título: un cajón es un conducto cerrado. Lo que falta es la fila. De las
> siete subfilas de «a. Concreto», seis dicen «tubo» y la séptima —`afinado`— no dice
> nada de forma. **Esto hace la analogía más estrecha que la del HDPE**, que sí estaba
> fuera de la tabla entera: aquí el conducto está dentro del grupo y solo falta su
> acabado. El n de Manning del marco se cubre con un criterio `[N→]` cuya justificación
> tiene que declarar las dos cosas — que el grupo aplica y que la fila no existe — y no
> puede copiar el argumento de `n_manning_hdpe` tal cual.

---

## E2 · §6, regla vinculante #11 — NUEVA

Es la refutación del `auditor-adversarial` en CN, verificada contra la ficha del criterio.
Añadir al final de §6:

> **#11 — `ke_entrada` = 0.5 es de TUBO y no vale para el cajón.** Su campo `fuente` lo
> ata explícitamente al bloque «Pipe, Concrete» de la Tabla C.2, fila «Square-edge»
> **sangrada bajo el rótulo de agrupación «Headwall or headwall and wingwalls»** — el
> propio criterio documenta que la fila suelta, sin su encabezado, pierde la condición.
> El bloque «Box, Reinforced Concrete» tiene once filas propias, de 0.4 a 0.7 según
> aletas y borde.
>
> **Lo que lo hace peligroso no es el valor, es que no se detiene.** El criterio tiene
> `valor=0.5`, `etiqueta="C"`, `nivel=NIVEL_PERFIL` y `sensibilidad=None`: con un cajón
> corre el control de salida con un `ke` que no le corresponde, sin bloqueo, sin ventana
> y sin nada que lo señale en la memoria. Con 0.5 → 0.7 el HW sale del orden de 0.09 m
> por debajo del real contra V4.
>
> **Y arrastra una premisa muerta.** `T_HDS5_C2.alcance` está `Acotada` con la razón «el
> catálogo de Sec. 3.2 no ofrece sección cajón» — exactamente la premisa que C5 destruye.
> Un `Acotada` que describe un alcance que ya no es el suyo es el antipatrón de §12.
>
> C5 tiene que abrir `ke_entrada` por forma, emparejado con la fila que `embocadura_cajon`
> declare. Las dos decisiones se mueven juntas con la embocadura de Sec. 9.1, igual que
> ya lo hacen la carta de HDS-5 y el detalle del cabezal.

---

## E3 · §4.5, contrato de memoria — corregir el vehículo y añadir la fila que faltaba

CN midió el código y yo no. Dos hechos medidos que cambian la tabla:

- un `Criterio(valor=None)` **nunca llega a `bloque_acotaciones`**: el filtro de
  `acotaciones_declaradas()` exige `valor is not None`;
- `Cita.interpretacion` **no tiene impresor** en la memoria.

En la fila «Lo adoptado donde la norma calla», añadir a la columna de exigencias:

> …y **tener valor**: `acotaciones_declaradas()` filtra por `valor is not None`, así que
> un criterio vacío no aparece en este bloque por mucho `vacio_verificado` que lleve.

Y añadir una fila nueva a la tabla:

| Qué se declara | Vehículo | Qué exige del código nuevo |
|---|---|---|
| **Lo que el proyecto hace más estrecho que la norma** (la norma habla, y el proyecto cubre solo parte) | `M11.bloque_alcance` (marcador `bloque_alcance`, imprime con el expediente abierto) + `PasoDeMemoria.nota_del_proyecto` en el punto | el campo `nota_del_proyecto` se imprime bajo «Lo que pone el proyecto» con clase CSS `interpretacion`. **No es acotación**: acotaciones es «lo adoptado donde la norma calla», y aquí la norma habla |

---

## E4 · §10, prompt de C5 — punto 6 NUEVO, y el actual 6 pasa a 7

Insertar antes del punto de tests:

```
6. `ke_entrada` (regla vinculante #11). Hoy vale 0.5 con etiqueta [C],
   NIVEL_PERFIL y sensibilidad None, y su `fuente` lo ata al bloque «Pipe,
   Concrete» de la Tabla C.2, fila «Square-edge» bajo el rótulo de agrupación
   «Headwall or headwall and wingwalls». Con un cajón ese valor no corresponde y
   NADA lo detiene: no hay bloqueo, no hay ventana, no hay marca en la memoria.
   Abrilo por forma: el ke del marco sale del bloque «Box, Reinforced Concrete»
   que C2 transcribió, emparejado con la fila que `embocadura_cajon` declare. Las
   dos decisiones se mueven juntas.
   Comprobá que el ke elegido sale en la memoria con SU FILA Y SU RÓTULO DE
   AGRUPACIÓN: el propio criterio ya documenta que la fila suelta pierde la
   condición.
   Y comprobá que `T_HDS5_C2.alcance` dejó de decir «el catálogo de Sec. 3.2 no
   ofrece sección cajón»: esa premisa la destruye esta misma sesión, y un
   `Acotada` que describe un alcance que ya no es el suyo es el antipatrón de §12.
```

---

## E5 · §10, prompt de C2 — añadir al punto 2

Al final del punto 2 (Tabla C.2), añadir:

```
   Dejá anotado en el reporte de la sesión que el consumidor de esta tabla es el
   criterio `ke_entrada`, que hoy tiene valor 0.5 tomado del bloque «Pipe,
   Concrete», y que C5 tendrá que abrirlo por forma (regla vinculante #11). NO lo
   toques en esta sesión: aquí solo se transcribe.
```

---

## E6 · §10, prompt de C5 punto 5 y §11 criterio 6 — el encuadre correcto

No es una **sustitución**. `M1_clasificacion.PERFILES[Familia.C].verificaciones_aceptacion`
es `None`, con el comentario «Sec. 2.3 no declara conjunto propio»: la Sec. 2.3 nunca le
dio a la Familia C un conjunto de aceptación. V1/V4/V4b no reemplaza nada declarado —
**llena un hueco**. El matiz cambia cómo se defiende ante un revisor.

En C5 punto 5, sustituir el texto por:

```
5. Implementá la declaración que CN redactó en §15 punto 4, por el vehículo que CN
   determinó: `bloque_alcance` más `PasoDeMemoria.nota_del_proyecto` en el punto.
   Lo que se declara: Sec. 2.3 NO le da a la Familia C un conjunto de
   verificaciones de aceptación —`PERFILES[Familia.C].verificaciones_aceptacion`
   es None, y el comentario del propio código lo dice—, de modo que a nivel de
   perfil el marco se acepta con V1/V4/V4b, que es el conjunto de una alcantarilla
   de paso. Eso LLENA UN HUECO, no sustituye a un criterio declarado, y el
   requisito de Sec. 2.3 que sí existe (no alterar la rasante hidráulica ni el
   borde libre del canal) queda diferido como VC1 (§13).
   Esto NO puede quedar en un docstring.
```

En §11, sustituir el criterio 6 por:

> 6. El **hueco de aceptación de la Familia C** está declarado y visible: que Sec. 2.3 no
>    le da conjunto propio, que a perfil se acepta con V1/V4/V4b, y que el requisito de
>    Sec. 2.3 queda diferido como VC1. Por `bloque_alcance` + `nota_del_proyecto`, no
>    implícito y no en un docstring.

---

## E7 · §8, preparación — dos correcciones medidas

Sustituir el punto 1 por:

> 1. **El contenedor de sesión arranca sin dependencias.** CN tuvo que instalarlas para
>    poder correr la suite. Deja resuelto, o instruye en el prompt, `numpy`, `scipy`,
>    `pytest` y **`pymupdf`**. Sin PyMuPDF los 32 tests de `test_normativa_pdf.py` se
>    saltan y las transcripciones de C2 pasarían sin verificar.

Añadir un punto 4:

> 4. **La configuración de referencia de este plan es «PyMuPDF sí / ventana Tk no»**, que
>    da `1536 passed / 2 skipped` (collected 1538). Es la que midió CN. Cualquier sesión
>    que reporte otro par tiene que decir con qué configuración corrió, no solo el número.

---

## E8 · §12, antipatrones — dos entradas nuevas

> - **No dejar `ke_entrada` en 0.5 cuando la sección es un cajón.** Tiene valor y no tiene
>   sensibilidad: no se detiene solo. Regla #11.
> - **No llamar «sustitución» al conjunto de aceptación de la Familia C.** Sec. 2.3 nunca
>   declaró uno; V1/V4/V4b llena un hueco.

---

## E9 · §9, tabla maestra — anotar CN como cerrada

Sustituir la fila de CN por:

| Sesión | Trabajo | Frente | Modelo | Esfuerzo | Plan mode | Estado |
|---|---|---|---|---|---|---|
| **CN** | Procedimiento normativo del marco | F0 | Opus 5 *(corrida real; el plan proponía Fable 5.1)* | max | sí | **Cerrada** — `e2da067`, PR #2 |

Y añadir bajo la tabla:

> **Nota de calibración, medida y no supuesta.** CN corrió con Opus 5 a `max` en lugar de
> Fable 5.1 a `high`, y salió bien: cuatro `verificador-normativo` en paralelo, cuatro
> autocorrecciones antes de cerrar y una refutación propia retirada (R-5). Para las
> sesiones de volumen (C2, C8) **no repitas `max`**: cuesta sin dar más que `xhigh`, que
> es lo que `ultracode` ya envía.

---

## E10 · §16 NUEVA — Bitácora de sesiones

Añadir al final del documento:

> ## 16. Bitácora de sesiones
>
> Una fila por sesión cerrada. El estado de detalle vive en §15 (normativa) y en
> `docs/decisiones_diferidas.md` (lo conservado sin consumidor); esta tabla es solo el
> índice de qué se corrió, con qué y con qué resultado medido.
>
> | Sesión | SHA | Suite (config) | Qué dejó | Qué quedó propuesto y no aplicado |
> |---|---|---|---|---|
> | **CN** | `e2da067` (PR #2) | 1536 p / 2 s, «PyMuPDF sí / Tk no» | §15: tabla numeral-por-paso, ocho `Fundamento`, la declaración del hueco de aceptación, 8 defectos contra la v8, 8 huecos del repo | regla vinculante #11 (`k_e`) y los 8 defectos contra la v8 — aplicados en el parche v2 / pendientes de la v9 |
> | **CP** | | | consolidación del parche v2 | |
