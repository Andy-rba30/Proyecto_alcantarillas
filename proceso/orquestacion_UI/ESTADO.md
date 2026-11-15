# Estado de la orquestación de la cadena UI (para retomar si la sesión se corta)

Actualizado: 2026-11-15 ~03:55 UTC por la sesión orquestadora (session_01XnJWqZewuN93pheZofoaRk).

## Dónde está cada cosa

- `origin/main` = 822091f (UI-1 a UI-5 y VE-1 entregados, 2026-11-15 ~07:10 UTC; par 6739+10=6749, proceso 145).
- `origin/claude/awesome-mendel-dyj4p4` (rama designada) = 2d37c2c = main + 50a7acc (CLAUDE.md al día) + 2d37c2c (prompt UI-5 en proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md).
- `origin/claude/awesome-mendel-dyj4p4-respaldo` = respaldo del trabajo en curso (se sobrescribe; contiene este archivo en proceso/orquestacion_UI/).

## Etapas

| Etapa | Commit | Estado |
|---|---|---|
| UI-1 hidrología + sesión v4 | 4066a24 | en main |
| UI-2 pestaña 4 (resumida, cabezal) | 4067b9a | en main |
| UI-3 barrido | 3117b2c | en main |
| UI-4 recorrido, capturas, README | 2a5d35f | en main |
| CLAUDE.md (3 frases) | 50a7acc | en rama designada |
| UI-5 decisiones del dueño | 7d52ca1 | en main |
| VE-1 defectos de la validación (D1 código, D2/D3 documentales) | 822091f | en main. Aprobado por Fable tras la ronda 2. Ronda 1: D1-D3 bien; H1 (rótulo Ø 1.07 con D=1.0668, modelos.py:1456), H2 (puerta de diametros_normalizados acepta paso 0/texto/ausente → traza fuera de ErrorProyecto), H3 (declarar la «Regla [N]» en M3:38 y docstring M2) y H5 (fichas, texto del NF) devueltos al implementador con permiso ampliado por la orquestadora (autorización del dueño de corregir los defectos de la validación) |

UI-5: cuatro decisiones (CSV invalida; texto de la remisión de la resumida; PDF atómico con src/escritura_atomica.py; guardia de claves en criterios_adoptados). Rondas de revisión: H1-H3 (26fa8f1→22890ce), N1-N4 (→ae51aa2), N5 (en curso: firma del editor al abrir otra obra). El dueño aceptó el cambio de texto del párrafo «0. Encabezado de trazabilidad» de src/plantillas/memoria_resumida.html.

## Puerta de cada etapa (la que se aplicó en toda la cadena)

1. Revisor independiente (sin el contexto del implementador) con el diff y el prompt; lo confirmado se corrige antes de integrar.
2. Medición limpia en un worktree FUERA del repo (varios tests recorren la raíz con rglob): `medir.sh <commit> <etiqueta> export` (está junto a este archivo). Con Tk real: python = 3.12, xvfb-run, NORMAS_DIR=/home/user/andy-rba30/normas (clon de Andy-rba30/Normas).
3. Integración por avance rápido en la rama designada, push, y push a origin/main (`git push origin <commit>:refs/heads/main`).

Pares medidos (entregable checkout / exportación / proceso):
- partida bcd2d1a: 6412+10 (+3 failed de T-3) / 6408+14 (+3) / 145
- 2a5d35f (UI-4): 6609+10=6619 / 6605+14 / 145
- ae51aa2 (UI-5 ronda 3): 6677+10=6687 (medido por el implementador; medición limpia de la orquestadora en curso)

## Instrucciones vigentes del dueño (2026-11-15, antes de irse a dormir)

