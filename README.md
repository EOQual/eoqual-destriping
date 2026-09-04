<p align="center">
  <img src="resources/eoqual_rounded.png" alt="EOQual" width="280">
</p>

# eoqual-destriping

Collection de méthodes de destriping d'images, pensée pour l'observation
de la Terre — voir **[REFERENCE_TECHNIQUE.md](REFERENCE_TECHNIQUE.md)**
pour le détail de chaque méthode (principe, implémentation, limites,
évolutions envisagées) et **[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)**
pour l'audit complet des licences du code tiers.

## Sommaire

1. [Installation](#installation)
2. [Démarrage rapide](#démarrage-rapide)
3. [Catalogue des méthodes](#catalogue-des-méthodes)
4. [Licence](#licence)
5. [Contribuer](#contribuer)
6. [Credits](#credits)

---

## Installation

### 1. Socle (obligatoire)

```bash
pip install git+https://github.com/EOQual/eoqual-destriping.git
```

Installe tout ce qui est nécessaire pour 7 des 9 méthodes du catalogue :
`auto_egal`, `rogass`, `pande_chhetri`, `lloyd`, `munch`, `swaney`, `uvdm`
— numpy, scipy, opencv-python, scikit-image, PyWavelets, matplotlib,
rich (voir `pyproject.toml`). `munch` et `swaney` n'ajoutent aucune
dépendance externe supplémentaire : leur code est inclus directement
dans le paquet (voir `THIRD_PARTY_LICENSES.md`).

### 2. Extras optionnels

Les deux méthodes restantes dépendent de bibliothèques volontairement
**non installées par défaut** — l'une pour rester légère, l'autre pour
une raison de licence :

| Extra | Commande | Débloque | Pourquoi optionnel |
|---|---|---|---|
| `deep` | `pip install "eoqual-destriping[deep]"` | `guan` (réseau DWSRN) | Dépendance lourde (TensorFlow/Keras, ~Go) — licence des poids (Apache-2.0) sans problème, voir `THIRD_PARTY_LICENSES.md` |
| `vsnr` | `pip install "eoqual-destriping[vsnr]"` | `vsnr` | `pyvsnr` est en **AGPL-3.0** (copyleft fort, clause réseau) — **lire `THIRD_PARTY_LICENSES.md` §2.2 avant d'installer** |

Sans ces extras, appeler `guan_destripe` ou `vsnr_destripe` lève une
`ImportError` explicite indiquant quoi installer — aucune méthode ne
plante à l'*import* du package (voir `eoqual/destriping/__init__.py`).

Pour lister, à tout moment, les méthodes réellement disponibles dans
votre environnement et leur licence amont :

```python
from eoqual.destriping.runner import list_methods
list_methods()  # tableau Rich : méthode, orientation, extra requis, licence, référence
```

---

## Démarrage rapide

```python
import numpy as np
import eoqual.destriping as d

# Image à rayures verticales
noisy = ...  # np.ndarray, 2D

clean = d.rogass_destripe(noisy)
clean = d.lloyd_destripe(noisy, width=4.0, power=2.0)
clean = d.munch_destripe(noisy, decomp_level=6, wavelet="db10", sigma=10)

# Ou par le dispatcher générique
from eoqual.destriping.runner import destripe
clean = destripe(noisy, method="rogass")
```

Voir `examples/all_methods_overview.py` pour une comparaison des méthodes
du socle sur une image synthétique, `examples/modis_real_example.py` pour
une comparaison quantitative (RMSE) sur une image MODIS réelle avec
référence connue, et `examples/one_method_cli.py` pour un usage en ligne
de commande.

---

## Catalogue des méthodes

Toutes les méthodes attendent une image 2D (niveaux de gris) en entrée.
L'orientation des rayures traitée nativement par chaque implémentation
est indiquée — transposer l'image en entrée pour l'orientation opposée.

| Méthode | Rayures | Extra | Principe |
|---|---|---|---|
| `auto_egal` | horizontale | — | Appariement des moments statistiques (moyenne/écart-type) ligne à ligne |
| `rogass` | verticale | — | Filtrage du gradient horizontal (médiane par colonne) |
| `pande_chhetri` | verticale | — | Décomposition en ondelettes + filtrage fréquentiel des sous-bandes HL |
| `lloyd` | verticale | — | Filtre super-gaussien orienté (Fourier) + raffinement spatial |
| `munch` | verticale | — | Décomposition en ondelettes + filtrage FFT combiné (`rmstripes`) |
| `swaney` | verticale | — | Filtre de streaks en ondelettes (`pystripe`, conçu pour la microscopie SPIM) |
| `uvdm` | horizontale | — | Modèle variationnel unidirectionnel (Gauss-Seidel) |
| `guan` | verticale | `deep` | Réseau convolutif (DWSRN) sur coefficients d'ondelettes |
| `vsnr` | verticale | `vsnr` | Modèle variationnel (VSNR), filtre de Dirac orienté — **AGPL-3.0** |

Détail de chaque méthode (principe, implémentation, limites) :
**[REFERENCE_TECHNIQUE.md](REFERENCE_TECHNIQUE.md)**.

**Une méthode est absente de ce catalogue** (licence amont non
identifiée) : voir
**[THIRD_PARTY_LICENSES.md §2.3](THIRD_PARTY_LICENSES.md#23-méthode-non-incluse-dans-ce-dépôt)**.

---

## Licence

**Le code propre à eoqual-destriping est sous licence MIT** (`license.txt`).

Les 7 méthodes du socle (installées par défaut) sont MIT, y compris le
code vendored de `munch` et `swaney` (`rmstripes`, `pystripe`). Les 2
méthodes en extra
optionnel restent sous leur licence d'origine : `guan` (Apache-2.0,
permissif) et `vsnr` (**AGPL-3.0** — jamais installé par défaut, lire
l'avertissement avant d'ajouter cet extra). Inventaire complet, fichier
par fichier, avec vérification de chaque source :
**[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)**.

---

## Contribuer

Bug, méthode manquante, algorithme à ajouter, erreur de licence
constatée : les contributions sont bienvenues — voir
**[CONTRIBUTING.md](CONTRIBUTING.md)** pour comment signaler un problème,
proposer une méthode, ou soumettre une implémentation.

---

## Credits

- rmstripes [https://github.com/DHI-GRAS/rmstripes] (Münch et al.)
- pystripe [https://github.com/LifeCanvas-Technologies/pystripe] (Swaney et al.)
- Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal [https://github.com/jtguan/Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal] (Guan et al., extra `deep`)
- pyvsnr [https://github.com/CEA-MetroCarac/pyvsnr] (Fehrenbach, Weiss & Lorenzo, extra `vsnr`)
- NumPy [https://numpy.org/]
- SciPy [https://scipy.org/]
- OpenCV [https://opencv.org/]
- PyWavelets [https://pywavelets.readthedocs.io/]

Jeu de données de test (`tests/images/`, extrait) :
"Efficient destriping of remote sensing images using an oriented
super-Gaussian filter" — dataset, Mendeley Data (Lloyd & Bouali).
