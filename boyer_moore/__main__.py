NO_OF_CHARS = 256


def bad_char_heuristic(string: str, size: int):
    bad_char = [-1] * NO_OF_CHARS

    for i in range(size):
        bad_char[ord(string[i])] = i

    return bad_char


def print_alignment(txt: str, pat: str, shift: int):
    t_line = "T\t"
    p_line = "P\t"

    for i in range(len(txt)):
        t_line += txt[i] + " "

    for i in range(shift):
        p_line += "  "
    for i in range(len(pat)):
        p_line += pat[i] + " "

    print(t_line)
    print(p_line)


def print_alignment_detailed(txt: str, pat: str, shift: int, bc=None, gs=None):
    print("-" * 60)
    t_line = "T\t"
    p_line = "P\t"

    for i in range(len(txt)):
        t_line += txt[i] + " "

    for i in range(shift):
        p_line += "  "
    for i in range(len(pat)):
        p_line += pat[i] + " "

    if bc is not None:
        t_line += f"\tBC: {bc}"
    if gs is not None:
        p_line += f"\tGS: {gs}"

    print(t_line)
    print(p_line)
    print("-" * 60)


def search(txt: str, pat: str, visualize=True):
    m = len(pat)
    n = len(txt)

    bad_char = bad_char_heuristic(pat, m)

    s = 0

    occurrences = []

    while s <= n - m:
        j = m - 1

        if visualize:
            bc_shift = 1
            gs_shift = j + 1

            print_alignment_detailed(txt, pat, s, bc_shift, gs_shift)

        while j >= 0 and pat[j] == txt[s + j]:
            j -= 1

        if j < 0:
            occurrences.append(s)
            if visualize:
                print(f"Pattern found at position {s}")
            s += 1
        else:
            bad_char_shift = max(1, j - bad_char[ord(txt[s + j])])

            s += bad_char_shift

            if visualize:
                print(f"Shift by {bad_char_shift} using Bad Character rule")

    return occurrences


def main():
    txt = "GTTATAGCTGATCGCGGCGTAGCGGCGAA"
    pat = "GTAGCGGCG"

    print("\nText:", txt)
    print("Pattern:", pat)

    occurrences = search(txt, pat, visualize=True)

    print("\nPattern found at positions:", occurrences)


if __name__ == "__main__":
    main()
