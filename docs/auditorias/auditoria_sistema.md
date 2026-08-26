# Auditoría técnica externa del sistema

**Commit auditado `2e1708abd91f6de1b80ec5456563cd1688e715bc` — 725 passed, 1 skipped (726 collected).**

*Vía de evitamiento, distrito de La Unión (Piura) — nivel de perfil.*
*Auditoría de solo lectura: no se corrigió nada, no se propuso ningún fix. El árbol
de trabajo quedó sin modificar en el commit auditado y la suite sigue en 725/1.*

---

## Qué es este documento

Inventario de los **97 hallazgos** que sobrevivieron a la verificación, sobre el
grafo de módulos, el código muerto, los literales fugados, el cableado de los
criterios, la taxonomía de excepciones y los tests. Cada hallazgo lleva el
comando que lo reproduce y su salida real.

| | |
|---|---|
| Commit auditado | `2e1708abd91f6de1b80ec5456563cd1688e715bc` |
| Suite ejecutada | 725 `passed`, 1 `skipped` (726 `collected`) |
| Test saltado | `tests/test_MD.py:344` — `skipif` permanente: la condición que guarda (ausencia de `M5_verificaciones`) ya no puede darse |
| Hallazgos consolidados | 97 |
| Hallazgos crudos / verificados / refutados | 118 sobrevivientes de la verificación, 3 refutados, resto fusionado por duplicación entre dimensiones |

### Recuento

| Severidad | | Clasificación | |
|---|---|---|---|
| BLOQUEANTE | 1 | defecto real | 48 |
| GRAVE | 14 | deliberado sin documentar | 22 |
| MENOR | 43 | deliberado documentado | 27 |
| OBSERVACIÓN | 39 | | |

La columna de clasificación separa lo que el proyecto declara a propósito de lo
que no. **27 de los 97 son decisiones deliberadas y documentadas**: están aquí
porque la auditoría las examinó y las dio por buenas, no porque haya algo que
corregir. Otros **22 son igual de intencionales y no están escritos donde un
revisor los buscaría**.

## Método

Once auditores independientes recorrieron seis dimensiones (A grafo de módulos,
B código muerto, C literales fugados, D cableado y clasificación, E excepciones,
F tests), cada uno con la instrucción de no reportar nada que no pudiera
reproducir con un comando. Sus 118 hallazgos crudos pasaron por una
**verificación adversaria de doble lente**:

- **Lente 1 — reproducibilidad.** Correr el comando, comprobar `archivo:línea`
  con `sed -n`, buscar activamente el consumidor que el auditor no encontró
  (`getattr`, f-string, iteración de dict, `dataclasses.fields`, marcador de
  plantilla), y refutar por defecto ante la duda.
- **Lente 2 — decisión documentada.** Buscar en `Claude.md`, la hoja de ruta,
  los dos manifiestos, `docs/auditoria_y_ruta_despliegue_v9.md` y los docstrings
  completos si la decisión ya estaba declarada, y reclasificar en consecuencia.

El veredicto del verificador prevalece sobre el del auditor: es quien corrió los
comandos y quien fue a leer la documentación. De los 118, **41 quedaron
CONFIRMADOS tal como se reportaron, 77 IMPRECISOS** (reales, pero mal descritos,
mal ubicados o con la severidad inflada — va la versión corregida) y **3
REFUTADOS**.

### Convenciones de severidad

| | |
|---|---|
| **BLOQUEANTE** | Produce un resultado incorrecto en la memoria entregable, rompe la regla nuclear («rellenar un vacío en silencio es el peor error posible»), o permite que un valor no declarado entre al cálculo |
| **GRAVE** | Rompe una regla explícita de la constitución con consecuencia práctica |
| **MENOR** | Rompe una regla sin consecuencia de cálculo hoy |
| **OBSERVACIÓN** | Riesgo latente o deuda, sin regla incumplida |

## Lo que hay que leer primero

**A-01, el único bloqueante.** Un criterio declarado desde la GUI «solo para
esta corrida» gobierna el cálculo y la memoria lo imprime como *sin valor
declarado*; el bloque de vacíos tampoco lo lista. `M11_reporte.py:1040` lee
`ca.criterio(clave).valor` —el valor del archivo— y nunca consulta los overrides.

**B-01, `clase_sitio` es inerte.** Cero invocaciones desde producción. M11
imprime solo los criterios registrados como usados, y en una corrida completa se
registran 6 de 46. La memoria nunca declara la adopción de Clase de Sitio F que
la hoja de ruta §0.5 obliga a escribir «con esas palabras» — el mismo documento
llama a su versión mal etiquetada «el error más grave que ha tenido este
expediente».

**A-02 y A-03, documentación que contradice al código.** V4b (HW/D ≤ 1.5) no
existe en ninguna línea y dos docstrings afirman que M5 la ejecuta; ocho
docstrings y dos filas del manifiesto declaran pendientes tres criterios ya
cerrados con cita.

> **Sobre el texto.** De «Tabla consolidada» en adelante, el cuerpo va tal como
> lo produjeron los auditores y los verificadores, sin acentos: intercala salida
> literal de comandos y reescribirlo arriesgaría alterar la evidencia.

## Dos incidentes de la propia auditoría

Se registran porque son hallazgos por derecho propio, aunque los provocara la
auditoría y no el código:

1. Un agente sobrescribió `tests/ejemplo_puntos.informe.json` al correr la CLI.
   Es un fixture versionado que `cli.py:1408` pisa por defecto y que ningún test
   referencia: cualquier corrida de la CLI sobre el CSV de ejemplo lo modifica.
2. `coverage` deja `.coverage` en la raíz y `.gitignore` no lo cubre.

Ambos fueron revertidos.

---

## Tabla consolidada

