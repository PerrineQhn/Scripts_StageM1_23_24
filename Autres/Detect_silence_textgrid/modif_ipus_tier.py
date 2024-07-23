"""
Script pour la correction de la durée des intervalles de silence dans le fichier TextGrid des IPUs.

Requis:
- Les fichiers TextGrid des IPUs

Peut se lancer directement dans le terminal avec la commande:
python3 modif_ipus_tier.py

ou via le script 1-sppas_textgrid.py
"""

import os
from collections import defaultdict

from praatio import tgio
from tqdm import tqdm


def pitchtier_count_silence_points(pitch_file: str, start: float, end: float) -> tuple:
    """
    Compter les points de silence dans le fichier PitchTier.

    Parameters:
    - pitch_file (str): chemin du fichier PitchTier
    - start (float): la valeur de début
    - end (float): la valeur de fin

    Returns:
    - tuple: le nombre de points de silence

    Variables:
    - point_count (int): le nombre de points
    - point_list (list): la liste des points
    """
    point_count = 0
    point_list = []

    with open(pitch_file, "r") as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(
                    ligne.split("=")[1].strip()
                )  # Ensure any extra whitespace is removed
                if start <= nombre <= end:
                    point_count += 1
                    point_list.append(nombre)

    # print(f"Checked points from {start} to {end}: {point_count} points found, {point_list}, \nnew_start {new_start}, new_end {new_end}, new_interval {new_interval}\n")
    return point_list


def create_intervals_automatically(start: float, end: float, points: list) -> list:
    """
    Création d'intervalle de façon automatique avec la correction des intervalles #.

    Parameters:
    - start (float): la valeur de début
    - end (float): la valeur de fin
    - points (list): la liste des points

    Returns:
    - list: la liste des intervalles

    Variables:
    - intervals (list): la liste des intervalles
    - current_label (str): le label actuel
    - previous_point (float): le point précédent
    - list_points_continu (list): la liste des points continus
    """
    intervals = []
    current_label = "#"
    previous_point = start
    list_points_continu = []

    if points:
        # Initialisation pour le premier point
        if abs(points[0] - start) > 0.011:
            current_label = "#"
            # intervals.append([start, points[0], current_label])
        elif abs(points[0] - start) <= 0.011:
            current_label = "ipu_"
            list_points_continu.append(start)

        # Boucle à travers les points
        for point in points:
            # print(point, previous_point, abs(point - previous_point))
            if abs(point - previous_point) <= 0.011 and abs(point - end) > 0:
                if previous_point not in list_points_continu:
                    list_points_continu.append(previous_point)
                # print('ajout de point', point)
                list_points_continu.append(point)
            elif abs(point - previous_point) > 0.011:
                # print('hors de la liste', point)
                if list_points_continu:
                    # print('******************************liste de points', list_points_continu)
                    intervals.append(
                        [list_points_continu[0], list_points_continu[-1], "ipu_"]
                    )
                    list_points_continu = []

                intervals.append([previous_point, point, "#"])

            if point == points[-1]:
                if list_points_continu:
                    # print('******************************liste de points', list_points_continu)
                    if abs(end - points[-1]) > 0.011:
                        intervals.append(
                            [list_points_continu[0], list_points_continu[-1], "ipu_"]
                        )
                        intervals.append([list_points_continu[-1], end, "#"])
                    elif abs(end - points[-1]) <= 0.011:
                        intervals.append([list_points_continu[0], end, "ipu_"])

            previous_point = point

    # print('start', start, 'end', end, 'points', points, '\nintervals', intervals, '\n')

    return intervals


def correct_intervals_limite_duration(intervals: list, limite: float = 0.10) -> list:
    """
    Correction des intervalles avec une durée inférieure à 0.10s par défaut mais peut être modifié.

    Parameters:
    - intervals (list): liste des intervalles
    - limite (float): la limite de durée

    Returns:
    - list: liste des intervalles corrigés

    Variables:
    - corrected_intervals (list): liste des intervalles corrigés
    - previous_end (float): la valeur de fin précédente
    """
    corrected_intervals = []
    previous_end = 0
    for interval in intervals:
        start, end, label = interval
        if end - start < limite and label == "#":
            previous_end = start
            continue
        else:
            if start < previous_end:
                start = previous_end
            corrected_intervals.append([start, end, label])
            previous_end = end
    return corrected_intervals


def get_total_duration(textgrid_file: str) -> float:
    """
    Obtenir la durée totale du fichier TextGrid.

    Parameters:
    - textgrid_file (str): le chemin du fichier TextGrid

    Returns:
    - float: la durée totale

    Variables:
    - tier_list (list): la liste des intervalles de la tier "trans"
    """
    textgrid_tier = tgio.openTextgrid(textgrid_file)
    tier_list = textgrid_tier.tierDict["trans"].entryList
    # print(tier_list)

    return tier_list[-1][1]


