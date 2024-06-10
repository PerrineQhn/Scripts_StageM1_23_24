"""
Ce script est utilisé pour analyser les fichiers TextGrid et les fichiers TSV afin de comparer les # dans les fichiers gold et non gold.

Requis :
- Fichiers TextGrids merges obtenu à partir du script merge.py
- TSVs contenant les phrases gold et non gold obtenus à partir du script compare_gold_non_gold.py

Commande : 
python3 ./Python_Stage_23_24/detect_silence_textgrid/5-stat_silence_gold-non_gold.py

"""

import csv
import os
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from praatio import tgio


def compare_silence(
    file_path: str,
    file: str,
    global_writer: csv.writer,
    silence_durations: dict,
    all_tokensalign_durations: list,
    all_combined_duration: list,
    files_with_short_pauses: list,
) -> None:
    """
    Détermine les correspondances et les chevauchements entre les silences dans les tiers Combined et TokensAlign.
    Écrit les détails des silences dans un fichier TSV individuel pour chaque fichier TextGrid.
    Nombre de silences uniques dans Combined et TokensAlign.
    Durée moyenne des silences uniques dans Combined et TokensAlign.
    Durée moyenne des silences dans Combined et TokensAlign.
    Nombre de silences courts (durée < 10ms) dans Combined et TokensAlign.

    Parameters:
    file_path (str): Chemin vers le fichier TextGrid à analyser.
    global_writer (csv.writer): Objet pour écrire les statistiques globales dans un fichier TSV.
    silence_durations (dict): Dictionnaire pour stocker les durées des silences.
    all_tokensalign_durations (list): Liste pour stocker les durées de tous les silences dans TokensAlign.
    all_combined_duration (list): Liste pour stocker les durées de tous les silences dans Combined.
    files_with_short_pauses (list): Liste pour stocker les noms des fichiers avec des silences courts.

    Returns:
    None

    Variables:
    exact_matches (list): Liste pour stocker les correspondances exactes entre les silences.
    partial_overlaps (list): Liste pour stocker les chevauchements partiels entre les silences.
    unique_combined (list): Liste pour stocker les silences uniques dans Combined.
    unique_tokensalign (list): Liste pour stocker les silences uniques dans TokensAlign.
    """
    # Ouvrir le fichier TextGrid
    textgrid_sil = tgio.openTextgrid(file_path)

    # Extraire les silences de 'Combined' et 'TokensAlign'
    combined_silences = [
        (interval[0], interval[1])
        for interval in textgrid_sil.tierDict["Combined"].entryList
        if "#" in interval[2]
    ]
    tokensalign_silences = [
        (interval[0], interval[1])
        for interval in textgrid_sil.tierDict["TokensAlign"].entryList
        if "#" in interval[2]
    ]

    # Fonction pour vérifier le chevauchement entre deux intervalles
    def check_overlap(interval1, interval2):
        return max(interval1[0], interval2[0]) < min(interval1[1], interval2[1])

    # Initialiser les listes pour les correspondances et les uniques
    exact_matches, partial_overlaps, unique_combined, unique_tokensalign = (
        [],
        [],
        [],
        [],
    )

    # Comparer les silences pour trouver les correspondances et les chevauchements
    for c_sil in combined_silences:
        for t_sil in tokensalign_silences:
            if c_sil == t_sil:
                exact_matches.append(c_sil)
            elif check_overlap(c_sil, t_sil):
                partial_overlaps.append((c_sil, t_sil))

    # Identifier les silences uniques
    unique_combined = [
        c_sil
        for c_sil in combined_silences
        if c_sil not in exact_matches
        and not any(check_overlap(c_sil, t_sil) for t_sil in tokensalign_silences)
    ]
    unique_tokensalign = [
        t_sil
        for t_sil in tokensalign_silences
        if t_sil not in exact_matches
        and not any(check_overlap(t_sil, c_sil) for c_sil in combined_silences)
    ]
    all_tokensalign = [t_sil for t_sil in tokensalign_silences]

    # Ajouter les durées de tous les silences dans tokensalign_silences
    all_tokensalign_durations.extend([end - start for start, end in all_tokensalign])
    all_combined_duration.extend([end - start for start, end in combined_silences])

    # Accumuler les durées des silences pour le calcul global
    silence_durations["unique_combined"] += sum(
        end - start for start, end in unique_combined
    )
    silence_durations["unique_tokensalign"] += sum(
        end - start for start, end in unique_tokensalign
    )
    silence_durations["count_unique_combined"] += len(unique_combined)
    silence_durations["count_unique_tokensalign"] += len(unique_tokensalign)
    silence_durations["tokensalign"] += sum(
        end - start for start, end in all_tokensalign
    )
    silence_durations["count_tokensalign"] += len(all_tokensalign)
    silence_durations["combined"] += sum(
        end - start for start, end in combined_silences
    )
    silence_durations["count_combined"] += len(combined_silences)

    silence_durations.setdefault("short_combined", 0)
    silence_durations.setdefault("short_tokensalign", 0)

    has_short_pauses = False
    for c_sil in combined_silences:
        # Calculer la durée et vérifier si elle est inférieure à 100ms
        if (c_sil[1] - c_sil[0]) < 0.09:  # 10ms = 0.1 secondes
            silence_durations["short_combined"] += 1
            has_short_pauses = True

    for t_sil in tokensalign_silences:
        # Calculer la durée et vérifier si elle est inférieure à 100ms
        if (t_sil[1] - t_sil[0]) < 0.09:
            silence_durations["short_tokensalign"] += 1

    # Ajouter le fichier à la liste si des pauses courtes existent
    if has_short_pauses:
        files_with_short_pauses.append(os.path.basename(file_path))

    # Préparation des détails pour l'écriture dans le fichier individuel
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    individual_tsv_path = os.path.join(
        "TSV/silence_details_TALN/" + file + "/", base_name + "_details.tsv"
    )
    with open(individual_tsv_path, "w", newline="") as file:
        individual_writer = csv.writer(file, delimiter="\t")
        individual_writer.writerow(
            ["Category", "Start Time (second)", "End Time (second)"]
        )

        # Écrire les détails des silences
        for match in exact_matches:
            individual_writer.writerow(["Exact Match", match[0], match[1]])
        for overlap in partial_overlaps:
            individual_writer.writerow(
                ["Partial Overlap", overlap[0][0], overlap[0][1]]
            )
        for unique in unique_combined:
            individual_writer.writerow(["Unique in Gold", unique[0], unique[1]])
        for unique in unique_tokensalign:
            individual_writer.writerow(["Unique in Non Gold", unique[0], unique[1]])

    # Ajouter les données au fichier global sans les moyennes individuelles
    global_writer.writerow(
        [
            base_name,
            len(tokensalign_silences),
            len(combined_silences),
            len(exact_matches),
            len(partial_overlaps),
            len(unique_tokensalign),
            len(unique_combined),
            abs(len(combined_silences) - len(tokensalign_silences)),
        ]
    )


