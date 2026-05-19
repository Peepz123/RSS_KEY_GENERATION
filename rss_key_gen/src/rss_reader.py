"""
src/rss_reader.py — Load RSS measurements from CSV or generate synthetic data
"""

import csv
import random
import math
from typing import Tuple, List


def read_input_file(foldername: str, filename: str) -> List[float]:
    """Read a CSV file of RSS values and return them as a list of floats."""
    path = f"{foldername}/{filename}"
    values: List[float] = []
    print(f"      Reading: {path}")
    try:
        with open(path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    values.append(float(cell))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"File '{filename}' not found in '{foldername}'. "
            "Run with use_sample=True to use synthetic data instead."
        )
    return values


def generate_sample_rss(
    n: int = 100,
    noise_std: float = 3.0,
    base_rss: float = -65.0,
    walk_std: float = 2.0,
) -> Tuple[List[float], List[float]]:
    """
    Simulate correlated RSS readings for Alice and Bob.

    Both nodes observe the same underlying channel (random walk),
    but each adds independent Gaussian noise to model antenna
    placement differences and measurement error.

    Args:
        n         : number of samples
        noise_std : std-dev of per-node additive noise (dBm)
        base_rss  : starting RSS value (dBm)
        walk_std  : std-dev of the underlying channel random walk

    Returns:
        (alice_rss, bob_rss) — two correlated RSS lists of length n
    """
    channel: List[float] = []
    s = base_rss
    for _ in range(n):
        s += _randn() * walk_std
        s = max(-90.0, min(-40.0, s))   # clamp to realistic dBm range
        channel.append(round(s, 2))

    alice_rss = [round(max(-90.0, min(-40.0, v + _randn() * noise_std * 0.4)), 2) for v in channel]
    bob_rss   = [round(max(-90.0, min(-40.0, v + _randn() * noise_std * 0.6)), 2) for v in channel]

    return alice_rss, bob_rss


# ── helpers ──────────────────────────────────────────────────
def _randn() -> float:
    """Box–Muller standard normal sample."""
    u, v = 0.0, 0.0
    while u == 0:
        u = random.random()
    while v == 0:
        v = random.random()
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
