from praatio import tgio
import os
from collections import defaultdict
from tqdm import tqdm

def pitchtier_count_silence_points(pitch_file, start, end):
    point_count = 0
    max_duration = start  # Initialize to start to ensure we get a value at least as large as start

    with open(pitch_file, 'r') as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1].strip())  # Ensure any extra whitespace is removed
                if start <= nombre <= end:
                    point_count += 1
                    if nombre > max_duration:
                        max_duration = nombre

    # print(f"Checked points from {start} to {end}: {point_count} points found, max duration {max_duration}")
    return point_count, max_duration

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

def correct_silence_duration(textgrid_file, ipu_textgrid, pitch_path, output):
    textgrid_ipus = tgio.openTextgrid(ipu_textgrid)
    new_intervals = []
    ipu_intervals = textgrid_ipus.tierDict['IPUs'].entryList
    pitchtier_silence = defaultdict(dict)
    previous_ipu_end = None

    total_duration = get_total_duration(textgrid_file)
    # print(f"Total duration: {total_duration}")
    
    count_ipu = len(ipu_intervals)
    # print(f"Number of intervals: {count_ipu}")
    interval_count = 0

    for ipu in ipu_intervals:
        ipu_start, ipu_end, ipu_label = ipu

        interval_count += 1

        # print("Current Count: ", interval_count)
        if interval_count == count_ipu-1:
            ipu_end = total_duration
            # print(f"Last interval: {ipu_label} from {ipu_start} to {ipu_end}")

        # Handle silence intervals
        if "#" in ipu_label:
            count, new_max = pitchtier_count_silence_points(pitch_path, ipu_start, ipu_end)
            if count < 1:
                # Ajust the end of the silence interval if less than 9 points are found
                if new_max > ipu_start:
                    ipu_start = new_max  # Move the start of the silence interval to the last pitch point
            elif count > 1:
                # Delete the silence interval if more than 9 points are found
                # No need to add it to the new intervals list
                continue
            
            # print(f"Adjusting {ipu_label} from {ipu_start} to {ipu_end} based on pitch points")

        # Update the end of the previous non-silence interval if necessary
        if previous_ipu_end and new_intervals and new_intervals[-1][1] == previous_ipu_end:
            new_intervals[-1][1] = ipu_start

        previous_ipu_end = ipu_end

        if ipu_start < ipu_end:
            new_intervals.append([ipu_start, ipu_end, ipu_label])
        else:
            print(f"Skipping interval with start >= end: {ipu_start} >= {ipu_end}")

    # Merge and rename intervals after all adjustments
    new_intervals = merge_intervals(new_intervals)
    new_intervals = rename_intervals(new_intervals)

    # Save the adjusted TextGrid
    new_ipus_textgrid = tgio.Textgrid()
    new_ipus_textgrid.addTier(tgio.IntervalTier("IPUs", new_intervals))
    new_ipus_textgrid.save(output)

    return pitchtier_silence

def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_2pt_15ms/"
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
                textgrid_file = textgrid.replace("-ipus.TextGrid", ".TextGrid")
                pitch_path = os.path.join(pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier"))

                # if ipus_file_path == "./TEXTGRID_WAV_gold_non_gold_TALN/LAG_21/LAG_21_I-Like-Stout-ipus.TextGrid":
                correct_silence_duration(textgrid_file, ipus_file_path, pitch_path, os.path.join(subdir_path, textgrid.replace("-ipus.TextGrid", "-ipus.TextGrid")))

if __name__ == "__main__":
    main()
