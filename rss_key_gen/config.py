"""
config.py — Global project settings
"""

# ── Quantization parameters ──────────────────────────────────
ALPHA = 1.0          # threshold multiplier (alpha * std)
M     = 1            # lag for RSSI differencing

# ── Simulation parameters ────────────────────────────────────
NUM_SAMPLES = 100    # number of RSS readings to generate
NOISE_LEVEL = 3.0    # channel noise std-dev (dBm) between Alice & Bob

# ── File paths ───────────────────────────────────────────────
DATASET_DIR  = "dataset-files"
RESULTS_DIR  = "results"
BIT_SEQ_DIR  = "results/Bit-Sequences"
DISCARD_DIR  = "results/discard"
KEYS_DIR     = "results/keys"

FILENAME_TAG = "simulation"   # used to name output files
