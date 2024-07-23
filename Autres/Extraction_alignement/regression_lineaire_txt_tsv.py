# Génère un fichier TSV contenant les résultats de la régression linéaire pour chaque syllabe dans un ensemble de fichiers texte.
# Les fréquences et les durées des syllabes sont utilisées pour effectuer une régression linéaire et calculer des caractéristiques telles que les coordonnées, les seuils de glissando, les nombres de demi-tons et les pentes.
# Les résultats sont enregistrés dans un fichier TSV avec des colonnes correspondant aux différentes caractéristiques pour chaque syllabe.
# Rapide si fichiers txt déjà créés sinon, il faut utiliser le programme regression_lineaire_dict_to_tsv.py, car pour la création de fichiers txt, le programme dure 1h (recuperation_point_pitchtier_save_txt_1h.py)
import os
import re
import csv
from sklearn.linear_model import LinearRegression
import numpy as np
from hertz_to_semitone import *
from tqdm import tqdm
import matplotlib.pyplot as plt


# Dossier contenant les fichiers txt
folder_path = '../PitchTier_TXT/syllabes_regression_lineaire'

# Ouvrir le fichier TSV en écriture
output_path = '../TSV/Regression_Lineaire.tsv'

with open(output_path, 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\t')

    # Écrire l'en-tête du fichier TSV
    columns = ['File', 'SentID', 'TokenID', 'Token']
    for i in range(1, 9):
        columns.extend([f'Syl{i}Coordonnee', f'Syl{i}Glissando', f'Syl{i}Semiton', f'Syl{i}Slope'])
    writer.writerow(columns)

    # Parcourir tous les fichiers dans le dossier
    for file_name in tqdm(os.listdir(folder_path)):
        if file_name.endswith('.txt'):
            with open(os.path.join(folder_path, file_name), 'r') as file:
                content = file.readlines()

                # Extraire l'identifiant de la phrase (SentID) du premier ligne du fichier
                sent_id = re.search(r'Sent_ID: (.*)', content[0]).group(1).strip()

                # Extraire l'identifiant du token (TokenID) du nom du fichier
                token_id = file_name.replace('.txt', '').split('__')[-1].split('_')[-1]

                # Extraire le token du deuxième ligne du fichier
                token = content[1].split(":")[-1].strip() if content[1].startswith('Token:') else 'X'

                row = [file_name, sent_id, token_id, token]
                content_str = " ".join(content)

                # Parcourir chaque syllabe (Syl1, Syl2, etc.) dans le fichier
                for i in range(1, 9):
                    match_values = re.search(f't1_syl{i}_form_values = (\[.*?\])', content_str)
                    match_nomb = re.search(f't1_syl{i}_form_nomb = (\[.*?\])', content_str)
                    if match_values and match_nomb:
                        # Convertir les valeurs de fréquence en Hz et les valeurs de temps en secondes
                        hertz = eval(match_values.group(1))
                        sec = eval(match_nomb.group(1))

                        # Effectuer la régression linéaire pour obtenir les coordonnées de la syllabe
                        model = LinearRegression().fit(np.array(sec).reshape(-1, 1), hertz)
                        coordonnee = (sec[0], sec[-1], hertz[0], hertz[-1])

                        # Calculer le seuil de glissando et le nombre de demi-tons
                        if sec[-1] - sec[0] != 0:
                            seuil_glissando = 0.16 /(sec[-1] - sec[0])
                        else:
                            seuil_glissando = 0
                        semiton = semitones_between(hertz[-1], hertz[0])

                        # Déterminer la pente (rise, fall, flat) en fonction du seuil de glissando et du semiton
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

                        # Ajouter les valeurs à la ligne du fichier TSV
                        row.extend([coordonnee, seuil_glissando, semiton, slope])

                        # Visualisation du graphe de la régression linéaire (rallonge le temps d'exécution du code)
                        # plt.figure()
                        # plt.scatter(sec, hertz, label='Données')
                        # plt.plot(sec, model.predict(np.array(sec).reshape(-1, 1)), color='red',
                        #          label='Régression linéaire')
                        # plt.xlabel('Temps (s)')
                        # plt.ylabel('Fréquence (Hz)')
                        # plt.title(f'{file_name} - Syllabe {i}')
                        # plt.legend()
                        # plt.savefig(f'../Regression_Lineaire/V2/graph_{file_name}_syl_{i}.png')
                        # plt.close()

                    else:
                        # Si les informations de la syllabe ne sont pas disponibles, ajouter des valeurs 'X'
                        row.extend(['X', 'X', 'X', 'X'])

                # Écrire la ligne dans le fichier TSV
                writer.writerow(row)
