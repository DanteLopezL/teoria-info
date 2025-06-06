from math import log2
from typing import Optional
import heapq
import matplotlib.pyplot as plt


class Node:
    def __init__(self, symbol: str | None, frequency: int):
        self.sequence: str | None = symbol
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
        return {node.sequence: "0"} if node.sequence is not None else {}, node

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
            if node.sequence is not None:
                codes[node.sequence] = code
            assign_codes(node.left, code + "0")
            assign_codes(node.right, code + "1")

    assign_codes(tree_root)
    return codes, tree_root


def plot_tree(root: Node, m: int):
    _, ax = plt.subplots()
    ax.axis("off")
    ax.set_title(f"m = {m}")

    def _plot_node(node: Node, x: float, y: float, dx: float, dy: float):
        label = (
            f"{node.sequence}:{node.frequency}"
            if node.sequence
            else f"{node.frequency}"
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

        current.sequence = symbol

    result: list[str] = []
    current = root

    for bit in encoded_data:
        if bit == "0":
            current = current.left
        else:
            current = current.right

        if current is None:
            return ""

        if current.sequence is not None:
            result.append(current.sequence)
            current = root

    return "".join(result)


def frequency_estimation(text: str, n: int, m: int, alpha: int = 0) -> dict[str, int]:
    df: dict[str, int] = {}

    for i in range(1, m + 1):
        for j in range(n - i + 1):
            s = text[j : j + i]
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


def get_m_optimal_range(text: str) -> int:
    n = len(text)
    for m in range(n - 1, 0, -1):
        for i in range(0, n - m + 1):
            candidate = text[i : i + m]
            if text.find(candidate, i + 1) != -1:
                return m
    return 1
