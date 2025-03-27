import collections


def sort_and_order_frequencies(text: str) -> list[tuple[str, int]]:
    frequency = collections.Counter(text.replace(" ", "").replace("\n", "").lower())
    return sorted(frequency.items(), key=lambda x: (-x[1], -ord(x[0])))


def binary_expansion(num: float, tolerance: float = 1e-10) -> list[int]:
    expansion = []
    history = []

    while True:
        if num >= float(1):
            num = (num - 1) * 2
        else:
            num *= 2
        bit = 1 if num >= float(1) else 0
        expansion.append((num, bit))

        # Check for repeated numbers with a tolerance
        if any(abs(num - h) < tolerance for h in history):
            break
        else:
            history.append(num)
    sequence = [num for _, num in expansion]
    return sequence
