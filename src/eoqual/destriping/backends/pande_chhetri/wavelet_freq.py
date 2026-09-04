#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pande-Chhetri & Abd-Elrahman — destriping par décomposition en ondelettes
et filtrage fréquentiel des sous-bandes horizontales.

Réimplémentation depuis les équations publiées (pas de code tiers repris) :

    Pande-Chhetri, R., Abd-Elrahman, A. (2011). "De-striping hyperspectral
    imagery using wavelet transform and adaptive frequency domain
    filtering." ISPRS Journal of Photogrammetry and Remote Sensing,
    66(5), 620-636.

Principe : décomposition en ondelettes discrètes (db4), puis pour chaque
niveau, filtrage de la sous-bande HL (détails horizontaux, porteuse de la
rayure verticale) : on identifie par colonne les échantillons aberrants
(> k écart-types de la moyenne), on recalcule la composante continue (DC)
de la FFT de la colonne à partir des seuls échantillons non-aberrants, et
on la réinjecte avant reconstruction.

Licence : MIT (implémentation propre du projet).
"""
from __future__ import annotations

import numpy as np
import pywt

__all__ = ["pande_chhetri_destripe"]


def _frequency_domain_filtering(hl_subband: np.ndarray, k: float) -> np.ndarray:
    """Filtre chaque colonne de la sous-bande HL dans le domaine fréquentiel."""
    filtered = np.zeros(hl_subband.shape)
    n_cols = hl_subband.shape[1]

    for i in range(n_cols):
        column = hl_subband[:, i]
        column_fft = np.fft.fft(column)

        mean_col = np.mean(column)
        std_col = np.std(column)

        # Échantillons non-aberrants (dans k écarts-types de la moyenne)
        inliers = column[np.abs(column - mean_col) < k * std_col]
        mean_inliers = np.mean(inliers)
        inliers_fft = np.fft.fft(inliers)

        dc_original = inliers_fft[0]
        dc_normalized = dc_original * (mean_col - mean_inliers) / mean_col

        column_fft[0] = dc_normalized
        filtered[:, i] = np.real(np.fft.ifft(column_fft))

    return filtered


def pande_chhetri_destripe(image: np.ndarray, level: int = 4, k: float = 2.5) -> np.ndarray:
    """
    Destripe une image à rayures verticales par la méthode de
    Pande-Chhetri & Abd-Elrahman.

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.
    level : int
        Niveau de décomposition en ondelettes (db4). Par défaut ``4``,
        comme dans l'article.
    k : float
        Seuil d'exclusion des échantillons aberrants, en écarts-types.
        Par défaut ``2.5``.

    Returns
    -------
    np.ndarray
        Image destripée, même forme que l'entrée.
    """
    image = np.asarray(image, dtype=np.float64)
    level = int(level)

    coeffs = pywt.wavedec2(image, wavelet="db4", level=level)
    coeffs_filtered = list(coeffs)
    for i in range(level):
        # coeffs[i + 1] = (LH, HL, HH) ; HL (index 1) porte les rayures verticales
        lh, hl, hh = coeffs[i + 1]
        coeffs_filtered[i + 1] = (lh, _frequency_domain_filtering(hl, k), hh)

    return pywt.waverec2(tuple(coeffs_filtered), "db4")
