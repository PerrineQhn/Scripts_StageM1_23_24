"""
Ce script a pour vocation d'extraire des fichiers TextGrid les informations nécessaires pour l'alignement des tokens.

Requis:
- Fichier TextGrid avec tokens
- Fichier CoNLL-U avec transcription
"""

import csv
import os
import subprocess

from praatio import tgio


def save_textgrid_praat(textgrid_dir):
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
    praat_script = "/Users/perrine/Desktop/Stage_2023-2024/Praat/script/new_save.praat"

    try:
        print("Exécution de Praat pour sauvegarder les fichiers TextGrid")
        result = subprocess.run(
            [praat_executable, "--run", praat_script],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Sortie de Praat : Success")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Praat : {e}")
        print("Code de retour :", e.returncode)
        print("Sortie standard :", e.stdout)
        print("Erreur standard :", e.stderr)


def extraction_sentences_conllu(path_to_conllu_file):
    """
    Extraction des phrases du fichier CoNLL-U

    Parameters:
    path_to_conllu_file (str): le chemin vers le fichier CoNLL-U

    Returns:
    conllu_dict (dict): un dictionnaire avec les phrases extraites (clé: nom du fichier, valeur: sentences_id et sentences_text)
    """
    conllu_dict = {}
    with open(path_to_conllu_file, "r") as f:
        sent_id = ""
        for line in f:
            if line.startswith("# sent_id = "):
                sent_id = line.split("=")[1].strip()
                file_name = sent_id.split("__")[0]
                if file_name not in conllu_dict:
                    conllu_dict[file_name] = {}
            if line.startswith("# text = "):
                # print("line", sent_id, line)
                if sent_id not in conllu_dict[file_name]:
                    conllu_dict[file_name][sent_id] = []

                conllu_dict[file_name][sent_id].append(line.split(" =")[1])
    return conllu_dict


def extraction_tokens_textgrid(textgrid_file):
    """
    Extraction des tokens du fichier TextGrid

    Parameters:
    textgrid_file (str): le chemin vers le fichier TextGrid

    Returns:
    tokens (list): une liste des tokens extraits
    """
    if not os.path.exists(textgrid_file):
        raise FileNotFoundError(f"Le fichier TextGrid n'existe pas: {textgrid_file}")

    tg = tgio.openTextgrid(textgrid_file)
    # print("tg tiers:", tg.tierNameList)

    if "TokensAlign" not in tg.tierNameList:
        raise ValueError(
            f"Tier 'TokensAlign' non trouvé dans le fichier {textgrid_file}"
        )

    tokens_tier = tg.tierDict["TokensAlign"]

    tokens = []
    for interval in tokens_tier.entryList:
        label, xmin, xmax = interval[2], interval[0], interval[1]
        tokens.append((label, xmin, xmax))
    return tokens


def extraction_syllabes_textgrid(textgrid_file):
    """
    Extraction des syllabes du fichier TextGrid

    Parameters:
    textgrid_file (str): le chemin vers le fichier TextGrid

    Returns:
    syllabes (list): une liste des syllabes extraits
    """
    if not os.path.exists(textgrid_file):
        raise FileNotFoundError(f"Le fichier TextGrid n'existe pas: {textgrid_file}")

    tg = tgio.openTextgrid(textgrid_file)
    # print("tg tiers:", tg.tierNameList)

    if "SyllAlign" not in tg.tierNameList:
        raise ValueError(
            f"Tier 'SyllabesAlign' non trouvé dans le fichier {textgrid_file}"
        )

    syllabes_tier = tg.tierDict["SyllAlign"]

    syllabes = []
    for interval in syllabes_tier.entryList:
        label, xmin, xmax = interval[2], interval[0], interval[1]
        syllabes.append((label, xmin, xmax))
    return syllabes


