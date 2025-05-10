from utils import utils
import polars as pl
import typer


def frequency_estimation(text: str, n: int, m: int, alpha: int = 0) -> dict[str, int]:
    """Estimate weighted frequencies of all character sequences in a text.

    This function calculates the weighted frequencies of all possible character sequences
    of lengths 1 to m in the input text. The weighting is applied according to the
    sequence length raised to the power of alpha (i^α).

    Args:
        text: Input string to analyze.
        m: Maximum sequence length to consider (inclusive).
        alpha: Weighting exponent (default: 0). When alpha=0, all sequences are
               counted equally regardless of length. Higher alpha values give more
               weight to longer sequences.

    Returns:
        Dictionary where keys are character sequences and values are their weighted
        frequencies. The weighting is calculated as count * (length^alpha).

    Examples:
        >>> frequency_estimation("abc", 2, 0)
        {'a': 1, 'b': 1, 'c': 1, 'ab': 1, 'bc': 1}

        >>> frequency_estimation("aab", 2, 1)
        {'a': 2, 'a': 2, 'b': 1, 'aa': 2, 'ab': 2}
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


def main(file: str, m: int = 3, alpha: int = 1, sort: bool = False) -> None:
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
    print(dc)
    dn = optimal_coding(text, dc, n, m)
    print("===DN===", dn)


if __name__ == "__main__":
    typer.run(main)