def merge_intervals(intervals: list):
    """
    Fusionner les intervalles

    Parameters:
    - intervals (list): liste des intervalles

    Returns:
    - list: liste des intervalles fusionnés

    Variables:
    - merged_intervals (list): liste des intervalles fusionnés
    - i (int): l'index
    """
    merged_intervals = []
    i = 0
    while i < len(intervals):
        current_start, current_end, current_label = intervals[i]
        # print('\n ######## current_start', current_start, 'current_end', current_end, 'current_label', current_label)
        if current_end < current_start:
            # print(f"*-* Skipping interval with start >= end: {current_start} >= {current_end}")
            i += 1
            continue

        # Si l'intervalle actuel n'est pas un silence et qu'il y a un intervalle suivant
        if "#" not in current_label and i + 1 < len(intervals):
            # Initialise l'intervalle fusionné
            merged_start = current_start
            merged_label = current_label
            # Regarde si l'intervalle suivant est un silence
            while i + 1 < len(intervals) and "#" not in intervals[i + 1][2]:
                i += 1
                current_end = intervals[i][1]
            merged_intervals.append([merged_start, current_end, merged_label])

        # Si l'intervalle actuel est un silence et qu'il y a un intervalle suivant
        elif "#" in current_label and i + 1 < len(intervals):
            merged_start = current_start
            merged_label = "#"
            while i + 1 < len(intervals) and "#" in intervals[i + 1][2]:
                i += 1
                current_end = intervals[i][1]
            merged_intervals.append([merged_start, current_end, merged_label])

        else:
            # Si l'intervalle actuel est un silence ou s'il n'y a pas d'intervalle suivant
            merged_intervals.append([current_start, current_end, current_label])
        i += 1
    return merged_intervals


def rename_intervals(intervals: list) -> list:
    """
    Renommer les intervalles IPU en ipu_1, ipu_2, etc.

    Parameters:
    - intervals (list): liste des intervalles

    Returns:
    - list: liste des nouveaux intervalles

    Variables:
    - new_intervals (list): liste des nouveaux intervalles
    """
    new_intervals = []
    counter = 1
    for interval in intervals:
        start, end, label = interval
        if "#" in label:
            new_intervals.append([start, end, label])
        elif label == "*":
            new_intervals.append([start, end, "#"])
        else:
            new_label = f"ipu_{counter}"
            new_intervals.append([start, end, new_label])
            counter += 1
    return new_intervals


def correct_intervals(intervals: list) -> list:
    """
    Corrige les intervalles en fonction de la durée de l'intervalle précédent et suivant.
    Si start > end, start = end de l'intervalle précédent et end = start de l'intervalle suivant.

    Parameters:
    - intervals (list): liste des intervalles

    Returns:
    - list: liste des intervalles corrigés

    Variables:
    - corrected_intervals (list): liste des intervalles corrigés
    - previous_end (float): la valeur de fin précédente
    """
    corrected_intervals = []
    previous_end = 0
    for i, interval in enumerate(intervals):
        start, end, label = interval
        if start >= end:
            start = previous_end
            if i + 1 < len(intervals):
                end = intervals[i + 1][0]
            else:
                end = (
                    start + 0.01
                )  # Ensure there's a minimal duration for the last interval
        previous_end = end
        corrected_intervals.append([start, end, label])
    return corrected_intervals


