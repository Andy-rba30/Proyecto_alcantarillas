#!/usr/bin/env python3
"""
Verificacion independiente de cierre de sesion.

No lee reportes ni mensajes de commit: comprueba el arbol y el tracker.
Correr desde la raiz del repo, sobre un checkout limpio de origin/main:

    git fetch origin && git checkout origin/main
    python3 -m proceso.verificar_sesion

MATERIAL DE PROCESO DESDE T-12 (INF-5.2.2): vivia en la raiz y solo sirve al
proceso de desarrollo (cierre de sesion, tracker de auditorias, ramas), de
modo que se movio a `proceso/` con el resto. Se lanza con `-m` desde la raiz,
como todo lo que importa del paquete `src` (EXT-9).

Codigo de salida 0 si todo pasa, 1 si algo falla.

Los tres proceso/auditorias/auditoria_*.md son evidencia historica: los conteos
que citan son de cuando se hizo la auditoria y NO deben actualizarse. Por eso
el chequeo 2 los excluye.
"""
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

FALLOS = []
AVISOS = []

# Numero de FILAS de la matriz cruzada. No es un valor de proyecto -- no entra
# en ningun calculo --: es el tamaño del tracker, y si cambia es que alguien
# añadio o retiro una ficha, que es justo lo que este script comprueba.
#
# 237 = 234 + 3, y los dos numeros son correctos, cada uno de lo suyo. Las tres
# auditorias externas trajeron 234 hallazgos: ese es el numero que citan
# CLAUDE.md y docs/hoja_de_ruta_correcciones_v12.md, y ahi NO se toca, porque
# la frase que lo lleva dice «de tres auditorias externas». Las tres filas de
# mas --- SIS-G-01, SIS-G-02 (S16.5) y SIS-G-03 (S19) --- son hallazgos que
# encontraron las propias sesiones de correccion, no las auditorias. Quien vea
# 237 aqui y 234 alli y los "cuadre" bajando este a 234 rompe el chequeo:
# comprobado con `git show 799cba9:...xlsx` (234 filas) contra main (237), cuya
# unica diferencia son esos tres IDs.
#
# 303 = 237 + 66 desde EXT-0 (2026-09-20): los 23 hallazgos de la auditoria
# externa del 2026-09-19 con prefijo EXT- (EXT-A-01 ... EXT-G-03; el dictamen
# dice «22» en su encabezado y su tabla lista 23: A 3, N 4, M 7, V 6, G 3), los 35
# puntos ciegos PC-01 ... PC-35 del dictamen
# (docs/planes_mejora/06_DICTAMEN_AUDITORIA_EXTERNA_2026-09-19.md), la ficha
# C5-02 de decisiones_diferidas.md que EXT-0 reabrio como defecto, y siete
# items ALTA/CRITICA de los temarios de refutacion R95/R48 cuya sustancia no
# tenia fila de estado (R95-031, R48-001, R48-006, R48-007, R48-019, R48-025,
# R48-030). El 234 de CLAUDE.md sigue siendo el de «las tres auditorias».
#
# 367 = 303 + 64 desde T-0 de la cadena T (2026-11-11): los hallazgos del
# INFORME_evaluacion_app_alcantarillas_vs_PDF.md con prefijo INF-, con el
# numero del INFORME como ID canonico --- 18 del §5.1 (INF-5.1.1 ... .18), 7
# del §5.2, 30 filas de las cuatro tablas del §3 (6 + 9 + 8 + 7), 7 apartados
# del §4 y los puntos 4 y 5 del §0 (INF-0.4, INF-0.5), que no tienen fila en
# ninguna tabla y que la cadena cita ---. El alias con que cada prompt cita
# un hallazgo esta en «Vinculos cruzados» de su fila y en la nota inicial de
# docs/planes_mejora/09_CADENA_PROMPTS_TESIS.md.
HALLAZGOS_EN_LA_MATRIZ = 367   # literal-ok: tamaño del tracker de auditorias
ANCHO_CONSOLA = 66             # literal-ok: ancho de la caja del resumen

# Evidencia historica: no deben reflejar el estado actual.
DOCS_CONGELADOS = {
    "proceso/auditorias/auditoria_matematica.md",
    "proceso/auditorias/auditoria_sistema.md",
    "proceso/auditorias/auditoria_normativa.md",
}


def ok(msg):
    print(f"  [OK]    {msg}")


def fallo(msg):
    print(f"  [FALLO] {msg}")
    FALLOS.append(msg)


def aviso(msg):
    print(f"  [AVISO] {msg}")
    AVISOS.append(msg)


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True,
                          text=True).stdout.strip()