def check_special_characters(sent_token, tier_token, tier_index, tier):
    move_step = 0
    if "'" in sent_token and "'" not in tier_token:
        if tier_token.upper() == "DO":
            if (
                tier[tier_index + 1][0].upper() == "N"
                and tier[tier_index + 2][0].upper() == "T"
            ):
                tier_token = (
                    tier_token + tier[tier_index + 1][0] + "'" + tier[tier_index + 2][0]
                )
                move_step = 3
            elif (
                tier[tier_index + 1][0].upper() == "N"
                and tier[tier_index + 2][0].upper() == "#"
                and tier[tier_index + 3][0].upper() == "T"
            ):
                tier_token = (
                    tier_token + tier[tier_index + 1][0] + "'" + tier[tier_index + 3][0]
                )
                move_step = 4

        elif tier_token.upper() == "DAT" and tier[tier_index + 1][0].upper() == "S":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "N" and tier[tier_index + 1][0].upper() == "T":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "WHAT" and tier[tier_index + 1][0].upper() == "S":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "YOU" and tier[tier_index + 1][0].upper() == "LL":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "IT" and tier[tier_index + 1][0].upper() == "S":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "I" and tier[tier_index + 1][0].upper() == "M":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "CA"
            and tier[tier_index + 1][0].upper() == "N"
            and tier[tier_index + 2][0].upper() == "T"
        ):
            tier_token = (
                tier_token + tier[tier_index + 1][0] + "'" + tier[tier_index + 2][0]
            )
            move_step = 3
        elif (
            tier_token.upper() == "SHOULD"
            and tier[tier_index + 1][0].upper() == "N"
            and tier[tier_index + 2][0].upper() == "T"
        ):
            tier_token = (
                tier_token + tier[tier_index + 1][0] + "'" + tier[tier_index + 2][0]
            )
            move_step = 3

        elif tier_token.upper() == "M" and sent_token.upper() == "'M":
            tier_token = "'" + tier_token
            move_step = 1

        elif (
            tier_token.upper() == "CHAMPIONS"
            and tier[tier_index + 1][0].upper() == "LEAGUE"
        ):
            tier_token = tier_token + "'"
            move_step = 1

        elif sent_token.upper() == "'S" and tier_token.upper() == "S":
            tier_token = "'" + tier_token
            move_step = 1

        elif tier_token.upper() == "MOMO" and tier[tier_index + 1][0].upper() == "S":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "HM" and tier[tier_index + 1][0].upper() == "M":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "WE" and tier[tier_index + 1][0].upper() == "RE":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "DEVIL" and tier[tier_index + 1][0].upper() == "S":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            sent_token.upper() == "DIDN'T"
            and tier_token.upper() == "DID"
            and tier[tier_index + 1][0].upper() == "N"
            and tier[tier_index + 2][0].upper() == "T"
        ):
            tier_token = (
                tier_token + tier[tier_index + 1][0] + "'" + tier[tier_index + 2][0]
            )
            move_step = 3

        elif sent_token.upper() == "LADIES'" and tier_token.upper() == "LADIES":
            tier_token = tier_token + "'"
            move_step = 1

        elif sent_token.upper() == "JESUS'" and tier_token.upper() == "JESUS":
            tier_token = tier_token + "'"
            move_step = 1

        elif sent_token.upper() == "D'" and tier_token.upper() == "D":
            tier_token = tier_token + "'"
            move_step = 1

        elif sent_token.upper() == "IF'S" and tier_token.upper() == "IF":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif sent_token.upper() == "T'OUNJE" and tier_token.upper() == "T":
            tier_token = tier_token + "'" + tier[tier_index + 2][0]
            move_step = 3

        elif sent_token.upper() == "KE'BEJI" and tier_token.upper() == "KE":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif sent_token.upper() == "TEEN'S" and tier_token.upper() == "TEEN":
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            sent_token.upper() == "DEY'VE"
            and tier_token.upper() == "DEY"
            and tier[tier_index + 1][0].upper() == "VE"
        ):
            tier_token = tier_token + "'" + tier[tier_index + 1][0]
            move_step = 2

    if tier_token.upper() == "CO-" and tier[tier_index + 1][0].upper() == "COMMANDER":
        tier_token = tier_token + tier[tier_index + 1][0]
        move_step = 2

    if "." in sent_token and (
        "." not in tier_token
        or tier_token.upper() == "O."
        or tier_token.upper() == "A."
    ):
        if tier_token.upper() == "O." and tier[tier_index + 1][0].upper() == "D.S":
            tier_token = tier_token + tier[tier_index + 1][0] + "."
            move_step = 2

        elif tier_token.upper() == "A." and tier[tier_index + 1][0].upper() == "M.":
            tier_token = tier_token + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "O." and tier[tier_index + 1][0].upper() == "A.":
            tier_token = tier_token + tier[tier_index + 1][0]
            move_step = 2

        elif sent_token.upper() == "ST." and tier_token.upper() == "ST":
            tier_token = tier_token + "."
            move_step = 1

        elif (
            sent_token.upper() == "2.5"
            and tier_token.upper() == "2"
            and tier[tier_index + 1][0].upper() == "POINT"
            and tier[tier_index + 2][0].upper() == "#"
        ):
            tier_token = tier_token + ".5"
            move_step = 2

        elif (
            sent_token.upper() == "2.5"
            or sent_token.upper() == "2.40"
            or sent_token.upper() == "2.3"
        ) and tier_token.upper() == "2":
            tier_token = tier_token + "." + tier[tier_index + 2][0]
            move_step = 3

        elif sent_token.upper() == "1.0" and tier_token.upper() == "1":
            tier_token = tier_token + "." + tier[tier_index + 2][0]
            move_step = 3

        elif sent_token.upper() == "95.1" and tier_token.upper() == "95":
            tier_token = tier_token + "." + tier[tier_index + 2][0]
            move_step = 3

        elif sent_token.upper() == "100.9" and tier_token.upper() == "100":
            if tier[tier_index + 1][0] == "#" and tier[tier_index + 3][0] == "#":
                tier_token = tier_token + "." + tier[tier_index + 4][0]
                move_step = 5
            elif tier[tier_index + 1][0] == "#" and tier[tier_index + 3][0] != "#":
                tier_token = tier_token + "." + tier[tier_index + 3][0]
                move_step = 4
            else:
                tier_token = tier_token + "." + tier[tier_index + 2][0]
                move_step = 3

    if (
        sent_token.upper() == "CANNOT"
        and tier_token.upper() == "CAN"
        and tier[tier_index + 1][0].upper() == "NOT"
    ):
        tier_token = tier_token + tier[tier_index + 1][0]
        move_step = 2

    if "-" in sent_token and "-" not in tier_token:
        if tier_token.upper() == "UN" and tier[tier_index + 1][0].upper() == "AFRICAN":
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2
        elif (
            tier_token.upper() == "PRO"
            and tier[tier_index + 1][0].upper() == "EUROPEAN"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "MA":
            if tier[tier_index + 1][0].upper() == "FIREWOOD":
                tier_token = tier_token + "-" + tier[tier_index + 1][0]
                move_step = 2
            elif tier[tier_index + 1][0].upper() == "AKARA":
                tier_token = tier_token + "-" + tier[tier_index + 1][0]
                move_step = 2

        elif (
            tier_token.upper() == "PRE" and tier[tier_index + 1][0].upper() == "DEGREE"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "E" and tier[tier_index + 1][0].upper() == "SERVICES"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "POP" and tier[tier_index + 1][0].upper() == "CORN":
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "UNDER"
            and tier[tier_index + 1][0].upper() == "SEVENTEEN"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "NIGER"
            and tier[tier_index + 1][0].upper() == "TORNADOES"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "WIKI"
            and tier[tier_index + 1][0].upper() == "TORRIES"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "EL" and tier[tier_index + 1][0].upper() == "KALNEMY"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "NA" and tier[tier_index + 1][0].upper() == "EME":
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "VICE"
            and tier[tier_index + 2][0].upper() == "PRESIDO"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 2][0]
            move_step = 3

        elif (
            tier_token.upper() == "VICE"
            and tier[tier_index + 1][0].upper() == "PRESIDO"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif tier_token.upper() == "HIP" and tier[tier_index + 1][0].upper() == "HOP":
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "TIN"
            and tier[tier_index + 1][0].upper() == "N-"
            and tier[tier_index + 2][0].upper() == "TIN"
        ):
            tier_token = (
                tier_token + "-" + tier[tier_index + 1][0] + tier[tier_index + 2][0]
            )
            move_step = 3

        elif (
            tier_token.upper() == "BED" and tier[tier_index + 1][0].upper() == "RIDDEN"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "RE"
            and tier[tier_index + 1][0].upper() == "ORIENTATE"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "GRAND"
            and tier[tier_index + 1][0].upper() == "MOTHER"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "MOTHER"
            and tier[tier_index + 1][0].upper() == "IN"
            and tier[tier_index + 2][0].upper() == "LAW"
        ):
            tier_token = (
                tier_token
                + "-"
                + tier[tier_index + 1][0]
                + "-"
                + tier[tier_index + 2][0]
            )
            move_step = 3

        elif (
            tier_token.upper() == "TWENTY"
            and tier[tier_index + 1][0].upper() == "THREE"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "ENUGU"
            and tier[tier_index + 1][0].upper() == "ONITSHA"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

        elif (
            tier_token.upper() == "GEO"
            and tier[tier_index + 1][0].upper() == "POLITICAL"
        ):
            tier_token = tier_token + "-" + tier[tier_index + 1][0]
            move_step = 2

    return tier_token, move_step


def get_alignement_informations(conllu, tier_tok, tier_syll, filename):
    """
    Comparer les tokens du fichier TextGrid avec les phrases du fichier CoNLL-U, récupérer les informations nécessaires pour l'alignement de chaque token correspondant pour chaque phrase.
    Si un token est dans la phrase mais est remplacé par un # dans le tier, mettre X pour alignbegin et alignend.
    Si une ponctuation, alignbegin et alignend = alignend du token précédent.

    Parameters:
    conllu (dict): un dictionnaire avec les phrases extraites (clé: nom du fichier, valeur: sentence_id et sentence_text)
    tier (list): une liste des tokens extraits du fichier TextGrid (label, xmin, xmax)

    Returns:
    sentences (dict): un dictionnaire contenant les informations pour les alignements de chaque token correspondant pour chaque phrase (clé: nom du fichier, valeur: sentence_id, sentence_text et token_info). Si un token est dans la phrase mais est remplacé par un # dans le tier, mettre X pour alignbegin et alignend.
    """
    punctuation_list = [
        ">",
        "<",
        "//",
        "?//",
        "]",
        "}",
        "|c",
        ">+",
        "||",
        "}//",
        "&//",
        "//.",
        ")",
        "|r",
        ">=",
        "//+",
        "<+",
        "?//]",
        "//]",
        "//=",
        "!//",
        "?//=",
        "!//=",
        "//)",
        "|a",
        "&?//",
        "!//]",
        "&//]",
        "//&",
        "?//]",
        "!//)",
        "&?//]",
        "{",
        "(",
        "[",
        "&",
        "||e",
        "<{",
        "//t",
        "{|c",
        "|}",
        "|",
        "/",
        "?",
        "+",
        ",",
    ]

    sentences = {}
    filename = filename.split(".")[0]
    if filename not in conllu:
        raise KeyError(f"Le fichier {filename} n'est pas présent dans conllu dict")

    tier_index = 0
    tier_index_syll = 0
    prev_xmax = 0
    sent_idx = 1
    # print("tokens :", tier_tok)

    for sent_id, sent_text_list in conllu[filename].items():
        sent_text = " ".join(sent_text_list).replace("\n", "")
        sent_tokens = sent_text.split()
        token_info = []
        syll_info = []

        word_id = 1

        # print("\n")
        for sent_token in sent_tokens:
            found = False
            token_tild = False
            ponctu = False

            while tier_index < len(tier_tok):
                tier_token, xmin, xmax = tier_tok[tier_index]

                # Convertir xmin et xmax en millisecondes avec 6 chiffres
                xmin = f"{int(float(xmin) * 1000):06d}"
                xmax = f"{int(float(xmax) * 1000):06d}"

                if "~" in sent_token:
                    token_tild_true = sent_token
                    sent_token = sent_token.replace("~", "")
                    token_tild = True

                tier_token, move_step = check_special_characters(
                    sent_token, tier_token, tier_index, tier_tok
                )
                ponctu = move_step > 0

                if sent_token.upper() == tier_token.upper():
                    # print("tier_index", tier_index)
                    # print("sent_token", sent_token, "tier_token", tier_token)
                    alignbegin = xmin
                    alignend = xmax
                    prev_xmax = xmax

                    if token_tild:
                        sent_token = token_tild_true

                    token_info.append((sent_token, alignbegin, alignend, word_id))
                    found = True
                    tier_index += move_step if ponctu else 1
                    word_id += 1

                    # print("tier_index_2", tier_index)
                    break

                elif sent_token in punctuation_list:
                    alignbegin = prev_xmax
                    alignend = prev_xmax
                    token_info.append((sent_token, alignbegin, alignend, word_id))
                    word_id += 1
                    found = True
                    break

                elif tier_token == "#":
                    # print(
                    #     "tier_index_#_1",
                    #     tier_index,
                    #     "sent_token",
                    #     sent_token,
                    #     "tier_token",
                    #     tier_token,
                    #     # "tier_token_+1",
                    #     # tier_tok[tier_index + 1][0],
                    #     # "tier_token_+2",
                    #     # tier_tok[tier_index + 2][0],
                    # )
                    if tier_index + 1 < len(tier_tok):
                        if sent_token.upper() == tier_tok[tier_index + 1][0].upper():
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0],
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}"
                            )
                            tier_index += 2  # saut des deux index car les deux tokens ont été utilisés
                            # print("tier_index_#_2", tier_index)

                        elif tier_index + 2 < len(tier_tok) and sent_token.upper() == (
                            tier_tok[tier_index + 1][0].upper()
                            + "-"
                            + tier_tok[tier_index + 2][0].upper()
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0]
                                    + "-"
                                    + tier_tok[tier_index + 2][0],
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 2][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 2][2]) * 1000):06d}"
                            )
                            tier_index += 3

                        elif (
                            sent_token.upper() == "VICE-PRESIDO"
                            and tier_tok[tier_index + 1][0].upper() == "VICE"
                            and tier_tok[tier_index + 2][0].upper() == "#"
                        ):
                            # print(
                            #     "VICE-PRESIDO",
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token",
                            #     tier_tok[tier_index][0],
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            #     "tier_token_+3",
                            #     tier_tok[tier_index + 3][0],
                            # )
                            token_info.append(
                                (
                                    sent_token,
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 3][1]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 3][1]) * 1000):06d}"
                            )
                            tier_index += 3

                        elif tier_index + 3 < len(tier_tok) and sent_token.upper() == (
                            tier_tok[tier_index + 1][0].upper()
                            + tier_tok[tier_index + 2][0].upper()
                            + "'"
                            + tier_tok[tier_index + 3][0].upper()
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0]
                                    + tier_tok[tier_index + 2][0]
                                    + "'"
                                    + tier_tok[tier_index + 3][0],
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}"
                            )
                            tier_index += 4

                        elif (
                            tier_index + 2 < len(tier_tok)
                            and sent_token.upper()
                            == tier_tok[tier_index + 2][0].upper()
                            and tier_tok[tier_index + 1][0].upper() == "#"
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 2][0],
                                    f"{int(float(tier_tok[tier_index + 2][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 2][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 2][2]) * 1000):06d}"
                            )
                            tier_index += 3

                        elif (
                            sent_token.upper() == "LADIES'"
                            and tier_tok[tier_index + 1][0].upper() == "LADIES"
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0] + "'",
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}"
                            )
                            tier_index += 2

                        elif (
                            sent_token.upper() == "JESUS'"
                            and tier_tok[tier_index + 1][0].upper() == "JESUS"
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            # )
                            token_info.append((tier_token, xmin, xmax, word_id))
                            word_id += 1
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0] + "'",
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 1][2]) * 1000):06d}"
                            )
                            tier_index += 2

                        elif (
                            tier_index + 3 < len(tier_tok)
                            and sent_token.upper() == "2.40"
                            and tier_tok[tier_index + 1][0].upper() == "2"
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            #     "tier_token_+3",
                            #     tier_tok[tier_index + 3][0],
                            # )
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0]
                                    + "."
                                    + tier_tok[tier_index + 3][0],
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}"
                            )
                            tier_index += 4
                            word_id += 1

                        elif (
                            tier_index + 3 < len(tier_tok)
                            and sent_token.upper() == "2.3"
                            and tier_tok[tier_index + 1][0].upper() == "2"
                        ):
                            # print(
                            #     "sent_token",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "tier_token_+2",
                            #     tier_tok[tier_index + 2][0],
                            #     "tier_token_+3",
                            #     tier_tok[tier_index + 3][0],
                            # )
                            token_info.append(
                                (
                                    tier_tok[tier_index + 1][0]
                                    + "."
                                    + tier_tok[tier_index + 3][0],
                                    f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                    f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}",
                                    word_id,
                                )
                            )
                            prev_xmax = (
                                f"{int(float(tier_tok[tier_index + 3][2]) * 1000):06d}"
                            )
                            tier_index += 4
                            word_id += 1

                        elif (
                            tier_index + 4 < len(tier_tok)
                            and sent_token.upper() == "100.9"
                        ):
                            if (
                                tier_tok[tier_index + 1][0].upper() == "100"
                                and tier_tok[tier_index + 2][0].upper() == "#"
                                and tier_tok[tier_index + 3][0].upper() == "POINT"
                                and tier_tok[tier_index + 4][0].upper() == "#"
                                and tier_tok[tier_index + 5][0].upper() == "9"
                            ):
                                # print(
                                #     "sent_token",
                                #     sent_token,
                                #     "tier_token_+1",
                                #     tier_tok[tier_index + 1][0],
                                #     "tier_token_+2",
                                #     tier_tok[tier_index + 2][0],
                                #     "tier_token_+3",
                                #     tier_tok[tier_index + 3][0],
                                #     "tier_token_+4",
                                #     tier_tok[tier_index + 4][0],
                                # )
                                token_info.append(
                                    (
                                        tier_tok[tier_index + 1][0]
                                        + "."
                                        + tier_tok[tier_index + 5][0],
                                        f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                        f"{int(float(tier_tok[tier_index + 5][2]) * 1000):06d}",
                                        word_id,
                                    )
                                )
                                prev_xmax = f"{int(float(tier_tok[tier_index + 5][2]) * 1000):06d}"
                                tier_index += 6
                                word_id += 1

                            elif (
                                tier_tok[tier_index + 1][0].upper() == "100"
                                and tier_tok[tier_index + 2][0].upper() == "#"
                                and tier_tok[tier_index + 3][0].upper() == "POINT"
                                and tier_tok[tier_index + 4][0].upper() == "9"
                            ):
                                # print(
                                #     "sent_token",
                                #     sent_token,
                                #     "tier_token_+1",
                                #     tier_tok[tier_index + 1][0],
                                #     "tier_token_+2",
                                #     tier_tok[tier_index + 2][0],
                                #     "tier_token_+3",
                                #     tier_tok[tier_index + 3][0],
                                #     "tier_token_+4",
                                #     tier_tok[tier_index + 4][0],
                                # )
                                token_info.append(
                                    (
                                        tier_tok[tier_index + 1][0]
                                        + "."
                                        + tier_tok[tier_index + 4][0],
                                        f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}",
                                        f"{int(float(tier_tok[tier_index + 4][2]) * 1000):06d}",
                                        word_id,
                                    )
                                )
                                prev_xmax = f"{int(float(tier_tok[tier_index + 4][2]) * 1000):06d}"
                                tier_index += 5
                                word_id += 1

                        elif (
                            sent_token.upper() != tier_tok[tier_index + 1][0].upper()
                            and tier_tok[tier_index][2] < tier_tok[tier_index + 1][1]
                        ):
                            # print(
                            #     "sent_token_3",
                            #     sent_token,
                            #     "tier_token",
                            #     tier_token,
                            #     "alignend", tier_tok[tier_index][2],
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            #     "alignbegin", tier_tok[tier_index + 1][1],
                            # )
                            xmin_new = (
                                f"{int(float(tier_tok[tier_index][2]) * 1000):06d}"
                            )
                            xmax_new = (
                                f"{int(float(tier_tok[tier_index + 1][1]) * 1000):06d}"
                            )
                            # print("xmin_new", xmin_new, "xmax_new", xmax_new)
                            token_info.append((sent_token, xmin_new, xmax_new, word_id))
                            prev_xmax = xmax_new
                            tier_index += 1
                            word_id += 1
                            found = True
                            # print("tier_index_#_3", tier_index)
                            break

                        else:
                            # print(
                            #     "sent_token_3",
                            #     sent_token,
                            #     "tier_token_+1",
                            #     tier_tok[tier_index + 1][0],
                            # )
                            tier_index += 1
                            # print("tier_index_#_3", tier_index)
                            break

                        word_id += 1

                    elif "-" not in sent_token:
                        # print("sent_token", sent_token, "tier_token", tier_token)
                        token_info.append((sent_token, "X", "X", word_id))
                        token_info.append((tier_token, xmin, xmax, word_id))
                        prev_xmax = xmax
                        tier_index += 1
                        word_id += 1
                        print("tier_index_#_3", tier_index)

                    else:
                        # print("sent_token_VE", sent_token, "tier_token", tier_token)
                        token_info.append((tier_token, xmin, xmax, word_id))
                        tier_index += 1
                        word_id += 1
                        # print(
                        #     "tier_index_#_4",
                        #     tier_index,
                        #     "sent_token",
                        #     sent_token,
                        #     "tier_token",
                        #     tier_tok[tier_index][0],
                        # )

                    found = True
                    break

                elif sent_token == "#" and sent_token != tier_token:
                    # print("tier_index_#", tier_index)
                    # print("sent_token", sent_token, "tier_token", tier_token)
                    break

                elif (
                    sent_token != tier_token
                    and sent_token not in punctuation_list
                    and tier_token != "#"
                    and sent_token != "#"
                ):
                    # print("tier_index_diff", tier_index)
                    # print("sent_token", sent_token)
                    # print("tier_token", tier_token)
                    # print("sent_text", sent_text)
                    break

                # else:
                #     print("sent_token", sent_token)
                #     print("tier_token", tier_token)
                #     print("tier_index_increment", tier_index)
                #     print("!!!!!!!!!!!!!!!!!!!!!!!")

            if not found and sent_token != "#":
                if sent_token not in punctuation_list:
                    # print("NOT FOUND")
                    token_info.append((sent_token, "X", "X", word_id))
                else:
                    alignbegin = prev_xmax
                    alignend = prev_xmax
                    token_info.append((sent_token, alignbegin, alignend, word_id))

        if token_info:
            phrase_alignbegin = next(
                (token[1] for token in token_info if token[1] != "X"), None
            )
            phrase_alignend = next(
                (token[2] for token in reversed(token_info) if token[2] != "X"), None
            )

            for tier_syllable, xmin, xmax in tier_syll[tier_index_syll:]:
                tier_syllable = tier_syllable.replace("-", "")
                syll_start = int(float(xmin) * 1000)
                syll_end = int(float(xmax) * 1000)

                if syll_start >= int(phrase_alignbegin) and syll_end <= int(
                    phrase_alignend
                ):
                    alignbegin = f"{syll_start:06d}"
                    alignend = f"{syll_end:06d}"
                    syll_info.append((tier_syllable, alignbegin, alignend))
                    tier_index_syll += 1
                else:
                    continue

        new_sent_text = " ".join([token_info[i][0] for i in range(len(token_info))])
        sent_info = [new_sent_text, phrase_alignbegin, phrase_alignend, sent_idx]
        sent_idx += 1
        # print("sent_text", sent_text)
        # print("new_sent_text", new_sent_text)
        # print("token_info", token_info, "\n")
        # print("syll_info", syll_info)

        sentences[sent_id] = {
            "sent_text": sent_text,
            "new_sent_text": sent_info,
            "token_info": token_info,
            "syll_info": syll_info,
        }

    return sentences


