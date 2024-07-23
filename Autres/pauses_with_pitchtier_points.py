from praatio import tgio
import os
from collections import defaultdict
from tqdm import tqdm

def pitchtier_count_silence_points(pitch_file, start, end):
    point_count = 0

    with open(pitch_file, 'r') as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1])
                if start <= nombre <= end:
                    point_count += 1

    return point_count

def get_silence_duration(textgrid, pitch_path):
    filename = textgrid.split("/")[-1].replace(".TextGrid", "")
    textgrid_syl_tok = tgio.openTextgrid(textgrid)


    pitchtier_silence = defaultdict(dict)

    for interval in textgrid_syl_tok.tierDict['IPUs'].entryList:
        if "#" in interval[2]:
            xmin = interval[0]
            xmax = interval[1]

            valeur_durée = str(f"{xmin} - {xmax}")
            count = pitchtier_count_silence_points(pitch_path, xmin, xmax)

            # if count != 0:
            pitchtier_silence[filename][valeur_durée] = count

    return pitchtier_silence

            


def write_tsv(file_path, data):
    with open(file_path, "w") as f:
        f.write("filename\tdurée\tcount\n")

        for filename in data:
            for durée in data[filename]:
                f.write(f"{filename}\t{durée}\t{data[filename][durée]}\n")



def main():
    base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_9pt_15ms/"
    tsv_folder = "./TSV/"

    all_pitchtier_silence = defaultdict(dict)

    pitchtier_folder = "./Praat/"

    for subdir in tqdm(os.listdir(base_folder)):
        subdir_path = os.path.join(base_folder, subdir)

        # Check if the item is a folder
        if os.path.isdir(subdir_path):
            sil_tok = []

            for file in os.listdir(subdir_path):
                if file.endswith("ipus.TextGrid"):
                    sil_tok.append(file)

            for textgrid in sil_tok:
                sil_tok_path = os.path.join(subdir_path, textgrid)
                pitch_path = os.path.join(pitchtier_folder, textgrid.replace("-ipus.TextGrid", ".PitchTier"))

                pitchtier_silence = get_silence_duration(sil_tok_path, pitch_path)

                all_pitchtier_silence.update(pitchtier_silence)

    write_tsv(tsv_folder + "silence_duration_pitchtier_points_ipu_9pt_15ms.tsv", all_pitchtier_silence)

if __name__ == "__main__":
    main()

