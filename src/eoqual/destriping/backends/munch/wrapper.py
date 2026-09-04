#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Münch et al. — destriping combiné ondelettes / FFT.

Appelle une copie vendored, non modifiée, de ``rmstripes/stripes.py``
(https://github.com/DHI-GRAS/rmstripes, MIT) — voir
``backends/munch/vendor/NOTICE.md`` pour la provenance exacte et la
raison du vendoring (packaging amont incompatible Python 3.12, pas un
problème de licence), et ``THIRD_PARTY_LICENSES.md`` pour l'entrée
correspondante dans l'audit des licences.

Référence :
    Münch, B., Trtik, P., Marone, F., Stampanoni, M. (2009). "Stripe and
    ring artifact removal with combined wavelet — Fourier filtering."
    Optics Express, 17(10), 8567-8591.
"""
from __future__ import annotations

import numpy as np

from .vendor.stripes import remove_stripes

__all__ = ["munch_destripe"]


def munch_destripe(
    image: np.ndarray,
    decomp_level: int = 6,
    wavelet: str = "db10",
    sigma: float = 10,
) -> np.ndarray:
    """
    Destripe une image par la méthode de Münch et al. (ondelettes + FFT).

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.
    decomp_level : int
        Niveau de décomposition en ondelettes. Par défaut ``6``.
    wavelet : str
        Ondelette utilisée (nom PyWavelets). Par défaut ``"db10"``.
    sigma : float
        Écart-type du filtre gaussien appliqué dans le domaine de Fourier
        à chaque sous-bande. Par défaut ``10``.

    Returns
    -------
    np.ndarray
        Image destripée, même forme que l'entrée.
    """
    return remove_stripes(image, decomp_level=decomp_level, wavelet=wavelet, sigma=sigma)
