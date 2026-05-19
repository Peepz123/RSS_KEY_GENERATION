"""
src/quantization.py — RSSI differencing and Mean Value Quantization (MVQ)
"""

import math
from typing import List, Dict, Tuple, Optional


def calculate_rssi_difference(rss_values: List[float], m: int = 1) -> List[float]:
    """
    Compute lagged differences:  diff[i] = rss[i] - rss[i+m]

    Args:
        rss_values : raw RSS readings
        m          : lag (default 1)

    Returns:
        list of length len(rss_values) - m
    """
    return [
        round(rss_values[i] - rss_values[i + m], 4)
        for i in range(len(rss_values) - m)
    ]


def mean_value_quantization(
    diff_values: List[float],
    alpha: float = 1.0,
    mean: Optional[float] = None,
    std:  Optional[float] = None,
) -> Tuple[List[int], Dict]:
    """
    Apply Mean Value Quantization to a list of RSSI differences.

    Decision rule
    -------------
    value > mean + alpha*std  →  1
    value < mean - alpha*std  →  0
    otherwise                 →  2  (discard / guard zone)

    Args:
        diff_values : RSSI difference array
        alpha       : threshold multiplier
        mean        : pre-computed mean  (if None, computed from diff_values)
        std         : pre-computed std   (if None, computed from diff_values)

    Returns:
        (bit_sequence, stats_dict)
    """
    if mean is None:
        mean = _mean(diff_values)
    if std is None:
        std = _std(diff_values, mean)

    upper = mean + alpha * std
    lower = mean - alpha * std

    bits: List[int] = []
    for v in diff_values:
        if v > upper:
            bits.append(1)
        elif v < lower:
            bits.append(0)
        else:
            bits.append(2)   # guard / discard zone

    stats = {
        "mean":  round(mean,  6),
        "std":   round(std,   6),
        "upper": round(upper, 6),
        "lower": round(lower, 6),
        "alpha": alpha,
        "n_ones":    bits.count(1),
        "n_zeros":   bits.count(0),
        "n_discard": bits.count(2),
    }
    return bits, stats


# ── helpers ──────────────────────────────────────────────────
def _mean(values: List[float]) -> float:
    return sum(values) / len(values)


def _std(values: List[float], mean: float) -> float:
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)
