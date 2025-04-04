from utils.utils import sort_and_order_frequencies, binary_expansion
import numpy as np
import math
import polars as pl


def print_table(
    frequencies: list[tuple[str, int]],
    fi: list[float],
    matrix: np.ndarray,
    binaries: list[tuple[str, str]],
):
    letters = [i[0] for i in frequencies]
    freq = [i[1] for i in frequencies]
    fx = [i[0] for i in matrix]
    ix = [i[1] for i in matrix]
    binary = [i[1] for i in binaries]
    print(
        pl.DataFrame(
            {
                "LETTERS": letters,
                "FREQ": freq,
                "fi": fi,
                "F(X)": fx,
                "I(X)": ix,
                "BINARY": binary,
            }
        )
    )


def calculate_fi(frequencies: list[tuple[str, int]]) -> tuple[int, list[float]]:
    total = sum([freq for _, freq in frequencies])
    fi = [freq / total for _, freq in frequencies]

    return total, fi


def shanon_fano_elias(text: str):
    frequencies = sort_and_order_frequencies(text)
    _, fi = calculate_fi(frequencies)
    lenght = len(frequencies)
    matrix: np.ndarray = np.zeros((lenght, 2), dtype=float)
    binaries: list[tuple[str, str]] = []
    for i in range(lenght):
        num = fi[i] / 2 if i == 0 else sum(fi[:i]) + (fi[i] / 2)
        lk = math.ceil(math.log2((1 / fi[i]) + 1))
        matrix[i][0] = num
        matrix[i, 1] = lk
        binaries.append(
            (
                frequencies[i][0],
                "".join(map(str, [i for i in binary_expansion(num, lk)])),
            )
        )
    print_table(frequencies, fi, matrix, binaries)
    lms = sum(
        a * b
        for a, b in zip(fi, [float(math.ceil(math.log2((1 / i) + 1))) for i in fi])
    )
    print(f"lms: {lms} lme: {8} RC: {8 / lms}")


def main():
    text = "Jos sä tahdot niin tullen kalioden läpi"
    shanon_fano_elias(text)


if __name__ == "__main__":
    main()
