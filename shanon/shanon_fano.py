import polars as pl
from typing import Dict, List, Tuple
from utils.utils import sort_and_order_frequencies


def print_table(
    frequencies: List[Tuple[str, int]], codes: Dict[str, str], total_freq: int
) -> None:
    characters: List[str] = [char for char, _ in frequencies]
    freqs: List[int] = [freq for _, freq in frequencies]
    probabilities: List[float] = [freq / total_freq for _, freq in frequencies]
    code_lengths: List[int] = [len(codes.get(char, "")) for char, _ in frequencies]
    code_values: List[str] = [codes.get(char, "") for char, _ in frequencies]
    lms: float = sum(p * l for p, l in zip(probabilities, code_lengths))

    print(
        pl.DataFrame(
            {
                "Character": characters,
                "Frequency": freqs,
                "Probability": [f"{p:.4f}" for p in probabilities],
                "Code": code_values,
                "Code Length": code_lengths,
            }
        )
    )
    print(f"lms: {lms}, lme: 8 , RC: {8 / lms}")


def split_frequencies(
    frequencies: List[Tuple[str, int]], codes: Dict[str, str], current_code: str = ""
) -> None:
    if len(frequencies) == 1:
        codes[frequencies[0][0]] = current_code
        return

    total: int = sum(f[1] for f in frequencies)
    cumulative: int = 0
    best_diff: float = float("inf")
    split_idx: int = 0

    for i in range(len(frequencies) - 1):
        cumulative += frequencies[i][1]
        diff: float = abs(2 * cumulative - total)
        if diff < best_diff:
            best_diff = diff
            split_idx = i

    left: List[Tuple[str, int]] = frequencies[: split_idx + 1]
    right: List[Tuple[str, int]] = frequencies[split_idx + 1 :]

    if left:
        split_frequencies(left, codes, current_code + "0")
    if right:
        split_frequencies(right, codes, current_code + "1")


def shannon_fano(text: str) -> Dict[str, str]:
    frequencies: List[Tuple[str, int]] = sort_and_order_frequencies(text)
    total_freq: int = sum(num for _, num in frequencies)
    codes: Dict[str, str] = {}

    split_frequencies(frequencies, codes)
    print_table(frequencies, codes, total_freq)

    return codes


def __run__() -> None:
    text: str = "Jos sä tahdot niin tullen kalioden läpi"
    shannon_fano(text)


if __name__ == "__main__":
    __run__()
