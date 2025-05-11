mod utils; // This loads utils/mod.rs
use clap::Parser;
use polars::prelude::*;
use std::cmp::Ordering;
use std::collections::{BTreeMap, HashMap};
use std::fs::File;
use std::io::{self, Read};

/// Text Sequence Frequency Analysis and Optimal Coding Tool
///
/// This program analyzes character sequence frequencies with length-based weighting,
/// generates optimal encodings using dynamic programming, and displays results in
/// tabular format using Polars.
#[derive(Parser, Debug)]
#[clap(author, version, about)]
struct Args {
    /// Path to input text file
    #[clap(value_parser)]
    file: String,

    /// Maximum sequence length to consider
    #[clap(short, long, default_value_t = 3)]
    m: usize,

    /// Weighting exponent (0 = no weighting)
    #[clap(short, long, default_value_t = 1)]
    alpha: i32,

    /// Sort frequencies before coding
    #[clap(short, long)]
    sort: bool,
}

/// Calculate weighted frequencies of character sequences in text
fn frequency_estimation(text: &str, n: usize, m: usize, alpha: i32) -> HashMap<String, f64> {
    let mut frequencies: HashMap<String, f64> = HashMap::new();

    for i in 1..=m {
        // i = 1, 2, ..., m
        for j in 0..=(n - i) {
            // Slide window over input
            let s = &text[j..(j + i)]; // Extract sequence of length i
            let weight = (i as f64).powi(alpha);
            *frequencies.entry(s.to_string()).or_insert(0.0) += weight;
        }
    }

    frequencies
}

/// Generate optimal encoding for text using provided coding table
fn optimal_coding(text: &str, dc: &HashMap<String, String>, n: usize, m: usize) -> String {
    let mut dn: HashMap<usize, String> = HashMap::new();
    dn.insert(0, String::new());

    for e in 0..n {
        for i in e..=(e * m).min(n - 1) {
            let k = i + 1;
            let l = (i + m).min(n);

            for j in k..=l {
                let s = &text[i..j];
                if !dc.contains_key(s) {
                    continue;
                }

                let c = format!(
                    "{}{}",
                    dn.get(&i).unwrap_or(&String::new()),
                    dc.get(s).unwrap_or(&String::new())
                );

                if !dn.contains_key(&j) || dn.get(&i).unwrap_or(&String::new()).len() > c.len() {
                    dn.insert(j, c);
                }
            }
        }
    }

    dn.get(&n).cloned().unwrap_or_default()
}

/// Generate Huffman codes recursively from the tree
fn generate_codes(
    tree: &HashMap<String, (String, String)>,
    node: &str,
    code: &str,
    codes: &mut HashMap<String, String>,
) {
    if !tree.contains_key(node) {
        codes.insert(node.to_string(), code.to_string());
        return;
    }

    let (left, right) = tree.get(node).unwrap();

    // Recurse left (0) and right (1)
    generate_codes(tree, left, &format!("{}0", code), codes);
    generate_codes(tree, right, &format!("{}1", code), codes);
}

/// Build a Huffman tree from character frequencies
fn generate_tree(frequencies: &HashMap<String, f64>) -> HashMap<String, (String, String)> {
    let total: f64 = frequencies.values().sum();
    let mut encoding: Vec<(String, f64)> = Vec::new();
    let mut tree: HashMap<String, (String, String)> = HashMap::new();

    // Convert frequencies to probabilities
    for (char, count) in frequencies {
        encoding.push((char.clone(), count / total));
    }

    // Sort by probability (descending)
    encoding.sort_by(|a, b| {
        let ord = b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal);
        if ord == Ordering::Equal {
            a.0.cmp(&b.0)
        } else {
            ord
        }
    });

    // Build the tree bottom-up
    for i in 0..(encoding.len().saturating_sub(1)) {
        if encoding.len() < 2 {
            break;
        }

        let last = encoding.pop().unwrap();
        let penultimate = encoding.pop().unwrap();

        let new_node = format!("o{}", i + 1);
        let new_prob = last.1 + penultimate.1;

        tree.insert(new_node.clone(), (penultimate.0.clone(), last.0.clone()));

        // Insert the new node and sort again
        encoding.push((new_node, new_prob));
        encoding.sort_by(|a, b| {
            let ord = b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal);
            if ord == Ordering::Equal {
                a.0.cmp(&b.0)
            } else {
                ord
            }
        });
    }

    if encoding.len() >= 2 {
        // Add the root node
        tree.insert(
            "origin".to_string(),
            (
                encoding[encoding.len() - 2].0.clone(),
                encoding[encoding.len() - 1].0.clone(),
            ),
        );
    } else if encoding.len() == 1 {
        // Single character case
        tree.insert(
            "origin".to_string(),
            (encoding[0].0.clone(), "dummy".to_string()),
        );
        tree.insert("dummy".to_string(), ("".to_string(), "".to_string()));
    }

    // Return tree (from root to leaves)
    tree
}

