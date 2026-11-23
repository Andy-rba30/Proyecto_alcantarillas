# Decisiones diferidas — el registro único

Este documento existe por una razón concreta: el proyecto tiene **veintidós
objetos que la auditoría de sistema clasificó «deliberado sin documentar»**.
No son defectos. Son decisiones que alguien tomó a conciencia —conservar una
API sin llamador, excluir un directorio de un barrido, no implementar un
procedimiento todavía— y que **no estaban escritas en ningún sitio donde un
revisor las buscara**. La auditoría no las encontró mal hechas: las encontró
mudas.

El plan (`docs/hoja_de_ruta_correcciones_v12.md`, S14 punto 5 y S19 punto 1)
pide desde hace cinco sesiones «cada criterio sin consumidor, con su razón
escrita **en un solo lugar**». Este es ese lugar.

## Qué es y qué no es

- **Es** el índice de las decisiones. Cada ficha dice cuatro cosas y siempre
  las mismas: **qué se difirió**, **por qué**, **qué haría falta para
  cerrarlo**, y **dónde vive en el código**.
- **No es** una segunda copia de la razón. La razón vive donde vive el
  código —en el docstring del símbolo, en el comentario de la constante, en el
  test que la vigila— y aquí se **cita el símbolo**, no se transcribe el
  párrafo. Dos copias de la misma razón divergen sin que nada avise, y ese
  defecto ya lo tuvo el proyecto con las transcripciones normativas
  (NOR-MEM-01).
- **No es** el tracker, y los dos números no miden lo mismo. En el tracker
  (`docs/auditorias/matriz_cruzada_auditorias.xlsx`, hoja `Hallazgos`) **las 22
  figuran como `Cerrado`**, y con razón: lo que el tracker sigue es si el
  hallazgo está atendido, y todos lo están —la decisión se tomó y se escribió—.
  Aquí se mide otra cosa: **cuántas no esperan nada**. Son **quince**. Las otras
  **siete** están cerradas Y siguen esperando algo que no depende de esta
  decisión: SIS-A-04 (la cota levantada en campo), SIS-A-13 (el n del cauce
  natural, para el segundo indicador del num. 5.3.3), SIS-A-16 (que la Sec. 1.5
  recoja las dos filas), SIS-B-04 (el levantamiento de la sección del receptor),
  SIS-B-07, SIS-B-08 (un discriminante en `PeriodoRetorno`) y SIS-B-10 (que la
  §1.2 deje de nombrar `Tc.py`, o que su procedimiento entre al calculador).
  **Dos de las siete cambiaron de naturaleza en S20** y las fichas lo dicen:
  SIS-A-13 y SIS-B-04 pasaron de «difierido» a IMPLEMENTADO, y lo que esperan
  ya no es permiso para escribir el código sino un dato de campo que lo
  alimente mejor. Es la distinción que el epígrafe de arriba adelanta: cerrado
  no significa que el mundo no pueda cambiar.
- **Un hallazgo `Cerrado` con «qué haría falta» lleno no es una contradicción**,
  y conviene decirlo porque lo parece: cerrado significa que la decisión está
  tomada y escrita, no que el mundo ya no pueda cambiar. El día que llegue la
  cota levantada, SIS-A-04 no se reabre — se rehace la decisión con el dato.

## Cómo se mantiene

`tests/test_decisiones_diferidas.py` deriva la lista de los veintidós
**del propio informe de auditoría** —las fichas cuya línea `**Clasificacion**`
dice «deliberado sin documentar»— y comprueba que cada una tenga ficha aquí,
con sus cuatro campos, y que el símbolo que la ficha nombra **siga existiendo
en el repositorio**. Si alguien renombra el símbolo, este documento se pone en
rojo en vez de envejecer en silencio. Es la misma lección que dejó
`FACTOR_MURO_TABLA`: un documento que nadie verifica es una afirmación, no un
registro.

---

# Índice de fichas

> Tabla derivada automáticamente de las **401** fichas del documento (`75` cerradas, `150` abiertas/parciales, `176` diferidas/declaradas).
> Regla de estado (verificada por `tests/test_decisiones_diferidas.py`): `cerrada` si el título marca IMPLEMENTADA/CERRADA o tiene `**Cerrado` sin `**Abierto`; `abierta / parcial` si declara `**Abierto`; `diferida / declarada` en el resto.

| Ficha | Tema | Estado |
|---|---|---|
| SIS-A-04 | `cota_entrada_supuesta` rellena un vacío de dato dentro de M5 | diferida / declarada |
| SIS-A-13 | V2b (sedimentación / colmatación) — IMPLEMENTADA en S20 | cerrada |
| SIS-A-16 | Dos validaciones cruzadas de M0 que no son fila de la tabla de Sec. 1.5 | diferida / declarada |
| SIS-A-17 | La GUI no exponía `--alcance` | diferida / declarada |
| SIS-A-18 | La sesión JSON no guardaba los criterios declarados | diferida / declarada |
| SIS-B-04 | «TW se calcula, no se mide» (Sec. 1.3) — IMPLEMENTADO en S20 | cerrada |
| SIS-B-05 | Entregable 5 (análisis de sensibilidad): su única API la consumían los tests | diferida / declarada |
| SIS-B-06 | `--plantilla memoria_perfil.html` sobre corrida de expediente | diferida / declarada |
| SIS-B-07 | `CriterioPendienteError.mensaje_gui` no tiene consumidor de producción | diferida / declarada |
| SIS-B-08 | `PeriodoRetorno.exigir_anios` no tiene llamador | diferida / declarada |
| SIS-B-09 | Constantes `NUMERAL_*` de módulo declaradas y nunca leídas | diferida / declarada |
| SIS-B-10 | `legacy/Tc.py`: sin importadores, sin tests, sin barrido y sin estatus | diferida / declarada |
| SIS-C-06 | `barrido()` solo recorría `src/` | diferida / declarada |
| SIS-C-11 | El barrido solo miraba `.py` | diferida / declarada |
| SIS-C-12 | El ejemplo de uso de M1 daba luces sin la salvedad que sí lleva el test | diferida / declarada |
| SIS-D-08 | `clase_sitio` es el único `[A]` con valor y sin sensibilidad | diferida / declarada |
| SIS-D-09 | `datos_sitio.py` no tenía guardia al importar | diferida / declarada |
| SIS-D-12 | `v_max_hdpe` y `v_max_tmc` sin ancla `vacio_verificado` | diferida / declarada |
| SIS-E-02 | M9 usaba `DatoInvalidoError` para validar argumentos internos | diferida / declarada |
| SIS-E-04 | El único `raise` de la GUI valida un campo tecleado con `ValueError` | diferida / declarada |
| SIS-F-17 | Un test que no invocaba código de producción | diferida / declarada |
| SIS-F-19 | El `ValueError` de `escribir_valor_en_archivo` y los criterios multilínea | diferida / declarada |
| (sin ID) | `M9_cabezal.combinaciones()` prometía un consumidor que no existe | diferida / declarada |
| (sin ID) | La premisa de SIS-A-08 se había sustituido por otra premisa falsa | diferida / declarada |
| (sin ID) | Las referencias de prosa del manifiesto eran dos poblaciones, no una | diferida / declarada |
| NOR-E060-02 | El acero en dos caras entre 200 y 250 mm | abierta / parcial |
| NOR-HDS-05 | Las tres condiciones de uso de h_o | abierta / parcial |
| NOR-PRO-04 | La norma a la que se difiere la verificación del TMC | abierta / parcial |
| NOR-ANA-03 | La analogía de embocadura del HDPE | abierta / parcial |
| SIS-F-01 | La GUI y sus tests de contrato | abierta / parcial |
| SIS-F-13 | Los módulos de cálculo sin caso patrón | abierta / parcial |
| (sin ID) | MAT-D1 estaba corregido y no lo defendía ningún test | diferida / declarada |
| C1-01 | La mitad por tirante de `Seccion` no tiene consumidor | diferida / declarada |
| C1-02 | `SeccionCircular.etiqueta()` no la invoca ningún módulo — **CERRADA en C8** | cerrada |
| C1-03 | `Geometria.y_sobre_D` se quedó sin consumidor de producción | diferida / declarada |
| C1-04 | `M3_hidraulica.tirante` se quedó huérfana | diferida / declarada |
| C5-01 | La clave `"cajon"` de `factores_carga_aashto` no tiene consumidor | diferida / declarada |
| C5-02 | `ke_entrada` sigue declarando un número y `ke_entrada_cajon` una fila | diferida / declarada |
| C6-01 | `sucs_fundacion` se carga, se valida y no la lee ningún módulo | diferida / declarada |
| C6-02 | `_Columna.criterio_destino` admite un solo destino | diferida / declarada |
| C8-01 | Nueve de 38 `Parte.cita_id` anuncian una cita que nadie transcribió | diferida / declarada |
| C8-02 | `Registro.discrepancias_abiertas` sigue sin consumidor de producción | diferida / declarada |
| C8-03 | `Registro.discrepancias_de_cita` solo lo usa el propio registro | diferida / declarada |
| C8-04 | `M2.diametro_exterior` — se RETIRÓ, y por qué no se difirió | diferida / declarada |
| VC1-01 | La deuda de §13 se cierra por MITADES, y la otra mitad sigue diferida | abierta / parcial |
| VC1-02 | V5 no se difiere en la Familia C: NO APLICA, y VC1 ocupa su hueco | diferida / declarada |
| R2a-01 | `factores_carga_aashto`: el par único descartado, y la dirección que la ficha NOR-PUE-03 invierte | diferida / declarada |
| R2a-02 | `HW_D_max`: V4b estuvo declarado y sin cablear a propósito | diferida / declarada |
| R2a-03 | `espesor_pared_conducto`: la cifra del código (−33.1 %) no es la de la ficha MAT-D3 (−31.6 %) | diferida / declarada |
| R2b-01 | `clase_sitio`: la dispensa inventada y el [A] que confesaba no ser una elección | diferida / declarada |
| R2b-02 | `cortante_alto_muro_e060_art_11_10_10_2`: el umbral 0.5·φ·Vc era una atribución inventada | diferida / declarada |
| R2b-03 | `k_v`: la sensibilidad numérica (0.0, 0.5) retirada, y las tres formas del rango | diferida / declarada |
| S24-01 | Las claves externas sin techo, y el punto de decisión de `longitud_m` | diferida / declarada |
| N1-01 | La vía 3 del canal de discrepancias (`Criterio.discrepancias`) se quedó sin usuario de producción | diferida / declarada |
| N2-01 | La traducción no oficial de M 294-11 entra como Fuente propia, sin firma en sus citas, y el original sigue ausente | diferida / declarada |
| T1-01 | La vigencia de las ediciones es una marca en la nota, no un campo del esquema | diferida / declarada |
| I4-01 | El chequeo dimensional piloto (M3–M5) midió cuatro inconsistencias de presentación y ninguna de valor; PD las cerró sin mover un número, y la extensión del barrido a M6–M10 sigue diferida | abierta / parcial |
| D9-01 | La vía 2 del canal de discrepancias (`PasoDeMemoria.discrepancias`) volvió a quedarse sin usuario de producción | diferida / declarada |
| SIS-B-22 | `limpiar_valores_dinamicos` sí tiene caso de uso: abrir una sesión | diferida / declarada |
| NOR-HID-02 | La cuneta está en la pág. 179 y la memoria sigue imprimiendo 178 | diferida / declarada |
| EXT-V-01 | Un expediente por repositorio; multi-obra es requisito de producto | diferida / declarada |
| EXT-G-03 | Las seis fichas de ayuda de claves externas: se llenan, pero sólo por derivación | diferida / declarada |
| PC-32 | El umbral de `factor_esviaje` es una tolerancia numérica, no una cota de esviaje | diferida / declarada |
| EXT-V-02 | La celda que la procedencia cita se infiere cuando la fila tiene una sola | diferida / declarada |
| EXT-2-01 | V6 sigue rechazando N > 1 aunque el multicelda ya se resuelve bien | cerrada |
| EXT-2-02 | El JSON de la CLI no lleva `Q_celda_m3s` ni `numero_celdas` todavía | cerrada |
| EXT-3-01 | El 0.75 de V1 y el 0.25 m/s de V2 siguen rotulados [N] aunque la v8 ya dice que el umbral duro es [A] | diferida / declarada |
| EXT-3-02 | V1 y V2 se evalúan con el escenario de TW gobernante, no con los dos | diferida / declarada |
| EXT-3-03 | El bloqueo «método no evaluable» no aparece en el tablero de criterios de la GUI | diferida / declarada |
| EXT-4-01 | La sesión sigue en formato v2: sin identidad, sin huella del CSV y sin corridas | diferida / declarada |
| EXT-4-02 | El contexto vive en registros de módulo, no en `contextvars`: la GUI sigue corriendo en su hilo | diferida / declarada |
| EXT-4-03 | Un `Informe` sin contexto no se exporta: no hay caída al estado vivo | diferida / declarada |
| EXT-5-01 | Ocho formas, no siete: `serie_de_claves` y la unión de formas | diferida / declarada |
| EXT-5-02 | La forma va última, y las guardias de los consumidores se quedan | diferida / declarada |
| EXT-5-03 | Once criterios de texto cuyo conjunto cerrado vive en el consumidor, no en `sensibilidad` | cerrada |
| EXT-6-01 | El RNGIV no vuelve a `normas/`: lo que se borró no era el decreto | diferida / declarada |
| EXT-6-02 | El piso [N] del ancho del derecho de vía está en el registro y no tiene consumidor | diferida / declarada |
| EXT-6-03 | PC-24 no se cierra en EXT-6: su resto es EXT-3-01 | diferida / declarada |
| EXT-6-04 | La cláusula de alcance no crea un `Fundamento`: el rótulo del marco es texto del registro, no un paso | diferida / declarada |
| EXT-7-01 | La ec. (11-32) del Art. 11.10.10.3 no se implementa: se declara evaluada fuera | diferida / declarada |
| EXT-7-02 | E6 (excentricidad sísmica) no entra en las `exigidas` por defecto | diferida / declarada |
| EXT-7-03 | El Ka de Coulomb se adopta entero, no la «guardia mínima» | diferida / declarada |
| EXT-7-04 | La resultante de Coulomb se toma entera como horizontal: la descomposición queda diferida | diferida / declarada |
| EXT-8-01 | El anexo se decide contra el «de arriba abajo» de la §4.4, y el objetivo de tamaño no se alcanzó | diferida / declarada |
| EXT-8-02 | El hijo recalcula: la equivalencia se afirma sobre la sesión serializada, no sobre el objeto `Informe` | diferida / declarada |
| EXT-8-03 | Las claves enteras de un criterio declarado no sobreviven al JSON de la sesión | diferida / declarada |
| EXT-8-04 | El progreso del hijo se lee de un archivo, no de un pipe, y no hay hilo | diferida / declarada |
| EXT-8-05 | Un paso renderizado suelto lleva enlaces sin destino | diferida / declarada |
| EXT-9-01 | `cli` conserva reexportaciones del servicio hasta que la suite migre | diferida / declarada |
| EXT-9-02 | La CLI se queda en la raíz: no hay `python -m src.cli` | diferida / declarada |
| EXT-9-03 | El índice de fórmulas no se regeneró en EXT-9, y su sello sigue siendo el de EXT-8 | diferida / declarada |
| EXT-10-01 | La ventana normativa sigue sin declarar datos de sitio | diferida / declarada |
| EXT-10-02 | «Importar decisiones» importa criterios y no datos de sitio | diferida / declarada |
| EXT-10-03 | La advertencia de corredor es por origen, no por texto; no bloquea y no va al JSON | diferida / declarada |
| EXT-10-04 | La sesión embebe la corrida; el hijo del PDF sigue recalculando | diferida / declarada |
| EXT-10-05 | El nivel de seis datos de sitio es un argumento, no una medida | diferida / declarada |
| EXT-10-06 | El `id` de una sesión migrada sólo es estable desde que se guarda | diferida / declarada |
| EXT-11-01 | Sin `hypothesis` ni `mutmut`: mallas y un arnés propio, hasta que se apruebe la dependencia | diferida / declarada |
| EXT-11-03 | El cruce de los temarios lleva un censo manual porque el auditor y el informe numeran distinto | diferida / declarada |
| EXT-11-04 | La Fase 8 se prueba llamándola sobre el resultado real de perfil, porque el expediente no dimensiona | diferida / declarada |
| EXT-11-05 | El determinismo de la línea base se demuestra con los archivos comprometidos, no con una segunda corrida | diferida / declarada |
| EXT-11-02 | Cuarenta y tres mutantes sobreviven a toda la suite, y cada uno tiene su razón escrita | diferida / declarada |
| EA-01 | Los dorados del perfil son límites de la propia fórmula, no una corrida HY-8 | diferida / declarada |
| EA-02 | El resalto no se sitúa por momentum: la S1 que no llega a la entrada se lee como control de entrada | cerrada |
| EA-03 | En la banda 0.75 ≤ HW/D < 1.2 la aproximación es el método y la comprobación manda sólo si pide más carga; el paso 4.3c puede decir NO CUMPLE sin rechazar el punto | diferida / declarada |
| EA-04 | La compuerta de h_o queda como guardia sin alcance en producción | diferida / declarada |
| EA-05 | «Most of its length» es un [A] con ventana, y su lectura vive en el registro | diferida / declarada |
| EA-06 | Veinticuatro mutantes del perfil sobreviven a toda la suite, y cada uno tiene su razón escrita | diferida / declarada |
| EA-07 | La asíntota del perfil no es el tirante normal de M3, y la diferencia queda impresa | diferida / declarada |
| EB-01 | El literal sigue existiendo: el editor lo compone y es la fuente al aplicar; un dict que la ficha no descompone no recibe campos inventados | diferida / declarada |
| EB-02 | Una categoría no exige fila, y un número nunca nombra una fila | diferida / declarada |
| EB-03 | El comparador compara volcados, no informes; «método» son tres campos | diferida / declarada |
| EB-04 | Responsable y evidencia son una derivación de la ficha, no una matriz; van al JSON y no a la memoria | diferida / declarada |
| EB-05 | El índice se deriva de la plantilla y de los puntos; el «histórico» no ganó una vista | diferida / declarada |
| EB-06 | La ventana emergente conserva su campo único; las dos ventanas no se unifican | diferida / declarada |
| PF-1-01 | La carga a la entrada fuera de rango es un vacío declarable, no un método no evaluable ni un descarte definitivo | diferida / declarada |
| PF-2-01 | El pre-vuelo estima de más a propósito, y lo que exige una sola familia es un dato declarado del servicio, no una deducción | diferida / declarada |
| PF-3-01 | El barrido vive en la CLI y en el servicio, y desde UI-3 también en el botón «Barrido…» de la pestaña 2 — cerrado (UI-3) | cerrada |
| PF-4-01 | INDICADOR es un valor de `TipoDeVeredicto` y no una cuarta capa del estado de verificación; el segundo indicador del 5.3.3 sigue sin evaluarse | diferida / declarada |
| PF-4-02 | El barrido leía el veredicto sólo de `cumple`, y desde PF-4 son dos campos | abierta / parcial |
| PF-5-01 | La guía dice lo que el programa hace, no lo que el prompt suponía: diez [A] de perfil sin valor, un `si` a perfil, una celda del CSV y una sesión escrita a mano | diferida / declarada |
| PF-5-02 | Lo que el test de la guía comprueba y lo que deja a la prosa | diferida / declarada |
| PF-6-01 | El CBR no tiene techo que la fuente fije: `CBR_MAX_FISICO` se retira y queda sólo el piso | abierta / parcial |
| PF-6-02 | El editor escalar suelta la fila cuando el texto deja de ser su clave, y sólo entonces | abierta / parcial |
| PF-6-03 | Lo que el comparador omite se dice desde `CAMPOS_OMITIDOS`, y lo que la prosa del registro decía antes no se reescribe | abierta / parcial |
| C10-01 | `ke_entrada` conserva la forma `float`; la fila viaja por la resolución y por la procedencia, y el consumidor no atribuye rótulos a un número que no es la celda | abierta / parcial |
| C10-02 | El estado de verificación tiene una sola fuente, `EstadoDeVerificacion`; `cumple` y el veredicto del paso son vistas comprobadas, y «no aplica» existe con un productor real | abierta / parcial |
| C10-03 | El esviaje máximo constructivo es un [A] opcional de perfil, y sin declararlo nada cambia | abierta / parcial |
| C05-01 | El umbral duro de V1 y V2 es un [A] de perfil con el valor recomendado por defecto, y sólo se puede endurecer | abierta / parcial |
| C05-02 | La hoja de ruta nombra a WSDOT y al valor; la fuente sigue fuera de `normas/` | abierta / parcial |
| C11-01 | El umbral de 6.0 m compara la abertura de la estructura, y la discrepancia entre las cuatro fuentes queda declarada en el paso | abierta / parcial |
| C14-01 | El registro normativo es una sola instancia | abierta / parcial |
| C09-01 | Las tres caras restantes de la ventana normativa y su camino de declarar corren bajo Tk | abierta / parcial |
| C09-02 | La serie de diámetros del concreto se transcribió por imagen de la única tabla legible de M 170M, y la ficha de la fuente dice cuáles no lo son | abierta / parcial |
| REDISEÑO-3-01 | La navegación es lateral y el Notebook se conserva por debajo, con la tira de pestañas retirada por estilo | abierta / parcial |
| T0-01 | Los PDF de normas se encuentran por `NORMAS_DIR`, con caída a `normas/`; las dos fuentes nuevas viven sólo en el repositorio de normas | diferida / declarada |
| T0-02 | El código de paso del tirante crítico es `F4.YC`; `F4.YC_RECT` sigue resolviendo como alias, y el índice de fórmulas se regeneró con la corrida que hay | abierta / parcial |
| T0-03 | La hoja de ruta declara desde T-0 cosas que el código todavía no hace: el conjunto de aceptación de la Familia B y cuatro enmiendas prospectivas | diferida / declarada |
| T0-04 | Los `INF-` del tracker llevan el número del INFORME, no el de los prompts; cuatro no tienen prompt, y la severidad es una propuesta | diferida / declarada |
| T2-01 | `S = 0` se admite y se dice con un objeto propio; la pendiente adversa y `S_cauce = 0` siguen fuera, y queda una discontinuidad con la convención de PC-06 | abierta / parcial |
| T2-02 | `borde_libre_bajo_tw_ahogante` queda en `no_cumple` por decisión del dueño; `aviso` es una alternativa barrible, continua en el TW, que hace dimensionar A-02 en la corrida estrecha | abierta / parcial |
| T2-03 | La sección medida del receptor entra por `--datos-externos` como un objeto, no como columnas del CSV; y el aviso de sección adoptada sale también en la vía 3 | diferida / declarada |
| T2-04 | `regimen_v2b` y `hw_entrada_fuera_de_rango` reciben valor de archivo pero siguen siendo [A], no [C]; la «nota de Ks·S de la Tabla A.1» no existe, y la tabla no tiene filas de tubo con aleros | abierta / parcial |
| T2-05 | El ejemplo publicado de HDS-5 (Design Guideline 1) se reproduce dentro de la tolerancia salvo cinco casillas censadas; las filas de metal corrugado se comparan por intervalo, y ninguna fila toca la transición | abierta / parcial |
| T2-06 | HDS-5 §5.3.3 presenta dos indicadores de sedimentación y la aplicación evalúa uno: el segundo necesita el n del cauce natural, que no es un dato del proyecto | cerrada |
| T2-07 | La aceptación de T-2 no se escribió en rojo antes del código: se midió después; 34 de sus 160 tests valen antes y después, y quedan 28 mutantes vivos, censados | diferida / declarada |
| T4-01 | El espesor del TMC es profundidad de corrugación más plancha; el del HDPE sale del diámetro exterior máximo de AASHTO LRFD, y dos tamaños se quedan sin fila | diferida / declarada |
| T4-02 | El tope de diámetro es el de la norma de producto —en concreto, el último diámetro con diseño estándar—; la disponibilidad de mercado es opcional y sólo puede bajarlo | diferida / declarada |
| T4-03 | `v_max_tmc` es [A] con ventana y `v_max_hdpe` sigue [C]: los dos valen 4.572 m/s y no son la misma cosa | diferida / declarada |
| T4-04 | La matriz de durabilidad filtra de verdad, con ensayos opcionales que entran por `--datos-externos` y no por `CLAVES_EXTERNAS` | diferida / declarada |
| T4-05 | `sucs_fundacion` tiene consumidor: el aviso de marco, con el conjunto de suelos declarado y no inventado | diferida / declarada |
| T4-06 | `DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO` se conserva sin consumidor: la «rama inactiva» de la hoja de ruta no existe y no se le inventa una | cerrada |
| T4-07 | El n de Manning del HDPE es [C] de HDS-5 (0.009 a 0.015): la cadena esperaba WSDOT Tabla 4-1 o un [A] de 0.009 a 0.013 | diferida / declarada |
| T4-08 | Entrada obligada de T-5: la plancha adoptada del TMC no cumple el factor de flexibilidad hasta su tope, y `espesor_pared` de TMC y HDPE es una ENVOLVENTE geométrica | diferida / declarada |
| T4-09 | El suelo agresivo para el acero se lee de AASHTO LRFD por analogía y por defecto avisa; EG-2013 507.10 se aplica entera; los ensayos no entraron al censo de variables | diferida / declarada |
| T4-10 | Un dato que falta en un candidato anterior bloquea la aceptación de uno posterior: el «caso mixto» de PC-28 cambia | diferida / declarada |
| T1-01 | De las ocho distribuciones del núm. 3.7.1 el programa ajusta tres, y la prueba χ² no se implementa | diferida / declarada |
| T1-02 | El tratamiento FEN `dos_poblaciones` se puede declarar y no se evalúa | diferida / declarada |
| T1-03 | V8 (evento extremo) todavía no pide su caudal a la hidrología | diferida / declarada |
| T1-04 | La hidrología entraba sólo por la CLI; desde UI-1 la ventana y la sesión la conocen, y desde VE-4b el pre-vuelo anticipa lo que detendría la Fase 1-bis — Cerrado (UI-1 y VE-4b) | cerrada |
| T1-05 | Lo que el prompt de T-1 suponía y el Manual no trae | diferida / declarada |
| VE5-MH-01 | La ponderación de C por subáreas tiene fuente [C] y no se implementa: pide cambiar el contrato | cerrada |
| T1-06 | `MetodoNoEvaluableError` admite un rótulo propio para la hidrología | diferida / declarada |
| T1-07 | De las seis filas de la Tabla Nº 05 se implementan cuatro: Izzard y onda cinemática quedan diferidas — Cerrado (VE-5, lote mh) | cerrada |
| T1-08 | El método racional modificado no estaba implementado: de él se tomaban la fórmula de Témez y el coeficiente K — Cerrado (VE-2) de 10 a 770 km² | cerrada |
| T1-09 | CERRADA: declarar `serie_sin_fen` cuando da menos lluvia que la serie completa detiene el cálculo del punto | cerrada |
| T6-01 | El diseño corre con la longitud aproximada al fondo; la longitud entre cabezales a la clave se imprime y no la sustituye | diferida / declarada |
| T6-02 | M7 acota la pendiente del cauce a la banda de T-2 y V10 juzga la que quedó: V10 sólo se incumple con una pendiente declarada | diferida / declarada |
| T6-03 | El desnivel de entrega (0.0 m) y el esviaje máximo (45°) son adopciones: ninguna fuente da el número del primero, y el del segundo es una analogía | diferida / declarada |
| T6-04 | `bombeo` y `peralte` entran sólo por el JSON de datos externos, y sólo los lee el método por extremo | diferida / declarada |
| T6-05 | La fuente sostiene la superposición aproximada del barril; medir al fondo es elección del proyecto, y no es el lado seguro por construcción | diferida / declarada |
| T8-01 | El apron de HEC-14 es contraste y no regla; el espesor adoptado queda siempre bajo su piso, y la decisión queda preparada | abierta / parcial |
| T8-02 | La Tabla N° 11 decide si se reviste la salida, y no revestir es lectura del proyecto | abierta / parcial |
| T8-03 | La protección de entrada declara la clase de revestimiento y lo que se protege; ninguna fuente de `normas/` le da dimensiones | abierta / parcial |
| T8-04 | La hoya de socavación es HEC-14 Cap. 5 y no el 3; la duración y la referencia de hs las declara el proyecto | abierta / parcial |
| T8-05 | El filtro es un requisito declarado; EG-2013 no lo obliga, y su nota (5) vale para la fila | abierta / parcial |
| T8-06 | La aceptación de T-8 se escribió después del código; el rojo se midió contra la base y la mutación de M6 se midió con el arnés | diferida / declarada |
| T8-07 | Rige la envolvente de Laushey y de HEC-14, y alcanza al tamaño de la piedra; fuera de la Tabla 10.1 son cotas inferiores | cerrada |
| T8-08 | El tirante de borde no está digitalizado: con la velocidad al crítico el contraste con la Tabla N° 11 no concluye | abierta / parcial |
| T8-09 | La velocidad de salida salta en la banda en que n máximo da flujo subcrítico y n mínimo lo daría supercrítico: es de M4 y sólo se avisa | abierta / parcial |
| T8-10 | La nota (5) b de la Tabla 511-06 se lee sólo para la columna «>50», y las filas «arcilla (no coloidal)» de la Tabla N° 11 se clasifican por su nombre: dos lecturas que esperan una fuente | abierta / parcial |
| T8-11 | Lo que la segunda auditoría pidió y no se hizo: techos físicos para los datos de la Fase 6, y la cadena numérica en el JSON | diferida / declarada |
| T8-12 | La pasada de correcciones: el rojo se escribió primero y se remidió, y las decisiones del dueño llegaron por el orquestador | diferida / declarada |
| T5-01 | La Fase 8 que decide si el escalón existe corre a nivel de perfil, detrás de V9 y solo si todo lo anterior cumple | diferida / declarada |
| T5-02 | De M 170M solo se lee la D-load de la Clase II, y un tubo que pida más BLOQUEA el punto | diferida / declarada |
| T5-03 | El TMC sube de plancha dentro de su corrugación, la Tabla 507-01 del EG-2013 pone el piso, y la plancha elegida no se devuelve a la geometría | cerrada |
| T5-04 | El TMC rige por LRFD y A796 es solo contraste: el expediente de referencia «VARIOS» se reproduce, y su H-20 no es el HL-93 | diferida / declarada |
| T5-05 | El HDPE se calcula con tres lecturas declaradas, y sin el perfil del fabricante no tiene veredicto | diferida / declarada |
| T5-06 | La carga viva HL-93 atraviesa el relleno por 3.6.1.2.6, y los pesos que cargan no son los que estabilizan | diferida / declarada |
| T5-07 | Del marco se calcula la demanda, y el pórtico se difiere | abierta / parcial |
| T5-08 | El caso de la auditoría de T-4 deja de dimensionarse con la fabricación de archivo: cambio declarado y aprobado por el dueño | diferida / declarada |
| T5-09 | Los valores de archivo de los [A] de la Fase 8 NO son todos «lo más desfavorable», y cada uno dice qué es | diferida / declarada |
| T5-10 | Sin el perfil del fabricante el HDPE queda «no verificado con un producto real», no se adopta, y el punto no sale «no factible» | diferida / declarada |
| T5-11 | La carga viva bajo relleno alto se conserva: el permiso de 3.6.1.2.6a no se toma en silencio | diferida / declarada |
| T5-12 | El tubo de concreto se verifica con el Tipo 3 y el Tipo 4 se imprime al lado: la correspondencia con el EG-2013 es lectura del proyecto, y tiene una condición | diferida / declarada |
| T5-13 | El pandeo general del HDPE va con el módulo de la vida de diseño, y rige el mayor de dos términos | diferida / declarada |
| T5-14 | Lo que las dos auditorías adversariales de T-5 encontraron, lo que se corrigió y lo que se refutó | diferida / declarada |
| T3-01 | La progresión de secciones es la decisión del dueño; la de la cadena T no se activa | abierta / parcial |
| T3-02 | La embocadura del marco es la de aletas de 30° a 75°, la de hoy; la de cabezal recto se midió y da otra carga | abierta / parcial |
| T3-03 | VC2 avisa y no detiene, con la tolerancia de una placa de concreto del EG-2013 por analogía | abierta / parcial |
| T3-04 | El remanso aguas arriba del canal es una cota inferior, no un perfil, y sin la sección medida no se evalúa | abierta / parcial |
| T3-05 | V6 con N > 1 publica el reparto, el tabique y el ancho total, y sigue sin aceptar la multicelda | abierta / parcial |
| T3-06 | La geometría del marco queda en `modelos.GeometriaMarco` para la Fase 8 y el cabezal; M8 no se toca | abierta / parcial |
| T3-07 | Con la embocadura del cajón declarada, R4 ya no frena una fila de cajón para el ke del TUBO; la frena el consumidor | abierta / parcial |
| T3-08 | V7 del marco no pesa el concreto (DC = 0): de eso cuelgan la progresión corta y el espesor | cerrada |
| T3-09 | El n del marco es la fila del cajón de la Tabla B.1 del HDS-5 [C]; la errata de la Tabla N° 09 se sostiene en su página | abierta / parcial |
| T3-10 | G1 del marco avisa cuando sólo falta la cobertura adoptada por analogía | abierta / parcial |
| T3-11 | `espesor_pared_cajon` queda [A] aunque su piso sea de una norma peruana | diferida / declarada |
| T3-12 | Las correcciones de la auditoría se escribieron antes del código, y su rojo se midió | abierta / parcial |
| T9-01 | La sección de la cuneta: el mínimo de la región muy lluviosa de la Tabla Nº 34, con el talud exterior como elección declarada | diferida / declarada |
| T9-02 | El aporte por metro: con el tramo conocido, Q / s; sin él, q · b con la longitud implícita avisada | diferida / declarada |
| T9-03 | VB1 por tramo: el extremo es el inicio declarado o la obra anterior (B, o A por la decisión C); sin extremo, es un bloqueo | cerrada |
| T9-04 | Cuatro ecuaciones del ejemplo del Manual no reproducen la geometría que nombran, y no se usan | diferida / declarada |
| T9-05 | La pendiente de la cuneta es un dato del trazo: no se deriva del CSV, y fuera de la banda del Manual se avisa con el mínimo del DG-2018 al lado | diferida / declarada |
| T9-06 | La aceptación de T-9 se escribió después del código; el rojo se midió contra la base | diferida / declarada |
| T9-07 | VB2: la condición literal del Manual, el caudal de aporte contra la capacidad de la cuneta | diferida / declarada |
| T9-08 | El periodo de retorno del aporte es el del punto, y la fila del alivio es una envolvente declarada | diferida / declarada |
| T9-09 | Las lecturas del proyecto en la Fase 10 son `Interpretacion` del registro, y tres dudas del auditor quedan dichas | diferida / declarada |
| T9-10 | Las correcciones de T-9 se escribieron después del código; el rojo se midió contra la FASE A | diferida / declarada |
| T9-11 | La mutación de la integración: 262 de 288 en M10 y 78 de 78 en la Fase 10 de `servicio`; los vivos, censados | diferida / declarada |
| T7A-01 | La Fase 9 por punto no se alcanza en una corrida de expediente: la detienen TRES capas, y abrir la puerta de `ancho_derecho_via_m` no quita ninguna | diferida / declarada |
| T7A-02 | La embocadura es de perfil y gobierna la coherencia del marco; en el tubo la fuente no distingue y nada se mueve; la caja receptora no se modela y se avisa | abierta / parcial |
| T7A-03 | Los aleros llevan el coseno de su ángulo con la bajada del talud: con esviaje, los dos aleros de un cabezal miden distinto | abierta / parcial |
| T7A-04 | Las reglas del predimensionamiento son [A] en el extremo de más material, y eso NO es el lado seguro de la estabilidad | abierta / parcial |
| T7A-05 | El desplante de salida y el dentellón bajan hasta la socavación con el margen de AASHTO 12.6.5, leído como aplicable al cabezal | abierta / parcial |
| T7A-06 | La longitud entre cabezales queda cerrada con el relleno retenido, da también la de metrado, y no sustituye a la del diseño | cerrada |
| T7A-07 | La aceptación de T-7a se escribió después del código; el rojo se midió contra la base | diferida / declarada |
| T7A-08 | Los mínimos de E.050 y de E.060 15.7 son [N→] para un cabezal vial, y la hoja de ruta los rotula [N] | abierta / parcial |
| T7B-01 | V5 mide el embalse con un plano horizontal: el perfil de remanso está nombrado y no implementado | cerrada |
| T7B-02 | V8 juzga «no colapsa» por el desborde de la plataforma, que es la lectura más exigente; el desborde admitido no estaba implementado (lo está desde VE-4d) | cerrada |
| T7B-03 | El cabezal se calcula como muro de semigravedad en voladizo, por metro y en la sección llena: es hipótesis del proyecto | diferida / declarada |
| T7B-04 | La capacidad portante es la de terreno horizontal, zapata corrida y sin factor de profundidad; las tablas de talud de AASHTO no se transcribieron | diferida / declarada |
| T7B-05 | Sin drenaje declarado el relleno se calcula lleno de agua: es el valor de archivo, y deja la condición sísmica sin evaluar | diferida / declarada |
| T7B-06 | Mononobe-Okabe solo dentro de su dominio: con el k_h de archivo la condición sísmica no se evalúa | diferida / declarada |
| T7B-07 | E4 y E5 (estabilidad global del muro y del talud) se imprimen diferidas al expediente | cerrada |
| T7B-08 | Las solicitaciones por elemento para T-7c son las de la sección de arranque, con tres aproximaciones declaradas | cerrada |
| T7B-09 | Con la regla de predimensionamiento de T-7a el cabezal de A-01 no pasa el deslizamiento del marco que rige: medido, no corregido | cerrada |
| T7B-10 | La aceptación de T-7b se escribió después del código; el rojo y la mutación se midieron | diferida / declarada |
| T7B-11 | La orientación del muro frente al tráfico sigue siendo un dato de corredor: no se deriva del esviaje de cada punto | cerrada |
| T7B-12 | Declarados, V5 y V8 se evalúan también a nivel de perfil; y el pre-vuelo de expediente anuncia el freático | diferida / declarada |
| T7B-13 | El cierre de T-7b aplicó las diez correcciones de la auditoría: el datum del freático, V5 por cota, V8 a presión, la cuña de tanteo, el agua y el régimen | diferida / declarada |
| T7B-14 | El cabezal se calcula como muro que CEDE; el que no cede está en la ventana y no implementado, y la interfaz de T-7c lo marca | cerrada |
| T7C-01 | Rige AASHTO LRFD Sección 5 y E.060 contrasta: dos marcos que no se cruzan, y en los mínimos, el más exigente | abierta / parcial |
| T7C-02 | Los elementos se arman con el empuje en reposo, y lo que esa elección no resuelve | abierta / parcial |
| T7C-03 | El cortante se verifica con el procedimiento simplificado donde la fuente lo permite; fuera de él no se evalúa, y la pantalla se trata como losa | diferida / declarada |
| T7C-04 | Los aleros se arman en su arranque; su zapata y sus secciones intermedias no | cerrada |
| T7C-05 | Sin el análisis químico ni la categoría del acero, el recubrimiento con que se arma es la cota más exigente, no los 70 mm del encargo | diferida / declarada |
| T7C-06 | El desarrollo y los empalmes de las barras no se evalúan; la fisuración de 5.6.7 se evalúa con la clase de exposición que declare el Propietario | cerrada |
| T7C-07 | La zapata se arma con presión de contacto lineal y el talón con el peso entero: no son las solicitaciones de zapata de la interfaz de T-7b | abierta / parcial |
| T7C-08 | La aceptación de T-7c se escribió después del código; el rojo y la mutación se midieron | diferida / declarada |
| T7C-09 | El cabezal de gravedad en ciclópeo se juzga por tracciones nulas, solo en la condición estática, y su zapata no se verifica | abierta / parcial |
| T7C-10 | El rótulo por ámbito de E.060: lo que T-7c usa es [N→]; el 0.30 m de 22.7.4 pasa a criterio [N→] en el cierre, y las cuantías de 14.3.1 siguen como constante | abierta / parcial |
| T7C-11 | El modificador de carga η no entra en el cabezal: la fuente lo sostiene, pero el cambio no es acotado | cerrada |
| T7C-12 | La pantalla y el alero integran cada diagrama por encima del arranque; el incremento sísmico se reparte con el diagrama lineal de su resultante | cerrada |
| T7C-13 | El cierre de T-7c aplicó las doce correcciones de la auditoría | cerrada |
| T7V-01 | V8 con el caudal que no cabe en flujo uniforme compite con el perfil de la lámina; el escalón de la regla de E-A en 1.2 D sigue ahí y lo cubre la guardia | abierta / parcial |
| T7V-02 | El η de AASHTO 1.3.2.1 es del cruce: el cabezal lee el mismo η_I que el conducto, y η_D y η_R son suyos | abierta / parcial |
| T7V-03 | El piso de la zapata armada se construye con la lectura de A8: 300 mm al eje de la capa inferior, con el recubrimiento con que se arma y la mayor barra del catálogo | abierta / parcial |
| T7V-04 | La aceptación de la verificación se escribió con el código; el rojo se midió contra la base | diferida / declarada |
| T10-01 | El objetivo de EXT-8 (< 15 KB y < 10 páginas por punto) no se alcanza sin perder sustento: lo repetido se quitó y se midió | diferida / declarada |
| T10-02 | El índice de fórmulas se genera con dos corridas de PRUEBA que sí dimensionan, y no imprime los valores que un módulo escribe en una procedencia | abierta / parcial |
| T10-03 | V4b, V6 y V9 ganan paso, y el censo de lo que no puede tener fundamento queda vacío | abierta / parcial |
| T10-04 | El censo JSON ↔ memoria se mide por clave, y tres claves de texto se imprimen de otra forma | abierta / parcial |
| T10-05 | Lo que el dueño decidió no hacer se imprime como ALCANCE, en las tres vistas | cerrada |
| T10-06 | El anexo de sensibilidad imprime la ventana y no recalcula: el barrido sigue siendo PF-3 | abierta / parcial |
| T10-07 | La aceptación de T-10 se escribió después del código; el rojo se midió contra la base | cerrada |
| T10-08 | Las correcciones de la auditoría adversarial de T-10 | cerrada |
| T11-01 | El juego de prueba entra sólo por las puertas de la CLI y no rellena ningún vacío del archivo | abierta / parcial |
| T11-02 | La lista exacta de lo que detiene una etapa se MIDE sobre dos bases, y el contrato de entradas la repite en su §7 | abierta / parcial |
| T11-03 | El escalón que no cabe bajo la subrasante es «no factible por rasante», con el delta de 7.A sólo cuando es geometría pura | abierta / parcial |
| T11-04 | Validación externa: HDS-5 y HEC-14 contra sus ejemplos resueltos; HY-8 sólo como procedimiento, con la tolerancia que el dueño aceptó | abierta / parcial |
| T11-05 | La sensibilidad se mide con el barrido de PF-3 sobre el juego, una clave a la vez, y la lista se deriva del censo | abierta / parcial |
| T11-06 | La hidrología calculada entra al índice de fórmulas con una tercera corrida de prueba | abierta / parcial |
| T11-07 | El alcance declarado completa lo que el dueño dejó fuera | abierta / parcial |
| T11-08 | La aceptación de T-11 no se escribió en rojo primero | diferida / declarada |
| T11-09 | Tres correcciones de formato y transparencia que tocan el programa: `HW_salida_m`, la fila A7 y el tipo de cabezal del resumen | abierta / parcial |
| T11-10 | El lado alto de la ventana de `n_manning_cajon` no se puede declarar | abierta / parcial |
| T12-01 | Los PDF de normas viven sólo en el repositorio de normas; la historia de git los conserva | abierta / parcial |
| T12-02 | El material de proceso vive en `proceso/`, fuera del entregable, y sus tests con él | abierta / parcial |
| T12-03 | La advertencia de fixture la pone el generador de la línea base, no el programa | cerrada |
| T12-04 | La memoria en dos vistas de la misma corrida; la ventana exporta las dos desde UI-2 | abierta / parcial |
| T12-05 | Licencia «todos los derechos reservados», `pyproject.toml` sin empaquetado y el README de usuario | cerrada |
| T12-06 | La aceptación de T-12 no se escribió en rojo primero | cerrada |
| T12-07 | Las correcciones de la auditoría de T-12: el entregable se sostiene solo y la resumida no pierde lo que la completa dice a propósito | cerrada |
| UI1-01 | Cómo entra la hidrología a la ventana: cinco decisiones de UI-1 y una premisa refutada | abierta / parcial |
| UI1-02 | Tres conductores de ventana real se habían quedado atrás de T-3, y el editor de la pestaña 2 sólo nombra filas de la primera tabla | abierta / parcial |
| UI2-01 | La memoria resumida en la ventana: cinco decisiones de UI-2 | abierta / parcial |
| UI2-02 | El cabezal del proyecto en la pestaña 4, con el texto de la CLI | cerrada |
| UI2-03 | Las correcciones de la revisión independiente de UI-2: el hijo del PDF y lo que la ventana promete de él | cerrada |
| UI3-01 | Dónde corre el barrido de la ventana: en un proceso hijo, la CLI con la sesión de la ventana | abierta / parcial |
| UI3-02 | Lo que la revisión independiente de UI-3 encontró: una sesión que no reponía claves enteras, y la regla del botón fuera de src/ | abierta / parcial |
| UI3-03 | Una clave entera escrita como texto se rechaza en TODAS las puertas que declaran; sólo la frontera del JSON la lee como entero | abierta / parcial |
| UI4-01 | El recorrido de extremo a extremo, y las tres cosas que encontró o heredó | abierta / parcial |
| UI4-02 | Las capturas y el README salen del recorrido; lo que de `CLAUDE.md` queda para el dueño | cerrada |
| UI4-03 | Lo que la revisión independiente de UI-4 encontró: el hijo que ya terminó al cerrar y un ciclo de sesión que no distinguía «repuesto» de «por defecto» | cerrada |
| UI5-01 | Lo que las cuatro decisiones dejan abierto | abierta / parcial |
| UI5-02 | Lo que la revisión independiente de UI-5 encontró: una implicación al revés, la pestaña 2 sin repintar y un temporal de nombre fijo | cerrada |
| UI5-03 | Lo que la verificación de la revisión de UI-5 encontró: la hoja de ruta en la remisión, el borrador de la pestaña 2, su motivo y los permisos | cerrada |
| VE1-01 | La validación externa confirmó tres defectos: la progresión declarada se recorre tal cual (D1), V7 no lee el nivel freático (D2) y la hoja de ruta sigue mal en dos textos (D3) | abierta / parcial |
| VE1-02 | Las decisiones del dueño que la validación externa dejó a la vista, sin tomarlas | cerrada |
| VE2-B | La velocidad de erosión resuelve su propio tirante con n mínimo | cerrada |
| VE2-A | La columna del n del concreto es una elección [A] | abierta / parcial |
| VE2-G | Los diámetros son los designados por la norma de producto | abierta / parcial |
| VE2-C | V7: el nivel de agua de diseño es una elección [A] del Propietario | abierta / parcial |
| VE2-E | Aviso de consistencia de la serie de lluvias, sin umbral — Cerrado (VE-2) | cerrada |
| VE2-F | Método racional modificado de 10 a 770 km² — Cerrado (VE-2), con tres lecturas declaradas | cerrada |
| VE2-D | Factor de intervalo fijo de la serie de 24 h como criterio [A], con 1.00 — Cerrado (VE-2) | cerrada |
| VE2-01 | Lo que seguía mal en la hoja de ruta después de VE-2 (lo corrigió el dueño, 2026-11-18) | cerrada |
| VE2-02 | Lo que VE-2 dejó diferido, reunido | diferida / declarada |
| VE2-03 | Lo que la revisión independiente de VE-2 encontró y se corrigió (A1, M3, M4, B1, B3, B4) | cerrada |
| VE2-04 | V3 no mira la velocidad de salida bajo control de salida (M1 de la revisión independiente de VE-2) | diferida / declarada |
| VE2-05 | Lo que la verificación de las correcciones de VE-2 encontró (N1 a N7) | cerrada |
| VE3-01 | Bajo control de salida V3 juzga la mayor de `V_erosion` y `V_salida` (cierre de VE2-04) | cerrada |
| VE3-02 | Los parámetros del suelo de fundación son [S] pendientes de ensayo (cierre de lo que VE2-05 dejó al dueño) | cerrada |
| VE3-03 | M9 contra ejemplos publicados (Caltrans BDP 11.2.2, CDOT Ex. 11) | abierta / parcial |
| VE3-04 | M8 contra ejemplos publicados (ACPA, USACE, PPI) | abierta / parcial |
| VE3-06 | VC3: las pérdidas de la obra contra el desnivel del perfil del canal (Familia C) | cerrada |
| VE3-07 | El remanso del canal por paso directo (Familia C) | abierta / parcial |
| VE3-05 | El cabezal se dimensiona: la zapata crece por el talón (estabilidad) y en peralte (armado) | abierta / parcial |
| VE3-08 | Ensayos de diseño del conducto: H4, H2, H6 y H3 (VE-3.11) | abierta / parcial |
| VE3-09 | El diámetro gobernado por el nivel del receptor se dice (decisión 8 del dueño, VE-3.13) | cerrada |
| VE3-10 | Clases III a V del tubo de concreto desde una fuente secundaria, con tope de diámetro por clase | cerrada |
| VE3-11 | El hueco 1.0 ≤ H < 2.0 ft del tubo de concreto no se implementa | cerrada |
| VE3-12 | El cortante fuera de 5.7.3.4.1 se verifica con el procedimiento general de 5.7.3.4.2 (VE-3.14, bloque 1; H-2 de los ensayos) | abierta / parcial |
| VE3-13 | El bucle de la zapata se detiene en el tope y prueba la punta (VE-3.14, bloque 2; H-5, H-6, H-12) | abierta / parcial |
| VE3-14 | La pantalla y el alero se dimensionan por su armado (VE-3.14, bloque 3; H-1) | abierta / parcial |
| VE3-15 | Con agua en el plano de empuje el sismo se evalúa (VE-3.14, bloque 4; H-3) | abierta / parcial |
| VE3-16 | Lo que la app dice de sí misma: alcance declarado y resumen de la CLI (VE-3.14, bloque 5; H-10, H-11) | cerrada |
| VE3-17 | Opciones 9, 10 y 13 del cabezal como alternativas de criterio; 11 y 14 con su alcance; 12 no se propone (VE-3.14, bloque 6) | diferida / declarada |
| VE3-18 | Decisiones 9 a 14 del dueño sobre el cabezal: valores de archivo y un solo régimen de k_h (VE-3.15) | abierta / parcial |
| VE3-19 | Los máximos anuales repetidos se avisan, sin umbral (H1 de la validación hidrológica con casos reales) | abierta / parcial |
| VE3-20 | El sismo del cabezal con los valores de archivo no cierra: causa, decisión y defecto de la §9.2 de la hoja de ruta | cerrada |
| VE3-21 | El trasdós drenado es el valor de archivo (VE-3.16, decisión del dueño del 2026-11-18) | abierta / parcial |
| VE4A-01 | E4 y E5 con el FS declarado del EMS: tres lecturas del proyecto y una fila sin valor (VE-4a, decisión del dueño del 2026-11-20) | abierta / parcial |
| VE5-M6-01 | La poza de enrocado de HEC-14 Sec. 10.1 entra donde el apron no llega (VE-4g, ítem 2 del censo) | abierta / parcial |
| VE5-M6-02 | La Figura 10.3 de HEC-14 está digitalizada: el TW sobre 1.0·D y el paso 5 de la poza (VE-5, lote m6) | abierta / parcial |
| VE5-M6-03 | La salida colgada se cierra con la caída recta de HEC-14 Cap. 11 (decisión del dueño: dentro del alcance) | abierta / parcial |
| VE5-M6-04 | Zampeado, uña y dentellón (ítem 30) y filtro granular (ítem 31) siguen pendientes [C] | diferida / declarada |
| VE5-MET-01 | Metrados referidos al EG-2013 y cuadro de compatibilidad rasante-alcantarilla (Fase 11, entregables 8 y 9; ítem 8 del censo) | abierta / parcial |
| VE4F-01 | La carga viva con relleno somero: la franja de 4.6.2.10.2, la cobertura mínima y un [A] sin valor (VE-4f) | abierta / parcial |
| VE5M9-01 | El muro que no cede se calcula: reposo en la estática, 1.0·k_h0 y h/2 bajo sismo (VE-5, ficha T7B-14) | abierta / parcial |
| VE5M9-02 | La cuña de tanteo sísmica donde M-O no es aceptable y sobre el trasdós inclinado (VE-5, ficha T7B-06) | cerrada |
| VE5M9-03 | Capacidad portante: la RC_BC de AASHTO sustituye a Meyerhof, forma y profundidad declarables, y la admisible de corredor con consumidor (VE-5, ficha T7B-04) | cerrada |
| VE6M9-01 | El cabezal ciclópeo se verifica bajo sismo (C8) y su zapata como voladizo de concreto simple (C7) (VE-6, ítem 10; T7C-09 (2)(3)) | abierta / parcial |
| VE6M9-02 | Las cuantías mínimas de muro de E.060 14.3.1 pasan a criterio [N→] (VE-6, ítem 29; T7C-10) | cerrada |
| VE6M9-03 | El alero se arma por sus propias secciones y su espesor se dimensiona por su armado (VE-6, ítem 9; VE3-14 H-13, T7B-08 (3), T7C-04) | abierta / parcial |
| VE6M9-04 | La orientación del muro y la distancia al borde de calzada, por punto (VE-6, ítem 28; T7B-11) | cerrada |
| VE7-01 | El alero se verifica como muro en sus franjas, con su zapata dimensionada y armada (VE-7; cierre de T7C-04) | abierta / parcial |
| VE5-CAT-01 | La rama de selva alta del TMC: [S] `region_natural` y la recomendación como piso del catálogo (cierre de T4-06) | cerrada |
| VE5-CAT-02 | La cuneta trapezoidal de la Tabla Nº 34 (región > 3000 mm/año): el fondo como campo de `seccion_cuneta` (cierre de lo que T9-01 dejó diferido) | cerrada |
| VE5-CAT-03 | Fase 0-bis: la licuefacción como resultado declarado del EMS, con bloqueo de expediente donde AASHTO 10.5.4.2 la exige | cerrada |
| VE5GUI-38 | La pestaña 2 se desplaza y las filas de exportación se parten solas | abierta / parcial |
| VE5GUI-40 | `S_conducto`, `bombeo` y `peralte` con campo y bandera | abierta / parcial |
| VE5GUI-39 | Temporales únicos al exportar y el fallo de escritura sin traza | abierta / parcial |
| VE5GUI-46 | Ids `FH.*` en el índice, la fila de rugosidad y los decimales de `D` | abierta / parcial |
| VE5GUI-43 | Los ensayos de durabilidad, quinta población del censo | abierta / parcial |
| VE5GUI-44 | Techos de transcripción de la Fase 6, como aviso (decisión pendiente de Fable) | cerrada |
| VE5GUI-49 | El hijo del PDF formatea la corrida embebida; las entradas de la pestaña 1 invalidan | abierta / parcial |
| VE5GUI-45 | Estado del expediente: discrepancias abiertas y corridas para comparar | abierta / parcial |
| VE5GUI-47 | El chequeo dimensional llega a M6–M10; los fundamentos sin ejercitar siguen | abierta / parcial |
| VE5GUI-48 | La integración continua corre los tests de ventana | abierta / parcial |
| VE6-01 | El nivel freático en M12 es de expediente y detiene el rubro, no el punto | cerrada |
| VE6-02 | La licuefacción se registra al lado de las demás faltas, no delante | cerrada |
| VE6-22 | El control de salida se rehace con la longitud entre cabezales: pasada de refinamiento con aviso | abierta / parcial |
| VE6-T7A03 | El cabezal paralelo a la vía en un marco: lo pide una fila de la Carta 11 del HDS-5 | abierta / parcial |
| VE6-34 | La progresión del catálogo: G1 dentro del bucle, V10 la detiene y el delta con V4 bajo control de entrada | abierta / parcial |
| VE7A-01 | La Carta 10 con cabezal normal empareja el ke por el borde de su fila (cierra VE6-T7A03 (4)) | abierta / parcial |
| VE7A-02 | La embocadura del marco se declara por punto (cierra VE6-T7A03 (1)) | abierta / parcial |
| VE7A-03 | C8 a media altura decide con cualquier criterio de tracción (cierra VE6M9-01 (b)) | abierta / parcial |
| VE7A-04 | C8 con k_v ≠ 0: el peso estabilizante va con (1 − k_v) (cierra VE6M9-01 (a)) | abierta / parcial |
| VE7A-05 | El empuje sísmico declarado por punto y cabezal donde el programa no lo calcula (VE5M9-02, VE3-15) | abierta / parcial |
| VE7A-06 | La geometría del talud de delante del cabezal, por punto (VE5M9-03) | abierta / parcial |
| VE7A-07 | La h_eq con el cabezal paralelo a la vía (VE6-T7A03 (3)) | abierta / parcial |
| VE7A-08 | El cabezal paralelo avisa el borde libre esviado de la losa del marco (VE6-T7A03 (2)) | abierta / parcial |
| VE7A-09 | Lo que dejaría de cumplirse con la longitud entre cabezales bloquea el expediente (VE6-22) | abierta / parcial |
| VE7A-10 | La `D` de M9 con los decimales del rótulo (VE5GUI-46) | abierta / parcial |
| VE7C-01 | `E060.22.10.2.2#VOLADIZO` con cita propia, firmada en A11 (C1; VE6M9-01 (c)) | abierta / parcial |
| VE7C-02 | `F9.LONGITUD`: la cercanía a la longitud aproximada es recomendación y la juzga el refinamiento (C2) | abierta / parcial |
| VE7C-03 | `COND-SELVA-ALTA` se resuelve con el [S] `region_natural` (C3; VE5-CAT-01) | abierta / parcial |
| VE7C-04 | La Fase 0-bis con sección propia en la memoria y clave `licuefaccion` en el JSON (C4; VE5-CAT-03) | abierta / parcial |
| VE7C-05 | `cli.py --estado-expediente`: las discrepancias abiertas y las corridas para comparar (C5; VE5GUI-45) | abierta / parcial |
| VE7C-06 | Corridas de referencia cuarta y quinta: de 39 fundamentos sin paso a 2 sin ninguna puerta (C6; VE5GUI-47; dictamen Fable (i-a), (i-c), C6) | abierta / parcial |
| VE7C-07 | test_c7: la sesión v3 difiere por clases con causa, no sólo por la huella (dictamen Fable (v)) | abierta / parcial |
| VE7C-08 | Comparador cerrado, línea de la Fase 0-bis en la CLI y la ventana sobre las cuatro (dictamen Fable (ii), (iii), (iv)) | cerrada |
| VE7B-01 | El arranque de la progresión lo valida M2 sobre el criterio (cierre de T11-03 (6)) | abierta / parcial |
| VE7B-02 | La pared del diámetro inglés convertido es la de su designado (cierre de VE2-G (2)) | abierta / parcial |
| VE7B-03 | La regla del escalón más bajo vale también en la rama «no cabe» (cierre de T11-03 (5)) | abierta / parcial |
| VE7B-04 | El delta del resguardo bajo control de salida, con el HW de entrada (cierre del abierto de VE6-34) | abierta / parcial |
| VE7B-05 | El largo del área cargada sobre el tubo de concreto somero: el del neumático, valor de archivo (VE4F-01) | abierta / parcial |
| VE7B-06 | El coeficiente de escorrentía ponderado por subáreas (cierre de VE5-MH-01) | abierta / parcial |
| VE7B-07 | La región pluvial de la Tabla Nº 34 como [S] opcional (cierre de VE5-CAT-02) | abierta / parcial |
| VE7B-08 | Lo que la Fase 11 no metra sale como renglón «no medido» (VE5-MET-01) | abierta / parcial |
| VE7B-09 | Las caras del pórtico que no se traccionan llevan el mínimo de 5.10.6 (T5-07 (3)) | abierta / parcial |
| VE7B-10 | El agua exterior del pórtico con el freático sobre la losa inferior (T5-07 (5)) | abierta / parcial |
| VE7B-11 | El pórtico que no cumple dice qué canto declarar, y no se lo auto-adopta (T5-07 (1)) | abierta / parcial |
| VE7B-12 | El acero del pórtico del marco se metra con sus armados (VE5-MET-01) | abierta / parcial |
| D2-01 | Las fichas de criterios viven en `src/criterios/`, y la huella de criterios cubre el catálogo entero | cerrada |
| D3-01 | `modelos.py` partido en el paquete `src/modelos/` | cerrada |
| D3-02 | `M11_reporte.py` partido en el subpaquete `src/modulos/M11_reporte/` | cerrada |
| D3-03 | `constantes_normativas.py` no se partió | diferida / declarada |
| EXT-8-06 | El presupuesto de `import cli` se mide con el mínimo de siete corridas | diferida / declarada |

---

# Parte I — Los 22 «deliberado sin documentar»

## SIS-A-04 · `cota_entrada_supuesta` rellena un vacío de dato dentro de M5

- **Qué se difirió:** la cota de fondo de entrada no se mide: se adopta desde
  `cota_terreno` por una regla que el proyectista declara.
- **Por qué:** el dato es del levantamiento topográfico y el expediente no lo
  trae por punto. Adoptarlo en silencio era el defecto; adoptarlo **declarado**
  es la única alternativa que no inventa una medición.
- **Qué haría falta:** la cota de fondo levantada en campo, por punto, como
  columna del CSV.
- **Dónde vive:** `src/criterios/verificaciones.py::origen_cota_fondo_entrada`

## SIS-A-13 · V2b (sedimentación / colmatación) — IMPLEMENTADA en S20

- **Qué se difirió:** ya nada, y conviene decir qué se difería y por qué dejó
  de estar bien difierido. La Fase 5 enuncia once verificaciones y el programa
  implementaba diez; V2b no existía en ninguna línea de código y en su lugar
  había una constancia: un párrafo que la memoria imprimía y que nadie tenía
  que contestar.
- **Por qué se cerró:** la premisa del diferimiento —«la colmatación no es un
  cálculo con umbral que este programa pueda evaluar»— era cierta **del Manual
  peruano** y falsa del cuerpo normativo que el proyecto ya aplica. El HDS-5
  3.ª ed., que vive en `normas/` y del que salen el control de salida y `h_o`,
  nombra los indicadores en su num. 5.3.3 «Sedimentation» (pág. impresa 5.11)
  y los nombra en términos de **dos números que el cálculo ya tiene**: la
  pendiente del barril frente a la del cauce natural, y la rugosidad de uno
  frente a la del otro. El primero se evalúa; el segundo exige el n del cauce,
  que no es columna, y queda declarado.
- **Qué haría falta:** dos cosas, y ninguna bloquea. (1) El **n de Manning del
  cauce natural** por punto, para evaluar el segundo indicador del mismo
  numeral. (2) Que la hoja de ruta recoja el 5.3.3: hoy su fila V2b atribuye
  la mitad [N] al «material sólido de arrastre», que es el asunto de V6, y
  afirma que «la norma no protege del riesgo real» sin acotar de qué norma
  habla. El defecto se reporta ahí, en su punto de uso.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v2b_sedimentacion` y
  `src/criterios_adoptados.py::acceso_mantenimiento_v2b`, que es la mitad [A]
  —el acceso de mantenimiento en planos— y que **detiene** la corrida mientras
  siga vacía: la obligación no se relajó al implementarse la otra mitad, se
  endureció.

## SIS-A-16 · Dos validaciones cruzadas de M0 que no son fila de la tabla de Sec. 1.5

- **Qué se difirió:** el diámetro implícito y la entrega por gravedad se
  validan aunque la tabla de Sec. 1.5 no las liste.
- **Por qué:** son contradicciones internas de la fila —el dato está y no puede
  ser— y dejarlas pasar sería aceptar un expediente incoherente por un
  tecnicismo de tabla. Se declaran como añadidos del proyecto, no como norma.
- **Qué haría falta:** que la Sec. 1.5 incorpore las dos filas, o que declare
  por qué no las quiere.
- **Dónde vive:** `src/modulos/M0_carga.py::_valida_cruzadas`

## SIS-A-17 · La GUI no exponía `--alcance`

- **Qué se difirió:** nada, ya. Estaba difierido de hecho y sin declarar: la
  ventana corría siempre «expediente» y `memoria_perfil.html` era inalcanzable.
- **Por qué:** se cerró en S17 exponiendo el selector, y la plantilla se elige
  con `cli.plantilla_por_alcance`, la misma función que usa `cli.main`.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `gui/app.py::_construir_tab_datos`

## SIS-A-18 · La sesión JSON no guardaba los criterios declarados

- **Qué se difirió:** nada, ya. Quien declaraba cinco criterios y volvía al día
  siguiente perdía las cinco decisiones sin aviso.
- **Por qué:** se cerró en S17. Se guardan valores **y procedencia**, y se
  reponen por la misma guardia que usan la ventana y la CLI, porque una sesión
  es un archivo que alguien pudo editar a mano.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/declaracion.py::restaurar_sesion`

## SIS-B-04 · «TW se calcula, no se mide» (Sec. 1.3) — IMPLEMENTADO en S20

- **Qué se difirió:** el procedimiento de tres pasos de Sec. 1.3 —Q del
  receptor → tirante normal del receptor → TW—. `Q_receptor_m3s` y `cota_TW`
  se validaban y no alimentaban nada: un CSV con las dos columnas llenas
  seguía exigiendo `--tw`.
- **Por qué se cerró:** el diferimiento se apoyaba en que faltaba un dato —el
  caudal del receptor— y en que el paso 2 necesita además la **sección
  transversal del receptor**, que no es columna. Lo segundo sigue siendo
  cierto y lo primero dejó de serlo: el dato es del Tablero 3.1 y el CSV lo
  admite. Lo que faltaba no era esperar: era **declarar la sección** como el
  vacío que es y escribir el procedimiento alrededor.
- **Qué haría falta:** el **levantamiento de la sección del receptor** en cada
  punto de descarga, que es una obra de terceros —el dren de la Junta de
  Usuarios— y que hoy entra como adopción de perfil con su ventana. Mientras
  no exista, la memoria dice que el nivel del receptor es una adopción; el día
  que llegue, el criterio deja de aplicarse. Falta además que la hoja de ruta
  lo recoja: su Sec. 1.3 pide correr Manning «en la sección del receptor» y ni
  la Sec. 1.1 ni la Sec. 1.2 la traen. El defecto se reporta ahí.
- **Dónde vive:** `src/modulos/M3_hidraulica.py::tw_seccion_1_3` (las cuatro
  vías, en orden de precedencia) y `src/criterios_adoptados.py::seccion_receptor`.
  `TW_receptor` sigue existiendo y sigue vacío a propósito: es la **última
  puerta**, la que detiene cuando el expediente no aporta ni el nivel, ni el
  caudal, ni la sección.

## SIS-B-05 · Entregable 5 (análisis de sensibilidad): su única API la consumían los tests

- **Qué se difirió:** nada, ya. `parametros_sensibilizables()` existía y solo
  la llamaban los tests; ningún bloque de alcance la declaraba diferida.
- **Por qué:** se cerró en S18 cableándola: la sensibilidad de cada criterio
  `[A]` llega hoy al documento.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modulos/M11_reporte/sitio_criterios.py::_sensibilidad_declarada`

## SIS-B-06 · `--plantilla memoria_perfil.html` sobre corrida de expediente

- **Qué se difirió:** nada, ya. La combinación descartaba 13 647 caracteres de
  pendientes mientras el docstring afirmaba que las dos plantillas «comparten
  el contrato de marcadores».
- **Por qué:** se cerró en S18 en las dos direcciones. `substitute` ya reventaba
  cuando la plantilla pide un marcador que M11 no entrega; la dirección
  contraria —M11 calcula contenido y la plantilla no lo imprime— **no se
  quejaba de nada**, porque `substitute` ignora los valores sobrantes. Ésa era
  la que perdía los 13 647 caracteres, y no tenía guardia.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modulos/M11_reporte/memoria.py::_exigir_que_la_plantilla_no_pierda_contenido`

## SIS-B-07 · `CriterioPendienteError.mensaje_gui` no tiene consumidor de producción

- **Qué se difirió:** conservar la propiedad sin cablearla.
- **Por qué:** es el único objeto ejecutable que fija la redacción que
  `CLAUDE.md` manda para esta excepción, y cablearla **degradaría** lo que la
  GUI muestra hoy: seis columnas (clave, etiqueta, concepto, fuente, fases,
  puntos) por la vía del `Bloqueo`, contra un solo dato. Además esa vía no es
  la más rica de dos: es la **única**. Lo comprobé vaciando el `valor` de los
  46 criterios y de todos los datos de sitio: `cli.correr` devuelve su informe
  sin levantar nada, con los bloqueos archivados. Ningún `CriterioPendienteError`
  alcanza el `except ErrorProyecto` de la ventana, porque los tres únicos sitios
  que lo levantan —`criterios_adoptados.valor`, `datos_sitio.valor` y
  `GeometriaCabezal.exigir_ancho_talon`— cuelgan todos de etapas envueltas por
  `_etapa`. (Sí corre otro código fuera de `_etapa` —`correr_cabezal` llama a
  `condicion_normativa_cabezal`, y varias fases piden `externos.valor`—: la
  conclusión se sostiene, pero decir «lo único que corre fuera de `_etapa` es
  `cargar_puntos`» era describir mal el archivo.)
- **Qué haría falta:** un consumidor que necesitara la frase corta y no el
  tablero. Hoy no existe y no se ve de dónde saldría.
- **Dónde vive:** `src/modelos/errores.py::mensaje_gui`

> **Defecto contra `CLAUDE.md`, corregido en S19.** La cláusula
> `CriterioPendienteError` de la taxonomía decía «La GUI la muestra como
> "falta declarar: `<clave>`"», y la GUI muestra algo estrictamente más rico.
> Quien leyera la constitución sin leer el código creería que la ventana
> imprime una sola línea.

## SIS-B-08 · `PeriodoRetorno.exigir_anios` no tiene llamador

- **Qué se difirió:** conservar la guardia sin consumidor.
- **Por qué:** es la única sentencia ejecutable del invariante «un TR ausente
  no se sustituye». `anios` está anotado `Optional[int]`; sin la guardia, el
  consumidor que llegue escribirá `tr.anios or 35`, que es el default
  silencioso que `CLAUDE.md` llama el peor error posible. Los cinco accesos de
  producción tratan el `None` y ninguno necesita el entero, porque el paso que
  sí lo necesitaría —«Tc.py + IDF con el TR de Fase 2», Sec. 1.1— ocurre fuera
  de este programa.
- **Qué haría falta, y es dos cosas:** (1) un consumidor, que aparecerá el día
  que el cálculo hidrológico entre al programa; (2) **un discriminante en
  `PeriodoRetorno`**. La guardia distingue mal sus dos ramas: `anios` es `None`
  por Familia C (falta el dato: `DatoFaltanteError('Q_m3s')`, correcto) y por
  punto fuera de alcance (es un puente: correspondería
  `DisenoNoFactibleError`, como en `M1_clasificacion.exigir_alcance`). Hoy no
  hay con qué separarlos sin oler el texto de `fundamento`, y el orden que M1
  documenta —`exigir_alcance` antes de leer el TR— deja la segunda rama fuera
  del camino. **La decisión sobre `exigir_anios` está cerrada; este límite
  queda declarado y sin cerrar**, y no se puede cerrar sin tocar el modelo, que
  no es trabajo de esta fase.
- **Dónde vive:** `src/modelos/proyecto.py::exigir_anios`

## SIS-B-09 · Constantes `NUMERAL_*` de módulo declaradas y nunca leídas

- **Qué se difirió:** nada, ya. Son ocho, no siete.
- **Por qué:** se cerró en S12 con un censo declarado y su razón.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/modelos/base.py::NUMERALES_DE_SECCION_SIN_LECTOR`

## SIS-B-10 · `legacy/Tc.py`: sin importadores, sin tests, sin barrido y sin estatus

- **Qué se difirió:** conservar un archivo de más de mil trescientas líneas y
  185 literales prohibidos que nadie importa, nadie prueba y ningún barrido
  recorre. (Eran 1320 antes de que esta sesión le añadiera su encabezado de
  estatus; los 185 literales sí siguen siendo 185, medidos con el detector del
  propio repositorio.)
- **Por qué, y no es nostalgia:** **no es código muerto, es otro programa.**
  La §1.2 de `docs/hoja_de_ruta_alcantarillas_v8.md` lo nombra por su nombre en
  la fila del caudal —«Caudal de diseño Q | m³/s | Tc.py + IDF con TR de Fase
  2»—, de modo que Q entra al calculador como columna del CSV y este archivo es
  la herramienta que la produce, aguas arriba y fuera de la corrida. Borrarlo
  dejaría al expediente sin la herramienta que produce una columna obligatoria.
  Sus literales están exentos **por directorio**, con la razón escrita y
  verificada por un test que barre el AST del repositorio buscando
  importadores: si alguien lo importa, la exención cae en rojo.
- **Qué haría falta, dicho entero porque no es inocuo:** tal como está
  commiteado **no corre aquí**. `matplotlib` es import de nivel superior y no
  está en `requirements.txt` (ni debe estarlo: no es dependencia del software
  calculado), y `plantilla_memoria.html`, que su encabezado anuncia «junto a
  este archivo», no existe en el repositorio. Para volver a ejecutarlo hacen
  falta las dos cosas. Para **borrarlo**: que la §1.2 deje de nombrarlo como
  origen de Q, o que su procedimiento entre al calculador.
- **Dónde vive:** `tests/test_sin_literales.py::DIRECTORIOS_FUERA_DEL_BARRIDO`

> **Defecto contra `CLAUDE.md`, corregido en S19.** La §GUI ordenaba «Leer esos
> archivos antes de escribir GUI», mandando a un programa que ya no se puede
> importar y cuyos ocho componentes están los ocho extraídos: `Tooltip` y
> `MarcoScroll` son el mismo código movido a `gui/componentes.py`,
> `CampoValidable` es su `_campo_validable` con la validación al escribir que
> pide la Sec. 4.3, y el patrón de plantilla `%%` vive en
> `M11_reporte.PlantillaHTML`.

## SIS-C-06 · `barrido()` solo recorría `src/`

- **Qué se difirió:** nada, ya. `cli.py` (8 literales) y `gui/app.py` (151)
  quedaban sin vigilancia.
- **Por qué:** se cerró en S16 metiéndolos al barrido con una regla estrecha y
  declarada para la capa de presentación.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_sin_literales.py::CAPA_DE_PRESENTACION`

## SIS-C-11 · El barrido solo miraba `.py`

- **Qué se difirió:** nada, ya. Las dos plantillas bajo `src/` quedaban fuera.
- **Por qué:** se cerró en S16 con una regla propia para las plantillas.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_sin_literales.py::PLANTILLAS`

## SIS-C-12 · El ejemplo de uso de M1 daba luces sin la salvedad que sí lleva el test

- **Qué se difirió:** nada, ya, **y el hallazgo se quedaba corto**. No era solo
  que el ejemplo diera las luces sin decir de dónde salen y con ids del fixture
  presentados como si fueran cruces reales: es que **no ejecutaba**. Llamaba a
  `clasificar_puntos` con dos de sus tres argumentos y abortaba en el primer
  punto con `CriterioPendienteError` sobre
  `umbral_area_quebrada_importante_ha`.
- **Por qué:** un ejemplo que no corre es peor que no tener ejemplo, porque el
  lector culpa a su entorno.
- **Qué haría falta:** nada para M1, y de paso se cerró más de lo que la ficha
  pedía. La primera versión de esta ficha decía que «los otros doce bloques
  `Uso` son fragmentos a propósito» — **y era falso**: los de `M0_carga` y
  `M10_espaciamiento` corren enteros. Era la misma especie de defecto que
  SIS-C-12 denuncia —una razón escrita que nadie ejecutó antes de escribirla—,
  cometida al cerrarlo. Hoy la suite **ejecuta los tres que se sostienen
  solos**, y un segundo test hace crecer la lista si alguien arregla otro. Los
  que quedan sí son fragmentos —parten de un `resultado` o un `material` que
  el llamante ya tiene—, medido ejecutándolos, no declarado.
- **Dónde vive:** `tests/test_M1_clasificacion.py::test_el_ejemplo_del_docstring_de_M1_ejecuta_y_da_los_TR_del_fixture`

## SIS-D-08 · `clase_sitio` es el único `[A]` con valor y sin sensibilidad

- **Qué se difirió:** nada, ya, **y el hallazgo se resolvió cambiando la
  pregunta.** El archivo estaba confesando el problema sin sacar la
  consecuencia: la razón escrita de por qué no declaraba sensibilidad era que
  «declarar un rango de clases alternativas sería fijar la respuesta antes de
  resolver la pregunta».
- **Por qué:** un valor que no puede declarar rango porque la pregunta no está
  resuelta **no es una elección: es un hecho que falta**. `clase_sitio` dejó de
  ser `[A]` y pasó a `[S]` sin valor, con `trazabilidad` en lugar de
  sensibilidad — que es exactamente la regla que separa las dos etiquetas en
  `CLAUDE.md`. Hoy: etiqueta `[S]`, `valor=None`, y la memoria declara que
  **no se ha ejecutado ninguna lectura**.
- **Qué haría falta:** el ensayo. La trazabilidad ya dice cómo se reproducirá
  la lectura cuando exista.
- **Dónde vive:** `src/criterios/sismo.py::clase_sitio`

## SIS-D-09 · `datos_sitio.py` no tenía guardia al importar

- **Qué se difirió:** nada, ya. `DatoSitio(trazabilidad='', etiqueta='A')` se
  construía sin error mientras el homólogo de criterios lo rechazaba.
- **Por qué:** se cerró en S15 con la guardia simétrica.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/datos_sitio.py::_coherencia_de_datos_sitio`

## SIS-D-12 · `v_max_hdpe` y `v_max_tmc` sin ancla `vacio_verificado`

- **Qué se difirió:** nada, ya.
- **Por qué:** se cerró en S14 consolidando las afirmaciones negativas.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `src/criterios/hidraulica.py::v_max_tmc`

## SIS-E-02 · M9 usaba `DatoInvalidoError` para validar argumentos internos

- **Qué se difirió:** nada, ya. Cuatro `DatoInvalidoError` validaban strings
  que produce el propio código: un fallo de programa presentado como problema
  del expediente.
- **Por qué:** se cerró en S16 separando las dos clases de fallo.
- **Qué haría falta:** nada. Cerrado. La razón vive en el bloque «POR QUÉ ESTE
  MÓDULO VALIDA ARGUMENTOS INTERNOS CON `DatoInvalidoError`», encima de las
  cuatro funciones que nombra.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_base.py::fs_requerido`

## SIS-E-04 · El único `raise` de la GUI valida un campo tecleado con `ValueError`

- **Qué se difirió:** conservar el `ValueError`, que **no** es de la taxonomía
  `ErrorProyecto`.
- **Por qué:** el campo lo teclea el usuario y el error se atrapa tres líneas
  más abajo, en sus dos llamadores, para pintarlo en el panel. Subirlo a la
  taxonomía lo haría viajar al informe como problema del expediente, que no lo
  es: es un renglón vacío en una caja de texto.
- **Qué haría falta:** nada. Es la decisión, y está fijada por un test que la
  rompería si alguien cambia el tipo sin tocar los dos llamadores.
- **Dónde vive:** `gui/app.py::_interpretar_valor_declarado`

## SIS-F-17 · Un test que no invocaba código de producción

- **Qué se difirió:** nada, ya. Reescribía la fórmula y se comparaba consigo
  mismo; contaba en el total y no protegía nada.
- **Por qué:** se cerró en S16 haciéndolo llamar a producción.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_M3_hidraulica.py::test_pendiente_que_produce_v_objetivo_de_cp3`

## SIS-F-19 · El `ValueError` de `escribir_valor_en_archivo` y los criterios multilínea

- **Qué se difirió:** nada, ya. El patrón de la regex no alcanza a los dos
  criterios de valor multilínea, y ese `ValueError` era lo único que impedía
  escribirles un escalar encima.
- **Por qué:** se cerró en S16 ejercitando el patrón sobre los dos casos.
- **Qué haría falta:** nada. Cerrado.
- **Dónde vive:** `tests/test_criterios_adoptados.py::test_la_escritura_permanente_se_niega_ante_un_valor_multilinea`

---

# Parte II — Lo que S19 encontró al escribir este registro

Tres cosas que ninguna de las tres auditorías nombra y que aparecieron al
verificar las veintidós fichas contra el código de hoy. Se anotan aquí porque
son de la misma especie —una decisión que el código toma y no dice— y porque
el sitio donde un revisor las buscaría es este.

## `M9_cabezal.combinaciones()` prometía un consumidor que no existe

- **Qué se difirió:** conservar la función sin llamador de producción.
- **Por qué:** las tres combinaciones (Resistencia I, Servicio I, Evento
  Extremo I) son `[N]` y esta función es su única forma ejecutable. Que la
  memoria las declare es una fase que no está escrita, no una llamada que
  falte.
- **Qué haría falta:** que M11 imprima las combinaciones vigentes, que hoy no
  imprime.
- **Matiz que hay que leer con esto**, o parece una contradicción: el registro
  normativo **sí la nombra** —las tres filas de `T_MP_COMBINACIONES` llevan
  `uso=Usada(por=(…, "M9.combinaciones"))`, y la ventana emergente se lo
  muestra al proyectista. No es una promesa incumplida: ese campo dice **qué
  símbolo lee la tabla**, no que una corrida pase por él, y esta función es en
  efecto la que lee la transcripción de esas etiquetas.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_base.py::combinaciones`

> Su docstring afirmaba «es la que M11 usa para declarar QUÉ combinaciones
> rigen», y `M11_reporte` no la referencia: sus únicos llamadores son cuatro
> tests. Es la misma forma de prometer un consumidor que el proyecto ya
> desterró en `ControlEntrada.HW_sobre_D` (SIS-B-02).

## La premisa de SIS-A-08 se había sustituido por otra premisa falsa

- **Qué se difirió:** nada. Es una corrección.
- **Por qué importa:** SIS-A-08 retiró de `MD.py` la frase «M5 todavía no
  existe en el repositorio» y la sustituyó por «la importación perezosa evita
  además un ciclo de importación en el arranque». **Eso también es falso:** M5
  importa `criterios_adoptados`, `constantes_normativas`, `modelos`, M2, M8 y
  `tolerancias`, y ninguno vuelve a MD. Sustituir una premisa falsa por otra no
  cierra el hallazgo: le cambia el hecho. La premisa original, además,
  sobrevivía **verbatim** en el docstring de `tests/test_MD.py`.
- **Qué haría falta:** nada. Cerrado en S19, con guardia.
- **Dónde vive:** `tests/test_MD.py::test_la_premisa_de_que_M5_no_existe_no_vuelve_como_afirmacion`

## Las referencias de prosa del manifiesto eran dos poblaciones, no una

- **Qué se difirió:** el cupo de referencias no verificables del manifiesto.
- **Por qué importa:** «de prosa» significaba «la fila no cita ningún símbolo
  **definido en el archivo de destino**», y eso mezclaba la fila que no nombra
  nada (hueco real) con la que nombra un símbolo que el archivo **usa** sin
  definir (verificable: basta exigir que el bloque de destino lo nombre). Al
  separarlas aparecieron dieciséis referencias desviadas que nadie buscaba,
  entre ellas dos nombres que el código ya no tiene.
- **Qué haría falta para llegar a cero:** que cada fila del manifiesto nazca de
  un objeto del registro normativo con id estable. Hoy el registro cubre C11,
  C12 y C02; el resto sigue en prosa. Quedan 32 filas sin identificador.
- **Dónde vive:** `tests/test_manifiesto_citas.py::test_toda_fila_que_cita_un_identificador_lo_nombra_en_su_destino`

---

# Parte III — Los seis parciales que la fase F5 heredó

`Plan_Fases` reclama a esta fase seis hallazgos que otras sesiones dejaron en
**Cerrado parcial**: cuatro normativos y dos de la suite. Ninguno se cierra
borrando código ni escribiendo prosa, y por eso conviene decir, uno por uno,
**qué falta exactamente y de qué clase de trabajo es**. Un «parcial» sin esa
frase se lee como pereza; con ella se lee como lo que es: una espera con
condición escrita.

## NOR-E060-02 · El acero en dos caras entre 200 y 250 mm

- **Cerrado:** la lógica. `ESPESOR_DOS_CAPAS_REFUERZO = 0.200` m (Art. 14.3.2)
  y `M9.requiere_refuerzo_dos_capas`: entre 200 y 250 mm el muro lleva dos
  capas aunque el acero por temperatura vaya en una cara, que es lo contrario
  de lo que la memoria imprimía.
- **Abierto:** la nota no tiene llamador de producción, porque su insumo es el
  espesor y el espesor sale de `predimensionamiento_cabezal`, que **sigue
  siendo un vacío declarado** (verificado hoy: `valor=None`, etiqueta `[A]`).
  Está censado en `M9_cabezal.FUNCIONES_SIN_CONSUMIDOR` junto a las otras
  siete funciones del num. 9.4, con la misma razón.
- **Qué haría falta:** que el proyectista declare el predimensionamiento del
  cabezal, y que `diseno_flexion_corte` deje de detenerse en
  `NotImplementedError`. Ninguna de las dos es trabajo documental.
- **Dónde vive:** `src/modulos/M9_cabezal/durabilidad.py::FUNCIONES_SIN_CONSUMIDOR`

## NOR-HDS-05 · Las tres condiciones de uso de h_o

- **Cerrado:** dos de las tres se **evalúan punto por punto** —los límites
  HW/D < 0.75 y HW/D < 1.2, como `H_O_HW_SOBRE_D_MIN` y
  `H_O_HW_SOBRE_D_CAUTELA`— y viajan a la memoria del punto junto a su HW.
- **Abierto:** la tercera —que el barril fluya lleno en la mayor parte de su
  longitud— no se puede evaluar sin un perfil de la lámina de agua. Está
  transcrita y **declarada como no evaluable** en
  `H_O_CONDICION_APLICACION`, y M4 lo dice en el punto de uso.
- **Qué haría falta:** el procedimiento de barril parcialmente lleno del
  Cap. III del HDS-5. Es implementar un método hidráulico, no redactar.
- **Evaluado en I1 (2026-09-12): el procedimiento SÍ es transcribible.** Se
  abrió el Cap. III de la 3.ª edición (fuente `HDS5_3ED`,
  `normas/hif12026.pdf`) y el paquete completo para la sesión que lo
  implemente —numeral y página de cada pieza (3.12/PDF 94 con la Ec. 3.7;
  3.24/PDF 106; Secc. 3.5), qué implementar en M4 y por qué M5 no cambia,
  y por qué los dorados no se fabrican— quedó ESCRITO en el bloque de
  comentario que precede a `H_O_CONDICION_APLICACION`, que es donde se va a
  pisar. La implementación es sesión propia con plan mode: toca
  `M4.control_salida`, que es motor validado.
- **Reabierta en EXT-0 (2026-09-20)** con argumento nuevo (`EXT-M-02`: el
  aviso convivía con un punto aceptado mientras el paso imprimía NO_CUMPLE,
  SIS-A-07; `EXT-M-01`: «M5 no cambia» era falso). La v8 §4.3 decidió
  «método no evaluable» por vía `Bloqueo`, diferible en perfil y no en
  expediente. **Cerrado parcial en EXT-3:** bloqueo, régimen y velocidad de
  salida (`modelos.MetodoNoEvaluableError`, `servicio._compuerta_metodo_h_o`,
  `ResultadoHidraulico.V_salida`); quedaba sólo el perfil (EXT-3b / E-A).
- **CERRADA en E-A (2026-09-21):** el perfil por paso directo existe
  (`M4.perfil_lamina`, `modelos.PerfilLamina`, pasos 4.3c/4.3d; siete citas
  nuevas de las págs. 3.12 y 3.36–3.38). Las tres condiciones se evalúan: la
  primera se mide (fracción llena contra `'fraccion_llena_mayor_parte'` [A]),
  bajo HW/D < 0.75 el HW es el del remanso o gobierna la entrada, y V1/V2
  salen del perfil. Lo que sigue sin hacer a propósito: Parte XXVIII (EA-01
  a EA-07).
- **Dónde vive:** `src/modulos/M4_control.py::perfil_lamina`

## NOR-PRO-04 · La norma a la que se difiere la verificación del TMC

- **Cerrado:** la **atribución**, y desde N1 **verificada**: ASTM A796/A796M-13
  está en `normas/` y en el registro (`fuentes.ASTM_A796`), y su num. 22.1
  nombra a A807/A807M como práctica de **instalación** (`ASTM_A796.22.1`).
  `DIS-HR-A807` quedó RESUELTA y la fila de la Fase 8 de la v8 corregida.
- **Cerrado también en I1 la mitad transcribible:** la relación
  diámetro/corrugación (`ASTM_A760.T1`, `AASHTO_M36.T6`, `CORR-TAMANOS-TMC`).
  El criterio sigue vacío a propósito: quién especifica el producto es el
  proyectista.
- **Cerrado en N1 lo que la fuente SÍ trae, y cambió de naturaleza lo que
  no:** la mitad (2) esperaba de A796 «la tabla de calibre por altura de
  cobertura», y **esa tabla no existe** (`SIN_TABLA_CALIBRE_POR_COBERTURA_A796`,
  con su ámbito): el espesor es la *salida* del procedimiento de los num. 7 a
  10 (`ASTM_A796.8.1.1.2#SELECCION`) y la cobertura mínima sale del num. 11.1
  (`ASTM_A796.11.1#PISOS`). Transcrito entero y verificado por imagen: las
  siete tablas SI de propiedades seccionales del catálogo (`ASTM_A796.T3` a
  `T17`), la carga viva por cobertura (`ASTM_A796.6.2.2.1`), los límites del
  factor de flexibilidad (`ASTM_A796.10.2`, `.10.3`) y las cargas por eje
  (`ASTM_A796.11.1`).
- **Abierto:** la mitad TMC sigue **sin valor**, ya no por fuente ausente sino
  porque cerrarla es **implementar el procedimiento** en M8
  (`seleccionar_clase_calibre`), con caso patrón y con los `[A]` que el
  procedimiento pide. La mitad concreto sigue esperando las Tablas 1 a 5 de
  M 170M. Y el hueco del generador hallado en I1b: `manifiesto.py` no emite
  las `CorrespondenciaDeTablas`.
- **Qué haría falta:** para el TMC, una sesión de cálculo que implemente los
  num. 6 a 11 de A796 sobre las tablas ya transcritas (dicho en el plan
  ANTES, con caso patrón y en commit propio); para el concreto, transcribir
  las Tablas 1 a 5 de M 170M por imagen.
- **Dónde vive:** `src/criterios/conducto.py::clases_producto_por_relleno`

## NOR-ANA-03 · La analogía de embocadura del HDPE

- **Cerrado:** la comparación que la ficha reclama está **declarada**. La fila
  alternativa (`Circular CM / Headwall`) vive en `sensibilidad`, y
  `verificacion_pendiente` declara la comparación completa entre las dos filas.
- **Corregido en I1b, y contra la propia ficha:** hasta I1b la declaración
  copiaba de NOR-ANA-03 que la fila adoptada da un HW **menor** (dirección
  insegura). La verificación adversarial la **midió** con las constantes del
  propio criterio y los dominios de M4, y la dirección es la contraria en los
  tres regímenes vigentes: no sumergida manda K (0.0098 > 0.0078), sumergida
  la diferencia 0.0019·q*²−0.02 es positiva en todo su dominio (q* ≥ 4.0; el
  cruce en q* = 3.245 queda fuera, que es donde la ficha evaluó), y la
  transición es una recta entre dos extremos donde el concreto ya es mayor.
  La ficha además enumera «c y Y ambos menores» cuando 0.0398 > 0.0379. El
  defecto se reportó **contra la ficha NOR-ANA-03** en el tracker; la
  adopción resulta conservadora en dirección, pero se sigue sosteniendo en el
  argumento físico, no en ese margen.
- **Abierto:** no se cambia de fila, y es una decisión, no una omisión. La
  adopción se sostiene en el perfil de pared en la boca —argumento físico que
  la ficha no refuta—, no en un margen de seguridad; elegir la fila del metal
  por su resultado sería sustituir una analogía por otra.
- **Qué haría falta:** el detalle constructivo de la embocadura. Es contenido
  de planos.
- **Dónde vive:** `src/criterios/hidraulica.py::hds5_embocadura_hdpe`

## SIS-F-01 · La GUI y sus tests de contrato

- **Cerrado en S19, y es la parte que faltaba dentro de la frontera:** las
  tres decisiones de `gui/app.py` que nadie ejercitaba —el estado con que se
  rotula cada criterio, la leyenda de etiquetas y de dónde saca la tabla el
  valor que muestra— tienen test, más las dos guardias de encabezado
  (pestañas y exportaciones contra el árbol; el campo validable).
- **Cerrado después, por etapas que conviene fechar:** S20 abrió el primer
  test de **ventana real** (la corrida de perfil de punta a punta, que
  construye `gui/app.py` entero), S21 dejó escrito cómo conseguir Tk en el
  contenedor, S22 sumó la ayuda de entrada y G1 la selección real de la
  pestaña 2. **I1 cerró el último archivo que faltaba:**
  `gui/ventana_normativa.py` no se construía nunca bajo Tk —los apoyos
  anteriores lo evitaban a propósito y lo decían—, y el smoke de
  `tests/apoyo/gui_smoke_normativa.py` construye la app, puebla las cuatro
  pestañas con el CSV de expediente y abre y cierra la emergente de un
  criterio `de_tabla` por el camino del ratón.
- **Abierto, en dos frentes que conviene no confundir.** (1) De **alcance**,
  medido en I1b: el smoke abre la emergente de UN criterio `de_tabla`, de
  modo que de las cuatro caras que `VentanaNormativa._construir` despacha
  solo la cara TABLA se construye bajo Tk; `_pintar_rango`,
  `_pintar_catalogo`, `_pintar_campo` y el camino de `_declarar` siguen sin
  construirse nunca en la suite — el mismo riesgo que el docstring del test
  describe, en las otras tres caras. (2) De **entorno**: los cuatro tests de
  ventana se **saltan** donde no hay Tk ni servidor X —la clase de saltos que
  CLAUDE.md censa—, de modo que una integración continua sin entorno gráfico
  sigue sin ejecutarlos.
- **Qué haría falta:** infraestructura de CI con entorno gráfico
  (instalar `python3-tk` + `xvfb`), no un test más.
- **Cerrada en C09 (2026-09-22):** las tres caras y `_declarar` corren bajo Tk; ver C09-01.
- **Dónde vive:** `tests/test_gui_contrato.py::test_la_ventana_normativa_se_construye_y_se_cierra_de_verdad`
  (el smoke que lanza es `tests/apoyo/gui_smoke_normativa.py`; los cuatro
  tests de ventana comparten el `skipif` de `_interprete_con_ventana`).

## SIS-F-13 · Los módulos de cálculo sin caso patrón

- **Cerrado en S19 una de las tres razones:** `test_M5_verificaciones.py`
  consume ya CP-3 por la cadena de producción entera —catálogo de M2, Manning
  de M3, umbral de M5—, sin fabricar ningún dorado. Y la regla de `CLAUDE.md`
  «todo módulo de cálculo se contrasta contra `casos_patron`» **dejó de vivir
  solo en la constitución**: la ejecuta una guardia con la lista de exentos
  declarada, que además falla si un exento deja de serlo.
- **Cerrado también en C7 el de M8**, y conviene decirlo aquí porque esta
  ficha decía tres: la FLOTACIÓN no necesitaba ninguna de las fuentes
  ausentes y `CP10_FLOTACION_MARCO` le dio a M8 su caso patrón, así que M8
  **salió de la lista de exentos** (el comentario de la guardia conserva el
  motivo viejo y por qué dejó de cubrir al módulo entero;
  `seleccionar_clase_calibre` sigue sin dorado: por M 170M Tablas 1-5 sin
  transcribir y, desde N1, por el procedimiento de A796 sin implementar —la
  fuente ya está, la tabla que se esperaba de ella no existe—).
- **Cerrado también en N2 el de M2, en dos tercios y sin fabricar nada:**
  `CP11_SERIES_NOMINALES` es la serie de diámetros nominales TRANSCRITA de
  las normas de producto —la del TMC desde I1 (`ASTM_A760.T1`,
  `AASHTO_M36.T6`) y la del HDPE desde N2 (`AASHTO_M294_TRAD.T7.2.2`, leída
  de la **traducción no oficial** de M 294-11 que entró en `normas/`, sin
  firma)—, y `test_M2_material.py` contrasta `siguiente_diametro` contra
  esas tablas y no contra la fórmula (conflicto #7). M2 **salió de la lista
  de exentos**; el tercio que sigue sin dorado —la serie del concreto, porque
  AASHTO M 170M-04 Tablas 1 a 5 no están transcritas (OCR inutilizable; se
  leen por imagen en una sesión propia)— está censado en el propio fixture
  (`CP11_SERIES_NOMINALES['concreto_reforzado'] is None`, con test).
- **Abierto:** M10 sigue sin caso patrón, y M2 en su tercio del concreto.
  **No es pereza de la fase de tests:** fabricarles un dorado sería inventar
  el valor de referencia, que es exactamente lo que prohíbe el conflicto #7
  del plan. M11 no cuenta: es el módulo de reporte y no le corresponde dorado
  numérico.
- **Qué haría falta:** para el tercio de M2, transcribir por imagen la
  columna «Internal Designated Diameter, mm» de las Tablas 1 a 5 de M 170M-04
  y añadirla a CP11; para M10, no una norma sino el expediente vial. Están en
  la §15 del plan, y ahora también en la guardia, con su fuente concreta.
- **C09:** el ejemplar de M 170M no es transcribible; ver C09-02.
- **Dónde vive:** `tests/test_guardias_de_la_suite.py::SIN_CASO_PATRON`

---

# Parte IV — Un hallazgo nuevo que la suite no defendía

## MAT-D1 estaba corregido y no lo defendía ningún test

- **Qué se difirió:** nada — es lo contrario. MAT-D1 («V2 se evalúa con la
  rama `n_min`, que es la estimación alta: el conservadurismo queda
  invertido») se corrigió hace varias sesiones y **la corrección no la
  defendía ningún test**. Al escribir el caso patrón de M5 se mutó
  `v2_velocidad_minima` de vuelta a `resultado.V_erosion` y la suite entera
  quedó en verde: 1497 tests.
- **Por qué era invisible:** todos los tests de V2 usaban `_resultado(V=...)`,
  que fija **las dos ramas al mismo número**. Con las dos iguales, la rama que
  se lea da igual y la mutación no cambia nada.
- **Qué haría falta:** nada para MAT-D1 — el test nuevo separa las dos ramas a
  los dos lados del piso (la ventana que el propio docstring de la función
  describe, S entre 3.55e-5 y 6.01e-5) y mata la mutación. Lo que sí queda
  abierto es la pregunta general: **cuántas otras correcciones cerradas están
  sin defender**. Esta salió por casualidad, al escribir otra cosa; no hay
  barrido que las busque.
- **Dónde vive:** `tests/test_M5_verificaciones.py::test_v2_decide_con_la_rama_de_n_MAXIMO_y_no_con_la_de_erosion`

---

# Parte V — Los tres símbolos que C1 introdujo sin consumidor

La sesión **C1** (abstracción `Seccion`) creó tres cosas que hoy no llama
nadie. No son residuo: las tres existen por una razón y las tres tienen fecha
de consumidor —**C4**, la sesión que implementa `SeccionRectangular`—. Se
fichan aquí porque `CLAUDE.md` lo exige para *todo* objeto que se conserva sin
consumidor, y porque el precedente propio del repositorio es exactamente éste:
`M9_cabezal.combinaciones()` prometía un consumidor que no existía, y
`PeriodoRetorno.exigir_anios` lleva su ficha desde S19.

Las tres las descubrió la auditoría adversarial del cierre de C1, no la
sesión: C1 las escribió, documentó su razón en el código y **no abrió ficha**,
que es literalmente el defecto que este registro existe para impedir.

## C1-01 · La mitad por tirante de `Seccion` no tiene consumidor

- **Qué se difirió:** conservar `area(y)`, `perimetro(y)`,
  `ancho_superficial(y)` y el auxiliar `theta_desde_tirante(y)` sin llamador.
- **Por qué:** es el vocabulario de la Sec. 4.1 y la vía que
  `SeccionRectangular` usará directamente, porque en la rectangular el
  parámetro propio **es** el tirante. Retirarla ahora obligaría a C4 a
  reabrir el protocolo.
- **Qué haría falta:** que C4 la consuma desde `SeccionRectangular`. Y ojo:
  **no puede consumirla desde M3 ni M4**, que es la trampa que la regla
  vinculante **#12** de `docs/ruta_familia_c.md` §6 documenta con su
  medición — en la circular esta vía está mal condicionada y en los extremos
  de `bracket_llenado()` devuelve `0.0` exacto para P y para T.
- **Dónde vive:** `src/modelos/conducto.py::Seccion` (el docstring lleva la medición) y
  `src/modelos/conducto.py::SeccionCircular.theta_desde_tirante`

## C1-02 · `SeccionCircular.etiqueta()` no la invoca ningún módulo — **CERRADA en C8**

- **Qué se difirió:** conservar el método sin llamador.
- **Por qué:** es el miembro del protocolo con el que la memoria nombrará la
  sección cuando haya dos formas que distinguir. Con una sola forma, M11
  imprime `D` y no necesita preguntarle a la sección cómo se llama.
- **Qué haría falta:** nada ya. Hacía falta que M11 lo consumiera; era de **C8** (la memoria del
  marco), no de C4: hasta que la memoria tuviera que decir «marco 1.20 × 0.90 m»
  en vez de un diámetro, no había a quién preguntárselo.
- **Cómo se cerró (C8):** M11 lo invoca en **cinco** sitios —el titular de la
  combinación adoptada, la tabla de iteraciones, los dos textos de «último
  escalón evaluado» y la fila del cuadro resumen—, la CLI en **tres** (el
  volcado de texto y las dos claves del JSON), MD en **cinco** (los tres
  motivos de descarte y el mensaje del escalón sin verificaciones) y la GUI en
  **uno** (la columna del tablero de puntos). La ficha se conserva, marcada
  como cerrada, porque la razón que la abrió es lo que explica por qué el
  método existió tres sesiones sin llamador; borrarla dejaría el método sin
  historia.
- **Dónde vive:** `src/modelos/conducto.py::etiqueta`

## C1-03 · `Geometria.y_sobre_D` se quedó sin consumidor de producción

- **Qué se difirió:** conservar la propiedad, y **conservar su nombre**.
- **Por qué:** el número sí llega al entregable, pero **por otra expresión** —
  `ResultadoPunto.y_sobre_D`, que es `y_normal / self.D` —, y V1 calcula la
  suya por tercera vez dentro de `M5_verificaciones.v1_borde_libre`. Los
  consumidores de *esta* propiedad son los tests del motor. El nombre se
  conserva porque es el de la columna `y_sobre_D` del CSV entregable
  (`M11_reporte.COLUMNAS_RESUMEN_CSV`) y el que la suite pinea.
- **Qué haría falta:** unificar las **tres** expresiones del mismo número en
  una. No es de C1 (mover el número era exactamente lo prohibido) ni de C4;
  quien las toque tiene que saber que son tres y que hoy no hay nada que
  avise si divergen.
- **Dónde vive:** `src/modelos/conducto.py::y_sobre_D` — el de `Geometria`. Las otras
  dos expresiones del mismo número están en `ResultadoPunto.y_sobre_D` (mismo
  archivo) y en `src/modulos/M5_verificaciones.py::v1_borde_libre`

## C1-04 · `M3_hidraulica.tirante` se quedó huérfana

- **Qué se difirió:** conservar la función sin llamador.
- **Por qué:** la llamaba `M3.geometria` antes de C1; desde que `geometria`
  delega en `seccion.geometria_en()`, nadie la llama — ni producción ni la
  suite, que sí contrasta sus dos hermanas `area` y `perimetro`. Se conserva
  porque las tres nombran juntas, en el lenguaje de la Sec. 4.1, lo que la
  sección devuelve de una vez, y romper el trío por asimetría de llamadores
  deja peor la lectura del módulo.
- **Qué haría falta:** o un consumidor, o retirarla con sus dos hermanas
  cuando alguien decida que `geometria()` basta. **La primera redacción del
  comentario que la acompaña le inventó un consumidor** («la API pública que
  la suite contrasta»), que es el antipatrón de esta misma parte del
  registro; está corregido y medido en el propio comentario.
- **Dónde vive:** `src/modulos/M3_hidraulica.py::tirante`


---

# Parte VI — Lo que C5 dejó puesto y todavía sin consumidor

C5 abrió el catálogo del cajón (Familia C). Dos cosas quedan **escritas y sin
leer** hasta la sesión siguiente, y las dos por la misma razón: el frente que
las consumiría es de otra sesión, y adelantarlo habría metido en C5 cambios de
M8 y de M11 que su propio alcance excluye.

## C5-01 · La clave `"cajon"` de `factores_carga_aashto` no tiene consumidor

- **Qué se difirió:** dejar declarada la fila de γ_EV del marco —«Pórticos
  rígidos»— **sin cablear el consumidor que la leería**.
- **Por qué:** la fila la fija la regla vinculante #8 de
  `docs/ruta_familia_c.md` §6, no esta sesión, y el consumidor
  (`M8.factores_carga_flotacion`) indexa por `material.tipo.value`, que **no
  distingue un marco de un tubo de concreto**. Generalizar ese índice es el
  punto 2 del brief de C7. Mientras tanto un marco recibe la fila del tubo;
  el mínimo de las dos es 0.90, de modo que **el número de V7 no cambia** y lo
  que sale mal es la fila que la memoria imprime. Está escrito entero en el
  comentario de la clave y en el docstring de `M5.v7_flotacion`, que es quien
  consume la función.
- **Qué haría falta:** que `M8.factores_carga_flotacion` elija la clave por
  **forma** y no por material, como ya hace `M4.criterio_ke_de`. Es C7.
- **Dónde vive:** `src/criterios/cabezal_base.py::factores_carga_aashto`

## C5-02 · `ke_entrada` sigue declarando un número y `ke_entrada_cajon` una fila

- **Qué se difirió:** **no** migrar `ke_entrada` (el circular) al patrón de
  clave de fila que C5 estrenó para el marco.
- **Por qué:** en el bloque «Box, Reinforced Concrete» de la Tabla C.2 el
  coeficiente **no identifica la fila** —el 0.2 está en tres y el 0.5 en dos—,
  y por eso el criterio del marco declara la clave. En el bloque «Pipe,
  Concrete» esa presión no existe hoy, `ke_entrada` tiene valor y consumidor, y
  **cambiarle la forma por simetría es mover un dato de proyecto que nadie
  pidió mover**. La asimetría, con su medición, está escrita en el comentario
  de la vista derivada.
- **Qué haría falta:** migrar `ke_entrada` a una clave de `KE_HDS5_C2` y
  retirar la rama de `M4.ke_declarado` que devuelve los dos rótulos vacíos.
  ~~No tiene sesión asignada; es una limpieza, no un defecto.~~
- **Reabierta en EXT-0 (2026-09-20): pasa de limpieza a DEFECTO.** `EXT-V-02`
  midió que `ke_entrada` acepta −50 (y `'texto'`, `True`, `[1,2]`) con la
  procedencia «proviene de la fila» de la Tabla C.2: `--declarar
  ke_entrada=-50` produce `HW_salida_m = −7.668` con el punto dimensionado y
  cero incumplidas, y `PC-02`/`PC-34` añaden que sin ventana ni dominio la CLI
  declara la tupla `(0, 5)` por una coma. La forma por número es lo que hace
  posible que la procedencia mienta; la forma por clave de fila —la que ya usa
  `ke_entrada_cajon`— no puede. Sesión: EXT-1 si cabe, si no EXT-6.
- **EXT-1 (2026-09-20) cerró la mitad de VALIDACIÓN y difiere la MIGRACIÓN a
  EXT-6.** Lo que ya no puede pasar: `ke_entrada` lleva la ventana de la Tabla
  C.2 derivada de `KE_HDS5_C2` (0.2–0.9), `M4.perdida_carga` y `M4.ke_declarado`
  rechazan con `DatoInvalidoError` todo ke que no sea un real finito con
  `ke >= 0`, `declaracion.declarar_desde_tabla` guarda `valor_de_la_celda` y
  exige nota si el valor declarado difiere de la celda, y la memoria imprime
  «DIFIERE de la celda (0.5)» en vez de «proviene de esa fila». Lo que sigue
  abierto es la FORMA: `ke_entrada` declara un número y `ke_entrada_cajon` una
  clave de fila, y `M4.ke_declarado` conserva la rama que devuelve los tres
  rótulos vacíos. No cupo en EXT-1 porque migrar la forma mueve la memoria del
  corredor de referencia (la procedencia del ke de tubo pasaría a imprimir fila,
  agrupación y bloque) y ese cambio de salida pertenece a la sesión que rehace
  la forma de los criterios (EXT-6), no a la de guardias sin cambio de contrato.
- **2026-09-22:** EXT-6 no la migró (`d5ff74c`); C10 la cerró sin migrar la forma: C10-01.
- **Dónde vive:** `src/constantes_normativas.py::KE_HDS5_C2`


---

# Parte VII — Lo que C6 revisó y decidió NO cablear

## C6-01 · `sucs_fundacion` se carga, se valida y no la lee ningún módulo

> **Superada en parte por T-4 (ficha T4-05, `INF-5.1.9`).** Desde T-4 la
> columna SÍ tiene consumidor: `M2.matriz_durabilidad` la lee para el aviso de
> marco del num. 4.1.1.3.4 a). El mapeo SUCS → «mala calidad» sigue sin estar
> en el Manual y **no se inventó**: lo declara el criterio [A]
> `sucs_fundacion_deficiente`, que tiene valor —los tres suelos orgánicos del
> Art. 24 de la E.050, la «candidata peruana» que esta misma ficha nombraba— y
> por eso no entra en `criterios_sin_valor()` como el vacío bloqueante que el
> último párrafo de abajo descartaba con razón. Lo que sigue describe el
> estado anterior y se conserva porque el argumento —el vacío es del Manual—
> es el que obliga a que sea un aviso con conjunto declarado y no una regla.
> El primer consumidor, `c_phi_fundacion`, sigue sin cablear.

- **Qué se difirió:** conectar la columna al num. 4.1.1.3.4 a), que recomienda
  el marco según la calidad del suelo de fundación. Es el **segundo**
  consumidor plausible; el declarado, `c_phi_fundacion`, es de expediente y lo
  consumen E1–E5 de la Sec. 9.3, que esta CLI no ensambla.
- **Por qué:** **el vacío es del Manual, no del proyecto.** La fuente
  recomienda el marco según esa calidad y **no define «mala calidad»** — sin
  umbral, sin lista de grupos SUCS, sin remisión a otra norma —, de modo que el
  mapeo SUCS → «mala calidad» habría que **inventarlo**, que es el peor error
  posible de este repositorio. La medición, con el literal verificado y su
  página, está en `COND-MARCO-SUELO-MALA-CALIDAD`, que por eso lo resuelve como
  `NoEvaluable` y no como un dato pendiente. Dos razones más, medidas en §15.5:
  el párrafo es **recomendación atenuada** y no soporta una regla dura (un
  `Fundamento` con `verbo=OBLIGA` lo rechazaría T11); y **no cambiaría ningún
  resultado**, porque en la Familia C el tipo ya lo fija la Sec. 2.3.
- **Qué haría falta:** una fuente que respalde el mapeo — la candidata peruana
  es la **E.050**; la tabla de calidad por CBR del Manual de Suelos num. 4.5.4
  **no sirve**, clasifica la *subrasante* y no el suelo de *fundación* — y,
  con ella, el cambio de esquema de `_Columna.criterio_destino`, que hoy admite
  **un solo** destino. **Abrir el criterio «para declarar el vacío» no vale**:
  un `Criterio(valor=None)` entraría en `criterios_sin_valor()` como vacío
  bloqueante que nadie tiene obligación de contestar, y `opcional=True` está
  definido para el criterio que refina un valor que la norma ya fija — aquí no
  hay valor normativo por defecto.
- **Dónde vive:** `src/variables_entrada.py::sucs_fundacion`

## C6-02 · `_Columna.criterio_destino` admite un solo destino

- **Qué se difirió:** decidir si el campo pasa a tupla.
- **Por qué:** es **cambio de esquema**. Hoy `sucs_fundacion` apunta a
  `c_phi_fundacion` y no hay un segundo consumidor cableado (ver C6-01), de
  modo que **nada lo fuerza todavía**: cambiarlo ahora sería mover el contrato
  que la memoria y la GUI leen para explicar dónde aterriza cada columna, sin
  un caso que lo pida. C6 lo midió y lo deja **propuesto**, que es lo que su
  brief pide: proponer y parar.
- **Qué haría falta:** el primer segundo consumidor real. Cuando llegue, hay
  que decidir entre tupla (una columna alimenta varios criterios) o cambio de
  destino (la columna cambia de dueño), y arrastrar `test_variables_entrada.py`.
- **Dónde vive:** `src/variables_entrada.py::criterio_destino`

# Parte VIII — Lo que C8 dejó puesto, cerró o retiró

C8 abrió el canal de las discrepancias a la memoria y retiró `ResultadoPunto.D`.
Las tres fichas de abajo son lo que ese trabajo dejó **sin consumidor de
producción o sin cerrar del todo**, más la única retirada. La cuarta cosa que
C8 tocó de este registro está arriba: **C1-02 quedó CERRADA** — el
`Seccion.etiqueta()` que llevaba tres sesiones sin llamador tiene ahora
catorce, y su ficha lo dice sin borrarse.

## C8-01 · Nueve de 38 `Parte.cita_id` anuncian una cita que nadie transcribió

- **Qué se difirió:** transcribir las nueve citas, y con ellas hacer que el
  registro EXIJA que toda `Parte.cita_id` exista.
- **Por qué:** transcribir una cita es leer el PDF y verificar numeral, página
  impresa y texto literal (regla 8 de `CLAUDE.md`), y son nueve repartidas en
  cinco documentos. Inventarlas para poner el barrido en verde sería
  exactamente el defecto que este proyecto persigue. **Lo que sí se hizo es
  darles el primer consumidor y hacerlas visibles**: la memoria imprime «cita
  anunciada y NO transcrita al registro» en vez de un ancla rota, y el censo
  queda con trinquete decreciente.
- **Por qué no lo vio nadie antes:** la validación del registro mete estos ids
  en el conjunto de `referenciadas` —para que una cita no cuente como
  huérfana— y **nunca comprobó que existieran**. Un id que solo sirve para
  excusar a otro de estar huérfano no se comprueba jamás. Se destapó al
  darles el primer consumidor de verdad.
- **Qué haría falta:** las nueve transcripciones, con su test de página. Al
  llegar a cero, la rama del aviso en `M11._ancla_de_parte` sobra y el
  registro puede pasar a rechazar la parte sin cita.
- **Dónde vive:** `src/normativa/registro.py::partes_sin_cita_transcrita`

## C8-02 · `Registro.discrepancias_abiertas` sigue sin consumidor de producción

- **Qué se difirió:** cablearla, o retirarla.
- **Por qué:** es el **censo completo** de lo abierto, y la memoria no consume
  censos: consume lo que ESTA corrida toca (`discrepancias_que_tocan`). Son dos
  destinatarios distintos —el manifiesto es para quien audita el código, la
  memoria para quien sustenta— y fundirlos volcaría las diez abiertas en la
  memoria de un perfil que difiere seis de ellas. Su consumidor legítimo es el
  test T20 y un futuro informe de estado del expediente, no la memoria.
- **Cuidado con leer su docstring viejo:** decía «M11 las imprime» y era falso
  —M11 no importaba el módulo—. C8 lo corrigió en el sitio. Es el caso de
  manual de la primera lección de §4.5: **una declaración en un docstring no
  imprime nada**.
- **Qué haría falta:** un informe de estado del expediente, distinto de la
  memoria de cálculo, que enumere lo abierto con independencia de la corrida.
- **Dónde vive:** `src/normativa/registro.py::discrepancias_abiertas`

## C8-03 · `Registro.discrepancias_de_cita` solo lo usa el propio registro

- **Qué se difirió:** nada; se declara para que no se lea como código muerto.
- **Por qué:** es el índice inverso `cita_id → discrepancias`, y hoy su único
  llamador es `discrepancias_que_tocan`, en el mismo archivo. Se conserva
  **separado y público** porque es la operación que un revisor querrá hacer a
  mano —«¿qué discrepancias hay sobre este numeral?»— y porque tenerla aparte
  es lo que deja el filtro (`viva` + `tocada`) legible en una sola expresión.
  Es la ventana normativa, y no la memoria, su segundo consumidor plausible.
- **Qué haría falta:** que `gui/ventana_normativa.py` la consulte al pintar una
  cita, que es lo que hoy hace solo con las erratas atadas a una tabla
  (`_texto_de_errata` publica cinco de las veintitrés).
- **Dónde vive:** `src/normativa/registro.py::discrepancias_de_cita`

## C8-04 · `M2.diametro_exterior` — se RETIRÓ, y por qué no se difirió

- **Qué se difirió:** nada. Se anota la **no** deferencia, porque la pregunta
  «¿por qué esto no está en este registro?» tiene respuesta y conviene que
  esté escrita donde se buscaría.
- **Por qué:** `diametro_exterior(*, material, D)` devolvía `D + 2t` y **no
  tenía ninguna llamada** —medido sobre el AST de M7, M5, M8, MD, la CLI y su
  propio módulo, y tampoco en tests—, pese a seguir importado en dos módulos y
  citado en cinco docstrings, que es como un símbolo muerto sobrevive a la
  revisión: se lee como si alguien lo usara. Aquí viven los objetos que se
  CONSERVAN sin consumidor **por una razón**, y éste no tiene ninguna: en un
  marco no hay «un diámetro exterior» —hay `Bc = B + 2t` y `B'c = H + 2t`, que
  son números distintos— y una función que recibe un escalar solo puede
  devolver uno de los dos. C5 la usó para el `Bc` de la cobertura mínima y le
  entregó el **canto** donde iba el **ancho**, que es la regla vinculante #9
  arrastrada dos veces. Lo que la sustituye son los tres miembros del
  protocolo `Seccion` que C7 añadió.
- **Qué haría falta:** nada. Retirada en C8, con la razón completa en el
  bloque de comentario que quedó en su lugar.
- **Dónde vive:** `src/modulos/M2_material.py::siguiente_diametro` (el
  comentario que la sustituye está justo encima de ese símbolo)

# Parte IX — Lo que VC1 cerró, y la mitad que dejó abierta

## VC1-01 · La deuda de §13 se cierra por MITADES, y la otra mitad sigue diferida

- **Cerrado:** la mitad del requisito de la Sec. 2.3 que habla del **borde
  libre del canal**. `M5.vc1_borde_libre_canal` compara `cota_entrada + HW`
  contra `cota_coronacion_canal − borde_libre_canal` y emite `Verificacion`
  con veredicto y margen en metros. Corre en la posición de V5 —que en esta
  familia no aplica— y es OBLIGATORIA también a `--alcance perfil`: sin la
  columna o sin el criterio se detiene, no devuelve «no evaluable».
- **Abierto (cerrado en VE-3.6 y VE-3.7: fichas VE3-06 y VE3-07; sigue abierta sólo la
  coronación a lo largo del tramo):** la mitad que habla de la **rasante hidráulica**. VC1 acota el
  NIVEL que el agua alcanza; no mide en cuánto la obra levanta el pelo de agua
  del canal respecto del que tendría sin ella. Un punto puede cumplir VC1 con
  holgura y haber elevado la rasante hidráulica en una fracción apreciable del
  calado. Y VC1 mide **en la sección del cruce**: no acota cuánto se extiende
  el remanso aguas arriba, donde el canal puede tener la coronación más baja.
- **Qué haría falta:** dos datos que hoy no son columna de la Sec. 1.2. (1) La
  **geometría trapecial del canal** en cada cruce —ancho de solera y talud— y
  su **n de Manning**, con los que se calcula su tirante normal y, restándolo,
  la alteración. El levantamiento ya midió la sección trapecial, de modo que
  lo que falta de verdad es transcribirla a columnas y conseguir el n. (2) Un
  **perfil de remanso** aguas arriba, que es el mismo dato que V5 pide en las
  otras familias y que ninguna de las dos tiene. Y, aparte de las dos, el
  **borde libre que el propio canal adoptó en SU proyecto** (ANA / Junta de
  Usuarios del Bajo Piura), que sustituiría a la analogía con el badén: si
  fuera mayor que 0.50 m, esta verificación es menos exigente que el proyecto
  del canal.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::NOTA_VC1_LO_QUE_NO_MIDE`
  (la advertencia pegada al veredicto) y `cli.py::DECLARACION_ALCANCE_FAMILIA_C`
  (la declaración entera, una vez por punto)

## VC1-02 · V5 no se difiere en la Familia C: NO APLICA, y VC1 ocupa su hueco

- **Qué se difirió:** nada, y ése es el cambio. Hasta aquí V5 quedaba
  «pendiente para siempre» en la Familia C: se intentaba, fallaba por falta de
  `ancho_derecho_via_m`, y el fallo se anotaba como diferido al expediente. La
  deuda no era diferible porque el dato que la cerraría no habría cerrado
  nada: el umbral de V5 es un ANCHO.
- **Por qué:** V5 verifica que el embalse quede dentro del derecho de vía, y
  esa formulación presupone agua que se **extiende lateralmente** sobre la
  plataforma al remansarse contra el terraplén. En un paso de canal el agua
  sube **confinada** entre las dos coronaciones: su avance no es lateral sino
  vertical contra el labio del canal, y un ancho de derecho de vía no acota
  nada ahí. La preocupación —los terceros— no desaparece: cambia de dirección,
  y es exactamente la que mide VC1. Por eso V5 no se declara «no aplicable» a
  secas sino **sustituida**, con su sustituta corriendo en la misma posición
  de la tabla y con veredicto real.
- **Qué haría falta:** nada para cerrar esto; sí para lo que la sustitución no
  cubre, que es la extensión aguas arriba del remanso (ficha VC1-01). V5
  tampoco la cubría —su umbral era un ancho, no una longitud—, de modo que la
  sustitución no pierde alcance, pero decir que cierra el hueco entero sería
  falso.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::pieza_del_hueco_de_V5`
  (la regla de familia, en un solo sitio y consultada por los dos llamadores)

---

# Parte X — La historia que R2a retiró de las justificaciones del lote de perfil

R2a (plan R, `docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md` §R2)
reescribió la redacción de los criterios de nivel de perfil: la narración de
bitácora salió de `justificacion` porque la historia vive en git y aquí.
Estas fichas conservan la parte de esa narración que un revisor futuro
necesita y que no queda escrita en ningún otro registro.

## R2a-01 · `factores_carga_aashto`: el par único descartado, y la dirección que la ficha NOR-PUE-03 invierte

- **Qué se difirió:** nada nuevo; se conserva la razón del cambio de forma
  que la justificación ya no narra. El criterio transcribía un único par EV
  {max 1.35, min 0.90} con etiqueta [C]; ese par no es ninguna fila de la
  Tabla 2.4.5.3.1-2 —mezclaba el máximo del muro con el mínimo de la
  estructura enterrada— y ningún par único podía servir a la vez a V7 y al
  cabezal. La corrección fue el desglose por estructura (cluster C03: MAT-D8,
  MAT-D15, NOR-PUE-03, NOR-PUE-04, NOR-AAS-04).
- **Por qué se escribe aquí:** dos afirmaciones de aquellas fichas no hay que
  repetirlas. NOR-PUE-03 sostiene que usar 0.90 en E2/E3/V7 es la dirección
  insegura, y es al revés: rebajar lo que estabiliza es la dirección
  conservadora (AASHTO LRFD C3.4.1) y el desglose corrige conformidad, no
  seguridad. Y la afirmación «EH en reposo 1.35, sin mínimo declarado» era un
  corrimiento de fila: el N/A es de las paredes ancladas; el reposo lleva
  1.35 / 0.90.
- **Qué haría falta:** nada — cerrado; la lectura vinculante quedó en la
  justificación del criterio, en presente y sin narración.
- **Dónde vive:** `src/criterios/cabezal_base.py::factores_carga_aashto`

## R2a-02 · `HW_D_max`: V4b estuvo declarado y sin cablear a propósito

- **Qué se difirió:** ya nada; se conserva el porqué de un hueco que en el
  historial se leería como olvido. El chequeo V4b (HW/D máximo) estuvo
  declarado y sin consumidor hasta S14: el conflicto #1 de la matriz de
  auditorías (NOR-HDS-02 frente a MAT-D2 / SIS-A-02 / SIS-B-02) prohibía
  implementarlo mientras la etiqueta del criterio siguiera abierta, porque un
  umbral que rechaza diámetros apoyado en una cita mal leída es peor que un
  umbral que no se evalúa.
- **Por qué se cerró:** primero se cerró la procedencia —el num. 2.2.5 d) del
  HDS-5 describe práctica de agencias y no prescribe HW/D; etiqueta [A]— y el
  cableado a `M5.v4b_relacion_hw_d` vino después, en S14.
- **Qué haría falta:** nada — cerrado.
- **Dónde vive:** `src/criterios/hidraulica.py::HW_D_max`

## R2a-03 · `espesor_pared_conducto`: la cifra del código (−33.1 %) no es la de la ficha MAT-D3 (−31.6 %)

- **Qué se difirió:** nada; se fija una divergencia numérica que invita a
  «corregirla» mal. La subestimación del empuje de flotación al usar el D
  interior es −33.1 % bajo la convención del código (D_ext = D + 2·t, con
  t = 0.100 m y D = 0.90 m); la ficha MAT-D3 publica −31.6 % porque supone
  OD = 1.088 m.
- **Por qué:** las dos cifras son coherentes cada una con su convención; la
  que vale en el código es la de su propia convención, y la justificación del
  criterio ya solo lleva esa.
- **Qué haría falta:** nada para esta ficha; el día que la Fase 8 especifique
  el producto, la cifra se recalcula con su espesor real.
- **Dónde vive:** `src/criterios/geotecnia.py::espesor_pared_conducto`

---

# Parte XI — La historia que R2b retiró de las justificaciones del lote de expediente

R2b (plan R, `docs/planes_mejora/02_PLAN_REDACCION_CRITERIOS.md` §R2) cerró
la reescritura de estilo con el lote de nivel expediente. Como en la Parte X:
la narración de bitácora salió de `justificacion` porque la historia vive en
git y aquí, y estas fichas conservan la parte que un revisor futuro necesita
y que no queda escrita en ningún otro registro.

## R2b-01 · `clase_sitio`: la dispensa inventada y el [A] que confesaba no ser una elección

- **Qué se difirió:** nada; se conserva la historia que la justificación ya
  no narra. Dos piezas. (1) La redacción histórica del criterio y la §0.5 de
  la hoja de ruta v7 atribuían a AASHTO una dispensa por periodo fundamental
  corto (T ≤ 0.5 s) que permitía clasificar el sitio como si el suelo no
  licuara. El barrido de verificación dio cero coincidencias en las 1905
  páginas de AASHTO LRFD 9.ª ed. (2020): no fue un vacío relleno en
  silencio, fue una autorización normativa inventada — que es peor, porque
  un vacío se ve y una cita falsa se cree. La v8 ya retiró la regla en su
  §0.5. (2) Mientras el criterio tuvo valor fue el único [A] con valor que
  no declaraba sensibilidad (SIS-D-08), con la razón escrita de que declarar
  un rango de clases alternativas sería fijar la respuesta antes de resolver
  la pregunta; esa confesión es la que llevó a reetiquetarlo [S] sin valor.
- **Por qué se escribe aquí:** la justificación conserva íntegro el
  argumento presente (las prohibiciones de suponer E o F, el salto
  S5→Clase F que ninguna de las dos fuentes escribe, y la verificación de
  que la dispensa no existe), pero ya no cuenta de dónde venía cada error;
  sin esta ficha, la lección «una cita falsa se cree» quedaba solo en git.
- **Qué haría falta:** nada — cerrado; el pendiente vivo del criterio es la
  medición (Vs30/N/su), declarada en su `resolucion`.
- **Dónde vive:** `src/criterios/sismo.py::clase_sitio`

## R2b-02 · `cortante_alto_muro_e060_art_11_10_10_2`: el umbral 0.5·φ·Vc era una atribución inventada

- **Qué se difirió:** nada; se conserva la corrección que la justificación
  ya no narra (NOR-E060-03). El criterio decía que el Art. 11.10.10.2 de
  E.060 define un umbral de entrada «del orden de Vu > 0.5·φ·Vc». Verificado
  contra el PDF, el artículo entero es una sola frase y no define umbral
  alguno; el 0.5·φ·Vc existe en E.060 pero en el Art. 11.5.6.1 (pág. 91) y
  para elementos sometidos a flexión, no para muros. Era una atribución
  inventada del mismo tipo que la de NOR-PUE-01.
- **Por qué se escribe aquí:** la justificación conserva los umbrales que sí
  escalonan el régimen de un muro (11.10.10.1 y 11.10.7/11.10.8) en
  presente; la procedencia del error y su ficha correctora son historia y
  viven aquí y en el tracker.
- **Qué haría falta:** nada — cerrado; el pendiente vivo del criterio es la
  demanda Vu, que espera a `procedimiento_flexion_corte_aashto_sec5`.
- **Dónde vive:** `src/criterios/cabezal_base.py::cortante_alto_muro_e060_art_11_10_10_2`

## R2b-03 · `k_v`: la sensibilidad numérica (0.0, 0.5) retirada, y las tres formas del rango

- **Qué se difirió:** nada; se conserva por qué la `sensibilidad` de `k_v`
  declara dos regímenes y no un rango numérico. El criterio llevó una
  sensibilidad (0.0, 0.5) que se retiró por tres razones encadenadas:
  sugería una libertad que el num. 2.8.1.1.14.2.1 no concede (el cero es
  prescrito, no elegido); su propio comentario no coincidía con su extremo —
  hablaba de 0.5·k_h como escenario alterno, que con la cadena de este
  proyecto vale 0.25 y no 0.5 —; y la hoja de ruta escribe (0, 0.5·k_h),
  que es una tercera forma distinta de las otras dos.
- **Por qué se escribe aquí:** quien vea la tupla declarativa actual podría
  «completarla» con un rango numérico plausible; esta ficha deja dicho que
  ese rango ya existió y por qué se retiró.
- **Qué haría falta:** nada — cerrado; si algún caso reservado del numeral
  se diera en esta obra, el número sería del proyectista y entraría como
  valor del criterio, no como sensibilidad.
- **Dónde vive:** `src/criterios/sismo.py::k_v`
# Parte XII — Lo que S24 anotó sin abrir

## S24-01 · Las claves externas sin techo, y el punto de decisión de `longitud_m`

- **Qué se difirió:** decidir si las claves de `--datos-externos` que quedan
  fuera de `cli.py::_DOMINIO_DE_CLAVE` necesitan cota, y con ella el **punto de
  decisión de `longitud_m`**. El diagnóstico **está hecho y escrito**; lo que
  se difiere es actuar sobre él. El conjunto no se transcribe aquí ni allí: se
  **calcula** (`set(CLAVES_EXTERNAS) - set(_DOMINIO_DE_CLAVE)`), porque un
  conteo a mano al lado de la colección que cuenta ya envejeció tres veces en
  este mismo bloque.
- **Por qué:** porque de las que quedan fuera **ninguna es una deuda abierta**,
  y eso hubo que establecerlo antes de poder no hacer nada con tranquilidad.
  `categoria_tr` está fuera por construcción (es de `CLAVES_TEXTO`); `Q_m3s`
  está fuera por decisión ya tomada y escrita —techo ausente, guardia en la
  salida de la aritmética—; `luz_m` tiene umbral normativo que **no debe**
  copiarse aquí, porque `LUZ_MAX_ALCANTARILLA` clasifica y no invalida, y
  copiarlo cambiaría el veredicto «es puente, fuera de alcance» por un
  `DatoInvalidoError`; `TW_m` y `L_hidraulico_m` no tienen cota que heredar ni
  que derivar, e inventarla está prohibido.
  `longitud_m` es la excepción y es una **elección**, no un olvido: su cota
  existe, no es constante —es la fórmula de Sec. 7.B— y la puerta que la
  aplica es la que la declaración existe **para no usar**.
- **Qué haría falta:** decidir si `longitud_m` declarada se contrasta contra la
  geometría de su propia fila (validación cruzada de Sec. 1.5, con
  `DatoInvalidoError`) o si se deja como está, por el precedente de `Q_m3s`.
  Lo que **no** haría falta es una guardia de finitud o de signo: las dos
  puertas ya las tienen, y está medido que no es ahí donde pasa. Está medido
  también qué pasa hoy: sobre A-01 de `tests/ejemplo_puntos.csv`, con
  `ancho_plataforma` de 9.60 m, un `longitud_m` declarado de 0.5 m llega a la
  Sec. 7.B y sale `factible`.
- **Dónde vive:** `src/servicio.py::_DOMINIO_DE_CLAVE` (en `cli.py` hasta EXT-9) (el diagnóstico completo, clave
  por clave, en su comentario) y `cli.py::_resolver_longitud` (las dos puertas)

---

# Parte XIII — Lo que N1 dejó sin usuario al resolver la última discrepancia contra la v8

## N1-01 · La vía 3 del canal de discrepancias (`Criterio.discrepancias`) se quedó sin usuario de producción

- **Qué se difirió:** darle a la vía 3 un caso real de producción. `DIS-HR-A807`
  era el único criterio-portador desde I2 (`clases_producto_por_relleno`), y
  N1 la resolvió: con ASTM A796/A796M-13 en `normas/` sus partes llevan cita,
  la fila de la v8 está corregida y una resuelta no se declara (la guardia
  `_verificar_discrepancias` lo impide). Ningún criterio declara hoy una
  discrepancia.
- **Por qué:** porque inventarle una discrepancia a un criterio para que la
  vía tenga usuario es fabricar el defecto que este registro persigue. Es la
  misma decisión que I2 tomó con la vía 2 cuando resolvió `DIS-HR-G-LAUSHEY`,
  y que I3 cerró cuando apareció el caso real (`DIS-HR-FORMAS-HDS5` en el
  paso `de_forma`). La mecánica sigue probada en las dos direcciones con el
  registro, y el censo «ningún criterio declara ninguna» es una aserción
  medida que falla el día que uno la declare.
- **Qué haría falta:** una discrepancia viva cuyo canal natural sea un
  criterio y no un paso ni una cita — y entonces reescribir el test con ese
  caso, no al revés.
- **Dónde vive:** `tests/test_canal_discrepancias.py::test_la_via_del_criterio_existe_porque_V9_no_emite_paso`

## N2-01 · La traducción no oficial de M 294-11 entra como Fuente propia, sin firma en sus citas, y el original sigue ausente

- **Qué se difirió:** firmar (`Verificado`) las citas de AASHTO M 294-11 y
  retirar al original del censo de ausentes. Lo que llegó a `normas/` es una
  **traducción al español no oficial**, sin folio en sus 17 hojas: Fuente
  PRESENTE con la naturaleza en título y nota (`AASHTO_M294_TRAD`, como la
  traducción de ASTM A760), `convive_con` cruzado con el original, que
  **sigue en `FUENTES_AUSENTES`** con `que_desbloquearia` redefinido —citar a
  AASHTO y no a un traductor—, y las cuatro citas SIN FIRMA, censadas en
  `CITAS_SIN_FIRMA_A_PROPOSITO` con el precedente de `HDS5_SI_1985.EC4B#K`.
- **Por qué:** UNA razón, no dos —la primera redacción sumaba «y además es
  traducción», y el auditor adversarial de N2 mostró que choca con el
  precedente—. Sin folio, la paginación es `SinDeterminar` y T6 prohíbe
  firmar una página PDF de una fuente sin paginación medida; un tipo nuevo
  de `Paginacion` («sin número impreso») se descartó porque no habría nada
  que predecir. Ser traducción NO impide firmar: la firma acredita el
  ARCHIVO (`Verificado.sha1_pdf`), no a AASHTO, y la de ASTM A760 va firmada
  por eso; la reserva viaja en la nota, y la exige
  `test_toda_cita_de_la_traduccion_de_M294_lo_dice`. Lo que vigila el
  contenido, en cada corrida con PyMuPDF: T0, T2 y T3, porque el texto SÍ es
  extraíble.
- **Qué haría falta:** el original en inglés. Reverificar 1.1.1, 1.4, 7.2.1
  y la tabla de 7.2.2 contra él, citarlo (con firma si imprime folio), sacar
  las cuatro del censo y cerrar la Ausencia. Ni entonces el tope pasaría a
  `[N]`: es norma de producto extranjera. De leer el numeral salió además
  `DIS-HR-M294-PASO` (la v8 decía «150 mm por encima de 600 mm»; la serie
  tiene el 675), corregida en la v8 y resuelta.
- **Dónde vive:** `src/normativa/fuentes.py::AASHTO_M294_TRAD`

## T1-01 · La vigencia de las ediciones es una marca en la nota, no un campo del esquema

- **Qué se difirió:** el campo `Fuente.vigencia`. Lo que T1 (2026-09-14)
  verificó contra cada emisor —siete ediciones confirmadas, ocho con edición
  posterior publicada, ninguna indeterminable— vive en la `nota` de cada
  Fuente presente detrás de una de las tres marcas de `MARCAS_DE_VIGENCIA`,
  que `estado_de_vigencia` lee, `fuentes_con_eleccion_de_edicion_pendiente`
  deriva y `tests/test_vigencia_fuentes.py` exige en las quince. La elección
  de qué edición rige el expediente es del proyectista y está declarada
  vacía en `criterios_adoptados['edicion_que_rige_el_expediente']`.
- **Por qué:** el esquema no modela «el emisor publica hoy una edición
  posterior a la citada»: `reemplaza_a` mira hacia atrás (lo que ESTA fuente
  sustituye) y `convive_con` exige que la otra Fuente exista en el registro.
  `Discrepancia` sí tiene precedente de cuestión abierta con `gana`
  provisional (`EstadoDiscrepancia.ABIERTA`), y se descartó igual, por dos
  razones: una discrepancia dice qué AFIRMAN dos fuentes sobre un objeto, y
  la vigencia no es una afirmación de la fuente; y un `gana` provisional a
  favor de la citada sería exactamente el default que el prompt prohíbe
  decidir por el proyectista. Es la fila 6 de la tabla de decisiones
  abiertas de `docs/diseno_registro_normativo.md` («cómo se versiona el
  registro cuando salga una edición nueva»): T1 cierra la mitad de registrar
  la vigencia y deja abierta la política de migración de citas. El prompt de
  T1 pedía proponer el campo en el cierre en vez de forzar el esquema, y eso
  es lo que se hizo: la marca es el mínimo que convierte la prosa en algo
  enumerable mientras el campo no exista.
- **Qué haría falta:** una sesión de esquema que añada a `Fuente` un
  `Vigencia(estado, fecha, como, edicion_posterior, resolucion_posterior,
  pendiente_gabinete)`, mueva las marcas a ese campo, haga que
  `estado_de_vigencia` y el manifiesto lean de él y retire la marca de las
  notas. Y, aparte, lo que T1 dejó para gabinete porque ninguna página del
  emisor fue legible desde su entorno: leer la RD 22-2013-MTC/14 (la
  actualización del EG-2013, que probablemente es la que este ejemplar
  imprime como «Revisada y Corregida a Junio 2013»), la RM 217-2026-VIVIENDA
  (la transitoria de la E.030) y el listado de manuales del portal del MTC.
- **CERRADA en EXT-6 (2026-09-20):** `esquema.Vigencia` existe, con
  `acto_aprobatorio` y `derogado_por` (EXT-N-01); la marca salió de las notas.
- **Dónde vive:** `src/normativa/fuentes.py::estado_de_vigencia`

---

# Parte XIV — Lo que I4 midió y dejó sin corregir

## I4-01 · El chequeo dimensional piloto (M3–M5) midió cuatro inconsistencias de presentación y ninguna de valor; PD las cerró sin mover un número, y la extensión del barrido a M6–M10 sigue diferida

- **Cerrado (PD):** las cuatro que I4 midió, sin cambiar un solo número de
  cálculo —la línea base de la Familia C se regeneró y su diff es sólo texto
  de la memoria—: (1) el coeficiente de unidades de Manning es
  `constantes_normativas.K_MANNING_SI = 1.0 m^(1/3)/s`, con el molde de
  `KU_SI` (imperial 1.486 al lado, nombrado y no usado; etiqueta [N]
  declarada), sostenido por la ec. (47) del num. 4.1.1.3.6, que el Manual
  imprime en forma SI sin coeficiente —verificado contra el PDF—; M3
  multiplica por él en vez de esconderlo en `(1/n)` y `F4.MANNING` lo trae
  como `k_n`; (2) el paso 4.2 trae el `D` con que HW/D pasa a HW_entrada;
  (3) el paso 4.3 imprime `D` y `HW/D` (`salida.HW_sobre_D`, el cociente que
  ya juzgaba) sin cambiar qué se compara ni el veredicto, declarado en
  `UMBRAL_JUZGA`; (4) el comentario de `K_FRICCION_SI` dice la derivación que
  cierra (2·32.2/1.486² = 29.164 → 19.63) y no la del «29» redondeado. Los
  dos censos quedaron en cero y se conservan como guardia.
- **Abierto:** (a) `K_FRICCION_SI` sigue sin nombrarla ningún paso: H llega
  al 4.3 como número, y transcribir su fórmula es un paso nuevo con relación
  propia, que PD no abrió (`la_nombra_algun_paso=False` lo mide). (b) El
  barrido NO se extiende a M6–M10 (M6–M9 en el encargo; M10 también emite
  un paso), y el argumento es medido, no el del plan: la corrida de
  referencia emite 119 pasos, todos de M1, M3, M4 y M5, y ninguno de M6–M10
  —los cuatro puntos se detienen en Fases 3-5 (A-01, A-02 y B-01 por
  `CriterioPendienteError`, C-01 por `DatoFaltanteError`), B-01 además en
  Fase 10 por `DatoFaltanteError`, C-01 difiere VC1 por alcance y la Fase 9
  se bloquea en seis pendientes—, de modo que `RELACIONES` para esos módulos
  no tendría nada que medir; y M8 no emite ningún `paso()`. Extenderlo hoy
  sería censar en el vacío.
- **Qué haría falta:** para (a), un paso propio para H en M4 con
  `K_FRICCION_SI` en su sustitución y `la_nombra_algun_paso=True` en el mismo
  commit; para (b), que la corrida de referencia alcance M6–M10 —declarar los
  pendientes de perfil— y entonces escribir sus `RELACIONES` con las dos
  direcciones que ya rigen M3–M5.
- **Dónde vive:** `tests/test_dimensional_piloto.py::INHOMOGENEIDADES_CENSADAS`

---

# Parte XV — Lo que D9 dejó sin usuario al resolver la última discrepancia contra la v8

## D9-01 · La vía 2 del canal de discrepancias (`PasoDeMemoria.discrepancias`) volvió a quedarse sin usuario de producción

- **Qué se difirió:** darle a la vía 2 un caso real de producción. `DIS-HR-FORMAS-HDS5`
  fue el único paso-portador de I3 a D9 (el paso `de_forma` de M4, que habla del
  NÚMERO que sustituye: la forma de la ecuación de control de entrada), y D9 la
  resolvió: la v8 escribe ya la Forma 2, ec. (A.2), con la regla de selección por
  la columna «Equation Form» de la Tabla A.1 (los cinco puntos de §16.19 de
  `docs/ruta_familia_c.md`), y una resuelta no se declara (la guardia de `paso()`
  lo impide). Ningún paso de producción declara hoy una discrepancia.
- **Por qué:** porque el único candidato honesto se midió y no aporta. La otra
  viva, `DIS-AASHTO-GAMMA-EV-12.6.1`, habla de γ_EV en la flotación, y el paso V7
  —que sí se emite en la corrida de referencia— ya la recibe por la vía 1: sus
  `citas_textuales` llevan a propósito las citas de las DOS partes. Declararla
  además por la vía 2 imprimiría el mismo objeto del registro por segunda puerta;
  inventarle a otro paso una discrepancia para conservar el test sería fabricar
  el defecto que este registro persigue. Es la misma decisión que I2 tomó al
  resolver `DIS-HR-G-LAUSHEY` y que N1 tomó con la vía 3 (N1-01). La mecánica
  sigue probada sobre la corrida real en las dos direcciones, y el censo «ningún
  paso declara ninguna» es una aserción medida que falla el día que uno la declare.
- **Qué haría falta:** una discrepancia viva que hable del NÚMERO que un paso
  sustituye y a la que el cruce por cita no alcance —por ejemplo, una que las
  citas del `Fundamento` de ese paso no toquen—, y entonces reescribir el test
  con ese caso, no al revés.
- **Desde C11 (R48-001) la vía tiene usuario otra vez:** el paso 2.1 declara
  `DIS-LUZ-DENOMINACION`, sobre la magnitud que ese paso compara.
- **Dónde vive:** `tests/test_canal_discrepancias.py::test_la_via_del_paso_quedo_sin_usuario_al_resolver_FORMAS`


---

# Parte XVI — Lo que EXT-0 reabrió y decidió tras el dictamen de la auditoría externa

Fuente: `docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md` y la
cadena `07_CADENA_PROMPTS_EXT.md`. Los IDs `EXT-*` y `PC-*` están de alta en el
tracker desde EXT-0. Las dos fichas anteriores que EXT-0 reabrió con argumento
nuevo —`NOR-HDS-05` y `C5-02`— llevan la reapertura escrita dentro de su propia
ficha, arriba, para no duplicar el símbolo.

## SIS-B-22 · `limpiar_valores_dinamicos` sí tiene caso de uso: abrir una sesión

- **Qué se difirió:** en S16.5 se cerró SIS-B-22 escribiendo en el docstring de
  `limpiar_valores_dinamicos` que **no tiene llamador a propósito**: «una corrida
  de la CLI es un proceso de un solo uso y no necesita borrar todo; la GUI retira
  UNA clave; el consumidor real es conftest.py». Se difirió, sin decirlo, decidir
  qué pasa con los valores dinámicos de una obra cuando se abre la sesión de otra.
- **Por qué se reabre (EXT-0, 2026-09-20):** la premisa era de S16.5 y S17 la
  dejó atrás al crear la sesión JSON (SIS-A-18). `EXT-A-02` midió que
  `restaurar_sesion` es **aditiva**: abrir la sesión B tras declarar en A deja
  las claves de A vivas, `estado_de_sesion()` de B las **persiste**, y una clave
  de B sin procedencia **hereda la de A** — la memoria afirma algo falso sobre
  otra obra. Abrir sesión **es** el caso de uso de vaciar todo, y la ficha no es
  vinculante (no está entre los ocho conflictos).
- **Qué haría falta:** `restaurar_sesion(estado, *, sustituir=True)` que valide
  el candidato en seco, vacíe con `limpiar_valores_dinamicos()` y las
  procedencias, y vuelque sólo lo aceptado; `sustituir=False` como «importar
  decisiones». Sesión EXT-4, junto con el contexto de corrida (`EXT-A-01`).
- **CERRADA en EXT-4 (2026-09-20):** exactamente eso. `restaurar_sesion` valida
  el candidato entero con `criterios_adoptados.verificar_declaracion` —la
  guardia de `establecer_valor_dinamico` en seco, sin escribir—, después
  vacía con `limpiar_valores_dinamicos()` y el libro de procedencias, vuelca
  sólo lo aceptado por el único camino y devuelve `retirados`. «Cargar
  sesión» de la GUI la llama con `sustituir=True`; «Importar decisiones» es un
  botón aparte con `sustituir=False`. El docstring de
  `limpiar_valores_dinamicos` dice ahora que SÍ tiene llamador de producción
  y cuál; `tests/test_ext4_contexto_corrida.py` (casos d, d2, d3, d4) fija que
  abrir la sesión B vacía deja `valores_dinamicos() == {}` y
  `procedencias() == {}`, y que una clave de B sin procedencia no hereda la de A.
- **Dónde vive:** `src/criterios_adoptados.py::limpiar_valores_dinamicos`

## NOR-HID-02 · La cuneta está en la pág. 179 y la memoria sigue imprimiendo 178

- **Qué se difirió:** nada a propósito: `NOR-HID-02` figura «Cerrado» desde S12
  porque el registro (`MC_HHD_CUNETA`) lleva la 179 y el carácter por valor. Lo
  que quedó sin tocar, sin que nadie lo decidiera, fue **lo que la memoria
  imprime**: `NUMERAL_FASE_10`, `Espaciamiento.numeral`, la ficha de
  `long_max_cuneta` y la v8 seguían en 178 (`PC-30`, `EXT-G-03`).
- **Por qué se reabre (EXT-0, 2026-09-20):** un cierre que corrige el registro y
  deja el texto que llega al entregable es un cierre incompleto, y el tracker lo
  daba por entero. La v8 se corrigió en EXT-0 (verificado sobre el PDF: la 178
  es la Tabla Nº 34; el apartado d) con 250 m y 200 m está en la 179).
- **Qué haría falta:** los tres textos del código a 179 y un test que los
  compare con `MC_HHD_CUNETA.pagina_impresa` en vez de repetir el número.
  Sesión EXT-6.
- **CERRADA en EXT-6 (2026-09-20).** `NUMERAL_FASE_10` lee la página de la
  cita (`MC_HHD_CUNETA.pagina_impresa`); `Espaciamiento.numeral` y la ficha
  de `long_max_cuneta` dicen 179 y
  `tests/test_ext6_registro_normativo.py::test_la_pagina_de_la_cuneta_que_imprime_la_memoria_es_la_del_registro`
  los compara con la cita en vez de repetir el número.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::NUMERAL_FASE_10`

## EXT-V-01 · Un expediente por repositorio; multi-obra es requisito de producto

- **Qué se difirió:** el mecanismo multi-obra: que un mismo despliegue calcule
  dos corredores con sus propios datos de sitio sin editar archivos de código.
- **Por qué:** el hallazgo V-01 de la auditoría externa leía los [S] de La Unión
  en `datos_sitio.py` como «hardcoding indebido». No lo es: es el **diseño
  constitucional** (v8 §0.7 «se declara una sola vez», taxonomía [S] de
  CLAUDE.md, `auditoria_y_ruta_despliegue_v9.md` A.0): el repositorio **es** el
  expediente de una obra, y un [S] con trazabilidad en un archivo versionado es
  más revisable que un campo de formulario. Lo que falta para «herramienta
  general» es un **requisito de producto**, no la corrección de un defecto, y se
  hace en ese orden: primero la enmienda constitucional (CLAUDE.md y v8 §0.7:
  dónde vive un [S] declarado por sesión), después el mecanismo. Radio medido
  por el dictamen: la corrida de perfil no lee ningún [S]; la de expediente sólo
  `PGA_roca_B`; ponerlos a `None` sin enmendar la constitución mata 18 tests en
  5 archivos y no gana nada. **Lo que no hay que hacer:** un objeto `Proyecto`
  que duplique `DatoSitio`/`Criterio`/`Procedencia`, ni vaciar los archivos.
- **Qué haría falta:** `DatoSitio.nivel`, `datos_sitio.establecer_dato_dinamico`
  con trazabilidad obligatoria, `--datos-sitio sitio.json`, sesión formato 3 como
  único lugar del «proyecto actual», y la advertencia cuando `--proyecto` no
  coincide con `corredor_del_proyecto`. Sesión EXT-10, sólo después de EXT-4 y
  EXT-9.
- **CERRADA en EXT-10 (2026-09-21).** Enmienda constitucional primero
  (CLAUDE.md, taxonomía [S]; v8 §0.7) y mecanismo después: `DatoSitio.nivel`
  medido en las dos direcciones (`tests/test_ext10_multiobra.py`),
  `datos_sitio.establecer_dato_dinamico` (replace + `_verificar_dato`,
  trazabilidad y fecha obligatorias, `Derivada` rechazada), `--datos-sitio`
  (`servicio.cargar_datos_sitio`, rechazo entero y en seco), sesión formato
  3 (`src/sesion.py`) como único lugar del «proyecto actual»,
  `ContextoCorrida.datos_efectivos` con origen, y la memoria con «Origen» y
  la advertencia de corredor. Los valores de La Unión siguen en los
  archivos; un proyecto nuevo es `sesion_vacia()`. Parte XXVI.
- **Dónde vive:** `src/datos_sitio.py::establecer_dato_dinamico`

## EXT-G-03 · Las seis fichas de ayuda de claves externas: se llenan, pero sólo por derivación

- **Qué se difirió:** el contenido de `concepto`, `unidad` y `de_donde_sale` para
  las seis claves de `cli.CLAVES_EXTERNAS` que no son columna del CSV, ni dato de
  sitio, ni criterio, y que por eso no están en `variables_entrada.VARIABLES`.
  El docstring de `FichaDeClaveExterna` lo decidió: «prefiere un hueco declarado
  a una frase inventada o sacada de un docstring que puede reformatearse mañana».
- **Por qué (decisión EXT-0, 2026-09-20):** el hueco declarado es honesto, pero
  quien lo mira es justamente la persona que tiene que rellenar el JSON y no sabe
  qué unidad lleva `luz_m` ni de dónde sale `Q_m3s`. La objeción del docstring
  vale contra la prosa a mano, no contra la **derivación**: la fase y el módulo
  que consumen cada clave los mide `variables_entrada._consumo_por_modulo`, y la
  unidad y el origen están en el contrato que `cli` ya exige (`_numero_externo`,
  los `DatoFaltanteError` que dicen de dónde tendría que venir el dato). **Se
  llenan por derivación**: las seis entran a `VARIABLES` como variables de origen
  «dato externo», con concepto y unidad **leídos del código** y la fase medida; lo
  que no se pueda derivar sigue vacío y la ventana lo sigue diciendo. Nunca una
  frase escrita para la ficha.
- **Qué haría falta:** las seis variables en `variables_entrada`, la ficha
  derivándose de ahí y un test que compruebe que ninguna ficha lleva texto que no
  esté en su variable. Sesión EXT-5.
- **CERRADA en EXT-5 (2026-09-20).** Las seis entraron a `variables_entrada`
  como la cuarta población, `Poblacion.DATO_EXTERNO` (`_EXTERNOS`), con la
  fase medida por `_consumidores` donde hay consumidor (`luz_m`, `S_conducto`,
  `categoria_tr`) y declarada donde no lo hay (`TW_m`, `longitud_m`,
  `L_hidraulico_m`, que entran a MD ya resueltas o las lee `cli._fase_10`),
  el dominio de `S_conducto` nombrado contra `dominios.S_CAUCE_MAX` —el mismo
  que `cli._DOMINIO_DE_CLAVE` aplica— y las opciones de `categoria_tr` leídas
  de `modelos.CategoriaTR`. `fichas_de_datos_externos` ya no tiene rama vacía:
  las ocho fichas salen del censo, `tests/test_ext5_forma_gui.py` comprueba
  que dicen letra por letra lo que dice su variable, y la GUI de ayuda retiró
  la etiqueta «sin ficha». El docstring de `cli.py` sigue sin parsearse.
- **Dónde vive:** `src/ayuda_entrada.py::FichaDeClaveExterna`


---

# Parte XVII — Lo que EXT-1 dejó escrito al cerrar las guardias locales

Fuente: prompt EXT-1 de `docs/planes_mejora/07_CADENA_PROMPTS_EXT.md` y el
paso 1 del dictamen. Los tests de aceptación están en
`tests/test_ext1_entradas.py`, uno por ID. Las dos fichas de abajo son las dos
decisiones que la sesión tomó **distintas de lo que el prompt pedía a la
letra**, y por eso se escriben aquí y no sólo en el docstring.

## PC-32 · El umbral de `factor_esviaje` es una tolerancia numérica, no una cota de esviaje

- **Qué se difirió:** cortar el esviaje de **89.9 grados** (factor 573,
  longitud de 10 313 m sobre A-01), que es el caso que el dictamen usa para
  motivar PC-32. La guardia de salida **existe** desde EXT-1 y lanza
  `LimiteNumericoError` con umbral nombrado, pero su umbral es
  `tolerancias.COS_ESVIAJE_MIN` ≈ 3.5e-7 —cos(θ) por debajo del cual el
  redondeo del ángulo en doble precisión mueve el factor más que
  `TOL_UMBRAL_NORMATIVO` en relativo—, o sea θ > 89.99998°. El 89.9 pasa.
- **Por qué:** porque cualquier umbral que atrape 89.9° es un **valor de
  proyecto**, no una tolerancia: no hay norma en `normas/` que fije un esviaje
  máximo constructivo (ni Sec. 7.B ni EG-2013), y el docstring de
  `factor_esviaje` (MAT-O18) ya había decidido que si el proyecto quiere esa
  cota, «el camino es declararla como criterio [A] con su sensibilidad, no
  escribirla aquí». Escribirla en `tolerancias.py` con nombre de tolerancia
  sería la misma cota disfrazada. Lo que sí es numérico —y se derivó, no se
  eligió: `(π/2)·ε/TOL_UMBRAL_NORMATIVO`— es dónde 1/cos deja de estar
  determinado por el dato, y eso es lo que la guardia mide. El caso del
  dictamen sigue **visible**: la longitud absurda llega a la memoria y G2 la
  contrasta contra la cota del receptor, como MAT-O18 escribió.
- **Qué haría falta:** un criterio `[A]` de nivel perfil con el esviaje máximo
  que el proyecto acepta construir, su ventana y su fuente técnica ([C] si
  alguna guía lo fija), leído por `factor_esviaje` con `valor_si_declarado` para
  no mover la línea base mientras nadie lo declare. Es una decisión del
  proyectista, no de esta sesión.
- **Cerrada en C10:** el criterio existe, `esviaje_max_grados`; ver C10-03.
- **Dónde vive:** `src/tolerancias.py::COS_ESVIAJE_MIN`

## EXT-V-02 · La celda que la procedencia cita se infiere cuando la fila tiene una sola

- **Qué se difirió:** exigir que la GUI y `declarar_desde_tabla` nombren
  siempre la **columna** además de la fila. El prompt pedía guardar
  `valor_de_la_celda` «cuando se nombra una fila y una columna con celda
  escalar»; la ventana de la Tabla C.2 deja elegir sólo la fila (la tabla tiene
  una columna de coeficientes), de modo que con la letra del prompt la
  procedencia veraz no se habría activado nunca en el flujo real.
- **Por qué:** `declaracion._celda_escalar` resuelve la celda también cuando se
  nombra una sola fila que tiene **una sola** celda numérica; con varias celdas
  numéricas (los tres n de la Tabla N.º 09), varias filas o una celda no
  escalar devuelve `None` y la procedencia dice «fila» como hasta ahora. No es
  una inferencia sobre el dato —la celda es la que la tabla imprime— sino sobre
  cuál celda se está citando, y sólo cuando no hay ambigüedad posible. **Y la
  celda sólo se cita cuando lo declarado es un número**: los criterios que
  declaran la CLAVE de la fila (`ke_entrada_cajon`, `embocadura_cajon`) no
  «difieren» de ninguna celda. Lo encontró el auditor adversarial de EXT-1: la
  primera versión comparaba la clave con el coeficiente y rechazaba la
  declaración legítima que hace la ventana de la GUI; hay test de regresión en
  `tests/test_ext1_entradas.py`.
- **Qué haría falta:** nada mientras la ventana siga ofreciendo fila y columna
  por separado; si algún día exige la columna, la rama de una sola celda
  numérica se vuelve redundante y se retira.
- **Dónde vive:** `src/declaracion.py::_celda_escalar`

---

# Parte XVIII — Lo que EXT-2 dejó escrito al cerrar el cluster hidráulico A

EXT-2 cerró EXT-M-03, EXT-M-04, PC-06 y PC-19 (el reparto Q/N dentro de M4, la
recta de transición con `H_c(Q_lo)` y el techo `Q_lleno` del tirante normal).
Dos cosas quedaron sin cambiar a propósito, y las dos se dejan aquí con su
argumento para que nadie las lea como olvido.

## EXT-2-01 · V6 sigue rechazando N > 1 aunque el multicelda ya se resuelve bien

- **Qué se difirió:** cambiar `v6_material_solido_arrastre` (`cumple = celdas == 1`)
  para que un marco de N > 1 celdas pueda **aceptarse**. El prompt de EXT-2 lo
  ataba a que existiera un test multicelda de punta a punta y a que el cambio
  fuera en el mismo commit que el contrato de `Q_celda_m3s`; el test existe
  desde EXT-2 (`tests/test_ext2_multicelda_transicion.py::test_el_multicelda_se_dimensiona_con_Q_sobre_N_y_publica_los_dos_caudales`,
  con verificador inyectado) y el contrato también, y aun así V6 no se toca.
- **Por qué:** V6 no es una propiedad del programa sino una **lectura de la
  fuente**: el num. 4.1.1.3.4 a) del Manual RECOMIENDA sección única sin
  subdivisiones **ante capacidad de arrastre del curso** (`MC_HHD.4.1.1.3.4a#MULTIPLES`,
  fundamento `F3.CELDAS`). Aceptar N > 1 exige saber si ESTE cauce arrastra
  palizada, y ese dato —un [S] por punto, o al menos por corredor— no existe
  en el CSV ni en `datos_sitio.py`. Sin él, la única V6 que no inventa nada es
  la que hoy está: N > 1 no cumple, y quien declare multicelda lo ve como
  incumplimiento con su criterio citado, no como un silencio. Cambiarla a
  «cumple siempre» sería rellenar un vacío; cambiarla a «cumple si no hay
  arrastre» exige el dato. El reparto Q/N (regla vinculante #3) queda
  correcto y visible en la memoria con V6 tal cual: el defecto EXT-M-03 vivía
  en la traza y en el motivo de rechazo, no en el veredicto.
- **Qué haría falta:** una entrada [S] `arrastre_de_solidos` (o equivalente)
  por punto, con su trazabilidad (observación de campo, registro de la Junta
  de Usuarios), y una V6 que la lea: N > 1 cumple sólo sin arrastre
  declarado. Con ese dato, `test_V6_sigue_rechazando_el_multicelda` se
  reescribe en la misma sesión.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v6_material_solido_arrastre`
- **Cerrado (VE-5, lote m45, ítem 18):** la entrada existe: `arrastre_de_solidos`, booleano
  por punto o global de `--datos-externos` ([S] de la inspección del cauce), en
  `servicio.CLAVES_EXTERNAS` (29), con ficha en `variables_entrada` y fila en
  `docs/contrato_entradas.md`. Viaja en `DatosDeExpediente` y V6 la lee con N > 1: `false`
  acepta la multicelda; `true` o sin declarar, no. Tests:
  `tests/test_ve5_m45_arrastre_v6.py`; `test_V6_sigue_rechazando_el_multicelda` sigue
  valiendo sin el dato.

## EXT-2-02 · El JSON de la CLI no lleva `Q_celda_m3s` ni `numero_celdas` todavía

- **Qué se difirió:** publicar los dos campos nuevos de `ResultadoHidraulico`
  en `cli._diseno_json` (y por tanto en la GUI, que lee el mismo `Informe`).
  Hoy viajan en la memoria HTML —el paso del reparto los imprime— y en el
  objeto, pero el JSON sólo imprime `Q_m3s`, que sigue siendo el del punto.
- **Por qué:** EXT-3 tiene asignada la mitad JSON de SIS-B-18 (`ahogado_por_TW`
  y las banderas de h_o que tampoco llegan al JSON ni a la GUI), y meter aquí
  dos claves nuevas al esquema sería tocar el mismo objeto en dos commits
  consecutivos, que es lo que la regla «un cluster entero por commit» existe
  para evitar. Ningún número publicado está mal: `Q_m3s` es el caudal del
  punto, que es lo que su clave dice.
- **Qué haría falta:** en EXT-3, sumar `Q_celda_m3s` y `numero_celdas` a
  `_diseno_json` junto a las banderas de SIS-B-18, y regenerar la línea base
  declarando que las tres corridas de la CLI ganan dos claves por punto.
- **Dónde vive:** `src/modelos/hidraulica.py::ResultadoHidraulico`
- **Cerrado en EXT-3 (2026-09-20):** `cli._diseno_json` publica `Q_celda_m3s`
  y `numero_celdas` junto al bloque h_o entero y al régimen del barril (trece
  claves nuevas por punto dimensionado); la línea base lo declara archivo por
  archivo en el README de `tests/linea_base_familia_c/` (entrada EXT-3).

# Parte XIX — Lo que EXT-3 dejó escrito al cerrar el régimen del barril y el dominio del método

EXT-3 cerró EXT-M-01, EXT-M-02 y PC-04, la mitad compuerta de PC-27 y la mitad
JSON de SIS-B-18 (régimen del barril, velocidad de salida de HDS-5 3.1.6, la
sexta excepción `MetodoNoEvaluableError` y `Bloqueo` en `modelos.py` con
`tipo` Enum). Tres cosas quedaron sin hacer a propósito, y una de ellas la v8
decía que EXT-3 la haría: se dejan aquí con su argumento y su sesión.

## EXT-3-01 · El 0.75 de V1 y el 0.25 m/s de V2 siguen rotulados [N] aunque la v8 ya dice que el umbral duro es [A]

- **Qué se difirió:** reetiquetar `Y_SOBRE_D_MAX` y `V_MIN` —que
  `constantes_normativas.py` lleva como [N]— a la forma que la v8 §4.1
  enmendada en EXT-0 fija para V1 y V2: **[N] el deber de verificar** (el
  Manual manda «verificar que la velocidad mínima… no produzca sedimentación»
  y tomar en cuenta el borde libre) y **[A] el valor aplicado como umbral
  duro**, porque las dos cifras llegan con «se recomienda» (págs. 77 y 79) y
  aplicar una recomendación como rechazo es una adopción del proyectista, con
  sensibilidad. La nota de §4.1 decía «lo cambia EXT-3».
- **Por qué:** son 56 usos en 13 archivos, y el cambio no es un renombre:
  exige dos criterios nuevos en `criterios_adoptados.py` con ventana,
  `nivel` y `resolucion` (ambos de perfil), mueve la tabla de criterios que
  `test_nivel_medido` contrasta contra las corridas, el bloque
  `UMBRALES_DE_VERIFICACION` que M11 imprime siempre, los manifiestos y las
  fichas de los dos criterios. EXT-3 ya era «la sesión más delicada de la
  cadena» por el régimen del barril, y meter el reetiquetado en el mismo
  commit habría mezclado dos clusters. La memoria SÍ imprime hoy el matiz
  («recomienda, no prohíbe», NOR-HID-10 / NOR-MEM-01): lo que falta es la
  etiqueta, no la honestidad del texto. La v8 §4.1 quedó corregida en EXT-3
  para no prometer lo que el código no hizo.
- **Qué haría falta:** una sesión propia (EXT-3c) que cree los dos criterios
  [A] de perfil —o un solo criterio por verificación con el valor de la
  fuente como default declarado—, mueva las lecturas de M5, deje las cifras
  de la fuente donde están como constantes de tabla (el 25 % y el 0.25 m/s
  SÍ los escribe el Manual: el patrón `F_PGA_TABLA` / `'F_pga'`) y regenere
  los manifiestos.
- **Cerrada en C05:** los dos criterios existen; ver C05-01.
- **Dónde vive:** `src/constantes_normativas.py::Y_SOBRE_D_MAX`

## EXT-3-02 · V1 y V2 se evalúan con el escenario de TW gobernante, no con los dos

- **Qué se difirió:** la frase que la v8 §1.3 añadió en EXT-0 —«para V1/V2 el
  escenario de TW mayor es el gobernante sólo si el barril llena en los dos;
  si llena en uno solo, se evalúan los dos»— cuando el TW sale de la vía 4 de
  Sec. 1.3 (dos escenarios acotados: salida libre y receptor a sección llena).
  La corrida sigue resolviendo M4 y la Fase 5 UNA vez, con el TW gobernante
  (el mayor), y por tanto con UN régimen del barril.
- **Por qué:** bajo «cumplir en ambos» evaluar el segundo escenario no cambia
  la aceptación. Si con el TW mayor el barril llena, V1 no cumple (y/D = 1) y
  el escalón se rechaza igual; si con el TW mayor no llena, con el menor
  tampoco, y de los dos el mayor es el que puede llevar el control de salida
  a gobernar y dejar V1/V2 pendientes, que ya impide cerrar. Lo que se pierde
  es sólo la impresión del segundo escenario en la memoria, y resolverlo
  exige correr M4 dos veces por escalón y decidir cómo se publican dos trazas
  hidráulicas del mismo punto, que es un cambio de forma de `ResultadoPunto`
  y de M11 y no de EXT-3. **Con una salvedad que la auditoría de EXT-3
  señaló y que no es de aceptación sino de la Fase 6:** la velocidad de
  salida que recibe M6 es la del escenario de TW mayor, y con
  y_c ≤ TW < D esa es la MENOR de las dos (Q/A(TW) < Q/A(y_c)): el d50 sale
  del lado no conservador respecto del escenario de salida libre. Hoy ningún
  punto dimensionado de la línea base cae ahí (los de vía 4 con TW ≥ D no
  dimensionan), y es una razón más para evaluar los dos escenarios en EXT-3b.
- **Qué haría falta:** un `ResultadoHidraulico` por escenario (o la pareja
  dentro de `TWDeterminado`), la Fase 5 evaluada sobre los dos y la memoria
  imprimiendo ambos regímenes; conviene hacerlo junto al perfil por paso
  directo (EXT-3b), que es el que cambia la respuesta bajo control de salida.
- **Dónde vive:** `src/modulos/M4_control.py::regimen_del_barril`

## EXT-3-03 · El bloqueo «método no evaluable» no aparece en el tablero de criterios de la GUI

- **Qué se difirió:** que `M11.criterios_bloqueantes` —el bloque «Criterios
  pendientes que bloquearon una etapa» de la memoria y el tablero de seis
  columnas de la pestaña 4 de la GUI— liste los `Bloqueo` de tipo
  `METODO_NO_EVALUABLE`. Hoy los salta, porque llevan `criterio=None` y ese
  agregador está construido por clave de criterio.
- **Por qué:** es exactamente el hueco que PC-03 describe para el
  `DisenoNoFactibleError` de MAT-D10, y PC-03 no está asignado a EXT-3 ni a
  ninguna sesión de la cadena: cerrarlo aquí sería decidir la forma del
  tablero para dos tipos de bloqueo a la vez sin su sesión. El bloqueo SÍ es
  visible en todo lo demás que lee el `Informe`: `cli.volcar` (bloque
  «Bloqueos» y bloque de alcance), `informe_json` (`bloqueos` del punto y
  `alcance.diferidos`), la tabla «Etapas bloqueadas» y el bloque de alcance de
  la memoria HTML, y el conteo de bloqueos de la pestaña de puntos de la GUI.
  Lo que no ve el proyectista es una FILA en el tablero de criterios, que es
  un tablero de criterios y no de bloqueos.
- **Qué haría falta:** la sesión que recoja PC-03: un tablero de bloqueos sin
  criterio (o una columna «qué hace falta» que admita «otro método» además de
  «declarar»), con la GUI leyendo el mismo agregador que la memoria.
- **Dónde vive:** `src/modulos/M11_reporte/tableros.py::criterios_bloqueantes`

---

# Parte XX — Lo que EXT-4 dejó escrito al cerrar el contexto de corrida y las sesiones

EXT-4 cerró EXT-A-01, EXT-A-02, EXT-G-02, PC-07, PC-09, PC-15, PC-16 y
SIS-B-22 (reabierta en EXT-0), y retiró los 27 accesos a `_USADOS` de la
suite: `cli.correr` vacía los registros de uso al entrar y fotografía al
salir un `ContextoCorrida` congelado en `Informe.contexto`, del que leen los
cuatro exportadores; `restaurar_sesion(sustituir=True)` valida en seco,
vacía y vuelca; la GUI invalida el informe en los cuatro gestos que cambian
el estado y valida la sesión entera antes de tocar un campo. Tres cosas
quedaron sin hacer a propósito, con su argumento y su sesión.

## EXT-4-01 · La sesión sigue en formato v2: sin identidad, sin huella del CSV y sin corridas

- **Qué se difirió:** un formato de sesión v3 con migración explícita v2→v3,
  el `csv_sha1` de la corrida, el `informe_json` embebido por corrida y
  escritura temporal + `os.replace`, que es lo que el dictamen pide para E04
  («persistencia con revisiones»). EXT-4 dejó `FORMATO_SESION = 2` y cerró
  PC-16 por la vía estrecha: el esquema v2 se valida ENTERO
  (`gui.app.errores_de_sesion`, tipo por clave) antes de escribir en ningún
  `StringVar`, y los externos ausentes se reponen a vacío.
- **Por qué:** subir la versión del formato en la misma sesión que cambia la
  semántica de «cargar» (de aditiva a sustitutiva) habría mezclado dos
  decisiones que se revisan por separado, y E04 exige además decidir qué es
  una «revisión» de expediente —un objeto que EXT-4 no crea a propósito: el
  prompt dice «no crees un objeto Proyecto»—. El `ContextoCorrida` ya lleva
  las dos huellas (`csv_sha1`, `criterios_sha1`) y `informe_json` las
  publica, de modo que E04 no tiene que inventar dónde guardarlas.
- **Qué haría falta:** la sesión E04 del plan de evolución: formato 3 con
  migración, corridas embebidas (cada una con su `contexto`), escritura
  atómica; y decidir si «Importar decisiones» —que hoy suma sin vaciar y sin
  preguntar— pide confirmación clave a clave cuando pisa.
- **CERRADA en EXT-10 (2026-09-21), salvo la pregunta de «Importar
  decisiones», que queda como ficha EXT-10-02.** `FORMATO_SESION = 3`,
  `sesion.migrar_a_actual` (explícita, por escalones, `ValueError` para lo
  que no se puede migrar), `id`, `csv_sha1`, `corridas` con `informe_json`
  (`sesion.corrida_para_sesion`; la CLI dice si su corrida REPRODUCE o
  DIFIERE de la embebida), y `sesion.escribir_json_atomico` (temporal +
  `os.replace`) en las cuatro escrituras. `ResultadoDeRestauracion` no
  cambió de contrato: `restaurar_datos_de_sitio` lo reutiliza.
- **Dónde vive:** `src/sesion.py::migrar_a_actual`

## EXT-4-02 · El contexto vive en registros de módulo, no en `contextvars`: la GUI sigue corriendo en su hilo

- **Qué se difirió:** pasar los cuatro registros (`_OVERRIDES`, los dos
  `_USADOS`, `_PROCEDENCIAS`) a `contextvars` para que dos corridas
  concurrentes —una GUI en hilo, o un servicio— no compartan la foto. Hoy
  `cli.correr` vacía y fotografía sobre estado de PROCESO, y eso es correcto
  porque la GUI corre el pipeline en el hilo de Tk, de forma síncrona.
- **Por qué:** el dictamen lo dice en su propuesta 1: «si un día la GUI corre
  en hilo, el mismo almacén pasa a `contextvars` sin tocar M2–M10», porque
  los 79 escritores de uso pasan por tres funciones (`ca.valor`,
  `ca.valor_si_declarado`, `ds.valor`). Hacerlo antes de que exista un hilo
  sería resolver una carrera que no se puede medir, y EXT-8 (rendimiento y
  GUI no bloqueante) es donde se decide si la corrida sale a hilo o a
  subproceso —la propuesta 2 del dictamen prefiere el subproceso, con el que
  el aislamiento es gratis y esta ficha se cierra sola—.
- **Qué haría falta:** que EXT-8 decida hilo o subproceso; si hilo,
  `contextvars.ContextVar` por registro con `reiniciar_usos`/`capturar_contexto`
  sobre la variable de contexto, y un test con dos corridas concurrentes
  cuyos `contexto.criterios_usados` no se mezclen.
- **Dónde vive:** `src/servicio.py::capturar_contexto` (en `cli.py` hasta EXT-9)

## EXT-4-03 · Un `Informe` sin contexto no se exporta: no hay caída al estado vivo

- **Qué se difirió:** nada a favor del código viejo, y conviene decirlo
  porque la alternativa existía y se descartó: `Informe.contexto` es
  `Optional` y `None` en un informe armado a mano, y `ContextoCorrida.de`
  levanta `ValueError` en vez de fotografiar el estado del proceso en ese
  momento. El único `Informe` de la suite armado a mano
  (`test_M11_reporte.py::test_un_informe_sin_bloqueos_no_inventa_bloqueantes`)
  no se exporta; los tests que prueban un bloque de M11 suelto arman su foto
  con `cli.capturar_contexto` y se la pasan.
- **Por qué:** una caída silenciosa al estado vivo sería EXACTAMENTE el
  defecto que EXT-A-01 cierra, escondido en el caso raro. Que un informe sin
  corrida no se pueda exportar es lo que la constitución pide de todo vacío:
  detener, no rellenar. Y el registro de usos ya no se puede leer desde M11
  (la guardia AST de `tests/test_ext4_contexto_corrida.py` lo prohíbe), de
  modo que el fallback no tendría siquiera de dónde leer sin abrir la puerta.
- **Qué haría falta:** nada; queda escrito para que nadie lo lea como un
  hueco. Si algún consumidor futuro necesita exportar un `Informe`
  construido fuera de `cli.correr`, tiene que construirlo CON su
  `ContextoCorrida`, no pedir que la capa de reporte lo adivine.
- **Dónde vive:** `src/modelos/memoria.py::ContextoCorrida`

---

# Parte XXI — Lo que EXT-5 dejó escrito al cerrar la forma por criterio y el parser GUI–GUI

EXT-5 cerró EXT-G-01, PC-13, PC-14, la mitad de FORMA de EXT-V-02, EXT-V-05
y EXT-V-06 que EXT-1 había dejado abierta, la mitad de pestaña 2 de EXT-V-04
y EXT-G-03: `Criterio.forma` exigida a las 70 claves por `_verificar_criterio`,
un solo parser `gui/componentes.py::interpretar_texto_declarado` para la
pestaña 2 y la emergente, `validar_contra_rango` en forma MAT-D13, la cara de
solo lectura de un `Derivada` en la pestaña 2 y la cuarta población del censo.
Tres decisiones se apartaron de la letra del prompt o merecen quedar escritas.

## EXT-5-01 · Ocho formas, no siete: `serie_de_claves` y la unión de formas

- **Qué se difirió:** ceñir `Criterio.forma` a las siete formas que el prompt
  enumera (`int | float | str | par_ordenado | serie_de_pares |
  dict_con_campos | categoria`). Se añadió una octava, `serie_de_claves`, y
  la posibilidad de declarar la UNIÓN de formas como tupla.
- **Por qué:** `F_pga` declara la tupla de filas de la tabla de factores de
  sitio sobre las que M9 lee la envolvente (`('C', 'D', 'E')`), y eso no es un
  texto, ni una serie de pares, ni una categoría: forzarla en `categoria`
  escondía la estructura que `M9.factor_sitio_desde_tabla` exige (tupla no
  vacía de filas existentes). Y `k_v` admite, por contrato de
  `M9.k_v_declarado`, la cadena del régimen prescrito O el número del caso
  reservado: una forma única habría estrechado un contrato que el consumidor
  ya tiene, y estrechar en la puerta lo que el consumidor acepta es una
  regresión, no una guardia. Las dos ampliaciones son las mínimas que las 70
  claves pidieron; ninguna otra clave las usa.
- **Qué haría falta:** nada; queda escrito para que la familia no crezca sin
  argumento. Si una novena forma aparece, entra con su clave, su consumidor y
  su rama en `_cumple_la_forma`, no como excepción en un test.
- **Dónde vive:** `src/criterios/_base.py::FORMA_SERIE_DE_CLAVES`

## EXT-5-02 · La forma va última, y las guardias de los consumidores se quedan

- **Qué se difirió:** retirar de M2, M4, M5, M7 y M9 las guardias de tipo que
  la puerta de declaración ahora hace redundantes (`numero_de_celdas`,
  `progresion_de_cajon`, `_espesor_valido`, `k_v_declarado`,
  `_exposicion_quimica_validada`, las de `condicion_pavimento` y
  `geometria_control_salida`), y colocar `_verificar_forma` en cabeza de
  `_verificar_criterio`.
- **Por qué:** dos líneas de defensa no son duplicación cuando la segunda
  tiene un lector distinto: la puerta protege a quien DECLARA (ValueError,
  contrato SIS-E-05, rótulo rojo en la ventana); la guardia del consumidor
  protege al CÁLCULO de lo que no entró por la puerta —`con_valor` en los
  tests, un `CRITERIOS[...]` pisado a mano, una versión vieja de una sesión— y
  sale como `DatoInvalidoError` con el nombre del criterio. Retirarlas habría
  dejado los tests de consumidor sin objeto y el cálculo confiando en una
  puerta que no es la única vía a `CRITERIOS`. Y la forma se comprueba al
  FINAL porque las guardias anteriores dicen cosas más precisas cuando
  aplican —la ventana de sensibilidad, el par ordenado, el bool—; la forma es
  la última palabra sobre lo que ninguna de ellas mira. Consecuencia medida:
  los tests que probaban una guardia de consumidor con un valor que la puerta
  ya rechaza pasaron a `tests/apoyo/criterios.py::con_valor`, que exige decir
  por qué se esquiva la puerta.
- **Qué haría falta:** nada por diseño. Si algún día `CRITERIOS` deja de ser
  escribible fuera de la puerta, las guardias de consumidor pasan a ser
  aserciones de invariante y pueden simplificarse. Y un hueco MEDIDO que la
  forma no cubre porque es dominio y no estructura: `TW_receptor = -1.0`
  pasa la puerta y `cli.resolver` lo entrega literal a `M3.tw_seccion_1_3`,
  sin segunda línea (auditoría adversarial de EXT-5). Es preexistente y no
  se cierra aquí: pide una ventana numérica en la ficha o una guardia
  MAT-D13 en el consumidor, y decidir cuál es de la sesión que toque V4.
- **Dónde vive:** `src/criterios_adoptados.py::_verificar_forma`

## EXT-5-03 · Once criterios de texto cuyo conjunto cerrado vive en el consumidor, no en `sensibilidad`

- **Qué se difirió:** promover a `categoria` los criterios de valor textual
  cuya ventana de sensibilidad es PROSA y no una tupla de opciones
  (`homogeneidad_serie_fen`, `h_eq_bajo_altura_tabulada`,
  `h_eq_banda_intermedia_borde`, `categoria_refuerzo_aashto`,
  `edicion_que_rige_el_expediente`, `metodo_estabilidad_global`,
  `metodo_transicion_hds5`, `geometria_control_salida`,
  `resguardo_HW_subrasante`, `embocadura_cajon`, `n_manning_cajon`,
  `ke_entrada_cajon`, `PERFIL_SUELO_PRESUNTO`, `clase_sitio`). Llevan
  `forma=str`. (`cortante_alto_muro_e060_art_11_10_10_2` estuvo en esta
  lista hasta que el auditor adversarial de EXT-5 midió que M9 hace
  `float()` sobre su valor: es la CUANTÍA que rige, no un sí/no, y su forma
  es `float`; la ficha decía `dominio="declaracion si/no"` y se corrigió.)
- **Por qué:** `categoria` valida contra `sensibilidad`, que es donde
  CLAUDE.md dice que vive el conjunto cerrado de un criterio, y sólo cinco
  claves lo tienen escrito como tupla de textos (`condicion_pavimento`,
  `origen_cota_fondo_entrada`, `acceso_mantenimiento_v2b`,
  `factor_muro_eleccion`, `F_pga_lectura_columna_extrema`). En las demás el
  conjunto admisible está en constantes del consumidor (`CARTAS_CAJON_TA1`,
  `FILAS_MANNING_CONCRETO`, `H_EQ_BAJO_TABLA_*`, las filas de la Tabla
  5.10.1-1) o no está enumerado en ningún sitio (un método de estabilidad
  global, una edición). Copiar esas listas a `sensibilidad` crearía dos
  fuentes de verdad; inventar la lista donde no existe sería rellenar un
  vacío. Con `str` la puerta rechaza lo que NO es texto ('cero' entra como
  texto y lo rechaza el consumidor con `DatoInvalidoError`, que es un
  problema del expediente y no un fallo de programa), y por eso el conjunto
  de claves que aceptan 'cero' bajó de 53 a las de forma textual, medido en
  `tests/test_ext5_forma_gui.py`.
- **Qué haría falta:** que cada consumidor exponga su conjunto cerrado como
  dato reutilizable y que `sensibilidad` lo referencie sin copiarlo (o que la
  ventana de esas claves pase a `DeTabla` con la fila como clave, como ya
  hacen `embocadura_cajon` y `ke_entrada_cajon`); entonces pasan a
  `categoria` una a una.
- **Dónde vive:** `src/criterios/_base.py::FORMA_CATEGORIA`

---

# Parte XXII — Lo que EXT-6 dejó escrito al cerrar el registro normativo

EXT-6 cerró EXT-N-01, EXT-N-02, EXT-N-03, EXT-N-04, PC-23, PC-26, PC-30 y
el resto de EXT-G-03: el DG-2018 entró como `Fuente` presente con sha1,
285 páginas y desfase +1 medidos (284 de 285 páginas) y sus citas del
304.07 y la Tabla 304.09; la guardia «todo PDF de `normas/` es Fuente
presente o está censado» existe y censa dos PDF con motivo; las tres normas
de producto tienen su cláusula de alcance y el marco ya no lleva la norma de
un tubo; la elección de edición se partió en legal y técnica y la vigencia es
un campo; y los textos que la memoria imprime dicen 179, «una geometría y dos
velocidades», la tabla de la v8 §2.2 y las dos bases de la fricción. Tres
decisiones se apartaron de la letra del prompt o merecen quedar escritas, y
una queda diferida a sabiendas.

## EXT-6-01 · El RNGIV no vuelve a `normas/`: lo que se borró no era el decreto

- **Qué se difirió:** restaurar el archivo «Reglamento Nacional de Gestion de
  Infraestructura Vial.pdf» que el dueño borró en `5196dd2` y al que el
  DG-2018 §304.07.01 remite (DS 034-2008-MTC).
- **Por qué:** se recuperó del historial para decidir, y **no era ese
  decreto**: son 12 páginas de El Peruano fechadas el 10 de febrero de 2006,
  dos años anteriores al DS 034-2008-MTC y con otra numeración de artículos
  (su artículo 4 son las definiciones; el DG-2018 cita el artículo 4 como el
  de las autoridades competentes). Restaurarlo habría puesto en `normas/` un
  texto que no es el que la remisión nombra; registrarlo habría firmado
  citas contra un documento equivocado. Lo que falta se censa como falta:
  `RNGIV` entra en `FUENTES_AUSENTES` con lo que desbloquearía (la definición
  jurídica del derecho de vía y quién lo aprueba; ningún número: los anchos
  están en la Tabla 304.09, que sí está).
- **Qué haría falta:** el DS 034-2008-MTC con sus modificatorias, en
  `normas/`, medido como toda Fuente; entonces `DG2018.304.07.01` gana una
  `corresponde_en` y la remisión deja de ser el sustituto.
- **Dónde vive:** `src/normativa/fuentes.py::RNGIV`

## EXT-6-02 · El piso [N] del ancho del derecho de vía está en el registro y no tiene consumidor

- **Qué se difirió:** cablear la Tabla 304.09 y el incremento de 5.00 m del
  304.07.02 a V5. Están transcritos (`DG2018.T304.09`,
  `ANCHO_MIN_DERECHO_VIA_M`, `INCREMENTO_DERECHO_VIA_OBRAS_DRENAJE_M`) y las
  cinco filas dicen `NoUsada` con su razón; las dos constantes están en
  `CONSTANTES_DE_REFERENCIA`.
- **Por qué:** V5 se detiene antes, en dos vacíos que el piso no cierra: el
  método de perfil de remanso es [A] (`remanso_derecho_via`, vacío) y el ancho
  de ESTE corredor es un dato de sitio que no llega por ninguna vía
  (`ancho_derecho_via_m`); y elegir fila exige `clase_de_via`, vacía hasta que
  el estudio de demanda cierre el IMDA. Cablear el piso sin los tres habría
  sido una verificación que compara contra nada. Y el 304.07 no enuncia
  condición hidráulica alguna: F5.V5 sigue en `SIN_FUNDAMENTO` con la razón
  reescrita, porque un `Fundamento` con las citas del DG-2018 convertiría un
  piso de ancho en una verificación hidráulica que la fuente no escribe.
- **Qué haría falta:** el dato `ancho_derecho_via_m` (columna del CSV o
  tablero externo), `clase_de_via` declarada y el método de remanso; con los
  tres, V5 compara el ancho declarado contra el de su fila con el incremento
  de 5.00 m compuesto como diga la `Interpretacion` registrada en
  `DG2018.304.07.02#INCREMENTO` (la norma escribe el incremento y el caso,
  no la composición; el auditor adversarial de EXT-6 encontró la lectura
  «fila + 5» escrita como hecho y se retiró), y su fundamento cuelga de
  `DG2018.304.07.02`.
- **Dónde vive:** `src/normativa/tablas.py::DG2018_T304_09`

## EXT-6-03 · PC-24 no se cierra en EXT-6: su resto es EXT-3-01

- **Qué se difirió:** el prompt de EXT-6 pedía cerrar PC-24. Lo que de PC-24
  quedaba abierto tras EXT-0 —reetiquetar `Y_SOBRE_D_MAX` y `V_MIN` de [N] a
  «[N] el deber de verificar, [A] el valor como umbral duro»— es exactamente
  la ficha EXT-3-01: 56 usos en 13 archivos, dos criterios nuevos de perfil
  con ventana y `resolucion`, la tabla de `test_nivel_medido`, el bloque
  `UMBRALES_DE_VERIFICACION` de M11 y los manifiestos.
- **Por qué:** meterlo en el commit del registro normativo habría mezclado
  dos clusters (el mismo argumento con que EXT-3 lo dejó fuera), y EXT-6 no
  lo puede cerrar «de paso» sin escribir la sesión entera. Se dice aquí para
  que el tracker no lo dé por cerrado con un ID que no lo está.
- **Qué haría falta:** la sesión EXT-3c que EXT-3-01 describe.
- **Cerrada en C05:** ver C05-01.
- **Dónde vive:** `src/constantes_normativas.py::Y_SOBRE_D_MAX`

## EXT-6-04 · La cláusula de alcance no crea un `Fundamento`: el rótulo del marco es texto del registro, no un paso

- **Qué se difirió:** un `PasoDeMemoria` de Fase 3 que imprima la norma de
  producto con su alcance. El rótulo por (material, forma) lo produce
  `M2.norma_producto_de`, su alcance sale del registro por
  `constantes_normativas.ALCANCE_NORMA_PRODUCTO` (`como_texto` de las citas
  1.1 de M 170M, M 36, A760 y M 294, y de LRFD 12.4.2.4 y 12.11.1 para el
  marco) y viaja al JSON como `alcance_norma_producto`; pero ningún paso lo
  emite y por eso las citas de alcance no cuelgan de un `Fundamento`.
- **Por qué:** un `Fundamento` sin paso que lo imprima es exactamente lo que
  `test_memoria_sustentada` prohíbe (F9.CABEZAL está censado por eso), y M2
  no emite paso al elegir material: elige catálogo, no verifica nada. Las
  citas no quedan huérfanas —T4 las reconoce por el numeral en los textos de
  `constantes_normativas`— y el JSON, el resumen y los tres sitios de M11
  imprimen el rótulo correcto; lo que falta es que la memoria diga, como paso,
  «este material se compra contra esta norma, que cubre esto».
- **Qué haría falta:** un paso de Fase 3 en `M2.catalogo` (o en
  `_pasos_del_marco`) con un `Fundamento` F3.NORMA_PRODUCTO de verbo
  `DEFINE` sobre las citas de alcance; entonces salen de la lista de
  `test_memoria_sustentada` y `consumidores_de_cita` las ve.
- **Dónde vive:** `src/modulos/M2_material.py::norma_producto_de`

# Parte XXIII — Lo que EXT-7 dejó escrito al cerrar el cabezal (cluster C07)

EXT-7 cerró EXT-M-05 (y R95-031, que es el mismo defecto con otra fila),
EXT-M-06 y EXT-M-07: la rama vertical de `cuantia_de_diseno` con cortante
alto ya no devuelve 0.0015 —se detiene en dos criterios [A] de expediente,
el plano del cortante (E.060 11.10.2 / 11.10.1) y el piso de la ec. (11-32)—,
`verificar_cuantia` pregunta lo mismo con el mismo argumento; el empuje
estático y la sobrecarga van con el Ka de Coulomb del Manual de Puentes
(num. 2.4.4.1.5.3, cita nueva, discrepancia `DIS-HR-KA-COULOMB` resuelta) y
CP-9 tiene un bloque C con ángulos no nulos; y `EstabilidadCabezal` lleva
`exigidas`, `pendientes` y un `estable` que sólo es cierto con las cinco
filas presentes y cumplidas. Nada se cableó a la CLI. Tres decisiones quedan
escritas porque se apartan de lo que un lector esperaría.

## EXT-7-01 · La ec. (11-32) del Art. 11.10.10.3 no se implementa: se declara evaluada fuera

- **Cerrada en T-7c (2026-11-13):** la ecuación **se evalúa**, completa y con sus dos
  topes, en `M9.cuantia_vertical_ec_11_32` (piso 0,0025 y techo en la ρh requerida), con
  la altura total y la longitud del cabezal del punto, que desde T-7a existen. Los tres
  criterios que el cierre de C07 dejó vacíos tienen valor: el piso horizontal 0,0025 de
  11.10.10.2 y el piso vertical 0,0025 de la ec. (11-32), **[N→] por analogía** (E.060 es
  norma de edificaciones), y el régimen del cortante, [A] = «perpendicular al plano»,
  porque el único cortante que el ensamble de T-7b entrega para la pantalla es el del
  empuje de tierras. Lo que sigue sin existir es una carga **en el plano** del muro: con
  «en el plano» declarado los pisos se aplican con aviso, la ρh requerida por 11.10.10.1
  se toma igual a su piso y el umbral de 11.10.7 no se evalúa.
- **Qué se difirió:** evaluar en M9 la cuantía vertical mínima bajo el
  régimen de cortante en el plano, ρv = 0.0025 + 0.5·(2.5 − hm/ℓm)·(ρh −
  0.0025) ≥ 0.0025, con tope en la ρh requerida por 11.10.10.1 (E.060
  11.10.10.3, pág. 104; cita `E060.11.10.10.3`).
- **Por qué:** de sus tres entradas el software no tiene ninguna: hm y ℓm
  son geometría que `GeometriaCabezal` no lleva (no tiene longitud), y la
  ρh requerida sale de una demanda Vu que `diseno_flexion_corte` no produce
  (`NotImplementedError`, bloqueado en
  `procedimiento_flexion_corte_aashto_sec5`). Evaluarla con un hm/ℓm
  supuesto sería inventar una dimensión del cabezal. Lo que sí se cierra es
  el defecto: la rama vertical con cortante alto **se detiene** en
  `cuantia_vertical_cortante_alto_e060_art_11_10_10_3` (forma `float`, como
  su hermano horizontal: lo que M9 lee es la cuantía que rige, evaluada por
  el proyectista con hm, ℓm y ρh delante) en vez de devolver el 0.0015 del
  14.3.1, y el docstring ya no afirma lo contrario de la norma.
- **Qué haría falta:** la longitud del cabezal en `GeometriaCabezal` (o en
  `predimensionamiento_cabezal`), y el diseño por corte de AASHTO LRFD Sec.
  5 que produzca Vu y con él la ρh requerida; entonces la ecuación se
  transcribe como fórmula con su cita y el criterio pasa a `Derivada`.
- **Dónde vive:** `src/modulos/M9_cabezal/durabilidad.py::cuantia_de_diseno`

## EXT-7-02 · E6 (excentricidad sísmica) no entra en las `exigidas` por defecto

- **Cerrada en T-7b (2026-11-13):** la excentricidad de la resultante bajo sismo se
  **evalúa**, como la fila E2 del marco LRFD de la condición sísmica
  (`M9.ensamble_estabilidad`, código `E2-LRFD.sis.*`), con el límite que interpola
  `gamma_EQ` —que deja de estar vacío: 0.5 [A], ventana 0–1—. No entró en `exigidas`
  de `verificar_estabilidad`, que sigue siendo la función suelta de antes y sin
  llamador: el ensamble emite sus propias filas por marco y por condición, de modo que
  la estática no arrastra una fila que solo existe bajo sismo, que era la objeción.
- **Qué se difirió:** exigir la fila E6 —`verificar_excentricidad_sismica`,
  la ubicación de la resultante bajo sismo del Manual de Puentes— dentro de
  `EstabilidadCabezal.exigidas`, junto a E1..E5.
- **Por qué:** `exigidas` se deriva de las claves de
  `constantes_normativas.FS` (`FS_CODIGO`), que es la tabla de Sec. 9.3 de la
  hoja de ruta, y E6 no es fila de esa tabla: E.050 no la escribe, la trae el
  Manual (num. 2.4.3.11 de la excentricidad, con `gamma_EQ` vacío) y su
  umbral cambia con la condición —sólo existe en la sísmica—. Meterla en la
  tupla por defecto habría hecho que **ningún** expediente estático pudiera
  ser `estable`, y habría escrito en la constitución del tipo una fila que
  la tabla que lo gobierna no tiene. La vía queda abierta y probada:
  `verificar_estabilidad(..., exigidas=EXIGIDAS_SEC_9_3 + ("E6",))` la
  registra como pendiente hasta que alguien la resuelva.
- **Qué haría falta:** decidir, con `gamma_EQ` declarado, si E6 se exige
  sólo en la condición sísmica (entonces `exigidas` deja de ser una tupla
  única y pasa a depender de `CondicionAnalisis`) y cablear
  `presion_contacto_base` → `verificar_excentricidad_sismica` en el
  ensamble, que hoy no existe (`FUNCIONES_SIN_CONSUMIDOR`).
- **Dónde vive:** `src/modulos/M9_cabezal/_criterios.py::EXIGIDAS_SEC_9_3`

## EXT-7-03 · El Ka de Coulomb se adopta entero, no la «guardia mínima»

- **Qué se difirió:** la alternativa mínima que el prompt ofrecía —dejar
  Rankine en el estático y detener en condición sísmica cuando
  |K_A_rankine − K_A_coulomb| supere una tolerancia nombrada—.
- **Por qué:** habría conservado la base mixta que EXT-M-06 denuncia y la
  habría vuelto **condicional**: con i = β = δ = 0 nada la dispara, y en
  cuanto un ángulo se declara el cálculo se detiene en vez de calcular con el
  coeficiente correcto. La fuente primaria del marco (MP 2.4.4.1.5.3, PERMISO
  verificado) escribe Coulomb y la v8 ya está enmendada (EXT-0), de modo que
  no había nada que proteger con una guardia: había que usar el coeficiente.
  Consecuencia declarada en `empujes_trasdos`: los cuatro ángulos de Sec. 9.2
  son entrada también en condición **estática** y un vacío la detiene, donde
  antes sólo φ lo era. `ka_rankine` se conserva como patrón del caso límite y
  como la forma reducida que la hoja escribía.
- **Qué haría falta:** nada para cerrarla; se registra para que nadie vuelva
  a proponer la guardia como si fuera equivalente.
- **Dónde vive:** `src/modulos/M9_cabezal/empujes.py::empujes_trasdos`

## EXT-7-04 · La resultante de Coulomb se toma entera como horizontal: la descomposición queda diferida

- **Cerrada en T-7b (2026-11-13):** `M9.cargas_del_cabezal` descompone la resultante
  sobre el plano vertical del extremo del talón (AASHTO C3.11.5.3): `EH.h` =
  P·cos(δ + β) empuja y vuelca, `EH.v` = P·sen(δ + β) carga la base en ese plano; lo
  mismo el incremento sísmico. `M9.empujes_trasdos` conserva la forma antigua y sigue
  sin llamador (`FUNCIONES_SIN_CONSUMIDOR`).
- **Qué se difirió:** descomponer el empuje activo de Coulomb (y la
  sobrecarga, que va con el mismo Ka, y el incremento sísmico, que ya estaba
  inclinado) en su componente horizontal P·cos(δ + β) y vertical
  P·sen(δ + β), y llevar la vertical al modelo de cargas de la base.
- **Por qué:** `EmpujesTrasdos` no tiene modelo de cargas verticales del
  trasdós —el único vertical que lleva es la subpresión— y el ensamble de
  estabilidad que las consumiría no existe (`verificar_estabilidad` recibe
  las demandas ya calculadas; `FUNCIONES_SIN_CONSUMIDOR`). Inventarlo en
  EXT-7 habría sido ensanchar el cluster. Lo que sí se hace es **declararlo**
  con su dirección, que no es una: tomar la resultante entera como
  horizontal es conservador para el volteo y el deslizamiento y no lo es para
  la capacidad portante en la parte de la componente vertical que deja de
  cargar sobre la base. Medido en el bloque C de CP-9 (δ + β = 22°): la
  horizontal se sobreestima +7.9 %, y hasta +18.8 % en el extremo de ventana
  (δ = 22.7°, β = 10°). Lo encontró el auditor adversarial de EXT-7: la frase
  «+9.7 % sobre Rankine» era cierta para el coeficiente y engañosa para la
  fuerza horizontal (+1.7 %).
- **Qué haría falta:** un campo de carga vertical del trasdós en
  `EmpujesTrasdos` (con su brazo, porque también resiste el volteo) y el
  ensamble de la normal en la base que lo sume antes de E1 y E3; entonces
  `E_activo` pasa a ser la componente horizontal y el dorado del bloque C
  gana `C_E_h_esperado` y `C_E_v_esperado`.
- **Dónde vive:** `src/modelos/cabezal.py::EmpujesTrasdos`

# Parte XXIV — Lo que EXT-8 dejó escrito al cerrar el rendimiento y la GUI no bloqueante

EXT-8 cerró PC-10, PC-11, PC-12 y PC-17: `import cli` pasó de 870–930 ms a
125–150 ms (weasyprint, scipy y el censo de `variables_entrada` perezosos);
el PDF sale de la ventana en un SUBPROCESO (`cli.py --sesion … --pdf
--progreso`) con progreso, cancelación, botón apagado con motivo visible y
estado terminal; la memoria dejó de renderizar dos veces el paso 2.1, los
punteros son enlaces y hay un anexo único de fundamentos, citas y umbrales
al que cada punto enlaza, construido por streaming; y la ventana tiene
rueda en X11/macOS, rótulo visible del motivo, Escape y Control-Return.
Cuatro decisiones quedan escritas porque se apartan de lo que un lector
esperaría o porque dejan algo abierto.

## EXT-8-01 · El anexo se decide contra el «de arriba abajo» de la §4.4, y el objetivo de tamaño no se alcanzó

- **Qué se difirió:** el objetivo del dictamen —«< 15 KB y < 10 páginas
  por punto»— y, con él, cualquier recorte adicional de lo que la memoria
  de un punto imprime.
- **Por qué:** la §4.4 de `hoja_de_ruta_correcciones_v12.md` pide que «la
  memoria de un punto se lea de arriba abajo y se entienda sin abrir el
  código». El anexo lo tensiona a sabiendas y se decide así: lo que es DEL
  PUNTO (qué se calcula, con qué valores y su procedencia, el resultado,
  contra qué valor se compara y el veredicto) se queda en el punto; lo que
  es DEL REGISTRO (el argumento del fundamento, la frase literal de cada
  cita, el carácter y la aplicación de cada umbral) se imprime una vez y
  el punto lo enlaza con su numeral en la línea. «Sin abrir el código» se
  conserva —todo está en el mismo documento—; «de arriba abajo» pasa a
  «con una remisión al anexo», que es cómo cita una memoria impresa.
  MEDIDO en el árbol de EXT-8, coste marginal por punto a alcance
  expediente (cuatro puntos contra uno): 54.0 KB y ~20 páginas antes;
  44.6 KB y 14.0 páginas después; la repetición de texto cayó del 44 % al
  7 % de los bytes. Lo que queda no es repetición: la sustitución con la
  procedencia de cada valor (8 KB), las tablas de datos, iteraciones y
  verificaciones (15 KB), los resultados y veredictos. Bajar de 15 KB
  exigiría quitar del punto contenido que la §4.4 pone en el punto, y eso
  no es una decisión de formato. Los techos de
  `tests/test_ext8_rendimiento_gui.py` (`KB_POR_PUNTO_MAX`,
  `PAGINAS_POR_PUNTO_MAX`) se fijaron sobre la MEDIDA, con holgura, no
  sobre el objetivo.
- **Qué haría falta:** una decisión de contenido sobre la memoria del
  punto (por ejemplo, la sustitución sin la procedencia larga, con la
  procedencia en el anexo también), tomada contra la §4.4 y no por debajo
  de ella; y medir el PDF de 40 y 200 puntos después.
- **Dónde vive:** `src/modulos/M11_reporte/umbrales_anexos.py::anexo_referencias`

## EXT-8-02 · El hijo recalcula: la equivalencia se afirma sobre la sesión serializada, no sobre el objeto `Informe`

- **Qué se difirió:** serializar el `Informe` de la ventana y pasárselo al
  proceso hijo para que sólo formatee.
- **Por qué:** el cálculo cuesta 2 ms por punto y el `Informe` no tiene
  forma serializable de ida y vuelta (`informe_json` es un volcado de
  salida, no un formato de carga). El hijo corre la CLI con la MISMA
  sesión que «Guardar sesión» escribe —`ExpedienteApp._datos_de_sesion`,
  una sola definición— y la CLI la repone por `declaracion.restaurar_sesion`,
  el mismo camino con guardia que la ventana. Lo que se afirma y se mide
  (`test_pc11_el_pdf_del_subproceso_describe_la_misma_corrida`) es «misma
  sesión serializada → misma corrida, salvo la marca de tiempo»
  (`gui.exportacion_pdf.sin_marca_de_tiempo`).
- **Qué haría falta:** un formato de sesión con la corrida embebida
  (`informe_json` por corrida, `FORMATO_SESION = 3`): es EXT-10 / E04.
- **Cerrada EN PARTE en EXT-10 (2026-09-21).** La sesión embebe la corrida
  y la CLI compara la suya con la embebida (`cli._comparar_con_la_corrida_
  embebida`); el hijo del PDF SIGUE RECALCULANDO, porque `Informe` sigue
  sin forma de ida y vuelta. Lo que queda es la ficha EXT-10-04.
- **Dónde vive:** `gui/exportacion_pdf.py::ProcesoPdf`

## EXT-8-03 · Las claves enteras de un criterio declarado no sobreviven al JSON de la sesión

- **Qué se difirió:** corregir que un criterio `dict_con_campos` declarado
  con claves ENTERAS (el espesor de pared por diámetro, que `conftest`
  declara como `{"concreto_reforzado": {900: 0.1, …}}`) vuelva de una
  sesión guardada con claves de TEXTO (`"900"`), de modo que el consumidor
  no encuentra la fila y se detiene con «Falta el dato
  `espesor_pared_conducto[concreto_reforzado][900]`».
- **Por qué:** lo encontró EXT-8 al medir la equivalencia del subproceso
  —la corrida propia y la del hijo diferían en ese bloqueo— y NO es del
  subproceso: «Guardar sesión» y «Cargar sesión» ya lo hacían antes.
  Convertir claves de texto a enteros al restaurar sería adivinar (una
  clave `"900"` puede ser un texto legítimo en otro criterio), y cambiar
  la forma de guardar es cambiar el formato de sesión, que es EXT-10. El
  test de equivalencia repone la sesión con su forma serializada por las
  dos puertas, para que la afirmación sea la que se puede sostener.
- **Qué haría falta:** en el formato 3 de la sesión, guardar los valores
  de los criterios en una forma que conserve el tipo de las claves (un
  literal de Python, o el par tipo/valor), con migración explícita v2→v3.
- **Dónde vive:** `src/declaracion.py::restaurar_sesion`

## EXT-8-04 · El progreso del hijo se lee de un archivo, no de un pipe, y no hay hilo

- **Qué se difirió:** leer stdout del subproceso por un pipe sin bloquear.
- **Por qué:** un pipe sin bloqueo no existe igual en Windows y en POSIX,
  y la alternativa portable —un hilo lector— es lo que E06/E07 proponían
  y el dictamen descartó: el estado de módulo de los tres archivos de
  valores no es seguro entre hilos. stdout y stderr del hijo van a un
  archivo de trabajo y `ProcesoPdf.sondear()` lee lo que haya llegado
  desde el `after` de Tk; las líneas de progreso llevan
  `cli.PREFIJO_PROGRESO` para separarlas del volcado. `gui/app.py` no
  importa `threading`, y un test lo fija.
- **Qué haría falta:** nada para cerrarla; se registra para que nadie
  proponga el hilo como equivalente.
- **Dónde vive:** `gui/exportacion_pdf.py::ProcesoPdf`

## EXT-8-05 · Un paso renderizado suelto lleva enlaces sin destino

- **Qué se difirió:** que `bloque_paso` / `bloque_pasos` / `memoria_de_punto`,
  usados FUERA de `memoria_html_por_partes`, impriman los enlaces al anexo
  con destino. `tests/linea_base_familia_c/memoria_punto_cajon.html` (el
  driver `punto_cajon.py` imprime sólo `bloque_pasos`) tiene hoy 35 `href`
  y 0 `id`.
- **Por qué:** ningún consumidor de producción muestra un punto suelto como
  HTML —la traza de la GUI es texto por `traza_punto`— y el anexo es del
  DOCUMENTO: se construye con los pasos de todos los puntos y las citas de
  sus fundamentos. Darle a cada fragmento su propio anexo sería la segunda
  transcripción que la §4.5 prohíbe, y ponerlo al pie del fragmento
  cambiaría el oráculo de la línea base por un formato que nadie lee. En
  las siete memorias completas (las generadas y las de línea base) el cruce
  `href`↔`id` da cero huérfanos (`test_pc12_todo_enlace_interno_de_la_
  memoria_tiene_destino`). Lo encontró el auditor adversarial de EXT-8.
- **Qué haría falta:** si algún día un fragmento se entrega solo, una
  función `fragmento_con_anexo(pasos)` que lo cierre con su propio anexo.
- **Dónde vive:** `src/modulos/M11_reporte/pasos.py::bloque_paso`


# Parte XXV — Lo que EXT-9 dejó escrito al convertir `src/` en paquete y separar el servicio de cálculo

## EXT-9-01 · `cli` conserva reexportaciones del servicio hasta que la suite migre

- **Qué se difirió:** retirar de `cli.py` el bloque `from src.servicio import
  (...)  # noqa: F401` que reexporta lo que `gui/app.py` lee como `cli.X` y
  lo que la suite lee de `cli` (por atributo y por `from cli import`), y
  con él esas lecturas.
- **Por qué:** E01 pedía mover la orquestación sin cambiar el contrato de
  quien la consume («se retiran solo cuando los archivos de tests migren»).
  Lo que SÍ se fija ya es que la reexportación es el MISMO objeto, con el
  censo derivado del AST de la GUI y de la suite por las dos vías
  (`test_e03_cli_reexporta_el_mismo_objeto_que_el_servicio`); los tres
  `monkeypatch` sobre lo que el servicio LLAMA migraron a `servicio`. El
  auditor adversarial midió que sólo cinco privados se leen como código y
  que seis (`_etapa`, `_fase_*`, `_dato_externo`, `_avisar_ids_desconocidos`)
  se conservan porque el prompt los nombra; y que los lectores son 17
  archivos por atributo más 6 por `from cli import`, no once. La lista y la
  razón viven en el bloque de imports de `cli.py`.
- **Qué haría falta:** cambiar `cli.X` y `from cli import` por `servicio` en
  `gui/app.py` y en esos archivos, retirar el bloque y dejar que el censo del
  test —que sale del código— se apague solo.
- **Dónde vive:** `cli.py::main`

## EXT-9-02 · La CLI se queda en la raíz: no hay `python -m src.cli`

- **Qué se difirió:** mover `cli.py` dentro del paquete para que
  `python -m src.cli` y `python -m src.normativa.manifiesto` compartan
  literalmente la misma escritura, que es como el prompt de EXT-9 enuncia
  la convención (`python -m <paquete>.cli`).
- **Por qué:** la convención que se comparte es la que importa —todo se
  lanza desde la raíz, con `-m` o como script de la raíz, y nada inserta
  rutas en `sys.path`—, y `cli.py` en la raíz ya la cumple: `python cli.py`
  y `python -m cli` resuelven `src` porque la raíz es `sys.path[0]`. Moverlo
  habría tocado el contrato de EXT-8 (el subproceso del PDF lanza
  `python cli.py --sesion ...`, `gui/exportacion_pdf.py::comando_exportar_pdf`),
  el README, la línea base de la Familia C (`regenerar.sh` lo invoca cuatro
  veces) y una docena de tests que lo ejecutan por ruta, sin cerrar ningún
  hallazgo: PC-08 se cierra con un solo nombre importable para `src/`, no
  con la ubicación del adaptador. Lo que sí cambió de escritura es lo que
  no tenía otra salida: `src/indice_formulas.py` se lanza como
  `python -m src.indice_formulas` —como script, `sys.path[0]` es `src/` y el
  paquete no se ve—, igual que `tests/linea_base_familia_c/punto_cajon.py`
  (`python -m tests.linea_base_familia_c.punto_cajon` en `regenerar.sh`).
  Por la misma razón `python gui/app.py` dejó de funcionar —`sys.path[0]`
  sería `gui/`— y la escritura vigente es la del README, `python -m gui.app`;
  la forma vieja sobrevive en documentos históricos
  (`docs/auditoria_y_ruta_despliegue_v9.md`, `prompt_PD_piloto_dimensional.md`
  con `python3 src/indice_formulas.py`), que no se reescriben.
- **Qué haría falta:** si algún día el adaptador entra al paquete, un
  `src/cli.py` con el `main` actual y un `cli.py` de raíz que sólo lo
  invoque, actualizando a la vez el comando del hijo del PDF, el README y
  `regenerar.sh`; y decidir qué pasa con `import cli` en la GUI y en la
  suite, que volvería a ser un segundo nombre para el mismo módulo.
- **Dónde vive:** `gui/exportacion_pdf.py::comando_exportar_pdf`

## EXT-9-03 · El índice de fórmulas no se regeneró en EXT-9, y su sello sigue siendo el de EXT-8

- **Qué se difirió:** regenerar `docs/indice_formulas.md` con un sello de
  EXT-9.
- **Por qué:** EXT-9 es un refactor de imports y de ubicación: la corrida de
  referencia emite los MISMOS `PasoDeMemoria` —el test de sincronía lo
  comprueba regenerando a memoria y comparando el cuerpo sin la fecha—, de
  modo que no hay nada que resincronizar, y el sello exige el par de la suite
  medido sobre `origin/main`, que no se conoce antes de fusionar. El
  dictamen ya lo había dicho de E03c («no puede "regenerar el índice con
  sello" dentro de la sesión») y el prompt de EXT-9 lo repite. El
  encabezado del documento nombra `src/indice_formulas.py` como ruta de
  archivo, que sigue siendo cierta; el comando de regeneración, que sí
  cambió, vive en el docstring del módulo y en los mensajes de
  `tests/test_indice_formulas.py`, no en el documento generado.
- **Qué haría falta:** nada para cerrarla; la próxima sesión que toque
  citas, criterios, memoria o pasos regenera los cuatro documentos con su
  sello, como manda el ritual de cierre. (T-10: la función
  `corrida_de_referencia` pasó a ser `correr_referencia`, una por cada corrida
  de `CORRIDAS_DE_REFERENCIA`; ver la ficha T10-02.)
- **Dónde vive:** `src/indice_formulas.py::correr_referencia`


---

# Parte XXVI — Lo que EXT-10 dejó escrito al hacer del despliegue una herramienta multi-obra

EXT-10 cerró EXT-V-01 y la fase E04 del plan de evolución: la enmienda
constitucional primero (CLAUDE.md, v8 §0.7) y después el mecanismo —
`DatoSitio.nivel`, `datos_sitio.establecer_dato_dinamico`, `--datos-sitio`,
la sesión formato 3 como único lugar del «proyecto actual», el origen de
cada [S] en la memoria y la advertencia de corredor—. Seis cosas quedaron
decididas DISTINTAS de la lectura más directa del prompt, o sin hacer a
propósito, y cada una lleva su argumento y su símbolo.

## EXT-10-01 · La ventana normativa sigue sin declarar datos de sitio

- **Qué se difirió:** que la pestaña 2 / la ventana emergente declaren un
  [S] como declaran un criterio.
- **Por qué:** la regla R4 («cuando una fila depende de un dato que el
  proyecto no tiene, la ventana pide o bloquea; nunca elige») vale para la
  variable entera: un [S] no se elige en un formulario, se LEE con un
  procedimiento y se defiende con la trazabilidad de esa lectura. La casa
  nueva de EXT-10 es la sesión —un archivo con valor, trazabilidad y fecha
  por clave, revisable y versionable—, y por eso el campo de la pestaña 1 y
  `--datos-sitio` son la puerta, no un cuadro de texto por dato. El texto de
  `_POR_QUE_NO_DECLARABLE[DATO_SITIO]` dice ahora dónde sí se declara.
- **Qué haría falta:** decidir si un editor por dato en la GUI (valor +
  trazabilidad + fecha, sobre `verificar_declaracion_de_sitio`) es un
  requisito de producto; es la misma pregunta que E10 para los criterios.
- **Dónde vive:** `src/ventana_normativa.py::_POBLACION_DECLARABLE`

## EXT-10-02 · «Importar decisiones» importa criterios y no datos de sitio

- **Qué se difirió:** que «Importar decisiones» (sustituir=False) sume
  también el bloque `sitio` de otra sesión, y la confirmación clave a clave
  cuando pisa (pregunta abierta desde EXT-4-01).
- **Por qué:** importar decisiones de otra sesión tiene sentido para lo que
  se ELIGE —un criterio elegido en la obra A puede valer en la B—; un [S] es
  un hecho de UN sitio y sumar los de otra obra es exactamente el error que
  la etiqueta existe para impedir. Abrir sustituye, importar suma sólo
  criterios, y `_aplicar_bloques_de_sesion` es la única función que toca los
  [S] de la sesión. La confirmación clave a clave sigue sin decidirse: no
  cabe en un cluster de estado de datos de sitio.
- **Qué haría falta:** un caso de uso real en que dos obras compartan un
  [S] (no se conoce ninguno), y para la confirmación, la sesión E10 de
  editores tipados.
- **Dónde vive:** `gui/app.py::importar_decisiones`

## EXT-10-03 · La advertencia de corredor es por origen, no por texto; no bloquea y no va al JSON

- **Qué se difirió:** comparar el nombre de `--proyecto` con
  `corredor_del_proyecto` («advierte si no coinciden», letra del prompt),
  un bloqueo cuando no coinciden, y meter la advertencia en `informe_json`.
- **Por qué:** la primera versión comparaba los dos textos por contención
  normalizada y el auditor adversarial la refutó en las dos direcciones: el
  corredor del archivo es una descripción («terraplen de ~5 km de la Fase
  0-bis…») que ningún nombre de obra contiene, así que la propia obra del
  repositorio recibía el aviso siempre; y un proyecto de nombre corto («A»,
  «km») o sin nombre no lo recibía nunca. Dos rótulos escritos por personas
  no se pueden comparar con provecho. Lo que sí se sabe con certeza es el
  ORIGEN del corredor efectivo: si gobierna desde `datos_sitio.py`, los [S]
  son los de la obra del repositorio y el aviso lo dice, con o sin nombre
  de proyecto; si otra obra los declaró por sesión, la sesión es el
  proyecto y no hay nada que advertir. Sigue siendo puro, sólo avisa, y no
  va al JSON porque `Informe` no lleva `proyecto`. El [S]
  `corredor_del_proyecto` de La Unión no se reescribió para callar el
  aviso, y por eso la memoria de la obra del repositorio lo lleva: es
  cierto que sus [S] gobiernan desde el archivo.
- **Qué haría falta:** una cabecera de obra con progresivas en el CSV o en
  el sitio.json (lo que `reemplazado_por` de `corredor_del_proyecto` ya
  pide) y entonces una comparación por dato y no por texto.
- **Dónde vive:** `src/datos_sitio.py::advertencia_de_corredor`

## EXT-10-04 · La sesión embebe la corrida; el hijo del PDF sigue recalculando

- **Qué se difirió:** que el subproceso del PDF (EXT-8) lea el `informe_json`
  embebido en la sesión y sólo formatee, en vez de repetir el cálculo.
- **Por qué:** `informe_json` es un volcado de salida, no un formato de
  carga: `Informe` no tiene ida y vuelta y M11 formatea objetos, no dicts.
  Lo que E04 sí da es la equivalencia MEDIDA sobre la sesión: la CLI, al
  abrir una sesión con corrida embebida del mismo CSV y alcance, dice si su
  corrida la REPRODUCE (mismo JSON salvo la marca de tiempo) o DIFIERE, y
  eso es lo que un revisor necesita para saber si la memoria sigue vigente.
- **Qué haría falta:** un cargador de `Informe` desde su JSON, con los
  `PasoDeMemoria` incluidos; es la sesión E14 (comparador) la que lo
  necesitará primero.
- **Dónde vive:** `cli.py::_comparar_con_la_corrida_embebida`

## EXT-10-05 · El nivel de seis datos de sitio es un argumento, no una medida

- **Qué se difirió:** medir por corridas el `nivel` de `ZONA_SISMICA_LA_UNION`,
  `Z_E030`, `corredor_del_proyecto`, `carriles_por_sentido`, `clase_de_via` y
  `existe_informacion_secundaria_tramo`.
- **Por qué:** ningún módulo de cálculo los invoca por `valor()` (la zona y
  el Z son sólo referencia, Sec. 0.4; el corredor lo imprime M11 desde el
  contexto; los tres de calicatas los pide el Manual de Suelos y ningún
  módulo los consume todavía), de modo que ninguna corrida puede medirlos.
  Se clasifican por argumento, escrito junto al campo, y están censados en
  `DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA` para que el grupo no crezca en
  silencio, con la misma técnica que `test_nivel_medido`. Los otros tres se
  midieron: `PGA_roca_B` lo invoca sólo la corrida de expediente, y los dos
  de M9 se detienen antes en otros pendientes.
- **Qué haría falta:** un consumidor real de los tres de calicatas (el
  programa de exploración del expediente), que los haría medibles.
- **Dónde vive:** `tests/test_ext10_multiobra.py::DATOS_SIN_CONSUMIDOR_Y_SIN_MEDIDA`

## EXT-10-06 · El `id` de una sesión migrada sólo es estable desde que se guarda

- **Qué se difirió:** una identidad de sesión derivada del contenido (una
  huella) en vez de un `uuid4` asignado al migrar.
- **Por qué:** una sesión v1 o v2 no tiene identidad, y una huella del
  contenido cambiaría con cada campo editado, que es lo contrario de una
  identidad. `migrar_a_actual` asigna un `uuid4` nuevo a cada apertura de
  una sesión sin `id` y LO DICE en el aviso («solo sera estable cuando la
  guarde»); la ventana lo conserva en `sesion_id` y «Guardar sesion» lo
  escribe, y desde entonces abrir y guardar conservan el mismo. Los
  archivos de `tests/apoyo/` que escriben `FORMATO_SESION` sin `id` entran
  por la misma regla.
- **Qué haría falta:** nada para cerrarla; es el comportamiento elegido.
- **Dónde vive:** `src/sesion.py::_migrar_v2_a_v3`

# Parte XXVII — Lo que EXT-11 dejó escrito al medir la suite con propiedades y mutación

EXT-11 cerró PC-18 (residuo), PC-20, PC-21, PC-22 y PC-29: siete propiedades
del motor hidráulico por mallas, un arnés de mutación propio medido sobre
M3–M5/MD y el par (n_min, n_max), y la higiene de suite que el dictamen
enumeró (dos tests textuales al AST con su guardia, la corrida real en
concreto de test_cli, la ausencia real de M5, la marca `lento`, el censo de
públicas sin referencia y el cruce de los temarios como test). Cinco cosas
quedaron decididas DISTINTAS de la lectura más directa del prompt, o sin
hacer a propósito, y cada una lleva su argumento y su símbolo.

## EXT-11-01 · Sin `hypothesis` ni `mutmut`: mallas y un arnés propio, hasta que se apruebe la dependencia

- **Qué se difirió:** sumar `hypothesis` y `mutmut` a `requirements-dev.txt`
  como dependencias de TEST, con la misma justificación que PyMuPDF.
- **Por qué:** el prompt de EXT-11 manda CONSULTAR antes (regla de
  dependencias de CLAUDE.md) y da el camino por defecto si no se aprueban:
  `pytest.parametrize` sobre mallas. La consulta no obtuvo respuesta en la
  sesión, y sin respuesta la regla es que no se suma nada. Las siete
  propiedades se escribieron sobre mallas deterministas (10 secciones × 3
  materiales o el marco × 4 pendientes × 6 fracciones de Q_lleno; 58 pasos
  de q\* para la monotonía), y la mutación se midió con
  `tests/apoyo/mutacion.py`, un arnés por AST de un archivo que genera los
  ocho operadores —seis sintácticos y dos del dominio, el par de n y las dos
  velocidades— y corre los tests objetivo en subproceso. Lo que se pierde
  frente a `hypothesis` es la búsqueda aleatoria de contraejemplos y el
  encogimiento; frente a `mutmut`, la caché incremental y el catálogo
  completo de operadores. Lo que se gana es que la malla se lee entera y
  que la mutación corre en minutos sin dependencia nueva.
- **Qué haría falta:** la aprobación de las dos dependencias. Con ella, las
  mallas se conservan (son la documentación de cada propiedad) y se añade
  por encima una estrategia de `hypothesis` por propiedad; el arnés propio
  se retira si `mutmut` reproduce su censo de supervivientes.
- **Dónde vive:** `tests/apoyo/mutacion.py::MODULOS_DE_EXT11`

## EXT-11-03 · El cruce de los temarios lleva un censo manual porque el auditor y el informe numeran distinto

- **Qué se difirió:** un cruce puramente automático entre
  `temario_refutar_*.json` y la hoja `Hallazgos`, sin lista mantenida a mano.
- **Por qué:** los ítems de los temarios remiten a la numeración ORIGINAL
  del auditor (`H-13`, `E-06`, `G-06`, `H-MC-19`) y las filas del tracker a
  la del informe consolidado (`NOR-E060-03`, `NOR-HID-05`), y ningún
  documento del repositorio enlaza las dos: `auditoria_normativa.md` §13
  lista los ítems por `R95-nnn`/`hallazgo_id` sin decir a qué ficha NOR
  corresponden. EXT-0 cruzó los 71 ítems ALTA/CRÍTICA a mano y dejó huella
  sólo de los 7 con fila propia y de los 8 grupos PARCIAL anotados en
  «Vínculos cruzados»; los 45 restantes están cubiertos por una fila NOR y
  nadie lo había escrito. `CUBIERTOS_POR_FILA_NOR` es ese resto, ítem por
  ítem con la fila que lo cubre, y el test lo exige en las dos
  direcciones: un ítem sin fila, sin mención y sin censo falla, y una
  entrada del censo que el tracker ya absorbió también. Los otros 26 se
  cubren solos por (a) y (b).
- **Qué haría falta:** una columna «ID auditor» en las filas NOR del
  tracker (o en las fichas de §11 del informe) que enlace `H-nn` ↔ `NOR-*`;
  con ella el censo se deriva y desaparece.
- **Dónde vive:** `proceso/tests/test_ext11_cruce_temarios.py::CUBIERTOS_POR_FILA_NOR` (en `tests/` hasta T-12, que lo movió con el material de proceso)

## EXT-11-04 · La Fase 8 se prueba llamándola sobre el resultado real de perfil, porque el expediente no dimensiona

- **Qué se difirió:** una corrida de EXPEDIENTE que dimensione un punto
  sin ayuda, para que las Fases 6, 7 y 8 se prueben de punta a punta por la
  puerta del expediente.
- **Por qué:** a nivel de expediente V5 y V8 son obligatorias y están
  vacías (`remanso_derecho_via`, `TR_evento_extremo`), y con ellas
  declaradas piden datos que ninguna puerta aporta todavía
  (`ancho_derecho_via_m`, `Q_evento_extremo_m3s`): el bucle de MD se
  detiene ANTES de dimensionar, por diseño. La corrida de perfil sí
  dimensiona A-01, A-02 y B-01 en concreto reforzado con las Fases 6 y 7
  reales, V5 y V8 diferidas con fundamento y el contexto completo, y ESA
  corrida es `informe_dimensionado`: salida del producto sin parche. La
  Fase 8, diferida en perfil también por diseño, se ejercita llamando
  `servicio._fase_8` sobre una copia del punto real, y llega a la cama de
  apoyo del concreto y al bloqueo de la clase de producto. Se descartó la
  alternativa que la sesión escribió primero —una corrida de expediente con
  `disenar_punto` devolviendo el resultado de perfil— porque el auditor
  adversarial midió que no era «el producto»: perdía los usos de criterios
  de la Fase 4 (`correr` reinicia el registro al entrar) y mostraba tres
  puntos dimensionados a nivel de expediente con V5 y V8 ni verificadas,
  ni bloqueadas, ni diferidas. El stub de HDPE D = 0.60 m que el producto
  no podía producir (PC-20) se retiró; queda un solo doble, de la capa de
  reporte (`informe_con_criterio_desconocido`), sobre una copia.
- **Qué haría falta:** cerrar V5 y V8 en el expediente (los datos de
  remanso y del evento extremo por una puerta real); entonces la Fase 8 se
  prueba por la corrida de expediente y la llamada explícita sobra.
- **Dónde vive:** `tests/test_cli.py::informe_dimensionado`

## EXT-11-05 · El determinismo de la línea base se demuestra con los archivos comprometidos, no con una segunda corrida

- **Qué se difirió:** la segunda corrida de `regenerar.sh` que
  `test_la_corrida_es_determinista` lanzaba siempre (6 s medidos en
  5196dd2) para comparar dos corridas del mismo árbol.
- **Por qué:** los archivos comprometidos SON una corrida anterior del
  mismo árbol, hecha en otro clon y a otra hora, que es exactamente el eje
  por el que el mtime de `criterios_adoptados.py` variaba (C0). Si la
  corrida de la fixture coincide con ellos byte a byte, el determinismo
  queda demostrado con una prueba más fuerte que dos corridas seguidas en
  la misma máquina, y sin correr nada más. La segunda corrida se conserva
  para el caso rojo, donde separa los dos diagnósticos que la discrepancia
  mezcla: un campo volátil sin normalizar (dos corridas seguidas también
  difieren) o un cambio del código (dos corridas seguidas coinciden y es el
  test de la línea base el que tiene que fallar). Es la mitad «compartir la
  corrida entre sus dos tests» de PC-22; la fixture de módulo ya la
  compartía entre los otros tres desde antes del dictamen. Queda dicho lo
  que el auditor adversarial señaló: en verde, este test afirma la MISMA
  comparación que el de la línea base, con otro sentido; lo que añade es el
  diagnóstico del caso rojo, y en el clon que regeneró la línea base el
  eje del mtime no lo ejercita ninguna de las dos pruebas.
- **Qué haría falta:** nada para cerrarla; es el comportamiento elegido.
- **Dónde vive:** `tests/test_linea_base.py::test_la_corrida_es_determinista`

## EXT-11-02 · Cuarenta y tres mutantes sobreviven a toda la suite, y cada uno tiene su razón escrita

- **Qué se difirió:** matar los 43 mutantes de M3–M5/MD que sobreviven a
  los diez archivos objetivo del arnés y a la segunda vuelta (línea base,
  cierre de perfil y CLI), medidos el 2026-09-21 sobre el árbol de EXT-11:
  568 de 679 muertos en la primera vuelta (83.6 %), 65 de los 111
  supervivientes muertos en la segunda, 46 vivos; tres más murieron con la
  segunda tanda de tests que la propia lista motivó (el motivo de descarte
  del marco, la identidad de anchos en `_mismo_escalon`, la procedencia del
  ke) y quedan 43.
- **Por qué:** ninguno de los 43 es un hueco real, y la clase de cada uno
  está escrita en `SUPERVIVIENTES_CON_RAZON`: 34 son equivalentes (una
  `<=` frente a `<` cuando la banda `TOL_UMBRAL_NORMATIVO` ya cubre la
  igualdad exacta, de medida nula; las guardias del corchete de
  `tirante_normal`, inalcanzables tras la de `Q_lleno`; un `return None`
  donde sólo se lee la falsedad; un argumento por defecto que nadie usa; el
  `cota_agua` sin efecto de la vía de escenarios; el techo de la tabla del
  CBR, que el orden descendente de la tabla vuelve redundante); 6 son de
  banda (el signo de la tolerancia en V4, V4b, VC1, V7, `hw_gobernante` y
  la altura del barril, donde fijar el umbral exacto exige cotas o pesos al
  pelo); 2 son de borde
  (HW/D exactamente 0.75 y 1.2 de HDS-5 pág. 3.24, de medida nula) y 1
  está fuera del alcance de la suite (`M5.verificar` entera, porque V5
  vacía detiene el expediente antes de su último `return`; ficha
  EXT-11-04). Los huecos reales que la mutación encontró —V3 juzgando la
  rama baja, los umbrales inclusivos, las guardias del receptor, el par de
  Manning, el ke, la progresión que se repite, la cota del TW— se cerraron
  con tests y se remidieron con el arnés función por función; ninguno se
  censó. La lista se ancla por (módulo, función, operador, fragmento,
  ordinal) y `test_cada_superviviente_del_censo_sigue_siendo_un_mutante_
  del_codigo` la contrasta con lo que el arnés genera hoy.
- **Qué haría falta:** para los de banda y borde, casos construidos al pelo
  (invertir el control de salida para HW/D = 0.75 exacto, cotas que dejen
  V4 a menos de 1e-9 del admisible), que fijarían una lectura de la fuente
  que hoy es de medida nula; para el de `M5.verificar`, cerrar V5 en el
  expediente.
- **Dónde vive:** `tests/test_ext11_mutacion.py::SUPERVIVIENTES_CON_RAZON`

# Parte XXVIII — Lo que E-A dejó escrito al calcular el perfil de la lámina

E-A cerró NOR-HDS-05 entera: el perfil de la lámina de agua por paso directo
(HDS-5 pág. 3.12 y Sección 3.5), con sus dos salidas —la fracción de longitud
a sección llena, que vuelve medida la primera condición de h_o, y el HW por
remanso bajo HW/D < 0.75, que deshace la circularidad de la aproximación— y
con V1/V2 evaluadas sobre él. Siete cosas quedaron decididas DISTINTAS de la
lectura más directa de la fuente o del prompt, o sin hacer a propósito, y
cada una lleva su argumento y su símbolo.

## EA-01 · Los dorados del perfil son límites de la propia fórmula, no una corrida HY-8

- **Qué se difirió:** un caso patrón de perfil con números externos
  (HY-8 u otra corrida citable) en `tests/fixtures/casos_patron.py`.
- **Por qué:** el conflicto #7 de la matriz de auditorías prohíbe fabricar
  dorados, y el paquete I1 lo dijo para el perfil: «un caso patrón de perfil
  necesita una corrida de referencia externa citable». No la hay. Lo que sí
  se puede fijar sin inventar son los LÍMITES de la propia fórmula —con la
  línea de energía llena de punta a punta el perfil reproduce
  HW = H + h_o − S·L de `control_salida` (identidad algebraica); con TW = y_n
  el perfil es plano y HW = y_n + (1 + ke)·V_n²/2g— y el BALANCE DE ENERGÍA
  estación a estación, que es la ecuación que el método resuelve. Los números
  del prototipo (0.489, 0.391, 1.130, 0.5518, 0.501) se contrastan a la cifra
  impresa, como los del dictamen en EXT-3: lectura, no dorado.
- **Qué haría falta:** una corrida HY-8 (o equivalente) aportada por el dueño
  del expediente sobre uno de los casos del dictamen, con su archivo de
  entrada; con ella el caso entra en `casos_patron.py` con su cita.
- **Dónde vive:** `tests/test_ea_perfil_lamina.py::REL_DORADO_LIMITE`

## EA-02 · El resalto no se sitúa por momentum: la S1 que no llega a la entrada se lee como control de entrada

- **Qué se difirió:** situar el resalto hidráulico dentro del barril (HY-8
  7.3 lo hace por momentum, Sección 3.5.1) y computar la S2 desde la
  entrada aguas arriba de él.
- **Por qué:** para el HW basta lo que la Sección 3.5.1 escribe del tipo 1:
  la S1 se usa «if the S1 curve extends to the face of the culvert»; si
  corta el tirante crítico antes, el control es de entrada y el HW es el de
  la pieza 4.2, exista o no un resalto aguas abajo. Dónde queda el resalto
  cambia el tirante y la velocidad del tramo intermedio, y ahí el proyecto
  aproxima el tramo supercrítico por el uniforme —la misma decisión de EXT-3
  para el control de entrada— y toma como tirante máximo el mayor entre la S1
  medida y y_n (`PerfilLamina.y_max_m`), que es conservador para V1 y para
  V2. Situar el resalto exigiría la ecuación de cantidad de movimiento en la
  sección circular, que ninguna de las dos fuentes transcribe.
- **Qué haría falta:** transcribir la condición de profundidades secuentes
  para la sección circular y el marco (Chow o HY-8) con su cita, y una
  corrida de referencia que la valide.
- **Dónde vive:** `src/modulos/M4_control.py::perfil_lamina`
- **Cerrado (VE-5, lote m45, ítem 17):** `M4.situar_resalto` lo sitúa por momentum
  (HEC-14 Ec. 6.1; Ec. 6.5 con la sección 2 llena) entre la S2 que baja desde y_c en la
  entrada y la S1 que sube desde el receptor; viaja en `ResultadoHidraulico.resalto` y en
  el paso 4.4b. Oráculo: ejemplos SI de HEC-14 Cap. 6 (`tests/test_ve5_m45_resalto.py`).
  Dominio S < 10 % (núm. 6.3). E13: con TW = 0.70 m el resalto queda dentro.
- **Sigue diferido:** la S2 no sustituye al uniforme en V3 ni en la Fase 6, y la longitud
  del resalto (sólo gráfica) no se calcula.

## EA-03 · En la banda 0.75 ≤ HW/D < 1.2 la aproximación es el método y la comprobación manda sólo si pide más carga; el paso 4.3c puede decir NO CUMPLE sin rechazar el punto

- **Qué se difirió:** sustituir la aproximación por el remanso siempre que
  exista el perfil (la lectura de HY-8, Sección 3.5), o siempre que el barril
  no vaya lleno en la mayor parte de su longitud.
- **Por qué:** la v8 §4.3 (EXT-0) decidió que en la banda 0.75–1.2 «el método
  sí se usa, con cautela, y el remanso es la comprobación que la fuente
  pide», y el prompt de E-A pide el remanso «bajo HW/D < 0.75». La fuente
  sostiene esa lectura (pág. 3.12: «adequate results … down to a headwater of
  0.75D»). Lo que la auditoría adversarial de E-A midió es que una
  comprobación sin consecuencia no comprueba nada: en 165 de 228
  combinaciones de la banda el remanso pedía MÁS carga que la aproximación
  (hasta +34 mm, +5 %), y publicar la menor teniendo la mayor no es
  conservador. Por eso en la banda manda el mayor de los dos
  (`PerfilLamina.comprobacion_manda`) y por encima de 1.2 la aproximación, con
  el remanso impreso. La viñeta de la pág. 3.24 («can only be used if the
  barrel flows full for most of its length») es más estricta que su propia
  prosa y el proyecto la MIDE en vez de aplicarla: cuando la aproximación se
  usa y el barril no va lleno en la mayor parte, el paso 4.3c imprime NO
  CUMPLE sobre esa condición, con la cita de la 3.12 que ampara el HW. No es
  la divergencia de SIS-A-07 (`TipoDeVeredicto` lo dice): lo que no se cumple
  es la condición ideal de un método cuya validez la propia fuente extiende,
  y `verificaciones_incumplidas` lee las `Verificacion`, no los pasos. V3
  tampoco cambia: sigue comparando `V_erosion` del uniforme (EXT-3).
- **Qué haría falta:** que la v8 §4.3 decida que el remanso gobierna siempre
  que exista; con ella `HW_efectivo_m` devuelve siempre el remanso y el paso
  4.3 se vuelve informativo.
- **Dónde vive:** `src/modelos/hidraulica.py::PerfilLamina`

## EA-04 · La compuerta de h_o queda como guardia sin alcance en producción

- **Qué se difirió:** retirar `servicio._compuerta_metodo_h_o`, los dos casos
  de `MetodoNoEvaluableError` bajo control de salida y el texto
  `M5.PROCEDIMIENTO_PERFIL_LAMINA`.
- **Por qué:** con el perfil que M4 emite siempre, la aproximación fuera de
  rango no se usa y `ResultadoHidraulico.h_o_fuera_de_rango` no puede ser
  True; V1/V2 tampoco llegan al `MetodoNoEvaluableError`. Pero el tipo sigue
  admitiendo un resultado SIN perfil —los constructores de la suite que no
  pasan por M4—, y ahí la guardia es la respuesta honesta: no se inventa un
  llenado. Retirarla convertiría ese estado en un `AttributeError` fuera de
  `ErrorProyecto`. Los dos tests que la llaman directamente
  (`test_ext3_regimen_barril`, `test_ea_perfil_lamina`) fijan que dispara sin
  perfil y calla con él.
- **Qué haría falta:** que `ResultadoHidraulico.perfil` deje de admitir
  `None` —lo que exige reescribir los constructores de la suite— y entonces
  la compuerta y los dos casos se retiran juntos.
- **Dónde vive:** `src/servicio.py::_compuerta_metodo_h_o`

## EA-05 · «Most of its length» es un [A] con ventana, y su lectura vive en el registro

- **Qué se difirió:** un número [N] para «most of its length», o la
  cuantificación por la fuente.
- **Por qué:** «most» es una palabra de la fuente, no un número. La primera
  redacción de E-A lo escribió como 1/2 en `constantes_normativas.py` («el
  significado de la palabra»), y la auditoría adversarial lo refutó con la
  propia `Interpretacion` registrada: admite «casi toda», o sea que hay
  alternativas, y una lectura con alternativas es una elección con ventana,
  [A] por la taxonomía de CLAUDE.md. Es `'fraccion_llena_mayor_parte'`
  (0.5, sensibilidad 0.5–0.9, nivel perfil, forma float) y la lectura
  sigue en `citas.INTERPRETACION_MAYOR_PARTE`, con lo que juega en contra.
  Sólo mueve el rótulo del veredicto del paso 4.3c: la consecuencia de fallar
  la condición la fija la pág. 3.12 (EA-03).
- **Qué haría falta:** que la fuente cuantifique «most»; entonces el número
  pasa a [N] y la `Interpretacion` se retira.
- **Dónde vive:** `src/criterios/hidraulica.py::fraccion_llena_mayor_parte`

## EA-06 · Veinticuatro mutantes del perfil sobreviven a toda la suite, y cada uno tiene su razón escrita

- **Qué se difirió:** matar los 24 mutantes de `M4.perfil_lamina` y sus
  auxiliares que sobreviven a los once archivos objetivo del arnés
  (`tests/test_ea_perfil_lamina.py` sumado a los diez de EXT-11) y a la
  segunda vuelta (línea base, cierre de perfil, CLI), medidos el 2026-09-21
  con `--funcion` sobre las once funciones tocadas por E-A: 242 mutantes,
  212 muertos en la primera vuelta (87.6 %), 5 más en la segunda, 25 vivos.
  Uno era un hueco real —`V_entrada_m_s` del retorno UNIFORME, que ningún
  test leía (Q/A → Q·A sobrevivía)— y se cerró con una aserción en el dorado
  de flujo uniforme; una primera medición, antes de la auditoría adversarial,
  había dejado 37 vivos y motivó cinco tests más y la retirada de dos
  términos muertos (`max(y_max, y_n)`, `min(V_min, Q/A_n)`).
- **Por qué:** ninguno de los 24 es un hueco, y la clase de cada uno está en
  `SUPERVIVIENTES_CON_RAZON`: 4 ya estaban censados desde EXT-11
  (`hw_gobernante` ×2, V1, V2: banda); de los 20 nuevos, 13 son de borde
  (una igualdad exacta en punto flotante: la raíz de Sf = S en un extremo del
  corchete, Sf exactamente S en la frontera o en la línea llena, HW/D
  exactamente 0.75 o 1.2, el corte de la clave o un escalón que termina
  exactamente en la entrada, dx exactamente cero, una frontera a
  exactamente 1e-9 m de y_c, de la clave o de la asíntota), 5 son
  equivalentes (el signo del cociente frente al del producto; TW == D;
  TW == y_c; `longitud_llena` = 0 en los dos retornos donde el mutante lo
  multiplica) y 2 son de banda (la frontera a menos de 2·TOL de y_c, y el
  freno de la escalera en 1e-12·S frente a 1e-12/S, entre los que ninguna
  estación cae porque acercarse tanto a la asíntota exige del orden de 1e9
  escalones). Los de borde y banda son los de siempre: fijarlos pediría
  casos al pelo sobre tolerancias numéricas que no mueven ninguna magnitud.
- **Qué haría falta:** casos construidos exactamente sobre cada borde
  (un TW igual a y_c a la ulp, un Sf_llena igual a S), que fijarían lecturas
  de medida nula; nada para los equivalentes.
- **Dónde vive:** `tests/test_ext11_mutacion.py::SUPERVIVIENTES_CON_RAZON`

## EA-07 · La asíntota del perfil no es el tirante normal de M3, y la diferencia queda impresa

- **Qué se difirió:** unificar la ley de fricción del perfil (Ec. 3.7 con
  `K_FRICCION_SI` = 19.63) con la de Manning en M3 (`K_MANNING_SI` = 1), o
  clasificar el perfil contra `y_normal`.
- **Por qué:** la auditoría adversarial de E-A midió que 19.63/(2·9.81) =
  1.00051, de modo que en el y_n de Manning la pendiente de fricción del
  perfil vale 1.00051·S y la lámina tiende a un y_n' un 0.05 % más alto
  (0.07 mm en D = 0.90, Q = 0.3, S = 0.001). Clasificar contra y_n dejaba una
  banda de TW entre y_n y y_n' en la que la escalera iba contra su propio
  perfil y lanzaba `LimiteNumericoError`. La corrección es clasificar e
  integrar contra la raíz de Sf = S con la MISMA ley
  (`M4._llenado_donde_Sf_iguala_S`), publicar y_n' junto a y_n en el paso
  4.3c y no tocar la ley: 19.63 es el número que la fuente escribe para la
  fricción del control de salida (v8 §4.3, conflicto #6) y M3 sigue siendo
  Manning con k = 1 como manda la Sec. 4.1; el 0.05 % es el mismo que separa
  19.63 de 2g y está declarado desde PD.
- **Qué haría falta:** que la v8 decida una sola g para la fricción (2g o
  19.63), lo que movería el término de fricción de H en un 0.05 % y con él la
  línea base; hasta entonces las dos asíntotas conviven, dichas.
- **Dónde vive:** `src/modulos/M4_control.py::_llenado_donde_Sf_iguala_S`

# Parte XXIX — Lo que E-B dejó escrito al construir los editores tipados, el comparador y el índice

E-B ejecutó las cuatro piezas del último prompt de la cadena (E10, E14, E13
reducido, E21 acotado) sobre lo que EXT-4, EXT-5 y EXT-10 ya habían dejado:
la forma de cada criterio, el contexto de corrida y la sesión con corridas
embebidas. Seis cosas quedaron decididas DISTINTAS de la lectura más directa
del prompt, o sin hacer a propósito, y cada una lleva su argumento y su
símbolo.

## EB-01 · El literal sigue existiendo: el editor lo compone y es la fuente al aplicar; un dict que la ficha no descompone no recibe campos inventados

- **Qué se difirió:** sustituir el campo literal «Valor nuevo» de la pestaña 2
  por los editores tipados, y dar campos a TODOS los `dict_con_campos`.
- **Por qué:** el literal es el único camino de declaración desde EXT-5 y
  los cuatro apoyos de ventana real de la suite declaran por él; los
  editores lo COMPONEN (dos vistas, un valor) en vez de abrir un segundo
  camino con su propia guardia. Al aplicar, la fuente es el editor cuando
  tiene campos y el literal cuando no (`_valor_a_declarar`): medido en la
  ventana real, un campo que no arma (n = 0.05 fuera de su ventana) dejaba
  el literal en el valor ANTERIOR y «Aplicar» declaraba un número que el
  proyectista no veía. Y un dict cuyos campos no salen de la ficha —un dict
  de dicts como `cobertura_minima_aashto`, o uno vacío sin ventana ni
  campos obligatorios como `N_cq_N_gammaq_meyerhof`— cae al editor LITERAL:
  darle campos sería escribir en el editor lo que la ficha no declara,
  que es el error que el proyecto persigue en todas partes.
- **Qué haría falta:** que las fichas de esos dicts declaren sus campos
  (`campos_obligatorios`, o una ventana por campo) y entonces el editor
  los deriva solo; no hay nada que cambiar en `gui/editores.py`.
- **Dónde vive:** `src/editores.py::_campos_del_dict`

## EB-02 · Una categoría no exige fila, y un número nunca nombra una fila

- **Qué se difirió:** exigir la fila de la tabla a TODO criterio `de_tabla`
  al declararlo desde la pestaña 2, y resolver por el número tecleado la
  fila de la que «proviene».
- **Por qué:** en una `categoria` la selección normativa ES el conjunto
  cerrado que la ficha deriva de la tabla (`sensibilidad`): las filas de
  `condicion_pavimento` son materiales de conducto y sus claves no son los
  tres textos que el criterio admite, de modo que exigir fila la habría
  vuelto indeclarable, y por eso sus filas se ofrecen como contexto y no
  proponen valor (la primera versión proponía la clave de la fila y la
  guardia la rechazaba en las catorce: R8 de la auditoría adversarial). Y
  un número no nombra ninguna fila, ni cuando coincide con una sola celda:
  la primera versión infería la única coincidencia y la auditoría midió que
  0.9 atribuía `ke_entrada` a «Corrugated metal, projecting» sin que nadie
  la eligiera (R3); adivinar la fila es inventar la procedencia (EXT-V-02
  al revés). El rechazo DICE con qué filas coincide el número, para que se
  elija. Teclear la CLAVE de una fila sí la nombra —es el camino del ratón
  de EXT-5, que sigue valiendo—, y vale para toda fila, elegible o no: la
  que no lo es la rechaza R4 en `declaracion`, como desde la ventana
  emergente (R4 de la auditoría: con nota entraba por `declarar_valor`).
  Un dato `de_ensayo` exige la nota, que es su trazabilidad (A1, Conflicto
  #8). Y un texto que nombra una fila DISTINTA de la elegida no entra, con
  o sin nota: la revisión posterior al cierre midió que
  «cajon_aletas_paralelas_escuadra» (ke = 0.7) entraba con la fila
  «cajon_aletas_30_75_escuadra» (ke = 0.4) y la memoria citaba la segunda;
  la parte 2 había cerrado el DIFIERE para números, pares y dicts y no para
  el texto. La guardia vive en la puerta
  (`declaracion.declarar_desde_tabla`) y por eso cubre también la ventana
  emergente.
- **Qué haría falta:** nada para el producto; una tabla con una fila por
  categoría permitiría emparejar `categoria` con fila, y entonces
  `exige_fila` podría incluirla.
- **Dónde vive:** `src/editores.py::fila_implicita`

## EB-03 · El comparador compara volcados, no informes; «método» son tres campos

- **Qué se difirió:** un cargador de `Informe` desde su JSON (la ficha
  EXT-10-04 lo pedía «para el comparador») y una definición más ancha de
  «método distinto».
- **Por qué:** el comparador trabaja sobre dos `dict` y no necesita
  reconstruir objetos: comparar volcados es lo que la línea base hace byte
  a byte y lo que la CLI hacía con `==` sobre la corrida embebida; ahora hay
  UNA definición de «la misma corrida» y las dos la llaman. Cargar un
  `Informe` desde JSON seguiría siendo un segundo motor sin tests, y
  EXT-10-04 queda como estaba. «Método distinto» son el control gobernante,
  el régimen del barril y el tipo de perfil de la lámina: los tres deciden
  de qué fórmula salió cada número del diseño; el material o la sección no
  son método sino RESULTADO, y su cambio se reporta como diferencia.
- **Qué haría falta:** un consumidor que necesite el objeto —el hijo del
  PDF leyendo la corrida embebida— y entonces el cargador, con los
  `PasoDeMemoria` incluidos.
- **Dónde vive:** `src/comparador.py::CAMPOS_DE_METODO`

## EB-04 · Responsable y evidencia son una derivación de la ficha, no una matriz; van al JSON y no a la memoria

- **Qué se difirió:** la «matriz requisito-aplicabilidad-responsable-
  evidencia» del plan original, y una columna de responsable en la memoria
  HTML.
- **Por qué:** el dictamen la descartó por no tener forma en el esquema del
  registro; lo que E13 reducido pide cabe en dos lecturas de objetos que ya
  existen —`resolucion` dice quién fija el valor y `reemplazado_por` (o la
  trazabilidad exigida por el ensayo, o la fuente de un vacío) qué lo
  sostiene— y por eso vive en un módulo sin estado que leen el anticipo y
  M11. Van al JSON `criterios.bloquearon` porque es el otro reporte de la
  corrida y dejarlo sin la columna que la pestaña 4 muestra repetiría
  SIS-A-13; no van a la memoria porque el bloque de pendientes ya imprime
  «Qué lo resuelve» desde `reemplazado_por` y una segunda columna diría lo
  mismo con otras palabras.
- **Qué haría falta:** un caso en que responsable y evidencia no se lean de
  la ficha (una asignación de obra, un plazo), que sería un campo nuevo de
  `Criterio` y una decisión de producto.
- **Dónde vive:** `src/responsable.py::evidencia_de`

## EB-05 · El índice se deriva de la plantilla y de los puntos; el «histórico» no ganó una vista

- **Qué se difirió:** un índice escrito en la plantilla, un índice de pasos
  dentro de cada punto, y una vista del histórico de corridas (el «e
  histórico» del título del prompt).
- **Por qué:** el índice sale de los `<h2 id>` del texto que se va a
  imprimir y de los `InformePunto`, de modo que no puede divergir de las
  secciones ni de los puntos («nada que no exista como objeto»); un índice
  de pasos por punto duplicaría los `<h5>` que el anexo ya enlaza (EXT-8) y
  engordaría la memoria que EXT-8 adelgazó. El histórico ya existe como
  objeto desde EXT-10 —las corridas embebidas en la sesión, con su
  `informe_json`— y la CLI ya dice si una corrida reproduce la guardada; la
  pieza que faltaba para leerlo es el comparador de E14, y una vista de
  lista de corridas no añade ningún objeto nuevo. Consecuencia que conviene
  saber: una `--plantilla` propia sin `%%indice` cae en la guardia de
  contenido (SIS-B-06), porque el índice nunca está vacío; es el mismo
  precedente que el anexo de EXT-8, y la plantilla se corrige añadiendo el
  marcador.
- **Qué haría falta:** una pestaña o un volcado que liste las corridas de la
  sesión y compare dos cualesquiera por el comparador; es presentación
  sobre objetos que ya existen.
- **Dónde vive:** `src/modulos/M11_reporte/anclas.py::indice_de_la_memoria`

## EB-06 · La ventana emergente conserva su campo único; las dos ventanas no se unifican

- **Qué se difirió:** montar los editores tipados también en la ventana
  normativa emergente (`gui/ventana_normativa.py`), que declara con UN
  `CampoValidable` y el mismo parser.
- **Por qué:** la emergente existe para LEER la norma —la tabla completa con
  sus notas, el rango con su semántica— y su campo declara lo que esa
  lectura decide; los editores tipados existen para COMPONER un valor
  estructurado, que es la pregunta de la pestaña 2. Las dos comparten el
  parser (EXT-5) y la puerta de declaración, que es lo que impide que
  diverjan; duplicar los editores en la emergente habría sido un segundo
  sitio donde mantener la misma composición.
- **Qué haría falta:** decidir si la emergente absorbe la pestaña 2 (una
  sola ventana de declaración), que es una decisión de producto y no de
  este cluster.
- **Dónde vive:** `gui/ventana_normativa.py::_pie`

---

# Parte XXX — Lo que PF-1 dejó escrito al abrir el vacío de PC-03

## PF-1-01 · La carga a la entrada fuera de rango es un vacío declarable, no un método no evaluable ni un descarte definitivo

- **Qué se difirió:** tratar el HWi/D ≤ 0 de MAT-D10 como
  `MetodoNoEvaluableError`, y la otra mitad que el prompt PF-1 pedía:
  probar «el siguiente diámetro» antes de descartar el material.
- **Por qué:** la taxonomía se pregunta en orden y este caso se detiene en
  «declarar»: H_c, que el paso 4.2.1 ya resolvió, es un piso que el
  proyectista puede adoptar cuando la ecuación no entrega carga; un método
  no evaluable es el que ninguna declaración resuelve (V1/V2 exigían un
  cálculo). PC-03 medía un descarte definitivo y mudo; con el criterio [A]
  de perfil `hw_entrada_fuera_de_rango` el bloqueo viaja con clave, punto y
  el par (Q, S) con su S*. El piso acota el signo y no impone H_c como
  mínimo (la carga salta en S*: la ficha lo dice). El «siguiente diámetro»
  estaba al revés: S*(D) no crece con D bajo Forma 1, la de las tres cartas
  circulares; bajo Forma 2 no es general y con S ≤ `S_CAUCE_MAX` sólo la
  Forma 1 no sumergida puede dispararse. La v8 §4.2 describía el rechazo
  anterior y se enmendó con nota «Corregido». El argumento entero, con los
  números medidos, está en el docstring del símbolo.
- **Qué haría falta:** un procedimiento de control de entrada válido para
  pendientes de ese orden en una fuente de `normas/`, que convertiría el
  [A] en [C] o lo retiraría.
- **Dónde vive:** `src/modulos/M4_control.py::_resolver_hw_fuera_de_rango`

---

# Parte XXXI — Lo que PF-2 dejó escrito al abrir el pre-vuelo de datos por punto

## PF-2-01 · El pre-vuelo estima de más a propósito, y lo que exige una sola familia es un dato declarado del servicio, no una deducción

- **Qué se difirió:** que el cuarto bloque del anticipo reproduzca EXACTAMENTE
  lo que la corrida registra (ni una falta de más), y que la familia que
  exige una columna admitida vacía se derive del código en vez de declararse.
- **Por qué:** la corrida registra UN bloqueo por etapa (`servicio._etapa`) y
  se detiene en la primera falta de cada punto, de modo que las siguientes
  no llegan a producirse; el pre-vuelo existe justamente para decirlas todas
  de una vez, y por eso estima de más en la dirección medida (sin luz, C-01
  no pasa de la Fase 2; con luz y TW, el bucle de MD se detiene en `Q_m3s`;
  con el JSON ampliado, MD se detiene en los criterios del cajón antes de
  que VC1 exija la coronación). La dirección que importa la fija la unión de
  `tests/test_pf2_prevuelo.py`: ningún `DatoFaltanteError` real sobre una
  columna o una clave externa escapa a la estimación —ni los que M0 lanza
  al cargar, que no son bloqueos: el auditor adversarial midió que una celda
  obligatoria vacía «cubierta» por el JSON salía como resuelta cuando M0 la
  rechaza antes de leer el JSON, y desde la parte 2 la carga se comprueba
  PRIMERO—, y lo de más queda censado con su razón. Qué familia exige
  `cota_coronacion_canal` (VC1, sólo C) o `area_ha` (`M1._categoria_por_area`,
  sólo A) no se lee del AST —el consumidor es el mismo módulo en las tres
  familias y la compuerta vive en la lógica de `_verificador_perfil` y de
  `periodo_retorno_de`—: se declara en `servicio.FAMILIAS_QUE_EXIGEN_COLUMNA`,
  al lado de `FAMILIAS_QUE_USAN`, que nació igual y se corrigió por medida;
  y las claves externas con vía alterna en el código (`longitud_m`,
  `categoria_tr`, `S_conducto`) se declaran en
  `servicio.EXTERNOS_CON_VIA_ALTERNA` con un test que exige la partición
  exacta. El TW no se declara: `servicio.tw_sin_via_de_sec_1_3` es el
  predicado que `_resolver_tw` y el pre-vuelo comparten (registra el uso de
  `seccion_receptor` fuera de una corrida; inocuo, porque `servicio.correr`
  vacía los usos al entrar).
- **Qué haría falta:** una corrida «en seco» que registre TODAS las faltas de
  un punto sin detenerse en la primera —es otra semántica de `_etapa`— y
  entonces el pre-vuelo sería una medida y no una estimación.
- **Dónde vive:** `src/anticipo.py::datos_faltantes_por_punto`

# Parte XXXII — Lo que PF-3 dejó escrito al abrir el barrido de sensibilidad

## PF-3-01 · El barrido vive en la CLI y en el servicio, y desde UI-3 también en el botón «Barrido…» de la pestaña 2 — cerrado (UI-3)

- **Cerrado (UI-3):** PF-3 difirió el botón «Barrido…» de la pestaña 2 sobre el criterio
  seleccionado. UI-3 lo pone (`gui/app.py::_abrir_barrido`): activo sólo con un criterio
  que tenga ventana de sensibilidad y no se derive, apagado con su motivo en los demás
  (`MOTIVO_SIN_VENTANA`, `MOTIVO_DERIVADO`) y mientras haya otra ventana de barrido
  abierta (`MOTIVO_BARRIDO_ABIERTO`). Abre `gui/ventana_barrido.py::VentanaBarrido`: la
  lista de valores compuesta con el editor tipado de E-B (`construir_editor` sin su nota),
  un valor por fila, y una fila y una nota para todos —las de `--barrido-fila` y
  `--barrido-nota`, con el rótulo de «Aplicar» (`gui/editores.py::rotulo_de_la_nota`)—. La
  puerta es `barrido.verificar_valores`, antes de lanzar nada. Corre en un proceso hijo
  (ficha UI3-01), pinta `barrido.lineas_de_la_tabla` sobre el JSON del hijo
  (`barrido.resultado_del_volcado`, el inverso de `volcado_del_barrido`) con la columna de
  las incumplidas y el «no comparable», guarda ese JSON, se cancela, y al cerrarse
  refresca la pestaña 2. No arma memoria ni toca los exportadores. UI-4 lo recorrió en la
  ventana de verdad sobre la corrida de la guía y encontró que la tabla del barrido nacía
  en un panel de alto cero (corregido, ficha UI4-01): hoy se ve sin mover el divisor.
- **Por qué así:** es lo que esta ficha pedía —el editor tipado, fuera del hilo de Tk, sin
  tocar el informe de la pestaña 3, la pestaña 2 refrescada al volver y su test de ventana
  real (`tests/test_ui3_barrido_ventana.py`)—. Lo único nuevo en `src/` es leer de vuelta
  el JSON del barrido: sin ello la ventana pintaría con una copia suya de la tabla.
- **Qué haría falta:** nada para esta ficha. La frase de `CLAUDE.md` «El botón «Barrido…»
  de la pestaña 2 se difirió con símbolo», desfasada desde UI-3, la corrigió el dueño
  tras la cadena UI (2026-11-15; ficha UI4-02).
- **Dónde vive:** `gui/ventana_barrido.py::VentanaBarrido`

# Parte XXXIII — Lo que PF-4 dejó escrito al declarar el régimen de V2b

## PF-4-01 · INDICADOR es un valor de `TipoDeVeredicto` y no una cuarta capa del estado de verificación; el segundo indicador del 5.3.3 sigue sin evaluarse

- **Qué se difirió:** dos cosas, y ninguna es la corrección de PF-4. (1) La
  unificación de las tres capas del estado de verificación que PC-27 dejó
  «Cerrado parcial» —`Verificacion.cumple: bool`, `TipoDeVeredicto` adosado
  al `PasoDeMemoria` y `Bloqueo`—: PF-4 la toca sin cerrarla. Añade el quinto
  valor `INDICADOR` a la capa del veredicto y deja `cumple` como el bool que
  lee la compuerta de MD (`all(v.cumple ...)`), de modo que bajo `regimen_v2b`
  = `indicador_con_aviso` una misma `Verificacion` dice `cumple=True` al
  pipeline y `INDICADOR` a la memoria, a propósito y con el JSON llevando las
  dos cosas (`cumple` y la clave nueva `veredicto` de `_verificacion_json`).
  (2) El segundo indicador del num. 5.3.3 —«roughness greater than the
  channel»—, que exige el n de Manning del cauce natural: no es columna de la
  Sec. 1.2, la hoja de ruta no lo fija y ninguno de los dos regímenes lo
  evalúa; `regimen_v2b.verificacion_pendiente` lo dice con esas palabras.
- **Por qué:** para (1), porque el prompt de PF-4 lo prohíbe con razón: «el
  estado de verificación ya tiene tres capas y no puede ganar una cuarta sin
  cerrar aquélla». Un valor nuevo de la capa existente no es una capa: no
  añade un objeto que los lectores tengan que consultar además de `cumple`,
  y lo que dice —«se evaluó, el indicador se disparó, y el proyecto decidió
  por un [A] declarado no detener el punto»— no lo podía decir ninguno de
  los cuatro valores anteriores sin mentir (CUMPLE), sin divergir del
  pipeline (NO_CUMPLE, SIS-A-07), sin fingir que no se evaluó (DIFERIDO) o
  que no se juzgó (SIN_VEREDICTO). `Veredicto.cumple` sigue devolviendo
  False para INDICADOR y no tiene consumidor de producción (medido por grep
  en PF-4). Para (2), porque la regla de la constitución para un vacío es no
  inventarlo: el dato que cerraría la fila entera es un [S] por punto que
  hoy nadie levanta.
- **Qué haría falta:** para (1), la sesión que PC-27 sigue esperando: un
  solo estado de verificación del que `cumple`, el veredicto del paso y el
  `Bloqueo` sean vistas y no fuentes, con «no aplica» como valor, y
  `EstabilidadCabezal` sin su tupla vacía. Para (2), una columna
  `n_manning_cauce` de la Sec. 1.2 (o un [S] por punto) con su
  trazabilidad, y la segunda comparación en `M5.v2b_sedimentacion` bajo el
  mismo `regimen_v2b`.
- **(1) cerrada en C10:** `EstadoDeVerificacion`, ver C10-02. (2) sigue.
- **Dónde vive:** `src/modelos/memoria.py::TipoDeVeredicto`

## PF-4-02 · El barrido leía el veredicto sólo de `cumple`, y desde PF-4 son dos campos

- **Cerrado (PF-4):** `src/barrido.py` decidía si una verificación «cambia de
  veredicto» mirando un solo sufijo del rótulo del comparador,
  `_CAMPO_VEREDICTO = ".cumple"`. Con el veredicto INDICADOR eso deja de
  bastar: bajo `regimen_v2b` = `indicador_con_aviso` una verificación pasa de
  CUMPLE a INDICADOR con `cumple` en True las dos veces, y la tabla del
  barrido habría dicho «sin cambios de veredicto» sobre una corrida en la que
  el indicador se disparó. Son dos campos desde PF-4
  (`_CAMPOS_DE_VEREDICTO`), y el conjunto de códigos deduplica, de modo que
  una verificación que mueve los dos sigue contando una vez.
- **Abierto:** nada de este hueco. Queda dicho porque es la clase de defecto
  que un campo nuevo del volcado produce en silencio: todo lector que
  clasifique diferencias del comparador POR NOMBRE DE CAMPO hay que revisarlo
  cuando `cli._verificacion_json` gana una clave. Los otros lectores se
  midieron en PF-4 y ninguno lo hace: `comparador` compara el dict entero,
  `MD` y `servicio.InformePunto.incumplidas` leen el objeto y no el volcado,
  y la interfaz cuenta por `incumplidas()`.
- **Qué haría falta:** nada; está cerrado. Para no repetirlo, el sitio donde
  se decide qué campos del volcado son «el veredicto» es esa tupla, y es la
  que hay que ampliar si aparece un tercero.
- **Dónde vive:** `src/barrido.py::_CAMPOS_DE_VEREDICTO`

# Parte XXXIV — Lo que PF-5 dejó escrito al abrir la guía de corrida de perfil

## PF-5-01 · La guía dice lo que el programa hace, no lo que el prompt suponía: diez [A] de perfil sin valor, un `si` a perfil, una celda del CSV y una sesión escrita a mano

- **Qué se difirió:** cuatro lecturas del prompt de PF-5 que el árbol ya no
  sostenía, resueltas del lado del programa. (1) «Los nueve [A] de perfil sin
  valor» son DIEZ desde PF-1 (`hw_entrada_fuera_de_rango`): la guía lista lo
  que `ca.criterios_de_perfil_sin_valor()` devuelve y el test compara contra
  la función, no contra un número. (2) «Expediente cerrado: no» no es lo
  esperado cuando nada bloquea al alcance declarado: `Informe.cerrado` mide
  contra el alcance, y la corrida completa (cuatro puntos, cero bloqueadas,
  trece diferidas) imprime `si` y sale con 0. La guía muestra el `no` de la
  corrida con el cajón sin declarar y el `si` de la completa, y dice que un
  `si` a perfil no es un expediente completo. (3) Sobre `tests/ejemplo_puntos.csv`
  tal cual la Familia C no dimensiona nunca: la coronación del canal de C-01
  va vacía a propósito (`M0_carga.VACIOS_ADMITIDOS`) y VC1 detiene el punto.
  La guía trabaja sobre una COPIA con esa sola celda rellenada, y el test la
  construye desde el CSV del repositorio y exige que la fila de la guía
  difiera del ejemplo exactamente ahí. (4) La sesión la escribe la ventana y
  la CLI no tiene bandera para escribirla: la guía muestra una sesión mínima
  con las claves de `sesion.sesion_vacia`, el test la valida con
  `sesion.errores_de_sesion`, la corre con `--sesion` y exige que sus siete
  criterios sean los del comando `--declarar` de la guía.
- **Por qué:** la regla de PF-5 es «NADA que no exista como objeto», y las
  cuatro lecturas describían objetos que no existen así. Lo que la guía
  promete lo mide `tests/test_guia_perfil.py` corriendo sus bloques en
  subproceso y comparando las líneas del RESUMEN impresas en la guía con la
  salida real: si el programa cambia, la guía se pone en rojo antes que en
  falso.
- **Qué haría falta:** para (1) y (2), nada. Para (3), rellenar la celda en
  el CSV del repositorio movería la línea base y los tests de PF-2 que miden
  el vacío. Para (4), una bandera de la CLI que escriba la sesión de una
  corrida (`sesion.corrida_para_sesion` ya produce el bloque `corridas`),
  que no está pedida.
- **Dónde vive:** `tests/test_guia_perfil.py::ORDEN_EN_LA_GUIA`

## PF-5-02 · Lo que el test de la guía comprueba y lo que deja a la prosa

- **Qué se difirió:** la guardia sobre la PROSA de la guía. El test mide
  las siete tablas generadas texto a texto contra `tests/apoyo/guia_perfil.py`
  (derivadas de `M0_carga.COLUMNAS` y `VACIOS_ADMITIDOS`,
  `servicio.CLAVES_EXTERNAS` con la bandera leída del parser real,
  `datos_sitio.DATOS_SITIO`, `ca.criterios_de_perfil_sin_valor()` con
  `Criterio.forma`, `M11.COLUMNAS_RESUMEN_CSV`, `sesion.sesion_vacia`); los
  ocho bloques de comandos ejecutados en orden con sus archivos, su código
  de salida y las líneas del RESUMEN; los diez ejemplos de `--declarar` por
  la puerta real; y el enlace del README. Las frases sueltas —qué significa
  cada cifra del RESUMEN, la precedencia por punto > bandera > global, qué
  resuelve «por otra vía» cada clave— se escribieron leyendo
  `Informe.cerrado`, `DatosExternos.dato` y `EXTERNOS_CON_VIA_ALTERNA`, y
  ninguna guardia las relee. La columna «Ventana» se deriva con tres ramas
  (`categoria` → opciones de `sensibilidad`; `DeTabla` → tablas; `Libre` →
  `dominio`): un criterio con otra resolución, o una `Libre` sin `dominio`,
  hace que el generador lance `ValueError` hasta que la ficha diga su ventana.
- **Por qué:** la prosa que explica un objeto no se deriva de él sin un
  segundo motor de texto, y una guía redactada para pasar un test deja de
  redactarse para el tesista. Lo que sí se deriva —listas, formas, ventanas,
  cifras impresas— es lo que envejece en silencio, y eso se deriva.
- **Qué haría falta:** una afirmación por frase que alguien quiera vigilar,
  escrita como test contra el símbolo que la sostiene, como
  `test_decisiones_diferidas` ancla cada ficha por símbolo y no por texto.
- **Dónde vive:** `tests/apoyo/guia_perfil.py::ventana_de`

# Parte XXXV — Lo que PF-6 dejó escrito al cerrar tres cabos

## PF-6-01 · El CBR no tiene techo que la fuente fije: `CBR_MAX_FISICO` se retira y queda sólo el piso

- **Cerrado (PF-6):** R48-007. `dominios.CBR_MAX_FISICO = 100.0` topaba el
  CBR de subrasante y M0 lo aplicaba con `DatoInvalidoError`, con el
  comentario «por encima de 100 el dato está en otra escala o mal
  transcrito». Verificado contra el PDF del Manual de Suelos, Geología,
  Geotecnia y Pavimentos (MTC): el Cuadro 4.11 «Categorías de Sub rasante»
  (pág. impresa 37 / PDF 38) deja S5 abierta («CBR ≥ 30%»); el Cuadro Nº
  10.2 «Valor Relativo de Soporte, CBR en Base Granular» (pág. impresa 108 /
  PDF 109) exige «Mínimo 100%» a la base de carreteras de primera clase o
  tráfico > 10 × 10⁶ EE; el Cuadro 12.13 (pág. impresa 129 / PDF 130)
  tabula «Base Granular CBR 100%»; y en las 281 páginas no hay techo del CBR
  ni la expresión «piedra patrón». Un techo que la fuente no fija es un
  valor de proyecto inventado, y `dominios.py` sólo acota lo que un dato
  PUEDE SER. Queda `CBR_MIN_FISICO = 0.0` (exclusivo), que es lo único que
  la escala fija, y la ayuda lo rotula como piso.
- **Abierto:** la ficha del tracker llamaba «tabla de base granular» al
  Cuadro 12.13, que es la tabla de coeficientes estructurales a_i; la cita
  fuerte es el Cuadro Nº 10.2, y así se dejó escrito junto al símbolo. Y la
  fuente no afirma que un CBR > 100 % sea legítimo con esas palabras: lo que
  sostiene sin interpretar es que no fija techo. Que la tabla de resguardo
  de Sec. 5.1 tenga su fila más alta ilimitada (`test_M5_verificaciones`) es
  lo que hace que un CBR alto no deje a V4 sin fila.
- **Qué haría falta:** nada para el techo. Si alguna vez una norma peruana
  fijara una escala cerrada del CBR, volvería como [N] con numeral, no a
  `dominios.py`.
- **Dónde vive:** `src/dominios.py::CBR_MIN_FISICO`

## PF-6-02 · El editor escalar suelta la fila cuando el texto deja de ser su clave, y sólo entonces

- **Cerrado (PF-6):** `EditorEscalar` prellenaba la clave de la fila
  elegida y dejaba el campo editable; reescribirlo con la clave de otra
  fila dejaba `fila()` en la vieja y la puerta rechazaba con «NOMBRA la
  fila…». Ahora una traza sobre el texto suelta la fila cuando el texto
  deja de ser su clave, sin declarar nada (la guardia por AST de EB-01 sigue
  verde), y la pestaña 2 declara la fila que el texto nombra por
  `src.editores.fila_implicita`. Medido en la ventana de verdad
  (`tests/apoyo/gui_eb_real.py`, bloque 3b).
- **Abierto:** la suelta vale SÓLO para las filas que ponen su CLAVE
  (`embocadura_cajon`, `ke_entrada_cajon`, `n_manning_cajon`). En una fila
  que pone una CELDA (`ke_entrada`, 0.5 de la Tabla C.2) teclear otro
  número NO suelta la fila, a propósito: ese caso es «DIFIERE de la celda»
  y exige nota, y la puerta sólo puede decirlo si la fila sigue citada
  (bloque 3 del mismo script). Son dos gestos distintos con dos
  significados distintos, y unificarlos perdería uno.
- **Qué haría falta:** nada; queda dicho para que nadie «complete» la
  suelta a las filas de celda.
- **Dónde vive:** `gui/editores.py::_soltar_fila_si_el_texto_cambia`

## PF-6-03 · Lo que el comparador omite se dice desde `CAMPOS_OMITIDOS`, y lo que la prosa del registro decía antes no se reescribe

- **Cerrado (PF-6):** `lineas()` decía «salvo la marca de tiempo y las rutas
  de origen» y callaba `expediente.csv`, que `comparar` nunca miró (mira
  `csv_sha1`); `alcance.diferidos` se comparaba sólo por longitud; `True` y
  `1` salían iguales. Hoy `CAMPOS_OMITIDOS` nombra las cinco rutas, `lineas()`
  y el mensaje «REPRODUCE» de la CLI (`cli._comparar_con_la_corrida_embebida`)
  las leen de `descripcion_de_lo_omitido()`, los diferidos se comparan por
  contenido y en su orden, y un bool nunca es igual a un número.
  `tests/test_pf6_cabos.py` contrasta la tupla contra el comportamiento:
  cada ruta se muta sin romper la igualdad y cada otra hoja de `expediente`
  la rompe.
- **Abierto:** la frase vieja sigue citada en fichas anteriores de este
  registro y en docstrings de tests que describen lo que se midió entonces
  (`test_ext8`, `test_ext9`): son historia, no una segunda transcripción
  viva, y no se reescriben.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/comparador.py::CAMPOS_OMITIDOS`

# Parte XXXVI — Lo que el cierre de C10 dejó escrito: la fila del ke, el estado único y la cota de esviaje

## C10-01 · `ke_entrada` conserva la forma `float`; la fila viaja por la resolución y por la procedencia, y el consumidor no atribuye rótulos a un número que no es la celda

- **Cerrado (C10):** C5-02 pedía migrar `ke_entrada` a clave de fila «como
  `ke_entrada_cajon`». No se migró, y es decisión: la forma `float` es la que
  leen los editores tipados de E-B, el barrido de PF-3 y
  `declaracion.declarar_desde_tabla` (que exige nota cuando el valor difiere
  de la celda). Lo que el hallazgo denunciaba —que la procedencia pudiera
  mentir— se cierra por otra vía: `M4._fila_del_ke_numerico` recupera la
  fila de la que sale el número (del archivo, `DeTabla.fila_id`; en
  caliente, `declaracion.procedencia_de(...).filas`), `M4.ke_declarado`
  imprime fila, agrupación y bloque SOLO si el número coincide con la celda
  (a `TOL_UMBRAL_NORMATIVO`) y rechaza con `DatoInvalidoError` una fila del
  bloque «Box» para el tubo, la simétrica de NOR-HID-01. La memoria del
  corredor de referencia dejó de decir «declarado como NUMERO: la fila… se
  lee en el campo fuente» e imprime «Square-edge» bajo «Headwall or headwall
  and wingwalls» del bloque «Pipe, Concrete».
- **Abierto:** una declaración por `--declarar` o por
  `establecer_valor_dinamico` a secas no nombra fila, y el consumidor no se
  la inventa: imprime el número sin rótulos y la procedencia lo dice.
- **Qué haría falta:** nada para el hallazgo. Migrar la forma seguiría
  siendo mover un dato que nadie pidió mover.
- **Dónde vive:** `src/modulos/M4_control.py::_fila_del_ke_numerico`

## C10-02 · El estado de verificación tiene una sola fuente, `EstadoDeVerificacion`; `cumple` y el veredicto del paso son vistas comprobadas, y «no aplica» existe con un productor real

- **Cerrado (C10):** PC-27 llevaba tres capas —`Verificacion.cumple`, el
  `TipoDeVeredicto` del paso y `Bloqueo`— sin decir cuál gobierna. Hoy
  `modelos.EstadoDeVerificacion` (CUMPLE, NO_CUMPLE, INDICADOR, NO_APLICA)
  es la fuente: `Verificacion.estado` se deriva del veredicto del paso, o de
  `cumple` si no hay paso, y `__post_init__` rechaza con `ValueError` un
  `cumple` que no sea la vista del estado y un veredicto que discrepe.
  NO_APLICA exige `motivo_no_aplica` y tiene productor:
  `M5.v5_no_aplica_en_canal`, la fila de V5 que en la Familia C sustituye
  VC1, cableada en `M5.verificar` y en `servicio._verificador_perfil`; antes
  V5 no figuraba, y una fila ausente no se distingue de una olvidada. El JSON
  lleva `estado`, M11 pinta la marca «no aplica» sin hacer aritmética.
  `Bloqueo` se queda para lo que NO se evaluó (una etapa detenida no es una
  verificación), y `EstabilidadCabezal` rechaza la tupla vacía desde EXT-7.
- **Abierto:** DIFERIDO y SIN_VEREDICTO siguen siendo valores del veredicto
  sin traducción a estado —no hay `Verificacion` que los produzca—. El
  segundo indicador del num. 5.3.3 se evalúa desde VE-5 (ficha T2-06), como
  aviso de la verificación y sin estado propio.
- **Qué haría falta:** un productor de esos dos valores, si alguna vez lo
  hay, extendería `EstadoDeVerificacion.de_veredicto`.
- **Dónde vive:** `src/modelos/memoria.py::EstadoDeVerificacion`

## C10-03 · El esviaje máximo constructivo es un [A] opcional de perfil, y sin declararlo nada cambia

- **Cerrado (C10):** PC-32 quedó en EXT-1 con la guardia NUMÉRICA
  (`COS_ESVIAJE_MIN`) y con la cota de cordura diferida a «un criterio [A]».
  Ese criterio existe: `esviaje_max_grados`, opcional, de perfil, `float`,
  sensibilidad (0.0, `ESVIAJE_MAX`) y resolución `Libre`. `M7.factor_esviaje`
  lo lee con `valor_si_declarado` y, declarado, detiene con
  `DatoInvalidoError` —dato, criterio y máximo nombrados— todo esviaje del
  CSV que lo supere: el dato está y hay que corregirlo, que es lo que
  separa Invalido de Faltante. Sin declarar, la línea base no se mueve y el
  89.9° del dictamen sigue pasando, como MAT-O18 decidió.
- **Abierto:** el valor. Ninguna fuente de `normas/` fija un esviaje máximo
  para una alcantarilla: DG-2018 num. 502.03.03 (pág. impresa 220) es de
  intersecciones entre carreteras. Elegirlo es del proyectista.
- **Qué haría falta:** que el proyectista lo declare, o una guía técnica que
  lo acote, que lo pasaría a [C].
- **Enmendada por T-6 (2026-11-11):** el criterio tiene valor (45°, ventana
  45°–60°), ya no es opcional y superarlo es aviso (G3) y no
  `DatoInvalidoError`. Ver la ficha T6-03.
- **Dónde vive:** `src/criterios_adoptados.py::CRITERIOS`

# Parte XXXVII — Lo que el cierre de C05 dejó escrito: la adopción de V1 y V2 tiene sitio propio, y la hoja de ruta ya nombra a WSDOT

## C05-01 · El umbral duro de V1 y V2 es un [A] de perfil con el valor recomendado por defecto, y sólo se puede endurecer

- **Cerrado (C05):** PC-24 quedó en EXT-0 con la v8 enmendada («[N] el
  deber de verificar, [A] el valor como umbral duro») y en EXT-3/EXT-6 con
  la etiqueta del código sin mover (EXT-3-01, EXT-6-03). Hoy la adopción
  vive donde manda la constitución: `borde_libre_y_sobre_d_max`
  (valor `Y_SOBRE_D_MAX`) y `velocidad_minima_autolimpieza_m_s` (valor
  `V_MIN`), [A] de perfil con sensibilidad y resolución `Libre`, y la cifra
  sigue como [N] en `constantes_normativas.py` porque la escribe el Manual:
  tabla y elección separadas, el patrón `F_PGA_TABLA` / `'F_pga'`. M5 los
  lee por `_umbral_adoptado_v1` / `_umbral_adoptado_v2`, que rechazan con
  `DatoInvalidoError` un y/D máximo mayor que 0.75 o un piso menor que
  0.25 m/s: relajar una recomendación no es ejercer una adopción, es
  salirse de lo que la fuente concede (el contrato de
  `riesgo_admisible_propietario` en M1). V1 y V2 llevan `criterio_aplicado`
  y su `Umbral` también, de modo que la fila de la memoria imprime [A] y la
  remisión al criterio en vez de «[N] constante normativa».
- **Abierto:** la ventana de V2 es simbólica: su piso lo escribe la fuente
  (0.25 m/s) y ningún techo la acota, así que la puerta no evalúa un piso
  laxo y es el consumidor quien lo rechaza. El auditor de C05 midió que MD
  tragaba ese rechazo como «material no evaluable» y sacaba el punto como
  NO FACTIBLE con `criterio: None`; hoy `MD.disenar_punto` acumula el
  `DatoInvalidoError` cuyo `campo` es clave de criterio y lo relanza
  (`_exigir_criterios_validos`), de modo que sale como bloqueo
  `DATO_INVALIDO` con la clave. La de V1 sí es numérica, (0, 0.75): los dos
  extremos existen sin inventar nada, y la puerta rechaza 0.9 antes de
  correr.
- **Qué haría falta:** nada para el hallazgo. Si alguna fuente acotara el
  techo del piso de velocidad, la ventana de V2 pasaría a numérica.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::_umbral_adoptado_v1`

## C05-02 · La hoja de ruta nombra a WSDOT y al valor; la fuente sigue fuera de `normas/`

- **Cerrado (C05):** R48-030 denunciaba que `v_max_tmc` y `v_max_hdpe`
  llevaban 4.572 m/s de la Tabla 8-4 del WSDOT Hydraulics Manual
  M 23-03.12 mientras la v8 decía «PPI/FHWA, valor por extraer» en seis
  sitios, y el código declaraba «DISCREPANCIA ABIERTA CON LA HOJA DE RUTA».
  Los seis sitios quedaron enmendados con «Corregido desde …» (§0.1, §0.3,
  el tablero del TMC, la fila V3 de la Fase 5, el Tablero 1.3 y el Anexo
  A), y la ficha de los dos criterios dice que la hoja está enmendada.
- **Abierto:** lo que MAT-O14 ya decía y sigue siendo cierto: la Tabla 8-4
  no está en `normas/` (`fuentes.WSDOT_HM` es una fuente ausente) y la cita
  no es auditable contra un documento del repositorio. El Tablero 1.3 lo
  deja como trabajo de gabinete.
- **Qué haría falta:** traer la Tabla 8-4 a `normas/` y transcribirla al
  registro; entonces el [C] tendría cita verificable.
- **Dónde vive:** `src/normativa/fuentes.py::WSDOT_HM`

# Parte XXXVIII — Lo que el cierre de C09, C11 y C14 dejó escrito: la magnitud de la luz, el registro único, las tres caras y el ejemplar ilegible

## C11-01 · El umbral de 6.0 m compara la abertura de la estructura, y la discrepancia entre las cuatro fuentes queda declarada en el paso

- **Cerrado (C11):** R48-001 denunciaba que M1 comparaba con 6.0 m «el ancho
  del cauce natural» cuando la norma ancla el umbral a la luz libre de la
  ESTRUCTURA. Hoy el registro lleva las definiciones que faltaban, todas
  verificadas contra su página: `MP.GLOSARIO#OBRAS_DE_ARTE_MENORES» («luz
  libre menor que 6.00 m»), `MP.1.10#FIG_1_10A_LUZ_LIBRE` (la Fig. 1.10-a,
  que dibuja la luz libre POR VANO, entre pilares), `AASHTO_LRFD_9.1.2#BRIDGE`
  («an opening not less than 20.0 ft») y `HDS5_3ED.1.2#NBIS` («the total
  width of a multiple barrel crossing» cuenta como puente para el NBIS; y el
  matiz hidráulico de `HDS5_3ED.1.2#MODELO`). La discrepancia
  `DIS-LUZ-DENOMINACION` nombra el desacuerdo REAL —por vano contra ancho
  total, 6.0 m contra 6.096 m— y quién gana en cada cosa: en la magnitud
  HDS-5 (ancho total del cruce, la lectura conservadora), en la cifra el
  Manual de Hidrología (6.0 m, [N]). Llega a la memoria por el paso F2.LUZ
  —la vía 2 del canal vuelve a tener usuario, D9-01— y por el fundamento, y
  `luz_m` dice lo que es. El auditor adversarial de C09/C11/C14 refutó la
  primera versión, que afirmaba «las tres fuentes coinciden» y razonaba el
  multicelda por cuenta propia: las dos citas que faltaban estaban en
  `normas/`.
- **Abierto:** el caso del hallazgo (8 m salvados con tres celdas de 2.5 m)
  sigue saliendo PUENTE, ahora con la fuente que lo sostiene en vez de con
  un argumento; y HDS-5 distingue clasificación (ancho total) de método
  hidráulico (un barril), distinción que este proyecto no necesita porque
  el umbral de 6.0 m decide la denominación, no el método.
- **Qué haría falta:** nada para el hallazgo.
- **Dónde vive:** `src/normativa/discrepancias.py::DIS_LUZ_DENOMINACION`

## C14-01 · El registro normativo es una sola instancia

- **Cerrado (C14):** PC-31 medía cinco construcciones y cuatro instancias
  de `Registro`. `registro.construir` lleva `functools.lru_cache(maxsize=1)`
  y los cuatro sitios que el dictamen nombró comparten la instancia (test).
  Es seguro porque el registro no lleva estado de corrida: lo único que
  deriva y guarda, `_referenciadas`, sale de las tablas y citas del archivo.
- **Abierto:** nada.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/normativa/registro.py::construir`

## C09-01 · Las tres caras restantes de la ventana normativa y su camino de declarar corren bajo Tk

- **Cerrado (C09):** el alcance que el auditor de I1b dejó medido como
  abierto en SIS-F-01 —`_pintar_rango`, `_pintar_catalogo`, `_pintar_campo`
  y `_declarar` sin construirse nunca bajo un Tk real— lo cubre
  `tests/apoyo/gui_caras_normativa.py` (el décimo test de ventana real):
  una clave por cara, medida contra el modelo y no copiada; un valor malo
  que no deja rastro y uno bueno que deja los cuatro (rótulo, caliente,
  procedencia, callback).
- **Abierto:** lo que la ficha original llamó entorno: la suite corre las
  ventanas cuando ALGÚN intérprete del contenedor levanta un Tk, y sin él
  salta. Un CI con servidor X virtual sigue siendo infraestructura, no un
  test.
- **Qué haría falta:** ese CI.
- **Dónde vive:** `tests/apoyo/gui_caras_normativa.py::CARAS`

## C09-02 · La serie de diámetros del concreto se transcribió por imagen de la única tabla legible de M 170M, y la ficha de la fuente dice cuáles no lo son

- **Cerrado (C09):** SIS-F-13 y NOR-PRO-04 esperaban «M 170M Tablas 1–5 sin
  transcribir». Medido página a página: las Tablas 1 a 4 (PDF 3–7, 9) son
  recomposiciones OCR con dígitos equivocados en la propia imagen (371 por
  375, 1390 por 1350, «3tS0», «6tXI») y filas superpuestas, y transcribir
  de ahí sería inventar (regla 8); la Tabla 5 (Clase V, PDF 10, girada 90°)
  es un escaneo real y legible. Su columna de diámetros (27 filas, 300 a
  3600 mm) y sus paredes B y C están en `AASHTO_M170M.T5` por imagen, con la
  interpretación en contra declarada (las Clases I a IV no se pueden
  contrastar contra este ejemplar). CP11 tiene por fin dorado de tabla para
  los tres materiales y `M2.siguiente_diametro` se contrasta contra la serie
  del concreto. La primera versión de este cierre decía «PDF 10 en blanco»
  y «hace falta otro ejemplar»; el auditor adversarial lo refutó renderizando
  la página, y tenía razón.
- **Abierto:** las clases D-load (Tablas 1–4) siguen sin transcribir, que es
  lo que `clases_producto_por_relleno` necesitaría para el concreto; y M10
  sigue sin caso patrón (expediente vial).
- **Qué haría falta:** otro ejemplar de M 170M para las Tablas 1 a 4 (o la
  M 170M-23 que la vigencia ya pide para gabinete).
- **Dónde vive:** `src/normativa/tablas.py::T_M170M_T5`

# Parte XXXIX — Lo que el rediseño visual de la GUI dejó escrito: la navegación lateral conmuta el Notebook

## REDISEÑO-3-01 · La navegación es lateral y el Notebook se conserva por debajo, con la tira de pestañas retirada por estilo

- **Cerrado (rediseño visual, bloque 3):** la regla «Notebook por pestañas»
  de CLAUDE.md queda enmendada, no derogada. La ventana principal muestra
  una columna de cuatro pasos numerados (`NavegacionLateral`) y el
  `ttk.Notebook` sigue debajo con sus cuatro `add`: `select`, `tabs` e
  `index` son la puerta única para cambiar de vista, y el paso activo tiene
  una sola fuente —el Notebook, leído por `<<NotebookTabChanged>>`—. La
  alternativa era retirar el Notebook y apilar los cuatro marcos a mano con
  un índice propio; se descartó porque duplicaría el estado (la columna y la
  pila cada una con «su» paso activo) y rompería el contrato que la suite y
  los diez apoyos de ventana real leen (`nb.select`, `nb.tabs`, `nb.index`).
  La tira de pestañas se retira por estilo (`Lateral.TNotebook`, layout
  vacío de su `Tab`), de modo que la emergente de ayuda conserva las suyas.
- **Abierto:** el atajo de teclado Control+n y el clic de la columna llegan
  al mismo `select`; lo que no hay es lectura de la columna por un lector de
  pantalla más allá del texto de sus rótulos, que es el límite de `ttk`.
- **Qué haría falta:** nada para el expediente. Si algún día el Notebook se
  retira de verdad, la columna tendría que llevar el paso activo, y esta
  ficha se reescribe.
- **Dónde vive:** `gui/componentes.py::NavegacionLateral`

# Parte XL — Lo que T-0 de la cadena T dejó escrito: gobernanza, especificación y enlace a las normas

T-0 (2026-11-11) abre la cadena T (`docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md`), que
implementa el `INFORME_evaluacion_app_alcantarillas_vs_PDF.md`. No toca fórmulas ni
umbrales. Cuatro decisiones suyas no son un cierre sino algo que queda dicho para las
sesiones que siguen.

## T0-01 · Los PDF de normas se encuentran por `NORMAS_DIR`, con caída a `normas/`; las dos fuentes nuevas viven sólo en el repositorio de normas

- **Qué se difirió:** retirar los 18 PDF de `normas/` (es de T-12) y transcribir las
  citas de HEC-14 y del WSDOT Hydraulics Manual (son de T-8 y T-4). T-0 hizo lo que
  les abre el camino: una sola puerta, `fuentes.ruta_pdf`, que busca cada PDF por su
  nombre primero en la carpeta de la variable `NORMAS_DIR` —el clon del repositorio
  de normas, su raíz o su subcarpeta `normas/`— y después en `normas/` de este
  repositorio mientras exista; y las dos fuentes dadas de alta como presentes, con
  sha1, páginas, edición y paginación por capítulo medidos abriendo los PDF.
- **Por qué:** se eligió la variable y no un submódulo ni un enlace simbólico porque
  el repositorio de normas lleva documentos con copyright y T-12 recomendará hacerlo
  privado: un submódulo ataría cada clon de la app a una credencial sobre él y dejaría
  su URL y su commit versionados aquí; un enlace simbólico `normas → …` no convive con
  la carpeta `normas/` real que todavía no se ha retirado. La variable no versiona
  nada y deja que un despliegue que sólo calcula no clone 330 MB. Y `hec14.pdf` y
  `HydraulicsManual.pdf` **no se copiaron a `normas/`**: esa carpeta no gana PDF
  (`INF-5.2.3`). Consecuencia que hay que conocer: **hay un tercer eje de entorno**,
  «repositorio de normas enlazado sí / no». Sin `NORMAS_DIR` la suite queda verde con
  siete saltos más —los dos T0 de `test_normativa_pdf`, que verifican las dieciséis
  fuentes que sí están y después saltan nombrando las dos que faltan; los cuatro
  tests de `test_t0_gobernanza` que abren los dos PDF; y la mitad de la guardia de
  PC-23 que mira el repositorio enlazado—, y `verificar_sesion.py` lo dice en su paso
  5 como aviso. Un `NORMAS_DIR` que apunta a una carpeta inexistente **no** se calla:
  `FileNotFoundError`.
- **Qué haría falta:** T-12 retira los PDF de `normas/` y, con ellos, el censo
  `SOLO_EN_EL_REPO_NORMAS`, que es transitorio: entonces todas las fuentes presentes
  viven en el repositorio de normas y la guardia de PC-23 se reescribe sobre una sola
  carpeta. T-4 y T-8 transcriben las citas con su firma; la `nota` de cada fuente
  adelanta dónde dice cada cosa (la Tabla 8-4 es de niveles de abrasión, no de
  velocidades máximas, y la prohibición del termoplástico está en el §8-3.3; en HEC-14
  la socavación es el capítulo 5 y no el 3). La vigencia de las dos se confirmó por
  búsqueda web, sin leer las páginas del emisor: queda para gabinete.
- **Hecho por T-12:** ficha T12-01.
- **Dónde vive:** `src/normativa/fuentes.py::directorios_de_normas`

## T0-02 · El código de paso del tirante crítico es `F4.YC`; `F4.YC_RECT` sigue resolviendo como alias, y el índice de fórmulas se regeneró con la corrida que hay

- **Cerrado (T-0):** `INF-5.1.10`. El paso 4.2.1 se emitía con el código `F4.YC_RECT`
  también para la sección circular (anotado como C4-2 en `docs/ruta_familia_c.md`) y
  sin `formula_cita_id` (C4-1); el paso 4.4, «cuál control gobierna», citaba las
  ecuaciones de control de entrada. Hoy el código es `F4.YC`, la fórmula cita la
  condición de flujo crítico que HDS-5 escribe en su pág. A.3 (`HDS5_3ED.A.3.1#CRITICO`)
  y el paso 4.4 cita el num. 3.3.5 del procedimiento de diseño
  (`HDS5_3ED.3.3.5#GOBIERNA`, pág. impresa 3.25). Las dos citas se leyeron por texto
  contra el PDF y las fija `test_normativa_pdf`.
- **Abierto:** el nombre anterior no se borró. `ALIAS_DE_FUNDAMENTO` lo censa y lo
  entienden `Registro.fundamento`, `modelos.paso` e `id_vigente`; lo que se **emite** es
  siempre `F4.YC`. Un lector que guardó una traza con `F4.YC_RECT` la sigue pudiendo
  resolver; uno que **filtra** pasos recién emitidos por el nombre viejo tiene que
  pasar su id por `id_vigente`. El ancla de la ficha en la memoria HTML cambia con el
  id. `docs/indice_formulas.md` se regeneró con la corrida de referencia de siempre,
  que llega a M4 y **no dimensiona** ningún punto (0 de 4): sus filas del paso 4.2.1
  y del 4.4 ya llevan las dos citas nuevas, pero las fórmulas de lo que esa corrida no
  alcanza —V7, VC1, Laushey— siguen sin fila.
- **Qué haría falta:** retirar el alias cuando ningún lector externo dependa del
  nombre viejo (hoy no hay ninguno en el repositorio: la suite migró entera); y
  regenerar el índice con una corrida que dimensione los cuatro puntos, que es el
  punto 3 de T-10.
- **Dónde vive:** `src/normativa/fundamentos.py::ALIAS_DE_FUNDAMENTO`

## T0-03 · La hoja de ruta declara desde T-0 cosas que el código todavía no hace: el conjunto de aceptación de la Familia B y cuatro enmiendas prospectivas

- **Qué se difirió:** la implementación de cinco enmiendas de la v8 que T-0 escribió
  como especificación y no como descripción del código: §1.1 (el caudal lo calculará
  `MH_hidrologia`, T-1), §2.3 (la Familia B se acepta con V1 + V2 + V4 + V5 +
  espaciamiento de la Fase 10), la fila V5 (método de remanso sin adoptar y
  `ancho_derecho_via_m` como dato externo), §7.B (pendiente mínima y máxima del
  conducto y desnivel mínimo de entrega pasan a criterios, T-2 y T-6) y §9 (cabezal
  por punto y con aleros, T-7).
- **Por qué:** es el orden que la casa sigue —«si un cambio contradice la v8, primero
  se enmienda la v8»— y T-0 no toca lógica. Cada nota dice qué hace **hoy** el código,
  para que nadie la lea como descripción: `PERFILES[Familia.B].verificaciones_aceptacion`
  sigue en `None`, `S = 0` se rechaza, G2 compara sin desnivel, la Fase 9 es «del
  proyecto» y V5 se detiene. La de la Familia B es la única que **declara un conjunto**
  que la hoja no traía; no es una elección nueva —son las cuatro que la sección nombra
  para la A, porque la Fase 5 no exime a ninguna familia, más el espaciamiento que la
  propia frase de la B ya nombraba—, y aun así es una frase de la fuente de verdad
  escrita por una sesión: **el dueño del proyecto puede corregirla**, y no mueve
  ningún número porque ningún módulo despacha sobre ese campo (`SIS-B-13`).
- **Qué haría falta:** que cada prompt cierre lo suyo y retire de su nota el «hoy el
  código…». Para la Familia B, que T-9 —que convierte el espaciamiento en una
  verificación que puede fallar— le dé código de verificación y escriba la tupla; el
  prompt de T-9 **no lo pide** y hay que decírselo. Para V5, nada de la cadena la
  implementa: sigue diferida, y T-11 la lista entre lo que requiere entrada del
  proyecto.
- **CERRADA para la Familia B en T-9 (2026-11-12).** VB1 es la verificación de la Fase
  10 que puede fallar y `PERFILES[Familia.B].verificaciones_aceptacion` vale
  `("V1", "V2", "V4", "V5", "VB1")` —y desde las correcciones de su auditoría
  `("V1", "V2", "V4", "V5", "VB1", "VB2")`: VB2 es la condición literal del Manual, el aporte
  contra la capacidad de la cuneta (ficha T9-07)—; sigue siendo huella y no filtro (un test lo
  fija por AST), y ningún diámetro se movió. La de V5 sigue abierta.
- **Dónde vive:** `src/modulos/M1_clasificacion.py::PERFILES`

## T0-04 · Los `INF-` del tracker llevan el número del INFORME, no el de los prompts; cuatro no tienen prompt, y la severidad es una propuesta

- **Qué se difirió:** nada del INFORME se dejó sin fila, pero tres cosas del alta son
  decisiones y no transcripción. (1) El ID canónico es el del INFORME (`INF-5.1.10` es
  su ítem 10), aunque la cadena cite ese hallazgo como «INF-5.1.9»: seis prompts usan
  un número que no es el del ítem, y T-8 y T-9 usan el mismo para dos distintos. (2)
  Las tablas del §3 van **por fila** (`INF-3.2.7`), y los puntos 4 y 5 del §0 entran
  como `INF-0.4` e `INF-0.5` porque no tienen fila en ninguna tabla y la cadena los
  cita. (3) La severidad de las 64 filas es una **propuesta de T-0**: el INFORME no la
  asigna por hallazgo.
- **Por qué:** un tracker con los números de los prompts tendría dos filas
  «INF-5.1.11» y ninguna para tres ítems del INFORME. Con el número del INFORME cada
  hallazgo tiene una fila y cada alias lleva a una sola: la tabla de equivalencias
  está al principio de la copia de la cadena y en «Vínculos cruzados» de cada fila, y
  el test la fija en las dos direcciones. Cuatro hallazgos del §5.1 **no los nombra
  ningún prompt** —`INF-5.1.3` (el umbral de 100 ha justificado con el fixture),
  `INF-5.1.8` (`area_ha` obligatoria en la Familia B sin consumidor), `INF-5.1.9`
  (`sucs_fundacion` obligatoria y nunca leída) e `INF-5.1.16` (una constante sin
  consumidor)—, y dos filas del §3 tampoco (`INF-3.2.5`, la analogía de V4;
  `INF-3.2.9`, el segundo indicador de sedimentación): quedan abiertos con su prompt
  vecino escrito, no escondidos bajo otro.
- **Qué haría falta:** que el dueño confirme o corrija las severidades; que el
  orquestador asigne los seis sin prompt (T-11, en su censo final, es la última
  ocasión); y que cada prompt escriba el ID **canónico** al cerrar.
- **Dónde vive:** `proceso/tests/test_t0_gobernanza_proceso.py::ALIAS_DE_LA_CADENA` (en `tests/test_t0_gobernanza.py` hasta T-12, que separó la mitad de proceso)

---

# Parte XLI — Lo que T-2 de la cadena T dejó escrito: el barril horizontal, el borde libre bajo el receptor, la sección medida y el ejemplo publicado

T-2 (2026-11-11) cierra los huecos de método de la hidráulica que el INFORME lista en su
§3.2 y en los ítems 6 y 7 del §5.1. Siete decisiones suyas no son un cierre limpio: unas
contradicen lo que el prompt pedía porque la fuente no lo sostiene, otras dejan una
alternativa sin aplicar porque decidirla es del proyectista.

## T2-01 · `S = 0` se admite y se dice con un objeto propio; la pendiente adversa y `S_cauce = 0` siguen fuera, y queda una discontinuidad con la convención de PC-06

- **Cerrado (T-2):** `INF-5.1.6`. `M3.resolver_manning`, `M4.control_entrada`,
  `M4.control_salida` y `M4.perfil_lamina` admiten `S = 0`; la guardia (forma MAT-D13,
  `not S >= 0`) rechaza sólo la pendiente negativa y el NaN. Fuente: HDS-5 num. 3.3.4,
  pág. impresa 3.25 / PDF 107 (citas `HDS5_3ED.3.3.4#HORIZONTAL`, `#KS`,
  `#H_SIN_AJUSTE`). M3 devuelve `SinTiranteNormal` —ni excepción, porque el dato es
  válido, ni `None`, que significa «el escalón no alcanza»—; el perfil se rotula
  `TipoDePerfil.H2`; V1 y V2 se juzgan sobre el perfil, y V3 y el d50 sobre la
  velocidad de salida, también cuando gobierna el control de entrada. Medido: A-01 con
  `S_conducto = 0` y TW = 0.3 m dimensiona con Ø 1.05 m bajo control de salida.
- **Abierto:** tres cosas. (1) **La pendiente adversa**, que el mismo numeral admite
  como asentamiento de la entrada: el proyecto no diseña con ella y `S < 0` sigue
  siendo `DatoInvalidoError`. (2) **`S_cauce = 0` en el CSV** se sigue rechazando
  (`M0_carga`: `0 < S_cauce < S_CAUCE_MAX`); el barril horizontal se declara por
  `S_conducto`. (3) **La discontinuidad con PC-06, y su dirección**: para `S` pequeña
  y positiva el escalón se rechaza si Q alcanza el caudal a sección llena de Manning,
  y para `S = 0` se resuelve por el perfil. El barril horizontal es la **envolvente**
  (da el mayor llenado: `y_max/D` = 0.6426 con S = 0 frente a 0.6151 con S = 0.001,
  en D = 0.90 m y Q = 0.6 m³/s), de modo que aceptarlo no es lo optimista; lo
  sobreconservador es el `None` de M3 para 0 < S ≲ 0.00105. Consecuencia: **declarar
  `S_conducto = 0` en vez de 0.001 da un tubo menor**. La medida completa está en el
  docstring de `M3.resolver_manning`.
- **Qué haría falta:** para (3), resolver por el perfil también cuando `S > 0` y Q
  supera el caudal a sección llena de Manning. Cambia el criterio de capacidad del
  catálogo entero y puede mover diámetros de la línea base: es decisión del dueño.
  Mientras tanto, una pendiente de proyecto menor que el uno por mil no se declara
  como cero para ganar un diámetro. Para (1), un caso de obra y la regla práctica del
  numeral (D/2). Para (2), que alguien lo necesite: V2b no tendría con qué comparar.
- **Dónde vive:** `src/modelos/hidraulica.py::SinTiranteNormal`

## T2-02 · `borde_libre_bajo_tw_ahogante` queda en `no_cumple` por decisión del dueño; `aviso` es una alternativa barrible, continua en el TW, que hace dimensionar A-02 en la corrida estrecha

- **Cerrado (T-2):** `INF-3.2.6`, en lo que T-2 podía cerrar. V1 separa quién le quita
  el borde libre al barril: el **caudal de diseño**, que no cumple siempre (Manual,
  num. 4.1.1.3.7 b), pág. impresa 79, cita `MC_HHD.4.1.1.3.7b#LLENA`), o el **nivel
  del receptor** —el TW por encima del llenado admisible y fijando el tirante máximo
  del barril, llegue o no a la clave—, que gobierna el criterio [A] con dos lecturas;
  la memoria imprime cuál aplicó. **El dueño decidió (2026-11-11) la opción (a): el
  valor de archivo es `no_cumple`**, la conducta anterior; con él T-2 no cambia ningún
  veredicto.
- **Abierto:** la lectura `aviso` no se aplica y queda para barrer (`--barrido
  borde_libre_bajo_tw_ahogante=no_cumple,aviso`). Medido por la CLI sobre la corrida
  estrecha de la línea base, cuyo TW sale de la vía 4 con la sección **adoptada**:
  con `no_cumple`, 0 de 4 puntos dimensionan; con `aviso`, **A-02 dimensiona con
  Ø 0.90 m** (TW = 1.196 m, régimen lleno, control de salida, HW = 1.106 m, V1 como
  indicador) y A-01 y B-01 siguen sin dimensionar, ya no por V1 sino por V4, V7 y V2.
  Cambia qué puntos dimensionan en una corrida de la línea base, y ahí el TW no es
  una medición: aceptar el ahogamiento sería aceptar la adopción. La primera
  redacción de `aviso` sólo actuaba con el barril lleno y resultó discontinua en el
  TW (más ahogamiento era más permisivo, y el tubo chico pasaba donde el grande no:
  lo midió el auditor adversarial sobre A-02); se corrigió antes de integrar, y el
  comentario de `M5.v1_borde_libre` cuenta el caso. Con el barril horizontal no hay
  tirante normal con que separar los dos casos y V1 no cumple bajo las dos lecturas.
- **Qué haría falta:** para adoptar `aviso`, un nivel del receptor **medido**
  (`seccion_receptor_medida` y su caudal, o la cota de agua de quien lo opera) y la
  decisión del dueño; «aviso sólo si el TW viene de las vías 1 a 3» pediría una
  tercera opción en la ventana.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::CRITERIO_BORDE_LIBRE_BAJO_TW`

## T2-03 · La sección medida del receptor entra por `--datos-externos` como un objeto, no como columnas del CSV; y el aviso de sección adoptada sale también en la vía 3

- **Qué se difirió:** las columnas de CSV para la sección del receptor. El prompt pedía
  «entrada opcional de la sección medida (ancho de fondo, talud z, profundidad, n,
  pendiente) que gana sobre el criterio»; entra por la clave `seccion_receptor_medida`
  del JSON de datos externos, global o por punto, con los cinco campos de
  `servicio.CAMPOS_SECCION_RECEPTOR`.
- **Por qué:** cinco columnas más en el CSV son cinco celdas vacías por fila para todo
  punto sin levantamiento y un cambio en `M0_carga.COLUMNAS`, que otros prompts de la
  cadena tocan a la vez; y el levantamiento de un dren suele valer para varios cruces, que es lo
  que el bloque `globales` del JSON ya resuelve. La sección entra completa o no entra:
  un campo que falte, uno de más o uno fuera de dominio detienen la carga
  (`DatoInvalidoError`); nunca se completa con el del criterio. El dominio es el
  físico de `dominios.py`, no uno normativo: pendiente menor que 1 m/m, n de Manning
  menor que 1 (`N_MANNING_MAX_FISICO`: un valor mayor delata un coeficiente de
  Strickler) y profundidad menor que 100 m (`ALTURA_RECEPTOR_MAX_FISICA_M`: delata
  centímetros). El aviso «seccion
  adoptada [A] por falta de levantamiento» sale en la vía 4, que es lo que el prompt
  pedía, **y en la vía 3**, que también usa la sección: con caudal del receptor
  documentado y sección adoptada, el tirante sigue saliendo de una geometría que
  nadie midió. El script de QGIS del repositorio de cotas es referencia de dónde sale
  el levantamiento; este programa no lo ejecuta.
- **Qué haría falta:** si el dueño prefiere columnas, sumarlas a `M0_carga.COLUMNAS`
  con `VACIOS_ADMITIDOS` y hacer que `_resolver_tw` las arme en una `SeccionReceptor`;
  la puerta de M3 (`seccion_del_receptor(seccion_medida=…)`) no cambia.
- **Dónde vive:** `src/servicio.py::CLAVE_SECCION_RECEPTOR_MEDIDA`

## T2-04 · `regimen_v2b` y `hw_entrada_fuera_de_rango` reciben valor de archivo pero siguen siendo [A], no [C]; la «nota de Ks·S de la Tabla A.1» no existe, y la tabla no tiene filas de tubo con aleros

- **Cerrado (T-2):** `INF-0.5`, en la parte de T-2. `regimen_v2b =
  indicador_con_aviso` y `hw_entrada_fuera_de_rango = energia_critica` son el valor
  del archivo, con la otra opción en la ventana. La mitad [N] de la fila V2b tiene su
  cita (`MC_HHD.4.1.1.3.7d`, Manual num. 4.1.1.3.7 d), pág. impresa 80 / PDF 83), y si
  el acceso está previsto entra, opcional, por `acceso_mantenimiento_previsto`. Medido
  antes y después sobre diez corridas: ningún diámetro se mueve y los mismos puntos
  dimensionan. Un indicador que no detiene se ve fuera de su fila: sube a
  `InformePunto.avisos()` y el RESUMEN cuenta aparte las «Verificaciones con aviso»
  (`ResumenDeCorrida.con_aviso`); la pestaña 4 lo muestra fila a fila y todavía no lo
  cuenta.
- **Abierto:** tres desacuerdos con el prompt, por la fuente. (1) **Las etiquetas**:
  pedía [C]; HDS-5 define el indicador y la base de la Forma 1, pero no prescribe qué
  hacer cuando el indicador se dispara ni un piso para la carga: sigue habiendo
  elección y siguen siendo [A]. (2) **La cita**: nombraba una «nota de Ks·S» de la
  Tabla A.1, que tiene una sola nota, bibliográfica (PDF 197); lo que sostiene la
  elección está en A.2.1 (cita `HDS5_3ED.A.2.1#FORMA_1`), A.3 y 3.3.4. (3) **Las
  filas**: la tabla no tiene tubo circular con aleros; se transcribieron las ocho que
  faltaban de las cartas 1, 2, 3 y 13. Además: el piso `energia_critica` **no es una
  cota conservadora** —omite K·(q*)^M y queda por debajo de lo que la ecuación da con
  S = 0— y con V10 es casi inalcanzable (con Ø 0.90 m hace falta Q < 0.005 m³/s); la
  ficha del criterio lo dice. Y un efecto fuera de la línea base: con los siete del
  cajón, la coronación y `S_conducto = 0.004`, C-01 pasa de no dimensionar (V2b) a un
  marco de 1.20 × 0.90 m (`tests/test_pf4_regimen_v2b.py`).
- **Qué haría falta:** para volver a la conducta anterior, declarar
  `regimen_v2b=umbral_duro` o `hw_entrada_fuera_de_rango=descartar`. Para que alguno
  sea [C], una fuente que prescriba la consecuencia y no sólo el indicador.
- **Dónde vive:** `src/normativa/citas.py::HDS5_A21_FORMA_1`

## T2-05 · El ejemplo publicado de HDS-5 (Design Guideline 1) se reproduce dentro de la tolerancia salvo cinco casillas censadas; las filas de metal corrugado se comparan por intervalo, y ninguna fila toca la transición

- **Cerrado (T-2):** `INF-3.2.2`, en la parte de validación externa. `CP_HDS5_DG1`
  transcribe los dos ejemplos de la Design Guideline 1 (formularios de las págs.
  impresas DG1.4 / PDF 275 y DG1.10 / PDF 281), con la conversión de unidades en el
  fixture, y el motor reproduce HW/D, la carga de entrada, d_c, h_o, H, la cota de
  control de salida y la velocidad de salida. La tolerancia de lectura es del 3 % y
  la que la fuente declara para su procedimiento, del ±10 % (num. 3.1.1, pág. impresa
  3.1 / PDF 83).
- **Abierto:** tres límites, los tres escritos en el fixture con sus números. (1)
  **Cinco casillas superan el 3 %** y no se ajustó ni el test ni el motor: están en
  `CP_HDS5_DG1["fuera_de_tolerancia"]` con su causa —dos son lecturas de nomograma
  frente a la ecuación, una no es el producto de las dos cifras que tiene al lado, y
  la H del cajón de 5 × 5 con bisel (−11.4 %, la única fuera también del 10 %) no se
  reproduce con la fórmula y el ke del propio formulario—, y el test exige en las dos
  direcciones que el censo diga la verdad. (2) **El n del metal corrugado no está
  impreso**: sus dos filas se comparan con el n **interpretado**, acotado por la
  fuente (Tabla B.1, 0.022–0.027, pág. impresa B.6 / PDF 208; típico 0.024, pág.
  impresa 3.8 / PDF 90): lo publicado tiene que caer en el intervalo que da el rango,
  y con el típico sale el control que el formulario anota —salida en el tubo de 60
  pulgadas, la única fila que la salida gobierna—, a −5.5 % en H. (3) **Ninguna de
  las siete filas cae en la transición** 3.5 < q* < 4.0: el ejemplo valida las dos
  ramas del control de entrada y no la recta que las une.
- **Qué haría falta:** el n de las filas corrugadas, un caso publicado dentro de la
  transición, o un ejemplo resuelto por ecuación y no por nomograma: HY-8 con sus
  salidas impresas serviría, y no está en `normas/` (T-11 punto 2).
- **Dónde vive:** `tests/fixtures/casos_patron.py::CP_HDS5_DG1`

## T2-06 · HDS-5 §5.3.3 presenta dos indicadores de sedimentación y la aplicación evalúa uno: el segundo necesita el n del cauce natural, que no es un dato del proyecto

- **Qué se difirió:** `INF-3.2.9`. El numeral, leído entero (págs. impresas 5.11 y
  5.12 / PDF 147 y 148), nombra **dos** indicadores —la pendiente y la rugosidad del
  conducto frente a las del cauce natural— y, sin cifra, otros factores: la magnitud
  del caudal y el material del cauce, los cauces en agradación, los cambios de
  pendiente a la entrada, las instalaciones multibarril y las entradas deprimidas.
  V2b evalúa el primero (`S_conducto ≥ S_cauce`).
- **Por qué:** comparar rugosidades exige el n de Manning del **cauce natural** en el
  cruce, que no es columna del CSV ni dato externo, y el proyecto no lo suple con un
  valor por defecto: sería inventar un dato de sitio. El n que sí existe, el del
  criterio `seccion_receptor`, es del cuerpo receptor aguas abajo —un dren o un
  canal—, no del cauce que llega a la alcantarilla. Y la fuente no dice qué diferencia
  de rugosidad es un problema: ni siquiera con el dato habría umbral.
- **Qué haría falta:** el n del cauce por punto, de campo (estudio hidrológico o
  inspección), como columna opcional o dato externo; y una regla de comparación que
  el proyectista adopte y declare, porque la fuente no la da. Hasta entonces la ficha
  de `regimen_v2b` lo declara en `verificacion_pendiente` y la memoria lo imprime.
- **Dónde vive:** `src/normativa/citas.py::HDS5_5_3_3_DEPRESION`
- **Cerrado (VE-5, lote m45, ítem 19):** el segundo indicador se evalúa como INDICADOR, no
  veredicto (`M5._indicador_de_rugosidad`): n_max del conducto (la rama de la
  sedimentación, MAT-D1) frente al n del cauce natural, que entra con la sección del cauce
  de aproximación del punto (`seccion_cauce_aproximacion`, su campo `n`; sin ella no se
  evalúa ni se supone). La regla es la literal de la fuente, «roughness greater than the
  channel» (n_conducto > n_cauce), sin umbral añadido; si se dispara viaja como aviso de
  V2b (`Verificacion.avisos`) y no cambia `cumple` bajo ningún `regimen_v2b`. Tests:
  `tests/test_ve5_m45_rugosidad_v2b.py`. Sigue sin evaluarse en la Familia C (la clave es
  de A y B) y los demás factores del numeral siguen sin cifra.

## T2-07 · La aceptación de T-2 no se escribió en rojo antes del código: se midió después; 34 de sus 160 tests valen antes y después, y quedan 28 mutantes vivos, censados

- **Qué se difirió:** el orden que la casa sigue —el test en rojo con
  `xfail(strict=True)`, y liberarlo al corregir—. T-2 implementó primero y escribió
  `tests/test_t2_hidraulica.py` después.
- **Por qué:** la sesión se interrumpió dos veces y el orden se perdió; se dice en vez
  de reconstruirlo. Para que la aceptación no fuera vacua, el archivo se corrió
  contra un árbol exportado de `87d1ce7` (T-0), con los cuatro nombres de `modelos.py`
  que ese árbol no tiene sustituidos por un marcador: **126 rojos y 34 verdes**. Los
  34 son guardias que valen antes y después: la pendiente negativa o NaN, las filas
  de la Tabla A.1 que el catálogo usa, las 24 casillas de los tres cajones del
  ejemplo publicado (las Cartas 8 y 10 ya estaban transcritas), el censo de casillas
  fuera de tolerancia, las cifras del formulario contra la página, la transición que
  ninguna fila toca, la velocidad de salida con el TW entre el crítico y la clave, el
  censo de mutantes y los diámetros de la línea base.
- **Qué haría falta:** nada que se pueda rehacer; el oráculo de cada test es la fuente
  o un invariante. La **mutación** de lo tocado se midió con el arnés de EXT-11 sobre
  veinte funciones y seis archivos de tests: 283 mutantes y **28 vivos**, listados
  uno a uno con su clase en `MUTANTES_VIVOS_DE_T2` (catorce de banda de tolerancia,
  cinco de guardia o corchete sin caso que la distinga, seis de texto, dos sin caso
  construido y uno que muere con otro archivo). Los tres que la revisión adversarial
  encontró vivos sobre el barril horizontal con control de entrada mueren con
  `test_un_barril_horizontal_gobernado_por_la_entrada`. El censo
  `SUPERVIVIENTES_CON_RAZON` de EXT-11 no se amplió con los que no estaban, ni la
  lista se comprueba contra el arnés en cada corrida: es trabajo de T-10.
- **Dónde vive:** `tests/test_t2_hidraulica.py::MUTANTES_VIVOS_DE_T2`

# Parte XLII — Lo que T-4 de la cadena T dejó escrito: espesores, topes, velocidad máxima, durabilidad y dos hallazgos sin prompt

T-4 cerró `INF-5.1.17`, `INF-3.3.1`, `INF-3.3.4`, `INF-3.2.4`, la mitad del HDPE de
`INF-3.2.1` y, por encargo del orquestador, `INF-5.1.9` e `INF-5.1.16`. Estas
fichas registran lo que quedó **decidido con argumento** o **abierto con nombre**, y
lo que la cadena suponía y la fuente no sostiene.

## T4-01 · El espesor del TMC es profundidad de corrugación más plancha; el del HDPE sale del diámetro exterior máximo de AASHTO LRFD, y dos tamaños se quedan sin fila

- **Qué se difirió:** las filas de **1350 y 1500 mm** del HDPE en
  `espesor_pared_conducto`. El resto del punto 1 del prompt está cerrado
  (`INF-5.1.17`, `INF-3.3.4`): el TMC y el HDPE ya no se descartan por falta de
  espesor y llegan al recubrimiento mínimo de 7.A y a V7.
- **Por qué:** el prompt pedía el espesor «por tabla» de la norma de producto, y
  ninguna de las dos lo da como tal. **TMC:** el diámetro nominal se mide en la
  cresta interior (AASHTO M 36 núm. 8.1.1, pág. M 36-10), de modo que lo que separa
  el diámetro hidráulico del exterior es la profundidad de la corrugación (Table 1,
  pág. M 36-6: 13 mm en la de 68 por 13) **más** el espesor de la plancha (ASTM A796
  Tabla 5): 15.01 mm con la adopción `corrugacion_y_espesor_tmc` [A] = `68x13/2.01`.
  El criterio se barre dentro de las diecisiete planchas tabuladas. Que 2.0 mm y
  68×13 sea «la práctica del expediente de referencia» **no se verificó de primera
  mano**: la pág. 57 del PDF «VARIOS» no estaba disponible y la ficha lo dice como
  dato de segunda mano, por el INFORME §1.1. **HDPE:** AASHTO M 294 (traducción no
  oficial) tabula el espesor mínimo de la pared **interior**, no la altura del
  perfil, y no da diámetro exterior. Sí lo da la Table A12-11 de AASHTO LRFD (pág.
  12-108, PDF 1746), como **máximo** del producto: t = (OD máx − D)/2, que es el
  lado seguro para la clave y para el volumen de V7. Esa tabla termina en 48 in. Para
  1350 y 1500 mm no hay fuente en el repositorio de normas, y la fila se queda sin
  escribir: `DatoFaltanteError` que nombra la fila, sin interpolar.
  Dos cosas más, medidas: (a) el mínimo de relleno del HDPE de EG-2013 508.07
  (0.30 m) **participa y no gobierna**: la cobertura de AASHTO para el termoplástico
  es 0.61 m bajo pavimento y 0.3048 m sin él; (b)
  `conftest.py` **conserva** su espesor sintético de TMC y HDPE (22 tests de fórmula
  usan diámetros que ninguna serie tiene), menor que el del archivo: la suite corre
  con él y la línea base con el del archivo.
- **Qué haría falta:** la ficha de un fabricante de tubería de PE corrugado de 1350 y
  1500 mm con su diámetro exterior (se declara en `espesor_pared_conducto["hdpe"]`),
  o una edición de AASHTO LRFD cuya tabla llegue a 60 in; y el PDF «VARIOS» para
  pasar de segunda a primera mano la práctica del calibre.
- **Dónde vive:** `src/modulos/M2_material.py::espesor_pared_de_tmc`

## T4-02 · El tope de diámetro es el de la norma de producto —en concreto, el último diámetro con diseño estándar—; la disponibilidad de mercado es opcional y sólo puede bajarlo

- **Qué se difirió:** los tubos de concreto de **2850 a 3600 mm**, que AASHTO M 170M
  lista como diseños especiales. El catálogo no los recorre.
- **Por qué:** `D_max_catalogo` valía 2.70 / 2.10 / 1.50 m como [A], y su propia
  ficha admitía que los dos primeros no tenían respaldo. Desde T-4 el tope lo
  resuelve `M2.tope_de_diametro` como el **menor** de tres cosas, y dice cuál gobernó
  (`Material.D_max_criterio`): la **norma de producto** (`D_max_norma_producto` [C]:
  2.70 / 3.60 / 1.50 m); en TMC, el mayor diámetro en que la **corrugación adoptada**
  es estándar según la Table 6 de M 36 (2100 mm con 68 por 13); y, **si el
  proyectista la declara**, la disponibilidad (`D_max_catalogo` [A], ahora opcional y
  sin valor), que se rechaza con `DatoInvalidoError` si supera a las otras dos.
  **Ninguno de los tres topes efectivos se movió**; lo que cambió es que ahora
  tienen de dónde salir. **El del concreto, corregido por la auditoría adversarial
  (H2):** la primera versión de T-4 lo llevó a 3.60 m —la última fila de la serie— y
  dejó escrito que «faltaba transcribir» la pared de 2850 a 3600 mm. **La norma no
  la tabula.** Leído por imagen, tabla a tabla: en la Tabla 1 (Clase I, PDF 3) las
  filas de 1500 a 2700 mm traen pared y acero (2700: pared B 250 mm) y las de 2850 a
  3450 mm llevan llamada a nota y rayas; en la Tabla 3 (Clase III, PDF 6–7) la
  última fila con acero es la de 2700 mm. La nota manda a la Sección 7.2, y su
  7.2.1 (pág. impresa M 170M-13) los llama «special designs for pipe sizes that do
  not have steel reinforcement areas shown in Tables 1 to 5»; el **7.2.2** —no el
  7.2.3, como citaba el auditor— exige que su descripción «shall include the wall
  thickness». El tope es por tanto **2.70 m, el último diámetro con diseño
  estándar** (`constantes_normativas.DIAMETRO_MAX_CON_DISENO_ESTANDAR_M170M_MM`,
  citas `AASHTO_M170M.7.2.1` y `.7.2.2`), y coincide con la última fila de pared B
  declarada: ningún escalón del concreto puede detenerse por falta de espesor. No
  leído en el ejemplar: el cuerpo de la Tabla 2 (PDF 4) y el final de la Tabla 4.
- **Qué haría falta:** para ofrecer un tubo de concreto de 2850 a 3600 mm, el diseño
  especial aprobado de un fabricante con su espesor de pared, y entonces una puerta
  que lo admita —hoy no existe: declarar la pared en `espesor_pared_conducto` no
  basta, porque el tope no pasa de 2.70 m—; y, de quien conozca el mercado, el valor
  de `D_max_catalogo`.
- **Dónde vive:** `src/modulos/M2_material.py::tope_de_diametro`
- **VE-5 (ítem 24):** sigue igual, ver VE2-G.

## T4-03 · `v_max_tmc` es [A] con ventana y `v_max_hdpe` sigue [C]: los dos valen 4.572 m/s y no son la misma cosa

- **Qué se difirió:** la sustitución del techo por la regla de nivel de abrasión
  (opción B del dictamen), que el dueño descartó: se aplicó la **opción A**
  (`INF-3.2.4`).
- **Por qué:** WSDOT Hydraulics Manual M 23-03.12 **prohíbe** el termoplástico en
  abrasión severa (§8-3.3, pág. 8-13) y describe ese nivel, entre otras dos
  características, por velocidades mayores de 15 ft/s (Table 8-4, págs. 8-27 y 8-28):
  el techo del HDPE es [C], con la prohibición citada de donde está y la tabla sólo
  para el umbral, y la lectura —tomar la velocidad sola como suficiente— declarada
  como `Interpretacion` de la tabla. Para el **metal** la misma tabla no prohíbe
  nada en ningún nivel: pide más calibre o solera de concreto, y lo pide ya desde
  6 ft/s (1.829 m/s). El techo del TMC es por tanto una **adopción**: [A], valor
  4.572 m/s, ventana **(3.048, 4.572)** —el piso son los 10 ft/s del §3-3.5 (pág.
  3-11), el techo no es 4.6—, sin «límite conservador» ni «por encima de este valor
  exige mayor calibre» en la ficha. `M5._paso_v3` lee la etiqueta de la ficha y ya no
  imprime «[C], con fuente WSDOT» para los dos. **V3 no deduce el nivel de abrasión
  de la velocidad**: el nivel es un dato de campo opcional y lo aplica la matriz de
  durabilidad. Consumidores de la ventana vieja `(V_MIN, 4.572)` del TMC, revisados:
  dos tests llevaban el techo del TMC al piso de la ventana (`test_pf3_barrido`,
  `test_ext11_propiedades`) y ahora lo hacen con `con_valor`, diciéndolo.
- **Qué haría falta:** para volver a [C], una fuente que fije una velocidad máxima
  para la tubería metálica corrugada; ninguna de las seis consultadas lo hace (la
  ficha las lista con página).
- **Dónde vive:** `src/criterios/hidraulica.py::v_max_tmc`

## T4-04 · La matriz de durabilidad filtra de verdad, con ensayos opcionales que entran por `--datos-externos` y no por `CLAVES_EXTERNAS`

- **Qué se difirió:** un umbral de cloruros para el **concreto** y la casa de [S] de
  corredor (`datos_sitio.py`) para los ensayos.
- **Por qué:** `M2.matriz_durabilidad` devuelve un dictamen y
  `M2.materiales_candidatos` lo aplica; `MD.disenar_punto` lo recibe del servicio.
  Sin ensayos no actúa y la memoria imprime «durabilidad: sin ensayos, matriz no
  aplicada» en cada punto que llega a la Fase 3. Cada regla lleva sólo la fuente que
  la sostiene: **pH** fuera de 5.0–8.5 y **resistividad** menor de 1000 ohm-cm
  excluyen el TMC (WSDOT §8-5.1 y §8-5.2; criterio [C] `durabilidad_tmc_umbrales`,
  que sólo se puede endurecer); pH menor de 5.8 **exige** proteger la tubería
  metálica ([N], EG-2013 507.10, que lo escribe para el agua que conduce el tubo: con
  una sola clave `pH` se aplica al valor declarado, lado seguro); **abrasión** severa
  excluye el HDPE (§8-3.3) y **avisa** al metal y al concreto; los **sulfatos**
  **exigen** al concreto el cemento, la a/c y el f'c de la Tabla 4.4 de E.060 y nunca
  lo excluyen. Decisiones que no son del prompt: (a) **dos claves de sulfatos**
  (`sulfatos_suelo_ppm`, `sulfatos_agua_ppm`) y no una `sulfatos_ppm`, porque la
  Tabla 4.4 tiene dos escalas —% en peso en el suelo, ppm en el agua— y una sola
  clave sería ambigua; (b) para el **concreto** los cloruros avisan y no deciden,
  porque E.060 4.4.2 define la exposición por el origen del cloruro y no por un
  umbral en ppm; (c) las seis claves entran
  por el mismo JSON de `--datos-externos` (sección `globales` para el sitio, `puntos`
  para una calicata) y **no** están en `servicio.CLAVES_EXTERNAS`, cuyas claves son
  datos que alguna etapa **exige**: metidas ahí, el pre-vuelo las habría anunciado
  como seis faltas por punto; (d) si la etapa se bloquea, el bucle de materiales
  **no corre** sin filtro; (e) «suelo de fundación deficiente → marco» es aviso y
  no filtro (ficha T4-05).
  Lo que la auditoría adversarial corrigió de esta ficha —umbral de cloruros para
  el acero, la segunda mitad de EG-2013 507.10, el aviso fijo y el cruce con el [S]
  del EMS— está en la ficha T4-09.
- **Qué haría falta:** decidir si los ensayos de corredor merecen ficha en
  `datos_sitio.py` —hoy un ensayo «del sitio» es un global del JSON, con su origen
  impreso—; y un umbral de cloruros para el concreto, que E.060 no da.
- **Dónde vive:** `src/modulos/M2_material.py::matriz_durabilidad`

## T4-05 · `sucs_fundacion` tiene consumidor: el aviso de marco, con el conjunto de suelos declarado y no inventado

- **Qué se difirió:** que el aviso se convierta en regla (cambiar el tipo de obra), y
  el primer consumidor de la columna, `c_phi_fundacion`.
- **Por qué:** `INF-5.1.9` —columna obligatoria que ningún módulo leía— lo asignó el
  orquestador a T-4. El Manual (núm. 4.1.1.3.4 a) **recomienda** el marco cuando el
  suelo de fundación es de mala calidad y **no define** «mala calidad» (ficha C6-01,
  condición `COND-MARCO-SUELO-MALA-CALIDAD`). No se inventó el mapeo: el criterio [A]
  `sucs_fundacion_deficiente` declara el conjunto, se elige dentro de los quince
  símbolos de la Figura 3 de la E.050 (pág. 31) y vale por defecto `OL`, `OH`, `PT`
  —los suelos orgánicos y la turba sobre los que el Art. 24 de la E.050 (pág. 37) no
  deja cimentar—. `M2.matriz_durabilidad` parte los suelos de frontera (`CL-OL`),
  rechaza un conjunto con símbolos que no existen, no avisa en la Familia C (ya es
  marco) y, ante una celda que no es SUCS, lo dice sin detener. Es **aviso** porque el
  párrafo de la fuente es recomendación atenuada y un `Fundamento` con verbo de
  obligación no pasaría T11. Los cuatro puntos del fixture (SM, SP-SM, SM, ML) no
  están en el conjunto: ganan una línea, no un aviso, y ningún resultado cambia.
- **Qué haría falta:** un estudio de suelos que diga, para la obra, qué grupos tratar
  como deficientes (se declara en el criterio); y la Sec. 9.3 ensamblada para el
  otro consumidor.
- **Dónde vive:** `src/criterios/geotecnia.py::sucs_fundacion_deficiente`

## T4-06 · `DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO` se conserva sin consumidor: la «rama inactiva» de la hoja de ruta no existe y no se le inventa una

- **Cerrado en VE-5 (lote catlic): ver la ficha VE5-CAT-01.** Lo que sigue es el texto de T-4.

- **Qué se difirió:** programar la rama de selva alta que la hoja de ruta §3.1 pide
  («programar la rama y declararla inactiva»). `INF-5.1.16`.
- **Por qué:** comprobado por AST sobre `src/modulos/`, `src/servicio.py` y
  `cli.py`: **ningún módulo nombra la constante**; la rama inactiva no existe. Lo que
  sí existe es la cita `MC_HHD.4.1.1.3.7a` con su condición `COND-SELVA-ALTA` y la
  constante en `CONSTANTES_DE_REFERENCIA`. No se cablea por dos razones: (1) ningún
  dato de entrada dice en qué región natural está la obra —ni columna del CSV ni [S]
  de `datos_sitio.py`—, de modo que una rama necesitaría **primero** una entrada que
  nadie ha pedido, y activarla por defecto sería inventar el dato; (2) el corredor
  del repositorio es de costa, donde la hoja de ruta dice que no aplica. Una rama
  que nunca se ejecuta y no tiene con qué decidir si se ejecuta es código muerto con
  apariencia de regla. La constante se queda porque es un valor [N] recomendado,
  verificado contra su página, que el día que haya región natural se usa tal cual.
- **Qué haría falta:** un [S] de corredor `region_natural` (o equivalente) en
  `datos_sitio.py` con su trazabilidad, y entonces la rama en `M2.catalogo`: piso de
  diámetro del TMC igual a la constante cuando la región es selva alta, como
  recomendación impresa y no como rechazo —la fuente recomienda—.
- **Dónde vive:** `src/constantes_normativas.py::DIAMETRO_MIN_TMC_SELVA_ALTA_RECOMENDADO`

## T4-07 · El n de Manning del HDPE es [C] de HDS-5 (0.009 a 0.015): la cadena esperaba WSDOT Tabla 4-1 o un [A] de 0.009 a 0.013

- **Qué se difirió:** nada; se registra la discrepancia entre el prompt y la fuente.
- **Por qué:** el punto 5 pedía dejar la analogía con el concreto y citar una fuente
  «si alguna da n» —nombraba la Tabla 4-1 de WSDOT—, o declarar un [A] con ventana
  (0.009, 0.013). Leída, la Table 4-1 de WSDOT (PDF 93) es una tabla de
  **referencias**, sin valores de n. La que sí los da es la **Table B.1 de HDS-5**
  (pág. B.6, PDF 208), fila «Corrugated Polyethylene, Smooth»: 0.009–0.015. Es fuente
  técnica reconocida y ya adoptada por el proyecto, de modo que el criterio es [C] y
  no [A], su valor se **deriva** de la tabla del registro y su ventana es el rango de
  la fila. El rango es más ancho que el del concreto en los dos sentidos: n máximo
  0.015 pide más diámetro por capacidad; n mínimo 0.009 da más velocidad contra el
  techo de V3. M 294 no trae n.
- **Qué haría falta:** nada para el perfil. Un fabricante con ensayo propio puede
  estrechar el rango declarándolo dentro de la ventana.
- **Dónde vive:** `src/criterios/hidraulica.py::n_manning_hdpe`

## T4-08 · Entrada obligada de T-5: la plancha adoptada del TMC no cumple el factor de flexibilidad hasta su tope, y `espesor_pared` de TMC y HDPE es una ENVOLVENTE geométrica

- **Qué se difirió:** la verificación estructural del calibre del TMC —factor de
  flexibilidad, empuje de anillo, pandeo, costura— y la del perfil del HDPE. Son de
  la Fase 8 (T-5), **también a nivel de perfil**.
- **Por qué:** lo midió la auditoría adversarial de T-4 (H7). El catálogo ofrece la
  plancha adoptada (`corrugacion_y_espesor_tmc` = 68 por 13 mm, 2.01 mm) hasta
  2.10 m, que es el tope de la **corrugación** (Table 6 de M 36), no el de la
  plancha. ASTM A796 núm. 10.3 (PDF 4) limita el factor de flexibilidad FF =
  s²/(E·I) a 0.245 mm/N para 13 mm de profundidad en terraplén; con I = 39.20 mm⁴/mm
  (Tabla 5) y E = 200 000 MPa el diámetro límite es √(0.245 × 200 000 × 39.20) ≈
  1386 mm. De 1.50 a 2.10 m esa plancha **no cumple** y el catálogo la recorre igual.
  M2 no duplica la Fase 8: lo dice la ficha del criterio, el rótulo del tope
  (`ROTULO_TOPE_DE_CORRUGACION`) y el docstring de `M8.seleccionar_clase_calibre`,
  que ya no afirma que el espesor es consecuencia del calibre que la Fase 8
  seleccione. **Y una advertencia de tipo:** lo que `M2.espesor_pared` devuelve para
  TMC y HDPE es una **ENVOLVENTE** geométrica —(exterior − interior)/2: profundidad
  de corrugación más plancha, o altura del perfil hasta el diámetro exterior
  máximo—, que sirve para la clave física (7.A) y el volumen desplazado (V7). **No
  es un espesor estructural**: quien lo use como tal para un área o una inercia se
  equivoca en un orden de magnitud.
- **Qué haría falta:** que T-5 seleccione el calibre por punto con el área, la
  inercia y el radio de giro de `constantes_normativas.TMC_PLANCHA_CORRUGADA`, rechace
  o suba de plancha donde el FF no cumpla, y devuelva al catálogo la plancha que
  resulte (el espesor de la envolvente cambia con ella).
- **Dónde vive:** `src/modulos/M2_material.py::ROTULO_TOPE_DE_CORRUGACION`

## T4-09 · El suelo agresivo para el acero se lee de AASHTO LRFD por analogía y por defecto avisa; EG-2013 507.10 se aplica entera; los ensayos no entraron al censo de variables

- **Qué se difirió:** la entrada de las seis claves de durabilidad al censo
  `variables_entrada` y a la ayuda del JSON; unificar los sulfatos con el [S]
  `exposicion_quimica_ems`; la nota (*) de las Tablas 4.2 y 4.4 de E.060.
- **Por qué:** correcciones de la auditoría adversarial de T-4 (H3 a H6, H8). AASHTO
  LRFD da criterios electroquímicos para **acero galvanizado enterrado** —Art.
  11.10.6.4.2a (pág. 11-89) y 11.12.8 (pág. 11-134): pH 5 a 10, resistividad ≥ 3000
  ohm-cm, cloruros ≤ 100 ppm, sulfatos ≤ 200 ppm; 10.7.5 (pág. 10-125), indicativos
  para pilotes—. Son de refuerzos de muros y anclajes, **no de alcantarillas**: la
  matriz los aplica **por analogía** (`suelo_agresivo_acero_lrfd` [C]) y su efecto
  sobre la TMC es un [A] de perfil que vale **`aviso`** —decisión del orquestador: la
  exclusión se reserva a las fuentes de alcantarillas—, con `excluye` declarable y
  barrible. La materia orgánica no entra (no hay dato) y la dispensa con ≥ 5000
  ohm-cm no se aplica. La segunda mitad de EG-2013 507.10 —«o que los suelos
  circundantes presenten sustancias agresivas»— **exige** proteger la TMC con
  sulfatos sobre la exposición insignificante de E.060 o con ese suelo agresivo;
  qué cuenta como «sustancias agresivas» es **lectura del proyecto**, dicha en la
  regla y en el fundamento `F3.DUR.SUELO_AGRESIVO` (no como objeto `Interpretacion`,
  que en el registro cuelga de las tablas). El texto cualitativo del Manual (núm.
  4.1.1.3.7 f y g) es un **aviso fijo** de la TMC candidata. Las ventanas de
  `durabilidad_tmc_umbrales` sólo endurecen. Si los sulfatos de la matriz y el [S]
  del EMS dan exposiciones distintas, la matriz **avisa**: no se unificaron, porque
  una entrada es de perfil y por punto y la otra de expediente y de corredor. Las
  seis claves no entraron al censo: el de datos externos se deriva de
  `servicio.CLAVES_EXTERNAS`, que el pre-vuelo de PF-2 lee como «dato que una etapa
  exige», y abrir una población «opcional» es un cambio de esquema del censo.
- **Qué haría falta:** una población de datos opcionales en `variables_entrada`, con
  ficha en la ayuda del JSON y panel en la pestaña 1, que el pre-vuelo no cuente
  como falta; y un criterio de agresividad escrito para tubería de acero corrugado.
- **Dónde vive:** `src/criterios/geotecnia.py::suelo_agresivo_lrfd_sobre_tmc`

## T4-10 · Un dato que falta en un candidato anterior bloquea la aceptación de uno posterior: el «caso mixto» de PC-28 cambia

- **Qué se difirió:** nada; se registra una inversión de contrato aceptada por el
  orquestador.
- **Por qué:** EXT-1 (PC-28) dejó dicho que si a TODOS los candidatos les faltaba un
  dato el punto salía con `DatoFaltanteError`, y dejó **sin cambio** el caso mixto: si
  a uno le faltaba y otro posterior cerraba, se adoptaba el posterior. El auditor
  adversarial de T-4 (H1) lo midió sobre el pipeline real: un punto cuyo concreto
  incumplía V3 hasta el último escalón con pared declarada, y se detenía en el
  siguiente por falta de espesor, salía **dimensionado en TMC sin bloqueo** — elegido
  por descarte de un material más preferente que nadie terminó de evaluar. Desde T-4
  vale la regla que ya valía para criterios pendientes, criterios inválidos y método
  no evaluable: antes de aceptar un candidato, ninguno anterior puede haberse detenido
  por un dato que falta; se relanza el primero, con su campo. Al revés no cambia:
  cuando ninguno cierra, el punto sigue «no factible» si los escalones evaluados
  incumplen, y el motivo dice cuáles no se evaluaron y por qué dato.
- **Qué haría falta:** nada. Quien quiera el comportamiento anterior tiene que
  declarar el dato que falta, que es lo que el bloqueo pide.
- **Dónde vive:** `src/modulos/MD.py::_exigir_datos_presentes`

---

# Parte XLIII — Lo que T-1 de la cadena T dejó escrito: la hidrología que el programa calcula y la que no

T-1 (2026-11-11) crea `src/modulos/MH_hidrologia.py` (Fase 1-bis): el caudal de diseño de
las Familias A y B por el método racional, a partir de `--cuencas` y `--estacion`, sin
quitar la vía de siempre (`Q_m3s` lleno gana). Seis cosas quedan dichas y no hechas, y
tres más (`T1-07` a `T1-09`) las dejó la auditoría adversarial de la misma sesión.

## T1-01 · De las ocho distribuciones del núm. 3.7.1 el programa ajusta tres, y la prueba χ² no se implementa

- **En parte en VE-5 (lote mh, 2026-11-20): la χ² se calcula; las cinco siguen sin
  evaluarse.** La prueba χ² (núm. 3.7.2 a, ecuación 12; citas `MC_HHD.3.7.2a`,
  `#INTERVALOS`, `#ALCANCE`) se imprime en el paso de la bondad como **contraste** de
  Kolmogorov-Smirnov —no detiene ni elige— y sólo para la normal y la log normal, que
  son las que el numeral dice que verifica. k sale del criterio [A]
  `intervalos_de_clase_chi_cuadrado` (Sturges, 1 + ⌈log2 n⌉; ventana: ⌈√n⌉), con
  intervalos de igual amplitud entre el menor y el mayor dato y los extremos abiertos; el
  valor crítico es el cuantil de `scipy.stats.chi2`. Decisión del dueño: las cinco
  distribuciones sólo con un estimador que una fuente de `NORMAS_DIR` imprima. Barrido
  hecho (texto de cada PDF): el Manual de Hidrología imprime sólo la densidad de las cinco
  (págs. impresas 27 a 30); el Manual de Puentes las nombra (PDF 51) sin estimador;
  WSDOT, HDS-5, HEC-14, USACE, USBR y DG-2018 no las tratan. Las tesis de
  `ejemplos_resueltos/casos_reales/` no son fuente (sirven para comparar). Siguen
  `MetodoNoEvaluableError` con el rótulo de la hidrología.

- **Qué se difirió:** el ajuste de Log Normal 3P, Gamma 2P, Gamma 3P, Log Pearson III y
  Log Gumbel, y la prueba de bondad χ² del núm. 3.7.2 a).
- **Por qué:** el Manual imprime la densidad de las ocho y sólo de tres dice cómo se
  estiman los parámetros (Normal, Log Normal 2P y Gumbel por momentos). Elegir un
  estimador para las otras cinco —momentos, máxima verosimilitud, factores de
  frecuencia— es adoptar un procedimiento sin fuente en `normas/`. La χ² exige un número
  de intervalos de clase que el Manual no fija, y el propio texto la limita a la normal
  y la log normal; Kolmogorov–Smirnov cubre las tres y es la que «permite elegir».
- **Qué haría falta:** una fuente que fije el estimador (el texto de Chow o de Aparicio
  que el Manual cita, en `normas/`), su cita en el registro y el caso patrón.
  Declarar hoy una de las cinco detiene el cálculo con «método no evaluable».
- **Dónde vive:** `src/modulos/MH_hidrologia.py::_modelo`

## T1-02 · El tratamiento FEN `dos_poblaciones` se puede declarar y no se evalúa

- **Qué se difirió:** el análisis de población mixta de la serie (una distribución para
  los años FEN, otra para los neutros, combinadas por su probabilidad de ocurrencia).
- **Por qué:** es el tratamiento que describe el fenómeno, y ni el Manual de Hidrología
  ni ninguna fuente de `normas/` da el procedimiento. Con tres años FEN en una serie
  tampoco hay con qué ajustar la segunda población. El criterio
  `homogeneidad_serie_fen` lo lista en su ventana para que la opción exista y diga por
  qué no corre, en vez de desaparecer.
- **Qué haría falta:** una fuente técnica con el procedimiento, y una serie con años
  FEN suficientes. Mientras tanto la memoria imprime la lluvia de diseño con la serie
  completa y sin los años FEN, lado a lado.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::precipitacion_de_diseno`

## T1-03 · V8 (evento extremo) todavía no pide su caudal a la hidrología

- **En parte en T-7b (2026-11-13):** la mitad que faltaba del lado de V8 existe. V8
  tiene método y umbral declarables, y `Q_evento_extremo_m3s` y `TW_evento_extremo_m`
  son claves de `--datos-externos` que V8 lee (ficha T7B-02). **Sigue diferido** el
  enlace con la Fase 1-bis: el programa no calcula ese caudal aunque tenga la cuenca y
  la estación; lo recibe declarado.
- **Qué se difirió:** el enlace entre `TR_evento_extremo` y la Fase 1-bis: que V8, con
  el TR declarado, obtenga `Q_evento_extremo_m3s` de la cuenca y la estación, o lo
  reciba declarado (y entonces gane).
- **Por qué:** la mitad hidrológica está lista —`caudal_de_diseno(cuenca, serie, TR)`
  vale para cualquier TR, y un test fija que crece con él— pero V8 no tiene la otra
  mitad: no hay clave por la que declarar ese caudal, V8 no recibe la cuenca ni la
  serie (vive en M5, que no importa la hidrología), y la comparación contra la corona
  del terraplén no está escrita. Cablear sólo el caudal dejaría a V8 con un número y
  sin nada que hacer con él. El TR sigue siendo decisión del Propietario: no se adopta.
- **Qué haría falta:** una clave externa `Q_evento_extremo_m3s`; que el servicio la
  resuelva (declarada, o calculada por MH con el TR del criterio) y se la pase a V8; y
  el umbral de colapso, que la hoja de ruta no fija.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v8_evento_extremo`

## T1-04 · La hidrología entraba sólo por la CLI; desde UI-1 la ventana y la sesión la conocen, y desde VE-4b el pre-vuelo anticipa lo que detendría la Fase 1-bis — Cerrado (UI-1 y VE-4b)

- **Cerrado (UI-1, la interfaz y la sesión):** T-1 difirió los campos de `--cuencas` y
  `--estacion` en la pestaña 1, su sitio en la sesión, el SHA-1 de los dos archivos y la
  mitad del pre-vuelo que estima si el cálculo se detiene. UI-1 cierra las tres primeras:
  dos campos de archivo con «Examinar…» y su «i» (la ayuda sale de
  `src/ayuda_entrada.py::fichas_de_hidrologia`), `servicio.cargar_hidrologia` al
  ejecutar y `hidrologia=` a `correr`, la sesión formato 4 con las dos rutas
  (`sesion.FORMATO_SESION`), el hijo del PDF y `cli.py --sesion` con ellas, el anticipo
  con el mismo conjunto de obras calculables que la CLI y M0
  (`servicio.ids_con_caudal_calculable`) y las dos huellas en `ContextoCorrida`, de los
  bytes que se leyeron. Las decisiones, en la ficha UI1-01. UI-4 lo recorrió de extremo a
  extremo en la ventana de verdad sobre la corrida de referencia `hidrologia_calculada`:
  los dos CSV por «Examinar...», el caudal «calculado» en el detalle de la pestaña 3, el
  mismo JSON que la CLI con `--cuencas` y `--estacion`, los dos PDF del hijo con la
  hidrología y la sesión que la guarda y la repone (ficha UI4-01).
- **Cerrado (VE-4b, el estimador):** con los dos CSV el pre-vuelo de la CLI y el
  anticipo de la ventana (que sólo pinta) anuncian, punto a punto, lo que la Fase 1-bis
  registraría como `Bloqueo`, con su misma etapa y su mismo mensaje
  (`anticipo.POBLACION_HIDROLOGIA`, todas DETIENE). Qué compuertas anticipa sin TR y sin
  registrar usos: `MH_hidrologia.anticipar_caudal`; la precedencia (el área escrita dos
  veces siempre, nada más con `Q_m3s` declarado): `servicio.anticipar_fase_hidrologia`;
  lo que depende del TR, como «puede detener»: `anticipo.PUEDE_DETENER_SEGUN_TR`. La
  unión contra la corrida real: `tests/test_ve4b_prevuelo_hidrologia.py`.
- **Abierto (a propósito):** lo que sólo se decide con el TR o con el cálculo hecho: el C
  vial por encima de 100 años, el rango de duración de la intensidad, el coeficiente de
  la ecuación (35) y un Tc o un caudal no positivos; y nada se anticipa de un punto cuya
  Fase 2 se detiene antes, donde lo anunciado sobra.
- **Qué haría falta:** el TR en el pre-vuelo (la Fase 2 sin cargar los puntos); no se
  recomienda: haría del pre-vuelo una segunda corrida.
- **Dónde vive:** `src/servicio.py::anticipar_fase_hidrologia`

## T1-05 · Lo que el prompt de T-1 suponía y el Manual no trae

- **Qué se difirió:** nada de cálculo; son cinco discrepancias entre el encargo y la
  fuente, resueltas a favor de la fuente. (1) La Tabla Nº 05 no lista a Témez: su
  fórmula es la ecuación (30) del núm. 3.12.2.1, con L en km y Tc en horas. (2) La
  Tabla Nº 04 no es de «coeficientes regionales» sino de duración. (3) La Tabla Nº 08
  no tiene fila de pavimento ni de talud: una superficie de la plataforma vial entra
  por el criterio [C] `coeficiente_escorrentia_superficie_vial` (WSDOT, Table 2-2), y
  nunca por una fila de la Tabla Nº 08 puesta por omisión. (4) El límite del método racional es «A<10 Km2», estricto, y no «≤ 10».
  (5) El núm. 3.12.2 no trae ejemplo numérico: los dorados están calculados a mano.
- **Por qué:** `CLAUDE.md`, «Fuente de verdad»: gana el PDF verificado.
- **Qué haría falta:** nada. Lo que sí queda abierto: la ponderación de C por subáreas
  (plataforma más talud) no está en el Manual y no se implementa —una fila por obra—,
  y la relación regional I = K·T^m/t^n (ecuación 17) tampoco, porque sus tres factores
  son datos de un estudio regional.
- **En parte en VE-5 (lote mh, 2026-11-20): la ecuación (17) tiene puerta.** El criterio
  `relacion_intensidad_duracion` admite una tercera opción, `idf_regional_ec17`, y con
  ella la intensidad es I = K·T^m / t^n (cita `MC_HHD.3.8.1#EC17`, pág. impresa 38) con
  t la duración de diseño en minutos (el tc, con la duración mínima) y T el periodo de
  retorno del caudal. K, m y n son el criterio `factores_idf_regional` [S], **sin valor**
  (dato de un estudio regional: sin él, `CriterioPendienteError`, y el pre-vuelo lo
  anticipa); `MH.factores_idf_regional` exige las tres claves y que sean positivos. La
  serie de la estación se sigue ajustando —la puerta FEN no cambia— y su intensidad por
  Dick y Peschke se imprime al lado como contraste. Vale también para el punto fijo de
  Izzard y la onda cinemática.
- **Sigue abierta la ponderación de C por subáreas**, ya con fuente: ficha VE5-MH-01.
- **Dónde vive:** `src/normativa/tablas.py::T05`

## VE5-MH-01 · La ponderación de C por subáreas tiene fuente [C] y no se implementa: pide cambiar el contrato

- **Qué se difirió:** el coeficiente de escorrentía ponderado de una cuenca con varias
  coberturas (plataforma más talud), ΣC·A / ΣA.
- **Por qué:** el Manual no la trae (ficha T1-05), pero la fuente técnica que el proyecto
  ya usa para la plataforma sí: WSDOT Hydraulics Manual, Equation 2-4 (pág. impresa 2-8,
  PDF 44), «When several subareas within a drainage basin have different runoff
  coefficients, the rational formula can be modified as follows», Q = I·ΣCA / K. Sería
  [C], no [A]. Lo que falta no es fuente sino forma de entrada: hoy el CSV de cuencas es
  una fila por obra, con un área que tiene que coincidir con `area_ha`, y varias subáreas
  por obra cambian el contrato, que decide su dueño.
- **Cerrado en VE-7 (lote B, B10; ficha VE7B-06):** la columna opcional `subareas` y ΣC·A/ΣA en
  el paso del coeficiente. La cita de la Eq. 2-4 sigue sin registrar.
- **Qué haría falta:** la cita de la Eq. 2-4 en el registro.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::_paso_c`

## T1-06 · `MetodoNoEvaluableError` admite un rótulo propio para la hidrología

- **Qué se difirió:** nada ya. Durante la FASE A quedó pendiente actualizar la frase
  de `CLAUDE.md` «Su `str()` empieza siempre por `MOTIVO_METODO_NO_EVALUABLE`»; se
  hizo al integrar.
- **Por qué:** ese rótulo nombra a HDS-5 («HDS-5 3.24, Sección 3.5») porque los dos
  casos de EXT-3 son de HDS-5. La hidrología levanta la misma excepción por límites del
  Manual de Hidrología, y encabezarla con HDS-5 sería una cita falsa: pasa `rotulo=`
  con el suyo. El defecto no cambia y los tests de EXT-3 siguen valiendo.
- **Qué haría falta:** nada ya: la sección «Excepciones» de `CLAUDE.md` lo dice desde
  la integración de T-1 (2026-11-12).
- **Dónde vive:** `src/modelos/errores.py::MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA`

## T1-07 · De las seis filas de la Tabla Nº 05 se implementan cuatro: Izzard y onda cinemática quedan diferidas — Cerrado (VE-5, lote mh)

- **Cerrado (VE-5, 2026-11-20):** las seis filas tienen función. `metodo_tc` admite
  `izzard` y `onda_cinematica`, con su dato de superficie en dos columnas opcionales del
  CSV de cuencas (`c_retardo_izzard`, `n_manning_superficial`: obligatorias con su método,
  vacías con cualquier otro). El tiempo de concentración sale del **punto fijo tc ↔ I**
  (`MH._punto_fijo_tc`): sustitución sucesiva desde una lluvia de 24 horas, con la MISMA
  relación intensidad-duración y la MISMA duración mínima del paso de la intensidad
  (`MH._intensidad_de_diseno`), hasta `TOL_REL_PUNTO_FIJO_TC` relativo; sin convergencia en
  `ITERACIONES_MAX_PUNTO_FIJO_TC`, `LimiteNumericoError`. La condición de Izzard «el producto
  de i por L debe ser ≤ 3800» (cita `MC_HHD.3.9#T05_IZZARD_IL`, exigencia) se exige con la
  intensidad del punto fijo y fuera de ella el punto no se evalúa. La onda cinemática lee la
  S de `S_terreno` («pendiente promedio del terreno»: la `Interpretacion` de
  `MC_HHD.3.9#T05_ONDA`). Los dorados son forma cerrada (onda, con una curva I = a/t^b) y
  `brentq` (Izzard), en `tests/test_ve5_mh.py`. Sigue sin anticiparse en el pre-vuelo la
  condición i·L de Izzard, que depende de la intensidad y por tanto del TR (ficha T1-04).

- **Qué se difirió:** las filas «Izzard (1946)» y «Ecuaciones de onda cinemática
  Morgali y Linsley (1965), Aron y Erborge (1973)» de la tabla de fórmulas de tiempo
  de concentración. Las seis filas están transcritas enteras en el registro
  (`MC_HHD.T05`), con sus observaciones; cuatro tienen función y dos no.
- **Por qué:** las dos llevan la **intensidad de la lluvia dentro de la fórmula**, y
  la intensidad depende a su vez de la duración, que es el tiempo de concentración:
  hay que iterar. Además piden datos que el CSV de cuencas no trae y que no se pueden
  suponer: Izzard, un coeficiente de retardo de la superficie y una condición de
  aplicación (el producto de intensidad por longitud); la onda cinemática, el n de
  Manning del flujo superficial. Para que una cuenca plana y el área tributaria de
  una cuneta tuvieran un tiempo de concentración evaluable y citado bastaban las dos
  que se hicieron: la de la FAA (C, L y S, que ya están) y la de retardo SCS (con el
  número de curva como columna opcional `CN`, sin valor por omisión).
- **Qué haría falta:** dos columnas opcionales más en el CSV de cuencas (coeficiente
  de retardo; n de Manning superficial), el punto fijo tc ↔ I con su guardia de
  convergencia, y un caso patrón hecho a mano para cada una.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::METODOS_TC`

## T1-08 · El método racional modificado no estaba implementado: de él se tomaban la fórmula de Témez y el coeficiente K — Cerrado (VE-2) de 10 a 770 km²

- **Qué se difirió:** el método completo del núm. 3.12.2.1 del Manual de Hidrología
  (págs. impresas 50 a 52): su intensidad con el factor de torrencialidad, su factor
  reductor de la lluvia por área y su coeficiente de escorrentía por número de curva.
- **Por qué:** el prompt pedía Témez como método de tiempo de concentración, y la
  fórmula no es una fila de la Tabla Nº 05 sino la ecuación (30) de ese método. Usarla
  con el racional simple es un **uso híbrido**, y la auditoría pidió que se declarara
  en vez de callarse: el paso del tiempo de concentración y el del caudal lo dicen, y
  el coeficiente de uniformidad K de la ecuación (31) —que es del mismo numeral y
  sube el caudal— lo decide el criterio [A] `coeficiente_uniformidad_temez`, con
  «aplicar» como valor de archivo. El resto del método pide el número de curva. **Corregido
  en VE-2:** esta ficha decía que pedía también «un mapa de isolíneas del factor de
  torrencialidad» para España, y la página no lo trae: el 11 está escrito, fijo, dentro de
  la ecuación (34) (pág. impresa 52, leída en la imagen).
- **Cerrado (VE-2):** el método entero calcula de 10 a 770 km² (ficha VE2-F); bajo 10 km²
  sigue el uso híbrido de arriba.
- **Qué haría falta:** hecho en VE-2 lo que esta ficha pedía (las ecuaciones en el registro,
  el número de curva como dato de la cuenca, el método elegido por el área); el 11 es el
  del Manual, y un factor regional del Perú en su lugar pediría una fuente que hoy no está
  en el repositorio de normas. Lo de 770 km² en adelante, en VE2-F.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::coeficiente_de_uniformidad`

## T1-09 · CERRADA: declarar `serie_sin_fen` cuando da menos lluvia que la serie completa detiene el cálculo del punto

- **Qué se difirió:** nada ya. La auditoría de T-1 dejó abierta una sola pregunta —si
  el incumplimiento de la regla de la hoja de ruta (Fase 1-bis: «reportar el ajuste
  con y sin ellos, adoptar el más conservador») debía **bloquear** el dimensionamiento
  o sólo imprimirse— y la sesión la dejó en «se imprime NO CUMPLE y no detiene», a la
  espera del dueño. **El dueño decidió (2026-11-11): detiene.**
- **Por qué:** un punto no puede quedar dimensionado sobre un caudal que incumple la
  exigencia del núm. 3.4 del Manual (la serie «deberá incluir» los años de El Niño) y
  la regla de la hoja. El criterio `homogeneidad_serie_fen` sigue siendo [A] y su
  ventana sigue listando `serie_sin_fen`: se puede declarar, y **pasa** cuando da
  igual o más lluvia que la serie completa. Cuando da menos, el cálculo hidrológico
  del punto se detiene por la vía que el módulo ya usa para un ajuste que no pasa la
  prueba de bondad (`MetodoNoEvaluableError`: no falta un dato ni un criterio, hace
  falta otro tratamiento), con las dos lluvias en el mensaje y el remedio: declarar
  `serie_completa`, o traer el caudal del estudio hidrológico por la columna `Q_m3s`.
  El caso inverso —la serie completa da menos que la serie sin los años marcados
  FEN— **no** se detiene: la serie completa es la que el Manual manda usar, y el paso
  lo imprime como indicador con aviso. Un caudal declarado por columna no cambia:
  avisa y no bloquea.
- **Qué haría falta:** nada. Lo que el bloqueo no hace: la memoria de un punto
  detenido no trae los pasos de la Fase 1-bis (el cálculo no llegó a entregarlos); el
  contraste va entero en el mensaje del bloqueo. El paso 1b.3b se imprime cuando la
  regla se cumple, o cuando no hay segundo ajuste con que comparar.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::CODIGO_FEN`

---

# Parte XLIV — Lo que T-6 de la cadena T dejó escrito: la geometría de 7.B

T-6 (2026-11-11, integrado el 12 detrás de T-2, T-4 y T-1) cerró la cota de
fondo de entrada adoptada sin aviso (`INF-5.1.18`), la longitud con la altura
del eje para los dos taludes y los pasos de 7.B que iban como frase
(`INF-3.3.3`), y la mitad de M7 de la pendiente del conducto (`INF-3.2.7`,
que T-2 había abierto con la banda y V10). Cinco cosas quedaron decididas de
una manera que conviene poder discutir.

## T6-01 · El diseño corre con la longitud aproximada al fondo; la longitud entre cabezales a la clave se imprime y no la sustituye

- **Qué se difirió:** la longitud por extremo se mide hasta el **fondo** del
  conducto en cada extremo y es la que usan el control de salida, el TW por
  cota, la caída y la cota de salida. La longitud con el talud muriendo en la
  **clave** de la sección adoptada —la de un conducto entre muros de
  cabecera— se calcula después del diseño (`M7.longitud_a_la_clave`), se
  imprime en el paso 7.B.5 con su diferencia y **no** vuelve a entrar al
  cálculo hidráulico.
- **Por qué:** la longitud a la clave depende de la sección, y la sección
  depende de la longitud: `MD.disenar_punto` recibe `L` y `TW` como datos y
  recorre el catálogo con ellos. Hacer `L` función de cada escalón exige que
  el TW por cota también lo sea y cambia el contrato de MD; iterar el diseño
  hasta el punto fijo puede no converger sobre un catálogo discreto. La
  fuente resuelve el círculo de otra manera y es la que se sigue: el HDS-5
  manda empezar con una longitud **aproximada** (núm. 3.1.4, pág. impresa
  3.9; núm. 2.2.4 b., pág. impresa 2.8) y encajar después la sección elegida
  (núm. 3.3.5, pág. impresa 3.25: «the length should be close to the
  approximate length, and the headwalls and wingwalls must be dimensioned»),
  sin dar tolerancia. Medido en A-01 del fixture: 18.869 m al fondo y 14.676 m
  a la clave (22 % menos), con el control de entrada gobernando en los dos
  casos.
- **Qué haría falta:** que el cabezal por punto (T-7a) fije la cota de
  coronación del muro de cabecera —la clave es su mínimo—; con ella queda
  cerrada la **longitud entre cabezales, que es la de construcción y
  metrado**, y la longitud a la clave deja de ser sólo su cota superior. Si
  entonces se quiere que el control de salida use esa longitud, hace falta
  `L` por sección en MD, o declarar `longitud_m` por punto, que ya gana. El
  tamaño de la memoria que los pasos de 7.B añaden (70.3 KB por punto a
  expediente donde `5bca7c6` medía 63.7, y 87.6 KB a perfil donde medía
  76.8; el techo `KB_POR_PUNTO_MAX` sólo mide expediente y quedó pegado a la
  medida) lo reconcilia T-10, que es quien rehace la memoria.
- **VE-6 (ítem 22 del censo):** el control de salida de la sección adoptada se REHACE una vez
  con la longitud entre cabezales, se imprime (paso 9.0.6) y se avisa si la carga sube o el
  control cambia; el diseño no se sustituye. Ficha VE6-22.
- **Dónde vive:** `src/modulos/M7_geometria.py::longitud_a_la_clave`

## T6-02 · M7 acota la pendiente del cauce a la banda de T-2 y V10 juzga la que quedó: V10 sólo se incumple con una pendiente declarada

- **Qué se difirió:** nada queda diferido; es un reparto entre dos piezas que
  leen la misma banda (`M5.limites_de_pendiente()`, lectura única de
  `pendiente_minima_conducto` y `pendiente_maxima_conducto`) y que el auditor
  de T-6 pidió dejar escrito. `M7.pendiente_adoptada` resuelve la pendiente
  una vez, antes de la Fase 4, con tres orígenes: la **declarada**
  (`S_conducto`), que no se recorta; el **extremo** de la banda cuando la
  pendiente del **cauce** lo traspasa (origen «mínima» o «máxima»); y la del
  cauce. V10 juzga la pendiente con que corrió el diseño: como la del cauce
  ya llega dentro de la banda, en la corrida del servicio V10 sólo puede
  incumplirse con una pendiente declarada.
- **Por qué:** la cadena pide que 7.B deje la pendiente con su origen
  («mín/máx si gobierna»), y un punto cuyo cauce se sale de la banda no tiene
  remedio en el catálogo: V10 no depende del diámetro. Acotar no resuelve la
  obra y por eso se **avisa** (`M7.aviso_de_pendiente`, por
  `InformePunto.avisos()`, con el desnivel en metros en el paso 7.B.4). Con
  la **máxima**, el conducto queda más tendido que su cauce: el desnivel
  (S_cauce − S)·L pide una estructura de caída o de disipación que el
  programa no dimensiona, y V2b lo juzga según `regimen_v2b` —con
  `indicador_con_aviso`, el valor de archivo, el punto dimensiona con el
  indicador disparado; con `umbral_duro` no dimensiona y el motivo nombra
  V2b—. Con la **mínima**, la salida queda bajo el cauce natural y G2 la
  juzga contra el fondo del receptor. Una pendiente de cauce no positiva o no
  finita no se sustituye por un extremo: es `DatoInvalidoError`.
- **Cierre de la integración:** las fichas de los dos criterios de la banda
  dicen el reparto (decían «la aplica V10»), y la banda vacía, que se lee
  ahora fuera de `_etapa`, es un bloqueo del punto
  (`servicio.ETAPA_PENDIENTE`) y no tumba la corrida.
- **Qué haría falta:** dimensionar la caída o el disipador cuando gobierna
  la máxima (la protección de salida es de otro prompt de la cadena). Con
  los valores de archivo (0.0 y 0.10) el fixture no se mueve: sus pendientes
  de cauce van de 0.006 a 0.010 y la mínima, 0.0, no puede gobernar sobre un
  cauce positivo. Los casos patrón con cauce fuera de la banda
  (`test_pf1_hw_fuera_de_rango`) pasaron a declarar su pendiente.
- **Dónde vive:** `src/modulos/M7_geometria.py::pendiente_adoptada`

## T6-03 · El desnivel de entrega (0.0 m) y el esviaje máximo (45°) son adopciones: ninguna fuente da el número del primero, y el del segundo es una analogía

- **Qué se difirió:** nada del prompt, pero los dos valores se eligieron y
  hay que poder decir cómo. `desnivel_minimo_entrega_m` vale **0.0** —la
  entrega a nivel del fondo del receptor, que es lo que G2 verificaba sin
  ficha—, con ventana (0.0, 0.30). `esviaje_max_grados` vale **45°**, con
  ventana (45, 60), deja de ser opcional y superarlo es **aviso** (G3,
  veredicto INDICADOR, que sale por `InformePunto.con_aviso` como V2b) en
  vez del `DatoInvalidoError` que dejó el cierre de C10 (ficha C10-03).
- **Por qué:** el núm. 4.1.1.3.3 del Manual del MTC —al que la cadena remite
  el desnivel— son dos oraciones sin cifra que no hablan de la entrega; su
  Lámina Nº 01 tipifica las ubicaciones sin acotar ninguna y advierte que una
  salida sobre el cauce exige terreno resistente o enrocado. Un desnivel
  positivo no es, por tanto, conservador sin más, y el remanso del receptor
  ya entra por el TW. Para el esviaje, la única cifra de fuente es el máximo
  práctico de «about 45-degrees» del esviaje de **embocadura** (HDS-5 núm.
  5.4.2, pág. impresa 5.13), que alcanza al barril sólo con el cabezal
  paralelo a la vía: analogía, y por eso `[A]` y no `[C]`. Medido sobre el
  fixture: ningún valor de ninguna de las dos ventanas cambia un veredicto
  (el menor margen de G2 es 0.31 m; el mayor esviaje, 30°).
- **Qué haría falta:** el levantamiento del receptor y su cota de limpieza
  para el desnivel; la solución constructiva del cruce (cabezal esviado o
  terraplén alabeado) para el esviaje.
- **Dónde vive:** `src/modulos/M7_geometria.py::g3_esviaje`

## T6-04 · `bombeo` y `peralte` entran sólo por el JSON de datos externos, y sólo los lee el método por extremo

- **Qué se difirió:** las dos claves nuevas de `servicio.CLAVES_EXTERNAS` no
  tienen bandera en la CLI ni campo en la pestaña 1 de la GUI, como
  `S_conducto`. El método `terraplen_simetrico` no las lee aunque se
  declaren, ni una longitud declarada (`longitud_m`): el paso lo dice y sale
  un aviso. Son **excluyentes** en un mismo punto —una sección tiene bombeo
  (tangente, DG-2018 304.05) o peralte (curva, 304.06)— y declararlas a la
  vez es `DatoInvalidoError` sobre el par, también cuando una viene de
  `globales`; un punto en curva anula el bombeo global con `bombeo` = 0. Y
  su **ausencia** se avisa en cada punto, con lo que cada 1 % de bombeo
  acortaría la longitud.
- **Por qué:** son datos de la sección típica que afinan la longitud en
  décimas de metro (un bombeo de 2 % sobre 9.60 m de plataforma acorta 0.40
  m), no datos sin los que un punto no se dimensione; abrirles campo en la
  ventana ensancha la interfaz por un refinamiento. El peralte, además, no
  cambia la longitud —gira la plataforma alrededor del eje— y sólo mueve la
  altura de terraplén de cada extremo, que es lo que el cabezal por punto
  (T-7a) leerá de `LongitudConducto`.
- **Qué haría falta:** una petición de uso. La bandera y el campo son
  mecánicos: `CLAVE_EXTERNA_DE_CAMPO` de `src/sesion.py` y `CAMPOS_EXTERNOS`
  de `gui/app.py`.
- **Dónde vive:** `src/servicio.py::CLAVES_TRANSVERSALES`

## T6-05 · La fuente sostiene la superposición aproximada del barril; medir al fondo es elección del proyecto, y no es el lado seguro por construcción

- **Qué se difirió:** nada; es una atribución que el auditor adversarial de
  T-6 corrigió y que conviene poder releer. La primera redacción decía que
  bajar cada talud hasta el fondo del conducto era «lo que la fuente
  describe».
- **Por qué:** el HDS-5 2.2.4 b. sostiene la superposición **aproximada** del barril
  estimado; su Figura 2.4 dibuja los taludes muriendo en la cara superior
  del barril, y la Lámina Nº 01 a) del Manual, en la coronación de los
  cabezales. Medir **al fondo** —un barril de altura cero— es elección del
  proyecto y da la **cota superior** de la longitud; no es el lado seguro
  por construcción: en A-01 el HW de salida es 0.9925 m con la longitud al
  fondo y 1.0002 m con la longitud a la clave (alargar el conducto lo baja
  7.7 mm), sin consecuencia allí porque gobierna la entrada (1.042 m). Y la
  longitud a la clave es, a su vez, la cota **superior** de la longitud
  entre cabezales: un cabezal 0.30 m sobre la clave da 13.42 m en A-01.
  Con el fondo de entrada **adoptado** igual al terreno —la cota del
  terreno en el eje— el método ancla ahí la entrada y carga toda la caída
  aguas abajo: para un lecho que pasara por esa cota en el eje A-01 daría
  18.638 m, no 18.869; el paso 7.B.3 lo dice junto al aviso «medir en el
  cauce», y con el fondo medido es exacto.
- **Qué haría falta:** la coronación del cabezal por punto (T-7a), que
  convierte la cota superior en la longitud de construcción; o el fondo de
  entrada medido en el cauce, que quita el sesgo del eje.
- **Dónde vive:** `src/modulos/M7_geometria.py::longitud_del_conducto`
---

# Parte XLV — Lo que T-8 de la cadena T dejó escrito: la Fase 6 de entrada y salida, el apron de HEC-14 y la hoya de socavación

T-8 (2026-11-12) hace que la Fase 6 sea de verdad la protección de entrada y salida
(`INF-3.3.7`, `INF-5.1.13`). Laushey sigue rigiendo; lo nuevo va al lado. Cinco decisiones
no son un cierre limpio.

**Enmendada el 2026-11-12 por la segunda auditoría adversarial de T-8** (independiente, sobre
`df1b23c`: 0 bloqueantes, 2 altas, 4 medias, 8 bajas) **y por las seis decisiones que el dueño
tomó sobre ella**. Las fichas T8-01, T8-02, T8-04 y T8-05 llevan al pie lo que cambió; las
T8-07 a T8-12 son nuevas. Lo que ya no es cierto de la frase de arriba: desde esa fecha
**rige la envolvente** de Laushey y de HEC-14, no Laushey a secas.

## T8-01 · El apron de HEC-14 es contraste y no regla; el espesor adoptado queda siempre bajo su piso, y la decisión queda preparada

- **Cerrado (T-8):** `INF-3.3.7` en su parte de salida. Froude con el tirante equivalente
  (HEC-14 10.1.1) como parámetro y régimen por el tirante contra el crítico
  (`flujo_supercritico`, una regla para el Froude y la Ec. 10.5); apron por la Ec.
  (10.4)/(10.5) y la Tabla 10.1 con sus límites (circular, TW de 0.4D a 1.0D, alto de hasta
  1500 mm); la clase que toca a la piedra adoptada (paso 6.6b); aviso en todo punto de que
  1.75·d₅₀ queda bajo el piso de 2.0·D₅₀; la familia de Laushey frente al Apéndice D.
- **Abierto:** (1) **qué rige**: el d₅₀ del Manual llena `ProteccionSalida.d50`; el espesor y
  la longitud los decide el [A] `regla_espesor_longitud_proteccion_salida` (`manual`, la
  conducta de hoy; `envolvente_hec14` toma el mayor). Es decisión del dueño. (2) El `y_n` de
  la Ec. (10.5) es el de registro (n máximo). (3) Fuera: la poza (10.1), la Figura 10.3,
  los disipadores (Caps. 7–9) y el aliviadero de la Lámina N° 04.
- **Qué haría falta:** para (1), que el dueño elija la regla; para (2), publicar en M3 el
  tirante con n mínimo; para (3), el diseño del disipador en el expediente.
- **Enmendado (2026-11-12):** (1) está **decidido** —rige la envolvente, y alcanza a la
  piedra: ficha T8-07—. El límite de alto es **60 in = 1.524 m**, no 1500 mm: la nota 8
  de la Tabla 1.1 imprime las dos cifras, que no coinciden, y con 1.500 m el ejemplo
  resuelto de la propia fuente (D = 5.0 ft, pág. impresa 10-19) salía «no evaluable»
  (H5; `constantes_normativas.HEC14_APRON_ALTURA_MAX_M`). Los límites del TW aplicados al
  diámetro ajustado D′ son lectura del proyecto y están declarados como `Interpretacion`
  de la cita `HEC14.10.2#TW` (H6). Sin tirante de salida el régimen no se decide: el apron
  no ajusta y **lo avisa** (`ApronHEC14.regimen_determinado`; antes `bool(None)` lo resolvía
  en silencio, H15).
- **Dónde vive:** `src/modulos/M6_proteccion.py::apron_hec14`

## T8-02 · La Tabla N° 11 decide si se reviste la salida, y no revestir es lectura del proyecto

- **Cerrado (T-8):** con `tipo_terreno_receptor` y `regimen_flujo_descarga` declarados, la
  velocidad de salida se compara con la admisible: si no la supera, no hay enrocado
  (`requerida` False, d₅₀ en `None`) y se AVISA que esa inversa es lectura del proyecto, con
  la frase del HDS-5 5.3.2 (`citas.INTERPRETACION_SIN_ENROCADO`; el fundamento ya no
  obliga). El terreno se cruza con el lecho declarado y la incoherencia se avisa.
- **Abierto:** (1) en la **entrada** la comparación usa la velocidad en la boca del barril:
  extensión del proyecto, del lado alto. (2) El terreno es un [S] por punto y entra por
  `--datos-externos`, como la sección medida de T-2 (ficha T2-03), sin trazabilidad
  obligatoria: no cambia las 19 columnas del CSV. (3) La inspección de campo que el HDS-5
  pide para no revestir no es un dato del programa.
- **Qué haría falta:** para (1), la sección del cauce de aproximación; para (2), una
  decisión de producto sobre columnas opcionales con trazabilidad; para (3), el expediente.
- **Enmendado (2026-11-12):** el título de esta ficha **ya no es cierto**. Decisión 6 del
  dueño: «sin enrocado» no es nunca una conclusión del programa. La Tabla N° 11 **informa**
  (`requerida` True / False) y la protección se calcula y se mantiene siempre; con `False`
  la corrida avisa, con la frase del HDS-5, que suprimirla queda sujeto a inspección de
  campo. La cadena T pedía lo contrario (T-8 punto 1: «cálculo del d50 solo entonces») y
  se declara: lo sostienen la fuente (HDS-5 5.3.2) y el hallazgo H2, que midió que la
  conclusión «sin enrocado» salía con una velocidad que el propio programa avisaba como
  subestimada (ficha T8-08). Leer «alta» (núm. 4.1.1.3.7 c)) como «mayor que la Tabla N°
  11» es `Interpretacion` de la cita `MC_HHD.4.1.1.3.7c#PROTECCION`. Las tres celdas del
  CSV de resumen ya no quedan vacías en ese caso (H11).
- **Dónde vive:** `src/modulos/M6_proteccion.py::velocidad_admisible_del_cauce`

## T8-03 · La protección de entrada declara la clase de revestimiento y lo que se protege; ninguna fuente de `normas/` le da dimensiones

- **Cerrado (T-8):** `INF-5.1.13`. Criterio [A] `tipo_proteccion_entrada` con las tres
  clases del num. 4.1.1.3.7 c); velocidad en la boca de lo que M4 resolvió; lo que se
  protege por embocadura (lectura del proyecto sobre HDS-5 5.3.1).
- **Abierto:** la longitud y el espesor del zampeado, la uña y el dentellón: las Láminas
  02, 02-A y 03 los traen como letras o «VARIABLE». La embocadura es la adoptada para todo
  el proyecto (`EMBOCADURA_CABEZAL_RECTO`); T-7a pasará la de cada punto.
- **Qué haría falta:** T-7a punto 5 (geometría del zampeado y del dentellón como parte de
  `GeometriaCabezal`) y pasar su embocadura a `proteccion_entrada`.
- **Dónde vive:** `src/modulos/M6_proteccion.py::EMBOCADURAS`

## T8-04 · La hoya de socavación es HEC-14 Cap. 5 y no el 3; la duración y la referencia de hs las declara el proyecto

- **Cerrado (T-8):** la Ec. (5.1) o (5.2)–(5.4) con sus dos ejemplos resueltos, entregada al
  desplante (`socavacion_salida`, para T-7a; HEC-14 5.1.3), con la cota del fondo de la hoya.
  La declarada gana. Sin la duración rige el [C] de 30 min, extremo no conservador: se avisa
  con la profundidad a 360 min. Con menos de 30 min, cota superior con 30. Un IP fuera de
  5–16 (también 0) avisa y no bloquea.
- **Abierto:** (1) el lecho es dato del EMS y la línea base no lo trae. (2) HEC-14 Cap. 5
  no dice desde qué cota se mide hs: el [A] `referencia_profundidad_socavacion` toma el
  fondo del cauce (conservador; ~0.7 m más abajo que la solera en A-01). (3) La lectura
  entre filas es [A]. (4) La degradación general (Cap. 2) no está incluida.
- **Qué haría falta:** el EMS del lecho por punto o un estudio del cauce declarado como
  `profundidad_socavacion_estimada_m` desde la misma referencia; T-7a para el desplante.
- **Enmendado (2026-11-12):** decisión 3 del dueño: sin hidrograma la hoya se estima con
  **360 min** y el criterio `duracion_caudal_pico_socavacion_min` pasa de [C] a **[A]**
  (ventana 30–360; 30, lo que la fuente recomienda, queda barrible). La razón es el
  literal de la frase siguiente a la recomendación, ahora citado
  (`HEC14.5.1.2#DOS_TERCIOS`): a los 30 minutos se alcanza de 2/3 a 3/4 de la hoya máxima,
  y esa profundidad fija el desplante de un cabezal. **Lo que la fuente no sostiene y se
  dice:** el techo de 360 min no sale de HEC-14, que no da duración máxima; es adopción
  del proyecto. Sensibilidad medida en los dos puntos del fixture que dimensionan, con un
  lecho declarado (la línea base no lo trae, así que ninguno de sus números se mueve):
  arena (D84 = 0.5 mm, D16 = 0.08 mm), A-01 1.196 → 1.389 m y A-02 0.846 → 0.982 m (×1.161);
  grava (30 y 2 mm), 1.034 → 1.200 m y 0.731 → 0.849 m; cohesivo (IP 12, Sv 24 kPa),
  2.087 → 2.676 m y 2.009 → 2.576 m (×1.282, θ = 0.10). La referencia de hs de la Figura
  10.1 se apoya ahora en su propia cita, `HEC14.10.1#HS` (H9; antes en `#DOS_D50`, cuyo
  literal habla del espesor). Y «manda» pasó a «recomienda» (H8).
- **Dónde vive:** `src/modulos/M6_proteccion.py::socavacion_salida`

## T8-05 · El filtro es un requisito declarado; EG-2013 no lo obliga, y su nota (5) vale para la fila

- **Cerrado (T-8):** el filtro se declara (Lámina N° 05, HEC-14) y, con el pasante del
  tamiz N° 200, se elige la columna de la Tabla 511-06 de EG-2013. La nota (5) la llama el
  rótulo de la fila: (5) b lleva la abertura a 0.30 mm con un lecho cohesivo de IP > 7 en
  las tres columnas, y (5) a se avisa con un lecho no cohesivo de más de la mitad de finos
  (un limo en SUCS: lectura del proyecto).
- **Abierto:** EG-2013 511.08 especifica el geotextil cuando se pone; no obliga a ponerlo,
  de modo que el requisito no es [N]. El filtro granular no se diseña: HEC 11 no está en
  `normas/`. Y sin el pasante del EMS no se elige columna.
- **Qué haría falta:** HEC 11 o una norma peruana de filtros; el pasante por punto.
- **Enmendado (2026-11-12):** «su nota (5) vale para la fila» **se retira** (H4, decisión 4
  del dueño): ver la ficha T8-10.
- **Dónde vive:** `src/modulos/M6_proteccion.py::requisito_de_filtro`

## T8-06 · La aceptación de T-8 se escribió después del código; el rojo se midió contra la base y la mutación de M6 se midió con el arnés

- **Qué se difirió:** el orden de la casa (rojo con `xfail(strict=True)` y liberar). El
  prompt se retomó a medias de otra sesión, con el código ya escrito.
- **Por qué:** se dice en vez de reconstruirlo. Medido contra `ad5cb97` con marcadores
  para los nombres que no existían: 57 rojos, 5 errores y 1 verde (la guardia de las tres
  advertencias, que vale antes y después). Los tests de validación de la carga miden el
  MOTIVO: con sólo la clave pasaban vacuos en la base, que rechazaba las claves por
  desconocidas. Los oráculos son los ejemplos resueltos de HEC-14 y la aritmética escrita.
- **Qué haría falta:** nada que se pueda rehacer. Mutación con el arnés de EXT-11 sobre
  M6 entero contra `tests/test_t8_proteccion.py`, en dos momentos. Antes del auditor
  adversarial (375 mutantes): 296 muertos en la primera medida y 337 (89.9 %) tras los
  tests que enseñó. Sobre el M6 final, ya con las correcciones del auditor y fusionado con
  T-6 (514 mutantes): 448 muertos (87.2 %) en la primera medida —el código nuevo del
  auditor tenía avisos sin texto comprobado— y **472 (91.8 %)** tras endurecer las
  aserciones de los tests existentes, sin sumar tests. De los 42 vivos, 35 son de banda de
  tolerancia (`TOL_UMBRAL_NORMATIVO`, `>` frente a `>=`), tres equivalentes (el
  `or`/`and` del cruce del terreno con el lecho, donde con un dato ausente ninguna fila
  coincide, y dos en `coeficiente_de_tabla`), dos de la guardia de salida de la hoya, que
  ningún dato válido alcanza, y dos de presentación (las cifras de ρ en la sustitución y
  la nota vacía frente a `None`). No se censan uno a uno: ampliar el censo es de T-10.
- **Dónde vive:** `tests/test_t8_proteccion.py::test_hec14_la_socavacion_es_el_capitulo_5_y_el_apron_el_10`

## T8-07 · Rige la envolvente de Laushey y de HEC-14, y alcanza al tamaño de la piedra; fuera de la Tabla 10.1 son cotas inferiores

- **Cerrado (pasada de correcciones):** `regla_espesor_longitud_proteccion_salida` vale `envolvente_hec14`
  (decisión 1 del dueño, 2026-11-12). Piedra = el mayor del d₅₀ de Laushey y del D₅₀ de la
  Ec. (10.4); espesor y longitud = los mayores de lo adoptado y de los que la Tabla 10.1 da
  a esa piedra. `manual` reproduce los números anteriores y queda barrible; donde HEC-14 no
  es evaluable rige Laushey con lo adoptado, con aviso.
- **Por qué:** el hallazgo H1. Con la regla de T-8 la envolvente subía espesor y longitud y
  dejaba la piedra de Laushey, y además **callaba** los dos avisos que hablaban del tamaño:
  en una descarga llena de Ø 0.90 m con 1.15 m³/s salía una capa de 0.60 m hecha con piedra
  de 0.108 m, rotulada «rige la envolvente con HEC-14» cuando HEC-14 pedía 0.168 m. Y no es
  un caso raro: a sección llena y con TW = 0.4D, `D50(HEC-14)/d50(Laushey) =
  2.04·(D^2.5/Q)^(2/3)`, mayor que 1 siempre que `Q/D^2.5 < 2.9`.
- **Qué cubre y qué no:** la clave conserva su nombre («espesor_longitud») aunque gobierna
  también la piedra —está en sesiones, barridos y la línea base—; el concepto de la ficha
  lo dice. Los avisos del contraste salen bajo las dos reglas (con la envolvente callan
  solos, porque lo que rige no queda por debajo). **No cubre** el caso en que la piedra que
  rige no cabe en la Tabla 10.1 (más de 0.55 m): la tabla, que es un *ejemplo*, no da ni
  profundidad ni longitud, y el programa imprime **cotas inferiores** —2.0 veces el d₅₀, el
  límite que la fuente escribe para las piedras mayores, y 8D, la longitud de su última
  clase—, que son **lectura del proyecto**, y avisa que la salida pide un disipador.
- **Qué se movió en la línea base (aprobado):** el d₅₀ no (en A-01 y A-02 rige Laushey:
  0.338 y 0.274 m, mayores que lo que pide la Ec. 10.4); el espesor, de 0.592 y 0.479 m a
  **0.770 m**, y la longitud, de 5.00 a **5.40 m**: los de la clase 4 (D₅₀ = 0.35 m) de la
  Tabla 10.1, `2.2·0.35` y `6·0.90`. Ningún diámetro ni material.
- **Qué haría falta:** para el caso fuera de tabla, el diseño de un disipador por HEC-14
  (Caps. 7 a 10), que el programa no implementa.
- **Dónde vive:** `src/modulos/M6_proteccion.py::_regla_de_la_proteccion`

## T8-08 · El tirante de borde no está digitalizado: con la velocidad al crítico el contraste con la Tabla N° 11 no concluye

- **Cerrado (validacion/T8-08, 2026-11-18, trabajo posterior a la cadena, README §8):** las
  Figuras 3.3 y 3.4 de HEC-14 (págs. impresas 3-5 y 3-6, PDF 36 y 37) son las tablas
  `HEC14.F3_3` y `HEC14.F3_4` del registro, leídas por imagen con la tolerancia
  `TOL_LECTURA_FIGURA_HEC14` = 0.01 en yo/D (método y contraste en la nota de las citas
  `HEC14.F3.3` y `HEC14.F3.4`: los tres anclajes de esta ficha, 0.323 / 0.467 / 0.572, dan
  0.322 / 0.466 / 0.570, y el ejemplo de la pág. 3-4 se reproduce a ±0.006). En la primera
  viñeta de `velocidad_de_salida` el área es la del borde (`tirante_de_borde`); el tirante
  de registro sigue siendo el crítico. El caso del auditor (A-02 horizontal sobre grava,
  1.739 m/s al crítico) da 2.08 m/s y el contraste concluye.
- **Abierto:** donde la figura no da lectura —otra forma (la fuente acepta el crítico, «not
  conservative, but is acceptable»), fuera de la familia de curvas, o una lectura que no
  queda bajo el crítico (las curvas de trazo discontinuo de la 3.4, que lo contradicen
  arriba)— la velocidad sigue al crítico, `V_salida_cota_inferior` y el contraste no
  concluye (`ALCANCE_DECLARADO`, clave `tirante_de_borde_hec14`). La interpolación entre
  curvas y entre líneas de la retícula es lineal: lectura del proyecto, declarada en el
  paso 4.3b.
- **Qué haría falta:** para lo abierto, las curvas de Simons (1970) en otra fuente o una
  figura de mayor resolución; nada para el resto.
- **Dónde vive:** `src/modulos/M4_control.py::tirante_de_borde`

## T8-09 · La velocidad de salida salta en la banda en que n máximo da flujo subcrítico y n mínimo lo daría supercrítico: es de M4 y sólo se avisa

- **Cerrado (validacion/T8-09, 2026-11-18, decisión del dueño: la regla del máximo):** en la
  primera viñeta, si con n mínimo el tirante normal es supercrítico,
  `V_salida = max(V_borde o V_crítica, V_erosion)`, y la procedencia nombra las dos. El
  aviso `_aviso_banda_de_regimen` de M6 se retiró. V3 sigue juzgando la mayor de
  `V_erosion` y `V_salida` (VE-3.1), sin duplicar nada. Con n máximo también supercrítico
  la figura no aplica («Horizontal and Mild Slopes») y rige `V_erosion`.
- **Abierto:** el antes/después que esta ficha escribía (d₅₀ 0.191 → 0.319 m) era con la
  `V_erosion` anterior a VE-2 (3.114 m/s); hoy es 2.960 m/s (d₅₀ 0.288 m) y, con el borde
  de T8-08 (3.110 m/s), A-01 con S = 0.0056 sale con d₅₀ 0.318 m: gana el borde. La regla
  sólo actúa en la primera viñeta; con el TW entre el crítico y la clave no se aplica.
- **Qué haría falta:** nada para la regla; el HDS-5 no trata la doble n.
- **Dónde vive:** `src/modulos/M4_control.py::velocidad_de_salida`

## T8-10 · La nota (5) b de la Tabla 511-06 se lee sólo para la columna «>50», y las filas «arcilla (no coloidal)» de la Tabla N° 11 se clasifican por su nombre: dos lecturas que esperan una fuente

- **Cerrado (pasada de correcciones):** decisión 4 del dueño: la lectura que **no relaja**, declarada como
  `Interpretacion`, hasta conseguir AASHTO M 288. La Tabla 511-06 lleva «(5)» en el rótulo
  de la fila y en la celda «0,22(5)», y dos notas, (5) a y (5) b; la lectura de T-8 (la del
  primer auditor) las aplicaba a las tres columnas, y en «15-50» eso **abría** la abertura
  de 0.25 a 0.30 mm para una arena arcillosa (H4).
- **Por qué:** lo sostiene la propia fuente. La **Tabla 511-02** de la misma Sección
  (subdrenaje, pág. impresa 1011, PDF 1019) trae la misma fila, las mismas tres celdas y
  las mismas dos notas **numeradas por separado**: el rótulo lleva «(3) (4)» —la (4) es el
  diseño específico— y sólo la celda «0,22 (5)» lleva la de los suelos cohesivos (cita
  `EG2013.511.05#T511_02_NOTA_5`, leída por texto y por imagen). De ahí: el rótulo llama a
  la (5) a y la celda a la (5) b.
- **Abierto:** (1) el «(5)» sin letra del rótulo de la 511-06 admite la otra
  lectura; en la columna «<15» esa otra daría 0.30 mm en vez de 0.43 —más cerrada—, y la
  corrida **lo avisa**. (2) Aparte, la Tabla N° 11 declara al pie «Manual de Carreteras de
  California» y sus filas «Arcilla arenosa / limosa (no coloidal)» podrían ser francos
  («loam») traducidos como arcilla: `TERRENOS_COHESIVOS_T11` las clasifica por el nombre
  impreso y sólo alimentan el aviso de incoherencia entre terreno y lecho, que pide revisar
  los dos datos sin afirmar cuál está mal.
- **Qué haría falta:** AASHTO M 288 y el manual de California en el repositorio de normas
  (`docs/contrato_entradas.md`, §6).
- **Dónde vive:** `src/normativa/citas.py::INTERPRETACION_NOTA_5_T511_06`

## T8-11 · Lo que la segunda auditoría pidió y no se hizo: techos físicos para los datos de la Fase 6, y la cadena numérica en el JSON

- **Qué se difirió:** el hallazgo H12. Entran sin techo `duracion_caudal_pico_min` = 1e9,
  `profundidad_socavacion_estimada_m` = 1e6, `Sv_Pa` = 1e300 y `D84_m` = 5.0; y las dos
  claves numéricas admiten la cadena `"1.0"` por `_numero_externo`, mientras que dentro de
  `material_lecho_salida` una cadena se rechaza.
- **Por qué no se pusieron techos:** porque ninguna fuente de `normas/` los da, y este
  proyecto no los inventa. Es la regla escrita en `CLAUDE.md` («No se corrige poniendo
  techos en dominios.py») y aplicada en `servicio._DOMINIO_DE_CLAVE`, cuyo comentario
  dice de `TW_m` y `L_hidraulico_m` lo mismo: «sin techo en `dominios.py` y sin ninguno
  que derivar. Inventar uno está prohibido». HEC-14 Cap. 5 no limita `Sv`, ni la
  duración, ni el tamaño del lecho (se releyeron las págs. 5-1 a 5-7). Los cuatro valores
  son absurdos y **ninguno rompe**: dan un número finito, y la guardia de salida de la
  hoya (`LimiteNumericoError`, que desde esta pasada nombra al par culpable de verdad,
  H10-b) atrapa lo que desborda.
- **Por qué no se tocó la cadena:** `_numero_externo` acepta `"1.0"` para **todas** las
  claves numéricas desde EXT-1, no sólo para las dos de T-8; endurecerlo es de esa puerta
  entera y de sus tests, no de la Fase 6.
- **Qué haría falta:** una decisión de producto sobre «techos de transcripción» —como el
  `S_CAUCE_MAX` que atrapa una pendiente escrita en porcentaje—: un `D84_m` de 5.0 huele a
  milímetros escritos como metros. Sería un aviso, no un rechazo, y necesita un criterio
  que diga dónde está el umbral.
- **Dónde vive:** `src/servicio.py::_DOMINIO_DE_CLAVE`

## T8-12 · La pasada de correcciones: el rojo se escribió primero y se remidió, y las decisiones del dueño llegaron por el orquestador

- **Qué se difirió:** el orden estricto de la casa para una parte de la pasada. Los tests
  de H1 a H15 se escribieron con `xfail(strict=True)` antes de tocar el código; con la
  pasada a medias llegaron las seis decisiones del dueño (2026-11-12), que cambiaron lo que
  debían afirmar los de H1, H2, H11 y D3, y ésos se reescribieron con el código en marcha.
- **Por qué:** se dice en vez de reconstruirlo. El rojo que vale es el **medido**:
  `tests/test_t8_correcciones.py` final contra un árbol exportado de `df1b23c` (el de
  T-8): **43 rojos y 20 verdes** de 63. Los verdes son guardias que valen antes y después —los seis bordes inclusivos
  de la fuente que la ficha T8-06 agrupaba como «banda de tolerancia» (IP = 5 y 16, Hd = 4,
  TW = 1.0·D, espesor = 2.0·d₅₀, la clase «mayor o igual», V = V admisible), ahora con un
  test cada uno, y la transcripción entera de las Tablas N° 11, 5.1, 5.2, 5.3 y 5.4 (H13)—.
- **Lo que hay que saber de las decisiones:** las recibió el agente por la sesión
  orquestadora (`DECISIONES_DUENO_2026-11-12.md`), no directamente del dueño. Una premisa
  de la decisión 3 no la sostiene el literal y se dijo en vez de aplicarla a ciegas: «la
  ventana 30–360 que la fuente sostiene» —la fuente sostiene el piso de 30 min y la razón
  para no quedarse en él («2/3 to 3/4»), no el techo de 360, que es adopción del proyecto—.
  La decisión se aplicó (360 min, [A]) y la ficha del criterio lo declara.
- **Qué haría falta:** nada que se pueda rehacer. La mutación de M6 se **remidió** con el
  arnés de EXT-11 sobre el M6 de esta pasada, contra los dos archivos
  (`tests/test_t8_proteccion.py` y `tests/test_t8_correcciones.py`): 574 mutantes, **531
  muertos (92.5 %)** en la medida entera. De los 43 vivos, cinco eran huecos del código
  nuevo —la procedencia del diámetro y del TW en el paso 6.5, la lectura que sólo se imprime
  en la salida, y la longitud `8·D` de fuera de tabla, que con D = 1 m no se distinguía de
  `8/D`— y se cerraron con aserciones: remedidas sólo las tres funciones tocadas (90
  mutantes, 82 muertos), el total queda en **536 de 574 (93.4 %)**, sumando una medida
  entera y una parcial, y se dice así. Los 38 que quedan son de banda de tolerancia
  (`±TOL_UMBRAL_NORMATIVO`, `<` frente a `<=`, que sólo difieren a 1e-9 del borde y cuyo
  comportamiento EN el borde sí está fijado por test desde esta pasada), los tres
  equivalentes de la ficha T8-06 y los de presentación; no se censan uno a uno (T-10).
- **Dónde vive:** `tests/test_t8_correcciones.py::test_manual_sigue_dando_exactamente_los_numeros_de_antes`

---

# Parte XLVI — Lo que T-5 de la cadena T dejó escrito: la Fase 8 real del conducto

T-5 (2026-11-12) cerró `INF-3.3.5` (el «5.1.5 Fase 8 no verifica nada» de la cadena; el
`INF-5.1.5` canónico es la mezcla de marcos del cabezal, de T-7b). Estas fichas
registran lo que quedó **decidido con argumento** o **abierto con nombre**. Las nueve
primeras son de la FASE A; **dos auditorías adversariales independientes** la
encontraron AJUSTADA, y el dueño del proyecto decidió el mismo día las siete preguntas
que dejaban abiertas: las fichas `T5-10` a `T5-14` son del cierre, y las nueve primeras
se corrigieron donde las auditorías las desmintieron (cada una lo dice).

## T5-01 · La Fase 8 que decide si el escalón existe corre a nivel de perfil, detrás de V9 y solo si todo lo anterior cumple

- **Qué se difirió:** a nivel de perfil, la cama de apoyo (ítem 4) y la demanda
  del marco; el diseño del pórtico, en los dos alcances.
- **Por qué:** la v8 difería el ítem 5 entero al expediente, y T4-08 dejó dicho
  que la plancha adoptada del TMC no cumple el factor de flexibilidad desde
  ~1.39 m: una corrida de perfil que aceptara ese escalón aceptaría un tubo que
  no existe. Por eso lo que decide la **existencia** —la clase del concreto, el
  calibre del TMC, el perfil del HDPE— entra a la tabla de la Fase 5 como
  verificaciones `F8.*` (`M5.fase_8_estructural`), igual que V7, que ya es
  Fase 8. Corren **solo si todo lo anterior cumple**: un escalón que incumple
  una V se rechaza igual, y evaluarle la Fase 8 dejaría que un dato estructural
  que falta (una clase de M 170M sin transcribir) tapara el incumplimiento que
  de verdad lo descarta (lo de B-01, que incumple V2 en todo diámetro). La
  consecuencia: la memoria de un escalón rechazado por una V no imprime su
  Fase 8. La etapa `servicio._fase_8_conducto` vuelve a llamar a la misma
  función sobre la sección aceptada para quedarse con lo que no es una
  verificación (pasos de carga, relleno máximo, avisos) en
  `InformePunto.estructural`. El relleno máximo se busca por el PRIMER cruce
  del margen (muestreo de `TRAMOS_BUSQUEDA_RELLENO_MAXIMO` tramos y Brent),
  porque la carga viva decrece con la profundidad mientras la de tierra crece
  —y, si el proyecto declara tomar el permiso de 3.6.1.2.6a (T5-11), se
  desprecia de golpe a 8 ft—: el margen no es monótono.
- **Qué haría falta:** nada para el perfil. Para el expediente, el diseño del
  pórtico (T5-07).
- **Dónde vive:** `src/modulos/M5_verificaciones.py::fase_8_estructural`

## T5-02 · De M 170M solo se lee la D-load de la Clase II, y un tubo que pida más BLOQUEA el punto

- **Qué se difirió:** las D-load de 0.3 mm de las Clases I, III, IV y V.
- **Por qué:** el ejemplar de AASHTO M 170M-04 de `normas/` es una recomposición
  OCR con dígitos equivocados; leído página por página y por imagen —por la FASE A
  y otra vez por los dos auditores—, solo la D-load de 0.3 mm de la Clase II es
  legible (50.0 N/m/mm, Tabla 2, pág. M 170M-5, cita `AASHTO_M170M.T2#DLOAD`).
  Ninguna otra se completa de memoria: si la D-load requerida supera la de la
  mayor clase transcrita, la Fase 8 levanta `DatoFaltanteError` sobre
  `'clases_producto_por_relleno'` nombrando **las clases que la norma tabula para
  ese diámetro y faltan** y lo que lo destraba. **Es decisión del dueño del
  proyecto (2026-11-12) BLOQUEAR**: la solución de un tubo que pide más que la
  Clase II es una clase superior, no un tubo mayor para esquivarla. La versión
  anterior de esta ficha lo justificaba con «subir de diámetro no lo resuelve (W_E
  crece con B_c y S_i con D)», y **es falso en general** (auditoría): con 0.50 m de
  relleno la D-load baja al crecer el diámetro —52.2, 41.7 y 36.0 N/m/mm en 0.90,
  1.20 y 1.50 m—; solo sube con relleno profundo. Tres cosas más del cierre: la
  clase no se ofrece por debajo del primer diámetro que la norma le tabula
  (`DIAMETRO_MIN_TABULADO_POR_CLASE_M170M_MM`: la Clase I desde 1500 mm; sin eso,
  completar el criterio hacía que un tubo de 0.90 m saliera «Clase I»); con las
  clases superiores todas transcritas, un tubo que no alcanza **no cumple**
  (`cumple=False` frente a la mayor) en vez de pedir un dato que ya no falta; y
  una clave que no sea una de las cinco clases es `DatoInvalidoError`. En el
  expediente de referencia no se alcanza: A-01 y A-02 piden 37.4 y 37.0 N/m/mm
  con el Tipo 3, y su relleno máximo con la Clase II es **2.85 m** (3.18 m en la
  FASE A, que despreciaba la carga viva pasados 8 ft: T5-11).
- **Qué haría falta:** un ejemplar legible de M 170M (la vigente) o de ASTM C76M
  —**entrada que debe conseguir el dueño**: `docs/contrato_entradas.md`— y añadir
  sus filas al dict del criterio.
- **Dónde vive:** `src/modulos/M8_estructural.py::clases_de_concreto_para`

## T5-03 · El TMC sube de plancha dentro de su corrugación, la Tabla 507-01 del EG-2013 pone el piso, y la plancha elegida no se devuelve a la geometría

- **Qué se difirió:** devolver a la geometría la plancha que la Fase 8 elige; la costura
  **empernada**.
- **Por qué:** la progresión recorre las planchas de la corrugación adoptada desde el mayor
  de la adoptada y del mínimo de la Tabla 507-01 (cita `EG2013.T507-01`; entre dos filas,
  la superior; sobre 1.80 m manda el cálculo), sólo las que la fabricación declarada hace
  (ASTM A796 Tabla 5: «. . .» donde no se fabrica). La empernada no tiene tabla para 68×13
  en ninguna fuente del repositorio (A796 Tablas 5 y 7 y AASHTO A12-7 son de remaches):
  declararla detiene la Fase 8 pidiendo la resistencia del fabricante. El archivo trae la
  remachada simple, la más débil de las tabuladas (decisión del dueño, 2026-11-12). El
  EG-2013 507.02 a) describe tubería **empernada** (cita `EG2013.507.02#EMPERNADA`, que
  desmintió la frase anterior de esta ficha), y por eso un `F8.COSTURA` que cumple con la
  remachada se avisa siempre (`AVISO_COSTURA_DE_OTRA_FABRICACION`). La progresión no cambia
  sola la fabricación, que es una elección declarada.
- **Cerrado por VE-5 (m8, ítem 23 del censo):** la plancha elegida vuelve a la geometría
  (`Material.plancha_tmc`, `M2.material_con_plancha_tmc`); MD re-verifica el escalón con la
  plancha de `M8.plancha_requerida_tmc` y adopta el punto con ella; el escalón siguiente
  parte de la adoptada. El aviso «Declare la plancha requerida» queda para la llamada suelta.
- **Qué haría falta:** la resistencia de costura empernada del producto que se
  especifique.
- **Dónde vive:** `src/modulos/M8_estructural.py::verificar_tmc`

## T5-04 · El TMC rige por LRFD y A796 es solo contraste: el expediente de referencia «VARIOS» se reproduce, y su H-20 no es el HL-93

- **Qué se difirió:** nada; se declara el marco de cada número.
- **Por qué:** AASHTO LRFD 12.7.2 es de factores de carga y resistencia (γ_EV
  1.95 de la fila flexible de la Tabla 2.4.5.3.1-2, γ_LL 1.75, φ de la Tabla
  12.5.5-1, η de 12.5.4); ASTM A796 núm. 8 es de tensiones admisibles (SF = 2,
  f_y 225 MPa). Mezclarlos —un γ de LRFD con un FS de A796— es la incoherencia
  que la Sec. 0.2 prohíbe, y no ocurre: el FS solo vive en
  `M8.area_requerida_asd_a796`, que imprime un paso rotulado «NO RIGE»
  (fijado por AST en `tests/test_t5_estructural_conducto.py`). La presión de
  clave que 12.7.2.2 toma de 12.12.3.4 se lee como la de campo libre a la cota
  de la clave, sin el K_γE del termoplástico (C12.7.2.2; es la misma que A796
  núm. 9.1 mayora con 1.95). Con los datos de «VARIOS» (D 0.90 m, DL 4.5 kPa,
  LL 86 kPa H-20; **según el INFORME §1.1**, las páginas del PDF original no se
  verificaron en esta sesión) el contraste da C = 40.725 kN/m y A = 0.354 mm²/mm
  con f_y = 230 MPa, que es el redondeo del expediente; con el 225 de A796-13,
  0.362 (+2.2 %). Su D/r = 207 es el de la plancha de 1.63 mm y el pandeo no
  gobierna. Su FF de 0.109 mm/N **no se reproduce** con las inercias de la
  Tabla 5 de A796 (0.131 con 1.63 mm, 0.103 con 2.01): usa otra tabla de
  propiedades; los dos lados quedan bajo el límite de 0.245. Y la H-20 de A796 6.2.2.1 (86.2 kPa a 1 ft, con impacto) **no
  se compara** con el HL-93: a 1 ft el método de 3.6.1.2.6 ni siquiera aplica a
  un flexible, y apenas por encima (0.31 m) el HL-93 da más del doble.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M8_estructural.py::area_requerida_asd_a796`

## T5-05 · El HDPE se calcula con tres lecturas declaradas, y sin el perfil del fabricante no tiene veredicto

- **Qué se difirió:** la deformación combinada de flexión y empuje
  (12.12.3.10.2) y el pandeo local por elementos del perfil (12.12.3.10.1b),
  que necesitan la geometría idealizada del perfil.
- **Por qué:** sin esa geometría, el área efectiva sale del **mínimo de producto**
  que M 294 núm. 7.7 exige al ensayo de compresión (traducción no oficial):
  A_eff = 0.5 A_g F_u,ini K_t / F_u por la Eq. 12.12.3.10.1b-5 (0.45 A_g inicial,
  0.417 A_g a 75 años). **La deformación de empuje se suma por duración** (lectura
  de la definición de E_p en 12.12.3.10.1c): la de las cargas permanentes con las
  propiedades de largo plazo, la de la carga viva con las iniciales; el pandeo
  general **no** se suma así desde el cierre (T5-13). En 42 y 48 in la llamada
  «*» de la Tabla A12-11 lleva también la carga viva al largo plazo. R = (D +
  D_o)/4 a falta del centroide. El ν del suelo (0.40) **no tiene fuente**.
  **Lo que la FASE A no decía, y las dos auditorías midieron:** con su relleno
  por defecto (`Cl-95`) y el perfil mínimo de la Tabla A12-11, el HDPE de 900 a
  1200 mm **no cumple a ninguna altura de relleno**; la ficha decía solo que «el
  de 0.90 m de A-01 no cumple». Dos causas: (a) **el relleno**: `Cl-95` se
  justificaba con «cualquier material apto para terraplén» y omitía el EG-2013
  **508.02 d)**, que manda la cama y la sujeción lateral de material **granular**
  de la Sección 301 (finos de 5 a 25 %, IP de 4 a 9): el valor de archivo pasa a
  `Si-95`, la columna menos favorable de las que corresponden a ese material
  (cita `EG2013.508.02#GRANULAR`, con su `Interpretacion`), y `Cl-95` queda en la
  ventana como cota conservadora; (b) **el perfil**: T5-10. Con `Si-95` y el
  perfil mínimo de 36 in, el de 0.90 m de A-01 da ε = 0.0356 ≤ 0.041, u = 0.194
  ≤ 0.70, 3.5 % ≤ 5 % y FF = 0.422 ≤ 0.542 mm/N (el factor de flexibilidad de
  12.12.3.6 no se verificaba), con 1.48 m de relleno máximo. No mueve la línea
  base: el concreto cierra antes.
- **Qué haría falta:** la geometría idealizada del perfil del fabricante o el
  ensayo T 341 para el área efectiva, y el ν del ensayo del relleno.
- **Dónde vive:** `src/modulos/M8_estructural.py::_evaluar_hdpe`

## T5-06 · La carga viva HL-93 atraviesa el relleno por 3.6.1.2.6, y los pesos que cargan no son los que estabilizan

- **Qué se difirió:** la distribución para relleno somero (4.6.2.10) y el
  análisis «more comprehensive» por debajo de 1 ft.
- **Por qué:** el HL-93 (32.0 kip el eje del camión, 25.0 kip el tándem), la
  presencia múltiple de un carril (1.20) y el IM de componentes enterrados
  (33 (1 − 0.125 D_E) %, D_E en pies) son del Manual de Puentes [N]; la
  distribución por el relleno no la trae el Manual —su 2.4.3.2.2 pasa del área
  de contacto de los neumáticos (3.6.1.2.5 AASHTO) a la presencia múltiple, y
  ninguna sección del ejemplar remite a 3.6.1.2.6: buscado en el texto
  extraído— y se toma de AASHTO LRFD 3.6.1.2.6 [C], con tráfico paralelo al
  vano y un carril (el de casi toda
  alcantarilla vial, C3.6.1.2.6b). **GOBIERNA EL VEHÍCULO DE MAYOR EFECTO, no el
  de mayor presión** (auditoría: la FASE A elegía por presión, y su test
  repetía la misma regla): lo que carga al conducto es P_L por el largo del
  área cargada que cae sobre él, y con poco relleno y luz grande el tándem da
  menos presión sobre un área más larga y carga más —en el tubo de concreto de
  2.10 m con 0.47 m de relleno, 102.4 kN/m contra 65.5, y la D-load 38.7 contra
  30.7 N/m/mm—; cada consumidor pasa su medida (`efecto=`: W_L el concreto, P_L
  C_L F_1 los flexibles, P_L el marco, que la aplica a toda la luz). La «cubierta de tierra» D_E del IM se toma
  como el relleno SIN el paquete estructural (subrasante menos clave), que da
  el IM mayor; la profundidad que distribuye la carga sí llega a la rasante.
  Fuera de su dominio (menos de 2.0 ft sobre
  concreto o marco, 1.0 ft o menos sobre un flexible) la Fase 8 se detiene con
  `MetodoNoEvaluableError` (rótulo `MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL`),
  diferido a nivel de perfil como V1/V2. W_L = P_L min(l_w, B_c) sobre el tubo
  de concreto es lectura del proyecto. **Los pesos**: el relleno carga con el
  mayor de `'peso_especifico_relleno_kn_m3'` [A] (17.0, el extremo bajo porque
  en V7 estabiliza), del 0.120 kcf que el Manual permite usar a falta de
  información precisa (Tabla 2.4.2.1-1) y, en el concreto, del piso de 110
  lb/ft³ de 12.10.2.1; el paquete pesa 0.140 kcf. El agua llega al menos a la
  clave (la hipótesis de V7) o al NF del punto medido desde la cota de terreno
  si queda más alto; el suelo pesa húmedo también bajo el agua (cota superior).
- **Qué haría falta:** implementar 4.6.2.10 si el corredor tuviera rellenos de
  menos de 2 ft.
- **Dónde vive:** `src/modulos/M8_estructural.py::carga_viva_enterrada`

## T5-07 · Del marco se calcula la demanda, y el pórtico se difiere

- **Cerrado en lo principal (VE-5, lote m8, ítem 1 del censo):** el pórtico del marco
  se analiza y se arma a expediente (etapa `servicio.ETAPA_PORTICO_MARCO`): rigidez
  directa exacta de una o varias celdas, contrastada con la solución cerrada y con MnDOT
  LRFD BDM §12.5 (Tabla 12.5.2, dentro del 3.5 %); cargas de 12.11.2 con el empuje en
  REPOSO (3.11.5.2, `phi_relleno_trasdos`), LS por analogía con la Tabla 3.11.6.4-1, agua
  interior y la carga viva movida por la losa; las tres combinaciones de C12.11.2.1 con y
  sin LS, y el 50 % de 3.11.7 sólo en el positivo de la losa superior (decisiones del
  dueño); armado de cada cara traccionada con `M9.diseno_flexion_corte` y los φ del cajón
  vaciado in situ (Tabla 12.5.5-1). Sus verificaciones cuentan en el punto. El empuje
  lateral queda cerrado. Las lecturas del proyecto están en el docstring del símbolo.
- **Abierto:** lo que lista `M8.DIFERIDO_PORTICO`. El principal: los cantos separados
  existen en `GeometriaPortico` pero no en la geometría del programa (M2/M5/M7 forman la
  clave con `espesor_pared_cajon`), y el pórtico no itera el canto: con 0.20 m y el
  recubrimiento de la cota más exigente la losa de A-01 no cumple A1. Los pasos del armado
  llevan los fundamentos F9.ARM_* (rótulo «Fase 9»). Decisiones pendientes de Fable (sin
  subagentes en la sesión): reutilizar para el marco `phi_relleno_trasdos` y los criterios
  de material, recubrimiento y exposición del cabezal; la altura de la Tabla 3.11.6.4-1.
- **VE-7 (lote B):** el canto que cerraría se busca y se dice en el bloqueo, sin adoptarlo (VE7B-11);
  las caras sin tracción llevan el mínimo de 5.10.6 (VE7B-09); el agua exterior entra (VE7B-10); el
  acero del pórtico se metra (VE7B-12).
- **Qué haría falta:** separar los cantos en la geometría del programa y dimensionar la
  losa por su armado, como el peralte del cabezal (VE-3.9).
- **Dónde vive:** `src/modulos/M8_estructural.py::disenar_portico`

## T5-08 · El caso de la auditoría de T-4 deja de dimensionarse con la fabricación de archivo: cambio declarado y aprobado por el dueño

- **Qué se difirió:** nada; se registra un cambio de veredicto fuera de la línea
  base, **aprobado por el dueño del proyecto el 2026-11-12**.
- **Por qué:** el caso G2 del auditor adversarial de T-4 (rasante 52.20 m, Q =
  6 m³/s, ~8.5 m de relleno) se adoptaba en TMC de 1.95 m sin ninguna
  verificación estructural. Con la Fase 8 real y la costura remachada SIMPLE
  de archivo, ninguna plancha de 68 por 13 desarrolla el empuje (320.7 kN/m
  en 1.95 m frente a 0.67 × 374 = 250.6 kN/m de la de 4.27 mm, la última de la
  tabla: la progresión sube hasta ella antes de rendirse) y el TMC se descarta
  por `F8.COSTURA`; con la DOBLE (0.67 × 748) o la helicoidal se dimensiona con
  la plancha de 4.27 mm. **La FASE A había resuelto el test de T-4 que fijaba esa
  adopción añadiéndole la remachada doble, sin subir la pregunta** (PARADA (c),
  auditoría): el cierre restauró el test de `origin/main` y lo reescribió a la
  verdad nueva **declarándolo** —qué pasaba, qué pasa y por qué—, con el caso de
  la fabricación declarada al lado.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t4_materiales_durabilidad.py::test_h1_el_caso_del_auditor_ya_no_adopta_tmc_con_la_costura_de_archivo`

## T5-09 · Los valores de archivo de los [A] de la Fase 8 NO son todos «lo más desfavorable», y cada uno dice qué es

- **Qué se difirió:** nada; se declara la regla de cada valor de archivo.
- **Por qué:** la versión anterior de esta ficha decía que los cinco [A] nuevos
  «traen por defecto lo más desfavorable que la norma peruana admite», y las dos
  auditorías lo desmintieron en cuatro de cinco. Lo que cada uno es desde el
  cierre (y quién lo decidió):
  `'instalacion_estandar_concreto'` = **Tipo 3**, la instalación que la
  compactación exigida por el EG-2013 corresponde, con `tipo_4` **dentro de la
  ventana** (la FASE A lo dejaba fuera: «el Tipo 4 no la exige y queda fuera» era
  una lógica invertida, porque diseñar con el Tipo 4 es siempre válido y más
  desfavorable) y el Tipo 4 **impreso al lado** como contraste (decisión del
  dueño; T5-12); `'fabricacion_tmc'` = remachada simple, la costura más débil
  **tabulada**, que no es la del producto que el EG-2013 describe (T5-03);
  `'eta_importancia_operativa_conducto'` = 1.05: **ninguna fuente lo prescribe
  para una estructura enterrada** —12.5.4 solo fija la redundancia (η_R = 1.00) y
  1.3.5 dice «The Owner may declare»—; es la clasificación de importancia que
  hace el Propietario (vía de acceso en emergencia, FEN), [A] con la ventana del
  Manual de Puentes 2.3.2.5 (decisión del dueño); `'relleno_estructural_hdpe'` =
  `Si-95`, la columna menos favorable de las que corresponden al material
  granular del 508.02 d) (T5-05); `'parametros_diseno_hdpe'`, los valores que
  la norma llama **típicos** —K_B 0.10 y D_L 1.5 no son el extremo desfavorable
  de sus ventanas, que serían 0.110 y 6.0; ν = 0.40 tampoco (0.45), y no tiene
  fuente— y las propiedades a 75 años; `'carga_viva_bajo_relleno_alto'` =
  conservar (T5-11); y `'perfil_hdpe_fabricante'`, sin valor (T5-10). Los siete
  son de perfil, con ventana, y se barren con `--barrido`. **Qué corrida midió
  el nivel de cada uno** está escrito en la cabecera de su bloque en
  `criterios_adoptados.py`: dos los alcanza la corrida de referencia y cinco la
  corrida que excluye el concreto (y el TMC) por catálogo.
- **Qué haría falta:** las especificaciones técnicas del expediente (cama,
  relleno, producto) y la declaración del propietario sobre la vía.
- **Dónde vive:** `src/criterios/conducto.py::instalacion_estandar_concreto`

## T5-10 · Sin el perfil del fabricante el HDPE queda «no verificado con un producto real», no se adopta, y el punto no sale «no factible»

- **Qué se difirió:** el veredicto del HDPE, hasta que el expediente declare el
  perfil del producto.
- **Por qué:** decisión del dueño del proyecto (2026-11-12) sobre el hallazgo que
  las dos auditorías dieron por el más grave. AASHTO LRFD 12.12.3.2 dice que las
  propiedades de sección «should be determined from cut sections of pipe or
  obtained from the pipe manufacturer», y su comentario que los mínimos que las
  especificaciones traían —los de la Tabla A12-11— «have been minimum values and
  are not meaningful for design» (citas `AASHTO_LRFD_9.12.12.3.2` y
  `.C12.12.3.2`). El criterio `'perfil_hdpe_fabricante'` es por eso un [A]
  **opcional sin valor por defecto**: `{'900': {'A_mm2_mm', 'I_mm4_mm', 'od_m'}}`,
  cada propiedad no menor que el mínimo de la tabla. Sin él,
  `M8.verificar_hdpe` calcula con el perfil mínimo solo para dar la **cota
  inferior** (`M8.cota_inferior_hdpe`, `ResultadoEstructural.cota_inferior`), y
  se detiene con `DatoFaltanteError` sobre el criterio, con los cuatro números
  de la cota y el rótulo `ROTULO_HDPE_SIN_PRODUCTO` en el mensaje. **El HDPE no
  se adopta sin ese dato.** Dos consecuencias cuidadas: (1) el HDPE es el
  ÚLTIMO candidato del orden de M2, de modo que su dato faltante no bloquea a
  ningún material anterior (regla T4-10) ni mueve el fixture —medido: A-01 y A-02
  siguen en concreto de 0.90 m, B-01 «no factible» por V2, C-01 en los criterios
  del cajón—; (2) **un punto al que solo le falta un dato no es «no factible»**:
  cuando la Fase 8 detiene por dato faltante un escalón que CUMPLE toda la tabla
  de la Fase 5 (este caso, y el tubo de concreto sin clase transcrita), `MD`
  relanza ese `DatoFaltanteError` en vez de `DisenoNoFactibleError`
  (`ATRIBUTO_ESCALON_CUMPLE_LO_DEMAS`); la otra mitad de T4-10 —el dato que falta
  ANTES de la tabla en un material cuyos escalones evaluados incumplen— no
  cambia. El área efectiva sigue saliendo del mínimo de M 294 núm. 7.7 aunque el
  perfil esté declarado (T5-05).
- **Qué haría falta:** el catálogo o la certificación del fabricante del tubo
  que el expediente especifique (EG-2013 508.02 b)): entrada del
  `docs/contrato_entradas.md`.
- **Dónde vive:** `src/modulos/M8_estructural.py::cota_inferior_hdpe`

## T5-11 · La carga viva bajo relleno alto se conserva: el permiso de 3.6.1.2.6a no se toma en silencio

- **Qué se difirió:** nada; se declara una elección.
- **Por qué:** AASHTO LRFD 3.6.1.2.6a dice que los efectos de la carga viva «may
  be neglected» cuando el relleno supera 8.0 ft y la luz (y, en varios vanos, la
  distancia entre las caras interiores de los muros extremos). Es un PERMISO, y
  la FASE A lo tomaba siempre, sin criterio ni aviso: entre ~2.85 y 3.18 m de
  relleno el programa aceptaba un tubo de concreto de 0.90 m Clase II que con
  la carga viva no alcanza (50.59 N/m/mm con 2.90 m, contra 46.04
  despreciándola). El criterio `'carga_viva_bajo_relleno_alto'` [A] vale
  `conservar` (decisión del dueño, 2026-11-12; es el lado seguro) y
  `despreciar_3_6_1_2_6a` queda como alternativa barrible, que cuando se toma
  sale en el paso, en la cita y **en los avisos del punto**. El marco de varias
  celdas usa para el permiso la distancia entre muros extremos (N B + (N − 1) t,
  con los muros interiores del espesor de los exteriores a falta del diseño), no
  la luz de una celda. Movimiento declarado de la línea base: el relleno máximo
  de A-01 y A-02 pasa de 3.183 a 2.851 m; no es un diámetro.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M8_estructural.py::regla_de_la_carga_viva_bajo_relleno_alto`

## T5-12 · El tubo de concreto se verifica con el Tipo 3 y el Tipo 4 se imprime al lado: la correspondencia con el EG-2013 es lectura del proyecto, y tiene una condición

- **Qué se difirió:** nada; se declara una lectura y lo que tiene en contra.
- **Por qué:** decisión del dueño del proyecto (2026-11-12): valor de archivo
  Tipo 3 —la hipótesis de cálculo tiene que coincidir con lo que la
  especificación garantiza—, `tipo_4` dentro de la ventana y el Tipo 4 impreso
  como contraste (pasos `F8.TIPO4` y `F8.HMAX_TIPO4`; en A-01, 44.85 N/m/mm y
  1.69 m de relleno máximo contra 37.42 y 2.85). **Una precisión contra la
  fuente primaria**: la decisión citaba el EG-2013 508.07 (más del 95 % del
  Proctor Modificado), que es el numeral de la tubería de **polietileno**. Para
  el tubo de concreto rigen el 506.07 y el 506.10 (solado de subbase granular de
  15 cm y sujeción hasta un sexto del diámetro exterior, compactados como la
  corona: 95 % del Proctor Modificado) y, por encima, el 506.11 → Sección 502 →
  205.12(c)(1): los materiales de terraplén (A-1-a, A-1-b, A-2-4, A-2-6, A-3) al
  **90 %** del Proctor Modificado. La decisión se aplica igual —el EG-2013 exige
  compactar todo el relleno, que es lo que el Tipo 4 no pide—, con la
  justificación corregida y la condición dicha en la `Interpretacion` de la cita
  `AASHTO_LRFD_9.T12.10.2.1-1`: la Tabla 12.10.2.1-1 gradúa en Proctor
  **Estándar** y remite la equivalencia con el Modificado a la Tabla 27.5.2.2-3
  de la especificación de construcción de AASHTO, que no está en `normas/`; sin
  ella, el 90 % del Modificado garantiza el Tipo 3 con suelo granular o limoso
  (85 y 90 %), y no con el más plástico que el EG-2013 admite (A-2-6), para el
  que la tabla pide 95 %.
- **Qué haría falta:** las especificaciones de cama y relleno del expediente, o
  la Tabla 27.5.2.2-3 de AASHTO LRFD Bridge Construction Specifications.
- **Dónde vive:** `src/modulos/M8_estructural.py::_contraste_tipo_4`

## T5-13 · El pandeo general del HDPE va con el módulo de la vida de diseño, y rige el mayor de dos términos

- **Qué se difirió:** nada; se corrige una lectura que no estaba anclada.
- **Por qué:** AASHTO LRFD 12.12.3.3: «Investigation of general buckling shall be
  based on the value of modulus of elasticity that represents the design life of
  the project» (cita `AASHTO_LRFD_9.12.12.3.3#PANDEO`, EXIGENCIA). La FASE A
  sumaba el pandeo por duración —la carga viva contra la capacidad con el módulo
  inicial— apoyándose en la definición de E_p de 12.12.3.10.1c, que es de la
  deformación de compresión, y no citaba esa frase (auditoría). Desde el cierre
  `u_letra` = (ε_d + ε_l,lp)/ε_bck,lp, con la carga viva, su arqueo y su área
  efectiva de largo plazo, es la letra de 12.12.3.3 (decisión del dueño); la suma
  por duración (`u_duracion`) se conserva **al lado** y rige **la mayor**, porque
  cuál es mayor depende del suelo: con `Cl-95` la letra (0.513 contra 0.488 en
  A-01), con `Si-95` y `Sn-95` la suma por duración (0.194 contra 0.175). El
  paso imprime las dos y dice cuál gobierna.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M8_estructural.py::_evaluar_hdpe`

## T5-14 · Lo que las dos auditorías adversariales de T-5 encontraron, lo que se corrigió y lo que se refutó

- **Qué se difirió:** cortar la progresión de diámetros de un material cuando el
  último escalón solo incumple la Fase 8 (se refuta: ver abajo), y la
  devolución de la plancha elegida a la geometría (T5-03, sin cambio).
- **Por qué:** veredicto AJUSTADO de las dos, sin bloqueantes; cinco hallazgos
  ALTA entre las dos (vehículo por presión, permiso de 8 ft, HDPE excluido en
  todo el dominio, «Tipo 3 el más desfavorable», el test de T-4 reescrito en
  silencio). Corregidos todos: T5-06, T5-11, T5-05 y T5-10, T5-12 y T5-09, T5-08.
  De los MEDIA y BAJA: el carácter del umbral se lee de la cita y ya no se
  escribe "EXIGENCIA" a mano (la deflexión del 5 % es la RECOMENDACIÓN de
  C12.12.2.2); lo que no se verifica se imprime **por material**
  (`ResultadoEstructural.diferido`), no la lista de todos; guardias de segunda
  línea en `carga_viva_enterrada` (conducto fuera del conjunto cerrado) y en
  `incremento_dinamico_enterrado` (una cubierta negativa daba un IM de 100.7 %);
  la fila «< 2.0 ft» de B_FLL era código muerto y se retiró; el piso de 110
  lb/ft³ no puede gobernar y el docstring lo dice; el contraste ASD dice que no
  es «A796 puro» (lleva el m = 1.20 y el IM de LRFD); la lectura de 12.7.2.2 sin
  K_γE queda declarada en el paso como la de la menor demanda; y los huecos que
  dejó la mutación (deflexión admisible, rama elástica del pandeo, relleno
  máximo del TMC y del HDPE, muestreo del primer cruce, nivel freático,
  márgenes, marco con H ≠ 1) tienen test con dorado a mano
  (`CP_FASE_8_CIERRE`). **Refutado con evidencia:** que el TMC «sube de diámetro
  inútilmente» cuando falla la Fase 8 (O-H14) no se corrige cortando la
  progresión, porque la monotonía no vale en general —el propio auditor mide en
  el concreto que la D-load baja al crecer el diámetro con relleno somero—; lo
  que se corrige es el motivo, que ahora dice que el catálogo no se agotó por la
  hidráulica (`ACLARACION_DESCARTE_POR_FASE_8`). **Los tests de las correcciones
  no se escribieron en rojo antes del código**: se midió el rojo contra la FASE A
  rebasada (`1768b45`): 48 de 71 fallan allí; los 23 que valen antes y después
  son 15 literales del PDF y 8 guardias (entre ellas las que matan mutantes de
  código que ya era correcto).
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t5_correcciones_auditoria.py::test_cada_consumidor_pasa_su_medida_del_efecto`

---

# Parte XLVII — Lo que T-3 de la cadena T dejó escrito: el marco de la Familia C se dimensiona sin declarar nada

T-3 (2026-11-12) da valor de archivo a los siete criterios del cajón (`INF-0.4`), añade
VC2 y el remanso aguas arriba del canal, publica la geometría del marco y amplía V6 para
la multicelda. Ningún valor de archivo mueve una sección ya fijada. La auditoría
adversarial (AJUSTADO, doce hallazgos H1 a H12) se aplicó el 2026-11-13 con las
resoluciones del orquestador y las decisiones del dueño del 2026-11-12: el n del marco
pasa a la fila del cajón de la Tabla B.1 del HDS-5 [C] (mueve el tirante y el HW de
salida de C-01, no su sección), el remanso dice cuándo no concluye, G2 y VC2 son una
sola banda en la Familia C y G1 del marco avisa cuando sólo falta la cobertura adoptada.
Doce fichas; las cinco últimas son de la auditoría.

## T3-01 · La progresión de secciones es la decisión del dueño; la de la cadena T no se activa

- **Cerrado (T-3, decisión del dueño del 2026-11-12):** `secciones_cajon_normalizadas`
  = ((1.20, 0.90), (1.50, 1.20), (2.00, 1.50)), [A] con su ventana y `vacio_verificado`:
  la progresión con que C-01 dimensiona desde C7. Deja de ser «provisional»: es la
  decisión, y C-01 sigue en marco 1.20 × 0.90.
- **Abierto:** la de la cadena T (anchos 1.00–4.00 paso 0.50 × alturas 1.00–3.00 paso
  0.25) no contiene el 1.20 × 0.90 y deja a C-01 sin dimensionar —V7 incumple en los
  siete primeros escalones y el octavo deja la clave sobre la subrasante—; queda en la
  `sensibilidad`, barrible. La causa de V7 no es que el marco no quepa: es `DC = 0` en
  `M5.v7_flotacion` (ficha T3-08). Con tres escalones la serie se agota en 2.00 × 1.50 m.
- **Qué haría falta:** la sección real del canal (ancho de solera y tirante, de ANA o de
  la Junta de Usuarios) para ampliar la progresión —alturas de 0.60 y 0.75 m, más
  anchos— siguiendo al canal; y la ficha T3-08 si se quiere medir la de la cadena con el
  peso propio del marco.
- **Dónde vive:** `src/criterios/geotecnia.py::secciones_cajon_normalizadas`

## T3-02 · La embocadura del marco es la de aletas de 30° a 75°, la de hoy; la de cabezal recto se midió y da otra carga

- **Cerrado (T-3):** `embocadura_cajon` = Carta 8 escala 1 (Forma 1, K 0.026, M 1.0,
  c 0.0347, Y 0.81; Tabla A.1, PDF 197) y `ke_entrada_cajon` = la fila «Square-edged at
  crown» bajo «Wingwalls at 30° to 75° to barrel» (0.4; Tabla C.2, pág. impresa C.6): la
  misma embocadura en la carta y en el ke.
- **Abierto:** la cadena T sugería «por ahora square edge headwall 90°». Medido sobre C-01:
  con la Carta 8 escala 2 («90° and 15° wingwall flares») y el ke de «Headwall parallel to
  embankment (no wingwalls)» (0.5), HW = 0.629 m frente a 0.589 m con aletas. Como la carga
  cambia, se dejó la de hoy (precisión del orquestador). La Lámina N° 03 no decide: es un
  corte longitudinal y no muestra el ángulo de las aletas.
- **Qué haría falta:** T-7a, que dimensiona el cabezal y los aleros por punto, cierra la
  coherencia entre la geometría de los aleros, la carta y el ke.
- **Dónde vive:** `src/criterios/geotecnia.py::embocadura_cajon`

## T3-03 · VC2 avisa y no detiene, con la tolerancia de una placa de concreto del EG-2013 por analogía

- **Cerrado (T-3):** `M7.vc2_empalme_canal`, sólo en la Familia C, banda de dos lados
  |cota_salida − cota_fondo_receptor| ≤ `desajuste_empalme_canal_m` [A] = 0.010 m (ventana
  0.010 a 0.020): la tolerancia de aceptación de la cota superior de una placa de concreto
  (EG-2013 503.11 g) 2., pág. impresa 934) y la de cota de la excavación (501.07, pág.
  impresa 889). Veredicto INDICADOR: cuenta en «Verificaciones con aviso» y sale en los
  avisos del punto.
- **Abierto:** (1) Ninguna fuente fija la tolerancia de un empalme con un canal: es
  analogía declarada en el umbral. (2) VC2 no detiene porque el desajuste lo fijan la cota
  de entrada y la pendiente, no la sección; en C-01 del fixture sale un desajuste de
  +0.571 m, que es la firma de la cota de entrada ADOPTADA del terreno (36.90) frente al
  fondo del canal (36.20). (3) La homonimia de `cota_fondo_receptor` (en un paso de canal
  es el mismo canal aguas abajo) se declara en el paso, no se resuelve con una columna.
- **Corregido por la auditoría (H4, H9):** VC2 **gobierna el empalme**: en la Familia C
  `M7.g2_cota_salida` admite por debajo su tolerancia (a 36.195 m sobre 36.20 los dos
  cumplían y no cumplía; hoy los dos cumplen); A y B no cambian. Y el aviso imprime la S
  que cerraría el empalme con las cotas dadas, (entrada − fondo) / L, rotulada como valor
  calculado de primer orden. Decisión del dueño: aviso, no bloqueo.
- **Qué haría falta:** la cota de fondo de la entrada medida en el cauce
  (`cota_fondo_entrada`) y la pendiente que une las dos cotas del canal; y, para que VC2
  detenga, la tolerancia del proyecto del canal (ANA / Junta).
- **Dónde vive:** `src/modulos/M7_geometria.py::vc2_empalme_canal`

## T3-04 · El remanso aguas arriba del canal es una cota inferior, no un perfil, y sin la sección medida no se evalúa

- **Cerrado (T-3):** `M7.remanso_canal`: con `seccion_receptor_medida` (que en un paso de
  canal es la del mismo canal) calcula el tirante normal del canal, la sobreelevación en el
  cruce dh = HW − y_n y la longitud dh / S, a la que la horizontal del embalse corta la
  lámina normal; lo publica como aviso y paso 7.B.R. Sin la sección medida, aviso «no se
  evaluó», sin supuesto.
- **Abierto:** (1) dh / S es una COTA INFERIOR sólo en un canal suave: el perfil M1 real
  queda por encima de la horizontal y llega más lejos. (2) Se toma el fondo del canal en
  el cruce igual a la cota de fondo de la entrada, y el HW sin la carga de velocidad de
  aproximación. (3) No hay umbral: ninguna fuente de `normas/` fija cuánto puede subir la
  lámina de un canal. (4) Corregido por la auditoría (H2, H3): **no concluye**, sin
  cifra, con el canal de pendiente fuerte (y_n ≤ y_c: S1 con resalto) o con VC2 fuera de
  tolerancia (HW de una descarga libre que el canal no tiene).
- **Qué haría falta:** un perfil de remanso paso a paso sobre la sección del canal y la
  coronación del canal a lo largo del tramo (hueco 2 de §13 de `docs/ruta_familia_c.md`).
- **Dónde vive:** `src/modulos/M7_geometria.py::remanso_canal`

## T3-05 · V6 con N > 1 publica el reparto, el tabique y el ancho total, y sigue sin aceptar la multicelda

- **Cerrado (T-3):** con N > 1 la fila de V6 dice Q/N por celda (el reparto de EXT-2), el
  tabique entre celdas y el ancho exterior total N·B + (N − 1)·t + 2·t.
- **Abierto:** (1) El veredicto no cambia: la multicelda sigue sin aceptarse mientras no
  haya dato de arrastre del cauce (ficha EXT-2-01). (2) La separación entre celdas de un
  marco vaciado in situ es el TABIQUE (monolítico, §14.1): la regla del num. 4.1.1.3.4 a)
  —la mitad del diámetro, entre 0.40 y 1.00 m, medida entre superficies externas— es de
  TUBERÍAS con relleno compactado entre ellas, y la fila la nombra para decir por qué no la
  aplica (cita `MC_HHD.4.1.1.3.4a#SEPARACION`). La cadena T pedía usarla: la fuente no la
  da para un marco. (3) V7 se evalúa por celda: con N > 1 no carga el marco entero.
- **Cerrado (VE-5, lote m45, ítem 18):** (1) el dato existe —`arrastre_de_solidos`, ficha
  EXT-2-01— y V6 acepta la multicelda en un cauce declarado sin arrastre.
- **Qué haría falta:** si se adopta la multicelda, V7 sobre la sección completa.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v6_material_solido_arrastre`

## T3-06 · La geometría del marco queda en `modelos.GeometriaMarco` para la Fase 8 y el cabezal; M8 no se toca

- **Cerrado (T-3):** `M7.geometria_marco` publica B, H, N, el espesor, el tabique, el
  ancho y el canto exteriores, las cotas de fondo, de clave interior y exterior (la misma
  de `M5.cota_clave`) y de base, y el relleno sobre la losa; viaja en
  `CompatibilidadGeometrica.geometria_marco`, en el JSON y en la memoria (paso 7.B.M).
- **Abierto:** (1) Un solo espesor para paredes, losas y tabique (`espesor_pared_cajon`
  = 0.20 m, piso de la E.060 14.5.3.2 por analogía): la cadena T hablaba de «espesor de
  losa» y no se abre un criterio que nadie declaró. (2) Integrado detrás de T-5,
  `GeometriaMarco` queda SIN consumidor en M8: `M8.demanda_marco` lee `Seccion`,
  `espesor_pared` y la misma `M5.cota_clave`, de modo que los números coinciden; no se
  fuerza el cambio.
- **Qué haría falta:** que la demanda de la losa (y el cabezal por punto, T-7a) lean la
  geometría de aquí cuando se toquen; el cálculo estructural del pórtico en el
  expediente, que hará del espesor un resultado y no una adopción. **Desde VE-5 (m8)**
  el pórtico se calcula (`M8.disenar_portico`, ficha T5-07) con su propia
  `GeometriaPortico`, que separa los cantos de losa, pared y tabique; la de aquí sigue con
  uno solo y el pórtico lo toma de `espesor_pared`, de modo que los números coinciden.
- **Dónde vive:** `src/modelos/remanso.py::GeometriaMarco`

## T3-07 · Con la embocadura del cajón declarada, R4 ya no frena una fila de cajón para el ke del TUBO; la frena el consumidor

- **Cerrado (T-3):** nada se abre: la segunda capa de C5-02 sigue en pie —si una fila del
  bloque «Box» de la Tabla C.2 llega a `ke_entrada` (el tubo) por cualquier vía,
  `M4.ke_declarado` la rechaza con `DatoInvalidoError`— y se mide igual que antes.
- **Abierto:** la PRIMERA capa era incidental. Toda fila de cajón de la Tabla C.2 lleva la
  condición de `embocadura_cajon`, y mientras ese criterio estuvo sin valor R4 la hacía
  inelegible para cualquier criterio que leyera la tabla, el del tubo incluido. Con valor
  de archivo (T-3) la fila es elegible y `declaracion.declarar_desde_tabla` la acepta
  para el tubo: el error ya no sale al declarar sino al correr, en el punto. La medida está
  en `tests/test_cierre_c10.py` (la capa 1 se mide con el criterio vaciado).
- **Qué haría falta:** que la puerta de declaración filtre las filas de la Tabla C.2 por el
  BLOQUE que corresponde a la forma del criterio (tubo o cajón), en lugar de apoyarse en
  la condición de la embocadura. Toca `declaracion.py` y la ventana normativa; no es de T-3.
- **Dónde vive:** `src/modulos/M4_control.py::ke_declarado`

## T3-08 · V7 del marco no pesa el concreto (DC = 0): de eso cuelgan la progresión corta y el espesor

- **Qué se difirió:** pesar el marco en `M5.v7_flotacion` con
  `peso_especifico_concreto_kn_m3` [C]. V7 lleva DC = 0 (lado seguro) desde C7, y es lo
  que deja fuera la progresión de la cadena T (1.00 × 1.00: 18.21 contra 19.23 kN/m; su
  concreto, 0.96 m² a ~23.5 kN/m³, pesa ~22.6 kN/m), lo que hace inalcanzable en C-01 el
  segundo escalón adoptado (1.50 × 1.20: 18.9 contra 29.8) y lo que deja a C-01 sin
  dimensionar con t ≥ 0.26 m.
- **Por qué:** con DC, la progresión de la cadena daría probablemente 1.00 × 1.00 en C-01
  y movería una sección del fixture (parada (c)); V7 es código de C7, no de T-3. La
  auditoría lo pidió diferido y el orquestador lo resolvió así: no se toca V7 en T-3.
- **Cerrado por VE-5 (m8, ítem 26 del censo):** V7 pesa el conducto, marco incluido, con
  `M5.peso_propio_conducto_kn_m` y `peso_especifico_concreto_kn_m3` [C], minorado con el
  γ_DC mínimo de la Tabla 2.4.5.3.1-2 (`M8.factores_carga_flotacion`). La entrada
  `flotacion_marco_sin_peso_propio` salió del alcance declarado.
- **Qué haría falta:** nada para V7; el efecto sobre la progresión del marco lo mide la
  línea base regenerada.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v7_flotacion`

## T3-09 · El n del marco es la fila del cajón de la Tabla B.1 del HDS-5 [C]; la errata de la Tabla N° 09 se sostiene en su página

- **Cerrado (auditoría, H1 y H10):** `n_manning_cajon` = `concrete_boxes` (0.012, 0.015),
  [C], HDS-5 Tabla B.1, pág. impresa B.6 —la misma fuente de la carta y del ke—; el num.
  B.3 (0.012–0.022 en vaciado in situ, pág. impresa B.2) es la ventana hacia arriba, y la
  fila «afinado» de la Tabla N° 09 (0.011, 0.014), la alternativa barrible. La errata
  `DIS-MCHHD-T09-A2-DESPLAZADA` deja de apoyarse en Chow (no está en `normas/`).
- **Abierto:** sobre C-01 el cambio mueve el tirante normal y el HW de control de salida,
  no la sección ni el HW de entrada (README de la línea base). Con dos tablas la
  resolución no fija `fila_id`; la alternativa se declara por la CLI o se barre con nota.
- **Qué haría falta:** la ficha técnica del encofrado del marco, que diría el n real.
- **Dónde vive:** `src/criterios/geotecnia.py::n_manning_cajon`

## T3-10 · G1 del marco avisa cuando sólo falta la cobertura adoptada por analogía

- **Cerrado (auditoría, H5):** 0.3048 m se mantiene como umbral de aviso; la fuente
  admite el marco sin relleno (MTC 4.1.1.3.4 a), Lámina N° 03, AASHTO LRFD 12.6.6.3,
  pág. impresa 12-22). `TamizadoRasante.cobertura_como_aviso`: bloquea la clave bajo la
  subrasante y el resguardo; la cobertura adoptada da INDICADOR. G1 del tubo no cambia.
- **Abierto:** con relleno < 2 ft la Fase 8 del marco no era evaluable (AASHTO 3.6.1.2.6a);
  desde VE-4f lo es (la franja de 4.6.2.10.2, ficha VE4F-01), y la losa para carga directa
  se diseña con el pórtico (ítem 1 del censo, ficha T5-07). En C-01, con sumersión completa, V7 (DC = 0)
  rechaza antes el escalón, y el caso de la auditoría (rasante 38.40 / subrasante 38.25)
  termina con V4 y V7 en el primero y la clave sobre la subrasante en el segundo.
- **Qué haría falta:** el diseño de la losa para carga vehicular directa (expediente) y
  la ficha T3-08.
- **Dónde vive:** `src/modulos/M7_geometria.py::g1_rasante_congelada`

## T3-11 · `espesor_pared_cajon` queda [A] aunque su piso sea de una norma peruana

- **Qué se difirió:** etiquetarlo [N→]. El 0.20 m es el piso de la E.060 num. 14.5.3.2,
  pero ese numeral es del **método empírico** de diseño de muros (14.5) y la pared del
  marco se diseña por flexión (14.8.1 → Cap. 10): la analogía es de objeto, no de método.
- **Por qué:** además hay ventana (0.20–0.30 m) y elección: 0.20 es su extremo favorable a
  V7 mientras V7 lleve DC = 0 (ficha T3-08). Un [A] con ventana dice eso; un [N→] lo
  presentaría como lectura de la norma.
- **Qué haría falta:** el cálculo estructural del pórtico, que haría del espesor un
  resultado.
- **Dónde vive:** `src/criterios/geotecnia.py::espesor_pared_cajon`

## T3-12 · Las correcciones de la auditoría se escribieron antes del código, y su rojo se midió

- **Cerrado:** `tests/test_t3_correcciones_auditoria.py` se escribió antes del código y se
  midió contra la FASE A rebasada sobre `e78a4e7` (`c6712d4`): 23 rojos y 29 verdes; con
  el archivo final, 33 rojos y 30 verdes, que son guardias y matadores de mutantes que
  valen antes y después (H8). El arnés de EXT-11 sobre `vc2_empalme_canal`,
  `remanso_canal`, `geometria_marco`, `_desajuste_admisible`, `g2_cota_salida` y
  `M3.tirante_critico_trapecial` mataba 104 de 120; con los nueve tests que eso sumó,
  113 de 120 (94.2 %).
- **Abierto:** no se escribió con `xfail(strict=True)`: el rojo se midió corriendo el
  archivo sobre el árbol previo. Los siete vivos son equivalentes: la frontera y_n = y_c
  con su tolerancia de 1e-9 (dos), desajuste = 0 (el brazo del aviso no lo alcanza) y la
  semilla, la duplicación y el signo del corchete del tirante crítico (cuatro).
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t3_correcciones_auditoria.py::test_h4_G2_y_VC2_no_se_contradicen_en_la_familia_C`
---

# Parte XLVIII — Lo que T-9 de la cadena T dejó escrito: la longitud por capacidad de la cuneta y el espaciamiento que puede fallar

## T9-01 · La sección de la cuneta: el mínimo de la región muy lluviosa de la Tabla Nº 34, con el talud exterior como elección declarada

- **Qué se difirió:** la sección **del trazo**. En la FASE A `seccion_cuneta` [A] nació sin
  valor de archivo; desde las correcciones de la auditoría de T-9 tiene uno, por la
  **decisión A del dueño** (2026-11-12): {profundidad 0.40 m, ancho 1.20 m, talud exterior
  1.0 H:V, borde libre 0}. Lo que sigue diferido es la sección típica real del proyecto vial
  y el talud de corte del EMS, que la sustituyen cuando lleguen.
- **Por qué:** 0.40 × 1.20 m es el **mínimo** de la Tabla Nº 34 (núm. 4.1.2.1 c), pág. impresa
  178) para la región «muy lluviosa (1600 a <3000 mm/año)», que es la región que el proyecto
  ya adopta con `long_max_cuneta` (200 m por el FEN), y la tabla lo **exige** («las
  dimensiones mínimas serán»). Como el ancho se mide hasta la vertical del vértice (pág. 173),
  0.40 × 1.20 fija el talud **interior** Z1 = 3; el **exterior** no lo fija la tabla —el
  Manual lo hace depender del talud de corte y el DG-2018 (núm. 304.11) dice que «por lo
  general coincide con el talud de corte»—, y Z2 = 1.0 es **elección [A] de este proyecto**:
  el más empinado de las filas de suelo fino o arenoso de la Tabla 304.10 del DG-2018 para
  cortes menores de 5 m (limo arcilloso 1:1, arenas 2:1; Relación H:V, pág. impresa 204), el
  lado seguro para la capacidad (0.467 a 0.871 m³/s con Z2 de 0.10 a 2.0). La ventana (H5)
  empieza en ese mínimo; sus techos de ancho (2.40 m) y de borde libre (0.10 m) son
  **adopción**, no de la fuente (la FASE A atribuía el primero a la Tabla 304.12 leyéndola al
  revés). El **borde libre** vale 0 porque el Manual calcula a cuneta llena, y «con borde
  libre» se **retiró** de la v8 (decisión B). El talud interior se contrasta con la Tabla
  304.12 (`M10.aviso_de_talud_interior`): más empinado que 1:2 es `DatoInvalidoError`; Z1 = 3
  se **avisa** (con V.D. > 70 km/h e IMDA > 750 la tabla pide 1:4). El detalle, en la
  justificación del criterio.
- **Qué haría falta:** (i) la REGIÓN pluvial del corredor en año FEN medida por el estudio
  hidrológico —es una elección ligada a un dato de sitio sin trazabilidad en el repositorio;
  si supera 3000 mm/año el mínimo es una sección **trapezoidal** (nota * de la Tabla Nº 34),
  que la Fase 10 no implementa—; (ii) el talud de corte del EMS por tramo; (iii) la velocidad
  de diseño y el IMDA de la vía, para cerrar el aviso de la Tabla 304.12; (iv) si la sección
  cambia entre tramos, el criterio pasa a dato externo por punto.
- **Dónde vive:** `src/criterios/hidraulica.py::seccion_cuneta`

## T9-02 · El aporte por metro: con el tramo conocido, Q / s; sin él, q · b con la longitud implícita avisada

- **Qué se difirió:** iterar el tiempo de concentración con la longitud de la cuneta (la
  intensidad de una cuneta más larga es menor) y exigir que el área tributaria declarada sea la
  faja del tramo.
- **Por qué:** la FASE A repartía el caudal declarado con q = Q / `area_ha` por un ancho
  tributario independiente, y con un área que no era la faja b × tramo la longitud por
  capacidad salía cientos de veces el tramo (B-01: 42 282 m) y VB1 **cumplía** con un aporte
  82 % mayor que la capacidad (H1 de la auditoría, ALTA). Desde las correcciones: (a) la
  condición literal del Manual es su propia verificación, **VB2** (ficha T9-07); (b) con el
  **tramo** conocido y el caudal declarado, el aporte se reparte uniformemente en el tramo real,
  q' = Q / s, y L_hidraulico = Q_adm · s / Q —su equivalente exacto: L ≥ s si y sólo si
  Q_adm ≥ Q—, sin mezclar el área con el ancho; (c) sin tramo, se conserva q' = (Q / A) · b,
  pero el paso imprime la longitud que ese par implica, s_impl = A · 10⁶ / b, y **avisa** por
  `avisos()` cuando supera el recorrido máximo (`long_max_cuneta`; B-01 con 18 ha y 12 m:
  15 000 m), sin tolerancia inventada; (d) con el caudal CALCULADO por la Fase 1-bis sigue el
  camino q · b, y no se recalcula (H11: la Fase 1-bis lo calcula para la Familia B con
  `MH.caudal_de_aporte_cuneta`, una vez, y la Fase 10 lo reutiliza sin repetir sus pasos). La
  lluvia es la del periodo de retorno del **punto** (ficha T9-08). Con el tramo conocido y el
  caudal declarado, VB1 y VB2 miran la misma desigualdad desde dos lados (la capacidad contra
  el aporte, y el tramo contra la longitud que la capacidad alcanza) y un mismo defecto puede
  incumplir las dos: se dice, no se esconde.
- **Qué haría falta:** que el estudio hidrológico declare, para cada alivio, el caudal y el
  área de SU tramo de cuneta (no los de una cuenca mayor); si se quiere la longitud exacta lejos
  del tramo, una iteración de tc con el recorrido en la cuneta, con su método declarado.
- **Dónde vive:** `src/servicio.py::_aporte_del_punto`

## T9-03 · VB1 por tramo: el extremo es el inicio declarado o la obra anterior (B, o A por la decisión C); sin extremo, es un bloqueo

- **Cerrado (T-9):** `INF-5.1.12` — el paso 10.1 dejó de decir «cumple» por construcción (es un
  límite, sin veredicto) y la verificación es **VB1**: el tramo de cuneta entre el alivio y el
  extremo de su lado de progresivas **menores** no puede exceder el espaciamiento máximo; entre
  dos alivios el sentido del flujo no es dato y se toma el menor de sus dos máximos.
- **Por qué, y lo corregido tras la auditoría:** el extremo lo resuelve `M10.extremo_del_tramo`, antes de los
  puntos: el inicio declarado (`inicio_tramo_cuneta_km`, que gana y no puede ser posterior a la
  obra —`DatoInvalidoError` que nombra el par, H3—), o la obra anterior en progresiva que lo
  cierre: de Familia B, y de Familia A por el criterio `obras_familia_a_extremo_de_cuneta` = `si`
  (**decisión C del dueño**; la sostiene el DG-2018 núm. 304.11 y no el Manual, y va declarada
  como `Interpretacion` de la cita `DG2018.304.11#DESAGUE`). Un VB1 que **no se evaluó** —sin
  extremo, o con el máximo de un extremo desconocido— es un **bloqueo** del punto que espera el
  dato que lo destraba (H2: `TramoDeAlivio.falta`, `DatoFaltanteError` en la etapa de VB1), y
  el pre-vuelo lo estima. Los tramos de cuneta que VB1 no mira se **avisan** (H3): el que queda
  entre la obra anterior y un inicio declarado posterior a ella, y el del lado de progresivas
  mayores cuando la obra siguiente no es otro alivio. Ningún texto supone el sentido del flujo.
- **Consecuencia que se declara:** en el fixture, B-01 (2+450) queda a **530 m** de A-02 (1+920)
  y VB1 **no cumple** —contra los 200 m normativos en la línea base, donde su máximo no se
  conoce; contra los 120 m de `L_hidraulico_m` en la guía—. No se mueve ningún diámetro.
- **Qué haría falta:** las progresivas de inicio de los tramos de cuneta del proyecto de
  drenaje longitudinal (con el perfil, que decide si la cuneta llega de verdad a una obra de
  Familia A) y las obras B reales del corredor.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::extremo_del_tramo`

## T9-04 · Cuatro ecuaciones del ejemplo del Manual no reproducen la geometría que nombran, y no se usan

- **Qué se difirió:** usar las ecuaciones (4.1), (4.3), (4.4) y (4.6) del num. 4.1.2.1 a)
  (págs. impresas 175-176).
- **Por qué:** escritas para taludes «1:2 y 1:2» y «1:1.5 y 1:1.5», dan A = 5H²/4 y
  A = 13H²/12; con los dos taludes 1:2 (V:H) el área de la sección triangular de
  profundidad H es 2·H², y (4.1) «Rh = 5x√H / 6» no es siquiera dimensionalmente un radio.
  El programa calcula A, P y Rh de la geometría declarada y usa de esa página sólo (4.2) y
  (4.5), Rh = (n·v/√S)^(3/2), que es Manning despejado. Es un defecto de la fuente
  primaria, no de la hoja de ruta (que no las cita), y se declara en la nota de la cita
  `MC_HHD.4.1.2.1a#VELOCIDAD` y en la memoria.
- **Qué haría falta:** nada que el programa pueda hacer; para la tesis, citar el
  procedimiento del Manual (los dos límites y la condición Q manning > Q de aporte) y no su
  ejemplo.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::geometria_triangular`

## T9-05 · La pendiente de la cuneta es un dato del trazo: no se deriva del CSV, y fuera de la banda del Manual se avisa con el mínimo del DG-2018 al lado

- **Qué se difirió:** derivar `S_cuneta` de las cotas de rasante del CSV, y elegir entre
  el mínimo del Manual y el del DG-2018.
- **Por qué:** el CSV trae `cota_rasante` sólo en cada cruce; la pendiente de la cuneta es
  la local del tramo, con sus curvas verticales, y una media entre dos cruces la puede
  esconder. Las dos fuentes no dicen lo mismo del mínimo: el Manual (núm. 4.1.2 c), pág.
  impresa 172) pide 0.5 % < i < 2 % para el drenaje longitudinal; el DG-2018 (núm.
  304.11) da 0.2 % como mínima absoluta de una cuneta revestida y 0.5 % sin revestir.
  La pendiente no es una decisión de la Fase 10: la Fase 10 la usa y avisa.
- **Qué haría falta:** el perfil longitudinal del trazo por tramo de cuneta.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::aviso_de_pendiente`

## T9-06 · La aceptación de T-9 se escribió después del código; el rojo se midió contra la base

- **Qué se difirió:** el orden de la casa (rojo con `xfail(strict=True)` y liberar).
- **Por qué:** se dice en vez de reconstruirlo. Medido corriendo
  `tests/test_t9_espaciamiento.py` contra un árbol exportado de `df1b23c` con un
  `xfail(strict=True)` de módulo y los nombres nuevos sustituidos por marcadores: de los
  82 tests, 81 en rojo y 1 XPASS —la guardia de que M10 no importa la hidrología, que vale
  antes y después—; además el teardown del fixture `_limpio` falla en la base en los 82,
  porque los criterios de la cuneta no existen, y pytest los cuenta también como xfailed
  (163 en el resumen). Los tests de la carga de los datos de la cuneta miden el MOTIVO: con sólo la
  excepción pasaban vacuos en la base, que rechazaba las claves por desconocidas. Los
  dorados son la aritmética escrita en el propio archivo (el Manual no trae un ejemplo
  numérico que sirva: sus ecuaciones de ejemplo están mal, ficha T9-04).
- **Qué haría falta:** nada que se pueda rehacer.
- **Dónde vive:** `tests/test_t9_espaciamiento.py::test_M10_no_importa_la_hidrologia`

## T9-07 · VB2: la condición literal del Manual, el caudal de aporte contra la capacidad de la cuneta

- **Qué se difirió:** nada de la condición; queda diferido exigir la pendiente de la cuneta a
  quien declara la longitud.
- **Por qué:** el Manual de Hidrología (núm. 4.1.2.1 a), pág. impresa 177, PDF 180) cierra el
  procedimiento con «Q manning > Q de aporte, Entonces el diseño está terminado. Si ocurre lo
  contrario, debemos volver al paso 2 y elegir otra altura de cuneta (H).» (cita
  `MC_HHD.4.1.2.1a#CONDICION`, EXIGENCIA). En la Familia B el caudal del punto es, por
  contrato, el de la cuneta que descarga en el alivio: VB2 lo compara con la capacidad
  admisible (`CapacidadCuneta.Q_admisible_m3s`), **puede fallar** y entra a la aceptación de la
  Familia B (`PERFILES[Familia.B].verificaciones_aceptacion` = V1 + V2 + V4 + V5 + VB1 + VB2:
  las dos son «el espaciamiento de la Fase 10» de la v8 §2.3). No necesita el tramo. Sin
  `S_cuneta` no hay capacidad y VB2 no se evalúa: con `L_hidraulico_m` declarado sólo se
  **avisa** (quien declara la longitud declara que la cuneta conduce su aporte hasta ella; no se
  le exigen datos nuevos), y sin la longitud la Fase 10 ya se detiene por la misma falta. El
  caso del auditor (0.20 × 0.50, Z2 0.5, concreto, S 0.005, Q 0.095) da Q_adm = 0.052215 m³/s y
  VB2 NO CUMPLE, con la aritmética escrita en `CP_T9_CUNETA`. **`INF-5.1.8` queda CERRADO EN
  PARTE**, dicho con honestidad: `area_ha` en la Familia B tiene dos consumidores reales —el
  contraste Q/A de T-1 y el reparto q · b sin tramo, con la longitud implícita que avisa
  cuando el área no es la faja del tramo—, pero con el tramo conocido ya no entra a la
  longitud, y nada comprueba que el área declarada sea la de la cuneta del alivio: eso sigue
  siendo del estudio hidrológico.
- **Qué haría falta:** si el proyecto quiere exigir la capacidad también a quien declara la
  longitud, convertir el aviso de VB2 sin evaluar en un bloqueo (decisión del dueño).
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::verificar_aporte`

## T9-08 · El periodo de retorno del aporte es el del punto, y la fila del alivio es una envolvente declarada

- **Qué se difirió:** que el programa conozca el periodo de retorno con que el estudio calculó
  un caudal DECLARADO.
- **Por qué:** la FASE A escribía «TR = 35 años» en los textos de M10 (H4): con el riesgo del
  Propietario el TR del punto cambia (R 0.20, n 15: 67.7 años) y la nota seguía diciendo 35. La
  Tabla Nº 02 (núm. 3.6, pág. impresa 25, PDF 28) da **riesgo**, no periodo de retorno, y deja
  al Propietario la definición del riesgo y de la vida útil. Desde las correcciones el paso del
  aporte imprime el TR del **punto** (Fase 2, con el riesgo del Propietario si lo declaró) y,
  con el caudal declarado, dice que el programa no conoce el TR del estudio. Que se use la fila
  del alivio (R 35 %, n 15: T = 35.32 años) y no la del drenaje de la plataforma (R 40 %, n 15:
  T = 29.87 años) es una **envolvente conservadora** —más lluvia, menos longitud—, declarada como
  `Interpretacion` de la cita `MC_HHD.4.1.2a` (decisión D; H10), con lo que juega en contra
  (el núm. 4.1.2 a) remite al drenaje longitudinal, y ninguna fila es exigencia).
- **Qué haría falta:** que el estudio hidrológico declare el periodo de retorno de cada caudal
  que entrega; y que el Propietario fije el riesgo de la cuneta si quiere otro.
- **Dónde vive:** `src/servicio.py::_texto_periodo_retorno`

## T9-09 · Las lecturas del proyecto en la Fase 10 son `Interpretacion` del registro, y tres dudas del auditor quedan dichas

- **Qué se difirió:** nada; se registra dónde quedó cada lectura.
- **Por qué:** (H10) la unión de una fila de la Tabla Nº 32 con una de la Tabla Nº 33 es
  `Interpretacion` de la cita `MC_HHD.4.1.2.1#T33`, y el paso la lee del registro cuando el
  revestimiento no es concreto; el fundamento `F10.TRAMO` dejó de decir «más de lo que el Manual
  admite» sobre un umbral que la fuente sólo recomienda: separa lo que el Manual EXIGE (250 m)
  de lo que RECOMIENDA (200 m) y de lo que el proyecto adopta. (Dudoso 1) B-01 está en terraplén:
  la sección del modelo es la de la cuneta en corte del **tramo** que descarga en el alivio, no
  la del cruce (`Interpretacion` de `MC_HHD.4.1.2.1#UBICACION`, con lo que juega en contra: la
  v8 §2.3 pide bordillo y bajantes en terraplén de más de 1.5 m). (Dudoso 2) el n sale de la
  Tabla Nº 32 —la del numeral de cunetas— y el paso nombra la Tabla Nº 09 como la alternativa
  que el mismo apartado ofrece (cita `MC_HHD.4.1.2.1#T09`). (Dudoso 3) la nota «* Para flujos de
  muy corta duración» de las filas de concreto y mampostería se imprime **desde el registro**
  cuando el revestimiento es una de ellas, con la lectura de que el extremo inferior es el
  conservador: la fuente no da otro valor para un flujo prolongado. (H6) la ficha de
  `revestimiento_cuneta` dice que el concreto es, para la longitud, el extremo **menos**
  conservador de la ventana.
- **Qué haría falta:** el modelo de la cuneta en terraplén (bordillo y bajantes) si el proyecto
  tiene alivios cuyo tramo entero va en terraplén.
- **Dónde vive:** `src/normativa/citas.py::INTERPRETACION_CUNETA_DEL_TRAMO`

## T9-10 · Las correcciones de T-9 se escribieron después del código; el rojo se midió contra la FASE A

- **Qué se difirió:** el orden de la casa (rojo con `xfail(strict=True)` y liberar).
- **Por qué:** se dice en vez de reconstruirlo. `tests/test_t9_correcciones.py` se corrió
  contra un árbol exportado de `304cea6` (la FASE A de T-9) con el caso patrón nuevo copiado:
  de sus 66 tests de entonces, **62 en rojo y 4 verdes** (los 21 `test_mut_*` que sumó la
  integración se midieron en rojo contra sus mutantes: ficha T9-11), que valen antes y después y son guardias —el dorado
  de `caudal_a_velocidad` con Z2 ≠ 1 (la fórmula era correcta; el test mata el mutante que la
  auditoría dejó vivo), la progresiva 0 aceptada por VB1, la sensibilidad de Z2 que la ficha
  declara, y los riesgos de la Tabla Nº 02 y la Tabla 304.12 leídos de su página—. Los tests de
  `tests/test_t9_espaciamiento.py`, `tests/test_guia_perfil.py` y los demás que cambian de
  verdad se reescribieron **declarándolo** en su docstring (qué fijaban, por qué era el
  síntoma o qué decisión lo cambia, qué fijan ahora). M10 sale de la exención de caso patrón
  (H8): su dorado es `CP_T9_CUNETA`.
- **Qué haría falta:** nada que se pueda rehacer.
- **Dónde vive:** `tests/fixtures/casos_patron.py::CP_T9_CUNETA`

## T9-11 · La mutación de la integración: 262 de 288 en M10 y 78 de 78 en la Fase 10 de `servicio`; los vivos, censados

- **Qué se difirió:** cerrar con un test los mutantes vivos que son banda de tolerancia,
  guardias inalcanzables, presentación o equivalentes.
- **Por qué:** el arnés de EXT-11 (`tests/apoyo/mutacion.py`), sobre una copia del árbol
  fusionado con `tests/test_t9_correcciones.py`, `tests/test_t9_espaciamiento.py` y
  `tests/test_M10_espaciamiento.py` de objetivos: primera medida 240/288 en M10 (83.3 %) y
  66/78 en `_fase_10`, `_aporte_del_punto`, `extremos_de_los_tramos`,
  `_verificar_tramos_de_alivio`, `_texto_periodo_retorno` y `claves_de_la_cuneta_necesarias`
  (84.6 %). Los vivos que cambiaban conducta o texto se cerraron con los tests `test_mut_*`
  —entre ellos uno REAL: el extremo se resolvía también para las obras A y C, y eso
  enmascaraba un `solo` invertido; desde aquí sólo se resuelve para los alivios—: remedido,
  261/288 y 77/78, y los dos que quedaban con conducta murieron con dos tests más (medido
  aplicando cada mutante a mano): **262/288 (91.0 %) y 78/78**. Los 26 vivos de M10: diez de
  banda de tolerancia o igualdad (`>=` por `>` y `<=` por `<` frente a `TOL_UMBRAL_NORMATIVO`
  en el talud interior, VB1, VB2, el inicio del tramo, su hueco y la longitud implícita;
  `Q_v <= Q_llena`); diez de las guardias `LimiteNumericoError` de la capacidad y de las dos
  longitudes, que ningún dato válido alcanza (cada dato es finito y positivo); tres de
  presentación (`CIFRAS_FINA + CIFRAS_FACTOR`); y tres equivalentes (`return ''` por `None`
  donde quien llama sólo mira la verdad del texto o la nota siempre existe, y `o[0]` por `o[1]`
  en los nodos, porque el alivio es de Familia B y entra igual).
- **Qué haría falta:** ampliar el censo de supervivientes con razón por función (es de T-10,
  como en T8-06).
- **Dónde vive:** `tests/test_t9_correcciones.py::test_mut_las_fronteras_de_la_tabla_304_12_son_las_de_la_tabla`

# Parte XLIX — Lo que T-7a de la cadena T dejó escrito: el cabezal por punto y sus aleros

T-7a (2026-11-12) hace que la Fase 9 deje de ser «del proyecto»: cada punto dimensionado
tiene dos cabezales (entrada y salida) con su geometría propuesta por reglas declaradas,
sus aleros, su losa de entrega con dentellón y la verificación de que rematan al conducto
(`INF-4.1`, `INF-4.2`, `INF-4.3`, `INF-5.1.15`). No verifica estabilidad ni arma: eso es
T-7b y T-7c. Una auditoría adversarial (2026-11-13, AJUSTADO: 2 ALTA, 6 MEDIA, 2 BAJA)
refutó dos cosas de la FASE A —la fórmula de los aleros con esviaje y la premisa de la
decisión 4 del dueño— y las correcciones las aplicaron; las fichas de abajo están escritas
sobre el árbol corregido, y cada una dice qué cambió.

## T7A-01 · La Fase 9 por punto no se alcanza en una corrida de expediente: la detienen TRES capas, y abrir la puerta de `ancho_derecho_via_m` no quita ninguna

- **Cerrada en T-7b (PUNTO 0):** las tres capas se atraviesan declarando, sin valor de
  archivo: el método de V5, su dato `ancho_derecho_via_m` (con puerta) y los de V8. Lo
  mide `test_A01_llega_a_la_Fase_9_con_E1_a_E3_evaluadas` de
  `tests/test_t7b_cabezal_estabilidad.py`. Lo que sigue describe el estado de archivo.
- **Qué se difirió:** que una corrida `--alcance expediente` real imprima el cabezal de un
  punto. La Fase 9 propone sobre la sección adoptada y las cotas de 7.B, y a expediente
  ningún punto del fixture se dimensiona. La FASE A lo atribuyó a que «V5 se detiene en
  `ancho_derecho_via_m`, que no tiene puerta», y la decisión 4 del dueño (abrir esa puerta
  como dato externo opcional) partía de esa premisa. **La auditoría la refutó y las
  correcciones la midieron** (`tests/test_t7a_correcciones.py::test_h2_las_tres_capas_que_detienen_la_fase_9_a_expediente`):
  (1) A-01, A-02 y B-01 se detienen ANTES, en el criterio `remanso_derecho_via` [A] sin
  valor (`CriterioPendienteError` en el bucle de MD); (2) con ese criterio declarado,
  `M5.v5_remanso` levanta `DatoFaltanteError('ancho_derecho_via_m')` SIN CONDICIÓN: no lee
  el dato, porque no hay método de remanso con que compararlo; (3) aunque V5 cumpliera
  (simulada), A-01 y A-02 se detienen en V8, en `TR_evento_extremo` sin valor, y detrás
  falta el caudal del evento extremo (ficha T1-03); C-01, con los siete del cajón, también
  se detiene en V8. **La decisión 4 NO se aplicó**: un dato sin lector no se abre, y abrir
  la puerta no habría hecho alcanzable la Fase 9. Hoy ningún test recorre la Fase 9 por la
  ruta real de expediente: todos la llaman por `servicio._fase_9` sobre un punto que la
  corrida de PERFIL dimensiona (A-01, A-02 y el marco C-01).
- **Por qué:** el encargo de T-7a es expreso en que la Fase 9 es de nivel EXPEDIENTE y no
  se corre a perfil; la etapa existe y es la misma que usaría la corrida de expediente.
  Lo que la cierra no es de T-7a.
- **Qué haría falta:** las tres cosas, juntas, y el dueño las asignó a **T-7b** como su
  primer punto (2026-11-13): el método de V5 como opción DECLARABLE sin valor por defecto
  (que entonces sí lee `ancho_derecho_via_m`, y ahí se abre su puerta), el valor de
  `remanso_derecho_via`, y el TR y el caudal del evento extremo de V8 declarados. Sin
  ellos V5 sigue bloqueando como hoy. Mientras tanto `INF-4.2` e `INF-4.3` quedan «en
  parte»: la función, la memoria y los tests existen sobre `servicio._fase_9`, y el
  residual es que una corrida de expediente la alcance.
- **Dónde vive:** `src/servicio.py::_fase_9`

## T7A-02 · La embocadura es de perfil y gobierna la coherencia del marco; en el tubo la fuente no distingue y nada se mueve; la caja receptora no se modela y se avisa

- **Cerrado (T-7a):** `embocadura_cabezal` [A] y `angulo_aletas` [A] (45° / 30° si el
  esviaje supera 30°) se resuelven antes de la Fase 4 en los dos alcances
  (`M9.embocadura_del_punto`). En un marco, la carta de la Tabla A.1 y la fila de la C.2
  declaradas tienen que ser de la banda de ángulo del cabezal
  (`BANDAS_ALETAS_CAJON_A1/_C2`, leídas del rótulo de cada fila); si no, el punto se
  detiene y el bucle de MD no corre. Con las filas coherentes M4 calcula con ellas (C-01
  recto: HW 0.6234 → 0.6391 m). En un TUBO la Tabla C.2 agrupa «Headwall or headwall and
  wingwalls» y las Cartas 1 a 3 no separan aleros: nada se mueve (ficha T2-04). Con la
  embocadura del marco de 30–75° que T-3 dejó de archivo (Carta 8 escala 1, ke 0.4) la
  coherencia se cumple en toda la ventana de α y C-01 sigue en marco 1.20 × 0.90 con el
  HW de T-3; su nota es un DATO del punto (JSON, paso 9.0.0), no un aviso.
- **Abierto:** (1) en la ventana de α (30–60°) el ke del cajón no cambia; la carta sí,
  en las Cartas 9, 12 y 13. (2) Las filas de cabezal esviado (Carta 11) o de barril
  esviado (Carta 12, escala 3: su banda se quitó en las correcciones, H9) no casan con el
  cabezal normal al eje. (3) **La CAJA RECEPTORA no está en el catálogo**: la Lámina Nº
  02-A la dibuja sin aleros y es la entrada habitual de un alivio de cuneta; la rama «60°
  en caja receptora» del encargo no se adoptó (decisión 3 del dueño) y desde las
  correcciones **cada punto de la Familia B lo AVISA** (`EmbocaduraDelPunto.avisos`): su
  pérdida de entrada, su protección y su cabezal de entrada salen de una embocadura que no
  es la suya. (4) La coherencia se decide por la FAMILIA (corre antes de que exista la
  sección); equivale a la forma mientras M2 solo dé el marco a la Familia C, y un test lo
  fija.
- **Qué haría falta:** para (3), una embocadura «caja receptora» con su hidráulica (un
  drop inlet no está en las Tablas A.1 y C.2 del HDS-5) y su geometría.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::verificar_coherencia_embocadura_cajon`

## T7A-03 · Los aleros llevan el coseno de su ángulo con la bajada del talud: con esviaje, los dos aleros de un cabezal miden distinto

- **Verificado en T-7b:** el HDS-5 núm. 5.4.2, pág. impresa 5.13 (PDF 149), dice que
  los cabezales se construyen generalmente paralelos al eje de la vía y que esa
  embocadura esviada debe evitarse cuando se pueda (citas `HDS5_3ED.5.4.2#PARALELO` y
  `#EVITAR`): sostiene el cabezal normal al eje y deja diferido el paralelo.
- **Cerrado (T-7a, corregido en H1):** α se mide con la prolongación de la pared del barril
  (ΘW del HDS-5, List of Symbols, pág. impresa xix; cita `HDS5_3ED.SIMBOLOS#THETA_W`): por
  eso coseno y no seno. La FASE A daba la misma longitud a los dos aleros y decía «los
  aleros absorben el giro»; la auditoría lo refutó. El talud baja PERPENDICULAR A LA VÍA
  (como en `M7.longitud_conducto`) y el eje forma θ con esa dirección: con el cabezal
  normal al eje, un alero forma α − θ con la bajada del talud y el otro α + θ, y
  `L = (h0 − H_f)·talud / cos(α ∓ θ)`. En la entrada de A-01 (θ 15°, α 45°): 2.425 y
  4.200 m, donde la FASE A daba 2.970 m a los dos. El CSV da la magnitud del esviaje, no
  su sentido: «corto» y «largo», y el lado lo fija la planta. Con α + θ ≥ 90°,
  `LimiteNumericoError` con el par y su remedio. Un muro normal al eje deja el talud a
  cotas distintas en sus extremos, Δz = L_c·sen θ/talud (0.22 m en A-01), y se AVISA.
- **Abierto:** (1) **el cabezal PARALELO A LA VÍA**, que haría coincidir corona y talud:
  el dueño (2026-11-13) dejó el NORMAL AL EJE como el de archivo en las tres familias —es
  lo que supone la hidráulica del HDS-5— y el paralelo como alternativa SOLO para el marco
  (filas de la **Carta 11**, hoy sin banda), diferida a un paso posterior a T-7c: cambiaría
  la carta y el HW de C-01. Mientras tanto el alero largo (8.1 m en C-01) se acorta
  declarando un α menor de ese lado (`cabezal_declarado.angulo_alero_largo_grados`,
  aleros asimétricos; con un marco el ke y la carta siguen con el α de la regla, y se
  avisa). (2) **Aviso para T-7b:** la orientación está acoplada con el [S]
  `orientacion_muro_respecto_al_trafico` y con el conflicto #4, y T-7b verifica qué dice
  el HDS-5 núm. 5.4.2 de las embocaduras esviadas. (3) «/ sen α» del encargo: solo
  coincide a 45° sin esviaje.
- **VE-6:** el abierto (1) queda cerrado para el marco con las filas de la Carta 11 (ficha
  VE6-T7A03); siguen el aleros-con-barril-esviado de la Carta 12 escala 3 y el (2).
- **Qué haría falta:** la banda de la Carta 11 y el paso posterior a T-7c; corregir la
  frase del INFORME, que no es de este repositorio.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::predimensionar_aleros`

## T7A-04 · Las reglas del predimensionamiento son [A] en el extremo de más material, y eso NO es el lado seguro de la estabilidad

- **Cerrado (T-7a):** `predimensionamiento_cabezal` guarda trece reglas con ventana por
  campo (encargo e INFORME §4.2–§4.3), en el extremo de más material (pantalla 0.30 m,
  H/6, B = 0.7·H, peralte H/10, losa 1.5·D y 0.30 m). Lo que tiene número va aparte: 0.30
  m de E.060 22.7.4 ([N]), 0.80 m de E.050 26.2 y el piso de la zapata armada de E.060
  15.7 ([N→], ficha T7A-08), 2.0 ft de AASHTO 12.6.5 ([C]) y el dentellón de la Lámina Nº
  04 ([N→]). Lo que la regla calcula desde una dimensión declarada se imprime «derivada».
- **Abierto:** (1) **«Más material» no es el lado seguro** (H10): con kh = 0.50 y μ = tan
  20° = 0.364 < kh, cada kN de muro suma más fuerza que desliza que resistencia y la masa
  **empeora** el deslizamiento sísmico; depende de φ, que el EMS no ha dado: lo evalúa
  T-7b. (2) **El umbral «gravedad hasta 2.0 m» se mide sobre la altura TOTAL** (desplante
  incluido) y con altura interior ≥ 0.90 m la mínima es 2.15 m más la pared: **todo
  cabezal sale voladizo armado**; el umbral no se cambia (alternativa en su ventana,
  hasta 2.5 m) y la corrida lo AVISA (H7). Si sale gravedad, E.060 22.10.2.1–22.10.2.2
  (pág. 195) limitan el ciclópeo a muros de gravedad y piden flexión y corte en voladizos:
  se avisa y lo juzga T-7c. (3) El PDF de VARIOS (pp. 18 y 42) no está en `normas/`: el
  origen de «H/8–H/6» como pantalla de gravedad **no se pudo verificar**, y sigue [A]. (4)
  E.060 14.5.3.2 (200 mm) es del método empírico de muros de carga: no se aplica. (5) Un
  solo terreno por extremo para desplante, dentellón y aleros: la solera en la entrada y
  la más baja entre solera y receptor en la salida (decisión 2 del dueño). (6) E.060
  22.7.4 queda [N] por la §9.4 de la hoja; la objeción de ámbito que hace [N→] a E.050
  alcanzaría a E.060, y el dueño la remitió a T-7c (2026-11-13).
- **Qué haría falta:** el plano tipo de cabezal, el EMS (φ) para que T-7b diga si el
  material de más ayuda, o el PDF de VARIOS en `normas/`.
- **Dónde vive:** `src/criterios/cabezal_base.py::predimensionamiento_cabezal`

## T7A-05 · El desplante de salida y el dentellón bajan hasta la socavación con el margen de AASHTO 12.6.5, leído como aplicable al cabezal

- **Cerrado (T-7a, corregido en H3 y H4):** `D_f = max(0.80 m, pie − (fondo de la hoya −
  margen))`, con la hoya que entrega la Fase 6 (T-8; la declarada gana). **El dentellón
  se mide desde el TERRENO del pie**, no desde la cara superior de la losa: la cota «0.80
  min.» de la Lámina Nº 04 (pág. impresa 210, PDF 213, releída por imagen) arranca en la
  superficie del terreno natural junto al dentellón —allí la cara inferior del paquete
  losa + relleno granular— y llega a su base. La FASE A la medía desde la losa, a la cota
  de la solera, y en la salida de A-01 la base quedaba 0.11 m bajo el lecho receptor
  (41.187); con una sola referencia por extremo queda en 40.50. A la salida con hoya, la
  base del dentellón baja a min(pie − 0.80, hoya − margen): AASHTO 12.6.5 pide el
  «cut-off wall … extending below the maximum anticipated depth of scour» sin cifra, y el
  proyecto le aplica el margen de 2.0 ft que el mismo artículo da a las zapatas (antes
  llegaba AL fondo de la hoya, con margen 0). Verificaciones CB4 (E.050, por analogía), CB5
  (AASHTO, la zapata), CB6 (el espesor de la zapata contra el mínimo de su tipo) y CB7 (la
  base del dentellón contra el terreno y la hoya): las dos últimas, nuevas en las
  correcciones (H4), porque una dimensión DECLARADA podía violar un mínimo con número y
  ninguna verificación lo decía.
- **Abierto:** (1) que la zapata de un cabezal sea una de las «footings of structures» del
  12.6.5, y que el margen valga también para el dentellón, es lectura del proyecto, del
  lado seguro: está declarada como `Interpretacion` de la cita
  `AASHTO_LRFD_9.12.6.5#ZAPATAS`, con lo que juega en contra, y por eso el margen es [C]
  con ventana (0 de AASHTO 10.6.1.2 y HEC-14 5.1.3; 0.6096 m de 12.6.5). (2) Sin el lecho
  ni una profundidad declarada no hay hoya: el desplante de salida queda con 0.80 m y la
  corrida lo AVISA con el motivo que la Fase 6 dio (desde las correcciones, también cuando
  la etapa de la Fase 6 se bloqueó). (3) En la entrada no se estima socavación (HEC-14 Cap.
  5 es de la salida).
- **Qué haría falta:** el EMS del lecho por punto (`material_lecho_salida`) o un estudio
  de socavación (`profundidad_socavacion_estimada_m`).
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::predimensionar_cabezal`

## T7A-06 · La longitud entre cabezales queda cerrada con el relleno retenido, da también la de metrado, y no sustituye a la del diseño

- **Cerrado (T-7a, corregido en H6):** la ficha T6-01 pedía la coronación del cabezal para
  cerrar la longitud entre cabezales. **El talud muere en el RELLENO que cada muro retiene
  —la coronación menos el bordillo, que por definición sobresale—, contra la cara
  interior (trasdós) del muro**: `L_cab = [ancho + talud·(borde_e − rel_e + borde_s −
  rel_s)] / cos(esviaje)`, paso 9.0.5. La FASE A lo hacía morir en la corona del bordillo:
  en A-01 daba 12.865 m y ahora 13.486 m (frente a 18.869 m al fondo y 14.676 m a la
  clave). La longitud de METRADO del barril suma el espesor de los dos muros, normales al
  eje: 14.086 m en A-01. Las alturas de los aleros se miden con el mismo criterio: h0 y
  H_f son alturas del alero sobre el pie con su bordillo, de modo que h0 − H_f es la caída
  del talud; si H_f se leyera sobre el talud los aleros saldrían más cortos, y la lectura
  adoptada es la de más longitud.
- **Abierto:** la coronación de salida se fija con la cota de salida de 7.B, que sale de la
  longitud aproximada; con la longitud entre cabezales el muro de salida queda unos 2.7 m
  más cerca de la vía y la solera bajo él sube S·ΔL: **centímetros**, no milímetros como
  decía la FASE A (1.6 cm en A-01, con S = 0.006), y no se itera. El control de salida
  sigue con la aproximada (T6-01 sigue abierta en esa mitad).
- **Qué haría falta:** `L` por sección en MD, o declarar `longitud_m` por punto.
- **VE-6 (ítem 22 del censo):** la mitad del control de salida queda cerrada con la pasada de
  refinamiento de la ficha VE6-22; la coronación de salida sigue sin iterarse.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::longitud_entre_cabezales`

## T7A-07 · La aceptación de T-7a se escribió después del código; el rojo se midió contra la base

- **Qué se difirió:** el orden de la casa (rojo con `xfail(strict=True)` y liberar), en
  la FASE A y en las correcciones.
- **Por qué:** se dice en vez de reconstruirlo. El rojo de la FASE A se midió copiando
  `tests/test_t7a_cabezal_geometria.py` a un checkout de `df1b23c`; el de las correcciones,
  copiando `tests/test_t7a_correcciones.py` a un checkout de la FASE A (`1b83d39`). Los
  oráculos son la aritmética escrita en cada test, no la fórmula cerrada del código. Once
  tests de la FASE A se reescribieron a la verdad nueva DECLARÁNDOLO en su docstring (el
  piso de la zapata armada, los dos aleros, el dentellón, CB6/CB7, el origen «derivada»,
  la longitud al relleno, E.050 [N→]).
  La mutación de las 17 funciones de la Fase 9 del punto con el arnés de EXT-11: 275/326
  muertos con la primera tanda (la FASE A, 185/226); con la segunda tanda de
  `test_t7a_correcciones.py`, escrita contra los supervivientes, 309/326, y uno más muerto
  después a mano. Los 16 vivos son de frontera contra `TOL_UMBRAL_NORMATIVO`, de texto o
  equivalentes en el dominio.
- **Qué haría falta:** nada que se pueda rehacer.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::cabezal_del_punto`

## T7A-08 · Los mínimos de E.050 y de E.060 15.7 son [N→] para un cabezal vial, y la hoja de ruta los rotula [N]

- **Cerrado (correcciones de T-7a, H8 y dudoso 4):** el ámbito de E.050 son las
  edificaciones del RNE (Art. 1 y 3, pág. 7) y la FASE A escribía su 0.80 m de profundidad
  mínima (Art. 26.2, pág. 38) como [N] en `constantes_normativas` y CB4 como «EXIGENCIA de
  E.050». Pasa a criterio [N→] `profundidad_cimentacion_min_cabezal_m` con la analogía
  declarada —lo que la hace cercana es que la misma norma manda que el muro de contención
  cumpla su Capítulo IV (39.13.7, pág. 73), donde está el Art. 26— y una `Interpretacion`
  en la cita con lo que juega en contra; CB4 dice «por analogía». Y el peralte mínimo de la
  zapata ARMADA, verificado en E.060 15.7 (pág. 138: «La altura de las zapatas, medida
  sobre el refuerzo inferior no debe ser menor de 300 mm para zapatas apoyadas sobre el
  suelo»), entra como piso del espesor propuesto del voladizo armado, [N→]
  (`peralte_min_zapata_armada_m`), más los 70 mm de recubrimiento contra el suelo de 7.7.1
  a): `e_z = max(H/10, 0.37 m)`; en la entrada de A-01 la regla daba 0.225 m.
  **Corregido en la verificación de fórmulas (punto 7):** ese 0.37 m no podía cumplir
  nunca la norma que cita tal como la fila A8 del armado la mide; el piso suma ahora el
  recubrimiento con que se arma y medio diámetro de la mayor barra del catálogo (0.4041 m
  con la cota de recubrimiento, 0.3827 m con 70 mm; ficha T7V-03).
- **Abierto:** la tabla de la §0.1 de la hoja de ruta rotula E.050 como [N] para
  «Capacidad portante, FS de muros…» sin la salvedad del ámbito: **es un defecto de la
  hoja**, declarado en ella con una nota, y la hoja sigue mal en su §9.3 («Estabilidad —
  E.050 [N]») mientras T-7b no la corrija al decidir el marco de estabilidad. Quien la lea
  sin leer el código pensará que E.050 rige el cabezal vial como norma propia.
- **Qué haría falta:** que T-7b corrija la §9.3 al ensamblar la estabilidad (el dictamen
  del verificador ya lo pide).
- **Dónde vive:** `src/criterios/cabezal_base.py::profundidad_cimentacion_min_cabezal_m`

# Parte L — Lo que T-7b de la cadena T dejó escrito: la estabilidad del cabezal en dos marcos, y V5 y V8 con método declarable

T-7b (2026-11-13, FASE A) ensambla la estabilidad externa de cada cabezal —capacidad
portante, excentricidad o volteo, y deslizamiento, estática y sísmica— en dos marcos que
no se cruzan (`INF-4.4`, `INF-4.5`, `INF-5.1.5`), y abre lo que hacía inalcanzable la
Fase 9 a nivel de expediente: V5 y V8 con método declarable y sus datos por punto (el
PUNTO 0 de las precisiones; residual de `INF-4.2` e `INF-4.3`). No arma: eso es T-7c.
Las fichas de abajo son lo que el ensamble **no** hace, lo que hace por hipótesis del
proyecto, y lo que la corrida de punta a punta dejó medido. **El cierre de T-7b
(2026-11-13) aplicó las diez correcciones de la auditoría adversarial (H1 a H10) y las
resoluciones del orquestador**: cada ficha que cambió lo dice en un párrafo «Corrección
del cierre», y las dos fichas nuevas (T7B-13, T7B-14) son la medida del cierre y la
marca del régimen para T-7c.

## T7B-01 · V5 mide el embalse con un plano horizontal: el perfil de remanso está nombrado y no implementado

- **Qué se difirió:** el método `perfil_de_remanso_paso_a_paso` de `remanso_derecho_via`.
  Declarado, V5 se detiene con `MetodoNoEvaluableError` (rótulo
  `MOTIVO_METODO_NO_EVALUABLE_REMANSO`). El implementado, `embalse_a_nivel`, compara
  d = (L_boca + HW / S_cauce)·cos(esviaje) con la mitad del ancho del derecho de vía.
- **Por qué:** la curva de remanso exige la sección y la pendiente del cauce de
  aproximación y su topografía, que no son entradas del programa. El plano horizontal
  usa solo lo que ya hay (HW, `S_cauce`, la semilongitud de entrada de 7.B y el esviaje)
  y dice sus cinco supuestos en el paso: fondo recto con `S_cauce` en la dirección del
  eje, faja simétrica, sin topografía lateral, y que **no es** la curva de remanso —en
  un cauce de pendiente suave el perfil real llega más lejos, y el programa no clasifica
  el régimen del cauce de aproximación ni presume el lado—. (La corrección del cierre,
  abajo, añade el sexto: el plano corta el **fondo**.) El HDS-5 núm. 2.2.5
  identifica la carga con la profundidad del embalse; la extensión es método del
  proyecto. No se le dio valor de archivo al criterio: decisión del dueño.
- **Qué haría falta:** decidir si el ancho se mide simétrico o con el eje de la faja
  declarado (la sección y el paso directo los trajo VE-4c, abajo).
- **Corrección del cierre (H2, ALTA).** `embalse_a_nivel` mide hasta donde el plano
  corta el **fondo**: incluye el tramo natural del cauce, es una **cota superior** de lo
  que la obra añade y con los anchos de la Tabla 304.09 solo cumple en cauces de
  pendiente fuerte (A-01: d = 176.75 m). Restar el tirante natural exige la sección del
  cauce de aproximación: **diferido**. El método que la fuente sí sostiene (HDS-5 núm.
  2.2.5, citas `HDS5_3ED.2.2.5#NO_EXCEDER` y `HDS5_3ED.2.2.5a#COTA_DE_DANO`) es de
  **cota**: `cota_de_afectacion` (`M5._v5_cota_de_afectacion`, dato
  `cota_afectacion_aguas_arriba_msnm`). El criterio sigue sin valor de archivo.
- **Cerrado (VE-4c, 2026-11-20):** implementado (`M5._v5_perfil_de_remanso`, `F5.V5_PERFIL`):
  mide hasta dónde la obra eleva la lámina del cauce de aproximación más de Δ
  (`sobreelevacion_admisible_remanso_m` [A], sin valor, 0–0.30 m) sobre su tirante normal,
  por el paso directo de VE-3.7 desde la boca (`M3.remanso_aguas_arriba`), sobre el dato
  externo `seccion_cauce_aproximacion`. Validado contra el USBR (`CP_VE4C_USBR_WSP`).
  **Abierto:** faja simétrica, sección prismática, tirante natural normal.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v5_remanso`

## T7B-02 · V8 juzga «no colapsa» por el desborde de la plataforma, que es la lectura más exigente; el desborde admitido no estaba implementado (lo está desde VE-4d)

- **Qué se difirió:** el umbral `desborde_admitido_con_terraplen_protegido` —lo que la
  fila V8 literalmente admite— y el flujo a presión o sobre la vía con el caudal del
  evento extremo. V8 levantaba `MetodoNoEvaluableError`
  (`MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO`).
- **Por qué:** a V8 le faltaban el método y el umbral: la hoja no dice cómo se juzga el
  colapso. Se escribió lo mínimo que no inventa nada —cota de entrada + HW(Q_ext) ≤ cota
  del borde de la plataforma— con el umbral **sin valor**.
- **Qué haría falta (y qué se hizo):** el flujo a presión llegó en el cierre de T-7b
  (H3, `M4.hidraulica_a_presion`; V8 sólo sobre el candidato que ya cumple lo anterior,
  y no deja en «no evaluable» un punto que V5 descarta; con ×1.97 el caudal de A-01
  desborda el Ø 0.90 m y MD adopta Ø 1.05 m) y compite con el perfil de la lámina desde
  la verificación de fórmulas (ficha T7V-01). **El desborde admitido, en VE-4d (2026-11-20):** el caudal se reparte entre
  el conducto y la plataforma por tanteo (`M4.repartir_caudal_con_desborde`, HDS-5 núm.
  3.1.5, Ec. 3.9) con la Figura 3.11 digitalizada (`coeficientes_desborde_plataforma`
  [C]), la cresta como un tramo horizontal de longitud declarada
  (`longitud_cresta_desborde_m`) y «no colapsa» como caudal unitario ≤
  `caudal_unitario_admisible_desborde_m2s` [A], **sin valor de archivo**: la fuente
  acepta el desborde (núm. 5.4.5) y remite la protección a HEC-23, ausente del
  repositorio de normas. Validado contra el DG 1.5 del HDS-5 y su solución HY-8
  (`tests/test_ve4d_v8_desborde.py`). Con los datos de archivo nada cambia.
  **Sigue diferido** (el docstring de `_v8_con_desborde` lo detalla): el diseño de la
  protección y el sifonamiento; la cresta que crece con el nivel (Figura 3.12A); el
  tirante y la velocidad sobre la vía; el reparto por debajo del caudal de diseño y el
  coeficiente fuera de los ejes de la figura, que se detienen con «método no evaluable».
  Y que el Propietario declare el periodo de retorno y el caudal unitario admisible.
- **VE-5 fixve4:** cada raíz del tanteo se comprueba (la carga de M4 salta: «método no
  evaluable»); C_r en SI con `K_CD_DESBORDE_SI`; el tirante hidráulico del tramo único
  queda declarado (en_contra de `HDS5_3ED.3.1.5#UN_TRAMO`); el pre-vuelo pide también
  `TR_evento_extremo` (`servicio.CRITERIOS_PREVIOS_DE_LA_CLAVE`).
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v8_evento_extremo`

## T7B-03 · El cabezal se calcula como muro de semigravedad en voladizo, por metro y en la sección llena: es hipótesis del proyecto

- **Qué se difirió:** modelar el cabezal como lo que es —un muro corto, con el vano del
  conducto, restringido por el barril y por los aleros—. El ensamble toma un metro de
  muro en la sección llena junto al conducto: no descuenta el vano (menos peso y menos
  empuje), no cuenta la restricción del barril ni la de los aleros, no cuenta empuje
  pasivo delante de la zapata (AASHTO 11.6.3.5) ni el agua del cauce contra la cara
  frontal. Con esviaje, el empuje se toma normal al muro.
- **Por qué:** ninguna fuente de `normas/` prescribe el marco de estabilidad de un
  cabezal: la Sección 12 de AASHTO trata la estructura enterrada, y la 11.6 los
  estribos y muros convencionales. La decisión del dueño (rige el LRFD de 11.6, E.050
  informa) fija el marco; aplicarlo a un cabezal es analogía, y `marco_estabilidad_cabezal`
  lo dice. Las simplificaciones van del lado de más demanda, salvo el vano, que quita
  peso estabilizante y empuje a la vez y cuyo signo no se midió.
- **Qué haría falta:** un modelo de placa o de pórtico con el barril, o al menos la
  franja del vano con su carga del conducto; y decidir si los aleros cuentan como
  contrafuertes.
- **Corrección del cierre (H6).** Con el drenaje declarado (`drenado`) el modelo toma el
  agua del relleno en el freático natural y **no** el desembalse rápido —el relleno
  mojado por la avenida hasta la cota del agua de diseño con el cauce ya vacío—, que
  el comentario C11.6.6 hace plausible («Weep holes … do not assure fully drained
  conditions»). El ensamble lo **avisa** con su orden de magnitud
  (`M9._aviso_desembalse_rapido`: en la entrada de A-01, con el agua de diseño a 1.84 m
  sobre la base, γ_w·h²/2 ≈ 16.6 kN/m frente a 15.6 kN/m de la componente horizontal
  del empuje con la cuña). Modelarlo exige decidir el nivel residual del relleno tras la avenida.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad.py::ensamble_estabilidad`

## T7B-04 · La capacidad portante es la de terreno horizontal, zapata corrida y sin factor de profundidad; las tablas de talud de AASHTO no se transcribieron

- **Qué se difirió:** tres cosas. (1) Los coeficientes de reducción por talud de AASHTO
  LRFD 10.6.3.1.2c (9.ª ed.), que son **tablas** —no las figuras N_cq / N_γq de
  Meyerhof, que son las de la edición que tradujo el Manual de Puentes 2016—: no se
  transcribieron. (2) Los factores de forma (zapata corrida: 1) y de profundidad
  (d_q = 1). (3) La lectura entre filas de las Tablas 10.6.3.1.2a-1 y -2, que se
  interpola linealmente.
- **Por qué:** la hoja de ruta (§9.3) afirmaba que el cabezal «se apoya en el borde del
  terraplén». Con el cabezal que T-7a predimensiona eso no es así: la zapata queda bajo
  el fondo del cauce y el talud **sube** detrás; delante el terreno no desciende, y la
  reducción de la fuente se define con la altura del talud por debajo de la base, que es
  cero. Es una **discrepancia con la hoja de ruta, declarada en ella** (nota de §9.3) y
  en el punto de uso (`terreno_delante_del_cabezal` [A] = `horizontal`); quien tenga un
  cabezal en media ladera declara `talud_descendente` y la ecuación del Manual de
  Puentes pide `N_cq_N_gammaq_meyerhof`, que sigue sin valor. Los factores de
  inclinación de la carga se **aplican** (`factores_inclinacion_carga_portante` [A]):
  el comentario de la fuente admite omitirlos con empotramiento modesto y aplicarlos no
  relaja. La hoya de socavación de la Fase 6 descuenta el empotramiento a la salida.
- **Qué haría falta:** transcribir las tablas de 10.6.3.1.2c con su verificación contra
  el PDF si aparece un cabezal en ladera; y el EMS, que con `q_n_kpa` o `q_adm_kpa`
  gana sobre todo esto.
- **VE-5 (lote M9):** cerrados (1), (2) y la admisible suelta; ver la ficha VE5M9-03.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::resistencia_portante_nominal`

## T7B-05 · Sin drenaje declarado el relleno se calcula lleno de agua: es el valor de archivo, y deja la condición sísmica sin evaluar

- **Qué se difirió:** nada del cálculo; lo que queda abierto es **cuál debe ser el
  valor de archivo** de `drenaje_trasdos`. Rige `sin_drenaje`: agua hasta la superficie
  del relleno retenido (AASHTO 11.6.6: si no se provee drenaje el muro se diseña para
  la presión del agua), que además exige el peso saturado del relleno (dato de ensayo,
  sin valor) y deja Mononobe-Okabe fuera de su dominio (11.6.5.3: relleno no saturado).
- **Por qué:** el encargo de T-7b dice que la presión solo se reduce si el drenaje se
  **declara**, y así quedó. Pero las dos normas piden el drenaje (AASHTO 11.6.6 y E.050
  39.13.8), los planos tipo lo llevan, y con el valor de archivo ningún cabezal puede
  evaluarse sin dos declaraciones más. Es una pregunta para el dueño, no una decisión
  tomada: la recomendación del ejecutor es `drenado` de archivo, con el aviso de que
  compromete el filtro y los lloraderos en planos.
- **Qué haría falta:** la decisión del dueño; y, si el relleno puede saturarse bajo
  sismo, el tratamiento del agua de C11.6.5.3 (dos casos según la permeabilidad, uno
  con presión hidrodinámica), que no está implementado.
- **Corrección del cierre (H6 y pregunta 1).** Resuelta: `sin_drenaje` **se queda** de
  archivo (AASHTO 11.6.6: «shall be drained or, if drainage cannot be provided … full
  hydrostatic pressure»); `drenado` es una declaración que compromete el filtro y los
  lloraderos en planos y se declara en la sesión o con `--declarar`. Y el **tope del
  agua** sin drenaje se corrigió: llena el relleno **retenido** hasta su superficie
  contra el trasdós (coronación menos bordillo, z_rel), **nunca por encima del muro**;
  la FASE A la subía hasta el terreno sobre el extremo del talón (en la entrada de A-01,
  43.78 msnm contra 43.55 de la coronación). `HIPOTESIS_EMPUJE_BAJO_NF` dice lo mismo.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::drenaje_trasdos`

## T7B-06 · Mononobe-Okabe solo dentro de su dominio: con el k_h de archivo la condición sísmica no se evalúa

- **Qué se difirió:** el método de equilibrio límite generalizado (GLE, AASHTO A11.3.3)
  y el análisis de cuña, que la fuente pide cuando φ < i + arctan[k_h/(1 − k_v)] o el
  relleno no es homogéneo, drenado y sin cohesión. Fuera del dominio el ensamble levanta
  `MetodoNoEvaluableError` (rótulo `MOTIVO_METODO_NO_EVALUABLE_CABEZAL`) y no da cifra.
- **Por qué:** con `factor_muro_eleccion` = `sin_reduccion` (archivo) k_h = k_h0 = 0.50
  y ψ = 26.6°; el relleno detrás del cabezal sube con el talud (i ≈ 9 a 11° en A-01 con
  la regla del talud quebrado), de modo que haría falta φ ≥ 36 a 38°. Con φ = 34° de
  prueba la sísmica queda sin evaluar en los dos cabezales. La fuente desaconseja
  forzar la ecuación. Lo que lo destraba es una decisión del Propietario —admitir el
  desplazamiento del muro, que reduce k_h a la mitad— o un análisis externo.
- **Qué haría falta:** GLE, o la declaración del Propietario; y un contraste externo
  del K_AE con relleno en talud quebrado, que aquí entra con la pendiente equivalente.
- **Corrección del cierre (H4 y pregunta 3).** La cuña de tanteo de Culmann con la
  superficie real es la regla de archivo de `regla_pendiente_relleno_trasdos`
  (`M9.cuna_de_tanteo`; citas `AASHTO_LRFD_9.3.11.5.3#CULMANN`,
  `AASHTO_LRFD_9.3.11.5.8.1#CUNA`, `AASHTO_LRFD_9.C11.6.5.3#CUNA`), estática y
  pseudoestática; la fórmula 2H queda de contraste y barrible (subestima del 7 al 11 % en
  A-01). Dorados en `CP_T7B_CUNA`; los oráculos del auditor se reproducen (59.7 y 98.2
  kN/m con k_h 0.50): **con el k_h de archivo la sísmica da cifra**. `factor_muro_eleccion`
  no cambia. Sigue diferido el GLE.
- **VE-5 (lote M9):** la cuña sobre el trasdós inclinado y fuera del dominio de M-O; ver
  la ficha VE5M9-02.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::cargas_del_cabezal`

## T7B-07 · E4 y E5 (estabilidad global del muro y del talud) se imprimen diferidas al expediente

- **Qué se difirió:** el análisis de superficies de falla. El ensamble las lleva en
  `EstabilidadDelCabezal.pendientes`, con un paso (`F9.GLOBAL`) y un aviso por cabezal;
  no cuentan como cumplidas. `verificar_estabilidad_global` y `verificar_talud`,
  llamadas a mano con `metodo_estabilidad_global` declarado, levantan
  `MetodoNoEvaluableError` (hasta T-7b, `AssertionError`).
- **Por qué:** necesitan la estratigrafía del EMS y un programa de equilibrio límite;
  AASHTO 11.6.3.7 remite al Art. 11.6.2.3 y E.050 39.13.6 b) y 30.3 dan solo el factor
  de seguridad. El punto 4 del encargo las deja «diferidas al expediente con el EMS».
- **Qué haría falta:** el EMS y el análisis externo; el programa solo podría registrar
  su resultado como dato declarado.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad.py::PENDIENTES_E4_E5`
- **Cerrado en parte en VE-4a (decisión del dueño, 2026-11-20):** el resultado del
  análisis externo ya se registra como dato declarado. El punto declara, por cabezal, el FS
  estático y el sísmico de E4 y/o de E5 con el documento, la fecha y el método que los
  sostienen (`estabilidad_global_declarada` de `--datos-externos`, sólo por punto; puerta
  `M9.validar_estabilidad_global_declarada`), y el ensamble los **contrasta** en los dos
  marcos: el ASD contra el FS de E.050 (1.50 / 1.25, 39.13.6 b y Art. 30.3, por analogía) y
  el LRFD contra 1/φ (φ de AASHTO 11.6.3.7 en estática, la fila es el [A]
  `fila_phi_estabilidad_global` sin valor de archivo; 0.9 de 11.5.8 bajo sismo). Lo
  declarado sale de `pendientes`; lo no declarado sigue diferido con su paso y su aviso, y
  sin el dato nada cambia. El programa sigue sin **calcular** E4 ni E5 (no tiene la
  estratigrafía ni un programa de equilibrio límite) y la memoria lo dice en cada paso
  (`F9.GLOBAL_DECLARADA`). Ficha VE4A-01.

## T7B-08 · Las solicitaciones por elemento para T-7c son las de la sección de arranque, con tres aproximaciones declaradas

- **Qué se difirió:** el diagrama de cada elemento. `solicitaciones_por_elemento`
  entrega V_u y M_u de la pantalla en su arranque, de la punta y del talón en la cara
  de la pantalla, y de los aleros, por cada combinación del marco LRFD. Aproximaciones:
  (1) la pantalla recibe la resultante entera de cada empuje, incluido el tramo del
  canto de la zapata (más cortante del que le llega); (2) la presión de contacto se toma
  uniforme sobre B − 2e **arrancando en la punta**, también cuando la resultante cae
  hacia el talón (más carga en la punta y menos alivio en el talón que la real); (3)
  los aleros llevan la solicitación de la pantalla en su arranque, sin su altura
  variable. La subpresión se reparte uniforme en el talón.
- **Por qué:** T-7b no arma; deja la interfaz (`EstabilidadDelCabezal.cargas`, con el
  elemento al que llega cada carga y su brazo; `.combinaciones`, con sus factores) para
  que T-7c calcule lo que necesite sin rehacer el ensamble. Las tres aproximaciones van
  del lado de más solicitación.
- **Qué haría falta:** que T-7c tome las cargas sin factorar y las integre sobre la
  altura real de cada elemento; y el ensamble por secciones del alero.
- **Corrección del cierre (H7).** Cada `SolicitacionDeElemento` lleva ahora con qué
  empuje sale: `regimen` (el de `regimen_cabezal`), `coeficiente_de_empuje` ('K_A' en
  la estática, 'K_AE' en la sísmica), `K_empuje`, y el `K0` de AASHTO 3.11.5.2 con
  `K0_sobre_K_A`: el factor por el que crecerían los empujes de una pantalla que **no
  cede** (C11.6.5.4: «… designed for K0 conditions for the strength limit state»). Ver
  T7B-14.
- **Lo que T-7c hizo con ella (2026-11-13).** (1) La de la pantalla **se corrigió** en el
  cierre (H1): no era del lado seguro para el momento —el tramo bajo el arranque restaba—
  y cada diagrama se integra ahora sobre el arranque, con la inercia de la pantalla sola
  (ficha T7C-12); (2) la presión uniforme **no se usa para armar**: el armado calcula la
  lineal de 10.6.5 (ficha T7C-07); (3) los aleros se arman en su arranque (ficha T7C-04).
  `solicitaciones_por_elemento` ganó el parámetro `marco`.
- **Cerrado en VE-6 (3):** el alero ya no lleva la solicitación de la pantalla: cada
  sección tiene la de su franja (ficha VE6M9-03).
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad.py::solicitaciones_por_elemento`

## T7B-09 · Con la regla de predimensionamiento de T-7a el cabezal de A-01 no pasa el deslizamiento del marco que rige: medido, no corregido

- **Qué se difirió:** la progresión de dimensiones del cabezal. La corrida de punta a
  punta (A-01, expediente, con el suelo y el relleno **de prueba**: φ del relleno 34°,
  fundación friccionante con φ_f = 32° y γ = 18 kN/m³, freático a 1.40 m, trasdós
  drenado, k_h reducido a 0.25) deja medido que con la zapata de la regla (0.70 de la
  altura total: 1.575 m a la entrada) **E3-LRFD estático no cumple en ninguno de los
  dos cabezales** (33.95 > 28.86 kN/m a la entrada; 54.07 > 48.57 a la salida) **ni
  E1-LRFD sísmico** (79.3 > 56.1 kPa; 100.2 > 57.9). Con la zapata declarada de 3.00 m
  las doce filas LRFD cumplen; con 2.40 m el de salida todavía no.
- **Por qué:** la ficha T7A-04 ya advertía que «más material» no es el lado seguro de
  la estabilidad y dejaba la comprobación a T-7b. El encargo de T-7b no trae la regla
  de iteración (qué dimensión crece, con qué paso y hasta dónde), y elegirla es
  decisión de proyecto: no se inventó. Las filas salen como incumplidas del punto, con
  «ampliar la zapata o añadir un dentellón de corte» en el veredicto, y el proyectista
  las cierra con `cabezal_declarado`. Los números son de prueba: con el EMS real pueden
  ser otros.
- **Qué haría falta:** la decisión del dueño —subir `fraccion_ancho_zapata` de la
  regla, añadir un dentellón de corte (y entonces contar el pasivo, AASHTO 11.6.3.5), o
  iterar B hasta cumplir—, y entonces la progresión en `predimensionar_cabezal`.
- **Corrección del cierre (H5 y pregunta 2).** El «no pasa» es **sensible** a dos
  elecciones [A] en su extremo más exigente —la fila de φ (`zapatas_seccion_10`, la más
  exigente y la que transcribe el Manual de Puentes; la letra de AASHTO 11.5.7 da 0.55 /
  1.0 a los muros) y los factores de inclinación— y a datos de prueba: toda fila cuyo
  veredicto cambia dentro de esas ventanas se avisa (`M9._avisos_de_sensibilidad`). La
  iteración del ancho sigue diferida. Con el modelo corregido y los datos de prueba de la
  FASE A (más γ_sat = 20), A-01 incumple E3 estático en los dos cabezales (38.05 > 29.39;
  58.07 > 47.10, que cumpliría con la fila de muros) y E1 sísmico a la entrada (80.26 >
  50.28, que cumpliría sin inclinación); la sísmica de salida no es evaluable (H1).
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::predimensionar_cabezal`

- **Cerrado en VE-3.5 (decisión del dueño, 2026-11-17):** la iteración del ancho que faltaba
  existe (`M9.dimensionar_zapata_por_estabilidad`, ficha VE3-05); con los datos de prueba del
  juego los ocho cabezales cumplen la estabilidad.
## T7B-10 · La aceptación de T-7b se escribió después del código; el rojo y la mutación se midieron

- **Qué se difirió:** escribir la aceptación en rojo con `xfail(strict=True)` antes del
  código. `tests/test_t7b_cabezal_estabilidad.py` (207 tests) y los dorados a mano de
  `tests/fixtures/casos_patron.py` (`CP_T7B_ESTABILIDAD`, `CP_T7B_MURO_2`,
  `CP_T7B_COHESIVO`, `CP_T7B_SOLICITACIONES`, `CP_T7B_PEOR_COMBINACION`) se escribieron
  en la misma sesión que el ensamble.
- **Por qué:** el diseño del ensamble (qué cargas, sobre qué plano, qué combinaciones)
  salió de leer la fuente, y la aceptación fija ese diseño. **Rojo medido** copiando el
  archivo y el fixture a un árbol de `250c972`: de los 202 tests de entonces, 186 rojos y
  16 verdes (cuatro literales del PDF, cuatro guardias de criterios sin valor, la
  guardia «sin declarar nada» y siete rechazos de dato que allí pasan por la razón
  equivocada: la clave no existía). **Mutación** con el arnés de EXT-11 sobre lo nuevo
  de M9 (26 funciones) y de V5 y V8: la primera medida válida mató 525 de 833 mutantes
  de M9 y 64 de 82 de M5; con tres tandas de tests escritas contra los vivos —el segundo
  muro de tanteo, el suelo cohesivo, la roca, los márgenes, las solicitaciones, la peor
  combinación bajo sismo— quedó en **715 de 833 (85.8 %) y 78 de 82 (95.1 %)**. Una
  primera corrida dio 100 % y era falsa: un test localizaba el bloque de M9 por su
  comentario de cabecera, que el arnés borra al reescribir el módulo; se ancló por
  símbolo. Los 118 vivos de M9: 29 fronteras a tolerancia (`<=` por `<`, el signo de la
  tolerancia), 32 comparaciones en valores degenerados (`> 0` por `>= 0` sobre pesos y
  anchos que solo son cero con geometría nula) y 57 constantes de guardia, textos de
  mensaje y el factor i_c con φ > 0, que E.050 Art. 20 deja sin efecto (c = 0).
- **Qué haría falta:** casos de frontera exacta para las seis filas, que exigen un muro
  construido para caer en el umbral; y un tercer conjunto de objetivos para la segunda
  vuelta del arnés.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::combinaciones_de_estabilidad`

## T7B-11 · La orientación del muro frente al tráfico sigue siendo un dato de corredor: no se deriva del esviaje de cada punto

- **Qué se difirió:** deducir por punto qué tabla de la sobrecarga viva aplica. El
  cabezal es normal al eje del conducto (decisión del dueño), de modo que con esviaje
  θ forma θ con el eje de la vía: a 0° es paralelo al tráfico y a esviajes altos se
  acerca a perpendicular. El ensamble lee `orientacion_muro_respecto_al_trafico` y
  `distancia_borde_calzada_al_trasdos_m`, los dos [S] de corredor de siempre.
- **Por qué:** AASHTO reparte las dos tablas de h_eq por el título de cada una
  (estribos perpendiculares, muros paralelos) y no da regla para un muro oblicuo; una
  derivación por el ángulo sería inventar un umbral. La distancia del borde de calzada
  al trasdós sí varía por punto (depende de la longitud del conducto) y también entra
  como dato de corredor.
- **Qué haría falta:** una regla declarada para el muro oblicuo (un [A] con ventana), o
  los dos datos por punto en `--datos-externos`.
- **Cerrado en VE-6:** los dos datos por punto (ficha VE6M9-04); la regla del muro oblicuo
  no se escribe (la fuente no la da).
- **Dónde vive:** `src/modulos/M9_cabezal/empujes.py::h_eq_sobrecarga_trasdos`

## T7B-12 · Declarados, V5 y V8 se evalúan también a nivel de perfil; y el pre-vuelo de expediente anuncia el freático

- **Qué se difirió:** nada; son dos consecuencias que conviene leer. (1)
  `_verificador_perfil` decía desde antes de T-7b que V5 y V8 «se intentan igual» a
  perfil y que, el día que su lógica existiera, entrarían a la tabla: existe, y con el
  método y los datos declarados V5 y V8 deciden también a perfil (sin declarar se
  difieren como siempre). Sus criterios son de nivel EXPEDIENTE, que es donde se
  consumen sin declarar nada; `tests/test_nivel_medido.py` censa el caso
  (`DE_UNA_VERIFICACION_DIFERIDA`). (2) El ensamble lee la columna `NF_profundidad_m`,
  el censo le encuentra ese consumidor y el pre-vuelo **de expediente** la anuncia como
  falta que detiene en los puntos que la traen vacía —los cuatro del fixture—: el
  freático pasa de «espera» a «DETIENE». (Corrección del cierre, H8: la FASE A escribía
  que el código de salida de `--prevuelo` a expediente pasaba de 0 a 1; con
  `tests/ejemplo_puntos.csv` ya salía con 1 en `250c972`, y lo que cambia es la clase
  de la falta.) Es cierto (la estabilidad de su cabezal se detendría), y es de
  más mientras V5 y V8 sigan sin declarar: el pre-vuelo estima de más a propósito.
  Desde el cierre, cada método de V5 anuncia **su** dato (`ancho_derecho_via_m` con
  `embalse_a_nivel`, `cota_afectacion_aguas_arriba_msnm` con `cota_de_afectacion`).
- **Por qué:** la primera es el diseño previo de la corrida de perfil; la segunda, el
  del pre-vuelo (ficha PF-2-01).
- **Qué haría falta:** si se quisiera que el nivel de perfil no evalúe nunca V5 ni V8,
  diferirlas por alcance antes de intentarlas; y para el pre-vuelo, condicionar la
  falta del freático a que la Fase 9 sea alcanzable.
- **Dónde vive:** `src/servicio.py::_verificador_perfil`

## T7B-13 · El cierre de T-7b aplicó las diez correcciones de la auditoría: el datum del freático, V5 por cota, V8 a presión, la cuña de tanteo, el agua y el régimen

- **Qué se difirió:** nada nuevo; esta ficha es la medida del cierre. La auditoría
  adversarial de la FASE A (AJUSTADO: 3 ALTA, 4 MEDIA, 3 BAJA; la aritmética del ensamble
  coincidía con AASHTO) dejó: **H1** el freático medido desde el pie de cada cabezal y no
  desde el terreno del cruce (en la salida de A-01, agua 0.80 m más baja: seca cuando
  tiene 0.20 m sobre la base); **H2** V5 por embalse a nivel, que falla en falso; **H3**
  V8 «no evaluable» desde 1.29·Q; **H4** la pendiente 2H que subestima la cuña; **H5** el
  «no pasa» presentado como hecho; **H6** el agua por encima del muro y el desembalse
  sin decir; **H7** el muro no cedente sin marcar para T-7c; **H8–H10**, textos,
  aleros y una aserción tautológica. Cómo quedó cada uno: H1 —el entorno lleva la
  **cota** del agua (`EntornoDelCabezal.cota_freatico` = `cota_terreno − NF`, la
  convención de M8, del censo y del contrato) y de ella salen `h_w_natural` y `D_w`; el
  test que congelaba el defecto se reescribió declarándolo y hay un dorado a mano con
  pie ≠ terreno (la salida de A-01: agua a 40.70 msnm, 0.20 m sobre la base)—; H2 (T7B-01);
  H3 (T7B-02); H4 (T7B-06); H5 (T7B-09); H6 (T7B-03 y T7B-05); H7 (T7B-08 y T7B-14);
  H8 —la nota de `AASHTO_LRFD_9.10.6.3.4#RESISTENCIA` (el suelo cohesivo SÍ está
  implementado), el docstring de `servicio._fase_9`, `gamma_saturado_kn_m3` del suelo de
  fundación retirado (se validaba y nadie lo leía), y el aviso del cabezal con una sola
  condición evaluada—; H9 —el alero largo que supera la longitud entre cabezales se
  avisa, comparado con esa magnitud y sin umbral nuevo—; H10 —la última aserción del
  contraste con VARIOS era tautológica (k_h se reconstruyó de EQ/(DC + EV)) y se
  reescribió como lo que es—.
- **Por qué:** las resoluciones del orquestador para H1–H10 y las seis preguntas
  (`ENCARGO_T-7b_cierre.md`), vinculantes salvo que el PDF contradijera una premisa; no
  la contradijo ninguna: las ocho citas nuevas se leyeron en su página.
- **Rojo y mutación:** los tests del cierre (`H1` a `H10` en
  `tests/test_t7b_cabezal_estabilidad.py`) no se escribieron en rojo con
  `xfail(strict=True)`: se escribieron con el código, y el rojo se mide contra la FASE A
  (`fc792d9`), donde los símbolos nuevos no existen y cada test falla por separado.
- **Qué haría falta:** lo que cada ficha dice.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::cuna_de_tanteo`

## T7B-14 · El cabezal se calcula como muro que CEDE; el que no cede está en la ventana y no implementado, y la interfaz de T-7c lo marca

- **Qué se difirió:** las presiones de un muro que no cede: empuje en reposo K0 en el
  estado límite de resistencia y, bajo sismo, k_h = 1.0·k_h0 con resultante en h/2
  (AASHTO 11.6.5.4 y C11.6.5.4). `regimen_cabezal` [A] = `cedente` de archivo, con
  `no_cedente` en la ventana: declararlo detiene la estabilidad con
  `MetodoNoEvaluableError` (rótulo del cabezal).
- **Por qué:** los métodos de 11.6.5.3 «assume that the abutment or wall is free to
  laterally yield», y el comentario de 11.6.5.4 pone entre los muros que pueden no ceder
  a los estribos con aleros estructurales, a los que un cabezal monolítico con el barril
  se parece. Para la **estabilidad externa** —vuelco y deslizamiento del conjunto— el
  muro cede por definición del mecanismo, y es lo que el ensamble calcula; para la
  **resistencia** de la pantalla puede no ceder, y eso lo decide T-7c. Por eso la
  interfaz lo marca en vez de resolverlo: cada solicitación lleva el coeficiente con que
  salió y el `K0 / K_A` de referencia (en A-01, con φ = 34° y la cuña: K0 = 1 − sen 34°
  = 0.441 frente a K_A = 0.325 a la entrada y 0.304 a la salida, un 36 % y un 45 % más;
  contra el K_A de la fórmula 2H, 0.290, era el +52 % que midió el auditor). El K0 de 3.11.5.2-1 es de muro vertical y
  terreno **horizontal**: es una referencia de orden de magnitud, no el coeficiente de
  ese relleno.
- **Qué haría falta:** que T-7c decida el régimen de la pantalla para su armado; y, si
  el cabezal se declara no cedente, las presiones de muro rígido (Wood, 1973) o un
  análisis numérico aprobado por el Propietario.
- **Decidido en T-7c (2026-11-13).** El régimen del **armado** es un criterio aparte,
  `regimen_resistencia_elementos_cabezal` [A] = `no_cedente_k0` (decisión del dueño), y
  este criterio no se tocó: la estabilidad externa sigue con el muro que cede. Ver la
  ficha T7C-02.
- **Cerrado en VE-5 (lote M9, 2026-11-20):** `no_cedente` se calcula; ver la ficha
  VE5M9-01 al final de este registro.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::regimen_cabezal`

# Parte LI — Lo que T-7c de la cadena T dejó escrito: el armado del cabezal y su alternativa ciclópea

T-7c (2026-11-13, FASE A y cierre, integrado detrás de T-7b) arma cada cabezal —pantalla, punta y talón de la zapata, y
aleros en su arranque— o verifica su alternativa en concreto ciclópeo (`INF-4.6`, la
ficha `EXT-7-01` y el `NotImplementedError` de `M9.diseno_flexion_corte`). No itera
dimensiones: arma la geometría que T-7a propone y T-7b verifica, pase o no su
estabilidad. Las fichas de abajo son lo que el armado hace por elección del proyecto, lo
que no hace, y lo que el encargo pedía y la fuente no sostiene. El **cierre** (el mismo
día, tras la auditoría adversarial: AJUSTADO, 2 ALTA, 5 MEDIA, 5 BAJA) corrigió las
fichas en su sitio y añadió T7C-11 a T7C-13.

## T7C-01 · Rige AASHTO LRFD Sección 5 y E.060 contrasta: dos marcos que no se cruzan, y en los mínimos, el más exigente

- **Cerrado (T-7c):** la resistencia de cada sección se verifica con AASHTO LRFD 9.ª ed.
  Sección 5 —flexión de 5.6.3.2 con el bloque rectangular de 5.6.2.2, cortante de 5.7.3.3,
  factores de 5.5.4.2 (0.90 y 0.90) y 1.0 en el Evento Extremo I por 1.3.2.1— sobre las
  solicitaciones factoradas de Resistencia I y Evento Extremo I (filas A1 y A2, que
  deciden). E.060 se calcula **en paralelo**, con sus combinaciones (9.2.5: 1,4 CM + 1,7
  CV + 1,7 CE y 0,9 CM + 1,7 CE) y sus factores (0,90 y 0,85), como fila A5, que **informa**
  ([N→], por analogía). Las constantes de AASHTO se convierten a SI **en la constante**
  (`VC_COEFICIENTE_AASHTO_SI`, `MODULO_ROTURA_AASHTO_SI`,
  `TEMPERATURA_COEFICIENTE_AASHTO_SI`), no en la llamada, y el procedimiento general de
  cortante transcrito en ksi y pulgadas queda bajo una clave rotulada «no ejecutable».
- **Abierto:** (1) en los **mínimos** —acero mínimo de cada cara y espaciamiento máximo—
  se aplica el más exigente de AASHTO (5.6.3.3, 5.10.6, 5.10.3.2) y de E.060 (14.3.1,
  14.3.3, 9.7.2, 10.5.4): es `regla_minimos_constructivos_cabezal` [A], con «solo_aashto»
  en la ventana, y ninguna fuente dice cuál prevalece sobre un cabezal vial. (2) El
  reparto de la cuantía de muros de E.060 entre las dos capas (la mitad por cara) es del
  proyecto: 14.8.3 deja disponer más en la cara expuesta. (3) E.060 no escribe una
  combinación con sismo **y** empuje de suelos: el contraste es solo estático. (4) El
  ensamble de T-7b no aplica el modificador de carga η de 1.3.2.1 (el conducto sí, η_I =
  1.05, T-5): el armado hereda sus solicitaciones tal como salen. El cierre lo midió y
  **no** lo aplicó: ficha T7C-11.
- **Qué haría falta:** una especificación del Propietario que fije el juego de mínimos y
  el modificador de carga del cabezal.
- **Dónde vive:** `src/modulos/M9_cabezal/armado_secciones.py::diseno_flexion_corte`

## T7C-02 · Los elementos se arman con el empuje en reposo, y lo que esa elección no resuelve

- **Cerrado (T-7c, decisión del dueño del 2026-11-13):**
  `regimen_resistencia_elementos_cabezal` [A] = `no_cedente_k0`, con `cedente` en la
  ventana. La estabilidad externa de T-7b **no cambia** (`regimen_cabezal` sigue en
  «cedente»). Lo que se escala y lo que no (`M9.cargas_en_reposo`): solo el empuje del
  suelo —de P_A a (K0/K_A)·P_A, horizontal, sin su componente vertical— y el de la
  sobrecarga viva; el peso del concreto, el del relleno, el de la sobrecarga, el agua y la
  subpresión no. El factor de carga es el de la fila «En reposo» (1.35), no el de la
  activa (1.50). En cada sección rige la **mayor** de la solicitación en reposo y la del
  muro que cede, y las dos se imprimen. En el muro de tanteo, el momento de la pantalla
  pasa de 21.47 a 35.40 kN·m/m (diagrama integrado sobre el arranque, ficha T7C-12).
- **Abierto:** (1) el K0 de AASHTO 3.11.5.2-1 es de **terreno horizontal** y detrás del
  cabezal el relleno sube: el reposo calculado es una cota inferior del real, la fuente no
  da la fórmula y por eso se toma la envolvente con el activo de la cuña, que sí lleva la
  pendiente. (2) Bajo **sismo** la fuente no da un coeficiente de reposo: manda k_h =
  1.0·k_h0 (11.6.5.4) y pide considerar la resultante a h/2 (C11.6.5.4, «should be
  considered»). El armado usa el método de empuje sísmico del ensamble y, en la pantalla
  y los aleros, la mayor de su posición y h/2 (un diagrama uniforme, que mueve también el
  cortante). **Cierre (H2):** el armado del muro que no cede va con k_h = 1.0·k_h0
  (11.6.5.4, «shall»), por la puerta `k_h` de `M9.cargas_del_cabezal`; la estabilidad
  conserva el reducido. **Cierre (H10):** K0·(1 + sen i) se imprime como contraste no
  adoptado. (3) C3.11.5.2 dice que un muro en voladizo
  típico de más de 5.0 ft desarrolla la condición activa: es lo que sostiene la
  alternativa, y lo que juega en contra del valor de archivo (está en la
  `Interpretacion` de la cita `AASHTO_LRFD_9.C3.11.1#REPOSO`).
- **Qué haría falta:** un análisis de la interacción del cabezal con el relleno, el barril
  y los aleros que diga cuánto se desplaza la pantalla; y, bajo sismo, las presiones de
  muro rígido (Wood, 1973) o un análisis numérico aprobado por el Propietario.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::regimen_resistencia_elementos_cabezal`

## T7C-03 · El cortante se verifica con el procedimiento simplificado donde la fuente lo permite; fuera de él no se evalúa, y la pantalla se trata como losa

- **Qué se difirió:** el procedimiento **general** de cortante de AASHTO 5.7.3.4.2 (β y θ
  en función de la deformación del acero) y el refuerzo transversal. El armado usa β =
  2.0 y θ = 45° (5.7.3.4.1), que la fuente **permite** solo en zapatas con el vuelo menor
  que 3·d_v y en secciones de menos de 16.0 in (0.4064 m) de peralte;
  `M9.simplificado_permitido` lo comprueba sección por sección y, fuera de esas
  condiciones, `diseno_flexion_corte` se detiene con `MetodoNoEvaluableError` (rótulo
  `MOTIVO_METODO_NO_EVALUABLE_ARMADO`), que el servicio registra como bloqueo del
  elemento.
- **Por qué:** el encargo de T-7c excluye el MCFT general, y el comentario de la fuente
  dice que las expresiones tradicionales son «seriously unconservative» en elementos
  grandes sin estribos: aplicar β = 2.0 a una pantalla de 0.45 m sería justo eso. Con la
  regla de T-7a (pantalla de 0.30 m, zapata de 0.37 m) todo cabezal propuesto cae dentro
  del permiso. Y una lectura que se declara: AASHTO 5.7.2.3 exige refuerzo transversal
  donde V_u > 0.5·φ·V_c «except for slabs, footings, and culverts»; la pantalla **no se
  nombra**. El proyecto la trata como una losa en voladizo y exige V_u ≤ φ·V_c; cuando V_u
  pasa de la mitad lo avisa (`Interpretacion` de la cita
  `AASHTO_LRFD_9.5.7.2.3#TRANSVERSAL`). El cortante se toma en la cara del apoyo, sin
  reducirlo a d_v de ella. **Cierre (pregunta 4 y H8):** cuando V_u pasa de 0.5·φ·V_c en
  la pantalla o el alero, A2 sale como **INDICADOR** y no como CUMPLE (en la salida de
  A-01 ocurre); y d_v se acota al peralte efectivo (`Interpretacion` de la cita
  `AASHTO_LRFD_9.5.7.2.8#DV`: con el recubrimiento de cota, 0.72·h supera a d_e), con el
  de la letra impreso al lado y avisado; la aplicabilidad del simplificado se lee con el
  de la letra.
- **Qué haría falta:** implementar 5.7.3.4.2 (no es iterativo en la 9.ª ed., pero pide el
  tamaño máximo del agregado y el parámetro de espaciamiento de fisuras) o dimensionar
  estribos; y la decisión del proyectista sobre si la pantalla es o no una «losa» a
  efectos de 5.7.2.3.
- **Dónde vive:** `src/modulos/M9_cabezal/armado_secciones.py::simplificado_permitido`

## T7C-04 · Los aleros se arman en su arranque; su zapata y sus secciones intermedias no

- **Qué se difirió:** el ensamble por secciones del alero. `M9.armar_elemento` arma el
  alero en su **arranque** —el encuentro con el cabezal, que es su sección más alta y la
  crítica de un muro en voladizo de altura variable— con el espesor del alero y la
  solicitación de la pantalla a esa altura. No arma la zapata del alero ni reduce el
  armado hacia la punta, donde la altura baja hasta 0.40 m.
- **Por qué:** la interfaz de T-7b entrega para los aleros la solicitación de la pantalla
  en su arranque (ficha T7B-08); la zapata del alero tiene su propio ancho
  (`Aleros.ancho_zapata`) y no tiene ensamble de estabilidad. Armar todo el alero con el
  acero del arranque es el lado seguro; lo que falta es la zapata.
- **Qué haría falta:** el ensamble de estabilidad del alero por secciones (altura
  variable con el talud) y sus solicitaciones de zapata.
- **Cerrado en VE-6, a medias:** el fuste del alero se arma por secciones (arranque y
  mitad, ficha VE6M9-03); la zapata del alero sigue sin armar ni verificar.
- **Cerrado en VE-7:** el alero se verifica como muro (E1–E3 en cinco franjas),
  su zapata se dimensiona por estabilidad y se arma (ficha VE7-01).
- **Y lo que el armado tampoco cubre (cierre, H6):** el **vano del conducto** —la
  pantalla de 1.70 m de A-01 es hueco en el ancho del barril, y la sección llena de la
  hipótesis de T-7b son los machones a cada lado—: el refuerzo de borde alrededor de la
  abertura no se dimensiona (E.060 22.6.6.5 pide dos barras de 5/8" en las aberturas de
  los muros de concreto simple, cita `E060.22.6.6.5#ABERTURAS`; para el armado, por
  analogía); ni la **losa de entrega** ni el **dentellón**, que `GeometriaCabezal.losa`
  trae. El aviso de cada cabezal lo nombra; no se dimensiona.
- **Dónde vive:** `src/modulos/M9_cabezal/armado.py::armar_elemento`

## T7C-05 · Sin el análisis químico ni la categoría del acero, el recubrimiento con que se arma es la cota más exigente, no los 70 mm del encargo

- **Qué se difirió:** el recubrimiento del proyecto. El prompt de T-7c pedía que
  `categoria_refuerzo_aashto` y `exposicion_quimica_ems` pasaran a entradas [S] «con valor
  por defecto NO» y que, sin dato, se tomaran los 70 mm de E.060 7.7.1. **No se aplicó
  así**: tomar 70 mm es suponer la categoría del acero y la agresividad del sitio, que es
  rellenar un dato. Los dos criterios siguen **sin valor**; el armado calcula el peralte
  efectivo con la **cota más exigente** que la regla del mayor puede dar para esa cara
  —max(E.060, la fila de AASHTO en su columna de más recubrimiento × el factor por a/c
  más alto): 3.0 in × 1.2 = 91.44 mm— y lo **avisa** por `avisos()`
  (`M9.recubrimiento_para_armar`). Con los dos datos declarados es el de
  `recubrimiento_de_diseno`.
- **Por qué:** más recubrimiento es menos brazo y más acero: la cota es el lado seguro de
  la resistencia, y no impide armar. `categoria_refuerzo_aashto` sigue siendo [A] y no
  [S]: qué acero se especifica es una decisión de proyecto, no una medición del sitio;
  `exposicion_quimica_ems` ya era [S].
- **Dónde NO es el lado seguro (cierre, pregunta 2).** La cota es la más exigente de la
  regla ANTES del aumento por ambiente corrosivo de E.060 7.7.5.1, que la regla no
  cuantifica: sin ambiente corrosivo es el lado exigente de la flexión, de la
  fisuración de 5.6.7 (d_c) y de la altura de la zapata sobre su refuerzo (E.060 15.7);
  si el EMS declara un ambiente corrosivo, el recubrimiento real puede pasarla y esas
  tres hay que rehacerlas. En el cortante el piso 0.72·h de 5.7.2.8 no depende del
  recubrimiento: por eso d_v se acota a d_e (H8). La auditoría lo había dicho al revés
  para 5.6.7 («el lado inseguro de la fisuración»): con más d_c la ecuación da menos
  espaciamiento, de modo que la cota es la comprobación más exigente; el aviso dice lo
  que la aritmética sostiene.
- **Qué haría falta:** el análisis químico del EMS y la especificación del acero.
- **Dónde vive:** `src/modulos/M9_cabezal/durabilidad.py::recubrimiento_para_armar`

## T7C-06 · El desarrollo y los empalmes de las barras no se evalúan; la fisuración de 5.6.7 se evalúa con la clase de exposición que declare el Propietario

- **Cerrado en el cierre de T-7c (H3 y pregunta 5):** AASHTO 5.6.7 «shall apply» en todo
  componente cuya tracción de servicio pase de 0.8·f_r, y la FASE A la difería mientras
  A4 decía CUMPLE. Ahora es la fila **A6** (`M9.fisuracion_aashto`): Servicio I de la
  Tabla 3.4.1-1 con el mismo empuje con que se arma, la tracción bruta frente a 0.8·f_r,
  f_ss de la sección fisurada elástica (n = E_s/E_c con 5.4.3.2 y C5.4.2.4-1), β_s de la
  ec. 5.6.7-2 y s ≤ 700·γe/(βs·f_ss) − 2·d_c, con la constante en SI
  (`FISURACION_COEFICIENTE_AASHTO_SI`) y el tope f_ss ≤ 0.60·f_y. La clase de exposición
  es `clase_exposicion_fisuracion_cabezal` [A] **sin valor de archivo**: declarada,
  decide y la barra propuesta la respeta; sin declarar, la propuesta respeta la Clase 1
  —la menos exigente, «an upper bound in regards to crack width» (C5.6.7)— y A6 imprime
  las dos y sale INDICADOR «no decidida» cuando el espaciamiento solo cumple la 1. d_c es
  el recubrimiento real con que se arma (C5.6.7: «the actual concrete cover thickness
  should be used»); la alternativa de «2.0 in plus the bar radius» de la práctica no se
  toma. En A-01 con datos de prueba aplica solo en la pantalla de salida.
- **Qué se difirió todavía:** las longitudes de desarrollo y de empalme de las barras
  (5.10.8), y el refuerzo de piel de 5.6.7 (no aplica: d_l < 3.0 ft).
- **Por qué:** el desarrollo y los empalmes dependen del despiece, que el armado por
  metro no produce.
- **Qué haría falta:** la clase de exposición declarada; y, para el desarrollo, el
  despiece de las barras.
- **Dónde vive:** `src/modulos/M9_cabezal/armado_secciones.py::fisuracion_aashto`

## T7C-07 · La zapata se arma con presión de contacto lineal y el talón con el peso entero: no son las solicitaciones de zapata de la interfaz de T-7b

- **Cerrado (T-7c):** AASHTO 10.6.5 exige para el **diseño estructural** de una zapata
  cargada con excentricidad una presión de contacto «triangular or trapezoidal»; la
  uniforme sobre B − 2e es la de la capacidad portante (10.6.1.4) y la que
  `M9.solicitaciones_por_elemento` (T-7b) usaba para la punta y el talón. El armado
  calcula la suya (`M9.presion_de_contacto_lineal`, `M9.solicitaciones_de_la_zapata`): en
  la punta, la presión lineal más la subpresión del agua, que también empuja la zapata
  hacia arriba y que la de T-7b no contaba, menos el peso propio; en el talón, el **peso
  entero** de lo que tiene encima, sin descontar la reacción (11.6.1.2: «loaded with the
  full weight of the superimposed material, unless a more exact method is used»), con el
  método más exacto impreso al lado. En el muro de tanteo: punta 15.52 kN·m/m (con la
  uniforme de T-7b y el empuje activo, 9.32); talón 56.89 kN·m/m (descontando la
  reacción, 22.05).
- **Abierto:** las solicitaciones de zapata de `EstabilidadDelCabezal.solicitaciones`
  siguen siendo las de la presión uniforme: el armado no las usa, y la interfaz no se
  tocó. Tomar el talón con el peso entero es la regla por defecto de la fuente y da del
  orden del doble de momento que el método exacto.
- **Qué haría falta:** nada para el armado; si se quiere una sola cifra, que la interfaz
  de T-7b entregue las de la presión lineal.
- **Dónde vive:** `src/modulos/M9_cabezal/armado_secciones.py::solicitaciones_de_la_zapata`

## T7C-08 · La aceptación de T-7c se escribió después del código; el rojo y la mutación se midieron

- **Qué se difirió:** escribir los tests en rojo con `xfail(strict=True)` antes del
  código. El archivo `tests/test_t7c_cabezal_armado.py` y el bloque de M9 se escribieron
  en la misma sesión.
- **Por qué:** el rojo se **midió** copiando el archivo y el fixture a un árbol exportado
  de `451a10a`, y la mutación de lo nuevo de M9 con el arnés de EXT-11
  (`tests/apoyo/mutacion.py`); las dos medidas están en el informe de la FASE A. Los
  dorados (`CP_T7C_ARMADO`, `CP_T7C_CICLOPEO`, `CP_T7C_EC_11_32`,
  `CP_T7C_BASE_SERVICIO`) están calculados a mano, con la aritmética escrita, y el del
  acero de temperatura reproduce los tres ejemplos que el comentario C5.10.6 publica.
- **Lo que se midió.** El rojo es de **recolección**: sobre `451a10a` el archivo no se
  importa (`ImportError: cannot import name 'MARCO_E060'`), de modo que no hay un rojo test
  a test. La mutación, sobre las 34 funciones nuevas de M9 (1007 mutantes) y con los tests
  rápidos de este archivo como único objetivo: 748 muertos en la primera medida (74.3 %);
  con los 20 tests de la sección «lo que la mutación enseñó», 843 (83.7 %), sumando una
  medida entera y una parcial de las cuatro funciones que cambiaron de tests. De los 164
  vivos, 43 son la frontera de un umbral con tolerancia, 16 guardias de entrada que ningún
  dato válido distingue, 37 valores por omisión o de relleno que no se alcanzan y 3 textos;
  de los 65 restantes, la mayoría son cifras de presentación y fronteras donde las dos
  ramas dan el mismo valor, y quedan **huecos reales** que el informe de la FASE A nombra:
  el aviso de la punta sin presión de contacto, el umbral numérico del aviso de 0.5·φ·V_c,
  el contraste C6 del ciclópeo cuando no cumple, el aviso del vuelo de su zapata, el
  empuje inclinado en las secciones del cuerpo, y el aviso de «ninguna barra del catálogo».
  No hay censo de vivos fijado en un test.
- **Qué haría falta:** nada para el conteo; para la mutación, cerrar los huecos nombrados y
  una segunda vuelta con la línea base y la CLI como objetivo.
- **El cierre.** Sus tests tampoco se escribieron en rojo: el rojo se midió con el
  archivo final contra la FASE A (`f50edbe`): 60 rojos y 189 verdes. La mutación se
  rehízo sobre las 23 funciones tocadas: 810 de 1012 (80.0 %), con cuatro tests de lo
  que enseñó; de los 202 vivos, 61 son fronteras con tolerancia y 84 constantes de
  relleno o presentación. C6 incumpliendo y el reparto con el mayor ancho tienen test.
- **Dónde vive:** `tests/test_t7c_cabezal_armado.py::test_diseno_flexion_corte_ya_no_lanza_NotImplementedError`

## T7C-09 · El cabezal de gravedad en ciclópeo se juzga por tracciones nulas, solo en la condición estática, y su zapata no se verifica

- **Cerrado (T-7c):** `M9.verificar_cabezal_ciclopeo` no arma: comprueba la resultante
  de las cargas de **servicio** dentro del tercio central de la base (C1) y del cuerpo, en
  su arranque y a media altura (C2, C3), la resistencia de la matriz y el volumen de
  piedra (C4, C5: el mayor de los 10 MPa de E.060 22.10.1 y los 14 MPa de la Clase G del
  EG-2013, y 30 %), y un contraste con E.060 Cap. 22 (C6: φ = 0,5, f'c ≤ 10 MPa, peralte
  reducido en 50 mm, tracción ≤ φ·0,42·√f'c y cortante ≤ φ·0,11·√f'c·b·h, con cargas 0,9
  CM + 1,7 CE). Cuál decide lo declara `criterio_traccion_cabezal_ciclopeo` [A]:
  «tracciones_nulas» por archivo.
- **Corregido en el cierre (H5).** «Ninguna fuente exige tracciones nulas» era falso en
  el ARRANQUE: E.060 22.4.7 (cita `E060.22.4.7#JUNTAS`) prohíbe la tracción a través de
  una junta de construcción. C2 **decide siempre**, con la mayor de la excentricidad de
  servicio y la amplificada de E.060, salvo vaciado monolítico declarado
  (`junta_arranque_cabezal_ciclopeo` [A]). El umbral de C1 y C3 es criterio del proyecto
  (`Interpretacion` de `E060.22.6.3#TERCIO`); C6 aplica la excentricidad mínima de 0,10·h
  de 22.6.3.
- **Abierto:** (1) fuera de la junta, las tracciones nulas son criterio del proyecto: en
  el dorado, e = 0.60 m (1.18 m amplificada) frente a t/6 = 0.083 m, y la tracción de
  E.060 cumple (0.54). (2) Solo condición
  estática: bajo sismo la base es la fila E2 de la estabilidad y las secciones del cuerpo
  no se evalúan. (3) La zapata no se verifica como voladizo de concreto simple, que
  22.10.2.2 pide cuando el vuelo supera la mitad del peralte: se avisa. (4) Con D ≥ 0.90 m
  todo cabezal de la regla de T-7a sale voladizo armado: la rama solo se alcanza
  declarando `altura_max_gravedad_m` o el tipo en `cabezal_declarado`, y por esa puerta
  está probada.
- **Qué haría falta:** una especificación del Propietario para muros de gravedad en
  ciclópeo, y la verificación de la zapata por 22.7.
- **Cerrado en VE-6 (2) y (3):** el cuerpo bajo sismo (C8) y la zapata como voladizo (C7);
  ficha VE6M9-01.
- **Dónde vive:** `src/modulos/M9_cabezal/ciclopeo.py::verificar_cabezal_ciclopeo`

## T7C-10 · El rótulo por ámbito de E.060: lo que T-7c usa es [N→]; el 0.30 m de 22.7.4 pasa a criterio [N→] en el cierre, y las cuantías de 14.3.1 siguen como constante

- **Cerrado (T-7c):** todo artículo de E.060 que el armado usa entra **por analogía**:
  los dos pisos de cortante en el plano son criterios [N→], el contraste A5 y el C6 dicen
  «por analogía» en su umbral, y la `Interpretacion` de la cita `E060.9.2.5#EMPUJE` lo
  declara con lo que juega en contra (el artículo 1.1.1 de E.060 no se limita a sí mismo
  a las edificaciones: lo es por el reglamento del que forma parte).
- **Cerrado en el cierre (pregunta 1, resuelta por el orquestador):** el mínimo de 300 mm
  de la zapata de concreto simple (E.060 22.7.4), que T-7a dejó como constante [N]
  (`ESPESOR_MIN_ZAPATA_CONCRETO_SIMPLE_M`), pasa al criterio [N→]
  `espesor_min_zapata_concreto_simple_m`: la excepción de la §0.2 de la hoja de ruta que
  hace regir E.060 en el cabezal cubre la **durabilidad** (Cap. 4 y Art. 7.7), y un mínimo
  estructural de su Cap. 22 aplicado a una obra vial es una analogía, como E.050 26.2 y
  E.060 15.7. `M9.peralte_minimo_zapata` lo lee del criterio y CB6 no cambia de valor.
  El recubrimiento de 7.7.1 sigue [N] por esa excepción.
- **Abierto:** las cuantías mínimas de muros de **14.3.1** (`CUANTIA_MIN_MURO`) tienen la
  misma objeción y **no se movieron**: arrastran más de lo que parece —las lee
  `servicio` en una comprobación de la corrida, `M9.cuantia_minima` y
  `M9.verificar_cuantia` (código de antes de la cadena T, con sus tests de EXT-7), y el
  manifiesto de citas las resincroniza **por símbolo**—, de modo que el traslado es una
  sesión de registro aparte, no una línea de este cierre.
- **Qué haría falta:** una sesión que pase `CUANTIA_MIN_MURO` a un criterio [N→] y
  resincronice el manifiesto y los consumidores.
- **Cerrado en VE-6:** es el criterio [N→] `cuantia_minima_muro_e060`; ficha VE6M9-02.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::cuantia_minima_muro_e060`

## T7C-11 · El modificador de carga η no entra en el cabezal: la fuente lo sostiene, pero el cambio no es acotado

- **Cerrado (verificación de T-7):** η entra con el η_I del cruce (T7V-02).
- **Qué se difirió:** el modificador de carga η = η_D·η_R·η_I de AASHTO 1.3.2.1 en las
  combinaciones de Resistencia I del cabezal —estabilidad externa **y** armado— con el
  mismo η_I del conducto (`eta_importancia_operativa_conducto` [A] = 1.05, T-5). La
  pregunta 6 del informe de la FASE A, que el orquestador resolvió aplicarlo «si la
  fuente lo sostiene y el cambio es acotado».
- **Lo que la fuente dice (verificado en el PDF):** 1.3.2.1 (pág. impresa 1-3, PDF 18):
  Σ η_i·γ_i·Q_i ≤ φ·R_n, con η_i = η_D·η_R·η_I ≥ 0.95 para las cargas con γ máximo y η_i
  = 1/(η_D·η_R·η_I) ≤ 1.0 para las de γ mínimo. 1.3.3 (PDF 20): η_D = 1.00 para «designs
  and details complying with these Specifications», en resistencia. 1.3.4 (PDF 21): η_R =
  1.00 para «conventional levels of redundancy, foundation elements where φ already
  accounts for redundancy as specified in Article 10.5». 1.3.5 (PDF 22): η_I ≥ 1.05 para
  puentes críticos o esenciales, y en los demás estados límite —Evento Extremo
  incluido— η_D = η_R = η_I = 1.00. La fuente **lo sostiene** como lo planteó el
  orquestador; la Sección 11 no lo exceptúa para los muros.
- **Por qué no se aplicó:** el cambio no es acotado. Aplicado en
  `M9.combinaciones_de_estabilidad` y `M9._combinaciones_en_reposo` (1.05 en las cargas
  de γ máximo, 1/1.05 en las de γ mínimo), **22 tests rápidos** de T-7b y T-7c fallan:
  los dorados a mano de la estabilidad de T-7b (`CP_T7B_ESTABILIDAD`,
  `CP_T7B_SOLICITACIONES`, `CP_T7B_PEOR_COMBINACION`, `CP_T7B_MURO_2`,
  `CP_T7B_COHESIVO`), ya integrados y auditados, habría que rehacerlos todos. Medido en
  A-01 con los datos de prueba: E1-LRFD est. de entrada 67.52 ≤ 87.41 → 72.94 ≤ 85.69 kPa;
  E3 de entrada 38.05 > 29.39 → 39.95 > 28.47 kN/m; E1 de salida 81.85 ≤ 100.81 →
  77.68 ≤ 90.78; E3 de salida 57.93 > 49.13 → 60.83 > 47.60 (**ningún veredicto
  cambia**); en el armado solo el talón de salida (71.72 → 75.31 kN·m/m: Ø 1/2" @ 0.175
  → @ 0.15). Las filas sísmicas no se mueven (η = 1 en Evento Extremo).
- **Qué haría falta:** una sesión dedicada que aplique η a la estabilidad y al armado a
  la vez y rehaga los dorados de T-7b y de T-7c a mano; y la decisión del Propietario
  sobre η_R del cabezal (1.3.4: una pantalla en voladizo es un elemento de un solo
  camino de carga, y «nonredundant members» pide ≥ 1.05; el valor de T-5, 1.00, viene
  de 12.5.4, que es de estructuras ENTERRADAS y no alcanza al cabezal).
- **Dónde vive:** `src/criterios/conducto.py::eta_importancia_operativa_conducto`

## T7C-12 · La pantalla y el alero integran cada diagrama por encima del arranque; el incremento sísmico se reparte con el diagrama lineal de su resultante

- **Cerrado en el cierre de T-7c (H1):** `M9.solicitaciones_por_elemento` (código de
  T-7b) tomaba la resultante ENTERA de cada empuje con su brazo desde el arranque, y su
  docstring lo llamaba «del lado seguro»: lo era para el cortante y no para el momento
  (el tramo bajo el arranque restaba). Ahora `M9.empujes_sobre_el_arranque` integra cada
  diagrama sobre el arranque: el suelo con el diagrama de tres partes del ensamble
  truncado en e_z (`M9.diagrama_del_suelo_sobre`, el mismo que
  `M9.acciones_sobre_una_seccion` usa en el cuerpo del ciclópeo), escalado a la
  resultante de cada carga para que valga igual con el activo y con el reposo; la
  sobrecarga uniforme; el agua del relleno con su triángulo; y la inercia de la
  **pantalla sola** (la de la zapata no la carga). Dorado de control del auditor,
  reproducido a mano: muro de tanteo, activo 26.491 / 21.466, reposo 43.502 / 35.402 kN/m
  y kN·m/m; A_s de resistencia 476 mm²/m y mínimo con M_cr 630.7 mm²/m (la misma Ø 1/2"
  @ 0.20). La estabilidad externa no usa esta solicitación y **no cambia** (las filas E1 a
  E3 de A-01, idénticas: medido).
- **Lo que es del proyecto y se declara:** (1) el cortante en la cara se integra **también**
  sobre el arranque: es estática (la fuerza que cruza la sección es la que está por
  encima de ella), y la fuente no pide otra cosa; se toma en la cara y no a d_v de ella
  (lado seguro, 5.7.3.2). (2) El diagrama del suelo es el del **plano del talón** truncado
  en el arranque; con el relleno que sube sobre el talón llega más arriba que la
  pantalla, y es cota superior de la presión sobre su cara. (3) El incremento sísmico:
  la fuente da el PUNTO de aplicación (`punto_aplicacion_incremento_sismico`, 0.6·h), no
  el diagrama; el proyecto toma el **único diagrama lineal** con esa resultante
  (2H/h·(2 − 3f) en la base, 2H/h·(3f − 1) en la corona: con 0.6, un trapecio cuatro
  veces más cargado arriba); bajo h/3 el triángulo de h/3 y, sobre 2h/3 —fuera de la
  ventana—, la resultante entera a su altura. (4) La resultante a h/2 de C11.6.5.4 es un
  diagrama **uniforme**: integrado sobre el arranque mueve el momento y el cortante.
- **Por qué:** es la estática de la sección del arranque, y la que el cuerpo del
  ciclópeo ya usaba; el docstring de T-7b decía «del lado seguro» y para el momento no lo
  era.
- **Qué haría falta:** nada para la pantalla; el alero por secciones es T7C-04.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad.py::empujes_sobre_el_arranque`

## T7C-13 · El cierre de T-7c aplicó las doce correcciones de la auditoría

- **Cerrado (2026-11-13):** H1 (T7C-12); H2 (el armado del muro que no cede con k_h0,
  T7C-02); H3 y la pregunta 5 (la fisuración de 5.6.7, fila A6, T7C-06); H4 (la fila A8:
  la altura de la zapata sobre su refuerzo inferior frente a los 300 mm de E.060 15.7,
  con el recubrimiento con que se arma; la zapata de 0.37 m de A-01 da 0.272 m y **no
  cumple**: no se itera, se dice —hasta la verificación de fórmulas, que corrigió la
  regla del piso y con ella A8 cumple por construcción en el cabezal de regla, ficha
  T7V-03—); H5 (la junta del arranque del ciclópeo, T7C-09); H6
  (el vano, la losa y el dentellón en el aviso, T7C-04); H7 (la fila A7 del f'c por
  durabilidad, que decide cuando el análisis químico existe, y los textos que nombraban
  A6, A5 y R4/R5 donde el código dice A7, A1 y C4/C5); H8 (d_v ≤ d_e, T7C-03); H9 (el
  aviso cuando el reposo factorado de mínimos deja la resultante fuera de la base: en
  los dos cabezales de A-01); H10 (la sensibilidad de K0 con talud, T7C-02); H11 (los dos
  mutantes vivos, T7C-08); H12 (el sufijo `_SI` en las conversiones de AASHTO y
  `RECUBRIMIENTO_BARRA_GRUESA_DESDE` en `constantes_normativas`, junto a la tabla de E.060
  7.7.1 cuya fila parte). Y las preguntas 1 (T7C-10), 2 (T7C-05), 4 (T7C-03) y 6
  (T7C-11, no aplicada).
- **Lo que la auditoría pidió y no se hizo como lo pidió:** en H3/pregunta 2 la premisa
  de que el recubrimiento de cota es «el lado inseguro de la fisuración» no la sostiene
  la aritmética (con más d_c la ecuación da menos espaciamiento: es la comprobación más
  exigente); el aviso dice dónde la cota deja de ser el lado seguro, que es con un
  ambiente corrosivo (T7C-05).
- **Por qué:** la auditoría adversarial (AJUSTADO) y las resoluciones del orquestador.
- **Qué haría falta:** lo abierto de cada ficha que cita.
- **Dónde vive:** `src/modulos/M9_cabezal/armado.py::ensamblar_armado`

# Parte LII — Lo que la verificación de las fórmulas de los cierres de T-7b y T-7c dejó escrito

Un verificador recalculó a mano y contra el PDF las fórmulas del cabezal (estabilidad y
armado, M9) y de V5 y V8 (M4 y M5) ya integradas (`451a10a` y `2b13dc1`): **AJUSTADO**,
seis puntos conformes y tres con defecto. Esta pasada (2026-11-13) corrige los tres y un
matiz de texto; los seis conformes no se tocan. Ningún diámetro, sección, material ni HW
del fixture se mueve.

## T7V-01 · V8 con el caudal que no cabe en flujo uniforme compite con el perfil de la lámina; el escalón de la regla de E-A en 1.2 D sigue ahí y lo cubre la guardia

- **Cerrado (punto 3, MEDIA, lado inseguro):** `M4.hidraulica_a_presion` llamaba a
  `hw_gobernante` **sin** perfil («lleno no hay lámina que integrar»), de modo que la
  aproximación h_o = (d_c + D)/2 competía sin las dos reglas del HDS-5 núm. 3.3.3 (pág.
  impresa 3.24) que `resolver_control` aplica desde E-A. Que el caudal no quepa en flujo
  **uniforme** no quiere decir que el barril vaya lleno. Ahora calcula el perfil
  (`perfil_lamina` no necesita tirante normal) y gobierna con él: entre 0.75 y 1.2 D la
  carga de salida es la mayor de la aproximación y del remanso, y se avisa; bajo 0.75 D
  la aproximación no se usa y rige el remanso, con aviso. Control del verificador (tubo
  de A-01, S 0.003, L 60 m, TW 0): HW(1.0213 m³/s) pasa de 0.9570 a **0.9890 m** ≥ 0.9654
  m. A-01 no cambia (gobierna la entrada: 1.588 m, 43.69 msnm). Y `M5.v8_evento_extremo`
  lleva la guardia HW_ext ≥ HW de diseño: si no se cumple, juzga con la de diseño y lo
  avisa por `Verificacion.avisos`, que `InformePunto.avisos()` recoge.
- **Por qué aviso y no «método no evaluable» bajo 0.75 D:** la fuente dice que la
  aproximación «should not be used», y la misma fuente dice qué hacer (pág. 3.12: el
  cálculo de remanso desde la salida, que M4 tiene). Es la misma decisión de E-A para
  la lámina libre; levantar `MetodoNoEvaluableError` habría sido negar un método que
  existe.
- **Abierto, medido y no corregido:** la regla de E-A tiene un escalón **propio** donde
  la aproximación cruza HW/D = 1.2: por debajo compite el remanso y por encima deja de
  competir. En el tubo de A-01 con S 0.006, L 18.869 m y TW 0.5 m, los dos caudales en
  lámina libre: 1.1507 m con 1.276 m³/s (rige el remanso) y 1.1394 m con 1.290 m³/s (rige
  la entrada): un caudal mayor con 11 mm menos. Es de `M4.resolver_control` (E-A,
  conforme en la verificación) y no se tocó. Para V8 lo cubre la guardia; para el caudal
  de **diseño** queda como está: es el umbral que la fuente escribe.
- **Qué haría falta:** decidir si sobre 1.2 D el remanso sigue compitiendo cuando alcanza
  la entrada y pide más carga (sería ir más allá de la letra del HDS-5, que ahí da la
  aproximación por buena); y el barrido en otras secciones y en el marco, que la
  verificación no hizo.
- **Dónde vive:** `src/modulos/M4_control.py::hidraulica_a_presion`

## T7V-02 · El η de AASHTO 1.3.2.1 es del cruce: el cabezal lee el mismo η_I que el conducto, y η_D y η_R son suyos

- **Cerrado (punto 9, MEDIA; cierra T7C-11):** `M9.modificador_de_carga` arma η = η_D·η_R·η_I
  y `M9.combinaciones_de_estabilidad` y `M9._combinaciones_en_reposo` lo llevan dentro de
  cada factor de Resistencia I: η_i = η ≥ 0.95 en las cargas de γ máximo y 1/η ≤ 1.0 en
  las de γ mínimo (Ec. 1.3.2.1-2 y -3, pág. impresa 1-3); 1.00 en el Evento Extremo I y
  en Servicio («For all other limit states», 1.3.3, 1.3.4 y 1.3.5). Rige en la
  estabilidad LRFD y en el armado; el marco ASD de E.050 y el contraste de E.060 no lo
  llevan. **η_I es uno**: la clave `eta_importancia_operativa_conducto` [A] (1.05), la
  misma que lee la Fase 8 del conducto; no se duplicó el número y el concepto del
  criterio dice ahora que rige el cruce (la clave conserva su nombre). **η_D y η_R** son
  dos [A] nuevos del cabezal, `eta_ductilidad_cabezal` y `eta_redundancia_cabezal`, 1.00
  convencional con ventana 0.95–1.05: la fuente obliga a separarlos del conducto, porque
  el 1.00 de éste sale de 12.5.4 (estructuras enterradas) y no alcanza al cabezal.
  El paso de combinaciones y el del régimen del armado lo imprimen con sus citas.
- **Lo que es lectura del proyecto:** el agua (WA) y la sobrecarga viva (LS) tienen un
  solo factor en la Tabla 3.4.1-1; se leen como cargas de γ máximo en las dos
  combinaciones, y solo DC y EV llevan 1/η en la de mínimos (`Interpretacion` de la cita
  `AASHTO_LRFD_9.1.3.2.1#ETA`, con lo que juega en contra).
- **Por qué importa:** en el muro de tanteo el deslizamiento LRFD estático **cambia de
  veredicto** con η (37.177 > 37.156 kN/m; con 1.00, 35.407 ≤ 38.607). En A-01 con los
  datos de prueba ningún veredicto cambia y el talón de salida pasa a Ø 1/2" @ 0.15.
- **Abierto:** los dorados del muro de tanteo de T-7b y T-7c (`CP_T7B_*`, `CP_T7C_*`) **no
  se rehicieron uno a uno**: se calcularon con los factores de la tabla (η = 1.00) y el
  fixture `tanteo` de los dos archivos declara ahora η_I = 1.00 para que sigan fijando
  la aritmética del ensamble; lo que η hace con el 1.05 de archivo lo fija a mano
  `CP_T7V_ETA` (las dos combinaciones, E1 a E3 y la pantalla en reposo). Y η_R = 1.00 es
  una elección: la pantalla en voladizo tiene un solo camino de carga y clasificarla
  como no redundante (≥ 1.05) es del Propietario.
- **Qué haría falta:** la decisión del Propietario sobre η_R y η_D del cabezal.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::modificador_de_carga`

## T7V-03 · El piso de la zapata armada se construye con la lectura de A8: 300 mm al eje de la capa inferior, con el recubrimiento con que se arma y la mayor barra del catálogo

- **Cerrado (punto 7, BAJA):** `M9.peralte_minimo_zapata` daba 0.30 + 0.070 = 0.37 m, y la
  fila A8 —que mide hasta el eje de la barra con el recubrimiento con que se arma, nunca
  menor de 70 mm— no podía cumplir E.060 15.7 en ningún cabezal de regla (0.2722 m con la
  cota de 91.44 mm; 0.2937 m aun con 70 mm y Ø 1/2"). Ahora el piso es 300 mm + el
  recubrimiento de `recubrimiento_para_armar` + medio diámetro de la **mayor** barra del
  catálogo de propuesta (Ø 1": 12.7 mm): **0.40414 m** con la cota y 0.3827 m con 70 mm,
  sin redondeo. A8 cumple por construcción con cualquier barra del catálogo y sigue
  pudiendo fallar con una zapata declarada más delgada (CB6 la detecta en la geometría).
  La nota de A8 ya no ofrece «bajar el recubrimiento con el dato de exposición», que no
  alcanzaba, y la fila imprime las tres lecturas de «medida sobre el refuerzo inferior»
  diciendo cuál usa.
- **Lo que es lectura del proyecto:** la altura se mide hasta el **eje** de la capa
  inferior (el peralte efectivo). La lectura hasta la cara **superior** de la barra, la
  más exigente, no la garantiza la regla: con Ø 1/2" da exactamente 0.3000 m y con una
  barra más gruesa queda por debajo (0.2968 m con Ø 5/8"); se imprime y no decide.
- **Abierto:** mueve la geometría de T-7a —la zapata de A-01 pasa de 0.37 a 0.40414 m— y
  con ella los números de estabilidad y de armado de los datos de prueba (declarados en
  los tests); el deslizamiento LRFD estático de A-01 sigue sin cumplir (ficha T7B-09).
- **Qué haría falta:** que el EMS y el expediente declaren la exposición y la categoría
  del acero (el piso baja entonces a 0.3827 m), y la decisión sobre la lectura de 15.7.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::peralte_minimo_zapata`

## T7V-04 · La aceptación de la verificación se escribió con el código; el rojo se midió contra la base

- **Qué se difirió:** escribir los tests en rojo con `xfail(strict=True)` antes del código,
  y la mutación de lo tocado.
- **Por qué:** una sola sesión para tres correcciones acotadas. El rojo se midió con el
  archivo final (`tests/test_t7_verificacion.py`, 28 tests) y el fixture sobre un árbol
  exportado de `2b13dc1`: **26 rojos y 2 verdes** (las dos guardias que valen antes y
  después: los marcos que no llevan η y la vía del «método no evaluable»).
- **Qué haría falta:** la mutación con el arnés de EXT-11 sobre `hidraulica_a_presion`,
  `v8_evento_extremo`, `modificador_de_carga`, `_resistencia_i_con_eta`,
  `peralte_minimo_zapata` y `_fila_de_peralte_de_zapata`.
- **Dónde vive:** `tests/test_t7_verificacion.py::test_p9_resistencia_I_del_muro_de_tanteo_con_eta_a_mano`

---

# Parte LIII — Lo que T-10 de la cadena T dejó escrito: la memoria M11 completa

T-10 (2026-11-13, FASE A sobre `2b13dc1`, rebasada e integrada sobre `2265d90` con las correcciones de su auditoría adversarial: AJUSTADO, 2 MEDIA y 5 BAJA, «ningún cálculo cambió») no calcula nada nuevo: hace que la memoria HTML
imprima lo que la CLI y el JSON ya publicaban, sin repetir lo idéntico, y regenera el índice
de fórmulas con corridas que sí dimensionan. Cierra `INF-3.4.7` («la Fase 9 no aparece en la
memoria HTML») e `INF-4.7`, y lo que la cadena llama `INF-5.1.9` (canónico `INF-5.1.10`). El
censo se midió con dos corridas de prueba —la de la guía de perfil y la de punta a punta de
T-7b/T-7c— y lo fija `tests/test_t10_memoria.py`, por clave del JSON.

## T10-01 · El objetivo de EXT-8 (< 15 KB y < 10 páginas por punto) no se alcanza sin perder sustento: lo repetido se quitó y se midió

- **Qué se difirió:** el objetivo del dictamen de EXT-8 para la memoria por punto. Medido con
  el método de `tests/test_ext8_rendimiento_gui.py` (coste marginal, cuatro puntos contra uno,
  a expediente con las entradas ampliadas y las declaraciones de la suite): **113.99 KB y
  32.33 páginas por punto en la base `2265d90` (las mismas que en `2b13dc1`); 107.04 KB y 31.00 páginas con T-10** (los
  techos de `KB_POR_PUNTO_MAX` y `PAGINAS_POR_PUNTO_MAX` quedan pegados a la medida). La de
  perfil, sin techo: 149.96 → 141.16 KB por punto. Lo fijo sube (un punto: 104 → 119
  páginas; 118 antes de las correcciones de la auditoría) porque entra la Fase 9 del proyecto, el alcance declarado, el anexo A.4 y tres
  umbrales en 0-ter. Por fase, sobre las corridas del censo: en A-01 a expediente, con la
  Fase 9 entera, el bloque del punto bajó de 721 a 612 KB; el peso está en el desarrollo de
  las verificaciones (CB, E y A del cabezal: ~300 KB) y en la traza de la Fase 9 (~100 KB).
- **Por qué:** lo que queda es contenido DEL PUNTO —fórmula, sustitución con procedencia,
  umbral y veredicto de cada paso— y un cabezal armado son más de cien pasos. Lo que estaba
  repetido se quitó: (1) los 50 pasos del armado que salían dos veces en A-01 (161 KB), una en
  el desarrollo de las verificaciones y otra en la traza de la Fase 9, que ahora remite; (2)
  todo paso IDÉNTICO a uno ya impreso en el documento (el 2.1 con la luz global en los cuatro
  puntos, el 4.2 de una misma carta), toda elección de proyecto idéntica (las de los
  criterios de corredor) y toda nota del proyecto idéntica, que se imprimen una vez con su
  ancla y después como una línea con su enlace. Recortar sustituciones o pasos para llegar a
  una cifra sería perder lo que la memoria tiene que sostener.
- **Decisión del dueño (2026-11-13):** los techos remedidos se ACEPTAN; se remidieron otra
  vez tras las correcciones de la auditoría (el mismo marginal: 107.04 KB y 31.00 páginas) y
  quedan pegados a la medida.
- **Qué haría falta:** una memoria por punto y un anexo común por obra (el formato de las
  págs. 110–122 del PDF guía, que imprime UNA tabla de cargas por cabezal sin el desarrollo
  paso a paso), si el dueño acepta que el desarrollo completo viva en un anexo digital.
- **Dónde vive:** `src/modulos/M11_reporte/pasos.py::_YaImpreso`

## T10-02 · El índice de fórmulas se genera con dos corridas de PRUEBA que sí dimensionan, y no imprime los valores que un módulo escribe en una procedencia

- **Cerrado (T-10):** la corrida de referencia de I4 no dimensionaba ningún punto (V5 sin
  método) y el índice no podía mostrar las Fases 6 a 10. Desde T-10 son dos
  (`CORRIDAS_DE_REFERENCIA`, en `tests/fixtures/corridas_de_referencia/`): `perfil_guia`
  —la de `docs/guia_perfil.md`, que dimensiona los cuatro puntos, B-01 con el TW de 0.30 m de
  la guía y no con el de 1.00 m de la línea base— y `expediente_cabezal` —la de punta a punta
  de T-7b/T-7c, con A-01 hasta el armado—. Ningún valor es nuevo: un test los compara con los
  bloques de la guía y con el AST de los tests de T-7c. El índice pasa de 159 pasos, 28 fórmulas y
  19 fundamentos a 476, 197 y 79 de 122, y la fila del paso «cuál control gobierna» cita el HDS-5
  3.3.5 (INF-5.1.10).
- **Abierto:** un módulo puede escribir VALORES dentro de una procedencia («D' = (D + yn)/2,
  con D = 0.900 m e yn = 0.627 m…», paso 6.5); el índice los enmascara (`_sin_valores`:
  «= número» y número con unidad) para seguir sin imprimir números. Los fundamentos de la
  hidrología CALCULADA (`--cuencas`, `--estacion`) y de las ramas que estos datos no recorren
  siguen en el cuadro de «no ejercitados» del propio índice.
- **Qué haría falta:** una tercera corrida con la hidrología de prueba de
  `tests/fixtures/hidrologia/`, para ver la Fase 1-bis calculada en el índice. **Decisión del
  dueño (2026-11-13): la hace T-11**, como una entrada más de `CORRIDAS_DE_REFERENCIA`.
- **Dónde vive:** `src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`

## T10-03 · V4b, V6 y V9 ganan paso, y el censo de lo que no puede tener fundamento queda vacío

- **Cerrado (T-10):** las tres verificaciones salían como un hueco censado. V4b tiene
  `F5.V4b` con el verbo DEFINE sobre la frase del HDS-5 que DESCRIBE la banda 1.0–1.5 de las
  agencias de EE. UU. (cita nueva `HDS5_3ED.2.2.5d#AGENCIAS`, pág. impresa 2.10, PDF 72,
  carácter DEFINICIÓN, verificada contra la página): el tope sigue siendo la adopción [A]
  `HW_D_max` y el umbral lo dice; y lleva la nota de §15.6.3 en la Familia C, que el test de
  M5 pedía «el día que V4b tenga fundamento». V6 tiene `F5.V6` con RECOMIENDA, sobre la
  oración del núm. 4.1.1.3.4 a) que recomienda la sección sin subdivisiones con arrastre.
  V9 tiene `F5.V9` con DEFINE, y juzga contra la cita de la serie de su norma de producto
  (M 170M 7.2.1, M 36 Table 6, M 294 7.2.1) cuando el tope sale de ella.
- **Abierto:** cuando el tope de V9 es de disponibilidad de mercado (`D_max_catalogo` [A]) o
  la progresión del marco (`secciones_cajon_normalizadas` [A]) el paso SUSTITUYE y no juzga
  —sin umbral ni veredicto; el veredicto está en la tabla del punto—, porque un catálogo no
  tiene numeral (NOR-PRO-01, NOR-PRO-02). Las entradas de V4b, V6 y V9 en
  `UMBRALES_DE_VERIFICACION` dicen, como la de V10, que ninguna cita fija el número.
- **Decisión del dueño (2026-11-13):** V9 sin veredicto cuando el tope es de catálogo o de la
  progresión del marco: ACEPTADO.
- **Qué haría falta:** nada para cerrarlo; la tupla `SIN_FUNDAMENTO` se conserva vacía para la
  verificación que mañana no pueda tener fundamento, y dos tests la ejercitan con una entrada
  de prueba (`test_traza_punto`, `test_indice_formulas`: corrección H3).
- **Dónde vive:** `src/normativa/fundamentos.py::SIN_FUNDAMENTO`

## T10-04 · El censo JSON ↔ memoria se mide por clave, y tres claves de texto se imprimen de otra forma

- **Cerrado (T-10):** todo número que el JSON publica de un punto dimensionado aparece en su
  bloque de la memoria —o en el paso, la elección o la nota idénticos a los que enlaza—, y
  todo aviso de `InformePunto.avisos()` sale en las tres vistas. Lo que faltaba y se cerró:
  las tablas del armado (secciones críticas y tabla por elemento) y de las solicitaciones del
  cabezal; la excentricidad de cada combinación; 40 de los 47 avisos de A-01 a expediente
  (los indicadores E y A2 del cabezal, los del armado); el reparto por extremo de 7.B (paso
  7.B.3b, emitido por M7); las columnas `cota_fondo_entrada` y `cota_coronacion_canal`; el
  alcance de la norma de producto; la nota de la cota de entrada (`CotaDeEntrada.nota`, una
  fuente para el JSON y la memoria); el origen del caudal de VB2; las citas del filtro; la
  embocadura del punto que no llega a la Fase 9; y la Fase 9 del PROYECTO —la cadena sísmica
  eslabón por eslabón, K_AE, recubrimientos, cuantías y notas—, que solo estaba en la CLI y
  el JSON. Y 17 anclas rotas de T-5 y T-9 (pasos de la Fase 8 y de la 10 que el anexo no
  escribía).
- **Abierto:** tres claves de texto se imprimen de otra forma y están censadas con su razón
  (`TEXTOS_CON_OTRA_VISTA`): el mensaje de un bloqueo por criterio pendiente (la memoria
  imprime sus partes), el rótulo de fase de cada verificación y los ids de las citas del
  filtro (la memoria imprime su numeral, y el test lo comprueba).
- **Corregido tras la auditoría (H1):** el censo buscaba cada número en TODO el bloque del
  punto («0.40» sale 99 veces en A-01) y cuatro mutantes vivían. Desde las correcciones cada
  entrada de la tabla de armado, de sus secciones, de las combinaciones (con su excentricidad)
  y de las solicitaciones se compara con SU fila, localizada por su clave; el bloque del
  proyecto se imprime en tablas con la clave en la primera columna (cabezales, K_AE y K_A,
  recubrimientos, cuantías, eslabones de la cadena) y se censa así; y el anexo A.4 exige la
  ventana de cada clave en su fila. Los cinco mutantes de la auditoría (M-A, M-E, M-L, M-M y
  el del hueco, M-N) mueren.
- **Qué haría falta:** nada; un texto nuevo del JSON que la memoria no lleve rompe el test.
- **Dónde vive:** `src/modulos/M11_reporte/proyecto.py::bloque_cabezal_proyecto`

## T10-05 · Lo que el dueño decidió no hacer se imprime como ALCANCE, en las tres vistas

- **Cerrado (T-10):** `modelos.ALCANCE_DECLARADO` dice, con su ficha y su símbolo, cinco cosas
  que el expediente NO hace por decisión declarada: el armado de la sección del marco
  (T5-07), el cabezal paralelo a la vía (T7A-03), la iteración del ancho de la zapata del
  cabezal (T7B-09), el peso propio del marco en V7 (T3-08) y las Figuras 3.3–3.4 de HEC-14
  (T8-08). Lo imprimen la CLI (bloque ALCANCE DE LA CORRIDA), el JSON (`alcance.declarado`) y
  la memoria (`bloque_alcance`). Las etapas que no se completaron dicen además qué SON
  —«espera un dato», «método no evaluable»…— al lado del tipo técnico
  (`ROTULO_TIPO_DE_BLOQUEO`).
- **Por qué:** sin esta lista, la memoria callaba lo que no hace y un lector lo leía como
  omisión.
- **Qué haría falta:** retirar cada entrada cuando su ficha se cierre.
- **Dónde vive:** `src/modelos/hidraulica.py::ALCANCE_DECLARADO`

## T10-06 · El anexo de sensibilidad imprime la ventana y no recalcula: el barrido sigue siendo PF-3

- **Cerrado (T-10):** el anexo A.4 de la memoria lista cada criterio [A] que la corrida usó
  con su valor efectivo, su ventana, su modo de resolución y los puntos cuyo cálculo lo nombra
  (`criterios_A_por_punto`, leído de lo que cada punto emitió). Todo [A] con valor tiene
  ventana (los siete [A] sin ventana son de expediente y sin valor, que es lo que el
  invariante de `CLAUDE.md` admite).
- **Abierto:** el barrido que recorre la ventana es `cli.py --barrido` (PF-3; desde UI-3
  también el botón «Barrido…» de la pestaña 2) y no corre dentro de la memoria: el anexo no dice cómo cambia el diseño dentro de la ventana, solo cuál
  es.
- **Qué haría falta:** si se quiere el efecto en la memoria, un anexo que lea los volcados de
  un barrido ya corrido, nunca uno que corra dentro del exportador.
- **Dónde vive:** `src/modulos/M11_reporte/umbrales_anexos.py::anexo_sensibilidad`

## T10-07 · La aceptación de T-10 se escribió después del código; el rojo se midió contra la base

- **Cerrado (T-10):** `tests/test_t10_memoria.py` no se escribió en rojo con
  `xfail(strict=True)`: el censo tenía que medirse antes de saber qué fijar. El rojo se
  midió con el archivo final sobre un árbol de `2265d90` (el número, en el informe
  de la FASE A).
- **Por qué:** el censo es el entregable; los tests lo fijan.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M11_reporte/umbrales_anexos.py::anexo_sensibilidad`

## T10-08 · Las correcciones de la auditoría adversarial de T-10

- **Cerrado (2026-11-13):** H1 (el censo por clave, T10-04); H2 (el paso 7.B.3b ya no atribuye
  su fórmula a HDS-5 2.2.4 b., que no la escribe: la cita queda como contexto y lleva la misma
  nota del proyecto que el 7.B.3, `M7.NOTA_ALGEBRA_DE_LA_LONGITUD`); H3 (los dos tests que
  quedaron vacuos al vaciar `SIN_FUNDAMENTO` se ejercitan con una entrada de prueba); H4 (los
  docstrings y comentarios de M5, `modelos`, `traza_punto`, `indice_formulas`, M11 y
  `UMBRALES_DE_VERIFICACION` que todavía decían «V4b no emite paso» o «ninguna cita fija el
  número»); H5 (V4b sin «que es más exigente»; el rótulo de la frase del anexo sigue al
  CARÁCTER de la cita —una DEFINICIÓN «describe», no «fija»: `ROTULO_DE_LA_FRASE_POR_CARACTER`—;
  la elección de V4b se imprime como ventana); H6 (un test con la V8 acotada de
  `test_t7_verificacion` comprueba que su aviso sale UNA vez en la memoria); H7 (la regla de
  la excentricidad vive en el dato, `CombinacionDeEstabilidad.excentricidad_publicable`, y el
  0.8·f_r y el piso de 25.4 mm salen de sus constantes).
- **Por qué:** la auditoría adversarial (AJUSTADO) y las resoluciones del orquestador.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M11_reporte/umbrales_anexos.py::ROTULO_DE_LA_FRASE_POR_CARACTER`

# Parte LIV — Lo que T-11 de la cadena T dejó escrito: la validación integral de las tres familias

T-11 (2026-11-13, sobre `14f6138`, integrado con las correcciones de su auditoría
adversarial) valida y no cambia cálculo: corre el fixture de punta a punta a `--alcance
expediente` con un juego de DATOS DE PRUEBA, lo contrasta con los ejemplos resueltos de
HDS-5 y HEC-14, barre la sensibilidad de los [A] (la lista se deriva del censo de
criterios), y deja la lista exacta de lo que sigue requiriendo entrada del proyecto. Lo
que destapó de cálculo no lo corrigió la FASE A: lo dejó reproducido en
`xfail(strict=True)`, y lo corrigió después la sesión de T11-03 (ficha T11-03, que quedó
cerrada en parte). La auditoría adversarial (AJUSTADO: 1 ALTA, 6 MEDIA, 7 BAJA, ninguna de
fórmula ni de cita) se aplicó entera en el cierre (fichas T11-09 y T11-10). Los cuatro
documentos de la validación se GENERAN (`docs/validacion_integral.md`,
`docs/validacion_hds5.md`, `docs/validacion_hy8.md`, `docs/validacion_sensibilidad.md`)
y un test regenera cada uno.

## T11-01 · El juego de prueba entra sólo por las puertas de la CLI y no rellena ningún vacío del archivo

- **Cerrado (T-11):** el juego vive en un módulo con la cabecera «DATOS DE PRUEBA, NO DEL
  PROYECTO» (un CSV de puntos y un JSON de datos externos no admiten cabecera) y se
  materializa en los archivos que la CLI lee: copia del CSV, `--datos-externos`,
  `--datos-sitio`, `--cuencas`/`--estacion` y `--declarar`. Reutiliza los datos de T-7b,
  T-7c, T-8 y la guía. Decisiones del juego, dichas y con su otro lado medido como
  variante: B-01 corre con el TW de 0.30 m de la guía (con el de 1.00 m de la línea base no
  dimensiona por V2), con el tramo de cuneta empezando a 150 m (sin él, VB1 no cumple por
  los 530 m desde A-02), el freático a 3.0 m (con 2.0 m la sísmica de salida de A-01 y A-02
  es «método no evaluable», ficha T7B-06), y C-01 con su TW igual al tirante normal del
  canal que el mismo juego declara (0.41 m; corrección H7). **El juego PISA dos criterios
  con valor de archivo** (`drenaje_trasdos` y `factor_muro_eleccion`, decisiones que el
  dueño confirmó; `PISA_EL_ARCHIVO_PORQUE`): por eso la corrida TITULAR del documento es la
  variante `decisiones_de_archivo` y el juego es la variante que ejercita la cadena sísmica
  y el caso drenado (corrección H2). Ningún valor se escribió en `criterios_adoptados.py`,
  `datos_sitio.py` ni `constantes_normativas.py` (un test lo fija).
- **Abierto:** son valores de prueba; los del sitio los dan los estudios del contrato. Dos
  líneas de plausibilidad no sostienen su dato y lo dicen: el caudal del evento extremo
  (1.11 veces el de diseño, de T-7b; medido: desde 1.8 veces A-01 pasa a Ø 1.05 m por V8) y
  los sulfatos de 500 ppm (insignificantes para el concreto por la Tabla 4.4 de E.060,
  agresivos para el acero galvanizado por el umbral de AASHTO LRFD 11.10.6.4.2a).
- **Qué haría falta:** las entradas de la §7 de `docs/contrato_entradas.md`.
- **Dónde vive:** `tests/fixtures/juego_validacion_integral.py::OMITIDAS_A_PROPOSITO`

## T11-02 · La lista exacta de lo que detiene una etapa se MIDE sobre dos bases, y el contrato de entradas la repite en su §7

- **Cerrado (T-11, con la corrección H1 de su auditoría, ALTA):** la lista es lo que la
  corrida SIN juego bloquea más lo que, quitado de a uno, hace aparecer un bloqueo en
  CUALQUIERA DE LAS DOS BASES: el juego y el juego con las decisiones de archivo
  (`quitar_una_en_la_titular`). Medida sólo sobre el juego, no veía el peso específico
  saturado del relleno, que con el `drenaje_trasdos` de archivo detiene 24 etapas, y la §7
  contradecía a la §3.3 del contrato. Cada bloqueo cae en una de tres clases (entrada del
  proyecto, criterio que se declara, método diferido con ficha) o el test falla. La §7 del
  contrato nombra exactamente las mismas veintiuna entradas, con su clase, ADEMÁS de las
  columnas obligatorias del CSV, y un test las compara en los dos sentidos. Corrección 3.4
  del contrato: sin `exposicion_quimica_ems` o `categoria_refuerzo_aashto` la Fase 9 del
  PROYECTO queda bloqueada en la 9.4 (decía sólo «aviso»).
- **Abierto:** las condicionales que ninguna de las dos bases dispara no se miden: se
  NOMBRAN (`CONDICIONALES_NO_MEDIDAS`: el tratamiento FEN, el perfil del HDPE, las clases de
  M 170M, la costura empernada del TMC, el ancho tributario, el derecho de vía,
  `TW_receptor`, las dos de h_eq de AASHTO 3.11.6.4, Meyerhof en talud y `q_n_kpa` en roca)
  y la §7 las repite; las fija el test de su prompt.
- **Qué haría falta:** nada en el programa; si se abre una entrada nueva, el test pide su
  fila en la §7.
- **Dónde vive:** `tests/apoyo/validacion_integral.py::lista_exacta`

## T11-03 · El escalón que no cabe bajo la subrasante es «no factible por rasante», con el delta de 7.A sólo cuando es geometría pura

- **Cerrado (corrección de T11-03, 2026-11-13; hallazgo H4 de la auditoría de T-11):**
  **(A)** `MD.disenar_material` reconoce por geometría (`_escalon_sin_cabida`) el escalón
  cuya clave no cabe, lo anota con sus dos cotas (`PasoDiseno.sin_cabida`) y descarta el
  material POR RASANTE; el punto ya no nombra un dato inválido de `cota_subrasante`. Mismos
  escalones y mismas verificaciones que antes. **(B)** CLAUDE.md («si aplica, el delta de
  rasante») y el docstring de MD («sale vacío a propósito») se resolvieron con la v8 (§7.A,
  §7.B y su nota): MD no mueve la rasante y pide a `M7.tamizado_rasante` el delta DEL
  ESCALÓN QUE NO CABE, que informa sólo si ese escalón cumple lo evaluado y gobierna el
  recubrimiento (`_delta_de_7A`); es cota inferior para ese escalón, y lo dice. A-01 sin
  TW: 0.320 m; B-01 con TW = 1.00 m, sin delta y con V2 en el motivo. **(C)** el dato
  inválido del punto que levanta la Fase 5 sale con su `campo` (`_exigir_datos_validos`).
- **Cerrado (abiertos 3 y 4, decisión del dueño, README §8; `tests/test_t11_03_diagnostico.py`):**
  **(3)** un candidato que cierra no se adopta si la Fase 5 detuvo a uno anterior por un dato
  inválido DEL PUNTO: sale ése, con su `campo` (`_exigir_datos_validos_al_aceptar`, la regla
  de T4-10). **(4)** el que M3 o M4 levantan antes de la Fase 5 cuenta para «detuvo a todos»:
  la rama de error de la línea base sale DATO_INVALIDO sobre `D`, no «no factible».
- **Abierto:** (1) el delta no es el remedio verificado del punto: con la rasante nueva la
  corrida se repite, y un escalón menor que hoy sólo incumple V4 o V7 podría cerrar con
  menos. (2) Si el escalón que no cabe incumple sólo V4, el tamizado daría un delta por
  resguardo, que depende del HW: no se informa. (5) cerrado en VE-7 (ficha VE7B-03). (6) El inválido de
  antes de la Fase 5 que detiene a UN solo material no bloquea ni decide (el `campo` del
  arranque: cerrado en VE-7, ficha VE7B-01).
- **VE-6 (ítem 34):** el abierto (2) queda cerrado bajo control de ENTRADA (ficha VE6-34);
  bajo salida, con el HW de entrada desde VE-7 (ficha VE7B-04).
- **Qué haría falta:** para (1), el tamizado previo de 7.A corrido antes del bucle con la
  sección máxima supuesta, que el servicio no corre; para (6), decisión del dueño.
- **Dónde vive:** `src/modulos/MD.py::_resumen_por_rasante`

## T11-04 · Validación externa: HDS-5 y HEC-14 contra sus ejemplos resueltos; HY-8 sólo como procedimiento, con la tolerancia que el dueño aceptó

- **Cerrado (T-11):** `docs/validacion_hds5.md` se genera con los casos de `CP_HDS5_DG1` y la
  cuenta del test de T-2 (importada): 38 de 43 cifras dentro del 3 % de lectura, las cinco
  restantes censadas con su causa (la diferencia, desde las correcciones, con dos decimales
  y la misma que el motor da: H12), los cinco controles iguales, y las dos filas de metal
  corrugado dentro del intervalo del n de la Tabla B.1. Suma los cinco ejemplos de HEC-14
  que T-8 usó como oráculo, cada cifra buscada en el texto de su página (marca `pdf`): 19
  cifras, TODAS dentro del 1 % —la profundidad 3.3·D50 del apron SI cae sobre la frontera
  (0.495 frente a «0.50 m», redondeo de la fuente), y la comparación sin tolerancia la
  censaba fuera por 1e-17 (`TOL_FRONTERA_DE_BANDA`)—.
- **Abierto:** HY-8 no está en el entorno: `docs/validacion_hy8.md` dice qué cargar por
  punto (Roadway Data con la rasante de cada punto incluida), qué comparar y con qué
  tolerancia, y no afirma ningún resultado. La tolerancia es la que el dueño ACEPTÓ el
  2026-11-13 como **criterio del proyecto, NO normativo** (≤ 3 % coincide, 3–10 % se
  explica, > 10 % discrepancia; sobre HW y HW/D; control distinto → explicar; velocidad sin
  veredicto donde el programa no la saca del mismo modo; versión y fecha de HY-8
  obligatorias), y un test fija las cinco reglas (corrección H5). Ningún ejemplo publicado
  toca la transición 3.5 < q* < 4.0, el perfil de la lámina, V8 a presión, la Fase 8 ni el
  cabezal.
- **Qué haría falta:** que el autor corra HY-8 con ese procedimiento y deje sus tablas.
- **Dónde vive:** `tests/apoyo/validacion_externa.py::juicio_hy8`

## T11-05 · La sensibilidad se mide con el barrido de PF-3 sobre el juego, una clave a la vez, y la lista se deriva del censo

- **Cerrado (T-11, con la corrección H3 de su auditoría):** 82 barridos sobre 80 criterios:
  los escritos a mano (los de PRECISIONES y los que necesitan valores propios) más TODO
  criterio con valor efectivo en el juego y ventana legible por máquina
  (`barribles_del_censo`); los otros 61 están por nombre en `NO_BARRIBLES` con su razón, y
  un test exige que las dos listas partan el archivo. La base es el juego (la variante que
  deja evaluar la sísmica), no la titular, y el anexo lo dice. Mueven el diseño dentro de
  su ventana diez criterios (once barridos): `v_max_concreto_eleccion` (3.0 m/s: A-01 a TMC
  de 1.20 m; con el TMC excluido por los sulfatos, A-01 se detiene en el dato del
  fabricante del HDPE), `regimen_v2b`, `borde_libre_y_sobre_d_max`, `embocadura_cabezal`,
  `seccion_receptor` sin `TW_m`, `espesor_pared_cajon`, `pendiente_minima_conducto`,
  `remanso_derecho_via`, `umbral_no_colapso_evento_extremo` y `origen_cota_fondo_entrada`.
  «Leído, sin efecto medible» se definió (material, sección, veredictos y HW con
  `TOL_HW_SENSIBILIDAD_M`; las demás magnitudes no se comparan).
- **Abierto:** un solo juego, sin producto cartesiano; los no barribles (ventana en prosa,
  por campo o de tabla) no se midieron, y lo dicen. El lado ALTO de la ventana de
  `n_manning_cajon` (HDS-5 B.3, 0.012–0.022 en vaciado in situ) no se podía declarar y
  el anexo no lo midió; desde T11-10 se declara como par (ficha T11-10). El criterio `v_max_concreto_eleccion` se queda SIN valor por decisión del
  dueño (rige 6.0 m/s de la Tabla Nº 10): su resultado es de la tesis y no cambia el
  fixture.
- **Qué haría falta:** repetir el anexo con los datos del sitio.
- **Dónde vive:** `tests/apoyo/sensibilidad.py::BARRIDOS`

## T11-06 · La hidrología calculada entra al índice de fórmulas con una tercera corrida de prueba

- **Cerrado (T-11, decisión del dueño de T-10, ficha T10-02):** `hidrologia_calculada` es
  el juego con la variante `caudal_calculado`, escrito en su carpeta por el apoyo de la
  validación (un test exige que sea, byte a byte, esa materialización) con un `LEEME.md`
  rotulado (tres de sus seis archivos no admiten la cabecera: corrección H12). Sus datos
  son NUEVOS de T-11, y el docstring de `src/indice_formulas.py` ya no dice lo contrario.
  Los ocho `FH.*` salen del cuadro de no ejercitados. La máscara de valores suma `m2`.
- **Abierto:** con las cuencas SINTÉTICAS de T-1 el caudal de A-01, A-02 y B-01 es de 19 a
  47 veces el declarado y los tres no caben bajo la subrasante (no factible POR RASANTE,
  ficha T11-03): **la cadena «caudal calculado → diseño» NO está validada con datos
  coherentes**. Veinte fundamentos siguen sin ejercitar (Fase 8 del TMC y del HDPE,
  ciclópeo…).
- **Qué haría falta:** un juego sintético de cuencas COHERENTE con el CSV (lote posterior a
  la cadena, prioridad baja, decisión del dueño del 2026-11-13); para la tesis, contrastar
  los caudales del fixture con el estudio hidrológico real.
- **Dónde vive:** `src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`

## T11-07 · El alcance declarado completa lo que el dueño dejó fuera

- **Cerrado (T-11):** `ALCANCE_DECLARADO` suma la velocidad de salida en la banda de régimen
  de M4 (T8-09, trabajo posterior a la cadena con las Figuras 3.3 y 3.4 de HEC-14) y el
  escalón de la regla de E-A en HW/D = 1.2 (T7V-01). Las otras cinco ya estaban (T-10).
- **Abierto:** cada entrada sale cuando su ficha se cierre.
- **Qué haría falta:** el prompt posterior a la cadena que digitalice las Figuras 3.3–3.4.
- **Dónde vive:** `src/modelos/hidraulica.py::ALCANCE_DECLARADO`

## T11-08 · La aceptación de T-11 no se escribió en rojo primero

- **Qué se difirió:** escribir la aceptación en rojo antes del código, como pide la regla
  común 4.
- **Por qué:** T-11 mide comportamiento que ya existía; lo nuevo (el juego, los cuatro
  documentos, la §7 del contrato, el alcance, la tercera corrida) se midió en rojo con los
  archivos finales contra la base `14f6138`, y el número está en el informe de la FASE A.
  Las correcciones de la auditoría tampoco: su rojo se midió con los cuatro archivos de
  tests finales contra el árbol previo (`10fb84b`), y el número está en el informe final.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t11_validacion_integral.py::test_las_tres_familias_llegan_a_la_fase_11_con_diseno`

## T11-09 · Tres correcciones de formato y transparencia que tocan el programa: `HW_salida_m`, la fila A7 y el tipo de cabezal del resumen

- **Cerrado (correcciones de T-11, H9, H10 y H8 de su auditoría; ninguna es cálculo):**
  **(H9, decisión del dueño del 2026-11-13)** `diseno.HW_salida_m` del JSON es `null` donde
  el control de salida no se forma —el perfil sustituye a la aproximación (HW_aprox/D <
  0.75, HDS-5 pág. impresa 3.24) y su remanso no alcanza la entrada—, con la aproximación
  descartada en `perfil_HW_aproximado_m`, y la línea «Control» de la CLI dice «salida no se
  forma»; el HW que gobierna, la entrada, los diámetros y los materiales no cambian (en la
  línea base: A-02 de dos JSON y su línea de texto). **(H10)** con el análisis químico
  declarado y sin f'c mínimo aplicable (exposición «insignificante» de la Tabla 4.4 de
  E.060, pág. impresa 38, y ninguna fila de la Tabla 4.2), la fila A7 existe con
  `EstadoDeVerificacion.NO_APLICA` y su razón; ningún veredicto ni número cambia.
  **(H8)** la columna «Tipo de cabezal» del cuadro resumen sale del punto
  (`M11.tipo_cabezal_del_punto`): la decisión única del Tablero 2.3 («tubo a ras del
  muro») es el borde de entrada del TUBO y se imprimía también en el marco.
- **Abierto:** nada desde T-12 (decisión del dueño del 2026-11-13 ~21:55 UTC), que cerró
  lo que quedaba: la fila «Control gobernante» de la MEMORIA —de las dos vistas, la completa y la
  resumida— ya no imprime «salida» con la aproximación descartada: dice «salida no se
  forma: el perfil no alcanza la entrada», la misma redacción y la MISMA condición que la
  línea «Control» de la CLI y el `null` del JSON. La regla vive desde T-12 en el dato
  (`PerfilLamina.salida_no_se_forma`, leída por `ResultadoHidraulico.salida_no_se_forma`);
  `cli.salida_no_se_forma` la delega y M11 la lee sin aritmética
  (`M11._celda_control_gobernante`, texto `M11.SALIDA_NO_SE_FORMA`). La aproximación
  descartada sigue impresa en la fila del perfil, rotulada HW<sub>aprox</sub>. Formato, no
  cálculo: en la línea base cambia sólo esa cadena de A-02 en `memoria_perfil_ancha.html`
  (README de la línea base); el HW que gobierna, la entrada, diámetros, secciones y
  materiales no se mueven (`tests/test_t12_entregable.py`).
- **Qué haría falta:** nada.
- **Dónde vive:** `cli.py::salida_no_se_forma`

## T11-10 · El lado alto de la ventana de `n_manning_cajon` no se puede declarar

- **Qué se difirió (hasta T11-10):** medir el n del marco con el num. B.3 del HDS-5 (0.012 a
  0.022 en un cajón vaciado in situ, según el encofrado), que la ficha del criterio da como la
  ventana hacia arriba —el lado seguro para el tirante y el HW— y dice que «se declara como el
  par de la especificación del encofrado». La forma era `str` y la puerta rechazaba el par con
  `ValueError` (medido en las correcciones de T-11, H3): la ficha prometía una declaración que
  la forma no admitía.
- **Cerrado (T11-10, decisión del dueño del 2026-11-13: «abrir la forma»):** la forma del
  criterio es la UNIÓN `(str, par_ordenado)`, como `k_v`; el valor de archivo no cambia
  (`concrete_boxes`). El rango del B.3 se LEE de la cita `HDS5_3ED.B.3#CAJON_IN_SITU` (pág.
  impresa B.2, PDF 204: «Manning's n values for cast-in-place boxes range from 0.012 to
  0.022», verificado contra la página) en `constantes_normativas.MANNING_CAJON_IN_SITU_HDS5`;
  su extremo inferior es el n_min de la fila del cajón de la Tabla B.1 (pág. impresa B.6, PDF
  208: 0.012-0.015). La puerta (`criterios_adoptados._verificar_par_de_encofrado`, por los
  tres caminos) rechaza con `ValueError` el par invertido, con booleanos o textos, de otro
  largo, no finito o fuera del rango; el consumidor (`M2._fila_manning_de_cajon`, segunda
  línea) lo detiene como `DatoInvalidoError` y lo usa en la regla de doble n como las columnas
  de una fila, con su propio paso (`F4.N_CAJON_IN_SITU`). Los editores tipados lo admiten por
  el campo único de la unión (sin campos nuevos); sin fila exige la nota, que dice de dónde
  sale el par. Y `declaracion.declarar_desde_tabla` rechaza sin nota un par que DIFIERE del de
  la fila elegida (EXT-V-02 extendido al par): sin eso la ventana emergente, que declara con
  fila y sin nota, registraba «proviene de la fila concrete_boxes» para un par que esa fila no
  escribe. La CLI lo declara con `--declarar n_manning_cajon=(0.013,0.016)`. Lo fija
  `tests/test_t11_10_n_cajon.py`, con C-01 de punta a punta.
- **Abierto:** la ventana emergente no tiene campo de nota (EB-06), de modo que el par del
  encofrado, que no es el de ninguna fila, se declara desde la pestaña 2 o la CLI, no desde
  ella. La línea base y los documentos generados no se regeneraron en T11-10 (la huella de
  `criterios_adoptados.py` cambia).
- **Qué haría falta:** nada para el criterio; regenerar la línea base y los documentos
  generados cuando el dueño lo indique.
- **Dónde vive:** `src/criterios_adoptados.py::_verificar_par_de_encofrado`

# Parte LV — Lo que T-12 de la cadena T dejó escrito: el repositorio listo para la sustentación

T-12 (2026-11-13, sobre `f77c5d4`, integrado con las correcciones de su auditoría) es el
último prompt de la cadena y no cambia cálculo: retira los PDF de normas
del repositorio, separa el material de proceso, rotula los fixtures, añade la licencia, el
`pyproject.toml` y el README de usuario, deja el manifiesto del registro en su estado
final, y —por decisión del dueño del 2026-11-13— entrega la memoria en dos vistas y lleva
T11-09 a la memoria.

## T12-01 · Los PDF de normas viven sólo en el repositorio de normas; la historia de git los conserva

- **Cerrado (T-12):** los dieciocho PDF de `normas/` se retiraron con `git rm` después de
  comprobar, uno a uno, que su sha1 es el de los del repositorio de normas
  (`INF-5.2.3`). `fuentes.directorios_de_normas()` devuelve sólo la carpeta de
  `NORMAS_DIR`; sin la variable no hay carpeta, `ruta_pdf` devuelve la ruta bajo
  `RUTA_SIN_ENLACE` (`$NORMAS_DIR/normas/<archivo>`, que no existe) y TODO test `pdf` se
  salta con un solo motivo (`conftest.py::pytest_runtest_setup`). Se retiraron
  `SOLO_EN_EL_REPO_NORMAS` (el censo transitorio de T-0) y
  `DIRECTORIO_NORMAS_DEL_REPOSITORIO`; la guardia de PC-23 comprueba que la app no
  versiona ningún PDF (`git ls-files`) y que el repositorio enlazado trae todo lo que el
  registro declara. El README recomienda que el repositorio de normas sea privado.
- **Abierto:** el `git rm` no reescribe la historia: los PDF siguen en los commits
  anteriores a T-12, y un clon del repositorio los trae. Quitarlos también de ahí exige
  reescribir la historia (`git filter-repo` y un empuje forzado sobre `main`), que rompe
  los SHA que citan el tracker y los documentos.
- **Decidido por el dueño (2026-11-13):** NO se reescribe la historia; el repositorio de la
  app queda privado, como el de normas, hasta la sustentación (lo hace el dueño en GitHub).
  Reescribirla sólo si se publica, y después.
- **Qué haría falta:** nada antes de la sustentación.
- **Dónde vive:** `src/normativa/fuentes.py::RUTA_SIN_ENLACE`

## T12-02 · El material de proceso vive en `proceso/`, fuera del entregable, y sus tests con él

- **Cerrado con salvedad (T-12, `INF-5.2.2`):** con `git mv` a `proceso/`:
  `.claude/agents/`, `docs/planes_mejora/` (con la cadena T), `docs/auditorias/` (con el
  tracker), `verificar_sesion.py`, `tests/apoyo/tracker.py` y, en el cierre (H5 de la
  auditoría), `docs/hoja_de_ruta_correcciones_v12.md` y `docs/auditoria_y_ruta_despliegue_v9.md`
  (prompts literales y asignación de modelos; nada los lee). La bitácora de conteos e
  incidentes de `CLAUDE.md` y sus reglas de corrección salieron ENTERAS a
  `proceso/bitacora_conteos_y_entorno.md` y `proceso/reglas_de_correccion_de_auditorias.md`.
  Los tests que leen ese material salieron con él (138 de los 6469 de la base) a
  `proceso/tests/`, que `proceso.verificar_sesion` corre; la suite del entregable es
  `tests/` (`testpaths`), `git archive` excluye `proceso/` (`.gitattributes`) y la suite
  pasa sobre esa exportación (H1).
- **Abierto (la salvedad):** quedan en `docs/` cinco documentos técnicos de origen de
  proceso —`ruta_familia_c.md`, que el código exige al importar (`vacio_verificado`), y
  `diseno_registro_normativo.md`, `resolucion_clase_sitio.md`,
  `manifiesto_datos_proyecto_vs_constantes.md` y `linea_base.md`— con menciones a las
  sesiones y, `ruta_familia_c.md`, a los modelos de IA. Las rutas viejas citadas en prosa
  no se reescribieron (la v8 entre ellas: su huella va en cada memoria); las traduce
  `proceso/README.md`.
- **Qué haría falta:** para quitar también esas menciones, depurar `ruta_familia_c.md`
  conservando las secciones que el código valida; decisión del dueño (aceptó dejarlos).
- **Dónde vive:** `proceso/tests/conftest.py::pytest_collection_modifyitems`

## T12-03 · La advertencia de fixture la pone el generador de la línea base, no el programa

- **Cerrado (T-12, `INF-5.2.4`):** las memorias HTML de `tests/linea_base_familia_c/`
  llevan en el título y al principio del cuerpo «FIXTURE DE PRUEBA, NO ES UN RESULTADO DEL
  PROYECTO», puesto por `regenerar.sh` con el envoltorio declarado
  `tests/apoyo/rotulo_fixture.py` DESPUÉS de la CLI; los dos `datos_referenciales_prueba*.md`
  empiezan por esa advertencia, y `entradas_ampliadas.json` la lleva en la clave
  `_advertencia`, la única de nivel superior que `servicio.cargar_datos_externos` admite
  sin leerla (`servicio.CLAVE_ADVERTENCIA_EXTERNOS`; tiene que ser texto).
- **Por qué así:** una bandera del programa para rotular «fixture» pondría en el producto
  un texto que una memoria real podría llevar por error, o que una de prueba podría
  perder: falsea en las dos direcciones. El generador sólo se invoca sobre el ejemplo.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/apoyo/rotulo_fixture.py::rotular`

## T12-04 · La memoria en dos vistas de la misma corrida; la ventana exporta las dos desde UI-2

- **Cerrado (T-12, decisión del dueño del 2026-11-13):** `M11.memoria_resumida_html` (con
  `exportar_html_resumida`, `exportar_pdf_resumida` y la plantilla
  `src/plantillas/memoria_resumida.html`) arma la vista para imprimir —por punto: la
  combinación adoptada, la tabla de verificaciones con su veredicto, los avisos, las etapas
  bloqueadas y los criterios [A] que el punto nombra con su valor y su ventana; para el
  proyecto: trazabilidad, alcance, cuadro resumen y pendientes— a partir del MISMO
  `Informe` que la completa, con sus mismos formateadores (`_filas_combinacion_adoptada`,
  `_filas_verificaciones`, `fila_resumen`, `_tabla_bloqueos`) y sin aritmética. La CLI
  escribe las dos en una invocación (`--html` y `--html-resumida`, `--pdf-resumida`).
  `tests/test_t12_entregable.py` mide que la resumida no publica ningún número que la
  completa no tenga (en total y por punto, sobre las tres corridas de referencia, el juego
  de T-11 y la línea base) y que las dos llevan el mismo encabezado de trazabilidad. La
  completa no cambia de contenido por esto.
- **Cerrado en la ventana (UI-2 de la cadena de interfaz, 2026-11-14):** la pestaña 4 tiene
  «Memoria resumida (HTML)» y «Memoria resumida (PDF)» en el grupo de exportación
  (`gui/app.py::BOTONES_DE_EXPORTACION`), con el contrato de los demás: nacen apagados con
  el motivo compartido sin corrida, se apagan con el motivo de cada gesto que retira el
  informe y se encienden al correr; leen de `Informe.contexto` (EXT-4). El HTML se escribe
  en el proceso de la ventana con `M11.exportar_html_resumida` (la que `cli` reexporta) y
  el PDF sale por el proceso hijo de EXT-8 (`cli.py --sesion … --pdf-resumida …`, armado por
  `gui/exportacion_pdf.py::comando_exportar_pdf` con la vista como parámetro) con la sesión
  de la corrida de UI-1, «Cancelar PDF», el rótulo con su progreso y el manejo de errores
  del completo. `tests/test_ui2_pestana4.py` lo mide con dobles y con la ventana de verdad
  (las dos memorias en HTML llevan el mismo encabezado; el JSON del hijo es el de la
  ventana salvo la hora, porque el hijo recalcula). Las correcciones de su revisión, en la
  ficha UI2-03. UI-4 las exportó en su recorrido de extremo a extremo (ficha UI4-01).
- **Abierto:** nada: la remisión de la resumida a su completa se cerró en UI-5 (ficha
  UI2-01).
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M11_reporte/resumida.py::memoria_resumida_html`

## T12-05 · Licencia «todos los derechos reservados», `pyproject.toml` sin empaquetado y el README de usuario

- **Cerrado (T-12, `INF-5.2.7`; decisiones del dueño del 2026-11-13):** `LICENSE` reserva
  todos los derechos, dice que los PDF de normas no son del autor ni se licencian y que
  abrir el código bajo MIT es una decisión posterior a la sustentación; el autor es el
  usuario de GitHub del repositorio, con la indicación de dónde cambiarlo por el nombre de
  la carátula, y sin correo. `pyproject.toml` declara metadatos, las dependencias con las
  MISMAS versiones que `requirements*.txt` (obligatorias numpy y scipy; opcionales `gui`,
  `pdf`, `test` y `proceso`) y la configuración de pytest; no lleva `[build-system]`
  porque el programa se usa desde el clon (la memoria lee `docs/` y `src/plantillas/` por
  su posición). El README de la raíz es de usuario —instalación, entradas, corrida,
  salidas, alcance declarado y trabajo posterior— y el de proceso es `proceso/README.md`.
- **Por qué así:** el dueño decidió no licenciar todavía; un `pyproject.toml` con
  `[build-system]` prometería un `pip install .` que no produce un programa que funcione,
  y el README anterior mezclaba la instalación con notas de desarrollo (está en el
  historial, `git show f77c5d4:README.md`).
- **Qué haría falta:** el nombre de la carátula en `LICENSE` y `pyproject.toml`, y la
  versión de `pyproject.toml` (hoy `Andy-rba30` y `0.1.0`, marcadores): **pendiente del
  dueño** antes de la sustentación (decisión del 2026-11-13).
- **Dónde vive:** `tests/test_t12_entregable.py::test_pyproject_fija_las_mismas_versiones_que_requirements`

## T12-06 · La aceptación de T-12 no se escribió en rojo primero

- **Cerrado (T-12):** `tests/test_t12_entregable.py` se escribió con el código; el rojo se
  midió corriendo el archivo final contra el árbol base (`f77c5d4`, exportado con `git
  archive`), y el número está en el informe de la FASE A. Los tests reescritos al contrato
  nuevo lo dicen en su docstring (`test_t0_gobernanza`, `test_ext6_registro_normativo`,
  `test_sin_literales`, `test_decisiones_diferidas`).
- **Por qué:** la mayor parte de T-12 es mover y rotular, y su rojo es de existencia (lo
  que no estaba no se puede probar antes de crearlo); se midió y se dice, como en T-10 y
  T-11.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t12_entregable.py::test_la_resumida_no_publica_ningun_numero_que_la_completa_no_tenga`

## T12-07 · Las correcciones de la auditoría de T-12: el entregable se sostiene solo y la resumida no pierde lo que la completa dice a propósito

- **Cerrado (cierre de T-12; auditoría AJUSTADO: 1 ALTA, 4 MEDIA, 3 BAJA):** (H1, ALTA) la
  suite del entregable pasa sobre una EXPORTACIÓN (`git archive HEAD`, sin `proceso/` ni
  `.git`): la exención de `proceso` no caduca en una exportación
  (`test_sin_literales.AUSENTES_EN_UNA_EXPORTACION`), el arnés de mutación se salta sin
  `.git`, y se fija con un censo de lo que invoca git y con la corrida de esos tests sobre
  una exportación emulada; el par medido sobre la exportación real está en la bitácora y en
  el README. (H2) la resumida marca en texto la adopción sobre vacío verificado
  (`M11.MARCA_VACIO_VERIFICADO`). (H3) lleva el corredor, su advertencia y los [S] con su
  origen (`M11.datos_sitio_resumidos`, que comparte `_cabecera_de_corredor` con la
  completa). (H4) la bitácora se puede actualizar (el test exige que su texto histórico
  siga, en orden, con las cifras libres) y `proceso.verificar_sesion` corre
  `proceso/tests`. (H5) dos documentos con prompts y modelos de IA, a `proceso/`
  (ficha T12-02). (H6) la fila «h_o fuera de rango» es del formateador común
  (`M11._filas_h_o`). (H7) identidad de filas entre las vistas y un solo formateador del
  estado (`M11.estado_del_expediente`). (H8) textos que habían quedado falsos, y la
  resumida nombra la completa que de verdad se escribió.
- **Por qué:** sin H1, quien siguiera el README sobre la descarga ZIP veía la suite roja;
  sin H2/H3/H6 la vista que se imprime callaba lo que la completa dice a propósito.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/test_t12_entregable.py::test_la_suite_del_entregable_pasa_sobre_una_exportacion`


# Parte LVI — Lo que UI-1 de la cadena de interfaz dejó escrito: la hidrología en la ventana y la sesión de formato 4

UI-1 (2026-11-14, sobre `bcd2d1a`) lleva a la ventana las dos entradas de la Fase 1-bis
(ficha T1-04, en parte) y no cambia ningún cálculo: la línea base de la Familia C no se
mueve, porque sin hidrología la memoria y el JSON no ganan ni un byte.

## UI1-01 · Cómo entra la hidrología a la ventana: cinco decisiones de UI-1 y una premisa refutada

- **Cerrado (UI-1):** (1) Cambiar el CSV de cuencas o el de la estación invalida el
  informe vigente (`gui/app.py::MOTIVO_HIDROLOGIA_CAMBIADA`), como pedía el prompt. Su
  premisa —«el mismo gesto que cambiar el CSV»— no se cumple: desde EXT-4 y EXT-8
  cambiar el CSV NO invalida (el informe es de su corrida y el hijo del PDF usa las
  entradas fotografiadas al correr), y UI-1 no lo tocó. (2) Una sesión v3 sube a v4 SIN
  aviso: las dos rutas vacías son lo que v3 significaba (`sesion._migrar_v3_a_v4`); el
  fixture `tests/fixtures/sesion_v3/` es una sesión de verdad guardada con el código de
  partida. (3) Una convención de rutas para las dos puertas: el texto del campo sin
  espacios en los extremos (`sesion.ruta_de_campo`; la CLI hacía `Path` crudo). (4) La
  ayuda de los dos CSV sale de src/ y está a medias: cabecera, obligatoriedad, claves
  admitidas (del cargador, por el servicio) y remisiones; concepto, unidad y origen, en
  `docs/contrato_entradas.md` §2-bis. (5) El comparador mira la hidrología sin sus rutas
  (`comparador.RUTAS_DE_LA_HIDROLOGIA`), y el anticipo dice lo mismo que `--prevuelo`
  (`servicio.mensaje_de_carga_fallida`, `anticipo.AVISO_HIDROLOGIA_NO_CALCULADA`).
- **Cerrado (UI-5, decisión del dueño del 2026-11-15):** cambiar el CSV de puntos
  invalida el informe, un gesto con la hidrología (`MOTIVO_CSV_CAMBIADO`). La premisa que
  (1) refutaba se cumple desde UI-5 por decisión: hasta entonces el campo sólo releía las
  familias (ningún test lo fijaba; lo decía esta ficha). Qué cuenta como «cambiar» —toda
  escritura, también la misma ruta— y por qué abrir una sesión o un proyecto nuevo no pisan
  su motivo, en el docstring de `_al_cambiar_el_csv`.
- **Abierto:** el hijo del PDF relee los archivos de la hidrología como relee el CSV
  (ficha EXT-8-02), y los demás campos de la pestaña 1 no invalidan (ficha UI5-01). Las
  dos frases de `CLAUDE.md` que UI-1 dejó desfasadas las corrigió el dueño (ficha UI4-02).
  Y un resto anterior a UI-1: si falla el JSON de datos externos, el anticipo dice «El
  pre-vuelo no pudo armar los datos externos» y la CLI «No se pudo leer la entrada».
- **Qué haría falta:** para la relectura, lo que se decida en EXT-8-02; el resto del
  JSON, `servicio.mensaje_de_carga_fallida` también en ese brazo del anticipo.
- **Dónde vive:** `gui/app.py::_al_cambiar_el_csv`

## UI1-02 · Tres conductores de ventana real se habían quedado atrás de T-3, y el editor de la pestaña 2 sólo nombra filas de la primera tabla

- **Cerrado (UI-1):** la suite de partida (`bcd2d1a`, con Tk) daba tres rojos de ventana
  real anteriores a UI-1, que nadie había corrido con Tk desde T-3. No eran defectos de
  la ventana sino de los conductores: T-3 dio valor de archivo a los siete criterios del
  cajón y pasó `n_manning_cajon` a la fila de la Tabla B.1 del HDS-5. Se corrigieron sin
  tocar cálculo ni criterio: `tests/apoyo/gui_corrida_perfil.py` teclea la fila de
  archivo (`concrete_boxes`, como hizo T-3 con su test, H1) y deja los siete sin valor
  mientras corre (`tests/apoyo/criterios.py::sin_valor`), para que el aserto de C8
  —el pendiente de la Familia C se ve y se declara desde la ventana— conserve su
  objeto; `tests/apoyo/gui_eb_real.py` vacía con «Quitar par» la serie que el editor
  monta con el valor de archivo antes de teclear la suya.
- **Abierto:** el editor tipado de la pestaña 2 deriva sus filas de la PRIMERA tabla de un
  criterio de varias (`src/editores.py::_opciones_de_tabla`): `concreto_afinado`, la
  alternativa barrible de la Tabla N 09 que la ficha de `n_manning_cajon` nombra, sólo
  entra con nota, como adopción, y no con la procedencia de su fila (el barrido de T-11
  la pasa con nota por eso).
- **Qué haría falta:** que `esquema_de` ofrezca las filas de todas las tablas de la ficha y
  que `declarar` declare cada una con su `tabla_id`. Es semántica de declaración, fuera
  del alcance de UI-1.
- **Dónde vive:** `src/editores.py::_opciones_de_tabla`


# Parte LVII — Lo que UI-2 de la cadena de interfaz dejó escrito: la pestaña 4 con la memoria resumida y el cabezal del proyecto

UI-2 (2026-11-14, sobre `4066a24`) lleva a la pestaña 4 la memoria resumida de T-12 (ficha
T12-04) y el bloque del cabezal del proyecto que la CLI imprime y la ventana no pintaba
(hueco 3 del §0 de `proceso/planes_mejora/10_CADENA_PROMPTS_INTERFAZ.md`). No cambia ningún
cálculo, ni la plantilla ni el texto de la memoria: en `src/` sólo entra la plomería del
progreso de la resumida (ficha UI2-03), y la línea base no se mueve.

## UI2-01 · La memoria resumida en la ventana: cinco decisiones de UI-2

- **Cerrado (UI-2):** (1) El grupo de exportación es UNA tupla (`BOTONES_DE_EXPORTACION`):
  la leen `_apagar_exportadores` y el encendido de `ejecutar_pipeline`, que la escribían a
  mano, y los demás sitios que el grep encontró —los dobles de `test_ext4_contexto_corrida`
  y `test_ui1_hidrologia_ventana`, los métodos de SIS-E-03 en `test_gui_contrato` y los
  conductores `gui_contexto_real`, `gui_ext10_real` y `gui_ui1_hidrologia_real`, que así
  miden también «Comparar»—. (2) Los dos botones van en una SEGUNDA fila del panel
  «Exportacion» (abierto (c)). (3) El PDF resumido no pregunta por el tamaño:
  `UMBRAL_PUNTOS_PDF` se midió sobre la completa (en `expediente_cabezal`, 4 puntos: 5.1 s y
  163 KB la resumida, 45.1 s y 1783 KB la completa). (4) Un PDF a la vez: las dos vistas
  comparten el hijo, «Cancelar PDF» y el rótulo (`BOTONES_PDF`), que nombra la vista
  (`exportacion_pdf.ROTULO_DE_LA_VISTA`). (5) La ventana escribe la resumida sin
  `nombre_completa`: no escribe las dos en una invocación.
- **Abierto:** (a) cerrado en la revisión (UI2-03). (b) La remisión a la completa
  (`M11._remision_a_la_completa`) habla de `--html`/`--pdf` «en la MISMA invocación» y dice
  que el encabezado de trazabilidad «es el mismo en las dos»: entre la completa de la
  ventana y la resumida en PDF del hijo NO lo es (el hijo recalcula: otra hora, y las
  huellas de los archivos al exportar, EXT-8-02). Es texto de la memoria y la línea base lo
  fija. (c) cerrado en UI-4 (ficha UI4-01): a 1100 px la primera fila no cabía —«Exportar
  cuadro resumen (CSV)» salía cortado y «Comparar con otro JSON...» fuera de la vista—, y
  pasar sólo «Comparar» a la segunda no bastaba (medido: el CSV seguía cortado); hoy son
  tres filas, la memoria completa con el JSON, la resumida y los datos (CSV y comparar).
- **Cerrado (UI-5, decisión del dueño del 2026-11-15):** (b) la remisión es cierta en la
  CLI con las dos vistas, en la resumida HTML de la ventana y en la PDF del hijo: nombra la
  completa sólo si la escribió la misma invocación, y dice lo que el encabezado prueba de
  las dos vistas, y sólo eso (`M11.REMISION_COMO_COMPROBARLO`, corregida en la revisión:
  ficha UI5-02). La línea base se regeneró: esa frase y la huella de
  `criterios_adoptados.py` (ficha UI3-03), ningún número.
- **Qué haría falta:** nada de (b); que el hijo no recalcule sigue en EXT-8-02.
- **Dónde vive:** `gui/app.py::BOTONES_DE_EXPORTACION`

## UI2-02 · El cabezal del proyecto en la pestaña 4, con el texto de la CLI

- **Cerrado (UI-2, hueco 3 de la cadena de interfaz):** el panel «Cabezal del proyecto»
  pinta `cli._lineas_cabezal(informe.cabezal)` con `comp.escribir_lineas_de_cli`: la suma de
  los cabezales por punto, la cadena sísmica con la condición de cada eslabón, los
  recubrimientos, las cuantías, las notas y los bloqueos de la Fase 9 del proyecto. A
  perfil, o con la Fase 9 detenida, es lo que la CLI imprime (el título y el bloqueo,
  diferido o real). Sin corrida queda vacío con `MOTIVO_SIN_CORRIDA_CABEZAL`; con un gesto
  que retira el informe, vacío con «Sin informe vigente: <motivo>», lo mismo que la barra.
  Se llena con `_llenar_resumen` y se vacía con `_vaciar_tablas_del_informe`, que desde
  UI-2 llaman también los dos brazos de fallo de `ejecutar_pipeline` (escribían la barra a
  mano): así el panel no se queda diciendo «la corrida esta en marcha» tras una corrida
  que no produjo informe.
- **Por qué así:** la ventana sólo pinta (§1.2 de la cadena). El motivo va en un rótulo
  aparte y no dentro del texto, para que el panel sea, palabra por palabra, el bloque de la
  CLI: `tests/test_ui2_pestana4.py` lo compara con el que `cli.py` imprime para las mismas
  entradas de la corrida de referencia `expediente_cabezal`, con la ventana de verdad.
- **Qué haría falta:** nada.
- **Dónde vive:** `gui/app.py::_pintar_cabezal_del_proyecto`

## UI2-03 · Las correcciones de la revisión independiente de UI-2: el hijo del PDF y lo que la ventana promete de él

- **Cerrado (revisión de UI-2 sobre `6392c34`, cinco hallazgos confirmados):** (1) La ayuda
  del PDF resumido prometía «el mismo encabezado de trazabilidad» que la completa, y el hijo
  vuelve a correr la obra; las dos ayudas de PDF lo dicen con un texto
  (`gui/exportacion_pdf.py::AVISO_EL_HIJO_RECALCULA`) y la del HTML resumido sólo promete el
  encabezado entre los dos HTML (`gui/app.py::AYUDA_HTML_RESUMIDA`). (2) El éxito del hijo
  era «el destino existe y no está vacío»: un hijo con código 2 daba por bueno un PDF
  anterior, y cancelar lo borraba. El hijo escribe ahora en su directorio de trabajo (que
  `iniciar` vacía de lo de un hijo anterior) y el PDF se entrega al destino (`.parcial` y
  `os.replace`) sólo con un código de `CODIGOS_DE_SALIDA_CON_MEMORIA` y un PDF suyo ENTERO
  (`%PDF` y el trailer `%%EOF` en sus últimos `COLA_DEL_PDF_BYTES`: weasyprint escribe por
  partes, y un fallo a mitad salía con 1 y un PDF cortado, reproducido con `ulimit -f`);
  fallar o cancelar no tocan el destino. Vale para los dos PDF. (3) Correr con un PDF en marcha encendía los dos botones de PDF
  (`_encender_exportadores`). (4) Un test lleva la resumida de la ventana sobre
  `hidrologia_calculada` y mira la sesión del hijo. (5) `M11.exportar_pdf_resumida` recibe
  `progreso`, que `cli.main` pasa con `--pdf-resumida` (plomería autorizada por la
  orquestadora). Cada corrección mata su mutante en `tests/test_ui2_pestana4.py`.
- **Por qué (0, 1) y no sólo 0:** `cli.main` sale con 1 cuando corre y el expediente NO
  cierra, y escribe la memoria igual; exigir 0 daba por fallido el PDF de todo expediente
  que aún no cierra (las dos corridas de referencia lo son). Un 1 de Python (excepción sin
  atrapar) no se confunde porque el éxito exige además el PDF de trabajo.
- **Cerrado (UI-5, decisión del dueño del 2026-11-15):** el PDF se escribe de forma
  atómica (`src/escritura_atomica.escribir_atomico`, ficha UI5-02), en las dos vistas, la
  CLI directa y el hijo. La
  defensa de este módulo queda como SEGUNDA LÍNEA (comentario de
  `CODIGOS_DE_SALIDA_CON_MEMORIA`), y el test del hijo bajo `ulimit -f` de UI-2 se cambió
  declarando la causa: ya no queda PDF de trabajo cortado.
- **Qué haría falta:** nada en la ventana. Si el hijo cae a la vía del navegador, el
  HTML se retira con el directorio de trabajo y la exportación sale FALLIDA, sin archivo.
  La CLI que falla al escribir, en la ficha UI5-01.
- **Dónde vive:** `gui/exportacion_pdf.py::CODIGOS_DE_SALIDA_CON_MEMORIA`


# Parte LVIII — Lo que UI-3 de la cadena de interfaz dejó escrito: el botón «Barrido…» de la pestaña 2

UI-3 (2026-11-14, escrita sobre `4066a24` en paralelo con UI-2 y rebasada sobre
`4067b9a`, main con UI-1 y UI-2) lleva a la ventana el barrido de sensibilidad de PF-3
(ficha PF-3-01, cerrada) y no cambia ningún cálculo, criterio ni texto de memoria: la
línea base no se mueve y la CLI imprime lo mismo salvo con la entrada atípica de UI3-03.

## UI3-01 · Dónde corre el barrido de la ventana: en un proceso hijo, la CLI con la sesión de la ventana

- **Cerrado (UI-3):** (1) En un PROCESO HIJO y no en un hilo
  (`gui/proceso_barrido.py`): `barrer` declara cada valor en el estado de módulo de
  `criterios_adoptados` y `declaracion` y lo repone al salir, y en el proceso de la
  ventana ese intervalo sería otro estado para la pestaña 2, un «Aplicar» o una
  exportación. El hijo es `cli.py --sesion … --barrido … --json <temporal>`, sondeado con
  `after`, cancelable; si falla o no arranca, termina con su motivo. (2) Su sesión es la
  de «Guardar sesión» leída al pulsar «Correr» —con la hidrología de UI-1 y las
  procedencias—, sin corridas y con los datos de sitio que EJECUTAR declararía
  (`sesion_para_el_barrido`): el barrido describe el estado de la ventana y no el informe
  vigente, que no toca ni invalida. (3) La única huella en el proceso de la ventana es la
  puerta (`barrido.verificar_valores`), que declara y repone en el mismo gesto; medido en
  la ventana real, el estado declarado, los [S], el informe (mismo objeto y volcado), los
  exportadores y la pestaña 2 quedan iguales. El hijo vuelve a cerrarla. (4) Los valores
  viajan por su `repr`, comprobado con `cli.valores_del_barrido` (`texto_del_barrido`), y
  la tabla se lee con los valores pedidos porque el JSON no tiene tuplas. (5) Una fila y
  una nota para todos, como la CLI: en el editor, elegir una fila sólo propone su valor.
- **Abierto:** la tabla de la ventana y la de la CLI para la misma sesión difieren sólo en
  el segundo de cada declaración (`declarado el …`), que es de cada corrida. El panel de
  declaración de la pestaña 2 no tiene scroll: en la geometría por defecto, con el editor
  de un criterio de tabla, la fila de «Quitar» y «Barrido…» queda fuera de la vista, como
  «Aplicar» antes de UI-3 (sigue así tras UI-4: las capturas del README se toman a 1280 ×
  1000). Lo que UI-4 corrigió de esta ventana: la tabla se pintaba en un panel de alto cero
  y no se veía sin arrastrar el divisor (ficha UI4-01); los tests de UI-3 leían el texto
  del widget, no la pantalla.
- **Qué haría falta:** un scroll en el panel de declaración de la pestaña 2 (rediseño,
  fuera de UI-3).
- **Dónde vive:** `gui/proceso_barrido.py::ProcesoBarrido`

## UI3-02 · Lo que la revisión independiente de UI-3 encontró: una sesión que no reponía claves enteras, y la regla del botón fuera de src/

- **Cerrado (revisión de UI-3):** (H2, causa anterior a UI-3) la sesión JSON escribe las
  claves enteras como texto: `espesor_pared_conducto` pisado —aun con el valor del
  archivo— volvía de «Guardar/Cargar», del hijo del PDF y del hijo del barrido con
  `'900'`, la guardia lo aceptaba y tres puntos salían «no dimensionado» sin aviso. Se
  corrige en la raíz: `restaurar_sesion` rearma cada valor con la forma de su ficha antes
  de la guardia (`declaracion.valor_desde_json`); las sesiones v3 y v4 abren igual. (H1)
  la tabla del barrido de ese criterio terminaba FALLIDO (`barrido._texto_json`). (H3) un
  barrido en marcha al cerrar la ventana principal quedaba huérfano con su carpeta: el
  `<Destroy>` del Toplevel lo termina y la retira (`ProcesoBarrido.terminar_y_limpiar`).
  (H4) un segundo «Correr» que no arranca conserva el barrido anterior y lo dice. (H5) la
  regla del botón vive en `barrido.motivo_para_no_barrer`. (H6) el hijo registra el origen
  de los [S] que la ventana registra (`proceso_barrido.ORIGEN_SESION_ABIERTA`). (H7) los
  tests prueban que la corrida del valor vigente ES la de la ventana.
- **Abierto:** (1) la ventana no ofrece barrer los 26 criterios sin ventana, y la puerta
  de la CLI (`verificar_valores`) sí deja barrer 16 de ellos con su valor de archivo
  (censados en `tests/test_ui3_barrido_ventana.py`); UI-3 no cambia lo que la CLI acepta.
  (2) Las tuplas vuelven de la sesión como listas: la guardia y los consumidores aceptan
  las dos y el volcado es el mismo, y normalizarlas cambiaría el estado vivo que el barrido
  repone de una declaración `--declarar` con lista. (3) cerrado en UI-4 (ficha UI4-01): el
  hijo del PDF tenía el patrón de H3 —cerrar la ventana principal con un PDF en marcha lo
  dejaba escribiendo para nadie y su carpeta en el temporal—, y hoy el `<Destroy>` de la
  raíz lo termina y la retira (`ExpedienteApp._al_destruirse`).
- **Qué haría falta:** para (1), la decisión del dueño —igualar la CLI a la ventana, o
  ofrecer en la ventana lo que la CLI acepta—.
- **Dónde vive:** `src/declaracion.py::valor_desde_json`

## UI3-03 · Una clave entera escrita como texto se rechaza en TODAS las puertas que declaran; sólo la frontera del JSON la lee como entero

- **Cerrado (verificación de la revisión de UI-3, N1):** la corrección de H2 rearmaba las
  claves enteras sólo al reponer una sesión, y las puertas seguían aceptando
  `espesor_pared_conducto` con `'900'` (copiado de un JSON): EJECUTAR dejaba tres puntos
  «no dimensionado», la primera corrida del barrido con el mismo valor los dimensionaba y,
  al cerrar el barrido, el estado de la ventana había cambiado. Ahora la forma de las
  claves se exige en la puerta (`declaracion.verificar_claves_de_la_ficha`): donde las
  claves del valor del archivo son enteras, otra clave es `ValueError` con su motivo
  («Escriba 900 sin comillas»), el MISMO por la pestaña 2 y sus editores, la ventana
  emergente, `--declarar`, el barrido y sus declaraciones de base. `restaurar_sesion` es la
  frontera del JSON —allí `900` y `'900'` son la misma clave—: lee el entero escrito
  (`valor_desde_json`) y rechaza lo demás con el mismo motivo. El estado vivo ya no puede
  llevar una clave de texto, y el barrido lo repone sin cambiarlo.
- **Abierto:** la salida de la CLI con esa entrada atípica CAMBIA respecto de `4066a24`:
  `--declarar espesor_pared_conducto={…'900'…}` corría sin encontrar la fila (puntos «no
  dimensionado», medido por la revisión) y hoy sale con 2 y el motivo, antes de correr
  nada; con `--barrido` sale igual. Ninguna entrada bien escrita cambia de resultado. La guardia de
  `criterios_adoptados.verificar_declaracion` sigue sin mirar las claves: es un archivo
  protegido, y la puerta se puso en las capas que lo llaman.
- **Cerrado (UI-5, decisión del dueño del 2026-11-15):** la regla vive en la guardia del
  archivo (`criterios_adoptados._verificar_claves_de_la_ficha`, que `_verificar_criterio`
  llama: archivo, declaración en caliente y escritura permanente), con el mismo mensaje.
  `declaracion.verificar_claves_de_la_ficha` se retiró con sus siete llamadas: las capas de
  arriba llaman a la guardia; la frontera del JSON (`valor_desde_json`) se queda, con la
  definición de la guardia. El valor de archivo de los 141, sus filas de tabla y los
  extremos de su ventana pasan por todos los caminos, `restaurar_sesion` incluido
  (`tests/test_ui5_decisiones.py`). Ningún valor ni nivel cambia; la huella del archivo sí.
  La frase de EXT-5 de `CLAUDE.md` sigue siendo cierta y no se tocó.
- **Qué haría falta:** nada; lo que deja la plantilla de archivo, en la ficha UI5-01.
- **Dónde vive:** `src/criterios_adoptados.py::_verificar_claves_de_la_ficha`


# Parte LIX — Lo que UI-4 de la cadena de interfaz dejó escrito: la ventana verificada de extremo a extremo

UI-4 (2026-11-14, sobre `3117b2c`, main con UI-1, UI-2 y UI-3) cierra la cadena de interfaz
sin añadir funciones: recorre la ventana de verdad de extremo a extremo, toma sus capturas,
escribe la sección de la ventana del README y corrige lo que el recorrido encontró y lo que
UI-2 y UI-3 dejaron escrito para UI-4. Ningún cálculo, criterio, constante ni texto de
memoria cambia, y la línea base no se mueve: el recorrido la reproduce por la ventana.

## UI4-01 · El recorrido de extremo a extremo, y las tres cosas que encontró o heredó

- **Cerrado (UI-4):** `tests/apoyo/gui_ui4_recorrido_real.py` recorre la ventana de verdad
  bajo xvfb, por sus botones (los pasos, en su docstring), y
  `tests/test_ui4_recorrido_ventana.py` lo juzga: el CSV de ejemplo reproduce la línea
  base a perfil y a expediente; las tres corridas de referencia, con las entradas por
  «Examinar...» y las declaraciones tecleadas en la pestaña 2, dan el MISMO JSON que
  `cli.py`; el detalle de la pestaña 3 (caudal calculado, Fases 6, 8 y 9) y el panel
  «Cabezal del proyecto» son las líneas de la CLI; los seis exportadores escriben (los dos
  PDF por el hijo, con la hidrología); guardar, «Nuevo proyecto», cargar y ejecutar dan el
  mismo JSON; la sesión v3 REPRODUCE su corrida y se reescribe en el formato 4; el barrido
  pinta las líneas de la CLI y deja la ventana como estaba. Lo que encontró o heredó: (1)
  la tabla del barrido nacía en un panel de alto cero: `componentes.repartir_al_mostrar`
  colocaba el divisor de un `PanedWindow` VERTICAL con el ANCHO (609 px en 526 de alto);
  los tests de UI-3 leían el widget y no la pantalla, y lo mostró la captura. Hoy reparte
  a lo largo de su orientación. (2) Cerrar la ventana con un PDF en marcha dejaba el hijo y
  su carpeta (ficha UI3-02, abierto (3)): el `<Destroy>` de la raíz los retira
  (`ProcesoPdf.terminar_y_limpiar`; el hijo que ya terminó, ficha UI4-03). (3) A 1100 px la
  fila de exportación no cabía (ficha UI2-01, abierto (c)): son tres filas.
- **Por qué así:** el prompt pide no añadir funciones, y las tres son correcciones. Sus
  tests, y los del README y las capturas, se escribieron en rojo (13 `xfailed`, cada uno
  por su motivo) y se liberaron al corregir; los demás del recorrido verifican lo que UI-1
  a UI-3 ya hacían y no tenían rojo que medir (28 pasaron desde el principio).
- **Abierto:** el recorrido no mide un gestor de ventanas real ni otra escala de pantalla
  (el ancho de los botones depende de la tipografía), y al ancho mínimo de la ventana (900
  px) «Exportar memoria (PDF)» sale cortado 14 px.
- **Qué haría falta:** una medida con la pantalla del autor; para el ancho mínimo, otra
  fila o un `minsize` mayor, decisión de diseño.
- **Dónde vive:** `tests/apoyo/gui_ui4_recorrido_real.py::main`

## UI4-02 · Las capturas y el README salen del recorrido; lo que de `CLAUDE.md` queda para el dueño

- **Cerrado (UI-4):** las cinco capturas de `docs/capturas_interfaz/` (las cuatro pestañas y
  la ventana del barrido) las toma el mismo recorrido con `--capturas`, con ImageMagick
  (`import -window root` sobre la región de la ventana) a `GEOMETRIA_DE_LAS_CAPTURAS` (1280
  × 1000, que cabe en la pantalla por defecto de `xvfb-run`): son DATOS DE PRUEBA —la
  corrida `hidrologia_calculada`; la de la guía en la pestaña 2 y en el barrido—, con las
  rutas relativas a la raíz. La suite comprueba que el README las nombra todas en su
  sección «La ventana» (§4), que existen y son PNG de esa geometría y que el recorrido las
  regenera; que el README dice dónde está cada cosa —la hidrología en la pestaña 1, el
  barrido en la 2, el cabezal del proyecto y la memoria resumida en la 4— con el rótulo que
  la ventana le pone (comprobado contra las cadenas de `gui/app.py`), y qué hace sólo la
  CLI (las dos memorias en una invocación y `--plantilla`). `docs/guia_perfil.md` no cambia:
  ninguna instrucción suya dejó de ser cierta.
- **Por qué así:** una captura hecha a mano envejece sin aviso; tomada por el recorrido que
  la suite ejecuta se regenera con un comando y su forma queda fijada. No se comparan sus
  bytes: la hora de la corrida está en la barra de estado.
- **Cerrado después (dueño, 2026-11-15):** las TRES frases de `CLAUDE.md` que la cadena UI
  dejó desfasadas, sin tocar durante la cadena por decisión de la orquestadora, quedaron
  corregidas por decisión del dueño: «`FORMATO_SESION = 3`» (sección «Taxonomía de
  etiquetas»; es 4 desde UI-1), «La GUI y la sesión todavía no conocen las dos entradas»
  (sección «Arquitectura», la hidrología) y «El botón «Barrido…» de la pestaña 2 se difirió
  con símbolo» (sección «GUI», PF-3). UI-4 no añadió ninguna: `CLAUDE.md` no nombra ni el
  reparto del divisor, ni el cierre de la ventana, ni las filas de exportación.
- **Qué haría falta:** nada de `CLAUDE.md`.
- **Dónde vive:** `tests/apoyo/gui_ui4_recorrido_real.py::GEOMETRIA_DE_LAS_CAPTURAS`

## UI4-03 · Lo que la revisión independiente de UI-4 encontró: el hijo que ya terminó al cerrar y un ciclo de sesión que no distinguía «repuesto» de «por defecto»

- **Cerrado (revisión de UI-4, sin hallazgos altos ni medios; dos bajos confirmados):** (H1)
  el contrato de `ProcesoPdf.terminar_y_limpiar` prometía «el destino no se toca», y si el
  hijo ya había salido con su PDF sin que la ventana lo sondeara (cada
  `CADENCIA_SONDEO_PDF_MS`) el cierre lo entregaba: estado TERMINADO. Se decide ENTREGAR
  —el usuario lo pidió y ya está escrito— y el docstring lo dice con los dos casos, que
  separa el `poll()` del cierre: en marcha, CANCELADO sin tocar el destino; ya salido, lo que
  habría hecho el sondeo (un PDF entero se entrega; un fallo no toca el destino). (H2) el
  ciclo guardar / «Nuevo proyecto» / cargar del recorrido se hacía con una sesión de
  expediente y sin banderas, que es lo que «Nuevo proyecto» deja: quitar de
  `cargar_sesion` la línea que repone el alcance sobrevivía a toda la suite. Hoy el ciclo
  corre a perfil y con la luz tecleada, compara el alcance y las banderas guardados con los
  repuestos y el JSON con el de la corrida hecha antes de guardar. Y dos menores: el test
  del grupo de exportación nombra los siete botones en vez de leerlos de la tupla que
  vigila, y los diálogos de error se cuentan después del cierre.
- **Por qué así:** la conducta de H1 es la que el código ya tenía, y por eso su test no
  tuvo rojo; se midió por mutación (cancelar siempre: caen los dos casos del test). H2 se
  midió con el mutante del revisor y con el de las banderas: sin la línea del alcance, o
  sin el bucle que repone las banderas, cae el test del ciclo.
- **Qué haría falta:** nada.
- **Dónde vive:** `tests/apoyo/gui_ui4_recorrido_real.py::ALCANCE_DEL_CICLO`


# Parte LX — Lo que UI-5 de la cadena de interfaz dejó escrito: cuatro decisiones del dueño sobre lo que la cadena dejó abierto

UI-5 (2026-11-15, sobre `2d37c2c`: main con UI-1 a UI-4 y la corrección de tres frases de
`CLAUDE.md`) aplica cuatro decisiones del dueño del 2026-11-15 y cierra los puntos de las
fichas UI1-01, UI2-01 (b), UI2-03 y UI3-03 que esperaban por ellas. Ningún cálculo cambia:
la línea base se regeneró y su diff es la frase de la remisión en la resumida y la huella de
`criterios_adoptados.py`, cuya guardia se tocó (ficha UI3-03); ningún número.

## UI5-01 · Lo que las cuatro decisiones dejan abierto

- **Cerrado (UI-5):** (1) el CSV de puntos invalida el informe, un gesto con la hidrología
  (ficha UI1-01); (2) la remisión de la resumida a su completa es cierta en la CLI, en la
  ventana y en el hijo (ficha UI2-01); (3) el PDF se escribe de forma atómica (ficha
  UI2-03); (4) la forma de las claves la exige la guardia del archivo (ficha UI3-03). Cada
  una con sus tests en `tests/test_ui5_decisiones.py`, escritos en rojo.
- **Abierto:** (a) los demás campos de la pestaña 1 —el JSON de datos externos, el de
  datos de sitio, las banderas y el alcance— siguen sin invalidar el informe, como decidió
  EXT-8 (el hijo usa las entradas fotografiadas al correr): «un solo gesto» es el del CSV y
  la hidrología, y la ventana real lo fija como frontera. (b) El hijo del PDF sigue
  recalculando y releyendo los archivos (fichas EXT-8-02 y EXT-10-04): la resumida dice lo
  que el encabezado prueba, y un encabezado igual no prueba la misma corrida. (c) Si la
  escritura del PDF falla, la CLI sale con la traza de Python y el código 1, el mismo que
  «corre y no cierra»; el destino queda intacto y el hijo lo distingue porque no deja PDF
  de trabajo, pero quien usa la CLI lee una traza. (d) `exportar_html` y
  `exportar_html_resumida` (EXT-8, T-12) siguen con su temporal FIJO `<destino>.parcial`,
  con los cuatro defectos que la revisión midió en el primer intento (ficha UI5-02), y
  `exportar_csv` escribe directo: fuera del permiso de UI-5 en `M11_reporte.py`.
  `sesion.escribir_json_atomico` usa un temporal único, pero su nombre lleva el del destino
  y no sigue enlaces ni conserva el modo. (e) La plantilla de la forma de las claves es el
  valor de ARCHIVO de la ficha: un criterio sin valor de archivo no tiene forma de claves
  que exigir (hoy el único de claves enteras, `espesor_pared_conducto`, lo tiene).
- **Qué haría falta:** (a) y (b), decisión del dueño sobre EXT-8-02; (c) atrapar el
  `OSError` de la escritura en `cli.main` con su mensaje y otro código; (d) que esas
  escrituras usen `src/escritura_atomica.escribir_atomico`; (e) un campo de la ficha con la
  forma de las claves, si aparece un criterio de claves enteras sin valor de archivo.
- **Dónde vive:** `src/escritura_atomica.py::escribir_atomico`

## UI5-02 · Lo que la revisión independiente de UI-5 encontró: una implicación al revés, la pestaña 2 sin repintar y un temporal de nombre fijo

- **Cerrado (revisión de UI-5, sin hallazgos altos ni medios; tres bajos confirmados):**
  (H1) la remisión daba por SUFICIENTE que el encabezado coincidiera, y dos corridas con un
  valor declarado distinto en el mismo segundo llevan el mismo encabezado y dimensionan
  distinto: hoy dice sólo la implicación que vale (`M11.REMISION_COMO_COMPROBARLO`), y la
  línea base cambia en ese párrafo y nada más. (H2, anterior a UI-5 y alcanzable con el
  gesto nuevo) la pestaña 2 con «Solo los que bloquearon esta corrida» seguía filtrando por
  el informe retirado: toda retirada la repinta sin corrida (`_vaciar_tablas_del_informe`),
  también una corrida que falla. (H3) el temporal fijo `<destino>.parcial` fallaba con un
  destino de nombre largo, pisaba un archivo del usuario con ese nombre, se compartía entre
  dos exportaciones al mismo destino y volvía archivo regular un enlace sin conservar el
  modo: la memoria en PDF y la entrega del PDF del hijo usan una función,
  `src/escritura_atomica.escribir_atomico` (temporal único, corto y oculto, junto al archivo
  enlazado; conserva el modo).
- **Por qué así:** los tres se escribieron en rojo (14 `xfailed`) y se liberaron al
  corregir; tres guardias los acompañan (el hecho que obliga a la redacción de H1 y el modo
  de un archivo nuevo, por las dos vías). Cada corrección se midió por mutación.
- **Qué haría falta:** nada; lo que queda de H3 fuera del permiso, en la ficha UI5-01 (d).
- **Dónde vive:** `gui/app.py::_vaciar_tablas_del_informe`

## UI5-03 · Lo que la verificación de la revisión de UI-5 encontró: la hoja de ruta en la remisión, el borrador de la pestaña 2, su motivo y los permisos

- **Cerrado (verificación de `22890ce`; H1 a H3 confirmados, cuatro bajos nuevos):** (N1) la
  remisión y el párrafo del encabezado de la plantilla de la resumida contaban la huella de
  la hoja de ruta como de la corrida, y se lee al exportar: hoy no cuenta
  (`M11.REMISION_COMO_COMPROBARLO`; la trazabilidad no cambia). (N2) el repintado de H2
  reseleccionaba la fila y la reselección reescribía un valor tecleado y sin aplicar: con la
  misma fila y el mismo valor efectivo el borrador se queda (`_al_seleccionar_criterio`).
  (N3) la pestaña 2 decía «todavía no se ejecutó» tras un informe retirado: dice lo que la
  barra (`texto_sin_informe`). (N4) la escritura atómica rechazaba menos y nombraba el
  temporal: un destino sin permiso de escritura se rechaza nombrándolo, un directorio que
  no admite el temporal con destino escribible se escribe directo como antes de UI-5, y todo
  error nombra el destino (`escribir_atomico`, por las dos vías). Medido además como usuario
  sin privilegios: los cuatro casos dan lo de `2d37c2c`. Y de la verificación de `ae51aa2`
  (N1 a N4 confirmados), (N5) con la firma de N2, abrir OTRA obra con el mismo valor
  efectivo dejaba el borrador de la anterior: «Cargar sesión», «Nuevo proyecto» e «Importar
  decisiones» olvidan la firma (`_restaurar_criterios`), y el borrador sigue a salvo en la
  misma obra. El cambio de texto de la plantilla de la resumida (N1) lo aceptó el dueño.
- **Por qué así:** el borrador se conserva por firma (fila y valor efectivo) porque la
  reselección es un evento encolado de Tk que llega después del repintado; la escritura
  directa en un directorio sin permiso es la de siempre, y negarse a escribir lo que el
  usuario puede escribir era peor. Dieciocho tests en rojo (`--runxfail`, cada uno por su
  motivo; cuatro de N5) y una guardia; cada corrección, comprobada por mutación.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/escritura_atomica.py::_nombrando_el_destino`



## VE1-01 · La validación externa confirmó tres defectos: la progresión declarada se recorre tal cual (D1), V7 no lee el nivel freático (D2) y la hoja de ruta sigue mal en dos textos (D3)

- **Cerrado (VE-1):** (D1) `M2.siguiente_diametro` redondeaba el escalón a dos decimales:
  con la serie de 6 in que la ficha de `diametros_normalizados` llama «la serie real»
  (0.9144 + 0.1524) evaluaba 1.07 m, que nadie declaró, y rechazaba el tercer escalón
  culpando al dato `D`. Hoy la recorre tal cual, y la progresión de archivo da los mismos
  trece escalones: línea base sin diff. (D2) V7 no lee `NF_profundidad_m`, y el contrato
  y el concepto de la columna decían que sí; hoy nombran a la Fase 9 y a la Fase 8. De la
  revisión independiente, con el permiso que la orquestadora amplió bajo la
  autorización del dueño de corregir los defectos de la validación: (H1) el rótulo dice
  el diámetro declarado, «Ø 1.0668 m», y «Ø 0.90 m» como siempre
  (`modelos.texto_de_dimension`); (H2) la puerta rechaza con `ValueError` un `inicio` o un
  `paso` ausente, de texto o booleano, un campo de más y un paso ≤ 0, que tumbaban la
  corrida fuera de `ErrorProyecto` o recorrían otra serie
  (`criterios_adoptados._verificar_campos_de_la_progresion`); (H3) la discrepancia de la
  doble n está declarada en `M3_hidraulica` y en `M2_material`.
- **Cerrado (D3, el dueño corrigió la hoja de ruta, 2026-11-18):** (1) su §1.2, nota
  `INF-5.1.11`, decía de la columna «la lee V7», contra su fila V7 («Tubería vacía, NF en
  su cota más alta») y el Manual de Puentes núm. 2.4.3.8.2, pág. 113 («debajo del nivel
  de agua de diseño»); (2) su §4.1 rotulaba «Regla [N]» la doble n sin numeral: el Manual
  de Hidrología, núm. 4.1.1.3.6, pág. impresa 74, sólo dice
  «n : Coeficiente de Manning (Ver Tabla Nº 09)», y la Tabla Nº 09 (pág. impresa 75) da
  MÍNIMO, NORMAL y MÁXIMO sin regla de columna. Las dos llevan su nota «Corregido
  (`VE1-01` D3…)»; se retiraron las declaraciones del punto de uso y el centinela.
- **Abierto (fuera de D3):** las magnitudes `D` de los pasos de la memoria siguen con dos
  decimales, fuera del permiso.
- **Por qué así:** D1 en el consumidor porque la ficha y la puerta aceptan la serie (la
  otra vía es VE1-02 (g)); quitar el redondeo a secas dejaba 1.7999999999999998 en el
  JSON. D2 y D3 en la documentación: el código lo sostienen la fila V7 y el Manual de
  Puentes. Tests en rojo, guardias y un centinela que caía cuando el dueño corrigiera la
  hoja de ruta, retirado al corregirla (`tests/test_ve1_validacion.py`).
- **Qué haría falta:** para D3, nada; para los dos decimales de `D`, una decisión de
  formato en la memoria.
- **Dónde vive:** `src/modulos/M2_material.py::_escalon_de_la_serie`

## VE1-02 · Las decisiones del dueño que la validación externa dejó a la vista, sin tomarlas

- **Qué se difirió:** siete decisiones, cada una con el número que la motiva; ninguna es un
  defecto de cálculo. (a) El n del concreto, o su columna de la Tabla Nº 09, como [A]
  declarable, como `n_manning_hdpe` y `n_manning_cajon`: con 0.013 el tirante normal sale
  de +5 a +8 % sobre el de HY-8 con 0.012 (13 filas del TDOT). (b) `V_erosion` es V(n
  máx) × n_máx/n_mín (× 1.30) sobre la geometría de n máximo, no Manning con n mínimo
  (+21.5 a +23 %): en UPAO ALC46 (Q = 0.317 m³/s, S = 0.10) sube el diámetro
  de 0.90 a 1.35 m (a 0.90 m, 6.28 frente a 5.81 m/s; umbral 6.0). (c) Las hipótesis de V7,
  sumersión completa y DC = 0, justificadas en `M8_estructural` con el NF somero del Bajo
  Piura, un argumento de sitio: con el NF a 10 m V7 descarta igual (1.2745 frente a
  9.6235 kN/m); equivalen a un relleno de unas 0.50 veces el diámetro exterior con γ_EV = 0.90
  (0.45 con γ_EV = 1.00, sin factorar). (d) El
  factor 1.13 de intervalo fijo de las series de 24 h, que el Manual no trae y aplican la
  tesis UPAO y la vía TU-107: sin él P24 y Q quedan 11.5 % abajo. (e) Un aviso de
  plausibilidad de la serie SIN umbral (patrón de `FH.Q_ESPECIFICO`): el Manual manda
  evaluar «la consistencia de los datos registrados» (núm. 3.3, pág. impresa 21; el prompt
  citaba el 3.4); la serie de TU-107 (mediana 140, máximo 729 mm) se ajusta sin aviso.
  (f) El racional modificado hasta 770 km² (pág. impresa 51, ficha T1-08): la Fase 1-bis
  se detiene desde 10 km², y Tinas (55.9 km²) y cinco cuencas de TU-107 no se calculan.
  (g) En D1, resolución de centímetro: rechazar en la puerta la serie de 6 in, que
  redondeada se leía 1.07 por 1.0668 (+0.3 % de diámetro, +0.6 % de área).
- **Cerrado (VE-2):** (b), ficha VE2-B; (a) y (g), VE2-A y VE2-G; (e), (f) y (d), VE2-E,
  VE2-F y VE2-D.
- **Cerrado (VE-2), (c1):** ficha VE2-C.
- **Cerrado (VE-2), (c2):** ficha VE2-C.
- **Por qué no se toman aquí:** cambian fichas, etiquetas o diseños —(b) y (c)— o lo que
  el programa calcula; el permiso de VE-1 no las alcanza.
- **Qué haría falta:** la decisión del dueño y, por cada una adoptada, un prompt con sus
  tests en rojo: un criterio con nivel, sensibilidad y resolución en (a) a (d), un aviso
  con su `Fundamento` en (e), el método con su cita en (f), la guardia en (g).
- **Dónde vive:** `src/modulos/M3_hidraulica.py::resolver_manning` (a) y (b);
  `M8_estructural.empuje_flotacion_kn_m` (c); `MH_hidrologia.precipitacion_de_diseno`
  (d) y (e); `MH_hidrologia.caudal_de_diseno` (f); `criterios_adoptados._verificar_criterio` (g).

## VE2-B · La velocidad de erosión resuelve su propio tirante con n mínimo

- **Cerrado (VE-2, bloque 1; decisión (b) de VE1-02, 2026-11-17):** la velocidad alta
  era la de n mínimo sobre el tirante de n máximo (V·A = 1.3·Q en el concreto); hoy
  una segunda resolución de Brent da su tirante (`TiranteNormal.geometria_erosion`) y
  `V_erosion = Q/A` de él, con el trato de la primera si no converge. No cambian
  `V_sedimentacion`, el tirante de capacidad ni la velocidad de salida bajo control de
  salida. Citas: HDS-5 núm. 3.3.2, pág. impresa 3.24 (ya registrada) y HEC-14 núm.
  3.2.2, pág. impresa 3-7 (`HEC14.3.2.2#V_SALIDA_NORMAL`, nueva, con el ejemplo de la
  pág. 3-8). `F4.MANNING` dice que la doble n es adopción (y, hasta que el dueño corrigió
  la hoja de ruta el 2026-11-18, que ésta la rotulaba «Regla [N]»).
- **Por qué así:** consumidores, con la tabla de cada uno verificada en el Manual
  (págs. impresas 76-77): V3 juzga la velocidad del conducto contra la Tabla Nº 10;
  M4 la toma como `V_salida` bajo control de entrada; M6 la usa en Laushey, el Froude
  y el contraste con la Tabla Nº 11 (velocidad de salida), y en el aviso de la banda
  de régimen; M11, la CLI y la ventana la imprimen. El tirante de salida que M4
  publica bajo control de entrada sigue siendo el de n máximo, porque lo leen como
  NIVEL la Ec. (10.5) de HEC-14 y el cabezal (M9). La variante `caudal_calculado` de
  T-11 vacía el caudal del evento extremo, que era el del Q declarado (V8 lo
  rechazaba en B-01). Los números movidos, punto por punto, en `docs/linea_base.md`
  §11: A-01 3.206 → 3.040 m/s y d50 0.338 → 0.304 m; A-02 2.883 → 2.681 m/s, d50
  0.274 → 0.237 m y la piedra baja a la clase 3; C-01 2.084 → 1.955 m/s. **Ningún
  diámetro, sección ni material se mueve; ninguno sube.** UPAO ALC46 dimensiona
  Ø 0.90 m con 5.81 m/s. Los tests que cambiaron, con su causa, en el mismo §11.
- **Qué haría falta (lo diferido):** (i) si el tirante de salida bajo control de
  entrada pasa al de n mínimo en la Ec. (10.5) de HEC-14 (sube el D50) sin bajar el
  nivel del cabezal: decisión del dueño, separando los dos tirantes en
  `ResultadoHidraulico`; (ii) el 1.184 m/s del dictamen (hoy 1.107) sigue como
  histórico en `src/servicio.py` y `src/constantes_normativas.py`, fuera del permiso;
  (iii) la hoja de ruta §4.1, corregida por el dueño el 2026-11-18 (VE1-01, VE2-01).
- **Dónde vive:** `src/modulos/M3_hidraulica.py::resolver_manning`

## VE2-A · La columna del n del concreto es una elección [A]

- **Cerrado (VE-2, decisión VE1-02 (a)):** la columna de la Tabla Nº 09 de la que sale el n
  del TUBO de concreto es el criterio [A] de perfil `columna_n_manning_concreto` (forma
  `categoria`): `doble_n_minimo_maximo` (archivo: MÍNIMO 0.010 para velocidad, MÁXIMO
  0.013 para capacidad, lectura corregida del bloque A.2, DIS-MCHHD-T09-A2-DESPLAZADA),
  `columna_normal` (0.011, NORMAL de la misma fila) y `n_unico_hds5` (0.012, [C], HDS-5
  núm. 3.1.4, pág. impresa 3.8, PDF 90). Lo lee `M2.catalogo` sólo para el tubo; el marco
  sigue con `n_manning_cajon` y el HDPE con `n_manning_hdpe`. La tabla sigue [N] en
  `constantes_normativas.TABLA_09_FILAS`; el 0.012 es [C] en
  `criterios_adoptados.N_MANNING_PARED_LISA_HDS5`, atado por test a su frase. La elección
  se desarrolla en la memoria (paso `F4.N_CONCRETO`, verbo DEFINE: sus cuatro citas son
  DEFINICION, ninguna manda una columna). Barrido en `docs/validacion_sensibilidad.md`.
- **Por qué así:** el Manual (núm. 4.1.1.3.6, pág. impresa 74) sólo dice «n : Coeficiente
  de Manning (Ver Tabla Nº 09)» y la tabla (pág. impresa 75) no dice qué columna; el HDS-5
  da 0.012 como n típico de pared lisa y 0.011 a 0.013 para el tubo en obra (núm. B.2,
  pág. impresa B.2). Con el valor de archivo **ningún número se mueve**: la línea base
  cambia sólo en la huella de `criterios_adoptados.py`, el recuento 141 → 142, la ficha
  del criterio y el paso nuevo (texto); ninguna cota, tirante, velocidad ni diámetro.
- **Abierto:** (1) cerrado el 2026-11-18: el dueño corrigió la §4.1 (ficha VE1-01, D3). (2) La fila «Rugosidad (regla de doble n) … Fila de la Tabla N 09» de
  `M11._filas_combinacion_adoptada` es texto fijo de M11, fuera del permiso: con una
  alternativa declarada imprime ese rótulo seguido de la columna o de la fuente real
  (`Material.fila_manning`). (3) El comentario de `modelos.Material.pasos` («VACIA EN LA
  CIRCULAR») ya no es cierto del tubo de concreto; `modelos.py` está fuera del permiso.
- **Qué haría falta:** (2) y (3), una línea en
  `M11_reporte.py` y otra en `modelos.py` al integrar.
- **Dónde vive:** `src/modulos/M2_material.py::_par_manning_del_tubo_de_concreto`

## VE2-G · Los diámetros son los designados por la norma de producto

- **Cerrado (VE-2, decisión VE1-02 (g)):** comprobado PRIMERO que los trece escalones de
  la progresión de archivo son designados para cada material que los usa (13 el
  concreto, 9 el TMC, 5 el HDPE). Las series designadas son [N] en
  `constantes_normativas.DIAMETROS_DESIGNADOS_MM`, leídas del registro: M 170M Tabla 5
  (300 a 3600 mm), M 36 Table 6 / ASTM A760 Tabla 1 (100 a 3600, con 500 y sin 525) y
  M 294 núm. 7.2.1 (300 a 1500, sin 825). `M2.siguiente_diametro` rechaza, POR MATERIAL,
  el escalón no designado (`DatoInvalidoError` sobre 'diametros_normalizados'). El
  diámetro inglés convertido (p. ej. 1.0668 m) sólo lo admite el concreto y sólo con el
  criterio [A] de perfil `diametro_de_diseno_concreto` = 'designado_o_ingles_convertido'
  (archivo: 'designado'): AASHTO M 170M núm. 12.1, pág. impresa M 170M-19 (PDF 19),
  PERMISO, y su Table 6, pág. impresa M 170M-20 (PDF 20), en el registro como
  `AASHTO_M170M.T6` (300 a 2700 mm, `EQUIVALENTE_INGLES_M170M`). Las dos leídas por
  imagen: la página es una recomposición OCR y la transcripción corrige nueve celdas
  (DIS-M170M-T6-RECOMPOSICION) y letras de la frase (nota de la cita).
- **Por qué así:** la guardia vive en M2 y no en la puerta del criterio porque la
  progresión es una para tres materiales con series distintas, y la puerta no sabe qué
  materiales ni qué tope recorrerá la corrida; la puerta sigue exigiendo la estructura
  (VE-1 H2). Tolerancia `TOL_UMBRAL_NORMATIVO` en metros, no de centímetro: 375, 525, 675
  y 825 mm son designados. Un escalón no positivo lo sigue rechazando la hidráulica
  (rama de error de la línea base). Con los valores de archivo ningún número se mueve.
- **Abierto:** (1) cerrado en VE-5 (abajo). (2) cerrado en VE-7 (ficha VE7B-02: la pared del
  inglés es la del designado). (3) Las seis filas de 2850 a 3600 de la
  Table 6 no se transcriben (`Acotada`).
- **Cerrado (VE-5, ítem 24), (1):** el tope y V9 comparan el designado
  (`M2.diametro_designado`); 108 in entra como 2700 mm. (3) releída por imagen: sigue
  ilegible (2830, iM8, 3333, U38, 3S05 y la última fila).
- **Qué haría falta:** (3) otro ejemplar de M 170M, no recompuesto.
- **Dónde vive:** `src/modulos/M2_material.py::_exigir_escalon_designado`

## VE2-C · V7: el nivel de agua de diseño es una elección [A] del Propietario

- **Cerrado (VE-2), (c1):** V7 ya no se justifica con el NF somero del Bajo Piura (argumento
  de sitio): el Manual de Puentes 2.4.3.8.1, pág. impresa 113 (AASHTO 3.7.1, pág. 3-45),
  deja el nivel de agua de diseño al Propietario; 2.4.3.8.2 hace actuar la subpresión
  «debajo» de él; AASHTO 12.6.1 y 12.6.2.3 no dan cota. El nivel en la clave es una adopción
  [A] conservadora, y DC = 0 queda del lado seguro frente al 0.90·DC de la Tabla
  2.4.5.3.1-2 (C12.6.2.3: «the dead load on the crown»). La equivalencia de VE1-02 (c),
  medida con el código: 0.50 · D_ext con γ_EV = 0.90 (0.45 con 1.00, sin factorar).
- **Cerrado (VE-2), (c2):** criterio `nivel_agua_diseno_v7` [A] de perfil: `en_la_clave`
  de archivo (lo de siempre; ningún número de la línea base se mueve) o `nf_del_punto`,
  cota_terreno − NF + `margen_estacional_nf_v7_m` ([A] de perfil sin valor, que detiene: la
  columna es una lectura de campo y no el freático más alto de 12.6.2.3). V7 se evalúa sólo
  si el fondo exterior queda bajo el nivel (12.6.1; si no, «no aplica»), con el área
  exterior bajo el nivel, y el relleno bajo el agua pesa γ_sat − γ_agua, [N→] del Manual de
  Puentes 2.4.4.1.3 (empuje lateral). El pre-vuelo y el censo lo dicen con y sin la
  alternativa.
- **Abierto:** (1) cerrado en las correcciones de la revisión (VE2-03, M3): con
  `nf_del_punto` y el nivel sobre la clave una corrida de perfil se detiene en
  `peso_especifico_saturado_relleno_kn_m3`, que hoy es [S] pendiente de ensayo y de perfil
  (VE2-05, N2), y el filtro de perfil de la pestaña 2 lo muestra;
  (2) la hoja de ruta (fila V7; Fase 8, ítem 3, «con NF a 1.4 m») callaba que el nivel lo
  fija el Propietario: cerrado el 2026-11-18, el dueño la corrigió (ficha VE2-01).
- **Qué haría falta:** nada para (1) y (2).
- **Dónde vive:** `src/modulos/M8_estructural.py::cota_nivel_agua_v7_del_nf`

## VE2-E · Aviso de consistencia de la serie de lluvias, sin umbral — Cerrado (VE-2)

- **Qué se difirió:** nada de lo decidido: el dueño eligió (2026-11-17) el aviso sin umbral
  de VE1-02 (e). La lluvia de diseño emite un quinto paso, `1b.3c` (`FH.CONSISTENCIA`,
  verbo «obliga»), DESPUÉS de los cuatro de T-1: dice que el Manual exige evaluar «la
  consistencia de los datos registrados» (núm. 3.3, pág. impresa 21, PDF 24, cita
  `MC_HHD.3.3#CONSISTENCIA`, EXIGENCIA) y que es «primordial» (núm. 3.4, pág. impresa 22,
  `MC_HHD.3.4#CONSISTENCIA`, DEFINICIÓN), que el programa NO la evalúa y que el
  proyectista tiene que declarar que lo hizo. Imprime mínimo, mediana, máximo (con su año)
  y máximo / mediana de la serie ENTERA registrada, sin umbral ni veredicto. **Queda
  diferido** un contraste cuantitativo: no hay procedimiento ni número de corte (buscados
  «doble masa», «double mass», «outlier» y «dudoso» en el Manual de Hidrología, WSDOT,
  HEC-14, HDS-5, Puentes y DG-2018: cero; «consistencia» sólo en las dos citas).
- **Por qué:** fijar un corte sería rellenar un vacío (CLAUDE.md, «Fuente de verdad»).
  Patrón de `FH.Q_ESPECIFICO`. Va al final para no mover las posiciones que T-1 fijó; dos
  tests de T-1 cambiados declarando la causa (`PASOS_DE_LA_FASE_1B`, y el paso sin
  `formula_cita_id`). Ningún número se mueve: el índice de fórmulas gana una fila.
- **Qué haría falta:** para el contraste cuantitativo, una fuente con procedimiento y umbral
  en el repositorio de normas, su cita, y un criterio [A] con valor None que detenga hasta
  que se declare; los tests, en `tests/test_ve2_hidrologia.py` (siete mutantes muertos).
- **Dónde vive:** `src/modulos/MH_hidrologia.py::_paso_consistencia`

## VE2-F · Método racional modificado de 10 a 770 km² — Cerrado (VE-2), con tres lecturas declaradas

- **Qué se difirió:** nada de lo decidido (dueño, 2026-11-17, VE1-02 (f)). Desde 10 km² el
  caudal de una obra sale del núm. 3.12.2.1 entero, ec. (29) a (35), leídas en la IMAGEN
  de las págs. impresas 51 y 52 (PDF 54 y 55): KA, P = KA·Pd, I con el 11 fijo, Po =
  5000/CN − 50, C, K siempre, Q = 0.278·C·I·A·K; citas `MC_HHD.3.12.2.1#METODO`, `#KA`,
  `#P`, `#I`, `#C`; literales [N] en `constantes_normativas.py`. Fuera de A < 770 km² y de
  0.25-24 h, `MetodoNoEvaluableError` con el rótulo de la hidrología, nombrando SCS
  triangular (hasta 30 km², pág. 56), Snyder (30 a 30 000 km², pág. 58) y HEC-HMS (núm.
  3.12.4), **no implementados**. El aporte de una cuneta sigue con el racional simple.
- **Por qué:** tres lecturas, declaradas en el punto de uso: (1) KA = 1 − log10(A)/15
  (`Interpretacion` de `#KA`); (2) la ec. (35) escribe Pd y no la P corregida: se aplica
  sin corregirla, y el paso imprime el C que daría P; la «pd» minúscula se lee Pd; (3) la
  frontera de 10 km² es la del racional simple («Muy usado para cuencas, A<10 Km2», pág.
  49): los dos rangos se solapan y bajo 10 km² no cambia nada. Se avisa «adaptada para las
  condiciones climáticas de España». CN es la columna opcional de la ecuación de retardo,
  REUSADA: desde 10 km² obligatoria (Tabla Nº 07, pág. 47, cita `MC_HHD.3.11#T07`), y
  `metodo_tc` tiene que ser `temez` (ec. 30). Ni el pre-vuelo ni la pestaña 1 listan
  columnas a mano: no se tocan. Ningún número de la línea base ni de la corrida de
  referencia (sus cuencas tienen menos de 10 km²).
- **Qué haría falta:** para cuencas desde 770 km², implementar un método de hidrograma con su
  cita; para Pd ≤ Po (C ≤ 0), que el Manual diga qué hacer: hoy detiene. Tests y una cuenca
  de PRUEBA de 55.9 km² (`cuencas_racional_modificado_prueba.csv`) en
  `tests/test_ve2_hidrologia.py`.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::_caudal_racional_modificado`

## VE2-D · Factor de intervalo fijo de la serie de 24 h como criterio [A], con 1.00 — Cerrado (VE-2)

- **Qué se difirió:** nada de lo decidido (dueño, 2026-11-17, VE1-02 (d)). Criterio [A] de
  perfil `factor_intervalo_fijo_p24`, forma `float`, valor de archivo 1.00 (la lectura
  literal del Manual: la máxima en 24 horas sin conversión, núm. 3.8.1, pág. impresa 36,
  cita `MC_HHD.3.8.1#P24`, y la fila de 24 h de la Tabla Nº 04 vale 1.00, pág. 37),
  ventana 1.00-1.13 y resolución `Libre`. El 1.13 es práctica SIN FUENTE en el
  repositorio de normas («1.13», «intervalo fijo», «fixed interval», «Weiss», «OMM», «WMO»
  buscados en el Manual de Hidrología, WSDOT, HEC-14, HDS-5, Puentes y DG-2018: ninguna
  aparición como factor de lluvia); pasaría a [C] sólo si se trae la guía de la OMM o
  Weiss (1964) con su página.
- **Por qué así:** se aplica a la SERIE, antes del ajuste (`precipitacion_de_diseno`), y no
  al cuantil: corrige cada lectura, y el contraste con lo observado (1b.2) y el de los
  años FEN (1b.3b) comparan lo mismo. Las tres distribuciones ajustadas son de escala: el
  cuantil sale exactamente multiplicado y D no cambia. El aviso de consistencia (1b.3c)
  sigue sobre la serie REGISTRADA. La memoria imprime el factor (`f_24h`, con su
  procedencia) y su elección (`FH.FACTOR_P24`) con la lluvia de los dos extremos; con un
  factor distinto de 1, un aviso. Con 1.00 cada dato se multiplica por 1.0: ningún número
  se mueve (índice de fórmulas y validación integral, sólo textos).
- **Qué haría falta:** para el [C], el PDF de la fuente del 1.13 en el repositorio de normas
  y su cita. Tests en `tests/test_ve2_hidrologia.py`; barrido sobre la variante
  `caudal_calculado` en `tests/apoyo/sensibilidad.py`.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::precipitacion_de_diseno`

## VE2-01 · Lo que seguía mal en la hoja de ruta después de VE-2 (lo corrigió el dueño, 2026-11-18)

- **Qué se difirió:** corregir `docs/hoja_de_ruta_alcantarillas_v8.md`, que VE-2 no edita.
  Tres textos, cada uno verificado contra su PDF y declarado en el punto de uso:
  (1) la §4.1 rotula la doble n «**Regla [N]**» sin numeral: el Manual de Hidrología, núm.
  4.1.1.3.6, pág. impresa 74, sólo dice «n : Coeficiente de Manning (Ver Tabla Nº 09)», y la
  Tabla Nº 09 (pág. impresa 75) da MÍNIMO, NORMAL y MÁXIMO sin regla de columna; desde VE-2
  la columna es el criterio [A] `columna_n_manning_concreto` (VE2-A), y la velocidad a
  tirante normal la sostienen HDS-5 núm. 3.3.2, pág. 3.24 y HEC-14 núm. 3.2.2, pág. 3-7
  (VE2-B). (2) La fila **V7** de la Fase 5 («Tubería vacía, NF en su cota más alta») y la
  Fase 8, ítem 3 («obligatoria con NF a 1.4 m») callan que el nivel de agua de diseño lo
  especifica o aprueba el Propietario (Manual de Puentes núm. 2.4.3.8.1, pág. impresa 113);
  desde VE-2 es el criterio [A] `nivel_agua_diseno_v7` (VE2-C). (3) De VE1-01 sigue sin
  corregir la §1.2, nota `INF-5.1.11`: «la lee V7» de `NF_profundidad_m`, sin condición;
  desde VE-2 V7 la lee **sólo** con `nivel_agua_diseno_v7` = `nf_del_punto`.
- **Por qué:** la hoja de ruta es la fuente normativa única y la corrige su dueño; mientras
  no lo haga, quien la lea sin leer el código diseñará con el rótulo y la hipótesis
  equivocados (CLAUDE.md, «Fuente de verdad»). Las tres discrepancias están declaradas en
  `F4.MANNING`, en `M8_estructural` («Por que U asume sumersion completa») y en la fila de
  `NF_profundidad_m` de `docs/contrato_entradas.md`.
- **Cerrado (el dueño corrigió la hoja de ruta, 2026-11-18):** los tres textos, verificados
  de nuevo contra su PDF, con una nota «Corregido (`VE2-01` …)» cada uno: (1) la §4.1 rotula
  la doble n adopción [A] (`columna_n_manning_concreto`); (2) la fila V7 y la Fase 8, ítem 3,
  dicen que el nivel de agua de diseño lo especifica o aprueba el Propietario y que es el
  criterio [A] `nivel_agua_diseno_v7`; (3) la §1.2 dice que V7 lee el NF sólo con
  `nf_del_punto`. Retiradas las declaraciones de `F4.MANNING`, de `M8_estructural`, de la
  fila del contrato, de los docstrings de M3 y M2, de la ficha del criterio, y el centinela.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M8_estructural.py::regla_nivel_agua_v7`

## VE2-02 · Lo que VE-2 dejó diferido, reunido

- **Qué se difirió:** lo abierto de cada parte, cada uno en su ficha: (b) el tirante de
  salida bajo control de entrada sigue siendo el de n máximo (lo leen como nivel la Ec.
  10.5 de HEC-14 y el cabezal) y el 1.184 m/s del dictamen sigue como histórico fuera del
  permiso (VE2-B); (a) la fila «Rugosidad (regla de doble n)» de
  `M11._filas_combinacion_adoptada` es texto fijo que no nombra la columna declarada
  (VE2-A); (g) con la opción inglesa, el tope de 2.70 m y V9 comparan el diámetro de cálculo
  y no el designado, y la pared del diámetro inglés no está decidida (VE2-G); (c2) la hoja de ruta callaba que el nivel de agua de
  diseño lo fija el Propietario, corregida por el dueño el 2026-11-18 (VE2-C, VE2-01; el dato de ensayo de expediente que perfil pedía lo
  cerró VE2-03, M3); (e) el contraste
  cuantitativo de la consistencia, sin fuente (VE2-E); (f) cuencas desde 770 km² y Pd ≤ Po
  (VE2-F); (d) el 1.13 como [C], sin el PDF de su fuente (VE2-D). Y uno de la integración:
  `src/indice_formulas.py::menciones_del_fundamento` sólo reconoce ids `F<n>.<nombre>`, de
  modo que el índice rotula «sin mención fuera del registro» a `FH.FACTOR_P24`, que entra
  por `eleccion()` desde `MH_hidrologia` (lo mismo le pasa desde antes a
  `F5.V2b.REGIMEN`); es herramienta del índice, fuera del permiso de VE-2.
- **Por qué:** cada uno pide una decisión del dueño, una fuente que no está en el
  repositorio de normas o un archivo fuera del permiso de la etapa.
- **Qué haría falta:** lo que dice cada ficha; para el índice, ampliar el patrón a
  `F[0-9H]+\.[A-Za-z0-9_.]+` y regenerar `docs/indice_formulas.md`.
- **Dónde vive:** `src/indice_formulas.py::menciones_del_fundamento`

## VE2-03 · Lo que la revisión independiente de VE-2 encontró y se corrigió (A1, M3, M4, B1, B3, B4)

- **Cerrado (revisión Fable, `proceso/planes_mejora/ve2_estado/REVISION_FABLE.md`; un alto,
  dos medios y tres bajos):** (A1) el `DatoFaltanteError` de un dato DEL PUNTO que la Fase 5
  levanta sobre un escalón que cumple lo evaluado decide como el inválido de T11-03
  (`MD._detuvo_un_escalon_que_cumplia`; uno de catálogo no, ficha VE2-05): B-01 de la variante `caudal_calculado` ya no sale
  «no factible» con delta de rasante, sale el dato que falta (`Q_evento_extremo_m3s`), y
  con ese dato coherente se detiene en `perfil_hdpe_fabricante`. (M3)
  `peso_especifico_saturado_relleno_kn_m3` es de perfil, medido por una corrida de perfil
  con `nivel_agua_diseno_v7` = `nf_del_punto`, y es [S] pendiente de ensayo con su
  `trazabilidad` (ficha VE2-05, N2). (M4) `Criterio.no_negativo`, comprobado por `_verificar_signo` en los tres
  caminos, sólo en `margen_estacional_nf_v7_m`; sin tope inventado. (B1) el caso G2
  original (S = 0.012) queda fijado: se detiene en la clase D-load de la Fase 8. (B3)
  `TOL_REL_CONTINUIDAD_MANNING` a 1e-8: fuera de la malla de la suite (marcos con Q bajo el
  5 % del lleno) se midieron 1.81e-9. (B4) los cuatro parches de `ve2_estado/` retirados
  (siguen en la historia) y su LEEME al día.
- **Por qué así:** A1 es la regla de CLAUDE.md («un punto al que solo le falta un dato no
  es "no factible"»), aplicada con el mismo criterio que el dato inválido; M3 sigue la
  regla de las dos direcciones del nivel. Tests en rojo primero
  (`tests/test_ve2_correcciones.py`, `tests/test_ve2_revision_m3_m4.py`).
- **Qué haría falta:** nada para estos. Quedan para el dueño M1 (ficha VE2-04) y, ya
  diferido, M2 (VE2-B); B2 (un `TypeError` inalcanzable en M8) y B5 (dos diámetros de
  cálculo del concreto con la opción inglesa, declarado en la `Interpretacion`) se dejan
  como están.
- **Dónde vive:** `src/modulos/MD.py::_detuvo_un_escalon_que_cumplia`

## VE2-04 · V3 no mira la velocidad de salida bajo control de salida (M1 de la revisión independiente de VE-2)

- **Qué se difirió:** `M5._velocidad_de_v3` compara con el techo de la Tabla Nº 10 siempre
  `V_erosion` (Q / A del tirante normal de n mínimo) cuando S > 0. Bajo control de salida la
  sección de salida la define el tirante crítico, el TW o la altura del conducto (HDS-5,
  hif12026, núm. 3.1.6, pág. impresa 3.18: «In outlet control, the cross sectional area of
  the flow is defined by the geometry of the outlet and either critical depth, tailwater
  depth, or the height of the conduit»), y en pendiente suave con salida libre esa velocidad
  supera a la normal. El programa ya la calcula (`ResultadoHidraulico.V_salida`) y la juzga
  M6; V3 sólo la usa con S = 0 (T-2). Medido (`M4.resolver_control`, Ø 0.90 m, Q = 0.3 m³/s,
  S = 0.001, L = 20 m, TW = 0, concreto): `V_salida` = 1.508 m/s a y_c = 0.316 m y
  `V_erosion` = 1.107 m/s (1.184 con la fórmula anterior a VE-2, cuyo 30 % de más tapaba
  parte de la diferencia).
- **Por qué:** es anterior a VE-2, el prompt de VE-2 mandaba no tocar la velocidad de salida,
  y la corrección cambiaría diseños (puntos de pendiente suave con TW bajo el crítico
  podrían perder escalones por V3) y movería la línea base: es decisión del dueño, no una
  corrección. Con los techos de 3 a 6 m/s del concreto rara vez decide.
- **Qué haría falta:** nada: el dueño decidió que sí y se cerró en VE-3.1 (ficha VE3-01).
- **Dónde vive:** `src/modulos/M5_verificaciones.py::_velocidad_de_v3`

## VE2-05 · Lo que la verificación de las correcciones de VE-2 encontró (N1 a N7)

- **Cerrado (verificación Fable, `proceso/planes_mejora/ve2_estado/VERIFICACION_FABLE.md`;
  un alto, un medio y cinco bajos; decisiones del dueño del 2026-11-17 en N1 y N2):** (N1)
  A1 volvía decisiva también la fila de pared de un diámetro que V7 pide dentro de la Fase 5
  (30 casos del juego de T-11 pasaban de «no factible por rasante» con delta a «falta la
  pared»): decide sólo el dato del punto; el que nombra un criterio no
  (`MD._falta_un_dato_de_catalogo`), con el caso real fijado (A-01, Q = 1.0, S = 0.004,
  extremo 3.0: delta 0.31981) y los textos que decían que la pared se pide «antes de la
  tabla» corregidos. (N2) `peso_especifico_saturado_relleno_kn_m3` es [S] pendiente de
  ensayo, con `trazabilidad`, de perfil (medido); la excepción que M3 había puesto en la
  regla 3 de `_verificar_nivel` se retira y CLAUDE.md vuelve a su texto; `Criterio.positivo`
  rechaza en la puerta 0 y negativos, sólo en este criterio. (N3) VE2-C y VE2-02 al día. (N4)
  CLAUDE.md («Excepciones») recoge A1 y N1. (N5) VE2-04 detrás de VE2-03. (N6) la tolerancia
  de continuidad dice su dominio (Q desde el 0.1 % del lleno). (N7) el mutante de
  `_verificar_signo` con el criterio vacío muere.
- **Por qué así:** N1 conserva la ficha T4-10 para lo que es catálogo y la regla de CLAUDE.md
  («un punto al que solo le falta un dato no es "no factible"») para el dato del punto, con
  la misma frontera que el dato inválido (`exc.campo in ca.CRITERIOS`); N2 sigue la
  taxonomía: un dato determinado por un procedimiento no tiene rango que elegir y se
  defiende con trazabilidad, que es [S].
- **Qué haría falta:** nada para estos. De la segunda verificación (Fable, `VERIFICACION_FABLE_2.md`,
  «integrar en main»): la regla de N1 queda fijada también por `TW_evento_extremo_m`; la
  frontera es por NOMBRE (un dato de catálogo futuro de la Fase 5 cuyo campo no sea un
  criterio decidiría como del punto); por la CLI un dato de ensayo se sigue declarando sin
  nota, como antes de VE-2; y `c_phi_fundacion`, `capacidad_portante_adm` y
  `Mw_licuefaccion` seguían [A] con `DeEnsayo` (cerrado en VE-3.2, ficha VE3-02: los dos
  primeros son [S], el tercero sigue [A]).
- **Dónde vive:** `src/modulos/MD.py::_falta_un_dato_de_catalogo`

## VE3-01 · Bajo control de salida V3 juzga la mayor de `V_erosion` y `V_salida` (cierre de VE2-04)

- **Cerrado (VE-3.1, decisión del dueño del 2026-11-17):** con S > 0 y control de SALIDA, V3
  compara contra la Tabla Nº 10 la mayor de `V_erosion` y `V_salida`. La tabla limita «la
  velocidad» del flujo en el conducto sin restringirla al tirante normal (Manual de
  Hidrología, núm. 4.1.1.3.6, pág. impresa 76, `tablas.T10.texto_previo`), y bajo control de
  salida la sección de salida la definen y_c, TW o D (HDS-5, núm. 3.1.6, pág. impresa 3.18).
  Bajo control de entrada y con S = 0 no cambia; sin `V_salida` bajo control de salida sale
  `MetodoNoEvaluableError`. El caso de VE2-04 compara 1.5076 m/s.
- **Por qué así:** medir en la sección más rápida del conducto es la lectura conservadora, y
  es LECTURA del proyecto, declarada en el docstring. La línea base no mueve ningún número
  (en sus corridas la salida es más lenta): sólo crece la procedencia (docs/linea_base.md
  §18); ningún diámetro, sección ni material cambia.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::_velocidad_de_v3`

## VE3-02 · Los parámetros del suelo de fundación son [S] pendientes de ensayo (cierre de lo que VE2-05 dejó al dueño)

- **Cerrado (VE-3.2, decisión del dueño del 2026-11-17):** `c_phi_fundacion` y
  `capacidad_portante_adm` son [S] con su `trazabilidad`: salen del estudio de mecánica de
  suelos de este sitio y no hay rango que elegir, la misma razón que N2 aplicó al peso
  saturado. La capacidad portante lleva `positivo`; `c_phi_fundacion` no (es un dict: sus
  campos los valida `M9.validar_suelo_fundacion`). `Mw_licuefaccion` sigue [A]: elegir el
  escenario sísmico es decisión del proyectista. Ningún valor cambia.
- **Por qué así:** la taxonomía de CLAUDE.md: un [S] se defiende con trazabilidad, no con
  sensibilidad; el anexo A.4 de la memoria (sólo [A]) deja de listarlos, que es lo coherente.
  Línea base: la huella y la etiqueta de las dos filas (docs/linea_base.md §19).
- **Qué haría falta:** nada para estos; por la CLI un dato de ensayo se sigue declarando sin
  nota, como antes de VE-2.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::validar_suelo_fundacion`

## VE3-03 · M9 contra ejemplos publicados (Caltrans BDP 11.2.2, CDOT Ex. 11)

- **Cerrado:** 64 contrastes de M9 contra lo recalculado con la fórmula de cada fuente: 57
  coinciden al 1 %, 4 son erratas de la fuente (el motor coincide con lo recalculado), 3
  difieren por el módulo Ec y 0 son defectos (empujes, excentricidad, presión de contacto
  uniforme y lineal, e admisible sísmica, flexión, Mcr, fisuración, dv y Vc con el β de la
  fuente, decisión del simplificado, acero de temperatura). Las filas de método exigen además
  que el motor dé la referencia de su método, calculada aparte. Correcciones de la revisión
  Fable (A-3, M-1): la «errata» de temperatura de CDOT se retiró (la hoja comprueba el piso en
  AD456) y la ec. 5.10.6-1 se contrasta en los tres casos de la hoja y el piso aparte. O-1 se
  cierra a favor de M9: AASHTO C5.4.2.4-1 (pág. 5-20, PDF 379) da 2 500·f'c^0.33 para el
  concreto de peso normal con w_c = 0.145 kcf; los 0.150 kcf de CDOT son los del concreto
  armado para cargas muertas.
- **Abierto:** O-2 se CERRÓ (decisión 3 del dueño, VE-3.12): el acero de temperatura usa el
  ancho real, que es lo que 5.10.6 escribe («least width of component section»). Sin ejemplo
  externo: la estabilidad integrada
  (`ensamble_estabilidad`, cuña de tanteo, Mononobe-Okabe con relleno inclinado) y las ramas
  piso 0.72·h de dv, γEQ = 1 y tope de V_n.
- **Qué haría falta:** un ejemplo con la geometría completa del relleno para la cuña y el
  sismo.
- **Dónde vive:** `tests/apoyo/validacion_cabezal.py::contrastes`

## VE3-04 · M8 contra ejemplos publicados (ACPA, USACE, PPI)

- **Cerrado:** `docs/validacion_conducto.md` contrasta M8 con ACPA DD 1, DD 22 y CPDM cap. 4
  y con el USACE EM 1110-2-2902 ap. B: 44 contrastes en dos categorías que no se suman
  (revisión Fable, A-1). Contrastados con la fuente, 33 (IM, VAF, B_FE con el 3.93 del CPDM
  4-2, un B_FLL, el empuje de flotación, el USACE y la clase II); el motor reproduce su propio
  método, 11 (toda la carga viva y la D-load, más la rama l_w < B_c sin fuente). 0 defectos;
  dos erratas de las fuentes (el intermedio del CPDM 4-7 y el «4267» de DD 22). W_L se lee por
  la ruta real (`verificar_concreto`) y la referencia interpola a mano (A-2).
- **Abierto:** con poco relleno la carga viva de M8 sobre tubos pequeños sale por encima de
  ACPA (+65 % en DD 1 ej. 1, +104 % de D-load en el CPDM 4-7), casi toda por la longitud
  efectiva (ej. 1: +9.6 % de presión y +50.7 % de L_e; ej. 4: −2.1 % y +32.2 %). Repartir sin
  L_e es la lectura LITERAL de la 9.ª ed., no un defecto: 12.10.2.3 (pág. 12-54, PDF 1692,
  «uniform vertical distribution across the top of the pipe») y C12.10.4.3.2c (pág. 12-66,
  PDF 1704). Reserva: ningún ejemplo resuelto con la edición 2013 o posterior lo confirma con
  un número. Sin contrastar: el HDPE del PPI, la costura y el FF ASD del TMC.
- **Qué haría falta:** decisión 6 del dueño (VE-3.12): se MANTIENE la lectura literal; se
  añade sólo el paso F8.ACPA, un contraste que NO gobierna (la clase que saldría con
  W_L·w_w/(w_w + 1.75·0.75·B_c)), para tubo de concreto con relleno menor que
  `relleno_max_contraste_acpa_m` ([A] de perfil, 1.0 m); la causa dominante del +65 % es que
  la 9.ª ed. no escribe L_e (×1.51), no la edición (×1.10). Sigue pendiente la revisión de un
  ingeniero y un ejemplo de HDPE con HL-93.
- **Dónde vive:** `tests/apoyo/validacion_conducto.py::contrastes`

## VE3-06 · VC3: las pérdidas de la obra contra el desnivel del perfil del canal (Familia C)

- **Cerrado (VE-3.6; VE-3.10, decisión del dueño del 2026-11-17):** VC3 = (cota_entrada + HW) −
  (cota_fondo_receptor + TW) ≤ F, con F el desnivel del perfil del canal en el cruce
  (`desnivel_perfil_canal_m`, clave [S] del canal en `--datos-externos`, sólo Familia C).
  Fuente [C] `USBR_DSCS`: USBR, *Design of Small Canal Structures* (1978), núm. 2-6, pág.
  impresa 23 («F (water surface differential) = Upstream canal NWS El. - Downstream canal NWS
  El.») y 24 («Compare computed losses with the loss provided on profile sheet»); el PDF, de
  dominio público, está en el repositorio de normas. Va en la posición de VC1 y DIMENSIONA
  (con la entrada en el canal, F = 0.30 m lleva el marco de C-01 a 1.50 × 1.20 m). SIN F el
  punto se DETIENE (`DatoFaltanteError`, a los dos alcances), el pre-vuelo lo anuncia como
  falta que detiene y el aviso de 7.B se retiró. Los juegos de prueba declaran F = 1.20 m,
  rotulado (con la entrada en el terreno el marco pierde entre 0.91 y 1.02 m); la variante
  `C01_sin_desnivel` muestra el bloqueo.
- **Por qué así:** es el criterio del propio diseño de canales (la obra no puede consumir más
  carga que la que el perfil del canal le deja), y F es del canal, no del proyectista de la
  vía: un cruce sin él no se entrega sin verificar.
- **Qué haría falta:** el bloqueo diferido de VC1 sigue diciendo «rasante hidráulica, no»
  aunque VC3 ya la verifica, y la CLI imprime «umbral del criterio» para un dato externo:
  dos textos por corregir.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::vc3_rasante_canal`
## VE3-07 · El remanso del canal por paso directo (Familia C)

- **Cerrado (VE-3.7):** `M3.perfil_remanso_trapecial`, paso directo (HDS-5 núm. 3.5) en canal
  prismático trapecial con escalones geométricos en (y − y_n), y el tirante conjugado por la
  función momentum (`M3.tirante_conjugado_trapecial`): en canal de pendiente fuerte la curva
  S1 concluye en el resalto; en canal suave la M1 se calcula hasta donde el proyectista declare
  (`fraccion_fin_remanso_canal`, [A] de perfil, opcional, ventana 0.001–0.05) y sin el
  criterio queda la cota inferior dh/S. Contrastado con una integración independiente
  (scipy `solve_ivp`, rtol 1e-11) y con Bélanger en el rectangular: peor error 6.5e-8, contra
  una tolerancia nombrada de 1e-6.
- **Abierto:** el perfil supone un canal prismático (sin la coronación a lo largo del tramo, el
  cruce es la sección crítica). Desde VE-4c V5 de las Familias A y B usa este mismo paso
  directo con la sección del cauce de aproximación (T7B-01), y su escalón —la energía y la
  fricción, `M3.energia_y_friccion_trapecial`— se contrasta con el perfil publicado del USBR
  (223-E3WSP, pág. impresa 428); un remanso M1 resuelto paso a paso y publicado sigue sin
  aparecer en el repositorio de normas.
- **Qué haría falta:** un ejemplo resuelto publicado de un perfil M1 o S1 (p. ej. del manual
  de referencia de HEC-RAS).
- **Dónde vive:** `src/modulos/M3_hidraulica.py::perfil_remanso_trapecial`

## VE3-05 · El cabezal se dimensiona: la zapata crece por el talón (estabilidad) y en peralte (armado)

- **Cerrado (VE-3.5; VE-3.9, decisiones del dueño del 2026-11-17):** detrás de la estabilidad de
  la regla, B_k = B_regla + k·paso hasta cumplir E1 a E3, sin pasar fraccion_ancho_max·H_c
  (crece el talón). Después el peralte crece con el mismo paso hasta que el armado de la punta
  y del talón (A1, A2, A3, A4, A6) cumple, re-verificando la estabilidad con cada peralte (el
  ancho puede volver a crecer; el bucle termina porque los dos sólo crecen y están acotados).
  `dimensionamiento_zapata_cabezal` [A] con valor de archivo 0.10 m y 1.5·H_c (decisión del
  dueño; ventana propuesta 0.05–0.20 m y 1.0–2.0·H_c); el tope del peralte es físico (deja
  pantalla). Orígenes «dimensionada por estabilidad» y «dimensionada por armado»; trazas en
  `F9.DIMENSIONADO` y `F9.DIMENSIONADO_PERALTE` (AASHTO 11.6.3.x, 5.6.3.2.1, 5.7.3.3). Con los
  datos de prueba no queda ninguna fila de zapata ni de estabilidad LRFD sin cumplir (titular:
  peraltes de 1.00 a 1.50 m y anchos de 3.38 a 5.28 m; juego: dos salidas con 0.80 y 0.70 m).
- **Abierto:** (1) los peraltes con el cortante fuera de 5.7.3.4.1 se saltan (el procedimiento
  general de 5.7.3.4.2 no está implementado), lo que agranda el peralte más de lo necesario;
  (2) el espesor de la pantalla y del alero no se dimensionaba (A1 de la salida de A-01, A-02 y
  C-01 sin cumplir): CERRADO en VE-3.14 (ficha VE3-14); (3) el dentellón de corte de 11.6.3.5 no se ofrece.
- **Qué haría falta:** el cortante general de 5.7.3.4.2 y extender el dimensionamiento a la
  pantalla y al alero.
- **Dónde vive:** `src/modulos/M9_cabezal/dimensionamiento.py::dimensionar_peralte_por_armado`

## VE3-08 · Ensayos de diseño del conducto: H4, H2, H6 y H3 (VE-3.11)

- **Cerrado:** (H4) V7 suma el peso propio del conducto de concreto, γ_c·(A_ext − A_int), con
  `peso_especifico_concreto_kn_m3` [C], ahora de nivel perfil (fila V7 de la hoja de ruta:
  0.90·(DC + EV) ≥ U); TMC y HDPE sin DC (el peso del producto no es dato declarado); con DC,
  engrosar la pared mejora la flotación. (H2) Bajo control de entrada, si el TW alcanza el
  conjugado del tirante normal (`M3.tirante_conjugado_barril`, función momentum) el resalto
  entra al barril (HDS-5 3.1.3, pág. 3.2) y V1 juzga con el tirante máximo del perfil; también
  con barril subcrítico y TW > y_n: la lectura de `borde_libre_bajo_tw_ahogante` es una sola a
  lo largo del TW (nota T-2). (H6) El titular de un «no factible» nombra V2, V2b o V10 cuando
  fallan en todo escalón evaluado. (H3 b) El delta de 7.A se rotula si V7 seguiría sin cumplir.
  Línea base §25: ningún diámetro, sección ni material (B-01 pasa a «NO FACTIBLE POR V2»).
- **Cerrado (VE-5, lote m45, ítem 17):** V2 adopta la velocidad aguas abajo del resalto. Con
  el resalto dentro del barril bajo control de entrada (o el barril subcrítico con el remanso
  M1 en la salida) V2 juzga la velocidad MÍNIMA del perfil, Q_celda / A(y_max), por la misma
  bifurcación que V1 (`M5._entrada_con_receptor`): el numeral pide «la velocidad mínima del
  flujo dentro del conducto», y tras el resalto la lámina sube hasta el TW. El paso imprime
  al lado la velocidad tras el resalto de HEC-14 (V2 = Q/A2, paso 3 de los ejemplos, cita
  `HEC14.6#V_TRAS_RESALTO`), que no se compara. El resalto lo sitúa M4 (ficha EA-02).
- **Abierto:** (H3 a) el delta con V4 gobernada por el resguardo sigue sin darse (regla de
  T11-03: el HW depende de la longitud); E06
  (titular por V3), H7 (la progresión sigue tras una falla que sólo empeora) y H8 (cobertura G1
  fuera del bucle).
- **VE-6 (ítem 34):** H8 (G1 dentro del bucle), H7 con V10 y el delta con V4 bajo control de
  entrada quedan cerrados (ficha VE6-34); siguen H7 con V2/V2b/V7 y el delta bajo salida.
- **Qué haría falta:** iterar 7.A con el HW para dar el delta de resguardo.
- **Dónde vive:** `src/modulos/M5_verificaciones.py::v1_borde_libre`

## VE3-09 · El diámetro gobernado por el nivel del receptor se dice (decisión 8 del dueño, VE-3.13)

- **Cerrado:** `borde_libre_bajo_tw_ahogante` sigue en «no_cumple» y ningún diámetro cambia.
  Cuando V1 descarta escalones SÓLO por el TW (marca `Verificacion.descarta_solo_el_receptor`),
  MD vuelve a pasar la Fase 5 por ellos con la lectura «aviso» forzada
  (`M5.lectura_bajo_tw_forzada`, sin declarar nada) y emite el paso `F5.V1.RECEPTOR` y
  `ResultadoPunto.gobierno_por_receptor`: (a) los escalones descartados por el receptor; (b)
  el diámetro hidráulico (el que «aviso» adopta); (c) el descenso del TW o la subida de la
  solera, TW − (y/D)max·D_h, rotulado como ALTERNATIVA no verificada. Lo imprimen la memoria
  completa y la resumida, la CLI, la pestaña 3 y el JSON. E07 de los ensayos: Ø 1.35 adoptado,
  Ø 0.90 hidráulico, 0.325 m. La línea base no lo ejercita (§27).
- **Por qué así:** es presentación emitida por el cálculo (la regla de la memoria), no
  aritmética en M11, y la causa la dice la propia justificación del criterio.
- **Qué haría falta:** si el dueño quiere la cota absoluta de salida, pasar la cota de 7.B al
  paso (hoy se da como descenso, porque 7.B corre después de MD); si la pasada hipotética con
  «aviso» lanza en algún escalón, no se afirma nada.
- **Dónde vive:** `src/modulos/MD.py::_gobierno_por_receptor`

## VE3-10 · Clases III a V del tubo de concreto desde una fuente secundaria, con tope de diámetro por clase

- **Cerrado (decisiones 1 y 7 del dueño, VE-3.12):** `clases_producto_por_relleno` [C] = II 50,
  III 65, IV 100, V 140 N/m/mm (0.3 mm). La II, de M 170M legible; III a V, de la tabla de ASTM
  C76 del ejemplo resuelto del USACE EM 1110-2-2902, ap. B, pág. B-7 (PDF 71), cita
  `USACE_EM_1110_2_2902.B-7#C76`: fuente SECUNDARIA (el tubo sigue siendo de M 170M, que en
  el ejemplar del repositorio sólo corrobora el orden de las clases). Topes leídos de M 170M:
  la V con pared B sólo hasta 1200 mm (Tabla 5, pág. M 170M-10); la IV es legible sólo en la
  fila de 300 mm (Tabla 4) y por encima queda BLOQUEADA: si es la clase mínima que se pide, el
  punto se detiene con `DatoFaltanteError` (no se salta a la V ni se sube de diámetro). En los
  ensayos del conducto cierran 10 de las 12 corridas sin diseño; quedan 2 bloqueadas por la IV
  (Ø 0.90). El caso G2 original de T-4 pasa de «falta un dato» a «no factible» por F8.CLASE
  (ninguna clase estándar alcanza a Ø 1.65 m).
- **Por qué así:** es la única fuente legible de esos valores en el repositorio; inventar el
  tope de la IV sería rellenar un vacío.
- **Qué haría falta:** un ejemplar legible de AASHTO M 170M o ASTM C76 que confirme III a V y
  dé el tope real de la IV.
- **Dónde vive:** `src/modulos/M8_estructural.py::clases_bloqueadas_para`

## VE3-11 · El hueco 1.0 ≤ H < 2.0 ft del tubo de concreto no se implementa

- **Cerrado por VE-4f (ficha VE4F-01):** el tubo de concreto con 1.0 ft o más y menos de
  2.0 ft hasta la rasante reparte el eje en la franja de la Eq. 4.6.2.10.2-1 a la
  profundidad de diseño de 1.0 ft y lee el B_FLL de la fila «< 2.0 ft». De las tres
  lecturas que esta ficha nombraba, dos se resolvieron con la fuente (E a lo largo del
  tubo; lo que cae sobre el tubo es lo que de cada eje cae en B_c) y la tercera, el largo
  A TRAVÉS del tubo, es el criterio [A] `carga_viva_tubo_concreto_somero`, sin valor.
- **Por qué:** la fuente da el camino (3.6.1.2.6a, Eq. 4.6.2.10.2-1, B_FLL «< 2.0 ft»); lo
  único que calla es una elección, y se dejó como [A] sin valor en vez de inventarla.
- **Qué haría falta:** declarar `carga_viva_tubo_concreto_somero` (ficha VE4F-01).
- **Dónde vive:** `src/modulos/M8_estructural.py::verificar_concreto`

## VE3-12 · El cortante fuera de 5.7.3.4.1 se verifica con el procedimiento general de 5.7.3.4.2 (VE-3.14, bloque 1; H-2 de los ensayos)

- **Cerrado:** fuera del simplificado, el cortante del cabezal se verifica con el procedimiento
  general (β de la ec. 5.7.3.4.2-2 con ε_s de la ec. 5.7.3.4.2-4 y s_xe), con un β por
  combinación. Antes el programa se detenía con «método no evaluable» en cuanto el simplificado
  dejaba de aplicar, y cada peralte intermedio se rechazaba sin que nada fallara. Cinco citas
  verificadas en el PDF. Con el general, los peraltes de la zapata del juego bajan a 0.45–0.50 m
  donde antes salían 0.70–1.00 m (contraste con el motor del revisor).
- **Abierto:** el acero longitudinal que pide el cortante general (`acero_para_cortante_general`,
  ec. 5.7.3.4.2-2 despejada) sube antes que el espesor: sin eso el espesor crecía para bajar εs.
  Es decisión de la sesión y se deja escrita aquí.
- **Qué haría falta:** nada para el cortante; el acero longitudinal queda como decisión documentada de la sesión.
- **Dónde vive:** `src/modulos/M9_cabezal/armado_secciones.py::acero_para_cortante_general`

## VE3-13 · El bucle de la zapata se detiene en el tope y prueba la punta (VE-3.14, bloque 2; H-5, H-6, H-12)

- **Cerrado:** al llegar al tope de `fraccion_ancho_max`·H_c, la zapata se declara NO FACTIBLE y el
  peralte deja de crecer (antes el bucle seguía con 14 intentos idénticos y un peralte de 1.70 m).
  Con el talón al tope prueba crecer la punta, que el dimensionamiento no tocaba (suelo cohesivo,
  excentricidad), y tras fijar el peralte vuelve a probar anchos menores, porque la zapata más
  pesada ya no necesita tanto ancho (H-12). Demuestra que termina. En arcilla blanda (E5) la
  zapata queda no factible con los criterios de archivo, y se dice.
- **Abierto:** la fila NF de los casos en que la zapata no cabe no itera el peralte (H-6); ver
  VE3-17 para las opciones de criterio.
- **VE-6 (ítem 34):** sigue abierto; la razón y lo que haría falta, en la ficha VE6-34.
- **Qué haría falta:** la decisión 9 del dueño (ver VE3-17) para que el talón se calcule con el método exacto, y, si se quiere, iterar el peralte también en las filas NF.
- **Dónde vive:** `src/modulos/M9_cabezal/dimensionamiento.py::dimensionar_zapata_por_estabilidad`

## VE3-14 · La pantalla y el alero se dimensionan por su armado (VE-3.14, bloque 3; H-1)

- **Cerrado:** el espesor de la pantalla (uniforme) crece con el paso de la zapata hasta que su
  armado cumple, con tope físico e < H. La zapata crece lo mismo, con punta y talón fijos, y se
  re-verifican la estabilidad y el armado de la zapata. Origen «dimensionada por armado» y paso de
  memoria 9.3.m. Las trazas de los tres dimensionamientos (`intentos_de_zapata`,
  `intentos_de_peralte`, `intentos_de_pantalla`) salen en el JSON.
- **Decisión de la sesión, que conviene ver:** fuera del simplificado el armado sube primero el
  acero longitudinal que pide el cortante general y sólo después el espesor. Sin eso la pantalla
  de E2 llegaba a 1.20 m; con eso queda en 0.70 m.
- **Abierto:** el alero se dimensiona con la pantalla, no por separado (sus aleros largos con
  esviaje alto —13 m con 45°— quedan sin diseño, H-13). **Cerrado en VE-6** (ficha
  VE6M9-03): el alero se arma por sus secciones y su espesor crece por su armado; su
  estabilidad sigue abierta (T7C-04).
- **Qué haría falta:** dimensionar el alero por separado y decidir su tratamiento con esviaje alto (H-13).
- **Dónde vive:** `src/modulos/M9_cabezal/dimensionamiento.py::dimensionar_peralte_por_armado`

## VE3-15 · Con agua en el plano de empuje el sismo se evalúa (VE-3.14, bloque 4; H-3)

- **Cerrado:** el incremento sísmico se calcula con el peso TOTAL bajo el agua (AASHTO C11.6.5.3,
  criterio nuevo [C] `agua_del_relleno_bajo_sismo`, valor de archivo `se_mueve_con_el_suelo`), y el
  ancho ya no se dimensiona solo con la estática. Un ancho dimensionado sin alguna condición
  evaluada se rotula «dimensionada con la estabilidad evaluable (falta una condición)». El mensaje
  ya no recomienda declarar el drenaje cuando está declarado.
- **Abierto:** con `relleno_muy_abierto` la condición sísmica se detiene salvo que el punto
  declare el empuje con la hidrodinámica (VE7A-05): Westergaard no está en el repositorio de normas.
- **Qué haría falta:** una fuente en el repositorio de normas para la fórmula de Westergaard.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::cargas_del_cabezal`

## VE3-16 · Lo que la app dice de sí misma: alcance declarado y resumen de la CLI (VE-3.14, bloque 5; H-10, H-11)

- **Cerrado:** `ALCANCE_DECLARADO` (`iteracion_ancho_zapata_cabezal`) y el docstring de
  `servicio._fase_9_armado` dicen lo que el código hace desde VE-3.5/3.9 (la zapata SÍ se itera);
  `tests/test_t10_memoria.py` lo fija. La traza de los tres dimensionamientos sale en el JSON. El
  resumen de la CLI atribuye el no cierre a la causa real de cada bloqueo (un método no evaluable
  ya no se llama «criterio sin valor»).
- **Qué haría falta:** nada.
- **Por qué:** es presentación y registro de lo que el código ya hace; la línea base no cambia.
- **Dónde vive:** `src/modelos/hidraulica.py::ALCANCE_DECLARADO`, `cli.py`

## VE3-17 · Opciones 9, 10 y 13 del cabezal como alternativas de criterio; 11 y 14 con su alcance; 12 no se propone (VE-3.14, bloque 6)

- **Qué se difirió:** tres decisiones de criterio del dueño, pendientes (LEEME, «Decisiones pendientes»,
  con la verificación independiente en `verificaciones_del_dueno/cabezal_decisiones_9_14.md`).
  Cada opción queda implementada y medida, y el valor de archivo es el comportamiento de HOY: no
  cambia ningún número hasta que el dueño elija.
  - **9 · `momento_talon_cabezal`:** `'exacto'` (envolvente de Resistencia I con γ máximo y mínimo
    y de los dos casos del Evento Extremo I; reacción lineal de 10.6.5 sin tracción). Peso entero
    como contraste.
  - **10 · `carga_pantalla_cabezal`:** `'cuna_sobre_la_pantalla'` (la cuña llega a la superficie
    real, con talud sobre la corona y sobrecarga, más la cuña sísmica).
  - **13 · `distribucion_incremento_sismico`:** `'distribucion_estatica'` (centroide estático o h/3,
    el mayor; sólo con el muro que cede; con el que no cede se rechaza).
  - **11:** la justificación es AASHTO 11.5.7 y su Tabla 11.5.7-1 (0.55/1.0). La cita del Manual de
    Puentes 2.11.8.5 se retiró: estaba mal leída (es de barreras de sonido).
  - **14:** sólo bajar `margen_zapata_bajo_socavacion_m` (HEC-14 5.1.3 sostiene margen 0). La
    «hoya protegida» no se implementa: no hay fuente que dé esa profundidad.
  - **12 (régimen cedente o no cedente):** no se propone. C11.6.5.4 pone el estribo con aleros
    estructurales entre los que pueden no ceder, y la hoja de ruta §9.2 lo advierte.
- **Efecto medido:** tabla de opciones en `proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CABEZAL.md`
  (y su resumen en el LEEME). Con todas las opciones juntas, el peralte cae al rango del revisor
  (0.40–0.55 m).
- **Por qué:** cada opción cambia un diseño y la elección es del dueño, no de la sesión.
- **Qué haría falta:** la decisión del dueño sobre 9, 10 y 13 (con las condiciones de la verificación),
  y sobre 14.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::CRITERIO_MOMENTO_TALON` (con sus hermanas `CRITERIO_CARGA_PANTALLA` y `CRITERIO_DISTRIBUCION_INCREMENTO`)

## VE3-18 · Decisiones 9 a 14 del dueño sobre el cabezal: valores de archivo y un solo régimen de k_h (VE-3.15)

- **Cerrado (VE-3.15, con las correcciones de su revisión):** talón por el método exacto (9),
  cuña sobre la pantalla (10; una cuña sin máximo ya no detiene la estabilidad externa, sólo
  el armado de la pantalla), fila de muros de 11.5.7 (11), un solo régimen de k_h con la
  guardia de `M9.factor_muro` (12; la estabilidad externa sigue con el activo), el brazo del
  incremento derivado del régimen (13: resultante no bajo h/2 con el muro que no cede, el
  mayor del centroide estático y H/3 con el que cede) y margen cero bajo la hoya sin proteger
  (14; el desplante cita AASHTO 10.6.1.2 y HEC-14 5.1.3, y 12.6.5 es el techo de la ventana).
  La §9.4 de la hoja de ruta (puntos 5 y 9) la corrigió el dueño, con su nota «Corregido».
- **Abierto:** (1) con el PGA del sitio (0.50 g) y los valores de archivo ningún cabezal del
  juego cierra el sismo; el dentellón de corte no lo resuelve (informe `dentellon_norma.md`);
  la causa y lo que se decidió, en la ficha VE3-20; (2) el ancho final puede superar el tope cuando la pantalla crece
  después (A-01 salida, 4.852 frente a 4.825 m); (3) el φ de la decisión 11 se revisa con el
  EMS real (C11.5.7).
- **Por qué:** son elecciones [A] y [C] dentro de sus ventanas, verificadas cita por cita
  (`proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/`).
- **Qué haría falta:** la salida del sismo del cabezal; acotar el ancho final al tope; el EMS.
- **Dónde vive:** `src/modulos/M9_cabezal/empujes.py::factor_muro`


## VE3-19 · Los máximos anuales repetidos se avisan, sin umbral (H1 de la validación hidrológica con casos reales)

- **Cerrado (`docs/validacion_hidrologica.md`):** el aviso de consistencia de la serie (paso
  1b.3c, VE-2 (e)) suma un renglón con los máximos anuales que aparecen en más de un año y sus
  años —en Cañaveral (UNTumbes, Tabla 24, p. 61): 129.0 mm en 1989 y 2002; 63.0 mm en 1996 y
  2001— y dice que el programa no distingue una coincidencia de un año copiado y que el
  proyectista tiene que contrastar esos años con el registro mensual o diario de origen. Sólo
  aparece cuando hay repetidos. No detiene, no quita ningún año, no juzga y no lleva número de
  corte (`TOL_ABS_MISMO_MAXIMO_ANUAL_MM` es sólo representación). Dos etiquetas de año iguales
  siguen siendo `DatoInvalidoError` al cargar.
- **Por qué así:** el dossier de la verificación independiente
  (`proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/hidrologia/hidrologia_casos_reales.md`,
  §3.4) halló en UNTumbes dos años copiados mes a mes de otros dos. Con un máximo por año la copia
  no es demostrable y dos máximos iguales son normales (8 de las 10 series reales del dossier;
  `tests/test_ve3_19_maximos_repetidos.py` fija el recuento). Ninguna excepción encaja,
  deduplicar sería corregir una entrada que el módulo sólo valida, y no se sabe cuál es la copia
  (quitar 2001 y 2002 sube la LN2 a 70 años un 5.6 %).
- **Abierto: la hoja de ruta no lo recoge.** La Fase 1-bis de la hoja de ruta vigente no dice
  nada de valores repetidos; es comportamiento nuevo del aviso sin umbral y tiene que entrar
  junto al de VE-2 (e). No se edita aquí (otra tarea la corrige en paralelo): mientras no lo
  recoja, quien lea sólo la hoja de ruta no sabrá que la memoria lista esos años.
- **Qué haría falta:** recogerlo en la hoja de ruta; si el contrato admitiera la serie MENSUAL,
  una fila idéntica mes a mes a la de otro año sí sería `DatoInvalidoError`, con el par de años.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::maximos_anuales_repetidos` (el renglón, en
  `_paso_consistencia`)

## VE3-20 · El sismo del cabezal con los valores de archivo no cierra: causa, decisión y defecto de la §9.2 de la hoja de ruta

- **Qué se difirió:** la reducción de k_h a 0.5·k_h0 como valor de archivo. Sigue
  «sin_reduccion» y se declara por obra junto con el armado «cedente» (decisión 12), como hace
  el juego de la validación integral; con esas dos declaraciones y el relleno drenado los
  cuatro puntos del juego cumplen E1 a E3 sísmicos.
- **Por qué:** la revisión independiente
  (`proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/sismo_cabezal_que_se_pasa.md`)
  no halló error aritmético: lo que no cierra es el relleno lleno de agua bajo sismo
  (`drenaje_trasdos` de archivo) sobre k_h = k_h0, que por definición es desplazamiento nulo.
  La exención de AASHTO 11.5.4.2 no puede invocarse: A_s = 0.50 g y la zona sísmica (Zona 4
  estimada, S_D1 ≈ 0.63 a 0.72, con una lectura de S1 que el EMS tiene que confirmar) no es
  dato del proyecto. Aceptar el desplazamiento es del
  Propietario («acceptable to the Owner»), y el programa no lo asume.
- **Cerrado (dueño, 2026-11-20), el defecto de la hoja de ruta:** la §9.2 decía «No asumirlo
  en un cabezal empotrado en terraplén» y presentaba «sin reducción» como el lado seguro sin
  decir que k_h0 es la aceleración con desplazamiento nulo, ni que con el PGA del sitio ningún
  cabezal del juego lo cumple. Hoy dice «No se asume de archivo: se declara por obra», con su
  nota «Corregido (`VE3-20`, dueño, 2026-11-20)» verificada contra AASHTO 11.6.5.2.1,
  11.6.5.2.2, 11.5.4.2 y C11.6.5.4. El docstring de `M9.factor_muro` y la ficha de
  `factor_muro_eleccion`, que citaban la frase vieja, se ajustaron.
- **Qué haría falta:** el EMS real (φ de la fundación, clase de
  sitio, licuefacción, que 11.5.4.2 pone como condición previa); y, para cada obra, el detalle
  que permite el movimiento (junta en los aleros y en la unión con el conducto) con la
  aceptación escrita del Propietario.
- **Dónde vive:** `src/modulos/M9_cabezal/empujes.py::factor_muro`

## VE3-21 · El trasdós drenado es el valor de archivo (VE-3.16, decisión del dueño del 2026-11-18)

- **Cerrado:** `drenaje_trasdos` pasa de «sin_drenaje» a «drenado» de archivo (AASHTO 11.6.6,
  «shall be drained»). Adoptarlo COMPROMETE el filtro y los lloraderos en planos y su
  mantenimiento (C11.6.6). Con el relleno drenado el agua bajo sismo es la del freático del
  punto, el nivel medio que C11.6.5.3 recomienda.
- **Cerrado (VE-4e, 2026-11-20), lo diferido:** con «sin_drenaje» el sismo iba con el relleno
  lleno. Hoy el agua es POR CONDICIÓN en `cargas_del_cabezal`: la estática llena el relleno
  retenido (11.6.6) y la sísmica va con el nivel medio en el tiempo (cita nueva
  `AASHTO_LRFD_9.C11.6.5.3#NIVEL_MEDIO`, pág. impresa 11-31, PDF 1500, «should»). WA, el suelo
  sumergido, el peso del relleno sobre el talón y el incremento salen del nivel de SU condición.
- **Por qué es [A] sin valor:** la fuente no dice cuál es el nivel medio de un relleno que no
  drena. Lo declara el proyectista con el EMS en `nivel_agua_relleno_sin_drenaje_bajo_sismo`
  (`superficie_del_relleno`, lo de antes de VE-4e, o `freatico_natural`); sin declararlo la
  condición sísmica se detiene (`CriterioPendienteError`). Con «drenado» no se lee y ningún
  número cambia (`tests/test_ve4e_agua_por_condicion.py`; variantes `sin_drenaje_declarado` y
  `sin_drenaje_sismo_en_el_freatico` de la validación integral).
- **Abierto contra la hoja de ruta:** su nota «Corregido (`VE3-21`…)» de la Fase 9 dice aún que,
  declarado `sin_drenaje`, el sismo va con el relleno lleno «(diferido en la ficha VE3-21)».
  Mientras no se corrija, quien lea sólo la hoja creerá que es así siempre.
- **Qué haría falta:** el nivel medio como cota declarada por punto (dato del EMS entre el
  freático y la superficie), si una obra lo tuviera medido.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::cargas_del_cabezal`

## VE4A-01 · E4 y E5 con el FS declarado del EMS: tres lecturas del proyecto y una fila sin valor (VE-4a, decisión del dueño del 2026-11-20)

- **Cerrado:** el dato `estabilidad_global_declarada` (por punto y por cabezal: `E4` y/o `E5`,
  cada uno con `estatico` y `sismico`, y la traza `documento`, `fecha`, `metodo` y,
  opcional, `programa`) entra por `--datos-externos` como `suelo_fundacion`, fuera de
  `CLAVES_EXTERNAS` porque ninguna etapa lo exige, y es la única clave del cabezal que no
  admite `globales`. El ensamble emite cuatro filas por cabezal y condición
  (`E4-LRFD`, `E4-ASD`, `E5-LRFD`, `E5-ASD`) en `EstabilidadDelCabezal.globales`, aparte de
  `verificaciones`: el dimensionamiento de la zapata itera sobre E1 a E3 y el ancho no mueve
  un FS que el programa no calcula. `integrar_estabilidad` las suma a las del cabezal, que es
  por donde el informe cuenta incumplidas e indicadores.
- **Abierto (lecturas del proyecto, declaradas en la `Interpretacion` de la cita
  `AASHTO_LRFD_9.C11.6.3.7#FS`):** (1) el puente entre el FS del programa de taludes y el
  marco LRFD es el comentario C11.6.3.7 («essentially the inverse of the FS that should be
  targeted»), y el proyecto toma **1/φ exacto** (1.333 y 1.538), no las cifras redondeadas
  del comentario (1.3 y 1.5), que quedan por debajo; (2) la misma lectura se extiende al φ =
  0.9 del evento extremo (11.5.8), que el comentario no cubre; (3) la combinación de cargas
  con que el analista obtuvo el FS (Resistencia I en la 9a edición; Servicio I en el
  2.4.5.3.1 del Manual de Puentes, que no da cifra de φ) la sostiene su documento, no el
  programa. Y `fila_phi_estabilidad_global` no tiene valor de archivo: sin declararla, la
  fila LRFD estática decide sólo si las dos filas dan lo mismo; entre 1.333 y 1.538 **espera
  el criterio** (VE-5 fixve4: `Bloqueo`; razón en
  `M9._fila_global_declarada` y `EstabilidadDelCabezal.pendientes_por_criterio`; la A6, sin
  cambio). 1/φ exacto se conserva (FS 1.50 con φ 0.65 no cumple).
  **Decisión pendiente de Fable**.
- **Qué haría falta:** que el dueño confirme las tres lecturas o elija otra (por ejemplo,
  las cifras redondeadas del comentario); declarar `fila_phi_estabilidad_global` con el EMS
  real; y corregir la hoja de ruta, cuya §9.3 y la nota de Fase 9 aún dicen que E4
  y E5 «se imprimen como diferidas al expediente con el EMS» sin el camino del FS declarado
  (texto en informe VE-4a). `metodo_estabilidad_global` y las funciones
  sueltas `verificar_estabilidad_global` / `verificar_talud` quedan como estaban: el método
  viaja ahora en la traza del dato declarado.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::validar_estabilidad_global_declarada`

## VE5-M6-01 · La poza de enrocado de HEC-14 Sec. 10.1 entra donde el apron no llega (VE-4g, ítem 2 del censo)

- **Cerrado:** `M6.poza_de_enrocado_hec14` sigue el procedimiento del núm. 10.1.5 (Ec. 10.1
  con Co de la 10.2 o la 10.3; Ls, LA y LB de la Sec. 10.1; abocinado 3:1 y taludes 2:1 de la
  Figura 10.2, leída por imagen; tirante crítico de salida por la Ec. 7.14; espesores 2·D50 y
  3·D50 del núm. 10.1.4) contra los cuatro ejemplos resueltos (págs. impresas 10-6 a 10-16).
  La Tabla 1.1 la da sin límite de alto y para marcos, que la Ec. (10.4) no cubre: la Fase 6
  la evalúa cuando el apron falla por **marco** o por **alto de más de 60 in**
  (`_remite_a_la_poza`), la reviste con la piedra de Laushey y la regla de la protección forma
  la envolvente con ella (`_regla_con_la_poza`). Con la piedra que da hs/D50 < 2 la poza se
  dimensiona con la de hs/D50 = 2 exacto y se reviste con la mayor (cita
  `HEC14.10.1#MAYOR_REVISTE`); bajo D50/ye = 0.1 la piedra se sube a 0.1·ye; si la velocidad
  de salida supera la admisible (Tabla N° 11), el apron se alarga con el mismo abocinado
  hasta Vc = Vallow, como el ejemplo de la fuente. Criterio [A] nuevo,
  `relacion_co_poza_enrocado_hec14` (envolvente, el archivo; mejor ajuste, barrible). El
  rótulo del apron ya no dice «no implementa»: remite a la poza.
- **Abierto:** (1) **varios barriles**: los ensayos de la poza, del apron y del Cap. 5 son
  de un conducto; ninguna fuente del repositorio de normas da la descarga conjunta. Sigue
  como aviso (la poza lo dice con «barriles»). (2) **Froude ≥ 3**: la Tabla 1.1 limita la
  poza a Fr < 3; por encima, los disipadores de los Caps. 7 a 9, fuera de alcance (D). (3)
  La hoya que no llega a 2·D50 ni con la piedra de 0.1·ye no se extrapola. (4) Vallow es la
  de la Tabla N° 11 (criterio de estabilidad); la fuente admite la normal del cauce si es
  mayor, que el programa no tiene: lado conservador, declarado en el umbral del paso 6.6p.
  (5) **IP fuera de 5–16** en la hoya cohesiva (Ec. 5.2 y 5.3): la fuente limita sus
  ecuaciones y no da otra; sigue como aviso.
- **Qué haría falta:** para (1), una fuente que dé la protección de varios barriles (o un
  modelo físico); para (2), los disipadores de los Caps. 7–9, que el dueño dejó fuera.
- **Dónde vive:** `src/modulos/M6_proteccion.py::poza_de_enrocado_hec14`

## VE5-M6-02 · La Figura 10.3 de HEC-14 está digitalizada: el TW sobre 1.0·D y el paso 5 de la poza (VE-5, lote m6)

- **Cerrado:** la curva de diseño de la Figura 10.3 (pág. impresa 10-4) leída por imagen
  (render 4x, retícula log-log localizada por sus líneas, curva trazada columna a columna),
  con los cuatro puntos que la fuente imprime en sus ejemplos tal cual
  (`constantes_normativas.HEC14_FIGURA_10_3`; método en la nota de la cita
  `HEC14.10.1.3#FIGURA_10_3`; tolerancia 0.015 en VL/Vo). Con ella y la Ec. (10.6) de la Sec.
  10.3: (a) el apron con el TW sobre 1.0·D de un tubo de hasta 60 in, que hasta aquí salía
  «no evaluable», se dimensiona como la Sec. 10.2 manda (`M6.proteccion_tw_alto_hec14`:
  longitud hasta VL = Vallow, piedra de la Ec. 10.6 con Vo, espesor 2·D50) y entra a la
  envolvente; (b) el paso 5 de la poza con TW/yo > 0.75 da la extensión de la protección
  aguas abajo y la piedra en la salida de la poza. Oráculos: 41.0 m y 135 ft de los dos
  ejemplos del marco.
- **Abierto:** (1) el espesor de la protección con el TW alto, que la Sec. 10.3 no da, es
  2·D50: **lectura del proyecto** sobre el piso que HEC-14 pone al enrocado de la poza y del
  apron. (2) Sin el terreno del receptor no hay Vallow ni longitud: aviso, y rige Laushey. (3)
  Más allá de L/De = 60 la figura no da nada y no se extrapola. (4) El ancho de esa
  protección no lo da la fuente para este caso.
- **Qué haría falta:** HEC-11 (Brown y Clyde, 1989), al que la fuente remite el detalle del
  enrocado y el filtro, que no está en el repositorio de normas.
- **Dónde vive:** `src/modulos/M6_proteccion.py::proteccion_tw_alto_hec14`

## VE5-M6-03 · La salida colgada se cierra con la caída recta de HEC-14 Cap. 11 (decisión del dueño: dentro del alcance)

- **Cerrado:** `M6.caida_recta_hec14` (núm. 11.1.3, Ec. 11.5 a 11.16 leídas por imagen;
  bloques, umbral, muros y aproximación revestida) contra los dos ejemplos resueltos (págs.
  impresas 11-9 a 11-11). La Fase 6 la evalúa en `socavacion_salida` cuando **gobierna la
  pendiente máxima** del conducto (el desnivel queda en la salida; ficha T6-02, cuyo «qué
  haría falta» cierra) o cuando la caída **pasa la Tabla 5.2** (Hd > 4). Sus límites
  (llegada supercrítica, lámina no aireada, Wo ≤ 1.5·yc, |ho| ≥ 15 ft, |ho|/yc fuera de
  1–15) salen como aviso. El límite de 15 ft se toma como 4.572 m, no 4.6: la cifra en las
  unidades de los ensayos, como los 60 in del apron (`HEC14_CAIDA_HO_MAX_M`).
- **Decisión Fable (Wo y yc):** la longitud de cresta Wo es el ancho de los barriles en la
  salida (n·B o n·D, sin tabiques). En el **marco** el yc sale de la Ec. (11.5) con q =
  Q/(n·B), que es lo que la fuente escribe para la sección rectangular (pág. 11-6, cita
  `HEC14.11.1.3#EC_11_5`), y ahí n·B es el lado conservador. En el **tubo** n·D es solo la
  longitud de cresta de la condición 3: el yc es el de la Ec. (11.6) sobre la sección
  circular, por barril (el `y_critico` de M4, resuelto con Q_celda; cita
  `HEC14.11.1.3#EC_11_6`), porque q = Q/(n·D) da un yc menor y un estanque más corto, del
  lado inseguro (Q = 1 m³/s, D = 1.2 m: 0.414 contra 0.542 m). Queda como `Interpretacion`
  declarada de la cita `HEC14.11.1.3#ANCHO_APROXIMACION`, no como [A]; el paso 6.15 dice qué
  ecuación dio el yc.
- **Abierto:** (1) con varios barriles, el ancho real de la cresta incluye los tabiques. (2) La caja de
  entrada (Sec. 11.2) no se implementa: es para la entrada, no para la salida colgada. (3)
  La rejilla de la llegada supercrítica (núm. 11.1.2) no se implementa. (4) La socavación y
  el desplante del cabezal siguen saliendo de la hoya o del dato declarado; la estructura de
  caída no los sustituye. Los Caps. 7–9 son fuera de alcance (D).
- **Qué haría falta:** con varios barriles, el ancho real de la cresta con los tabiques
  (el plano de la salida).
- **Dónde vive:** `src/modulos/M6_proteccion.py::caida_recta_hec14`

## VE5-M6-04 · Zampeado, uña y dentellón (ítem 30) y filtro granular (ítem 31) siguen pendientes [C]

- **Qué se difirió:** el ítem 30 (zampeado, uña y dentellón de la protección; ficha T8-03)
  y el ítem 31 (filtro granular bajo el enrocado; ficha T8-05).
- **Por qué:** los dos dependen de documentos que **no están** en el repositorio de normas
  (`NORMAS_DIR`, revisado el 2026-11-20): HEC-11 (Brown y Clyde, 1989), al que HEC-14 remite
  el detalle del enrocado y el filtro (núm. 10.1.4, Sec. 10.2), y un plano tipo del dueño
  para el zampeado y el dentellón (las Láminas 02, 02-A y 03 del Manual los traen como letras
  o «VARIABLE»). La Figura 10.1 de HEC-14 dibuja el muro de corte de la poza sin dimensión.
- **Qué haría falta:** HEC-11 en `NORMAS_DIR/normas/` para el filtro granular; el plano tipo
  del dueño o una regla [A] declarada para el zampeado y el dentellón.
- **Dónde vive:** `src/modulos/M6_proteccion.py::requisito_de_filtro`

## VE5-MET-01 · Metrados referidos al EG-2013 y cuadro de compatibilidad rasante-alcantarilla (Fase 11, entregables 8 y 9; ítem 8 del censo)

- **Cerrado:** `M12_metrados` mide la geometría FINAL de las fases anteriores, sin rediseñar,
  con la regla de MEDICIÓN de cada Sección del EG-2013 (18 citas): conducto por metro lineal
  entre caras exteriores de cabezales y siguiendo la pendiente (506.14, 507.12, 508.11; el
  marco en m³, 503.12); excavación en posición original con caras verticales (501.09; zanja
  de 506.06, 507.05 y 508.04 bajo la cama de 506.07 y 508.05; zapatas con el sobreancho de
  501.04; partida 501.C/D por el freático, 501.01); concreto con el vano descontado y la clase
  de la Tabla 503-07 por el f'c (503.12); acero por la Tabla 504-01 (504.10); losa, dentellón,
  enrocado (sin partida: [A]) y geotextil (511.13). Sin desperdicio ni esponjamiento (503.13,
  504.11). Lo que no se mide es un `Bloqueo` de `servicio.FASE_METRADOS` y los demás rubros
  siguen. Tres criterios: `sobreancho_excavacion_estructuras_m` [A] opcional (0–0.45 m),
  `incremento_acero_por_despiece` y `clase_concreto_losa_entrega`, [A] sin valor.
- **Cerrado por VE-6:** el NF en M12 es de expediente y detiene sólo el rubro de excavación,
  y el signo de dos criterios de metrado queda censado (ficha VE6-01).
- **Decisión de Fable (VE-6, 2026-11-20):** los dos sin valor se quedan así. 504.10 mide las
  longitudes del despiece (504.03) y ninguna fuente del repositorio da una fracción de
  anclajes y empalmes; la Tabla 503-07 da clases, no usos, y heredar la del cabezal fijaría
  sin diseño si la losa es simple o reforzada.
- **Abierto:** el relleno para estructuras (502.A), la cama y el emboquillado no se metran, y desde
  VE-7 lo dicen como bloqueos «no medido» (ficha VE7B-08); el acero del marco (ficha VE7B-12); la zanja de varios tubos y el
  enrocado de varios barriles, no evaluables. La hoja de ruta (Fase 11, ítem 8) cita una
  «Sección 500» que no existe y omite 501, 511 y la falta de partida del enrocado.
- **Qué haría falta:** para el acero, que el programa calcule ganchos, desarrollo y empalmes
  (E.060 Cap. 12 o AASHTO 5.10.8, por transcribir) o el despiece declarado; para la losa, la
  especificación del zampeado o su diseño (ficha T8-03); el relleno, la sección del plano.
- **Dónde vive:** `src/modulos/M12_metrados.py::renglones_concreto_cabezales`

## VE4F-01 · La carga viva con relleno somero: la franja de 4.6.2.10.2, la cobertura mínima y un [A] sin valor (VE-4f)

- **Cerrado:** por debajo del dominio de la rueda distribuida de AASHTO LRFD 3.6.1.2.6a la
  Fase 8 ya no se detiene entera. (1) El MARCO con menos de 2.0 ft reparte un eje en la
  franja de 4.6.2.10.2 (12.11.2.1 y 4.6.2.10.1): E = 96 + 1.44 S, E_span = L_T + LLDF H,
  un carril con su m, con la profundidad que tiene; contrastado con MnDOT, LRFD Bridge
  Design Manual §12.6 (cajón de 16 ft bajo 1 ft: E = 119.04 in, E_span = 23.8 in, 2.52 y
  1.97 ksf), sin la carga de carril que MnDOT suma y la 9.ª ed. no manda. (2) El TUBO DE
  CONCRETO con 1.0 a 2.0 ft se diseña «for a depth of 1.0 ft» (IM con D_E = 1.0 ft, o la
  cubierta si es menor), con E a lo largo del tubo, lo que de cada eje cae sobre B_c como
  W_L y el B_FLL de la fila «< 2.0 ft»; no hay contraste ACPA (la franja ya reparte a lo
  largo del tubo). (3) Un conducto REDONDO bajo el dominio se juzga antes contra la
  cobertura mínima de la Tabla 12.6.6.3-1 (F8.COBERTURA, medida hasta la rasante porque la
  fuente cuenta la base): sin ella INCUMPLE y el escalón se rechaza, no es «no evaluable».
- **Abierto:** el largo del área cargada A TRAVÉS del tubo de concreto somero no lo fija la
  fuente: `carga_viva_tubo_concreto_somero` [A] tiene desde VE-7 valor de archivo L_T (ficha
  VE7B-05); L_T + LLDF·1.0 ft queda en la ventana. Sigue sin método (`MetodoNoEvaluableError`): el tubo de
  concreto bajo pavimento rígido entre 9 y 12 in («more comprehensive methods») y el
  flexible con 1.0 ft o menos que cumple la cobertura (sólo justo en 1.0 ft).
- **Qué haría falta:** los métodos completos para el tubo con menos de 1.0 ft. Con el pórtico (ficha T5-07) la presión de la franja se
  aplica al marco como carga concentrada sobre la losa.
- **Dónde vive:** `src/modulos/M8_estructural.py::_carga_viva_en_la_franja`
# Parte LXI — Lo que VE-5 (lote M9) dejó escrito: el cabezal

## VE5M9-01 · El muro que no cede se calcula: reposo en la estática, 1.0·k_h0 y h/2 bajo sismo (VE-5, ficha T7B-14)

- **Cerrado:** `regimen_cabezal` = `no_cedente` ya no detiene el ensamble.
  `M9.cargas_del_cabezal`: (1) estática con el empuje en reposo de 3.11.5.2-1 sobre el
  mismo diagrama (suelo sumergido bajo el agua), todo horizontal y con el γ_p de la fila
  «En reposo» (1.35/0.90); K0 es de terreno horizontal, de modo que si el activo con la
  superficie real da más componente horizontal rige el activo —la regla del armado,
  ficha T7C-02—; (2) sísmica con k_h = 1.0·k_h0 aunque `factor_muro_eleccion` declare la
  reducción («shall be increased to 1.0kh0»), la distribución estática del incremento
  rechazada y la resultante del estático más el sísmico no bajo h/2 (C11.6.5.4).
  `cargas_en_reposo` es idempotente sobre ese ensamble, y el armado avisa si se declara
  del muro que cede con el cabezal que no cede. Dorados a mano:
  `tests/test_ve5_m9_no_cedente.py`.
- **Abierto (decisión pendiente de Fable):** cómo se suma el reposo al empuje
  pseudoestático, que es de muro que cede; la fuente no lo dice. Lo declara
  `empuje_sismico_muro_que_no_cede` [A]: `reposo_mas_incremento` de archivo (lado
  seguro: más que Mononobe-Okabe, como dice C11.6.5.4) y `mayor_de_reposo_y_total` en la
  ventana. El agente no pudo consultar a Fable y tomó la conservadora.
- **Qué haría falta:** la solución de muro rígido de Wood (1973) o un análisis numérico
  aprobado por el Propietario (11.6.5.4), que no están en el repositorio de normas.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::empuje_sismico_muro_que_no_cede`

## VE5M9-02 · La cuña de tanteo sísmica donde M-O no es aceptable y sobre el trasdós inclinado (VE-5, ficha T7B-06)

- **Cerrado:** (1) la cuña de Coulomb/Culmann va sobre un plano de empuje inclinado β
  (zapata sin talón), con la normal girada β; con el talud uniforme reproduce Coulomb
  (3.11.5.3-1) y Mononobe-Okabe (A11.3.1-1) con β a cinco decimales. Hasta VE-5 se
  detenía pidiendo la fórmula cerrada. (2) Con la fórmula cerrada de las reglas
  `talud_quebrado_2h` o `talud_del_terraplen` fuera del dominio de M-O (φ < i + ψ), el
  incremento sísmico sale de la cuña de tanteo pseudoestática con la superficie real
  (C11.6.5.3: «may also be used for situations when the M–O Method is not suitable»):
  P_AE − P_A de la MISMA cuña, y el estático sigue con la fórmula de la regla
  (`METODO_INCREMENTO_CUNA`); con la pendiente declarada, la cuña con ese talud sin
  quiebre. (3) La cuña sin máximo interior ya no se describe como un defecto del método:
  con la superficie que se quiebra en la plataforma sólo pasa con ψ ≥ φ, y el mensaje
  dice que es el relleno el que no es estable bajo ese k_h.
- **Por qué no más:** la fuente da el GLE como método general y la cuña como el de mano;
  el GLE no se calcula a mano.
- **Qué haría falta (C):** el GLE de A11.3.3 necesita un programa de estabilidad de
  taludes; la puerta del P_AE declarado por punto se abrió en VE7A-05. La cuña sobre la CARA de la
  pantalla (`carga_pantalla_cabezal` = `cuna_sobre_la_pantalla`) sigue vertical: con
  talón el trasdós de la regla es vertical, y un β declarado con talón no la inclina.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::cuna_de_tanteo`

## VE5M9-03 · Capacidad portante: la RC_BC de AASHTO sustituye a Meyerhof, forma y profundidad declarables, y la admisible de corredor con consumidor (VE-5, ficha T7B-04)

- **Cerrado:** (1) las Tablas 10.6.3.1.2c-1 y -2 de AASHTO 9.ª ed. transcritas enteras
  (`constantes_normativas.RCBC_EN_TALUD_T10_6_3_1_2C_1` y `RCBC_JUNTO_AL_TALUD_…`), leídas
  con un analizador del texto del PDF y comprobadas celda a celda por un test `pdf`;
  `M9.coeficiente_rcbc` interpola en φ, B/H, b/B, β y N_s, toma la fila de 10° bajo 10°
  (lado seguro) y, fuera de la tabla, se detiene («analysis limite», C10.6.3.1.2c). La
  zapata en talud es RC_BC·(c·N_cm + 0.5·γ·B'·N_γm) sin empotramiento, con la geometría
  de `talud_delante_del_cabezal` [S]. `N_cq_N_gammaq_meyerhof` (abacos de Meyerhof del
  Manual de Puentes) se **retiró**, y con él el `H_s = 0` que se le pasaba. (2) Forma
  (Tabla 10.6.3.1.2a-3, con L = longitud del cabezal) y profundidad (ec.
  10.6.3.1.2a-10, ≤ 1.4) por `factores_forma_profundidad_portante` [A]; el archivo sigue
  en la zapata corrida sin profundidad, de modo que ningún dorado se mueve. (3)
  `capacidad_portante_adm` **no se retiró**: el Anexo A de la hoja de ruta la nombra; se le
  dio consumidor (`M9.suelo_de_fundacion`), como el `q_adm_kpa` de corredor.
- **Por qué:** la Fase 9 rige con AASHTO LRFD 9.ª ed. y su 10.6.3.1.2c son tablas, no
  figuras; la §9.3 de la hoja de ruta sigue nombrando la ecuación del Manual de Puentes
  2.8.1.3.1.2c (Meyerhof): **la hoja de ruta sigue mal** mientras no se corrija.
- **Qué haría falta:** corregir la §9.3 de la hoja de ruta (la geometría del talud por punto
  se cerró en VE7A-06; `terreno_delante_del_cabezal` sigue de corredor).
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_base.py::coeficiente_rcbc`
## VE6M9-01 · El cabezal ciclópeo se verifica bajo sismo (C8) y su zapata como voladizo de concreto simple (C7) (VE-6, ítem 10; T7C-09 (2)(3))

- **Cerrado:** `M9.verificar_cabezal_ciclopeo` suma dos filas. **C7** (punta y talón que
  vuelan más que la mitad del peralte, E.060 22.10.2.2): max[(M_u/S)/(φ·0,42√f'c),
  V_u/(φ·0,11√f'c·b·h)] ≤ 1, φ = 0,5, f'c ≤ 10 MPa, h − 50 mm (22.4.8), con las
  solicitaciones del armado (presión lineal, subpresión) y las dos combinaciones de E.060
  9.2.5 por cada empuje del régimen; decide. **C8** (arranque y media altura): e ≤ t/6 con el
  Evento Extremo I sin factorar. Dorados a mano: `tests/test_ve5_m9_ciclopeo.py`.
- **Decisiones:** (1) los dos casos de 11.6.5.1 (MP 2.8.1.1.14.1: «el resultado más
  conservador … para el diseño del muro»), los de E2; (2) inercia en el centroide del
  trapecio; (3) diagrama estático del plano virtual de C2/C3; (4) con `no_cedente_k0`,
  1.0·k_h0 y resultante total no bajo h/2; (5) cortante de C7 en la cara; (6) sin presión
  en ninguna combinación, `MetodoNoEvaluableError`.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: la sobrecarga de C8 va con γ_EQ
  (`gamma_EQ`), como E2; el arranque bajo sismo decide con cualquier criterio
  (`criterio_traccion_cabezal_ciclopeo`); C7 avisa las combinaciones de E.060 descartadas
  por sacar la resultante de la base y decide con las demás; C8 cita `MP.2.8.1.1.14.1#EXC`
  (el numeral de los dos casos: su texto no tiene cita propia, vive en `P_SEIS_TEXTO`).
- **Abierto:** (a) no procede mientras k_v = 0; con k_v ≠ 0, C8 debe afectar W con
  (1 − k_v); (b) a media altura, con `traccion_admisible_e060`, C8 informa; (c) la cita
  `E060.22.10.2.2#VOLADIZO` existe desde VE-7 y se firmó en A11 (ficha VE7C-01), y es la
  cita principal de C7 (cerrado); (d) C7 no se evalúa bajo sismo (E.060 9.2.3 no
  combina CS con CE): la punta bajo Evento Extremo I queda cubierta sólo por E2.
- **Qué haría falta:** nada para (c): cerrado en A11 con el PDF de E.060.
- **Dónde vive:** `src/modulos/M9_cabezal/ciclopeo.py::_verificar_cuerpo_bajo_sismo`

## VE6M9-02 · Las cuantías mínimas de muro de E.060 14.3.1 pasan a criterio [N→] (VE-6, ítem 29; T7C-10)

- **Cerrado:** la constante [N] `CUANTIA_MIN_MURO` se retiró de `constantes_normativas` y
  su valor (0,0020 horizontal, 0,0015 vertical) es el criterio [N→]
  `cuantia_minima_muro_e060` (expediente, sin ventana), por el argumento que movió el 0,30 m
  de 22.7.4 en el cierre de T-7c. `M9.cuantia_minima` lo lee y valida;
  `M9.DIRECCIONES_CUANTIA_MURO` sustituye a las claves de la constante en `servicio`; la fila
  R1/R2 sin cortante alto se atribuye al criterio (`criterio_aplicado`, antes None). El
  manifiesto, `variables_entrada` y los censos (169 criterios) se resincronizaron.
- **Por qué:** E.060 es norma de edificaciones; la excepción de la §0.2 de la hoja de ruta
  cubre la durabilidad, no los mínimos estructurales.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: el número de la norma queda en
  `constantes_normativas.CUANTIA_MIN_MURO_E060_14_3_1` [N] (tabla y elección separadas) y
  el criterio lo toma de ahí; `M9.cuantia_minima` rechaza un valor por debajo (bajaría de
  la norma con etiqueta [N→]); `fuente` cita 14.8.1/14.8.2 y `reemplazado_por` dice «el
  retiro del contraste de E.060 si el proyecto adopta sólo AASHTO 5.10.6, o el ejercicio
  declarado de 14.8.2».
- **Qué haría falta:** nada.
- **Dónde vive:** `src/criterios/cabezal_calculo.py::cuantia_minima_muro_e060`

## VE6M9-03 · El alero se arma por sus propias secciones y su espesor se dimensiona por su armado (VE-6, ítem 9; VE3-14 H-13, T7B-08 (3), T7C-04)

- **Cerrado:** cada franja vertical del alero es el fuste de un muro en voladizo que baja
  con el talud (`M9.entorno_de_la_seccion_del_alero`: Δ = (h0 − H_f)·f, su espesor, su
  zapata toda como talón, el relleno Δ más abajo y subiendo hasta la plataforma). Se arma
  en dos secciones, cada una con `solicitaciones_de_resistencia` de su franja (AASHTO 5:
  cada sección con sus cargas): el arranque (tramo 0–L/2) y la mitad (tramo L/2–L, clave
  `alero_mitad`); sin caída, sólo el arranque. El espesor del alero ya no copia el de la
  pantalla: parte del de la regla y crece con el paso de `dimensionamiento_zapata_cabezal`
  hasta que sus dos secciones cumplen (`M9._dimensionar_aleros`, paso 9.3.al, origen
  «dimensionada por armado»); la pantalla crece sólo por las suyas. Los metrados reparten
  cada fila en su tramo (L/2). Dorados: `tests/test_ve6_m9_alero.py`.
- **Decisiones de la sesión** (Fable no se pudo consultar; lado seguro): (1) la franja
  apoya en la zapata entera como talón y el plano virtual queda en su extremo (con la cuña
  sobre la cara, la de archivo, no cambia); (2) detrás de la franja el relleno sube con el
  talud entero (normal al alero sube menos); (3) la sobrecarga es la del cabezal; (4) dos
  tramos, porque la altura baja monótona y cada tramo se arma con su sección más alta.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: el ancho de la sección de la mitad es la
  altura de su franja; el armado avisa «alero armado, no verificado como muro (E1–E3 de
  11.6), ficha T7C-04».
- **Abierto:** la zapata del alero y su estabilidad (T7C-04): CERRADO en VE-7 (ficha
  VE7-01), en cinco franjas de su longitud.
- **Qué haría falta:** lo que dice VE7-01.
- **Dónde vive:** `src/modulos/M9_cabezal/armado.py::entorno_de_la_seccion_del_alero`

## VE6M9-04 · La orientación del muro y la distancia al borde de calzada, por punto (VE-6, ítem 28; T7B-11)

- **Cerrado:** dos claves de `--datos-externos`, por punto o en `globales`, con un valor o
  `{"entrada": …, "salida": …}`: `orientacion_muro_del_punto` y
  `distancia_borde_calzada_del_punto_m` (`servicio.CLAVES_DE_CABEZAL`, validadas por
  `M9.validar_sobrecarga_del_punto`). `servicio.fundir_sobrecarga_del_punto` las pasa
  extremo por extremo a lo declarado del cabezal; `predimensionar_cabezal` las lleva a
  `GeometriaCabezal.orientacion_trafico` / `.distancia_borde_calzada_m`, y el ensamble
  (`h_eq_sobrecarga_trasdos`) las usa y lo dice en el paso 9.2.2. Lo que el punto no
  declara sale del [S] de corredor; las secciones del alero lo heredan.
- **Por qué no una regla:** AASHTO 3.11.6.4 no tiene tabla para el muro oblicuo; deducir
  la orientación del esviaje sería inventar un umbral (T7B-11).
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: el ensamble avisa
  (`M9.avisos_de_la_sobrecarga_del_punto`) si el cruce tiene esviaje y el punto no declara
  la orientación (rige la de corredor, sin deducir nada), y si se declara la distancia con
  la orientación perpendicular vigente (no se usa). El aviso vive en el ensamble y no en
  `fundir_sobrecarga_del_punto`: sólo allí se conoce la orientación vigente.
- **Qué haría falta:** nada; un muro oblicuo con tabla propia necesitaría una fuente.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::validar_sobrecarga_del_punto`

## VE7-01 · El alero se verifica como muro en sus franjas, con su zapata dimensionada y armada (VE-7; cierre de T7C-04)

- **Cerrado:** `M9.estabilidad_del_alero` verifica cada franja de
  `FRACCIONES_DE_ESTABILIDAD_DEL_ALERO` (0, L/4, L/2, 3L/4, L; la sin fuste no, y el paso
  9.3.f lo dice) con el ensamble del cabezal: E1–E3 de AASHTO 11.6.3.2, 11.6.3.3, 11.6.3.6
  y 11.6.5, códigos `.alero[.25…]`. Rige más de una franja: el borde de la plataforma no
  baja y la pendiente equivalente crece (C3.11.5.8.1-1). La zapata de los aleros (un ancho
  por cabezal) crece por el talón con `dimensionamiento_zapata_cabezal` hasta que cumplen
  todas (al tope, NO FACTIBLE); su peralte, por el armado del talón en cada franja (la
  tabla toma el de mayor acero). Con forma declarada rige la menor resistencia portante de
  la zapata corrida y de L = alero corto (10.6.3.1.2a). Los aleros de gravedad: la sección
  del cabezal cortada, E1–E3 y C1–C3, C6–C8 (`verificacion_ciclopea_del_alero`); el
  cuerpo no se itera. `ancho_zapata_aleros_m` y `espesor_zapata_aleros_m` se declaran,
  ganan y no se iteran (CB6 del alero); lo del cabezal es la partida y, si el alero lo
  supera, se avisa. E4/E5 diferidas son «del cabezal y de sus aleros», y el FS declarado
  avisa que no se comprueba que cubra los aleros. Memoria, JSON y metrado (trapecio en
  gravedad) lo reflejan. Dorados a mano: `tests/test_ve7_alero_estabilidad.py`.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios,
  aplicados: decisiones 2 y 6 sin cambios; 1 sustituida por las franjas; 3 y 5 con las
  claves propias; 4 con los dos textos; abiertos (a) a (d) implementados.
- **Abierto:** nada, salvo la discretización: entre dos franjas no se verifica (la
  fracción es resolución de la verificación, `src/tolerancias.py`).
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M9_cabezal/alero.py::estabilidad_del_alero`

## VE5-CAT-01 · La rama de selva alta del TMC: [S] `region_natural` y la recomendación como piso del catálogo (cierre de T4-06)

- **Cerrado (VE-5, lote catlic, 2026-11-20):** la entrada que faltaba es el [S] de corredor
  `region_natural` (categoría costa / sierra / selva_alta / selva_baja; La Unión = `costa`,
  nivel perfil, medido). `M2.piso_de_selva_alta` lo lee siempre que el material es TMC; con
  `selva_alta`, `M2.siguiente_diametro` arranca la serie del TMC en el primer escalón que no
  baja de Ф 48" y `M2.catalogo` emite el paso `F3.SELVA_ALTA_TMC` con verbo **RECOMIENDA**
  (la cita `MC_HHD.4.1.1.3.7a` es RECOMENDACION). En la costa la rama no actúa. La constante
  salió de `CONSTANTES_DE_REFERENCIA`.
- **Por qué así (decisión pendiente de Fable, tomada del lado seguro):** (1) la recomendación
  se aplica como piso del catálogo y no como aviso, porque la hoja de ruta §3.1 manda
  programar la rama y el piso es el lado seguro frente al flujo de barros; (2) el designado
  de 1200 mm de AASHTO M 36 queda por debajo de 48 in = 1219.2 mm y no se toma por el
  «Ф 48”» (ninguna fuente del repositorio los equipara para el acero corrugado; la
  equivalencia de M 170M Table 6 es del concreto): el primer escalón es 1.35 m; (3) las
  cuatro características del párrafo anterior se presumen para todo cruce de un corredor
  declarado de selva alta.
- **Qué haría falta:** que Fable o el dueño confirme (1) y (2) o elija aviso sin piso o
  1200 mm por equivalencia [N→]. La condición `COND-SELVA-ALTA` ya se resuelve con
  `PorDatoDeSitio("region_natural")` (VE-7, ficha VE7C-03).
- **Dónde vive:** `src/modulos/M2_material.py::piso_de_selva_alta`

## VE5-CAT-02 · La cuneta trapezoidal de la Tabla Nº 34 (región > 3000 mm/año): el fondo como campo de `seccion_cuneta` (cierre de lo que T9-01 dejó diferido)

- **Cerrado (VE-5, lote catlic, 2026-11-20):** `seccion_cuneta` tiene un quinto campo,
  `ancho_fondo_m` (valor de archivo 0 = la triangular de siempre; ventana 0–1.20 m). Con
  fondo, `M10.capacidad_cuneta` calcula la sección TRAPEZOIDAL (`M10.geometria_cuneta`:
  A = b·y + (Z1+Z2)·y²/2, P = b + y·(√(1+Z1²)+√(1+Z2²)); el tirante a la velocidad límite
  por brentq) y la contrasta con la fila «Muy lluviosa (>3000 mm/año)» de la Tabla Nº 34
  (pág. impresa 178, PDF 181): profundidad 0.30, ancho 1.20 y la nota «* Sección
  Trapezoidal con un ancho mínimo de fondo de 0.30»; por debajo, `DatoInvalidoError` con el
  campo culpable (la tabla lo exige: «las dimensiones mínimas serán»). La fila pasó de
  `NoUsada` a `Usada` en el registro; `CapacidadCuneta.ancho_fondo_m` lo lleva al informe.
- **Por qué así:** (1) el ancho de la tabla se lee, con fondo, del borde de la rasante a la
  vertical del pie del talud exterior, de modo que Z1 = (a − b)/d: es LECTURA del proyecto
  (la fuente no dibuja la trapezoidal), declarada en la nota del paso 10.2, y la única con
  la que la fila da Z1 = 3, como la triangular de 1600 a < 3000 mm/año; (2) el campo es
  obligatorio en la puerta y en M10 (sin él no se supone sección): una sesión que declaró
  `seccion_cuneta` antes de VE-5 tiene que añadirlo; (3) la región pluvial sigue sin ser
  dato: la ventana de profundidad empieza en 0.40 (fila de 1600 a < 3000), de modo que la
  trapezoidal mínima exacta (0.30 de profundidad) no se puede declarar y una más honda sí.
- **Cerrado en VE-7 (lote B, B11; ficha VE7B-07):** la región pluvial es el [S] opcional
  `precipitacion_anual_corredor_mm`; declarado, la fila de la Tabla Nº 34 sale de él.
- **Qué haría falta:** la sección rectangular sigue sin implementarse.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::geometria_cuneta`

## VE5-CAT-03 · Fase 0-bis: la licuefacción como resultado declarado del EMS, con bloqueo de expediente donde AASHTO 10.5.4.2 la exige

- **Cerrado (VE-5, lote catlic, 2026-11-20; decisión del dueño adoptada, censo ítem 6):**
  módulo nuevo `ML_licuefaccion` (Fase 0-bis), corrido por `servicio._fase_licuefaccion`
  para cada punto clasificado y **sólo a expediente** (la corrida de perfil lo difiere
  entero: `MODULOS_DIFERIDOS_POR_ALCANCE`). Decide si AASHTO 10.5.4.2 (PDF 1323) exige la
  evaluación —zona 3 o 4 por el [S] nuevo `zona_sismica_aashto` (sin leer no se supone 1
  ni 2, como la §9.2 hace con la exención de 11.5.4.2), NF ≤ 50 ft de la columna del
  punto, suelo presumido mientras el EMS no lo descarte, con `PERFIL_SUELO_PRESUNTO`
  dicho al lado— y, donde la exige, pide el dato `licuefaccion_ems` (E.050 38.3, cita
  nueva `E050.38.3`): sin él, o con `licua` sin mitigación, `DatoFaltanteError` y el
  expediente no cierra. Declarado, se contrasta con `demanda_sismica_licuefaccion` y
  `Mw_licuefaccion`, que con `PERFIL_SUELO_PRESUNTO` salieron del censo
  `SIN_CONSUMIDOR_Y_SIN_MEDIDA` (7 → 3, con `clase_sitio`). Paso `F0.LICUEFACCION` (verbo
  OBLIGA). Censo §5: `ML.contrastar_clase_sitio` contrasta la clase medida, si se declara,
  con las filas de `F_pga` (F: método no evaluable, 3.10.2; fuera: inválido; dentro: aviso).
- **Por qué así (decisión pendiente de Fable, tomada del lado seguro):** (1) el dato es
  por punto con `globales` admitido (el 38.3 habla del potencial «de la zona»; el NF y el
  suelo varían por cruce) y el del punto gana; (2) la M_w del EMS no puede ser menor que
  la adoptada (una M_w mayor baja el MSF) y su Tr no puede ser menor; (3) la mitigación
  declarada se imprime y no se verifica; (4) no hay calculadora CSR/CRR.
- **Qué haría falta:** el EMS real por punto; la lectura de S_1 y la clase de sitio para
  `zona_sismica_aashto`; la M_w adoptada; una sección propia de la memoria y del JSON
  para la Fase 0-bis (hoy viaja como `InformePunto.licuefaccion`, su paso y sus avisos);
  y corregir la hoja de ruta (Fase 0-bis y §0.5 dicen que la licuefacción queda fuera del
  script, sin el bloqueo de expediente).
- **Cerrado por VE-6:** la falta se registra al lado de las demás, no delante (ficha VE6-02).
- **Dónde vive:** `src/modulos/ML_licuefaccion.py::evaluar_licuefaccion`


# Parte LXI — Lo que VE-5 (lote «gui») dejó escrito: la ventana, la CLI y el hijo del PDF

VE-5, lote «gui» (2026-11-20, rama `claude/ve5-gui`, sobre `70226de`), cierra los ítems 38 a 40 y
43 a 49 del censo del 2026-11-20 (`proceso/planes_mejora/ve3_estado/CENSO_PENDIENTES_FABLE_2026-11-20.md`,
sección 4). El 41 (editor de [S] en la ventana) no se hace: R4. Ningún número de cálculo cambia;
cambian textos de la memoria (el rótulo de la rugosidad, los decimales de `D` con la serie de 6 in)
y la huella de `criterios_adoptados.py` (un criterio nuevo, opcional y sin valor). Los documentos
generados (`indice_formulas.md`, línea base) no se regeneran aquí: los regenera el integrador.

## VE5GUI-38 · La pestaña 2 se desplaza y las filas de exportación se parten solas

- **Cerrado (ítem 38; fichas UI3-01 y UI4-01):** la columna derecha de la pestaña 2 es un
  `MarcoScroll` (con `relleno=0`): con el editor de un criterio de tabla, a 900 × 620 el contenido
  pide 1103 px y la vista da 423, y desplazándolo se llega a «Aplicar», «Quitar», «Barrido…», «Ver
  la norma…» y «Guardar en archivo fuente». Las tres filas de exportación de la pestaña 4 son
  `componentes.FilaFluida`, que coloca cada botón a la derecha del anterior mientras quepa y si no
  parte la fila, sin reordenar: el ancho de un botón depende de la tipografía de la pantalla, que
  la ventana no elige. Medido en ventana real (`tests/apoyo/gui_ve5_real.py`): a 900 × 620 los
  siete caben, y con la letra agrandada se parten y siguen cabiendo.
- **Abierto:** la medida sigue siendo de xvfb, no de la pantalla del autor (ficha UI4-01).
- **Qué haría falta:** nada más que esa medida.
- **Dónde vive:** `gui/componentes.py::FilaFluida`

## VE5GUI-40 · `S_conducto`, `bombeo` y `peralte` con campo y bandera

- **Cerrado (ítem 40; ficha T6-04):** `sesion.CLAVE_EXTERNA_DE_CAMPO` y `gui/app.py::CAMPOS_EXTERNOS`
  las suman (la sección donde aparecen la deriva `familias_que_usan`), la CLI tiene
  `--s-conducto`, `--bombeo` y `--peralte`, y viajan en la sesión como las demás. Una sesión de un
  formato anterior abre con los tres campos vacíos (un campo que la sesión no trae es un campo
  vacío; `FORMATO_SESION` no cambia). La exclusión bombeo/peralte sigue en
  `exigir_transversales_compatibles`, también con banderas.
- **Abierto:** nada.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/sesion.py::CLAVE_EXTERNA_DE_CAMPO`

## VE5GUI-39 · Temporales únicos al exportar y el fallo de escritura sin traza

- **Cerrado (ítem 39; ficha UI5-01 (c) y (d)):** `exportar_html`, `exportar_html_resumida`,
  `exportar_csv` y `sesion.escribir_json_atomico` escriben por `escritura_atomica.escribir_atomico`
  (temporal único, corto y oculto; sigue el enlace y conserva el modo); la copia que abre el
  navegador lleva un nombre único. `cli.main` atrapa el `OSError` de las salidas y sale con
  `CODIGO_ESCRITURA_FALLIDA` = 3 y un mensaje que nombra el destino; lo ya escrito queda entero.
  El hijo del PDF no cuenta el 3 entre los códigos que dejan memoria.
  El README (§4) documenta el código 3.
- **Abierto:** nada.
- **Qué haría falta:** nada.
- **Dónde vive:** `cli.py::CODIGO_ESCRITURA_FALLIDA`

## VE5GUI-46 · Ids `FH.*` en el índice, la fila de rugosidad y los decimales de `D`

- **Cerrado (ítem 46; fichas VE2-02, VE2-A (2)(3) y VE1-01):** el índice reconoce `FH.<nombre>` y
  los ids con punto interior (`PATRON_ID_DE_FUNDAMENTO`); la fila de M11 dice «Rugosidad (n de
  Manning)» y «Fila o fuente del n», sin suponer la doble n; el comentario de `Material.pasos` ya no
  dice «vacía en la circular»; y `modelos.cifras_de_dimension` da a las magnitudes `D`, `B` y `H`
  (las de forma y las cuatro `D` de M4) los decimales del rótulo: 0.90 sigue «0.90», 1.0668 dice
  «1.0668».
- **Abierto:** `docs/indice_formulas.md` no se regeneró (lo regenera el integrador; ya estaba
  desincronizado en la base).
- **Cerrado (VE-7: lote A, VE7A-10, y lote B, B13; decisión del consultor Fable, triaje VE-7,
  2026-11-20):** las `D` de M9 y las cinco `Magnitud("D", …)` de M5 (V4b, V9) y M6 (apron y clase
  de HEC-14) usan `cifras_de_dimension`; `tests/test_ve7_lote_b_cifras.py` lo fija por AST y con el
  paso de V9 en 1.0668 m.
- **Qué haría falta:** regenerar el índice.
- **Dónde vive:** `src/modelos/memoria.py::cifras_de_dimension`

## VE5GUI-43 · Los ensayos de durabilidad, quinta población del censo

- **Cerrado (ítem 43; ficha T4-09):** `Poblacion.DATO_EXTERNO_OPCIONAL` censa los seis ensayos
  (`variables_entrada._ENSAYOS`, con concepto, unidad, dominio y la Fase 3; `abrasion` con sus
  opciones de la Tabla 8-4 de WSDOT); la ayuda del JSON los lista rotulados como opcionales
  (`ayuda_entrada.fichas_de_ensayos_opcionales`); el pre-vuelo no los cuenta como falta (siguen
  fuera de `CLAVES_EXTERNAS`).
- **Abierto:** el panel de la pestaña 1 para los ensayos no se abrió: son datos por calicata, y un
  campo global los pondría iguales en todos los puntos (la misma razón por la que R4 deja los [S]
  en la sesión). `cabezal_declarado` sigue fuera del censo; unificar los sulfatos con
  `exposicion_quimica_ems` y el criterio para acero corrugado siguen en T4-09.
- **Qué haría falta:** una decisión del dueño sobre el panel y sobre `cabezal_declarado`.
- **Dónde vive:** `src/variables_entrada.py::_ENSAYOS`

## VE5GUI-44 · Techos de transcripción de la Fase 6, como aviso (decisión pendiente de Fable)

- **Cerrado (ítem 44; ficha T8-11):** el criterio [A] de perfil `techos_de_transcripcion_fase_6`
  (opcional, sin valor) da, cuando se declara, un techo por dato (`duracion_caudal_pico_min`,
  `profundidad_socavacion_estimada_m`, `material_lecho_salida.D84_m` y `.Sv_Pa`), y cada punto
  avisa, al empezar y aunque no llegue a dimensionarse, el dato que lo pasa
  (`M6.avisos_de_transcripcion`, desde `correr_punto`), sin rechazarlo ni mover un
  resultado. Un techo mal declarado es un `Bloqueo` del punto.
- **Por qué sin valor:** ninguna fuente de `normas/` da los techos (HEC-14 Cap. 5, págs. 5-1 a 5-7)
  y la sesión no pudo consultar a Fable: tomó la decisión más conservadora, que es no fijar ningún
  techo de archivo. Sin declarar, la corrida es la de antes de VE-5.
- **Qué haría falta:** la decisión de Fable o del dueño sobre los techos de archivo (y su respaldo).
  La cadena `"1.0"` de `_numero_externo` sigue como estaba (ficha T8-11).
- **Dónde vive:** `src/modulos/M6_proteccion.py::avisos_de_transcripcion`

## VE5GUI-49 · El hijo del PDF formatea la corrida embebida; las entradas de la pestaña 1 invalidan

- **Cerrado (ítem 49; fichas UI5-01 (a)(b), UI2-01 (b), EXT-8-02 y EXT-10-04; decisión del dueño):**
  `src/serializacion_informe.py` da al `Informe` ida y vuelta por JSON etiquetado, sin `pickle`:
  sólo construye dataclasses y enums de `src`, repone sin `__init__`, rechaza campos de otra
  versión y conserva la IDENTIDAD de los objetos compartidos (la memoria reconoce un paso ya impreso
  por identidad; sin ella `expediente_cabezal` imprimía un paso «repetido» de más). La sesión de
  trabajo del hijo embebe la corrida con su informe entero (`sesion_de_la_corrida`,
  `corrida_para_sesion(con_informe=True)`), y el hijo corre `cli.py --sesion … --corrida-embebida`:
  no relee el CSV ni ningún archivo, comprueba que el volcado del informe cargado es EXACTAMENTE el
  `informe_json` de la misma corrida y formatea; la memoria sale idéntica a la de la ventana (medido
  sobre las corridas de referencia). Y el JSON de datos externos, el de datos de sitio, los datos
  que no están en el CSV y el alcance invalidan el informe (`MOTIVO_ENTRADA_CAMBIADA`); abrir una
  sesión o un proyecto nuevo escriben esos campos después de retirar el informe con su motivo.
- **Abierto:** «Guardar sesión» no embebe el informe entero (pesa megabytes: 7 MB la sesión de
  `expediente_cabezal`), de modo que `--corrida-embebida` sólo vale con la sesión de trabajo del
  hijo; una sesión sin él recalcula como antes, y `ProcesoPdf` sólo pide la bandera cuando la sesión
  la trae (`trae_la_corrida_embebida`).
- **Qué haría falta:** si el dueño quiere memorias sin recalcular desde una sesión guardada, que
  «Guardar sesión» embeba el informe (o lo guarde aparte).
- **Dónde vive:** `src/serializacion_informe.py::informe_desde_dict`

## VE5GUI-45 · Estado del expediente: discrepancias abiertas y corridas para comparar

- **Cerrado (ítem 45; ficha C8-02):** `Registro.discrepancias_abiertas` tiene consumidor de
  producción: la pestaña 4 pinta, en un panel propio, las abiertas contra la hoja de ruta
  (`estado_del_expediente.discrepancias_abiertas`), con independencia de la corrida. Y la pestaña 4
  ofrece comparar la corrida vigente con una ANTERIOR de la sesión, de una lista derivada de las
  corridas embebidas (`corridas_para_comparar`, la más reciente primero), por el comparador de E14.
- **Abierto:** cerrado en VE-7 (ficha VE7C-05): la CLI lo imprime con `--estado-expediente`.
- **Qué haría falta:** nada en la CLI; la ventana y la CLI leen el mismo módulo.
- **Dónde vive:** `src/estado_del_expediente.py::discrepancias_abiertas`

## VE5GUI-47 · El chequeo dimensional llega a M6–M10; los fundamentos sin ejercitar siguen

- **Cerrado en parte (ítem 47; fichas I4-01 (b), T10-02 y T11-06):** las tres corridas de
  referencia emiten 401 pasos de M6 a M10 (M9 244, M7 74, M6 43, M8 31, M10 9), y
  `tests/test_ve5_dimensional_m6_m10.py` les aplica las dos comprobaciones del piloto que no
  necesitan relación escrita: toda unidad tiene dimensión (el mapa del piloto más ocho unidades
  propias de estas fases) y todo umbral es conmensurable con su resultado. Ninguna inconsistencia.
- **Abierto:** las RELACIONES por paso de M6–M10 (401 pasos, a mano desde su fórmula). Los
  fundamentos sin ejercitar los recorre desde VE-7 la cuarta corrida de referencia (ficha VE7C-06).
- **Qué haría falta:** esas relaciones, en una sesión propia.
- **Dónde vive:** `tests/test_ve5_dimensional_m6_m10.py::UNIDADES_DE_M6_A_M10`

## VE5GUI-48 · La integración continua corre los tests de ventana

- **Cerrado (ítem 48; fichas SIS-F-01 y C09-01):** `.github/workflows/pruebas.yml` instala el Tk del
  sistema, `xvfb` y las librerías de weasyprint, comprueba que la ventana se levanta y corre la
  suite entera bajo `xvfb-run -a`, el envoltorio con que la suite busca un Tk.
- **Abierto:** sin `NORMAS_DIR` (repositorio privado) los tests que abren un PDF se saltan allí.
- **Qué haría falta:** un secreto con acceso al repositorio de normas, si el dueño lo quiere en CI.
- **Dónde vive:** `tests/test_ve5_gui.py::test_48_la_integracion_continua_corre_la_suite_bajo_un_servidor_x`


# Parte LXII — Lo que VE-6 (pre-vuelo) dejó escrito: el pre-vuelo y la corrida dicen lo mismo

VE-6 (2026-11-20, rama `claude/ve6-prevuelo`, sobre `cc106ce`) corrige las dos causas que la
integración de VE-5 (lotes met y catlic) dejó en rojo. El subagente Fable no se pudo lanzar
en la sesión (la herramienta no estaba disponible): las dos decisiones salen del código y de
las fichas VE5-MET-01 y VE5-CAT-03, que ya las sostenían. Después las revisó Fable
(dictamen del consultor, 2026-11-20): las dos «aprobar con cambios»; los cambios están en
estas fichas.

## VE6-01 · El nivel freático en M12 es de expediente y detiene el rubro, no el punto

- **Cerrado:** el pre-vuelo anunciaba `NF_profundidad_m` como dato que DETIENE en todo
  punto («la exige M12_metrados»): M12 no se difiere entero a perfil (el cuadro de
  compatibilidad corre en los dos alcances) y la corrida de perfil no la pedía. Los dos
  leen ahora `servicio.CONSUMO_DETRAS_DE` (M12 → M9_cabezal) por
  `servicio.consumo_diferido`, que falla como `_difiere` ante un alcance desconocido. A
  expediente la falta es un `Bloqueo` de la Fase 11 sólo del rubro de excavación.
  Dictamen Fable («aprobar con cambios»): (1) todo renglón bajo agua (501.B, 501.D) lleva
  `M12.AVISO_PARTIDA_BAJO_AGUA`: el reparto sale de la lectura de campo del EMS, no del
  freático más alto previsto, y la partida la fija el Supervisor (EG-2013 501.09, «aprobadas
  por el Supervisor»; 501.01, pág. impresa 886, «la presencia permanente de agua dificulte
  los trabajos»), sin margen ni corrección numérica; (2) un punto dimensionado sin cabezal
  lleva su `Bloqueo` de la Fase 11 («metrados no medidos: sin cabezal»), que remite al de
  la Fase 9 o al que lo dejó sin 7.B.
- **Por qué así:** los metrados miden el cabezal de la Fase 9, que el perfil difiere. Un
  volumen único sin partida se asignaría en silencio a la partida en seco (501.01 separa
  las dos y 501.09 las paga aparte). VE-5 met extendió `Criterio.no_negativo` a
  `sobreancho_excavacion_estructuras_m` e `incremento_acero_por_despiece` (501.04, 504.10):
  censado en `tests/test_ve2_revision_m3_m4.py` (`CON_SIGNO_DE_METRADO`).
- **Qué haría falta:** el freático más alto previsto del EMS, si el dueño quiere que el
  reparto lo use; hoy lo resuelve el Supervisor en obra.
- **Dónde vive:** `src/servicio.py::consumo_diferido`

## VE6-02 · La licuefacción se registra al lado de las demás faltas, no delante

- **Cerrado:** el `Bloqueo` de la Fase 0-bis (ficha VE5-CAT-03) no detiene el dimensionado:
  la corrida sigue y dice también las faltas de las Fases 2 a 11. Lo que fallaba eran los
  lectores que tomaban el primer bloqueo por motivo del dimensionado (la fila del cuadro de
  compatibilidad y cuatro tests del bucle de MD). Dictamen Fable («aprobar con cambios»):
  el motivo del cuadro es por SELECCIÓN POSITIVA, el primer bloqueo no diferido de
  `servicio.FASES_QUE_LLEVAN_A_7A` (carga, clasificación, hidrología, bucle de MD y 7.B) y,
  sin ninguno, el texto por defecto de M12; `FASES_AL_MARGEN_DEL_DIMENSIONADO` es su
  complemento, para los tests. Y con la Fase 0-bis abierta el punto avisa
  (`servicio.AVISO_CIMENTACION_PROVISIONAL`) que la cimentación del cabezal es provisional.
- **Por qué así:** el riesgo de licuefacción es del terreno de fundación y del terraplén
  (AASHTO LRFD 10.5.4.2, PDF 1323) y su resultado lo declara el EMS (E.050 38.3): no cambia
  la sección hidráulica. Anteponerlo escondería las faltas reales (la lección de PF-2). La
  exclusión dejaba pasar por motivo cualquier bloqueo lateral —los techos de transcripción
  de la Fase 6, que se anotan antes que nada; la protección, antes de 7.B—: la selección
  positiva cierra el «Abierto» de los techos sin una constante por etapa.
- **Qué haría falta:** nada; una fase nueva que pueda dejar un punto sin 7.A se añade a
  `FASES_QUE_LLEVAN_A_7A` (lo fija `tests/test_ve6_prevuelo.py`).
- **Dónde vive:** `src/servicio.py::FASES_QUE_LLEVAN_A_7A`
# Parte LXIII — Lo que VE-6 (integrador) dejó escrito: ítems 22 y 34 y el cabezal paralelo (T7A-03)

VE-6 (2026-11-20, rama `claude/ve6-integrador`, base `3ce07b5` con VE-5 integrado) cierra lo que el
plan de lotes del censo (`proceso/planes_mejora/ve3_estado/CENSO_PENDIENTES_FABLE_2026-11-20.md`,
§7) dejó al integrador. La sesión no tuvo a mano la herramienta para consultar a Fable: las
decisiones ambiguas las tomó ella, y cada ficha dice cuál, por qué y con qué cita. Después
las revisó Fable (dictamen del consultor, 2026-11-20): las tres «aprobar con cambios», y los
cambios están aplicados en estas fichas.

## VE6-22 · El control de salida se rehace con la longitud entre cabezales: pasada de refinamiento con aviso

- **Cerrado (ítem 22 del censo; fichas T6-01 y T7A-06; decisión del dueño del 2026-11-20,
  «longitud entre cabezales con pasada de refinamiento y aviso»):** tras la Fase 9 del punto,
  `servicio._fase_9_refinamiento` toma la longitud entre cabezales del paso 9.0.5 y pide a M4
  (`refinar_con_longitud_entre_cabezales`) el control de la MISMA sección, material, caudal y
  pendiente del diseño con L = L_cab y con el TW que la Sec. 1.3 da con la solera de salida de esa
  longitud (`servicio._tw_de_la_seccion_1_3`, la misma vía del diseño: declarado, `cota_TW`,
  Manning en el receptor, escenarios o el criterio). La entrada queda anclada en la cota de entrada
  del punto y la salida en cota_entrada − S·L_cab: es EXACTAMENTE lo que daría declarar
  `longitud_m` = L_cab, y el test lo fija contra esa otra corrida entera. El paso 9.0.6
  (`F9.REFINAMIENTO_LONGITUD`, citas `HDS5_3ED.3.3.5#ENCAJE` y `HDS5_3ED.3.1.4#LONGITUD`) imprime
  las dos cargas; el aviso sale SÓLO si la carga gobernante sube o el control cambia (con la carga
  del diseño igual o mayor, el diseño quedó del lado de la carga mayor), y nombra el remedio:
  declarar `longitud_m` por punto. Si el TW o el control no se pueden rehacer, se avisa con el
  motivo y el punto no se bloquea (ya está verificado con la aproximada). Sin criterio nuevo: no hay
  número que elegir.
- **Decisión:** no se itera ni se sustituye: HDS-5 3.1.4 (pág. 3.9) arranca con longitud
  aproximada y 3.3.5 (pág. 3.25) pide que la final «should be close», sin tolerancia; L_cab
  depende de la coronación y ésta de la sección. En A-01 la carga no cambia (entrada gobierna).
- **Dictamen Fable (2026-11-20, aprobado con cambios):** el aviso dice «V4 NO se cumpliría» si
  Δ = HW(L_cab) − HW(L) supera el margen de V4 del diseño, y «V1 NO se cumpliría» si V1,
  re-evaluada con la hidráulica refinada, deja de cumplir (V1 juzga y/D, no el HW: comparar Δ
  con su margen mezclaría dimensiones); `F9.REFINAMIENTO_LONGITUD` pasa a RECOMIENDA («should
  be close», 3.3.5). `servicio._lo_que_no_se_cumpliria`.
- **Abierto:** V1, V4 y el tamizado de 7.A siguen juzgados con la carga del diseño; con la
  refinada se avisa y, desde VE7A-09, el punto se bloquea si V1 o V4 dejarían de cumplirse. La coronación de salida sigue fijada con la cota de salida de la
  aproximada (ficha T7A-06).
- **Qué haría falta:** declarar `longitud_m` = L_cab en el punto avisado (gana y se verifica
  entero); o, si el dueño lo pide, una segunda pasada completa de MD con L_cab.
- **Dónde vive:** `src/modulos/M4_control.py::refinar_con_longitud_entre_cabezales`

## VE6-T7A03 · El cabezal paralelo a la vía en un marco: lo pide una fila de la Carta 11 del HDS-5

- **Cerrado (T7A-03 (1); decisión del dueño del 2026-11-13):** las filas de la Carta 11 (Tabla
  A.1, PDF 197) tienen banda de esviaje del cabezal respecto del barril, leída del rótulo
  (`BANDAS_ESVIAJE_CABEZAL_CAJON_A1`). Si un marco declara una en `embocadura_cajon`, su cabezal es
  RECTO Y PARALELO A LA VÍA, sin aleros (`EmbocaduraDelPunto.orientacion`); la coherencia exige el
  esviaje en la banda y el ke del borde de esa fila (`KE_C2_POR_FILA_CARTA_11`, dictamen Fable:
  chaflán 3/4" → escuadra, 0.5; bisel 45° → biselado 0.2 o escuadra; es LECTURA de los rótulos
  —la A.1 separa «chamfers» de «bevels» y la C.2 da 0.2 a «beveled edges on 3 sides»—, no frase
  literal). L_c = ancho/cos θ + 2·empotramiento; CB1 contra ancho/cos θ. Avisa con aleros en
  `embocadura_cabezal` y con varias celdas (`HDS5_3ED.5.4.2#EVITAR`).
- **Decisiones (aprobadas por Fable):** la orientación la elige la FILA declarada (no alcanza a los
  tubos); con cabezal paralelo el esviaje de la embocadura es el del barril (nota de
  `#MAXIMO_PRACTICO`), sin interpolar fuera de banda; los dos cabezales van paralelos (`#PARALELO`).
- **Abierto:** (1) Cerrado en VE7A-02 (embocadura del marco por punto). (2) El extremo oblicuo del marco no se
  verifica en M8 (sin numeral atribuido); desde VE7A-08 se avisa. (3) Carta 12 escala 3 (paralelo con aleros) sin banda; la
  h_eq por orientación, cerrada en VE7A-07. (4) Cerrado en VE7A-01.
- **Qué haría falta:** el extremo oblicuo en M8; los aleros
  del paralelo.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::_embocadura_paralela`

## VE6-34 · La progresión del catálogo: G1 dentro del bucle, V10 la detiene y el delta con V4 bajo control de entrada

- **Cerrado (ítem 34; VE3-08 H7/H8/H3 a y T11-03 (2)):** (a) **H8**: el escalón que cumple toda la
  Fase 5 pasa por la COBERTURA de 7.A antes de adoptarse (`MD._escalon_sin_cobertura`); si la
  rasante no se la deja, queda rechazado con el delta de G1 (`EscalonSinCabida.por_cobertura`).
  El material se descarta por rasante sólo si NINGÚN escalón restante es más bajo
  (`_escalon_restante_mas_bajo`, dictamen Fable): en el tubo la progresión es ascendente y nada
  cambia; en el marco `M2.progresion_de_cajon` no ordena los pares (B, H) y un par más bajo baja
  la clave, así que la progresión sigue. Sólo la cobertura: el resguardo ya es V4. (b) **H7 con
  V10**: V10 incumplida detiene la progresión (juzga `ResultadoHidraulico.S`, igual en todo
  escalón). (c) **T11-03 (2)**: el escalón que no cabe y sólo incumple V4 da el delta del
  resguardo bajo control de ENTRADA (cota inferior); bajo SALIDA, no. La hoja de ruta lleva el
  «Addendum VE-6» en la nota T11-03 de §7.B.
- **Decisiones (aprobadas por Fable con cambios):** H7 sólo con V10, la única cuya independencia
  de la sección se demuestra; el delta bajo salida exigiría iterar 7.A con 7.B y no se inventa.
- **Abierto:** H7 con V2, V2b y V7; el delta de V4 bajo salida y la rama «no cabe» del marco se
  cerraron en VE-7 (fichas VE7B-04 y VE7B-03); la fila NF de VE3-13 sin iterar el peralte (M9 en otra rama; «inflar el
  peralte no es diseño», decisión de VE-3.14 que sólo el dueño revierte).
- **Qué haría falta:** la monotonía de V2/V2b/V7 con D; la decisión del dueño sobre la fila NF.
- **Dónde vive:** `src/modulos/MD.py::_escalon_sin_cobertura`

# Parte LXIV-A — Lo que VE-7 (lote A) dejó escrito: la embocadura, el sismo del cabezal y la Fase 9

VE-7, lote A (2026-11-20, rama `claude/ve7-lote-a`, base `cb15e32`) implementa lo que el triaje VE-7
del consultor Fable decidió para el cabezal y su embocadura. Cada ficha dice la decisión, la cita y
el test; lo que la sesión tuvo que decidir sin dictamen va rotulado «pendiente de revisión Fable».

## VE7A-01 · La Carta 10 con cabezal normal empareja el ke por el borde de su fila (cierra VE6-T7A03 (4))

- **Cerrado:** `KE_C2_POR_FILA_SIN_ALETAS` (constantes, [N] por lectura de rótulos): el chaflán de
  3/4" y la escala 2 de la Carta 8 («90° and 15° wingwall flares») sólo con la escuadra (ke 0.5);
  los biseles de 45° y 33.7° con la biselada (0.2) o la escuadra. `M9.filas_hds5_del_cajon` la
  aplica en la rama sin aletas, como `KE_C2_POR_FILA_CARTA_11` en la del paralelo.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** es LECTURA de los rótulos, no frase
  literal: la Tabla A.1 separa «chamfers» de «bevels» y la C.2 da 0.2 sólo a «beveled edges on 3
  sides». Ningún dorado usaba la Carta 8 e2 con 0.2 (el ejemplo del HDS-5 con 0.2 es el bisel de
  45°): no hubo declaración que corregir.
- **Abierto:** nada de esta ficha.
- **Qué haría falta:** nada; una frase literal de la fuente que empareje borde y fila la sustituiría.
- **Dónde vive:** `src/constantes_normativas.py::KE_C2_POR_FILA_SIN_ALETAS`

## VE7A-02 · La embocadura del marco se declara por punto (cierra VE6-T7A03 (1))

- **Cerrado:** clave `embocadura_cajon_del_punto` = {`carta`, `ke`}, sólo por punto, validada
  por `M9.validar_embocadura_cajon_del_punto`. En la Familia C `servicio.correr_punto` pisa
  `embocadura_cajon` y `ke_entrada_cajon` en caliente (la carta primero) y en `finally` repone lo
  que había; la coherencia sigue en `verificar_coherencia_embocadura_cajon` y el paso 9.0.0 dice
  «declarada por punto». En otra familia no se aplica y se avisa.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: la memoria no puede quedar falsa para el punto.
  `ContextoCorrida.criterios_por_punto` ({criterio: {id_punto: valor}}, de
  `servicio.criterios_por_punto`) lleva lo que cada punto pisó; la fila de los dos criterios en
  `M11.bloque_criterios` y en el JSON (`por_punto`) dice el valor de cada punto al lado del de
  proyecto. Sin la clave, la memoria no cambia (test byte a byte).
- **Abierto:** nada de esta ficha; el pre-vuelo no la anuncia (no es una falta).
- **Qué haría falta:** nada.
- **Dónde vive:** `src/servicio.py::correr_punto`

## VE7A-03 · C8 a media altura decide con cualquier criterio de tracción (cierra VE6M9-01 (b))

- **Cerrado:** en `M9._verificar_cuerpo_bajo_sismo` las dos secciones de C8 (arranque y media
  altura) deciden (`decide = True`); la media altura, atribuida a
  `criterio_traccion_cabezal_ciclopeo`, también con `traccion_admisible_e060`. Un e > t/6 a media
  altura bajo sismo es una incumplida del cabezal, no un indicador.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** la razón es la del arranque en el
  dictamen de VE-6: E.060 9.2 no combina el sismo con el empuje y no hay contraste que cubra la
  sección. Dos tests de `tests/test_ve5_m9_ciclopeo.py` que fijaban «informa» se reescribieron.
- **Abierto:** nada de esta ficha.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M9_cabezal/ciclopeo.py::_verificar_cuerpo_bajo_sismo`

## VE7A-04 · C8 con k_v ≠ 0: el peso estabilizante va con (1 − k_v) (cierra VE6M9-01 (a))

- **Cerrado:** C8 lleva el peso estabilizante con (1 − k_v), signo desfavorable; la inercia
  horizontal sigue con k_h·W entero. Con k_v = 0 nada cambia.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados (abierto (i)): el ensamble E1–E3 también.
  `cargas_del_cabezal` añade bajo sismo, sólo con |k_v| > 0, `C_EQ_KV` = −k_v·(W_w + W_s) en el
  centro de gravedad de los pesos; `combinaciones_de_estabilidad` le da 1.0 en las filas de
  excentricidad, deslizamiento y volteo (los dos casos de 11.6.5.1) y 0 en las de portante. Es
  genérico (todo muro que use el ensamble). El armado lleva los pesos enteros y lo avisa. Se
  retiró el aviso de C8. Citas `CITAS_K_V_EN_LOS_PESOS` (A11.3.1, 11.6.5.1, MP 2.8.1.1.14.1; dictamen Fable de la revisión residual: la cita anterior, MP 2.8.1.1.14.2.1#ROCA, era la de k_h0 en roca).
- **Abierto:** nada de esta ficha (k_v = 0 es el de archivo, prescrito).
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M9_cabezal/ciclopeo.py::_verificar_cuerpo_bajo_sismo`

## VE7A-05 · El empuje sísmico declarado por punto y cabezal donde el programa no lo calcula (VE5M9-02, VE3-15)

- **Cerrado:** clave `empuje_sismico_declarado`, sólo por punto; por cabezal un objeto o hasta dos
  de k_h distinto: `P_AE_kn_m` (componente horizontal del empuje TOTAL del suelo sobre el plano
  vertical del talón de altura h, 11.6.5.2.2, sin la hidrostática), `altura_aplicacion_m`,
  `incluye_hidrodinamica`, `k_h`, `k_v`, `altura_plano_m` y la traza. Se consume sólo donde
  `cargas_del_cabezal` levantaba `MetodoNoEvaluableError` en la cuña SÍSMICA (ψ ≥ φ) o con relleno
  muy abierto (exige la hidrodinámica); nunca sustituye un empuje calculado (lo avisa).
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: casa por k_h, k_v y plano (h ≤ `altura_plano_m`); si no, el
  bloqueo dice qué no casa. P_AE menor que el activo se rechaza; con el reposo rigiendo honra
  `empuje_sismico_muro_que_no_cede`. z del incremento sin techo y con los pisos h/3 y h/2: el
  momento no baja del declarado. K_AE equivalente sólo se imprime. Citas 11.6.5.3#VALIDEZ,
  3.11.5.8.1#CUNA (A11.3.3) y #DISTRIBUCION. El armado (abierto (ii)) usa el plano virtual del
  talón con el declarado de su k_h. Campo `EntornoDelCabezal.empuje_sismico` en `src/modelos/cabezal.py`.
- **Abierto:** el GLE en el programa.
- **Qué haría falta:** nada más del dictamen.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_cargas.py::validar_empuje_sismico_declarado`

## VE7A-06 · La geometría del talud de delante del cabezal, por punto (VE5M9-03)

- **Cerrado:** clave `talud_delante_del_cabezal_del_punto` de `--datos-externos`, por punto o en
  `globales`, con un valor para los dos cabezales o `{"entrada": …, "salida": …}`, en
  `servicio.CLAVES_DE_CABEZAL`; cada valor es la geometría del talud (validada con el validador
  del [S]) o el texto «horizontal». Viaja en `EntornoDelCabezal.talud_delante`.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados (abierto (iii)): el terreno de delante también es del punto.
  `M9._terreno_delante`: un talud del punto → zapata en talud (RC_BC, 10.6.3.1.2c) aunque el
  corredor diga horizontal; «horizontal» → 10.6.3.1.2a aunque el corredor diga talud; sin
  declaración, `terreno_delante_del_cabezal` y su [S]. El paso de E3 dice «terreno delante: del
  punto». Dos puntos con taludes distintos dan RC_BC distintos.
- **Abierto:** nada de esta ficha.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M9_cabezal/estabilidad_base.py::validar_talud_delante_del_punto`

## VE7A-07 · La h_eq con el cabezal paralelo a la vía (VE6-T7A03 (3))

- **Cerrado:** `EntornoDelCabezal.paralelo_a_la_via` (campo nuevo en `src/modelos/cabezal.py`, de
  `CabezalDelPunto.embocadura`). Con el muro paralelo a la vía el muro es paralelo al tráfico:
  si la orientación vigente es la perpendicular del corredor y el punto no declara
  `orientacion_muro_del_punto`, `M9.h_eq_del_cabezal` toma la MAYOR de las Tablas 3.11.6.4-1 y
  -2 (`envolvente_de_h_eq_paralelo`), con aviso que pide `orientacion_muro_del_punto` y
  `distancia_borde_calzada_del_punto_m`; el paso 9.2.2 lo dice. Con el corredor paralelo, o la
  orientación del punto, rige su tabla como hasta ahora.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** la envolvente con aviso, sin deducir
  la orientación. **Pendiente de revisión Fable:** sin distancia del punto la tabla del muro
  paralelo se lee con la columna «0.0 ft» (la mayor) y no con la distancia del corredor, que es la
  de un muro que el corredor declara perpendicular; con la del punto, su columna.
- **Abierto:** nada más de esta ficha.
- **Qué haría falta:** nada; declarar la orientación del punto quita la envolvente.
- **Dónde vive:** `src/modulos/M9_cabezal/empujes.py::h_eq_del_cabezal`

## VE7A-08 · El cabezal paralelo avisa el borde libre esviado de la losa del marco (VE6-T7A03 (2))

- **Cerrado:** `M9._embocadura_paralela` suma un aviso del punto: con el cabezal paralelo a la vía
  el extremo del marco se corta esviado y el borde libre esviado de la losa NO se verifica; las
  vigas de borde del comentario C12.11.2.1 son detalle del proyectista. El aviso nombra la cita
  cuya nota las recoge (`AASHTO_LRFD_9.12.11.2.1#SOMERO`, `CITA_BORDE_LIBRE_ESVIADO`).
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** un aviso, no una verificación: el
  comentario no da un procedimiento con número que el programa pueda aplicar.
- **Abierto:** el borde esviado sigue sin verificarse en M8.
- **Qué haría falta:** un procedimiento de la fuente para la viga de borde del marco esviado.
- **Dónde vive:** `src/modulos/M9_cabezal/geometria.py::_embocadura_paralela`

## VE7A-09 · Lo que dejaría de cumplirse con la longitud entre cabezales bloquea el expediente (VE6-22)

- **Cerrado:** en `servicio._fase_9_refinamiento`, si `_lo_que_no_se_cumpliria` no está vacío
  (V4 con Δ = HW(L_cab) − HW(L) mayor que su margen, o V1 re-evaluada que deja de cumplir), además
  del aviso hay un `Bloqueo` de la Fase 9 (`FASE_CABEZAL`, `ETAPA_REFINAMIENTO_LONGITUD`, sólo a
  expediente), `DatoFaltanteError` sobre `longitud_m`, con el remedio «declarar `longitud_m` =
  L_cab». A-01 no cambia.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: el aviso termina «el expediente queda bloqueado hasta declarar
  `longitud_m` (VE7A-09)» y el docstring de `_lo_que_no_se_cumpliria` ya no dice que nada
  bloquea. El tipo y el campo quedan aprobados.
- **Abierto:** no se itera MD con L_cab (VE6-22).
- **Qué haría falta:** nada; declarar `longitud_m` lo destraba y verifica el punto entero.
- **Dónde vive:** `src/servicio.py::_fase_9_refinamiento`

## VE7A-10 · La `D` de M9 con los decimales del rótulo (VE5GUI-46)

- **Cerrado:** la única magnitud `D` de M9 (la altura interior de la sección en el paso 9.0.4 de
  la losa de entrega) lleva `cifras=modelos.cifras_de_dimension(D)` en lugar de
  `CIFRAS_MAGNITUD`: 0.90 se escribe «0.90» y 1.0668, «1.0668», como el rótulo de la sección.
  Presentación: el valor con que se calcula no cambia.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** extender `cifras_de_dimension` a la
  `D` de M9; M5 y M6 son de otros lotes.
- **Abierto:** las `D` de M5 y M6 (VE5GUI-46).
- **Qué haría falta:** el mismo cambio en M5 y M6.
- **Dónde vive:** `src/modelos/memoria.py::cifras_de_dimension`

# Parte LXIV-C — Lo que VE-7 (lote C) dejó escrito: registro, memoria, CLI y dos corridas nuevas

VE-7, lote C (2026-11-20, rama `claude/ve7-lote-c`, sobre `cb15e32`), implementa los ítems C1 a C6
del triaje VE-7 y, después, el dictamen Fable sobre el lote (2026-11-20). Decisión del consultor
Fable (triaje VE-7, 2026-11-20): Fable decidió QUÉ hacer; estas fichas dicen cómo se hizo. Los documentos generados (manifiestos,
`trazabilidad.csv`, `indice_formulas.md`) no se regeneran aquí: los sella el integrador.

## VE7C-01 · `E060.22.10.2.2#VOLADIZO` con cita propia, firmada en A11 (C1; VE6M9-01 (c))

- **Cerrado (decisión del consultor Fable, triaje VE-7, 2026-11-20):** el registro tiene la cita
  `E060.22.10.2.2#VOLADIZO` (pág. 195, EXIGENCIA: «será necesario») con el `Verbatim` «En
  elementos en voladizo con una longitud mayor a la mitad de su peralte, será necesario
  verificar las resistencias en flexión y corte», el mismo que T-7a transcribió en la nota de
  `E060.22.10.2#CICLOPEO` (firmada). `F9.CICLOPEO` la cita. Test:
  `tests/test_ve7_lote_c_voladizo.py`.
- **Abierto (hasta A11; cerrado, ver abajo):** la cita NO llevaba firma: la sesión no tenía `NORMAS_DIR`. Estuvo en
  `CITAS_SIN_FIRMA_A_PROPOSITO` por una segunda razón, distinta de la paginación sin medir
  (`SIN_FIRMA_POR_SESION_SIN_PDF`, que exige que el `Verbatim` sea literalmente el de la nota
  de origen firmada, entrecomillado, de la misma fuente y página). La cita principal de C7
  en M9 siguió siendo `E060.22.10.2#CICLOPEO` hasta firmar.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: la exención caduca (trinquete
  `MAX_SIN_FIRMA_POR_SESION_SIN_PDF` = 1; con `NORMAS_DIR`,
  `test_con_el_pdf_enlazado_no_queda_cita_sin_firma_por_sesion` exige firmarla) y no sostiene
  sola nada (`test_una_cita_sin_firma_por_sesion_no_sostiene_sola_nada`: otro apoyo firmado del
  verbo, y ningún literal en `src/modulos/`).
- **Cerrado en A11 (cierre de VE-7, 2026-11-20):** la sesión de cierre enlazó `NORMAS_DIR`
  (clon de `Andy-rba30/Normas`), extrajo la página 195 de E.060 y el `Verbatim` casa letra por
  letra; la cita se firmó (`VE7_A11`), salió de `CITAS_SIN_FIRMA_A_PROPOSITO` y
  `SIN_FIRMA_POR_SESION_SIN_PDF` quedó vacío (trinquete a 0). La cita principal de C7 en M9
  es ahora `E060.22.10.2.2#VOLADIZO`, seguida de `E060.22.10.2#CICLOPEO`; ningún número cambia.
  Tests: `test_A11_*` en `tests/test_ve7_lote_c_voladizo.py` y el orden en
  `tests/test_ve5_m9_ciclopeo.py`. Manifiestos, trazabilidad e índice regenerados en el sello.
- **Qué haría falta:** nada: cerrado en A11.
- **Dónde vive:** `src/normativa/citas.py::E060_22_10_2_2_VOLADIZO`

## VE7C-02 · `F9.LONGITUD`: la cercanía a la longitud aproximada es recomendación y la juzga el refinamiento (C2)

- **Cerrado (decisión del consultor Fable, triaje VE-7, 2026-11-20):** el `por_que` de
  `F9.LONGITUD` decía «la fuente pide que quede cerca de la aproximada», que bajo el verbo
  OBLIGA se leía como exigencia. Ahora dice que es recomendación («should», HDS-5 3.3.5) y que
  la juzga `F9.REFINAMIENTO_LONGITUD` (RECOMIENDA desde VE-6). El verbo no cambia: el paso
  aplica «must be fitted» (`HDS5_3ED.3.3.5#ENCAJE`, EXIGENCIA). Test:
  `tests/test_ve7_lote_c_longitud.py`.
- **Abierto:** cambia el texto de la memoria de los puntos con cabezal (paso 9.0.5) y, por
  eso, los documentos generados que lo transcriben; ningún número cambia.
- **Qué haría falta:** regenerar `indice_formulas.md` en la integración.
- **Dónde vive:** `src/normativa/fundamentos.py::LONGITUD_ENTRE_CABEZALES`

## VE7C-03 · `COND-SELVA-ALTA` se resuelve con el [S] `region_natural` (C3; VE5-CAT-01)

- **Cerrado (decisión del consultor Fable, triaje VE-7, 2026-11-20):** la condición del núm.
  4.1.1.3.7 a) del Manual de Hidrología pasó de `PorExpresion("region == 'selva_alta'")`, sobre
  un símbolo que nadie entregaba, a `PorDatoDeSitio("region_natural")`, el [S] de corredor que
  `M2.piso_de_selva_alta` ya lee desde VE-5. El efecto (EXCLUYE) y la cita no cambian; la
  justificación nombra el dato. La ventana normativa la da por resuelta «por dato de sitio».
  `test_una_condicion_que_no_bloquea_deja_elegir_con_su_justificacion` pasa a ejercitar
  `COND-DMIN-CANAL-RIEGO`, que sigue siendo expresión. Test:
  `tests/test_ve7_lote_c_selva_alta.py`.
- **Abierto:** `docs/manifiesto_registro_normativo.md` sigue transcribiendo la expresión
  anterior hasta que se regenere; los puntos (1) y (2) de VE5-CAT-01 (piso del catálogo y no
  equiparar 1200 mm con Ф 48”) no se tocan aquí.
- **Qué haría falta:** regenerar los manifiestos en la integración.
- **Dónde vive:** `src/normativa/citas.py::MC_HHD_4_1_1_3_7a`

## VE7C-04 · La Fase 0-bis con sección propia en la memoria y clave `licuefaccion` en el JSON (C4; VE5-CAT-03)

- **Cerrado (decisión del consultor Fable, triaje VE-7, 2026-11-20):** el JSON del punto lleva
  `licuefaccion` (`cli._licuefaccion_json`, a partir de `InformePunto.licuefaccion`): código,
  numeral, estado, `cumple`, resultado del EMS, lo exigido, criterio, motivo de «no aplica» y
  avisos; `null` si la fase no corrió (perfil, punto sin clasificar) o su etapa se bloqueó. La
  memoria del punto lleva la sección «Fase 0-bis» detrás de la clasificación
  (`M11._bloque_licuefaccion`) con esos mismos textos y el paso `F0.LICUEFACCION`; bloqueada a
  expediente, lo dice y remite a la tabla de bloqueos; a perfil no hay sección (la constancia
  del diferimiento ya está en esa tabla). `traza_licuefaccion` entra a `pasos_del_punto` y a
  `pasos_impresos` (y al recorrido gemelo de `test_memoria_sustentada`). Las guardias de T-10
  se cumplen: todo texto del JSON está en el bloque del punto. Test:
  `tests/test_ve7_lote_c_licuefaccion.py`.
- **Abierto:** la línea base y los documentos generados cambian al regenerarse (clave nueva y
  línea de la CLI). La línea de la CLI y el comparador: ficha VE7C-08.
- **Qué haría falta:** regenerar la línea base en la integración.
- **Dónde vive:** `src/modulos/M11_reporte/bloques_punto.py::_bloque_licuefaccion`

## VE7C-05 · `cli.py --estado-expediente`: las discrepancias abiertas y las corridas para comparar (C5; VE5GUI-45)

- **Cerrado (decisión del consultor Fable, triaje VE-7, 2026-11-20):** la bandera imprime lo que
  `src/estado_del_expediente.py` ofrece: las discrepancias abiertas contra la hoja de ruta
  (`discrepancias_abiertas`, una línea cada una con `DiscrepanciaAbierta.linea`) y, con
  `--sesion`, las corridas embebidas que se pueden comparar, la más reciente primero
  (`corridas_para_comparar`, índice y rótulo). Como `--comparar`, no corre el pipeline ni lee
  el CSV; la sesión se lee y se valida, pero no se aplica. Sale con 0, o con 2 si la sesión no
  se pudo leer o no es válida. Test por subprocess: `tests/test_ve7_lote_c_estado_expediente.py`.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: sale con 0 aunque haya
  discrepancias abiertas: es informe, no puerta (dicho en la ayuda y en el docstring; sin modo
  estricto).
- **Abierto:** la comparación de dos
  corridas embebidas sigue siendo de la ventana: la CLI compara volcados en disco
  (`--comparar A.json B.json`).
- **Qué haría falta:** si se pide, `--comparar` con dos índices de corrida de la sesión.
- **Dónde vive:** `cli.py::_imprimir_estado_del_expediente`

## VE7C-06 · Corridas de referencia cuarta y quinta: de 39 fundamentos sin paso a 2 sin ninguna puerta (C6; VE5GUI-47; dictamen Fable (i-a), (i-c), C6)

- **Cerrado (decisión del consultor Fable, triaje VE-7 y dictamen, 2026-11-20):** dos corridas
  nuevas a expediente con datos de PRUEBA rotulados y LEEME. `materiales_y_ramas`: TMC y HDPE
  hasta la Fase 8, ciclópeo, filtro, socavación, `FH.RM_*` y ocho más (22). `regimenes_alternos`:
  el juego de T-11 con los regímenes alternos de los criterios de toda la corrida (remanso por
  perfil, desborde, `concreto_afinado`, selva alta) y tres puntos dedicados (caída recta,
  relleno somero, piso de HW) (9). El índice cuenta las tres puertas de
  `test_memoria_sustentada` (paso, elección, bloque fijo; §4.1 y §4.2, cuatro recuentos) y dice
  por corrida qué NO cumple (`raices_que_no_cumplen`): la corrida no es un diseño. Medido: de
  154, con paso 145, por elección 6, por bloque fijo 1 (`F3.D_MIN`, que no se retira), sin
  puerta 2. Tests: `tests/test_ve7_lote_c_cuarta_corrida.py`.
- **Revisado por Fable (dictamen del consultor, 2026-11-20):** aprobado con cambios, aplicados: la cuarta no cumple A7,
  E1/E3 (A-01), C2/C3/C7/C8, E1/E3 (A-02) y A2 (Fase 8, heredado del marco de
  `hidrologia_calculada`), A7, E1/E3 (C-01); la quinta, A2 en C-01. Censado por igualdad.
- **Abierto:** sin puerta quedan `F6.TW_ALTO` (V1 con `no_cumple` no deja TW sobre la clave) y,
  desde la integración del lote B, `FH.C_SUBAREAS` (ningún `cuencas.csv` de referencia trae la
  columna `subareas`). Trinquete `MAX_SIN_EJERCITAR` = 2.
- **La divergencia del peralte (depuración VE-7, medido):** diferencia legítima de datos, no
  defecto: con «exacto» de archivo (decisión 9) el talón de A-01 no hace crecer el peralte; sólo
  «peso_entero» lo hace. La medición, los dos hallazgos y la corrección del docstring de
  `M9.solicitaciones_de_resistencia` están en el docstring de
  `tests/test_ve7_lote_c_cuarta_corrida.py::test_ic_el_peralte_sin_puerta_es_por_el_metodo_del_talon`.
- **Cerrado (VE-7 fix-suite, medido; dictamen Fable: la corrida ejercita fórmulas, no es un
  diseño válido):** A-04 de la quinta no cumple `E3-LRFD.sis.s.alero.100` (zapata de los aleros
  al tope 1.5·H_c; la app avisa «ZAPATA DE LOS ALEROS NO FACTIBLE»). Censado por igualdad
  (`NO_CUMPLE_EN_LA_QUINTA`, `CODIGOS_QUE_NO_CUMPLEN_EN_A04_DE_LA_QUINTA`); los datos no se
  cambian.
- **Qué haría falta:** regenerar y sellar `docs/indice_formulas.md`; si se quiere puerta para
  `9.3.p.*` en una corrida de referencia, declarar «peso_entero» en la quinta (su ventana lo
  admite) y re-medir su censo de lo que no cumple — decisión del consultor.
- **Dónde vive:** `src/indice_formulas.py::CORRIDAS_DE_REFERENCIA`

## VE7C-07 · test_c7: la sesión v3 difiere por clases con causa, no sólo por la huella (dictamen Fable (v))

- **Cerrado (dictamen Fable, 2026-11-20):** la expectativa de `test_c7` pasa a
  `_diferencia_admitida`, por clase: (1) la huella de criterios; (2) criterios nuevos del
  archivo, sus recuentos y el concepto de `n_manning_cajon`; (3) el [S] nuevo `region_natural` y
  sus recuentos; (4) las notas del cabezal; (5) el bloqueo de la Fase 0-bis (VE-5), EXIGIDO en
  los cuatro puntos; (6) tras el comparador cerrado, `compatibilidad_rasante` y la raíz
  `metrados` que v3 no tenía, y `avisos[len]` sólo si el único texto nuevo es
  `AVISO_CIMENTACION_PROVISIONAL` (el recorrido registra los dos valores y los avisos por
  punto). Invariantes: nada no comparable, ningún punto de un solo lado, nada en diseño,
  verificaciones, iteraciones ni `dimensionado`. El fixture v3 no se regenera.
- **Abierto:** otro lote que sume claves o avisos añade una clase: se mide y se registra.
- **Qué haría falta:** nada, mientras v3 sea la sesión de la versión anterior.
- **Dónde vive:** `tests/test_ui4_recorrido_ventana.py::_diferencia_admitida`

## VE7C-08 · Comparador cerrado, línea de la Fase 0-bis en la CLI y la ventana sobre las cuatro (dictamen Fable (ii), (iii), (iv))

- **Cerrado (dictamen Fable, 2026-11-20):** (ii) `comparador._comparar_punto` compara toda
  clave del punto (las de regla propia: `id`, `diseno`, verificaciones, bloqueos, iteraciones;
  el resto por valor) y `comparar`, toda clave raíz sin regla (`metrados`); una corrida
  embebida antigua dice DIFIERE nombrando las claves que le faltan
  (`tests/test_ve7_comparador_cerrado.py`). (iii) `cli._lineas_licuefaccion`: código, numeral,
  estado, EMS, lo exigido, criterio y el motivo de «no aplica»; «no evaluada (ver bloqueos)» si
  la etapa se bloqueó. (iv) el recorrido de la ventana es un bucle sobre toda corrida con
  declaraciones: la cuarta entra por la pestaña 2 (17/17) y su volcado es el de la CLI.
- **Abierto:** la línea base cambia (`cli_expediente.txt`, JSON): la regenera el integrador.
- **Qué haría falta:** regenerar la línea base.
- **Dónde vive:** `src/comparador.py::CLAVES_DEL_PUNTO_CON_REGLA_PROPIA`
# Parte LXIV — Lo que VE-7 (lote B) dejó escrito: la progresión, el pórtico, los metrados y la hidrología

## VE7B-01 · El arranque de la progresión lo valida M2 sobre el criterio (cierre de T11-03 (6))

- **Cerrado (VE-7 lote B, B12):** un `inicio` de 'diametros_normalizados' no positivo lo rechaza
  `M2.siguiente_diametro` antes de construir ningún escalón, con `DatoInvalidoError` sobre
  `campo='diametros_normalizados'` (`M2._exigir_arranque_positivo`, forma MAT-D13: `not inicio > 0`).
  Hasta VE-7 lo rechazaba la sección sobre el dato `D`, que el usuario no escribió. Como el campo es
  un criterio, `MD.disenar_punto` lo trata por `_exigir_criterios_validos` (bloqueo DATO_INVALIDO con
  la clave). La puerta del criterio sigue sin acotar el inicio: el consumidor lo hace.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** validar en M2 con el campo del
  criterio. Verificado antes: no estaba (la puerta lo dejaba pasar a propósito y M3 lo rechazaba).
- **Revisado por Fable (dictamen del consultor, 2026-11-20): conforme, aplicado sin cambios.**
- **Abierto:** la línea base de la rama de error (`tests/linea_base_familia_c/`, corrida 3) cambia
  de texto («Dato invalido en 'diametros_normalizados'»): el test la fija y la regeneración queda
  para la integración, porque los archivos de la línea base llevan además la huella de los
  criterios, que cambia con cada lote. El inválido de antes de la Fase 5 que detiene a UN material
  sigue sin bloquear ni decidir (T11-03 (6), primera mitad).
- **Qué haría falta:** regenerar la línea base al integrar (`sh tests/linea_base_familia_c/regenerar.sh`).
- **Dónde vive:** `src/modulos/M2_material.py::_exigir_arranque_positivo`

## VE7B-02 · La pared del diámetro inglés convertido es la de su designado (cierre de VE2-G (2))

- **Cerrado (VE-7 lote B, B9):** si 'espesor_pared_conducto' no trae la fila del diámetro redondeado
  al mm (1067 para 1.0668 m), `M2.espesor_pared` lee la del designado de la misma fila de AASHTO
  M 170M Table 6 (`M2.diametro_designado`: 1050). Fundamento: el núm. 12.1 (`AASHTO_M170M.12.1`,
  «the designated diameter or the converted English diameter») trata a los dos como el MISMO tubo
  de la serie. Una fila declarada para el inglés gana; un diámetro sin fila ni designado sigue
  deteniéndose con `DatoFaltanteError`. Con la progresión de archivo no se mueve ningún número.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** leer la fila del designado cuando no
  existe la del inglés.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defecto 10, aplicado.** El paso de V7
  imprime «fila leida: 1050 (designado de 1067)» (`M2.fila_de_pared_leida`).
- **Abierto:** las seis filas de 2850 a 3600 de la Table 6 siguen ilegibles (VE2-G (3)).
- **Qué haría falta:** otro ejemplar de M 170M.
- **Dónde vive:** `src/modulos/M2_material.py::espesor_pared`

## VE7B-03 · La regla del escalón más bajo vale también en la rama «no cabe» (cierre de T11-03 (5))

- **Cerrado (VE-7 lote B, B1):** en el `except` de `MD.disenar_material`, si el escalón no cabe bajo
  la subrasante (`_escalon_sin_cabida`) y queda en la progresión uno MÁS BAJO
  (`_escalon_restante_mas_bajo`, la regla de G1 de VE6-34), el escalón se registra con «queda un
  escalón más bajo… la progresión sigue» y la progresión continúa; el material se descarta por
  rasante sólo si no queda ninguno. En el tubo (progresión ascendente) nunca lo hay y la traza es
  idéntica, palabra por palabra (`tests/test_ve7_lote_b_md.py`). Si recorrer el resto levanta un
  `ErrorProyecto`, se lee «ninguno» (`_mas_bajo_o_ninguno`): era lo que el bucle hacía antes.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** registrar y seguir; descartar por
  rasante sólo sin escalón más bajo.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): abierto (iii), aplicado.** Si tras un
  escalón sin cabida (o sin cobertura de G1) que dejó seguir la progresión el catálogo se agota sin
  cerrar, el material sale POR RASANTE con el escalón de menor delta (`MD._el_de_menor_delta`) y
  «los escalones más bajos que quedaban no cierran»; `disenar_punto` toma ALGÚN escalón con
  `sin_cabida`, no sólo el último, y el punto lleva su delta. La traza del tubo no cambia.
- **Abierto:** ninguno propio; el delta sigue siendo cota inferior para ese escalón (T11-03).
- **Qué haría falta:** nada más para esta ficha.
- **Dónde vive:** `src/modulos/MD.py::_mas_bajo_o_ninguno`

## VE7B-04 · El delta del resguardo bajo control de salida, con el HW de entrada (cierre del abierto de VE6-34)

- **Cerrado (VE-7 lote B, B2; VE3-08 H3a):** el escalón que no cabe y sólo incumple V4 bajo control
  de SALIDA recibe el delta de 7.A calculado con `resultado.HW_entrada`
  (`MD._delta_del_resguardo_bajo_salida`). Es cota inferior rigurosa sin iterar 7.A con 7.B: el HW
  gobernante es el mayor de los dos (`HDS5_3ED.3.3.5#GOBIERNA`, pág. impresa 3.25) y el de entrada
  no depende de la longitud. La nota lo dice («cota inferior con el HW de entrada») y da el HW
  gobernante de hoy. Si con el HW de entrada el resguardo ya cabe, se conserva el mensaje anterior
  (`MENSAJE_SIN_DELTA_BAJO_SALIDA`).
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** el HW de entrada como cota inferior.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): conforme, aplicado sin cambios.**
- **Abierto:** el delta con el HW gobernante real exigiría iterar 7.A con 7.B (la longitud crece con
  la rasante); no se hace.
- **Qué haría falta:** una pasada de MD con la rasante y la longitud nuevas.
- **Dónde vive:** `src/modulos/MD.py::_delta_del_resguardo_bajo_salida`

## VE7B-05 · El largo del área cargada sobre el tubo de concreto somero: el del neumático, valor de archivo (VE4F-01)

- **Cerrado (VE-7 lote B, B8):** `carga_viva_tubo_concreto_somero` [A] de perfil tiene valor de
  archivo `largo_del_neumatico` (L_T). Es el área menor y la presión mayor: con el camión las dos
  lecturas cargan igual, y con el tándem sobre tubos de B_c entre s_a = 1.22 m y s_a + E_span =
  1.82 m el segundo eje entra antes y entero, de modo que W_L(L_T) ≥ W_L(E_span). El comentario de la
  franja permite despreciar el aumento por el relleno (`AASHTO_LRFD_9.C4.6.2.10.2#E_SPAN`,
  PERMISO): es la cota superior. `e_span_a_un_pie` sigue en la ventana. Censos: sale de los
  criterios de perfil sin valor (`tests/test_criterios_adoptados.py`, `tests/test_cierre_perfil.py`)
  y de la tabla y el ejemplo de `docs/guia_perfil.md` (editados a mano, sin regenerar la guía).
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** L_T como valor de archivo, por el
  lado seguro.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): conforme, aplicado sin cambios.**
- **Abierto:** los tubos de concreto con menos de 1.0 ft y bajo pavimento rígido de 9 a 12 in
  siguen sin método (ficha VE4F-01).
- **Qué haría falta:** una disposición de AASHTO o del Manual de Puentes que fije el largo; si el
  dueño prefiere la otra lectura, declararla.
- **Dónde vive:** `src/modulos/M8_estructural.py::lectura_del_tubo_de_concreto_somero`

## VE7B-06 · El coeficiente de escorrentía ponderado por subáreas (cierre de VE5-MH-01)

- **Cerrado (VE-7 lote B, B10):** columna opcional `subareas` del CSV de cuencas, con Σáreas = el área
  de la cuenca (`TOL_REL_AREA_ESCRITA_DOS_VECES`; si no, `DatoInvalidoError` sobre `subareas`), y
  C = ΣC·A/ΣA (`coeficiente_ponderado`, fundamento `FH.C_SUBAREAS`: superposición de la ecuación (28)
  con la misma I y tc, sobre `MC_HHD.3.12.2`). Sin la columna, todo igual.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): decisión 1 y abierto (i), aplicados.** El
  C tecleado se rechaza (`FH.C`: el programa no acepta un coeficiente tecleado): la forma es
  «cobertura/suelo[/S_terreno]:area_ha» y, en una superficie vial, «cobertura:area_ha», con los
  validadores de `cargar_cuencas` (`MH._subareas`, `Cuenca.subareas` de cuatro campos). Cada C_k sale
  de su tabla (`MH._paso_c_por_subareas(cuenca, TR)`): la Tabla Nº 08 con la S de la subárea o la
  `S_terreno` de la cuenca, o la tabla vial con su incremento por periodo de retorno; el paso imprime
  cobertura, suelo, S, columna, C_k, A_k y la laguna del 1 %. Con `subareas`, `cobertura` y `suelo`
  de la fila van vacíos (con valor, «contradice a otro dato»). La memoria ya no nombra la Eq. 2-4.
- **Abierto (bloqueo declarado):** la Eq. 2-4 del WSDOT Hydraulics Manual no se nombra hasta tener el
  PDF de WSDOT y registrar su cita; `FH.C_SUBAREAS` se sostiene con `MC_HHD.3.12.2`.
- **Qué haría falta:** el PDF de WSDOT y la cita de la Eq. 2-4.
- **Dónde vive:** `src/modulos/MH_hidrologia.py::coeficiente_ponderado`

## VE7B-07 · La región pluvial de la Tabla Nº 34 como [S] opcional (cierre de VE5-CAT-02)

- **Cerrado (VE-7 lote B, B11):** `precipitacion_anual_corredor_mm` es un [S] de corredor OPCIONAL
  (estudio hidrológico, sin valor; `DatoSitio.opcional`, fuera de `datos_sin_valor()`, leído con
  `ds.valor_si_declarado`). Declarado, `M10.capacidad_cuneta` toma SU fila
  (`fila_de_la_tabla_34`, límites [N] `CUNETA_PRECIPITACION_MIN_FILA_T34` de los rótulos) y exige
  sus mínimos (`_contrastar_con_la_tabla_34`): con > 3000 mm/año la triangular es
  `DatoInvalidoError` y la trapezoidal pide 0.30 × 1.20 con fondo 0.30; con 500 mm/año, 0.30 ×
  0.75. Sin declarar: aviso «fila de la Tabla Nº 34 no verificada» y lo de siempre. Con fondo,
  el piso de `profundidad_m` baja a 0.30 en la puerta (`criterios_adoptados._PISO_CONDICIONADO`);
  la triangular sigue en 0.40 y las esquinas de la ventana siguen siendo válidas.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** [S] opcional, contraste contra su
  fila y aviso sin él.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): 2a y 2b, aplicados.** (2a) 3000 mm/año
  exactos van a la trapezoidal por la convención de límite inferior cerrado de los rótulos (no por
  ser la más exigente: 0.30 × 1.20 con fondo 0.30 = 0.225 m² < 0.24 m² de la triangular 0.40 × 1.20),
  y la nota del paso dice que la fuente no cubre ese valor. (2b) Sin la precipitación, una
  trapezoidal de menos de 0.40 m se detiene: `DatoFaltanteError` sobre
  `precipitacion_anual_corredor_mm` (esa profundidad sólo la concede la fila de más de 3000).
- **Abierto:** (1) con la precipitación de una fila seca o lluviosa, una triangular más chica que
  0.40 × 1.20 sólo entra pisando la ventana del criterio (la puerta no ve el [S]); (2) el editor de
  la pestaña 2 valida cada campo con su ventana (0.40): la trapezoidal de 0.30 entra por el literal y
  por la CLI.
- **Qué haría falta:** una ventana del criterio que dependa de un [S] declarado por sesión.
- **Dónde vive:** `src/modulos/M10_espaciamiento.py::fila_de_la_tabla_34`

## VE7B-08 · Lo que la Fase 11 no metra sale como renglón «no medido» (VE5-MET-01)

- **Cerrado (VE-7 lote B, B7):** el relleno para estructuras (502.A), la cama de apoyo y el
  revestimiento de la entrada (emboquillado, sólo si el punto tiene protección de entrada) salen,
  en cada punto metrado, como `Bloqueo` de `servicio.FASE_METRADOS` con la etapa
  «metrado de …: no medido» (`M12.etapa_no_medido`), `MetodoNoEvaluableError` con
  `MOTIVO_METODO_NO_EVALUABLE_METRADO`, el motivo («no medido: …») y lo que haría falta para medirlo
  (`M12.RENGLONES_NO_MEDIDOS`). Es la regla de `modelos.MetradoDelPunto` («un renglón que no se pudo
  medir … es un `Bloqueo`»): el cuadro ya no los omite en silencio y los demás rubros siguen.
  `servicio._fase_11_metrados` suma el bucle (cambio mínimo en `servicio.py`).
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** renglón explícito «no medido» con
  motivo en la fase de los metrados.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defecto 7, aplicado.** En una tubería
  la cama la paga la partida del tubo (nota del paso 11.1): el «no medido» de la cama sale sólo en el
  marco. Desde (ii-b.3), también el de la distribución de la losa superior cuando es obligatoria.
- **Abierto:** a expediente el punto con cabezal ya no queda sin bloqueos de la Fase 11 mientras
  estas partes no se metren: es lo que la decisión pide decir. Su medición sigue sin hacerse.
- **Qué haría falta:** la sección del relleno y de la cama de los planos; la geometría del
  zampeado y del dentellón de la entrada (ficha T8-03).
- **Dónde vive:** `src/modulos/M12_metrados.py::renglon_no_medido`

## VE7B-09 · Las caras del pórtico que no se traccionan llevan el mínimo de 5.10.6 (T5-07 (3))

- **Cerrado (VE-7 lote B, B4):** la cara que ninguna combinación de resistencia tracciona lleva una
  `FilaDeArmado` de retracción y temperatura (`DisenoPortico.minimos`, `M8._minimo_de_la_cara`): la
  fila de reparto del cabezal, `M9._fila_de_reparto`, importada sin modificarla (5.10.6 y E.060 9.7.2
  con la regla del más exigente), con su barra. 12.11.5.3.1 lo manda (nota de la cita
  `AASHTO_LRFD_9.12.11.5.3.1`). Paso `F8.PORTICO_MINIMOS`. Toda cara de toda sección tiene acero.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defecto 3, aplicado.** 5.10.6 se
  calculaba con b = h; ahora con el ANCHO REAL del elemento, el largo del miembro entre ejes
  (`M8.largos_de_los_miembros`), como la decisión 3 del dueño en O-2 para el cabezal: en las caras de
  mínimo y en las armadas (`ancho_seccion` de `M9.diseno_flexion_corte`). El oráculo discrimina con
  t = 0.40 y la regla «solo AASHTO».
- **Abierto:** el desarrollo y los empalmes siguen fuera (`M8.DIFERIDO_PORTICO`); el acero
  longitudinal y la distribución, en la ficha VE7B-12.
- **Qué haría falta:** transcribir 5.10.8 para el pórtico.
- **Dónde vive:** `src/modulos/M8_estructural.py::_minimo_de_la_cara`

## VE7B-10 · El agua exterior del pórtico con el freático sobre la losa inferior (T5-07 (5))

- **Cerrado (VE-7 lote B, B3):** con el nivel sobre el eje de la losa inferior
  (`M8._agua_exterior_del_portico`) el pórtico suma `WA_ext` (hidrostático en las paredes) y el EH
  bajo el nivel con el peso SUMERGIDO, en dos tramos lineales (el diagrama del ensamble de M9), con
  las citas del agua del ensamble (`AASHTO_LRFD_9.3.11.3`, `MP.2.4.4.1.3#SUMERGIDO`). Exige
  `peso_especifico_saturado_relleno_kn_m3`. `WA_ext` entra con γ_WA en el horizontal máximo y no en
  el del agua interior. La subpresión no flexa (reacción lineal; lectura declarada). Con el nivel
  bajo la losa, los números de antes. Oráculo de pendiente-deflexión (1 %).
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defectos 1 y 2 y decisión 3,
  aplicados.** (1) El nivel es el de V7: lectura + `margen_estacional_nf_v7_m` si está declarado
  (negativo, `DatoInvalidoError`); sin él, la lectura cruda y el aviso «nivel sin ascenso
  estacional». (2) Un nivel sobre la rasante es `DatoInvalidoError('NF_profundidad_m')`. (3) Con el
  nivel sobre la losa superior, envolvente seco/sumergido: `EV_sum` = F_e·(σ′_v − σ_v) con γ_EV y
  `WA_sup` = γ_w·d_w con γ_WA (η donde el EV va al máximo), en combinaciones DUPLICADAS con el
  sufijo `SUFIJO_SUMERGIDO`; el paso imprime d_w, w_EV,sum y w_WA,sup.
- **Abierto:** sin `NF_profundidad_m` el agua exterior no se evalúa (la columna la debe el EMS).
- **Qué haría falta:** la lectura del freático en cada punto de marco.
- **Dónde vive:** `src/modulos/M8_estructural.py::_agua_exterior_del_portico`

## VE7B-11 · El pórtico que no cumple dice qué canto declarar, y no se lo auto-adopta (T5-07 (1))

- **Cerrado (VE-7 lote B, B5):** si A1–A6 del pórtico no cumplen, `M8.disenar_portico` busca
  (`_con_el_canto_que_cierra`) en la grilla de `dimensionamiento_zapata_cabezal` (su `paso_m`, el del
  cabezal; aritmética decimal de `M2._escalon_de_la_serie`) el MENOR canto uniforme t_k = t_0 + k·paso
  con el que cumple, con la sección interior fija y el relleno sobre la clave reducido en Δt (la losa
  superior crece hacia arriba); el tope es físico (el relleno reducido > 0) y lo que no se puede
  evaluar termina la búsqueda. El `DisenoPortico` sigue siendo el de t_0 y lleva
  `canto_que_cierra_m`, `canto_buscado_hasta_m` y el paso `F8.PORTICO_CANTO`. La etapa del servicio
  llama a `exigir_canto_del_portico`: `DatoInvalidoError` sobre `espesor_pared_cajon` con «declarar
  `espesor_pared_cajon` >= X m y repetir» (cambio mínimo en `servicio._fase_8`). No se adopta porque
  ese canto forma la clave física, V4, V7 y G1. Oráculo: el canto impreso, declarado con el relleno
  reducido, cierra el pórtico; el anterior de la grilla no.
- **Decisión del consultor Fable (triaje VE-7, 2026-11-20):** buscar y decir, no iterar.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defecto 9, aplicado.** El bloqueo y el
  paso dicen «= X m (el menor de la grilla que cierra)»; la búsqueda tiene tope
  (`tolerancias.ITERACIONES_MAX_CANTO_PORTICO`, 20 escalones) y el paso lo imprime.
- **Abierto:** el canto es uniforme; los cantos separados NO PROCEDEN (dictamen, (ii-a)). Con el
  canto declarado la corrida se repite entera.
- **Qué haría falta:** nada más mientras la geometría del programa tenga un solo canto.
- **Dónde vive:** `src/modulos/M8_estructural.py::exigir_canto_del_portico`

## VE7B-12 · El acero del pórtico del marco se metra con sus armados (VE5-MET-01)

- **Cerrado (VE-7 lote B, B6):** `M12.renglones_acero_portico` mide el acero del pórtico (504.10,
  partida 504.A) con sus armados y la longitud de metrado del barril a lo largo del eje, Tabla 504-01
  (`EG2013.504.01#PESOS`), tras la puerta `incremento_acero_por_despiece`. `servicio._fase_11_metrados`
  pasa `estructural.portico`; el aviso del acero del marco sólo sale sin pórtico.
- **Revisado por Fable (dictamen del consultor, 2026-11-20): defecto 4 y (ii-b), aplicados.** (a) El
  LONGITUDINAL mínimo de 5.10.6 (12.11.5.3.1) se diseña (`DisenoPortico.longitudinales`, la fila de
  reparto de M9 con el ancho real, paso `F8.PORTICO_LONGITUDINAL`) y se metra: Σ (largo/s)·L_eje·w.
  (b) La barra transversal mide largo entre ejes + canto − 2·recubrimiento (el menor de los armados
  del miembro: lado seguro; `M8.espesores_de_los_miembros`). (c) Un pórtico que no cumple no se
  metra: `MetodoNoEvaluableError` «armado no cerrado». (ii-b.3) Con menos de 2.0 ft hasta la rasante
  la distribución de la losa superior es obligatoria: `M8.exigir_distribucion_del_portico` bloquea la
  etapa del pórtico y M12 da el renglón «no medido» de la distribución (9.7.3.2).
- **Abierto (bloqueo declarado):** 9.7.3.2 no está en el registro; al transcribirla, incluir también
  5.12.2.1 de la 9.ª ed. (exceptúa «culvert tops… fill exceeds 2.0 ft»; citado de memoria: verificar
  contra el PDF). Los cantos separados no proceden (dictamen, (ii-a)).
- **Qué haría falta:** transcribir 9.7.3.2 y 5.12.2.1 y diseñar la distribución.
- **Dónde vive:** `src/modulos/M12_metrados.py::renglones_acero_portico`

---

# Parte LXV — Lo que el plan de mantenibilidad y uso dejó escrito: archivos partidos, huella del catálogo y medida del `import cli`

Las tareas del plan (`proceso/planes_mejora/11_PLAN_MANTENIBILIDAD_Y_USO.md`)
no cambian ninguna fórmula ni ningún resultado (su sección 0). Lo que sí
cambia, y por eso se declara aquí, es dónde vive cada cosa y un valor
impreso que no es de cálculo: la huella de los criterios.

## D2-01 · Las fichas de criterios viven en `src/criterios/`, y la huella de criterios cubre el catálogo entero

- **Cerrado (plan de mantenibilidad, D2):** `criterios_adoptados.py` conserva
  sólo el MECANISMO (`Criterio`, `valor`, las guardias `_verificar_*`, el
  registro de usos, la declaración en caliente y la escritura permanente);
  las fichas pasan a `src/criterios/*.py` por dominio y se registran en el
  mismo `CRITERIOS`, en el mismo orden (`tests/test_d2_catalogo_de_fichas.py`).
  La escritura permanente y los mensajes de rango nombran el archivo real de
  la ficha (`ca.archivo_de_criterio`).
- **Por qué cambia la huella:** `ContextoCorrida.criterios_sha1` se calculaba
  sobre `criterios_adoptados.py`; con las fichas fuera, esa huella ya no se
  movía al cambiar un criterio, que es justo lo que tiene que delatar. Desde
  D2 es `ca.sha1_criterios()`: rutas relativas y bytes del mecanismo y de
  todos los `.py` de primer nivel de `src/criterios/`. **DECLARADO: su valor
  cambia respecto de toda corrida anterior a D2 aunque no haya cambiado
  ningún criterio**, de modo que comparar dos `informe_json` de uno y otro
  lado de D2 da la huella distinta sin que eso signifique otra decisión. La
  fecha de los criterios del encabezado de la memoria es la del archivo del
  catálogo modificado por última vez (`ca.archivo_de_criterios_mas_reciente`).
- **Qué haría falta:** nada para el cálculo. Quien compare una corrida previa
  a D2 con una posterior tiene que leer la diferencia de `criterios_sha1`
  como cambio de definición de la huella, no de criterio.
- **Dónde vive:** `src/criterios_adoptados.py::sha1_criterios`

## D3-01 · `modelos.py` partido en el paquete `src/modelos/`

- **Cerrado (plan de mantenibilidad, D3):** trece submódulos por familia de
  tipos, reexportados por `src/modelos/__init__.py` con los mismos nombres;
  el AST de los nodos es idéntico al del archivo único y la CLI y el JSON
  salen iguales byte a byte. `__module__` de cada clase se normaliza a
  `src.modelos`, porque la serialización del informe escribe
  `__module__:__qualname__` y una sesión guardada antes de la partición
  tiene que seguir abriéndose.
- **Por qué así y no importando cada submódulo:** ningún importador de fuera
  del paquete cambia (criterio de aceptación del bloque D), y el JSON de
  sesión no puede depender de en qué archivo quedó una clase.
- **Qué haría falta:** nada. Una clase nueva se declara en su submódulo y se
  añade a la reexportación; el bucle de normalización la cubre.
- **Dónde vive:** `src/modelos/__init__.py::_SUBMODULOS`

## D3-02 · `M11_reporte.py` partido en el subpaquete `src/modulos/M11_reporte/`

- **Cerrado (plan de mantenibilidad, D3):** dieciocho archivos más el
  `__init__.py` de reexportación (19 `.py`), todos de menos de 700 líneas; la
  memoria HTML, el CSV y el JSON salen idénticos byte a byte (salvo la fecha)
  en las cinco corridas de la línea base. Las guardias que
  barren el AST de M11 (no aritmética sobre magnitudes, lecturas estáticas
  de los catálogos) recorren el subpaquete entero
  (`tests/apoyo/fuente_m11.py`). Al integrar D2, la fecha de los criterios
  de la trazabilidad pasó a `ca.archivo_de_criterios_mas_reciente()` también
  aquí, y `ARCHIVO_CRITERIOS` quedó rotulado como el mecanismo.
- **Por qué:** era el archivo más largo de `src/` fuera del registro
  normativo, y el reporte es la capa que más se toca al pedir un cambio de
  presentación.
- **Qué haría falta:** nada.
- **Dónde vive:** `src/modulos/M11_reporte/trazabilidad.py::trazabilidad`

## D3-03 · `constantes_normativas.py` no se partió

- **Qué se difirió:** la tercera partición opcional del bloque D. La sesión
  que la empezó no dejó commit, y la integración la cierra sin ella.
- **Por qué:** es la casa única de los `[N]` y la constitución, la guardia de
  literales (`tests/test_sin_literales.py`), el manifiesto de citas (105
  anclas a sus renglones) y 34 archivos `.py` de `src/` y `tests/` la nombran
  por su ruta (156 la importan o la nombran). Partirla toca la regla de las tres casas,
  no sólo la organización del código, y no cambia ningún resultado: el
  beneficio de mantenibilidad no compensa el riesgo antes de la sustentación.
- **Qué haría falta:** decidir si la casa de los `[N]` pasa a ser un paquete
  (`src/constantes_normativas/` por norma, reexportado), enmendar la
  constitución y `test_sin_literales`, mudar las anclas del manifiesto como
  D2 mudó las de `criterios_adoptados.py`, y regenerar los documentos con
  diferencia nula salvo rutas.
- **Dónde vive:** `src/constantes_normativas.py::Y_SOBRE_D_MAX`

## EXT-8-06 · El presupuesto de `import cli` se mide con el mínimo de siete corridas

- **Qué se difirió:** subir el presupuesto de 0.30 s. El hallazgo H2 de la
  auditoría del cierre de VE-7 midió el test intermitente: en reposo el
  import cuesta 0.22–0.26 s, y con la suite en paralelo un mínimo de tres
  corridas no filtraba la carga (0.390 s en una corrida completa).
- **Por qué:** decisión del dueño: medir mejor y no relajar el límite. Lo que
  el test acota es el coste del import, no el ruido de la máquina; el mínimo
  de siete corridas en subproceso limpio es la medida de ese coste.
- **Qué haría falta:** si con siete vuelve a fallar en una máquina cargada,
  medir de nuevo en reposo antes de tocar el presupuesto: un import que de
  verdad pasa de 0.30 s es una regresión de PC-10, no ruido.
- **Dónde vive:** `tests/test_ext8_rendimiento_gui.py::CORRIDAS_IMPORTTIME`
