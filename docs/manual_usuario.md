# Manual de usuario — Diseño de alcantarillas de cruce de carretera

> Guía práctica para el ingeniero proyectista: cómo preparar sus archivos de entrada,
> correr el análisis a nivel de **perfil** o **expediente**, resolver bloqueos
> pendientes y exportar la memoria de cálculo auditable (CLI y ventana).
>
> Este manual se apoya en [`docs/guia_perfil.md`](guia_perfil.md) (recorrido de
> comandos verificados para nivel de perfil) y en
> [`docs/contrato_entradas.md`](contrato_entradas.md) (origen formal de cada dato),
> sin sustituirlos.

---

## 1. Flujo de trabajo recomendado

1. **Preparar las entradas de la obra:** CSV de puntos críticos (19 columnas),
   archivo `datos_externos.json` y —si es una carretera distinta a la obra del
   repositorio— archivo `sitio.json` (ver plantillas comentadas en [`plantillas/`](../plantillas/README.md)).
2. **Correr el pre-vuelo (`--prevuelo`):** identifica antes de calcular qué datos
   faltan punto a punto y si detienen alguna etapa.
3. **Correr a `--alcance perfil` o `--alcance expediente`:** dimensiona el conducto
   y, en expediente, verifica estabilidad/armado de cabezales, cargas estructurales
   y metrados.
4. **Revisar bloqueos y declarar pendientes:** leer qué criterio (`[A]`) o dato de
   estudio (`[S]` / tablero externo) detuvo cada punto y declararlo sin inventar valores.
5. **Exportar entregables:** memoria resumida (impresión), memoria completa
   (anexo digital HTML/PDF), cuadro resumen CSV y volcado JSON.

---

## 2. Preparar las entradas paso a paso

### 2.1 CSV de puntos críticos (19 columnas fijas)

El CSV debe llevar exactamente estas **19 columnas** (separadas por `,` o `;`):

1. `id` — identificador único del cruce (ej. `A-01`, `B-01`, `C-01`).
2. `progresiva_km` — formato `0+380` o kilómetros decimales (`0.380`).
3. `familia` — `A` (quebrada), `B` (alivio de cuneta) o `C` (cruce de canal).
4. `Q_m3s` — caudal de diseño (m³/s). Obligatorio en `A` y `B` salvo que se suministren `--cuencas` y `--estacion`; vacío permitido en `C` si aún falta el tablero ANA/Junta.
5. `area_ha` — área de cuenca (ha). Obligatoria en `A`; vacía admitida en `C`.
6. `S_cauce` — pendiente longitudinal del cauce natural (m/m). Obligatoria en `A`/`B`; vacía admitida en `C` hasta contar con dato de canal.
7. `cota_terreno` — cota del terreno natural en el cruce (msnm).
8. `cota_rasante` — cota de la rasante vial (msnm).
9. `cota_subrasante` — cota de subrasante (msnm).
10. `cbr_subrasante` — CBR de la subrasante (%).
11. `esviaje_grados` — ángulo de esviaje en grados bajo convención **0° = cruce perpendicular** al eje vial (si un expediente antiguo mide 90° = perpendicular, convertir con `esviaje_app = 90° - esviaje_exp`).
12. `ancho_plataforma` — ancho total de la plataforma vial (m).
13. `cota_fondo_receptor` — cota de fondo del cauce o dren receptor aguas abajo (msnm).
14. `Q_receptor_m3s` — caudal del cuerpo receptor (m³/s); puede ir vacío.
15. `cota_TW` — nivel de agua del receptor en la salida (msnm); puede ir vacío.
16. `sucs_fundacion` — clasificación SUCS del suelo de cimentación (ej. `SP`, `CL`, `SM`).
17. `NF_profundidad_m` — profundidad del nivel freático desde la superficie (m); puede ir vacío.
18. `cota_fondo_entrada` — cota de fondo medida a la entrada (msnm); si va vacía, puede declararse el criterio `origen_cota_fondo_entrada`.
19. `cota_coronacion_canal` — cota de coronación del canal (msnm); obligatoria en Familia `C` para `VC1`, puede ir vacía en `A` y `B`.

**Ejemplo mínimo por familia (`mi_obra/puntos.csv`):**

```csv
id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal
A-01,0+380,A,1.85,120.0,0.012,15.20,17.85,17.35,8.0,10.0,9.60,15.05,,,SM,2.50,15.15,
B-01,0+720,B,0.42,18.0,0.008,16.10,18.20,17.70,10.0,0.0,9.60,15.95,,,SM,3.00,16.05,
C-01,1+140,C,,0.0,,14.80,17.60,17.10,7.0,0.0,9.60,14.65,,,CL,1.80,14.70,16.20
```

### 2.2 `datos_externos.json` (`--datos-externos`)

Reúne los parámetros que no forman columna fija del CSV o los datos entregados por tableros externos (ANA/Junta, EMS, trazo):

```json
{
  "_advertencia": "PLANTILLA DE EJEMPLO — reemplazar con datos de su estudio.",
  "globales": {
    "luz_m": 2.5,
    "TW_m": 0.45,
    "bombeo": 0.025,
    "acceso_mantenimiento_previsto": true
  },
  "puntos": {
    "A-01": { "categoria_tr": "quebrada_importante" },
    "B-01": { "categoria_tr": "cuneta", "ancho_tributario_m": 12.0, "S_cuneta": 0.006, "inicio_tramo_cuneta_km": 0.38 },
    "C-01": { "Q_m3s": 2.40, "S_cauce": 0.0015, "desnivel_perfil_canal_m": 0.20 }
  }
}
```

