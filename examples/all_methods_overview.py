#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation — applique toutes les méthodes du socle sur une
image synthétique à rayures verticales connues, et affiche le résultat.
Script de démonstration, PAS un test automatisé (voir
REFERENCE_TECHNIQUE.md §5, tests/test_backends.py pour les smoke tests).

Usage
-----
    PYTHONPATH=src python examples/all_methods_overview.py
"""
__author__  = "Olivier Amram"
__version__ = "20260904"
__status__  = "Development"

# ── Imports standard ──────────────────────────────────────────────────────────
import sys
import os
from time import time

# ── Imports tiers ─────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
from skimage import data  # type: ignore

# ── Imports eoqual.destriping ─────────────────────────────────────────────────
# Ajoute src/ au path pour exécution sans installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import eoqual.destriping as d
from eoqual.destriping.config import METHODS_CONFIGS


# ── Helpers ───────────────────────────────────────────────────────────────────
def add_vertical_stripes(image: np.ndarray, amplitude: float = 25.0, seed: int = 0) -> np.ndarray:
    """
    Ajoute des rayures verticales synthétiques (biais additif constant par
    colonne, tiré uniformément dans ``[-amplitude, amplitude]``).
    """
    rng = np.random.default_rng(seed)
    stripe_profile = rng.uniform(-amplitude, amplitude, size=image.shape[1])
    stripes = np.tile(stripe_profile, (image.shape[0], 1))
    return np.clip(image.astype(np.float64) + stripes, 0, 255)


# ── Programme principal ───────────────────────────────────────────────────────
if __name__ == "__main__":

    image = data.camera().astype(np.float64)  # (512, 512)
    noisy = add_vertical_stripes(image)
    print(f"Image shape : {image.shape}  dtype : {image.dtype}")

    # Méthodes du socle uniquement (extras deep/vsnr non appelés ici — voir
    # examples/one_method_cli.py pour un exemple avec --method guan/vsnr)
    socle_methods = [name for name, cfg in METHODS_CONFIGS.items() if cfg["extra"] is None]
    print(f"Méthodes du socle : {socle_methods}")

    results = {}
    for name in socle_methods:
        cfg = METHODS_CONFIGS[name]
        # uvdm traite nativement des rayures horizontales -> transposer
        input_image = noisy.T if cfg["orientation"] == "horizontal" else noisy

        t0 = time()
        try:
            result = d.destripe(input_image, method=name)
        except ImportError as exc:
            print(f"  [{name}] ignoré : {exc}")
            continue
        elapsed = time() - t0

        if cfg["orientation"] == "horizontal":
            result = result.T
        results[name] = result
        print(f"  [{name}] {elapsed:.2f}s")

    # ── Affichage ─────────────────────────────────────────────────────────────
    n_axes = 2 + len(results)
    fig, axes = plt.subplots(1, n_axes, figsize=(4 * n_axes, 4))
    axes[0].imshow(image, cmap="gray")
    axes[0].set_title("Référence")
    axes[1].imshow(noisy, cmap="gray")
    axes[1].set_title("Striée (synthétique)")
    for ax, (name, result) in zip(axes[2:], results.items()):
        ax.imshow(result, cmap="gray")
        ax.set_title(name)
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.show()

# EOF
