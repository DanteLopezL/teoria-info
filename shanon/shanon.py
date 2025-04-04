import numpy as np
import math
from utils.utils import sort_and_order_frequencies, binary_expansion
import polars as pl


def print_table(matrix: np.ndarray, binaries: list[tuple[str, str]]):
    letters = [i[0] for i in binaries]
    freq = [i[0] for i in matrix]
    fi = [i[1] for i in matrix]
    fip = [i[2] for i in matrix]
    lk = [i[3] for i in matrix]
    binary = [i[1] for i in binaries]
    print(
        pl.DataFrame(
            {
                "LETTER": letters,
                "FREQ": freq,
                "fi": fi,
                "Fi": fip,
                "lk": lk,
                "BINARY": binary,
            }
        )
    )


def shanon(text: str) -> None:
    frequencies = sort_and_order_frequencies(text)
    total_freq = sum(num for _, num in frequencies)
    base_matrix: np.ndarray = np.zeros((len(frequencies), 4))
    binaries: list[tuple[str, str]] = []
    for i in range(len(frequencies)):
        base_matrix[i, 0] = frequencies[i][1]
        base_matrix[i, 1] = frequencies[i][1] / total_freq
        base_matrix[i, 2] = (
            0 if i == 0 else base_matrix[i - 1, 1] + base_matrix[i - 1, 2]
        )
        base_matrix[i, 3] = math.ceil(math.log2(1 / base_matrix[i, 1]))
        num = float(base_matrix[i, 2])
        lk = int(base_matrix[i, 3])
        binaries.append(
            (
                frequencies[i][0],
                "".join(map(str, [i for i in binary_expansion(num, lk)])),
            )
        )
    print_table(base_matrix, binaries)

    lms = sum(base_matrix[:, 1] * base_matrix[:, 3])
    rc = 8 / lms
    print(f"lms: {lms} , rc: {rc},  lme: 8")


def main():
    text = "Jos sä tahdot niin tullen kalioden läpi"
    shanon(text)


if __name__ == "__main__":
    main()
