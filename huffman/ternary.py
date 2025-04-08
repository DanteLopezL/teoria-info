from math import log2
from utils.utils import sort_and_order_frequencies
import polars as pl


def calculate_fi(frequencies: list[tuple[str, int]]) -> tuple[int, list[float]]:
    total = sum([freq for _, freq in frequencies])
    fi = [freq / total for _, freq in frequencies]

    return total, fi


def generate_codes(
    tree: dict[str, tuple[str, str, str]],
    node: str = "origin",
    code: str = "",
    codes: dict[str, str] = {},
) -> dict[str, str]:
    """Generate ternary Huffman codes recursively from the tree.

    Args:
        tree: The ternary Huffman tree dictionary
        node: Current node in traversal
        code: Current code accumulated during traversal
        codes: Dictionary to store character codes

    Returns:
        Dictionary mapping characters to their ternary Huffman codes
    """
    if codes is None:
        codes = {}

    # If node not in tree, it's a leaf node (character)
    if node not in tree:
        codes[node] = code
        return codes

    children = tree[node]
    
    # Handle both 2-child and 3-child nodes
    if len(children) == 3:
        left, middle, right = children
        # Recurse left (0), middle (1), and right (2)
        generate_codes(tree, left, code + "0", codes)
        generate_codes(tree, middle, code + "1", codes)
        generate_codes(tree, right, code + "2", codes)
    elif len(children) == 2:
        left, right = children
        # Recurse left (0) and right (1)
        generate_codes(tree, left, code + "0", codes)
        generate_codes(tree, right, code + "1", codes)

    return codes


def print_table(frequencies: list[tuple[str, int]], codes: dict[str, str]) -> None:
    """Print a formatted table with character frequencies and codes using Polars.

    Args:
        frequencies: List of (character, frequency) tuples
        codes: Dictionary mapping characters to their Huffman codes
    """

    chars = [char for char, _ in frequencies]

    total, fi = calculate_fi(frequencies)

    freq_list = [freq for _, freq in frequencies]
    code_list = [codes.get(char, "N/A") for char in chars]
    needed_chars = [len(codes.get(char, "")) for char in chars]

    # For ternary, we use log base 3 to calculate information content properly
    # H = -sum(p_i * log_3(p_i))
    hi_list = [-fi[i] * (log2(fi[i]) / log2(3)) for i in range(len(frequencies))]
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

    print("\n=== TERNARY HUFFMAN CODE TABLE ===")
    print(char_df)

    print("\n=== COMPRESSION METRICS ===")
    print(summary_df)


def calculate_compression(
    original_text: str, codes: dict[str, str]
) -> tuple[int, int, float]:
    """Calculate compression statistics.

    Args:
        original_text: The input text
        codes: Dictionary mapping characters to their ternary Huffman codes

    Returns:
        Tuple of (original bits, compressed bits, compression ratio)
    """
    # For ternary coding, we need log2(3) ≈ 1.585 bits per ternary digit
    bits_per_ternary_digit = log2(3)
    
    original_bits = len(original_text) * 8

    # For ternary codes, we multiply by log2(3) to get the actual bit equivalent
    compressed_bits = sum(len(codes[char]) * bits_per_ternary_digit for char in original_text)

    ratio = compressed_bits / original_bits

    return original_bits, compressed_bits, ratio


def encode_text(text: str, codes: dict[str, str]) -> str:
    """Encode the input text using ternary Huffman codes.

    Args:
        text: The input text
        codes: Dictionary mapping characters to their Huffman codes

    Returns:
        Encoded ternary string
    """
    return "".join(codes[char] for char in text)


