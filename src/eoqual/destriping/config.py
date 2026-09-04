"""
Registre central des méthodes de destriping disponibles dans
``eoqual.destriping``.

Chaque entrée décrit : l'orientation de rayure attendue par l'implémentation
(``"vertical"`` ou ``"horizontal"``), si la méthode fait partie du socle
d'installation (``extra=None``) ou nécessite un extra pip (``"deep"``,
``"vsnr"``), sa licence amont vérifiée, et une référence bibliographique.

Voir ``README.md`` (catalogue) et ``THIRD_PARTY_LICENSES.md`` (audit des
licences) pour le détail.
"""

from collections import OrderedDict

METHODS_CONFIGS: OrderedDict = OrderedDict(
    {
        "auto_egal": {
            "orientation": "horizontal",
            "extra": None,
            "license": "MIT",
            "reference": "Moik (1980), NASA SP-341, p. 87",
        },
        "rogass": {
            "orientation": "vertical",
            "extra": None,
            "license": "MIT",
            "reference": "Rogass et al. (2014), Remote Sensing 6(11), 11082-11106",
        },
        "pande_chhetri": {
            "orientation": "vertical",
            "extra": None,
            "license": "MIT",
            "reference": "Pande-Chhetri & Abd-Elrahman (2011), ISPRS J. Photogramm. 66(5), 620-636",
        },
        "lloyd": {
            "orientation": "vertical",
            "extra": None,
            "license": "MIT",
            "reference": "Lloyd & Bouali (2023), Applied Optics",
        },
        "munch": {
            "orientation": "vertical",
            "extra": None,
            "license": "MIT (rmstripes, DHI-GRAS — vendored)",
            "reference": "Münch et al. (2009), Optics Express 17(10), 8567-8591",
        },
        "swaney": {
            "orientation": "vertical",
            "extra": None,
            "license": "MIT (pystripe, LifeCanvas-Technologies — vendored)",
            "reference": "Swaney et al. (2019), bioRxiv 576595",
        },
        "uvdm": {
            "orientation": "horizontal",
            "extra": None,
            "license": "MIT",
            "reference": "Bouali & Ladjal (2011), IEEE TGRS 49(8), 2924-2935",
        },
        "guan": {
            "orientation": "vertical",
            "extra": "deep",
            "license": "Apache-2.0 (poids et architecture, jtguan)",
            "reference": "Guan, Lai & Xiong (2019), IEEE Access 7, 44544-44554",
        },
        "vsnr": {
            "orientation": "vertical",
            "extra": "vsnr",
            "license": "AGPL-3.0 (pyvsnr) — voir THIRD_PARTY_LICENSES.md",
            "reference": "Fehrenbach, Weiss & Lorenzo (2012), IEEE TIP 21(10), 4420-4430",
        },
    }
)
