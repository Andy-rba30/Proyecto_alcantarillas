# Plantillas de entrada (`plantillas/`)

Archivos mínimos de partida para iniciar una obra nueva sin modificar el código
del proyecto. Antes de calcular una obra real, copie esta carpeta y **reemplace
los valores ilustrativos** por los datos levantados en su proyecto.

## Contenido

| Archivo | Uso | Qué contiene |
|---|---|---|
| `familia_A_quebrada.csv` | Entrada CSV mínima — Familia `A` | 1 fila ejemplo (`A-01`) con las **19 columnas fijas** de `M0_carga.COLUMNAS`. |
| `familia_B_alivio_cuneta.csv` | Entrada CSV mínima — Familia `B` | 1 fila ejemplo (`B-01`) con las 19 columnas fijas. |
| `familia_C_canal.csv` | Entrada CSV mínima — Familia `C` | 1 fila ejemplo (`C-01`); deja vacías `Q_m3s`, `area_ha` y `S_cauce` (Tablero 3.1 ANA/Junta) e incluye `cota_coronacion_canal`. |
| `datos_externos.json` | `--datos-externos` / Pestaña 1 | Parámetros globales (`luz_m`, `TW_m`, `L_hidraulico_m`, `bombeo`, `acceso_mantenimiento_previsto`) y por punto (`categoria_tr`, datos de cuneta `B-01`, datos del canal `C-01`). |
| `sitio.json` | `--datos-sitio` / Pestaña 1 | Los **11 datos de sitio `[S]` declarables** con `valor`, `trazabilidad` y `fecha` (`Z_E030` se omite porque el programa lo deriva automáticamente desde `ZONA_SISMICA_LA_UNION`). |
| `sesion_nueva.json` | «Cargar sesión» / `--sesion` | Sesión vacía en formato vigente (`formato_version = 4`) para iniciar un proyecto desde cero en la GUI sin arrastrar estado previo. |

## Significado de los 19 encabezados del CSV

1. `id`: código único del cruce (`A-01`, `B-01`, `C-01`).
2. `progresiva_km`: progresiva (`0+380` o km decimal).
3. `familia`: `A` (quebrada), `B` (alivio de cuneta), `C` (cruce de canal).
4. `Q_m3s`: caudal de diseño (m³/s). Obligatorio en `A`/`B` salvo `--cuencas` + `--estacion`; vacío permitido en `C`.
5. `area_ha`: área de cuenca (ha). Vacía permitida en `C`.
6. `S_cauce`: pendiente longitudinal del cauce natural (m/m). Vacía permitida en `C`.
7. `cota_terreno`: cota del terreno natural en el eje (msnm).
8. `cota_rasante`: cota de la rasante vial (msnm).
9. `cota_subrasante`: cota de la subrasante (msnm).
10. `cbr_subrasante`: CBR de diseño (%).
11. `esviaje_grados`: esviaje respecto a la **perpendicular** al eje vial (`0°` = perpendicular).
12. `ancho_plataforma`: ancho total de plataforma (m).
13. `cota_fondo_receptor`: cota de fondo del cauce o canal receptor aguas abajo (msnm).
14. `Q_receptor_m3s`: caudal del receptor (m³/s), opcional.
15. `cota_TW`: nivel de agua en el receptor (msnm), opcional.
16. `sucs_fundacion`: clasificación SUCS del suelo de fundación (`SM`, `CL`, etc.).
17. `NF_profundidad_m`: profundidad del nivel freático bajo el terreno (m), opcional.
18. `cota_fondo_entrada`: cota de fondo medida a la entrada (msnm), opcional.
19. `cota_coronacion_canal`: cota de coronación del canal (msnm); obligatoria en `C` para `VC1`, opcional en `A`/`B`.

## Secciones aceptadas en `datos_externos.json`

El cargador valida estrictamente tres claves de primer nivel:

- `_advertencia`: texto informativo (el programa no lo usa en cálculos).
- `globales`: diccionario de claves externas válidas para todos los puntos (ej. `luz_m`, `TW_m`, `L_hidraulico_m`, `bombeo` / `peralte`).
- `puntos`: diccionario indexado por `id` del cruce; cada entrada sobrescribe `globales` y aporta claves específicas del punto o de su familia (`categoria_tr`, `ancho_tributario_m`, `S_cuneta`, `inicio_tramo_cuneta_km`, `Q_m3s`, `S_cauce`, `S_conducto`, `desnivel_perfil_canal_m`).

## Verificación rápida por CLI

```powershell
python cli.py plantillas/familia_A_quebrada.csv --datos-externos plantillas/datos_externos.json --datos-sitio plantillas/sitio.json --alcance perfil --prevuelo
python cli.py plantillas/familia_B_alivio_cuneta.csv --datos-externos plantillas/datos_externos.json --datos-sitio plantillas/sitio.json --alcance perfil --prevuelo
python cli.py plantillas/familia_C_canal.csv --datos-externos plantillas/datos_externos.json --datos-sitio plantillas/sitio.json --alcance perfil --prevuelo
```

Para la guía completa paso a paso, consulte [`docs/manual_usuario.md`](../docs/manual_usuario.md) y [`docs/guia_perfil.md`](../docs/guia_perfil.md).
