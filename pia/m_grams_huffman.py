import polars as pl


def frequency_estimation(text: str, m: int, alpha: int = 0) -> dict[str, int]:
    """
    Estimate the frequencies of all possible m-grams (sequences of length 1 to m) in input data I.

    Parameters:
        I (str or list): Input data (e.g., "aaaaaaab" or ['a','a','a','b']).
        m (int): Maximum sequence length to consider.
        alpha (float): Exponential scaling factor (α). If alpha=0, counts exact occurrences.

    Returns:
        dict: A dictionary where keys are sequences (str) and values are their weighted frequencies.
    """
    n = len(text)
    df = {}  # Dictionary to store frequencies

    for i in range(1, m + 1):  # i = 1, 2, ..., m
        for j in range(n - i + 1):  # Slide window over input
            s = text[j : j + i]  # Extract sequence of length i

            # Convert to string if I is a list (for consistency)
            if isinstance(s, list):
                s = "".join(s)

            # Update frequency in dictionary
            if s in df:
                df[s] += i**alpha
            else:
                df[s] = i**alpha

    return df


def main():
    text = "aaaaaaab"
    m = 3  # Maximum sequence length
    alpha = 1  # Weighting factor (α)

    frequencies = frequency_estimation(text, m, alpha)

    print("Sequence Frequencies (weighted by i^α):")

    keys = list(frequencies.keys())
    values = list(frequencies.values())

    print(pl.DataFrame({"keys": keys, "values": values}))


if __name__ == "__main__":
    main()
