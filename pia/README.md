# Huffman Coding CLI Tool

This command-line tool implements both **optimal** and **heuristic** Huffman coding for input text using weighted frequency estimation and customizable parameters. 
It processes the input, generates codewords, and computes compression metrics.

---

## 🚀 Usage

```bash
# With UV
uv run m_grams_huffman.py --file <path_to_text_file> [--heuristic] [--optimal] [--alpha <int>]
```

## Dependencies

- Typer
- Polars
- Matplotlib