import collections


def sort_and_order_frequencies(text: str) -> list[tuple[str, int]]:
    frequency = collections.Counter(text.replace(" ", "").replace("\n", "").lower())
    return sorted(frequency.items(), key=lambda x: (-x[1], (x[0])))


def binary_expansion(num: float, lk: int) -> list[int]:
    r = num
    expansion = []
    history = []

    while True:
        if r >= 1:
            r = (r - 1) * 2
        else:
            r *= 2

        bit = 1 if r >= 1 else 0
        expansion.append(bit)

        if r in history:
            break
        else:
            history.append(r)

    return expansion[:lk] if lk <= len(expansion) else [0] * lk
