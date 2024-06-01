"""
Ce script permet de fusionner les différents tiers de plusieurs fichiers TextGrid en un seul fichier.

Requis :
- TextGrids : 
    - palign.TextGrid (TokensAlign et PhonAlign), syll.TextGrid (SyllAlign) : obtenus par spaas 
    - id.TextGrid obtenus par get_index.py (index)
    - _MG.TextGrid : obtenus par text_grid.py (transcription)
    - syl_tok.TextGrid : obtenus par combine_silence_sentence_textgrid.py (Combined et SyllSil)

Commande :
python3 ./Python_Stage_23_24/detect_silence_textgrid/4-merge.py
"""

import os

import textgrid


def generate_tiers_selection(directory: str) -> tuple:
    """
    Génération d'une sélection de tiers à partir de fichiers TextGrid dans un répertoire spécifique.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid.

    Returns:
    dict: Dictionnaire des fichiers

    Variables:
    tiers_trans (dict): Dictionnaire des fichiers avec ayant le tier "trans"
    other_tiers (dict): Dictionnaire des autres tiers à fusionner
    """
    tiers_trans = {}
    other_tiers = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith(".TextGrid"):
            # Tiers pour l'alignement phonétique et token
            if "MG-palign.TextGrid" in file:
                other_tiers[file] = ["TokensAlign", "PhonAlign"]
                # print(file, "palign")
            # Tiers pour l'alignement des syllabes
            elif "MG-syll.TextGrid" in file:
                other_tiers[file] = ["SyllAlign"]
                # print(file)
            # Tiers pour l'alignement des index
            elif "MG-id.TextGrid" in file:
                other_tiers[file] = ["index"]
                # print(file)
            # Tiers pour la transcription
            elif not any(
                substring in file
                for substring in [
                    "MG-phon.TextGrid",
                    "MG-token.TextGrid",
                    "merged",
                    "MG-syll.TextGrid",
                    "MG-id.TextGrid",
                ]
            ):
                tiers_trans[file] = ["trans"]
                # print(file)

    return tiers_trans, other_tiers


def merge_textgrid_tiers(
    directory: str,
    tiers_trans: dict,
    other_tiers: dict,
    base_name_file: str,
    merged: str = None,
) -> None:
    """
    Fusionne différents tiers de plusieurs fichiers TextGrid en un seul fichier.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid
    tiers_trans (dict): Dictionnaire des fichiers avec le tier "trans"
    other_tiers (dict): Dictionnaire des autres tiers à fusionner
    base_name_file (str): Nom de base pour le fichier de sortie
    merged (str): Dossier de destination pour le fichier fusionné (optionnel)

    Returns:
    None

    Variables:
    merged_textgrid (TextGrid): TextGrid fusionné
    tier_order (list): Ordre spécifique des autres tiers
    """
    merged_textgrid = textgrid.TextGrid()

    # Ajout des tiers 'trans'
    for file, tiers_list in tiers_trans.items():
        tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
        for tier_name in tiers_list:
            tier = tg.getFirst(tier_name)
            print(tier)
            merged_textgrid.append(tier)

    # Définition de l'ordre spécifique des autres tiers
    tier_order = ["TokensAlign", "SyllAlign", "PhonAlign", "index"]

    # Ajout des autres tiers dans l'ordre spécifié
    for tier_name in tier_order:
        for file, tiers_list in other_tiers.items():
            if tier_name in tiers_list:
                tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
                tier = tg.getFirst(tier_name)
                merged_textgrid.append(tier)

    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f"{base_name_file}-merged.TextGrid"))
    else:
        merged_textgrid.write(
            os.path.join(directory, f"{base_name_file}-merged.TextGrid")
        )


