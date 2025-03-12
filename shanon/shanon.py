import numpy as np
import math

import collections


def sort_and_order_frequencies(text: str) -> list[tuple[str, int]]:
    frequency = collections.Counter(text.replace(" ", "").replace("\n","").lower())
    return sorted(frequency.items(), key=lambda x: (-x[1], -ord(x[0])))


def binary_expansion(num: float, tolerance: float = 1e-10) -> list[int]:
    expansion = []
    history = []

    while True:
        if num >= float(1):
            num = (num - 1) * 2
        else:
            num *= 2
        bit = 1 if num >= float(1) else 0
        expansion.append((num, bit))

        # Check for repeated numbers with a tolerance
        if any(abs(num - h) < tolerance for h in history):
            break
        else:
            history.append(num)
    sequence = [num for _,num in expansion]
    return sequence


def shanon(text: str) -> None:
    frequencies = sort_and_order_frequencies(text)
    total_freq = sum(num for _, num in frequencies)
    base_matrix = np.zeros((len(frequencies), 4))
    binaries = []
    for i in range(len(frequencies)):
        base_matrix[i, 0] = frequencies[i][1]
        base_matrix[i, 1] = frequencies[i][1] / total_freq
        base_matrix[i, 2] = 0 if i == 0 else base_matrix[i - 1, 1] + base_matrix[i - 1, 2]
        base_matrix[i, 3] = math.ceil(math.log2(1 / base_matrix[i, 1]))
        num = base_matrix[i, 2]
        binaries.append("".join(map(str, binary_expansion(float(num)))))

    print(base_matrix)
    print(binaries)
    lms = sum(base_matrix[:,1] * base_matrix[:,3])
    rc = 8/lms
    print(f"lms: {lms} , rc: {rc}")


def __run__():
    text = """
odottakaa vielä ei saa
pyöriä maa
aurinkokin
sammuttakaa
ja tsemppibiisinne
nyt ne verhot kii perukaa häät ristiäiset linnut junat ja internet pysäyttäkää ettekste nää
"""
    
    shanon(text)


if __name__ == '__main__':
    __run__()