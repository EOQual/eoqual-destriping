# Référence technique — eoqual-destriping

Détail de chaque méthode : principe, implémentation, limites connues,
évolutions envisagées. Pour le catalogue résumé et l'installation, voir
`README.md` ; pour l'audit des licences, `THIRD_PARTY_LICENSES.md`.

## 1. Conventions

- Toutes les fonctions publiques ont la signature
  `f(image: np.ndarray, ...) -> np.ndarray` (sauf `uvdm_destripe`, qui
  renvoie `(image, energy)` — `energy` permet de vérifier la convergence
  du schéma itératif).
- `image` est une image 2D niveaux de gris. Aucune méthode ne gère
  nativement le multi-bandes — appliquer bande par bande si nécessaire.
- L'orientation de rayure traitée nativement (verticale ou horizontale)
  est indiquée par méthode ci-dessous — transposer l'image en entrée
  (`image.T`) pour l'orientation opposée, puis re-transposer la sortie.
- Aucune méthode ne charge de dépendance lourde à l'*import* du paquet :
  `guan_destripe` et `vsnr_destripe` chargent leur backend au premier
  appel, avec une `ImportError` explicite si l'extra correspondant
  (`deep`, `vsnr`) n'est pas installé.

## 2. Méthodes du socle

### 2.1 `rogass` — filtrage du gradient horizontal

**Fichier** : `backends/rogass/gradient.py`
**Référence** : Rogass et al. (2014), *Remote Sensing* 6(11), 11082-11106.