### 2.3 `sitio.json` (`--datos-sitio`) para otra obra

Para evaluar un corredor distinto sin editar `src/datos_sitio.py`, declare los `[S]` de su corredor con **valor, trazabilidad y fecha**:

```json
{
  "corredor_del_proyecto": {
    "valor": "Tramo ejemplo km 0+000 - 2+000",
    "trazabilidad": "Expediente vial de la obra, plano clave.",
    "fecha": "2026-11-22"
  },
  "PGA_roca_B": {
    "valor": 0.35,
    "trazabilidad": "Mapa de isoaceleraciones / Norma E.030 sobre coordenadas del proyecto.",
    "fecha": "2026-11-22"
  },
  "ZONA_SISMICA_LA_UNION": {
    "valor": 3,
    "trazabilidad": "Anexo 1 de la Norma E.030 vigente segun distrito del proyecto.",
    "fecha": "2026-11-22"
  },
  "region_natural": {
    "valor": "sierra",
    "trazabilidad": "Clasificacion geografica del corredor para Tabla N 34.",
    "fecha": "2026-11-22"
  }
}
```

---

## 3. Ejecutar el análisis (CLI y GUI)

### 3.1 Pre-vuelo antes de calcular

- **En CLI:**
  ```powershell
  python cli.py mi_obra/puntos.csv --datos-externos mi_obra/datos_externos.json --datos-sitio mi_obra/sitio.json --alcance perfil --prevuelo
  ```
  El código de salida es `0` si nada detiene la carga ni las etapas alcanzadas, o `1` si quedan datos requeridos sin aportar.
- **En la ventana (`python -m gui.app`):** cargue las rutas en la **Pestaña 1 · Datos de entrada** y revise el panel inferior **«Anticipo antes de correr»** (es informativo y se actualiza en vivo al cambiar rutas o alcance).

### 3.2 Corrida a nivel de perfil vs. expediente

- **Nivel de perfil** (dimensiona sección hidráulica, verificaciones `V1`–`V10`/`VC`, protección `M6` y geometría `M7`; difiere diseño estructural y cabezal):
  ```powershell
  python cli.py mi_obra/puntos.csv --datos-externos mi_obra/datos_externos.json --datos-sitio mi_obra/sitio.json --alcance perfil --json mi_obra/salida_perfil.json --html mi_obra/memoria_perfil.html --html-resumida mi_obra/resumen_perfil.html --csv-resumen mi_obra/cuadro_perfil.csv
  ```
- **Nivel de expediente** (añade licuefacción, estructural del conducto `M8`, estabilidad/armado del cabezal `M9` y metrados `M12`):
  ```powershell
  python cli.py mi_obra/puntos.csv --datos-externos mi_obra/datos_externos.json --datos-sitio mi_obra/sitio.json --alcance expediente --json mi_obra/salida_exp.json --html mi_obra/memoria_exp.html --html-resumida mi_obra/resumen_exp.html --csv-resumen mi_obra/cuadro_exp.csv
  ```
- **Si `Q_m3s` va vacío en el CSV (Familias A/B):** agregue `--cuencas mi_obra/cuencas.csv --estacion mi_obra/estacion.csv` (o selecciónelos en los campos de hidrología de la Pestaña 1).

---

## 4. Leer bloqueos y declarar pendientes

Cuando una etapa se detiene, el programa **no inventa valores**: registra un `Bloqueo` explícito.

- **En la GUI:** revise la **Pestaña 4 · Resumen**:
  - La tabla **«Criterios pendientes que bloquearon una etapa»** indica la `clave`, `fuente`, `fases`, `puntos`, `responsable`, `evidencia` y **dónde se declara**:
    - Si es criterio `[A]`, vaya a la **Pestaña 2 · Criterios**, selecciónelo y use el editor tipado + **«Aplicar solo a esta corrida»** (si la regla requiere nota justificativa, ingrésela).
    - Si es dato de sitio `[S]`, declárelo en su `sitio.json` (Pestaña 1).
  - La tabla **«Datos faltantes o inválidos que bloquearon una etapa»** indica qué columna del CSV o qué clave de `--datos-externos` falta y en qué pestaña/archivo se completa.
- **En la CLI:** use `--declarar CLAVE=VALOR` (repetible) para criterios `[A]` dentro de su ventana de sensibilidad.
- Para guardar todo el trabajo de la GUI (rutas, alcance, criterios y datos de sitio declarados), use **«Guardar sesion»**; podrá reabrirla en la ventana con **«Cargar sesion»** o reproducirla en consola con `python cli.py --sesion mi_sesion.json`.

---

## 5. Exportar memorias y entregables

- **Memoria resumida (`--html-resumida` / `--pdf-resumida`):** formato conciso para impresión con los resultados por punto, verificaciones, adopciones `[A]` y cuadro de pendientes.
- **Memoria completa (`--html` / `--pdf`):** anexo digital completo con cada paso de cálculo, fórmula, sustitución numérica, citas literales verificadas y anexos de trazabilidad.
- **Cuadro resumen (`--csv-resumen`) y volcado JSON (`--json`):** tabla por punto y estructura auditable completa (incluyendo huellas SHA-1 de entradas y criterios).
- *(En Windows sin librerías nativas GTK/Pango para WeasyPrint, la exportación a PDF guarda el archivo `.html` equivalente junto al destino para imprimirlo desde el navegador con `Ctrl+P → Guardar como PDF`.)*
