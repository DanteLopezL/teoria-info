from math import log2
import polars as pl


def calculate_fi(frequencies: dict[str, int]) -> tuple[int, list[float]]:
    total = sum([i for i in frequencies.values()])
    fi = [i / total for i in frequencies.values()]

    return total, fi


def generate_codes(
    tree: dict[str, tuple[str, str]],
    node: str = "origin",
    code: str = "",
    codes=None,
) -> dict[str, str]:
    """Generate Huffman codes recursively from the tree.

    Args:
        tree: The Huffman tree dictionary
        node: Current node in traversal
        code: Current code accumulated during traversal
        codes: Dictionary to store character codes

    Returns:
        Dictionary mapping characters to their Huffman codes
    """

    # If node not in tree, it's a leaf node (character)
    if codes is None:
        codes = {}
    if node not in tree:
        codes[node] = code
        return codes

    left, right = tree[node]

    # Recurse left (0) and right (1)
    generate_codes(tree, left, code + "0", codes)
    generate_codes(tree, right, code + "1", codes)

    return codes


def print_table(frequencies: dict[str, int], codes: dict[str, str]) -> None:
    """Print a formatted table with character frequencies and codes using Polars.

    Args:
        frequencies: List of (character, frequency) tuples
        codes: Dictionary mapping characters to their Huffman codes
    """

    chars = [char for char in frequencies.keys()]

    total, fi = calculate_fi(frequencies)

    freq_list = [freq for freq in frequencies.values()]
    code_list = [codes.get(char, "N/A") for char in chars]
    needed_chars = [len(codes.get(char, "")) for char in chars]

    # Calculate entropy for each character (-fi * log2(fi))
    hi_list = [-fi[i] * log2(fi[i]) for i in range(len(frequencies))]
    h = sum(hi_list)

    lms = sum(f * nc for f, nc in zip(fi, needed_chars))

    char_df = pl.DataFrame(
        {
            "CHAR": chars,
            "FREQ": freq_list,
            "Fi": fi,
            "CODE": code_list,
            "NEEDED_CHARS": needed_chars,
            "Hi": hi_list,
        }
    )

    summary_df = pl.DataFrame(
        {
            "METRIC": ["LMS", "LME", "RC", "H"],
            "VALUE": [lms, 8, 8 / lms, h],
        }
    )

    print("\n=== HUFFMAN CODE TABLE ===")
    print(char_df)

    print("\n=== COMPRESSION METRICS ===")
    print(summary_df)


def calculate_compression(
    original_text: str, codes: dict[str, str]
) -> tuple[int, int, float]:
    """Calculate compression statistics.

    Args:
        original_text: The input text
        codes: Dictionary mapping characters to their Huffman codes

    Returns:
        Tuple of (original bits, compressed bits, compression ratio)
    """

    original_bits = len(original_text) * 8

    compressed_bits = sum(len(codes[char]) for char in original_text)

    ratio = compressed_bits / original_bits

    return original_bits, compressed_bits, ratio


def generate_table(
    frequencies: dict[str, int], tree: dict[str, tuple[str, str]]
) -> dict[str, str]:
    """Generate and display Huffman coding table and statistics.

    Args:
        frequencies: List of (character, frequency) tuples
        tree: The Huffman tree dictionary

    Returns:
        Dictionary mapping characters to their Huffman codes
    """

    codes = generate_codes(tree)

    print_table(frequencies, codes)

    return codes


def generate_tree(frequencies: dict[str, int]) -> dict[str, tuple[str, str]]:
    """Build a Huffman tree from character frequencies.

    Args:
        frequencies: List of (character, frequency) tuples

    Returns:
        Dictionary representing the Huffman tree
    """
    total = sum([i for i in frequencies.values()])
    encoding: list[tuple[str, float]] = []
    tree = {}

    # Convert frequencies to probabilities
    for char, count in frequencies.items():
        encoding.append((char, count / total))

    # Build the tree bottom-up
    for i in range(len(encoding) - 2):
        last = encoding[-1]
        penultimate = encoding[-2]
        del encoding[-2:]
        new = (f"o{i + 1}", last[1] + penultimate[1])
        encoding.append(new)
        encoding = sorted(encoding, key=lambda x: (-x[1], x[0]))
        tree[new[0]] = (penultimate[0], last[0])

    # Add the root node
    tree["origin"] = (encoding[-2][0], encoding[-1][0])

    # Return reversed tree (from root to leaves)
    return dict(reversed(tree.items()))