def get_totals_from_tsv(tsv_file_path: str) -> dict[str, int]:
    """
    Calcule les totaux des silences à partir d'un fichier TSV.

    Parameters:
    tsv_file_path (str): Chemin vers le fichier TSV.

    Returns:
    dict: Dictionnaire contenant les totaux des silences.
    """
    totals = {
        "Gold Silences": 0,
        "Non Gold Silences": 0,
        "Exact Matches": 0,
        "Partial Overlaps": 0,
        "Unique in Gold": 0,
        "Unique in Non Gold": 0,
    }

    with open(tsv_file_path, "r", newline="") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")
        for row in reader:
            for key in totals.keys():
                totals[key] += int(row[key])

    return totals


def histogramme_durees_silences(tier: list[float]) -> None:
    """
    Crée un histogramme des durées des silences.

    Parameters:
    tier (list): Liste des durées des silences.

    Returns:
    None

    Variables:
    bins (numpy.ndarray): Intervalles des bins de 0.2 en 0.2 secondes.
    """
    # Créer les intervalles des bins de 0.2 en 0.2 secondes
    bins = np.arange(0, 6.1, 0.1)

    # Créer l'histogramme avec seaborn
    plt.figure(figsize=(10, 6))
    ax = sns.histplot(tier, bins=bins, kde=False, edgecolor="black")
    ax.set_title("Histogramme des intervalles des pauses")
    ax.set_xlabel("Durée des silences (secondes)")
    ax.set_ylabel("Fréquence")
    ax.grid(True)
    ax.set_xlim(0, 6)

    # Ajouter les annotations
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Ajouter les annotations seulement pour les barres non nulles
            ax.annotate(
                f"{int(height)}",
                (p.get_x() + p.get_width() / 2, height),
                ha="center",
                va="bottom",
            )

    # Définir les positions des ticks sur l'axe x
    tick_positions = np.arange(0, 6.1, 0.1)
    ax.set_xticks(tick_positions)

    # Formatter pour n'afficher qu'une décimale
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}"))

    # Orienter les étiquettes à 45°
    ax.set_xticklabels([f"{tick:.1f}" for tick in tick_positions], rotation=45)

    plt.show()


