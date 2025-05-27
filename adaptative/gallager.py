class Node:
    def __init__(self, symbol=None, weight=0, order=0):
        self.symbol = (
            symbol  # None for internal nodes; a valid symbol (or "NYT") for leaves.
        )
        self.weight = weight
        self.order = order  # Higher order means lower in the tree.
        self.parent = None
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.left is None and self.right is None


def get_code(node):
    """Return the binary code (as string) corresponding to the given node by traversing upward."""
    code = ""
    while node.parent is not None:
        code = ("0" if node.parent.left == node else "1") + code
        node = node.parent
    return code


def is_ancestor(ancestor, node):
    """Return True if 'ancestor' is an ancestor of 'node'."""
    current = node
    while current:
        if current == ancestor:
            return True
        current = current.parent
    return False


class Gallager:
    def __init__(self, max_order=512):
        # Start with a single NYT node.
        self.max_order = max_order
        self.root = Node(symbol="NYT", weight=0, order=max_order)
        self.NYT = self.root
        self.nodes = {}
        self.all_nodes = [self.root]

    def swap_nodes(self, n1, n2):
        """Swap nodes in the tree (Gallager's swap, similar to Knuth's but used differently in update)."""
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
        print(
            f"Gallager: Swapped nodes {n1.symbol} and {n2.symbol} (new orders {n1.order}, {n2.order})"
        )

    def update(self, node):
        """
        Update the tree using Gallager's method.
        Instead of scanning all nodes, we traverse the nodes in descending order
        (by order number) and swap the first node we find with the same weight
        (and not in the current node's subtree). Then increment the weight.
        """
        while node:
            # Traverse in descending order of order numbers.
            sorted_nodes = sorted(self.all_nodes, key=lambda n: n.order, reverse=True)
            for other in sorted_nodes:
                if (
                    other is not node
                    and other.weight == node.weight
                    and not is_ancestor(other, node)
                ):
                    self.swap_nodes(node, other)
                    break  # In Gallager's method, do one swap per update cycle.
            node.weight += 1
            print(f"Gallager: Updated node '{node.symbol}' to weight {node.weight}")
            node = node.parent

    def insert(self, symbol):
        """Insert a symbol into the tree; handle new symbols as in the Knuth version."""
        if symbol in self.nodes:
            node = self.nodes[symbol]
            code = get_code(node)
            print(f"Gallager: Symbol '{symbol}' exists. Code: {code}")
            self.update(node)
            return code
        else:
            nyt_code = get_code(self.NYT)
            fixed_code = format(ord(symbol), "08b")
            print(
                f"Gallager: Symbol '{symbol}' new. NYT code: {nyt_code} + fixed: {fixed_code}"
            )
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
        """Encode a text string symbol-by-symbol using Gallager's update. Return the full bit string."""
        result = ""
        print("\n--- Adaptive Huffman Encoding using Gallager's Method ---")
        for symbol in text:
            code = self.insert(symbol)
            result += code
            print(f"Encoded '{symbol}' as: {code}")
        return result


def main():
    text = "adaptive"
    print("=" * 60)
    print("Adaptive Huffman Encoding Comparison".center(60))
    print("=" * 60)
    print("Input text:", text)

    # Test using Gallager's method.
    tree_gallager = Gallager()
    encoded_gallager = tree_gallager.encode(text)
    print("\nFinal encoded bit string (Gallager):")
    print(encoded_gallager)
    print("=" * 60)


if __name__ == "__main__":
    main()
