# Comandos exactos de la validacion (generado de los comandos.txt de cada caso)

Constructores de entradas (fuera del repo): python /tmp/validacion_web/scripts/arma_*.py <dir> [<D_ft>] <base|alt|publicada>

Recalculo independiente: python /tmp/validacion_web/scripts/recalculo_mano.py ; python /tmp/validacion_web/scripts/compara_wisdot.py ; python /tmp/validacion_web/scripts/compara_tu107.py

Ventana real: cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas xvfb-run -a python /tmp/validacion_web/scripts/gui_validacion.py <tdot_ex2|hidro|wisdot> /tmp/validacion_web/gui/<caso>

Tablas y resultados: python /tmp/validacion_web/scripts/genera_resultados.py ; python /tmp/validacion_web/scripts/invariancia.py ; python /tmp/validacion_web/scripts/arma_resultados_json.py

## casos/HIDRO_UPAO_UNC/alt/comandos.txt
```
# 2026-11-15T04:12:00 [cli_TR100_50] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/externos.json --cuencas /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/cuencas.csv --estacion /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/estacion.csv --datos-sitio /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/sitio.json --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=gumbel --declarar 'riesgo_admisible_propietario={"quebrada_importante": {"R": 0.222178640, "n": 25}, "quebrada_menor": {"R": 0.261430897, "n": 15}}' --proyecto 'Validacion hidrologia UPAO/UNC alt' --json /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/salida/cli_TR100_50.informe.json

# 2026-11-15T04:12:01 [cli_TR500_100] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/externos.json --cuencas /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/cuencas.csv --estacion /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/estacion.csv --datos-sitio /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/sitio.json --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=gumbel --declarar 'riesgo_admisible_propietario={"quebrada_importante": {"R": 0.048818199, "n": 25}, "quebrada_menor": {"R": 0.139941645, "n": 15}}' --proyecto 'Validacion hidrologia UPAO/UNC alt' --json /tmp/validacion_web/casos/HIDRO_UPAO_UNC/alt/salida/cli_TR500_100.informe.json

```
## casos/HIDRO_UPAO_UNC/base/comandos.txt
```
# 2026-11-15T04:11:35 [prevuelo] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/puntos.csv --alcance perfil --prevuelo --datos-externos /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/externos.json --cuencas /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/cuencas.csv --estacion /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/estacion.csv --datos-sitio /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/sitio.json --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=gumbel --declarar 'riesgo_admisible_propietario={"quebrada_importante": {"R": 0.222178640, "n": 25}, "quebrada_menor": {"R": 0.261430897, "n": 15}}'

# 2026-11-15T04:11:36 [cli_TR100_50] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/externos.json --cuencas /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/cuencas.csv --estacion /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/estacion.csv --datos-sitio /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/sitio.json --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=gumbel --declarar 'riesgo_admisible_propietario={"quebrada_importante": {"R": 0.222178640, "n": 25}, "quebrada_menor": {"R": 0.261430897, "n": 15}}' --proyecto 'Validacion hidrologia UPAO/UNC' --json /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/salida/cli_TR100_50.informe.json --html /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/salida/memoria_TR100_50.html

# 2026-11-15T04:11:59 [cli_TR500_100] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/externos.json --cuencas /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/cuencas.csv --estacion /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/estacion.csv --datos-sitio /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/sitio.json --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=gumbel --declarar 'riesgo_admisible_propietario={"quebrada_importante": {"R": 0.048818199, "n": 25}, "quebrada_menor": {"R": 0.139941645, "n": 15}}' --proyecto 'Validacion hidrologia UPAO/UNC TR500' --json /tmp/validacion_web/casos/HIDRO_UPAO_UNC/base/salida/cli_TR500_100.informe.json

```
## casos/OBRA_DALE/comandos.txt
```
# 2026-11-15T04:17:12 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_DALE/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_DALE/externos.json --declarar 'diametros_normalizados={"inicio": 2.8956, "paso": 0.3048}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {2896: 0.2667, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --json /tmp/validacion_web/casos/OBRA_DALE/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_DALE/salida/memoria.html

# 2026-11-15T04:17:24 [cli_solo_concreto] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_DALE/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_DALE/externos_solo_concreto.json --declarar 'diametros_normalizados={"inicio": 2.8956, "paso": 0.3048}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {2896: 0.2667, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --json /tmp/validacion_web/casos/OBRA_DALE/salida/cli_solo_concreto.informe.json --html /tmp/validacion_web/casos/OBRA_DALE/salida/memoria_solo_concreto.html

```
## casos/OBRA_TU107/alt/comandos.txt
```
# 2026-11-15T04:26:32 [cli_dick_peschke] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_TU107/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_TU107/alt/externos.json --cuencas /tmp/validacion_web/casos/OBRA_TU107/alt/cuencas.csv --estacion /tmp/validacion_web/casos/OBRA_TU107/alt/estacion.csv --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=lognormal_2p --declarar coeficiente_uniformidad_temez=no_aplicar --proyecto 'Obra real TU-107 hidrologia alt dick_peschke' --json /tmp/validacion_web/casos/OBRA_TU107/alt/salida/cli_dick_peschke.informe.json

# 2026-11-15T04:26:33 [cli_tabla04] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_TU107/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_TU107/alt/externos.json --cuencas /tmp/validacion_web/casos/OBRA_TU107/alt/cuencas.csv --estacion /tmp/validacion_web/casos/OBRA_TU107/alt/estacion.csv --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=lognormal_2p --declarar coeficiente_uniformidad_temez=no_aplicar --declarar relacion_intensidad_duracion=tabla_04_coeficientes_de_duracion --proyecto 'Obra real TU-107 hidrologia alt tabla04' --json /tmp/validacion_web/casos/OBRA_TU107/alt/salida/cli_tabla04.informe.json

```
## casos/OBRA_TU107/base/comandos.txt
```
# 2026-11-15T04:26:29 [cli_dick_peschke] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_TU107/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_TU107/base/externos.json --cuencas /tmp/validacion_web/casos/OBRA_TU107/base/cuencas.csv --estacion /tmp/validacion_web/casos/OBRA_TU107/base/estacion.csv --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=lognormal_2p --declarar coeficiente_uniformidad_temez=no_aplicar --proyecto 'Obra real TU-107 hidrologia base dick_peschke' --json /tmp/validacion_web/casos/OBRA_TU107/base/salida/cli_dick_peschke.informe.json

# 2026-11-15T04:26:30 [cli_tabla04] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_TU107/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_TU107/base/externos.json --cuencas /tmp/validacion_web/casos/OBRA_TU107/base/cuencas.csv --estacion /tmp/validacion_web/casos/OBRA_TU107/base/estacion.csv --declarar homogeneidad_serie_fen=serie_completa --declarar distribucion_precipitacion_maxima=lognormal_2p --declarar coeficiente_uniformidad_temez=no_aplicar --declarar relacion_intensidad_duracion=tabla_04_coeficientes_de_duracion --proyecto 'Obra real TU-107 hidrologia base tabla04' --json /tmp/validacion_web/casos/OBRA_TU107/base/salida/cli_tabla04.informe.json

```
## casos/OBRA_WISDOT/alt/D2.0ft/comandos.txt
```
# 2026-11-15T04:22:46 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.0ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.0ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.6096, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {610: 0.09525, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.0 ft alt' --json /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.0ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.0ft/salida/memoria.html

```
## casos/OBRA_WISDOT/alt/D2.25ft/comandos.txt
```
# 2026-11-15T04:22:47 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.25ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.25ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.6858000000000001, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {686: 0.10325000000000001, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.25 ft alt' --json /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.25ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.25ft/salida/memoria.html

```
## casos/OBRA_WISDOT/alt/D2.5ft/comandos.txt
```
# 2026-11-15T04:22:48 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.5ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.5ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.762, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {762: 0.111125, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.5 ft alt' --json /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.5ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/alt/D2.5ft/salida/memoria.html

```
## casos/OBRA_WISDOT/alt/D3.0ft/comandos.txt
```
# 2026-11-15T04:22:48 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/alt/D3.0ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/alt/D3.0ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.9144000000000001, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.127, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=3.0 ft alt' --json /tmp/validacion_web/casos/OBRA_WISDOT/alt/D3.0ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/alt/D3.0ft/salida/memoria.html

```
## casos/OBRA_WISDOT/base/D2.0ft/comandos.txt
```
# 2026-11-15T04:22:42 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.0ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.0ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.6096, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {610: 0.0762, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.0 ft base' --json /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.0ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.0ft/salida/memoria.html

```
## casos/OBRA_WISDOT/base/D2.25ft/comandos.txt
```
# 2026-11-15T04:22:43 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.25ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.25ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.6858000000000001, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {686: 0.0826, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.25 ft base' --json /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.25ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.25ft/salida/memoria.html

```
## casos/OBRA_WISDOT/base/D2.5ft/comandos.txt
```
# 2026-11-15T04:22:44 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.5ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.5ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.762, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {762: 0.0889, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=2.5 ft base' --json /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.5ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/base/D2.5ft/salida/memoria.html

```
## casos/OBRA_WISDOT/base/D3.0ft/comandos.txt
```
# 2026-11-15T04:22:45 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/OBRA_WISDOT/base/D3.0ft/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/OBRA_WISDOT/base/D3.0ft/externos.json --declarar 'diametros_normalizados={"inicio": 0.9144000000000001, "paso": 5.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 900: 0.1}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Obra real WisDOT STH 32 D=3.0 ft base' --json /tmp/validacion_web/casos/OBRA_WISDOT/base/D3.0ft/salida/cli.informe.json --html /tmp/validacion_web/casos/OBRA_WISDOT/base/D3.0ft/salida/memoria.html

```
## casos/TDOT_EX1/alt/comandos.txt
```
# 2026-11-15T04:07:52 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX1/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX1/alt/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX1/alt/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.1 alt' --json /tmp/validacion_web/casos/TDOT_EX1/alt/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX1/alt/salida/memoria.html

```
## casos/TDOT_EX1/base/comandos.txt
```
# 2026-11-15T04:07:51 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX1/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX1/base/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX1/base/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.1 base' --json /tmp/validacion_web/casos/TDOT_EX1/base/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX1/base/salida/memoria.html

```
## casos/TDOT_EX2/alt/comandos.txt
```
# 2026-11-15T04:06:50 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX2/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX2/alt/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX2/alt/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.2 (HY-8) alt' --json /tmp/validacion_web/casos/TDOT_EX2/alt/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX2/alt/salida/memoria.html

```
## casos/TDOT_EX2/base/comandos.txt
```
# 2026-11-15T04:06:49 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX2/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX2/base/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX2/base/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.2 (HY-8) base' --json /tmp/validacion_web/casos/TDOT_EX2/base/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX2/base/salida/memoria.html

# 2026-11-15T04:20:08 [prevuelo] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX2/base/puntos.csv --alcance perfil --prevuelo --datos-externos /tmp/validacion_web/casos/TDOT_EX2/base/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX2/base/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}'

```
## casos/TDOT_EX2/publicada/comandos.txt
```
# 2026-11-15T04:06:52 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX2/publicada/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX2/publicada/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX2/publicada/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.2 (HY-8) publicada' --json /tmp/validacion_web/casos/TDOT_EX2/publicada/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX2/publicada/salida/memoria.html

```
## casos/TDOT_EX4/alt/comandos.txt
```
# 2026-11-15T04:08:43 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX4/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX4/alt/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX4/alt/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 2.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 900: 0.1, 1050: 0.113, 1200: 0.125}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.4 alt' --json /tmp/validacion_web/casos/TDOT_EX4/alt/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX4/alt/salida/memoria.html

```
## casos/TDOT_EX4/base/comandos.txt
```
# 2026-11-15T04:08:41 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX4/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX4/base/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX4/base/sitio.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 2.0}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 900: 0.1, 1050: 0.113, 1200: 0.125}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --proyecto 'Validacion TDOT Ej.4 base' --json /tmp/validacion_web/casos/TDOT_EX4/base/salida/cli.informe.json --html /tmp/validacion_web/casos/TDOT_EX4/base/salida/memoria.html

```
## casos/TDOT_EX4/diseno_libre/comandos.txt
```
# 2026-11-15T04:09:26 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/TDOT_EX4/diseno_libre/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/TDOT_EX4/diseno_libre/externos.json --datos-sitio /tmp/validacion_web/casos/TDOT_EX4/diseno_libre/sitio.json --proyecto 'TDOT Ej.4 diseno libre de la app' --json /tmp/validacion_web/casos/TDOT_EX4/diseno_libre/salida/cli.informe.json

```
## casos/UNC_ALC36/alt/comandos.txt
```
# 2026-11-15T04:14:06 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/UNC_ALC36/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/UNC_ALC36/alt/externos.json --declarar v_max_concreto_eleccion=3.0 --proyecto 'Validacion UNC alcantarilla 36in' --json /tmp/validacion_web/casos/UNC_ALC36/alt/salida/cli.informe.json --html /tmp/validacion_web/casos/UNC_ALC36/alt/salida/memoria.html

```
## casos/UNC_ALC36/base/comandos.txt
```
# 2026-11-15T04:14:05 [cli_perfil] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/UNC_ALC36/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/UNC_ALC36/base/externos.json --declarar v_max_concreto_eleccion=3.0 --proyecto 'Validacion UNC alcantarilla 36in' --json /tmp/validacion_web/casos/UNC_ALC36/base/salida/cli.informe.json --html /tmp/validacion_web/casos/UNC_ALC36/base/salida/memoria.html

```
## casos/UPAO_MANNING/alt/comandos.txt
```
# 2026-11-15T04:14:30 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/UPAO_MANNING/alt/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/UPAO_MANNING/alt/externos.json --proyecto 'Validacion UPAO alcantarillas' --json /tmp/validacion_web/casos/UPAO_MANNING/alt/salida/cli.informe.json

```
## casos/UPAO_MANNING/base/comandos.txt
```
# 2026-11-15T04:14:29 [cli_perfil] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/casos/UPAO_MANNING/base/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/casos/UPAO_MANNING/base/externos.json --proyecto 'Validacion UPAO alcantarillas' --json /tmp/validacion_web/casos/UPAO_MANNING/base/salida/cli.informe.json

```
## defectos/D1_progresion_redondeo/comandos.txt
```
# 2026-11-15T04:13:32 [cli] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/defectos/D1_progresion_redondeo/puntos.csv --alcance perfil --datos-externos /tmp/validacion_web/defectos/D1_progresion_redondeo/externos.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1070: 0.1143, 1219: 0.127, 1220: 0.127, 1372: 0.1397, 1370: 0.1397}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --json /tmp/validacion_web/defectos/D1_progresion_redondeo/salida/cli.informe.json

```
## defectos/O2_NF_y_V7/comandos.txt
```
# 2026-11-15T04:20:21 [sin_nf] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/defectos/O2_NF_y_V7/puntos_sin_nf.csv --alcance perfil --datos-externos /tmp/validacion_web/defectos/O2_NF_y_V7/externos.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --json /tmp/validacion_web/defectos/O2_NF_y_V7/salida/sin_nf.json

# 2026-11-15T04:20:22 [nf_10m] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py /tmp/validacion_web/defectos/O2_NF_y_V7/puntos_nf_10m.csv --alcance perfil --datos-externos /tmp/validacion_web/defectos/O2_NF_y_V7/externos.json --declarar 'diametros_normalizados={"inicio": 0.9144, "paso": 0.1524}' --declarar 'espesor_pared_conducto={"concreto_reforzado": {914: 0.1016, 1067: 0.1143, 1219: 0.127, 1372: 0.1397, 1524: 0.1524, 900: 0.1, 1050: 0.113, 1200: 0.125, 1350: 0.138, 1500: 0.15}, "hdpe": {900: 0.08975, 1050: 0.0846, 1200: 0.0985}}' --json /tmp/validacion_web/defectos/O2_NF_y_V7/salida/nf_10m.json

```
## gui/hidro/comandos.txt
```
# 2026-11-15T04:16:50 [cli_desde_sesion] rc=1
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py --sesion /tmp/validacion_web/gui/hidro/ventana.sesion.json --json /tmp/validacion_web/gui/hidro/cli_desde_sesion.informe.json

```
## gui/tdot_ex2/comandos.txt
```
# 2026-11-15T04:16:49 [cli_desde_sesion] rc=0
cd /home/user/val_web && NORMAS_DIR=/home/user/andy-rba30/normas python cli.py --sesion /tmp/validacion_web/gui/tdot_ex2/ventana.sesion.json --json /tmp/validacion_web/gui/tdot_ex2/cli_desde_sesion.informe.json

```
