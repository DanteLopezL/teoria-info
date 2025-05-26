from math import log2
from typing import Optional
import heapq


class Node:
    """Node for Huffman tree construction"""

    def __init__(self, symbol: str | None, frequency: int):
        self.symbol: str | None = symbol
        self.frequency: int = frequency
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None

    def __lt__(self, other: "Node") -> bool:
        return self.frequency < other.frequency


def huffman(frequencies: dict[str, int]) -> dict[str, str]:
    """
    Implement Huffman coding as described in the document.

    Args:
        frequencies: Dictionary mapping symbols to their frequencies

    Returns:
        Dictionary mapping symbols to their Huffman codes
    """
    if not frequencies:
        return {}

    # Step 1: Create initial forest of nodes
    forest: list[Node] = [Node(symbol, freq) for symbol, freq in frequencies.items()]

    # Step 2: Build Huffman tree by iteratively combining trees with lowest frequencies

    heapq.heapify(forest)  # Convert forest to a min heap

    # Special case: only one symbol
    if len(forest) == 1:
        node = forest[0]
        return {node.symbol: "0"} if node.symbol is not None else {}

    # Iterate until only one tree remains
    while len(forest) > 1:
        # Find two trees with lowest frequencies
        left = heapq.heappop(forest)
        right = heapq.heappop(forest)

        # Create a new internal node with these two nodes as children
        new_node = Node(None, left.frequency + right.frequency)
        new_node.left = left
        new_node.right = right

        # Add the new tree back to the forest
        heapq.heappush(forest, new_node)

    # The remaining tree is the Huffman code tree
    tree_root = forest[0]

    # Step 3: Generate codewords by traversing the tree from root to each leaf
    # where '0' describes the left and '1' the right subtree
    codes: dict[str, str] = {}

    def assign_codes(node: Optional[Node], code: str = "") -> None:
        if node:
            if node.symbol is not None:  # Leaf node
                codes[node.symbol] = code
            # Traverse left with '0'
            assign_codes(node.left, code + "0")
            # Traverse right with '1'
            assign_codes(node.right, code + "1")

    assign_codes(tree_root)
    return codes


def decode(encoded_data: str, codes: dict[str, str]) -> str:
    """
    Decode Huffman-encoded data using the provided codes.

    Args:
        encoded_data: The binary string of encoded data
        codes: Dictionary mapping symbols to their Huffman codes

    Returns:
        Decoded string
    """
    if not encoded_data or not codes:
        return ""

    root = Node(None, 0)

    for symbol, code in codes.items():
        current = root

        for bit in code:
            if bit == "0":
                if current.left is None:
                    current.left = Node(None, 0)
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(None, 0)
                current = current.right

        current.symbol = symbol

    result: list[str] = []
    current = root

    for bit in encoded_data:
        if bit == "0":
            current = current.left
        else:
            current = current.right

        if current is None:
            return ""

        if current.symbol is not None:
            result.append(current.symbol)
            current = root

    return "".join(result)


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


def compression_ratio(text_size: int, encoded_size: int) -> float:
    return encoded_size / text_size


def calculate_entropy(frequencies: list[int], m: int) -> float:
    total = sum([freq for freq in frequencies])
    pi = [freq / total for freq in frequencies]
    return -sum([pi[i] * log2(pi[i]) for i in range(len(frequencies))]) / m
