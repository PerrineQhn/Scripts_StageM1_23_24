import os
import re

# Chemin du dossier contenant les fichiers CoNLL-U
conllu_folder = "conllu_syllables_18janv/"

# Chemin du fichier TSV
tsv_file = "TSV/align_begin_align_end_syl_29_01_hertz.tsv"

def lire_fichier_tsv(chemin):
    # Lit le contenu du fichier TSV et retourne une liste de lignes
    with open(chemin, "r", encoding="utf-8") as f:
        lignes = f.readlines()
    return lignes

def mettre_a_jour_fichier_conllu(fichier_conllu, lignes_tsv_dict):
    # Lit le contenu du fichier CoNLL-U et retourne une liste de lignes
    with open(fichier_conllu, "r", encoding="utf-8") as f:
        lignes = f.readlines()

    # Met à jour les lignes du fichier CoNLL-U avec les données de dureesyl et moyennesyl
    for i, ligne in enumerate(lignes):
        if ligne.startswith("# sent_id"):
            sent_id_conllu = ligne.split("=")[1].strip()
        elif not ligne.startswith("#"):
            colonnes = ligne.split("\t")
            token_id = colonnes[0]
            nb_syllabe_match = re.search(r"SyllableCount=(\d+)", colonnes[-1])
            nb_syllabe = int(nb_syllabe_match.group(1)) if nb_syllabe_match else 0  # Récupère le nombre de syllabes ou défini sur 0 si pas de correspondance
            misc_elements = colonnes[-1].rstrip("\n").split("|")
            
            # Conserve l'ordre et élimine les doublons
            misc_set = set()
            misc_ordered = [x for x in misc_elements if not (x in misc_set or misc_set.add(x))]

            if sent_id_conllu in lignes_tsv_dict and token_id in lignes_tsv_dict[sent_id_conllu]:
                # print(sent_id_conllu)
                colonnes[-1] = "|".join(set(colonnes[-1].split("|")))
                moyennehertz = lignes_tsv_dict[sent_id_conllu][token_id]["moyennehertz"]
                moyennesem = lignes_tsv_dict[sent_id_conllu][token_id]["moyennesem"]
                moyennehertz_sent = lignes_tsv_dict[sent_id_conllu][token_id]["moyennehertz_sent"]

                for k, moyenneH in enumerate(moyennehertz):
                    moyenneH_rounded = round(float(moyenneH), 3)
                    if k < nb_syllabe:
                        if k+1 == 1:
                            if moyenneH != '0.0':
                                misc_ordered.append(f"Syl{k + 1}MeanF0={moyenneH_rounded}")
                            else:
                                misc_ordered.append(f"Syl{k + 1}MeanF0=X")
                        else:
                            if moyenneH != '0.0':
                                misc_ordered.append(f"Syl{k + 1}MeanF0={moyenneH_rounded}")
                            else:
                                misc_ordered.append(f"Syl{k + 1}MeanF0=X")
                        
                # # Ajoute l'information de F0Enonce une seule fois si "root" est présent
                # if "root" in colonnes[7]:
                #     f0_enonce = float(moyennehertz_sent[0])
                #     f0_enonce_rounded = round(f0_enonce, 3)
                #     misc_ordered.append(f"|UtteranceMeanF0={f0_enonce_rounded}")
                    
                        
                # Ajoute les informations de moyennesem pour chaque syllabe
                for k, moyenne in enumerate(moyennesem):
                    if k < nb_syllabe:
                        if moyenne != '':
                            misc_ordered.append(f"Syl{k + 1}SemitonesFromUtteranceMean={moyenne}")
                   
                # Met à jour la ligne dans la liste des lignes
                colonnes[-1] = "|".join(misc_ordered) + '\n'
                lignes[i] = "\t".join(colonnes)
            
                # print(colonnes[-1])
                

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
    colonnes_tsv = ligne_tsv.split("\t")
    fichier_conllu = colonnes_tsv[0]
    moyennehertz = [str(colonnes_tsv[i]) for i in range(47, 61, 2)]
    moyennesem = [str(colonnes_tsv[i]) for i in range(48, 62, 2)]
    moyennehertz_sent = [colonnes_tsv[-1]]
    sent_id_conllu = colonnes_tsv[1]
    token_id = colonnes_tsv[2]
    if fichier_conllu not in lignes_tsv_dict:
        lignes_tsv_dict[fichier_conllu] = {}
    if sent_id_conllu not in lignes_tsv_dict[fichier_conllu]:
        lignes_tsv_dict[fichier_conllu][sent_id_conllu] = {}
    lignes_tsv_dict[fichier_conllu][sent_id_conllu][token_id] = {"moyennesem": moyennesem, "moyennehertz":moyennehertz, "moyennehertz_sent": moyennehertz_sent}

# Parcourir les fichiers CoNLL-U dans le dossier spécifié
valid_extensions = {".conllu"}
for fichier_conllu in os.listdir(conllu_folder):
    if fichier_conllu.endswith(tuple(valid_extensions)):
        chemin_conllu = os.path.join(conllu_folder, fichier_conllu)
        # Récupérer les données de dureesyl et moyennesyl du fichier TSV correspondant
        if fichier_conllu in lignes_tsv_dict:
            mettre_a_jour_fichier_conllu(chemin_conllu, lignes_tsv_dict[fichier_conllu])
