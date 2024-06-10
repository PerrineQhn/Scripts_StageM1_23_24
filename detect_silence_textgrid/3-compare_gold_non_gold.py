"""
Ce script permet d'ajuster les phrases non gold en insérant des pauses basées sur le fichier TextGrid.

Il permet ainsi de pouvoir comparer les phrases gold et non gold après l'inserion des pauses.

Requis:
- Le fichier .conllu
- Textgrids -syl_tok.TextGrid (obtenus en utilisant combine_silence_textgrid.py)

Commande:
python3 ./Python_Stage_23_24/detect_silence_textgrid/3-compare_gold_non_gold.py
"""

import csv
import os
import time

from praatio import tgio


def get_files_from_directory(directory_path: str, extension: str) -> list:
    """
    Obtenir tous les fichiers d'un répertoire avec une extension donnée.

    Parameters:
    directory_path (str): Le chemin du répertoire.
    extension (str): L'extension des fichiers à récupérer.

    Returns:
    list: La liste des fichiers du répertoire avec l'extension donnée.
    """
    return [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(extension)
    ]


def extract_sentences(conllu_file_path: str) -> list:
    """
    Extraire les phrases du fichier .conllu.

    Parameters:
    conllu_file_path (str): Le chemin du fichier .conllu.

    Returns:
    list: La liste des phrases extraites du fichier .conllu.

    Variables:
    gold_sentences (list): La liste des phrases extraites du fichier .conllu.
    """
    gold_sentences = []
    with open(conllu_file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("# text ="):
                gold_sentence = line.split("=")
                new_gold_sentence = []
                for i in range(1, len(gold_sentence)):
                    gold_sentence_i = gold_sentence[i].split()
                    if i != len(gold_sentence) - 1:
                        gold_sentence_i[-1] += "="
                    new_gold_sentence.extend(gold_sentence_i)
                gold_sentences.append(new_gold_sentence)
    return gold_sentences


def extract_token_and_pause_times(textgrid_file_path: str) -> list:
    """
    Extraire les temps des tokens et des pauses du fichier TextGrid.

    Parameters:
    textgrid_file_path (str): Le chemin du fichier TextGrid.

    Returns:
    list: La liste des temps des tokens et des pauses.

    Variables:
    tier_combined (list): La liste des temps des tokens et des pauses.
    """
    tg = tgio.openTextgrid(textgrid_file_path)
    tier = tg.tierDict["Combined"]

    tier_combined = []

    for interval in tier.entryList:
        label, xmin, xmax = interval[2], interval[0], interval[1]

        tier_combined.append((label, xmin, xmax))
    return tier_combined


def insert_pauses_in_non_gold_sentences(
    non_gold_sentences: list, tier: list, filename: str
) -> list:
    """
    Insérer des pauses dans les phrases non gold basées sur le TextGrid.

    Parameters:
    non_gold_sentences (list): La liste des phrases non gold.
    tier (list): La liste des temps des tokens et des pauses.
    filename (str): Le nom du fichier.

    Returns:
    list: La liste des phrases non gold ajustées.

    Variables:
    adjusted_non_gold_sentences (list): La liste des phrases non gold ajustées.
    punctuation_list (list): La liste des ponctuations.
    diese_punct (list): La liste des ponctuations avec avant un '#'.
    sentences_list (list): La liste des mots des phrases non gold.
    idx_sentences_list (int): L'index de la liste des mots des phrases non gold.
    l (int): L'index de la liste des phrases non gold.
    i (int): L'index de la liste des temps des tokens et des pauses.
    j (int): L'index de la liste des mots des phrases non gold.
    """
    adjusted_non_gold_sentences = []
    print(non_gold_sentences)

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
        "!//]",
        "&//]",
        "//&",
        "?//)",
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

    diese_punct = ["{", "(", "["]

    i = 0
    sentences_list = [word for s in non_gold_sentences for word in s]
    for punctuation in punctuation_list:
        if punctuation in sentences_list:
            sentences_list = [
                x.replace("~", "") for x in sentences_list if x != punctuation
            ]
    idx_sentences_list = 0

    l = 0
    while l < len(non_gold_sentences):
        sentence = non_gold_sentences[l]
        new_sentence = []
        j = 0
        while j < len(sentence):
            token = sentence[j]

            if i >= len(tier) or (i == len(tier) - 1 and tier[-1] == "#"):
                break

            token_label, xmin, xmax = tier[i]
            # print(token_label, sentences_list[idx_sentences_list])
            if token in punctuation_list:
                new_sentence.append(token)
                j += 1

            elif token_label == "#":
                if i == 0 and tier[i + 1][0] == "#":
                    i += 1
                    continue

                else:
                    new_sentence.append("#")
                    if len(new_sentence) > 1 and new_sentence[-2] in diese_punct:
                        tmp = new_sentence[-2]
                        new_sentence[-2] = new_sentence[-1]
                        new_sentence[-1] = tmp

                    try_time = 3
                    idx_tier_try = i + 1
                    idx_word_try = idx_sentences_list
                    current_try = 0

                    while current_try < try_time:
                        while (
                            idx_word_try < len(sentences_list)
                            and sentences_list[idx_word_try] in punctuation_list
                        ):
                            idx_word_try += 1

                        if (
                            idx_word_try < len(sentences_list)
                            and idx_tier_try < len(tier)
                            and tier[idx_tier_try][0].upper()
                            != sentences_list[idx_word_try].upper()
                            and tier[idx_tier_try][0].upper() != "#"
                        ):
                            break

                        # Si nous rencontrons un autre '#', cela signifie que ce '#' ne cache pas de caractères
                        if idx_tier_try < len(tier) and tier[idx_tier_try][0] == "#":
                            current_try = try_time
                            print(
                                "case token_label==#: sentences_list: ",
                                sentences_list[idx_sentences_list],
                                idx_sentences_list,
                                "tier: ",
                                token_label,
                                tier[i][0],
                                i,
                                ": pass",
                            )
                            break

                        if idx_tier_try < len(tier) - 1 and idx_word_try < len(
                            sentences_list
                        ):
                            idx_tier_try += 1
                            idx_word_try += 1
                        current_try += 1

                    print(
                        "current_try < try_time: ",
                        current_try,
                        try_time,
                        sentences_list[idx_sentences_list],
                    )

                    print(
                        "case token_label == #",
                        "sentence: ",
                        sentence[j],
                        j,
                        "sentences_list: ",
                        sentences_list[idx_sentences_list],
                        idx_sentences_list,
                        "tier: ",
                        token_label,
                        tier[i][0],
                        i,
                        "new_sentence: ",
                        new_sentence,
                    )

                    if current_try < try_time:  # token caché par #

                        if (
                            sentences_list[idx_sentences_list].upper() == "EH"
                            and sentences_list[idx_sentences_list + 1].upper() == "ME"
                        ):
                            print(
                                "EH",
                                sentences_list[idx_sentences_list],
                                tier[i][0],
                                tier[i + 1][0],
                                sentences_list[idx_sentences_list + 1],
                            )
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        if (
                            idx_sentences_list < len(sentences_list) - 2
                            and sentences_list[idx_sentences_list].upper()
                            == sentences_list[idx_sentences_list + 2].upper()
                            and sentences_list[idx_sentences_list + 1].upper()
                            == sentences_list[idx_sentences_list + 3].upper()
                            and sentences_list[idx_sentences_list].upper()
                            == tier[i + 1][0].upper()
                            and sentences_list[idx_sentences_list].upper() != "HOUSE"
                            and sentences_list[idx_sentences_list].upper() != "PEPPER"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(
                                    " ".join(new_sentence)
                                )
                                new_sentence = []
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(
                                    " ".join(new_sentence)
                                )
                                new_sentence = []

                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "I"
                            and sentences_list[idx_sentences_list + 1].upper() == "SAY"
                            and sentences_list[idx_sentences_list + 2].upper() == "AH"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(
                                    " ".join(new_sentence)
                                )
                                new_sentence = []

                        # Condition spécifique pour le fichier ABJ_GWA_10_Steven-Lifestory_MG
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "I"
                            and sentences_list[idx_sentences_list + 1].upper() == "IF"
                        ):
                            new_sentence.append(sentence[j])
                            new_sentence.append(sentence[j + 1])
                            idx_sentences_list += 1
                            j += 2
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "SO"
                            and sentences_list[idx_sentences_list + 1].upper() == "NA"
                            and sentences_list[idx_sentences_list + 2].upper() == "SO"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Condition spécifique pour le fichier ABJ_GWA_14
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "GO"
                            and sentences_list[idx_sentences_list + 1].upper()
                            == "STILL"
                            and sentences_list[idx_sentences_list + 2].upper() == "E"
                        ):

                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Condition spécifique pour le fichier LAG_11_Adeniyi-Lifestory_MG
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "IF"
                            and sentences_list[idx_sentences_list + 1].upper() == "I"
                            and sentences_list[idx_sentences_list + 2].upper() == "IF"
                            and sentences_list[idx_sentences_list + 3].upper() == "I"
                            and sentences_list[idx_sentences_list + 4].upper() == "WANT"
                        ):
                            print("ICI !!!!")
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Condition spécifique pour le fichier WAZL_08_Edewor-Lifestory_MG
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "CON"
                            and sentences_list[idx_sentences_list + 1].upper()
                            == "HAPPEN"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list].upper() == "WE"
                            and sentences_list[idx_sentences_list + 1].upper() == "TALK"
                            and sentences_list[idx_sentences_list + 2].upper() == "WE"
                            and sentences_list[idx_sentences_list + 3].upper() == "JUST"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list - 1].upper() == "#"
                            and sentences_list[idx_sentences_list].upper() == "WE"
                            and sentences_list[idx_sentences_list + 1].upper() == "TALK"
                            and sentences_list[idx_sentences_list + 2].upper() == "WE"
                        ):
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Specifique pour le fichier IBA_01
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list - 3].upper() == "CON"
                            and sentences_list[idx_sentences_list - 2].upper() == "DEY"
                            and sentences_list[idx_sentences_list - 1].upper() == "DO"
                            and sentences_list[idx_sentences_list].upper() == "O"
                            and sentences_list[idx_sentences_list + 1].upper() == "I"
                            and sentences_list[idx_sentences_list + 2].upper() == "DO"
                        ):
                            print("DO O I DO !*!*!")
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Specifique pour le fichier ENU_36
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list - 1].upper() == "DON"
                            and sentences_list[idx_sentences_list].upper() == "EVEN"
                            and sentences_list[idx_sentences_list + 1].upper() == "SAY"
                            and sentences_list[idx_sentences_list + 2].upper() == "I"
                            and sentences_list[idx_sentences_list + 3].upper() == "NO"
                        ):
                            print(
                                "EVEN SAY I !!!!",
                                sentences_list[idx_sentences_list],
                                sentences_list[idx_sentences_list + 1],
                                sentences_list[idx_sentences_list + 2],
                                sentences_list[idx_sentences_list + 3],
                            )
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        # Specifique pour le fichier LAG_05
                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list - 1].upper()
                            == "PLACE"
                            and sentences_list[idx_sentences_list].upper() == "NA"
                            and sentences_list[idx_sentences_list + 1].upper() == "LIE"
                            and sentences_list[idx_sentences_list + 2].upper() == "NA"
                        ):
                            print(
                                "PLACE NA LIE NA !!!!",
                                sentences_list[idx_sentences_list],
                                sentences_list[idx_sentences_list + 1],
                                sentences_list[idx_sentences_list + 2],
                            )
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1

                        if (
                            idx_sentences_list < len(sentences_list)
                            and sentences_list[idx_sentences_list - 1].upper() == "GO"
                            and sentences_list[idx_sentences_list].upper() == "DEY"
                            and sentences_list[idx_sentences_list + 1].upper()
                            == "FOLLOW"
                            and sentences_list[idx_sentences_list + 2].upper() == "AM"
                            and sentences_list[idx_sentences_list + 3].upper() == "UP"
                        ):
                            print(
                                "GO DEY FOLLOW AM UP !!!!",
                                sentences_list[idx_sentences_list],
                                sentences_list[idx_sentences_list + 1],
                                sentences_list[idx_sentences_list + 2],
                                sentences_list[idx_sentences_list + 3],
                            )
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1


                        if idx_sentences_list < len(sentences_list) - 2 and i + 3 < len(
                            tier
                        ):
                            print(
                                "case  token_label == #",
                                "idx_sentences_list < len(sentences_list) - 2 and i + 3 < len(tier):"
                                "sentence: ",
                                # sentence[j],
                                j,
                                "sentences_list: ",
                                sentences_list[idx_sentences_list],
                                idx_sentences_list,
                                "tier: ",
                                token_label,
                                tier[i][0],
                                i,
                                "new_sentence: ",
                                new_sentence,
                            )
                    i = i + 1

            elif (
                "'" in token
                and "'" not in token_label
                and token.upper() != "A'AH"
                and filename
                not in [
                    "JOS_38_Bokos-Traditional-Wedding_M",
                    "JOS_15_Graduate-Wahala_M",
                ]
            ):
                print(filename)
                print(
                    sentence[j],
                    j,
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    i,
                    token_label,
                    token,
                    ' "\'" in token and "\'" not in token_label',
                )
                # time.sleep(11)
                move_step = 0

                if token_label.upper() == "DO":
                    print("DO", tier[i + 1][0])
                    tmp = tier[i + 1][0]
                    if tier[i + 1][0] == "#" and tier[i + 2][0].upper() == "T":
                        new_sentence.append("#")
                        tmp = "N"
                        token_label = token_label + tmp + "'" + tier[i + 2][0]
                        move_step = 3
                    elif (
                        tier[i + 1][0].upper() == "N" and tier[i + 2][0].upper() == "T"
                    ):
                        token_label = (
                            token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                        )
                        move_step = 3
                    elif (
                        tier[i + 1][0].upper() == "N"
                        and tier[i + 2][0].upper() == "#"
                        and tier[i + 3][0].upper() == "T"
                    ):
                        new_sentence.append("#")
                        token_label = (
                            token_label + tier[i + 1][0] + "'" + tier[i + 3][0]
                        )
                        move_step = 4
                    elif (
                        tier[i + 1][0].upper() == "N"
                        and tier[i + 2][0].upper() == "#"
                        and tier[i + 3][0].upper() == "LIKE"
                    ):
                        new_sentence.append("#")
                        token_label = token_label + tier[i + 1][0] + "'t"
                        move_step = 3

                    else:
                        print("This case has not been handled")
                        token_label = (
                            token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                        )
                        move_step = 3

                if token_label.upper() == "N" and tier[i + 1][0].upper() == "#":
                    print("N", token_label, tier[i + 1][0])
                    token_label = token_label + "'t"
                    print("N", token_label)
                    move_step = 1

                if token_label.upper() == "T" and tier[i + 2][0].upper() != "OUNJE":
                    print("T", tier[i + 1][0])
                    token_label = "don" + "'" + token_label
                    print("T", token_label)
                    move_step = 1

                if token_label.upper() == "DID":
                    if tier[i + 1][0].upper() == "N" and tier[i + 2][0].upper() == "T":
                        token_label = (
                            token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                        )
                        move_step = 3

                if token_label.upper() == "CA":
                    if tier[i + 1][0].upper() == "N" and (
                        tier[i + 2][0].upper() == "T" or tier[i + 2][0].upper() == "#"
                    ):
                        token_label = token_label + tier[i + 1][0] + "'T"
                        move_step = 3

                if token_label.upper() == "CHAMPIONS":
                    token_label = token_label + "'"
                    move_step = 1

                if token_label.upper() == "DEVIL":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "M":
                    token_label = "'" + token_label
                    move_step = 1

                if token_label.upper() == "S":
                    token_label = "'" + token_label
                    move_step = 1

                if token_label.upper() == "IT":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "N":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "I":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "WE":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "MOMO":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "WHAT":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "YOU":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "WHAT":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "DAT" and filename not in [
                    "BEN_08_Egusi-And-Banga-Soup_MG",
                    "ABJ_INF_10_Women-Battering_MG",
                    "KAD_03_Why-Men-Watch-Football_MG",
                    "LAG_37_Soap-Making_MG",
                    "IBA_23_Bitter-Leaf-Soup_MG",
                    "LAG_11_Adeniyi-Lifestory_MG",
                    "WAZA_10_Bluetooth-Lifestory_MG",
                ]:
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "HM":
                    if tier[i + 1][0] == "#":
                        token_label = token_label + "'" + "m"
                    else:
                        token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "I" and tier[i + 1][0].upper() == "M":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "D":
                    token_label = token_label + "'"
                    move_step = 1

                if token_label.upper() == "JESUS":
                    token_label = token_label + "'"
                    move_step = 1

                if token_label.upper() == "T" and tier[i + 2][0].upper() == "OUNJE":
                    token_label = token_label + "'" + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "LADIES":
                    token_label = token_label + "'"
                    move_step = 1

                if token_label.upper() == "IF":
                    token_label = token_label + "'" + tier[i + 1][0]
                    print("IF", token_label)
                    if token_label == "if'{s|}":
                        token_label = "if's||"
                    move_step = 2

                if token_label.upper() == "DEY":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "TEEN":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "KE":
                    token_label = token_label + "'" + tier[i + 1][0]
                    move_step = 2

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif (
                "-" in token
                and "-" not in token_label
                and token.upper() != "CO-COMMANDER"
            ):
                print(
                    sentence[j],
                    j,
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    i,
                    token_label,
                    ' "-" in token and "-" not in token_label',
                    token_label,
                    tier[i + 1][0],
                    filename,
                )
                move_step = 0
                if token_label.upper() == "PRO":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "UN":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "MA":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "E":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "PRE":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "POP":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "UNDER":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "NIGER":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "WIKI":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "EL":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "NA":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "VICE":
                    token_label = token_label + "-" + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "HIP":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "TIN":
                    token_label = token_label + "-" + tier[i + 1][0] + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "BED":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "RE":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "GRAND":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "MOTHER":
                    token_label = (
                        token_label + "-" + tier[i + 1][0] + "-" + tier[i + 2][0]
                    )
                    move_step = 3

                if token_label.upper() == "TWENTY":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "ENUGU":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "GEO":
                    token_label = token_label + "-" + tier[i + 1][0]
                    move_step = 2

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif "." in token and len(token) != len(token_label):
                print(
                    sentence[j],
                    j,
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    i,
                    ' "." in token and "." not in token_label',
                    token_label,
                    tier[i + 1][0],
                    tier[i + 2][0],
                    filename,
                )
                move_step = 0
                if token_label.upper() == "O.":
                    if tier[i + 1][0].upper() == "A.":
                        token_label = token_label + tier[i + 1][0]
                        move_step = 2
                    else:
                        token_label = token_label + tier[i + 1][0] + "."
                        move_step = 2

                if token_label.upper() == "A.":
                    token_label = token_label + tier[i + 1][0]
                    move_step = 2

                if token_label.upper() == "ST":
                    token_label = token_label + "."
                    move_step = 1

                if token_label.upper() == "EH":
                    token_label = token_label + "."
                    move_step = 1

                if token_label.upper() == "2":
                    token_label = token_label + "." + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "1":
                    token_label = token_label + "." + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "95":
                    token_label = token_label + "." + tier[i + 2][0]
                    move_step = 3

                if token_label.upper() == "100":
                    print("100", tier[i + 1][0], tier[i + 2][0], tier[i + 3][0], tier[i + 4][0])
                    if tier[i + 1][0].upper() == "#" and tier[i + 3][0] == "#":
                        token_label = token_label + "." + tier[i + 4][0]
                        move_step = 5
                    elif tier[i + 1][0].upper() == "#" and tier[i + 3][0] != "#":
                        token_label = token_label + "." + tier[i + 3][0]
                        move_step = 4
                    else:
                        token_label = token_label + "." + tier[i + 2][0]
                        move_step = 3

                if token_label.upper() == "PROSPERITY":
                    token_label = token_label + "."
                    move_step = 1

                if token_label.upper() == "HM":
                    token_label = token_label + "."
                    move_step = 1

                if token_label.upper() == "DAY":
                    token_label = token_label + "."
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif sentences_list[idx_sentences_list].upper() == "CANNOT":
                move_step = 1
                if tier[i + 1][0].upper() == "NOT":
                    token_label = "CAN" + tier[i + 1][0]
                    move_step = 2

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif sentences_list[idx_sentences_list].upper() == "CO-COMMANDER":
                print("CO-COMMANDER", tier[i + 1][0].upper())
                if tier[i + 1][0].upper() == "COMMANDER":
                    token_label = "CO-" + tier[i + 1][0]
                    move_step = 2
                if tier[i + 1][0].upper() == "#":
                    token_label = "CO-" + tier[i + 2][0]
                    move_step = 3

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif "]" in token and "]" not in token_label:
                move_step = 0
                if token_label.upper() == "CHECHECHE":
                    token_label = token_label + "]"
                    move_step = 1

                if token_label.upper() == "HUSTLE":
                    token_label = token_label + "]"
                    move_step = 1

                if token_label.upper() == "TINS":
                    token_label = token_label + "]"
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif ")" in token and ")" not in token_label:
                move_step = 0
                if token_label.upper() == "BEFORE":
                    token_label = token_label + ")"
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif "}" in token and "}" not in token_label:
                move_step = 0
                if token_label.upper() == "SO":
                    token_label = token_label + "}"
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif "<" in token and "<" not in token_label:
                move_step = 0
                if token_label.upper() == "ALL":
                    token_label = token_label + "<"
                    move_step = 1

                if token_label.upper() == "HOUR":
                    token_label = token_label + "<"
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif "," in token and "," not in token_label:
                print(
                    sentence[j],
                    j,
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    i,
                    token_label,
                    ' "," in token and "," not in token_label',
                    filename,
                )
                move_step = 0
                if token_label.upper() == "O":
                    token_label = token_label + ","
                    move_step = 1

                if token_label.upper() == "KWALUM":
                    token_label = token_label + ","
                    move_step = 1

                if token_label.upper() == "WOS":
                    token_label = token_label + ","
                    move_step = 1

                if token_label.upper() == "PLACE":
                    token_label = token_label + ","
                    move_step = 1

                if token_label.upper() == "MYSELF":
                    token_label = token_label + ","
                    move_step = 1

                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            # elif "||" in token and "||" not in token_label:
            #     move_step = 0
            #     if token_label.upper() == "DE":
            #         token_label = token_label + "||"
            #         move_step = 1

            #     if token.upper() == token_label.upper():
            #         new_sentence.append(token)
            #         i += move_step
            #         j += 1
            #         idx_sentences_list += 1

            elif token_label.upper() == "{MILLION|C}":
                token_label = "million|c"
                move_step = 1
                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif token_label.upper() == "{SEY|C}":
                token_label = "sey|c"
                move_step = 1
                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif token_label.upper() == "{FOR|}":
                token_label = "for||"
                move_step = 1
                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif token_label.upper() == "{SAY|}":
                token_label = "say||"
                move_step = 1
                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif token_label.upper() == "{DI|}":
                token_label = "di||"
                move_step = 1
                if token.upper() == token_label.upper():
                    new_sentence.append(token)
                    i += move_step
                    j += 1
                    idx_sentences_list += 1

            elif sentences_list[idx_sentences_list].upper() == token_label.upper():
                c_tier = 0
                c_word = 0
                idx_tier = i + 1
                idx_word = idx_sentences_list + 1
                flag_diese = False
                while idx_tier < len(tier):
                    print(token_label.upper(), tier[idx_tier][0].upper())

                    if token_label.upper() == tier[idx_tier][0].upper():
                        print(
                            "case   sentences_list[idx_sentences_list].upper() == token_label.upper(): ",
                            sentences_list[idx_sentences_list],
                            # sentences_list[idx_word],
                            "tier[i-1][0] == #: idx_word_try < len(sentences_list): "
                            "sentence: ",
                            token_label.upper(),
                            tier[idx_tier][0].upper(),
                            " - ==",
                        )
                        idx_tier += 1
                        c_tier += 1

                    elif "#" == tier[idx_tier][0]:
                        try_time = 3
                        idx_tier_try = idx_tier + 1
                        idx_word_try = idx_word
                        current_try = 0
                        while current_try < try_time:
                            while (
                                idx_word_try < len(sentences_list)
                                and sentences_list[idx_word_try] in punctuation_list
                            ):
                                idx_word_try += 1
                            if idx_word_try < len(
                                sentences_list
                            ) and idx_tier_try < len(tier):
                                print(
                                    "case   sentences_list[idx_sentences_list].upper() == token_label.upper(): ",
                                    sentences_list[idx_sentences_list],
                                    sentences_list[idx_word],
                                    "tier[i-1][0] == #: idx_word_try < len(sentences_list):"
                                    "sentence: ",
                                    sentences_list[idx_word_try],
                                    idx_word_try,
                                    "tier: ",
                                    tier[idx_tier_try][0].upper(),
                                    idx_tier_try,
                                    " - flag_diese = Compare",
                                )
                            # If we encounter another '#', it means that this '#' doesn't hide characters
                            if (
                                idx_tier_try < len(tier)
                                and tier[idx_tier_try][0] == "#"
                            ):
                                current_try = try_time
                                print(
                                    "case   sentences_list[idx_sentences_list].upper() == token_label.upper():"
                                    "tier[i-1][0] == #: tier[idx_tier_try][0] == #: pass"
                                )
                                break
                            if (
                                idx_tier_try < len(tier)
                                and idx_word_try < len(sentences_list)
                                and tier[idx_tier_try][0].upper()
                                != sentences_list[idx_word_try].upper()
                            ):
                                break
                            if idx_tier_try < len(tier) - 1 and idx_word_try < len(
                                sentences_list
                            ):
                                idx_tier_try += 1
                                idx_word_try += 1
                            current_try += 1

                        if current_try < try_time:  # hide somethings
                            flag_diese = True
                            print(
                                "case   sentences_list[idx_sentences_list].upper() == token_label.upper(): tier[i-1][0] == #: current_try < try_time",
                                "sentence: ",
                                sentences_list[idx_word],
                                idx_word,
                                sentences_list[idx_sentences_list],
                                idx_sentences_list,
                                "tier: ",
                                token_label.upper(),
                                tier[idx_tier][0].upper(),
                                " - flag_diese = True",
                            )
                        idx_tier += 1
                        continue
                    else:
                        break

                while idx_word < len(sentences_list):
                    if (
                        sentences_list[idx_sentences_list].upper()
                        == sentences_list[idx_word].upper()
                    ):
                        idx_word += 1
                        c_word += 1
                        continue

                    elif sentences_list[idx_word] in punctuation_list:
                        idx_word += 1
                        continue

                    elif flag_diese is True and (
                        sentences_list[idx_word].upper() == "I"
                        or sentences_list[idx_word].upper() == "'M"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DI"
                        and sentences_list[idx_sentences_list].upper() != "PERFUME"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "SHE"
                        and sentences_list[idx_sentences_list].upper() == "AS"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "SAY"
                        and sentences_list[idx_sentences_list].upper() == "EHN"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "IF"
                        and sentences_list[idx_sentences_list].upper() == "DO"
                        and sentences_list[idx_word + 1].upper() == "I"
                        and sentences_list[idx_word + 2].upper() == "IF"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "EH"
                        and sentences_list[idx_sentences_list].upper() == "DIS"
                        and sentences_list[idx_word + 1].upper() == "DIS"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word - 2].upper() == "DEY"
                        and sentences_list[idx_word - 1].upper() == "DO"
                        and sentences_list[idx_word].upper() == "O"
                        and sentences_list[idx_sentences_list].upper() == "DO"
                        and sentences_list[idx_word + 1].upper() == "I"
                        and sentences_list[idx_word + 2].upper() == "DO"
                    ):
                        idx_word += 1
                        continue

                    if (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "SMALL"
                        and sentences_list[idx_sentences_list].upper() == "CON"
                        and sentences_list[idx_word + 1].upper() == "CON"
                        and sentences_list[idx_word + 2].upper() == "START"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DOT"
                        and sentences_list[idx_word + 1].upper() == "TV"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "VERY"
                        and sentences_list[idx_word + 1].upper() == "A"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "FIT"
                        and sentences_list[idx_sentences_list].upper() != "YOU"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "WEY"
                        and sentences_list[idx_sentences_list].upper() != "DEY"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "AM"
                        and sentences_list[idx_sentences_list].upper() == "PACK"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "TOO"
                        and sentences_list[idx_word + 1].upper() == "LIGHT"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "ONE"
                        and sentences_list[idx_word + 1].upper() == "OF"
                    ):
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word - 1].upper() == "SEY"
                        and sentences_list[idx_word].upper() == "MAH"
                        and sentences_list[idx_word + 1].upper() == "I"
                    ):
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "TO"
                        and sentences_list[idx_word + 1].upper() == "SITE"
                        and sentences_list[idx_word + 2].upper() == "TO"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "E"
                        and sentences_list[idx_word + 1].upper() == "DEY"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "WORK"
                        and sentences_list[idx_word + 1].upper() == "ANODER"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "FAKE"
                        and sentences_list[idx_word + 1].upper() == "STORY"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "MY"
                        and sentences_list[idx_sentences_list].upper() == "WORK"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "EH"
                        and sentences_list[idx_sentences_list].upper() == "SEY"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "N"
                        and sentences_list[idx_sentences_list].upper() == "I"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "WORK"
                        and sentences_list[idx_sentences_list].upper() == "FIND"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DEY"
                        and sentences_list[idx_sentences_list].upper() == "ON"
                        and sentences_list[idx_word + 1].upper() == "GO"
                        and sentences_list[idx_word + 2].upper() == "ON"
                        and sentences_list[idx_word + 3].upper() == "NA"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "YOURSELF"
                        and sentences_list[idx_sentences_list].upper() == "PROTECT"
                        and sentences_list[idx_word + 1].upper() == "PROTECT"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "COMMANDER"
                        and sentences_list[idx_sentences_list].upper() == "CO-"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "GO"
                        and sentences_list[idx_sentences_list].upper() == "STILL"
                        and sentences_list[idx_word + 1].upper() == "STILL"
                    ):
                        idx_word += 3
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "GO"
                        and sentences_list[idx_sentences_list].upper() != "STILL"
                        and sentences_list[idx_sentences_list].upper() != "ON"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True and sentences_list[idx_word].upper() == "IM"
                    ):
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DEY"
                        and sentences_list[idx_sentences_list].upper() != "ON"
                        and sentences_list[idx_sentences_list].upper() != "GO"
                    ):
                        print("DEY !!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_sentences_list].upper() == "YOU"
                        and sentences_list[idx_word].upper() == "#"
                        and sentences_list[idx_word + 1].upper() == "YOU"
                    ):
                        print("AM FOR YOU !!!!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "EH"
                        and sentences_list[idx_sentences_list].upper() == "OIL"
                        and sentences_list[idx_word + 1].upper() == "OIL"
                        and sentences_list[idx_word + 2].upper() == "NOW"
                        and sentences_list[idx_word + 3].upper() == "COME"
                    ):
                        print("OIL EH OIL !*!*!!!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "AT"
                        and sentences_list[idx_sentences_list].upper() == "PROCESS"
                        and sentences_list[idx_word + 1].upper() == "DI"
                        and sentences_list[idx_word + 2].upper() == "PROCESS"
                    ):
                        print("AT PROCESS !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "OR"
                        and sentences_list[idx_sentences_list].upper() == "TIME"
                        and sentences_list[idx_word + 1].upper() == "DI"
                        and sentences_list[idx_word + 2].upper() == "TIME"
                    ):
                        print("OR TIME !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word - 2].upper() == "PERSON"
                        and sentences_list[idx_word - 1].upper() == "DON"
                        and sentences_list[idx_word].upper() == "E"
                        and sentences_list[idx_sentences_list].upper() == "DON"
                        and sentences_list[idx_word + 1].upper() == "DON"
                        and sentences_list[idx_word + 2].upper() == "DIE"
                    ):
                        print("PERSON DON E !*!*!!!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "FALL"
                        and sentences_list[idx_sentences_list].upper() == "DON"
                        and sentences_list[idx_word + 1].upper() == "E"
                        and sentences_list[idx_word + 2].upper() == "DON"
                    ):
                        print("FALL DON E !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DE"
                        and sentences_list[idx_sentences_list].upper() == "NO"
                        and sentences_list[idx_word + 1].upper() == "NO"
                        and sentences_list[idx_word + 2].upper() == "DEY"
                        and sentences_list[idx_word + 3].upper() == "PUT"
                    ):
                        print("DE NO NO DEY PUT !*!*!!!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "HAP"
                        and sentences_list[idx_sentences_list].upper() == "NO"
                        and sentences_list[idx_word + 1].upper() == "NO"
                        and sentences_list[idx_word + 2].upper() == "HAPPEN"
                    ):
                        print("HAP NO NO AGAIN !*!*!!!!")
                        idx_word += 1
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "WE"
                        and sentences_list[idx_sentences_list].upper() == "ABOUT"
                        and sentences_list[idx_word + 1].upper() == "DEY"
                        and sentences_list[idx_word + 2].upper() == "COME"
                    ):
                        print("WE ABOUT DEY COME !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "DEY"
                        and sentences_list[idx_sentences_list].upper() == "GO"
                        and sentences_list[idx_word + 1].upper() == "YOU"
                        and sentences_list[idx_word + 2].upper() == "GO"
                    ):
                        print("GO DEY YOU GO !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "EHM"
                        and sentences_list[idx_sentences_list].upper() == "PRACTICE"
                        and sentences_list[idx_word + 1].upper() == "EHM"
                        and sentences_list[idx_word + 2].upper() == "PRACTICE"
                    ):
                        print("PRACTICE EHM EHM PRACTICE !*!*!!!!")
                        idx_word += 2
                        continue

                    elif (
                        flag_diese is True
                        and sentences_list[idx_word].upper() == "SAID"
                    ):
                        idx_word += 1
                        continue

                    else:
                        break

                print("c_tier == c_word:", c_tier, c_word)
                # print(sentences_list[idx_sentences_list], sentences_list[idx_word])

                if c_tier == c_word:
                    new_sentence.append(token)
                    print(
                        sentence[j],
                        j,
                        sentences_list[idx_sentences_list],
                        idx_sentences_list,
                        i,
                        token_label,
                        " - token.upper() == token_label.upper() =",
                    )
                    i = i + 1
                    j = j + 1
                    idx_sentences_list += 1

                else:
                    new_sentence.append(token)
                    print(
                        sentence[j],
                        j,
                        sentences_list[idx_sentences_list],
                        idx_sentences_list,
                        i,
                        token_label,
                        " - token.upper() == token_label.upper() !=",
                    )
                    j = j + 1
                    idx_sentences_list += 1

            # Adding hidden characters to new sentence
            elif tier[i - 1][0] == "#":
                print(
                    "case  tier[i-1][0] == #:",
                    "sentence: ",
                    sentence[j],
                    j,
                    "sentences_list: ",
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    # sentences_list[idx_word],
                    "tier: ",
                    token_label,
                    tier[i][0],
                    i,
                )
                print("case  tier[i-1][0] == #:", "new_sentence: ", new_sentence)

                while not (
                    i < len(tier) - 1
                    and idx_sentences_list < len(sentences_list) - 1
                    and sentences_list[idx_sentences_list].upper() == tier[i][0].upper()
                    and (
                        sentences_list[idx_sentences_list + 1].upper()
                        == tier[i + 1][0].upper()
                        or (tier[i + 1][0].upper() == "#")
                    )
                ):
                    while j < len(sentence) and sentence[j] in punctuation_list:
                        new_sentence.append(sentence[j])
                        j += 1
                    if (
                        j < len(sentence)
                        and sentence[j].upper() == "DON'T"
                        and tier[i][0].upper() == "DO"
                    ):
                        break
                    if (
                        j < len(sentence)
                        and sentence[j].upper() == "YOU'LL"
                        and tier[i][0].upper() == "YOU"
                    ):
                        break
                    elif (
                        j < len(sentence)
                        and sentence[j].upper() == "DON'T"
                        and tier[i][0].upper() == "T"
                    ):
                        break
                    else:
                        if j == len(sentence):
                            j = 0
                            if l < len(non_gold_sentences) - 1:
                                l += 1
                            sentence = non_gold_sentences[l]
                            adjusted_non_gold_sentences.append(" ".join(new_sentence))
                            new_sentence = []

                        if idx_sentences_list < len(sentences_list):
                            print(
                                "add hidden characters 2: ",
                                sentences_list[idx_sentences_list],
                            )
                            print(
                                sentences_list[idx_sentences_list].upper(),
                                tier[i][0].upper(),
                            )
                            new_sentence.append(
                                "(" + sentences_list[idx_sentences_list] + ")"
                            )
                            idx_sentences_list += 1
                            j += 1

                        # This condition is specific to WAZL_15_MAC-Abi_MG
                        if (
                            idx_sentences_list < len(sentences_list) - 1
                            and sentences_list[idx_sentences_list + 1].upper() == "IT'S"
                            and tier[i + 1][0].upper() == "IT"
                        ):
                            break

                        if idx_sentences_list == len(sentences_list) - 1:
                            break
                        if (
                            sentences_list[idx_sentences_list + 1].upper() == "'M"
                            and tier[i + 1][0].upper() == "M"
                        ):
                            break
                        if (
                            j < len(sentence)
                            and sentence[j].upper() == "I"
                            and tier[i][0].upper() == "I"
                        ):
                            break

                print("new sentence: ", new_sentence)
                if j < len(sentence):
                    print(
                        "case  tier[i-1][0] == #:",
                        "sentence: ",
                        sentence[j],
                        j,
                        "sentences_list: ",
                        sentences_list[idx_sentences_list],
                        idx_sentences_list,
                        "tier: ",
                        token_label,
                        tier[i][0],
                        i,
                        "new sentence: ",
                        new_sentence,
                    )
            else:
                print(filename)
                print(
                    token,
                    j,
                    sentences_list[idx_sentences_list],
                    idx_sentences_list,
                    i,
                    token_label,
                    sentences_list[idx_word],
                    "====================else",
                    "idx_word",
                    sentences_list[idx_word],
                    "idx_sentences_list",
                    sentences_list[idx_sentences_list],
                )
                time.sleep(1000)
        l += 1
        adjusted_non_gold_sentences.append(" ".join(new_sentence))

    return adjusted_non_gold_sentences


