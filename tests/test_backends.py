#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke tests — pour chaque méthode, vérifie que l'appel sur une image
synthétique striée ne lève pas d'exception et renvoie une image de même
forme. Ce ne sont PAS des tests de qualité numérique (pas d'assertion sur
le niveau de résiduel de rayure) — voir REFERENCE_TECHNIQUE.md §5.

Les méthodes dont une dépendance (socle ou extra) n'est pas installée
sont marquées ``skip`` plutôt qu'échouées (``pytest.importorskip``).
"""
import numpy as np
import pytest

from eoqual.destriping.config import METHODS_CONFIGS
from eoqual.destriping.runner import destripe


@pytest.fixture
def striped_image() -> np.ndarray:
    """
    Image 128x128 synthétique avec rayures verticales additives connues.
    (128 évite les avertissements PyWavelets sur des niveaux de
    décomposition trop élevés pour la taille d'image — voir
    ``pande_chhetri_destripe``, ``level=4`` par défaut.)
    """
    rng = np.random.default_rng(0)
    base = rng.uniform(50, 200, size=(128, 128))
    stripe_profile = rng.uniform(-20, 20, size=128)
    return base + np.tile(stripe_profile, (128, 1))


@pytest.mark.parametrize("method", [m for m, cfg in METHODS_CONFIGS.items() if cfg["extra"] is None])
def test_socle_method_smoke(striped_image, method):
    """Chaque méthode du socle s'exécute et renvoie une image de même forme."""
    cfg = METHODS_CONFIGS[method]
    if method == "swaney":
        pytest.importorskip("pystripe")

    input_image = striped_image.T if cfg["orientation"] == "horizontal" else striped_image
    # munch (db10, decomp_level=6 par défaut) a besoin d'une image bien plus
    # grande que 128x128 pour ne pas avertir sur les effets de bord PyWavelets
    # — non représentatif d'un bug, juste de la taille du fixture de test.
    kwargs = {"decomp_level": 2} if method == "munch" else {}
    result = destripe(input_image, method=method, **kwargs)

    assert result.shape == input_image.shape
    assert np.all(np.isfinite(result))


def test_guan_smoke(striped_image):
    """Méthode 'guan' (extra 'deep') — skip si TensorFlow/Keras absent."""
    pytest.importorskip("keras")
    result = destripe(striped_image, method="guan")
    assert result.shape == striped_image.shape
    assert np.all(np.isfinite(result))


def test_vsnr_smoke(striped_image):
    """Méthode 'vsnr' (extra 'vsnr', AGPL-3.0) — skip si pyvsnr absent."""
    pytest.importorskip("pyvsnr")
    result = destripe(striped_image, method="vsnr")
    assert result.shape == striped_image.shape
    assert np.all(np.isfinite(result))


def test_unknown_method_raises(striped_image):
    with pytest.raises(ValueError):
        destripe(striped_image, method="not_a_real_method")


def test_list_methods_matches_registry():
    """Toutes les méthodes de METHODS_CONFIGS sont bien dispatchables."""
    from eoqual.destriping.runner import _DISPATCH

    assert set(METHODS_CONFIGS.keys()) == set(_DISPATCH.keys())
