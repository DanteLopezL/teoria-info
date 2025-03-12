import json


def main():
    tree = {}
    word = 'RGFABASABPUEFABASFWFDMOGFOASABASABABASABWM'
    repeated = []
    for char in word:
        if char not in repeated:
            repeated.append(char)

    for i in range(len(repeated)):
        aux = 0
        for j in range(len(word)):
            if word[j] == repeated[i]:
                aux = j
                break
        tree[i] = word[aux:]

    print(json.dumps(tree, indent=2))


if __name__ == "__main__":
    main()
