#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rogass et al. — destriping par filtrage du gradient horizontal.

Réimplémentation depuis les équations publiées (pas de code tiers repris) :

    Rogass, C., Mielke, C., Scheffler, D., Boesche, N.K., Lausch, A.,
    Lubitz, C., Brell, M., Spengler, D., Eisele, A., Segl, K., Guanter, L.
    (2014). "Reduction of Uncorrelated Striping Noise—Applications for
    Hyperspectral Pushbroom Acquisitions." Remote Sensing, 6(11), 11082-11106.

Principe : le gradient horizontal d'une image striée porte une composante
colonne-dépendante quasi constante le long des lignes (la rayure). On
l'estime par un filtre boxcar puis la médiane par colonne du gradient
(équation 6 de l'article), on la recentre (équation 7), puis on la
retranche à l'image d'origine.

Licence : MIT (implémentation propre du projet).
"""
from __future__ import annotations

import numpy as np
from scipy import signal

__all__ = ["rogass_destripe"]


def rogass_destripe(image: np.ndarray) -> np.ndarray:
    """
    Destripe une image à rayures verticales par la méthode de Rogass et al.

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.

    Returns
    -------
    np.ndarray
        Image destripée, même forme et dtype flottant que l'entrée.
    """
    image = np.asarray(image, dtype=np.float64)

    # Gradient horizontal (direction x, colonnes)
    grad_x = np.gradient(image, axis=1)

    # Filtre boxcar de longueur 3, colonne centrale valant 1/3 (normalisation)
    kernel = np.zeros((3, 3))
    kernel[1] = 1 / 3
    kernel = np.transpose(kernel)
    grad_x_smoothed = signal.convolve2d(grad_x, kernel, boundary="fill", mode="same")

    # Médiane par colonne (équation 6)
    stripe_profile = np.median(grad_x_smoothed, axis=0)
    ones_column = np.ones(image.shape[0])
    stripe_estimate = np.outer(ones_column, stripe_profile)

    # np.gradient décale d'un pixel : compensé ici (équivalent à circshift MATLAB)
    stripe_estimate = np.roll(stripe_estimate, 1, axis=1)

    # Recentrage (équation 7) — conserve la radiométrie moyenne de l'image
    stripe_estimate = stripe_estimate - np.mean(stripe_estimate)
    stripe_estimate = (
        stripe_estimate
        - np.mean(image)
        + np.mean(image - stripe_estimate + np.mean(stripe_estimate))
    )
    # Équation (8) — correction de lumière parasite / gradients basse
    # fréquence — volontairement omise (non pertinente hors contexte capteur
    # spécifique de l'article).

    return image - stripe_estimate
