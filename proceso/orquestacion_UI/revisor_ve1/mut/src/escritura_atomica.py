"""
src/escritura_atomica.py
========================
ESCRIBIR UN ARCHIVO SIN DEJARLO NUNCA A MEDIAS (UI-5, decision del dueño del
2026-11-15, ficha UI2-03; corregido en la revision independiente de UI-5, H3).

Una exportacion que escribe directamente sobre su destino destruye, si falla a
mitad (disco lleno, cuota, E/S), el archivo que el usuario tuviera ahi: queda
cortado con el nombre del bueno. Aqui se escribe en un temporal del MISMO
directorio que el archivo real y solo al terminar se renombra encima con
`os.replace`, que en un mismo sistema de archivos es atomico: el destino es el
archivo anterior entero o el nuevo entero, nunca uno cortado.

La usan las dos escrituras de PDF del programa: la memoria (completa o
resumida) de `M11_reporte._escribir_pdf`, en la CLI y en el proceso hijo de la
ventana, y la entrega del PDF de ese hijo al destino que eligio el usuario
(`gui/exportacion_pdf.ProcesoPdf._entregar`, UI-2). Una sola funcion para las
dos: el primer intento de UI-5 tenia el patron escrito dos veces y con el
mismo defecto en las dos.

LO QUE LA REVISION DE UI-5 ENCONTRO EN EL PRIMER INTENTO (H3), que escribia
en «<destino>.parcial», un nombre FIJO derivado del destino, y que esta
funcion ya no hace:

  (a) un destino de nombre largo (248 a 255 bytes) no se podia escribir: el
      temporal pasaba del limite de nombre del sistema (Errno 36). El de aqui
      es CORTO y no depende del nombre del destino;
  (b) un archivo del usuario llamado «<destino>.parcial» se pisaba y se
      borraba. El de aqui es UNICO (`tempfile.mkstemp`, que lo crea en
      exclusiva) y OCULTO;
  (c) dos exportaciones al mismo destino compartian el temporal: una
      escribia sobre el archivo que la otra tenia abierto y la otra fallaba
      al renombrar. Con temporales unicos cada una deja su archivo entero, y
      gana la que termina despues;
  (d) un destino que es ENLACE SIMBOLICO se volvia archivo regular, y un
      archivo de modo 0600 pasaba a 0644. Aqui se escribe junto al archivo
      ENLAZADO y se reemplaza ese, y el modo del archivo previo se conserva;
      sin archivo previo, el modo es el de siempre (el que da la mascara del
      proceso al crear un archivo), no el 0600 con que nace el temporal.
"""

from __future__ import annotations

import errno
import os
import stat
import tempfile
from pathlib import Path
from typing import Callable

# El temporal: oculto (empieza por punto) y con el sufijo de los parciales
# del programa, de modo que un resto --- un proceso muerto a mitad --- se
# reconoce como tal. `mkstemp` le pone en medio una parte aleatoria corta.
PREFIJO_DEL_TEMPORAL = "."
SUFIJO_DEL_TEMPORAL = ".parcial"
# Los bits de permiso con que se crea un archivo regular nuevo, antes de la
# mascara del proceso: los de `open()` y de `Path.write_bytes`.
_MODO_DE_UN_ARCHIVO_NUEVO = 0o666   # literal-ok: permisos POSIX de un archivo nuevo antes de la umask


def archivo_real(destino: Path) -> Path:
    """
    El archivo que de verdad se reemplaza: el ENLAZADO si `destino` es un
    enlace simbolico (resuelto entero, tambien si el enlace apunta a otro
    enlace), y `destino` si no.
    """
    destino = Path(destino)
    return Path(os.path.realpath(destino)) if destino.is_symlink() else destino