def generate_tiers_selection_non_gold_silence(directory: str) -> tuple:
    """
    Génère une sélection de tiers à partir de fichiers TextGrid non gold dans un répertoire spécifique.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid.

    Returns:
    tuple: Deux dictionnaires - un pour le tier trans et un autre pour les autres tiers.

    Variables:
    tiers_trans (dict): Dictionnaire des fichiers avec ayant le tier "trans"
    other_tiers (dict): Dictionnaire des autres tiers à fusionner
    """
    tiers_trans = {}
    other_tiers = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith(".TextGrid"):
            # Tiers pour l'alignement des syllabes
            if "M-syl_tok.TextGrid" in file:
                other_tiers[file] = ["Combined"]
                # print(file)
            # Tiers pour l'alignement des index
            elif "M-id.TextGrid" in file:
                other_tiers[file] = ["index"]
                # print(file)
            # Tiers pour l'alignement des tokens
            elif "M-palign.TextGrid" in file:
                other_tiers[file] = ["TokensAlign"]
            # Tiers pour la transcription
            elif not any(
                substring in file
                for substring in [
                    "M-phon.TextGrid",
                    "M-token.TextGrid",
                    "merged",
                    "M-syll.TextGrid",
                    "M-id.TextGrid",
                    "M-syl_tok.TextGrid",
                ]
            ):
                tiers_trans[file] = ["trans"]
                # print(file)

    return tiers_trans, other_tiers


def merge_textgrid_non_gold_tiers(
    directory: str,
    tiers_trans: dict,
    other_tiers: dict,
    base_name_file: str,
    merged: str = None,
) -> None:
    """
    Fusionne différents tiers de plusieurs fichiers TextGrid en un seul fichier.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid
    tiers_trans (dict): Dictionnaire des fichiers avec le tier "trans"
    other_tiers (dict): Dictionnaire des autres tiers à fusionner
    base_name_file (str): Nom de base pour le fichier de sortie
    merged (str): Dossier de destination pour le fichier fusionné (optionnel)

    Returns:
    None

    Variables:
    merged_textgrid (TextGrid): TextGrid fusionné
    tier_order (list): Ordre spécifique des autres tiers
    """
    merged_textgrid = textgrid.TextGrid()

    # Ajout du tier "trans"
    for file, tiers_list in tiers_trans.items():
        tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
        for tier_name in tiers_list:
            tier = tg.getFirst(tier_name)
            if tier is not None:  # Check if the tier is found
                merged_textgrid.append(tier)
            else:
                print(f"Tier '{tier_name}' not found in file: {file}")

    # Définition de l'ordre spécifique des autres tiers
    tier_order = ["TokensAlign", "index", "Combined"]

    # Ajout des autres tiers dans l'ordre spécifié
    for tier_name in tier_order:
        for file, tiers_list in other_tiers.items():
            if tier_name in tiers_list:
                tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
                tier = tg.getFirst(tier_name)
                if tier is not None:  # Check if the tier is found
                    merged_textgrid.append(tier)
                else:
                    print(f"Tier '{tier_name}' not found in file: {file}")

    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f"{base_name_file}-merged.TextGrid"))
    else:
        merged_textgrid.write(
            os.path.join(directory, f"{base_name_file}-merged.TextGrid")
        )


def generate_tiers_selection_gold_non_gold_silence(
    directory: str, directory_gold: str
) -> tuple:
    """
    Génère une sélection de tiers à partir de fichiers TextGrid gold et non gold dans un répertoire spécifique.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid non gold.
    directory_gold (str): Chemin vers le répertoire contenant les fichiers TextGrid gold.

    Returns:
    tuple: Deux dictionnaires - un pour les tiers obtenus dans des fichiers gold et un autre pour les tiers obtenus dans les fichiers non-gold.

    Variables:
    tiers (dict): Dictionnaire des tiers TokensAlign, index, SyllAlign et trans.
    tiers_combined (dict): Dictionnaire des fichiers avec les tiers combinés (Combined et SyllSil).
    """
    tiers = {}
    tiers_combined = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith(".TextGrid"):
            # Récupération des tiers non gold Combined (Token+#) et SyllSil (Syllable+#)
            if "MG-syl_tok.TextGrid" in file:
                tiers_combined[file] = ["Combined", "SyllSil"]
                # print(file)

    for file in sorted(os.listdir(directory_gold)):
        if file.endswith(".TextGrid"):
            # Récupération des tiers TokensAlign
            if "MG-palign.TextGrid" in file:
                tiers[file] = ["TokensAlign"]
            # Récupération des tiers index
            elif "MG-id.TextGrid" in file:
                tiers[file] = ["index"]
                # print(file)
            # Récupération des tiers SyllAlign
            elif "MG-syll.TextGrid" in file:
                tiers[file] = ["SyllAlign"]
            # Récupération des tiers trans
            elif not any(
                substring in file
                for substring in [
                    "MG-phon.TextGrid",
                    "MG-token.TextGrid",
                    "merged",
                    "MG-syll.TextGrid",
                    "MG-id.TextGrid",
                    "MG-syl_tok.TextGrid",
                ]
            ):
                tiers[file] = ["trans"]
                # print(file)

    return tiers, tiers_combined


