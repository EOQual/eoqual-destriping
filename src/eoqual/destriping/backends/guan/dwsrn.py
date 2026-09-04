#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guan et al. — destriping par réseau de neurones convolutif (DWSRN), sur
les coefficients d'ondelettes de l'image.

Poids pré-entraînés et architecture dérivés de :
https://github.com/jtguan/Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal
(Apache-2.0 — voir ``THIRD_PARTY_LICENSES.md`` et ``NOTICE.md`` dans ce
dossier).

Référence :
    Guan, J., Lai, R., Xiong, A. (2019). "Wavelet Deep Neural Network for
    Stripe Noise Removal." IEEE Access, 7, 44544-44554.

Extra requis : ``pip install "eoqual-destriping[deep]"`` (TensorFlow/Keras,
~lourd — non installé par défaut, voir ``README.md``).
"""
from __future__ import annotations

import os
import threading

import numpy as np

__all__ = ["guan_destripe"]

_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "weights", "weight.hdf5")

_model = None
_model_lock = threading.Lock()


def _build_model():
    """Construit l'architecture DWSRN (8 blocs Conv2D 64 filtres + résidu)."""
    from keras.models import Model
    from keras.layers import Input, Conv2D, Activation, Add

    inputs = Input(shape=(None, None, 4))
    x = Conv2D(filters=64, kernel_size=(3, 3), padding="same", kernel_initializer="he_normal", name="Conv-1")(inputs)
    x = Activation("relu")(x)
    for _ in range(8):
        x = Conv2D(filters=64, kernel_size=(3, 3), padding="same", kernel_initializer="he_normal")(x)
        x = Activation("relu")(x)
    residual = Conv2D(filters=4, kernel_size=(3, 3), padding="same", kernel_initializer="he_normal", name="residual")(x)
    output = Add(name="res")([inputs, residual])

    return Model(inputs=inputs, outputs=[output, residual], name="DWSRN")


def _get_model():
    """Charge le modèle et ses poids une seule fois (singleton paresseux)."""
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            try:
                model = _build_model()
            except ImportError as exc:
                raise ImportError(
                    "guan_destripe nécessite l'extra 'deep' (TensorFlow/Keras). "
                    "Installer avec : pip install \"eoqual-destriping[deep]\""
                ) from exc

            if not os.path.exists(_WEIGHTS_PATH):
                raise FileNotFoundError(
                    f"Poids DWSRN introuvables : {_WEIGHTS_PATH}. "
                    "Voir THIRD_PARTY_LICENSES.md pour leur provenance "
                    "(Apache-2.0, jtguan/Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal)."
                )
            model.load_weights(_WEIGHTS_PATH)
            _model = model

    return _model


def _minmax_normalize(array: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    return (array - min_val) / (max_val - min_val)


def _minmax_denormalize(array: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    return array * (max_val - min_val) + min_val


def guan_destripe(image: np.ndarray) -> np.ndarray:
    """
    Destripe une image à rayures verticales par le réseau DWSRN de Guan
    et al.

    Le modèle et ses poids ne sont chargés qu'au premier appel de cette
    fonction (pas à l'import du module).

    Parameters
    ----------
    image : np.ndarray
        Image 2D (niveaux de gris) à rayures verticales.

    Returns
    -------
    np.ndarray
        Image destripée, même forme et dynamique que l'entrée.

    Raises
    ------
    ImportError
        Si l'extra ``deep`` (TensorFlow/Keras) n'est pas installé.
    FileNotFoundError
        Si le fichier de poids ``weights/weight.hdf5`` est absent.
    """
    import pywt  # dépendance du socle (PyWavelets)

    model = _get_model()

    min_val, max_val = np.amin(image), np.amax(image)
    normalized = _minmax_normalize(np.asarray(image, dtype=np.float64), min_val, max_val)

    ll, (lh, hl, hh) = pywt.dwt2(normalized, "haar")
    stacked = np.stack((ll, lh, hl, hh), axis=2)

    prediction, _residual = model.predict(np.expand_dims(stacked, axis=0), verbose=0)

    coeffs_pred = prediction[0, :, :, 0], (lh, prediction[0, :, :, 2], hh)
    reconstructed = pywt.idwt2(coeffs_pred, "haar")
    reconstructed = np.clip(reconstructed, 0, 1)

    return _minmax_denormalize(reconstructed, min_val, max_val)
