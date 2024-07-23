import os
import re

# Chemin du dossier contenant les fichiers CoNLL-U
conllu_folder = "conllu_syllables_18janv/"

# Chemin du fichier TSV
tsv_file = "TSV/Regression_Lineaire.tsv"

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
            nb_syllabe = int(nb_syllabe_match.group(1)) if nb_syllabe_match else 0
            colonnes[-1] = colonnes[-1].rstrip("\n")

            if sent_id_conllu in lignes_tsv_dict and token_id in lignes_tsv_dict[sent_id_conllu]:
                colonnes[-1] = "|".join(set(colonnes[-1].split("|")))
                semiton = lignes_tsv_dict[sent_id_conllu][token_id]["semiton"]
                syl_slope = lignes_tsv_dict[sent_id_conllu][token_id]["syl_slope"]


                # for k, Semiton in enumerate(semiton):
                #     if k < nb_syllabe:
                #         colonnes[-1] += f"|Syl{k + 1}Semiton={Semiton}"

                for k, Syl_Slope in enumerate(syl_slope):
                    if k < nb_syllabe:
                        Syl_Slope = Syl_Slope.replace('\n', "")
                        colonnes[-1] += f"|Syl{k + 1}Slope={Syl_Slope}"

                colonnes[-1] += '\n'
                # Met à jour la ligne dans la liste des lignes
                lignes[i] = "\t".join(colonnes)
                #print(colonnes)

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
    # print(ligne_tsv)
    colonnes_tsv = ligne_tsv.split("\t")
    fichier_conllu = colonnes_tsv[0]
    fichier_conllu = fichier_conllu.split('__')[0]+'.conllu'
    semiton = [str(colonnes_tsv[i]) for i in range(5, 26, 3)]
    # print("semition : ", semiton)
    syl_slope =[str(colonnes_tsv[i]) for i in range(6, 27, 3)]
    # print("syl_slope: ",syl_slope)
    sent_id_conllu = colonnes_tsv[1]
    token_id = colonnes_tsv[2]
    if fichier_conllu not in lignes_tsv_dict:
        lignes_tsv_dict[fichier_conllu] = {}
    if sent_id_conllu not in lignes_tsv_dict[fichier_conllu]:
        lignes_tsv_dict[fichier_conllu][sent_id_conllu] = {}
    lignes_tsv_dict[fichier_conllu][sent_id_conllu][token_id] = {"syl_slope": syl_slope, "semiton": semiton}

# Parcourir les fichiers CoNLL-U dans le dossier spécifié
valid_extensions = {".conllu"}
for fichier_conllu in os.listdir(conllu_folder):
    if fichier_conllu.endswith(tuple(valid_extensions)):
        chemin_conllu = os.path.join(conllu_folder, fichier_conllu)
        # Récupérer les données de dureesyl et moyennesyl du fichier TSV correspondant
        if fichier_conllu in lignes_tsv_dict:
            mettre_a_jour_fichier_conllu(chemin_conllu, lignes_tsv_dict[fichier_conllu])