def write_to_tsv(
    gold_sentences: list,
    non_gold_sentences: list,
    output_file_path: str,
    filename: str = None,
) -> None:
    """
    Ecrire les phrases gold et non-gold dans un fichier TSV.

    Parameters:
    gold_sentences (list): Liste des phrases gold.
    non_gold_sentences (list): Liste des phrases non-gold.
    output_file_path (str): Chemin du fichier de sortie.
    filename (str): Nom du fichier.

    Returns:
    None

    Variables:
    writer (csv.writer): Objet pour écrire dans le fichier.
    """
    if filename:
        with open(output_file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="\t")
            for gold, non_gold in zip(gold_sentences, non_gold_sentences):
                writer.writerow([filename, gold, non_gold])
    else:
        with open(output_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(["Gold", "Non-Gold"])
            for gold, non_gold in zip(gold_sentences, non_gold_sentences):
                writer.writerow([gold, non_gold])


def main():
    # Chemins des répertoires
    gold_dir = "SUD_Naija-NSC-master/non_gold"
    non_gold_dir = "SUD_Naija-NSC-master/non_gold"
    textgrid_dir = "TEXTGRID_WAV_nongold_sppas/"
    output_dir = "TSV/TSV_sentences_nongold_sppas/"

    # Obtenir tous les fichiers
    gold_files = get_files_from_directory(gold_dir, ".conllu")
    non_gold_files = get_files_from_directory(non_gold_dir, ".conllu")
    textgrid_files = get_files_from_directory(textgrid_dir, ".TextGrid")

    # Traitement pour chaque fichier
    for gold_file in gold_files:
        base_name = os.path.basename(gold_file).split(".")[0]

        if gold_file.endswith("MG.conllu") or gold_file.endswith("M.conllu"):
            # Construire les chemins pour les fichiers non_gold et textgrid correspondants
            non_gold_file = os.path.join(non_gold_dir, base_name + ".conllu")

            if base_name.startswith("ABJ"):
                folder = "_".join(base_name.split("_")[:3])
            else:
                folder = "_".join(base_name.split("_")[:2])

            textgrid_file = os.path.join(
                textgrid_dir, folder + "/" + base_name + "-syl_tok.TextGrid"
            )

            output_tsv_file_path = os.path.join(output_dir, base_name + ".tsv")
            # output_global_tsv_file_path = os.path.join(output_dir, 'all_sentences.tsv')
            output_global_tsv_file_path = os.path.join(
                output_dir, "all_sentences-nongold_sppas.tsv"
            )

            if not os.path.exists(output_global_tsv_file_path):
                with open(
                    output_global_tsv_file_path, "w", newline="", encoding="utf-8"
                ) as file:
                    writer = csv.writer(file, delimiter="\t")
                    writer.writerow(["File Name", "Gold", "Non-Gold"])

            if non_gold_file in non_gold_files:
                print(f"Traitement de {base_name}")
                print(f"Gold: {gold_file}")
                list_file = [
                    # "SUD_Naija-NSC-master/non_gold/WAZP_06_Tommys-Life-Story_M.conllu",
                    # "SUD_Naija-NSC-master/non_gold/LAG_18_Lagos-Districts_M.conllu",
                    # "SUD_Naija-NSC-master/non_gold/KAD_24_Biography_M.conllu",
                ]
                list_test = ["SUD_Naija-NSC-master/non_gold/ABJ_INF_11_Land_M.conllu"]

                # if "JOS_20" in gold_file:
                if gold_file not in list_file:
                    gold_sentences = extract_sentences(gold_file)
                    new_gold_sentences = [
                        " ".join(sentence) for sentence in gold_sentences
                    ]

                    tier_combined = extract_token_and_pause_times(textgrid_file)
                    non_gold_sentences = extract_sentences(non_gold_file)
                    adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(
                        non_gold_sentences, tier_combined, base_name
                    )

                    # Writing to TSV
                    write_to_tsv(
                        new_gold_sentences,
                        adjusted_non_gold_sentences,
                        output_tsv_file_path,
                    )
                    write_to_tsv(
                        new_gold_sentences,
                        adjusted_non_gold_sentences,
                        output_global_tsv_file_path,
                        filename=base_name,
                    )

            else:
                print(f"Fichier manquant pour {base_name}")


if __name__ == "__main__":
    main()
