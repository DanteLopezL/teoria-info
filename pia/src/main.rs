use polars::prelude::*;
use std::collections::HashMap;

fn frequency_estimation(text: &str, m: usize, alpha: i32) -> HashMap<String, i32> {
    let n = text.len();
    let mut df = HashMap::new();

    for i in 1..=m {
        for j in 0..=(n - i) {
            let s = &text[j..j + i];

            let count = df.entry(s.to_string()).or_insert(0);
            *count += (i as i32).pow(alpha as u32);
        }
    }

    df
}

fn main() {
    let text = "aaaaaaab";
    let m = 3;
    let alpha = 1;

    let frequencies = frequency_estimation(text, m, alpha);

    println!("Sequence Frequencies (weighted by i^α):");

    // Prepare data for DataFrame
    let mut keys = Vec::new();
    let mut values = Vec::new();

    for (k, v) in &frequencies {
        keys.push(k.clone());
        values.push(*v);
    }

    // Create DataFrame
    let df = df!(
        "keys" => keys,
        "values" => values
    )
    .unwrap();

    println!("{}", df);
}
