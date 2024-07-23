"""
Récupération des index des mots dans les fichiers TextGrid à partir des fichiers conllu.
"""

import os
import sys
import token

from praatio import textgrid as tgio

from conll3 import *


def create_textgrid(file_path, input_textgrid_path, output_textgrid_path):
    textgrid = tgio.openTextgrid(input_textgrid_path, includeEmptyIntervals=True)
    tier = textgrid.getTier("TokensAlign")
    tokens_align_intervals = tier.entries
    index_intervals = []
    token_pos = 0
    trees = conllFile2trees(file_path)
    special_cases = [
        "o'clock",
        "billionaire's",
        "dat's",
        "Africa's",
        "O'neill",
        "a'ah",
        "it's",
        "John's",
        "God's",
        "voter's",
        "admin's",
        "Zimbabwe's",
        "people's",
        "guy's",
    ]
    hyphenated_special_cases = [
        "ex-soldier",
        "self-sufficient",
        "twenty-fourth",
        "ninety-six",
        "D-Morris",
        "Port-Harcourt",
    ]

    print(file_path)
    for tree_pos, tree in enumerate(trees):
        # print(tokens_align_intervals[token_pos])
        tmp_interval = (
            tokens_align_intervals[token_pos][0],
            tokens_align_intervals[token_pos][1],
            tokens_align_intervals[token_pos][2],
        )

        if tmp_interval[2] == "#" or tmp_interval[2] == "":
            index_intervals.append(tmp_interval)
            token_pos += 1
        words = tree.words
        i = 0
        # print(words)
        while i < len(words) and token_pos < len(tokens_align_intervals):

            tmp_interval = (
                tokens_align_intervals[token_pos][0],
                tokens_align_intervals[token_pos][1],
                tokens_align_intervals[token_pos][2],
            )

            pos = tree[i + 1].get("tag")
            if "'" in words[i] and words[i] not in special_cases:
                if words[i].upper() == "'M":
                    if "'M" in words[i].upper() and tmp_interval[2].upper() == "M":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "'S":
                    if "'S" in words[i].upper() and tmp_interval[2].upper() == "S":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "'LL":
                    if "'LL" in words[i].upper() and tmp_interval[2].upper() == "LL":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "'RE":
                    if "'RE" in words[i].upper() and tmp_interval[2].upper() == "RE":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "CHAMPIONS'":
                    if (
                        "CHAMPIONS'" in words[i].upper()
                        and tmp_interval[2].upper() == "CHAMPIONS"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "N'T":
                    if "N'" in words[i].upper() and tmp_interval[2].upper() == "N":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if "'T" in words[i].upper() and tmp_interval[2].upper() == "T":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "HM'M":
                    if "HM'" in words[i].upper() and tmp_interval[2].upper() == "HM":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if "M" in words[i].upper() and tmp_interval[2].upper() == "M":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MOMO'S":
                    if (
                        "MOMO'" in words[i].upper()
                        and tmp_interval[2].upper() == "MOMO"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if "S" in words[i].upper() and tmp_interval[2].upper() == "S":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    c = words[i].split("'")
                    print("words with an ' : ", words[i], " :: ", c)
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval = (
                                tmp_interval[0],
                                tmp_interval[1],
                                "{}.{}".format(tree_pos + 1, i + 1),
                            )
                            index_intervals.append(tmp_interval)
                            token_pos += 1
                        i += 1
                        token_pos += 1

            elif "-" in words[i] and words[i] not in hyphenated_special_cases:
                if words[i].upper() == "CO-COMMANDER":
                    if "CO-" in words[i].upper() and tmp_interval[2].upper() == "CO-":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "COMMANDER" in words[i].upper()
                        and tmp_interval[2].upper() == "COMMANDER"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MA-FIREWOOD":
                    if "MA-" in words[i].upper() and tmp_interval[2].upper() == "MA":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "FIREWOOD" in words[i].upper()
                        and tmp_interval[2].upper() == "FIREWOOD"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MA-AKARA":
                    if "MA-" in words[i].upper() and tmp_interval[2].upper() == "MA":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "AKARA" in words[i].upper()
                        and tmp_interval[2].upper() == "AKARA"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "UN-AFRICAN":
                    if "UN-" in words[i].upper() and tmp_interval[2].upper() == "UN":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "AFRICAN" in words[i].upper()
                        and tmp_interval[2].upper() == "AFRICAN"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "E-SERVICES":
                    if "E-" in words[i].upper() and tmp_interval[2].upper() == "E":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "SERVICES" in words[i].upper()
                        and tmp_interval[2].upper() == "SERVICES"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "PRE-DEGREE":
                    if "PRE-" in words[i].upper() and tmp_interval[2].upper() == "PRE":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "DEGREE" in words[i].upper()
                        and tmp_interval[2].upper() == "DEGREE"
                    ):
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "PRO-EUROPEAN":
                    print(words[i])
                    if "PRO-" in words[i].upper() and tmp_interval[2].upper() == "PRO":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if (
                        "EUROPEAN" in words[i].upper()
                        and tmp_interval[2].upper() == "EUROPEAN"
                    ):
                        print("European")
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    c = words[i].split("-")
                    print("words with a - : ", words[i], " :: ", c)
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval = (
                                tmp_interval[0],
                                tmp_interval[1],
                                "{}.{}".format(tree_pos + 1, i + 1),
                            )
                            index_intervals.append(tmp_interval)
                            token_pos += 1
                        i += 1
                        token_pos += 1

            elif "." in words[i] and words[i] != "p.m.":
                if words[i].upper() == "O.D.S.":
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if "D.S" in words[i].upper() and tmp_interval[2].upper() == "D.S":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "A.M.":
                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1

                    if "M." in words[i].upper() and tmp_interval[2].upper() == "M.":
                        tmp_interval = (
                            tmp_interval[0],
                            tmp_interval[1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        )
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    words[i] = words[i].replace(".", " point ")
                    c = words[i].split()
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval = (
                                tmp_interval[0],
                                tmp_interval[1],
                                "{}.{}".format(tree_pos + 1, i + 1),
                            )
                            index_intervals.append(tmp_interval)
                            token_pos += 1
                        i += 1
                        token_pos += 1

            elif words[i].strip("~").upper() == tmp_interval[2].upper():
                if words[i] != "#":
                    tmp_interval = (
                        tmp_interval[0],
                        tmp_interval[1],
                        "{}.{}".format(tree_pos + 1, i + 1),
                    )
                token_pos += 1
                i += 1
                index_intervals.append(tmp_interval)

            elif pos == "PUNCT":
                i += 1
                continue

            else:
                i += 1
                print(
                    f"Error with word '{words[i]}' at position {i}, interval '{tmp_interval[2]}'"
                )

    # Supprimer les chevauchements et les doublons
    cleaned_intervals = []
    last_end = -1
    for interval in sorted(index_intervals, key=lambda x: (x[0], x[1])):
        if interval[0] >= last_end:
            cleaned_intervals.append(interval)
            last_end = interval[1]

    t = tgio.IntervalTier("index", cleaned_intervals)
    textgrid.addTier(t)
    textgrid.save(output_textgrid_path, format="long_textgrid", includeBlankSpaces=True)


def create_textgrid_nongold(file_path, input_textgrid_path, output_textgrid_path):
    print(file_path)
    textgrid = tgio.openTextgrid(input_textgrid_path, includeEmptyIntervals=True)
    tier = textgrid.getTier("TokensAlign")
    tokens_align_intervals = tier.entries
    index_intervals = []
    token_pos = 0
    special_cases = [
        "o'clock",
        "billionaire's",
        "dat's",
        "Africa's",
        "O'neill",
        "a'ah",
        "it's",
        "John's",
        "God's",
        "voter's",
        "admin's",
        "Zimbabwe's",
        "people's",
        "guy's",
    ]
    hyphenated_special_cases = [
        "ex-soldier",
        "self-sufficient",
        "twenty-fourth",
        "ninety-six",
        "D-Morris",
        "Port-Harcourt",
        "port-harcourt",
        "d-morris",
    ]
    trees = conllFile2trees(file_path)
    for tree_pos, tree in enumerate(trees):
        if token_pos >= len(tokens_align_intervals):
            print("Reached end of tokens_align_intervals")
            break

        tmp_interval = [
            tokens_align_intervals[token_pos][0],
            tokens_align_intervals[token_pos][1],
            tokens_align_intervals[token_pos][2],
        ]

        if tmp_interval[2] == "#" or tmp_interval[2] == "":
            index_intervals.append(tmp_interval)
            token_pos += 1
        words = tree.words
        words = [word.lower() for word in words]
        i = 0

        while i < len(words) and token_pos < len(tokens_align_intervals):
            tmp_interval = [
                tokens_align_intervals[token_pos][0],
                tokens_align_intervals[token_pos][1],
                tokens_align_intervals[token_pos][2],
            ]
            pos = tree[i + 1].get("tag")

            if (
                "{" in tmp_interval[2]
                and "}" in tmp_interval[2]
                and "|c" in tmp_interval[2]
            ):
                tmp_interval[2] = (
                    tmp_interval[2].replace("{", "").replace("}", "").replace("|c", "")
                )

            elif (
                "{" in tmp_interval[2]
                and "}" in tmp_interval[2]
                and "|" in tmp_interval[2]
            ):
                tmp_interval[2] = (
                    tmp_interval[2].replace("{", "").replace("}", "").replace("|", "")
                )

            symbols_to_remove = ("]", "[", ",", ".", "<", "|c", ")", "//", "'", "||")
            if (
                pos != "PUNCT"
                and words[i].endswith(symbols_to_remove)
                and words[i] != "p.m."
                and words[i] != "a.m."
                and words[i] != "o.a."
                and words[i] != "o.d.s."
                and words[i] != "s."
            ):
                for symbol in symbols_to_remove:
                    if words[i].endswith(symbol):
                        words[i] = words[i][: -len(symbol)]
                        break

            elif words[i].startswith("'"):
                words[i] = words[i].replace("'", "")

            if pos == "PUNCT":
                i += 1
                continue

            elif "'" in words[i] and "'" not in tokens_align_intervals[token_pos][2]:
                c = words[i].split("'")
                for x in c:
                    tmp_value = tokens_align_intervals[token_pos][2]
                    if x == tmp_interval[2]:
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1

            elif (
                "-" in words[i]
                and words[i] != "vice-president"
                and words[i] not in hyphenated_special_cases
                and "-" not in tokens_align_intervals[token_pos][2]
                and words[i] != "co-commander"
            ):
                c = words[i].split("-")
                for x in c:
                    tmp_value = tokens_align_intervals[token_pos][2]
                    if x == tmp_value:
                        tmp_interval = [
                            tokens_align_intervals[token_pos][0],
                            tokens_align_intervals[token_pos][1],
                            "{}.{}".format(tree_pos + 1, i + 1),
                        ]
                        print(tmp_interval, x, tokens_align_intervals[token_pos][2])
                        index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1

            elif words[i] == "co-commander":
                print(words[i])
                if "CO-" in tokens_align_intervals[token_pos][2].upper():
                    tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                    index_intervals.append(tmp_interval)
                    token_pos += 1

                if "COMMANDER" in tokens_align_intervals[token_pos][2].upper():
                    tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                    index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1

            elif "." in words[i] and words[i] != "p.m." and words[i] != "s.":
                if words[i].upper() == "A.M.":
                    print("WORD UPPER", words[i].upper())
                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [
                            tokens_align_intervals[token_pos][0],
                            tokens_align_intervals[token_pos][1],
                            tokens_align_intervals[token_pos][2],
                        ]

                    if "M." in words[i].upper() and tmp_interval[2].upper() == "M.":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        print(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "O.A.":
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [
                            tokens_align_intervals[token_pos][0],
                            tokens_align_intervals[token_pos][1],
                            tokens_align_intervals[token_pos][2],
                        ]

                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        print(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "O.D.S.":
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [
                            tokens_align_intervals[token_pos][0],
                            tokens_align_intervals[token_pos][1],
                            tokens_align_intervals[token_pos][2],
                        ]

                    if "D.S" in words[i].upper() and tmp_interval[2].upper() == "D.S":
                        tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    print(words[i])
                    words[i] = words[i].replace(".", " point ")
                    c = words[i].split()
                    print(c)
                    for x in c:
                        tmp_interval = tokens_align_intervals[token_pos][2]
                        if x == tmp_interval:
                            tmp_interval = [
                                tokens_align_intervals[token_pos][0],
                                tokens_align_intervals[token_pos][1],
                                "{}.{}".format(tree_pos + 1, i + 1),
                            ]
                            index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

            elif words[i].strip("~").upper() == tmp_interval[2].upper():
                if words[i] != "#":
                    tmp_interval[2] = "{}.{}".format(tree_pos + 1, i + 1)
                token_pos += 1
                i += 1
                index_intervals.append(tmp_interval)

            else:
                print(words[i])
                print(f"Error with word '{words[i]}' at position {i}, interval '{tmp_interval[2]}'\n")
                i += 1

    cleaned_intervals = []
    last_end = -1
    for interval in sorted(index_intervals, key=lambda x: (x[0], x[1])):
        if interval[0] >= last_end:
            cleaned_intervals.append(interval)
            last_end = interval[1]

    # Create the IntervalTier with cleaned intervals
    t = tgio.IntervalTier("index", cleaned_intervals)
    textgrid.addTier(t)
    textgrid.save(output_textgrid_path, format="long_textgrid", includeBlankSpaces=True)


def get_index_function(conllu_file: str, tg_file: str):
    """
    Fonction pour générer les index des mots dans les fichiers TextGrid à partir des fichiers conllu pour 1 fichier

    Parameters
    conllu_file (str): le chemin du fichier conllu
    tg_file (str): le chemin du fichier TextGrid
    """
    # print(input_textgrid_path)
    output_textgrid_path = os.path.join(
        tg_file.replace("-palign.TextGrid", "-id.TextGrid")
    )

    # Create TextGrid
    if conllu_file.endswith("_MG.conllu"):
        # if files == "WAZP_04_Ponzi-Scheme_MG.conllu":
        # create_textgrid(conllu_file, tg_file, output_textgrid_path)
        create_textgrid_nongold(conllu_file, tg_file, output_textgrid_path)

    elif conllu_file.endswith("_M.conllu"):
        # if files == "ENU_07_South-Eastern-Politics_M.conllu":
        create_textgrid_nongold(conllu_file, tg_file, output_textgrid_path)


if __name__ == "__main__":
    conllu_folder = "./data/SUD_Naija-NSC-master/gold_nongold/"
    textgrid_base_folder = "./data/TG_WAV/"

    for files in os.listdir(conllu_folder):
        if files.endswith("M.conllu") or files.endswith("MG.conllu"):
            file_path = os.path.join(conllu_folder, files)
            # print(file_path)
            # Adjust the folder path based on the file name
            if files.startswith("ABJ"):
                folder_name = "_".join(files.split("_")[:3])
            else:
                folder_name = "_".join(files.split("_")[:2])

            # Construct the specific TextGrid folder path
            textgrid_folder = os.path.join(textgrid_base_folder, folder_name)

            # Construct the paths for input and output TextGrid files
            input_textgrid_path = os.path.join(
                textgrid_folder, files.replace(".conllu", "-palign.TextGrid")
            )
            # print(input_textgrid_path)
            output_textgrid_path = os.path.join(
                textgrid_folder, files.replace(".conllu", "-id.TextGrid")
            )

            # Create TextGrid
            if files.endswith("_MG.conllu"):
                if "PRT_01" not in files:
                    create_textgrid_nongold(
                        file_path, input_textgrid_path, output_textgrid_path
                    )
                    print(
                        "###################################################################\n"
                    )

            if files.endswith("_M.conllu"):
                # if files == "ENU_07_South-Eastern-Politics_M.conllu":
                create_textgrid_nongold(
                    file_path, input_textgrid_path, output_textgrid_path
                )
