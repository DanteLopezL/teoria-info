import numpy as np
import pandas as pd


CONFIGURACION = "BASE 2"

VECTOR_PROBABILIDADES = [0.19, 0.38, 0.15, 0.28]
CONFIABILIDAD_DEL_CANAL = 0.95

if not np.isclose(np.sum(VECTOR_PROBABILIDADES), 1):
    raise ValueError("La suma de las probabilidades no es igual a 1.")

df_probabilidades = pd.DataFrame(VECTOR_PROBABILIDADES, columns=["Probabilidades"])
probabilidades = np.array(VECTOR_PROBABILIDADES)
probabilidades = probabilidades[probabilidades > 0]

n = len(VECTOR_PROBABILIDADES)
matriz_confiabilidad = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        if i == j:
            matriz_confiabilidad[i][j] = CONFIABILIDAD_DEL_CANAL
        else:
            matriz_confiabilidad[i][j] = (1 - CONFIABILIDAD_DEL_CANAL) / (n - 1)

producto_matriz = np.array(
    [probabilidades[i] * matriz_confiabilidad[i] for i in range(n)]
)
frecuencias_salida = np.sum(producto_matriz, axis=0)
nueva_matriz = np.zeros_like(matriz_confiabilidad)

for i in range(n):
    for j in range(n):
        denominador = np.sum(frecuencias_salida * matriz_confiabilidad[:, j])
        nueva_matriz[i][j] = matriz_confiabilidad[i][j] * np.log2(
            matriz_confiabilidad[i][j] / denominador
        )

suma_por_fila = np.sum(nueva_matriz, axis=1)
vector_multiplicado_por_frecuencia = np.array(
    [nueva_matriz[i, i] * probabilidades[i] for i in range(n)]
)

informacion_transmitida = np.sum(vector_multiplicado_por_frecuencia)

with open("informacion_transmitida.txt", "w", encoding="utf-8") as f:
    f.write("Vector de probabilidades:\n")
    f.write(str(probabilidades) + "\n\n")

    f.write("Matriz de confiabilidad:\n")
    f.write(str(matriz_confiabilidad) + "\n\n")

    f.write("Producto del vector de probabilidades con la matriz de confiabilidad:\n")
    f.write(str(producto_matriz) + "\n\n")

    f.write("Frecuencias de salida (suma por columna):\n")
    f.write(str(frecuencias_salida) + "\n\n")

    f.write(
        "Fórmula:\nMATRIZ_CONFIABILIDAD[i, j] * log2(MATRIZ_CONFIABILIDAD[i, j] / (sum(FRECUENCIA_DE_ENTRADA[k] * MATRIZ_CONFIABILIDAD[k, j] for k in range(n))))\n"
    )
    f.write(str(nueva_matriz) + "\n\n")

    f.write("Suma por fila de la nueva matriz:\n")
    f.write(str(suma_por_fila) + "\n\n")

    f.write(
        "Cada frecuencia de entrada multiplicada por su valor en el vector anterior:\n"
    )
    f.write(str(vector_multiplicado_por_frecuencia) + "\n\n")

    f.write(f"Información transmitida: {informacion_transmitida:.4f}\n")
