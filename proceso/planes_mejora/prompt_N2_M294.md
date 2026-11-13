# Prompt N2 — Incorporación de AASHTO M 294-11 (traducción no oficial)

**Prerrequisito:** el PDF «AASHTO M 294-11 Tuberia corrugada de polietileno
300 a 1500 mm (traduccion no oficial).pdf» debe estar ya en `normas/` en
`main`. Correr DESPUÉS de N1 (A796), no antes ni en la misma sesión.

**Configuración:** Fable 5 · esfuerzo high · plan mode activado.
**Al aprobar su plan, vigila:** que la naturaleza de TRADUCCIÓN NO OFICIAL
quede declarada en todo lo que la fuente sostenga — si el plan la trata
como equivalente al original de AASHTO, recházalo.

Pega desde aquí hacia abajo como primer mensaje de la sesión nueva:

---

Antes de tocar código: entra en plan mode / propón tu plan y espera mi aprobación.

Contexto: repo Proyecto_alcantarillas. Rige CLAUDE.md (reglas de
corrección, tracker, subagentes, jerarquía de fuentes). El dueño consiguió
la segunda fuente ausente top y ya está en normas/: «AASHTO M 294-11
Tuberia corrugada de polietileno 300 a 1500 mm (traduccion no oficial).pdf».
Datos del ejemplar, medidos: 17 páginas, texto extraíble, SHA-1
7cecb19f73e4d101866832a3fc57db752fa53379, y — el dato que gobierna toda la
sesión — es una TRADUCCIÓN AL ESPAÑOL NO OFICIAL del M 294-11 (de un sitio
de documentos compartidos), no el original en inglés de AASHTO. La portada
interior declara «Designación AASHTO: M 294-11» y el ámbito cubre tamaños
nominales de 300 a 1500 mm (12 a 60 in.).

Tarea, en orden:
1. DECIDE PRIMERO, leyendo src/normativa/esquema.py, cómo la casa modela
   una fuente derivada: Fuente presente con su naturaleza en nota, campo
   convive_con, u otra vía. La decisión con su argumento va en la nota de
   la Fuente y, si es una decisión de peso, en docs/decisiones_diferidas.md.
   El original en inglés SIGUE AUSENTE: su entrada de FUENTES_AUSENTES se
   actualiza (qué desbloquearía verificar contra el original) pero no
   desaparece, salvo que el esquema mande otra cosa.
2. Incorpora la fuente (sha1 de arriba — verifícalo tú, paginación medida,
   texto_extraible según midas) y, con verificador-normativo, transcribe
   lo que sostiene el tope del HDPE: la serie de tamaños nominales
   300–1500 mm (la sección de ámbito 1.1.1 y la tabla de dimensiones si
   existe). Transcripción completa, en el idioma del ejemplar, con la
   marca de traducción en la cita.
3. Cierra lo que destraba, con la cautela de fuente derivada:
   a. D_MAX["hdpe"] (~1.50 m): hoy es tope de catálogo [A]
      ('D_max_catalogo'). Si la serie 300–1500 mm lo sostiene, el criterio
      gana el respaldo — decide con el esquema si eso cambia algo de su
      ficha (¿pasa a [C] apoyado en traducción? ¿queda [A] con la fuente
      anotada?). No lo decidas por conveniencia: argumenta con la
      taxonomía de CLAUDE.md y decláralo.
   b. La exención de caso patrón de M2 (SIS-F-13): la serie de diámetros
      tabulada era lo que faltaba para el dorado de M2 junto a M170M/M36.
      Evalúa si con las tres fuentes ya se puede construir el caso patrón
      SIN inventar valores (el conflicto #7 sigue vigente: el dorado sale
      de la tabla, no de la fórmula). Si se puede, hazlo y actualiza la
      guardia y la ficha; si la naturaleza de traducción lo impide o lo
      degrada, decláralo y déjalo censado con esa razón.
   c. Revisa qué notas del registro/criterios decían «M294 ausente» y
      actualízalas a lo que ahora es cierto.
4. Actualiza el tracker para los IDs que cambien de estado (openpyxl
   preautorizado) y lanza auditor-adversarial con veredicto por pieza
   antes de fusionar. Manifiestos y línea base regenerados si corresponde,
   con diff declarado.

Reglas duras: cero valores inventados; la palabra «traducción no oficial»
acompaña a TODA cita de esta fuente; ningún valor de cálculo cambia salvo
que una tabla verificada lo exija (commit separado con caso patrón, dicho
en el plan antes).

Cierre: suite en verde; commit «normativa(N2): AASHTO M 294-11 (traducción
no oficial) incorporada — <qué cerró y qué quedó esperando al original>»;
entrega en origin/main; conteo como par passed+skipped=collected desde
origin/main, con el entorno.
