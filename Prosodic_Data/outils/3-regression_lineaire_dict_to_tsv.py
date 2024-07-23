import os
import re
import glob
import csv
import numpy as np
from hertz_to_semitone import *
import urllib.request
from conll3 import *
from sklearn.linear_model import LinearRegression
from tqdm import tqdm
import matplotlib.pyplot as plt


def extract_occurrences_infos(file_path):
    # Liste pour stocker toutes les occurrences
    occurrences = []

    # Convertir le fichier conllu en arbres de dépendance
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    def extract_misc_info(misc, syl_num):
        """Extraire les informations pour une syllabe spécifique."""
        misc_dict = convert_misc_to_dict(misc)
        align_begin = misc_dict.get(f"Syl{syl_num}AlignBegin", "_")
        align_end = misc_dict.get(f"Syl{syl_num}AlignEnd", "_")
        slope_glo = misc_dict.get(f"Syl{syl_num}SlopeGlo", "_")
        slope_loc = misc_dict.get(f"Syl{syl_num}SlopeLoc", "_")
        duree = int(align_end) - int(align_begin) if align_end.isdigit() else 0
        return align_begin, align_end, slope_glo, slope_loc, duree

    for tree in trees:
        # Extraction des informations générales du sent_id et du texte de la phrase
        tree_str = str(tree)
        sent_id = re.search(r'# sent_id = (.+)', tree_str).group(1) if re.search(r'# sent_id = (.+)', tree_str) else "_"
        sent_text = re.search(r'# text = (.+)', tree_str).group(1) if re.search(r'# text = (.+)', tree_str) else ""

        for word in tree:
            pos = word.get("tag", "_")
            if pos != 'PUNCT':
                iD = word.get("id", "_")
                form = word.get("t", "_")
                misc = word.get("misc", "_")

                syllable_data = {}
                for syl_num in range(1, 9):
                    align_begin, align_end, slope_glo, slope_loc, duree = extract_misc_info(misc_T1, syl_num)
                    syllable_data.update({
                        f"align_begin_Syl{syl_num}": align_begin,
                        f"align_end_Syl{syl_num}": align_end,
                        f"syl{syl_num}_slope_glo": slope_glo,
                        f"syl{syl_num}_slope_loc": slope_loc,
                        f"duree_syl{syl_num}": duree,
                    })

                occurrence = {
                    "file_name": file_name,
                    "sent_id": sent_id,
                    "id": iD,
                    "form": form,
                    **syllable_data
                }
                occurrences.append(occurrence)

    return occurrences

# Fonction pour extraire toutes les occurrences des fichiers d'un répertoire
def extract_all_occurrences(directory_path):
    occurrences = []  # Liste pour stocker toutes les occurrences
    for root, dirs, files in os.walk(directory_path):
        if "non_gold" in dirs:
            dirs.remove("non_gold")
        for file in files:
            if file.endswith(".conllu") and "MG" in file:
                file_path = os.path.join(root, file)
                occurrences += extract_occurrences_infos(file_path)
    return occurrences

# Fonction pour convertir une chaîne de caractères au format "misc" en un dictionnaire
def convert_misc_to_dict(misc):
    result_dict = {}  # Dictionnaire pour stocker les informations supplémentaires
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

def extract_values_from_occurrences(text_data, txt_file_name, align_begin, align_end):
    valeurs_correspondantes = []
    nombres_correspondants = []

    file_data = text_data.get(txt_file_name + '.txt')
    if file_data is not None:
        for ligne in file_data:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1])
            elif "value =" in ligne:
                valeur = float(ligne.split('=')[1])
                if align_begin <= nombre <= align_end:
                    valeurs_correspondantes.append(valeur)
                    nombres_correspondants.append(nombre)

    return valeurs_correspondantes, nombres_correspondants

tsv_file_path = 'TSV/align_begin_align_end_syl_29_01.tsv'
text_files_directory= 'pitchtier_18janv/txt_syll/'
directory_path = "conllu_syllables_18janv/"

