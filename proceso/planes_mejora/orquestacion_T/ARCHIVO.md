# Archivo de la orquestación de la cadena T

Material de proceso, no del entregable. Es la bitácora que la sesión orquestadora de la
cadena T (T-1 a T-12, noviembre de 2026) llevó en la rama `tesis/orquestacion-estado`,
que nunca se integró en `main`: estados, consumos, encargos a las sesiones hijas,
auditorías y los scripts de verificación de T-7c.

Se archiva aquí tal cual (VE-6, 2026-11-20) para que la rama pueda cerrarse sin perder
nada. Las rutas internas que mencionan `docs/planes_mejora/orquestacion_T/` se refieren a
esta carpeta: T-12 movió el material de proceso de `docs/` a `proceso/`.

Los scripts de auditoría (`aud_T-*_scripts/`) se guardan con extensión `.py.txt`: son
evidencia histórica, no código del proyecto. Con la extensión `.py` la guardia del paquete
(`tests/test_ext9_paquete_servicio.py`, que prohíbe tocar `sys.path`) los barría como fuente
viva. Para volver a correr uno, copiarlo fuera del repositorio y quitarle el `.txt`.
