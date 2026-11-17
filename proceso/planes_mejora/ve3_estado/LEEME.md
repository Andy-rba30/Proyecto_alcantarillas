# Estado de VE-3 (para retomar si la sesión se corta)

Material de proceso, no del entregable. Lo mantiene la sesión orquestadora y se actualiza
cada vez que se integra algo. Fecha de esta versión: 2026-11-17.

> **MENSAJE DEL DUEÑO A LA SESIÓN ORQUESTADORA DE VE-3 (2026-11-17, 20:30 UTC), dejado
> desde otra sesión porque el dueño ya NO tiene acceso a esta.** Nadie va a leer el chat de
> esta sesión ni a responder preguntas en él: todo lo que importe tiene que quedar en el
> repositorio.
>
> 1. **Copia ya al repo lo que tengas fuera de él**, empezando por
>    `/home/user/verificacion_fable/ENSAYOS_DISENO_CONDUCTO.md` (aunque esté a medias,
>    rotulado BORRADOR) a `proceso/planes_mejora/ve3_estado/`, con commit y push a esta
>    rama. Desde ahora, todo informe en curso se copia y empuja con los respaldos de cada
>    15 minutos, igual que el código.
> 2. **Las preguntas al dueño no se hacen en el chat**: escríbelas en este LEEME
>    («Decisiones pendientes del dueño»), con tu recomendación, y sigue con lo que no
>    dependa de ellas.
> 3. **Deja un `PROMPT_CONTINUAR.md` en esta carpeta, y mantenlo al día**, para que otra
>    sesión retome VE-3 desde las ramas si esta se corta (como se hizo con VE-2).
> 4. No integres en `main`: eso sigue esperando la autorización del dueño.

## Decisiones pendientes del dueño (con la recomendación de la sesión)

La sesión sigue con lo que no depende de ellas. Responder aquí (o en el chat) basta.

1. **Clases III a V del tubo de concreto (ensayos del conducto, H1, alta).** Sólo la Clase II
   de M 170M está transcrita, y con más de ≈ 2.4 m de tierra sobre la clave ningún tubo de
   concreto cierra (13 de 57 corridas sin diseño; en 11 la app ya tenía un TMC que cumple).
   El PDF de AASHTO M 170M del repositorio no deja leer esas filas, pero el USACE EM
   1110-2-2902 (en `Normas/ejemplos_resueltos/conducto/`, pág. PDF 71) imprime la tabla de
   ASTM C76: Clase I 40, II 50, III 65, IV 100, V 140 N/m/mm (D0.01). **Recomendación:
   transcribir III a V como [C] desde el USACE, con su cita verificada**; con ellas, 16 de 17
   corridas coinciden con el diseño a mano.
2. **`borde_libre_bajo_tw_ahogante` = `no_cumple` (H5, criterio [A]).** Sobredimensiona hasta
   cuatro escalones cuando el TW ahoga la salida (E07 1.35 → 0.90 con `aviso`). **Recomendación:
   mantener `no_cumple`** (es el lado seguro y fue una decisión anterior del dueño), salvo
   que el dueño prefiera la lectura `aviso`; la sensibilidad ya lo muestra.
3. **O-2 del cabezal (VE3-03):** ancho del acero de temperatura de M9 (el real) frente a la
   franja de 12 in de CDOT; en los casos de CDOT manda el piso. **Recomendación: dejar el
   ancho real** (es el de la ec. 5.10.6-1 aplicada a la sección) y cerrar O-2.
4. **Carga viva de M8 con poco relleno (VE3-04):** lectura literal de la 9.ª ed., del lado
   seguro (+65 % frente a ACPA 2009). **Recomendación: que la revise un ingeniero** antes de
   la sustentación; no hay cambio de código pendiente.
5. **Integrar en `main`** cuando la suite esté verde y los ensayos del cabezal hechos.

Lo que la sesión corrige SIN esperar decisión (defectos frente a la hoja de ruta): H2 (V1 con
control de entrada y TW entre 0.75 D y D usa el tirante normal, contra la nota T-2 de la hoja
de ruta), H4 (V7 omite el peso propio del tubo, contra la fórmula 0.90·(DC + EV) ≥ U, y el
proyecto ya declara el peso del concreto), H3 (el delta de rasante que falta o que ignora V7)
y los titulares engañosos de los «no factible».

## Dónde está cada cosa

- `main` = `3a65e30`: VE-2 integrado con sus correcciones y dos verificaciones Fable.
- `claude/youthful-shannon-rjzmuc` (rama de trabajo de la sesión): VE-3 integrado hasta
  `61a4dcc` y empujado:
  - VE-3.1: bajo control de salida V3 juzga la mayor de `V_erosion` y `V_salida` (ficha VE3-01).
  - VE-3.2: `c_phi_fundacion` y `capacidad_portante_adm` son [S]; `Mw_licuefaccion` sigue [A] (VE3-02).
  - VE-3.3: M9 contra Caltrans BDP 11.2.2 y CDOT Ex. 11/8 (`docs/validacion_cabezal.md`, VE3-03).
  - VE-3.4: M8 contra ACPA, USACE y PPI (`docs/validacion_conducto.md`, VE3-04).