def write_tsv_stat_from_textgrid(
    folder_path: str, tsv_file_path: str, file_tsv: str
) -> None:
    """
    Écrit les statistiques des silences dans les fichiers TextGrid dans un fichier TSV global.
    Calcule les durées moyennes des silences uniques et totaux dans Combined et TokensAlign.
    Compte les silences courts (durée < 10ms) dans Combined et TokensAlign.
    Crée un histogramme des durées des silences dans Combined et TokensAlign.

    Parameters:
    folder_path (str): Chemin vers le dossier contenant les fichiers TextGrid.
    tsv_file_path (str): Chemin vers le fichier TSV pour écrire les statistiques globales.
    file_tsv (str): Nom du fichier TSV pour écrire les détails des silences.

    Returns:
    None

    Variables:
    silence_durations (dict): Dictionnaire pour stocker les durées des silences.
    all_tokensalign_durations (list): Liste pour stocker les durées de tous les silences dans TokensAlign.
    all_combined_duration (list): Liste pour stocker les durées de tous les silences dans Combined.
    files_with_short_pauses (list): Liste pour stocker les noms des fichiers avec des silences courts.
    """
    silence_durations = {
        "unique_combined": 0,
        "unique_tokensalign": 0,
        "count_unique_combined": 0,
        "count_unique_tokensalign": 0,
        "tokensalign": 0,
        "count_tokensalign": 0,
        "combined": 0,
        "count_combined": 0,
        "short_combined": 0,
        "short_tokensalign": 0,
    }
    all_tokensalign_durations = []
    all_combined_duration = []
    files_with_short_pauses = []

    with open(tsv_file_path, "w", newline="") as global_file:
        global_writer = csv.writer(global_file, delimiter="\t")
        global_writer.writerow(
            [
                "File Name",
                "Gold Silences",
                "Non Gold Silences",
                "Exact Matches",
                "Partial Overlaps",
                "Unique in Gold",
                "Unique in Non Gold",
                "Difference",
            ]
        )

        for file in sorted(os.listdir(folder_path)):
            if file.endswith(".TextGrid"):
                file_path = os.path.join(folder_path, file)
                compare_silence(
                    file_path,
                    file_tsv,
                    global_writer,
                    silence_durations,
                    all_tokensalign_durations,
                    all_combined_duration,
                    files_with_short_pauses,
                )

    # Calculer et écrire/afficher les moyennes globales
    average_duration_combined_unique = (
        silence_durations["unique_combined"]
        / silence_durations["count_unique_combined"]
        if silence_durations["count_unique_combined"]
        else 0
    )
    average_duration_tokensalign_unique = (
        silence_durations["unique_tokensalign"]
        / silence_durations["count_unique_tokensalign"]
        if silence_durations["count_unique_tokensalign"]
        else 0
    )
    average_duration_tokensalign_all = (
        silence_durations["tokensalign"] / silence_durations["count_tokensalign"]
        if silence_durations["count_tokensalign"]
        else 0
    )
    average_duration_combined = (
        silence_durations["combined"] / silence_durations["count_combined"]
        if silence_durations["count_combined"]
        else 0
    )

    # Écrire les moyennes globales dans le fichier TSV ou les afficher
    print(
        f"Global Average Duration (Unique in Combined (Non Gold)): {average_duration_combined_unique} second"
    )
    print(
        f"Global Average Duration (Unique in Gold): {average_duration_tokensalign_unique} second"
    )
    print(
        f"Global Average Duration (All in Gold): {average_duration_tokensalign_all} second"
    )
    print(
        f"Global Average Duration (All in Combined (Non Gold)): {average_duration_combined} second\n"
    )

    print(
        f"Global Short Silences (Duration < 10ms) in Combined (Non Gold): {silence_durations['short_combined']}"
        f"\n{files_with_short_pauses}"
        f"\nGlobal Short Silences (Duration < 10ms) in Gold: {silence_durations['short_tokensalign']}\n"
    )

    # Créer et afficher l'histogramme des durées des silences
    histogramme_durees_silences(all_tokensalign_durations)
    histogramme_durees_silences(all_combined_duration)