def decode_text(encoded_text: str, tree: dict) -> str:
    """Decode a ternary Huffman-encoded text.

    Args:
        encoded_text: Ternary string of Huffman-encoded text
        tree: The ternary Huffman tree dictionary

    Returns:
        Decoded original text
    """
    current_node = "origin"
    decoded_text = ""

    for digit in encoded_text:
        # Move according to the ternary digit (0, 1, or 2)
        children = tree[current_node]
        
        if len(children) == 3:
            left, middle, right = children
            if digit == "0":
                current_node = left
            elif digit == "1":
                current_node = middle
            else:  # digit == "2"
                current_node = right
        else:  # Binary node
            left, right = children
            if digit == "0":
                current_node = left
            else:  # digit == "1" or "2"
                current_node = right

        # If we reached a leaf node (character)
        if current_node not in tree:
            decoded_text += current_node
            current_node = "origin"  # Reset to root

    return decoded_text


def generate_table(
    frequencies: list[tuple[str, int]], tree: dict
) -> dict[str, str]:
    """Generate and display ternary Huffman coding table and statistics.

    Args:
        frequencies: List of (character, frequency) tuples
        tree: The ternary Huffman tree dictionary

    Returns:
        Dictionary mapping characters to their Huffman codes
    """
    codes = generate_codes(tree)

    print_table(frequencies, codes)

    # Print tree structure
    print("\nTree structure:")
    for node, children in tree.items():
        print(f"{node} -> {children}")

    return codes


def tree(frequencies: list[tuple[str, int]]) -> dict:
    """Build a ternary Huffman tree from character frequencies.

    Args:
        frequencies: List of (character, frequency) tuples

    Returns:
        Dictionary representing the ternary Huffman tree
    """
    total = sum([i[1] for i in frequencies])
    encoding: list[tuple[str, float]] = []
    tree = {}

    # Convert frequencies to probabilities
    for char, count in frequencies:
        encoding.append((char, count / total))

    # Sort by frequency, then by character (lowest frequency first)
    encoding = sorted(encoding, key=lambda x: (x[1], x[0]))
    
    # If there are fewer than 3 nodes total, handle specially
    if len(encoding) <= 3:
        if len(encoding) == 1:
            # Single symbol case
            tree["origin"] = (encoding[0][0],)
        elif len(encoding) == 2:
            # Two symbols case - use binary node
            tree["origin"] = (encoding[0][0], encoding[1][0])
        else:  # len(encoding) == 3
            # Three symbols case
            tree["origin"] = (encoding[0][0], encoding[1][0], encoding[2][0])
        return tree
    
    # Build the tree bottom-up
    i = 0
    while len(encoding) > 3:
        # Take the three lowest frequency nodes
        lowest_three = encoding[:3]
        del encoding[:3]
        
        # Create a new internal node
        new_node = (f"o{i}", sum(freq for _, freq in lowest_three))
        
        # Add to tree
        tree[f"o{i}"] = (lowest_three[0][0], lowest_three[1][0], lowest_three[2][0])
        
        # Add new node back to encoding list
        encoding.append(new_node)
        
        # Sort again by frequency
        encoding = sorted(encoding, key=lambda x: (x[1], x[0]))
        
        i += 1
    
    # Final nodes (1, 2, or 3 remaining)
    if len(encoding) == 1:
        tree["origin"] = (encoding[0][0],)
    elif len(encoding) == 2:
        tree["origin"] = (encoding[0][0], encoding[1][0])
    else:  # len(encoding) == 3
        tree["origin"] = (encoding[0][0], encoding[1][0], encoding[2][0])
    
    return tree


def main():
    text = "aaaabbbccccddeefgggggh"

    frequencies = sort_and_order_frequencies(text)

    ternary_huffman_tree = tree(frequencies)

    codes = generate_table(frequencies, ternary_huffman_tree)

    # Encode the text
    encoded_text = encode_text(text, codes)
    print(f"\nEncoded text: {encoded_text}")

    # Decode to verify
    decoded_text = decode_text(encoded_text, ternary_huffman_tree)
    print(f"Decoded text: {decoded_text}")

    # Calculate compression
    original_bits, compressed_bits, ratio = calculate_compression(text, codes)
    print(f"\nOriginal size: {original_bits} bits")
    print(f"Compressed size: {compressed_bits:.2f} bits (equivalent)")
    print(f"Compression ratio: {ratio:.2%}")
    print(f"Space saving: {1 - ratio:.2%}")


if __name__ == "__main__":
    main()