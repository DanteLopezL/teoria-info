def digit_sum(num : int):
    result = 0
    num_str = str(num)
    for digit in num_str:
        result += int(digit)
    return result


def lz77(
    ruta_archivo, tam_ventana_historia, tam_ventana_futura, archivo_salida
):
    with open(ruta_archivo, "r") as archivo:
        datos = archivo.read().lower().replace(" ", "").replace("\n", "")

    datos_comprimidos = []  # Almacena las tripletas
    posicion_actual = tam_ventana_historia
    paso = 1

    with open(archivo_salida, "w") as salida:
        while posicion_actual < len(datos):
            # Determina los límites de la ventana histórica y de la ventana de búsqueda futura
            inicio_ventana = max(0, posicion_actual - tam_ventana_historia)
            fin_ventana_futura = min(posicion_actual + tam_ventana_futura, len(datos))

            # DefinE la ventana histórica y la ventana de búsqueda futura
            ventana_historia = datos[inicio_ventana:posicion_actual]
            ventana_futura = datos[posicion_actual:fin_ventana_futura]

            # Inicializa las variables para el desplazamiento y la longitud de coincidencia máxima
            longitud_coincidencia = 0
            desplazamiento_coincidencia = 0
            siguiente_caracter = ""

            # Busca la coincidencia más larga en la ventana de búsqueda
            for i in range(len(ventana_historia)):
                longitud = 0
                while (
                    i + longitud < len(ventana_historia)
                    and longitud < len(ventana_futura)
                    and ventana_historia[i + longitud] == ventana_futura[longitud]
                ):
                    longitud += 1

                # Actualiza la coincidencia más larga encontrada
                if longitud > longitud_coincidencia:
                    longitud_coincidencia = longitud
                    desplazamiento_coincidencia = len(ventana_historia) - i

            # Determina el carácter siguiente y marcar espacio o salto de línea si corresponde
            if longitud_coincidencia < len(ventana_futura):
                siguiente_caracter = ventana_futura[longitud_coincidencia]
                if siguiente_caracter == " ":
                    siguiente_caracter = "esp"
                elif siguiente_caracter == "\n":
                    siguiente_caracter = "SDL"
            else:
                siguiente_caracter = ""

            # Agrega la tripleta (desplazamiento, longitud, caracter) a los datos comprimidos
            datos_comprimidos.append(
                (desplazamiento_coincidencia, longitud_coincidencia, siguiente_caracter)
            )

            # EscribE el paso y el estado de las ventanas en el archivo de salida
            salida.write(f"Paso {paso}:\n")
            salida.write(f"  Posición actual: {posicion_actual}\n")
            salida.write(f"  Ventana histórica: ->{ventana_historia}<-\n")
            salida.write(f"  Ventana futura: ->{ventana_futura}<-\n")
            salida.write(
                f"  Desplazamiento: {desplazamiento_coincidencia}, Longitud: {longitud_coincidencia}, Caracter: '{siguiente_caracter}'\n\n"
            )

            # Avanza A la posición actual
            posicion_actual += (
                longitud_coincidencia + 1
                if siguiente_caracter
                else longitud_coincidencia
            )
            paso += 1  # Incrementar el paso

        salida.write("Resultados finales de la compresión LZ77:\n")
        for tripleta in datos_comprimidos:
            salida.write(f"{tripleta}\n")

    return datos_comprimidos


def main():
    text_route = "lyrics.txt"

    window_size = 38

    print(f"Usando ventana : {window_size}")
    history = round(window_size * (2 / 3))
    print(f"El tamaño de la ventana histórica es: {history}")

    lookahead = window_size - history
    print(f"El tamaño de la ventana futura es: {lookahead}")

    output = f"results{window_size}.txt"

    lz77(text_route, history, lookahead, output)

    print(f"Resultados guardados en {output}")


if __name__ == "__main__":
    main()
