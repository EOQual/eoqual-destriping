#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lloyd & Bouali — destriping par filtre super-gaussien orienté dans le
domaine de Fourier, avec raffinement spatial optionnel.

Réimplémentation depuis les équations publiées (pas de code tiers repris) :

    Lloyd, S., Bouali, M. (2023). "Efficient destriping of remote sensing
    images using an oriented super-Gaussian filter." Applied Optics.
    Jeu de données associé : Mendeley Data,
    https://data.mendeley.com/ — voir ``tests/images/`` pour un extrait.

Principe : un filtre super-gaussien, orienté à 90° pour des rayures
verticales, atténue la bande spectrale étroite portée par la rayure dans
le domaine de Fourier. Un test de gradient déclenche ensuite un
raffinement spatial (estimation de la rayure résiduelle par colonne,
médiane robuste) quand l'image présente des contours marqués.

Licence : MIT (implémentation propre du projet).
"""
from __future__ import annotations

import cv2
import numpy as np

__all__ = ["lloyd_destripe"]


def _gradient_magnitude(image: np.ndarray) -> np.ndarray:
    return cv2.Laplacian(np.asarray(image, dtype=np.float32), cv2.CV_32FC1)


def _oriented_super_gaussian(x_mesh, y_mesh, width_x, width_y, power_x, power_y, angle_deg):
    theta = np.deg2rad(angle_deg)
    x_rot = x_mesh * np.cos(theta) - y_mesh * np.sin(theta)
    y_rot = x_mesh * np.sin(theta) + y_mesh * np.cos(theta)
    y_rot = np.fft.fftshift(y_rot, axes=1)

    band = np.exp(-np.abs(x_rot / width_x) ** power_x - np.abs(y_rot / width_y) ** power_y)
    return 1 - band  # notch (atténuation), pas passe-bande


def _apply_super_gaussian_filter(image: np.ndarray, sg_width: float, sg_power: float) -> np.ndarray:
    n_rows, n_cols = image.shape
    x = np.linspace(-n_cols / 2 - 1, n_cols / 2, n_cols)
    y = np.linspace(-n_rows / 2 - 1, n_rows / 2, n_rows)
    x_mesh, y_mesh = np.meshgrid(x, y)

    # 90° : bande orientée pour des rayures verticales dans l'image spatiale
    notch = _oriented_super_gaussian(x_mesh, y_mesh, n_cols / 200, sg_width, 2, sg_power, 90)

    spectrum = np.fft.fftshift(np.fft.fft2(image))
    spectrum_filtered = np.fft.ifftshift(spectrum * notch)
    filtered = np.abs(np.fft.ifft2(spectrum_filtered))

    # Correction de puissance (théorème de Parseval) — le filtrage réduit
    # légèrement l'énergie totale de l'image.
    filtered *= np.sum(image) / np.sum(filtered)
    return filtered


def _refine_with_column_estimate(striped: np.ndarray, filtered: np.ndarray) -> np.ndarray:
    stripe_estimate = striped - filtered
    n_rows, n_cols = stripe_estimate.shape

    column_offsets = np.zeros(n_cols)
    for col in range(n_cols):
        values = stripe_estimate[:, col]
        values = values[striped[:, col] > 0]
        column_offsets[col] = np.median(values) if np.sum(np.abs(values)) > 0 else 0.0

    # Exclusion des colonnes aberrantes (> 4 sigma)
    outliers = np.abs(column_offsets - np.mean(column_offsets)) > 4 * np.std(column_offsets)
    column_offsets[outliers] = 0.0

    stripe_matrix = np.outer(np.ones(n_rows), column_offsets)
    return striped - stripe_matrix


def lloyd_destripe(image: np.ndarray, width: float = 4.0, power: float = 2.0) -> np.ndarray:
    """
    Destripe une image à rayures verticales par filtre super-gaussien
    orienté (Lloyd & Bouali).

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.
    width : float
        Largeur du filtre le long de la bande spectrale (contrôle
        l'agressivité du filtrage). Par défaut ``4.0``.
    power : float
        Puissance super-gaussienne le long de la bande (raideur du
        filtre). Par défaut ``2.0``.

    Returns
    -------
    np.ndarray
        Image destripée, même forme que l'entrée.

    Notes
    -----
    Un test de gradient (``cv2.Laplacian``) décide si un raffinement
    spatial est appliqué après le filtrage fréquentiel — sur une image
    peu contrastée, le filtrage fréquentiel seul suffit.
    """
    image = np.asarray(image, dtype=np.float64)
    filtered = _apply_super_gaussian_filter(image, width, power)

    normalized = np.asarray(image / np.mean(image), dtype=np.float32)
    if np.amax(_gradient_magnitude(normalized)) > 0.1:
        return _refine_with_column_estimate(image, filtered)
    return filtered
