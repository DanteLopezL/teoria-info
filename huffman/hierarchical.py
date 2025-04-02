from math import log2
from utils.utils import sort_and_order_frequencies
import polars as pl


def calculate_fi(frequencies: list[tuple[str, int]]) -> tuple[int, list[float]]:
    total = sum([freq for _, freq in frequencies])
    fi = [freq / total for _, freq in frequencies]

    return total, fi


def generate_codes(
    tree: dict[str, tuple[str, str]],
    node: str = "origin",
    code: str = "",
    codes: dict = {},
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
    if codes is None:
        codes = {}

    # If node not in tree, it's a leaf node (character)
    if node not in tree:
        codes[node] = code
        return codes

    left, right = tree[node]

    # Recurse left (0) and right (1)
    generate_codes(tree, left, code + "0", codes)
    generate_codes(tree, right, code + "1", codes)

    return codes


def print_table(frequencies: list[tuple[str, int]], codes: dict[str, str]) -> None:
    """Print a formatted table with character frequencies and codes.

    Args:
        frequencies: List of (character, frequency) tuples
        codes: Dictionary mapping characters to their Huffman codes
    """

    total, fi = calculate_fi(frequencies)
    needed_chars = [len(codes[char]) for char in codes]
    lms = sum(
        x * y
        for x, y in zip(
            fi,
            needed_chars,
        )
    )
    print(
        pl.DataFrame(
            {
                "CHAR": [char for char, _ in frequencies],
                "FREQ": [freq for _, freq in frequencies],
                "Fi": fi,
                "CODE": [codes[char] for char in codes],
                "NEEDED CHARS": needed_chars,
                "Hi": [-fi[i] * log2(fi[i]) for i in range(len(frequencies))],
            }
        ),
        pl.DataFrame(
            {
                "LMS": lms,
                "LME": 8,
                "RC": lms / 8,
            }
        ),
    )


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
    # Original size in bits (assuming 8 bits per character)
    original_bits = len(original_text) * 8

    # Compressed size in bits
    compressed_bits = sum(len(codes[char]) for char in original_text)

    # Compression ratio
    ratio = compressed_bits / original_bits

    return original_bits, compressed_bits, ratio


def encode_text(text: str, codes: dict[str, str]) -> str:
    """Encode the input text using Huffman codes.

    Args:
        text: The input text
        codes: Dictionary mapping characters to their Huffman codes

    Returns:
        Encoded binary string
    """
    return "".join(codes[char] for char in text)


def decode_text(encoded_text: str, tree: dict[str, tuple[str, str]]) -> str:
    """Decode a Huffman-encoded text.

    Args:
        encoded_text: Binary string of Huffman-encoded text
        tree: The Huffman tree dictionary

    Returns:
        Decoded original text
    """
    # Build reversed lookup tree for decoding
    current_node = "origin"
    decoded_text = ""

    for bit in encoded_text:
        # Move left or right in the tree
        left, right = tree[current_node]
        current_node = left if bit == "0" else right

        # If we reached a leaf node (character)
        if current_node not in tree:
            decoded_text += current_node
            current_node = "origin"  # Reset to root

    return decoded_text


def generate_table(
    frequencies: list[tuple[str, int]], tree: dict[str, tuple[str, str]]
) -> dict[str, str]:
    """Generate and display Huffman coding table and statistics.

    Args:
        frequencies: List of (character, frequency) tuples
        tree: The Huffman tree dictionary

    Returns:
        Dictionary mapping characters to their Huffman codes
    """
    # Generate codes from the tree
    codes = generate_codes(tree)

    # Print the frequency table with codes
    print_table(frequencies, codes)

    # Print tree structure
    print("\nTree structure:")
    for node, (left, right) in tree.items():
        print(f"{node} -> ({left}, {right})")

    return codes


def tree(frequencies: list[tuple[str, int]]) -> dict[str, tuple[str, str]]:
    """Build a Huffman tree from character frequencies.

    Args:
        frequencies: List of (character, frequency) tuples

    Returns:
        Dictionary representing the Huffman tree
    """
    total = sum([i[1] for i in frequencies])
    encoding: list[tuple[str, float]] = []
    tree = {}

    # Convert frequencies to probabilities
    for char, count in frequencies:
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


def main():
    # Example text
    text = "aaaabbbccccddeefgggggh"

    # Get character frequencies
    frequencies = sort_and_order_frequencies(text)

    # Build Huffman tree
    huffman_tree = tree(frequencies)

    # Generate and display codes
    codes = generate_table(frequencies, huffman_tree)

    # Encode the text
    # encoded_text = encode_text(text, codes)
    # print(f"\nEncoded text: {encoded_text}")

    # Decode to verify
    # decoded_text = decode_text(encoded_text, huffman_tree)
    # print(f"Decoded text: {decoded_text}")

    # Calculate compression
    original_bits, compressed_bits, ratio = calculate_compression(text, codes)
    # print(f"\nOriginal size: {original_bits} bits")
    # print(f"Compressed size: {compressed_bits} bits")
    # print(f"Compression ratio: {ratio:.2%}")
    # print(f"Space saving: {1 - ratio:.2%}")


if __name__ == "__main__":
    main()
