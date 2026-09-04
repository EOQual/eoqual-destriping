#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UVDM — Unidirectional Variational Destriping Model (Bouali & Ladjal).

Implémentation Python originale de l'algorithme décrit dans :

    Bouali, M., Ladjal, S. (2011). "Toward Optimal Destriping of MODIS
    Data Using a Unidirectional Variational Model." IEEE Transactions on
    Geoscience and Remote Sensing, 49(8), 2924-2935.

Licence : MIT (auteur du dépôt).

Attention : le modèle traite nativement des rayures **horizontales**
(direction ``theta`` = régularisation verticale) — transposer l'image en
entrée si les rayures sont verticales.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

__all__ = ["uvdm_destripe"]


def _gradient_x(array: np.ndarray) -> np.ndarray:
    """Gradient horizontal (colonnes)."""
    n_cols = array.shape[1]
    return array[:, 0 : n_cols - 1] - array[:, 1:n_cols]


def _gradient_y(array: np.ndarray) -> np.ndarray:
    """Gradient vertical (lignes)."""
    n_rows = array.shape[0]
    return array[0 : n_rows - 1, :] - array[1:n_rows, :]


def uvdm_destripe(
    striped_image: np.ndarray,
    n_iteration: int = 30,
    eps: float = 1.0,
    theta: float = 0.1,
    display: bool = False,
    verbose: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Destripe une image à rayures horizontales par le modèle variationnel
    unidirectionnel de Bouali & Ladjal (schéma de Gauss-Seidel).

    Parameters
    ----------
    striped_image : np.ndarray
        Image 2D à rayures horizontales.
    n_iteration : int
        Nombre d'itérations du schéma de Gauss-Seidel. Par défaut ``30``.
    eps : float
        Epsilon de régularisation (non-différentiabilité en 0 du modèle
        variationnel, TV-like). Pour des images 8 bits, valeur typique
        ``1``. Par défaut ``1.0``.
    theta : float
        Multiplicateur de Lagrange contrôlant le degré de régularisation.
        Pour des images 8 bits, valeur typique ``0.1``. Par défaut ``0.1``.
    display : bool
        Si ``True``, affiche en direct (matplotlib) l'image en cours de
        traitement et la rayure extraite — nécessite ``matplotlib``.
        Par défaut ``False``.
    verbose : bool
        Si ``True``, affiche à chaque itération l'Image Distortion (ID)
        et le Radiometric Improvement Factor (RIF). Par défaut ``False``.

    Returns
    -------
    destriped : np.ndarray
        Image destripée, même forme que l'entrée.
    energy : np.ndarray
        Valeur de la fonctionnelle d'énergie à chaque itération — permet
        de vérifier la convergence (doit décroître puis se stabiliser).

    Notes
    -----
    Les paramètres ``theta``, ``eps`` et ``n_iteration`` doivent être
    choisis de sorte que :

    - l'Image Distortion (ID) reste supérieure à 95 % ;
    - aucun artefact de flou n'apparaisse près des contours nets (survient
      si ``eps`` est trop grand) ;
    - la solution soit suffisamment proche du minimiseur de la
      fonctionnelle d'énergie (vérifier la convergence de ``energy``).
    """
    striped_image = np.asarray(striped_image, dtype=np.float64)
    n_rows, n_cols = striped_image.shape

    energy = np.empty(n_iteration)
    image_distortion = np.empty(n_iteration)
    radiometric_improvement = np.empty(n_iteration)

    solution = striped_image.copy()

    # Champ de gradient de l'image bruitée (référence pour l'ID)
    grad_x_ref = _gradient_x(striped_image)
    grad_y_ref = _gradient_y(striped_image)

    if display:
        import matplotlib.pyplot as plt  # import différé — extra visualisation

        plt.ion()
        _fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, sharey=True)
        ax1.imshow(striped_image)
        plt.show()

    for i in range(n_iteration):
        grad_x_sol = _gradient_x(solution)
        grad_y_sol = _gradient_y(solution)

        stripe_component = solution - striped_image

        ce = 1 / np.sqrt(
            (np.concatenate((stripe_component[:, 1:n_cols], stripe_component[:, n_cols - 1:n_cols]), axis=1) - stripe_component) ** 2 + eps
        )
        cw = 1 / np.sqrt(
            (stripe_component - np.concatenate((stripe_component[:, 0:1], stripe_component[:, 0 : n_cols - 1]), axis=1)) ** 2 + eps
        )
        cs = 1 / np.sqrt(
            (np.concatenate((solution[1:n_rows, :], solution[n_rows - 1:n_rows, :]), axis=0) - solution) ** 2 + eps
        )
        cn = 1 / np.sqrt(
            (solution - np.concatenate((solution[0:1, :], solution[0 : n_rows - 1, :]), axis=0)) ** 2 + eps
        )

        term_e = ce * (
            np.concatenate((solution[:, 1:n_cols], solution[:, n_cols - 1:n_cols]), axis=1)
            - np.concatenate((striped_image[:, 1:n_cols], striped_image[:, n_cols - 1:n_cols]), axis=1)
            + striped_image
        )
        term_w = cw * (
            np.concatenate((solution[:, 0:1], solution[:, 0 : n_cols - 1]), axis=1)
            - np.concatenate((striped_image[:, 0:1], striped_image[:, 0 : n_cols - 1]), axis=1)
            + striped_image
        )
        term_s = theta * cs * np.concatenate((solution[1:n_rows, :], solution[n_rows - 1:n_rows, :]), axis=0)
        term_n = theta * cn * np.concatenate((solution[0:1, :], solution[0 : n_rows - 1, :]), axis=0)

        denominator = ce + cw + theta * cs + theta * cn
        solution = (term_e + term_w + term_s + term_n) / denominator

        image_distortion[i] = 100 - (
            np.sum(np.abs(grad_x_ref - grad_x_sol)) * 100 / np.sum(np.abs(grad_x_ref))
        )
        radiometric_improvement[i] = (
            (np.sum(np.abs(grad_y_ref)) - np.sum(np.abs(grad_y_sol))) * 100 / np.sum(np.abs(grad_y_ref))
        )
        energy[i] = np.sum(np.sqrt((grad_x_sol - grad_x_ref) ** 2 + eps)) + theta * np.sum(
            np.sqrt(grad_y_sol**2 + eps)
        )

        if verbose and i > 0:
            print(
                f"Iteration: {i}   Image Distortion = {image_distortion[i]:.2f}   "
                f"Improvement Factor = {radiometric_improvement[i]:.2f}"
            )

        if display:
            ax2.imshow(solution)
            ax3.imshow(striped_image - solution)
            plt.pause(0.05)

    return solution, energy
