"""
src/visualizer.py — Pipeline visualisation using matplotlib
"""

from typing import List, Dict
import os


def plot_pipeline(
    alice_rss:  List[float],
    bob_rss:    List[float],
    diff_vals:  List[float],
    alice_bits: List[int],
    bob_bits:   List[int],
    final_key:  List[int],
    stats:      Dict,
    bob_stats:  Dict,
    tag:        str = "simulation",
) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("      [visualizer] matplotlib not installed — skipping plot.")
        return

    fig, axes = plt.subplots(4, 1, figsize=(12, 14))
    fig.suptitle("RSS-Based Secret Key Generation — MVQ Pipeline", fontsize=14, y=0.98)

    # Panel 1: RSS measurements
    ax = axes[0]
    ax.plot(alice_rss, label="Alice RSS", color="#185FA5", linewidth=1.2)
    ax.plot(bob_rss,   label="Bob RSS",   color="#3B6D11", linewidth=1.2, linestyle="--")
    ax.set_title("Step 1 — RSS Channel Measurements (dBm)", fontsize=11)
    ax.set_ylabel("RSS (dBm)"); ax.set_xlabel("Sample index")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

    # Panel 2: RSSI difference + both sets of thresholds
    ax = axes[1]
    x = list(range(len(diff_vals)))
    ax.plot(x, diff_vals, color="#534AB7", linewidth=1.0, label="ΔRSS (Alice)")
    ax.axhline(stats["upper"],     color="#993C1D", linestyle="--", linewidth=1.2, label=f"Alice upper ({stats['upper']:.2f})")
    ax.axhline(stats["lower"],     color="#185FA5", linestyle="--", linewidth=1.2, label=f"Alice lower ({stats['lower']:.2f})")
    ax.axhline(bob_stats["upper"], color="#cc6600", linestyle=":",  linewidth=1.0, label=f"Bob upper ({bob_stats['upper']:.2f})")
    ax.axhline(bob_stats["lower"], color="#006699", linestyle=":",  linewidth=1.0, label=f"Bob lower ({bob_stats['lower']:.2f})")
    ax.fill_between(x, stats["lower"], stats["upper"], alpha=0.07, color="gray", label="Alice guard zone")
    ax.set_title(f"Step 2/3 — RSSI Differencing & MVQ Thresholds (α={stats['alpha']})", fontsize=11)
    ax.set_ylabel("ΔRSS (dBm)"); ax.set_xlabel("Sample index")
    ax.legend(fontsize=7, ncol=3); ax.grid(True, alpha=0.3)

    # Panel 3: Bit sequences
    ax = axes[2]
    colors_map = {0: "#185FA5", 1: "#3B6D11", 2: "#993C1D"}
    for row_idx, (row, name) in enumerate([(alice_bits, "Alice"), (bob_bits, "Bob")]):
        y_base = 1 - row_idx * 1.4
        for col_idx, bit in enumerate(row):
            ax.barh(y_base, 1, left=col_idx, height=0.8,
                    color=colors_map[bit], alpha=0.85, linewidth=0)
    y_key = 1 - 2 * 1.4
    for col_idx, bit in enumerate(final_key):
        ax.barh(y_key, 1, left=col_idx, height=0.8, color=colors_map[bit], alpha=0.85, linewidth=0)
    ax.set_yticks([1, 1-1.4, 1-2.8])
    ax.set_yticklabels(["Alice bits", "Bob bits", "Final key"])
    ax.set_xlabel("Bit position")
    ax.set_title("Step 4 — Bit Sequences (blue=0, green=1, red=discard)", fontsize=11)
    ax.set_xlim(0, max(len(alice_bits), 1)); ax.grid(False)
    p0 = mpatches.Patch(color="#185FA5", label="0")
    p1 = mpatches.Patch(color="#3B6D11", label="1")
    p2 = mpatches.Patch(color="#993C1D", label="discard")
    ax.legend(handles=[p0, p1, p2], fontsize=8, loc="upper right")

    # Panel 4: Statistics
    ax = axes[3]
    labels = ["Alice 1s", "Alice 0s", "Guard disc.", "Mismatch disc.", "Key length", "Key 1s", "Key 0s"]
    key_ones  = sum(1 for b in final_key if b == 1)
    key_zeros = len(final_key) - key_ones
    values = [stats["n_ones"], stats["n_zeros"], stats["n_discard"],
              bob_stats["n_discard"], len(final_key), key_ones, key_zeros]
    bar_colors = ["#3B6D11","#185FA5","#993C1D","#cc6600","#534AB7","#3B6D11","#185FA5"]
    bars = ax.bar(labels, values, color=bar_colors, alpha=0.8, width=0.55)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.3, str(val),
                ha="center", va="bottom", fontsize=9)
    ax.set_title("Step 5 — Key Generation Statistics", fontsize=11)
    ax.set_ylabel("Count"); ax.tick_params(axis="x", labelsize=8); ax.grid(axis="y", alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs("results", exist_ok=True)
    out_path = f"results/{tag}_pipeline.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"      Plot saved → {out_path}")
