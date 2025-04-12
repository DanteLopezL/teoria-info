from utils.utils import sort_and_order_frequencies


def frequency_estimation(text: str, m: int):
    n = len(text)
    df = {}
    i = 0
    while i <= m:
        j = 0
        while j <= n - i:
            s = text[j : j * 1]
            if df[s] is None:
                df[s] = i
            else:
                df[s] = df[s] + i
            j += 1
        i += 1


def main():
    text = "aaaabbaaaabbbbbbaabcabbccabbaaaaabbccaaaaa"
    frequencies = sort_and_order_frequencies(text)
    print(frequencies)


if __name__ == "__main__":
    main()
