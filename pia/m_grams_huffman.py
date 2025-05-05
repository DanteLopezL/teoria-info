import polars as pl
import typer


def frequency_estimation(text: str, m: int, alpha: int = 0) -> dict[str, int]:
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
    n = len(text)
    df = {}  # Dictionary to store frequencies

    for i in range(1, m + 1):  # i = 1, 2, ..., m
        for j in range(n - i + 1):  # Slide window over input
            s = text[j : j + i]  # Extract sequence of length i

            # Convert to string if s is a list (for consistency)
            if isinstance(s, list):
                s = "".join(s)

            # Update frequency in dictionary with length-based weighting
            if s in df:
                df[s] += i**alpha
            else:
                df[s] = i**alpha

    return df


def main(m: int = 3, alpha: int = 1) -> None:
    text = "aaaaaaab"

    # Calculate weighted frequencies
    frequencies = frequency_estimation(text, m)
    weighted_frequencies = frequency_estimation(text, m, alpha)

    print("Sequence Frequencies (weighted by i^α):")

    # Convert results to a Polars DataFrame for nice display
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


if __name__ == "__main__":
    typer.run(main)
