
def digit_sum(num) -> int:
    result = 0
    num_str = str(num)
    for i in num_str:
        result += int(i)
    return result

def lz77_compress(data, window_size=20):

    i = 0              # Posición actual en la cadena
    result = []        # Lista donde se almacenará la salida (tuplas)
    step = 1           # Para numerar cada paso

    while i < len(data):
        best_match_distance = 0  # Distancia (offset) para el mejor match encontrado
        best_match_length = 0    # Longitud del mejor match
        # La ventana de búsqueda se limita a los caracteres anteriores hasta i, con un máximo de 'window_size'
        start_window = max(0, i - window_size)

        # Mostrar el estado actual: índice, ventana de búsqueda y vista futura (lookahead buffer)
        print(f"Step {step}:")
        print(f"  Current index (i): {i}")
        print(f"  Search Window: '{data[start_window:i]}'")
        print(f"  Lookahead Buffer: '{data[i:min(i+window_size, len(data))]}'")

        # Buscar la coincidencia más larga en la ventana anterior (diccionario)
        for j in range(start_window, i):
            length = 0
            # Se compara carácter a carácter mientras coincidan y no se exceda la cadena
            while i + length < len(data):
                # Si la parte a comparar está completamente dentro de la ventana de búsqueda
                if j + length < i:
                    if data[j + length] == data[i + length]:
                        length += 1
                    else:
                        break
                else:
                    # En caso de superposición, se permite repetir la secuencia:
                    # Se utiliza el operador módulo para "circular" por la sección encontrada.
                    offset = i - j  # Tamaño efectivo del fragmento en la ventana
                    if data[j + (length % offset)] == data[i + length]:
                        length += 1
                    else:
                        break

            if length > best_match_length:
                best_match_length = length
                best_match_distance = i - j

        # Si se encontró alguna coincidencia (la longitud mayor es mayor que cero)
        if best_match_length > 0:
            # Se toma el siguiente símbolo después de la coincidencia (si existe)
            next_char = data[i + best_match_length] if (i + best_match_length) < len(data) else ''
            print(f"  Match found: Distance = {best_match_distance}, Length = {best_match_length}, Next Char = '{next_char}'")
            result.append((best_match_distance, best_match_length, next_char))
            # El puntero avanza la longitud del match + 1 (para incluir el siguiente carácter)
            i += best_match_length + 1
        else:
            # Si no se encontró coincidencia, se codifica el literal
            print(f"  No match. Output literal: '{data[i]}'")
            result.append((0, 0, data[i]))
            i += 1

        print("-" * 50)
        step += 1

    return result


def main():
    # Cadena de entrada; puede cambiarse por cualquier otra para probar el algoritmo.
    input_str = "abracadabra"
    # También se puede ajustar el tamaño de la ventana según se desee.
    window_size = digit_sum("2077518")

    print("Input string:", input_str)
    print("=" * 50)
    compressed = lz77_compress(input_str, window_size)
    
    print("\nCompression result (tuples):")
    for triple in compressed:
        print(triple)


if __name__ == "__main__":
    main()