def correct_silence_duration(
    textgrid_file: str, ipu_textgrid: str, pitch_path: str, output: str
) -> dict:
    """
    Correction de la durée des intervalles de silence.

    Parameters:
    - textgrid_file (str): chemin du fichier TextGrid
    - ipu_textgrid (str): chemin du fichier TextGrid des IPUs
    - pitch_path (str): chemin du fichier PitchTier
    - output (str): chemin du fichier de sortie

    Returns:
    - dict: dictionnaire des points de silence

    Variables:
    - textgrid_ipus (Textgrid): le fichier TextGrid des IPUs
    - new_intervals (list): la liste des nouveaux intervalles
    - ipu_intervals (list): la liste des intervalles des IPUs
    - pitchtier_silence (dict): le dictionnaire des points de silence
    - previous_ipu_end (float): la valeur de fin précédente
    - total_duration (float): la durée totale
    - count_ipu (int): le nombre d'IPUs
    - interval_count (int): le compteur des intervalles
    - ipu (list): l'intervalle IPU
    - ipu_start (float): la valeur de début de l'IPU
    - ipu_end (float): la valeur de fin de l'IPU
    - ipu_label (str): le label de l'IPU
    - point_list (list): la liste des points de silence
    """
    textgrid_ipus = tgio.openTextgrid(ipu_textgrid)
    new_intervals = []
    ipu_intervals = textgrid_ipus.tierDict["IPUs"].entryList
    pitchtier_silence = defaultdict(dict)
    previous_ipu_end = 0

    total_duration = get_total_duration(textgrid_file)

    count_ipu = len(ipu_intervals)
    interval_count = 0

    for ipu in ipu_intervals:

        if previous_ipu_end:
            ipu_start = previous_ipu_end
        else:
            ipu_start = ipu[0]

        ipu_end, ipu_label = ipu[1], ipu[2]
        interval_count += 1

        if interval_count == count_ipu - 1:
            ipu_end = total_duration

        if "#" in ipu_label:
            point_list = pitchtier_count_silence_points(pitch_path, ipu_start, ipu_end)

            if point_list:
                new_intervals.extend(
                    create_intervals_automatically(ipu_start, ipu_end, point_list)
                )

            # Update the end of the previous non-silence interval if necessary
            if (
                previous_ipu_end
                and new_intervals
                and new_intervals[-1][1] == previous_ipu_end
            ):
                new_intervals[-1][1] = ipu_start

        else:
            new_intervals.append([ipu_start, ipu_end, ipu_label])

        if ipu_end > previous_ipu_end:
            previous_ipu_end = ipu_end

        # print('-------Previous IPU end:', previous_ipu_end, '\n')

        if ipu_start < ipu_end:
            print(
                f"Interval {interval_count}/{count_ipu}: {ipu_start} to {ipu_end} ({ipu_end - ipu_start} s) - {ipu_label}"
            )
        else:
            print(f"Skipping interval with start >= end: {ipu_start} >= {ipu_end}")
            continue

    if new_intervals[0][0] != 0.0:
        new_intervals.insert(0, [0.0, new_intervals[0][0], "#"])

    for i in range(1, len(new_intervals)):
        if new_intervals[i - 1][1] < new_intervals[i][0]:
            new_intervals.insert(i, [new_intervals[i - 1][1], new_intervals[i][0], "*"])

    new_intervals = rename_intervals(new_intervals)
    new_intervals = merge_intervals(new_intervals)
    new_intervals = correct_intervals_limite_duration(new_intervals, limite=0.10)
    new_intervals = merge_intervals(new_intervals)
    new_intervals = rename_intervals(new_intervals)
    # print('new_intervals', new_intervals, '\n')

    new_intervals = correct_intervals(new_intervals)
    # print('new_intervals_2', new_intervals, '\n')

    for interval in new_intervals:
        if interval[0] >= interval[1]:
            print(
                f"Anomaly: startTime={interval[0]}, stopTime={interval[1]}, label={interval[2]}"
            )
            interval[1] = interval[0] + 0.01

    for i in range(1, len(new_intervals)):
        if new_intervals[i - 1][1] > new_intervals[i][0]:
            new_intervals[i][0] = new_intervals[i - 1][1]

    new_ipus_textgrid = tgio.Textgrid()
    new_ipus_textgrid.addTier(tgio.IntervalTier("IPUs", new_intervals))
    new_ipus_textgrid.save(output)

    return pitchtier_silence


def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad3/"
    pitchtier_folder = "./Praat/"

    for subdir in tqdm(os.listdir(base_folder)):
        subdir_path = os.path.join(base_folder, subdir)
        if os.path.isdir(subdir_path):
            ipus = []

            for file in os.listdir(subdir_path):
                if file.endswith("-ipus.TextGrid"):
                    ipus.append(file)

            for textgrid in ipus:
                ipus_file_path = os.path.join(subdir_path, textgrid)
                # print(ipus_file_path)
                textgrid_file = ipus_file_path.replace("-ipus.TextGrid", ".TextGrid")
                # print(textgrid_file)
                pitch_path = os.path.join(
                    pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier")
                )

                if (
                    ipus_file_path
                    == "./TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad3/ABJ_GWA_03/ABJ_GWA_03_Cost-Of-Living-In-Abuja_MG-ipus.TextGrid"
                ):
                    print(f"Processing {ipus_file_path}")
                    correct_silence_duration(
                        textgrid_file,
                        ipus_file_path,
                        pitch_path,
                        os.path.join(
                            subdir_path,
                            textgrid.replace("-ipus.TextGrid", "-new_ipus.TextGrid"),
                        ),
                    )


if __name__ == "__main__":
    main()
