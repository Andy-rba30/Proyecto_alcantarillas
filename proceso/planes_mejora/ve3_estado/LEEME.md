# Estado de VE-3 (para retomar si la sesión se corta)

Material de proceso, no del entregable. Lo mantiene la sesión orquestadora y se actualiza
cada vez que se integra algo. Fecha de esta versión: 2026-11-17.

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

## En curso (agentes en paralelo) — actualizado tras integrar VE-3.5 a VE-3.8 (`6a87006`)

Integrado en la rama además de lo de arriba: VE-3.5 (la zapata del cabezal se dimensiona por
estabilidad), VE-3.6/3.7 (Familia C: VC3 contra el desnivel F del canal, fuente USBR; remanso
por paso directo), VE-3.8 (correcciones de la revisión Fable a la validación estructural).
148 criterios. El PDF del USBR está en el repositorio de normas (`normas/`).

| Trabajo | Respaldo del trabajo en curso (cada 15 min) |
|---|---|
| VE-3.9: paso 0.10 m y tope 1.5·H como valor de archivo de `dimensionamiento_zapata_cabezal`, y el ESPESOR de la zapata también se dimensiona (armado del talón A1/A2) | `claude/youthful-shannon-rjzmuc-respaldo-agent-a5b3b06a3d74de34c` |
| VE-3.10: VC3 sin F BLOQUEA el punto (DatoFaltanteError), con F de prueba en el juego y en la línea base de la Familia C | `claude/youthful-shannon-rjzmuc-respaldo-agent-a9faca4ff8abe1b54` |
| Regeneración de la línea base y de los documentos generados sobre el conjunto | — |

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
