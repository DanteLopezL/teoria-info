def prefix_function(p: str):
    m = len(p)
    a = [0] * m

    # Length of the previous longest prefix suffix
    k = 0
    i = 1

    # Loop calculates a[i] for i = 1 to M-1
    while i < m:
        if p[i] == p[k]:
            k += 1
            a[i] = k
            i += 1
        else:
            if k != 0:
                k = a[k - 1]
            else:
                a[i] = 0
                i += 1
    print(f"Prefix function {a}")
    return a


def search(p: str, s: str):
    m = len(p)
    n = len(s)

    a = prefix_function(p)
    result = []

    i = 0  # index for txt
    j = 0  # index for pattern
    while (n - i) >= (m - j):
        if p[j] == s[i]:
            j += 1
            i += 1

        if j == m:
            result.append(i - j + 1)
            j = a[j - 1]
        elif i < n and p[j] != s[i]:
            if j != 0:
                j = a[j - 1]
            else:
                i += 1
    return result


def main():
    text = "bacbabababacaab"
    pattern = "ababaca"
    result = search(pattern, text)

    for index in result:
        print(index, end=" ")


if __name__ == "__main__":
    main()