def merge_gold_non_gold(
    directory: str,
    directory_gold: str,
    tiers: dict,
    tiers_combined: dict,
    base_name_file: str,
    merged: str = None,
) -> None:
    """
    Fusionne les différents tiers en un seul fichier TextGrid.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TextGrid non gold.
    directory_gold (str): Chemin vers le répertoire contenant les fichiers TextGrid gold.
    tiers (dict): Dictionnaire des tiers obtenus dans des fichiers gold.
    tiers_combined (dict): Dictionnaire des fichiers avec les tiers combinés (Combined et SyllSil).
    base_name_file (str): Nom pour le fichier de sortie.
    merged (str): Dossier de destination pour le fichier fusionné (optionnel).

    Returns:
    None

    Variables:
    merged_textgrid (TextGrid): TextGrid fusionné
    tier_order (list): Ordre spécifique des autres tiers
    added_tiers (set): Ensemble pour suivre les tiers déjà ajoutés
    """
    merged_textgrid = textgrid.TextGrid()
    tier_order = ["trans", "TokensAlign", "SyllAlign", "index", "Combined", "SyllSil"]
    added_tiers = set()  # Ensemble pour suivre les tiers déjà ajoutés

    for tier_name in tier_order:
        for file, tiers_list in (
            tiers.items()
            if tier_name != "Combined" and tier_name != "SyllSil"
            else tiers_combined.items()
        ):
            # print(file, tiers_list)
            directory_used = (
                directory_gold
                if tier_name != "Combined" and tier_name != "SyllSil"
                else directory
            )
            for tier in tiers_list:
                # print(tier)
                if (
                    tier_name not in added_tiers
                ):  # Vérifier si le tier n'a pas déjà été ajouté
                    print(
                        f"Adding tier '{tier_name}' from file: {directory_used}, {file}"
                    )
                    tg = textgrid.TextGrid.fromFile(os.path.join(directory_used, file))
                    current_tier = tg.getFirst(tier_name)
                    if current_tier is not None:
                        merged_textgrid.append(current_tier)
                        added_tiers.add(tier_name)
                # else:
                #     print(f"Tier '{tier_name}' not found in file: {file}")

    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f"{base_name_file}-merged.TextGrid"))
    else:
        merged_textgrid.write(
            os.path.join(directory, f"{base_name_file}-merged.TextGrid")
        )


# base_folder = './TEXTGRID_WAV'
# merged = './MERGED'

# base_folder = './TEXTGRID_WAV_nongold'
# merged = './MERGED/non_gold'

base_folder = "TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad/"
base_folder_gold = "TEXTGRID_WAV/"
merged = "MERGED/gold_non_gold_04-05_10ms_webrtcvad/"


for subdir in os.listdir(base_folder):
    subdir_path = os.path.join(base_folder, subdir)
    base_name_file = os.path.basename(subdir_path)
    if os.path.isdir(subdir_path):
        
        # Generate tier selections and merge TextGrids
        # tiers_trans, other_tiers = generate_tiers_selection(subdir_path)
        # merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file)
        # merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file, merged)

        # tiers_trans, other_tiers = generate_tiers_selection_non_gold_silence(subdir_path)
        # merge_textgrid_non_gold_tiers(subdir_path, tiers_trans, other_tiers, base_name_file, merged)

        # print(subdir_path)
        gold_file = os.path.join(base_folder_gold, base_name_file)
        tiers, tiers_combined = generate_tiers_selection_gold_non_gold_silence(
            subdir_path, gold_file
        )
        # print(tiers, tiers_combined)
        merge_gold_non_gold(
            subdir_path, gold_file, tiers, tiers_combined, base_name_file, merged
        )
