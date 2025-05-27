import struct
import polars as pl


def digit_sum(num: str) -> int:
    result = 0
    for i in str(num):
        result += int(i)
    return result


def lz77_compress(text: str, window_size: int):
    i = 0  # Current position
    result = []  # List to store the output tuples
    step = 1  # Step counter for display

    while i < len(text):
        best_match_distance = 0  # Offset for the best match
        best_match_length = 0  # Length of the best match
        start_window = max(0, i - window_size)  # Define search window

        # Print current state: index, search window, and lookahead buffer
        print(f"Step {step}:")
        print(f"  Current index (i): {i}")
        print(f"  Search Window: '{text[start_window:i]}'")
        print(f"  Lookahead Buffer: '{text[i : min(i + window_size, len(text))]}'")

        # Search for the longest match in the search window
        for j in range(start_window, i):
            length = 0
            while i + length < len(text):
                if j + length < i:
                    if text[j + length] == text[i + length]:
                        length += 1
                    else:
                        break
                else:
                    offset = i - j  # Effective fragment length
                    if text[j + (length % offset)] == text[i + length]:
                        length += 1
                    else:
                        break

            if length > best_match_length:
                best_match_length = length
                best_match_distance = i - j

        if best_match_length > 0:
            next_char = (
                text[i + best_match_length]
                if (i + best_match_length) < len(text)
                else ""
            )
            print(
                f"  Match found: Distance = {best_match_distance}, Length = {best_match_length}, Next Char = '{next_char}'"
            )
            result.append((best_match_distance, best_match_length, next_char))
            i += best_match_length + 1
        else:
            print(f"  No match. Output literal: '{text[i]}'")
            result.append((0, 0, text[i]))
            i += 1

        print("-" * 50)
        step += 1

    return result


def pack_compressed_data(compressed):
    packed = bytearray()
    for offset, length, ch in compressed:
        # Encode the next character as ASCII (or a zero byte if missing)
        byte_ch = ch.encode("ascii") if ch else b"\x00"
        packed.extend(struct.pack("HHc", offset, length, byte_ch))
    return bytes(packed)


def main():
    text = "abracadabraabracadabraabracadabraabracadabra"
    window_size = digit_sum("2077518")  # Compute window size from digit sum

    print("Input string:", text)
    print("=" * 50)
    compressed = lz77_compress(text, window_size)

    # Create a Polars DataFrame from the compression tuples
    df = pl.DataFrame(
        {
            "Offset": [tpl[0] for tpl in compressed],
            "Length": [tpl[1] for tpl in compressed],
            "Char": [tpl[2] for tpl in compressed],
        }
    )

    print("\nCompression result (Polars DataFrame):")
    print(df)

    # Calculate the "real" sizes:
    # Original size: the UTF-8 encoded text size in bytes.
    original_bytes = text.encode("utf-8")
    original_size = len(original_bytes)

    # Compressed size: pack the compression tuples into a binary string.
    packed_compressed = pack_compressed_data(compressed)
    compressed_size = len(packed_compressed)

    print(
        "\nReal memory size of original data (serialized): {} bytes".format(
            original_size
        )
    )
    print(
        "Real memory size of compressed data (packed binary): {} bytes".format(
            compressed_size
        )
    )

    # Compression ratio (as a percentage of the original size)
    ratio = (compressed_size / original_size) * 100
    print("Compression ratio: {:.2f}%".format(ratio))


if __name__ == "__main__":
    main()