| ID | Sev | archivo:linea | Descripcion | Clasificacion |
|---|---|---|---|---|
| A-01 | BLOQ | src/modulos/M11_reporte.py:1040,1043 | `bloque_criterios` lee `ca.criterio().valor` y no `_OVERRIDES`: la memoria imprime "sin valor declarado" un criterio que el calculo si uso, y el bloque 4 tampoco lo lista | defecto real |
| A-02 | GRAVE | src/modulos/M4_control.py:24; src/modelos.py:564; src/criterios_adoptados.py:886 | V4b (HW/D <= 1.5) no existe en ninguna linea de codigo, `HW_D_max` no lo invoca nadie, y dos docstrings afirman que M5 la ejecuta | defecto real |
| A-03 | GRAVE | src/modulos/M2_material.py:40-42,264; src/modulos/M5_verificaciones.py:11-19,50,478; src/modulos/M7_geometria.py:21,157,262-265,375; src/modulos/MD.py:479-482 | Ocho docstrings y dos filas del manifiesto declaran pendientes o `[C]` tres criterios ya cerrados (v_max_tmc 4.6, v_max_hdpe 4.6, h_relleno_min_concreto_tmc 0.30 `[N->]`); M2 dice "Dos" y enumera tres | defecto real |
| A-04 | GRAVE | src/modulos/M5_verificaciones.py:305-318,56-69 | `cota_entrada_supuesta` adopta `cota_terreno` como cota de fondo y gobierna V4, V7 y la rasante de M7/M8; no existe entrada en criterios_adoptados.py, ni en el Anexo A, ni en docs/, y M11 imprime el numero sin marcarlo como supuesto | deliberado sin documentar |
| A-05 | MENOR | cli.py:485; src/modulos/M11_reporte.py:557 | `_bloqueo` resuelve toda clave con `ca.criterio()`: un `[S]` de corredor pendiente saldria como KeyError (fallo de programa) en vez de ErrorProyecto; hoy inalcanzable porque los tres datos tienen valor | defecto real |
| A-06 | MENOR | src/modelos.py:451,466-468; src/modulos/M2_material.py:282 | El campo anotado `Optional[Tuple[float,float]]` transporta el escalar 4.6 en TMC/HDPE, y el docstring de `v_max_definida` dice "False para TMC y HDPE" cuando devuelve True para los tres | defecto real |
| A-07 | MENOR | src/modulos/M11_reporte.py:5,903,953 | M11 declara "sin calcular nada nuevo" y calcula y/D en dos sitios en vez de leer el valor de V1 | defecto real |
| A-08 | MENOR | src/modulos/MD.py:56-71 | El docstring de MD abre con "M5 todavia no existe en el repositorio" y apoya en esa premisa la justificacion del Protocol y de la importacion perezosa | defecto real |
| A-09 | MENOR | src/modulos/MD.py:405-411,492-500 | El diagnostico de Familia C que MD escribio es inalcanzable desde el CSV: gana antes `DatoFaltanteError('Q_m3s')`, y la rama de `_motivo_sin_candidatos` no se ejecuta nunca | defecto real |
| A-10 | MENOR | gui/app.py:14-22,216-219,697-701 | El docstring de la GUI lista tres pestanas y la aplicacion crea cuatro; la omitida es la que reescribe criterios_adoptados.py, y la lista de exportaciones omite el CSV | defecto real |
| A-11 | MENOR | gui/app.py:321-323 | La leyenda de etiquetas anuncia `[N]` (imposible en ese archivo) y omite `[S]`, que si esta presente | defecto real |
| A-12 | MENOR | gui/app.py:5-7,202-204,277-285 | El docstring afirma reutilizar el "campo validable" de legacy/Tc.py; no existe y `color_borde_ok` queda muerto | defecto real |
| A-13 | MENOR | src/modulos/M5_verificaciones.py:4-5; cli.py:573-577 | V2b (sedimentacion/colmatacion) de la Fase 5 no existe en ninguna linea de codigo y el alcance reducido a nueve verificaciones no esta escrito | deliberado sin documentar |
| A-14 | MENOR | src/criterios_adoptados.py:279-285; gui/app.py:489 | El docstring dice `valor=None` y la regex reescribe cualquier valor dejando `fuente` intacta; el boton de la GUI se habilita para toda fila | deliberado documentado |
| A-15 | MENOR | Claude.md:55-56; tests/test_sin_literales.py:16-17 | La constitucion y el test guardian siguen diciendo que constantes_fisicas.py tiene "hoy solo la gravedad": son cinco nombres | deliberado documentado |
| A-16 | OBS | src/modulos/M0_carga.py:364-381 | Dos validaciones cruzadas (diametro implicito, entrega por gravedad) no son filas de la tabla de Sec. 1.5 y solo estan razonadas en comentarios de linea | deliberado sin documentar |
| A-17 | OBS | gui/app.py:748; cli.py:886-887 | La GUI no expone `--alcance`: siempre corre "expediente" y `memoria_perfil.html` es inalcanzable desde la interfaz | deliberado sin documentar |
| A-18 | OBS | gui/app.py:905-912,928-947 | La sesion JSON no guarda ni restaura los criterios declarados "solo para esta corrida" | deliberado sin documentar |
| A-19 | OBS | src/constantes_normativas.py:12-24; src/modulos/M2_material.py:273,276 | M2 lee `HDS5_INLET` y `H_RELLENO_MIN` del archivo cuya linea 24 lo prohibe; la excepcion por-clave esta insinuada en el bloque y explicada en M2, pero la frase final no se cerro | deliberado documentado |
| A-20 | OBS | src/constantes_normativas.py:124-126 | El comentario de la discrepancia 19.63 vs 19.62 cita lineas de la hoja de ruta que ya no corresponden (reales: 436, 440, 797, 908) | deliberado documentado |
| A-21 | OBS | cli.py:736-745 | `cli._fase_8` repite la resta "subrasante menos clave" sin la guarda `DatoInvalidoError` de V7; hoy sin efecto porque M8 se detiene antes | deliberado documentado |
| B-01 | GRAVE | src/criterios_adoptados.py:373-375,386,1988; src/modulos/M11_reporte.py:1032 | `clase_sitio` solo se invoca en el bloque `__main__`: no entra en `criterios_usados()` y la memoria (perfil y expediente) nunca declara la adopcion que la hoja de ruta:111 ordena escribir con esas palabras | defecto real |
| B-02 | MENOR | src/modelos.py:568; src/modulos/M4_control.py:392 | `ControlEntrada.HW_sobre_D` se calcula, se guarda y no lo lee ninguna ruta de produccion; su docstring dice que es "lo que compara V4b" | defecto real |
| B-03 | MENOR | Claude.md:109-110; requirements.txt | La lista de dependencias de la constitucion incluye jinja2 y pandas (cero usos, no instalados) y omite weasyprint, que si esta pineado | defecto real |
| B-04 | MENOR | src/modelos.py:375-376; src/modulos/M0_carga.py:386-389; cli.py:545-553 | El procedimiento de Sec. 1.3 ("TW se calcula, no se mide") no esta implementado: `Q_receptor_m3s` y `cota_TW` se validan y no alimentan nada; un CSV con `cota_TW` llena sigue exigiendo `--tw` | deliberado sin documentar |
| B-05 | MENOR | src/criterios_adoptados.py:1963; docs/hoja_de_ruta_alcantarillas_v8.md:660 | `parametros_sensibilizables()` (entregable 5, analisis de sensibilidad) solo la consumen los tests; ningun bloque de alcance lo declara diferido | deliberado sin documentar |
| B-06 | MENOR | cli.py:1379-1396,1439-1443 | `--plantilla memoria_perfil.html` sobre corrida de expediente descarta 13 647 caracteres de pendientes; el docstring afirma que las dos plantillas "comparten el contrato de marcadores" | deliberado sin documentar |
| B-07 | OBS | src/modelos.py:78-81 | `CriterioPendienteError.mensaje_gui` no tiene consumidor de produccion; la GUI muestra los pendientes por la via del `Bloqueo`, mas rica | deliberado sin documentar |
| B-08 | OBS | src/modelos.py:1244-1255 | `PeriodoRetorno.exigir_anios` no tiene llamador: los cinco accesos al TR tratan el None explicitamente y ninguno necesita el entero | deliberado sin documentar |
| B-09 | OBS | M2:127, M3:100, M4:182-183, M5:139, M8:134, MD:117 | Siete constantes `NUMERAL_*` de modulo declaradas y nunca leidas; dos de ellas por bloqueos ya documentados | deliberado sin documentar |
| B-10 | OBS | legacy/Tc.py; Claude.md:116-119 | legacy/Tc.py (803 sentencias, 185 literales prohibidos, anuncia matplotlib y una plantilla inexistente) no lo importa nadie, no lo prueba nadie y no lo barre nadie, sin una linea que declare ese estatus | deliberado sin documentar |
| B-11 | OBS | src/criterios_adoptados.py:604-605; src/modulos/MD.py:539 | `homogeneidad_serie_fen` no bloquea por una llamada `valor()`: el bloqueo es indirecto via la columna `Q_m3s` vacia, y esta escrito en el docstring de `disenar_lote` | deliberado documentado |
| B-12 | OBS | src/modelos.py:378; src/modulos/M11_reporte.py:145-160 | `NF_profundidad_m` no la lee ningun modulo (la pieza que la usaria es la estabilidad del cabezal, declarada no ensamblada) y es la unica columna de Sec. 1.2 ausente de `CAMPOS_CSV` | deliberado documentado |
| B-13 | OBS | src/modelos.py:1275; src/modulos/M1_clasificacion.py:337 | `PerfilFamilia.verificaciones_aceptacion` solo lo escribe M1 y lo leen dos asserts; el propio docstring declara que la Fase 5 aplica igual punto por punto | deliberado documentado |
| B-14 | OBS | src/constantes_normativas.py:29,30,91,146,147,149,152,161,173,283,284,287,293 | Trece constantes `[N]` sin ningun consumidor de produccion; el archivo se declara transcripcion literal del Anexo B y el manifiesto las cataloga una por una | deliberado documentado |
| B-15 | OBS | src/criterios_adoptados.py:1045-1056 | `demanda_sismica_licuefaccion = 1000` no lo invoca nadie: con valor y sin invocacion no cae en ninguno de los tres bloques de M11 y desaparece de la memoria | deliberado documentado |
| B-16 | OBS | src/modelos.py:377; src/modulos/M0_carga.py:209 | `sucs_fundacion` es columna obligatoria y ningun modulo la lee; la obligatoriedad viene del encabezado de Sec. 1.2 y su consumidor (`c_phi_fundacion`) es un pendiente externo declarado | deliberado documentado |
| B-17 | OBS | src/modelos.py:1060-1116; src/modulos/M9_cabezal.py:736 | `EmpujesTrasdos` no lo alcanza ninguna corrida: solo lo observan los tests, y `NOTA_ESTABILIDAD_CABEZAL` (impresa en la memoria) declara que la CLI no ensambla el plano de empuje | deliberado documentado |
| B-18 | OBS | src/modelos.py:599,1135-1136,1157,1180 | Cinco campos de dataclass escritos y nunca leidos; cuatro tienen su decision escrita, solo `ahogado_por_TW` no viaja al JSON ni al HTML sin cobertura documental | deliberado documentado |
| B-19 | OBS | src/criterios_adoptados.py:347,1013,1024,1033,1325 | Cinco criterios sin consumidor (`PERFIL_SUELO_PRESUNTO`, `c_phi_fundacion`, `capacidad_portante_adm`, `Mw_licuefaccion`, `angulo_aletas`); los cuatro vacios se imprimen en el bloque de pendientes | deliberado documentado |
| B-20 | OBS | src/modulos/M9_cabezal.py:1265,1288,1353,1361,1380,1389,1406 | Las siete funciones de armado de 9.4 no tienen llamador porque su insumo (`predimensionamiento_cabezal`) es un vacio declarado que la CLI registra como Bloqueo en cada corrida | deliberado documentado |
| B-21 | OBS | src/modulos/M9_cabezal.py:1018,1047,1086-1089 | `n_q/n_s_zapata_en_talud` no tienen llamador interno porque la funcion que las usaria se detiene en `N_cq_N_gammaq_meyerhof`; el docstring declara que N_s se calcula aparte al leer los abacos | deliberado documentado |
| B-22 | OBS | src/criterios_adoptados.py:181; M11:196; modelos.py:466; M9:561 | Cuatro APIs publicas sin consumidor de produccion; `aplica_sobrecarga_trasdos` declara su motivo en el docstring y la acusacion sobre `v_max_definida` es falsa | deliberado documentado |
| B-23 | OBS | src/modulos/M5_verificaciones.py:338-341; src/modulos/M7_geometria.py:403-409 | Dos guardas provablemente inalcanzables (tabla de resguardo exhaustiva; esviaje negativo que M0 ya rechaza), ambas declaradas defensivas en sus docstrings | deliberado documentado |
| C-01 | MENOR | tests/test_sin_literales.py:223 | La guardia de substring de `factor_muro` se evade con comillas simples: una entrada `'factor_muro': Criterio(...)` dentro de CRITERIOS deja la suite en 725 passed | defecto real |
| C-02 | MENOR | tests/test_sin_literales.py:177-206,221; test_M8:177-179; test_M5:180-186; test_M11:643-647; test_criterios_adoptados:247; test_datos_sitio:153 | 22 asserts comprueban subcadenas del texto fuente de modulos .py: un comentario o un docstring los satisface igual que una declaracion | defecto real |
| C-03 | MENOR | tests/test_sin_literales.py:79; src/dominios.py:38 | La marca se busca como substring de la linea: vale dentro de un string o de un docstring, y en dominios.py ya ocurre | defecto real |
| C-04 | MENOR | tests/test_sin_literales.py:65-73,117 | `_nodos_de_indice` exime TODO entero dentro de un `Subscript`: una clave numerica de tabla (`CAUDAL_POR_TR[500]`) pasa invisible | defecto real |
| C-05 | MENOR | tests/test_sin_literales.py:130-131,164-166 | La lista de exentos se aplica por nombre de archivo a cualquier profundidad: `src/modulos/dominios.py` quedaria exento sin declaracion | defecto real |
| C-06 | MENOR | tests/test_sin_literales.py:51,147 | `barrido()` solo recorre src/: cli.py (8 literales) y gui/app.py (151) quedan sin vigilancia, sin que ningun documento diga por que | deliberado sin documentar |
| C-07 | MENOR | tests/test_sin_literales.py:76-81 | La marca `# literal-ok` en linea propia exime todos los literales de la linea siguiente; el docstring la acota a "expresiones partidas" | deliberado documentado |
| C-08 | OBS | tests/test_sin_literales.py:57,115,119 | `valor in NUMEROS_PERMITIDOS` deja pasar complejos (`0j`, `2+0j`) ademas de los floats declarados | defecto real |
| C-09 | OBS | tests/test_sin_literales.py:111-124 | El detector es puramente sintactico: `int("13")/int("1000")`, `float("4.6")` e `int("500")` son invisibles | defecto real |
| C-10 | OBS | tests/ejemplo_puntos.informe.json; cli.py:1475 | Salida de corrida versionada que nadie lee y que cualquier ejecucion del CLI reescribe; .gitignore ya excluye los HTML generados y no este patron | defecto real |
| C-11 | OBS | tests/test_sin_literales.py:130; src/plantillas/*.html | El barrido solo mira `.py`: las dos plantillas bajo src/ quedan fuera (hoy sin valores de calculo) | deliberado sin documentar |
| C-12 | OBS | src/modulos/M1_clasificacion.py:54-62 | El ejemplo de uso de M1 da luces sin la salvedad que si lleva el test; los ids son los del fixture, no puntos reales del expediente | deliberado sin documentar |
| C-13 | OBS | src/modulos/M11_reporte.py:415-417,424,337 | M11 convierte prosa Markdown de la hoja de ruta en las 15 filas del bloque de pendientes; declarado en el docstring, con fallo ruidoso si el formato cambia | deliberado documentado |
| D-01 | GRAVE | src/criterios_adoptados.py:464,391; src/modulos/M9_cabezal.py:24 | `F_pga` se defiende con "sin SPT no hay clase de sitio definitiva" y `clase_sitio` dice "el sitio es Clase F... esa parte no cambia"; F_PGA_TABLA no tiene fila F y solo F_pga llega a la memoria | defecto real |
| D-02 | MENOR | docs/manifiesto_citas.md:457,519-521 | El censo del manifiesto declara 1 `[N->]` y 14 `[C]` (son 2 y 13) y titula "Los 33 criterios [A]" una tabla que incluye cuatro `[C]` y omite `clase_sitio` | defecto real |
| D-03 | MENOR | src/criterios_adoptados.py:781; docs/manifiesto_citas.md:445,471 | "Es la unica entrada que se lee con `valor_si_declarado()`" es falso en codigo y en el manifiesto: hay cuatro mas | defecto real |
| D-04 | MENOR | src/criterios_adoptados.py:496; src/modulos/M9_cabezal.py:327 | La sensibilidad de `k_v` es (0.0, 0.5) y su comentario dice "0.5*k_h", que con la cadena de hoy es 0.25; la hoja de ruta:719 prescribe (0, 0.5·k_h) | defecto real |
| D-05 | MENOR | src/criterios_adoptados.py:1325-1331; src/modulos/M11_reporte.py:1126 | `angulo_aletas` es el unico vacio sin `reemplazado_por` y con fuente que no empieza por PENDIENTE: la memoria imprime el enunciado del vacio en la columna "Que lo resuelve" | defecto real |
| D-06 | MENOR | src/datos_sitio.py:194-216,261-264; cli.py:1128 | `Z_E030` declara heredar la trazabilidad de `ZONA_SISMICA_LA_UNION` y no hereda su verificacion abierta: queda fuera de `trazabilidad_incompleta` del JSON | defecto real |
| D-07 | MENOR | src/datos_sitio.py:261-264; cli.py:1120-1140 | `criterios_adoptados` no expone el homologo de `datos_con_verificacion_pendiente()`: el JSON dice que datos de sitio estan sin cerrar y no que criterios (hoy 10 con valor) | defecto real |
| D-08 | MENOR | src/criterios_adoptados.py:386-457 | `clase_sitio` es el unico de los 30 `[A]` con valor y sin sensibilidad; la guardia solo la exige a los `opcional=True` | deliberado sin documentar |
| D-09 | MENOR | src/datos_sitio.py:97-118 vs src/criterios_adoptados.py:1787-1878 | `datos_sitio.py` no tiene guardia al importar: `DatoSitio(trazabilidad='', etiqueta='A')` se construye sin error mientras el homologo de criterios lo rechaza | deliberado sin documentar |
| D-10 | MENOR | src/modulos/M2_material.py:271,277,282 | M2 lee cuatro criterios no opcionales con `valor_si_declarado()`; la decision esta escrita, pero el docstring nombra la funcion vieja y deja fuera `n_manning_hdpe`, que degrada a TypeError | deliberado documentado |
| D-11 | MENOR | src/criterios_adoptados.py:732,742 | `n_manning_hdpe` es un valor normativo aplicado por analogia etiquetado `[A]`, contra la regla de coherencia de la hoja de ruta:40 que produjo `[N->]` en los dos casos gemelos | deliberado documentado |
| D-12 | OBS | src/criterios_adoptados.py:749-772; docs/manifiesto_citas.md:590-593 | `v_max_hdpe` y `v_max_tmc` no llevan ancla `vacio_verificado`; §14 anuncia consolidar las nueve afirmaciones negativas y entrega una | deliberado sin documentar |
| D-13 | OBS | src/criterios_adoptados.py:1187-1214 | `clases_producto_por_relleno` es el unico `[C]` con `valor=None`; registrado como pendiente en la auditoria v9 y en el manifiesto | deliberado documentado |
| E-01 | GRAVE | gui/app.py:749,755 | El manejador de EJECUTAR captura `(OSError, ValueError)` antes del brazo con traza: un ValueError nacido en el pipeline se muestra como "No se pudo leer la entrada"; la CLI usa el brazo estrecho correcto | defecto real |
| E-02 | MENOR | src/modulos/M9_cabezal.py:852,876,1163,1257 | Cuatro `DatoInvalidoError` validan strings que produce el propio codigo: un fallo de programa se presenta como problema del expediente | deliberado sin documentar |
| E-03 | OBS | gui/app.py:868,883,899 | Los tres exportadores capturan `except Exception` sin traza, mientras el patron hermano de la linea 755 si la imprime | defecto real |
| E-04 | OBS | gui/app.py:494 | El unico `raise` de la GUI valida un campo tecleado con ValueError en vez de la taxonomia; se atrapa a tres lineas en sus dos llamadores | deliberado sin documentar |
| E-05 | OBS | src/criterios_adoptados.py:144-173,1780 | Declarar un criterio desde la GUI con valor fuera de rango sale como ValueError/KeyError, fuera de ErrorProyecto; el docstring declara la guardia para los tres caminos | deliberado documentado |
| E-06 | OBS | src/modelos.py:108-109; src/modulos/M5_verificaciones.py:409 | `modelos.py` ensancha `DatoFaltanteError` a "o de un tablero externo" y el codigo lo explota; Claude.md:95-96 sigue diciendo "el nombre de la columna" | deliberado documentado |
| F-01 | GRAVE | gui/app.py:1-958 | 584 sentencias ejecutables con CERO tests; la GUI reimplementa la traduccion de banderas y decide el tipo del valor declarado, y ningun documento la exime | defecto real |
| F-02 | GRAVE | src/criterios_adoptados.py:299-320 | La rama que SI escribe el archivo fuente de los criterios nunca se ejecuta en la suite: el unico test comprueba el rechazo previo | defecto real |
| F-03 | GRAVE | tests/fixtures/casos_patron.py:41,48 | Los TR dorados de CP-1 (70.63 y 35.29) no salen de la formula que el propio fixture declara (70.593 y 35.323); el error cabe justo bajo la tolerancia | defecto real |
| F-04 | GRAVE | src/modulos/M9_cabezal.py:442-443,462-463,490,493-494 | El caso limite de Rankine no cubre las convenciones de beta, i y delta; siete mutantes de signo sobreviven pese a que docstring y test afirman que "si un signo esta cambiado, aqui se ve" | defecto real |
| F-05 | GRAVE | src/modulos/M9_cabezal.py:629; tests/test_M9_cabezal.py:361 | `empuje_activo_sismico_total` sin test de valor: 4/4 mutantes sobreviven y el unico assert es tautologico (`incremento == P_AE - P_A`) | defecto real |
| F-06 | GRAVE | src/modulos/M9_cabezal.py:958,961 | Ningun test asserta el FS de E3: `FS = R*A` y la guarda invertida (`fs = inf` siempre) pasan la suite; el test hermano de capacidad portante si asserta valor | defecto real |
| F-07 | GRAVE | src/modelos.py:1099,1111-1115 | `empuje_horizontal_total` y `momento_volcante` sobreviven a `*`→`/` y `+`→`-`: los unicos asserts son comparaciones de orden | defecto real |
| F-08 | GRAVE | src/modulos/M7_geometria.py:442,454,532 | La rama viva de longitud del conducto y proyeccion de taludes (Sec. 7.B) no tiene assert de valor: tres mutantes sobreviven | defecto real |
| F-09 | MENOR | src/modulos/M11_reporte.py:947-950,962-963 | El cuadro resumen CSV (entregable 3) nunca se genera con un punto dimensionado: el unico test comprueba cabecera y numero de filas | defecto real |
| F-10 | MENOR | M1:165,310,389; M4:272,443; M5:495; M9:466,1180; cli.py:250,255,292,310 | Trece `raise` de ErrorProyecto sin ninguna cobertura, dos de ellos alcanzables con una llamada normal | defecto real |
| F-11 | MENOR | cli.py:1368-1371,1492-1499 | Seis banderas del CLI sin cobertura, incluidas `--pdf`, `--csv-resumen` y `--criterios`: el cableado bandera->funcion no se ejercita | defecto real |
| F-12 | MENOR | src/modulos/M0_carga.py:230-235 | La celda de texto vacia (id, progresiva_km, familia, sucs_fundacion) nunca se ejecuta en la suite pese a ser la mitad de la definicion de `DatoFaltanteError` | defecto real |
| F-13 | MENOR | tests/fixtures/casos_patron.py:32-237 | Seis modulos de calculo no consumen ningun caso patron; para cuatro de ellos (M2, M7, M8, M10) el fixture no define ninguno | defecto real |
| F-14 | MENOR | tests/test_M9_cabezal.py:103-137,175 | Los valores dorados de CP-7 estan duplicados como literales en vez de leerse del fixture: corregir el fixture no llega a los tests de M9 | defecto real |
| F-15 | MENOR | tests/fixtures/datos_referenciales_prueba.md:9-10,34-35; ...NO_APLICADOS.md:10,28,45-50,86 | Los dos .md de fixtures afirman cosas del codigo ya falsas: v_max en 6.0/4.5, "siguen en valor=None", cinco sitios de AssertionError que no existen, remanso que ya no aborta la corrida, baseline 653 | defecto real |
| F-16 | MENOR | test_M6:58; test_M9:549,550,641,645,741; test_cli:99,114,115,123,207,237,342,359,388 | 15 asserts comparan floats con `==`, prohibido por Claude.md:111 sin exencion para tests (todos exactos por construccion) | defecto real |
| F-17 | MENOR | tests/test_M3_hidraulica.py:147-151 | Un test que no invoca codigo de produccion (unica llamada: `pytest.approx`) cuenta en el conteo de 725 y no protege nada | deliberado sin documentar |
| F-18 | OBS | docs/auditoria_y_ruta_despliegue_v9.md:44 | La auditoria previa sigue citando "12 modulos, 595 tests en verde"; hoy son 13 modulos y 725 passed | defecto real |
| F-19 | OBS | src/criterios_adoptados.py:302-312 | El patron de `escribir_valor_en_archivo` no alcanza a los 2 criterios de valor multilinea; ese ValueError es lo unico que impide escribirles un escalar encima | deliberado sin documentar |
| F-20 | OBS | tests/test_MD.py:344-352; src/modulos/MD.py:178,555 | Skip permanente documentado; la segunda rama de ImportError de MD (M5 presente sin `verificar`) no la cubre nadie | deliberado documentado |
| F-21 | OBS | M5:209,272,292,511; M7:482; M9:894,1397; M4:532 y 6 mas | El borde de la tolerancia (`TOL_UMBRAL_NORMATIVO = 1e-9`) no esta cubierto: invertir el signo deja la suite verde, en una banda fisicamente inalcanzable | deliberado documentado |

---

## Fichas

Las fichas marcadas **IMPRECISO** llegaron mal descritas del auditor que las encontro: lo que va escrito abajo es la version del verificador, que reprodujo los comandos y busco la documentacion.

### A-01 -- M11 imprime "sin valor declarado" un criterio que el calculo si uso
**Sev** BLOQUEANTE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M11_reporte.py:1029-1030,1040,1043
`bloque_criterios` lee `ca.criterio(clave).valor`, el valor del ARCHIVO, y nunca consulta `_OVERRIDES`. El calculo si usa el override y la clave entra en `criterios_usados()`, de modo que el criterio aparece en el bloque 3 tachado como pendiente; `criterios_sin_valor()` lo excluye, asi que el bloque 4 tampoco lo lista. La version en texto `ca.reporte_criterios` si lo marca, contra lo que el propio docstring promete. La GUI expone "Aplicar solo a esta corrida" y luego exporta HTML/PDF: es el camino normal.
**Regla:** Claude.md, Arquitectura: "Cada invocacion de un criterio o de un dato de sitio se registra, para que M11 imprima solo los usados" y "Rellenar un vacio en silencio es el peor error posible en este proyecto". Ademas contradice el docstring de la funcion (M11:1029-1030: "para que las dos digan exactamente lo mismo").
**Evidencia:**
```
$ python3 -c "...ca.establecer_valor_dinamico('talud_terraplen',1.5)..."
valor usado por el calculo: 1.5
texto CA: ['[A] talud_terraplen = 1.5  [declarado para esta corrida, no en archivo]']
HTML M11: <dt>Valor</dt><dd><span class="pendiente">sin valor declarado</span></dd>
criterios_sin_valor lo lista? False
$ sed -n '1038,1043p' src/modulos/M11_reporte.py
        c = ca.criterio(clave)
            f"<dt>Valor</dt><dd>{_valor_legible(c.valor)}"
$ grep -rn "valores_dinamicos|_OVERRIDES|en caliente" docs/   -> (sin resultados)
```
**Verificacion:** Lente 1 reprodujo la salida al caracter; lente 2 no encontro ninguna linea en docs/ que exima a M11 y si el docstring que promete lo contrario.

### A-02 -- V4b (HW/D <= 1.5) no existe en el codigo y dos docstrings afirman que M5 la ejecuta
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Detectado desde 3 dimensiones** (A1, B1, C2) - **Ubicacion** src/modulos/M4_control.py:24; src/modelos.py:564; src/criterios_adoptados.py:886; docs/hoja_de_ruta_alcantarillas_v8.md:457
La fila V4b de la tabla de Fase 5 no esta implementada, `HW_D_max` (valor 1.5, `[C]`) solo aparece en su propia declaracion y no entra en `criterios_usados()` tras una corrida completa. Dos docstrings afirman lo contrario: M4_control.py:24 dice que "HW/D <= 1.5 (V4b) ... son verificaciones de la Fase 5 y las hace M5", y modelos.py:564 dice que `HW_sobre_D` "es tambien lo que compara V4b". Ningun punto llega hoy a Fase 5 (V5 bloquea todo), de modo que no hay consecuencia de calculo.
**Regla:** Hoja de ruta Fase 5, fila V4b ("Relacion HW/D | 1.2 - 1.5 | [C]"). Claude.md: "Cada invocacion de un criterio ... se registra, para que M11 imprima solo los usados" -- un criterio del Anexo A que ningun modulo invoca no puede aparecer nunca en la memoria. No hay declaracion de fuera de alcance en ningun docstring ni en docs/.
**Evidencia:**
```
$ grep -rn "HW_D_max" src/modulos/ cli.py gui/ --include=*.py
(sin salida = nadie lo lee)
$ grep -rn "V4b" src/ cli.py gui/ tests/ --include=*.py
src/modulos/M4_control.py:24: ...que HW/D <= 1.5 (V4b) o que HW quede bajo
src/modelos.py:564:  ...y es tambien lo que compara V4b (HW/D <= 1.5).
$ python3 -c "...disenar_lote(cargar_puntos('tests/ejemplo_puntos.csv'), L=24.0, TW=0.30)..."
usados: [... 'remanso_derecho_via', 'resguardo_HW_subrasante', 'v_max_hdpe', 'v_max_tmc']
HW_D_max usado? False
$ python3 cli.py tests/ejemplo_puntos.csv --luz 3 --tw 0.4 --alcance perfil | grep -c 'Fase 4  sin dimensionar'
4   # ningun punto llega a Fase 5
```
**Verificacion:** Lente 1 reprodujo grep y corrida en las tres dimensiones; lente 2 hallo la hoja de ruta:75 ("El control real del embalse es V5"), que relativiza V4b pero NO declara que quede sin implementar.
**Nota de reconciliacion:** el verificador de A1 puso GRAVE y los de B1 y C2 pusieron MENOR tras comprobar que ningun punto alcanza Fase 5. Mantengo GRAVE porque el fondo del hallazgo, fusionado, es documentacion del propio codigo que afirma dos veces algo que no ocurre -- la misma clase que sostiene GRAVE en A-03 y D-01 --, y la evidencia de alcanzabilidad solo descarta BLOQUEANTE.

### A-03 -- Ocho docstrings y dos filas del manifiesto declaran pendientes tres criterios ya cerrados
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Detectado desde 4 dimensiones** (A1 x2, C2, D2) - **Ubicacion** src/modulos/M2_material.py:40-42,50,264; src/modulos/M5_verificaciones.py:11-12,16-19,45-54,478; src/modulos/M7_geometria.py:21,157,262-265,283,375; src/modulos/MD.py:479-482; docs/manifiesto_citas.md:253,324
`v_max_tmc` = `v_max_hdpe` = 4.6 y `h_relleno_min_concreto_tmc` = 0.30 con etiqueta `[N->]`. M2:40-42 dice "Dos de los criterios ... siguen sin valor" y enumera tres; M2:264 dice que los campos "pueden salir en None"; M5:11-19 lista V3 como "TMC / HDPE: criterio pendiente [C]" y V7 como pendiente en `factores_carga_aashto`; M7 describe seis veces el estado anterior (`[C]`, "M2 deja el campo en None"); MD:479-482 pone `v_max_tmc`/`v_max_hdpe` como ejemplo vivo de bloqueo cuando en la corrida real los tres materiales se detienen en `remanso_derecho_via`. Los mismos archivos se corrigen mas abajo (M5:260-266), lo que prueba que la actualizacion se hizo a medias.
**Regla:** Claude.md, Estilo y Fuente de verdad: el docstring de modulo es el contrato de responsabilidad y toda cita se verifica contra el expediente. El cierre esta registrado en docs/manifiesto_citas.md:361-362, :400-401 y :593-601 y hasta en un test (`tests/test_M5_verificaciones.py:571`): la documentacion de modulo contradice al expediente, no al reves.
**Evidencia:**
```
$ python3 -c "...CRITERIOS[k].valor/etiqueta..."
v_max_tmc  etiqueta=C   valor=4.6 | v_max_hdpe etiqueta=C valor=4.6
h_relleno_min_concreto_tmc etiqueta=N-> valor=0.3
$ sed -n '40,43p' src/modulos/M2_material.py
Dos de los criterios que alimentan el catalogo siguen sin valor (Tablero 1.3):
'v_max_tmc', 'v_max_hdpe' y 'h_relleno_min_concreto_tmc'.
$ sed -n '11,12p' src/modulos/M5_verificaciones.py
    V3  Velocidad maxima   concreto: rango Tabla N 10 [N]
                           TMC / HDPE: criterio pendiente   [C]
$ grep -rn "h_relleno_min_concreto_tmc' \[C\]" src/
M7_geometria.py:21 / M7_geometria.py:375
$ python3 -c "...disenar_lote(...)..." -> los 3 candidatos de A-01 paran en 'remanso_derecho_via'
```
**Verificacion:** Lente 1 reprodujo valores y docstrings en las cuatro pasadas; lente 2 encontro el cierre documentado en el manifiesto (Sec. 14.a describe el estado nuevo) y ninguna nota que declare estas citas congeladas a proposito.

### A-04 -- `cota_entrada_supuesta` rellena un vacio de dato dentro de M5
**Sev** GRAVE - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M5_verificaciones.py:56-69,305-318
El CSV no trae cota de fondo de entrada y M5 adopta `punto.cota_terreno`. Esa eleccion gobierna V4 (M5:362), V7 (M5:492) y cuatro puntos de M7 (252, 328, 465, 539) y M8. No existe ningun criterio para esto en criterios_adoptados.py (`ke_entrada` es otra cosa), no aparece en el Anexo A ni en ninguna linea de docs/, y M11 solo imprime el numero: "supuest"/"hipotesis" no aparecen en M11_reporte.py ni en cli.py.
**Regla:** Claude.md: "Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes. Crea una entrada en criterios_adoptados.py con valor=None, etiqueta [A] ... Rellenar un vacio en silencio es el peor error posible en este proyecto." El propio docstring manda "declarala en la memoria como tal" y la memoria no la declara.
**Evidencia:**
```
$ grep -n "def cota_entrada_supuesta" -A3 src/modulos/M5_verificaciones.py
305:def cota_entrada_supuesta(punto: PuntoCritico) -> float:
307:    Cota del fondo de la entrada, msnm. Es la INTERPRETACION declarada en el
$ python3 -c "[k for k in ca.CRITERIOS if 'entrada' in k or 'cota' in k.lower()]"
['ke_entrada']
$ grep -rn "cota_entrada_supuesta|cota de invert|fondo de la entrada|cota de entrada" docs/ Claude.md
(sin resultados)
$ grep -rn "supuest|hipotesis" src/modulos/M11_reporte.py cli.py
(sin resultados; M11:800 y cli.py:1244 imprimen solo el numero)
```
**Verificacion:** Lente 1 reprodujo exacto y trazo los consumidores; lente 2 hallo documentacion extensa pero solo en docstrings (M5:56-71, M7:120-129, M8:94), nada en criterios_adoptados.py, Anexo A, docs/ ni memoria.

### A-05 -- `cli._bloqueo` y `M11.criterios_bloqueantes` resuelven toda clave contra `ca.criterio()`
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** cli.py:485; src/modulos/M11_reporte.py:557; src/datos_sitio.py:234
`datos_sitio.valor()` lanza `CriterioPendienteError` igual que un criterio, pero `_bloqueo` busca la clave en `CRITERIOS` y un `[S]` de corredor daria KeyError: un problema del expediente saldria como fallo de programa. Los tres datos de corredor tienen valor hoy (PGA_roca_B=0.5, ZONA_SISMICA_LA_UNION=4, Z_E030=0.45), de modo que la rama es inalcanzable sin parchear `DATOS_SITIO`.
**Regla:** Claude.md, Excepciones: "Todas descienden de ErrorProyecto ... para que la GUI distinga un problema del expediente de un fallo del programa con un solo except". Ningun docstring declara que cli.py solo soporte `CriterioPendienteError` de criterios_adoptados.
**Evidencia:**
```
$ python3 -c "...replace(ds.DATOS_SITIO['PGA_roca_B'], valor=None); cli._etapa(...)" 2>&1 | tail -6
  File ".../cli.py", line 485, in _bloqueo
    declarado = ca.criterio(exc.clave)
  File ".../src/criterios_adoptados.py", line 242, in criterio
KeyError: 'PGA_roca_B'
$ python3 -c "[print(k, repr(v.valor)) for k,v in ds.DATOS_SITIO.items()]"
PGA_roca_B 0.5 | ZONA_SISMICA_LA_UNION 4 | Z_E030 0.45
```
**Verificacion:** Lente 1 reprodujo el KeyError exacto y comprobo que hay que mutar el estado del repo para alcanzarlo; lente 2 no hallo ninguna linea que declare la limitacion (GRAVE -> MENOR por guardia sobre un caso hoy inexistente).

### A-06 -- `Material.v_max_rango` transporta un escalar y `v_max_definida` afirma lo contrario de lo que devuelve
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Detectado desde 3 dimensiones** (A1, C2, F2) - **Ubicacion** src/modelos.py:451,466-468; src/modulos/M2_material.py:280-282
El campo anotado `Optional[Tuple[float, float]]` recibe el float 4.6 para TMC y HDPE; concreto lleva (3.0, 6.0). El escalar es deliberado y esta documentado en M5:259-266 ("Son un techo escalar, de modo que esta rama no cambia") y fijado por tests, pero no en modelos.py, donde se consulta el contrato. Ademas `v_max_definida` se documenta como "False para TMC y HDPE mientras el Tablero 1.3 siga abierto" y hoy devuelve True para los tres. El unico desempaquetado (M5:282) solo se alcanza para concreto: no hay TypeError posible hoy.
**Regla:** Claude.md, Arquitectura: "Los tipos que fluyen entre modulos estan en modelos.py."
**Evidencia:**
```
$ python3 -c "print(Material.__annotations__['v_max_rango']); ...catalogo(t).v_max_rango..."
anotacion: Optional[Tuple[float, float]]
concreto_reforzado (3.0, 6.0) tuple True | tmc 4.6 float True | hdpe 4.6 float True
$ sed -n '464,468p' src/modelos.py
    def v_max_definida(self) -> bool:
        """False para TMC y HDPE mientras el Tablero 1.3 siga abierto."""
$ sed -n '269,282p' src/modulos/M5_verificaciones.py
    if material.tipo in CRITERIO_V_MAX:   # TMC y HDPE salen aqui
    _, v_max = material.v_max_rango       # solo concreto llega
```
**Verificacion:** Lente 1 reprodujo anotacion y valores en las tres pasadas; lente 2 encontro la decision escrita en M5 y el docstring de modelos.py que la contradice.
**Nota de reconciliacion:** el verificador de C2 puso GRAVE por el docstring contrario al codigo; los de A1 y F2 pusieron MENOR, y F2 mostro que la frase de `v_max_definida` es condicional ("mientras el Tablero 1.3 siga abierto"), o sea obsoleta y no falsa. Va MENOR.

### A-07 -- M11 declara "sin calcular nada nuevo" y calcula y/D en dos sitios
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M11_reporte.py:5,903,953
El barrido AST confirma que las unicas operaciones aritmeticas sobre magnitudes en M11 son `h.y_normal / resultado.D` en 903 y 953 (las otras dos BinOp son `Path / str`). No hay comentario, nombre ni excepcion declarada: es inconsistencia entre el docstring de modulo y dos divisiones inline. El numero impreso es identico al de V1 (M5:162) y a `modelos.Geometria.y_sobre_D`.
**Regla:** docstring del propio M11 ("sin calcular nada nuevo") y Claude.md, Arquitectura: "Los tipos que fluyen entre modulos estan en modelos.py."
**Evidencia:**
```
$ sed -n '4,5p' src/modulos/M11_reporte.py
Fase 11 - Memoria de calculo. Convierte el `Informe` ... sin calcular nada nuevo.
$ python3 (barrido AST de BinOp sobre M11_reporte.py)
1318 DIR_PLANTILLAS / NOMBRE_PLANTILLA | 1477 Path(...) / respaldo.name
903 h.y_normal / resultado.D | 953 h.y_normal / resultado.D
$ grep -n "y_sobre_D = resultado.y_normal / D" src/modulos/M5_verificaciones.py
162:    y_sobre_D = resultado.y_normal / D
```
**Verificacion:** Lente 1 rehizo el barrido AST; lente 2 leyo el docstring completo (1-60) buscando una excepcion declarada para y/D y no existe, de ahi la reclasificacion a defecto real.

### A-08 -- El docstring de MD sostiene que M5 no existe en el repositorio
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/MD.py:56-71
La seccion "Interfaz con M5 -- supuesto de arquitectura" abre con "M5 todavia no existe en el repositorio". El archivo existe (28 551 bytes), MD lo importa por `import_module` en `_verificador_de_M5` y toda la suite lo ejercita. La justificacion del Protocol y de la importacion perezosa queda apoyada en un hecho falso.
**Regla:** el docstring de modulo es el contrato de responsabilidad del proyecto; un contrato que afirma la ausencia de un modulo presente no sirve para auditar el grafo de dependencias.
**Evidencia:**
```
$ sed -n '56,60p' src/modulos/MD.py
Interfaz con M5 -- supuesto de arquitectura, no valor de proyecto
M5 todavia no existe en el repositorio. MD no puede orquestar sin llamarlo, de
modo que fija la unica pieza que un orquestador esta obligado a fijar: la FIRMA.
$ ls -l src/modulos/M5_verificaciones.py
-rw-r--r-- 1 root root 28551 Aug 26 05:05 src/modulos/M5_verificaciones.py
```
**Verificacion:** Lente 1 exacta; lente 2 no hallo ninguna nota que matice la frase (el resto del parrafo sigue siendo coherente).

### A-09 -- El diagnostico de Familia C que MD escribio es inalcanzable desde el CSV
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/MD.py:405-411,492-500
`disenar_punto` exige Q y S antes de pedir candidatos, asi que una fila C leida del CSV muere en `DatoFaltanteError('Q_m3s')` y la rama Familia C de `_motivo_sin_candidatos` nunca se ejecuta. El diagnostico que si sale es verdadero (el Tablero 3.1 declara la Familia C completa como dato externo pendiente), solo menos fundamental que "esa familia no es de conducto circular". Ningun punto se acepta ni se rechaza mal por esto.
**Regla:** Claude.md, taxonomia de excepciones: "si el revisor tiene que anadir algo es Faltante, si tiene que corregir algo es Invalido". Contradice ademas el docstring de MD ("DisenoNoFactibleError ... o M2 no ofrece candidatos (Familia C, Sec. 2.3)").
**Evidencia:**
```
$ python3 -c "...disenar_punto(C-01) y disenar_punto(replace(C-01,Q_m3s=1.0,S_cauce=0.005))"
C-01 tal cual: DatoFaltanteError: Falta el dato 'Q_m3s' en el punto C-01
C-01 con Q=1.0: DisenoNoFactibleError: ... M2 (Sec. 3.4) no ofrece material candidato
                para la Familia C: Sec. 2.3 le asigna seccion de marco o multicelda...
$ sed -n '405,408p' src/modulos/MD.py
    Q = punto.exigir("Q_m3s") if Q is None else Q
    candidatos = materiales_candidatos(punto)
```
**Verificacion:** Lente 1 identica; lente 2 hallo MD:360-364 y hoja de ruta:698, que hacen del mensaje actual un diagnostico cierto (GRAVE -> MENOR).

### A-10 -- El docstring de gui/app.py lista tres pestanas; la aplicacion tiene cuatro
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:14-22,216-219,697-701
El docstring enumera tres pestanas y `nb.add` se llama cuatro veces; la omitida es "2. Criterios", la que reescribe criterios_adoptados.py y declara valores en caliente. La lista de exportaciones tambien esta incompleta: dice (JSON/HTML/PDF) y la pestana 4 monta ademas `btn_csv`, el CSV que Claude.md:118 exige entre los componentes reutilizados.
**Regla:** Claude.md, Estilo: el docstring declarado debe describir el comportamiento real. Ningun documento menciona la pestana de Criterios.
**Evidencia:**
```
$ sed -n '14,22p' gui/app.py
    1. Datos de entrada / 2. Resultados por punto / 3. Resumen ... (JSON/HTML/PDF)
$ grep -n "nb.add" gui/app.py
216: "  1. Datos de entrada  " | 217: "  2. Criterios  "
218: "  3. Resultados por punto  " | 219: "  4. Resumen  "
$ grep -n "btn_csv" gui/app.py
697: text="Exportar cuadro resumen (CSV)"
```
**Verificacion:** Lente 1 reprodujo literalmente; lente 2 no hallo mencion de la pestana de Criterios en docs/ (severidad subida de OBSERVACION a MENOR por el docstring falso sobre la funcionalidad de mayor riesgo).

### A-11 -- La leyenda de etiquetas de la GUI contradice la taxonomia de cinco
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:321-323
La leyenda anuncia `[N]`, categoria imposible en criterios_adoptados.py (hay test guardian que lo impide), y omite `[S]`, que si esta presente (`PERFIL_SUELO_PRESUNTO`). Es texto de una pestana, sin efecto sobre el calculo ni sobre la memoria (M11 imprime con `_etiqueta_html`).
**Regla:** Claude.md, "Taxonomia de etiquetas (cinco, no cuatro)": [N], [N->], [S], [C], [A].
**Evidencia:**
```
$ sed -n '321,323p' gui/app.py
    text="Etiquetas: [N] normativo  [N->] normativo por analogia  "
         "[C] fuente tecnica reconocida  [A] adopcion sin norma unica. "
$ python3 -c "Counter(c.etiqueta for c in ca.CRITERIOS.values())"
Counter({'A': 30, 'C': 13, 'N->': 2, 'S': 1})
$ sed -n '185,188p' tests/test_criterios_adoptados.py
def test_ningun_criterio_adoptado_lleva_ya_la_etiqueta_N():
```
**Verificacion:** Lente 1 reprodujo el Counter exacto; lente 2 no hallo ningun documento que declare que la GUI conserva el vocabulario anterior (GRAVE -> MENOR: cadena de UI).

### A-12 -- gui/app.py declara reutilizar el "campo validable" de legacy y no lo implementa
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:5-7,202-204,277-285
El docstring afirma reutilizar "MarcoScroll, Tooltip y campo validable"; `_campo_validable` no existe en la GUI y `color_borde_ok` queda como codigo muerto (dos asignaciones, ningun uso). Los campos se construyen con `ttk.Entry` desnudo. El usuario si sabe que campo esta mal (el mensaje de `cli.cargar_datos_externos` nombra el campo): lo que falta es la marca por campo.
**Regla:** Claude.md, GUI: "Reutilizar el patron de legacy/Tc.py: ... campo validable ... No reinventar los componentes." Es el unico de la lista que falta y el docstring afirma que esta.
**Evidencia:**
```
$ grep -n "_campo_validable\|color_borde_ok" gui/app.py legacy/Tc.py
gui/app.py:202, gui/app.py:204            (dos asignaciones, ningun uso)
legacy/Tc.py:332,340,358,361,447,563      (definicion y uso reales)
$ sed -n '277,283p' gui/app.py
            ent = ttk.Entry(f_ext, textvariable=..., ...)
```
**Verificacion:** Lente 1 reprodujo el grep; lente 2 confirmo Claude.md:116-119 y el docstring que afirma la reutilizacion (GRAVE -> MENOR: carencia de UI sin efecto en ningun numero).

### A-13 -- V2b (sedimentacion / colmatacion) no existe en ninguna linea del codigo
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M5_verificaciones.py:4-5; cli.py:573-577; docs/hoja_de_ruta_alcantarillas_v8.md:454
El identificador no existe en src/, cli.py, gui/ ni tests/, y no hay criterio ni mencion de "colmatacion"/"mantenimiento" en criterios_adoptados.py. El contenido de V2b es "acceso de mantenimiento en planos", entregable 7 de Sec. 11 que este software no produce, y el repo tiene una formula documental para ese caso (M8:306). Falta aplicarla: el alcance reducido a nueve verificaciones no esta escrito en ningun docstring ni en docs/.
**Regla:** Hoja de ruta Fase 5, fila V2b ([N] + [A]). Claude.md: la parte [A] ni siquiera se declaro como vacio.
**Evidencia:**
```
$ grep -n "V2b" docs/hoja_de_ruta_alcantarillas_v8.md
454:| **V2b** | Sedimentación / colmatación | ... | [N] + [A] |
$ grep -rn "V2b" src/ cli.py gui/ tests/ --include=*.py
(sin resultados)
$ grep -rn "mantenimiento" src/criterios_adoptados.py
(sin resultados)
$ sed -n '306p' src/modulos/M8_estructural.py
    memoria y los planos (Sec. 11, entregable 7): no compara contra ningun
```
**Verificacion:** Lente 1 exacta; lente 2 no hallo documentacion de la exclusion, y reclasifico de defecto real a deliberado sin documentar por tratarse de contenido de planos.

### A-14 -- El docstring de `escribir_valor_en_archivo` dice "valor=None" y la regex reescribe cualquier valor
**Sev** MENOR - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:279-285,302-306; gui/app.py:489,542-551
La regex `([^,\n]*)` sobrescribe un valor ya declarado y deja `fuente` intacta, con lo que el manifiesto queda desalineado. Dos de los tres reproches ya estan documentados: no tocar etiqueta/justificacion/fuente esta en el propio docstring, y la GUI abre antes un messagebox que describe la conducta real y advierte exactamente de ese riesgo. Queda inexacta la primera frase del docstring y el boton habilitado sin condicion.
**Regla:** Claude.md, Fuente de verdad, y docs/manifiesto_citas.md (cada fila es "un volcado literal de lo que el codigo YA afirma").
**Evidencia:**
```
$ cp src/criterios_adoptados.py $D/copia.py; python3 -c "...escribir_valor_en_archivo('ke_entrada',0.9,ruta=copia)"
antes  : valor = 0.5 | etiqueta C | fuente = HDS-5 (FHWA) 3a ed., ... Tabla C.2
despues: valor = 0.9 | fuente = HDS-5 (FHWA) 3a ed., ... Tabla C.2   (intacta)
$ git status --porcelain   -> (vacio: el repo no se toco)
$ sed -n '542,551p' gui/app.py
    messagebox.askyesno("Confirmar escritura permanente", ... "Es un cambio
    PERMANENTE al archivo fuente ... revisalas a mano si corresponde", icon="warning")
```
**Verificacion:** Lente 1 reprodujo la sobrescritura sobre copia; lente 2 hallo docstring y dialogo que documentan la decision (GRAVE -> MENOR, y reclasificado a deliberado documentado).

### A-15 -- Claude.md y el test guardian siguen diciendo "hoy solo la gravedad"
**Sev** MENOR - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** Claude.md:55-56; tests/test_sin_literales.py:16-17; src/constantes_fisicas.py:50-59
constantes_fisicas.py declara cinco nombres (G, RHO_AGUA, N_POR_KN, GAMMA_AGUA, GAMMA_AGUA_KN_M3). El argumento de fondo del auditor no distingue a `GAMMA_AGUA_KN_M3` de la gravedad: G tambien entra en el calculo (M4:241, 284, 432) y el manifiesto declara que su correccion "si cambia un valor calculado". Queda un unico defecto: la enumeracion vencida en la constitucion y en el docstring del test.
**Regla:** Claude.md, Arquitectura: "si cambiarlo puede alterar un resultado del calculo, no va ahi" mas la enumeracion "hoy solo la gravedad". La decision esta documentada en constantes_fisicas.py:33-47 y manifiesto_citas.md:19-27.
**Evidencia:**
```
$ sed -n '55,56p' Claude.md
  constantes_fisicas.py (constantes físicas universales -- hoy solo la
  gravedad, G = 9.81 m/s² -- ...
$ grep -n "^[A-Z_0-9]* =" src/constantes_fisicas.py
50:G | 52:RHO_AGUA | 56:N_POR_KN | 58:GAMMA_AGUA | 59:GAMMA_AGUA_KN_M3
$ grep -rn "GAMMA_AGUA_KN_M3" src/modulos/*.py | grep -v import
M8_estructural.py:209 | M9_cabezal.py:683 | M9_cabezal.py:699
```
**Nota de evidencia:** el auditor pego "src/modulos/M9_cabezal.py:209" como uso; esa linea no existe como tal (los usos reales en M9 son 683 y 699). Va la salida del verificador.
**Verificacion:** Lente 1 reprodujo la enumeracion y corrigio la linea mal pegada; lente 2 hallo la decision documentada en dos sitios.

### A-16 -- Dos validaciones cruzadas de M0 no salen de la tabla de Sec. 1.5
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M0_carga.py:364-381,4-6
Los dos chequeos (altura libre terreno-subrasante positiva; fondo del receptor bajo el terreno del cruce) no aparecen en la hoja de ruta. No son "criterios de factibilidad inventados": son comprobaciones de imposibilidad fisica entre dos datos de la misma fila, el tercer supuesto que Claude.md autoriza para `DatoInvalidoError`, y la frontera con la factibilidad esta fijada por test. Falta la declaracion escrita de ambas reglas fuera de los comentarios de linea.
**Regla:** Claude.md: "Si la hoja de ruta NO dice nada sobre algo que necesitas: NO lo inventes", y el docstring de M0 que atribuye las validaciones cruzadas a la tabla de Sec. 1.5.
**Evidencia:**
```
$ sed -n '364,375p' src/modulos/M0_carga.py
    # Diametro implicito: la altura libre entre el terreno natural y la subrasante...
    _exige(altura > TOL_UMBRAL_NORMATIVO, ...)
    # La alcantarilla entrega por gravedad: el fondo del receptor esta bajo el terreno...
$ grep -cn "entrega es por gravedad|diametro implicito" docs/hoja_de_ruta_alcantarillas_v8.md
0
$ sed -n '353,367p' tests/test_M0_carga.py
def test_un_terraplen_bajo_pero_posible_lo_decide_M7_y_no_M0  ("M0 solo rechaza lo imposible")
```
**Verificacion:** Lente 1 reprodujo sed y grep; lente 2 leyo la Sec. 1.5 completa (hoja de ruta:214-232) y Claude.md:97-103, que autoriza la contradiccion entre datos de la misma fila sin exigir que el par este tabulado.

### A-17 -- La GUI no expone `--alcance`
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:748; cli.py:886-887,1379-1396
"alcance" no aparece en gui/app.py; la llamada es `cli.correr(ruta_csv, externos)` y `correr` toma `ALCANCE_EXPEDIENTE` por defecto. `memoria_perfil.html` solo se alcanza por `plantilla_por_alcance`, usada unicamente en cli.py:1482. La GUI corre el SUPERCONJUNTO, de modo que ninguna memoria suya afirma algo falso: es carencia de funcionalidad, no regla incumplida.
**Regla:** el docstring de gui/app.py:9-12 promete llamar a las mismas funciones que cli.py (y lo cumple); Claude.md:115-119 no exige paridad de banderas.
**Evidencia:**
```
$ grep -n "alcance" gui/app.py   -> (sin resultados)
$ grep -n "cli.correr(" gui/app.py
748:            self.informe = cli.correr(ruta_csv, externos)
$ grep -n "plantilla_por_alcance" cli.py gui/app.py
cli.py:1379 (def) | cli.py:1482 (unico uso)
```
**Verificacion:** Lente 1 reprodujo todo; lente 2 leyo la seccion GUI de Claude.md y el docstring de `plantilla_por_alcance` ("El alcance elige el DEFECTO, no una obligacion"), que desarma la regla citada (GRAVE -> OBSERVACION).

### A-18 -- La sesion JSON de la GUI no guarda los criterios declarados "solo para esta corrida"
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:905-912,928-947,429/438/482
`guardar_sesion` no serializa `valores_dinamicos` y `cargar_sesion` no los restaura. La no-persistencia es coherente con la semantica declarada ("Declara, SOLO PARA ESTA CORRIDA...", criterios_adoptados.py:146) y con el mensaje de la propia GUI; al reabrir, los criterios vuelven a bloquear con su Bloqueo registrado, sin rellenar nada en silencio. Falta la linea que lo diga en el docstring de `guardar_sesion`.
**Regla:** Claude.md, GUI: "sesion en JSON" como parte del patron de legacy/Tc.py.
**Evidencia:**
```
$ sed -n '905,912p' gui/app.py
    def guardar_sesion(self):
        data = {"formato_version": ..., "proyecto": ..., "csv": ..., "externos": {...}}
$ grep -n "valores_dinamicos" gui/app.py
429 / 438 / 482        (ninguna en guardar_sesion ni en cargar_sesion)
```
**Nota de evidencia:** el auditor declaro las lineas 429/430/482; las reales son 429/438/482.
**Verificacion:** Lente 1 reprodujo y corrigio el numero de linea; lente 2 hallo la semantica documentada que hace defendible la ausencia (MENOR -> OBSERVACION).

### A-19 -- M2 lee `HDS5_INLET` y `H_RELLENO_MIN` del archivo que lo prohibe
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/constantes_normativas.py:12-24; src/modulos/M2_material.py:273,276
Las lecturas existen y la frase de CN:24 es categorica, pero el propio bloque de la ADVERTENCIA acota el homologo linea por linea ("HDS5_INLET <-> criterio 'hds5_embocadura_hdpe' (HDPE)") y el homologo de H_RELLENO_MIN se llama `h_relleno_min_concreto_tmc`, que por su nombre excluye la fila hdpe. La excepcion por-clave esta documentada en M2:26-38, marcada con comentarios de linea y recogida en el manifiesto. Falta cerrar la frase blanket de CN:24.
**Regla:** src/constantes_normativas.py:24 (regla de fuente unica derivada de Sec. 0.7).
**Evidencia:**
```
$ sed -n '12,24p' src/constantes_normativas.py
ADVERTENCIA DE DOBLE DEFINICION
    HDS5_INLET     <->  criterio "hds5_embocadura_hdpe" (HDPE)
    H_RELLENO_MIN  <->  criterio "h_relleno_min_concreto_tmc"
... Ningun modulo debe leer los tres bloques citados desde este archivo.
$ grep -n "HDS5_INLET\|H_RELLENO_MIN" src/modulos/M2_material.py
273:  h_relleno_min = H_RELLENO_MIN["hdpe"]   # [N] directo: sin vacio, sin homologo
276:  hds5 = ConstantesHDS5.desde_dict(HDS5_INLET[_HDS5_CLAVE[tipo]])
```
**Verificacion:** Lente 1 reprodujo sed y grep; lente 2 leyo el bloque completo (no la frase suelta) y el manifiesto_citas.md:567-569 (MENOR -> OBSERVACION, deliberado documentado).

### A-20 -- El comentario de la discrepancia 19.63/19.62 cita lineas que ya no corresponden
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (A2, C2) - **Ubicacion** src/constantes_normativas.py:124-126; src/modulos/M4_control.py:107-126
El comentario remite a las lineas 432, 436, 790 y 901 de la hoja de ruta; las ocurrencias reales de 19.62 son 436, 440, 797 y 908 (el auditor de C2 ademas omitio la 440, la "Nota de unidades"). Las citas estan corridas unas pocas lineas tras editar el documento, no inventadas. La decision de fondo (gana HDS-5 con 19.63) esta documentada en tres sitios y tiene test guardian.
**Regla:** Claude.md, Fuente de verdad: "Toda cita de numeral se verifica contra ese archivo" -- aplicada aqui a renglones de la hoja de ruta, no a numerales normativos.
**Evidencia:**
```
$ sed -n '124,126p' src/constantes_normativas.py
# ... (lineas 432, 436, 790 y 901) sigue escribiendo 19.62. Aqui gana la fuente
# primaria HDS-5 por verificacion externa; la hoja de ruta debe corregirse.
$ grep -n "19\.62" docs/hoja_de_ruta_alcantarillas_v8.md
436 / 440 / 797 / 908
$ sed -n '432p;901p;790p' docs/hoja_de_ruta_alcantarillas_v8.md
### 4.3 Control de salida [C] | ### Notas críticas de programación | "circular_cmp_mitered"...
$ sed -n '409,412p' docs/auditoria_y_ruta_despliegue_v9.md
**Corrección a mí mismo: `K_FRICCION_SI` debería ser 19.63** ... "KU = 29 in English Units (19.63 in SI)"
```
**Verificacion:** Lente 1 reprodujo el desfase y verifico que 432 y 901 son encabezados de seccion; lente 2 hallo la decision documentada en M4:123-126, en el manifiesto y en la auditoria v9 (MENOR -> OBSERVACION).

### A-21 -- `cli._fase_8` repite la resta "subrasante menos clave" sin la guarda de V7
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** cli.py:736-745; src/modulos/M5_verificaciones.py:492-500; src/modulos/M8_estructural.py:187-190
No hay tercera copia de la formula: cli.py importa `cota_clave` de M7 (cli.py:113) y solo repite la resta, con un comentario que la ata a V7. El riesgo de que una altura nula entre en `seleccionar_clase_calibre` es nulo: esa funcion invoca `ca.valor(CRITERIO_CLASES_PRODUCTO)` y se detiene antes de mirar la altura. Queda que la resta de cli.py no lleva la guarda `DatoInvalidoError` de V7.
**Regla:** Claude.md, Arquitectura: los modulos definen las reglas de calculo; cli.py se documenta como orquestador.
**Evidencia:**
```
$ sed -n '736,741p' cli.py
    # Altura real de relleno sobre la clave, la misma definicion que usa V7:
    # subrasante menos clave, no el minimo normativo de 7.A.
                    lambda: punto.cota_subrasante - cota_clave(punto=punto, D=D))
$ sed -n '186,190p' src/modulos/M8_estructural.py
    ca.valor(CRITERIO_CLASES_PRODUCTO)    # CriterioPendienteError mientras falte
    raise AssertionError("inalcanzable mientras 'clases_producto_por_relleno' este vacio")
$ grep -n "^from" src/modulos/M7_geometria.py | grep M5   -> 201 (ciclo M7->M5 confirmado)
```
**Verificacion:** Lente 1 reprodujo cli.py y M5 y verifico el import de `cota_clave` y el stub de M8; lente 2 hallo la decision escrita en el comentario de cli.py y en el docstring de M8 (MENOR -> OBSERVACION).

### B-01 -- `clase_sitio` es inerte: la memoria nunca declara la adopcion que la hoja de ruta obliga a escribir
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO/CONFIRMADO - **Detectado desde 2 dimensiones** (B1, D1) - **Ubicacion** src/criterios_adoptados.py:373-375,386,1988; src/modulos/M11_reporte.py:1032,1389; cli.py:1133
Ningun modulo de produccion invoca `clase_sitio`: la unica llamada `valor("clase_sitio")` esta dentro del bloque `if __name__ == "__main__"`. Como tiene valor no entra en `criterios_sin_valor()` y como nadie lo invoca no entra en `criterios_usados()`, de modo que no cae en ninguna de las tres puertas de M11 y da 0 coincidencias en la memoria de perfil y en la de expediente. Ademas dos textos afirman lo contrario: la trazabilidad de `PERFIL_SUELO_PRESUNTO` dice que "la clase de sitio que si entra en el calculo es la de AASHTO, criterio clase_sitio", y `tests/test_criterios_adoptados.py:604-609` declara que M11 lo imprime en la seccion sismica.
**Regla:** docs/hoja_de_ruta_alcantarillas_v8.md:111: "Etiqueta [A], declarada en criterios_adoptados.py como clase_sitio = \"F_con_factores_tabulados_por_adopcion\". **La memoria de calculo debe decirlo con esas palabras**." Y Claude.md, Arquitectura: "Cada invocacion de un criterio ... se registra, para que M11 imprima solo los usados".
**Evidencia:**
```
$ grep -rn "clase_sitio" src/modulos/ cli.py gui/app.py src/plantillas/
(sin salida; grep exit=1)
$ grep -rn 'valor("clase_sitio")' src/
src/criterios_adoptados.py:1988:    valor("clase_sitio")     # dentro de if __name__ == "__main__"
$ python3 cli.py tests/ejemplo_puntos.csv --html mem.html --alcance perfil >/dev/null 2>&1
$ grep -c "clase_sitio\|F_con_factores_tabulados_por_adopcion" mem.html mem_exp.html
0 / 0
$ python3 -c "from modulos.M9_cabezal import cadena_sismica; ..."
criterios usados tras la cadena sismica: ['F_pga', 'factor_muro_eleccion', 'k_v']
```
**Verificacion:** Lente 1 reprodujo grep, corrida y memoria en las dos dimensiones; lente 2 hallo que docs/ ordena lo contrario (hoja de ruta:111) y que ninguna nota declara el criterio como referencia muerta aceptada.

### B-02 -- `ControlEntrada.HW_sobre_D` se calcula, se guarda y no lo lee nadie
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modelos.py:562-568; src/modulos/M4_control.py:392
En produccion el campo solo aparece dentro de M4 (lineas 362, 364, 388 para calcularlo y 391-392 para guardarlo); los unicos lectores externos son los tests. El campo hermano `HW` si viaja al entregable (cli.py:998, M11:717/904/953), lo que descarta que la omision sea politica de la clase. Complementa A-02: el docstring dice que el campo existe para lo que compara V4b, comparacion que no existe.
**Regla:** src/modelos.py:564: "`HW_sobre_D` ... es tambien lo que compara V4b (HW/D <= 1.5)". V4b no existe en el codigo.
**Evidencia:**
```
$ grep -rn "\.HW_sobre_D" src/ cli.py gui/app.py src/plantillas/
(vacio: nadie lo lee en produccion)
$ grep -rn "\.HW_sobre_D" tests/ --include=*.py | head -2
tests/test_M4_control.py:215 / :226
$ grep -n "HW_gobernante_m" cli.py
998: "HW_gobernante_m": _num(hidraulica.HW)     # HW si sale; HW_sobre_D no
```
**Verificacion:** Lente 1 reprodujo el grep y trazo los cinco sitios internos de M4; lente 2 no hallo ninguna nota que declare pendiente la comparacion, solo las dos afirmaciones contrarias.

### B-03 -- La lista de dependencias de Claude.md esta desactualizada
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** Claude.md:109-110; requirements.txt; src/plantillas/*.html
Claude.md lista pandas y jinja2: cero apariciones en todo el arbol .py/.html y ninguna en requirements.txt. Las dos plantillas no tienen un solo delimitador Jinja (el motor es `string.Template` con "%%"). `weasyprint==69.0` esta pineado y no figura en Claude.md ni en docs/. El motor real si esta documentado (M11:40, M11:174, Claude.md:118): lo que envejecio es la lista.
**Regla:** Claude.md:109-110 "Dependencias: numpy, scipy (brentq), pandas, pytest, ttkbootstrap, jinja2. Cualquier dependencia adicional se consulta antes."
**Evidencia:**
```
$ cat requirements.txt
numpy==2.2.3 / scipy==1.15.2 / pytest==9.1.1 / ttkbootstrap==2.2.1 / weasyprint==69.0
$ grep -rn "jinja\|pandas" --include=*.py --include=*.html . | grep -v '^./.git' | wc -l
0
$ grep -c '{{\|{%' src/plantillas/memoria_alcantarillas.html src/plantillas/memoria_perfil.html
0 / 0
$ grep -n "weasyprint" Claude.md docs/*.md   -> (sin resultados)
```
**Verificacion:** Lente 1 reprodujo el comando entero; lente 2 confirmo que el cambio de motor si esta documentado en el codigo, de ahi GRAVE -> MENOR.

### B-04 -- El procedimiento de Sec. 1.3 ("TW se calcula, no se mide") no esta implementado
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:375-376; src/modulos/M0_carga.py:72,316-317,386-389; cli.py:545-553
Ningun modulo lee `punto.Q_receptor_m3s` ni `punto.cota_TW`; su unico destino es la tabla de la memoria via getattr. Con un CSV que trae ambos llenos, la corrida pasa la validacion cruzada y aun asi se detiene en `CriterioPendienteError('TW_receptor')`. Lo no implementado es el procedimiento completo de tres pasos de la hoja de ruta, no una conversion, y no esta declarado como diferido. El bloqueo es ruidoso, nunca un relleno silencioso.
**Regla:** El docstring de M0 explica que las columnas pueden venir vacias por el Tablero 3.1, no que, viniendo llenas, ningun modulo las lea. La consecuencia (un expediente con `cota_TW` sigue necesitando `--tw`) no esta escrita.
**Evidencia:**
```
$ grep -rn "\.Q_receptor_m3s\|\.cota_TW" src/ cli.py gui/app.py --include=*.py
(vacio: nadie lee los atributos)
$ sed 's/,,,SM,/,2.0,42.0,SM,/' tests/ejemplo_puntos.csv > tw.csv
$ python3 cli.py tw.csv --luz 3 | grep -i 'tirante en el receptor'
  [CriterioPendienteError] Fases 3-5 -> tirante en el receptor (TW)
      falta declarar: TW_receptor [A]
$ sed -n '192,196p' docs/hoja_de_ruta_alcantarillas_v8.md
### 1.3 TW: se calcula, no se mide  (tres pasos, ninguno existe en src/)
```
**Verificacion:** Lente 1 reprodujo el grep y construyo el CSV que demuestra la consecuencia; lente 2 no hallo ninguna nota de diferimiento (GRAVE -> MENOR: sin consecuencia de calculo, el codigo se detiene con excepcion).

### B-05 -- Entregable 5 (analisis de sensibilidad): su unica API la consumen solo los tests
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Ubicacion** src/criterios_adoptados.py:1963; src/plantillas/memoria_alcantarillas.html:259; docs/hoja_de_ruta_alcantarillas_v8.md:660
`parametros_sensibilizables()` no la invoca cli.py, gui/app.py ni M11, y no existe bloque de alcance que declare diferido el entregable 5, mientras la plantilla imprime "con analisis de sensibilidad obligatorio". La memoria si imprime el rango declarado de cada criterio (M11:1053-1055), de modo que el insumo llega al documento aunque el barrido no se ejecute. Hay ademas discrepancia de numeracion: la hoja de ruta llama 5 al analisis y 6 a HY-8, y la auditoria v9:834 llama 5 a HY-8.
**Regla:** docs/hoja_de_ruta_alcantarillas_v8.md:660 (Fase 11, entregable 5) y Claude.md:28 ("[A] ... Adopcion declarada + sensibilidad").
**Evidencia:**
```
$ grep -rn "parametros_sensibilizables" --include=*.py .
./src/criterios_adoptados.py:1963 (def) | ./tests/test_criterios_adoptados.py:22,296,423,424
(ningun hit en cli.py, gui/app.py ni src/modulos/)
$ sed -n '660,661p' docs/hoja_de_ruta_alcantarillas_v8.md
5. **Análisis de sensibilidad** alimentado por los rangos de `criterios_adoptados.py`
6. **Validación externa:** correr 1–2 puntos en HY-8 ...
$ grep -rn "entregable 5" docs/
docs/auditoria_y_ruta_despliegue_v9.md:834: ... Es el entregable 5 de la Fase 11 (HY-8)
```
**Verificacion:** Lente 1 reprodujo los cuatro comandos; lente 2 busco un bloque de acotacion (`acotaciones_declaradas`, `bloque_alcance`, `NOTA_*`) y no existe (GRAVE -> MENOR).

### B-06 -- `--plantilla memoria_perfil.html` sobre corrida de expediente pierde 13 KB de pendientes
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Ubicacion** cli.py:1379-1396,1439-1443; src/modulos/M11_reporte.py:179-182
`memoria_perfil.html` es el unico consumidor que no imprime `bloque_pendientes`, y `substitute` no falla por valores sobrantes. La omision esta documentada PARA la corrida de perfil, en la plantilla y en un test. La direccion cruzada -- que la propia CLI invita a usar, porque el docstring afirma que las dos plantillas "comparten el contrato de marcadores" y el help remata con "Las dos aceptan cualquier corrida" -- descarta 13 647 caracteres que incluyen los criterios bloqueantes del expediente.
**Regla:** comentario de contrato de M11_reporte.py:179-182: "un marcador que M11 calcula y la plantilla no imprime es contenido de la memoria que se pierde en silencio".
**Evidencia:**
```
$ python3 -c "...cli.correr(tests/ejemplo_puntos.csv) + memoria_html(NOMBRE_PLANTILLA_PERFIL)..."
alcance: expediente
len(bloque_pendientes): 13647
aparece en la memoria perfil: False
marcadores que la plantilla perfil no imprime: ['bloque_pendientes']
$ sed -n '1385,1390p' cli.py
    El alcance elige el DEFECTO, no una obligacion: la de perfil y la de
    expediente comparten el contrato de marcadores ...
```
**Verificacion:** Lente 1 reprodujo caracter por caracter; lente 2 confirmo que la direccion cruzada no esta documentada en ninguna parte.

### B-07 -- `CriterioPendienteError.mensaje_gui` no tiene consumidor de produccion
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:78-81; gui/app.py:647,826-832
La propiedad solo la llaman tres tests. Pero la GUI no muestra los pendientes por el `except` generico: `cli._etapa` captura cada `CriterioPendienteError` y `_bloqueo` lo traduce a un `Bloqueo` con clave, etiqueta, concepto y fuente, que la GUI pinta en una pestana dedicada -- mas informativo que "falta declarar: <clave>". La supuesta duplicacion en cli.py:1190 y :1320 es falsa: esas lineas formatean un `Bloqueo`, que no tiene esa propiedad.
**Regla:** Claude.md:91-93: "CriterioPendienteError ... La GUI la muestra como 'falta declarar: <clave>', no como error del programa." El mandato se cumple por otra via; falta la nota que lo diga.
**Evidencia:**
```
$ grep -rn "mensaje_gui" --include=*.py .
./src/modelos.py:79 (def) | tests/test_datos_sitio.py:99 | test_M1:219 | test_criterios_adoptados:114
$ sed -n '484,487p' cli.py
    if isinstance(exc, CriterioPendienteError):
        declarado = ca.criterio(exc.clave)
        datos = {"criterio": ..., "etiqueta": ..., "concepto": ..., "fuente": ...}
$ sed -n '828,832p' gui/app.py
        for c in cli.criterios_bloqueantes(informe): self.tree_criterios.insert(...)
```
**Verificacion:** Lente 1 reprodujo el grep; lente 2 encontro la via real que el auditor no busco (GRAVE -> OBSERVACION).

### B-08 -- `PeriodoRetorno.exigir_anios` no tiene llamador
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:1244-1255; src/modulos/M1_clasificacion.py:62
El docstring dice "Unico acceso permitido CUANDO EL MODULO QUE LLAMA NECESITA EL NUMERO" -- es condicional, y hoy ninguno lo necesita: los tres accesos de M11 y los dos de cli.py tratan el None explicitamente y ninguno sustituye un TR ausente. El caudal entra por columna del CSV. M1:62 esta dentro del ejemplo de uso del docstring, no en codigo ejecutado. Falta escribir que hoy ningun modulo consume el TR como numero.
**Regla:** src/modelos.py:1246-1248.
**Evidencia:**
```
$ grep -rn "exigir_anios" --include=*.py .
./src/modelos.py:1244 (def) | tests/test_M1_clasificacion.py:319, :324
$ grep -rn "\.anios\b" --include=*.py src/ cli.py gui/app.py
M11:638 (if ... is None) | M11:889, :941 (idem) | cli.py:979 (vuelca None) | cli.py:1207-1208
M1_clasificacion.py:62 (dentro del ejemplo del docstring, lineas 55-63)
$ grep -rn "exigir_anios" docs/ Claude.md; echo rc=$?   -> rc=1
```
**Verificacion:** Lente 1 reprodujo ambos greps; lente 2 leyo el docstring completo y verifico que ninguno de los cinco accesos inventa un TR (MENOR -> OBSERVACION).

### B-09 -- Siete constantes `NUMERAL_*` de modulo declaradas y nunca leidas
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** M2:127, M3:100, M4:182-183, M5:139, M8:134, MD:117
Las siete tienen un unico uso: su propia asignacion. La regla que se invoca no dice lo que el hallazgo afirmaba: Claude.md:113 exige el numeral EN EL DOCSTRING (y los docstrings lo llevan) y Claude.md:77-78 exige que cada VERIFICACION devuelva `Verificacion(...)` (M5 emite NUMERAL_V1, V2, V3, V4, V6, V7, V9). Dos de las siete son inertes por motivo documentado (V5 sin metodo declarado; Fase 8 items 1-2 bloqueados); las otras cinco son constantes muertas.
**Regla:** Claude.md:113 y :77-78; docs/manifiesto_citas.md:377-391 las lista sin declararlas inertes.
**Evidencia:**
```
$ for n in NUMERAL_MATERIAL NUMERAL_MANNING NUMERAL_ENTRADA NUMERAL_SALIDA NUMERAL_V5 NUMERAL_8_1_2 NUMERAL_BUCLE; do ... done
todos usos=1, y el unico hit es la propia asignacion
$ grep -n "NUMERAL_V" src/modulos/M5_verificaciones.py | grep numeral=
165,210,273,293,368,438,512,549  (V1,V2,V3,V3,V4,V6,V7,V9)
$ sed -n '81p' src/modulos/M8_estructural.py
clase/calibre seleccionada en los items 1-2 -- hoy bloqueados.
```
**Verificacion:** Lente 1 reprodujo el bucle; lente 2 verifico que la regla citada no se incumple (MENOR -> OBSERVACION).

### B-10 -- legacy/Tc.py: sin importadores, sin tests, sin barrido y sin estatus declarado
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Detectado desde 3 dimensiones** (B2, C1, F1) - **Ubicacion** legacy/Tc.py:1-1320,57; Claude.md:116-119,122
Nadie importa Tc.py, ningun test lo menciona, el barrido de literales no lo alcanza (185 literales prohibidos, 50 valores distintos) y sus 803 sentencias ejecutables no las cubre nada. Su cabecera anuncia matplotlib (0 en requirements.txt) y `NOMBRE_PLANTILLA` apunta a un `plantilla_memoria.html` que no existe ahi. La unica mencion en toda la documentacion es Claude.md:116, que lo enmarca como patron de GUI a leer; ninguna linea declara que legacy/ quede fuera de las reglas de literales y de tests.
**Regla:** Claude.md:47-50 (literales), Claude.md:122 ("Minimo un test por modulo") frente a Claude.md:116-119 ("Leer esos archivos antes de escribir GUI").
**Evidencia:**
```
$ grep -rn "import Tc\|from Tc\|from legacy" --include=*.py .   -> (sin resultados)
$ python3 -c "...literales_prohibidos(open('legacy/Tc.py'))..."
legacy/Tc.py: 185 literales prohibidos, 50 distintos
$ python3 -c "PythonParser(filename='legacy/Tc.py') ..."  -> 803 sentencias ejecutables
$ grep -rIl 'legacy' tests/*.py conftest.py || echo '(ninguno)'   -> (ningun test)
$ grep -rn "legacy" docs/*.md ; echo rc=$?   -> rc=1
$ grep -c matplotlib requirements.txt -> 0
```
**Verificacion:** Lente 1 reprodujo conteos y greps en las tres pasadas; lente 2 confirmo que no existe README ni linea de exencion, solo el nombre del directorio y el contexto de Claude.md.

### B-11 -- `homogeneidad_serie_fen` no bloquea por una llamada `valor()`
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:604-605; src/modulos/MD.py:537-541
No hay ninguna llamada `valor('homogeneidad_serie_fen')` en produccion y el criterio figura en `sin_valor_declarados` pero nunca en `usados` ni en `bloquearon`. El mecanismo esta escrito: el docstring de `disenar_lote` explica que el bloqueo es INDIRECTO (el hidrologo no entrega Q hasta cerrar la homogeneidad, la columna viene vacia y salta `DatoFaltanteError`), y la auditoria v9 lo registra como pendiente externo cuya salida correcta es imprimirse en el bloque de pendientes -- verificado en la memoria. Queda la debilidad: con `Q_m3s` lleno, nada obliga a declarar como se trato la poblacion mixta FEN.
**Regla:** Claude.md, Arquitectura: "criterios_adoptados.valor(clave) ... con valor None lanzan CriterioPendienteError. Nunca se sustituye por un default silencioso." No hay default silencioso aqui.
**Evidencia:**
```
$ grep -rn 'valor("homogeneidad_serie_fen")' src/ cli.py gui/app.py   -> (sin salida)
$ python3 -c "import json; d=json.load(open('o2b.json')) ..."
usados ['F_pga','factor_muro_eleccion','k_v','phi_relleno_trasdos','predimensionamiento_cabezal','recubrimiento_aashto_mm']
bloquearon ['phi_relleno_trasdos','predimensionamiento_cabezal']
sin_valor_declarados -> incluye 'homogeneidad_serie_fen'
$ grep -c "homogeneidad_serie_fen" mem_exp.html -> 1
$ sed -n '537,541p' src/modulos/MD.py
    Cuando un criterio pendiente bloquea TODOS los puntos (p.ej. Q_m3s = None
    en toda la Familia A porque 'homogeneidad_serie_fen' esta vacio) ...
```
**Verificacion:** Lente 1 reprodujo grep y JSON; lente 2 leyo entero el docstring que el auditor cito a medias y la auditoria v9:766-772 (GRAVE -> OBSERVACION).

### B-12 -- `NF_profundidad_m` sin consumidor y ausente de `CAMPOS_CSV`
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:378; src/modulos/M0_carga.py:73,86,343-345; src/modulos/M11_reporte.py:145-160
Ningun modulo de produccion lee el atributo (solo docstrings de M9 y tests) y M11.CAMPOS_CSV omite la columna. El motivo esta escrito y ademas se imprime: `NOTA_ESTABILIDAD_CABEZAL` declara que la CLI no ensambla E1-E5 y M9:85-89 dice que los ensambles que necesitan el NF se detienen hasta que el expediente cierre esos vacios. El manifiesto describe firmas, no llamadas. Sin cobertura queda solo la omision en `CAMPOS_CSV`, la unica columna de Sec. 1.2 ausente de esa tabla.
**Regla:** docs/manifiesto_datos_proyecto_vs_constantes.md, seccion "NF_profundidad_m: la columna va vacia".
**Evidencia:**
```
$ grep -rn "\.NF_profundidad_m\b\|exigir(\"NF_profundidad_m\")" src/modulos/*.py cli.py gui/app.py
src/modulos/M9_cabezal.py:669 / :774   (docstrings)
$ grep -c NF_profundidad_m <(sed -n '145,161p' src/modulos/M11_reporte.py) -> 0
$ python3 cli.py tests/ejemplo_puntos.csv --json o2b.json | grep 'nota: Las verificaciones E1-E5'
    nota: Las verificaciones E1-E5 de Sec. 9.3 no las ensambla esta CLI: ...
$ python3 -c "...d['puntos'][0]['pendientes_externos']"
['Q_receptor_m3s', 'cota_TW', 'NF_profundidad_m']
```
**Verificacion:** Lente 1 reprodujo el grep; lente 2 hallo la nota que la propia corrida imprime y el docstring de M9 (GRAVE -> OBSERVACION).

### B-13 -- `PerfilFamilia.verificaciones_aceptacion` es un campo declarativo
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:1265-1267,1275; src/modulos/M1_clasificacion.py:337
Solo lo escribe M1 y lo leen dos asserts de tests; no hay consumidores dinamicos (getattr, `fields`, `asdict`, plantillas). El docstring, leido entero, declara por que nada despacha sobre el: "None significa 'no declarado', no 'ninguna': la tabla de la Fase 5 sigue aplicando punto por punto". Queda como observacion que el campo tampoco viaja a la memoria (cli.py:976-977 publica solo familia y origen del caudal).
**Regla:** el docstring de `PerfilFamilia` promete decir "con que verificaciones se acepta"; Claude.md, Arquitectura: "Los tipos que fluyen entre modulos estan en modelos.py".
**Evidencia:**
```
$ grep -rn "verificaciones_aceptacion" src/ cli.py gui/app.py tests/ docs/
M1_clasificacion.py:337 (("V1","V2","V4","V5")), :351 None, :371 None
modelos.py:1265, :1275 | tests/test_M1_clasificacion.py:281, :291
(cero en docs/, cero en plantillas, cero via getattr)
$ sed -n '1265,1267p' src/modelos.py
    `verificaciones_aceptacion` es None cuando la hoja de ruta no declara un
    conjunto propio ... la tabla de la Fase 5 sigue aplicando punto por punto.
```
**Verificacion:** Lente 1 reprodujo el grep identico; lente 2 leyo el docstring completo que el auditor cito recortado (GRAVE -> OBSERVACION).

### B-14 -- Trece constantes `[N]` del Anexo B sin ningun consumidor
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** CONFIRMADO - **Detectado desde 2 dimensiones** (B1, B2) - **Ubicacion** src/constantes_normativas.py:29,30,91,146,147,149,152,161,173,283,284,287,293
DIAMETRO_MIN, DIAMETRO_MIN_SELVA_ALTA, LONG_MAX_CUNETA, CBR_MIN_SUBRASANTE, COMPACTACION_CORONA/CUERPO, CALICATAS_POR_KM/POR_SENTIDO, ESPACIAMIENTO_PERFIL_KM, SPT_PROF_MIN, SPT_ESPACIAMIENTO, SULFATOS y CLORUROS_EXTERNOS tienen prod=0. La razon esta en la primera linea util del archivo ("Anexo B ... copiado literalmente") y todas estan catalogadas en el manifiesto con numeral y fuente. Queda como observacion util que no existe lista que separe constantes de referencia de constantes que gobiernan el calculo.
**Regla:** ninguna incumplida. Contrasta con `PERFIL_SUELO_PRESUNTO`, declarado "referencia muerta" en el manifiesto y vigilado por test.
**Evidencia:**
```
$ for n in DIAMETRO_MIN ... CLOROS_EXTERNOS; do printf "%-24s prod=%s tests=%s docs=%s\n" ...; done
DIAMETRO_MIN prod=0 tests=4 docs=2 | LONG_MAX_CUNETA prod=0 tests=0 docs=2
CBR_MIN_SUBRASANTE prod=0 | COMPACTACION_CORONA prod=0 docs=8 | SULFATOS prod=0 docs=5 ...
$ sed -n '4p' src/constantes_normativas.py
Anexo B de docs/hoja_de_ruta_alcantarillas_v8.md, copiado literalmente.
$ sed -n '75p;93p' docs/manifiesto_citas.md
| `DIAMETRO_MIN_SELVA_ALTA = 1.22` m ... [CN:30] | [N] |
| `LONG_MAX_CUNETA = {...}` | 4.1.2.1 d) ... [CN:91] | [N] |
```
**Verificacion:** Lente 1 verifico las trece lineas una por una en las dos pasadas; lente 2 comparo el archivo con el Anexo B (hoja de ruta:745-797) y encontro la transcripcion literal.

### B-15 -- `demanda_sismica_licuefaccion = 1000` no aparece en ninguna salida
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:1045-1056
Cero referencias de codigo y 0 coincidencias en la memoria de perfil y de expediente: tiene valor (no entra en `criterios_sin_valor`) y nadie lo invoca (no entra en `criterios_usados`). La adopcion esta declarada en la fuente de verdad -- §0.6 de la hoja de ruta ("Adoptado: Tr = 1000 anios [A] ... Se descarta el sismo de 475 anios de E.030") y dos filas del manifiesto -- para un calculo que §0.5 declara fuera del alcance del script. Sin linea escrita queda que un criterio con valor y sin invocacion desaparece del HTML.
**Regla:** Claude.md: "[A] Sin norma ni fuente unica. Adopcion declarada + sensibilidad."
**Evidencia:**
```
$ grep -rn "demanda_sismica_licuefaccion" --include=*.py --include=*.html --include=*.md .
./src/criterios_adoptados.py:1045 | ./docs/manifiesto_citas.md:344, :480, :498
$ grep -c demanda_sismica_licuefaccion mem.html mem_exp.html -> 0 / 0
$ sed -n '115,117p' docs/hoja_de_ruta_alcantarillas_v8.md
### 0.6 Demanda sismica para la evaluacion de licuefaccion - CERRADO
**Adoptado: Tr = 1000 anios** `[A]` ...
```
**Verificacion:** Lente **Verificacion:** Lente 1 reprodujo grep y corrida (0 coincidencias en las dos memorias); lente 2 hallo §0.6 completa y las dos filas del manifiesto (GRAVE -> OBSERVACION).

### B-16 -- `sucs_fundacion` es columna obligatoria que ningun modulo lee
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:377; src/modulos/M0_carga.py:209; src/modulos/M11_reporte.py:160
Se carga con `_texto()` (obligatoria), ningun modulo lee el atributo y su unico destino es `CAMPOS_CSV`. La obligatoriedad no es invencion del codigo: la hoja de ruta:182 la lista con etiqueta `[N] E.050` y la linea 190 la incluye en el encabezado literal del CSV de Sec. 1.2. Su consumidor previsto, `c_phi_fundacion`, esta declarado vacio y registrado como pendiente externo que la memoria imprime.
**Regla:** Claude.md, Excepciones: "DatoFaltanteError ... la celda obligatoria viene vacia." Ninguna regla se rompe.
**Evidencia:**
```
$ grep -rn "\.sucs_fundacion" src/ cli.py gui/app.py --include=*.py   -> (vacio)
$ grep -rn "sucs_fundacion" src/modulos/ --include=*.py
M0_carga.py:209 (_texto) | M11_reporte.py:160 (CAMPOS_CSV)
$ sed -n '182p;190p' docs/hoja_de_ruta_alcantarillas_v8.md
| Clasificacion SUCS de fundacion | - | Calicata mas cercana | [N] E.050 |
cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion
```
**Verificacion:** Lente 1 reprodujo los dos greps; lente 2 encontro la columna en la fuente de verdad, que el auditor no busco (MENOR -> OBSERVACION).

### B-17 -- `EmpujesTrasdos` no lo alcanza ninguna corrida
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:1060-1116; src/modulos/M9_cabezal.py:736,802
Solo lo observan los tests: cli.py no importa `empujes_trasdos` y gui/ no toca M9. La constancia que el auditor daba por inexistente si existe y se imprime en el entregable: `NOTA_ESTABILIDAD_CABEZAL` (cli.py:168-175) declara que la CLI no ensambla E1-E5 porque "elegir el plano de empuje ... seria decidir por el proyectista", y M9:85-89 nombra `empujes_trasdos` entre los ensambles diferidos. Aunque la CLI lo llamara se detendria en `phi_relleno_trasdos`, que ya figura en `bloquearon`.
**Regla:** Claude.md, Arquitectura: "Los tipos que fluyen entre modulos estan en modelos.py."
**Evidencia:**
```
$ grep -rn "empujes_trasdos\|EmpujesTrasdos" src/ cli.py gui/app.py tests/ --include=*.py
M9_cabezal.py:88,170,736,739,802 | modelos.py:1060 | tests/test_M9_cabezal.py:56,447,924,928
(cero en cli.py, gui/app.py, MD.py)
$ python3 cli.py tests/ejemplo_puntos.csv | grep 'nota: Las verificaciones E1-E5'
    nota: Las verificaciones E1-E5 de Sec. 9.3 no las ensambla esta CLI: ...
$ sed -n '785,787p' src/modulos/M9_cabezal.py
    K_A_rankine = ka_rankine(phi_grados=ca.valor(CRITERIO_PHI_RELLENO))  # criterio vacio
```
**Verificacion:** Lente 1 reprodujo grep e imports; lente 2 hallo la nota impresa y el docstring que nombra la funcion (MENOR -> OBSERVACION).

### B-18 -- Cinco campos de dataclass escritos y nunca leidos
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:599 (`ahogado_por_TW`), :1135-1136, :1157, :1180
Ninguna lectura en produccion. Cuatro de los cinco tienen su decision escrita: `componentes`/`criterio_factores` porque `CombinacionCarga` "describe la combinacion y no la evalua"; `cuantia_adoptada` porque lo escribe `cuantia_de_diseno()`, parte del diseno por flexion detenido con `NotImplementedError`; `criterio_aashto` es redundante, no roto, porque la traza de `recubrimiento_aashto_mm` si llega a la memoria por `criterios_usados`. El unico sin cobertura es `ahogado_por_TW`, que distingue la rama que Sec. 4.3 advierte para descargas a drenes y no se emite ni al JSON ni al HTML.
**Regla:** Claude.md, Arquitectura: los campos `criterio_*` existen para que la trazabilidad viaje hasta la memoria.
**Evidencia:**
```
$ grep -rn "\.ahogado_por_TW\|\.cuantia_adoptada\|\.criterio_aashto\|\.criterio_factores\|\.componentes\b" src/ cli.py gui/app.py src/plantillas/
(vacio: ninguna lectura en produccion)
$ sed -n '1126,1131p' src/modelos.py
    ... este objeto describe la combinacion y no la evalua: pedir los factores
    detiene el calculo (Sec. 0.7).
$ python3 -c "...[c['clave'] for c in d['criterios']['usados']]"
[... 'recubrimiento_aashto_mm']   # la traza SI llega a la memoria
```
**Verificacion:** Lente 1 reprodujo los dos comandos y las cinco lineas; lente 2 leyo los docstrings completos y separo el unico caso sin cobertura (MENOR -> OBSERVACION).

### B-19 -- Cinco criterios sin consumidor, todos registrados como pendientes declarados
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (B1, D2) - **Ubicacion** src/criterios_adoptados.py:347,1013,1024,1033,1325
`PERFIL_SUELO_PRESUNTO`, `c_phi_fundacion`, `capacidad_portante_adm`, `Mw_licuefaccion` y `angulo_aletas` tienen cero invocaciones y cero referencias en produccion. Los cuatro con `valor=None` salen en `sin_valor_declarados` del JSON y en el bloque de criterios sin valor del HTML. Los consumidores que faltan son los que la CLI declara no ensamblar (E1-E5, licuefaccion fuera de alcance, geometria de aletas), y la auditoria v9:766-772 declara que imprimirlos como pendientes "es exactamente lo correcto a nivel de perfil".
**Regla:** Claude.md: "Crea una entrada ... **y deten el calculo con excepcion**." No hay calculo que detener porque el calculo esta declarado fuera de alcance.
**Evidencia:**
```
$ for k in PERFIL_SUELO_PRESUNTO c_phi_fundacion capacidad_portante_adm Mw_licuefaccion angulo_aletas; do ...; done
los cinco: invocaciones_valor=0 otras_refs_prod=0
$ grep -rn "c_phi_fundacion|capacidad_portante_adm" --include=*.py . | grep -v 'src/criterios_adoptados.py'
./tests/test_criterios_adoptados.py:56, :57   (CLAVES_DEL_ANEXO_A)
$ sed -n '766,772p' docs/auditoria_y_ruta_despliegue_v9.md
**C.3 - Dependen de datos externos** ... La memoria de calculo los va a imprimir
en el bloque 4 con su fundamento, que es exactamente lo correcto a nivel de perfil.
$ python3 -c "...d['criterios']['sin_valor_declarados']"  -> incluye los cuatro vacios
```
**Nota de evidencia:** el comando original de D2 estaba roto -- su `grep -v criterios_adoptados.py` borraba tambien `tests/test_criterios_adoptados.py` (coincidencia de subcadena) y su `echo "(sin coincidencias)"` corria siempre. Va la salida corregida del verificador.
**Verificacion:** Lente 1 reprodujo los conteos y corrigio el pipeline roto; lente 2 hallo `angulo_aletas` en la hoja de ruta:734 y en la auditoria v9:744, y los otros dos en C.3.

### B-20 -- Las siete funciones de armado de 9.4 no tienen llamador
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M9_cabezal.py:1265,1288,1353,1361,1380,1389,1406; cli.py:168-175
Cero referencias en cli.py, gui/app.py y M11. Cinco de las siete exigen el espesor o la cuantia del muro, que salen del predimensionamiento del cabezal: criterio vacio declarado en M9:64-66 y registrado como Bloqueo en cada corrida de `correr_cabezal()`. Las otras dos son verificaciones a posteriori por diseno declarado (`verificar_cuantia` dice que la cuantia "puede venir de un plano que nadie paso por cuantia_de_diseno").
**Regla:** el patron que el proyecto se impone (cli.py:140-141: "Nada de lo diferido se pierde: queda registrado como Bloqueo") -- y se cumple.
**Evidencia:**
```
$ for n in cuantia_de_diseno verificar_cuantia espaciamiento_maximo verificar_espaciamiento requiere_temperatura_dos_caras nota_temperatura_dos_caras verificar_ciclopeo; do ...; done
los siete: 0
$ sed -n '64,66p' src/modulos/M9_cabezal.py
    predimensionamiento_cabezal  H, B, D_f y espesores: Sec. 9 no dimensiona
                                 el cabezal y Sec. 1.2 no trae sus columnas.
$ python3 -c "import cli; [print(b.etapa,'|',b.tipo) for b in cli.correr_cabezal().bloqueos]"
K_AE de Mononobe-Okabe (9.2) | CriterioPendienteError
predimensionamiento del cabezal (9.3, E1-E5) | CriterioPendienteError
```
**Verificacion:** Lente 1 reprodujo el bucle y la nota; lente 2 encontro el vacio declarado y el Bloqueo emitido en cada corrida (GRAVE -> OBSERVACION).

### B-21 -- `n_q/n_s_zapata_en_talud` sin llamador interno
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M9_cabezal.py:1018,1047,1086-1089
`capacidad_portante_zapata_en_talud` llama `ca.valor(CRITERIO_MEYERHOF)` y lanza `AssertionError` sin usar ninguna de las dos funciones. El docstring de esa misma funcion (M9:1076-1079) declara por que: con suelo friccionante `n_s_zapata_en_talud` levantaria `DatoInvalidoError` culpando al dato "cuando lo que falta de verdad es la lectura de los abacos. N_s se calcula aparte, con esa funcion, al ir a leerlos". `n_q_zapata_en_talud` es un `[N]` literal catalogado en el manifiesto con su numeral.
**Regla:** Claude.md:9-12 obliga a detener el calculo ante un vacio, y se cumple.
**Evidencia:**
```
$ sed -n '1086,1089p' src/modulos/M9_cabezal.py
    ca.valor(CRITERIO_MEYERHOF)   # CriterioPendienteError mientras falte
    raise AssertionError("inalcanzable mientras 'N_cq_N_gammaq_meyerhof' este vacio")
$ sed -n '1076,1079p' src/modulos/M9_cabezal.py
    friccionante (c = 0 por E.050 Art. 20) `n_s_zapata_en_talud` levantaria
    `DatoInvalidoError` ... N_s se calcula aparte, con esa funcion, al ir a leerlos.
$ grep -rn "n_q_zapata_en_talud\|n_s_zapata_en_talud" --include=*.py . | grep -v 'def '
M9_cabezal.py:116, :1076 | tests/test_M9_cabezal.py:62, 640, 645, 649, 656
```
**Nota de evidencia:** la salida que el auditor pego (`tests/test_M9_cabezal.py:634 ... == pytest.approx(1.44)`) NO existe: la linea 634 es `def test_en_friccionante_c_se_anula`. Va la del verificador.
**Verificacion:** Lente 1 reprodujo el `sed` y desmintio la salida de tests; lente 2 hallo el uso previsto declarado en el docstring (MENOR -> OBSERVACION).

### B-22 -- Cuatro APIs publicas sin consumidor de produccion
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:181; src/modulos/M11_reporte.py:196; src/modelos.py:466; src/modulos/M9_cabezal.py:561-573
`limpiar_valores_dinamicos`, `marcadores_de_la_memoria`, `v_max_definida` y `aplica_sobrecarga_trasdos` solo aparecen en su definicion fuera de tests/. La acusacion que sostenia la regla es falsa: M5:282 no comprueba nada, es un desempaquetado `_, v_max = material.v_max_rango` detras del `return` de la rama TMC/HDPE, asi que nadie reimplementa `v_max_definida`. Y `aplica_sobrecarga_trasdos` declara su motivo en el docstring. Quedan dos utilidades sin llamador.
**Regla:** ninguna prohibicion explicita; Claude.md:71-72 no aplica una vez desmontado el caso de M5.
**Evidencia:**
```
$ for n in limpiar_valores_dinamicos marcadores_de_la_memoria v_max_definida aplica_sobrecarga_trasdos; do grep -rn "\b$n\b" --include=*.py . | grep -v '/tests/'; done
los cuatro: solo la def
$ sed -n '566,569p' src/modulos/M9_cabezal.py
    ... Esta funcion existe para el caso en que alguien tenga la distancia
    medida y quiera comprobarlo en vez de invocar la regla general.
$ grep -rn "v_max_rango" --include=*.py src/ cli.py gui/app.py
M5:228 (docstring), M5:282 (desempaquetado), M2:46,264,280-292, modelos.py:451,468
```
**Verificacion:** Lente 1 reprodujo el bucle; lente 2 leyo la linea acusatoria y comprobo que no dice lo afirmado (MENOR -> OBSERVACION).

### B-23 -- Dos guardas provablemente inalcanzables, ambas con su razon escrita
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M5_verificaciones.py:338-341; src/modulos/M7_geometria.py:403-409
Las cuatro filas de `RESGUARDO_NAPA_SUBRASANTE` cubren todo el eje real, de modo que el `ValueError` de `resguardo_por_cbr` no puede dispararse; y M0 exige `0 <= esviaje < ESVIAJE_MAX` mientras M7 admite ademas el rango negativo, de modo que su guarda es un superconjunto de lo que M0 ya admite. Las dos estan declaradas defensivas en sus docstrings.
**Regla:** ninguna. M5:325-326 ("exhaustivas por construccion") y M7:401 ("`dominios.ESVIAJE_MAX`, que M0 ya exige a la entrada").
**Evidencia:**
```
$ python3 -c "...RESGUARDO_NAPA_SUBRASANTE..."
filas: [(20.0, None), (6.0, 20.0), (3.0, 6.0), (None, 3.0)]
sin cobertura en [-1e6,1e6]: []
$ sed -n '325,331p' src/modulos/M0_carga.py
    _exige(cbr <= CBR_MAX_FISICO, ...)   /   _exige(0 <= v["esviaje_grados"] < ESVIAJE_MAX, ...)
$ sed -n '403p' src/modulos/M7_geometria.py
    if not (-ESVIAJE_MAX < punto.esviaje_grados < ESVIAJE_MAX):
```
**Nota de evidencia:** el auditor cito el `raise` de M5 en 337-340 (es 338-341) y parafraseo mal el motivo del CBR de M0 ("no es un CBR: es otra escala..." cuando el texto real es "no es un suelo: revisa si el valor esta en otra escala").
**Verificacion:** Lente 1 corrio el script de cobertura de la tabla y comparo los dos rangos; lente 2 confirmo los docstrings que declaran la redundancia intencional.

### C-01 -- La guardia de substring de `factor_muro` se evade con comillas simples
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** tests/test_sin_literales.py:223
Insertando una entrada `'factor_muro': Criterio(...)` con comillas SIMPLES dentro del dict CRITERIOS, la suite entera queda en 725 passed: ningun otro test comprueba semanticamente que `factor_muro` no sea clave de CRITERIOS. La mitad gemela del hallazgo original queda REFUTADA: reintroducir `ZONA_SISMICA_LA_UNION` en constantes_normativas.py SI hace fallar la suite, porque dos guardias usan `hasattr` sobre el modulo importado.
**Regla:** docs/manifiesto_datos_proyecto_vs_constantes.md:185-187: "Si alguien deshace cualquiera de las cuatro correcciones, falla la suite y no la lectura de un manifiesto." Se cumple para el `[S]`, no para `factor_muro`.
**Evidencia:**
```
$ cd $SP/repoA && printf '\nZONA_SISMICA_LA_UNION  = 4\n' >> src/constantes_normativas.py && pytest -q | tail -3
FAILED tests/test_constantes_normativas.py::test_el_Z_de_E030_ya_no_es_una_constante_normativa
FAILED tests/test_datos_sitio.py::test_ninguno_de_los_tres_sigue_declarado_en_otro_archivo
2 failed, 723 passed, 1 skipped
$ cd $SP/repoC   # 'factor_muro': Criterio(...) con comillas simples dentro de CRITERIOS
$ python3 -m pytest -q | tail -1
725 passed, 1 skipped in 3.09s
```
**Verificacion:** Lente 1 corrio la suite completa (no solo el archivo de test) y refuto la mitad del `[S]`; lente 2 confirmo que el manifiesto no documenta ninguna limitacion de las guardias (GRAVE -> MENOR: `factor_muro_eleccion` es el simbolo que entra al calculo).

### C-02 -- Guardias de arquitectura implementadas leyendo el texto fuente de modulos .py
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (C1, F2) - **Ubicacion** tests/test_sin_literales.py:177-206,221; test_M8_estructural.py:177-179; test_M5_verificaciones.py:180-186; test_M11_reporte.py:643-647; test_criterios_adoptados.py:247; test_datos_sitio.py:153
22 asserts comprueban subcadenas sobre el `.py`, no simbolos: comentar `METROS_POR_KM = 1000` en dominios.py deja pasar `test_los_limites_de_dominio_salieron_de_M0`, y la mencion del simbolo en un comentario de M0 satisface `assert nombre in m0`. Atenuantes verificados: la regresion no puede pasar desapercibida (la suite se cae en coleccion con 6 ImportError), el docstring del test declara que el guardia real es el barrido AST, y el test de M8 asserta comportamiento antes de mirar la fuente.
**Regla:** el docstring del propio test (tests/test_sin_literales.py:173-175): "este test dice donde tienen que estar" -- verifica que tres cadenas aparezcan, no que esten declaradas.
**Evidencia:**
```
$ python3 - (con METROS_POR_KM comentado en una copia)
PASA test_los_limites_de_dominio_salieron_de_M0
dominios.METROS_POR_KM existe? False
$ sed -n '180,182p' tests/test_sin_literales.py
        assert f"{nombre} =" in dominios / assert f"{nombre} =" not in m0 / assert nombre in m0
$ cd $SP/repoD && python3 -m pytest -q | tail -2
ERROR tests/test_cli.py
!!!!!! Interrupted: 6 errors during collection !!!!!!
$ grep -rn "read_text" tests/*.py | grep -v "\.md|\.html|\.csv|\.json|tmp_path"
test_sin_literales:177,178,191,192,193 | test_M8:177 | test_M11:643 | test_M5:180 | test_criterios_adoptados:247
```
**Verificacion:** Lente 1 reprodujo la evasion y la contraprueba de coleccion; lente 2 encontro el docstring que reparte el trabajo con el barrido AST (GRAVE -> MENOR).

### C-03 -- La marca `# literal-ok` se busca como substring: vale dentro de un string o de un docstring
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** tests/test_sin_literales.py:79; src/dominios.py:38
`MARCA in lineas[indice]` es texto plano, sin tokenizar: un string de produccion que contenga la cadena exime su linea y la siguiente, y un docstring que EXPLIQUE la convencion hace lo mismo. No es hipotetico: dominios.py:38 lleva la cadena dentro del docstring de modulo. dominios.py esta exento del barrido, asi que hoy no rompe nada.
**Regla:** tests/test_sin_literales.py:29 y Claude.md:68-69 declaran la exencion como "el comentario `# literal-ok: <razon>`"; el codigo acepta la cadena en cualquier posicion.
**Evidencia:**
```
$ python3 -c "...literales_prohibidos('MSG = \"vease # literal-ok\"\nN_MANNING = 0.013\n')"
string   : []
docstring: []
$ python3 (tokenize sobre todo src/)
src/dominios.py  comentario: [47,51,58,64] | dentro de string: [1]
otros modulos    dentro de string: []
$ sed -n '79p' tests/test_sin_literales.py
        if 0 <= indice < len(lineas) and MARCA in lineas[indice]:
```
**Verificacion:** Lente 1 reprodujo los dos casos y confirmo con `tokenize` el caso real de dominios.py; lente 2 no hallo documentacion de esta laxitud.

### C-04 -- `_nodos_de_indice` exime TODO entero dentro de un `Subscript`
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** tests/test_sin_literales.py:65-73,117
La funcion recorre el subarbol completo de `nodo.slice` y exime cualquier `ast.Constant` entero, sin mirar de que se indexa: `CAUDAL_POR_TR[500]` y `TABLA[900][2500]` no producen ni un hallazgo. Hoy no esta ejercitado (las tablas del proyecto se indexan por string), pero la primera tabla indexada por numero entra sin guardia.
**Regla:** el docstring de la propia funcion la acota a "indices y rebanadas: x[3], x[1:5]"; Claude.md:47-50 exige que un valor de proyecto viva en uno de los tres archivos declarados, y una clave numerica de tabla lo es.
**Evidencia:**
```
$ python3 -c "...literales_prohibidos('q = CAUDAL_POR_TR[500]\nD = TABLA[900][2500]\n')"
[]
$ grep -n "F_PGA_TABLA = \|FACTOR_MURO_TABLA = " -A3 src/constantes_normativas.py
238: {"C": 1.0, "D": 1.0, "E": 0.9}   246: {"rigido": 1.0, "desplazable": 0.5}
$ python3 (barrido de src/): enteros que sobreviven SOLO por la exencion de Subscript: []
```
**Verificacion:** Lente 1 reprodujo el `[]` y rehizo el barrido de src/; lente 2 comparo el codigo con los dos docstrings que lo acotan.

### C-05 -- La lista de exentos se aplica por nombre de archivo a cualquier profundidad
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** tests/test_sin_literales.py:130-131,164-166
`if ruta.name in EXENTOS` compara el basename: un archivo `src/modulos/dominios.py` quedaria exento sin que nadie lo declare, y la guardia que vigila la lista solo mira `SRC / nombre`, asi que tampoco lo detecta. Hoy no hay duplicados: cada uno de los seis nombres aparece una sola vez bajo src/.
**Regla:** tests/test_sin_literales.py:7 habla de "los seis archivos exentos" y :162 dice "Si alguno se renombra, la lista de exentos queda obsoleta sin avisar"; la exencion esta atada a seis nombres, no a seis archivos.
**Evidencia:**
```
$ python3 - (dos archivos con el mismo 4.5 en el mismo directorio)
barrido: {'modulos/M3_hidraulica.py': [(1, 4.5)]}
   # modulos/dominios.py, con 4.5 y 0.013 dentro, no produce ni un hallazgo
$ sed -n '130,131p;164p' tests/test_sin_literales.py
    for ruta in sorted(raiz.rglob("*.py")):  /  if ruta.name in EXENTOS:  /  ruta = SRC / nombre
$ for n in constantes_normativas criterios_adoptados datos_sitio tolerancias dominios constantes_fisicas; do find src -name "$n.py" | wc -l; done -> 1 cada uno
```
**Verificacion:** Lente 1 reprodujo el barrido y verifico las dos lineas; lente 2 confirmo que el docstring habla de archivos y el codigo de nombres.

### C-06 -- `barrido()` solo recorre src/: cli.py y gui/app.py quedan sin vigilancia
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (C1, C2) - **Ubicacion** tests/test_sin_literales.py:51,147; cli.py:178; gui/app.py:85
`SRC = RAIZ/'src'` y el unico `barrido(SRC)`. cli.py da 8 literales prohibidos (3 valores distintos) y gui/app.py 151 (32 distintos), frente a 0 en todo src/. Los 159 se clasificaron uno a uno: ANCHO=78, decimales=3, `SANGRIA*4`, paddings, anchos de columna, tamanos de fuente y el retardo del tooltip. Ninguno es valor de proyecto. El alcance esta declarado en el docstring del test; lo que no esta escrito en ninguna parte es POR QUE los dos archivos quedan fuera.
**Regla:** Claude.md:47-50: "Todo literal numerico fuera de [los tres archivos] es un defecto y se rechaza en revision" -- sin restringirlo a src/.
**Evidencia:**
```
$ python3 -c "...literales_prohibidos por archivo..."
cli.py 8 literales prohibidos; 3 valores distintos
gui/app.py 151 literales prohibidos; 32 valores distintos
conftest.py 0 | legacy/Tc.py 185 | src/ 0
$ grep -n "^SRC = \|barrido(SRC)" tests/test_sin_literales.py -> 51 / 147
$ sed -n '176,178p' cli.py
# Presentacion. Ninguno entra en un calculo: mueven columnas de texto.
ANCHO = 78
$ grep -rn "test_sin_literales\|barrido" docs/ Claude.md  -> nada sobre alcance
```
**Verificacion:** Lente 1 reprodujo las cifras en las dos pasadas y listo los 8 de cli.py; lente 2 hallo el alcance declarado y la razon ausente.
**Nota de reconciliacion:** el verificador de C1 puso MENOR aplicando la regla de calibracion del encargo ("un guardia que no cubre un archivo donde hoy no hay violacion real es MENOR"); el de C2 puso OBSERVACION. Va MENOR, que es lo que esa regla nombra.

### C-07 -- La marca en linea propia exime todos los literales de la linea siguiente
**Sev** MENOR - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (C1, F2) - **Ubicacion** tests/test_sin_literales.py:76-81
`_marcado` mira `n-1` y `n-2`: un `# literal-ok: coartada` en linea propia deja pasar `V_MAX_INVENTADA_SIN_DECLARAR = 4.5` dentro de M3_hidraulica.py con la suite en 725 passed. La regla esta escrita en el docstring de la funcion ("La marca vale en la propia linea o en la anterior"), pero el parentesis "(expresiones partidas)" describe una intencion mas estrecha que lo que el codigo permite. Hoy no hay en src/ ni un literal cubierto solo por la marca de la linea anterior.
**Regla:** Claude.md:67-70: la marca "lo declara y lo hace visible en revision".
**Evidencia:**
```
$ cd $D/r && printf '\n# literal-ok: coartada\nV_MAX_INVENTADA_SIN_DECLARAR = 4.5\n' >> src/modulos/M3_hidraulica.py
$ python3 -m pytest -q tests/test_sin_literales.py | tail -1  -> 19 passed
$ python3 -m pytest -q | tail -1                              -> 725 passed, 1 skipped
$ sed -n '76,80p' tests/test_sin_literales.py
def _marcado(lineas, numero_de_linea):
    """La marca vale en la propia linea o en la anterior (expresiones partidas)."""
    for indice in (numero_de_linea - 1, numero_de_linea - 2):
$ python3 (barrido de src/): lineas cubiertas SOLO por marca de la linea anterior: []
```
**Verificacion:** Lente 1 reprodujo la evasion sobre un modulo real y comprobo que no esta ejercitada hoy; lente 2 hallo la regla escrita en el docstring de la funcion implicada.
**Nota de reconciliacion:** el verificador de C1 bajo a OBSERVACION por estar documentada; el de F2 mantuvo MENOR por la evasion demostrada sobre un modulo de produccion. Va MENOR.

### C-08 -- `valor in NUMEROS_PERMITIDOS` deja pasar complejos
**Sev** OBSERVACION - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** tests/test_sin_literales.py:57,115,119
`0j` y `2+0j` pertenecen a `{0, 1, 2}` y el filtro admite `complex`, de modo que un literal complejo cuya parte real valga 0, 1 o 2 pasa el detector. El caso `float` (2.0, 1e0) si esta documentado en el propio archivo y no se reporta. Ningun modulo de un proyecto de hidraulica declara literales complejos: riesgo latente puro.
**Regla:** Claude.md:50-51: "Excepciones permitidas: 0, 1, 2, indices, y constantes matematicas puras (pi)."
**Evidencia:**
```
$ python3 -c "...literales_prohibidos('a=2.0\nb=1e0\nc=0j\nd=2+0j\ne=-0.0\n')..."
detector: []
2.0 in: True | 1e0 in: True | 0j in: True | (2+0j) in: True
$ sed -n '57p;115p;119p' tests/test_sin_literales.py
NUMEROS_PERMITIDOS = {0, 1, 2}
        if isinstance(valor, bool) or not isinstance(valor, (int, float, complex)):
        if valor in NUMEROS_PERMITIDOS:   # 2 y 2.0 entran por igual
$ grep -rn "complex\|complejo" docs/ Claude.md   -> (sin resultados)
```
**Verificacion:** Lente 1 reprodujo literalmente; lente 2 leyo Claude.md:50-51 completo -- la lista no contempla el caso ni lo prohibe (MENOR -> OBSERVACION por impacto nulo).

### C-09 -- Valores de proyecto construidos por conversion de string son invisibles al detector
**Sev** OBSERVACION - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** tests/test_sin_literales.py:111-124
El detector es puramente sintactico: `int("13")/int("1000")`, `float("4.6")` e `int("500")` no producen hallazgo, y el modulo importado expone 0.013, 4.6 y 500. Solo cae el 0.9 escrito como literal. Requiere ofuscacion deliberada, no es un riesgo de escritura accidental; el limite no esta acotado en el docstring, que presenta el test como "Guardia automatica de la regla de arquitectura".
**Regla:** Claude.md:47-50 (regla de revision humana, que el detector solo apoya).
**Evidencia:**
```
$ python3 - (fichero sintetico con las tres conversiones + un 0.9 literal)
barrido: {'modulos/M3_hidraulica.py': [(5, 0.9)]}
valores realmente declarados: 0.013 4.6 500 0.9
aislado: []          # 3*0.1 SI cae: [(1, 0.1), (1, 3)]
```
**Nota de evidencia:** el auditor pego `[(6, 0.9)]`; la salida real es `[(5, 0.9)]` (el fichero sintetico empieza con un salto de linea).
**Verificacion:** Lente 1 reprodujo la sustancia y corrigio el numero de linea; lente 2 confirmo que el docstring no acota el alcance del detector (MENOR -> OBSERVACION).

### C-10 -- `tests/ejemplo_puntos.informe.json`: salida de corrida versionada, sin uso y sin ignorar
**Sev** OBSERVACION - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Detectado desde 2 dimensiones** (C2, F2) - **Ubicacion** tests/ejemplo_puntos.informe.json; cli.py:1475; .gitignore
El archivo esta versionado, ninguna referencia lo lee (tests/, src/, cli.py, docs/, conftest.py) y cualquier corrida del CLI lo reescribe: `python3 cli.py tests/ejemplo_puntos.csv` deja ` M tests/ejemplo_puntos.informe.json` con 192 inserciones. `.gitignore` ya aplica el criterio contrario a los reportes HTML generados y no cubre `*.informe.json`. Su ultimo cambio viene arrastrado en un commit sobre otro tema (f6168fa): no hay decision, hay deriva.
**Regla:** Claude.md, Cierre de tarea: la entrega se comprueba sobre un arbol limpio; un artefacto generado y versionado hace que "git status limpio" deje de ser senal fiable.
**Evidencia:**
```
$ grep -rn "ejemplo_puntos.informe" tests/ src/ cli.py docs/ conftest.py   -> (sin salida)
$ git ls-files tests/ejemplo_puntos.informe.json -> versionado
$ cat .gitignore -> __pycache__/ *.pyc *.pyo .env  /reporte_*.html   (no cubre el patron)
$ sed -n '1475p' cli.py
    destino = args.json_salida or args.csv.with_suffix(".informe.json")
$ (en copia) python3 cli.py tests/ejemplo_puntos.csv; git diff --stat
 tests/ejemplo_puntos.informe.json | 225 ++++--  (192 insertions, 33 deletions)
$ git log --oneline -1 -- tests/ejemplo_puntos.informe.json
f6168fa h_relleno_min_concreto_tmc = 0.30 m, adoptado [N->] por analogia
```
**Verificacion:** Lente 1 reprodujo grep, .gitignore y el ensuciado sobre copia; lente 2 no hallo ninguna nota que lo declare fixture ni salida caduca.

### C-11 -- El barrido solo mira `.py`: las plantillas HTML quedan fuera
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Ubicacion** tests/test_sin_literales.py:130; src/plantillas/memoria_alcantarillas.html; src/plantillas/memoria_perfil.html
`raiz.rglob("*.py")` deja los dos ficheros de src/plantillas/ fuera de la guardia pese a vivir dentro de src/. Revisados numero a numero: fuera del `<style>` solo hay numeracion de seccion. No hay valores de calculo hoy; la limitacion por formato no esta escrita como decision en ningun sitio.
**Regla:** Claude.md:47-50 habla de "todo literal numerico" sin restringir el formato; el docstring del test dice "Todo literal numerico bajo src/" y src/plantillas/ esta bajo src/.
**Evidencia:**
```
$ for f in src/plantillas/*.html; do awk '/<\/style>/,0' $f | grep -oE "[0-9]+(\.[0-9]+)*" | sort -u | tr '\n' ' '; done
memoria_alcantarillas.html: 0 0.1 1 11 2 3 3.1 3.2 4
memoria_perfil.html:        0 1 2 3 3.1 3.2 4
$ sed -n '130p' tests/test_sin_literales.py
    for ruta in sorted(raiz.rglob("*.py")):
$ grep -rn "plantilla" docs/*.md Claude.md   -> ninguna linea sobre el alcance del barrido
```
**Verificacion:** Lente 1 reprodujo las dos listas byte a byte; lente 2 confirmo que la unica guardia sobre plantillas (test_M11_reporte.py:878) valida marcadores, no literales.

### C-12 -- El docstring de Uso de M1 da luces de ejemplo sin la salvedad que si lleva el test
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M1_clasificacion.py:54-62
El dict `{"A-01": 2.75, "A-02": 1.80, "B-01": 1.20, "C-01": 2.75}` aparece sin salvedad en el modulo y con tres lineas de advertencia en el test. La premisa que sostenia la severidad es falsa: los ids no son puntos reales del expediente sino los de `tests/ejemplo_puntos.csv`, que el propio ejemplo carga en la linea anterior; grep de esos ids y de sus progresivas en docs/ da cero. El ejemplo es internamente coherente; falta que la salvedad viva tambien en produccion.
**Regla:** cli.py:51-53 ("no se sustituye por un numero plausible") y Claude.md:9 -- ninguna se rompe aqui.
**Evidencia:**
```
$ sed -n '58,60p' src/modulos/M1_clasificacion.py
    puntos = cargar_puntos("tests/ejemplo_puntos.csv")
    luces = {"A-01": 2.75, "A-02": 1.80, "B-01": 1.20, "C-01": 2.75}
$ sed -n '40,43p' tests/test_M1_clasificacion.py
# Luz del cruce por punto: no es columna de Sec. 1.2 y por eso la pone el test ...
$ grep -rn "A-01\|0+380\|1+920\|2+450\|3+100" docs/   -> (sin resultados)
```
**Verificacion:** Lente 1 reprodujo el comando y verifico el origen de los ids; lente 2 confirmo que ningun documento los presenta como puntos medidos (MENOR -> OBSERVACION).

### C-13 -- M11 convierte prosa Markdown de la hoja de ruta en filas de la memoria
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M11_reporte.py:337,415-417,424
`tableros_pendientes()` parsea con expresiones regulares titulos, glosas y tablas Markdown y produce 15 filas que entran al entregable; `version_hoja_de_ruta()` extrae la version con `re.findall` sobre el titulo. Verificado que no alimenta ningun calculo: los Tableros solo llegan al bloque de pendientes del HTML.
**Regla:** ninguna. La decision, su razon y la garantia de fallo ruidoso estan en el docstring de la funcion (M11:427-436).
**Evidencia:**
```
$ python3 -c "from modulos.M11_reporte import tableros_pendientes; ..."
Tablero 1: Verificaciones documentales | 4 filas leidas del .md
Tablero 2: Decisiones de proyecto | 5 filas | Tablero 3: Datos externos | 6 filas
$ sed -n '428,433p' src/modulos/M11_reporte.py
    No se transcriben en este modulo a proposito: una copia en Python seria una
    segunda fuente de verdad ... se detiene con ValueError: una memoria con el
    bloque de pendientes vacio diria que no queda nada pendiente ...
```
**Verificacion:** Lente 1 reprodujo las 15 filas y las tres ubicaciones; lente 2 hallo la decision escrita donde un revisor la busca.

### D-01 -- La justificacion de `F_pga` contradice la de `clase_sitio`
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/criterios_adoptados.py:391,464; src/modulos/M9_cabezal.py:24
`F_pga` se defiende con "Sin SPT no hay clase de sitio definitiva ... conservador o exacto frente a las tres clases plausibles" (C, D, E); `clase_sitio`, reescrito tras la auditoria v9, dice "El sitio es Clase F por susceptibilidad a licuefaccion ... esa parte no cambia". `F_PGA_TABLA` no tiene fila F. M9_cabezal.py:24 arrastra el mismo error. Agravante verificado: `F_pga` SI se registra como usado en una corrida real y `clase_sitio` no, de modo que la memoria imprime solo la premisa desactualizada.
**Regla:** docs/auditoria_y_ruta_despliegue_v9.md:554: "Esto no invalida la decision de usar F_pga = 1.0 -- invalida la justificacion con la que se presento." La correccion se aplico a `clase_sitio` y no a `F_pga` ni a la cabecera de M9.
**Evidencia:**
```
$ sed -n '464,467p' src/criterios_adoptados.py
        justificacion="Sin SPT no hay clase de sitio definitiva. Para PGA >= 0.50 ...
                      "las tres clases plausibles; incertidumbre asociada <= 10%",
$ sed -n '391,392p' src/criterios_adoptados.py
        justificacion="El sitio es Clase F por susceptibilidad a licuefaccion ...
$ python3 -c "from constantes_normativas import F_PGA_TABLA; print(F_PGA_TABLA)"
{'C': 1.0, 'D': 1.0, 'E': 0.9}
$ sed -n '24p' src/modulos/M9_cabezal.py
SPT y la clase de sitio se cierre en E, F_pga baja a 0.9 y la cadena entera
$ python3 (corrida real) -> criterios usados: ['F_pga','factor_muro_eleccion','k_v']
```
**Verificacion:** Lente 1 reprodujo las tres citas y la tabla, y busco sin exito una lectura que salvara a F_pga; lente 2 hallo que la auditoria previa ordena la correccion y el codigo no la hizo.

### D-02 -- El censo de etiquetas del manifiesto no coincide con el archivo
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** docs/manifiesto_citas.md:457,519-521,530
El manifiesto declara "1 [N->] - 1 [S] - 14 [C] - 30 [A]" sobre 46; el archivo devuelve 2 `[N->]` (falta `h_relleno_min_concreto_tmc`, que el propio §14.a describe como `[N->]`) y 13 `[C]`. La tabla titulada "Los 33 criterios [A]" tiene 33 filas de las que cuatro son `[C]` en el codigo, y el unico `[A]` ausente es `clase_sitio`, que asi no aparece en ninguna lista de adopciones.
**Regla:** docs/manifiesto_citas.md:530 afirma de si mismo: "Los numeros de arriba son ahora los que devuelve el propio archivo." No lo son.
**Evidencia:**
```
$ python3 -c "Counter(x.etiqueta for x in CRITERIOS.values())"
{'S': 1, 'A': 30, 'C': 13, 'N->': 2}  total 46
N-> reales: ['resguardo_HW_subrasante', 'h_relleno_min_concreto_tmc']
$ sed -n '519,521p' docs/manifiesto_citas.md
**0 [N]** · **1 [N→]** (`resguardo_HW_subrasante`) · **1 [S]** · **14 [C]** · **30 [A]**
$ grep -c '^| `clase_sitio` | ' docs/manifiesto_citas.md -> 0
$ python3 (cruce de las 33 filas): [A] falsos: factores_carga_aashto, peso_especifico_concreto_kn_m3,
  recubrimiento_aashto_mm, procedimiento_flexion_corte_aashto_sec5 (los cuatro [C])
```
**Verificacion:** Lente 1 reprodujo el Counter y cruzo la tabla fila por fila; lente 2 hallo la frase autorreferencial que el documento incumple.

### D-03 -- "Es la unica entrada que se lee con `valor_si_declarado()`" es falso
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:781; docs/manifiesto_citas.md:445,471
La afirmacion esta escrita en tres sitios (codigo + dos filas del manifiesto) y hay cuatro claves mas leidas asi en M2. Matiz que acota el dano: para `h_relleno_min_concreto_tmc` y `v_max_hdpe`/`v_max_tmc` el calculo si se detiene mas tarde (M7:267, M5:270); la unica clave para la que la exclusividad es rotundamente falsa es `n_manning_hdpe`, que no se lee con `valor()` en ningun punto de src/.
**Regla:** Claude.md, Fuente de verdad: la justificacion de un criterio es lo que se defiende en la memoria.
**Evidencia:**
```
$ grep -rn "valor_si_declarado" src/modulos/*.py | grep -v "def \|Delega"
M2_material.py:207, :271, :277, :282 | M5_verificaciones.py:286
$ sed -n '781,783p' src/criterios_adoptados.py
    "memoria no declara este criterio. Es la unica entrada de este archivo que
     se lee con `valor_si_declarado()` en vez de `valor()`. "
$ grep -n "nico que se lee con" docs/manifiesto_citas.md -> 445 (y fila 471)
```
**Verificacion:** Lente 1 reprodujo el grep y las tres afirmaciones; lente 2 no hallo ninguna linea que registre o excuse la exclusividad (GRAVE -> MENOR: no altera ningun valor).

### D-04 -- El rango de sensibilidad de `k_v` no es el "0.5*k_h" que su comentario declara
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:496; src/modulos/M9_cabezal.py:327
Con la cadena de hoy k_h = 0.5, de modo que 0.5*k_h = 0.25 y el extremo declarado 0.5 equivale a 1.0*k_h. La hoja de ruta:719 prescribe literalmente "Sensibilidad (0, 0.5·k_h)": el codigo contradice a la fuente de verdad, no solo a su propio comentario. El archivo ya admite sensibilidades simbolicas (con test propio), asi que declarar el extremo en funcion de k_h era posible. Ningun modulo consume `parametros_sensibilizables()`, pero `reporte_criterios()` si imprime "Sensibilidad: (0.0, 0.5)".
**Regla:** criterios_adoptados.py:29-31: "el rango y el valor se defienden juntos en la memoria y no pueden contradecirse".
**Evidencia:**
```
$ python3 -c "...PGA * F_pga * factor_muro..."
PGA=0.5 F_pga=1.0 factor_muro=1.0 -> k_h=0.5 | 0.5*k_h = 0.25
sensibilidad k_v declarada = (0.0, 0.5) | extremo superior / k_h = 1.0
$ sed -n '496p' src/criterios_adoptados.py
        sensibilidad=(0.0, 0.5),   # 0.5*k_h como escenario alterno
$ grep -rn "k_v" docs/hoja_de_ruta_alcantarillas_v8.md
719:| k_v = 0 | [A] | Sensibilidad (0, 0.5·k_h) |
```
**Nota de evidencia:** el auditor cito las lineas 495 (es 496) y M9:326 (es 327).
**Verificacion:** Lente 1 rehizo el calculo y corrigio las dos ubicaciones; lente 2 hallo que la hoja de ruta prescribe lo contrario del codigo.

### D-05 -- `angulo_aletas` es el unico vacio sin `reemplazado_por` ni fuente PENDIENTE
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:1325-1331; src/modulos/M11_reporte.py:1126
M11 emite `_td(_esc(c.reemplazado_por or c.fuente))` en la columna "Que lo resuelve" de la tabla de criterios sin valor, de modo que la memoria dice que lo que resuelve este vacio es "Practica corriente; no fijado por el Manual" -- el enunciado del vacio. Es FALSO que sean cuatro campos fallados: el archivo exime deliberadamente de sensibilidad a los criterios vacios (12 de 22 `[A]` sin valor tampoco la declaran). El criterio no lo lee ningun modulo y sigue apareciendo en `criterios_sin_valor()`.
**Regla:** Claude.md, taxonomia `[A]`; la guardia solo exige `reemplazado_por` junto a `vacio_verificado`.
**Evidencia:**
```
$ python3 -c "c=ca.criterio('angulo_aletas'); ..."
etiqueta A | valor None | sens None | reemp None | vpdte None
fuente 'Practica corriente; no fijado por el Manual'
M11 columna Que-lo-resuelve -> 'Practica corriente; no fijado por el Manual'
$ sed -n '1126p' src/modulos/M11_reporte.py
                _td(_esc(c.reemplazado_por or c.fuente))]))
$ python3 (barrido de los 22 [A] vacios): angulo_aletas es el unico sin reemp y sin fuente PENDIENTE
```
**Verificacion:** Lente 1 reprodujo al caracter y barrio los 22 hermanos, refutando el argumento de los cuatro campos; lente 2 hallo el vacio registrado en la auditoria v9:744 pero no la declaracion incompleta (GRAVE -> MENOR).

### D-06 -- `Z_E030` hereda la trazabilidad pero no la verificacion abierta
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/datos_sitio.py:194-216,261-264; cli.py:1128
datos_sitio.py:205-207 declara que la lectura "hereda su misma trazabilidad" de `ZONA_SISMICA_LA_UNION`, cuya `verificacion_pendiente` exige contrastar el Anexo II de E.030 antes de citar el valor; `Z_E030` no declara ninguna. La consecuencia sobre la memoria impresa es FALSA: `Z_E030` no lo invoca ningun modulo, cli.py ni la GUI, y tanto `reporte_datos_sitio` como el aviso de M11:1013 iteran solo claves usadas. El efecto real es de export: `datos_con_verificacion_pendiente()` recorre todo el dict y `trazabilidad_incompleta` del JSON omite `Z_E030`.
**Regla:** Claude.md, `[S]`: "declara trazabilidad obligatoria: el procedimiento exacto, la fuente."
**Evidencia:**
```
$ python3 -c "...ds.datos_con_verificacion_pendiente(); ds.dato('Z_E030').verificacion_pendiente..."
con_verificacion_pendiente: ['PGA_roca_B', 'ZONA_SISMICA_LA_UNION']
Z_E030.verificacion_pendiente = None
$ grep -rn "Z_E030|ZONA_SISMICA_LA_UNION" --include=*.py . | grep -v src/datos_sitio.py
constantes_normativas.py:337-338 (comentarios de mudanza) + solo tests
$ sed -n '1013p' src/modulos/M11_reporte.py
    con_pendiente = [k for k in claves if ds.dato(k).verificacion_pendiente]   # claves = usadas
```
**Verificacion:** Lente 1 reprodujo la salida (que depende de que el propio comando inyecte `ds.valor('Z_E030')`); lente 2 hallo el no-uso documentado en datos_sitio.py:159-165, que anula la consecuencia sobre la memoria (GRAVE -> MENOR).

### D-07 -- `criterios_adoptados` no expone el homologo de `datos_con_verificacion_pendiente()`
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/datos_sitio.py:261-264; cli.py:1120-1140; src/criterios_adoptados.py:85
Las dos dataclasses comparten el campo `verificacion_pendiente` y hoy 10 criterios CON valor lo tienen abierto. `datos_sitio` expone la funcion y cli.py la vuelca al JSON como `trazabilidad_incompleta`; el bloque `criterios` no lleva ese campo. Un consumidor del informe.json ve que datos de sitio estan sin cerrar documentalmente y no ve que criterios lo estan. El HTML si los imprime (M11:1069-1075), asi que la asimetria es de API y de export.
**Regla:** datos_sitio.py:266-270 declara `reporte_datos_sitio` "hermano de `criterios_adoptados.reporte_criterios`"; la hermandad se rompe en el campo que ambos comparten.
**Evidencia:**
```
$ python3 -c "print([n for n in dir(ds) if 'verificacion' in n]); print([n for n in dir(ca) if 'verificacion' in n])"
ds: ['datos_con_verificacion_pendiente']   |   ca: []
criterios con valor y verificacion abierta: ['PERFIL_SUELO_PRESUNTO','clase_sitio','hds5_embocadura_hdpe',
 'metodo_transicion_hds5','n_manning_hdpe','geometria_control_salida','diametros_normalizados',
 'h_relleno_min_concreto_tmc','factores_carga_aashto','recubrimiento_aashto_mm']
$ grep -n "trazabilidad_incompleta\|sin_valor_declarados" cli.py
1127 / 1128 (bloque datos_sitio) / 1134 (bloque criterios, sin campo equivalente)
```
**Verificacion:** Lente 1 reprodujo la salida exacta y verifico las lineas del JSON; lente 2 no hallo ninguna nota que declare la asimetria deliberada.

### D-08 -- `clase_sitio` es `[A]` con valor y sin sensibilidad
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** CONFIRMADO - **Detectado desde 2 dimensiones** (C2, D1) - **Ubicacion** src/criterios_adoptados.py:386-457
Es el unico de los 30 `[A]` con valor declarado y `sensibilidad=None`. `_verificar_criterio` solo exige sensibilidad a los `opcional=True` y `_verificar_sensibilidad` retorna de inmediato cuando es None, asi que nada frena la omision, y no hay test que la fije. Su propia justificacion reconoce que la adopcion "no es conservadora por construccion", que es exactamente el caso en que el rango hace falta; el archivo admite sensibilidades simbolicas, con test, asi que el valor categorico no lo impedia.
**Regla:** Claude.md:28 y src/criterios_adoptados.py:50: "[A] Sin norma ni fuente unica. Adopcion declarada + sensibilidad obligatoria."
**Evidencia:**
```
$ python3 -c "[k for k,c in CRITERIOS.items() if c.etiqueta=='A' and c.valor is not None and c.sensibilidad is None]"
['clase_sitio']
A 'F_con_factores_tabulados_por_adopcion' sensibilidad= None
$ sed -n '1830,1834p' src/criterios_adoptados.py
    if c.opcional: ... raise ValueError(f"'{clave}' es opcional y no declara sensibilidad...")
$ sed -n '1748,1750p' src/criterios_adoptados.py
    if rango is None: return          # simbolica: declarada, respetada, no evaluada
```
**Verificacion:** Lente 1 reprodujo el filtro en las dos pasadas y verifico que la guardia no cubre el caso; lente 2 busco la excepcion en Claude.md, los dos manifiestos, la hoja de ruta y los tests: no existe.

### D-09 -- `datos_sitio.py` no tiene guardia al importar
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/datos_sitio.py:97-118; src/criterios_adoptados.py:1787-1878
`DatoSitio(trazabilidad='', etiqueta='A')` se construye sin error mientras `ca._verificar_criterio` rechaza el equivalente; el unico privado del modulo es `_USADOS`. Atenuantes: el manifiesto declara los tests como mecanismo de aplicacion legitimo del proyecto y los pone en la misma tabla que la guardia de import; `datos_sitio.py` no tiene API de escritura dinamica (la unica via de violacion es editar el archivo, cubierta por tests) y hoy los tres datos declaran `[S]` con trazabilidad no vacia.
**Regla:** Claude.md, `[S]`: "En vez de sensibilidad declara trazabilidad obligatoria." datos_sitio.py:14-19 la enuncia con las mismas palabras y no la hace cumplir.
**Evidencia:**
```
$ python3 -c "d=ds.DatoSitio(valor=1.0,...,trazabilidad='',etiqueta='A'); ..."
datos_sitio ACEPTA trazabilidad='' etiqueta='A'
criterios_adoptados RECHAZA: 'x' es [S] y no declara trazabilidad. ...
guardias en datos_sitio: []     (todos los _ del modulo: ['_USADOS'])
$ sed -n '186,196p' docs/manifiesto_datos_proyecto_vs_constantes.md
Este documento describe una decisión; los tests la sostienen. ...
| tests/... | criterios_adoptados._coherencia_de_etiquetas() (al importar) | tests/test_datos_sitio.py |
```
**Verificacion:** Lente 1 reprodujo los tres asertos; lente 2 hallo el modelo de aplicacion declarado que desarma el reproche "una prueba, no la arquitectura" (GRAVE -> MENOR).

### D-10 -- M2 lee cuatro criterios no opcionales con `valor_si_declarado()`
**Sev** MENOR - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Detectado desde 2 dimensiones** (D1, D2) - **Ubicacion** src/modulos/M2_material.py:271,277,282; src/criterios_adoptados.py:19
No hay relleno silencioso: la decision esta documentada bajo el titulo "Vacios que el catalogo deja en None, a proposito", `modelos.py` declara los campos `Optional`, y el vacio detiene el calculo en el punto de uso (M7:266-270, M5:270), lo que se comprueba vaciando los criterios. Residuo real: el docstring dice que `catalogo()` "llama a `criterio()`" cuando llama a `valor_si_declarado()`, y `n_manning_hdpe` -- el unico que nunca se lee con `valor()` en todo src/ -- no figura en la decision escrita: si se vaciara, el resultado es `TypeError`, no `CriterioPendienteError`.
**Regla:** criterios_adoptados.py:19-23: "La UNICA excepcion son los criterios marcados opcional=True ... Se leen con valor_si_declarado(), nunca con valor()."
**Evidencia:**
```
$ grep -n "_valor_si_declarado(CRITERIO" src/modulos/M2_material.py
271: n_min, n_max = _valor_si_declarado(CRITERIO_N_MANNING_HDPE)
277: h_relleno_min = _valor_si_declarado(CRITERIO_H_RELLENO_CONCRETO_TMC)
282: v_max_rango = _valor_si_declarado(CRITERIO_V_MAX[tipo])
$ python3 -c "...opcional=True en TODO el archivo..."  -> ['v_max_concreto_eleccion']
$ python3 (vaciando criterios y llamando al catalogo)
HDPE con n vacio -> TypeError cannot unpack non-iterable NoneType object
M7 con h_relleno vacio -> CriterioPendienteError
```
**Verificacion:** Lente 1 reprodujo los tres comandos y probo los consumidores; lente 2 leyo tambien el docstring de `_valor_si_declarado` (M2:187-207), que documenta la migracion (GRAVE -> MENOR).

### D-11 -- `n_manning_hdpe` es un valor normativo por analogia etiquetado `[A]`
**Sev** MENOR - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:732,742
El valor (0.010, 0.013) es identico a `MANNING['concreto_recto']` y la fuente dice "Analogia a Tabla N 09 (concreto, tubo recto)"; los unicos `[N->]` reales son `resguardo_HW_subrasante` y `h_relleno_min_concreto_tmc`, que son casos identicos. La etiqueta no altera ningun numero: cambia como lo presenta M11 y con que pregunta lo audita el revisor. Punto util que sobrevive: el valor duplica el literal del concreto sin ninguna guardia que ligue los dos.
**Regla:** hoja de ruta:40, regla de coherencia: "Un criterio justificado invocando una disposicion normativa no puede etiquetarse `[A]`", frente a la propia hoja de ruta, que escribe `[A]` para este criterio en cuatro lineas.
**Evidencia:**
```
$ python3 -c "...MANNING['concreto_recto'], CRITERIOS['n_manning_hdpe']..."
MANNING[concreto_recto] = (0.01, 0.013)
n_manning_hdpe valor = (0.01, 0.013)  etiqueta= A
fuente: Analogia a Tabla N 09 (concreto, tubo recto)
N-> reales: ['resguardo_HW_subrasante', 'h_relleno_min_concreto_tmc']
$ sed -n '40p' docs/hoja_de_ruta_alcantarillas_v8.md
**Regla de coherencia:** ... no puede etiquetarse `[A]`. ...
```
**Verificacion:** Lente 1 reprodujo valores y etiquetas; lente 2 hallo `[A]` escrito en cuatro sitios de la hoja de ruta y en el manifiesto (GRAVE -> MENOR: inconsistencia entre dos reglas escritas, sin efecto de calculo).

### D-12 -- `v_max_hdpe` y `v_max_tmc` no llevan ancla `vacio_verificado`
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:749-772; docs/manifiesto_citas.md:590-593
El unico criterio anclado del archivo es `h_relleno_min_concreto_tmc`, y §14 anuncia consolidar "las filas marcadas Afirmacion negativa" (nueve) entregando solo 14.a. La premisa del hallazgo es FALSA: si existe seccion a la que apuntar -- ejecute la guardia y `_verificar_ancla_de_vacio('v_max_hdpe','manifiesto_citas.md Sec. 10-bis')` resuelve. El obstaculo real es menor: la guardia exige ademas `reemplazado_por`, que los dos tienen en None. Y el manifiesto trata a estos dos como "cita cerrada", caso distinto del dossier de vacio agotado.
**Regla:** criterios_adoptados.py:93-102 (comentario del campo); ninguna obliga a que todo `[C]` con afirmacion negativa lleve ancla.
**Evidencia:**
```
$ python3 -c "...[k for k,v in C.items() if v.vacio_verificado]"
['h_relleno_min_concreto_tmc']
$ python3 -c "ca._secciones_de('manifiesto_citas.md') ..."
['1','10','10-bis','11','12','13','14','14.a', ...]   -> ANCLA a 10-bis RESUELVE OK
$ python3 -c "v_max_hdpe | reemplazado_por= None | vacio_verificado= ''"
$ grep -n "cita cerrada" docs/manifiesto_citas.md -> 400 (v_max_hdpe), 401 (v_max_tmc)
```
**Verificacion:** Lente 1 ejecuto la propia guardia del repo y derribo la premisa del hallazgo; lente 2 hallo el tratamiento diferenciado en el manifiesto (MENOR -> OBSERVACION).

### D-13 -- `clases_producto_por_relleno` es el unico `[C]` con `valor=None`
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:1187-1214
Su fuente empieza por "PENDIENTE". El estado esta registrado en los dos documentos donde un revisor lo buscaria: la auditoria v9 lo nombra tres veces (624-627, 656, 754) y dice que "quedan declarados `[A]`/`[C]` pendientes, sin bloquear nada", y el manifiesto lo tabula como `[C]` "sin extraer". Hay precedente interno: `v_max_tmc`/`v_max_hdpe` fueron `[C]` vacios y hoy valen 4.6. Lo que no esta escrito es el criterio general de eleccion entre `[A]` y `[C]` para un hueco abierto.
**Regla:** Claude.md: "[C] Vacio normativo cubierto con fuente tecnica reconocida"; la guardia no cubre este caso.
**Evidencia:**
```
$ python3 -c "[k for k,c in CRITERIOS.items() if c.etiqueta=='C' and c.valor is None]"
['clases_producto_por_relleno']   etiqueta C | valor None
fuente: PENDIENTE - AASHTO M-170M (clases I-V, concreto); ASTM A-807
$ sed -n '624,627p' docs/auditoria_y_ruta_despliegue_v9.md
**Quedan 3 sin cerrar...** `clases_producto_por_relleno` ... quedan declarados
`[A]`/`[C]` pendientes, sin bloquear nada ...
$ grep -n clases_producto_por_relleno docs/manifiesto_citas.md -> 322 (**sin extraer** ... [C])
```
**Verificacion:** Lente 1 reprodujo el filtro; lente 2 hallo el registro en tres lugares de la auditoria v9 y en el manifiesto (MENOR -> OBSERVACION, reclasificado a documentado).

### E-01 -- gui/app.py:749 disfraza un fallo de programa como problema del expediente
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** gui/app.py:749,755; cli.py:1465; src/modulos/MD.py:329-330
El manejador de EJECUTAR captura `except (OSError, ValueError)` ANTES del brazo que imprime traza. Cualquier ValueError nacido dentro del pipeline (MD:302, M5:338, M11:319/344/480/1396) escapa de `cli.correr` sin ser capturado por `_etapa` (que solo atrapa `ErrorProyecto`) y aterriza en ese primer brazo: la GUI lo muestra como "No se pudo leer la entrada", sin traza. El brazo es mas ancho de lo necesario: lo unico a atrapar era `json.JSONDecodeError`, y asi lo hacen bien cli.py:1465 y el propio gui/app.py:936.
**Regla:** Claude.md, Excepciones: "Todas descienden de ErrorProyecto ... para que la GUI distinga un problema del expediente de un fallo del programa con un solo except." MD:329-330 escribe la regla opuesta: "un ValueError o un ImportError es un fallo de programa y sube sin anotarse".
**Evidencia:**
```
$ PYTHONPATH=src:. python3 -c "...monkeypatch M5.v1_borde_libre -> ValueError; cli.correr(...)"
ESCAPA DE cli.correr -> ValueError | ErrorProyecto? False | lo atrapa el brazo (OSError,ValueError)? True
JSONDecodeError es ValueError: True
$ sed -n '748,757p' gui/app.py
        except (OSError, ValueError) as exc:
            self._mostrar_error_entrada(f"No se pudo leer la entrada:\n{exc}")
        except ErrorProyecto as exc: ...
        except Exception as exc:  # fallo de programa: se muestra con traza
$ grep -n "except (OSError, json.JSONDecodeError)" cli.py gui/app.py
cli.py:1465 | gui/app.py:936
```
**Verificacion:** Lente 1 reprodujo la fuga del ValueError y el sed literal; lente 2 no hallo documentacion que respalde el brazo ancho, solo la regla contraria en MD (la cita del auditor estaba en 330, no 325).

### E-02 -- M9 usa `DatoInvalidoError` para validar argumentos internos
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M9_cabezal.py:852,876,1163,1257
Cuatro sitios validan strings que produce el propio codigo (`nombre`, `verificacion`, `condicion`, `direccion`) y ahi `DatoInvalidoError` disfraza un fallo de programa de problema del expediente. El quinto (M9:1180) NO pertenece a la lista: su tabla sale de `ca.valor(CRITERIO_RECUBRIMIENTO_AASHTO)`, es decir del expediente. Consecuencia hoy nula: cli.py:844 y :851 iteran las mismas tablas que se validan y M9:892 pasa claves literales. La eleccion es deliberada y esta fijada por tests, pero no escrita.
**Regla:** Claude.md, Excepciones; la regla explicita del propio proyecto esta en src/modulos/M8_estructural.py:276-281.
**Evidencia:**
```
$ PYTHONPATH=src:. python3 -c "cli._etapa(..., M9.recubrimiento_de_diseno(condicion='no_existe'))"
devuelve: None
bloqueo registrado: DatoInvalidoError | Dato invalido en 'condicion': no es una fila del Art. 7.7.1 ...
$ awk 'NR>=844 && NR<=854' cli.py
844:    for condicion in RECUBRIMIENTO:      <- itera la MISMA tabla que valida
851:    for direccion in CUANTIA_MIN_MURO:   <- idem
$ awk 'NR>=1178 && NR<=1180' src/modulos/M9_cabezal.py
    tabla = ca.valor(CRITERIO_RECUBRIMIENTO_AASHTO)   <- la tabla es del EXPEDIENTE
$ grep -rn "argumento interno|contrato interno" src/modulos/M9_cabezal.py docs/*.md -> (nada)
```
**Verificacion:** Lente 1 reprodujo el bloqueo y busco los llamadores, que el auditor no reviso; lente 2 no hallo prosa que lo justifique pero si tests que lo fijan por nombre (GRAVE -> MENOR).

### E-03 -- Los tres exportadores de la GUI capturan `except Exception` sin traza
**Sev** OBSERVACION - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:868,883,899
Los tres manejadores no llaman `traceback.print_exc()`, a diferencia del patron hermano de la linea 755, y no declaran por que. Dos matices: el messagebox si imprime `type(exc).__name__`, de modo que lo que se pierde es la traza y el punto exacto, no la distincion; y un manejador de tope de un boton de exportacion no es logica de negocio (el mismo archivo usa `except Exception` en :188 para el fallback de estilo).
**Regla:** Claude.md, Excepciones: "No usar Exception generica" y el patron correcto ya presente en gui/app.py:749-757.
**Evidencia:**
```
$ grep -n "except Exception" -A2 gui/app.py
755:        except Exception as exc:  # fallo de programa: se muestra con traza
756-            traceback.print_exc()
868/883/899:  except Exception as exc:
              messagebox.showerror("Error al exportar", f"{type(exc).__name__}: {exc}")
$ awk 'NR>=865 && NR<=869' gui/app.py   -> el try cubre solo cli.exportar_* + showinfo
```
**Verificacion:** Lente 1 reprodujo el grep identico y leyo el cuerpo de los tres exportadores; lente 2 no hallo documentacion ni a favor ni en contra (MENOR -> OBSERVACION).

### E-04 -- gui/app.py:494 valida un dato tecleado con ValueError
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** gui/app.py:494 y sus consumidores gui/app.py:511 y :538
Es el unico `raise` del archivo y no sale de la clase de la GUI: se atrapa a tres lineas en ambos llamadores y funciona como senal de control interna. El brazo de la linea 497 NO lo consume -- esta dentro de la misma funcion y cubre solo el `float()`, y no puede alcanzarlo porque el raise ocurre antes del try. El valor vacio de un widget Tk no es todavia un dato de entrada del expediente. La funcion no tiene docstring donde dejar constancia.
**Regla:** Claude.md, Excepciones: "si el revisor tiene que anadir algo es Faltante" -- acotada a los datos de entrada del CSV.
**Evidencia:**
```
$ awk 'NR>=491 && NR<=498' gui/app.py
    def _interpretar_valor_declarado(self, texto):
        if texto == "": raise ValueError("El valor no puede quedar vacio.")
        try: return float(texto.replace(",", "."))
        except ValueError: return texto      # <- fallback de float, no consumidor del raise
$ grep -n "raise " gui/app.py  -> 494 (unico)
$ awk 'NR==511; NR==538' gui/app.py -> los dos consumidores reales
```
**Verificacion:** Lente 1 reprodujo sed y grep y corrigio la lectura del brazo 497; lente 2 no hallo linea que lo justifique (MENOR -> OBSERVACION).

### E-05 -- Declarar un criterio desde la GUI con valor fuera de rango sale como ValueError
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:144-173,1780,1809,1815; gui/app.py:510-511
El rechazo sale como `ValueError`/`KeyError`, fuera de `ErrorProyecto`. La afirmacion de que "en ningun sitio se argumenta" es falsa: el docstring de `_verificar_criterio` (1793-1804) enumera los TRES caminos que la atraviesan -- incluido "declaracion en caliente `establecer_valor_dinamico()`" -- y declara la funcion "una guardia de arquitectura, no una validacion de dato"; el docstring del propio `establecer_valor_dinamico` lo repite. Ningun valor no declarado entra al calculo: la guardia lo impide.
**Regla:** Claude.md, Excepciones: "DatoInvalidoError: el dato esta pero no puede ser."
**Evidencia:**
```
$ PYTHONPATH=src python3 -c "ca.establecer_valor_dinamico('F_pga', 99999.0)"
TIPO: ValueError | es ErrorProyecto? False
MSG: 'F_pga' tiene el valor 99999.0 fuera del rango de sensibilidad que el mismo declara, (0.9, 1.0) ...
$ awk 'NR>=1793 && NR<=1804' src/criterios_adoptados.py
    atraviesan los TRES caminos ... declaracion en caliente `establecer_valor_dinamico()` ...
    Es una guardia de arquitectura, no una validacion de dato ...
```
**Nota de evidencia:** el auditor ubico `establecer_valor_dinamico` en la linea 1166; esa linea es el campo `vacio_verificado` de un criterio. La funcion vive en 144-173.
**Verificacion:** Lente 1 reprodujo la salida y corrigio la ubicacion; lente 2 hallo la decision escrita en el docstring de la funcion que lanza (GRAVE -> OBSERVACION).

### E-06 -- `modelos.py` ensancha el contrato de `DatoFaltanteError` respecto de Claude.md
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** CONFIRMADO - **Ubicacion** src/modelos.py:108-109; src/modulos/M5_verificaciones.py:409-415; cli.py:511-515
Claude.md define la excepcion como "falta un dato de entrada del CSV ... Lleva el nombre de la columna"; modelos.py la redefine como "del CSV (Sec. 1.2) **o de un tablero externo**" y el codigo lo explota: M5:410 pasa `campo="ancho_derecho_via_m"`, que su propio detalle admite que "no es columna de Sec. 1.2", y `cli._falta_dato` la fabrica para datos de `--datos-externos`. Consecuencia: el campo `campo` del JSON no siempre nombra una columna del CSV.
**Regla:** Claude.md:95-96, no actualizado. La decision si esta en el docstring de la clase y en el de `v5_remanso`.
**Evidencia:**
```
$ awk 'NR>=108 && NR<=109' src/modelos.py
class DatoFaltanteError(ErrorProyecto):
    """Falta un dato de entrada del CSV (Sec. 1.2) o de un tablero externo."""
$ awk 'NR>=409 && NR<=415' src/modulos/M5_verificaciones.py
    raise DatoFaltanteError("ancho_derecho_via_m", ... "(no es columna de Sec. 1.2)" ...
$ grep -n "DatoFaltanteError" -A2 Claude.md
95:- DatoFaltanteError: falta un dato de entrada del CSV. Falta la **columna** ...
```
**Nota de evidencia:** `cli._falta_dato` esta en 511-515, no en 513-517.
**Verificacion:** Lente 1 reprodujo el ensanche y corrigio el rango; lente 2 confirmo que la decision esta declarada y que lo que falta es la actualizacion de la constitucion.

### F-01 -- gui/app.py: 584 sentencias ejecutables con CERO tests
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** gui/app.py:1-958 (logica sin cubrir en :491, :532, :707, :748); Claude.md:122
Ningun test importa gui/app.py, de modo que la cobertura real del repositorio es 69 % de las sentencias, no 96 %. La GUI no es un envoltorio inerte: decide el tipo del valor declarado (`_interpretar_valor_declarado`), traduce banderas a mano (`l_hidraulico` -> `L_hidraulico_m`) y llama `cli.correr(ruta_csv, externos)` con dos argumentos, de modo que nunca puede producir el entregable de "perfil". Agravante verificado: el bucle de banderas de `cargar_datos_externos` no pasa por `_exige_clave`, asi que una clave desincronizada entra y el dato se pierde en silencio.
**Regla:** Claude.md:122: "pytest en tests/. Minimo un test por modulo." Ninguna linea de Claude.md ni de docs/ exime a gui/.
**Evidencia:**
```
$ python3 -c "PythonParser(filename='gui/app.py') ..." -> 584 sentencias ejecutables
$ grep -rIl 'from gui\|import gui\|gui\.app' tests/*.py conftest.py || echo '(ninguno)'
(ningun test importa gui/app.py)
$ grep -n 'cli.correr(' gui/app.py -> 748:  cli.correr(ruta_csv, externos)
$ sed -n '886,887p' cli.py -> def correr(ruta_csv, externos, alcance=ALCANCE_EXPEDIENTE)
$ python3 -c "cli.cargar_datos_externos(None,{'l_hidraulico':'5.0'}).globales"
{'l_hidraulico': DatoDeclarado(...)}   -> clave desconocida aceptada sin _exige_clave
```
**Verificacion:** Lente 1 reprodujo el conteo, la ausencia de tests y la llamada sin alcance; lente 2 no hallo exencion escrita en Claude.md, la hoja de ruta ni la auditoria v9.

### F-02 -- La rama que SI escribe el archivo fuente de los criterios no tiene ningun test
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/criterios_adoptados.py:277-321 (299-320 sin cubrir); tests/test_criterios_adoptados.py:461-475; gui/app.py:555
`escribir_valor_en_archivo` es la unica ruta que muta permanentemente la fuente de verdad y la dispara el boton "Guardar en archivo". El unico test comprueba el rechazo previo. Todo lo posterior a la guardia queda sin ejecutar: lectura del archivo, sustitucion por regex del bloque `valor=`, el ValueError de "no se encontro el bloque", la escritura, la actualizacion en memoria de `CRITERIOS[clave]` y el retiro del override.
**Regla:** Claude.md:122 leido con Claude.md:9-12 ("Rellenar un vacio en silencio es el peor error posible"): nada en docs/ declara esta rama como no verificable.
**Evidencia:**
```
$ python3 -m coverage run -m pytest -q; python3 -m coverage report -m --include="src/criterios_adoptados.py"
src/criterios_adoptados.py  218  31  86%   162, 228, 291, 299-320, 1669, ...
$ grep -rIn "escribir_valor_en_archivo" tests/*.py gui/app.py
tests/test_criterios_adoptados.py:471 (test del rechazo) | gui/app.py:555
$ awk 'NR>=299&&NR<=320' src/criterios_adoptados.py
    ruta_archivo = ruta or __file__ ; texto = Path(...).read_text(...) ; ... write_text ...
$ grep -rn 'escribir_valor_en_archivo' docs/   -> (sin coincidencias)
```
**Verificacion:** Lente 1 reprodujo la linea de cobertura y mapeo 299-320 al cuerpo posterior a la guardia; lente 2 leyo el docstring completo, que no declara nada como no verificable.

### F-03 -- CP-1: los TR dorados del fixture no salen de la formula que el propio fixture declara
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** tests/fixtures/casos_patron.py:41,48; src/modulos/M1_clasificacion.py:207
CP-1 declara TR = 1/(1-(1-R)^(1/n)) y da 70.63 y 35.29; la formula da 70.59302 y 35.32272. Los errores (0.037 y 0.033) quedan justo por debajo de la tolerancia declarada (0.05), de modo que los dos tests pasan sin que nadie vea la discrepancia. El modulo bajo prueba escribe los valores correctos en su docstring. El 70.63 no aparece en docs/ ni en la hoja de ruta: no es un valor tomado de la fuente, es un dorado mal calculado.
**Regla:** el encabezado del fixture (casos_patron.py:16-20): "Todos los valores numericos fueron verificados con scipy.optimize.brentq de forma independiente ... si un test contra estos valores falla, el error esta en el modulo bajo prueba, no en el fixture."
**Evidencia:**
```
$ python3 -c "from tests.fixtures.casos_patron import CP1_PERIODO_RETORNO as C; ..."
R=0.3  n=25  fixture=70.63  formula=70.59302  error=0.03698  tolerancia=0.05
R=0.35 n=15  fixture=35.29  formula=35.32272  error=0.03272  tolerancia=0.05
$ awk 'NR>=206 && NR<=208' src/modulos/M1_clasificacion.py
    publica 71 y 35, que son 70.59 y 35.32 redondeados.
$ grep -rn "70\.63|35\.29" docs/ Claude.md   -> (ninguna aparicion)
```
**Verificacion:** Lente 1 recalculo con la formula del fixture y verifico los dos consumidores (`abs=caso['tolerancia']`); lente 2 confirmo que el valor no sale de la fuente de verdad y que el encabezado afirma lo contrario.

### F-04 -- Mononobe-Okabe: el caso limite de Rankine no cubre las convenciones de beta, i y delta
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M9_cabezal.py:442-443,462,463,490,493,494; tests/test_M9_cabezal.py:213-221
Con i = beta = delta = 0 los cuatro cosenos son insensibles al signo: mutar `cos(i - beta)` a `cos(i + beta)` deja la suite en 725 passed, y sobreviven siete mutantes con impacto de calculo. Es documentacion que afirma lo que el codigo no da, por partida doble: M9:442-443 dice "Es la comprobacion que garantiza que los signos estan bien puestos" y el docstring del test dice "Si un signo esta cambiado, aqui se ve". El unico test con angulo no nulo (i=5) es de excepcion.
**Regla:** Claude.md:123: "Todo modulo de calculo se contrasta contra tests/fixtures/casos_patron.py"; no existe caso patron de Mononobe-Okabe con angulos no nulos.
**Evidencia:**
```
$ (copia limpia) sed -i '463s|math.cos(i - beta)|math.cos(i + beta)|' src/modulos/M9_cabezal.py
$ python3 -m pytest -q --no-header | tail -1
725 passed, 1 skipped in 3.36s
$ (barrido) SOBREVIVEN: 462 '+'->'-' (x2), 463 '-'->'+', 490 '*'->'/', 493 '-'->'+', 494 '*'->'/' (x2)
   (470-471 tambien sobreviven pero son f-strings del mensaje de error)
$ python3 -c "k_ae_mononobe_okabe(phi=30,i=5,beta=0,delta=0,k_h=0.5,k_v=0)"
DisenoNoFactibleError  # el unico i!=0 de la suite es de excepcion
```
**Verificacion:** Lente 1 reprodujo la mutacion y separo los tres mutantes cosmeticos de los siete con impacto; lente 2 verifico que `k_ae_del_proyecto()` se detiene hoy con los cuatro angulos en None (BLOQUEANTE -> GRAVE).

### F-05 -- `empuje_activo_sismico_total` sin ningun test de valor: 4/4 mutantes sobreviven
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M9_cabezal.py:629; tests/test_M9_cabezal.py:361-372
`(1-k_v)` -> `(1+k_v)` y `/2` -> `*2` dejan la suite en 725 passed. El unico assert (`incremento == approx(P_AE - P_A)`) es tautologico porque `incremento_sismico` (M9:639-640) llama a la misma funcion. Agravante: el test invoca con `k_v = 0.0`, de modo que el mutante del `(1-k_v)` es indetectable por construccion. La funcion solo la consume `empujes_trasdos`, que la CLI no ensambla.
**Regla:** Claude.md:123. No hay caso patron de P_AE (CP-7 cubre la cadena sismica, no el empuje).
**Evidencia:**
```
$ (copia) sed -i '629s|(1 - k_v)|(1 + k_v)|' src/modulos/M9_cabezal.py && pytest -q | tail -1
    return gamma_relleno * H ** 2 * (1 + k_v) * K_AE / 2
725 passed, 1 skipped in 3.19s
$ (copia) sed -i '629s|K_AE / 2|K_AE * 2|' -> 725 passed, 1 skipped
$ sed -n '361,372p' tests/test_M9_cabezal.py
    mo = empuje_mononobe_okabe(..., k_h=0.50, k_v=0.0)
    assert incremento == pytest.approx(P_AE - P_A)     # tautologia
```
**Verificacion:** Lente 1 reprodujo los dos mutantes y trazo la tautologia hasta M9:639; lente 2 no hallo nota que difiera el contraste.

### F-06 -- E3 deslizamiento: ningun test asserta el FS
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M9_cabezal.py:958,961; tests/test_M9_cabezal.py:554-560
`fuerza_resistente * fuerza_actuante` en lugar de la division deja 725 passed, e invertir la guarda de la linea 958 (que hace `fs = math.inf` siempre) tambien. `verificar_deslizamiento` si se ejercita en cuatro tests (directo y via `verificar_estabilidad`), pero ninguno asserta el `valor_obtenido`: los asserts son de numeral, de codigo y de `cumple`. El test hermano de capacidad portante si asserta 3.10.
**Regla:** Claude.md:122-123: el assert es de existencia/booleano donde debia ser de valor, y fija como correcto un FS calculado con el operador equivocado.
**Evidencia:**
```
$ (copia) sed -i '961s|fuerza_resistente / fuerza_actuante|fuerza_resistente * fuerza_actuante|' && pytest -q|tail -1
            fs = fuerza_resistente * fuerza_actuante
725 passed, 1 skipped in 3.35s
$ (copia) sed -i '958s|<= 0|> 0|'  -> 725 passed, 1 skipped
$ sed -n '556,565p' tests/test_M9_cabezal.py
    v = verificar_deslizamiento(fuerza_resistente=90.0, fuerza_actuante=50.0, ...)
    assert v.criterio_aplicado is None / assert "39.13.6 a" in v.numeral / assert v.cumple ...
563: def test_capacidad_portante_es_q_ultima_sobre_q_actuante(): assert v.valor_obtenido == approx(3.10)
```
**Verificacion:** Lente 1 reprodujo los dos mutantes y encontro los tres consumidores adicionales que el auditor no vio; lente 2 confirmo que ninguno asserta valor y que la cadena E1-E5 no la ensambla la CLI.

### F-07 -- Empuje total y momento volcante del cabezal sin test de valor
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modelos.py:1099,1111-1115; tests/test_M9_cabezal.py:936-937,960-961
`EmpujesTrasdos.empuje_horizontal_total` y `.momento_volcante` sobreviven a `*`->`/` y `+`->`-` con la suite en 725 passed; los unicos asserts son dos comparaciones de orden. No alimentan ninguna memoria entregable hoy: ni cli.py ni gui/app.py importan `empujes_trasdos` ni `verificar_estabilidad`, la CLI declara por escrito que no ensambla E1-E5 y los cuatro criterios de angulo de Sec. 9.2 estan en None.
**Regla:** Claude.md:123. Nada en docs/ ni en los docstrings declara este ensamblado como diferido a efectos de prueba: `momento_volcante` se presenta como resultado vigente.
**Evidencia:**
```
$ (copia) sed -i '1111s|self.E_activo \* self.z_activo|self.E_activo / self.z_activo|' src/modelos.py && pytest -q|tail -1
        momento = (self.E_activo / self.z_activo
725 passed, 1 skipped in 3.17s
$ (copia) 1099 '+' -> '-'  -> 725 passed, 1 skipped
$ grep -rn "empuje_horizontal_total|momento_volcante" tests/
tests/test_M9_cabezal.py:936, :937 (comparaciones de orden), :960, :961 (argumentos)
$ python3 -c "...CRITERIOS[k].valor..." -> phi_relleno_trasdos None / ... / friccion_muro_suelo_delta None
```
**Verificacion:** Lente 1 reprodujo las dos mutaciones; lente 2 verifico que no hay consumidor en produccion y que cli.py:168-175 declara el no-ensamble (BLOQUEANTE -> GRAVE).

### F-08 -- Sec. 7.B: la rama viva de longitud del conducto no tiene assert de valor
**Sev** GRAVE - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** src/modulos/M7_geometria.py:442,454,532; tests/test_cli.py:285-291
Mutar `2 * talud` -> `2 / talud`, `ancho + proyeccion` -> `ancho - proyeccion` y la misma resta dentro de `compatibilidad_geometrica` deja la suite en 725 passed. El unico test que ejecuta la rama viva (con `talud_terraplen=1.5` declarado) asserta solo la cadena de procedencia. La linea 534 NO pertenece al hallazgo: mutarla rompe la suite, porque la rama con longitud DADA si tiene assert de valor (10.40). `talud_terraplen` esta hoy en None, pero en cuanto se declare la longitud entra a la memoria y se propaga a la friccion de M4 y a la caida S*L.
**Regla:** Claude.md:123; no hay caso patron de la Sec. 7.B.
**Evidencia:**
```
$ (copia) sed -i '454s|ancho_plataforma + proyeccion_taludes|ancho_plataforma - proyeccion_taludes|' && pytest -q|tail -1
725 passed, 1 skipped in 3.37s
$ (copia) 442 '2 * talud' -> '2 / talud'   -> 725 passed
$ (copia) 532 '+' -> '-'                   -> 725 passed
$ (copia) 534 '-' -> '+'                   -> 1 failed, 724 passed   <- 534 SI esta cubierta
$ sed -n '287,292p' tests/test_cli.py
    _declarar(monkeypatch, talud_terraplen=1.5) ... assert "M7.longitud_conducto" in ...origen
```
**Verificacion:** Lente 1 reprodujo los tres mutantes vivos y el cuarto que muere, corrigiendo la ubicacion; lente 2 verifico que los docstrings documentan la detencion por criterio vacio, no la ausencia de contraste.

### F-09 -- El cuadro resumen CSV (entregable 3) nunca se genera con un punto dimensionado
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M11_reporte.py:932-966 (947-950 y 962-963 sin cubrir); tests/test_M11_reporte.py:759-765
La rama de contenido (`if informe.dimensionado:` y el `else` de proteccion) nunca se ejecuta; el unico test comprueba que el archivo existe, la cabecera y el numero de lineas, sin comparar ninguna celda. No existe en Claude.md ni en docs/ ninguna regla de cobertura de ramas, y la auditoria v9:44 cuenta la exportacion entre lo terminado.
**Regla:** Claude.md:122 en su lectura util: el entregable tiene test, pero no de su contenido.
**Evidencia:**
```
$ python3 -m coverage report -m --include="src/modulos/M11_reporte.py"
src/modulos/M11_reporte.py  530  24  95%  ..., 947-950, 962-963, ...
$ awk 'NR>=946&&NR<=963' src/modulos/M11_reporte.py
946: if informe.dimensionado:   (cubierta)   947-955: cuerpo (947-950 sin cubrir)
959: if informe.proteccion is None: (cubierta)  962-963: rama else (sin cubrir)
$ sed -n '759,765p' tests/test_M11_reporte.py
    assert ruta.is_file() / assert lineas[0] == ",".join(M11.COLUMNAS_RESUMEN_CSV)
    assert len(lineas) == 1 + len(informe.puntos)
```
**Verificacion:** Lente 1 reprodujo la cobertura y mapeo las lineas; lente 2 confirmo que ningun documento declara el cuadro CSV como no verificado (GRAVE -> MENOR: no hay regla de cobertura de ramas escrita).

### F-10 -- Guardas de expediente sin cobertura en cuatro modulos y en cli.py
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** M1:165,310,389; M4:272,443; M5:495; M9:466,1180; cli.py:250,255,292,310 (+ MD:168,178)
Trece `raise` de ErrorProyecto no se ejecutan en ninguna corrida y no son inalcanzables: M4:443 (`geometria_control_salida` distinta de `seccion_llena`) es alcanzable desde la GUI, que acepta texto libre, y M9:466 (coseno del denominador nulo o negativo) se dispara con delta+beta+psi >= 90 -- lo verifique. Quedan tambien sin cubrir M1:389 (familia desconocida), M5:495 (clave a nivel de subrasante) y cuatro `DatoInvalidoError` del JSON de datos externos. Se excluyen los `AssertionError`, declarados en sus docstrings.
**Regla:** Claude.md:88-106: la taxonomia existe para que la GUI distinga; un `raise` sin test no garantiza que el tipo, el campo y el motivo sean los que la GUI espera.
**Evidencia:**
```
$ python3 -m coverage json ... && python3 -c "...raise sin cubrir..."
cli.py:250/255/292/310 | M0:233 | M1:165/310/389 | M4:272/443 | M5:495 | M9:466/1180 | MD:168/178
(+ dos ValueError: M11:1396, M5:338)
$ python3 -c "k_ae_mononobe_okabe(phi=30,i=0,beta=45,delta=45,k_h=0.5,k_v=0)"
DisenoNoFactibleError | Mononobe-Okabe fuera de su dominio ... delta+beta+psi = 116.57 ...
```
**Verificacion:** Lente 1 rehizo el barrido JSON con salida identica y probo la alcanzabilidad de M9:466; lente 2 confirmo que los `AssertionError` si estan declarados y estas guardas no.

### F-11 -- Seis banderas del CLI sin ninguna cobertura
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** cli.py:1411,1423,1430,1434,1437,1439 (cuerpos sin cubrir: 1368-1371, 1492-1495, 1498-1499)
Solo 8 de las 14 banderas aparecen en tests/test_cli.py. No se ejercitan `--pdf`, `--csv-resumen`, `--criterios`, `--datos-externos`, `--proyecto` ni `--plantilla`: el cableado bandera->funcion queda sin red, con una asimetria observable (`--pdf` pasa `ruta_plantilla` en 1494 y `--csv-resumen` no en 1498). Las funciones destino si estan probadas en test_M11_reporte.py.
**Regla:** Claude.md:122 sobre cli.py como modulo de entrega; docs/auditoria_y_ruta_despliegue_v9.md:16 y :782 presentan el CLI y la exportacion como terminados.
**Evidencia:**
```
$ grep -rIno -- '--[a-z-]\+' tests/test_cli.py | sort -u
--alcance --categoria-tr --html --json --l-hidraulico --longitud --luz --tw
$ grep -n 'add_argument("--' cli.py
1408 --json | 1411 --datos-externos | 1423 --criterios | 1427 --html | 1430 --pdf
1434 --csv-resumen | 1437 --proyecto | 1439 --plantilla | 1444 --alcance
$ python3 -m coverage report -m --include="cli.py"
cli.py  582  24  96%  ..., 1368-1371, 1492-1495, 1498-1499, 1505
```
**Nota de evidencia:** el auditor cito 1367-1371 y 1491-1499; las cabeceras `if` (1367, 1491, 1497) si se ejecutan, lo muerto es el cuerpo.
**Verificacion:** Lente 1 reprodujo las dos listas y corrigio el rango; lente 2 no hallo ninguna nota que declare las banderas fuera del alcance de los tests.

### F-12 -- La celda de texto vacia del CSV no la prueba nadie
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** src/modulos/M0_carga.py:230-235 (linea 233 sin cubrir); llamadores en :169, :209, :250, :267
La rama de celda vacia para columnas de TEXTO no se ejecuta en ninguna corrida de la suite, pese a cubrir cuatro columnas obligatorias (`id`, `progresiva_km`, `familia`, `sucs_fundacion`). El comportamiento hoy es correcto -- se reproduce vaciando cada columna --, pero nada lo fija: cambiar `_texto` por un default dejaria la suite en 725 verdes con la familia vacia colandose hasta M1.
**Regla:** Claude.md:95-97: "DatoFaltanteError ... Falta la columna entera, **o la celda obligatoria viene vacia**."
**Evidencia:**
```
$ for c in 1 3 16; do (fila 2 con la columna c vacia) cargar_puntos(v.csv); done
col 1  -> DatoFaltanteError | Falta el dato 'id' en el punto (fila 2). la fila 2 la deja vacia
col 3  -> DatoFaltanteError | Falta el dato 'familia' en el punto A-01 ...
col 16 -> DatoFaltanteError | Falta el dato 'sucs_fundacion' en el punto A-01 ...
$ python3 -m coverage report -m --include="src/modulos/M0_carga.py"
src/modulos/M0_carga.py  130  2  98%   233, 317
```
**Verificacion:** Lente 1 reprodujo las tres salidas y la cobertura; lente 2 confirmo que ningun documento declara la rama exenta.

### F-13 -- Seis modulos de calculo no consumen `casos_patron.py`
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** tests/fixtures/casos_patron.py:32-237; tests de M2, M5, M7, M8, M9, M10
Los seis dan `casos_patron=0`. Lo que baja la severidad: el fixture define SOLO OCHO casos y ninguno cubre M2, M7, M8 ni M10, de modo que para esos cuatro la regla no es incumplible por descuido -- exige primero escribir el caso dorado que no existe. El unico incumplimiento neto es M9, que tiene CP-7 escrito y no lo importa. M5 es intermedio: CP-3 le corresponde y se consume desde test_M3 y test_constantes_normativas.
**Regla:** Claude.md:123: "Todo modulo de calculo se contrasta contra tests/fixtures/casos_patron.py." Ninguna linea de docs/ declara exentos a estos modulos.
**Evidencia:**
```
$ for m in M2_material M5_verificaciones M7_geometria M8_estructural M9_cabezal M10_espaciamiento; do grep -c casos_patron tests/test_${m}.py; done
0 0 0 0 0 0
$ grep -n '^CP' tests/fixtures/casos_patron.py
36 CP1 | 63 CP2 | 97 CP3 | 112 CP4 | 130 CP5 | 144 CP5B | 145 CP5C | 154 CP6 | 167 CP7 | 196 CP8
  -> ninguno de M2/M7/M8/M10
$ for f in tests/test_M*.py; do grep -c casos_patron $f; done -> M0:1 M1:2 M3:1 M4:2 M6:3 MD:1 M11:0
```
**Verificacion:** Lente 1 reprodujo los conteos y abrio el fixture completo; lente 2 no hallo exencion en docs/ (GRAVE -> MENOR: el alcance real es mucho menor que el declarado).

### F-14 -- Los valores dorados de CP-7 estan duplicados como literales en test_M9_cabezal.py
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** tests/test_M9_cabezal.py:103-137,175; tests/fixtures/casos_patron.py:164-180; tests/test_criterios_adoptados.py:542-571
CP-7 lo consume un test que no importa M9. La afirmacion central del hallazgo original es FALSA: existe `test_cada_paso_lee_su_propio_criterio_y_no_un_0_50_escrito_a_mano`, que llama a las cuatro funciones de produccion, inyecta F_pga=0.9 y exige A_s == k_h == 0.45, es decir el detector exacto de un 0.50 hardcodeado. Lo que sobrevive es la duplicacion: 0.50, 0.45 y 0.25 estan escritos como literales en vez de importarse de `CP7_CADENA_SISMICA`, de modo que corregir el fixture no llega a los tests de M9.
**Regla:** Claude.md:123: el contraste tiene que ser contra el MODULO y contra el fixture.
**Evidencia:**
```
$ grep -n "CP7_CADENA_SISMICA" tests/test_criterios_adoptados.py -> 26 (import), 547
$ grep -c casos_patron tests/test_M9_cabezal.py -> 0
$ sed -n '123,137p' tests/test_M9_cabezal.py
def test_cada_paso_lee_su_propio_criterio_y_no_un_0_50_escrito_a_mano():
    A_s = aceleracion_ajustada_sitio(PGA=cadena.PGA, F_pga=0.9)
    assert A_s == pytest.approx(0.45) ; assert k_h != pytest.approx(cadena.k_h)
```
**Verificacion:** Lente 1 reprodujo el comando del auditor y encontro los dos tests que si llaman a M9 con los dorados; lente 2 no hallo documentacion de la division (GRAVE -> MENOR: deuda de trazabilidad, no agujero de verificacion).

### F-15 -- Los dos .md de tests/fixtures arrastran afirmaciones ya falsas sobre el codigo
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Detectado desde 3 dimensiones** (C2, E, F2) - **Ubicacion** tests/fixtures/datos_referenciales_prueba.md:9-10,14-17,34-35; tests/fixtures/datos_referenciales_prueba.NO_APLICADOS.md:9-22,28,45-50,86
El acta ofrece `v_max_hdpe = 6.0` y `v_max_tmc = 4.5` sobre valores cerrados en 4.6 y afirma que "los criterios siguen en valor=None a proposito", incumpliendo su propia regla de retirada (linea 14-17). NO_APLICADOS.md declara cuatro criterios que "estallan el AssertionError, que NO es ErrorProyecto ... aborta la corrida entera": con `remanso_derecho_via` declarado, `v5_remanso` lanza `DatoFaltanteError`, que SI es ErrorProyecto. Sus cinco "Sitios" de AssertionError no apuntan a ningun `raise`: dos son falsos (M5:309 es docstring, M5:424 una linea de guiones) y tres estan corridos una linea. Ademas justifica la no aplicacion con un desempaquetado en "M5_verificaciones.py:202", que hoy es prosa, y cita "Baseline en limpio: 653 passed" frente a 725.
**Regla:** el propio acta: "se retiraron 6 entradas que ya estan cerradas o retiradas en el codigo real (...). Aplicar estos valores encima pisaria trabajo ya verificado con cita." El registro autoritativo de minas (cli.py:596-604, :773-782) si esta al dia.
**Evidencia:**
```
$ sed -n '34,35p' tests/fixtures/datos_referenciales_prueba.md
*   **v_max_hdpe**: `6.0` (m/s)   /   *   **v_max_tmc**: `4.5` (m/s)
$ python3 -c "..." -> real hoy: v_max_hdpe = 4.6 / v_max_tmc = 4.6
$ git log -1 --date=short -- tests/fixtures/datos_referenciales_prueba.md -> 707b6ce 2026-08-19
$ git log -1 --date=short -S'valor=4.6' -- src/criterios_adoptados.py -> ffea9ca 2026-08-25
$ grep -n "raise AssertionError" src/modulos/*.py
M5:534 | M8:188 | M9:980, 996, 1087     (el .md dice M5:309, M5:424, M8:189, M9:981, M9:997)
$ PYTHONPATH=src:. python3 -c "...establecer_valor_dinamico('remanso_derecho_via',...); M5.v5_remanso(...)"
criterio DECLARADO -> DatoFaltanteError | ErrorProyecto? True
$ sed -n '202p' src/modulos/M5_verificaciones.py -> prosa de docstring, no el desempaquetado citado
```
**Verificacion:** Lente 1 reprodujo las cinco discrepancias en las tres pasadas (incluidas las fechas de git); lente 2 hallo el freno general de la cabecera del acta, que acota el riesgo pero no retira las entradas caducas ni corrige el inventario de minas.

### F-16 -- 15 asserts de la suite comparan floats con `==`
**Sev** MENOR - **Clasificacion** defecto real - **Veredicto** IMPRECISO - **Ubicacion** test_M6:58; test_M9:549,550,641,645,741; test_cli:99,114,115,123,207,237,342,359,388 (+ test_M2:129-130)
Las 15 apariciones existen y Claude.md:111 lo prohibe sin exencion para tests. Ninguna compara el resultado de una operacion de punto flotante: son constantes de modulo, valores declarados que viajan de punta a punta y retornos literales -- incluido el caso que el hallazgo llamaba "el mas expuesto" (`n_s_zapata_en_talud` con B<H_s hace `return 0.0`). Incumplimiento de la letra, sin riesgo de resultado.
**Regla:** Claude.md, Estilo: "No comparar floats con ==. Tolerancias explicitas y nombradas", repetido en src/tolerancias.py:39.
**Evidencia:**
```
$ grep -rn "assert .*== *[0-9]*\.[0-9]" tests/*.py | grep -v approx
test_M6_proteccion.py:58 | test_M9_cabezal.py:549,550,641,645,741
test_cli.py:99,114,115,123,207,237,342,359,388            (15 en total)
$ awk 'NR>=1033 && NR<=1035' src/modulos/M9_cabezal.py
    if B < H_s: return 0.0      # literal: el assert de la linea 645 es exacto por construccion
$ sed -n '108,112p' Claude.md   -> la seccion Estilo no exime a los tests
```
**Verificacion:** Lente 1 reprodujo el grep exacto y desmonto el "caso mas expuesto"; lente 2 leyo la seccion Estilo completa: no hay exencion.

### F-17 -- Un test que no invoca codigo de produccion y otro que contrasta el fixture consigo mismo
**Sev** MENOR - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** tests/test_M3_hidraulica.py:147-151; tests/test_modelos.py:141-148 (parcial: el assert de la linea 148)
`test_pendiente_que_produce_v_objetivo_de_cp3` tiene una unica llamada, `pytest.approx`, confirmado por AST: reimplementa la formula de velocidad y pasa aunque M3 devuelva basura. Dos correcciones que bajan la severidad: M3 SI esta contrastado contra CP-2/CP-3 por otros seis tests con assert de valor, asi que es redundancia y no hueco de cobertura; y `test_la_geometria_reproduce_CP2` si ejerce codigo de produccion (`Geometria.y_sobre_D`), de modo que solo su segundo assert es fixture contra si mismo. Ninguno declara en su docstring que sea comprobacion del fixture.
**Regla:** Claude.md:122-123: un test que no ejerce ninguna funcion del modulo no lo contrasta.
**Evidencia:**
```
$ python3 -c "import ast; ... test_pendiente_que_produce_v_objetivo_de_cp3 ..."
LLAMADAS: ['pytest.approx']
$ (con area/perimetro/_caudal_manning de M3 devolviendo basura) -> 1 passed
$ grep -n "def test_" tests/test_M3_hidraulica.py | head -6
43, 55, 62, 76, 87, 98   (seis tests con assert de valor contra CP-2)
$ awk 'NR>=488 && NR<=491' src/modelos.py -> @property y_sobre_D  (test_modelos.py:145 SI la ejerce)
```
**Verificacion:** Lente 1 confirmo el AST y corrio la prueba con M3 saboteado; lente 2 hallo la declaracion parcial en el comentario de cabecera del test (GRAVE -> MENOR).

### F-18 -- La auditoria previa sigue citando 595 tests y 12 modulos
**Sev** OBSERVACION - **Clasificacion** defecto real - **Veredicto** CONFIRMADO - **Ubicacion** docs/auditoria_y_ruta_despliegue_v9.md:44
Es el unico conteo de tests publicado en todo docs/, asi que no hay contradiccion entre documentos, solo desactualizacion: hoy son 725 passed + 1 skipped y src/modulos/ contiene 13 ficheros. La linea es la tabla de estado de una auditoria fechada y la desviacion va hacia arriba.
**Regla:** Claude.md:144-146: "Al reportar el conteo, distinguir passed de collected ... Decir cual de los dos se esta citando." La linea 44 ni distingue ni esta actualizada.
**Evidencia:**
```
$ sed -n '44p' docs/auditoria_y_ruta_despliegue_v9.md
| **El software como herramienta** | Terminado. 12 módulos, 595 tests en verde, GUI, exportación ... |
$ python3 -m pytest -q 2>&1 | tail -1   -> 725 passed, 1 skipped in 2.45s
$ ls src/modulos/*.py | wc -l -> 13
$ grep -rn 'tests en verde\|passed' docs/*.md -> unica coincidencia: la linea 44
```
**Verificacion:** Lente 1 reprodujo los tres comandos; lente 2 leyo el contexto (tabla de estado de un informe previo, no una especificacion).

### F-19 -- El ValueError de `escribir_valor_en_archivo` bloquea los 2 criterios de valor multilinea
**Sev** OBSERVACION - **Clasificacion** deliberado sin documentar - **Veredicto** IMPRECISO - **Ubicacion** src/criterios_adoptados.py:302-312; criterios afectados en :1339-1340 y :1586-1587
2 de los 46 criterios no los encuentra el patron porque su `valor=` abre un dict multilinea. El sentido esta invertido respecto del hallazgo original: `_verificar_criterio` NO rechaza un escalar para un criterio de valor dict -- llamar `escribir_valor_en_archivo('factores_carga_aashto', 1.5, ...)` deja pasar el 1.5 y lo unico que impide escribir un float encima de la tabla de factores AASHTO es ese ValueError. La GUI solo puede producir float o str. Falta la linea que acote el alcance en el docstring y una verificacion de tipo aguas arriba.
**Regla:** Claude.md:122; la limitacion no esta escrita en el docstring, en gui/app.py ni en docs/.
**Evidencia:**
```
$ python3 -c "...regex sobre CRITERIOS..."
total criterios: 46 | claves que el patron NO encuentra: 2
['factores_carga_aashto', 'procedimiento_flexion_corte_aashto_sec5']
$ awk 'NR==1339||NR==1340||NR==1586||NR==1587' src/criterios_adoptados.py -> ambos abren dict multilinea
$ python3 -c "... escribir_valor_en_archivo(k, 1.5, ruta=copia) ..."
-> ValueError | No se encontro el bloque 'valor=' ...   (_verificar_criterio ACEPTO el float 1.5)
$ awk 'NR>=554&&NR<=558' gui/app.py -> la GUI atrapa (KeyError, ValueError, OSError)
```
**Verificacion:** Lente 1 reprodujo el filtro y ejecuto la funcion sobre copia, invirtiendo el sentido del hallazgo; lente 2 confirmo que la intencion se lee en la forma del codigo, no en una linea escrita (MENOR -> OBSERVACION).

### F-20 -- El skip permanente y la segunda rama de ImportError de MD
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** CONFIRMADO - **Ubicacion** tests/test_MD.py:344-352; src/modulos/MD.py:167-168,178,555
El skip es deliberado y su motivo esta escrito en el `reason` y en el docstring de `MD._verificador_de_M5`, que ademas menciona expresamente la segunda condicion ("Un M5 ausente O SIN ESA FUNCION"). Queda deuda de cobertura de dos lineas: el segundo `raise ImportError` (M5 presente sin `verificar`, ejercitable sin borrar el modulo) y el `verificar = _verificador_de_M5()` del camino de lote.
**Regla:** Claude.md:122; no hay regla de cobertura de ramas escrita en Claude.md ni en docs/.
**Evidencia:**
```
$ python3 -m pytest -q -rs 2>&1 | tail -3
SKIPPED [1] tests/test_MD.py:344: M5 ya existe: el verificador por defecto lo importa
725 passed, 1 skipped in 2.37s
$ python3 -m coverage report -m --include="src/modulos/MD.py"
src/modulos/MD.py  107  4  96%   167-168, 178, 555
$ awk 'NR>=160 && NR<=161' src/modulos/MD.py
    Importa `modulos.M5_verificaciones.verificar`. Un M5 ausente o sin esa
    funcion es un fallo de PROGRAMA ...
```
**Verificacion:** Lente 1 reprodujo skip y cobertura; lente 2 hallo la decision escrita en dos sitios (MENOR -> OBSERVACION, reclasificado a documentado).

### F-21 -- El borde de tolerancia de los umbrales no esta cubierto
**Sev** OBSERVACION - **Clasificacion** deliberado documentado - **Veredicto** IMPRECISO - **Ubicacion** M5:209,272,292,511; M7:482; M9:894,1279,1337,1397,1418,1426; M4:532; M1:294; M3:103
Invertir el signo de `TOL_UMBRAL_NORMATIVO` en esas comparaciones deja la suite en 725 passed (tres reproducidos uno a uno). Sin riesgo: la tolerancia vale 1e-9, de modo que la banda invertida mide 2e-9 -- once ordenes por debajo de cualquier magnitud de diseno --, y el propio archivo lo declara ("una millonesima de milimetro"). La regla citada no esta incumplida: el codigo no compara floats con `==`, y `test_tolerancias.py:34-42` si ejerce la semantica de la banda.
**Regla:** Claude.md, Estilo: "No comparar floats con ==. Tolerancias explicitas y nombradas" -- se cumple.
**Evidencia:**
```
$ (copia) sed -i '209s|V_MIN - TOL_UMBRAL_NORMATIVO|V_MIN + TOL_UMBRAL_NORMATIVO|' && pytest -q|tail -1
725 passed, 1 skipped in 3.25s
$ (copia) M4_control.py:532 '+'->'-'  -> 725 passed | M7_geometria.py:482 '-'->'+' -> 725 passed
$ awk 'NR>=58 && NR<=63' src/tolerancias.py
# ... 1e-9 sobre magnitudes de orden 1 es una millonesima de milimetro ...
TOL_UMBRAL_NORMATIVO = 1e-9
$ sed -n '34,42p' tests/test_tolerancias.py -> test_el_umbral_no_tapa_un_incumplimiento_real
```
**Verificacion:** Lente 1 reprodujo tres mutantes; lente 2 leyo el valor y su justificacion escrita (MENOR -> OBSERVACION: deuda sin regla incumplida).

---

## Cobertura y límites

Lo que esta auditoria **no** cubrio, consolidado de las notas de los seis auditores:

**No verificado contra las fuentes normativas.** Ninguna cita de numeral, pagina o edicion se contrasto contra el PDF original: ningun documento fuente esta en el repositorio, y `docs/manifiesto_citas.md` declara lo mismo de si mismo ("Ningun PDF fue abierto para producirlo"). Todo lo reportado sobre etiquetas y citas es coherencia interna codigo/documento, no exactitud documental. Un `[C]` con cita cerrada puede seguir citando mal una pagina y esta auditoria no lo ve.

**GUI no ejecutada.** `tkinter` no esta instalado en el entorno (`ModuleNotFoundError: No module named 'tkinter'`). Todo lo reportado de gui/app.py sale de lectura estatica mas ejecucion directa de las funciones de `cli` y `criterios_adoptados` que la GUI invoca. Metodos enlazados solo por `command=`/`bind()` podrian estar vivos sin que el barrido lo vea (no aparecio ninguno huerfano, pero no se verifico en ejecucion).

**Mutacion parcial.** Se generaron 303 mutantes por AST sobre M0-M10 y modelos.py (46 sobreviven, 15,2 %: 23 en M9, 8 en M7, 7 en modelos.py, 4 en M5, 1 en cada uno de M0, M1, M3, M4). Quedaron **sin mutar**: M11_reporte.py (~45 mutantes potenciales, y sus tests son los que mas dependen de subcadenas sobre HTML), MD.py, criterios_adoptados.py (19), datos_sitio.py (6), cli.py y gui/. Regiones como los ~400 statements de generacion de HTML de M11 figuran cubiertas por linea y pueden estarlo sin comparacion de contenido, como ocurre demostrablemente con `exportar_csv`.

**Cobertura de rama no medida.** Se corrio `coverage` de linea, no `--cov-branch`: hay condicionales cuyo lado falso puede no ejercitarse aunque la linea figure cubierta.

**Modulos revisados en diagonal.** M9_cabezal.py (1495 lineas): no se verifico linea a linea Mononobe-Okabe, `empujes_trasdos`, E1-E5 ni `n_s_zapata_en_talud` contra la Sec. 9 de la hoja de ruta. M7_geometria.py: las ultimas ~140 lineas (compatibilidad geometrica, G2, cotas de salida) se leyeron por encima. M8_estructural.py: `cama_apoyo_relleno_lateral` y `verificacion_diferida_estructural` solo por encima.

**Diccionarios grandes por dentro.** `F_PGA_TABLA`, `FS`, `SULFATOS`, `HDS5_INLET` y `RESGUARDO_NAPA_SUBRASANTE` se consumen como objeto; no se comprobo si alguna FILA o CLAVE interna concreta es inalcanzable (exige analisis de flujo, no grep).

**tests/ como objetivo.** No se audito si hay fixtures o helpers muertos dentro de la suite; solo se verifico que los diez casos de `casos_patron.py` estan todos consumidos (ninguno huerfano) y que `TODOS_LOS_CASOS` (casos_patron.py:227-238) tiene 0 usos.

**legacy/Tc.py por dentro.** Se trato como unidad: no se reviso si tiene codigo muerto interno.

**Trazabilidad del CSV de ejemplo.** No se pudo comprobar si los valores de `tests/ejemplo_puntos.csv` (Q, cotas, CBR de A-01..C-01) corresponden a mediciones reales: no hay en el repositorio ninguna fuente contra la cual contrastarlos y la hoja de ruta no publica esa tabla. Es el vacio de trazabilidad mas grande detectado y no se pudo convertir en hallazgo reproducible.

**Criterios [A] vacios sin sensibilidad.** Los 12-16 `[A]` con `valor=None` y sin sensibilidad no se reportaron en bloque: un `[A]` sin valor todavia no eligio nada, la guardia no lo exige y la auditoria v9 planifica su cierre. Solo se reporta el caso singular (`angulo_aletas`, D-05) y el unico `[A]` **con** valor y sin sensibilidad (`clase_sitio`, D-08).

**Integridad del arbol.** Ningun auditor escribio en el repositorio: mutaciones y pruebas se hicieron sobre copias en scratchpad o en `mktemp`. El unico archivo que aparece modificado es `tests/ejemplo_puntos.informe.json`, que es el artefacto que `cli.py` reescribe por defecto (ver C-10). SHA verificado al cierre: `2e1708abd91f6de1b80ec5456563cd1688e715bc`; suite `725 passed, 1 skipped`.

**Evidencia que no reprodujo tal como llego** (en todos los casos va la version del verificador, indicada en la ficha): B-19 (comando roto: el `grep -v criterios_adoptados.py` filtraba tambien el archivo de tests y el `echo` corria siempre), B-21 (salida de tests inexistente: la linea citada dice otra cosa), A-15 (`M9_cabezal.py:209` no existe como uso; los reales son 683 y 699), A-18 (linea 430 por 438), C-09 (`(6, 0.9)` por `(5, 0.9)`), A-20 (el auditor omitio la linea 440 y conto tres apariciones donde hay cuatro), D-04 (lineas 495/326 por 496/327), E-05 (linea 1166, que es el campo de un criterio, por 144-173), E-06 (`_falta_dato` en 513-517 por 511-515), F-08 (M7:534 declarada sin cobertura cuando si la tiene), F-11 (cabeceras `if` contadas como muertas), B-23 (raise en 337-340 por 338-341 y motivo del CBR parafraseado mal), F-04 (tres de los diez mutantes declarados son cosmeticos: viven dentro del mensaje de la excepcion). Ningun hallazgo llego sin comando ni sin salida; ninguno se descarto por perdida de evidencia.

---

## Refutados

Tres hallazgos no sobrevivieron a la verificacion. Los dos primeros son instructivos:

**V8 lanza AssertionError desnudo (A1).** El AssertionError sale tal cual, pero el escenario descrito -- corrida abortada al declarar `TR_evento_extremo` desde la GUI -- no se produce: el lote termina con `DisenoNoFactibleError` por el `DatoFaltanteError` de V5, que precede a V8. Ademas cli.py:596 llama a esa linea "MINA DELIBERADA (no desactivar)", razona por que debe seguir siendo un fallo de programa, y un test la fija. Lo unico anotable, por debajo del umbral de reporte: la guarda vive en M5 y su razon vive en cli.py.

**`LONG_MAX_CUNETA` como cuarta doble definicion no declarada (B1).** El comando del auditor devuelve 3 lineas donde el declaro 1: la salida pegada no reproduce. Y la denuncia no se sostiene: la ADVERTENCIA de `constantes_normativas.py` enumera tres bloques donde el mismo parametro esta duplicado con identico valor; `LONG_MAX_CUNETA` es un caso distinto -- tabla de dos filas frente a eleccion de una --, cubierto por la regla de coherencia de la hoja de ruta:40 que el proyecto ya aplico a `F_pga`, `v_max_concreto_eleccion` y `factor_muro`. Es decision deliberada y documentada.

**Cuando faltan varias columnas del CSV, la excepcion solo nombra la primera (E).** El escenario no se reproduce: la cadena tiene un solo llamador de produccion (cli.py:899) y con un encabezado mutilado la `DatoFaltanteError` sale de `cli.correr` sin pasar por `_bloqueo`, de modo que no hay informe donde el dato estructurado llegue incompleto. La ruta esta ademas documentada como decision deliberada en el docstring de `correr`. Lo residual (`campo=faltan[0]`) no tiene consumidor.

---

*Auditoría producida sobre el commit `2e1708abd91f6de1b80ec5456563cd1688e715bc`.
Once auditores independientes más verificación adversaria de doble lente por
hallazgo; 1394 llamadas a herramientas. El repositorio no fue modificado durante
la auditoría.*
