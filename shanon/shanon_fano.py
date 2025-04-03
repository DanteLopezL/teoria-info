from utils.utils import sort_and_order_frequencies


def shanon_fano(text: str):
    frequencies = sort_and_order_frequencies(text)
    print(frequencies)


def main():
    text = "Jos sä tahdot niin tullen kalioden läpi"
    shanon_fano(text)


if __name__ == "__main__":
    main()
