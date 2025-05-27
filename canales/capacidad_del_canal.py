import numpy as np
import pandas as pd
from scipy.optimize import minimize

# CONFIGURACION = 'BASE 10'
CONFIGURACION = 'BASE 2'
# CONFIGURACION = 'LOGARITMO NATURAL'

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

def informacion_transmitida_objetivo(frecuencias_entrada):
    frecuencias_entrada = np.array(frecuencias_entrada)
    frecuencias_entrada = frecuencias_entrada / np.sum(frecuencias_entrada)
    
    producto_matriz = np.array([frecuencias_entrada[i] * matriz_confiabilidad[i] for i in range(n)])
    
    frecuencias_salida = np.sum(producto_matriz, axis=0)
    
    nueva_matriz = np.zeros_like(matriz_confiabilidad)
    for i in range(n):
        for j in range(n):
            denominador = np.sum(frecuencias_salida * matriz_confiabilidad[:, j])
            nueva_matriz[i][j] = matriz_confiabilidad[i][j] * np.log2(matriz_confiabilidad[i][j] / denominador)
    
    vector_multiplicado_por_frecuencia = np.array([nueva_matriz[i, i] * frecuencias_entrada[i] for i in range(n)])
    
    informacion_transmitida = np.sum(vector_multiplicado_por_frecuencia)
    
    return -informacion_transmitida

restricciones = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

limites = [(0.0001, 1) for _ in range(n)]

resultado = minimize(informacion_transmitida_objetivo, 
                     np.ones(n) / n,
                     bounds=limites,
                     constraints=restricciones)

frecuencias_optimas = resultado.x

producto_matriz_optimas = np.array([frecuencias_optimas[i] * matriz_confiabilidad[i] for i in range(n)])
frecuencias_salida_optimas = np.sum(producto_matriz_optimas, axis=0)

nueva_matriz_optimas = np.zeros_like(matriz_confiabilidad)
for i in range(n):
    for j in range(n):
        denominador = np.sum(frecuencias_salida_optimas * matriz_confiabilidad[:, j])
        nueva_matriz_optimas[i][j] = matriz_confiabilidad[i][j] * np.log2(matriz_confiabilidad[i][j] / denominador)

suma_por_fila_optimas = np.sum(nueva_matriz_optimas, axis=1)

vector_multiplicado_por_frecuencia_optimas = np.array([nueva_matriz_optimas[i, i] * frecuencias_optimas[i] for i in range(n)])

informacion_transmitida_optimas = np.sum(vector_multiplicado_por_frecuencia_optimas)

with open('capacidad_del_canal.txt', 'w', encoding="utf-8") as f:
    f.write("Frecuencias óptimas:\n")
    f.write(str(frecuencias_optimas) + '\n\n')
    
    f.write("Producto del vector de probabilidades con la matriz de confiabilidad:\n")
    f.write(str(producto_matriz_optimas) + '\n\n')
    
    f.write("Frecuencias de salida (suma por columna):\n")
    f.write(str(frecuencias_salida_optimas) + '\n\n')
    
    f.write(f"Fórmula:\nMATRIZ_CONFIABILIDAD[i, j] * log2(MATRIZ_CONFIABILIDAD[i, j] / (sum(FRECUENCIA_DE_ENTRADA[k] * MATRIZ_CONFIABILIDAD[k, j] for k in range(n))))\n")
    f.write(str(nueva_matriz_optimas) + '\n\n')
    
    f.write("Suma por fila de la nueva matriz:\n")
    f.write(str(suma_por_fila_optimas) + '\n\n')
    
    f.write("Cada frecuencia de entrada multiplicada por su valor en el vector anterior:\n")
    f.write(str(vector_multiplicado_por_frecuencia_optimas) + '\n\n')
    
    f.write(f"Información transmitida con frecuencias óptimas: {informacion_transmitida_optimas:.4f}\n")
