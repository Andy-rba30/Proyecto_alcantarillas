"""
dominios.py
===========
Limites de dominio del dato de entrada. NO son valores de proyecto.

Cuarta categoria exenta de la regla "todo literal numerico fuera de
constantes_normativas.py y criterios_adoptados.py es un defecto", junto con
0/1/2 e indices, las constantes matematicas puras (pi) y las tolerancias
numericas de `tolerancias.py`.

Por que no son constantes normativas ni criterios adoptados
-----------------------------------------------------------
Una constante normativa responde a "que exige la norma" y llega con numeral.
Un criterio adoptado responde a "que decidio el proyectista donde la norma
calla", y por eso lleva etiqueta, justificacion, fuente y sensibilidad.

Un limite de dominio no responde a ninguna de las dos: responde a "que valores
puede tomar este dato antes de dejar de ser ese dato". Un CBR negativo no es
una subrasante mala, es una celda mal llenada; un esviaje de 120 grados no es
un cruce forzado, es un numero imposible. Ninguno entra en formula ni en
verificacion alguna: solo deciden si el CSV se puede leer. Declararlos como
criterios llenaria el bloque de M11 de parametros que no defienden ninguna
decision de diseno, y ponerlos en el Anexo B les inventaria un numeral que no
tienen.

Regla practica para saber si un numero va aqui: si cambiarlo puede alterar un
resultado del calculo, NO es un limite de dominio.

El archivo hospeda ademas las DEFINICIONES DE UNIDAD que el calculo necesita
para leer o escribir un dato (METROS_POR_KM, CENTIMETROS_POR_METRO). No son
limites de dominio en sentido estricto, pero responden a la misma pregunta --
que significa el numero que entra o sale, no cuanto vale una magnitud del
proyecto -- y cambiarlas seria redefinir la unidad, no ajustar un criterio.
Ninguna entra en formula de calculo: METROS_POR_KM traduce la notacion vial de
progresivas al leer el CSV y CENTIMETROS_POR_METRO escribe en centimetros el
delta de rasante que Sec. 7.B redacta en esa unidad.

Las marcas `# literal-ok` viajaron con los valores desde M0_carga.py. En este
archivo son redundantes -- el archivo entero esta exento del barrido -- pero se
conservan porque son la justificacion de cada numero, no un permiso.
"""

# Piso de la escala del CBR: es una proporcion en porcentaje y no puede ser
# nula ni negativa. NO TIENE TECHO AQUI, y hasta PF-6 lo tenia (R48-007):
# `CBR_MAX_FISICO = 100.0`, con el comentario «por encima de 100 el dato esta
# en otra escala o mal transcrito». Se retiro contra la fuente primaria,
# verificada pagina a pagina: el Manual de Suelos, Geologia, Geotecnia y
# Pavimentos (MTC) deja la categoria S5 de subrasante ABIERTA por arriba
# (Cuadro 4.11 «Categorias de Sub rasante», pag. impresa 37 / PDF 38: «S5 :
# Sub rasante Excelente | CBR >= 30%»), exige «Minimo 100%» a la base
# granular de carreteras de primera clase o trafico > 10 x 10^6 EE (Cuadro
# N 10.2 «Valor Relativo de Soporte, CBR en Base Granular», pag. impresa 108
# / PDF 109) y tabula «Base Granular CBR 100%» (Cuadro 12.13, pag. impresa
# 129 / PDF 130); en sus 281 paginas no hay techo alguno del CBR ni la
# expresion «piedra patron». Un techo que la fuente no fija es un valor de
# proyecto inventado, y este archivo solo acota lo que un dato PUEDE SER.
# Que el CBR sea alto o bajo no lo juzga este archivo; lo juzga la tabla de
# resguardo de Sec. 5.1, cuya fila mas alta es ilimitada.
CBR_MIN_FISICO = 0.0      # literal-ok: piso de la escala del CBR (proporcion en %, exclusivo)

# A 0 grados el cruce es perpendicular a la via. A 90 el eje del conducto seria
# paralelo al eje de la via y no habria cruce que resolver.
ESVIAJE_MAX = 90.0        # literal-ok: a 90 grados el conducto seria paralelo a la via

# Pendiente del cauce en m/m. Un valor >= 1 (100 %) delata una celda cargada en
# porcentaje: es el error de transcripcion mas frecuente de esta columna.
S_CAUCE_MAX = 1.0

# Conversion de la notacion vial de progresivas ('0+380') a kilometros.
METROS_POR_KM = 1000      # literal-ok: definicion de la unidad, no valor de proyecto

# Conversion a la unidad de presentacion del delta de rasante de Sec. 7.B, que
# la hoja de ruta redacta en centimetros ("no factible -> subir rasante X cm").
# Mismo caso que METROS_POR_KM: es la definicion de la unidad, no un valor de
# proyecto. El calculo entero sigue en metros; esto solo lo escribe.
CENTIMETROS_POR_METRO = 100   # literal-ok: definicion de la unidad, no valor de proyecto

# Conversion al DIAMETRO DESIGNADO de las normas de producto, que tabulan en
# milimetros enteros (AASHTO M 170M-04, ASTM A760, AASHTO M294) mientras el
# calculo trabaja en metros. Mismo caso que los dos anteriores: es la
# definicion de la unidad, no un valor de proyecto -- no dice que diametros
# existen, solo como se escribe el mismo diametro en la otra unidad.
MILIMETROS_POR_METRO = 1000   # literal-ok: definicion de la unidad, no valor de proyecto
