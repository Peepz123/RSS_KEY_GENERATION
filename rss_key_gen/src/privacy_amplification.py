"""
src/privacy_amplification.py — Privacy amplification via SHA-256 hashing
"""

import hashlib
from typing import List


def privacy_amplification(key_bits: List[int], output_bits: int = 256) -> str:
    """
    Apply privacy amplification to a reconciled bit sequence.

    The bit list is converted to a binary string, hashed with SHA-256,
    and returned as a hex digest.  In a production system a universal
    hash family (e.g. Toeplitz matrix hashing) would be used; SHA-256
    is used here as a practical approximation.

    Args:
        key_bits    : reconciled key as a list of 0/1 integers
        output_bits : desired output length in bits (default 256)

    Returns:
        hex-encoded final key string
    """
    if not key_bits:
        return hashlib.sha256(b"empty").hexdigest()

    bit_string = "".join(str(b) for b in key_bits)
    raw_bytes  = bit_string.encode("utf-8")
    digest     = hashlib.sha256(raw_bytes).hexdigest()

    # Truncate to requested bit length (each hex char = 4 bits)
    hex_chars = output_bits // 4
    return digest[:hex_chars]


def compute_entropy(key_bits: List[int]) -> float:
    """
    Compute the empirical Shannon entropy (bits per bit) of the key.

    Args:
        key_bits : list of 0/1 integers

    Returns:
        entropy in bits per symbol (0.0 – 1.0)
    """
    import math
    n = len(key_bits)
    if n == 0:
        return 0.0
    p1 = sum(key_bits) / n
    p0 = 1.0 - p1
    h = 0.0
    if p1 > 0:
        h -= p1 * math.log2(p1)
    if p0 > 0:
        h -= p0 * math.log2(p0)
    return round(h, 6)


def compute_randomness_metrics(key_bits: List[int]) -> dict:
    """Return a dictionary of basic randomness quality metrics."""
    n = len(key_bits)
    if n == 0:
        return {}

    ones   = sum(key_bits)
    zeros  = n - ones
    runs   = 1 + sum(1 for i in range(1, n) if key_bits[i] != key_bits[i - 1])
    entropy = compute_entropy(key_bits)

    return {
        "key_length":    n,
        "ones":          ones,
        "zeros":         zeros,
        "bit_balance":   round(ones / n, 4),
        "run_count":     runs,
        "entropy_bpb":   entropy,
        "total_entropy": round(entropy * n, 2),
    }
