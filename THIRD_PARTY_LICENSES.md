# Licences tierces — inventaire et statut

> **Avertissement.** Cet inventaire est tenu au meilleur effort, à partir
> d'une vérification directe des dépôts/paquets sources (fichier LICENSE,
> champ `license` de l'API GitHub, classifieur PyPI). Si une erreur y est
> identifiée (source mal vérifiée, statut incorrect, nouvelle source
> vendored non recensée), elle sera corrigée dès que signalée — et si
> nécessaire, l'implémentation concernée sera retirée plutôt que sa
> licence "arrangée" a posteriori. Pour signaler un problème, voir
> `CONTRIBUTING.md`.

Ce document recense, pour chaque méthode de `src/eoqual/destriping/`, sa
source, la licence **réellement vérifiée** de cette source, et le statut
de compatibilité avec la licence MIT annoncée pour `eoqual-destriping`
(`license.txt`).

**État actuel** : toutes les méthodes du **socle** (installées par défaut,
sans extra) sont MIT ou reposent sur des dépendances MIT. Deux méthodes
sont reléguées en **extra optionnel**, jamais installées ni importées par
défaut : `guan` (Apache-2.0 — permissif mais dépendance lourde) et `vsnr`
(**AGPL-3.0** — copyleft fort, voir avertissement §2.2).

## 1. Légende

- 🔴 **Bloquant** — licence copyleft ou absente, et atteignable sans
  action explicite de l'utilisateur (import du socle). *Aucune entrée
  dans cet état actuellement.*
- 🟡 **À surveiller** — licence copyleft forte, mais l'utilisateur ne
  l'obtient qu'en installant explicitement un extra pip.
- 🟢 **Compatible** — licence permissive (MIT/BSD/Apache), compatible avec
  MIT moyennant la conservation de la notice d'origine.

## 2. Inventaire

### 2.1 Socle — sources permissives confirmées (🟢)

| Méthode | Fichier | Source | Licence vérifiée |
|---|---|---|---|
| `auto_egal` | `backends/auto_egal/moment_matching.py` | Réimplémentation depuis la description de la technique dans Moik (1980), NASA SP-341, p. 87 — aucun code tiers repris | MIT (auteur du dépôt) |
| `rogass` | `backends/rogass/gradient.py` | Réimplémentation depuis les équations de Rogass et al. (2014) — aucun code tiers repris | MIT (auteur du dépôt) |
| `pande_chhetri` | `backends/pande_chhetri/wavelet_freq.py` | Réimplémentation depuis les équations de Pande-Chhetri & Abd-Elrahman (2011) — aucun code tiers repris | MIT (auteur du dépôt) |
| `lloyd` | `backends/lloyd/super_gaussian.py` | Réimplémentation depuis Lloyd & Bouali (2023) — aucun code tiers repris | MIT (auteur du dépôt) |
| `uvdm` | `backends/uvdm/bouali.py` | Implémentation Python originale de l'algorithme de Bouali & Ladjal (2011), par l'auteur de ce dépôt | MIT (auteur du dépôt) |
| `munch` | `backends/munch/vendor/stripes.py` (**vendored**, copie verbatim) | https://github.com/DHI-GRAS/rmstripes | **MIT** — vérifié (`LICENSE`, copyright DHI GRAS 2018) — voir `backends/munch/vendor/NOTICE.md` |
| `swaney` | `backends/swaney/wrapper.py` (dépendance `pystripe`) | https://github.com/LifeCanvas-Technologies/pystripe (fork actif du dépôt historique `chunglabmit/pystripe`, publié sur PyPI) | **MIT** — vérifié (API GitHub, `license.spdx_id = "mit"`) |

Dépendances du socle (numpy, scipy, opencv-python, PyWavelets, matplotlib,
rich) : toutes BSD/MIT/Apache-2.0.

**Pourquoi `munch` est vendored plutôt que dépendance externe** :
`rmstripes` n'est pas publié sur PyPI, et son fichier de packaging
auto-généré (`versioneer.py`, non modifié depuis 2018) appelle
`configparser.SafeConfigParser()`, retiré de Python 3.12 — son
installation échoue donc sur Python 3.12, indépendamment de son code
(qui, lui, fonctionne sans modification). Le fichier concerné
(`stripes.py`, ~50 lignes, aucune dépendance hors numpy/PyWavelets déjà
dans le socle) est inclus verbatim plutôt que relégué en extra pour ce
seul problème de packaging amont — voir
`backends/munch/vendor/NOTICE.md`.

### 2.2 Extras optionnels — licences non permissives (🟡)

| Méthode | Extra | Fichier | Source | Licence vérifiée | Statut |
|---|---|---|---|---|---|
| `guan` | `deep` | `backends/guan/dwsrn.py` + `backends/guan/weights/weight.hdf5` | https://github.com/jtguan/Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal | **Apache-2.0** — vérifié (API GitHub, fichier `license` à la racine) | 🟢 permissif, mais dépendance lourde (TensorFlow/Keras) → relégué en extra pour garder le socle léger, pas pour raison de licence. NOTICE conservé (`backends/guan/weights/NOTICE.md`), architecture ré-écrite proprement pour charger les poids sans reprendre le code du dépôt. |
| `vsnr` | `vsnr` | `backends/vsnr/fehrenbach_weiss.py` (dépendance `pyvsnr`) | https://github.com/CEA-MetroCarac/pyvsnr (PyPI `pyvsnr`, mainteneurs Killian Pavy & Patrick Quémère, CEA) | **AGPL-3.0** — vérifié (classifieur PyPI `License :: OSI Approved :: GNU Affero General Public License v3`, champ `license` API GitHub) | 🟡 **Avertissement** : l'AGPL-3.0 est un copyleft plus fort que la GPL — sa clause réseau s'applique dès qu'un service utilisant `pyvsnr` est exposé, même sans distribution du binaire. `vsnr_destripe` n'est **jamais** importé ni installé par défaut ; son import lève une `ImportError` explicite tant que l'extra n'est pas installé volontairement. Si votre usage (interne, service exposé, produit distribué) est incompatible avec l'AGPL, n'installez pas cet extra. |

### 2.3 Méthode non incluse dans ce dépôt

| Méthode | Raison |
|---|---|
| **d1_WLS_Destriping (Fangzhou et al.)** | Portage quasi littéral du MATLAB de `LifangzhouSia/1D-Weighted-Least-Square-Destriping-for-Uncooled-Infrared-Images` (mêmes noms de fonctions : `fGHS`, `edgeIndicator`, `weightedLocalLinearFilter`...). **Ce dépôt source n'a aucun fichier LICENSE** (vérifié via l'API GitHub) — tous droits réservés par défaut. Le publier sous MIT constituerait une violation. Non incluse tant qu'une autorisation explicite de l'auteur original n'est pas obtenue, ou qu'une réécriture clean-room depuis le seul article (Applied Optics 58, 9141-9153, 2019) n'est pas faite. |

## 3. Pistes de remédiation restantes (facultatif)

- `d1_WLS` (Fangzhou et al.) : contacter les auteurs (Fangzhou Li, Yaohong
  Zhao, Wei Xiang) pour une autorisation explicite, ou réécrire clean-room
  depuis l'article seul.
- `guan` : envisager une évaluation indépendante de si un poids ré-entraîné
  depuis zéro (licence 100 % `eoqual-destriping`) serait préférable à la
  dépendance à un fichier de poids tiers, même Apache-2.0.
- `vsnr` : surveiller l'apparition d'une implémentation VSNR alternative
  sous licence permissive (aucune trouvée à ce jour).
