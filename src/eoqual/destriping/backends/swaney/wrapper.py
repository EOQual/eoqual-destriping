#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swaney et al. — destriping par filtre de streaks en ondelettes (wrapper).

Fine couche autour du paquet tiers ``pystripe`` (MIT — voir
``THIRD_PARTY_LICENSES.md``) :
https://github.com/LifeCanvas-Technologies/pystripe (fork actif, PyPI),
historiquement https://github.com/chunglabmit/pystripe.

Référence :
    Swaney, J., Kamentsky, L., Evans, N.B., Xie, K., Park, Y.G., Drummond,
    G., Chung, K. (2019). "Scalable image processing techniques for
    quantitative analysis of volumetric biological images from
    light-sheet microscopy." bioRxiv 576595.

Note : ``pystripe`` cible des images de microscopie (SPIM) à rayures
**horizontales** et une dynamique 12 bits ; ce wrapper transpose l'image
(rayures verticales -> horizontales) et re-normalise la dynamique
avant/après l'appel.
"""
from __future__ import annotations

import numpy as np

__all__ = ["pystripe_destripe"]


def pystripe_destripe(
    image: np.ndarray,
    sigma1: float = 32,
    sigma2: float = 32,
    level: int | None = None,
) -> np.ndarray:
    """
    Destripe une image à rayures verticales par la méthode de Swaney et
    al. (paquet ``pystripe``).

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
        ``pystripe`` choisir le niveau maximal pour la taille d'image.

    Returns
    -------
    np.ndarray
        Image destripée, même forme et dynamique que l'entrée.

    Raises
    ------
    ImportError
        Si ``pystripe`` n'est pas installé — ``pip install pystripe``.
    """
    try:
        import pystripe
    except ImportError as exc:
        raise ImportError(
            "pystripe_destripe nécessite le paquet 'pystripe' "
            "(https://github.com/LifeCanvas-Technologies/pystripe, MIT). "
            "Installer avec : pip install pystripe"
        ) from exc

    image = np.asarray(image, dtype=np.float64)

    # pystripe attend des rayures horizontales et une dynamique ~12 bits
    transposed = np.transpose(image)
    scale = np.amax(transposed) / 2**12
    scaled = transposed / scale

    destriped = pystripe.filter_streaks(
        scaled, sigma=[sigma1, sigma2], level=level, wavelet="db2"
    )

    return np.transpose(destriped * scale)
