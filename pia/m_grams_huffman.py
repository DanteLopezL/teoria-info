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
    m: int = 3,
    alpha: int = 1,
    sort: bool = False,
    heuristic: bool = False,
    optimal: bool = False,
) -> None:
    """Main function to analyze text and generate optimal encoding.

    Args:
        file: Path to input text file
        m: Maximum sequence length (default: 3)
        alpha: Weighting exponent (default: 1)
        sort: Sort frequencies before coding (default: False)

    Workflow:
        1. Reads and preprocesses input file
        2. Calculates sequence frequencies
        3. Generates coding table
        4. Produces optimal encoding
        5. Displays results
    """
    with open(file, "r", encoding="utf-8") as f:
        text = "".join(f.read().split())

    n = len(text)
    frequencies = utils.frequency_estimation(text, n, m)
    weighted_frequencies = utils.frequency_estimation(text, n, m, alpha)
    keys = list(frequencies.keys())
    values = list(frequencies.values())
    weighted_values = list(weighted_frequencies.values())

    print("Sequence Frequencies (weighted by i^α):")
    print(
        pl.DataFrame(
            {
                "Sequence": keys,
                "Frequency": values,
                f"Weighted (a={alpha})": weighted_values,
            }
        )
    )
    sorted_frequencies = dict(
        sorted(weighted_frequencies.items(), key=lambda x: (-x[1], x[0]))
    )

    dc = utils.huffman(sorted_frequencies)

    if not heuristic and not optimal:
        oc = optimal_coding(text, dc, n, m)
        ac = approximate_coding(text, dc, n, m)

        print(
            pl.DataFrame(
                {
                    "Input (I)": text,
                    "Optimal coding (dn)": oc,
                    "Aproximate coding (ac)": ac,
                }
            )
        )
        text_size = len(text)
        optimal_cr = utils.compression_ratio(text_size, len(oc))
        optimal_cr = utils.compression_ratio(text_size, len(ac))

        print(
            pl.DataFrame(
                {
                    "m": m,
                    "a": alpha,
                    "Optimal compression": optimal_cr,
                    "Approximate compression": optimal_cr,
                }
            )
        )

    elif heuristic:
        ac = approximate_coding(text, dc, n, m)
        print(pl.DataFrame({"Input (I)": text, "Approximate coding (ac)": ac}))

        text_size = len(text)
        optimal_cr = utils.compression_ratio(text_size, len(ac))

        print(
            pl.DataFrame(
                {
                    "m": m,
                    "a": alpha,
                    "Approximate compression": optimal_cr,
                }
            )
        )
    else:
        oc = optimal_coding(text, dc, n, m)
        print(pl.DataFrame({"Input (I)": text, "Optimal coding (c)": oc}))
        text_size = len(text)
        optimal_cr = utils.compression_ratio(text_size, len(oc))
        print(
            pl.DataFrame(
                {
                    "m": m,
                    "a": alpha,
                    "Approximate compression": optimal_cr,
                }
            )
        )


if __name__ == "__main__":
    typer.run(main)
