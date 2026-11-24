"""
modelos.py
==========
Tipos que fluyen entre modulos y taxonomia de excepciones del proyecto.

Regla de arquitectura: ningun modulo define dicts ad-hoc para lo que ya existe
aqui. Este archivo declara TIPOS, nunca valores: no contiene un solo literal
numerico de proyecto. Los valores [N] estan en `constantes_normativas.py`
(Anexo B) y los [N->], [C] y [A] en `criterios_adoptados.py` (Anexo A).

Unidades
--------
SI estricto: m, m2, m3/s, m/s, rad, Pa, kN. Ninguna estructura de este archivo
transporta pulgadas, pies ni kg/cm2.

Unica salvedad, y es de presentacion, no de calculo: `TamizadoRasante` expone
`delta_rasante_cm` junto al `delta_rasante_m` que almacena, porque Sec. 7.B
redacta su salida en centimetros ("no factible -> subir rasante X cm"). El
factor sale de `dominios.CENTIMETROS_POR_METRO` -- una definicion de unidad,
no un valor de proyecto -- y ningun campo almacenado esta en centimetros.

Dos campos conservan la unidad de su encabezado normativo porque son
localizadores o clasificadores y no entran en ningun calculo hidraulico ni
estructural (Sec. 1.1):

    progresiva_km : km  - progresiva del cruce
    area_ha       : ha  - area de cuenca, "solo clasificador"

Referencias de numeral: docs/hoja_de_ruta_alcantarillas_v8.md

Paquete (D3 del plan de mantenibilidad): `src/modelos.py` se partio POR FAMILIA
DE TIPOS, sin mover una linea de sitio dentro de cada tipo. Este `__init__`
reexporta TODOS los nombres que se usan desde fuera, privados incluidos
(`from src.modelos import X` y `from src import modelos` siguen valiendo).

    errores                 taxonomia de excepciones de `ErrorProyecto`
    base                    citas, enumeraciones y datos de entrada
    memoria                 Verificacion, traza de la memoria, bloqueos, contexto
    conducto                Material, Seccion (circular y rectangular), Geometria
    hidraulica              barril, TW, resultados de la Fase 5, proteccion, socavacion
    rasante_espaciamiento   Fase 7 (compatibilidad, longitud, pendiente) y Fase 10
    cabezal                 Fase 9: cabezal, estabilidad y armado
    proyecto                clasificacion, traza del diseno, resolucion de variables
    durabilidad             Fase 3
    hidrologia              Fase 1-bis
    estructural             Fase 8
    remanso                 marco, remanso del canal, V5 y V8, evento extremo
    metrados                Fase 11, entregables 8 y 9

El orden de los imports es el de dependencia (ningun submodulo importa a otro
que lo importe a el), y `__module__` de cada clase se NORMALIZA a `src.modelos`
al final: la serializacion del informe (`serializacion_informe._nombre_de`)
escribe `__module__:__qualname__`, y asi el JSON de sesion, el pickle y los
tracebacks siguen diciendo `src.modelos.X` como antes de la particion.
"""

from __future__ import annotations

