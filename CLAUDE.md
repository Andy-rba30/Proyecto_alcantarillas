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
