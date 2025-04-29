def frequency_estimation(text: str, m: int, alpha: int = 0):
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


if __name__ == "__main__":
    text = "aaaaaaab"
    m = 3  # Maximum sequence length
    alpha = 1  # Weighting factor (α)

    frequencies = frequency_estimation(text, m, alpha)

    print("Sequence Frequencies (weighted by i^α):")
    for seq in sorted(frequencies.keys(), key=lambda x: (len(x), x)):
        print(f"'{seq}': {frequencies[seq]}")
