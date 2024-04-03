from praatio import tgio
import os
from collections import defaultdict
from tqdm import tqdm

def pitchtier_count_silence_points(pitch_file, start, end):
    point_count = 0

    max_duration = 0
    with open(pitch_file, 'r') as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1])
                if start <= nombre <= end:
                    point_count += 1
                    if nombre > max_duration:
                        max_duration = nombre

    return point_count, max_duration

def merge_intervals(intervals):
    """ Merge consecutive non-silence intervals and rename labels. """
    merged_intervals = []
    i = 0
    while i < len(intervals):
        current_start, current_end, current_label = intervals[i]
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

def correct_silence_duration(textgrid, pitch_path, output):
    textgrid_ipus = tgio.openTextgrid(textgrid)

    new_intervals = []
    pitchtier_silence = defaultdict(dict)
    previous_ipu_end = None

    for ipu in textgrid_ipus.tierDict['IPUs'].entryList:
        ipu_start, ipu_end, ipu_label = ipu

        # If it's a silence interval with pitch points
        if "#" in ipu_label:
            count, new_max = pitchtier_count_silence_points(pitch_path, ipu_start, ipu_end)
            if count > 9:
                # Update the previous non-silence interval's end if needed
                if new_intervals and previous_ipu_end and new_intervals[-1][1] == previous_ipu_end:
                    new_intervals[-1] = (new_intervals[-1][0], new_max, new_intervals[-1][2])
                ipu_start = new_max  # Update this silence interval's start

        previous_ipu_end = ipu_end
        if ipu_start < ipu_end:
            new_intervals.append([ipu_start, ipu_end, ipu_label])
        else:
            print(f"Skipping interval with start >= end: {ipu_start} >= {ipu_end}")

    new_intervals = merge_intervals(new_intervals)  # Merge consecutive non-silence intervals
    new_intervals = rename_intervals(new_intervals)  # Rename intervals to maintain sequence

    new_ipus_textgrid = tgio.Textgrid()
    new_ipus_textgrid.addTier(tgio.IntervalTier("IPUs", new_intervals))
    new_ipus_textgrid.save(output)

    return pitchtier_silence

def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN/"
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
                pitch_path = os.path.join(pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier"))

                # if ipus_file_path == "./TEXTGRID_WAV_gold_non_gold_TALN/LAG_21/LAG_21_I-Like-Stout-ipus.TextGrid":
                correct_silence_duration(ipus_file_path, pitch_path, os.path.join(subdir_path, textgrid.replace("-ipus.TextGrid", "-ipus.TextGrid")))

if __name__ == "__main__":
    main()