Le gradient horizontal d'une image striée porte une composante
colonne-dépendante quasi constante le long des lignes (la rayure). On
l'estime par un filtre boxcar 3×1 puis la médiane par colonne du
gradient lissé (équation 6 de l'article), on la recentre pour préserver
la radiométrie moyenne de l'image (équation 7), puis on la retranche à
l'image d'origine.

**Limites** : suppose des rayures purement additives et colonne-constantes
(pas de dérive le long de la colonne). L'équation (8) de l'article
(correction de lumière parasite / gradients basse fréquence) est
volontairement omise — non pertinente hors du contexte capteur
spécifique traité dans l'article.

### 2.2 `pande_chhetri` — ondelettes + filtrage fréquentiel

**Fichier** : `backends/pande_chhetri/wavelet_freq.py`
**Référence** : Pande-Chhetri & Abd-Elrahman (2011), *ISPRS J.
Photogramm.* 66(5), 620-636.

Décomposition en ondelettes discrètes (`db4`, niveau réglable, 4 par
défaut comme dans l'article). Pour chaque niveau, la sous-bande HL
(détails horizontaux, porteuse de la rayure verticale) est filtrée
colonne par colonne : les échantillons aberrants (> `k` écarts-types de
la moyenne) sont exclus, la composante continue (DC) de la FFT de la
colonne est recalculée à partir des seuls échantillons restants, puis
réinjectée avant reconstruction (`waverec2`).

**Limites** : le seuil `k` (défaut `2.5`, non spécifié explicitement dans
l'article) doit être ajusté selon le contraste de l'image — trop bas, il
exclut des structures réelles ; trop haut, il n'exclut pas assez
d'échantillons de rayure.

### 2.3 `lloyd` — filtre super-gaussien orienté

**Fichier** : `backends/lloyd/super_gaussian.py`
**Référence** : Lloyd & Bouali (2023), *Applied Optics*.

Un filtre super-gaussien orienté à 90° (pour des rayures verticales)
atténue la bande spectrale étroite portée par la rayure dans le domaine
de Fourier. Un test de gradient (`cv2.Laplacian` sur l'image normalisée)
décide ensuite si un raffinement spatial est appliqué : estimation de la
rayure résiduelle par colonne (médiane robuste sur les pixels non nuls,
exclusion des colonnes à plus de 4σ), puis soustraction.

**Limites** : les paramètres `width`/`power` du filtre sont sensibles à
l'échelle spatiale de la rayure — pas de règle de calibration automatique
fournie ; à ajuster par image ou par capteur.

### 2.4 `munch` — ondelettes + FFT combiné

**Fichier** : `backends/munch/wrapper.py`, appelant le code vendored
`backends/munch/vendor/stripes.py` (copie verbatim de `rmstripes`, MIT —
voir `THIRD_PARTY_LICENSES.md` pour la raison du vendoring).
**Référence** : Münch et al. (2009), *Optics Express* 17(10), 8567-8591.

Décomposition en ondelettes (`wavelet`, niveau `decomp_level`), filtrage
gaussien (`sigma`) de chaque sous-bande de détails dans le domaine de
Fourier, reconstruction.

**Limites** : aucune logique propre au-delà du passage de paramètres à
l'algorithme d'origine — toute divergence de comportement doit être
comparée à `rmstripes` en amont (DHI-GRAS, non maintenu depuis 2018).

### 2.5 `swaney` — filtre de streaks en ondelettes (wrapper `pystripe`)

**Fichier** : `backends/swaney/wrapper.py`
**Référence** : Swaney et al. (2019), *bioRxiv* 576595.

Fine couche autour du paquet tiers `pystripe` (MIT), conçu à l'origine
pour la microscopie à feuille de lumière (SPIM) : rayures **horizontales**
et dynamique ~12 bits. Le wrapper transpose l'image (rayures verticales →
horizontales) et renormalise la dynamique avant/après l'appel.

**Limites** : conçu pour un domaine d'image différent (microscopie) — les
paramètres par défaut (`sigma1`/`sigma2` = 32) sont un point de départ,
pas une valeur calibrée pour l'imagerie satellite.

### 2.6 `uvdm` — modèle variationnel unidirectionnel (Bouali & Ladjal)

**Fichier** : `backends/uvdm/bouali.py`
**Référence** : Bouali & Ladjal (2011), *IEEE TGRS* 49(8), 2924-2935.

Implémentation Python de l'algorithme. Minimise une fonctionnelle
d'énergie combinant fidélité au gradient horizontal de l'image bruitée
et régularisation TV-like sur le gradient vertical, par un schéma
itératif de Gauss-Seidel. Traite nativement des rayures **horizontales**.

**Limites** : les paramètres `theta`/`eps` recommandés (0.1 / 1) sont
calibrés pour des images 8 bits — à re-calibrer pour d'autres dynamiques.
Convergence à vérifier via la sortie `energy` (doit décroître puis se
stabiliser) ; pas de critère d'arrêt automatique (nombre d'itérations
fixe).

### 2.7 `auto_egal` — appariement des moments statistiques

**Fichier** : `backends/auto_egal/moment_matching.py`
**Référence** : Moik (1980), *NASA SP-341*, p. 87.

Chaque ligne de l'image est normalisée indépendamment (moyenne nulle,
écart-type unitaire), ce qui élimine les différences de gain/offset
ligne à ligne typiques d'un capteur à balayage (whiskbroom) — la rayure
apparaît alors comme une bande **horizontale**. Le résultat est ensuite
recalé sur la dynamique radiométrique d'origine : celle de l'image
entière par défaut, ou celle d'une ligne de référence donnée
(`target_row`).

**Limites** : méthode purement statistique, sans modèle spatial de la
rayure — suppose que chaque ligne a, hors rayure, la même statistique
globale que ses voisines (peu adapté à une scène très hétérogène
ligne à ligne, ex. changement de couverture au sol en cours de ligne).

## 3. Méthodes en extra optionnel

### 3.1 `guan` (extra `deep`) — réseau DWSRN

**Fichier** : `backends/guan/dwsrn.py`
**Référence** : Guan, Lai & Xiong (2019), *IEEE Access* 7, 44544-44554.

Réseau convolutif (8 blocs Conv2D 64 filtres + connexion résiduelle),
appliqué aux 4 sous-bandes d'une décomposition en ondelettes de Haar
(LL/LH/HL/HH), avec normalisation min-max en entrée. Poids pré-entraînés
fournis (`weights/weight.hdf5`, Apache-2.0 — voir `NOTICE.md` et
`THIRD_PARTY_LICENSES.md`).

**Pourquoi en extra** : dépendance TensorFlow/Keras (~Go), pas pour
raison de licence (Apache-2.0, permissif). Chargé paresseusement (singleton
thread-safe) au premier appel de `guan_destripe` — jamais à l'import du
paquet.

**Limites** : les poids sont figés (entraînement d'origine, domaine et
capteur non documentés précisément par les auteurs) — pas de garantie de
généralisation hors du domaine d'entraînement d'origine. Pas de ré-entraînement
fourni dans ce dépôt.

### 3.2 `vsnr` (extra `vsnr`) — Variational Stationary Noise Remover

**Fichier** : `backends/vsnr/fehrenbach_weiss.py`
**Référence** : Fehrenbach, Weiss & Lorenzo (2012), *IEEE TIP* 21(10),
4420-4430.

Fine couche autour du paquet tiers `pyvsnr`. Un filtre de Dirac orienté
verticalement (`alpha`) est ajouté au modèle VSNR, résolu itérativement
(ADMM, `maxit`/`cvg_threshold`).

**Pourquoi en extra** : `pyvsnr` est en **AGPL-3.0** — voir l'avertissement
détaillé dans `THIRD_PARTY_LICENSES.md` §2.2 avant d'installer cet extra.

**Limites** : temps de calcul plus élevé que les autres méthodes (schéma
itératif ADMM, `maxit=200` par défaut).

## 4. Méthode non incluse

Voir `THIRD_PARTY_LICENSES.md` §2.3 : `d1_WLS`/Fangzhou, licence amont
non identifiée.

## 5. Tests et exemples

`tests/test_backends.py` vérifie, pour chaque méthode du socle, que
l'appel sur une image synthétique striée ne lève pas d'exception et
renvoie une image de même forme — ce ne sont pas des tests de qualité
numérique. `examples/all_methods_overview.py` affiche une comparaison
visuelle sur une image synthétique à rayures connues.

`examples/modis_real_example.py` va plus loin : `tests/images/MODIS_noisy.tif`
dispose d'une vraie référence (`MODIS_ref.tif`, CC BY 4.0), ce qui permet
un RMSE avant/après par méthode plutôt qu'une comparaison seulement
visuelle. Sur cette image, `rogass`, `pande_chhetri`, `lloyd` et `uvdm`
réduisent le RMSE (+20 à +30 %) ; `auto_egal` le dégrade fortement —
confirmation empirique de sa limite documentée en §2.7 (méthode
statistique globale, mal adaptée à une scène hétérogène ligne à ligne).
