from utils.utils import sort_and_order_frequencies


def tree(frequencies: list[tuple[str, int]]):
    total = 0
    for i in frequencies:
        total += i[1]
    tree = []
    for i in range(len(frequencies)):
        tree.append(frequencies[i][1] / total)
    print(tree)


def main():
    text = "aaaabbbccccddeefgggggh"
    frequencies = sort_and_order_frequencies(text)
    tree(frequencies)


if __name__ == "__main__":
    main()
