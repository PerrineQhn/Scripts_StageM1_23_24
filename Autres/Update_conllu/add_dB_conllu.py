import os
import re

# Chemin du dossier contenant les fichiers CoNLL-U
conllu_folder = "../SUD_Naija-NSC-master"

# Chemin du fichier TSV
tsv_file = "../TSV/align_begin_align_end_syl_dB.tsv"

def lire_fichier_tsv(chemin):
    # Lit le contenu du fichier TSV et retourne une liste de lignes
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

# Lire le fichier TSV et construire un dictionnaire
lignes_tsv = lire_fichier_tsv(tsv_file)
lignes_tsv_dict = {}
for ligne_tsv in lignes_tsv:
    colonnes_tsv = [colonne.strip() for colonne in ligne_tsv.split("\t")]
    avgamplitude = [str(colonnes_tsv[i]) for i in range(31, 46, 2)]
    #print("avg : ", avgamplitude)
    maxamplitude = [str(colonnes_tsv[i]) for i in range(32, 47, 2)]
    #print("max :", maxamplitude)
    fichier_conllu = colonnes_tsv[0].strip()
    sent_id_conllu = colonnes_tsv[1].strip()
    token_id = colonnes_tsv[2].strip()
    if fichier_conllu not in lignes_tsv_dict:
        lignes_tsv_dict[fichier_conllu] = {}
    if sent_id_conllu not in lignes_tsv_dict[fichier_conllu]:
        lignes_tsv_dict[fichier_conllu][sent_id_conllu] = {}
    lignes_tsv_dict[fichier_conllu][sent_id_conllu][token_id] = {"maxamplitude": maxamplitude, "avgamplitude": avgamplitude}
    #print(lignes_tsv_dict)
    
# Parcourir les fichiers CoNLL-U dans le dossier spécifié
valid_extensions = {".conllu"}
for fichier_conllu in os.listdir(conllu_folder):
    if fichier_conllu.endswith(tuple(valid_extensions)):
        chemin_conllu = os.path.join(conllu_folder, fichier_conllu)
        if fichier_conllu in lignes_tsv_dict:
            mettre_a_jour_fichier_conllu(chemin_conllu, lignes_tsv_dict[fichier_conllu])
