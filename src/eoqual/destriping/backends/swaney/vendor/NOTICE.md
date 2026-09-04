# NOTICE — code vendored (Swaney et al., `pystripe`)

`core.py` dans ce dossier est un extrait **verbatim**, non modifié, de
`pystripe/core.py` — uniquement le bloc autonome `wavedec` .. `filter_streaks`
(exclut les fonctions d'I/O fichier, CLI et traitement par lot, qui ne
sont pas utilisées par `swaney_destripe`) :

- Dépôt : https://github.com/LifeCanvas-Technologies/pystripe
- Licence : **MIT**, Copyright (c) 2018 Chung Lab — voir `LICENSE` dans
  ce dossier (texte exact du dépôt d'origine).
- Référence : Swaney, J., Kamentsky, L., Evans, N.B., Xie, K., Park,
  Y.G., Drummond, G., Chung, K. (2019). "Scalable image processing
  techniques for quantitative analysis of volumetric biological images
  from light-sheet microscopy." bioRxiv 576595.

## Pourquoi vendored plutôt que dépendance externe

Le `setup.py` de `pystripe` fixe des versions exactes et anciennes
(`numpy==1.19.5`, `scipy==1.5.4`, `scikit-image==0.17.2`,
`PyWavelets==1.1.1`...) qui ne se compilent plus du tout sur Python
3.12, et entrent de toute façon en conflit avec les versions de
numpy/scipy/scikit-image utilisées par le reste d'`eoqual-destriping`.
`import pystripe` charge aussi inconditionnellement `dcimg`, `tifffile`,
`imageio`, `tqdm` (son I/O fichier et son traitement par lot), qu'un
simple appel à `filter_streaks` n'utilise jamais.

Plutôt que reléguer `swaney` en extra pour ce seul problème
d'installabilité amont, le bloc de fonctions réellement nécessaire à
`filter_streaks` (`wavedec`, `waverec`, `fft`, `ifft`, `fft2`, `ifft2`,
`magnitude`, `notch`, `gaussian_filter`, `hist_match`, `max_level`,
`sigmoid`, `foreground_fraction`, `filter_subband`, `apply_flat`,
`filter_streaks`) est inclus directement (MIT, conditions respectées :
notice de copyright et d'autorisation conservées ci-dessus et dans
`LICENSE`). `swaney` reste ainsi dans le socle, sans dépendance externe
cassée.

Voir `THIRD_PARTY_LICENSES.md` (racine du projet) pour l'entrée
correspondante dans l'inventaire des licences tierces.
