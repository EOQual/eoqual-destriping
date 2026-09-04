#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-égalisation — destriping par appariement des moments statistiques
(moyenne/écart-type) ligne à ligne.

Réimplémentation depuis la description de la technique (pas de code tiers
repris) :

    Moik, J.G. (1980). "Digital Processing of Remotely Sensed Images."
    NASA SP-341, p. 87.

Principe : chaque ligne de l'image est normalisée indépendamment
(moyenne nulle, écart-type unitaire), ce qui élimine les différences de
gain/offset ligne à ligne typiques d'un capteur à balayage (whiskbroom) —
la rayure apparaît alors comme une bande **horizontale**. Le résultat est
ensuite recalé sur la dynamique radiométrique d'origine, soit celle de
l'image entière, soit celle d'une ligne de référence donnée (``target_row``).

Licence : MIT (implémentation propre du projet).
"""
from __future__ import annotations

from typing import Optional

import numpy as np

__all__ = ["auto_egal_destripe"]


def auto_egal_destripe(image: np.ndarray, target_row: Optional[int] = None) -> np.ndarray:
    """
    Destripe une image à rayures horizontales par appariement des moments
    statistiques (moyenne/écart-type) ligne à ligne.

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures horizontales.
    target_row : int, optional
        Index de la ligne dont la moyenne/écart-type sert de référence
        radiométrique pour la sortie. Par défaut ``None`` : la sortie est
        recalée sur la moyenne/écart-type de l'image entière.

    Returns
    -------
    np.ndarray
        Image destripée, même forme que l'entrée.
    """
    image = np.asarray(image, dtype=np.float64)

    normalized = np.empty_like(image)
    for row in range(image.shape[0]):
        line = image[row, :]
        normalized[row, :] = (line - np.nanmean(line)) / np.nanstd(line)

    normalized = (normalized - np.nanmean(normalized)) / np.nanstd(normalized)

    if target_row is not None:
        reference = image[target_row, :]
        target_mean = np.nanmean(reference)
        target_std = np.nanstd(reference)
    else:
        target_mean = np.nanmean(image)
        target_std = np.nanstd(image)

    return normalized * target_std + target_mean
