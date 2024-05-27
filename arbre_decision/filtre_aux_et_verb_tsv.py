import csv
import random

# Définir le nom du fichier d'entrée et de sortie
fichier_entree = "./TSV/ArbreDecision/Sey-Say/arbre_decision_sey_say.tsv"
fichier_sortie = "./TSV/ArbreDecision/Sey-Say/arbre_decision_sey_say_filtre.tsv"


# Lire le fichier d'entrée
with open(fichier_entree, "r", encoding="utf-8") as f_entree:
    lecteur = csv.reader(f_entree, delimiter="\t")
    lignes_aux = []
    lignes_verb = []

    # Parcourir chaque ligne du fichier d'entrée
    for ligne in lecteur:
        form = ligne[0]
        pos = ligne[1]
        durationGlobal = ligne[2]
        durationLocal = ligne[3]
        durationNormalized = ligne[4]
        meanGlobal = ligne[5]
        meanLocal = ligne[6]
        meanNormalized = ligne[7]
        semitonFromUtterance = ligne[8]

        # Vérifier si la POS est AUX ou VERB
        # if pos == "AUX" and semitonFromUtterance != 'X' and durationNormalized != "X":
        #     lignes_aux.append(ligne)
        # elif pos == "VERB" and semitonFromUtterance != 'X' and durationNormalized != "X":
        #     lignes_verb.append(ligne)

        if form == "sey":
            lignes_aux.append(ligne)
        elif form == "say":
            lignes_verb.append(ligne)

# Sélectionner un nombre identique de lignes aléatoires pour chaque POS
nombre_lignes = min(len(lignes_aux), len(lignes_verb))
lignes_aux_aleatoires = random.sample(lignes_aux, nombre_lignes)
lignes_verb_aleatoires = random.sample(lignes_verb, nombre_lignes)

# Fusionner les lignes aléatoires
lignes_finales = lignes_aux_aleatoires + lignes_verb_aleatoires

# Mélanger l'ordre des lignes finales
random.shuffle(lignes_finales)

# Écrire les lignes finales dans le fichier de sortie avec toutes les autres colonnes
with open(fichier_sortie, "w", encoding="utf-8", newline="") as f_sortie:
    ecrivain = csv.writer(f_sortie, delimiter="\t")

    # Écrire l'en-tête du fichier (s'il y en a)
    # Assurez-vous de le modifier en fonction de votre fichier
    en_tete = ["Form",	"POS",	"DurationGlobal", "DurationLocal", "DurationNormalized", "MeanGlobal",	"MeanLocal",	"MeanNormalized",	"SemitonFromUtterance",	]
    ecrivain.writerow(en_tete)

    # Écrire les lignes finales dans le fichier de sortie
    for ligne in lignes_finales:
        ecrivain.writerow(ligne)
