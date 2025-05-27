use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read};
use std::path::PathBuf;

use clap::Parser;
use polars::prelude::*;

mod utils;


fn optimal_coding(text: &str, dc: &HashMap<String, String>, n: usize, m: usize) -> String {
    let mut dp: HashMap<usize, String> = HashMap::new();
    dp.insert(0, String::new());

    for e in 0..n {
        for i in e..std::cmp::min(m * e + 1, n) {
            let k = i + 1;
            let l = std::cmp::min(i + m, n);

            for j in k..=l {
                if j > text.len() {
                    continue;
                }

                let s = &text[i..j];

                if !dc.contains_key(s) {
                    continue;
                }

                if let Some(prev_encoding) = dp.get(&i) {
                    let c = prev_encoding.clone() + &dc[s];

                    if !dp.contains_key(&j) || dp[&j].len() > c.len() {
                        dp.insert(j, c);
                    }
                }
            }
        }
    }

    dp.get(&n).cloned().unwrap_or_default()
}


fn approximate_coding(text: &str, dc: &HashMap<String, String>, n: usize, m: usize) -> String {
    let mut c = String::new();
    let mut i = 0;

    while i < n {
        let mut r = 0.0; // best ratio found value
        let mut l = i; // end of best ratio sequence

        for k in 1..=m {
            let j = std::cmp::min(i + k, n);
            let s = &text[i..j];

            if let Some(codeword) = dc.get(s) {
                let t = s.len() as f64 / codeword.len() as f64;
                if t > r {
                    r = t;
                    l = j;
                }
            }
        }

        if l > i {
            if let Some(code) = dc.get(&text[i..l]) {
                c.push_str(code);
            }
            i = l;
        } else {
            // No matching sequence found, move to next character
            i += 1;
        }
    }

    c
}

/// Command line arguments
#[derive(Parser, Debug)]
#[clap(author, version, about)]
struct Args {
    /// Path to input text file
    #[clap(short, long)]
    file: PathBuf,

    /// Maximum sequence length
    #[clap(short, long, default_value = "3")]
    m: usize,

    /// Weighting exponent
    #[clap(short, long, default_value = "1")]
    alpha: i32,

    /// Sort frequencies before coding
    #[clap(short, long)]
    sort: bool,

    /// Use heuristic (approximate) coding only
    #[clap(short, long)]
    heuristic: bool,

    /// Use optimal coding only
    #[clap(short, long)]
    optimal: bool,
}

fn main() -> io::Result<()> {
    // Parse command line arguments
    let args = Args::parse();

    // Read and preprocess input file
    let mut file = File::open(args.file)?;
    let mut text = String::new();
    file.read_to_string(&mut text)?;

    // Remove whitespace
    text = text.split_whitespace().collect();
    let n = text.len();
    let frequencies = utils::utils::frequency_estimation(&text, n, args.m, 0);
    let weighted_frequencies = utils::utils::frequency_estimation(&text, n, args.m, args.alpha);

    // Extract keys and values for display
    let keys: Vec<String> = frequencies.keys().cloned().collect();
    let values: Vec<usize> = frequencies.values().cloned().collect();
    let weighted_values: Vec<usize> = weighted_frequencies.values().cloned().collect();

    // Create DataFrame for display
    let df = df!(
        "Sequence" => &keys,
        "Frequency" => &values,
        format!("Weighted (a={})", args.alpha) => &weighted_values
    )
    .unwrap();

    println!("Sequence Frequencies (weighted by i^α):");
    println!("{}", df);

    // Sort frequencies if requested
    let mut sorted_frequencies = weighted_frequencies.clone();
    if args.sort {
        // Sort by frequency descending, then by sequence
        let mut freq_vec: Vec<(String, usize)> = sorted_frequencies.into_iter().collect();
        freq_vec.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0)));
        sorted_frequencies = freq_vec.into_iter().collect();
    }

    // Generate Huffman codes
    let dc = utils::utils::huffman(&sorted_frequencies);

    // Process based on options
    if !args.heuristic && !args.optimal {
        // Both optimal and approximate
        let oc = optimal_coding(&text, &dc, n, args.m);
        let ac = approximate_coding(&text, &dc, n, args.m);

        // Create result DataFrame
        let result_df = df!(
            "Input (I)" => &[text.clone()],
            "Optimal coding (dn)" => &[oc.clone()],
            "Approximate coding (ac)" => &[ac.clone()]
        )
        .unwrap();

        println!("{}", result_df);

        // Calculate compression ratios
        let text_size = text.len();
        let optimal_cr = utils::utils::compression_ratio(text_size, oc.len());
        let approx_cr = utils::utils::compression_ratio(text_size, ac.len());

        // Create compression ratio DataFrame
        let cr_df = df!(
            "m" => &[args.m],
            "a" => &[args.alpha],
            "Optimal compression" => &[optimal_cr],
            "Approximate compression" => &[approx_cr]
        )
        .unwrap();

        println!("{}", cr_df);
    } else if args.heuristic {
        // Approximate only
        let ac = approximate_coding(&text, &dc, n, args.m);

        // Create result DataFrame
        let result_df = df!(
            "Input (I)" => &[text.clone()],
            "Approximate coding (ac)" => &[ac.clone()]
        )
        .unwrap();

        println!("{}", result_df);

        // Calculate compression ratio
        let text_size = text.len();
        let approx_cr = utils::utils::compression_ratio(text_size, ac.len());

        // Create compression ratio DataFrame
        let cr_df = df!(
            "m" => &[args.m],
            "a" => &[args.alpha],
            "Approximate compression" => &[approx_cr]
        )
        .unwrap();

        println!("{}", cr_df);
    } else {
        // Optimal only
        let oc = optimal_coding(&text, &dc, n, args.m);

        // Create result DataFrame
        let result_df = df!(
            "Input (I)" => &[text.clone()],
            "Optimal coding (c)" => &[oc.clone()]
        )
        .unwrap();

        println!("{}", result_df);

        // Calculate compression ratio
        let text_size = text.len();
        let optimal_cr = utils::utils::compression_ratio(text_size, oc.len());

        // Create compression ratio DataFrame
        let cr_df = df!(
            "m" => &[args.m],
            "a" => &[args.alpha],
            "Optimal compression" => &[optimal_cr]
        )
        .unwrap();

        println!("{}", cr_df);
    }

    Ok(())
}
