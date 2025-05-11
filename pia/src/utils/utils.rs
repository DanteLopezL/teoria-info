use polars::prelude::*;
use std::collections::HashMap;
use std::f64;

/// Calculate the fi values (probabilities) from frequencies
pub fn calculate_fi(frequencies: &HashMap<String, i32>) -> (i32, Vec<f64>) {
    let total: i32 = frequencies.values().sum();
    let fi: Vec<f64> = frequencies
        .values()
        .map(|&i| i as f64 / total as f64)
        .collect();

    (total, fi)
}

/// Generate Huffman codes recursively from the tree
pub fn generate_codes(
    tree: &HashMap<String, (String, String)>,
    node: &str,
    code: &str,
    codes: &mut HashMap<String, String>,
) {
    // If node not in tree, it's a leaf node (character)
    if !tree.contains_key(node) {
        codes.insert(node.to_string(), code.to_string());
        return;
    }

    let (left, right) = &tree[node].clone();

    // Recurse left (0) and right (1)
    generate_codes(tree, left, &format!("{}0", code), codes);
    generate_codes(tree, right, &format!("{}1", code), codes);
}

/// Build a Huffman tree from character frequencies
pub fn generate_tree(frequencies: &HashMap<String, i32>) -> HashMap<String, (String, String)> {
    let total: i32 = frequencies.values().sum();
    let mut encoding: Vec<(String, f64)> = Vec::new();
    let mut tree: HashMap<String, (String, String)> = HashMap::new();

    // Convert frequencies to probabilities
    for (char, count) in frequencies {
        encoding.push((char.clone(), *count as f64 / total as f64));
    }

    // Sort by probability (descending)
    encoding.sort_by(|a, b| match b.1.partial_cmp(&a.1).unwrap() {
        std::cmp::Ordering::Equal => a.0.cmp(&b.0),
        other => other,
    });

    // Handle special case of only one character
    if encoding.len() == 1 {
        let char = encoding[0].0.clone();
        tree.insert("origin".to_string(), (char, "dummy".to_string()));
        return tree;
    }

    // Build the tree bottom-up
    let mut i = 0;
    while encoding.len() > 2 {
        let last = encoding.pop().unwrap();
        let penultimate = encoding.pop().unwrap();

        let new_name = format!("o{}", i + 1);
        let new_prob = last.1 + penultimate.1;

        tree.insert(new_name.clone(), (penultimate.0.clone(), last.0.clone()));

        // Find the correct position to insert the new node
        let mut insert_pos = 0;
        while insert_pos < encoding.len() && encoding[insert_pos].1 > new_prob {
            insert_pos += 1;
        }

        // Check if we have equal probabilities
        while insert_pos < encoding.len()
            && encoding[insert_pos].1 == new_prob
            && encoding[insert_pos].0 < new_name
        {
            insert_pos += 1;
        }

        encoding.insert(insert_pos, (new_name, new_prob));
        i += 1;
    }

    // Add the root node
    if encoding.len() == 2 {
        tree.insert(
            "origin".to_string(),
            (encoding[0].0.clone(), encoding[1].0.clone()),
        );
    }

    tree
}

/// Generate and display Huffman coding table and statistics
pub fn generate_table(
    frequencies: &HashMap<String, i32>,
    tree: &HashMap<String, (String, String)>,
) -> HashMap<String, String> {
    let mut codes: HashMap<String, String> = HashMap::new();
    generate_codes(tree, "origin", "", &mut codes);

    print_table(frequencies, &codes);

    // Print tree structure
    println!("\nTree structure:");
    for (node, (left, right)) in tree {
        println!("{} -> ({}, {})", node, left, right);
    }

    codes
}

/// Print a formatted table with character frequencies and codes using Polars
pub fn print_table(frequencies: &HashMap<String, i32>, codes: &HashMap<String, String>) {
    let chars: Vec<String> = frequencies.keys().cloned().collect();
    let (total, fi) = calculate_fi(frequencies);

    let freq_list: Vec<i32> = chars
        .iter()
        .map(|c| *frequencies.get(c).unwrap_or(&0))
        .collect();
    let code_list: Vec<String> = chars
        .iter()
        .map(|c| codes.get(c).unwrap_or(&"N/A".to_string()).clone())
        .collect();
    let needed_chars: Vec<i32> = chars
        .iter()
        .map(|c| codes.get(c).unwrap_or(&"".to_string()).len() as i32)
        .collect();

    // Calculate entropy for each character (-fi * log2(fi))
    let hi_list: Vec<f64> = fi
        .iter()
        .map(|&p| if p > 0.0 { -p * p.log2() } else { 0.0 })
        .collect();
    let h: f64 = hi_list.iter().sum();

    let lms: f64 = fi
        .iter()
        .zip(&needed_chars)
        .map(|(&p, &n)| p * n as f64)
        .sum();

    // Create DataFrame for character table
    let char_df = df!(
        "CHAR" => chars,
        "FREQ" => freq_list,
        "Fi" => fi,
        "CODE" => code_list,
        "NEEDED_CHARS" => needed_chars,
        "Hi" => hi_list
    )
    .unwrap();

    // Create DataFrame for summary metrics
    let summary_df = df!(
        "METRIC" => vec!["LMS", "LME", "RC", "H"],
        "VALUE" => vec![lms, 8.0, 8.0 / lms, h]
    )
    .unwrap();

    println!("\n=== HUFFMAN CODE TABLE ===");
    println!("{}", char_df);

    println!("\n=== COMPRESSION METRICS ===");
    println!("{}", summary_df);
}

/// Calculate compression statistics
pub fn calculate_compression(
    original_text: &str,
    codes: &HashMap<String, String>,
) -> (usize, usize, f64) {
    let original_bits = original_text.len() * 8;

    let compressed_bits = original_text
        .chars()
        .map(|c| codes.get(&c.to_string()).unwrap_or(&String::new()).len())
        .sum();

    let ratio = compressed_bits as f64 / original_bits as f64;

    (original_bits, compressed_bits, ratio)
}

/// Decode a Huffman-encoded text
pub fn decode_text(encoded_text: &str, tree: &HashMap<String, (String, String)>) -> String {
    let mut current_node = "origin";
    let mut decoded_text = String::new();

    for bit in encoded_text.chars() {
        let (left, right) = tree.get(current_node).unwrap();
        current_node = if bit == '0' { left } else { right };

        // If we reached a leaf node (character)
        if !tree.contains_key(current_node) {
            decoded_text.push_str(current_node);
            current_node = "origin"; // Reset to root
        }
    }

    decoded_text
}

/// Encode text using Huffman codes
pub fn encode_text(text: &str, codes: &HashMap<String, String>) -> String {
    let mut encoded = String::new();
    for c in text.chars() {
        if let Some(code) = codes.get(&c.to_string()) {
            encoded.push_str(code);
        }
    }
    encoded
}
