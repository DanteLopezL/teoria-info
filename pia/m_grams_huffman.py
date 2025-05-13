"""Text Sequence Frequency Analysis and Optimal Coding Tool

This module provides functionality for:
1. Analyzing character sequence frequencies with length-based weighting
2. Generating optimal encodings using dynamic programming
3. Displaying results in tabular format using Polars
4. Command-line interface via Typer

Typical usage:
    python script.py input.txt --m 3 --alpha 1 --sort
"""

from utils import utils
import polars as pl
import typer


def frequency_estimation(text: str, n: int, m: int, alpha: int = 0) -> dict[str, int]:
    """Calculate weighted frequencies of character sequences in text.

    Args:
        text: Input string to analyze
        n: Length of input text
        m: Maximum sequence length to consider
        alpha: Weighting exponent (0 = no weighting)

    Returns:
        Dictionary mapping sequences to their weighted frequencies
        where weights are length^alpha

    Example:
        >>> frequency_estimation("aab", 3, 2, 1)
        {'a': 2, 'b': 1, 'aa': 2, 'ab': 2}
    """
    df: dict[str, int] = {}  # Dictionary to store frequencies

    for i in range(1, m + 1):  # i = 1, 2, ..., m
        for j in range(n - i + 1):  # Slide window over input
            s = text[j : j + i]  # Extract sequence of length i
            if s in df:
                df[s] += i**alpha
            else:
                df[s] = i**alpha

    return df


def optimal_coding(text: str, dc: dict[str, str], n: int, m: int) -> str:
    """Generate optimal encoding for text using provided coding table.

    Args:
        text: Input text to encode
        dc: Dictionary mapping sequences to codes
        n: Length of input text
        m: Maximum sequence length to consider

    Returns:
        Optimally encoded string

    Note:
        Uses dynamic programming to find most efficient encoding
    """
    dn: dict[int, str] = {0: ""}
    for e in range(n):
        for i in range(e, min(m * e + 1, n)):
            k = i + 1
            l = min(i + m, n)

            for j in range(k, l + 1):
                s = text[i:j]

                if s not in dc:
                    continue

                c = dn[i] + dc[s]

                if j not in dn or len(dn[i]) > len(c):
                    dn[j] = c

    return dn.get(n, "")


def approximate_coding(text: str, dc: dict[str, str], n: int, m: int) -> str:
    c = ""
    i = 0
    while i < n:
        r = 0  # best ratio found value
        l = 0  # end of best rato sequence
        for k in range(1, m + 1):
            j = i + k
            if j > n:
                j = n

            s = text[i:j]
            c = dc[s]
            t = len(s) / len(c)
            if t > r:
                r = t
                l = j
        c = c + dc[text[i:l]]
        i = l
    return c


def main(file: str, m: int = 3, alpha: int = 1, sort: bool = False) -> None:
    """Main function to analyze text and generate optimal encoding.

    Args:
        file: Path to input text file
        m: Maximum sequence length (default: 3)
        alpha: Weighting exponent (default: 1)
        sort: Sort frequencies before coding (default: False)

    Workflow:
        1. Reads and preprocesses input file
        2. Calculates sequence frequencies
        3. Generates coding table
        4. Produces optimal encoding
        5. Displays results
    """
    with open(file, "r", encoding="utf-8") as f:
        text = "".join(f.read().split())

    n = len(text)
    frequencies = frequency_estimation(text, n, m)
    weighted_frequencies = frequency_estimation(text, n, m, alpha)

    print("Sequence Frequencies (weighted by i^α):")
    keys = list(weighted_frequencies.keys())
    values = list(frequencies.values())
    weighted_values = list(weighted_frequencies.values())

    print(
        pl.DataFrame(
            {
                "Sequence": keys,
                "Frequency": values,
                f"Weighted (a={alpha})": weighted_values,
            }
        )
    )
    sorted_frequencies = dict(sorted(frequencies.items(), key=lambda x: (-x[1], x[0])))
    tree = utils.generate_tree(sorted_frequencies)
    dc = (
        utils.generate_table(sorted_frequencies, tree)
        if sort
        else utils.generate_table(frequencies, tree)
    )

    dn = optimal_coding(text, dc, n, m)
    ac = approximate_coding(text, dc, n, m)

    print(
        pl.DataFrame(
            {"Input (I)": text, "Optimal coding (dn)": dn, "Aproximate coding (ac)": ac}
        )
    )


if __name__ == "__main__":
    typer.run(main)
