import os
import subprocess
from tqdm import tqdm
from modif_ipus_tier import *


# Path to the folder containing subfolders
# base_folder = "./TEXTGRID_WAV"
# base_folder = "./TEXTGRID_WAV_nongold"
base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_1pt"
praat_folder = "./Praat"

# Iterate through all the subfolders
for subdir in tqdm(os.listdir(base_folder)):
    subdir_path = os.path.join(base_folder, subdir)

    # Check if the item is a folder
    if os.path.isdir(subdir_path):
        # List to store the names of .wav and .TextGrid files
        wav_files = []
        textgrid_files = []

        # Iterate through all files in the subfolder
        for file in os.listdir(subdir_path):
            if file.endswith(".wav"):
                wav_files.append(file)
            elif file.endswith("MG.TextGrid"):
                textgrid_files.append(file)

        # Execute the command for each pair of corresponding files
        for wav_file in wav_files:
            # Construct the corresponding .TextGrid file name
            textgrid_file = wav_file.replace(".wav", ".TextGrid")

            if textgrid_file in textgrid_files:
                # Construct the full path of the files
                wav_file_path = os.path.join(subdir_path, wav_file)
                textgrid_file_path = os.path.join(subdir_path, textgrid_file)

                # Construct and execute the first command
                # if wav_file_path == "./TEXTGRID_WAV_gold_non_gold_TALN_2pt_15ms/WAZL_15/WAZL_15_MC-Abi_MG.wav":
                # print(wav_file_path, textgrid_file_path)
                command1 = f"python3 ./SPPAS-4_1/sppas/bin/searchipus.py -I {wav_file_path} -e .TextGrid --min_ipu 0.02 --min_sil 0.1"
                subprocess.run(command1, shell=True)

                ipu_filepath = os.path.join(subdir_path, wav_file.replace(".wav", "-ipus.TextGrid"))
                textgrid_filepath = os.path.join(subdir_path, wav_file.replace(".wav", ".TextGrid"))
                pitch_path = os.path.join(praat_folder, wav_file.replace(".wav", ".PitchTier"))
                correct_silence_duration(textgrid_filepath, ipu_filepath, pitch_path, os.path.join(subdir_path, wav_file.replace(".wav", "-ipus.TextGrid")))

                command = f"python3 ./SPPAS-4_1/sppas/bin/annotation.py -I {wav_file_path} -I {textgrid_file_path} -l pcm -e .TextGrid --textnorm --phonetize --alignment --syllabify"
                subprocess.run(command, shell=True)