def save_alignment_results(sentences, output_file):
    """
    Sauvegarde des résultats d'alignement dans un fichier CSV

    Parameters:
    sentences (dict): un dictionnaire contenant les informations pour les alignements de chaque token correspondant pour chaque phrase (clé: nom du fichier, valeur: sentence_id, sentence_text et token_info)
    output_file (str): le chemin vers le fichier de sortie

    Returns:
    None
    """
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["sent_id", "sent_text", "new_sent_text", "token_info", "syll_info"]
        )
        for sent_id, sent_info in sentences.items():
            writer.writerow(
                [
                    sent_id,
                    sent_info["sent_text"],
                    sent_info["new_sent_text"],
                    sent_info["token_info"],
                    sent_info["syll_info"],
                ]
            )


def create_textgrid_slam(sentences: dict, output_file: str):
    """
    Créer un fichier TextGrid à partir des informations d'alignement

    Parameters:
    sentences (dict): un dictionnaire contenant les informations pour les alignements de chaque token correspondant pour chaque phrase (clé: nom du fichier, valeur: sentence_id, sentence_text et token_info)
    output_file (str): le chemin vers le fichier de sortie

    Returns:
    None
    """
    SLAM = tgio.Textgrid()

    sent_idx_tier = []
    sent_text_tier = []
    word_id_tier = []
    word_text_tier = []
    tokenisation_tier = []
    syllabes_tier = []

    punctuation_list = [
        ">",
        "<",
        "//",
        "?//",
        "]",
        "}",
        "|c",
        ">+",
        "||",
        "}//",
        "&//",
        "//.",
        ")",
        "|r",
        ">=",
        "//+",
        "<+",
        "?//]",
        "//]",
        "//=",
        "!//",
        "?//=",
        "!//=",
        "//)",
        "|a",
        "&?//",
        "!//]",
        "&//]",
        "//&",
        "?//]",
        "!//)",
        "&?//]",
        "{",
        "(",
        "[",
        "&",
        "||e",
        "<{",
        "//t",
        "{|c",
        "|}",
        "|",
        "/",
        "?",
        "+",
        ",",
    ]

    for sent_id, sentence_data in sentences.items():
        sentence_id = sentence_data["new_sent_text"][3]
        sentence_text = sentence_data["new_sent_text"][0]
        token_info = sentence_data["token_info"]
        syll_info = sentence_data["syll_info"]

        phrase_alignbegin = int(sentence_data["new_sent_text"][1]) / 1000
        phrase_alignend = int(sentence_data["new_sent_text"][2]) / 1000

        if phrase_alignbegin < phrase_alignend:
            sent_idx_tier.append([phrase_alignbegin, phrase_alignend, str(sentence_id)])
            sent_text_tier.append([phrase_alignbegin, phrase_alignend, sentence_text])

        # Split the sentence text into words
        words_in_sentence = sentence_text.split()
        word_idx = 0

        for token in token_info:
            if token[0] in punctuation_list:
                continue

            if (
                word_idx < len(words_in_sentence)
                and words_in_sentence[word_idx].upper() == token[0].upper()
            ):
                word = words_in_sentence[word_idx]
                word_idx += 1
            else:
                word = token[0]

            tok = token[0].lower()

            alignbegin = int(token[1]) / 1000 if token[1] != "X" else None
            alignend = int(token[2]) / 1000 if token[2] != "X" else None
            word_idx_str = str(sentence_id) + ":" + str(token[3])

            if (
                alignbegin is not None
                and alignend is not None
                and alignbegin < alignend
            ):
                if word != "#":
                    word_id_tier.append([alignbegin, alignend, str(word_idx_str)])
                    word_text_tier.append([alignbegin, alignend, word])

                if "#" in word:
                    syllabes_tier.append([alignbegin, alignend, word])
                tokenisation_tier.append([alignbegin, alignend, tok])

        for syll in syll_info:
            syll_tier_label = syll[0]
            syll_alignbegin = int(syll[1]) / 1000
            syll_alignend = int(syll[2]) / 1000
            if syll_alignbegin < syll_alignend:
                syllabes_tier.append([syll_alignbegin, syll_alignend, syll_tier_label])

    sent_idx = tgio.IntervalTier(name="Sent-ID", entryList=sent_idx_tier)
    sent_text = tgio.IntervalTier(name="Sent-Text", entryList=sent_text_tier)
    word_id = tgio.IntervalTier(name="Word-ID", entryList=word_id_tier)
    word_text = tgio.IntervalTier(name="Word-Text", entryList=word_text_tier)
    tokenisation = tgio.IntervalTier(name="TokensAlign", entryList=tokenisation_tier)
    syllabes = tgio.IntervalTier(name="Syllables", entryList=syllabes_tier)

    SLAM.addTier(sent_idx)
    SLAM.addTier(sent_text)
    SLAM.addTier(word_id)
    SLAM.addTier(word_text)
    SLAM.addTier(tokenisation)
    SLAM.addTier(syllabes)

    SLAM.save(output_file, outputFormat="textgrid")


