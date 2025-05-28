class Node:
    def __init__(self, symbol=None, weight=0, order=0):
        self.symbol = symbol      # None for internal nodes; otherwise a character (or "NYT")
        self.weight = weight
        self.order = order        # Order number; larger numbers are “lower” in the tree.
        self.parent = None
        self.left = None
        self.right = None

    def is_leaf(self):
        return self.left is None and self.right is None


def get_code(node):
    """Return the binary code (as string) corresponding to the given node by traversing upward."""
    code = ""
    while node.parent is not None:
        # If node is the left child of its parent, prepend "0"; if right, prepend "1"
        code = ("0" if node.parent.left == node else "1") + code
        node = node.parent
    return code


def is_ancestor(ancestor, node):
    """Return True if 'ancestor' is indeed an ancestor of 'node'."""
    current = node
    while current is not None:
        if current == ancestor:
            return True
        current = current.parent
    return False


class AdaptiveHuffmanTree:
    def __init__(self, max_order=512):
        # Initialize with a single NYT (Not Yet Transmitted) node.
        self.max_order = max_order
        self.root = Node(symbol="NYT", weight=0, order=max_order)
        self.NYT = self.root
        # Dictionary mapping symbol to its leaf node in the tree.
        self.nodes = {}
        # Maintain a list of all nodes in the tree (useful for swapping)
        self.all_nodes = [self.root]

    def get_code_for_symbol(self, symbol):
        # Return the current code for an existing symbol, or the code for NYT if not seen.
        if symbol in self.nodes:
            return get_code(self.nodes[symbol])
        else:
            return get_code(self.NYT)

    def swap_nodes(self, n1, n2):
        """Swap the two nodes (their parent's pointers and order numbers)."""
        if n1.parent is None or n2.parent is None:
            return  # Do not swap the root.
        # Swap parent's child pointers.
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
        print(f"  >> Swapped nodes: {n1.symbol} and {n2.symbol} (new orders {n1.order} and {n2.order})")

    def update(self, node):
        """
        Update the tree from the given leaf (or internal) node up to the root.
        At each step, find the node with the highest order (i.e. lowest in the tree)
        among those with the same weight that is not an ancestor of the current node,
        and swap if necessary. Then increment the weight.
        """
        while node is not None:
            # Find candidate for swap: among all nodes with the same weight.
            candidate = node
            for candidate_node in self.all_nodes:
                if (candidate_node.weight == node.weight and candidate_node is not node
                        and not is_ancestor(candidate_node, node)):
                    if candidate_node.order > candidate.order:
                        candidate = candidate_node
            if candidate is not node:
                self.swap_nodes(node, candidate)
            node.weight += 1
            print(f"  >> Updated node: {node.symbol} new weight: {node.weight}")
            node = node.parent

    def insert(self, symbol):
        """
        Insert a symbol into the adaptive tree.
        If the symbol is new, output the NYT node code and then a fixed binary representation (8 bits) of the symbol.
        Otherwise, output the current code for that symbol.
        Then update the tree.
        Returns the bit string output for this symbol.
        """
        if symbol in self.nodes:
            # Symbol already exists. Get its current code.
            node = self.nodes[symbol]
            code = get_code(node)
            print(f"Symbol '{symbol}' found. Output code: {code}")
            self.update(node)
            return code
        else:
            # Symbol not seen: output NYT code followed by fixed 8-bit representation of symbol
            nyt_code = get_code(self.NYT)
            fixed_code = format(ord(symbol), '08b')
            print(f"Symbol '{symbol}' is new. Output NYT code: {nyt_code} and fixed code: {fixed_code}")
            # Split the NYT node: create an internal node that takes the place of NYT.
            new_internal = Node(symbol=None, weight=1, order=self.NYT.order - 1)
            new_leaf = Node(symbol=symbol, weight=1, order=self.NYT.order - 2)
            new_internal.left = self.NYT
            new_internal.right = new_leaf
            new_internal.parent = self.NYT.parent
            if self.NYT.parent is None:
                # NYT was the root.
                self.root = new_internal
            else:
                # Replace NYT in its parent's child pointer.
                if self.NYT.parent.left == self.NYT:
                    self.NYT.parent.left = new_internal
                else:
                    self.NYT.parent.right = new_internal
            self.NYT.parent = new_internal
            new_leaf.parent = new_internal
            # Append the new internal and leaf nodes to the list.
            self.all_nodes.append(new_internal)
            self.all_nodes.append(new_leaf)
            # Record the new leaf in our nodes dictionary.
            self.nodes[symbol] = new_leaf
            # Update the tree starting from the new internal node.
            self.update(new_internal)
            return nyt_code + fixed_code

    def encode(self, text):
        """Encode the given text string symbol-by-symbol and return the combined output bit string."""
        result = ""
        print("\n--- Encoding Process ---")
        for symbol in text:
            code = self.insert(symbol)
            result += code
            print(f"Encoded '{symbol}' as: {code}")
        return result


def main():
    # Sample text to encode. Feel free to change it.
    text = "adaptive"
    print("=" * 60)
    print("Adaptive Huffman Encoding (FGK Algorithm)")
    print("=" * 60)
    print("Input text:", text)
    print()

    # Create an AdaptiveHuffmanTree instance (no global variables used)
    tree = AdaptiveHuffmanTree()

    # Encode the text.
    encoded_bit_string = tree.encode(text)
    print("\nFinal encoded bit string:")
    print(encoded_bit_string)
    print("=" * 60)


if __name__ == "__main__":
    main()