- Repositorio de normas (`Andy-rba30/Normas`, `main` `b845d8b`): `ejemplos_resueltos/` con los
  PDF y hojas de los ejemplos (cajón, cabezal y muros, conducto) y su catálogo.

## En curso (agentes en paralelo) — actualizado tras integrar VE-3.5 a VE-3.8 (`6a87006`); línea base y documentos generados del conjunto en `1fdffd7` (sellos PROVISIONAL)

Integrado en la rama además de lo de arriba: VE-3.5 (la zapata del cabezal se dimensiona por
estabilidad), VE-3.6/3.7 (Familia C: VC3 contra el desnivel F del canal, fuente USBR; remanso
por paso directo), VE-3.8 (correcciones de la revisión Fable a la validación estructural).
148 criterios. El PDF del USBR está en el repositorio de normas (`normas/`).

| Trabajo | Respaldo del trabajo en curso (cada 15 min) |
|---|---|
| **Retomado** (el primer agente se detuvo a las 19:49 UTC; uno nuevo parte de su respaldo `3c15302` y respalda en `claude/youthful-shannon-rjzmuc-respaldo-cabezal-espesor-2`) — VE-3.9: paso 0.10 m y tope 1.5·H como valor de archivo de `dimensionamiento_zapata_cabezal`, y el ESPESOR de la zapata también se dimensiona (armado del talón A1/A2) | `claude/youthful-shannon-rjzmuc-respaldo-cabezal-espesor` |

VE-3.10 (VC3 sin F bloquea) ya está integrado (`8ca5fc9`, ficha VE3-06 en `eb97467`).
VE-3.9 quedó a medias: su último respaldo es `3c15302` en la rama de respaldo de la tabla
(sobre `6a87006`, con un commit «wip VE-3.9» y 21 archivos sin commitear: código, tests,
generados y la §23 de la línea base empezada). Para retomarlo: partir de esa rama, revisar
contra el encargo de VE-3.9 como BORRADOR, terminar, y rebasar sobre la rama de trabajo.

Además en curso: **VE-3.11**, las correcciones de los ensayos del conducto que no esperan
decisión (H2, H3, H4 y titulares), respaldo en
`claude/youthful-shannon-rjzmuc-respaldo-ensayos-h2-h4`. Los informes en curso de
`/home/user/verificacion_fable/` se copian a `informes_en_curso/` con cada respaldo.

## Decisiones del dueño (2026-11-17)

- VE2-04: sí, V3 con la mayor velocidad bajo control de salida (hecho, VE-3.1).
- VE2-05: c_phi y capacidad portante a [S], Mw sigue [A] (hecho, VE-3.2).
- Validar M8 y M9 con ejemplos americanos; los peruanos no hacen falta para lo estructural.
- El programa DIMENSIONA el cabezal (VE-3.5, en curso).
- Completar la Familia C (VE-3.6/3.7, en curso).
- Que Fable revise al final la validación con ejemplos, contando con que los ejemplos pueden
  estar mal (en curso).
- Después: ensayos de diseño simulados (la app diseña; Fable diseña a mano sin ver la app; se
  compara que cumpla, que no esté sobredimensionado y que sea monótono).
- Guardar el progreso periódicamente (este archivo y las ramas de respaldo).
- Paso 0.10 m y tope 1.5·H de la zapata como valor de archivo; que crezca también el espesor;
  VC3 sin F bloquea el punto (2026-11-17, tarde).
- Sin cuota de Fable: las revisiones independientes y los ensayos de diseño se hacen con Opus a
  esfuerzo máximo. Ensayos del conducto en curso (informe en
  /home/user/verificacion_fable/ENSAYOS_DISENO_CONDUCTO.md, se copia aquí al terminar); los del
  cabezal, después de VE-3.9.

## Pendiente después de lo que está en curso

1. Integrar VE-3.5 y VE-3.6/3.7, regenerar, suite (clon limpio y exportación), sellos, bitácora.
2. Ensayos de diseño simulados con Fable (conducto y cabezal).
3. Validación hidrológica con casos reales calificados (los PDF en el repositorio de normas,
   `ejemplos_resueltos/casos_reales/`, con su informe de calificación): INDECI Piura
   (Miraflores 1971-2008, con y sin FEN), UPeU Colpahuayco–Langui (Témez), UNTumbes TU-107
   (caso adversarial: años duplicados) y ESPOL Intervalles (cajón con HY-8).
4. Abierto para el dueño: VE3-03 O-1/O-2 (Ec y ancho del acero de temperatura de M9) y VE3-04
   (la carga viva de M8 con poco relleno sobre tubos pequeños: del lado seguro, sin ejemplo con
   la edición 2013 o posterior).
5. Integrar en `main` con autorización del dueño.

## Entorno

Entorno de nube «Proyecto_alcantarillas» (personal, red abierta). Python 3.12 de `uv` con Tk
en `/home/user/venv312` (`requirements.txt`, PyMuPDF, `pillow<13`; openpyxl sólo para leer las
hojas de CDOT). `NORMAS_DIR=/home/user/Normas`. Suite: `xvfb-run -a python -m pytest -q -p
no:cacheprovider --no-header` en un clon limpio fuera del repositorio.
