# DATOS DE PRUEBA — escenarios de los ensayos de diseño del cabezal

**No son datos de ningún proyecto.** Son entradas sintéticas que el revisor
independiente de los ensayos de diseño del cabezal (VE-3,
`proceso/planes_mejora/ve3_estado/ENSAYOS_DISENO_CABEZAL.md`) escribió para
probar la app; se copian aquí, sin cambios, para que los tests de VE-3.14
(`tests/test_ve3_14_cabezal.py`) las corran sin depender de una carpeta de
fuera del repositorio.

- `E5_arcilla_blanda/`: suelo de fundación cohesivo (c = 40 kPa, φ = 0),
  cabezal de salida alto. Con los criterios de archivo no hay zapata corrida
  que cumpla la estabilidad dentro del tope: el escenario con el que la app
  entregaba 5.68 × 1.70 m (H-6 de los ensayos) y que desde VE-3.14 declara
  «no factible» sin inflar el peralte.
- `E2_alto/`: relleno alto (H_c de la salida 4.51 m), suelo granular. Con los
  criterios de archivo la pantalla de 0.30 m de la regla no se podía armar
  (A1 a A6 de la pantalla y del alero, H-1 de los ensayos) y la app la
  entregaba así; desde VE-3.14 la pantalla se dimensiona por su armado.

El comando con que se corre está en el test; las declaraciones en caliente
del revisor están en `declaraciones.json`.
