"""
GRAFICACION DE SEÑALES Y TRANSFORMACIONES

Grafica una señal x(t) y sus transformaciones en amplitud y en tiempo.
Todas las transformaciones se definen con funciones lambda.

    y(t) = A * x(a*t + b) + B      A, B -> amplitud    a, b -> tiempo
"""

import numpy as np
import matplotlib.pyplot as plt

# --- 1. Señal original: una lambda que se puede evaluar en cualquier t -----
#     Cambia esta línea (y el nombre) para probar con otra señal.
nombre = "e^(-t)·sen(2πt)·u(t)"
x = lambda t: np.exp(-t) * np.sin(2 * np.pi * t) * (t >= 0)

t = np.linspace(-5, 5, 1000)          # eje de tiempo: 1000 puntos de -5 a 5

# --- 2. Transformaciones: cada una es (título, lambda) ---------------------
transformaciones = [
    ("Original                 x(t)",        lambda t: x(t)),
    ("Amplificación          2·x(t)",        lambda t: 2 * x(t)),
    ("Reflexión en amplitud  -x(t)",         lambda t: -x(t)),
    ("Desplazamiento vertical  x(t) + 1",    lambda t: x(t) + 1),
    ("Retardo                  x(t - 2)",    lambda t: x(t - 2)),
    ("Adelanto                 x(t + 2)",    lambda t: x(t + 2)),
    ("Reflexión en tiempo      x(-t)",       lambda t: x(-t)),
    ("Compresión               x(2t)",       lambda t: x(2 * t)),
    ("Expansión                x(t/2)",      lambda t: x(t / 2)),
]

# --- 3. Una gráfica por transformación ------------------------------------
fig, ejes = plt.subplots(3, 3, figsize=(13, 8))
fig.suptitle(f"Señal  x(t) = {nombre}  y sus transformaciones", fontsize=13)

for eje, (titulo, y) in zip(ejes.ravel(), transformaciones):
    eje.plot(t, x(t), "--", color="0.7", linewidth=1, label="original")
    eje.plot(t, y(t), "r", linewidth=2, label="transformada")
    eje.set_title(titulo, fontsize=10, family="monospace")
    eje.set_xlabel("t [s]")
    eje.set_ylabel("amplitud")
    eje.set_xlim(-5, 5)
    eje.set_ylim(-2.2, 2.2)
    eje.grid(True, alpha=0.4)
    eje.axhline(0, color="k", linewidth=0.8)
    eje.axvline(0, color="k", linewidth=0.8)

ejes[0, 0].legend(fontsize=8, loc="upper right")
plt.tight_layout()
plt.show()
