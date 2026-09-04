#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Münch et al. — destriping combiné ondelettes / FFT (wrapper).

Fine couche autour du paquet tiers ``rmstripes`` :
https://github.com/DHI-GRAS/rmstripes (MIT) — voir ``THIRD_PARTY_LICENSES.md``.

Référence :
    Münch, B., Trtik, P., Marone, F., Stampanoni, M. (2009). "Stripe and
    ring artifact removal with combined wavelet — Fourier filtering."
    Optics Express, 17(10), 8567-8591.
"""
from __future__ import annotations

import numpy as np

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

    Raises
    ------
    ImportError
        Si ``rmstripes`` n'est pas installé — voir
        ``pip install "eoqual-destriping"`` (dépendance du socle) ou
        ``pip install rmstripes`` directement.
    """
    try:
        from rmstripes.stripes import remove_stripes
    except ImportError as exc:
        raise ImportError(
            "munch_destripe nécessite le paquet 'rmstripes' "
            "(https://github.com/DHI-GRAS/rmstripes, MIT). "
            "Installer avec : pip install "
            "'rmstripes @ git+https://github.com/DHI-GRAS/rmstripes.git'"
        ) from exc

    return remove_stripes(image, decomp_level=decomp_level, wavelet=wavelet, sigma=sigma)