# ---------------------------------------------------------------- 1. suite
print("\n1. Suite de tests")
salida = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                        capture_output=True, text=True).stdout
m = re.search(r"(\d+) passed(?:, (\d+) skipped)?", salida)
passed = skipped = 0
if not m:
    fallo("no se pudo leer el resultado de pytest")
else:
    passed, skipped = int(m.group(1)), int(m.group(2) or 0)
    if re.search(r"\d+ (failed|error)", salida):
        fallo(f"la suite NO esta verde: {m.group(0)}")
    else:
        ok(f"{passed} passed, {skipped} skipped")

# ------------------------------------------- 1-bis. la suite de PROCESO
# Desde T-12 los tests del material de proceso viven en `proceso/tests` y
# `python -m pytest` (paso 1) no los recoge (`testpaths`). Se corren aqui:
# un cierre de sesion que actualiza el tracker o la bitacora tiene que
# dejarlos verdes (H4 de la auditoria de T-12).
print("\n1-bis. Suite de proceso (proceso/tests)")
salida_proceso = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "proceso/tests"],
    capture_output=True, text=True).stdout
m_proceso = re.search(r"(\d+) passed", salida_proceso)
if not m_proceso or re.search(r"\d+ (failed|error)", salida_proceso):
    fallo("la suite de proceso NO esta verde: "
          + (salida_proceso.strip().splitlines() or ["sin salida"])[-1])
else:
    ok(f"{m_proceso.group(1)} passed (proceso/tests)")

# --------------------------------------------- 2. docs coinciden con la suite
# EL CONTEO ES UN PAR, NO UN NUMERO, desde S12. Los tests que abren los PDF de
# normas/ llevan `@pytest.mark.pdf` y se saltan sin PyMuPDF, que es dependencia
# de TEST y no de produccion. Los dos numeros son legitimos y los documentos
# vivos citan los dos: este paso tiene que aceptar cualquiera de ellos y
# seguir cazando el tercero, que es el desactualizado.
print("\n2. Los documentos vivos citan el numero real de tests")
salida_sin_pdf = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "-m", "not pdf"],
    capture_output=True, text=True).stdout
m2 = re.search(r"(\d+) passed", salida_sin_pdf)
passed_sin_pdf = int(m2.group(1)) if m2 else passed
legitimos = {passed, passed_sin_pdf}
print(f"          con PyMuPDF {passed}, sin PyMuPDF {passed_sin_pdf}")
desfasados = 0
# Los documentos VIVOS del entregable. La bitacora de `proceso/` lleva los
# conteos de cada sesion a proposito (es historia, como las auditorias) y no
# se barre, igual que antes de T-12 no se barria CLAUDE.md.
for doc in Path("docs").rglob("*.md"):
    if doc.as_posix() in DOCS_CONGELADOS:
        continue
    texto = doc.read_text(errors="ignore")
    for n in sorted(set(re.findall(r"(\d{3,4}) passed", texto))):
        if int(n) not in legitimos:
            aviso(f"{doc}: dice '{n} passed', la suite da "
                  + " o ".join(str(x) for x in sorted(legitimos)))
            desfasados += 1
if not desfasados:
    ok("ningun documento vivo cita un conteo desactualizado")

# ------------------------------------------------------------- 3. git limpio
print("\n3. Estado del remoto")
sh("git fetch origin --prune")
ramas = [r.strip() for r in sh("git branch -r").splitlines()
         if r.strip() and "HEAD" not in r]
sobrantes = [r for r in ramas if r != "origin/main"]
for r in sobrantes:
    pendiente = sh(f"git log --oneline origin/main..{r}")
    if pendiente:
        aviso(f"{r}: tiene {len(pendiente.splitlines())} commit(s) fuera de main")
    else:
        fallo(f"{r}: ya fusionada, deberia estar borrada (CLAUDE.md)")
if not sobrantes:
    ok("solo existe origin/main")

if sh("git status --porcelain"):
    fallo("el working tree tiene cambios sin commitear")
else:
    ok("working tree limpio")

# ---------------------------------------------------------------- 4. tracker
print("\n4. Tracker (matriz_cruzada_auditorias.xlsx)")
try:
    import openpyxl
except ImportError:
    openpyxl = None
    fallo("openpyxl no instalado: pip install openpyxl --break-system-packages")

