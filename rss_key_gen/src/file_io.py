"""
src/file_io.py — CSV read/write helpers and directory management
"""

import csv
import os
from typing import List, Any


def ensure_dirs(dirs: List[str]) -> None:
    """Create directories (including parents) if they do not exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def write_csv(data: List[Any], foldername: str, filename: str) -> str:
    """
    Write a flat list to a single-row CSV file.

    Args:
        data       : list of values to write
        foldername : output directory (created if absent)
        filename   : output filename

    Returns:
        full path of the written file
    """
    os.makedirs(foldername, exist_ok=True)
    path = f"{foldername}/{filename}"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)
    return path


def read_csv(foldername: str, filename: str) -> List[float]:
    """
    Read a single-row CSV and return values as a list of floats.

    Args:
        foldername : directory containing the file
        filename   : filename to read

    Returns:
        list of float values
    """
    path = f"{foldername}/{filename}"
    values: List[float] = []
    try:
        with open(path, "r", newline="") as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                values.extend(row)
                break   # single-row files
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    return values


def read_int_csv(foldername: str, filename: str) -> List[int]:
    """Like read_csv but returns integers."""
    return [int(v) for v in read_csv(foldername, filename)]
