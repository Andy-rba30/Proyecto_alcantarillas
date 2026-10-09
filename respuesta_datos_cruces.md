# ¿Puedo diseñar mis alcantarillas con estos datos?

**Respuesta corta: no, todavía no.** Con tu tabla tienes resuelto lo del
**canal** (Familia C del proyecto: cruce de canal con la vía), pero falta casi
todo lo de la **vía** y lo del **sitio**. Esto está contrastado contra el
encabezado que exige el programa (`M0_carga.COLUMNAS`, documentado en
`docs/guia_perfil.md`).

## 1. Lo que ya tienes y sirve directamente

| Dato de tu tabla | Columna del CSV | Comentario |
|---|---|---|
| PUNTO | `id` | tal cual |
| PROGRESIVA | `progresiva_km` | tal cual (2+756.17) |
| (todos son canales) | `familia` | `C` en los seis puntos |
| Q Diseño | `Q_m3s` | es el caudal correcto para un cruce de canal (no el de cuenca) |
| Pendiente | `S_cauce` | en decimal: 3.4 % se escribe 0.034 |
| ANCH SUP., ANCHO INF., PROF | — | definen la sección del canal; sirven para `luz_m` y la coronación |
| ESTE, NORTE | — | ubican el punto, el programa no los usa |

## 2. Lo que falta y es OBLIGATORIO en toda fila

Sin estos el CSV no carga:

1. `cota_terreno`: cota del terreno natural en el cruce.
2. `cota_rasante` y `cota_subrasante`: cotas de la vía en esa progresiva.
   De ahí sale la cobertura sobre el conducto y la longitud.
3. `cbr_subrasante`: CBR del suelo en el cruce (estudio de suelos).
4. `sucs_fundacion`: clasificación SUCS del suelo de fundación (SM, ML, CL…).
5. `esviaje_grados`: ángulo entre el eje del canal y el eje de la vía.
   Si cruzan perpendiculares es 0.
6. `ancho_plataforma`: ancho total de la plataforma de la vía, en metros.
7. `cota_fondo_receptor`: cota del fondo del canal aguas abajo del cruce.

## 3. Lo que puede ir vacío pero BLOQUEA etapas del cálculo

- `cota_fondo_entrada`: cota del fondo del canal a la entrada. Con tu
  profundidad y la cota de terreno se puede derivar, pero conviene medirla.
- `cota_coronacion_canal`: cota del labio del canal. Sin ella no se verifica
  que la alcantarilla no ahogue el canal (VC1).
- `cota_TW` o `Q_receptor_m3s`: nivel de agua aguas abajo. Para un canal,
  `cota_TW` = cota de fondo + tirante normal del canal. Sin nada de esto el
  cálculo se detiene en el criterio `TW_receptor`.
- `NF_profundidad_m`: nivel freático en cada cruce (estudio geotécnico).
  Sólo frena la verificación de flotación.
- `luz_m`: no es columna; va por la bandera `--luz` o en el JSON de datos
  externos. Usa el ancho superior del canal.

## 4. Dos advertencias sobre tus datos

- **D1 no es alcantarilla.** Su ancho superior es 6.0 m y el umbral del
  Manual de Hidrología es luz ≥ 6.0 m = puente (`LUZ_MAX_ALCANTARILLA`).
  Con Q = 5 m³/s y 3 m de profundidad ese cruce sale del alcance del
  programa. Revisa si la luz libre que vas a cubrir es menor de 6 m.
- **Los cruces de canal se dimensionan como cajón rectangular**, y eso
  exige declarar siete criterios [A] del cajón: `embocadura_cajon`,
  `ke_entrada_cajon`, `n_manning_cajon`, `n_celdas_cajon`,
  `secciones_cajon_normalizadas`, `espesor_pared_cajon`,
  `cobertura_minima_cajon`. Son decisiones tuyas de proyectista, no datos
  de campo. `docs/guia_perfil.md` da un ejemplo de cada uno con `--declarar`.

## 5. Qué hacer ahora

1. Pide al topógrafo, por cada progresiva: cota de rasante, subrasante,
   terreno natural, fondo del canal (entrada y salida), coronación del canal
   y ángulo de cruce.
2. Pide al estudio de suelos, por cada cruce: CBR, SUCS y nivel freático.
3. Arma el CSV con el encabezado completo (copia `tests/ejemplo_puntos.csv`)
   y corre:

   ```sh
   python cli.py tu.csv --alcance perfil --prevuelo --luz 2.85
   ```

   El pre-vuelo lista exactamente qué falta en cada punto antes de calcular.

## 6. Borrador del CSV con lo que ya se sabe

Las celdas vacías son las que faltan (ver secciones 2 y 3):

```csv
id,progresiva_km,familia,Q_m3s,area_ha,S_cauce,cota_terreno,cota_rasante,cota_subrasante,cbr_subrasante,esviaje_grados,ancho_plataforma,cota_fondo_receptor,Q_receptor_m3s,cota_TW,sucs_fundacion,NF_profundidad_m,cota_fondo_entrada,cota_coronacion_canal
C1-L2,2+756.17,C,0.15,,0.034,,,,,,,,,,,,,
C4-L2,3+223.19,C,0.13,,0.010,,,,,,,,,,,,,
C5-L2,3+241.51,C,0.13,,0.010,,,,,,,,,,,,,
D1,3+308.8,C,5.00,,0.010,,,,,,,,,,,,,
C6-L2,3+420.07,C,0.10,,0.015,,,,,,,,,,,,,
C7-L2,4+030.97,C,0.12,,0.013,,,,,,,,,,,,,
```

Cuando tengas las cotas, pásamelas y armo el CSV y el JSON de externos
completos y corremos el perfil.
