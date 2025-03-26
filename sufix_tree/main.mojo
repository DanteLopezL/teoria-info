from collections import Dict


fn main():
    tree = Dict[Int, String]()
    word = String("RGFABASABPUEFABASFWFDMOGFOASABASABABASABWM")
    repeated = List[String]()
    for char in word.codepoint_slices():
        if String(char) not in repeated:
            repeated.append(String(char))

    for i in range(len(repeated)):
        aux = 0
        for j in range(len(word)):
            if word[j] == repeated[i]:
                aux = j
                break

        tree[i] = word[aux:]

    for item in tree.items():
        print(item[].key, item[].value)