"""
Script permettant d'obtenir les IPU, les tokens, les syllabes, les transcriptions phonétiques et les alignements à partir de fichier .wav et .TextGrid fournis.

Requis:
- SPPAS
- Praat
- TextGrid ayant la transcription de l'audio dans un intervalle nommé "trans"
- Fichier .wav de l'audio

Commande:
python3 ./Python_Stage_23_24/detect_silence_textgrid/1-sppas_textgrid.py
"""

import os
import subprocess

from modif_ipus_tier import *
from tqdm import tqdm


def save_textgrid_praat():
    """
    Sauvegarder via praat pour avoir le bon format de fichier TextGrid

    Parameters:
    None

    Returns:
    None

    Variables:
    praat_executable (str): le chemin vers l'exécutable de Praat
    praat_script (str): le chemin vers le script Praat
    """
    praat_executable = "/Applications/Praat.app/Contents/MacOS/Praat"
    praat_script = "/Users/perrine/Desktop/Stage_2023-2024/PRAAT/script/save_new.praat"

    try:
        print("Exécution de Praat pour sauvegarder les fichiers TextGrid")
        result = subprocess.run(
            [praat_executable, "--run", praat_script],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Sortie de Praat :", textgrid_file)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Praat : {e}")
        print(e.output)


# Chemin du dossier contenant les fichiers .wav et .TextGrid
# base_folder = "./TEXTGRID_WAV"
base_folder = "./TEXTGRID_WAV_nongold"
base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad3"
praat_folder = "./Praat/non_gold"

# Itérer à travers tous les sous-dossiers
for subdir in tqdm(os.listdir(base_folder)):
    subdir_path = os.path.join(base_folder, subdir)

    # Si le sous-dossier est un dossier
    if os.path.isdir(subdir_path):
        # Listes pour stocker les noms des fichiers .wav et .TextGrid
        wav_files = []
        textgrid_files = []

        # Itérer à travers tous les fichiers du sous-dossier
        for file in os.listdir(subdir_path):
            if file.endswith(".wav"):
                wav_files.append(file)
            elif file.endswith("_M.TextGrid") or file.endswith("_MG.TextGrid"):
                textgrid_files.append(file)

        # Exécutez la commande pour chaque paire de fichiers correspondants
        for wav_file in wav_files:
            # Construire le nom du fichier .TextGrid correspondant
            textgrid_file = wav_file.replace(".wav", ".TextGrid")

            if textgrid_file in textgrid_files:
                # Construire les chemins des fichiers .wav et .TextGrid
                wav_file_path = os.path.join(subdir_path, wav_file)
                textgrid_file_path = os.path.join(subdir_path, textgrid_file)

                # # Construire la commande pour exécuter SPPAS
                # if (
                #     wav_file_path
                #     == "./TEXTGRID_WAV_nongold/ENU_07/ENU_07_South-Eastern-Politics_M.wav"
                # ):
                    # print(wav_file_path, textgrid_file_path)

                # Commande permettant d'obtenir les IPU
                # command1 = f"python3 ./SPPAS-4/sppas/bin/searchipus.py -I {wav_file_path} -e .TextGrid --min_ipu 0.02 --min_sil 0.1"
                # subprocess.run(command1, shell=True)

                # ipu_filepath = os.path.join(
                #     subdir_path, wav_file.replace(".wav", "-ipus.TextGrid")
                # )
                # textgrid_filepath = os.path.join(
                #     subdir_path, wav_file.replace(".wav", ".TextGrid")
                # )
                # pitch_path = os.path.join(
                #     praat_folder, wav_file.replace(".wav", ".PitchTier")
                # )

                # # Script pour modifier le tier IPU et corriger la durée des silences, supprimer les silences de moins de 0.1s
                # correct_silence_duration(
                #     textgrid_filepath,
                #     ipu_filepath,
                #     pitch_path,
                #     os.path.join(
                #         subdir_path, wav_file.replace(".wav", "-ipus.TextGrid")
                #     ),
                # )

                # Commande permettant d'obtenir les tokens, syllabes, transcriptions phonétiques et alignements
                command2 = f"python3 ./SPPAS-4/sppas/bin/annotation.py -I {wav_file_path} -I {textgrid_file_path} -l pcm -e .TextGrid --textnorm --phonetize --alignment --syllabify"
                subprocess.run(command2, shell=True)

# Commande permettant de sauvegarder le fichier au bon format TextGrid via Praat
save_textgrid_praat()

print("Fin de l'exécution")
