from utils import utils
import polars as pl
import typer


def optimal_coding(text: str, dc: dict[str, str], n: int, m: int) -> str:
    """Generate optimal encoding for text using provided coding table.

    Args:
        text: Input text to encode
        dc: Dictionary mapping sequences to codes
        n: Length of input text
        m: Maximum sequence length to consider

    Returns:
        Optimally encoded string

    Note:
        Uses dynamic programming to find most efficient encoding
    """
    dn: dict[int, str] = {0: ""}
    for e in range(n):
        for i in range(e, min(m * e + 1, n)):
            k = i + 1
            l = min(i + m, n)

            for j in range(k, l + 1):
                s = text[i:j]

                if s not in dc:
                    continue

                c = dn[i] + dc[s]

                if j not in dn or len(dn[i]) > len(c):
                    dn[j] = c

    return dn.get(n, "")


def approximate_coding(text: str, dc: dict[str, str], n: int, m: int) -> str:
    c = ""
    i = 0
    while i < n:
        r = 0  # best ratio found value
        l = 0  # end of best rato sequence
        for k in range(1, m + 1):
            j = i + k
            if j > n:
                j = n
            s = text[i:j]
            codeword = dc[s]
            t = len(s) / len(codeword)
            if t > r:
                r = t
                l = j
        c = c + dc[text[i:l]]
        i = l
    return c


def main(
    file: str,
    m: int = 1,
    alpha: int = 0,
    heuristic: bool = False,
    optimal: bool = False,
) -> None:
    with open(file, "r", encoding="utf-8") as f:
        text = "".join(f.read().split())

    n = len(text)
    frequencies = utils.frequency_estimation(text, n, m, alpha)
    keys = list(frequencies.keys())
    values = list(frequencies.values())

    print("Sequence Frequencies (weighted by i^α):")
    print(
        "===FREQUENCIES===",
        pl.DataFrame(
            {
                "Sequence": keys,
                "Frequency": values,
            }
        ),
    )
    sorted_frequencies = dict(sorted(frequencies.items(), key=lambda x: (-x[1], x[0])))

    dc = utils.huffman(sorted_frequencies)

    dc = dict(sorted(dc.items()))

    print(
        "===CODEWORDS===",
        pl.DataFrame({"Sequence": dc.keys(), "Codeword": dc.values()}),
    )

    if heuristic:
        ac = approximate_coding(text, dc, n, m)
        print(
            "===ENCODED===",
            pl.DataFrame({"Input (I)": text, "Approximate coding (ac)": ac}),
        )

        text_size = len(text)
        compression_ratio = utils.compression_ratio(text_size, len(ac))
        entropy = utils.calculate_entropy(values, m)

        print(
            "===ADDITIONAL DATA===",
            pl.DataFrame(
                {
                    "m": m,
                    "a": alpha,
                    "Compression ratio": compression_ratio,
                    "Entropy": entropy,
                }
            ),
        )
    elif optimal:
        oc = optimal_coding(text, dc, n, m)
        print(
            "===ENCODED===",
            pl.DataFrame({"Input (I)": text, "Optimal coding (oc)": oc}),
        )

        text_size = len(text)
        compression_ratio = utils.compression_ratio(text_size, len(oc))
        entropy = utils.calculate_entropy(values, m)

        print(
            "===ADDITIONAL DATA===",
            pl.DataFrame(
                {
                    "m": m,
                    "a": alpha,
                    "Compression ratio": compression_ratio,
                    "Entropy": entropy,
                }
            ),
        )


if __name__ == "__main__":
    typer.run(main)
