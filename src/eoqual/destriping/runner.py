"""
Point d'entrée unique pour appeler n'importe quelle méthode de destriping
par son nom, et lister les méthodes disponibles.

Exemple
-------
>>> from eoqual.destriping.runner import destripe, list_methods
>>> list_methods()
>>> clean = destripe(noisy_image, method="rogass")
"""

from __future__ import annotations

import numpy as np
from rich.console import Console
from rich.table import Table

from .config import METHODS_CONFIGS

__all__ = ["destripe", "list_methods"]

# Import différé des fonctions publiques pour éviter tout import lourd
# (keras, pyvsnr...) au chargement de ce module — voir README.md.
_DISPATCH = {
    "auto_egal": "eoqual.destriping.backends.auto_egal.moment_matching:auto_egal_destripe",
    "rogass": "eoqual.destriping.backends.rogass.gradient:rogass_destripe",
    "pande_chhetri": "eoqual.destriping.backends.pande_chhetri.wavelet_freq:pande_chhetri_destripe",
    "lloyd": "eoqual.destriping.backends.lloyd.super_gaussian:lloyd_destripe",
    "munch": "eoqual.destriping.backends.munch.wrapper:munch_destripe",
    "swaney": "eoqual.destriping.backends.swaney.wrapper:pystripe_destripe",
    "uvdm": "eoqual.destriping.backends.uvdm.bouali:uvdm_destripe",
    "guan": "eoqual.destriping.backends.guan.dwsrn:guan_destripe",
    "vsnr": "eoqual.destriping.backends.vsnr.fehrenbach_weiss:vsnr_destripe",
}


def _resolve(method: str):
    module_path, func_name = _DISPATCH[method].split(":")
    module = __import__(module_path, fromlist=[func_name])
    return getattr(module, func_name)


def list_methods() -> None:
    """Affiche toutes les méthodes de destriping disponibles."""
    console = Console()
    table = Table(title="Méthodes disponibles dans eoqual.destriping", header_style="bold magenta")
    table.add_column("Méthode", style="bold cyan", no_wrap=True)
    table.add_column("Rayures", justify="center")
    table.add_column("Extra requis")
    table.add_column("Licence amont")
    table.add_column("Référence")

    for name, cfg in METHODS_CONFIGS.items():
        extra = cfg["extra"] or "—"
        table.add_row(name, cfg["orientation"], extra, cfg["license"], cfg["reference"])

    console.print(table)


def destripe(image: np.ndarray, method: str, **kwargs) -> np.ndarray:
    """
    Applique une méthode de destriping par son nom.

    Parameters
    ----------
    image : np.ndarray
        Image 2D à destriper.
    method : str
        Nom de la méthode — une des clés de :data:`METHODS_CONFIGS`
        (voir :func:`list_methods`).
    **kwargs
        Transmis à l'implémentation choisie (voir sa docstring).

    Returns
    -------
    np.ndarray
        Image destripée.

    Raises
    ------
    ValueError
        Si ``method`` n'est pas une méthode connue.
    ImportError
        Si la méthode nécessite un extra non installé (``deep``, ``vsnr``)
        — le message précise quoi installer.
    """
    if method not in METHODS_CONFIGS:
        raise ValueError(
            f"Méthode '{method}' inconnue. Méthodes disponibles : "
            f"{list(METHODS_CONFIGS.keys())}"
        )

    func = _resolve(method)
    result = func(image, **kwargs)
    # uvdm_destripe renvoie (image, energy) — on ne garde que l'image ici
    return result[0] if isinstance(result, tuple) else result
