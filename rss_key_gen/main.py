"""
Intelligent RSS-Based Secret Key Generation Over Noisy Channels
For Low Resource Devices — Main Pipeline
"""

from src.rss_reader import read_input_file, generate_sample_rss
from src.quantization import calculate_rssi_difference, mean_value_quantization
from src.reconciliation import get_discard_indexes, reconcile_keys
from src.privacy_amplification import privacy_amplification
from src.file_io import write_csv, read_csv, ensure_dirs
from src.visualizer import plot_pipeline
import config

def run_pipeline(filename: str = None, use_sample: bool = False):
    print("\n" + "="*60)
    print("  RSS-BASED SECRET KEY GENERATION  (MVQ Pipeline)")
    print("="*60)

    # ── Step 1: Load or generate RSS values ─────────────────────
    print("\n[1/5] Loading RSS measurements...")
    if use_sample or filename is None:
        alice_rss, bob_rss = generate_sample_rss(config.NUM_SAMPLES, config.NOISE_LEVEL)
        print(f"      Generated {len(alice_rss)} synthetic RSS samples (noise={config.NOISE_LEVEL} dBm)")
    else:
        alice_rss = read_input_file(config.DATASET_DIR, filename)
        bob_rss   = read_input_file(config.DATASET_DIR, filename)  # same file; diff nodes in real HW
        print(f"      Loaded {len(alice_rss)} RSS values from '{filename}'")

    # ── Step 2: RSSI differencing ────────────────────────────────
    print("\n[2/5] Computing RSSI differences (m={})...".format(config.M))
    alice_diff = calculate_rssi_difference(alice_rss, config.M)
    bob_diff   = calculate_rssi_difference(bob_rss,   config.M)

    # ── Step 3: Mean Value Quantization ─────────────────────────
    print("\n[3/5] Applying Mean Value Quantization (alpha={})...".format(config.ALPHA))
    alice_bits, stats     = mean_value_quantization(alice_diff, config.ALPHA)
    bob_bits,   bob_stats = mean_value_quantization(bob_diff,   config.ALPHA)

    print(f"      Alice — Mean={stats['mean']:.4f}  Std={stats['std']:.4f}")
    print(f"      Alice — Upper={stats['upper']:.4f}  Lower={stats['lower']:.4f}")
    print(f"      Bob   — Mean={bob_stats['mean']:.4f}  Std={bob_stats['std']:.4f}")
    print(f"      Bob   — Upper={bob_stats['upper']:.4f}  Lower={bob_stats['lower']:.4f}")

    write_csv(alice_bits, config.BIT_SEQ_DIR, f"alice_bits_{config.FILENAME_TAG}.csv")
    write_csv(bob_bits,   config.BIT_SEQ_DIR, f"bob_bits_{config.FILENAME_TAG}.csv")

    # ── Step 4: Information Reconciliation ──────────────────────
    print("\n[4/5] Performing information reconciliation...")
    alice_discard = get_discard_indexes(alice_bits)
    bob_discard   = get_discard_indexes(bob_bits)
    write_csv(alice_discard, config.DISCARD_DIR, f"discard_alice_{config.FILENAME_TAG}.csv")
    write_csv(bob_discard,   config.DISCARD_DIR, f"discard_bob_{config.FILENAME_TAG}.csv")

    alice_key, bob_key, report = reconcile_keys(alice_bits, bob_bits,
                                                 alice_discard, bob_discard)
    print(f"      Key length          : {report['key_length']} bits")
    print(f"      Guard discards      : {report['n_guard_discarded']}")
    print(f"      Mismatch discards   : {report['n_mismatch_discarded']}")
    print(f"      Total discard rate  : {report['discard_rate']*100:.2f}%")
    print(f"      Mismatch rate       : {report['mismatch_rate']*100:.2f}%")

    write_csv(alice_key, config.KEYS_DIR, f"reconciled_alice_{config.FILENAME_TAG}.csv")
    write_csv(bob_key,   config.KEYS_DIR, f"reconciled_bob_{config.FILENAME_TAG}.csv")

    # ── Step 5: Privacy Amplification ───────────────────────────
    print("\n[5/5] Applying privacy amplification (SHA-256)...")
    final_key_alice = privacy_amplification(alice_key)
    final_key_bob   = privacy_amplification(bob_key)

    from datetime import datetime
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(f"{config.KEYS_DIR}/final_key_{config.FILENAME_TAG}.txt", "w") as f:
        f.write(f"Run   : {run_time}\n")
        f.write(f"Alice : {final_key_alice}\n")
        f.write(f"Bob   : {final_key_bob}\n")
        f.write(f"Match : {final_key_alice == final_key_bob}\n")

    print(f"      Run time        : {run_time}")
    print(f"      Alice final key : {final_key_alice}")
    print(f"      Bob   final key : {final_key_bob}")
    print(f"      Keys match      : {final_key_alice == final_key_bob}")

    # ── Visualisation ────────────────────────────────────────────
    print("\nGenerating pipeline visualisation...")
    plot_pipeline(alice_rss, bob_rss, alice_diff, alice_bits, bob_bits,
                  alice_key, stats, bob_stats, config.FILENAME_TAG)

    print("\n" + "="*60)
    print("  Pipeline complete. Results saved to 'results/'")
    print("="*60 + "\n")

    return {
        "final_key_alice": final_key_alice,
        "final_key_bob":   final_key_bob,
        "match":           final_key_alice == final_key_bob,
        "stats":           stats,
        "report":          report,
    }


if __name__ == "__main__":
    ensure_dirs([config.BIT_SEQ_DIR, config.DISCARD_DIR, config.KEYS_DIR])
    run_pipeline(use_sample=True)
