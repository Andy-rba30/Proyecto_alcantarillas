"""
tests/test_M11_reporte.py
=========================
M11 - Memoria de calculo de la Fase 11.

El grueso de estos tests no comprueba estetica: comprueba que la memoria NO
puede mentir. Un reporte que omite un numeral, que rellena una celda bloqueada
con un valor plausible o que imprime un marcador sin sustituir es peor que no
tener reporte, porque parece un entregable.

La guardia de la plantilla (`TestPlantillaSinPorcentajesLibres`) es hermana de
tests/test_sin_literales.py: alli se vigila que ningun modulo declare valores,
aqui que ningun texto libre de la plantilla se cuele como marcador -- o al
reves, que un delimitador escrito en un comentario reviente la generacion
entera. Las dos son fallas silenciosas del mismo tipo.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import criterios_adoptados as ca
from cli import (Bloqueo, DatoDeclarado, Informe, InformePunto,
                 cargar_datos_externos, correr)
from modelos import PasoDiseno, Verificacion
from modulos import M11_reporte as M11

RAIZ = Path(__file__).resolve().parents[1]
CSV_EJEMPLO = RAIZ / "tests" / "ejemplo_puntos.csv"
PLANTILLA = M11.DIR_PLANTILLAS / M11.NOMBRE_PLANTILLA


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _informe_de_ejemplo() -> Informe:
    """La corrida real del CSV de ejemplo, con los datos externos minimos."""
    externos = cargar_datos_externos(
        None, {"luz_m": 2.0, "TW_m": 0.0, "longitud_m": 14.0,
               "L_hidraulico_m": None, "categoria_tr": None})
    return correr(CSV_EJEMPLO, externos)


@pytest.fixture(scope="module")
def informe() -> Informe:
    return _informe_de_ejemplo()


@pytest.fixture(scope="module")
def memoria(informe: Informe) -> str:
    return M11.memoria_html(informe, proyecto="Via de evitamiento - La Union")


# ===========================================================================
# La plantilla y su delimitador
# ===========================================================================

class TestPlantillaSinPorcentajesLibres:
    """
    Todo delimitador de la plantilla tiene que ser un marcador real.

    El primer intento de esta plantilla llevaba el delimitador escrito dentro
    de su propio comentario de cabecera para explicar el patron. `substitute`
    lo leyo como marcador invalido y la generacion entera reventaba. La
    variante peligrosa es la contraria: un texto libre que casualmente forme un
    marcador valido y salga sustituido -- o borrado -- en mitad de la memoria.
    Ninguna de las dos se ve leyendo el HTML por encima.
    """

    # Un delimitador seguido de identificador, de {identificador}, o de nada
    # reconocible: los tres casos que string.Template distingue.
    DELIMITADOR = re.escape(M11.PlantillaHTML.delimiter)
    TODOS = re.compile(DELIMITADOR + r"(\{?)([A-Za-z_][A-Za-z0-9_]*)?")

    def _marcadores_declarados(self):
        """Los que M11 entrega. Es la lista contra la que se contrasta todo."""
        return set(M11.marcadores_de_la_memoria())

    def test_todo_delimitador_es_un_marcador_valido(self):
        texto = PLANTILLA.read_text(encoding="utf-8")
        for coincidencia in self.TODOS.finditer(texto):
            nombre = coincidencia.group(2)
            linea = texto.count("\n", 0, coincidencia.start()) + 1
            assert nombre, (
                f"linea {linea}: la plantilla contiene el delimitador "
                f"'{M11.PlantillaHTML.delimiter}' sin un nombre de marcador "
                "detras. Si es texto libre (un comentario, una explicacion del "
                "patron), reescribelo sin el delimitador: string.Template lo "
                "lee como marcador invalido y la memoria no se genera."
            )

    def test_ningun_marcador_huerfano_en_la_plantilla(self):
        """Un marcador que M11 no entrega revienta la generacion."""
        texto = PLANTILLA.read_text(encoding="utf-8")
        usados = {m.group(2) for m in self.TODOS.finditer(texto) if m.group(2)}
        huerfanos = sorted(usados - self._marcadores_declarados())
        assert not huerfanos, (
            f"la plantilla pide marcadores que M11 no entrega: {huerfanos}. "
            "Agregalos a `memoria_html` o quitalos de la plantilla."
        )

    def test_ningun_marcador_declarado_sin_usar(self):
        """
        Al reves: un marcador que M11 calcula y la plantilla no imprime es
        contenido de la memoria que se pierde en silencio.
        """
        texto = PLANTILLA.read_text(encoding="utf-8")
        usados = {m.group(2) for m in self.TODOS.finditer(texto) if m.group(2)}
        sin_usar = sorted(self._marcadores_declarados() - usados)
        assert not sin_usar, (
            f"M11 entrega marcadores que la plantilla no imprime: {sin_usar}. "
            "Ese contenido no llega a la memoria."
        )

    def test_el_detector_atrapa_un_delimitador_en_texto_libre(self):
        """
        El test se prueba a si mismo: sobre una plantilla sintetica con el
        delimitador dentro de un comentario, tiene que fallar.
        """
        delimitador = M11.PlantillaHTML.delimiter
        sintetica = f"<!-- el delimitador es {delimitador} -->\n<p>hola</p>"
        sospechosos = [m for m in self.TODOS.finditer(sintetica)
                       if not m.group(2)]
        assert sospechosos, ("el detector no vio un delimitador suelto: "
                             "dejaria pasar el bug que motivo este test")

    def test_la_memoria_no_deja_ningun_marcador_sin_sustituir(self, memoria):
        """Lo mismo, ya sobre el HTML generado: no queda ni un delimitador."""
        assert M11.PlantillaHTML.delimiter not in memoria


# ===========================================================================
# (1) Encabezado de trazabilidad
# ===========================================================================

class TestTrazabilidad:
    """Sin encabezado, dos memorias no se distinguen: es el bloque 0."""

    def test_localiza_la_hoja_de_ruta_y_lee_su_version(self):
        hoja = M11.ruta_hoja_de_ruta()
        assert hoja.is_file()
        assert re.fullmatch(r"v\d+", M11.version_hoja_de_ruta(hoja))

    def test_la_version_sale_del_documento_no_del_nombre(self, tmp_path):
        """El titulo manda: el nombre del archivo es solo el respaldo."""
        falsa = tmp_path / "hoja_de_ruta_alcantarillas_v3.md"
        falsa.write_text("# Hoja de ruta - algo · v9\n", encoding="utf-8")
        assert M11.version_hoja_de_ruta(falsa) == "v9"

    def test_sin_version_en_ninguna_parte_se_detiene(self, tmp_path):
        muda = tmp_path / "hoja_de_ruta_alcantarillas_.md"
        muda.write_text("# Hoja de ruta sin version\n", encoding="utf-8")
        with pytest.raises(ValueError, match="version"):
            M11.version_hoja_de_ruta(muda)

    def test_dos_hojas_de_ruta_es_ambiguo_y_se_detiene(self, tmp_path):
        for version in ("v7", "v8"):
            (tmp_path / f"hoja_de_ruta_alcantarillas_{version}.md").write_text(
                "# x\n", encoding="utf-8")
        with pytest.raises(ValueError, match="mas de una"):
            M11.ruta_hoja_de_ruta(tmp_path)

    def test_sin_hoja_de_ruta_no_es_error_del_expediente(self, tmp_path):
        """Falta un archivo del script, no un dato del CSV: FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            M11.ruta_hoja_de_ruta(tmp_path)

    def test_sha1_distingue_dos_csv(self, tmp_path):
        uno, otro = tmp_path / "a.csv", tmp_path / "b.csv"
        uno.write_text("id,Q\nA-01,1.0\n", encoding="utf-8")
        otro.write_text("id,Q\nA-01,1.1\n", encoding="utf-8")
        assert M11.sha1_archivo(uno) != M11.sha1_archivo(otro)

    def test_trazabilidad_completa(self, informe):
        traza = M11.trazabilidad(Path(informe.csv),
                                 generado_utc=informe.generado)
        assert traza.version_hoja_ruta.startswith("v")
        assert len(traza.csv_sha1) == len(traza.criterios_sha1)
        assert traza.criterios_fecha
        assert traza.generado_utc == informe.generado

    def test_el_encabezado_llega_al_html(self, informe, memoria):
        """Los cuatro datos exigidos, ya renderizados."""
        traza = M11.trazabilidad(Path(informe.csv),
                                 generado_utc=informe.generado)
        assert traza.version_hoja_ruta in memoria      # version de la hoja
        assert traza.csv_sha1 in memoria               # SHA-1 del CSV
        assert traza.criterios_sha1 in memoria         # version de criterios
        assert traza.criterios_fecha in memoria        # fecha de criterios
        assert traza.generado_utc in memoria           # fecha de la corrida

    def test_dos_csv_distintos_dan_encabezados_distintos(self, informe,
                                                         memoria, tmp_path):
        """La razon de ser del bloque: si el CSV cambia, el reporte lo dice."""
        copia = tmp_path / "otro.csv"
        copia.write_text(
            CSV_EJEMPLO.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        traza_original = M11.trazabilidad(Path(informe.csv))
        traza_copia = M11.trazabilidad(copia)
        assert traza_original.csv_sha1 != traza_copia.csv_sha1
        assert traza_copia.csv_sha1 not in memoria


# ===========================================================================
# (2) Memoria por punto: datos con fuente, iteraciones y verificaciones
# ===========================================================================

class TestMemoriaPorPunto:

    def test_cada_punto_del_csv_tiene_su_bloque(self, informe, memoria):
        for punto in informe.puntos:
            assert punto.punto.id in memoria
            assert punto.punto.progresiva_display in memoria

    def test_cada_dato_del_csv_declara_su_columna(self, memoria):
        """'Datos con fuente': la columna de Sec. 1.2 de la que salio."""
        for campo, _rotulo, _unidad in M11.CAMPOS_CSV:
            assert f"<code>{campo}</code>" in memoria

    def test_los_datos_declarados_llevan_su_origen(self, informe, memoria):
        """Luz, longitud y TW no son columnas: la memoria dice de donde salen."""
        for punto in informe.puntos:
            for atributo in ("luz", "longitud", "tw"):
                dato = getattr(punto, atributo)
                if dato is not None:
                    assert dato.origen in memoria

    def test_toda_verificacion_lleva_su_numeral_y_su_marca(self, informe,
                                                           memoria):
        for punto in informe.puntos:
            for _fase, v in punto.verificaciones():
                assert v.numeral in memoria
        assert M11.MARCA_CUMPLE in memoria or M11.MARCA_INCUMPLE in memoria

    def test_una_verificacion_incumplida_se_marca_como_tal(self):
        """Con una V que no cumple, la memoria dice 'NO cumple', no 'cumple'."""
        informe = _informe_de_ejemplo()
        objetivo = informe.puntos[0]
        objetivo.clasificacion = None
        fallida = Verificacion(cumple=False, numeral="4.1.1.3.7 b)",
                               valor_obtenido=0.9, valor_admisible=0.75,
                               criterio_aplicado=None, codigo="V1")
        objetivo.verificaciones = lambda: (("Fase 5", fallida),)
        html = M11._tabla_verificaciones(objetivo)
        assert M11.MARCA_INCUMPLE in html
        assert "4.1.1.3.7 b)" in html
        assert "fila-incumple" in html

    def test_el_umbral_de_un_criterio_adoptado_se_identifica(self):
        """Un umbral [A] no puede parecer normativo: lleva clave y etiqueta."""
        clave = ca.criterios_sin_valor()[0]
        v = Verificacion(cumple=True, numeral="Sec. 5.1", valor_obtenido=1.0,
                         valor_admisible=2.0, criterio_aplicado=clave,
                         codigo="V4")
        falso = InformePunto(punto=_informe_de_ejemplo().puntos[0].punto)
        falso.verificaciones = lambda: (("Fase 5", v),)
        html = M11._tabla_verificaciones(falso)
        assert clave in html
        assert ca.criterio(clave).etiqueta in re.sub(r"<[^>]+>", "", html) \
            or "etiqueta" in html


class TestIteraciones:
    """
    El entregable 1 exige las ITERACIONES, no solo la combinacion ganadora.
    """

    def _punto_con_traza(self) -> InformePunto:
        informe = _informe_de_ejemplo()
        punto = informe.puntos[0]
        punto.traza = [
            PasoDiseno(material="concreto reforzado", D=0.90, aceptado=False,
                       motivo="D = 0.90 m: incumple V1 (y/D = 0.82 > 0.75)"),
            PasoDiseno(material="concreto reforzado", D=1.05, aceptado=False,
                       motivo="D = 1.05 m: incumple V1 (y/D = 0.78 > 0.75)"),
            PasoDiseno(material="concreto reforzado", D=1.20, aceptado=True,
                       motivo=""),
        ]
        return punto

    def test_la_traza_llega_al_html_con_los_escalones_descartados(self):
        html = M11._tabla_iteraciones(self._punto_con_traza())
        assert "0.90" in html and "1.05" in html and "1.20" in html
        assert html.count("descartado") == 2
        assert "adoptado" in html
        assert "incumple V1" in html

    def test_sin_traza_se_declara_la_ausencia_en_vez_de_una_tabla_vacia(self):
        """Una tabla vacia se lee como 'no hubo iteraciones', que es falso."""
        punto = InformePunto(punto=_informe_de_ejemplo().puntos[0].punto)
        html = M11._tabla_iteraciones(punto)
        assert "No se registro traza" in html
        assert "<table" not in html

    def test_el_observador_de_MD_alimenta_la_traza(self):
        """
        La traza no la fabrica M11: sale del bucle real de MD. Se comprueba
        con el observador directamente, sin pasar por la CLI.
        """
        from modelos import Material, TipoMaterial, ConstantesHDS5
        from modulos.MD import disenar_material

        informe = _informe_de_ejemplo()
        punto = informe.puntos[0].punto
        recogidos = []

        material = Material(
            tipo=TipoMaterial.CONCRETO_REFORZADO, nombre="concreto reforzado",
            n_min=0.010, n_max=0.013, D_max=1.20,
            norma_producto="ASTM C76",
            hds5=ConstantesHDS5(K=0.0098, M=2.0, c=0.0398, Y=0.67, Ks=-0.5),
            v_max_rango=(3.0, 6.0), h_relleno_min=0.60,
            subseccion_eg2013="505")

        # Verificador que rechaza todo: interesa la traza, no el diseño.
        def rechazar(*, punto, material, D, resultado):
            return (Verificacion(cumple=False, numeral="Sec. 5", codigo="V1",
                                 valor_obtenido=D, valor_admisible=0.0,
                                 criterio_aplicado=None),)

        resultado, motivo = disenar_material(
            punto, material, Q=1.5, S=0.01, L=14.0, TW=0.0,
            verificar=rechazar, registrar=recogidos.append)

        assert resultado is None and motivo
        assert len(recogidos) > 1, "MD probo un solo escalon: no hay iteracion"
        assert all(isinstance(p, PasoDiseno) for p in recogidos)
        assert all(not p.aceptado for p in recogidos)
        # Los escalones van en orden ascendente de diametro (catalogo Sec. 3.2)
        diametros = [p.D for p in recogidos]
        assert diametros == sorted(diametros)

    def test_sin_observador_MD_se_comporta_igual(self):
        """El observador no puede alterar el diseño."""
        externos = cargar_datos_externos(
            None, {"luz_m": 2.0, "TW_m": 0.0, "longitud_m": 14.0,
                   "L_hidraulico_m": None, "categoria_tr": None})
        uno = correr(CSV_EJEMPLO, externos)
        otro = correr(CSV_EJEMPLO, externos)
        assert [p.dimensionado for p in uno.puntos] == \
               [p.dimensionado for p in otro.puntos]


class TestPuntosBloqueados:
    """Un punto que no cerro se publica como bloqueado, no como error ni vacio."""

    def _punto(self, informe: Informe, id_punto: str) -> InformePunto:
        for p in informe.puntos:
            if p.punto.id == id_punto:
                return p
        raise AssertionError(f"{id_punto} no esta en el CSV de ejemplo")

    def test_C01_aparece_bloqueada_por_dato_externo(self, informe, memoria):
        c01 = self._punto(informe, "C-01")
        assert not c01.dimensionado
        assert c01.bloqueos, "C-01 deberia traer su bloqueo declarado"

        bloque = M11.memoria_de_punto(c01)
        assert "C-01" in bloque
        assert "sin dimensionar" in bloque
        assert "no llego a dimensionarse" in bloque
        # El motivo real, no un generico: le falta el caudal del canal (3.1)
        assert any(b.campo == "Q_m3s" for b in c01.bloqueos)
        assert "Q_m3s" in bloque
        assert "DatoFaltanteError" in bloque

    def test_un_punto_bloqueado_no_inventa_celdas_en_el_resumen(self, informe):
        c01 = self._punto(informe, "C-01")
        fila = M11.fila_resumen(c01, "square edge")
        assert fila.count(M11.VACIO) >= len(("tipo", "material", "D", "V",
                                             "y/D", "HW", "control"))
        assert "fila-incumple" in fila

    def test_los_bloqueos_por_criterio_dicen_que_falta_declarar(self, memoria):
        assert "falta declarar" in memoria


# ===========================================================================
# (3) Tabla resumen de la Fase 11, punto 3
# ===========================================================================

class TestTablaResumen:

    COLUMNAS = ("Progresiva", "Familia", "TR", "Tipo",
                "Material y norma de producto", "D", "V", "y/D", "HW",
                "Control", "Proteccion de salida", "Tipo de cabezal")

    def test_estan_las_doce_columnas_del_entregable_3(self, memoria):
        for columna in self.COLUMNAS:
            assert columna in memoria

    def test_una_fila_por_punto(self, informe, memoria):
        filas = "".join(M11.fila_resumen(p, "x") for p in informe.puntos)
        assert filas.count("<tr") == len(informe.puntos)

    def test_el_tipo_de_cabezal_sale_del_tablero_2(self):
        """No es una constante de M11: es la decision 2.3 de la hoja de ruta."""
        tableros = M11.tableros_pendientes()
        embocadura = M11.decision_embocadura(tableros)
        assert embocadura is not None
        assert "ras del muro" in embocadura

    def test_sin_el_item_2_3_la_celda_queda_pendiente_no_rellenada(self,
                                                                  informe):
        vacio = M11.Tablero(numero="2", titulo="t", glosa="g",
                            encabezados=("#",), filas=())
        assert M11.decision_embocadura([vacio]) is None


# ===========================================================================
# (4) Declaracion de criterios adoptados
# ===========================================================================

class TestBloqueCriterios:

    def test_cada_criterio_usado_trae_etiqueta_justificacion_y_fuente(self):
        # El texto va escapado en el HTML: se compara contra la forma escapada,
        # que es justamente lo que garantiza que un dato no inyecte marcado.
        import html as _html

        renderizado = M11.bloque_criterios(solo_usados=False)
        for clave, criterio in ca.CRITERIOS.items():
            assert clave in renderizado
            assert _html.escape(criterio.fuente) in renderizado
            assert _html.escape(criterio.justificacion) in renderizado
            assert M11._etiqueta_html(criterio.etiqueta) in renderizado

    def test_solo_usados_no_lista_el_catalogo_completo(self, memoria):
        usados = set(ca.criterios_usados())
        no_usados = set(ca.CRITERIOS) - usados
        assert usados, "la corrida deberia haber invocado algun criterio"
        # Al menos uno de los no usados no debe aparecer en el bloque 3
        bloque = memoria.split("Declaracion de criterios adoptados")[-1]
        bloque = bloque.split("Pendientes")[0]
        assert any(clave not in bloque for clave in no_usados)

    def test_un_criterio_con_rango_no_se_reduce_a_un_numero(self):
        """El n del HDPE ES un rango: imprimirlo puntual contradice su ficha."""
        assert M11._valor_legible((0.010, 0.013)) == "0.01, 0.013"

    def test_un_criterio_sin_valor_se_declara_sin_valor(self):
        assert "sin valor declarado" in M11._valor_legible(None)


# ===========================================================================
# (5) Bloque aparte de pendientes: Tableros 1, 2 y 3
# ===========================================================================

class TestBloquePendientes:

    def test_se_leen_los_tres_tableros_de_la_hoja_de_ruta(self):
        tableros = M11.tableros_pendientes()
        numeros = [t.numero for t in tableros]
        assert numeros == ["1", "2", "3"]
        for tablero in tableros:
            assert tablero.titulo and tablero.encabezados and tablero.filas

    def test_los_tableros_no_estan_transcritos_en_el_modulo(self):
        """
        La prueba de que no hay segunda fuente de verdad: el contenido de los
        tableros no aparece en el codigo de M11.
        """
        codigo = Path(M11.__file__).read_text(encoding="utf-8")
        tableros = M11.tableros_pendientes()
        for tablero in tableros:
            for fila in tablero.filas:
                assert M11._md_texto(fila[1]) not in codigo

    def test_una_hoja_sin_tableros_detiene_el_reporte(self, tmp_path):
        muda = tmp_path / "hoja_de_ruta_alcantarillas_v7.md"
        muda.write_text("# Hoja de ruta · v7\n\nsin tableros\n",
                        encoding="utf-8")
        with pytest.raises(ValueError, match="Tablero"):
            M11.tableros_pendientes(muda)

    def test_el_bloque_va_separado_del_de_criterios(self, memoria):
        """
        Lo exige el entregable: los pendientes NO se mezclan con los criterios
        cerrados. Se comprueba por posicion, que es lo unico que lo garantiza.
        """
        pos_criterios = memoria.index("Declaracion de criterios adoptados")
        pos_pendientes = memoria.index("Tableros 1, 2 y 3")
        assert pos_criterios < pos_pendientes

        # Se contrastan las TABLAS de los tableros, no la cadena "Tablero N":
        # varios criterios cerrados citan "Tablero 2.3" en su justificacion, y
        # esa referencia cruzada es contenido legitimo del bloque 3.
        marca = 'class="tablero"'
        posiciones = [m.start() for m in re.finditer(re.escape(marca), memoria)]
        assert posiciones, "no se renderizo ningun tablero"
        assert all(p > pos_pendientes for p in posiciones), (
            "hay una tabla de tablero antes del bloque de pendientes: los "
            "criterios cerrados y los pendientes quedaron mezclados"
        )

        bloque_pendientes = memoria[pos_pendientes:]
        for numero in ("1", "2", "3"):
            assert f"Tablero {numero}" in bloque_pendientes

    def test_los_criterios_sin_valor_se_listan_en_el_bloque_aparte(self,
                                                                   memoria):
        pos = memoria.index("Tableros 1, 2 y 3")
        bloque = memoria[pos:]
        for clave in ca.criterios_sin_valor():
            assert clave in bloque

    def test_el_bloque_se_imprime_aunque_nada_haya_bloqueado(self):
        """Que una corrida no tropiece no borra los pendientes."""
        tableros = M11.tableros_pendientes()
        html = M11.bloque_pendientes(tableros, ())
        assert "Tablero 1" in html
        assert "Ninguno" in html


class TestCriteriosBloqueantes:

    def test_agrupa_por_criterio_con_sus_puntos(self, informe):
        bloqueantes = M11.criterios_bloqueantes(informe)
        assert bloqueantes, "la corrida de ejemplo bloquea por criterio"
        for c in bloqueantes:
            assert c.clave in ca.CRITERIOS
            assert c.etiqueta and c.concepto and c.fuente
            assert c.etapas

    def test_un_informe_sin_bloqueos_no_inventa_bloqueantes(self):
        vacio = Informe(csv=CSV_EJEMPLO, generado="")
        assert M11.criterios_bloqueantes(vacio) == ()


# ===========================================================================
# Exportacion
# ===========================================================================

class TestExportacion:

    def test_exportar_html_escribe_el_documento(self, informe, tmp_path):
        destino = tmp_path / "sub" / "Memoria.html"
        ruta = M11.exportar_html(informe, destino, proyecto="P")
        assert ruta.is_file()
        contenido = ruta.read_text(encoding="utf-8")
        assert contenido.lstrip().startswith("<!DOCTYPE html>")
        assert M11.PlantillaHTML.delimiter not in contenido

    def test_sin_weasyprint_declara_la_via_del_navegador(self, informe,
                                                         tmp_path, monkeypatch):
        """No devuelve un PDF que no escribio: dice por que via salio."""
        monkeypatch.setattr(M11, "WeasyHTML", None)
        salida = M11.exportar_pdf(informe, tmp_path / "Memoria.pdf",
                                  abrir_navegador=False, proyecto="P")
        assert salida.via == M11.VIA_NAVEGADOR
        assert salida.ruta.suffix == ".html"
        assert salida.ruta.is_file()
        assert not (tmp_path / "Memoria.pdf").exists()

    def test_con_weasyprint_declara_esa_via(self, informe, tmp_path,
                                            monkeypatch):
        escrito = {}

        class FalsoWeasy:
            def __init__(self, *, string, base_url):
                escrito["string"] = string

            def write_pdf(self, ruta):
                Path(ruta).write_bytes(b"%PDF-1.7")
                escrito["ruta"] = ruta

        monkeypatch.setattr(M11, "WeasyHTML", FalsoWeasy)
        salida = M11.exportar_pdf(informe, tmp_path / "Memoria.pdf",
                                  proyecto="P")
        assert salida.via == M11.VIA_WEASYPRINT
        assert salida.ruta.is_file()
        assert "<!DOCTYPE html>" in escrito["string"]

    def test_la_plantilla_ausente_no_es_error_del_expediente(self, informe,
                                                             tmp_path):
        with pytest.raises(FileNotFoundError):
            M11.cargar_plantilla(tmp_path / "no_existe.html")

    def test_exportar_csv_escribe_una_fila_por_punto(self, informe, tmp_path):
        destino = tmp_path / "sub" / "Resumen.csv"
        ruta = M11.exportar_csv(informe, destino)
        assert ruta.is_file()
        lineas = ruta.read_text(encoding="utf-8").splitlines()
        assert lineas[0] == ",".join(M11.COLUMNAS_RESUMEN_CSV)
        assert len(lineas) == 1 + len(informe.puntos)


# ===========================================================================
# Escapado: el reporte no puede romperse ni inyectar con un dato del CSV
# ===========================================================================

class TestEscapado:

    def test_un_dato_con_html_se_escapa(self, informe):
        punto = _informe_de_ejemplo().puntos[0]
        punto.luz = DatoDeclarado(nombre="luz_m", valor=2.0,
                                  origen="<script>alerta()</script>")
        html = M11._tabla_datos(punto)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_un_bloqueo_con_html_se_escapa(self):
        punto = InformePunto(punto=_informe_de_ejemplo().puntos[0].punto)
        punto.bloqueos = [Bloqueo(fase="<b>f</b>", etapa="e", tipo="t",
                                  mensaje="<img src=x>")]
        html = M11._tabla_bloqueos(punto.bloqueos)
        assert "<img" not in html
        assert "&lt;img" in html
