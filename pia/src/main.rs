use std::collections::HashMap;

fn sort_and_order_frequencies(text: &str) -> Vec<(char, i32)> {
    let filtered_text: String = text
        .chars()
        .filter(|c| !c.is_whitespace())
        .flat_map(|c| c.to_lowercase())
        .collect();

    let mut frequency = HashMap::new();
    for c in filtered_text.chars() {
        *frequency.entry(c).or_insert(0) += 1;
    }

    let mut sorted: Vec<(char, i32)> = frequency.into_iter().collect();
    sorted.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));

    sorted
}

fn calculate_fi(frequencies: &[(char, u16)]) -> (u16, Vec<f64>) {
    let total: u16 = frequencies.iter().map(|(_, freq)| freq).sum();
    let fi: Vec<f64> = frequencies
        .iter()
        .map(|(_, freq)| *freq as f64 / total as f64)
        .collect();

    (total, fi)
}

fn generate_tree(frequencies: &[(char, i32)]) -> HashMap<String, (String, String)> {
    let total: i32 = frequencies.iter().map(|(_, count)| count).sum();
    let mut encoding: Vec<(String, f64)> = frequencies
        .iter()
        .map(|(char, count)| (char.to_string(), *count as f64 / total as f64))
        .collect();

    encoding.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap().then(a.0.cmp(&b.0)));

    let mut tree = HashMap::new();

    for i in 0..encoding.len() - 1 {
        let last = encoding.pop().unwrap();
        let penultimate = encoding.pop().unwrap();
        let new_node = format!("o{}", i + 1);
        let new_prob = last.1 + penultimate.1;
        encoding.push((new_node.clone(), new_prob));

        // Re-sort
        encoding.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap().then(a.0.cmp(&b.0)));

        tree.insert(new_node, (penultimate.0, last.0));
    }

    if encoding.len() == 2 {
        tree.insert(
            "origin".to_string(),
            (encoding[0].0.clone(), encoding[1].0.clone()),
        );
    }

    tree.into_iter().rev().collect()
}

fn main() {
    let text = "aaaabbaaaabbbbbbaabcabbccabbaaaaabbccaaaaa";
    let frequencies = sort_and_order_frequencies(text);
    println!("{:?}", &frequencies);
}