def count_hashes_in_tsv_columns(tsv_file_path: str) -> tuple[int, int]:
    """
    Compte les # dans les colonnes Gold et Non-Gold d'un fichier TSV.

    Parameters:
    tsv_file_path (str): Chemin vers le fichier TSV.

    Returns:
    tuple: Nombre de # dans la colonne Gold et la colonne Non-Gold.
    """
    # Initialiser les compteurs pour chaque colonne
    gold_hashes = 0
    non_gold_hashes = 0

    with open(tsv_file_path, "r", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Sauter l'en-tête

        for row in reader:
            # print(row, row[1].count('#'), row[2].count('#'))
            # Compter les # dans la colonne Gold (index 1)
            gold_hashes += row[1].count("#")
            # Compter les # dans la colonne Non-Gold (index 2)
            non_gold_hashes += row[2].count("#")

    return gold_hashes, non_gold_hashes


def count_same_position_hashes(tsv_file_path: str) -> int:
    """
    Compte les # à la même position dans les phrases Gold et Non-Gold d'un fichier TSV.

    Parameters:
    tsv_file_path (str): Chemin vers le fichier TSV.

    Returns:
    int: Nombre de # à la même position dans les phrases Gold et Non-Gold.

    Variables:
    same_position_hashes_count (int): Compteur pour les # à la même position.
    """
    same_position_hashes_count = 0

    with open(tsv_file_path, "r", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header

        for row in reader:
            gold_phrase = row[1]
            non_gold_phrase = row[2]

            # Find positions of '#' in each phrase
            gold_hash_positions = [
                i for i, char in enumerate(gold_phrase) if char == "#"
            ]
            non_gold_hash_positions = [
                i for i, char in enumerate(non_gold_phrase) if char == "#"
            ]

            # Count '#' at the same positions in both phrases
            same_position_hashes_count += len(
                set(gold_hash_positions) & set(non_gold_hash_positions)
            )

    return same_position_hashes_count


def count_misplaced_hashes(tsv_file_path):
    """
    Compare les # n'ayant pas la même position dans les phrases Gold et Non-Gold d'un fichier TSV.

    Parameters:
    tsv_file_path (str): Chemin vers le fichier TSV.

    Returns:
    int: Nombre de # mal placés dans les phrases Gold et Non-Gold.

    Variables:
    misplaced_hashes_count (int): Compteur pour les # mal placés.
    """
    misplaced_hashes_count = 0

    with open(tsv_file_path, "r", newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip header

        for row in reader:
            gold_phrase = row[1]
            non_gold_phrase = row[2]

            # Trouver les positions de '#' dans chaque phrase
            gold_hash_positions = [
                i for i, char in enumerate(gold_phrase) if char == "#"
            ]
            non_gold_hash_positions = [
                i for i, char in enumerate(non_gold_phrase) if char == "#"
            ]

            # Trouver les # mal placés dans les phrases Gold et Non-Gold
            misplaced_hashes_count += len(
                set(non_gold_hash_positions) - set(gold_hash_positions)
            )

    return misplaced_hashes_count


def count_hashes_in_file(filepath: str) -> tuple[int, int, int, int]:
    """
    Compte les # dans les colonnes Gold et Non-Gold d'un fichier TSV.

    Parameters:
    filepath (str): Chemin vers le fichier TSV.

    Returns:
    tuple: Nombre de # dans la colonne Gold, la colonne Non-Gold, les # à la même position et les # mal placés.

    Variables:
    gold_hashes (int): Nombre de # dans la colonne Gold.
    non_gold_hashes (int): Nombre de # dans la colonne Non-Gold.
    same_position_hashes (int): Nombre de # à la même position.
    misplaced_hashes (int): Nombre de # mal placés.
    """
    if (
        filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/9pt_15ms/results_tsv-9pt_15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/2pt_15ms/results_tsv-2pt_15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/1pt_15ms/results_tsv-1pt_15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/8pt_15ms/results_tsv-8pt_15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/10pt_15ms/results_tsv-10pt_15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/10-05_05ms/results_tsv-10-05_05ms.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/15ms/results_tsv-15ms.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/15ms_02-04/results_tsv-15ms_02-04.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_entier/results_tsv-04-05_entier.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_10ms/results_tsv-04-05_10ms.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/9pt/results_tsv-9pt.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/1pt/results_tsv-1pt.tsv"
        and filepath
        != "TSV/TSV_sentences_gold_non_gold_TALN/entier/results_tsv-entier.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_webrtcvad/results_tsv-04-05_webrtcvad.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_10ms_webrtcvad2/results_tsv-04-05_10ms_webrtcvad2.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_10ms_webrtcvad3/results_tsv-04-05_10ms_webrtcvad3.tsv"
        and filepath != "TSV/TSV_sentences_gold_non_gold_TALN/04-05_webrtcvad3/results_tsv-04-05_webrtcvad3.tsv"
    ):

        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter="\t")
            gold_hashes = non_gold_hashes = same_position_hashes = misplaced_hashes = 0

            for row in reader:
                gold_text = row["Gold"]
                non_gold_text = row["Non-Gold"]
                gold_hash_positions = {
                    pos for pos, char in enumerate(gold_text) if char == "#"
                }
                non_gold_hash_positions = {
                    pos for pos, char in enumerate(non_gold_text) if char == "#"
                }

                gold_hashes += len(gold_hash_positions)
                non_gold_hashes += len(non_gold_hash_positions)
                same_positions = gold_hash_positions.intersection(
                    non_gold_hash_positions
                )
                same_position_hashes += len(same_positions)
                misplaced_hashes += len(
                    gold_hash_positions - non_gold_hash_positions
                ) + len(non_gold_hash_positions - gold_hash_positions)

            return gold_hashes, non_gold_hashes, same_position_hashes, misplaced_hashes


def process_all_tsv_files(directory: str, output_file: str = None) -> dict:
    """
    Compte les # dans les colonnes Gold et Non-Gold de chaque fichier TSV dans un répertoire.

    Parameters:
    directory (str): Chemin vers le répertoire contenant les fichiers TSV.
    output_file (str): Chemin vers le fichier de sortie pour écrire les statistiques.

    Returns:
    dict: Dictionnaire contenant les statistiques pour chaque fichier TSV.

    Variables:
    results (defaultdict): Dictionnaire pour stocker les statistiques.
    """
    results = defaultdict(
        lambda: {
            "gold_hashes": 0,
            "non_gold_hashes": 0,
            "same_position_hashes": 0,
            "misplaced_hashes": 0,
            "difference": 0,
        }
    )

    for root, dirs, files in os.walk(directory):
        for file in files:
            if (
                file != "all_sentences-9pt_15ms.tsv"
                and file != "all_sentences-8pt_15ms.tsv"
                and file != "all_sentences-10pt_15ms.tsv"
                and file != "all_sentences-10-05_05ms.tsv"
                and file != "all_sentences-15ms.tsv"
                and file != "all_sentences-15ms_02-04.tsv"
                and file != "all_sentences-9pt.tsv"
                and file != "all_sentences-entier.tsv"
                and file != "all_sentences-2pt_15ms.tsv"
                and file != "all_sentences-1pt_15ms.tsv"
                and file != "all_sentences-1pt.tsv"
                and file != "all_sentences-04-05_entier.tsv"
                and file != "all_sentences-04-05_10ms.tsv"
                and file != "all_sentences-04-05_webrtcvad.tsv"
                and file != "all_sentences-04-05_10ms_webrtcvad2.tsv"
                and file != "all_sentences-04-05_10ms_webrtcvad3.tsv"
                and file != "all_sentences-04-05_webrtcvad3.tsv"
                and file.endswith(".tsv")
            ):
                filepath = os.path.join(root, file)
                counts = count_hashes_in_file(filepath)
                if (
                    counts and len(counts) == 4
                ):  # Vérifiez que counts est une liste ou un tuple de longueur 4
                    results[file]["gold_hashes"] = counts[0]
                    results[file]["non_gold_hashes"] = counts[1]
                    results[file]["same_position_hashes"] = counts[2]
                    results[file]["misplaced_hashes"] = counts[3]
                    results[file]["difference"] = abs(counts[0] - counts[1])
                else:
                    print(f"Warning: failed to count hashes for file {file}")

    if output_file:
        with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
            fieldnames = [
                "Filename",
                "Gold Hashes",
                "Non-Gold Hashes",
                "Same Position Hashes",
                "Misplaced Hashes",
                "Difference",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter="\t")

            writer.writeheader()
            for filename, count_info in results.items():
                writer.writerow(
                    {
                        "Filename": filename,
                        "Gold Hashes": count_info["gold_hashes"],
                        "Non-Gold Hashes": count_info["non_gold_hashes"],
                        "Same Position Hashes": count_info["same_position_hashes"],
                        "Misplaced Hashes": count_info["misplaced_hashes"],
                        "Difference": count_info["difference"],
                    }
                )

    return dict(results)


def filter_files_by_hash_conditions(results: dict) -> list[str]:
    """
    Filtre les fichiers en fonction des conditions spécifiées pour les # dans les colonnes Gold et Non-Gold.

    Parameters:
    results (dict): Dictionnaire contenant les statistiques pour chaque fichier TSV.

    Returns:
    list: Liste des noms des fichiers qui correspondent aux conditions.

    Variables:
    matching_files (list): Liste pour stocker les noms des fichiers qui correspondent aux conditions.
    """
    # Liste pour stocker les noms des fichiers qui correspondent aux conditions
    matching_files = []

    # Parcourir les résultats pour chaque fichier
    for file_name, data in results.items():
        if file_name != "File Name":
            gold_hashes = data["gold_hashes"]
            non_gold_hashes = data["non_gold_hashes"]

            # Vérifier les conditions spécifiées
            if (
                gold_hashes == non_gold_hashes
                or gold_hashes == non_gold_hashes - 5
                or gold_hashes == non_gold_hashes + 5
            ):
                matching_files.append(file_name)

    return matching_files


def find_files_with_largest_hash_difference(results: dict) -> list[tuple[str, int]]:
    """
    Trouve les 4 fichiers avec la plus grande différence de # entre les colonnes Gold et Non-Gold.

    Parameters:
    results (dict): Dictionnaire contenant les statistiques pour chaque fichier TSV.

    Returns:
    list: Les 4 fichiers avec la plus grande différence de #.

    Variables:
    differences (list): Liste pour stocker les différences de # pour chaque fichier.
    top_4_files (list): Les 4 fichiers avec la plus grande différence de #.
    """
    # Calculer la différence absolue entre gold_hashes et non_gold_hashes pour chaque fichier
    differences = []
    for file_name, data in results.items():
        if (
            file_name != "all_sentences-9pt_15ms.tsv"
            and file_name != "results_tsv-9pt_15ms.tsv"
            and file_name != "all_sentences-15ms_02-04.tsv"
            and file_name != "results_tsv-15ms_02-04.tsv"
            and file_name != "all_sentences-04-05_entier.tsv"
            and file_name != "results_tsv-04-05_entier.tsv"
            and file_name != "all_sentences-04-05_10ms.tsv"
            and file_name != "results_tsv-04-05_10ms.tsv"
            and file_name != "all_sentences-10-05_05ms.tsv"
            and file_name != "results_tsv-10-05_05ms.tsv"
            and file_name != "all_sentences-15ms.tsv"
            and file_name != "results_tsv-15ms.tsv"
            and file_name != "all_sentences-entier.tsv"
            and file_name != "results_tsv-entier.tsv"
            and file_name != "all_sentences-9pt.tsv"
            and file_name != "results_tsv-9pt.tsv"
            and file_name != "all_sentences-8pt_15ms.tsv"
            and file_name != "results_tsv-8pt_15ms.tsv"
            and file_name != "all_sentences-10pt_15ms.tsv"
            and file_name != "results_tsv-10pt_15ms.tsv"
            and file_name != "all_sentences-2pt_15ms.tsv"
            and file_name != "results_tsv-2pt_15ms.tsv"
            and file_name != "all_sentences-1pt_15ms.tsv"
            and file_name != "results_tsv-1pt_15ms.tsv"
            and file_name != "all_sentences-1pt.tsv"
            and file_name != "results_tsv-1pt.tsv"
            and file_name != "all_sentences-04-05_webrtcvad.tsv"
            and file_name != "results_tsv-04-05_webrtcvad.tsv"
            and file_name != "all_sentences-04-05_10ms_webrtcvad2.tsv"
            and file_name != "results_tsv-04-05_10ms_webrtcvad2.tsv"
            and file_name != "all_sentences-04-05_10ms_webrtcvad3.tsv"
            and file_name != "results_tsv-04-05_10ms_webrtcvad3.tsv"
            and file_name != "all_sentences-04-05_webrtcvad3.tsv"
            and file_name != "results_tsv-04-05_webrtcvad3.tsv"
        ):

            difference = abs(data["gold_hashes"] - data["non_gold_hashes"])
            differences.append((file_name, difference))

    # Trier les fichiers par différence décroissante
    differences.sort(key=lambda x: x[1], reverse=True)

    # Sélectionner les 4 premiers fichiers
    top_4_files = differences[:4]

    return top_4_files


def calculer_pourcentages(fichier: str) -> pd.Series:
    """
    Calcule les pourcentages pour chaque métrique à partir d'un fichier TSV (Percentage : Exact Matches, Partial Overlap, Unique in Gold, Unique in Non Gold).

    Parameters:
    fichier (str): Chemin vers le fichier TSV.

    Returns:
    pandas.Series: Moyennes des pourcentages pour chaque métrique.

    Variables:
    data (pandas.DataFrame): Données chargées à partir du fichier TSV.
    """
    # Charger les données à partir du fichier TSV
    data = pd.read_csv(fichier, sep="\t")

    # Calculer le total des pauses Gold et Non-Gold
    data["Total Gold and Non Gold"] = data["Gold Silences"]

    # Calculer les pourcentages pour chaque métrique
    data["Percentage Exact Matches"] = (
        data["Exact Matches"] / data["Total Gold and Non Gold"]
    ) * 100
    data["Percentage Partial Overlaps"] = (
        data["Partial Overlaps"] / data["Total Gold and Non Gold"]
    ) * 100
    data["Percentage Unique in Gold"] = (
        data["Unique in Gold"] / data["Total Gold and Non Gold"]
    ) * 100
    data["Percentage Unique in Non Gold"] = (
        data["Unique in Non Gold"] / data["Total Gold and Non Gold"]
    ) * 100

    # Calculer les moyennes des pourcentages pour fournir une vue d'ensemble
    average_percentages = data[
        [
            "Percentage Exact Matches",
            "Percentage Partial Overlaps",
            "Percentage Unique in Gold",
            "Percentage Unique in Non Gold",
        ]
    ].mean()

    return average_percentages


def compter_phrases_avec_motif(fichier: str, motif: str) -> int:
    """
    Compte le nombre de phrases dans un fichier qui contiennent au moins une fois une expression correspondant au motif régulier fourni.

    Parameters:
    fichier (str): Chemin vers le fichier TSV.
    motif (str): Motif régulier pour rechercher dans les phrases.

    Returns:
    int: Nombre de phrases contenant le motif.

    Variables:
    pattern (re.Pattern): Expression régulière compilée pour améliorer les performances.
    count (int): Compteur pour les phrases contenant le motif.
    """
    # Compiler l'expression régulière pour améliorer les performances
    pattern = re.compile(motif)

    count = 0  # Initialiser le compteur

    with open(fichier, "r", encoding="utf-8") as file:
        next(file)  # Ignorer l'en-tête
        for line in file:
            columns = line.strip().split("\t")
            for col in columns[1:]:  # Analyser seulement les colonnes de texte
                if pattern.search(col):
                    count += 1
                    break  # Si trouvé, pas besoin de vérifier l'autre colonne pour cette ligne

    return count


def main():
    # Main processing

    # folder_path = "MERGED/gold_non_gold"
    # tsv_file_path = "TSV/combined-tokensalign_silences_TALN.tsv"
    # tsv_all_sentences = "TSV/TSV_sentences_gold_non_gold_TALN/all_sentences.tsv"
    file = "04-05_entier"
    folder_path = "MERGED/gold_non_gold_" + file
    tsv_file_path = "TSV/combined-tokensalign_silences_TALN-" + file + ".tsv"
    tsv_all_sentences = (
        "TSV/TSV_sentences_gold_non_gold_TALN/"
        + file
        + "/all_sentences-"
        + file
        + ".tsv"
    )
    sentences_folder = "TSV/TSV_sentences_gold_non_gold_TALN/" + file + "/"

    # Écrire les statistiques dans un fichier TSV
    write_tsv_stat_from_textgrid(folder_path, tsv_file_path, file)
    totals = get_totals_from_tsv(tsv_file_path)
    print("Total Counts:")
    for key, value in totals.items():
        print(f"{key}: {value}")
    print("\n")

    # Compter les # dans les colonnes Gold et Non-Gold
    gold_hashes, non_gold_hashes = count_hashes_in_tsv_columns(tsv_all_sentences)
    same_position_count = count_same_position_hashes(tsv_all_sentences)
    misplaced_count = count_misplaced_hashes(tsv_all_sentences)
    print(
        f"Gold hashes: {gold_hashes} \n",
        f"Non-Gold hashes: {non_gold_hashes} \n",
        f"Same position hashes: {same_position_count} \n",
        f"Misplaced hashes: {misplaced_count} \n",
    )

    results = process_all_tsv_files(sentences_folder)
    process_all_tsv_files(
        sentences_folder,
        "TSV/TSV_sentences_gold_non_gold_TALN/"
        + file
        + "/results_tsv-"
        + file
        + ".tsv",
    )

    matching_files = filter_files_by_hash_conditions(results)
    print("Files with the same gold_hashes and non_gold_hashes :", matching_files, "\n")

    # Calculer les pourcentages pour chaque fichier
    percentages = {}
    for file_name, data in results.items():
        if file_name in matching_files and file_name != "File Name":
            total_hashes = data[
                "gold_hashes"
            ]  # gold_hashes est égal à non_gold_hashes dans ces cas
            same_position_percentage = (
                data["same_position_hashes"] / total_hashes
            ) * 100
            misplaced_hashes_percentage = (
                data["misplaced_hashes"] / total_hashes
            ) * 100
            percentages[file_name] = {
                "same_position_percentage": round(same_position_percentage, 2),
                "misplaced_hashes_percentage": round(misplaced_hashes_percentage, 2),
            }

    print(
        "Pourcentages for each files with the same gold_hashes and non_gold_hashes :",
        percentages,
        "\n",
    )

    top_4_files = find_files_with_largest_hash_difference(results)
    print("Files with largest hash difference:", top_4_files, "\n")

    pourcentages = calculer_pourcentages(tsv_file_path)
    print(pourcentages)

    motif = r"\(\w+\)"
    nombre_phrases = compter_phrases_avec_motif(tsv_all_sentences, motif=r"\(\w+\)")
    print(f"Nombre de phrases avec le motif '{motif}':", nombre_phrases, "\n")


if __name__ == "__main__":
    main()