if openpyxl:
    wb = openpyxl.load_workbook(
        "proceso/auditorias/matriz_cruzada_auditorias.xlsx")
    ws = wb["Hallazgos"]
    cab = [c.value for c in ws[1]]
    i = {h: n for n, h in enumerate(cab)}
    filas = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]

    if len(filas) != HALLAZGOS_EN_LA_MATRIZ:
        fallo(f"{len(filas)} filas, se esperaban {HALLAZGOS_EN_LA_MATRIZ}")
    else:
        ok(f"{HALLAZGOS_EN_LA_MATRIZ} filas")

    estados = Counter(r[i["Estado"]] for r in filas)
    print(f"          {dict(estados)}")

    # todo lo cerrado cita un commit que existe en main
    huerfanos = []
    for r in filas:
        if str(r[i["Estado"]]).startswith("Cerrado"):
            ref = str(r[i["Commit / PR"]] or "")
            shas = re.findall(r"\b[0-9a-f]{7,40}\b", ref)
            if not shas:
                huerfanos.append(f"{r[0]}: cerrado sin commit citado")
                continue
            for s in shas:
                estado = sh(
                    f"git merge-base --is-ancestor {s} origin/main; echo $?")
                if estado != "0":
                    huerfanos.append(f"{r[0]}: cita {s}, que no esta en main")
    if huerfanos:
        for h in huerfanos:
            fallo(h)
    else:
        ok("todo hallazgo cerrado cita un commit presente en main")

    # las filas sin cluster no vuelven a "Pendiente"
    sin_cluster = [r for r in filas if r[i["Cluster"]] == "\u2014"]
    malos = [r[0] for r in sin_cluster if r[i["Estado"]] == "Pendiente"]
    if malos:
        fallo(f"filas sin cluster de vuelta en Pendiente: {malos}")
    else:
        ok(f"las {len(sin_cluster)} filas sin cluster siguen fuera de la cola")

    # parciales cuya fase ya fue ejecutada: nadie los va a volver a mirar
    #   F1 -> S2-S10 (hecho)   F2 -> S12   F3 -> S14   F4 -> S16   F5 -> S19
    # Actualizar FASES_EJECUTADAS al cerrar cada sesion de fase.
    FASES_EJECUTADAS = {"F1", "F2"}
    parciales = [r for r in filas if r[i["Estado"]] == "Cerrado parcial"]
    huerfanos_fase = [r[0] for r in parciales
                      if r[i["Fase"]] in FASES_EJECUTADAS]
    if huerfanos_fase:
        aviso("parciales cuya fase ya corrio, sin sesion que los recoja: "
              + ", ".join(huerfanos_fase))
    if parciales:
        ok(f"{len(parciales)} parcial(es); "
           f"{len(parciales) - len(huerfanos_fase)} esperan una fase futura")

# ----------------------------------------------------------------- 5. normas
# DONDE ESTAN LOS PDF (T-0, T-12). Se buscan por la misma puerta que usa la
# suite --- `fuentes.directorios_de_normas()`: desde T-12 SOLO `$NORMAS_DIR`,
# el clon del repositorio de normas; los PDF de `normas/` de la app se
# retiraron --- y se dice cuales faltan. Sin la variable no hay PDF en disco
# y es un AVISO, no un fallo: la suite del paso 1 quedo verde SALTANDO todos
# los tests `pdf`, y eso hay que leerlo aqui, no deducirlo del numero de
# `skipped`. Con la variable, cualquier falta SI es un fallo: una fuente
# presente sin PDF no se puede reverificar.
print("\n5. PDF de normas (NORMAS_DIR)")
from src.normativa import fuentes as _fuentes   # noqa: E402

try:
    carpetas = _fuentes.directorios_de_normas()
except FileNotFoundError as exc:
    carpetas = None
    fallo(str(exc))
if carpetas == ():
    aviso(f"sin {_fuentes.VARIABLE_NORMAS_DIR}: ningun PDF de normas esta en "
          "disco y los tests `pdf` se saltaron (ver CLAUDE.md, «Donde estan "
          "los PDF de normas»)")
elif carpetas:
    for carpeta in carpetas:
        print(f"          {carpeta}")
    sin_pdf = sorted(f.id for f in _fuentes.FUENTES.values()
                     if not _fuentes.ruta_pdf(f).exists())
    if not sin_pdf:
        ok(f"las {len(_fuentes.FUENTES)} fuentes presentes tienen su PDF en disco")
    else:
        fallo("fuentes presentes sin PDF en el repositorio de normas: "
              + ", ".join(sin_pdf))

# ----------------------------------------------------------------- resumen
print("\n" + "=" * ANCHO_CONSOLA)
if FALLOS:
    print(f"FALLA: {len(FALLOS)} problema(s). La sesion no esta cerrada.")
elif AVISOS:
    print(f"PASA con {len(AVISOS)} aviso(s) para revisar a mano.")
else:
    print("PASA: sesion cerrada limpiamente.")
print("=" * ANCHO_CONSOLA)
sys.exit(1 if FALLOS else 0)
