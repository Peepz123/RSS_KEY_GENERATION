# RSS-Based Secret Key Generation (MVQ Pipeline)

**B.Tech Project — Meenakshi Sundararajan Engineering College**  
Information Technology | Anna University | May 2024

---

## Project overview

Implements the full Physical Layer Secret Key Generation pipeline using
**Mean Value Quantization (MVQ)** on Received Signal Strength (RSS) measurements.

```
RSS samples → RSSI differencing → MVQ quantization
           → Information reconciliation → Privacy amplification → Secret key
```

---

## Quick start in VS Code

### 1. Clone / open the folder

```
File → Open Folder → select rss_key_gen/
```

### 2. Create a virtual environment

Open the **integrated terminal** (`Ctrl+\``) and run:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Select the interpreter in VS Code

`Ctrl+Shift+P` → **Python: Select Interpreter** → choose `.venv`

### 5. Run the pipeline

**Option A — Run & Debug panel** (`Ctrl+Shift+D`):
- Choose `Run Pipeline (sample data)` and press ▶

**Option B — Terminal**:
```bash
python main.py
```

Results are written to `results/`:
```
results/
├── Bit-Sequences/   # raw MVQ bit sequences (CSV)
├── discard/         # discard-index files (CSV)
├── keys/            # reconciled + final key files
└── simulation_pipeline.png   # 4-panel visualisation
```

---

## Using your own RSS data

Place a CSV file (single row of RSS values in dBm) in `dataset-files/` then
update `config.py`:

```python
FILENAME_TAG = "your_experiment_name"
```

And call from a terminal:

```python
from src.rss_reader import read_input_file
from main import run_pipeline
run_pipeline(filename="your_data.csv")
```

---

## Run the tests

```bash
# Integrated terminal
pytest tests/ -v
```

Or use the **Testing** tab in VS Code (beaker icon).

---

## Configuration (`config.py`)

| Parameter     | Default | Description                              |
|---------------|---------|------------------------------------------|
| `ALPHA`       | `1.0`   | MVQ threshold multiplier (α × σ)         |
| `M`           | `1`     | RSSI difference lag                      |
| `NUM_SAMPLES` | `100`   | Synthetic samples to generate            |
| `NOISE_LEVEL` | `3.0`   | Simulated channel noise (dBm std-dev)    |

---

## Project structure

```
rss_key_gen/
├── main.py               # Pipeline entry point
├── config.py             # Global parameters
├── requirements.txt      # Dependencies
├── dataset-files/        # Place real RSS CSV files here
├── results/              # Auto-created output directory
├── src/
│   ├── rss_reader.py         # CSV loader + synthetic generator
│   ├── quantization.py       # RSSI differencing + MVQ
│   ├── reconciliation.py     # Discard + error reconciliation
│   ├── privacy_amplification.py  # SHA-256 hashing + entropy metrics
│   ├── file_io.py            # CSV helpers
│   └── visualizer.py         # matplotlib 4-panel plot
├── tests/
│   └── test_pipeline.py      # pytest unit tests
└── .vscode/
    ├── launch.json           # Run/debug configurations
    └── settings.json         # Formatter + test runner settings
```

---

## References

1. Altun et al., "Scalable Secret Key Generation for Wireless Sensor Networks," *IEEE Systems Journal*, 2022.  
2. Rottenberg et al., "CSI-Based Versus RSS-Based Secret-Key Generation," *IEEE Trans. Communications*, 2021.  
3. Zeng, "Physical Layer Key Generation in Wireless Networks," *IEEE Communications Magazine*, 2015.
