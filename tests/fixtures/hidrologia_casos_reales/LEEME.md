# DATOS DE CASO REAL PUBLICADO — no son datos de este proyecto

Entradas de la Fase 1-bis (`--cuencas`, `--estacion`) transcritas de seis documentos publicados
por la verificación independiente de la hidrología (dossier
`proceso/planes_mejora/ve3_estado/verificaciones_del_dueno/hidrologia/hidrologia_casos_reales.md`,
carpeta hermana `casos/`). Los PDF están en el repositorio de normas, en
`ejemplos_resueltos/casos_reales/<caso>/`.

- Cada CSV lleva en su cabecera el documento, la página y la tabla de donde sale cada columna.
- Lo que el documento NO publica y el verificador puso para que el archivo cargue está rotulado
  en la cabecera como «VEHÍCULO DEL VERIFICADOR» (`cobertura`, `suelo`, `S_terreno`: llevan a
  la Tabla N.º 08 al mismo C que el documento declara) o «DECLARACIÓN DEL VERIFICADOR» (la
  columna `fen` = «no» donde el documento no nombra años FEN). No son datos del caso.
- Los archivos son los de `casos/` del dossier con un único cambio: la primera línea dice
  «no son datos de este proyecto» (y la de Tumbes, que el programa avisa los años copiados desde
  la ficha VE3-19). Las cifras son las del sello `SHA1SUMS_congelado.txt` del dossier.
- Los usan `tests/apoyo/validacion_hidrologica.py` (que genera `docs/validacion_hidrologica.md`),
  `tests/test_validacion_hidrologica.py` y `tests/test_ve3_19_maximos_repetidos.py`.
