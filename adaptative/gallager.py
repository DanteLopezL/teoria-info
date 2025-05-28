class Node:
    def __init__(self, symbol=None, weight=0, order=0):
        self.symbol = symbol
        self.weight = weight
        self.order = order
        self.parent = None
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.left is None and self.right is None


def get_code(node):
    code = ""
    while node.parent is not None:
        code = ("0" if node.parent.left == node else "1") + code
        node = node.parent
    return code


def is_ancestor(ancestor, node):
    current = node
    while current:
        if current == ancestor:
            return True
        current = current.parent
    return False


class Gallager:
    def __init__(self, max_order=512, log_file="resutls.txt"):
        self.max_order = max_order
        self.root = Node(symbol="NYT", weight=0, order=max_order)
        self.NYT = self.root
        self.nodes = {}
        self.all_nodes = [self.root]
        self.log_file = log_file
        with open(self.log_file, "w") as f:
            f.write("Gallager Adaptive Huffman Encoding Log\n")

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def swap_nodes(self, n1, n2):
        if n1.parent is None or n2.parent is None:
            return
        if n1.parent.left == n1:
            n1.parent.left = n2
        else:
            n1.parent.right = n2
        if n2.parent.left == n2:
            n2.parent.left = n1
        else:
            n2.parent.right = n1
        n1.parent, n2.parent = n2.parent, n1.parent
        n1.order, n2.order = n2.order, n1.order
        self.log(f"Swapped nodes {n1.symbol} and {n2.symbol} (new orders {n1.order}, {n2.order})")

    def update(self, node):
        weight_to_nodes = {}
        for n in self.all_nodes:
            weight_to_nodes.setdefault(n.weight, []).append(n)

        while node:
            candidates = weight_to_nodes.get(node.weight, [])
            for other in sorted(candidates, key=lambda n: n.order, reverse=True):
                if other is not node and not is_ancestor(other, node):
                    self.swap_nodes(node, other)
                    break
            node.weight += 1
            weight_to_nodes.setdefault(node.weight, []).append(node)
            self.log(f"Updated node '{node.symbol}' to weight {node.weight}")
            node = node.parent

    def insert(self, symbol):
        if symbol in self.nodes:
            node = self.nodes[symbol]
            code = get_code(node)
            self.log(f"Symbol '{symbol}' exists. Code: {code}")
            self.update(node)
            return code
        else:
            nyt_code = get_code(self.NYT)
            fixed_code = format(ord(symbol), "08b")
            self.log(f"Symbol '{symbol}' new. NYT code: {nyt_code} + fixed: {fixed_code}")
            new_internal = Node(symbol=None, weight=1, order=self.NYT.order - 1)
            new_leaf = Node(symbol=symbol, weight=1, order=self.NYT.order - 2)
            new_internal.left = self.NYT
            new_internal.right = new_leaf
            new_internal.parent = self.NYT.parent
            if self.NYT.parent is None:
                self.root = new_internal
            else:
                if self.NYT.parent.left == self.NYT:
                    self.NYT.parent.left = new_internal
                else:
                    self.NYT.parent.right = new_internal
            self.NYT.parent = new_internal
            new_leaf.parent = new_internal
            self.all_nodes.extend([new_internal, new_leaf])
            self.nodes[symbol] = new_leaf
            self.update(new_internal)
            return nyt_code + fixed_code

    def encode(self, text):
        result = ""
        self.log("\n--- Encoding Start ---")
        for symbol in text:
            code = self.insert(symbol)
            result += code
            self.log(f"Encoded '{symbol}' as: {code}")
        self.log(f"\nFinal encoded bit string: {result}")
        return result


def main():
    text = "c8c828ed"
    tree_gallager = Gallager(log_file="results.txt")
    encoded_gallager = tree_gallager.encode(text)
    print("Final encoded bit string:")
    print(encoded_gallager)


if __name__ == "__main__":
    main()