- La validación con ejemplos externos tiene que ser de PUNTA A PUNTA: la app entera (cli.py con CSV, datos externos, hidrología y declaraciones; y la ventana real), no funciones sueltas.
- Correcciones con Opus o Fable; validación con el otro modelo como revisor independiente.
- Guardar cada cierto tiempo (rama de respaldo). Vigilar los tokens: al 95 % guardar; al 98 %, si hubo avance significativo, guardar y dejar un prompt de continuación en el chat y en el repo (PROMPT_CONTINUACION.md, junto a este archivo).
- Advertencia del dueño: los ejemplos (sobre todo los académicos) pueden traer errores propios. Antes de llamar «defecto» a una diferencia: recálculo independiente a mano y consistencia interna de la fuente; el revisor Fable lo debe comprobar.
- Decisiones tomadas por defecto (el dueño no eligió opción): N5 se corrige antes de integrar UI-5; el cambio de texto del párrafo de src/plantillas/memoria_resumida.html queda aceptado.

## Lo que sigue (al cierre de la noche, 2026-11-15 ~07:10 UTC: TODO lo previsto está en main)

- PENDIENTE DEL DUEÑO: volver a limitar la red del entorno (lista más arriba); las siete decisiones de VE1-02 (n del concreto declarable, definición de V_erosion, hipótesis de V7, factor 1.13, aviso de plausibilidad de la serie, racional modificado hasta 770 km², resolución de la progresión); corregir la hoja de ruta (líneas 223 y 557, ficha VE1-01); los residuos de presentación N1-N3.

## Lo que seguía (histórico)

1. UI-5: recibir la corrección de N5 → verificación acotada del revisor → medición limpia → integrar en la rama designada → push a main.
2. Validación de PUNTA A PUNTA con ejemplos externos (pedido del dueño): un agente (Sonnet) busca ejemplos completos en internet (/tmp/ejemplos_web/; red del entorno ampliada con tn.gov, fhwa.dot.gov, rosap, codot, txdot, core.ac.uk, espol y repositorios peruanos). Luego correr la app ENTERA (cli.py con CSV + datos externos + hidrología, y la ventana real) con cada ejemplo, comparar con lo publicado y clasificar diferencias (defecto / fuente / método). Correcciones con Opus o Fable; validación con el otro modelo como revisor independiente.
3. Diferido sin decisión: barrido de la CLI fuera de ventana (UI3-02), editor de varias tablas (UI1-02), ancho mínimo 900 px (UI4-01), estimador del pre-vuelo (T1-04), exportar_html/csv no atómicos (UI5-01).

## Obras reales (búsqueda del 2026-11-15 ~04:10 UTC)

- 0 casos completos; 2 parciales en /tmp/ejemplos_web/obras_reales/obras.json (Dale Boulevard, FHWA-RD-01-095: modelo físico fuera de HDS-5, sólo cualitativo; MnDOT 2021-29: inventario de 50 alcantarillas con Q por StreamStats, sin HW).
- Los expedientes peruanos con memoria de cálculo de alcantarillas están en hosts NO permitidos: gis.pvn.gob.pe (Provías Nacional, p. ej. Alcantarilla Marco km 31+836.971, LP0024-2012) y apps.proviasdes.gob.pe (Provías Descentralizado). También pendientes: transparencia.mtc.gob.pe, sigrid.cenepred.gob.pe, repositorio.untumbes.edu.pe, trust.dot.state.wi.us; y repositorio.uni.edu.pe devuelve 401 en los PDF. La lista de hosts del entorno ya tiene 20: para añadir estos, retirar los que no sirvieron (dspace.espol.edu.ec, www.codot.gov, www.txdot.gov, wsdot.wa.gov, www.wsdot.wa.gov). APROBADO por el dueño (2026-11-15 ~04:20 UTC): se añadieron gis.pvn.gob.pe, apps.proviasdes.gob.pe, transparencia.mtc.gob.pe, sigrid.cenepred.gob.pe, repositorio.untumbes.edu.pe y trust.dot.state.wi.us, y se retiraron codot, txdot, core.ac.uk, espol y wsdot. Búsqueda de obras reales retomada.
- Nota técnica: WebFetch no resuelve hosts externos en esta sesión; usar curl (rosap.ntl.bts.gov sin User-Agent de navegador).

