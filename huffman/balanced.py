from utils.utils import sort_and_order_frequencies


def main():
    text = "aaaabbbccccddeefgggggh"
    frequencies = sort_and_order_frequencies(text)
    print(frequencies)


if __name__ == "__main__":
    main()
