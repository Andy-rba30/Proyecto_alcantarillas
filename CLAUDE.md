**Antes de cualquier tarea, leé también Claude.md (mixtas) en la raíz: contiene la
constitución completa del proyecto — la regla nuclear, la taxonomía de errores, las
convenciones de literales y criterios. Este archivo (CLAUDE.md, mayúsculas) existe
aparte solo porque Claude Code carga automáticamente ese nombre exacto; Claude.md sigue
siendo la fuente de verdad y no debe renombrarse ni duplicarse.**

## Protocolo de corrección — Fase 1 (auditorías externas)

### Referencia obligatoria
En `docs/auditorias/` están los tres informes de auditoría externa
(`auditoria_matematica.md`, `auditoria_sistema.md`, `auditoria_normativa.md`) y la matriz
cruzada `matriz_cruzada_auditorias.xlsx`.

Cuando un prompt cite identificadores de hallazgo (MAT-D1, SIS-A-01, NOR-PUE-03, etc.):
1. **Antes de tocar código**, abrí la ficha de cada ID citado y leé su evidencia completa.
2. **Después de implementar**, contrastá tu solución contra esa evidencia y decime
   explícitamente si la cierra, la cierra en parte, o no la cierra.
3. Si tu solución contradice lo que dice la ficha, paralo y explicá por qué antes de seguir.

### Git
- El trabajo puede pasar por ramas auxiliares, pero **ninguna queda abierta**: al cerrar
  cada prompt, todo tiene que estar fusionado en `main`.
- Un commit por prompt, con mensaje `fase1(Pn): resumen — IDs cerrados`.
- No hagas commit si la suite no está en verde.

### Reglas de detención
- **No inventes valores normativos.** Si necesitás un dato de una norma y no podés leerlo en
  `normas/`, DETENETE y decime exactamente qué falta. Rellenar un vacío en silencio es, según
  este documento, el peor error posible.
- **No inventes citas.** Numeral, artículo y página tienen que salir del PDF, no de memoria.
- Si un dato lo tiene que decidir el proyectista, no lo elijas vos: dejalo como vacío
  declarado por la vía que el proyecto ya usa para V5 y V8.

### Anclaje
Las referencias `archivo:línea` de las auditorías pueden estar corridas: la auditoría
normativa detectó que al menos 66 de 296 no llevan a lo que dicen. Anclá siempre al **nombre
del símbolo** (función, constante, clave de criterio), nunca al número de línea.

## Reglas de corrección de hallazgos de auditoría

Este repositorio tiene 236 hallazgos de tres auditorías externas, ya cruzados en
`docs/auditorias/matriz_cruzada_auditorias.xlsx` (14 clusters por causa raíz, 8
conflictos resueltos). Ese archivo es el TRACKER: el estado de cada hallazgo se
marca ahí, en las columnas Estado / Responsable / Commit. El PLAN es
`docs/hoja_de_ruta_correcciones_v12.md`.

1. Antes de tocar un archivo, busca su cluster en la hoja `Clusters`. Un cluster
   se corrige entero, en un solo cambio de diseño y un solo commit. Nunca
   hallazgo por hallazgo.
2. Antes de aplicar cualquier corrección, consulta la hoja `Conflictos` (o la §6
   del plan). Ocho objetos del repositorio tienen una corrección "obvia" que es
   la EQUIVOCADA porque otra auditoría descubrió por qué. Si el objeto que vas a
   tocar está ahí, la resolución de esa fila es vinculante y sustituye a tu
   criterio.
3. Ancla todo por NOMBRE DE SÍMBOLO (función, constante, clave de criterio),
   nunca por número de línea. Al menos 66 de 296 referencias archivo:línea del
   manifiesto no llevan a lo que dicen llevar, y las auditorías corren sobre dos
   commits distintos (71b134fb y 2e1708ab).
4. Cita los IDs siempre con prefijo MAT- / SIS- / NOR-. `F-01` y `F-02`
   significan hallazgos DISTINTOS en la auditoría Normativa y en la de Sistema.
5. No escribas tests contra el comportamiento actual antes de cerrar las fases
   de corrección: congelarías los defectos. Los tests van en su fase, después.
6. Cuando el código y la hoja de ruta discrepan, el defecto se reporta contra la
   hoja de ruta primero y la fuente primaria (el PDF en normas/) decide.
