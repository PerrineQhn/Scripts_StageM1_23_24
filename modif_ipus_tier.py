from praatio import tgio
import os
from collections import defaultdict
from tqdm import tqdm


def pitchtier_count_silence_points(pitch_file: str, start: float, end: float) -> tuple:
    """
    si |start - first_number| > 0.1 et chaque points liste on une différence de 0.1 par rapport au points précédent et |end-last_number| <= 0.1 , alors le end = le dernier point.
    si |start - first_number| <= 0.1 et |end-last_number| > 0.1 et chaque points liste on une différence de 0.1 par rapport au points précédent, alors le start = le dernier point.
    si |start - first_number| > 0.1 et |end - last_number| > 0.1 et chaque points liste on une différence de 0.1 par rapport au points précédent, 
    alors modification de l'intervalle # et ajout d'un intervale IPU et #, #_1 start = start et end = first_number, IPU start = first_number end = last_number et #_2 start = last_number end = end.
    si |s-fist_number| <= 0.1 et |end - last_number| <= 0.1 et dans la liste il y a deux points qui se suivent mais qui ont une différence > 0.1 (ex: nombre3 et nombre4), alors start = nombre3 et end = nombre4.

    Parameters:
    - pitch_file (str): the path to the PitchTier file
    - start (float): the start value
    - end (float): the end value

    Returns:
    - tuple: Adjusted end time, start time, number of points, and a flag indicating if a new interval is needed.
    """
    point_count = 0
    point_list = []
    
    with open(pitch_file, 'r') as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1].strip())  # Ensure any extra whitespace is removed
                if start <= nombre <= end:
                    point_count += 1
                    point_list.append(nombre)

    # print(f"Checked points from {start} to {end}: {point_count} points found, {point_list}, \nnew_start {new_start}, new_end {new_end}, new_interval {new_interval}\n")
    return point_list

def create_intervals_automatically(start, end, points):
    """Automatically create intervals based on points."""
    intervals = []
    current_label = '#'
    previous_point = start
    list_points_continu = []

    if points:
        # Initialisation pour le premier point
        if abs(points[0] - start) > 0.011:
            current_label = '#'
            # intervals.append([start, points[0], current_label])
        elif abs(points[0] - start) <= 0.011:
            current_label = 'ipu_'
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
                    intervals.append([list_points_continu[0], list_points_continu[-1], 'ipu_'])
                    list_points_continu = []
            
                intervals.append([previous_point, point, '#'])

            if point == points[-1]:
                if list_points_continu:
                    # print('******************************liste de points', list_points_continu)
                    if abs(end - points[-1]) > 0.011:
                        intervals.append([list_points_continu[0], list_points_continu[-1], 'ipu_'])
                        intervals.append([list_points_continu[-1], end, '#'])
                    elif abs(end - points[-1]) <= 0.011:
                        intervals.append([list_points_continu[0], end, 'ipu_'])

            previous_point = point
        
    # print('start', start, 'end', end, 'points', points, '\nintervals', intervals, '\n')
    
    return intervals

def correct_intervals_limite_duration(intervals, limite=0.15):
    """ 
    Correct intervals with end-start < 0.15 for #. 
    If end-start < 0.15, we skip the interval and the next start of the next interval is egal to the end before the skip interval.
    """
    corrected_intervals = []
    previous_end = 0
    for interval in intervals:
        start, end, label = interval
        if end - start < limite and label == '#':
            previous_end = start
            continue
        else:
            if start < previous_end:
                start = previous_end
            corrected_intervals.append([start, end, label])
            previous_end = end
    return corrected_intervals

def get_total_duration(textgrid_file):
    """Retrieve the total duration from a PitchTier file."""
    textgrid_tier = tgio.openTextgrid(textgrid_file)
    tier_list = textgrid_tier.tierDict['trans'].entryList
    # print(tier_list)

    return tier_list[-1][1]

