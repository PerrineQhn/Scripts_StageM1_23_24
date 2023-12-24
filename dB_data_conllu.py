import parselmouth
import numpy as np
import pandas as pd
import os
import glob
from tqdm import tqdm
import re

# Functions from recup_dB.py
def is_floatable(value):
    """ Check if a value can be converted to float. """
    try:
        float(value)
        return True
    except ValueError:
        return False

def calculate_amplitudes(audio_file, start_time, end_time):
    """ Calculate max and average amplitude of an audio segment. """
    try:
        sound = parselmouth.Sound(audio_file)
        segment = sound.extract_part(from_time=start_time, to_time=end_time)
        amplitudes = segment.to_intensity().values.T
        return np.max(amplitudes), np.mean(amplitudes)
    except Exception as e:
        return 0, 0

def process_audio_files_to_tsv(tsv_file_path, audio_base_path):
    """ Process audio files and save amplitude data to TSV. """
    # Load TSV file
    tsv_data = pd.read_csv(tsv_file_path, sep='\t')
    tsv_data.columns = [col.strip() for col in tsv_data.columns]

    # Add columns for amplitudes
    for syl_num in range(1, 9):
        tsv_data[f'Syl{syl_num}AvgAmplitude'] = np.nan
        tsv_data[f'Syl{syl_num}MaxAmplitude'] = np.nan

    # Iterate over TSV rows
    for index, row in tqdm(tsv_data.iterrows(), desc="Processing audio files", total=len(tsv_data)):
        file_base = '_'.join(row['File'].split('_')[:2])
        if row['File'].startswith('ABJ'):
            file_base = '_'.join(row['File'].split('_')[:3])

        folder_paths = glob.glob(os.path.join(audio_base_path, file_base + '*'))
        if folder_paths:
            folder_path = folder_paths[0]
            audio_file_paths = glob.glob(os.path.join(folder_path, '*.wav'))
            if audio_file_paths:
                audio_file_path = audio_file_paths[0]

                for syl_num in range(1, 9):
                    start_col_name = f'T1_Syl{syl_num}AlignBegin'
                    end_col_name = f'T1_Syl{syl_num}AlignEnd'
                    if is_floatable(row[start_col_name]) and is_floatable(row[end_col_name]):
                        start_time = float(row[start_col_name]) / 1000
                        end_time = float(row[end_col_name]) / 1000
                        max_amp, avg_amp = calculate_amplitudes(audio_file_path, start_time, end_time)
                    else:
                        max_amp, avg_amp = 0, 0

                    tsv_data.loc[index, f'Syl{syl_num}AvgAmplitude'] = avg_amp
                    tsv_data.loc[index, f'Syl{syl_num}MaxAmplitude'] = max_amp

    # Save modified DataFrame
    output_path = tsv_file_path.replace('.tsv', '_dB.tsv')
    tsv_data.to_csv(output_path, sep='\t', index=False)
    return output_path

