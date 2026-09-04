# Change Log

## Version History

0.1.0 (2026-09-04)

:   -   Première version publique.
    -   **9 méthodes** : `auto_egal`, `rogass`, `pande_chhetri`, `lloyd`,
        `munch`, `swaney`, `uvdm` dans le socle (MIT — `munch` et
        `swaney` par code vendored, sans dépendance externe) ; `guan`
        (réseau DWSRN, extra `deep`) et `vsnr` (extra `vsnr`,
        **AGPL-3.0** — jamais installé par défaut) en extras optionnels.
    -   Registre central unique (`config.py::METHODS_CONFIGS`) et
        dispatcher générique `eoqual.destriping.runner.destripe(image,
        method=...)`, en plus de l'import direct de chaque fonction.
    -   Chargement paresseux des dépendances lourdes/optionnelles
        (`guan_destripe` : TensorFlow/Keras + poids `.hdf5` ; `vsnr_destripe` :
        `pyvsnr`) — aucun import ne se produit avant le premier appel de
        la fonction correspondante ; `ImportError` explicite sinon.
    -   Audit de licence complet des sources amont (`THIRD_PARTY_LICENSES.md`) :
        vérification directe (fichier LICENSE, champ `license` de l'API
        GitHub/PyPI) pour chaque dépendance tierce.
    -   Une méthode n'est **pas incluse** dans cette version (voir
        `THIRD_PARTY_LICENSES.md` §2.3) : `d1_WLS` (Fangzhou et al.),
        portage MATLAB dont la source n'a aucune licence identifiée
        (tous droits réservés).
    -   Documentation : `README.md` (installation, catalogue, licence),
        `REFERENCE_TECHNIQUE.md` (principe/implémentation/limites par
        méthode), `THIRD_PARTY_LICENSES.md` (audit des licences tierces),
        `CONTRIBUTING.md` (signaler un bug, proposer/implémenter une
        méthode).

## Évolutions futures

Voir `THIRD_PARTY_LICENSES.md` §3 (pistes de remédiation sur `d1_WLS`,
`guan`, `vsnr`) et `CONTRIBUTING.md` (proposer/implémenter une méthode).