def merge_intervals(intervals):
    """ Merge consecutive non-silence intervals and rename labels. """
    merged_intervals = []
    i = 0
    while i < len(intervals):
        current_start, current_end, current_label = intervals[i]
        # print('\n ######## current_start', current_start, 'current_end', current_end, 'current_label', current_label)
        if current_end < current_start:
            # print(f"*-* Skipping interval with start >= end: {current_start} >= {current_end}")
            i += 1
            continue

        # If the current interval is non-silence and not the last one
        if "#" not in current_label and i + 1 < len(intervals):
            # Initialize merged interval data
            merged_start = current_start
            merged_label = current_label
            # Look ahead to find the end of the consecutive non-silence intervals
            while i + 1 < len(intervals) and "#" not in intervals[i + 1][2]:
                i += 1
                current_end = intervals[i][1]
            merged_intervals.append([merged_start, current_end, merged_label])

        elif "#" in current_label and i + 1 < len(intervals):
            merged_start = current_start
            merged_label = '#'
            while i + 1 < len(intervals) and "#" in intervals[i + 1][2]:
                i += 1
                current_end = intervals[i][1]
            merged_intervals.append([merged_start, current_end, merged_label])

        else:
            # If it's a silence interval or there are no more intervals to check
            merged_intervals.append([current_start, current_end, current_label])
        i += 1
    return merged_intervals

def rename_intervals(intervals):
    """ Rename intervals to maintain numbering after merging. """
    new_intervals = []
    counter = 1
    for interval in intervals:
        start, end, label = interval
        if "#" in label:
            new_intervals.append([start, end, label])
        else:
            new_label = f"ipu_{counter}"
            new_intervals.append([start, end, new_label])
            counter += 1
    return new_intervals

def correct_intervals(intervals):
    """ Correct intervals with start >= end 
    if start > end, start = end de l'intervalle précédent. et end = start de l'intervalle suivant."""
    corrected_intervals = []
    previous_end = 0
    for interval in intervals:
        start, end, label = interval
        if start >= end:
            start = previous_end
            end = intervals[intervals.index(interval) + 1][0]
        previous_end = end
        corrected_intervals.append([start, end, label])
    return corrected_intervals

def correct_silence_duration(textgrid_file, ipu_textgrid, pitch_path, output):
    textgrid_ipus = tgio.openTextgrid(ipu_textgrid)
    new_intervals = []
    ipu_intervals = textgrid_ipus.tierDict['IPUs'].entryList
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

        if interval_count == count_ipu-1:
            ipu_end = total_duration

        if "#" in ipu_label:
            point_list = pitchtier_count_silence_points(pitch_path, ipu_start, ipu_end)

            if point_list:
                new_intervals.extend(create_intervals_automatically(ipu_start, ipu_end, point_list))

            # Update the end of the previous non-silence interval if necessary
            if previous_ipu_end and new_intervals and new_intervals[-1][1] == previous_ipu_end:
                new_intervals[-1][1] = ipu_start

        else:
            new_intervals.append([ipu_start, ipu_end, ipu_label])
        
        if ipu_end > previous_ipu_end:
            previous_ipu_end = ipu_end
        
        # print('-------Previous IPU end:', previous_ipu_end, '\n')

        if ipu_start < ipu_end:
            print(f"Interval {interval_count}/{count_ipu}: {ipu_start} to {ipu_end} ({ipu_end - ipu_start} s) - {ipu_label}")
        else:
            print(f"Skipping interval with start >= end: {ipu_start} >= {ipu_end}")
            continue

    if new_intervals[0][0] != 0.0:
        new_intervals.insert(0, [0.0, new_intervals[0][0], '#'])
    
    # for i in range(1, len(new_intervals)):
    #     if new_intervals[i-1][1] < new_intervals[i][0]:
    #         new_intervals.insert(i, [new_intervals[i-1][1], new_intervals[i][0], '*'])

    
    new_intervals = correct_intervals_limite_duration(new_intervals, limite=0.10)
    new_intervals = merge_intervals(new_intervals)
    new_intervals = rename_intervals(new_intervals)
    # print('new_intervals', new_intervals, '\n')

    new_intervals = correct_intervals(new_intervals)
    # print('new_intervals_2', new_intervals, '\n')

    new_ipus_textgrid = tgio.Textgrid()
    new_ipus_textgrid.addTier(tgio.IntervalTier("IPUs", new_intervals))
    new_ipus_textgrid.save(output)

    return pitchtier_silence

def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms/"
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
                pitch_path = os.path.join(pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier"))

                if ipus_file_path == "./TEXTGRID_WAV_gold_non_gold_TALN_15ms_02-04/BEN_36/BEN_36_Clever-Girl_MG-ipus.TextGrid":
                    correct_silence_duration(textgrid_file, ipus_file_path, pitch_path, os.path.join(subdir_path, textgrid.replace("-ipus.TextGrid", "-new_ipus.TextGrid")))

if __name__ == "__main__":
    main()
