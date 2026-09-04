#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSNR — Variational Stationary Noise Remover (Fehrenbach, Weiss & Lorenzo).

Fine couche autour du paquet tiers ``pyvsnr`` — **AGPL-3.0**, voir
l'avertissement dans ``THIRD_PARTY_LICENSES.md``. N'est PAS installé par
défaut : ``pip install "eoqual-destriping[vsnr]"``.

Référence :
    Fehrenbach, J., Weiss, P., Lorenzo, C. (2012). "Variational Algorithms
    to Remove Stationary Noise: Applications to Microscopy Imaging." IEEE
    Transactions on Image Processing, 21(10), 4420-4430.
"""
from __future__ import annotations

import numpy as np

__all__ = ["vsnr_destripe"]


def vsnr_destripe(
    image: np.ndarray,
    alpha: float = 5e-2,
    maxit: int = 200,
    cvg_threshold: float = 1e-4,
) -> np.ndarray:
    """
    Destripe une image à rayures verticales par le modèle VSNR de
    Fehrenbach, Weiss & Lorenzo.

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.
    alpha : float
        Poids du filtre de Dirac orienté verticalement (intensité de la
        correction). Par défaut ``5e-2``.
    maxit : int
        Nombre maximal d'itérations. Par défaut ``200``.
    cvg_threshold : float
        Seuil de convergence. Par défaut ``1e-4``.

    Returns
    -------
    np.ndarray
        Image destripée, même forme que l'entrée.

    Raises
    ------
    ImportError
        Si ``pyvsnr`` n'est pas installé — voir l'avertissement de
        licence AGPL-3.0 dans ``THIRD_PARTY_LICENSES.md`` avant de
        l'installer : ``pip install "eoqual-destriping[vsnr]"``.
    """
    try:
        from pyvsnr import VSNR
    except ImportError as exc:
        raise ImportError(
            "vsnr_destripe nécessite le paquet 'pyvsnr' (PyPI), sous "
            "licence AGPL-3.0 — lire THIRD_PARTY_LICENSES.md avant "
            "installation. Installer avec : "
            "pip install \"eoqual-destriping[vsnr]\""
        ) from exc

    vsnr = VSNR(image.shape)
    vsnr.add_filter(alpha=alpha, name="dirac_v")
    vsnr.initialize()

    return vsnr.eval(image, maxit=maxit, cvg_threshold=cvg_threshold)
