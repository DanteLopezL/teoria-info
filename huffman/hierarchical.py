from utils.utils import sort_and_order_frequencies


def print_table():
    pass


def generate_table(
    frequencies: list[tuple[str, int]], tree: dict[str, tuple[str, str]]
):
    print(frequencies)
    print(tree)


def tree(frequencies: list[tuple[str, int]]) -> dict[str, tuple[str, str]]:
    total = sum([i[1] for i in frequencies])
    encoding: list[tuple[str, float]] = []
    tree = {}

    for char, count in frequencies:
        encoding.append((char, count / total))

    for i in range(len(encoding) - 2):
        last = encoding[-1]
        penultimate = encoding[-2]
        del encoding[-2:]
        new = (f"o{i + 1}", last[1] + penultimate[1])
        encoding.append(new)
        encoding = sorted(encoding, key=lambda x: (-x[1], x[0]))
        tree[new[0]] = (penultimate[0], last[0])

    tree["origin"] = (encoding[-2][0], encoding[-1][0])
    return dict(reversed(tree.items()))


def main():
    text = "aaaabbbccccddeefgggggh"
    frequencies = sort_and_order_frequencies(text)
    huffman_tree = tree(frequencies)
    generate_table(frequencies, huffman_tree)


if __name__ == "__main__":
    main()