def _modo_para(real: Path) -> int:
    """
    El modo que tiene que quedar: el del archivo previo, o, sin el, el de un
    archivo nuevo con la mascara del proceso. La mascara solo se lee
    poniendola: se pone y se repone en el acto. El programa no tiene hilos
    (ficha EXT-8-04), y por eso no hay otro hilo que cree un archivo en ese
    intervalo.
    """
    try:
        return stat.S_IMODE(os.stat(real).st_mode)
    except FileNotFoundError:
        mascara = os.umask(0)
        os.umask(mascara)
        return _MODO_DE_UN_ARCHIVO_NUEVO & ~mascara


# Los errores con que un directorio no admite crear el temporal: sin permiso
# de escritura en el, o en un sistema de archivos de solo lectura.
_SIN_PERMISO_EN_EL_DIRECTORIO = (errno.EACCES, errno.EPERM, errno.EROFS)


def _nombrando_el_destino(exc: OSError, destino: Path, *nombres: str) -> OSError:
    """
    El mismo error nombrando `destino` donde nombraba uno de `nombres` (el
    temporal, o el archivo enlazado): quien exporta pidio el destino, y un
    `.xxxx.parcial` en el mensaje no le dice que fallo. Un error sin numero,
    o que nombra otro archivo (el PDF de trabajo del hijo, por ejemplo), sale
    tal cual.
    """
    if exc.errno is None or not ({exc.filename, exc.filename2} & set(nombres)):
        return exc
    return type(exc)(exc.errno, exc.strerror, str(destino))


def escribir_atomico(destino: Path, escribir: Callable[[Path], None]) -> Path:
    """
    `escribir(temporal)` escribe el contenido en un temporal UNICO y CORTO del
    directorio del archivo real (`archivo_real`), que solo si termino recibe
    el modo que tiene que quedar (`_modo_para`) y se renombra sobre el archivo
    real con `os.replace`. Si `escribir`, el cambio de modo o el renombre
    fallan, el temporal se retira, la excepcion sigue su curso y el archivo
    previo queda intacto. Devuelve el archivo real que se escribio.

    LOS PERMISOS, COMO ANTES DE LA ESCRITURA ATOMICA (verificacion de UI-5,
    N4; medido como usuario sin privilegios contra `2d37c2c`):

    - un destino que existe y no se puede escribir se RECHAZA, con
      `PermissionError` que nombra el destino: escribir encima lo rechazaba,
      y el renombre lo habria reemplazado en silencio (el renombre solo pide
      permiso sobre el directorio);
    - un directorio que no admite el temporal (sin permiso de escritura, o de
      solo lectura) con un destino escribible se escribe DIRECTO, como antes:
      sin la garantia de la escritura atomica, que en ese directorio no se
      puede dar, pero sin negarse a escribir lo que el usuario puede escribir;
    - todo error nombra el DESTINO, no el temporal (`_nombrando_el_destino`).

    El rechazo se decide con `os.access`, que para root siempre contesta que
    si: root escribia encima, y sigue pudiendo.
    """
    destino = Path(destino)
    real = archivo_real(destino)
    if real.is_file() and not os.access(real, os.W_OK):
        raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), str(destino))
    try:
        descriptor, nombre = tempfile.mkstemp(prefix=PREFIJO_DEL_TEMPORAL,
                                              suffix=SUFIJO_DEL_TEMPORAL, dir=real.parent)
    except OSError as exc:
        if exc.errno not in _SIN_PERMISO_EN_EL_DIRECTORIO:
            raise type(exc)(exc.errno, exc.strerror, str(destino)) from exc
        try:
            escribir(real)
        except OSError as directo:
            raise _nombrando_el_destino(directo, destino, str(real)) from directo
        return real
    os.close(descriptor)
    temporal = Path(nombre)
    modo = _modo_para(real)
    reemplazado = False
    try:
        escribir(temporal)
        os.chmod(temporal, modo)
        os.replace(temporal, real)
        reemplazado = True
    except OSError as exc:
        nuevo = _nombrando_el_destino(exc, destino, str(temporal), str(real))
        if nuevo is exc:
            raise
        raise nuevo from exc
    finally:
        if not reemplazado:
            temporal.unlink(missing_ok=True)
    return real
