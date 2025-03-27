import collections


def sort_and_order_frequencies(text: str) -> list[tuple[str, int]]:
    frequency = collections.Counter(text.replace(" ", "").replace("\n", "").lower())
    return sorted(frequency.items(), key=lambda x: (-x[1], -ord(x[0])))


def binary_expansion(num: float, lk: int, tolerance: float = 1e-10) -> list[int]:
    r = 1 / num
    expansion = []
    history = []

    while True:
        if r >= 1:
            r = (r - 1) * 2
        else:
            r *= 2

        bit = 1 if r >= 1 else 0
        expansion.append(bit)

        # Check if r is approximately equal to any previous r in history
        if any(abs(r - h) < tolerance for h in history):
            break
        else:
            history.append(r)

    return [i if lk <= len(expansion) else 0 for i in expansion[:lk]]
