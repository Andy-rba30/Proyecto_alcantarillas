# Prompt para reanudar la cadena T en una sesión NUEVA (copiar tal cual)

```text
Eres la sesión orquestadora de la «Cadena de prompts T» sobre Andy-rba30/Proyecto_alcantarillas, que se interrumpió por límite de uso. Retómala donde quedó.

1. Repositorios: abre Andy-rba30/Proyecto_alcantarillas (escritura, rama main), Andy-rba30/Normas (lectura) y Andy-rba30/Cotas-esviaje-alcantarillas (lectura; el INFORME está en su rama claude/serene-mayer-88a2o0).

2. Antes de nada, lee en la rama tesis/orquestacion-estado de Proyecto_alcantarillas la carpeta docs/planes_mejora/orquestacion_T/: ESTADO_SESION.md (punto de reanudación: qué está en main, qué ramas hay y en qué estado), AUDITORIAS_PENDIENTES.md, ORQUESTACION.md, NOTAS_ORQUESTADOR.md, USO.md, los ENCARGO_T-n.md y los dos DICTAMEN_*.md. Lee también CLAUDE.md entero y docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md en main. Ahí están mis decisiones ya tomadas: no me las vuelvas a preguntar.

3. Instala dependencias (requirements.txt, requirements-dev.txt, openpyxl), exporta NORMAS_DIR apuntando al clon de Normas y corre la suite sobre origin/main para confirmar que el par coincide con el último que ESTADO_SESION.md anota (no hay tkinter: configuración «PyMuPDF sí · Tk no»).

4. Continúa desde el estado que diga ESTADO_SESION.md. Las ramas tesis/T-n del remoto (y las instantáneas tesis/wip-progreso-T-n) tienen el trabajo sin integrar: termina lo que falte de cada una, pasa un auditor adversarial sobre cada diff de cálculo, aplica sus correcciones e intégralas en main en serie, un commit tesis(T-n) por prompt con el ritual de cierre. Sigue el grafo de la cadena: T-3, T-5, T-7a, T-8, T-9 en paralelo donde se pueda; T-7b → T-7c; T-10 → T-11 → T-12.

5. Reparto de modelos: usa Opus 5.5 en esfuerzo extra para todo lo que no requiera Fable (implementación de T-3, T-5, T-7a, T-8, T-9, integraciones, T-10, T-12) y reserva Fable para las auditorías adversariales de los prompts de cálculo y para T-7b, T-7c y T-11. Lo hecho con Opus pasa una auditoría con Opus antes de integrarse y otra con Fable cuando haya cuota.

6. Reglas que no se negocian: las entradas de diseño no se corrigen ni se rellenan con valores por defecto; ningún valor inventado (criterio [A] con ventana o CriterioPendienteError); nada se rompe; ningún diámetro ya dimensionado del fixture se mueve sin preguntarme; todo verificado contra el PDF de la norma y coherente ingenierilmente, porque es para una tesis.

7. Al terminar cada prompt dame un resumen corto: IDs cerrados (entero / en parte / no), tests nuevos, números movidos y por qué, qué quedó diferido y el SHA. Guarda el progreso en el remoto en cada paso, mantén actualizados ESTADO_SESION.md y USO.md en la rama tesis/orquestacion-estado, y dime en cada hito los tres límites (5 horas, semanal de todos los modelos y semanal de Fable). Cuando Fable llegue a 96–97 % guarda todo y déjame el prompt de continuación; a 99 % revisa el avance y, si es significativo, guarda y déjamelo otra vez.
```
