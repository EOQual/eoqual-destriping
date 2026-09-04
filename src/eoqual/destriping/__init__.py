"""
eoqual.destriping — Collection de méthodes de destriping d'images
d'observation de la Terre.

Public API : importer les méthodes directement depuis ce paquet.

Examples
--------
>>> import eoqual.destriping as d
>>> clean = d.rogass_destripe(noisy_image)
>>> clean = d.lloyd_destripe(noisy_image, width=4.0, power=2.0)

>>> from eoqual.destriping.runner import destripe, list_methods
>>> list_methods()
>>> clean = destripe(noisy_image, method="rogass")

Aucune méthode ne charge de dépendance lourde à l'import de ce paquet —
``guan_destripe`` (extra ``deep``, TensorFlow/Keras) et ``vsnr_destripe``
(extra ``vsnr``, AGPL-3.0) ne chargent leur backend qu'à l'appel. Voir
``README.md`` pour l'installation et ``THIRD_PARTY_LICENSES.md`` pour
l'audit des licences.
"""

__version__ = "0.1.0"
__title__ = "eoqual.destriping"
__description__ = "Collection of Earth observation image destriping methods"
__url__ = "https://github.com/EOQual/eoqual-destriping"
__uri__ = __url__
__doc__ = __description__ + " <" + __uri__ + ">"
__author__ = "Olivier Amram"
__email__ = "olivier.amram@free.fr"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026 Olivier Amram"

from .config import METHODS_CONFIGS  # noqa: F401

from .backends.auto_egal.moment_matching import auto_egal_destripe  # noqa: F401
from .backends.rogass.gradient import rogass_destripe  # noqa: F401
from .backends.pande_chhetri.wavelet_freq import pande_chhetri_destripe  # noqa: F401
from .backends.lloyd.super_gaussian import lloyd_destripe  # noqa: F401
from .backends.munch.wrapper import munch_destripe  # noqa: F401
from .backends.swaney.wrapper import pystripe_destripe  # noqa: F401
from .backends.uvdm.bouali import uvdm_destripe  # noqa: F401
from .backends.guan.dwsrn import guan_destripe  # noqa: F401
from .backends.vsnr.fehrenbach_weiss import vsnr_destripe  # noqa: F401

from .runner import destripe, list_methods  # noqa: F401

__all__ = [
    "METHODS_CONFIGS",
    "auto_egal_destripe",
    "rogass_destripe",
    "pande_chhetri_destripe",
    "lloyd_destripe",
    "munch_destripe",
    "pystripe_destripe",
    "uvdm_destripe",
    "guan_destripe",
    "vsnr_destripe",
    "destripe",
    "list_methods",
]
