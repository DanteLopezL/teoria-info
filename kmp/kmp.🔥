fn prefix_function(p: String) -> List[Int]:
    m = len(p)
    a = List(0) * m
    k = 0
    i = 1

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
    print("Prefix function ", a.__repr__())
    return a


fn search(p: String, s: String) -> List[Int]:
    m = len(p)
    n = len(s)
    a = prefix_function(p)
    result = List[Int]()

    i = 0
    j = 0

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


fn main():
    text = String("ababababababacaabababacaababaca")
    pattern = String("ababaca")
    result = search(pattern, text)

    for index in result:
        print(index[], end=" ")
