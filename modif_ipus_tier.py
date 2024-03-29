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
            if count > 0:
                # Update the previous non-silence interval's end if needed
                if new_intervals and previous_ipu_end and new_intervals[-1][1] == previous_ipu_end:
                    new_intervals[-1] = (new_intervals[-1][0], new_max, new_intervals[-1][2])
                ipu_start = new_max  # Update this silence interval's start

        previous_ipu_end = ipu_end
        if ipu_start < ipu_end:
            new_intervals.append([ipu_start, ipu_end, ipu_label])
        else:
            print(f"Skipping interval with start >= end: {ipu_start} >= {ipu_end}")

    new_ipus_textgrid = tgio.Textgrid()
    new_ipus_textgrid.addTier(tgio.IntervalTier("New IPUs", new_intervals))
    new_ipus_textgrid.save(output)

    return pitchtier_silence

def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN/"
    pitchtier_folder = "./Praat/"

    for subdir in tqdm(os.listdir(base_folder)):
        subdir_path = os.path.join(base_folder, subdir)

        if os.path.isdir(subdir_path):
            sil_tok = []

            for file in os.listdir(subdir_path):
                if file.endswith("ipus.TextGrid"):
                    sil_tok.append(file)

            for textgrid in sil_tok:
                sil_tok_path = os.path.join(subdir_path, textgrid)
                pitch_path = os.path.join(pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier"))

                correct_silence_duration(sil_tok_path, pitch_path, os.path.join(subdir_path, textgrid.replace("-ipus.TextGrid", "-new_ipus.TextGrid")))

if __name__ == "__main__":
    main()
