# Scripts stage M1 2023-2024

Stage de M1 au laboratoire de Nanterre Université ModyCo sous la tutelle d'Emmett Strickland.

## Tâches principales

1. Récuperer de façon automatique les silences `#` à l'aide d'outils de VAD (Voice Activity Detection), pour ensuite les insérer dans les fichiers CoNLL-U n'ayant pas ces silences d'annotés.

2. Comparaison des données prosodiques (slope, f0, etc..) entre les fichiers CoNLL-U gold et les fichiers CoNLL-U gold obtenus de façon automatique. Déterminer ainsi si les données prosodiques des fichiers CoNLL-U gold obtenus de façon automatique sont similaires à celles des fichiers CoNLL-U gold.

## Organisation des dossiers

Les dossiers les plus importants sont les suivants:

- `Gold_Auto`: qui contient les différents scripts permettant l'annotation des silences `#` de façon automatique dans les fichiers CoNLL-U. Il est possible de lancer les 6 scripts de façon automatique en lançant le notebook `detection_insertion_silences_conllu.ipynb` qui se trouve dans le dossier `Gold_Auto` ou de lancer les 6 scripts de façon indépendante.

  - `Gold_Auto/Scripts`: qui contient les 6 scripts.
    - `1-create_trans_tier.ipynb`: qui permet d'obtenir le TextGrid annoté de la transcription obtenus via les CoNLL-U.
    - `2-sppas_tg.ipynb`: qui permet d'obtenir les fichiers TextGrid contenant la tokenisation, la syllabification, les ipus, etc.. via SPPAS.
    - `3-get_combine_tier.ipynb` : qui permet de combiner le tier IPUs comprenant les silences et le tiers TokensAlign.
    - `4-reconstruction_trans_merge.ipynb`: qui permet de reconstruire la transcription en ajoutant les silences et de créer un TextGrid comprenant Sent-ID, Sent-Text (nouvelle transcription), Word-ID et Word-Text.
    - `5-update_conllu_pause.ipynb`: qui permet de mettre à jour les fichiers CoNLL-U en ajoutant les silences.
    - `6-create_slam_tg.ipynb`: qui permet d'obtenir les TextGrid pour SLAM.

- `Prosodic_Data`: qui contient les différents scripts permettant l'ajout de données prosodiques aux fichiers CoNLL-U ainsi que des scripts permettant l'analyse, la comparaison de ces données entre celles des fichiers gold et celles des fichiers gold obtenus de façon automatique.
