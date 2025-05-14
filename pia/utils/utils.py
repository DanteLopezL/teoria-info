def decode(code: str):
    pass


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
