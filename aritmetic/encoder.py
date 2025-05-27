import numpy as np
import collections


def sort_and_order_frequencies(text: str) -> list[tuple[str, int]]:
    frequency = collections.Counter(text.replace(" ", "").replace("\n", "").lower())
    return sorted(frequency.items(), key=lambda x: (-x[1], x[0]))


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


def arithmetic_encoder(text: str, word: str) -> tuple:
    frequencies = sort_and_order_frequencies(text)
    frequency_sum = sum(freq for _, freq in frequencies)

    sorted_values = sorted(frequencies, key=lambda x: (not x[0].isalpha(), x[0]))
    sorted_frequencies = [
        (sym, freq, freq / frequency_sum) for sym, freq in sorted_values
    ]

    base_matrix = np.zeros((3, len(sorted_frequencies)))
    for i in range(len(sorted_frequencies)):
        base_matrix[0, i] = sorted_frequencies[i][2]
        base_matrix[1, i] = base_matrix[2, i - 1] if i != 0 else 0
        base_matrix[2, i] = base_matrix[0, i] + base_matrix[1, i]

    # Build new_matrix: iteratively refine the interval using the symbols of the word.
    new_matrix = np.zeros((3, len(sorted_frequencies)))
    iteration = 0
    char_index = 0
    for char in word:
        # Find the index of the current character in our sorted list.
        for i in range(len(sorted_frequencies)):
            if char == sorted_frequencies[i][0]:
                char_index = i
                break
        # Update the new_matrix according to the iteration
        for i in range(len(sorted_frequencies)):
            if iteration == 0:
                new_matrix[0, i] = base_matrix[0, i] * base_matrix[0, char_index]
                new_matrix[1, i] = (
                    new_matrix[2, i - 1] if i != 0 else base_matrix[1, char_index]
                )
                new_matrix[2, i] = new_matrix[0, i] + new_matrix[1, i]
            else:
                new_matrix[0, i] = base_matrix[0, i] * new_matrix[0, char_index]
        if iteration == len(word) - 1:
            break
        else:
            iteration += 1
        print(f"'{char}' sum {sum(new_matrix[0, :])}")
    # The final column for the sought character provides the parameters:
    l = new_matrix[0, char_index]
    alpha = new_matrix[1, char_index]
    beta = new_matrix[2, char_index]
    return l, alpha, beta


def method_one(l: np.float64, alpha: np.float64, beta: np.float64) -> None:
    print(f"l      : {l:.5f}")
    print(f"alpha  : {alpha:.5f}")
    print(f"beta   : {beta:.5f}")

    base_list = []
    t = 1
    while True:
        t_pow = pow(0.5, t)
        if not (t_pow <= l):
            base_list.append((t, t_pow, 0))
        else:
            base_list.append((t, t_pow, 1))
            break
        t += 1

    # Print the base matrix (as a list of tuples)
    print("\nBase Matrix (Method One):")
    header = f"{'t':>3s} | {'0.5^t':>8s} | {'bit':>3s}"
    print(header)
    print("-" * len(header))
    for tup in base_list:
        print(f"{tup[0]:3d} | {tup[1]:8.5f} | {tup[2]:3d}")

    mid_value = len(base_list)
    left_value = base_list[-1][1]
    right_value = 2 ** (-mid_value + 1)
    print(f"\nt: {left_value:.5f} <= {mid_value} <= {right_value:.5f}")

    upper_x = 2**mid_value
    left_x = upper_x * alpha
    rounded_x = round(left_x)
    initial_value = rounded_x / upper_x
    expansion_bits = binary_expansion(initial_value, 10)

    print("\nMethod One - Scaled Alpha:")
    print(f" Multiplier (2^t)       : {upper_x}")
    print(f" alpha * multiplier     : {left_x:.5f}")
    print(f" Rounded value          : {rounded_x}")
    print(f" Initial value (scaled) : {initial_value:.5f}")
    print(f"Binary expansion (10 bits): {expansion_bits}")


def method_two(l: np.float64, alpha: np.float64, beta: np.float64) -> None:
    """
    Method Two: Output the binary expansion of alpha and beta.
    """
    print(f"l      : {l:.5f}")
    print(f"alpha  : {alpha:.5f}")
    print(f"beta   : {beta:.5f}")

    alpha_bits = binary_expansion(float(alpha), 10)
    beta_bits = binary_expansion(float(beta), 10)

    print("\nMethod Two - Binary Expansions:")
    print(f"Alpha expansion (10 bits): {alpha_bits}")
    print(f"Beta  expansion (10 bits): {beta_bits}")


def main():
    # Print a pretty header.
    print("=" * 60)
    print("Arithmetic Encoding and Binary Expansion Results".center(60))
    print("=" * 60, "\n")

    text = """
    Two roads diverged in a yellow wood,
    And sorry I could not travel both
    And be one traveler, long I stood
    And looked down one as far as I could..., and I
    I took the one less traveled by,
    And that has made all the difference.
    """
    word = "could"

    print("Text (excerpt):")
    print(text.strip())
    print("\nTarget word to encode:", f"'{word}'")
    print("-" * 60, "\n")

    l, alpha, beta = arithmetic_encoder(text, word)

    print("\n" + "-" * 60 + "\n")
    print("Results from Arithmetic Encoder:")
    print(f" l (length parameter)   : {l:.5f}")
    print(f" alpha (lower bound)     : {alpha:.5f}")
    print(f" beta  (upper bound)     : {beta:.5f}")
    print("\n" + "=" * 60 + "\n")

    print("Method 1 Results:")
    print("-" * 60)
    method_one(l, alpha, beta)
    print("\n" + "=" * 60 + "\n")

    print("Method 2 Results:")
    print("-" * 60)
    method_two(l, alpha, beta)
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
