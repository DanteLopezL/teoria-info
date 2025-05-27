from math import log2
from typing import Optional
import heapq
import matplotlib.pyplot as plt


class Node:
    def __init__(self, symbol: str | None, frequency: int):
        self.symbol: str | None = symbol
        self.frequency: int = frequency
        self.left: Node | None = None
        self.right: Node | None = None

    def __lt__(self, other: "Node") -> bool:
        return self.frequency < other.frequency


def huffman(frequencies: dict[str, int]) -> tuple[dict[str, str], Node | None]:
    if not frequencies:
        return {}, None

    forest = [Node(symbol, freq) for symbol, freq in frequencies.items()]
    heapq.heapify(forest)

    if len(forest) == 1:
        node = forest[0]
        return {node.symbol: "0"} if node.symbol is not None else {}, node

    while len(forest) > 1:
        left = heapq.heappop(forest)
        right = heapq.heappop(forest)
        new_node = Node(None, left.frequency + right.frequency)
        new_node.left = left
        new_node.right = right
        heapq.heappush(forest, new_node)

    tree_root = forest[0]
    codes: dict[str, str] = {}

    def assign_codes(node: Optional[Node], code: str = "") -> None:
        if node:
            if node.symbol is not None:
                codes[node.symbol] = code
            assign_codes(node.left, code + "0")
            assign_codes(node.right, code + "1")

    assign_codes(tree_root)
    return codes, tree_root


def plot_tree(root: Node):
    _, ax = plt.subplots()
    ax.axis("off")

    def _plot_node(node: Node, x: float, y: float, dx: float, dy: float):
        label = (
            f"{node.symbol}:{node.frequency}" if node.symbol else f"{node.frequency}"
        )
        ax.text(
            x, y, label, ha="center", va="center", bbox=dict(boxstyle="round", fc="w")
        )

        if node.left:
            ax.plot([x, x - dx], [y, y - dy], "k-")
            ax.text(x - dx / 2, y - dy / 2, "0", ha="center", va="center")
            _plot_node(node.left, x - dx, y - dy, dx * 0.6, dy)

        if node.right:
            ax.plot([x, x + dx], [y, y - dy], "k-")
            ax.text(x + dx / 2, y - dy / 2, "1", ha="center", va="center")
            _plot_node(node.right, x + dx, y - dy, dx * 0.6, dy)

    _plot_node(root, x=0, y=0, dx=1.0, dy=1.0)
    plt.tight_layout()
    plt.show()


def decode(encoded_data: str, codes: dict[str, str]) -> str:
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


def validate_m(options: list[int], n:int):
    for i in options:
        if i > n:
            print(f"{i} cant be greater than {n} (n), removing")
            options.remove(i)