# Construire une table de hachage pour les fichiers TextGrid
def build_textgrid_index(base_path: str) -> dict:
    """
    Récupérer les fichiers TextGrid dans un répertoire et construire un index pour les fichiers TextGrid

    Parameters:
    base_path (str): le chemin du répertoire contenant les fichiers TextGrid

    Returns:
    textgrid_index (dict): un dictionnaire contenant les noms des fichiers TextGrid comme clés et les chemins complets des fichiers comme valeurs
    """
    textgrid_index = dict()
    # print("base_path:", base_path)
    for root, dirs, files in os.walk(base_path):
        # print("Current directory:", root)
        # print("Subdirectories:", dirs)
        # print("Files:", files)
        for file in files:
            if file.endswith("-merged.TextGrid"):
                textgrid_name = file.split("-", 1)[0]
                textgrid_index[textgrid_name] = os.path.join(root, file)
                # print(f"Indexed TextGrid: {textgrid_name} -> {os.path.join(root, file)}")  # Debugging line
    return textgrid_index


conllu_path = "/Users/perrine/Desktop/Stage_2023-2024/SUD_Naija-NSC-master/non_gold/"
# gold_textgrid_path = "/Users/perrine/Desktop/Stage_2023-2024/MERGED/"
non_gold_textgrid_path = (
    "/Users/perrine/Desktop/Stage_2023-2024/Merged_non_gold_Final/non_gold/"
)
# non_gold_textgrid_path = (
#     "/Users/perrine/Desktop/Stage_2023-2024/Merged_non_gold_Final/gold_10ms_webrtcvad3/"
# )