# Extraction de toutes les occurrences d'objets dans le répertoire donné
donnees = extract_all_occurrences(directory_path)

output_path = './TSV/Regression_Lineaire.tsv'

with open(output_path, 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\t')

    columns = ['File', 'SentID', 'TokenID', 'Token']
    for i in range(1, 9):
        columns.extend([f'Syl{i}Coordonnee', f'Syl{i}Glissando', f'Syl{i}Semiton', f'Syl{i}Slope'])
    writer.writerow(columns)

    text_data = {}  # Dictionnaire pour stocker les données des fichiers texte

    for file in glob.glob(text_files_directory + '/*.txt'):
        txt_file_name = os.path.basename(file)
        with open(file, 'r') as txt_file:
            text_data[txt_file_name] = txt_file.readlines()

    for occurrence in tqdm(donnees):
        file_name = occurrence['file_name']
        sent_id = occurrence['sent_id']
        token_id = occurrence['iD']
        token = occurrence['form']

        # Récupération du nom du fichier texte correspondant à l'occurrence
        if file_name.startswith('ABJ'):
            txt_file_name = '_'.join(file_name.split('_')[:3])
        else:
            txt_file_name = '_'.join(file_name.split('_')[:2])

        text_file_path = glob.glob(f"{text_files_directory}/{txt_file_name}.txt")[0]
        row = [file_name, sent_id, token_id, token]

        for i in range(1, 9):
            syl_key = f"Syl{i}"
            align_begin_key = occurrence[f'align_begin_{syl_key}']
            if align_begin_key != '_':
                align_begin = float(align_begin_key) / 1000
                align_end_key = occurrence[f'align_end_{syl_key}']
                align_end = float(align_end_key) / 1000 if align_end_key != '_' else None

                # Extraction des valeurs correspondantes dans les fichiers texte
                t1_form_values, nombres_correspondants = extract_values_from_occurrences(
                    text_data, txt_file_name, align_begin, align_end)

                # Calcul des coordonnées, seuil de glissando, semiton et pente
                if len(t1_form_values) > 0:
                    hertz = t1_form_values
                    sec = nombres_correspondants
                    model = LinearRegression().fit(np.array(sec).reshape(-1, 1), hertz)
                    coordonnee = (sec[0], sec[-1], hertz[0], hertz[-1])
                    if sec[-1] - sec[0] != 0:
                        seuil_glissando = 0.16 / (sec[-1] - sec[0])
                    else:
                        seuil_glissando = 0
                    semiton = semitones_between(hertz[-1], hertz[0])

                    if abs(semiton) > seuil_glissando and semiton > 0:
                        slope = 'Rise'
                    elif abs(semiton) > seuil_glissando and semiton < 0:
                        slope = 'Fall'
                    elif semiton == 0 and seuil_glissando == 0:
                        slope = 'X'
                    else:
                        slope = 'Flat'

                    semiton = round(semiton, 3)
                    seuil_glissando = round(seuil_glissando, 3)

                    if semiton == 0 and seuil_glissando == 0:
                        semiton, seuil_glissando = 'X', 'X'

                    row.extend([coordonnee, seuil_glissando, semiton, 3, slope])

                    # Visualisation du graphe de la régression linéaire (rallonge le temps d'exécution du code)
                    # plt.figure()
                    # plt.scatter(sec, hertz, label='Données')
                    # plt.plot(sec, model.predict(np.array(sec).reshape(-1, 1)), color='red',
                    #          label='Régression linéaire')
                    # plt.xlabel('Temps (s)')
                    # plt.ylabel('Fréquence (Hz)')
                    # plt.title(f'{file_name} - Syllabe {i}')
                    # plt.legend()
                    # plt.savefig(f'../Regression_Lineaire/png/graph_{file_name}_syl_{i}.png')
                    # plt.close()

                else:
                    row.extend(['X', 'X', 'X', 'X'])

        writer.writerow(row)