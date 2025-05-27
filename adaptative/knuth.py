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


class Knuth:
    def __init__(self, max_order=512):
        # Start with a single NYT (Not Yet Transmitted) node.
        self.max_order = max_order
        self.root = Node(symbol="NYT", weight=0, order=max_order)
        self.NYT = self.root
        # A dictionary mapping symbol -> leaf node.
        self.nodes = {}
        # List of all nodes (for scanning in update), initially only the NYT.
        self.all_nodes = [self.root]

    def swap_nodes(self, n1, n2):
        """Swap the two nodes’ positions (pointers and order numbers)."""
        if n1.parent is None or n2.parent is None:
            return  # do not swap the root
        # Swap parent's pointers.
        if n1.parent.left == n1:
            n1.parent.left = n2
        else:
            n1.parent.right = n2
        if n2.parent.left == n2:
            n2.parent.left = n1
        else:
            n2.parent.right = n1
        # Swap parent pointers.
        n1.parent, n2.parent = n2.parent, n1.parent
        # Swap order numbers.
        n1.order, n2.order = n2.order, n1.order
        print(
            f"Knuth: Swapped nodes {n1.symbol} and {n2.symbol} (new orders {n1.order}, {n2.order})"
        )

    def update(self, node):
        """
        Update the tree from the given node up to the root.
        (Knuth's method: For the current node, scan all nodes to
         find the one with the same weight that has the highest order
         (i.e. lowest in the tree) and is not an ancestor; then swap.)
        """
        while node:
            candidate = node
            for other in self.all_nodes:
                if (
                    other is not node
                    and other.weight == node.weight
                    and not is_ancestor(other, node)
                ):
                    if other.order > candidate.order:
                        candidate = other
            if candidate is not node:
                self.swap_nodes(node, candidate)
            node.weight += 1
            print(f"Knuth: Updated node '{node.symbol}' to weight {node.weight}")
            node = node.parent

    def insert(self, symbol):
        """
        Insert a symbol into the tree.
        If symbol is new, output the NYT code plus fixed (8-bit) representation,
        split the NYT node, and update. Otherwise, output the current code.
        Returns the output bit string for the symbol.
        """
        if symbol in self.nodes:
            node = self.nodes[symbol]
            code = get_code(node)
            print(f"Knuth: Symbol '{symbol}' exists. Code: {code}")
            self.update(node)
            return code
        else:
            nyt_code = get_code(self.NYT)
            fixed_code = format(ord(symbol), "08b")
            print(
                f"Knuth: Symbol '{symbol}' new. NYT code: {nyt_code} + fixed: {fixed_code}"
            )
            # Split the NYT node.
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
        """Encode the text symbol-by-symbol. Return the concatenated bit string."""
        result = ""
        print("\n--- Adaptive Huffman Encoding using Knuth's Method ---")
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

    # Test using Knuth's method.
    tree_knuth = Knuth()
    encoded_knuth = tree_knuth.encode(text)
    print("\nFinal encoded bit string (Knuth):")
    print(encoded_knuth)
    print("=" * 60)


if __name__ == "__main__":
    main()
