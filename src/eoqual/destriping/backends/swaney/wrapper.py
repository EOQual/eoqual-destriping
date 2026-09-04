#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swaney et al. — destriping par filtre de streaks en ondelettes.

Appelle une copie vendored de ``pystripe/core.py`` (extrait
``wavedec``..``filter_streaks``, https://github.com/LifeCanvas-Technologies/pystripe,
MIT) — voir ``backends/swaney/vendor/NOTICE.md`` pour la provenance
exacte et la raison du vendoring (dépendances amont figées à des
versions incompatibles avec Python 3.12, pas un problème de licence), et
``THIRD_PARTY_LICENSES.md`` pour l'entrée correspondante dans l'audit des
licences.

Référence :
    Swaney, J., Kamentsky, L., Evans, N.B., Xie, K., Park, Y.G., Drummond,
    G., Chung, K. (2019). "Scalable image processing techniques for
    quantitative analysis of volumetric biological images from
    light-sheet microscopy." bioRxiv 576595.

Note : cet algorithme cible des images de microscopie (SPIM) à rayures
**horizontales** et une dynamique 12 bits ; ce wrapper transpose l'image
(rayures verticales -> horizontales) et re-normalise la dynamique
avant/après l'appel.
"""
from __future__ import annotations

import numpy as np

from .vendor.core import filter_streaks

__all__ = ["pystripe_destripe"]


def pystripe_destripe(
    image: np.ndarray,
    sigma1: float = 32,
    sigma2: float = 32,
    level: int | None = None,
) -> np.ndarray:
    """
    Destripe une image à rayures verticales par la méthode de Swaney et
    al.

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.
    sigma1 : float
        Bande passante (ondelette) le long de la direction de la rayure.
        Par défaut ``32``.
    sigma2 : float
        Bande passante perpendiculaire à la rayure. Par défaut ``32``.
    level : int, optional
        Niveau de décomposition en ondelettes. ``None`` (défaut) laisse
        l'algorithme choisir le niveau maximal pour la taille d'image.

    Returns
    -------
    np.ndarray
        Image destripée, même forme et dynamique que l'entrée.
    """
    image = np.asarray(image, dtype=np.float64)

    # Cible nativement des rayures horizontales et une dynamique ~12 bits
    transposed = np.transpose(image)
    scale = np.amax(transposed) / 2**12
    scaled = transposed / scale

    destriped = filter_streaks(scaled, sigma=[sigma1, sigma2], level=level, wavelet="db2")

    return np.transpose(destriped * scale)