/// Generate and display Huffman coding table and statistics
fn generate_table(
    frequencies: &HashMap<String, f64>,
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
fn print_table(frequencies: &HashMap<String, f64>, codes: &HashMap<String, String>) {
    let total: f64 = frequencies.values().sum();

    let chars: Vec<String> = frequencies.keys().cloned().collect();
    let mut freq_list: Vec<f64> = Vec::new();
    let mut fi: Vec<f64> = Vec::new();
    let mut code_list: Vec<String> = Vec::new();
    let mut needed_chars: Vec<usize> = Vec::new();
    let mut hi_list: Vec<f64> = Vec::new();

    for char in &chars {
        let freq = *frequencies.get(char).unwrap_or(&0.0);
        let probability = freq / total;
        let code = codes.get(char).unwrap_or(&"N/A".to_string()).clone();
        let code_len = if code == "N/A" { 0 } else { code.len() };

        // Calculate entropy component for this character (-fi * log2(fi))
        let entropy_component = if probability > 0.0 {
            -probability * probability.log2()
        } else {
            0.0
        };

        freq_list.push(freq);
        fi.push(probability);
        code_list.push(code);
        needed_chars.push(code_len);
        hi_list.push(entropy_component);
    }

    // Calculate total entropy
    let h: f64 = hi_list.iter().sum();

    // Calculate LMS (average code length)
    let lms: f64 = fi
        .iter()
        .zip(needed_chars.iter())
        .map(|(&prob, &nc)| prob * nc as f64)
        .sum();

    // Create Polars DataFrame for character table
    let char_df = df! [
        "CHAR" => chars,
        "FREQ" => freq_list,
        "Fi" => fi,
        "CODE" => code_list,
        "NEEDED_CHARS" => needed_chars.iter().map(|&x| x as i64).collect::<Vec<i64>>(),
        "Hi" => hi_list
    ]
    .unwrap();

    // Create DataFrame for summary metrics
    let summary_df = df! [
        "METRIC" => vec!["LMS", "LME", "RC", "H"],
        "VALUE" => vec![lms, 8.0, 8.0 / lms, h]
    ]
    .unwrap();

    println!("\n=== HUFFMAN CODE TABLE ===");
    println!("{}", char_df);

    println!("\n=== COMPRESSION METRICS ===");
    println!("{}", summary_df);
}

/// Read and preprocess input file
fn read_file(file_path: &str) -> io::Result<String> {
    let mut file = File::open(file_path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    // Remove whitespace
    Ok(contents.split_whitespace().collect())
}

fn main() -> io::Result<()> {
    let args = Args::parse();

    // Read and preprocess input file
    let text = read_file(&args.file)?;
    let n = text.len();

    // Calculate frequencies
    let frequencies = frequency_estimation(&text, n, args.m, 0);
    let weighted_frequencies = frequency_estimation(&text, n, args.m, args.alpha);

    println!("Sequence Frequencies (weighted by i^α):");

    // Prepare data for DataFrame
    let keys: Vec<String> = weighted_frequencies.keys().cloned().collect();
    let values: Vec<f64> = keys
        .iter()
        .map(|k| *frequencies.get(k).unwrap_or(&0.0))
        .collect();
    let weighted_values: Vec<f64> = keys
        .iter()
        .map(|k| *weighted_frequencies.get(k).unwrap_or(&0.0))
        .collect();

    // Create and display DataFrame
    let freq_df = df! [
        "Sequence" => keys.clone(),
        "Frequency" => values,
        format!("Weighted (a={})", args.alpha) => weighted_values
    ]
    .unwrap();

    println!("{}", freq_df);

    // Sort frequencies if requested
    let sorted_frequencies = if args.sort {
        let mut sorted: BTreeMap<String, f64> = BTreeMap::new();
        let mut freq_vec: Vec<(String, f64)> =
            frequencies.iter().map(|(k, v)| (k.clone(), *v)).collect();
        freq_vec.sort_by(|a, b| {
            let ord = b.1.partial_cmp(&a.1).unwrap_or(Ordering::Equal);
            if ord == Ordering::Equal {
                a.0.cmp(&b.0)
            } else {
                ord
            }
        });
        for (k, v) in freq_vec {
            sorted.insert(k, v);
        }
        sorted.into_iter().collect()
    } else {
        frequencies.clone()
    };

    // Generate Huffman tree and codes
    let tree = generate_tree(&sorted_frequencies);
    let dc = generate_table(&sorted_frequencies, &tree);

    // Generate optimal encoding
    let dn = optimal_coding(&text, &dc, n, args.m);

    // Display results
    let result_df = df! [
        "Input (I)" => vec![text],
        "Optimal coding (dn)" => vec![dn]
    ]
    .unwrap();

    println!("{}", result_df);

    Ok(())
}