# Functions from add_dB_conllu.py
def lire_fichier_tsv(chemin):
    """ Read TSV file content and return a list of lines. """
    with open(chemin, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    return lignes

def mettre_a_jour_fichier_conllu(fichier_conllu, lignes_tsv_dict):
    # Lit le contenu du fichier CoNLL-U et retourne une liste de lignes
    with open(fichier_conllu, "r", encoding="utf-8") as f:
        lignes = f.readlines()

    # Met à jour les lignes du fichier CoNLL-U avec les données de MaxAmplitude et AvgAmplitude
    for i, ligne in enumerate(lignes):
        if ligne.startswith("# sent_id"):
            sent_id_conllu = ligne.split("=")[1].strip()
        elif not ligne.startswith("#"):
            colonnes = ligne.split("\t")
            token_id = colonnes[0]
            nb_syllabe_match = re.search(r"SyllableCount=(\d+)", colonnes[-1])
            nb_syllabe = int(nb_syllabe_match.group(1)) if nb_syllabe_match else 0
            misc_elements = colonnes[-1].rstrip("\n").split("|")
            
            # Conserve l'ordre et élimine les doublons
            misc_set = set()
            misc_ordered = [x for x in misc_elements if not (x in misc_set or misc_set.add(x))]

            if sent_id_conllu in lignes_tsv_dict and token_id in lignes_tsv_dict[sent_id_conllu]:
                MaxAmplitude = lignes_tsv_dict[sent_id_conllu][token_id]["maxamplitude"]
                AvgAmplitude = lignes_tsv_dict[sent_id_conllu][token_id]["avgamplitude"]

                # Ajoute les informations de MaxAmplitude et AvgAmplitude pour chaque syllabe à la fin
                for k, (maxAmplitude, avgAmplitude) in enumerate(zip(MaxAmplitude, AvgAmplitude)):
                    if k < nb_syllabe:
                        maxAmplitude_rounded = round(float(maxAmplitude), 3)
                        avgAmplitude_rounded = round(float(avgAmplitude), 3)
                        if maxAmplitude != '0.0':
                            misc_ordered.append(f"Syl{k + 1}MaxAmplitude={maxAmplitude_rounded}")
                        else:
                            misc_ordered.append(f"Syl{k + 1}MaxAmplitude=X")
                        if avgAmplitude != '0.0':
                            misc_ordered.append(f"Syl{k + 1}AvgAmplitude={avgAmplitude_rounded}")
                        else:
                            misc_ordered.append(f"Syl{k + 1}AvgAmplitude=X")

                # Met à jour la ligne dans la liste des lignes
                colonnes[-1] = "|".join(misc_ordered) + '\n'
                lignes[i] = "\t".join(colonnes)

    # Écrit les lignes mises à jour dans le fichier CoNLL-U
    try:
        with open(fichier_conllu, "w", encoding="utf-8") as f:
            f.write("".join(lignes))
            print("Écriture dans le fichier CoNLL-U réussie :", fichier_conllu)
    except Exception as e:
        print("Erreur lors de l'écriture dans le fichier CoNLL-U :", str(e))

def update_conllu_files_with_amplitudes_with_tsv(tsv_file, conllu_folder):
    """ Update CoNLL-U files with amplitude data from TSV. """
    lignes_tsv = lire_fichier_tsv(tsv_file)
    lignes_tsv_dict = {}
    for ligne_tsv in lignes_tsv:
        colonnes_tsv = [colonne.strip() for colonne in ligne_tsv.split("\t")]
        avgamplitude = [str(colonnes_tsv[i]) for i in range(31, 46, 2)]
        maxamplitude = [str(colonnes_tsv[i]) for i in range(32, 47, 2)]
        fichier_conllu = colonnes_tsv[0].strip()
        sent_id_conllu = colonnes_tsv[1].strip()
        token_id = colonnes_tsv[2].strip()
        if fichier_conllu not in lignes_tsv_dict:
            lignes_tsv_dict[fichier_conllu] = {}
        if sent_id_conllu not in lignes_tsv_dict[fichier_conllu]:
            lignes_tsv_dict[fichier_conllu][sent_id_conllu] = {}
        lignes_tsv_dict[fichier_conllu][sent_id_conllu][token_id] = {"maxamplitude": maxamplitude, "avgamplitude": avgamplitude}

    valid_extensions = {".conllu"}
    for fichier_conllu in os.listdir(conllu_folder):
        if fichier_conllu.endswith(tuple(valid_extensions)):
            chemin_conllu = os.path.join(conllu_folder, fichier_conllu)
            if fichier_conllu in lignes_tsv_dict:
                mettre_a_jour_fichier_conllu(chemin_conllu, lignes_tsv_dict[fichier_conllu])

def update_conllu_with_amplitudes(conllu_file, audio_base_path):
    """ Update CoNLL-U file directly with amplitude data. """
    # Read CoNLL-U file
    with open(conllu_file, "r", encoding="utf-8") as f:
        lignes = f.readlines()
        #print(lignes)

    for i, ligne in enumerate(lignes):
        if ligne.startswith("# sent_id"):
            sent_id_conllu = ligne.split("=")[1].strip()
            file_base = '_'.join(sent_id_conllu.split('_')[:2])
            if sent_id_conllu.startswith('ABJ'):
                file_base = '_'.join(sent_id_conllu.split('_')[:3])
            folder_paths = glob.glob(os.path.join(audio_base_path, file_base + '*'))
            if folder_paths:
                folder_path = folder_paths[0]
                audio_file_paths = glob.glob(os.path.join(folder_path, '*.wav'))
                if audio_file_paths:
                    audio_file_path = audio_file_paths[0]
        elif not ligne.startswith("#"):
            colonnes = ligne.split("\t")
            token_id = colonnes[0]
            nb_syllabe_match = re.search(r"SyllableCount=(\d+)", colonnes[-1])
            nb_syllabe = int(nb_syllabe_match.group(1)) if nb_syllabe_match else 0
            misc_elements = colonnes[-1].rstrip("\n").split("|")
            misc_dict = {elem.split('=')[0]: elem.split('=')[1] for elem in misc_elements if '=' in elem}

            misc_set = set()
            misc_ordered = [x for x in misc_elements if not (x in misc_set or misc_set.add(x))]

            for syl_num in range(1, nb_syllabe + 1):
                start_syl_key = f'Syl{syl_num}AlignBegin'
                end_syl_key = f'Syl{syl_num}AlignEnd'
                
                if start_syl_key in misc_dict and end_syl_key in misc_dict:
                    start_time = float(misc_dict[start_syl_key]) / 1000
                    end_time = float(misc_dict[end_syl_key]) / 1000
                    max_amp, avg_amp = calculate_amplitudes(audio_file_path, start_time, end_time)
                else:
                    max_amp, avg_amp = 0, 0

                max_amp_rounded = round(max_amp, 3)
                avg_amp_rounded = round(avg_amp, 3)
                if max_amp != 0.0:
                    misc_ordered.append(f"Syl{syl_num}MaxAmplitude={max_amp_rounded}")
                else:
                    misc_ordered.append(f"Syl{syl_num}MaxAmplitude=X")
                if avg_amp != 0.0:
                    misc_ordered.append(f"Syl{syl_num}AvgAmplitude={avg_amp_rounded}")
                else:
                    misc_ordered.append(f"Syl{syl_num}AvgAmplitude=X")

            colonnes[-1] = "|".join(misc_ordered) + '\n'
            lignes[i] = "\t".join(colonnes)

    # Write updated lines to CoNLL-U file
    try:
        with open(conllu_file, "w", encoding="utf-8") as f:
            f.write("".join(lignes))
            print("Updated CoNLL-U file successfully:", conllu_file)
    except Exception as e:
        print("Error updating CoNLL-U file:", str(e))

# Main execution
if __name__ == '__main__':
    # Define file paths and folders
    tsv_file_path = '../TSV/align_begin_align_end_syl.tsv'
    audio_base_path = '../TEXTGRID_WAV/'
    conllu_folder = '../SUD_Naija-NSC-master_test'

    # # Process audio files and generate TSV with amplitude data
    # output_tsv_path = process_audio_files_to_tsv(tsv_file_path, audio_base_path)

    # # Update CoNLL-U files with amplitude data from TSV
    # update_conllu_files_with_amplitudes_with_tsv(output_tsv_path, conllu_folder)

    # Update CoNLL-U files with amplitude data directly
    for conllu_file in tqdm(os.listdir(conllu_folder), desc="Updating CoNLL-U files"):
        if conllu_file.endswith('.conllu'):
            update_conllu_with_amplitudes(os.path.join(conllu_folder, conllu_file), audio_base_path)