from src.modelos.errores import (
    ErrorProyecto, CriterioPendienteError, DisenoNoFactibleError,
    DatoFaltanteError, DatoInvalidoError, LimiteNumericoError,
    MOTIVO_METODO_NO_EVALUABLE, MOTIVO_METODO_NO_EVALUABLE_HIDROLOGIA,
    MOTIVO_METODO_NO_EVALUABLE_HEC14, MetodoNoEvaluableError,
)
from src.modelos.base import (
    ReferenciaNormativa, NUMERALES_DE_SECCION_SIN_LECTOR, Familia,
    Denominacion, CategoriaTR, TipoMaterial, FormaSeccion, ControlGobernante,
    RegimenBarril, TipoDePerfil, CondicionRasante, CondicionAnalisis,
    GobiernaEspaciamiento, RegimenEntrada, PuntoCritico, CotaDeEntrada,
    REGLA_FONDO_IGUAL_AL_TERRENO, AVISO_FONDO_ENTRADA_ADOPTADO,
)
from src.modelos.memoria import (
    EstadoDeVerificacion, Verificacion, CIFRAS_MAGNITUD, CIFRAS_FINA,
    CIFRAS_FACTOR, CIFRAS_PORCENTAJE, cifras_de_dimension, texto_de_dimension,
    ALCANCE_PERFIL, ALCANCE_EXPEDIENTE, NIVEL_PERFIL, NIVEL_EXPEDIENTE,
    NIVELES, TipoDeVeredicto, TipoDeBloqueo, _TIPO_DE_BLOQUEO_POR_CLASE,
    Bloqueo, ObstaculoAnticipado, DatoEfectivoDeSitio, ContextoCorrida,
    Magnitud, Umbral, Veredicto, EleccionDeProyecto, PasoDeMemoria,
    _registro_normativo, paso, eleccion,
)
from src.modelos.conducto import (
    ConstantesHDS5, Material, Seccion, SeccionCircular, SeccionRectangular,
    Geometria, exigir_seccion_coherente,
)
from src.modelos.hidraulica import (
    TiranteNormal, SinTiranteNormal, TiranteCritico, TransicionEntrada,
    ControlEntrada, PisoDeCargaEntrada, ControlSalida, PerfilLamina,
    ResaltoHidraulico, SeccionReceptor, SECCION_RECEPTOR_MEDIDA,
    SECCION_RECEPTOR_ADOPTADA, ORIGENES_SECCION_RECEPTOR,
    AVISO_SIN_ACCESO_DE_MANTENIMIENTO, AlcanceDeclarado, ALCANCE_DECLARADO,
    ViaDelTW, TWDeterminado, TiranteDeBorde, ResultadoHidraulico,
    ProteccionSalida, FroudeSalida, VelocidadAdmisible, ApronHEC14,
    ClaseHEC14, PozaDeEnrocado, ProteccionTWAlto, EstructuraDeCaida,
    RequisitoDeFiltro, RelacionesDeFiltro, FiltroGranularHEC11,
    ProteccionEntrada, TIPO_LECHO_NO_COHESIVO,
    TIPO_LECHO_COHESIVO, TIPOS_DE_LECHO, MaterialLecho, HoyaDeSocavacion,
    ORIGEN_SOCAVACION_DECLARADA, ORIGEN_SOCAVACION_ESTIMADA,
    ORIGEN_SOCAVACION_SIN_DATO, SocavacionSalida, CamaApoyoRelleno,
    FactoresFlotacion,
)
from src.modelos.rasante_espaciamiento import (
    TamizadoRasante, CAPACIDAD_CUNETA_LLENA, CAPACIDAD_VELOCIDAD_LIMITE,
    ORIGEN_L_DECLARADO, ORIGEN_L_CALCULADO, CODIGO_VB1, CODIGO_VB2,
    METODO_APORTE_TRAMO, METODO_APORTE_AREA, Espaciamiento, CapacidadCuneta,
    LongitudHidraulica, AporteDelAlivio, ExtremoDeTramo, TramoDeAlivio,
    CompatibilidadGeometrica, MetodoLongitud, OrigenPendiente,
    PendienteAdoptada, LongitudConducto,
)
from src.modelos.cabezal import (
    PasoSismico, CadenaSismica, GeometriaCabezal, ORIGEN_DIMENSION_REGLA,
    ORIGEN_DIMENSION_DECLARADA, ORIGEN_DIMENSION_DERIVADA,
    ORIGEN_DIMENSION_ESTABILIDAD, ORIGEN_DIMENSION_ARMADO,
    ORIGEN_DIMENSION_ESTABILIDAD_INCOMPLETA, ORIGENES_DE_DIMENSION,
    DimensionDeCabezal, Aleros, LosaDeEntrega, ExtremoDelConducto,
    EmbocaduraDelPunto, CabezalDelPunto, IntentoDeZapata, IntentoDePeralte,
    EmpujeMononobeOkabe, EmpujesTrasdos, FuerzaInerciaMuro,
    CasoDemandaSismica, DemandaSismicaCabezal, PresionContactoBase,
    CombinacionCarga, RequisitosDurabilidad, RecubrimientoDiseno,
    CuantiaRefuerzo, EstabilidadCabezal, MARCO_LRFD, MARCO_ASD,
    MARCOS_DE_ESTABILIDAD, MARCO_RIGE_LRFD, MARCO_RIGE_ASD, MARCO_ENVOLVENTE,
    REGLAS_DE_MARCO, CARGA_DC, CARGA_EV, CARGA_EH, CARGA_LS, CARGA_WA,
    CARGA_EQ, TIPOS_DE_CARGA_DEL_CABEZAL, ELEMENTO_PANTALLA, ELEMENTO_ZAPATA,
    ELEMENTO_ALEROS, ELEMENTO_ZAPATA_ALEROS, ELEMENTOS_DEL_CABEZAL,
    MURO_CABEZAL, MURO_ALERO, CargaDeCabezal, CombinacionDeEstabilidad,
    SolicitacionDeElemento, EntornoDelCabezal, EstabilidadDelCabezal,
    REGIMEN_RESISTENCIA_K0, REGIMEN_RESISTENCIA_CEDENTE,
    REGIMENES_DE_RESISTENCIA, MINIMOS_MAS_EXIGENTE, MINIMOS_SOLO_AASHTO,
    REGLAS_DE_MINIMOS, TRACCION_NULA, TRACCION_ADMISIBLE_E060,
    CRITERIOS_DE_TRACCION_CICLOPEO, CLASE_EXPOSICION_1, CLASE_EXPOSICION_2,
    CLASES_DE_EXPOSICION, MARCO_E060, MOTIVO_METODO_NO_EVALUABLE_ARMADO,
    SECCION_PANTALLA, SECCION_PUNTA, SECCION_TALON, SECCION_ALERO,
    SECCION_ALERO_MITAD, SECCION_TALON_ALERO, SECCIONES_DEL_ARMADO,
    BarraPropuesta, SolicitacionDeArmado, ArmadoDeSeccion, FilaDeArmado,
    ArmadoDelCabezal,
)
from src.modelos.proyecto import (
    PeriodoRetorno, PerfilFamilia, Clasificacion, GobiernoPorReceptor,
    ResultadoPunto, EscalonSinCabida, PasoDiseno, ModoDeResolucion, Libre,
    DeTabla, EnRango, Derivada, DeEnsayo, DeCatalogo, Resolucion,
    _MODO_DE_TIPO, modo_de, Poblacion, VariableDeEntrada, VacioAdmitido,
    CabeceraCSV, CorridaDelBarrido, FilaDelBarrido, ResultadoDeBarrido,
)
from src.modelos.durabilidad import (
    DURABILIDAD_SIN_ENSAYOS, ENSAYOS_DE_DURABILIDAD, EnsayosDurabilidad,
    EfectoDeDurabilidad, ReglaDeDurabilidad, DictamenDurabilidad,
)
from src.modelos.hidrologia import (
    ORIGEN_CAUDAL_DECLARADO, ORIGEN_CAUDAL_CALCULADO,
    LEYENDA_CAUDAL_DECLARADO, LEYENDA_CAUDAL_CALCULADO, Cuenca,
    RegistroDeLluvia, SerieDeEstacion, EntradaHidrologica,
    AjusteDeDistribucion, CaudalDeDiseno,
)
from src.modelos.estructural import (
    CargaVivaEnterrada, DemandaMarco, GeometriaPortico, EsfuerzoDeSeccion,
    DisenoPortico, ResultadoEstructural,
    MOTIVO_METODO_NO_EVALUABLE_ESTRUCTURAL,
)
from src.modelos.remanso import (
    GeometriaMarco, RemansoCanal, MOTIVO_METODO_NO_EVALUABLE_REMANSO,
    MOTIVO_METODO_NO_EVALUABLE_EVENTO_EXTREMO,
    MOTIVO_METODO_NO_EVALUABLE_CABEZAL, METODO_REMANSO_EMBALSE_A_NIVEL,
    METODO_REMANSO_COTA_AFECTACION, METODO_REMANSO_PERFIL_PASO_A_PASO,
    METODOS_DE_REMANSO, UMBRAL_V8_SIN_DESBORDE, UMBRAL_V8_DESBORDE_ADMITIDO,
    UMBRALES_V8, DerechoDeViaDelPunto,
    MOTIVO_METODO_NO_EVALUABLE_REMANSO_PERFIL, RAMA_REMANSO_M1,
    RAMA_REMANSO_S1, RAMA_REMANSO_NINGUNA, RemansoAguasArriba,
    EventoExtremoDelPunto, REGIMEN_EVENTO_LAMINA_LIBRE,
    REGIMEN_EVENTO_A_PRESION, HidraulicaDelEventoExtremo,
    SUPERFICIE_CRESTA_PAVIMENTADA, SUPERFICIE_CRESTA_GRAVA,
    SUPERFICIES_CRESTA, PANEL_DESBORDE_PROFUNDO, PANEL_DESBORDE_SOMERO,
    RepartoDelDesborde, DatosDeExpediente,
)
from src.modelos.metrados import (
    MOTIVO_METODO_NO_EVALUABLE_METRADO, RUBRO_CONDUCTO, RUBRO_EXCAVACION,
    RUBRO_CONCRETO, RUBRO_ACERO, RUBRO_LOSA, RUBRO_ENROCADO, RUBRO_GEOTEXTIL,
    RUBROS_DE_METRADO, PARTIDA_DEL_EG2013, PARTIDA_ESPECIAL, RenglonDeMetrado,
    MetradoDelPunto, TotalDePartida, ESTADO_RASANTE_COMPATIBLE,
    ESTADO_RASANTE_SUBIR, ESTADO_RASANTE_SIN_TAMIZADO,
    FilaCompatibilidadRasante,
)


_SUBMODULOS = (errores, base, memoria, conducto, hidraulica, rasante_espaciamiento, cabezal, proyecto, durabilidad, hidrologia, estructural, remanso, metrados,)

# `__module__` de las clases: las del paquete se declaran en `src.modelos`.
for _sub in _SUBMODULOS:
    for _objeto in vars(_sub).values():
        if isinstance(_objeto, type) and _objeto.__module__ == _sub.__name__:
            _objeto.__module__ = __name__
del _sub, _objeto
