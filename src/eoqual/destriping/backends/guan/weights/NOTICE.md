# NOTICE — poids DWSRN (Guan et al.)

`weight.hdf5` provient de :

- Dépôt : https://github.com/jtguan/Wavelet-Deep-Neural-Network-for-Stripe-Noise-Removal
- Licence : **Apache License 2.0** (fichier `license` à la racine du dépôt,
  vérifié via l'API GitHub — champ `license.spdx_id = "apache-2.0"`)
- Référence : Guan, J., Lai, R., Xiong, A. (2019). "Wavelet Deep Neural
  Network for Stripe Noise Removal." IEEE Access, 7, 44544-44554.

Conformément à la licence Apache-2.0, ce NOTICE accompagne la
redistribution du fichier de poids dans `eoqual-destriping`. Aucune
modification n'est apportée au fichier lui-même ; l'architecture du
réseau (`backends/guan/dwsrn.py`) est une réécriture propre de celle
décrite dans le dépôt d'origine (Keras `Input/Conv2D/Activation/Add`),
nécessaire pour charger ces poids sans dépendre du code du dépôt.

Voir `THIRD_PARTY_LICENSES.md` (racine du projet) pour l'entrée
correspondante dans l'inventaire des licences tierces.
