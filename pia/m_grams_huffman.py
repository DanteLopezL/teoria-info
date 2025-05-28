from utils import utils
import polars as pl
import typer


def optimal_coding(text: str, dc: dict[str, str], n: int, m: int) -> str:
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
    heuristic: bool = False,
    optimal: bool = False,
    alpha: int = 0,
) -> None:
    with open(file, "r", encoding="utf-8") as f:
        text = "".join(f.read().split())

    n = len(text)

    max_m_range = utils.get_m_optimal_range(text)
    print(f"Using m range from 1 to {max_m_range}")

    for m in range(1, max_m_range):
        print(f"\n=== Processing for m = {m} ===")

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

        sorted_frequencies = dict(
            sorted(frequencies.items(), key=lambda x: (-x[1], x[0]))
        )

        dc, root = utils.huffman(sorted_frequencies)
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

            compression_ratio = utils.compression_ratio(len(text), len(ac))
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

        if optimal:
            oc = optimal_coding(text, dc, n, m)
            print(
                "===ENCODED===",
                pl.DataFrame({"Input (I)": text, "Optimal coding (oc)": oc}),
            )

            compression_ratio = utils.compression_ratio(len(text), len(oc))
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

        if root:
            utils.plot_tree(root, m)


if __name__ == "__main__":
    typer.run(main)