# Construire l'index des fichiers TextGrid
textgrid_index = build_textgrid_index(non_gold_textgrid_path)
# print("TextGrid Index:", textgrid_index)

all_sentences = {}
for root, dirs, files in os.walk(conllu_path):
    for file in files:
        if file.endswith("_MG.conllu") or file.endswith("_M.conllu"):
            conllu_file = os.path.join(root, file)

            if file.startswith("ABJ"):
                textgrid_name = "_".join(file.split("_")[:3])
            else:
                textgrid_name = "_".join(file.split("_")[:2])

            textgrid_path = os.path.join(non_gold_textgrid_path, textgrid_name, "/")

            # Recherche du fichier TextGrid dans l'index
            non_gold_textgrid_file = textgrid_index.get(textgrid_name)

            # print("textgrid_path", non_gold_textgrid_file)
            if non_gold_textgrid_file:
                # if non_gold_textgrid_file.endswith("WAZL_13-merged.TextGrid"):
                conllu_dict = extraction_sentences_conllu(conllu_file)
                # print(conllu_dict)

                print(
                    "Extraction des tokens du fichier TextGrid",
                    non_gold_textgrid_file,
                )
                tokens = extraction_tokens_textgrid(non_gold_textgrid_file)
                # print("tokens", tokens)

                syllabes = extraction_syllabes_textgrid(non_gold_textgrid_file)

                sentences = get_alignement_informations(
                    conllu_dict, tokens, syllabes, file
                )
                all_sentences.update(sentences)

                # print(sentences)

                output_file = non_gold_textgrid_path + "slam/" + textgrid_name + ".TextGrid"
                create_textgrid_slam(sentences, output_file)
                print("Fichier TextGrid créé:", output_file)
            # else:
            #     print(f"Le fichier TextGrid n'existe pas: {textgrid_name}")

# output_file = non_gold_textgrid_path + "alignement_results.csv"
# save_alignment_results(all_sentences, output_file)

# print("Alignement terminé. Les résultats ont été sauvegardés dans:", output_file)
