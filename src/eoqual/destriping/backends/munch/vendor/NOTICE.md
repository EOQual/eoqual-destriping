# NOTICE — code vendored (Münch et al., `rmstripes`)

`stripes.py` dans ce dossier est une copie **verbatim**, non modifiée, de
`rmstripes/stripes.py` :

- Dépôt : https://github.com/DHI-GRAS/rmstripes
- Licence : **MIT**, Copyright (c) 2018 DHI GRAS — voir `LICENSE` dans ce
  dossier (texte exact du dépôt d'origine).
- Référence : Münch, B., Trtik, P., Marone, F., Stampanoni, M. (2009).
  "Stripe and ring artifact removal with combined wavelet — Fourier
  filtering." Optics Express, 17(10), 8567-8591.

## Pourquoi vendored plutôt que dépendance externe

`rmstripes` n'est pas publié sur PyPI ; l'installer nécessite un build
PEP 517 depuis son dépôt Git. Son fichier de packaging auto-généré
(`versioneer.py`, non modifié depuis 2018) appelle
`configparser.SafeConfigParser()`, une méthode retirée de Python 3.12 —
l'installation échoue donc sur Python 3.12, indépendamment du code de
`stripes.py` lui-même (qui, lui, fonctionne sans modification).

Plutôt que reléguer `munch` en extra optionnel pour ce seul problème de
packaging amont, ce fichier est inclus directement dans
`eoqual-destriping` (MIT, conditions respectées : notice de copyright et
d'autorisation conservées ci-dessus et dans `LICENSE`). `munch` reste
ainsi dans le socle, sans dépendance externe cassée sur Python 3.12.

Voir `THIRD_PARTY_LICENSES.md` (racine du projet) pour l'entrée
correspondante dans l'inventaire des licences tierces.
