"""
tests/test_pipeline.py — Unit tests for all pipeline modules
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.quantization import calculate_rssi_difference, mean_value_quantization
from src.reconciliation import get_discard_indexes, reconcile_keys
from src.privacy_amplification import privacy_amplification, compute_entropy, compute_randomness_metrics
from src.rss_reader import generate_sample_rss


# ── quantization tests ────────────────────────────────────────

class TestRssiDifference:
    def test_basic(self):
        rss = [1.0, 3.0, 2.0, 5.0]
        diff = calculate_rssi_difference(rss, m=1)
        assert diff == [-2.0, 1.0, -3.0]

    def test_length(self):
        rss = list(range(10))
        assert len(calculate_rssi_difference(rss, m=1)) == 9
        assert len(calculate_rssi_difference(rss, m=3)) == 7


class TestMVQ:
    def test_output_values(self):
        diff = [5.0, -5.0, 0.0]
        bits, stats = mean_value_quantization(diff, alpha=1.0)
        assert set(bits).issubset({0, 1, 2})

    def test_stats_keys(self):
        _, stats = mean_value_quantization([1.0, -1.0, 0.5], alpha=1.0)
        for key in ("mean", "std", "upper", "lower", "alpha"):
            assert key in stats

    def test_custom_mean_std(self):
        diff = [10.0, -10.0, 0.0]
        bits, _ = mean_value_quantization(diff, alpha=1.0, mean=0.0, std=5.0)
        assert bits[0] == 1    # 10 > 0 + 5
        assert bits[1] == 0    # -10 < 0 - 5
        assert bits[2] == 2    # 0 in guard zone


# ── reconciliation tests ──────────────────────────────────────

class TestReconciliation:
    def test_discard_indexes(self):
        bits = [0, 1, 2, 0, 2, 1]
        assert get_discard_indexes(bits) == [2, 4]

    def test_no_discards(self):
        assert get_discard_indexes([0, 1, 0, 1]) == []

    def test_reconcile_removes_discards(self):
        a = [0, 1, 2, 0]
        b = [0, 1, 2, 1]
        a_key, b_key, report = reconcile_keys(a, b, [2], [2])
        assert 2 not in a_key
        assert report["key_length"] == 2  # position 3 is also discarded (mismatch)

    def test_mismatch_rate(self):
        a = [1, 0, 1]
        b = [1, 1, 1]
        _, _, report = reconcile_keys(a, b, [], [])
        assert report["n_mismatch_discarded"] == 1
        assert report["mismatch_rate"] == 0.0


# ── privacy amplification tests ───────────────────────────────

class TestPrivacyAmplification:
    def test_returns_string(self):
        key = privacy_amplification([0, 1, 0, 1])
        assert isinstance(key, str)

    def test_deterministic(self):
        key1 = privacy_amplification([1, 0, 1, 1, 0])
        key2 = privacy_amplification([1, 0, 1, 1, 0])
        assert key1 == key2

    def test_different_inputs_differ(self):
        assert privacy_amplification([0, 0, 0]) != privacy_amplification([1, 1, 1])

    def test_entropy_balanced(self):
        bits = [0, 1] * 50
        h = compute_entropy(bits)
        assert abs(h - 1.0) < 1e-9

    def test_entropy_biased(self):
        bits = [1] * 100
        h = compute_entropy(bits)
        assert h == 0.0

    def test_metrics_keys(self):
        m = compute_randomness_metrics([0, 1, 0, 1, 1])
        for k in ("key_length", "ones", "zeros", "bit_balance", "entropy_bpb"):
            assert k in m


# ── rss generator tests ───────────────────────────────────────

class TestRSSGenerator:
    def test_length(self):
        a, b = generate_sample_rss(n=50)
        assert len(a) == 50 and len(b) == 50

    def test_rss_range(self):
        a, b = generate_sample_rss(n=200)
        assert all(-90 <= v <= -40 for v in a)
        assert all(-90 <= v <= -40 for v in b)

    def test_correlation(self):
        """Alice and Bob should be correlated (same channel base)."""
        a, b = generate_sample_rss(n=200, noise_std=0.1)
        diffs = [abs(ai - bi) for ai, bi in zip(a, b)]
        assert sum(diffs) / len(diffs) < 5.0  # mean deviation < 5 dBm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
