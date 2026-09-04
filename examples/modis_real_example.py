#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation — applique les méthodes du socle sur une image
MODIS réelle striée (`tests/images/MODIS_noisy.tif`) et mesure le RMSE
contre la référence connue (`tests/images/MODIS_ref.tif`, CC BY 4.0 —
voir `tests/images/NOTICE.md`). Contrairement à
`examples/all_methods_overview.py` (rayures synthétiques sur une image
sans vérité terrain), cet exemple dispose d'une vraie référence : le
RMSE avant/après est un indicateur quantitatif, pas seulement visuel.
Script de démonstration, PAS un test automatisé (voir
REFERENCE_TECHNIQUE.md §5).

Usage
-----
    PYTHONPATH=src python examples/modis_real_example.py
"""
__author__  = "Olivier Amram"
__version__ = "20260904"
__status__  = "Development"

# ── Imports standard ──────────────────────────────────────────────────────────
import sys
import os

# ── Imports tiers ─────────────────────────────────────────────────────────────
import cv2
import numpy as np
from rich.console import Console
from rich.table import Table

# ── Imports eoqual.destriping ─────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import eoqual.destriping as d
from eoqual.destriping.config import METHODS_CONFIGS

HERE = os.path.dirname(__file__)
NOISY_PATH = os.path.join(HERE, "..", "tests", "images", "MODIS_noisy.tif")
REF_PATH = os.path.join(HERE, "..", "tests", "images", "MODIS_ref.tif")


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)))


# ── Programme principal ───────────────────────────────────────────────────────
if __name__ == "__main__":

    # IMREAD_UNCHANGED : TIFF flottants, non décodables en IMREAD_GRAYSCALE
    noisy = cv2.imread(NOISY_PATH, cv2.IMREAD_UNCHANGED)
    ref = cv2.imread(REF_PATH, cv2.IMREAD_UNCHANGED)
    if noisy is None or ref is None:
        raise FileNotFoundError(f"Images introuvables : {NOISY_PATH} / {REF_PATH}")
    print(f"Image shape : {noisy.shape}  dtype : {noisy.dtype}")

    rmse_before = rmse(noisy, ref)

    console = Console()
    table = Table(
        title="eoqual-destriping — MODIS réel vs. référence (RMSE)",
        header_style="bold magenta",
    )
    table.add_column("Méthode", style="bold cyan")
    table.add_column("RMSE avant", justify="right")
    table.add_column("RMSE après", justify="right")
    table.add_column("Amélioration", justify="right")

    socle_methods = [name for name, cfg in METHODS_CONFIGS.items() if cfg["extra"] is None]
    for name in socle_methods:
        cfg = METHODS_CONFIGS[name]
        # auto_egal/uvdm traitent nativement des rayures horizontales
        input_image = noisy.T if cfg["orientation"] == "horizontal" else noisy

        try:
            result = d.destripe(input_image, method=name)
        except ImportError as exc:
            table.add_row(name, "—", "—", f"[yellow]ignoré : {exc}[/yellow]")
            continue

        if cfg["orientation"] == "horizontal":
            result = result.T

        rmse_after = rmse(result, ref)
        improvement = (rmse_before - rmse_after) / rmse_before * 100
        table.add_row(name, f"{rmse_before:.3f}", f"{rmse_after:.3f}", f"{improvement:+.1f}%")

    console.print(table)

# EOF
