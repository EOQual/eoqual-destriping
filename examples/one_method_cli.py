#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation (CLI) — applique une méthode de destriping sur une
image. Script de démonstration, PAS un test automatisé (voir
REFERENCE_TECHNIQUE.md §5).

Usage
-----
    PYTHONPATH=src python examples/one_method_cli.py \\
        --image tests/images/MODIS_noisy.tif --method rogass

    # Méthode nécessitant un extra (pip install "eoqual-destriping[deep]") :
    PYTHONPATH=src python examples/one_method_cli.py \\
        --image tests/images/MODIS_noisy.tif --method guan
"""
__author__  = "Olivier Amram"
__version__ = "20260904"
__status__  = "Development"

# ── Imports standard ──────────────────────────────────────────────────────────
import sys
import os
import argparse

# ── Imports tiers ─────────────────────────────────────────────────────────────
import cv2
import matplotlib.pyplot as plt

# ── Imports eoqual.destriping ─────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from eoqual.destriping.runner import destripe, list_methods
from eoqual.destriping.config import METHODS_CONFIGS


# ── Programme principal ───────────────────────────────────────────────────────
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Destriping d'une image par une méthode nommée")
    parser.add_argument(
        "--method",
        choices=list(METHODS_CONFIGS.keys()),
        required=True,
        help="Méthode à appliquer — voir list_methods()",
    )
    parser.add_argument("--image", required=True, help="Image à destriper (chemin)")
    parser.add_argument("--no-plot", action="store_true", help="Désactiver l'affichage")
    args = parser.parse_args()

    list_methods()

    cfg = METHODS_CONFIGS[args.method]

    # IMREAD_UNCHANGED : les TIFF flottants (ex. tests/images/MODIS_noisy.tif)
    # ne sont pas décodables par OpenCV en IMREAD_GRAYSCALE ("32-bit samples").
    image = cv2.imread(args.image, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Image introuvable : {args.image}")
    if image.ndim > 2:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(f"Image shape : {image.shape}  dtype : {image.dtype}")

    # uvdm traite nativement des rayures horizontales
    input_image = image.T if cfg["orientation"] == "horizontal" else image

    try:
        result = destripe(input_image, method=args.method)
    except ImportError as exc:
        print(f"Erreur : {exc}")
        sys.exit(1)

    if cfg["orientation"] == "horizontal":
        result = result.T

    print(f"\n{args.method} appliqué — sortie shape : {result.shape}\n")

    # ── Affichage ─────────────────────────────────────────────────────────────
    if not args.no_plot:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(image, cmap="gray")
        axes[0].set_title("Entrée")
        axes[1].imshow(result, cmap="gray")
        axes[1].set_title(f"Destripée — {args.method}")
        for ax in axes:
            ax.axis("off")
        plt.tight_layout()
        plt.show()

# EOF
