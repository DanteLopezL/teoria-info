use std::cmp::Reverse;
use std::collections::{BinaryHeap, HashMap};

// Node for Huffman tree construction
struct Node {
    symbol: Option<String>,
    frequency: usize,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

impl Node {
    fn new(symbol: Option<String>, frequency: usize) -> Self {
        Node {
            symbol,
            frequency,
            left: None,
            right: None,
        }
    }
}

// Needed for BinaryHeap (priority queue)
impl Eq for Node {}

impl PartialEq for Node {
    fn eq(&self, other: &Self) -> bool {
        self.frequency == other.frequency
    }
}

impl PartialOrd for Node {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Node {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.frequency.cmp(&other.frequency)
    }
}

/// Implement Huffman coding.
///
/// # Arguments
///
/// * `frequencies` - HashMap mapping symbols to their frequencies
///
/// # Returns
///
/// HashMap mapping symbols to their Huffman codes
pub fn huffman(frequencies: &HashMap<String, usize>) -> HashMap<String, String> {
    if frequencies.is_empty() {
        return HashMap::new();
    }

    // Step 1: Create initial forest of nodes
    let mut forest: BinaryHeap<Reverse<Box<Node>>> = BinaryHeap::new();
    for (symbol, &freq) in frequencies {
        forest.push(Reverse(Box::new(Node::new(Some(symbol.clone()), freq))));
    }

    // Special case: only one symbol
    if forest.len() == 1 {
        if let Some(Reverse(node)) = forest.pop() {
            if let Some(symbol) = &node.symbol {
                let mut code_map = HashMap::new();
                code_map.insert(symbol.clone(), "0".to_string());
                return code_map;
            }
        }
        return HashMap::new();
    }

    // Step 2: Build Huffman tree by iteratively combining trees with lowest frequencies
    while forest.len() > 1 {
        // Find two trees with lowest frequencies
        let Reverse(left) = forest.pop().unwrap();
        let Reverse(right) = forest.pop().unwrap();

        // Create a new internal node with these two nodes as children
        let mut new_node = Node::new(None, left.frequency + right.frequency);
        new_node.left = Some(left);
        new_node.right = Some(right);

        // Add the new tree back to the forest
        forest.push(Reverse(Box::new(new_node)));
    }

    // The remaining tree is the Huffman code tree
    let tree_root = forest.pop().unwrap();

    // Step 3: Generate codewords by traversing the tree from root to each leaf
    let mut codes: HashMap<String, String> = HashMap::new();

    fn assign_codes(node: &Node, code: String, codes: &mut HashMap<String, String>) {
        if let Some(symbol) = &node.symbol {
            codes.insert(symbol.clone(), code.clone());
        }

        if let Some(left) = &node.left {
            assign_codes(left, code.clone() + "0", codes);
        }

        if let Some(right) = &node.right {
            assign_codes(right, code.clone() + "1", codes);
        }
    }

    assign_codes(&tree_root.0, String::new(), &mut codes);
    codes
}

/// Decode Huffman-encoded data using the provided codes.
///
/// # Arguments
///
/// * `encoded_data` - The binary string of encoded data
/// * `codes` - HashMap mapping symbols to their Huffman codes
///
/// # Returns
///
/// Decoded string
pub fn decode(encoded_data: &str, codes: &HashMap<String, String>) -> String {
    if encoded_data.is_empty() || codes.is_empty() {
        return String::new();
    }

    // Build the decode tree
    let mut root = Node::new(None, 0);

    for (symbol, code) in codes {
        let mut current = &mut root;

        for bit in code.chars() {
            match bit {
                '0' => {
                    if current.left.is_none() {
                        current.left = Some(Box::new(Node::new(None, 0)));
                    }
                    current = current.left.as_mut().unwrap();
                }
                '1' => {
                    if current.right.is_none() {
                        current.right = Some(Box::new(Node::new(None, 0)));
                    }
                    current = current.right.as_mut().unwrap();
                }
                _ => panic!("Invalid bit in Huffman code"),
            }
        }

        current.symbol = Some(symbol.clone());
    }

    // Decode
    let mut result = String::new();
    let mut current = &root;

    for bit in encoded_data.chars() {
        current = match bit {
            '0' => {
                if let Some(node) = &current.left {
                    node
                } else {
                    return String::new(); // Invalid encoding
                }
            }
            '1' => {
                if let Some(node) = &current.right {
                    node
                } else {
                    return String::new(); // Invalid encoding
                }
            }
            _ => panic!("Invalid bit in encoded data"),
        };

        if let Some(symbol) = &current.symbol {
            result.push_str(symbol);
            current = &root;
        }
    }

    result
}

/// Calculate weighted frequencies of character sequences in text.
///
/// # Arguments
///
/// * `text` - Input string to analyze
/// * `n` - Length of input text
/// * `m` - Maximum sequence length to consider
/// * `alpha` - Weighting exponent (0 = no weighting)
///
/// # Returns
///
/// HashMap mapping sequences to their weighted frequencies
pub fn frequency_estimation(text: &str, n: usize, m: usize, alpha: i32) -> HashMap<String, usize> {
    let mut df: HashMap<String, usize> = HashMap::new();

    for i in 1..=m {
        for j in 0..=(n - i) {
            let s = &text[j..(j + i)];
            let weight = if alpha == 0 { 1 } else { i.pow(alpha as u32) };

            *df.entry(s.to_string()).or_insert(0) += weight;
        }
    }

    df
}

/// Calculate compression ratio.
///
/// # Arguments
///
/// * `text_size` - Original text size in bits
/// * `encoded_size` - Encoded data size in bits
///
/// # Returns
///
/// Compression ratio (encoded_size / text_size)
pub fn compression_ratio(text_size: usize, encoded_size: usize) -> f64 {
    encoded_size as f64 / text_size as f64
}