## Red del entorno: SIN RESTRICCIÓN por esta noche (decisión del dueño, 2026-11-15 ~04:30 UTC)

Mañana hay que VOLVER a limitarla (update_environment network_access="limited", con allow_package_managers=true y allow_mcp_servers=true) y reponer esta lista de dominios, que es la que había antes de abrirla:
archive.ubuntu.com, www.tn.gov, www.fhwa.dot.gov, rosap.ntl.bts.gov, repositorio.uni.edu.pe, tesis.pucp.edu.pe, repositorio.pucp.edu.pe, repositorio.unc.edu.pe, repositorio.upao.edu.pe, www.gob.pe, cdn.www.gob.pe, www.pvd.gob.pe, www.proviasnac.gob.pe, prod2.seace.gob.pe, gis.pvn.gob.pe, apps.proviasdes.gob.pe, transparencia.mtc.gob.pe, sigrid.cenepred.gob.pe, repositorio.untumbes.edu.pe, trust.dot.state.wi.us
(Para el proyecto, en el día a día, basta con archive.ubuntu.com y los registros de paquetes; los demás eran para la búsqueda de ejemplos.)

## Validación de punta a punta (terminada 2026-11-15 ~04:45 UTC; resultados en proceso/orquestacion_UI/validacion_web/ del respaldo)

- 371 magnitudes contrastadas; 116 fuera de tolerancia: 3 error de la fuente (b), 113 método/norma (c), 0 defecto en los resultados. Obra real WisDOT STH 32: control 12/12, HW −0.2 a +0.6 % de HY-8. Ventana real = CLI (0 diferencias en el JSON) en 3 casos.
- Defectos candidatos: D1 (M2_material.py:973, la progresión declarada se redondea con round(…,2) y se rechaza a sí misma) y D2 (V7 no lee NF_profundidad_m aunque contrato_entradas.md:71 dice que sí; el código queda del lado seguro).
- Siguiente: revisión independiente con Fable (/tmp/revision_validacion/) → correcciones confirmadas con Opus (prompt en la cadena, revisor Fable) → puerta → main.

## Residuos de presentación tras VE-1 (BAJOS, sin efecto en resultados; para el dueño)

- N1: los pasos de la memoria sustituyen D con dos decimales (CIFRAS_FACTOR en M3, M4, M5, M6, M9): con la serie de 6 in imprimen «D = 1.22 m» para 1.2192 (declarado abierto en VE1-01); y dos mensajes de la Fase 8 formatean D con dos decimales (src/modulos/M8_estructural.py:1366 y :2033), no declarados.
- N2: modelos.texto_de_dimension imprime todos los decimales del repr: un número CALCULADO con ruido flotante se vería así («marco 1.2000000000000002 × 0.90 m»); con valores tecleados no ocurre.
- N3: el mínimo de dos decimales de texto_de_dimension sale de CIFRAS_FACTOR, una constante con otro significado.

## Consumo (get_session, 2026-11-15 07:07 UTC)

- Contexto de la orquestadora: 753k / 1M tokens (autocompactación activa hacia ~902k).
- Costo acumulado de la sesión: ~USD 494.
- Límite de 7 días de la cuenta: «allowed_warning» (sin porcentaje visible).
- En curso: VE-1 822091f aprobado por el revisor Fable (H1-H3, H5 corregidos; N1-N3 BAJOS de presentación anotados); medición limpia ve1b en curso → integrar y main.

## Entorno

- Entorno «Proyecto_alcantarillas» (personal) con script de instalación guardado (Tk, xvfb, ImageMagick, deps en python3.12).
- Si el contenedor es nuevo: clonar Andy-rba30/Normas (GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 ...) y exportar NORMAS_DIR.
