"""
Script permettant de combiner les intervalles de silence et de tokens/syllabes dans les fichiers TextGrid.

Le script prend en entrée les fichiers TextGrid contenant les intervalles de silence et de tokens/syllabes, et les combine pour créer un nouveau tier 'Combined' dans un nouveau fichier TextGrid.

Requis:
- TextGrids IPUs -ipus.TextGrid
- TextGrids Tokens -id.TextGrid (obtenus avec le script get_index.py) et Syllabes -syll.TextGrid
- TextGrids Phrases _MG.TextGrid (obtenus avec le script text_grid.py)

Commande:
python3 ./Python_Stage_23_24/detect_silence_textgrid/2-combine_silence_sentence_textgrid.py
"""

import os
import time

from praatio import tgio
from tqdm import tqdm

eps = 0.25 # durée 


def align_silence(ipus_path: str, tokens_path: str) -> tgio.Textgrid:
    """
    Aligne les intervalles de silence dans le tier 'Combined' du fichier TextGrid 'tokens_path'

    Parameters:
    ipus_path (str): Le chemin vers le fichier TextGrid contenant les intervalles de silence
    tokens_path (str): Le chemin vers le fichier TextGrid contenant les intervalles de tokens

    Returns:
    TextGrid: Le fichier TextGrid modifié

    Variables:
    textgrid_ipus (TextGrid): L'objet TextGrid contenant les intervalles de silence
    textgrid_tokens (TextGrid): L'objet TextGrid contenant les intervalles de tokens
    ipus_tier (IntervalTier): Le tier contenant les intervalles de silence
    combined_tier (IntervalTier): Le tier contenant les intervalles de tokens
    combined_interval (Interval): L'intervalle de tokens à aligner
    closest_silence_ipu (Interval): L'intervalle de silence le plus proche
    new_combined_interval (Interval): Le nouvel intervalle de tokens aligné
    """
    # Open the TextGrid files
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)

    # Get the tiers from the TextGrid objects
    ipus_tier = textgrid_ipus.tierDict["IPUs"]
    combined_tier = textgrid_tokens.tierDict["Combined"]

    # Loop over the intervals in the Combined tier
    for i, combined_interval in enumerate(combined_tier.entryList):
        if combined_interval.label == "#":
            # Find the closest matching silence interval from IPUs tier
            closest_silence_ipu = min(
                [
                    ipu_interval
                    for ipu_interval in ipus_tier.entryList
                    if ipu_interval.label == "#"
                ],
                key=lambda x: abs(x.start - combined_interval.start),
            )

            # Create a new interval with the start and end times of the closest silence
            new_combined_interval = tgio.Interval(
                closest_silence_ipu.start,
                closest_silence_ipu.end,
                combined_interval.label,
            )

            # Replace the interval in the combined tier
            combined_tier.entryList[i] = new_combined_interval

    # Save or return the modified TextGrid
    textgrid_tokens.tierDict["Combined"] = combined_tier
    return textgrid_tokens


def detect_silence_in_sentence(
    id_path: str, sent_path: str, syl_tok_path: str, output_tsv: str = None
) -> list:
    """
    Detecte les intervalles de silence dans les phrases du fichier 'sent_path' et les associe aux index du fichier 'id_path'

    Parameters:
    id_path (str): Le chemin vers le fichier TextGrid contenant les index
    sent_path (str): Le chemin vers le fichier TextGrid contenant les phrases
    syl_tok_path (str): Le chemin vers le fichier TextGrid contenant les intervalles de syllabes et tokens
    output_tsv (str): Le chemin vers le fichier TSV de sortie

    Returns:
    list: Une liste de tuples contenant les informations des phrases avec des intervalles de silence

    Variables:
    base_name (str): Le nom de base du fichier
    textgrid_id (TextGrid): L'objet TextGrid contenant les index
    textgrid_sent (TextGrid): L'objet TextGrid contenant les phrases
    textgrid_syl_tok (TextGrid): L'objet TextGrid contenant les intervalles de syllabes et tokens
    phrases_with_hash (list): La liste des phrases avec des intervalles de silence
    """
    base_name = os.path.splitext(os.path.basename(sent_path))[0]

    # Ouvrir les fichiers TextGrid
    textgrid_id = tgio.openTextgrid(id_path)
    textgrid_sent = tgio.openTextgrid(sent_path)
    textgrid_syl_tok = tgio.openTextgrid(syl_tok_path)

    # Initialiser la liste des phrases avec des intervalles de silence
    phrases_with_hash = []
    for interval in textgrid_syl_tok.tierDict["Combined"].entryList:
        if "#" in interval[2]:
            xmin = interval[0]
            xmax = interval[1]

            # Trouver l'intervalle de phrase correspondant
            for sent_interval in textgrid_sent.tierDict["trans"].entryList:
                if sent_interval[0] <= xmin and sent_interval[1] >= xmax:
                    # Initialiser les labels des index précédent et suivant
                    prev_index_label = None
                    next_index_label = None

                    # Itérer sur les intervalles d'index pour trouver le label précédent
                    for index_interval in reversed(
                        textgrid_id.tierDict["index"].entryList
                    ):
                        if index_interval[1] <= xmin:
                            prev_index_label = index_interval[2]
                            break

                    # Iterer sur les intervalles d'index pour trouver le label suivant
                    found_next_index = False
                    for index_interval in textgrid_id.tierDict["index"].entryList:
                        if index_interval[0] >= xmax:
                            next_index_label = index_interval[2]
                            found_next_index = True
                            break

                    # Si le label suivant n'est pas trouvé, prendre le dernier label
                    if not found_next_index:
                        next_index_label = textgrid_id.tierDict["index"].entryList[-1][
                            2
                        ]

                    if prev_index_label is None:
                        print(
                            f"Anomaly detected: file={base_name}, prev={prev_index_label}, next={next_index_label}, label={sent_interval[2]}"
                        )
                    else:
                        # Ajouter les informations à la liste
                        phrases_with_hash.append(
                            (
                                base_name,
                                prev_index_label,
                                next_index_label,
                                sent_interval[2],
                            )
                        )

    # # Write the phrases_with_hash to a TSV file
    # with open(output_tsv, 'w', encoding='utf-8') as f:
    #     for item in phrases_with_hash:
    #         f.write('\t'.join(item) + '\n')

    return phrases_with_hash


def create_tier(ipus_path: str, tokens_path: str, tier: str) -> tgio.IntervalTier:
    """
    Crée un tier 'Combined' à partir des intervalles de 'IPUs' et 'Tokens' des fichiers TextGrid

    Parameters:
    ipus_path (str): Le chemin vers le fichier TextGrid contenant les intervalles de silence
    tokens_path (str): Le chemin vers le fichier TextGrid contenant les intervalles de tokens
    tier (str): Le nom du tier à créer

    Returns:
    IntervalTier: Le tier 'Combined' contenant les intervalles combinés

    Variables:
    textgrid_ipus (TextGrid): L'objet TextGrid contenant les intervalles de silence
    textgrid_tokens (TextGrid): L'objet TextGrid contenant les intervalles de tokens
    combined_textgrid (TextGrid): L'objet TextGrid contenant les intervalles combinés
    combine_intervals (list): La liste des intervalles combinés
    ipus_tier (IntervalTier): Le tier contenant les intervalles de silence
    tokens_tier (IntervalTier): Le tier contenant les intervalles de tokens
    """
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)
    combined_textgrid = tgio.Textgrid()
    combine_intervals = []
    ipus_tier = textgrid_ipus.tierDict["IPUs"]
    tokens_tier = textgrid_tokens.tierDict[tier]
    ipus_intervals = ipus_tier.entryList
    tokens_intervals = tokens_tier.entryList

    # print("tokens_intervals: ", tokens_intervals)

    pos_ipu = 0
    pos_token = 0
    last_combine_end = 0.0
    is_inserted_diese = False
    is_after_space = False
    ipu_start_tmp = 0
    is_diese_inf = False

    if ipus_intervals[0][0] != 0.0:
        ipus_intervals.insert(0, [0.0, ipus_intervals[0][0], "#"])

    size_ipu = len(ipus_intervals)
    size_token = len(tokens_intervals)

    while pos_ipu < size_ipu and pos_token < size_token:
        # get ipu interval
        ipu_start, ipu_end, ipu_label = ipus_intervals[pos_ipu]
        # Process each token interval
        token_start, token_end, token_label = tokens_intervals[pos_token]

        print(
            "**",
            ipu_start,
            ipu_end,
            ipu_label,
            token_start,
            token_end,
            token_label,
            last_combine_end,
        )
        if is_diese_inf:
            ipu_start = ipu_start_tmp
            is_diese_inf = False

        print(
            "*#*",
            ipu_start,
            ipu_end,
            ipu_label,
            token_start,
            token_end,
            token_label,
            last_combine_end,
        )

        if pos_token > 0 and tokens_intervals[pos_token - 1] != token_start:
            is_after_space = True

        if ipu_label == "#":
            print("#", ipu_start, ipu_end, token_start, token_end, last_combine_end)


            if pos_ipu == 0 and ipu_start > token_end:
                combine_intervals.append([token_start, token_end, token_label])
                print("pos_ipu == 0 and ipu_start > token_end", combine_intervals[-1])
                last_combine_end = token_end
                pos_token += 1
                continue

            if ipu_start <= token_start <= token_end <= ipu_end:
                last_combine_end = ipu_start
                pos_token += 1
                is_inserted_diese = False
                print("A1")

            elif token_start < ipu_start and token_end < ipu_end:
                if is_after_space and last_combine_end < token_start:
                    token_start = last_combine_end
                    is_after_space = False
                combine_intervals.append([token_start, ipu_start, token_label])
                last_combine_end = ipu_start
                pos_token += 1
                is_inserted_diese = False
                print("A2")

            elif ipu_start <= token_start <= ipu_end <= token_end or pos_token == 0:
                if token_label == "#":
                    # At the beginning of the text
                    combine_intervals.append(
                        [min(ipu_start, token_start), ipu_end, "#"]
                    )
                    last_combine_end = ipu_end
                else:
                    if is_inserted_diese is False:
                        combine_intervals.append([last_combine_end, ipu_end, "#"])
                        is_inserted_diese = True
                    # print("combine_intervals[-1][1] : ", combine_intervals[-1][1], ipu_end)
                    combine_intervals.append([ipu_end, token_end, token_label])
                    # print("combine_intervals[-1] : ", combine_intervals[-1], token_end)
                    last_combine_end = token_end
                is_inserted_diese = False
                pos_ipu += 1
                pos_token += 1
                print(
                    ipu_start, ipu_end, ipu_label, token_start, token_end, token_label
                )
                print("A3")

            elif token_start <= ipu_start <= ipu_end <= token_end:
                left = (ipu_start - token_start) - (token_end - ipu_end)
                if left >= 0:
                    if is_after_space and last_combine_end < token_start:
                        token_start = last_combine_end
                        is_after_space = False
                    combine_intervals.append([token_start, ipu_start, token_label])
                    combine_intervals.append([ipu_start, ipu_end, "#"])
                    last_combine_end = ipu_end
                else:
                    combine_intervals[-1][1] = ipu_start
                    if (
                        combine_intervals[-1][2] == "#"
                        and combine_intervals[-1][1] <= ipu_end
                    ):
                        combine_intervals[-1][1] = ipu_end
                    else:
                        combine_intervals.append([ipu_start, ipu_end, "#"])
                    combine_intervals.append([ipu_end, token_end, token_label])
                    last_combine_end = token_end
                pos_ipu += 1
                pos_token += 1
                is_inserted_diese = True
                print("A4.5")

            # A cause d'un espace
            elif ipu_end <= token_start:
                print(
                    "????",
                    combine_intervals[-1][0],
                    combine_intervals[-1][1],
                    ipu_start,
                    ipu_end,
                    ipu_start,
                    ipu_end,
                    "#",
                )
                if is_after_space and combine_intervals[-1][1] != ipu_start:
                    combine_intervals[-1][1] = ipu_start
                if (
                    combine_intervals[-1][2] == "#"
                    and combine_intervals[-1][1] <= ipu_end
                ):
                    combine_intervals[-1][1] = ipu_end
                else:
                    combine_intervals.append([ipu_start, ipu_end, "#"])
                last_combine_end = ipu_end
                pos_ipu += 1
                is_inserted_diese = True
                print("A5")
            else:
                time.sleep(1000)
                print("impossible?")

            if pos_ipu == size_ipu - 1:
                print(
                    "pos_ipu == size_ipu",
                    last_combine_end,
                    combine_intervals[-1],
                    token_end,
                    ipu_end,
                )
                if last_combine_end < ipu_end:
                    combine_intervals.append([last_combine_end, ipu_end, ipu_label])

        else:
            # inserer # si " " est inclus dans l'ipu et > 0.25
            if is_after_space:
                if (
                    ipu_start
                    <= tokens_intervals[pos_token - 1][1]
                    < token_start
                    < ipu_end
                ):
                    if token_start - tokens_intervals[pos_token - 1][1] > eps:
                        if (
                            combine_intervals[-1][2] == "#"
                            and combine_intervals[-1][1] <= token_start
                        ):
                            combine_intervals[-1][1] = token_start
                        else:
                            combine_intervals.append(
                                [tokens_intervals[pos_token - 1][1], token_start, "#"]
                            )
                            print("combine_intervals[-1] A# : ", combine_intervals[-1])
                        last_combine_end = token_start
                        print("A #")

            if (
                pos_token == 0
                and token_label == "#"
                and ipu_start > token_start
                and token_end < ipu_end
            ):
                print("# en pos_token 0 :", ipu_start, ipu_end, token_start, token_end)
                combine_intervals.append([token_start, token_end, token_label])
                pos_token += 1
                last_combine_end = token_end
                is_inserted_diese = False

            if ipu_start <= token_start and token_end < ipu_end:
                combine_intervals.append([last_combine_end, token_end, token_label])
                last_combine_end = token_end
                pos_token += 1
                print(ipu_start, ipu_end, token_start, token_end, token_label)
                print(combine_intervals[-1])
                print("A7")
                is_inserted_diese = False

            elif token_start <= ipu_start and token_end < ipu_end:
                if token_label != "#":
                    print(
                        "*@*",
                        ipu_start,
                        ipu_end,
                        ipu_label,
                        token_start,
                        token_end,
                        token_label,
                        ", combine interval -1: ",
                        combine_intervals[-1],
                    )
                    combine_intervals.append(
                        [combine_intervals[-1][1], token_end, token_label]
                    )
                    print("combine interval -1 *@*: ", combine_intervals[-1])
                    pos_token += 1
                    is_inserted_diese = False

            elif token_start < ipu_start and token_end > ipu_end:
                print(
                    "@@@ : ",
                    ipu_start,
                    ipu_end,
                    ipu_label,
                    token_start,
                    token_end,
                    token_label,
                    "combine interval -1: ",
                    combine_intervals[-1],
                )
                combine_intervals.append(
                    [combine_intervals[-1][1], ipu_end, token_label]
                )
                pos_token += 1
                is_inserted_diese = False

            elif ipu_start <= token_start and token_end >= ipu_end:
                if (
                    len(combine_intervals) > 1
                    and combine_intervals[-1][1] > ipu_end
                    and combine_intervals[-2][2] == "#"
                ):
                    print(
                        "len(combine_intervals) > 1 and combine_intervals[-1][1] > ipu_end and combine_intervals[-2][2] == ",
                        combine_intervals[-1][1],
                        ipu_end,
                        combine_intervals[-2][2] == "#",
                    )
                    combine_intervals[-1][1] = ipu_end
                    last_combine_end = ipu_end
                elif pos_token == size_token - 1:
                    if ipu_end == token_end:
                        combine_intervals.append([token_start, token_end, token_label])
                        print("Last Token", combine_intervals[-1])
                pos_ipu += 1
                is_inserted_diese = False
                print(
                    " ipu_s < t_s et t_e > ipu_e",
                    ipu_start,
                    ipu_end,
                    ipu_label,
                    token_start,
                    token_end,
                    token_label,
                )
                print("A9")

            elif ipu_end < token_start:
                print("normal?")
                print(ipu_start, ipu_end, token_start, token_end)
                pos_ipu += 1
                is_inserted_diese = True
                print("A10")

            else:
                print(
                    ipu_start, ipu_end, ipu_label, token_start, token_end, token_label
                )
                print("impossible cases ?")
                time.sleep(111)

    # Combiner les intervalles vides dans IPUS
    if combine_intervals[0][0] != 0.0:
        combine_intervals.insert(0, [0.0, combine_intervals[0][0], "#"])

    # print("combine_intervals Origin : ", combine_intervals)
    # print(ipus_path)
    for i in range(1, len(combine_intervals)):
        if combine_intervals[i - 1][1] < combine_intervals[i][0]:
            combine_intervals.insert(
                i, [combine_intervals[i - 1][1], combine_intervals[i][0], "*"]
            )

    # print("combine_intervals : ", combine_intervals)
    new_combine_intervals = []
    for idx in range(1, len(combine_intervals)):
        # print(combine_intervals[idx - 1], combine_intervals[idx])

        if combine_intervals[idx][2] == "#":
            if (
                combine_intervals[idx - 1][2] == "*"
                and combine_intervals[idx - 2][2] == "#"
            ):
                new_combine_intervals[-1][0] = min(
                    combine_intervals[idx - 2][0], combine_intervals[idx][0]
                )
                new_combine_intervals[-1][1] = max(
                    combine_intervals[idx - 2][1], combine_intervals[idx][1]
                )
                # print(
                #     "XYU: ",
                #     combine_intervals[idx][0],
                #     combine_intervals[idx - 1][0],
                #     combine_intervals[idx][1],
                #     combine_intervals[idx - 1][1],
                #     combine_intervals[idx][2],
                #     combine_intervals[idx - 1][2],
                #     new_combine_intervals[-1],
                # )

            elif (
                combine_intervals[idx - 1][2] == "*"
                and combine_intervals[idx - 2][2] != "#"
            ):
                # print(
                #     "\nXXY",
                #     combine_intervals[idx][0],
                #     combine_intervals[idx - 1][0],
                #     combine_intervals[idx][1],
                #     combine_intervals[idx - 1][1],
                #     combine_intervals[idx][2],
                #     combine_intervals[idx - 1][2],
                #     new_combine_intervals[-1],
                #     "\n",
                # )
                combine_intervals[idx][0] = combine_intervals[idx - 1][0]
                new_combine_intervals.append(combine_intervals[idx])

            elif (
                combine_intervals[idx - 1][2] == "#"
                and combine_intervals[idx][2] == "#"
            ):
                # print(
                #     "\nYY",
                #     combine_intervals[idx][0],
                #     combine_intervals[idx - 1][0],
                #     combine_intervals[idx][1],
                #     combine_intervals[idx - 1][1],
                #     combine_intervals[idx][2],
                #     combine_intervals[idx - 1][2],
                #     new_combine_intervals[-1],
                # )
                new_combine_intervals[-1][0] = min(
                    combine_intervals[idx][0],
                    combine_intervals[idx - 1][0],
                    new_combine_intervals[-1][0],
                )
                new_combine_intervals[-1][1] = max(
                    combine_intervals[idx][1],
                    combine_intervals[idx - 1][1],
                    new_combine_intervals[-1][1],
                )

            elif (
                combine_intervals[idx][0] < combine_intervals[idx - 1][1]
                and combine_intervals[idx - 1][2] != "#"
            ):
                # print(
                #     "\nXX",
                #     combine_intervals[idx][0],
                #     combine_intervals[idx - 1][0],
                #     combine_intervals[idx][1],
                #     combine_intervals[idx - 1][1],
                #     combine_intervals[idx][2],
                #     combine_intervals[idx - 1][2],
                #     new_combine_intervals[-1],
                # )
                combine_intervals[idx][0] = new_combine_intervals[-1][1]
                new_combine_intervals.append(combine_intervals[idx])

            else:
                print("add interval #", combine_intervals[idx], "\n")
                new_combine_intervals.append(combine_intervals[idx])

        elif combine_intervals[idx][2] == "*":
            continue

        elif combine_intervals[idx][0] == combine_intervals[idx][1]:
            combine_intervals[idx][0] = combine_intervals[idx][0] - 0.0001
            new_combine_intervals.append(combine_intervals[idx])

        else:
            if combine_intervals[idx][0] == combine_intervals[idx - 1][0]:
                if combine_intervals[idx - 1] == combine_intervals[idx]:
                    # print(
                    #     "\nZZX",
                    #     combine_intervals[idx],
                    #     combine_intervals[idx - 1],
                    #     new_combine_intervals[-1],
                    # )
                    continue
                else:
                    # print(
                    #     "\nZX",
                    #     combine_intervals[idx],
                    #     combine_intervals[idx - 1],
                    #     new_combine_intervals[-1],
                    # )
                    combine_intervals[idx][0] = new_combine_intervals[-1][1]
                    new_combine_intervals.append(combine_intervals[idx])

            elif combine_intervals[idx][0] < combine_intervals[idx - 1][1]:
                if combine_intervals[idx][0] == 0.0:
                    # print("\nZZT", combine_intervals[idx], combine_intervals[idx - 1])
                    combine_intervals[idx][0] = combine_intervals[idx - 1][1]
                    new_combine_intervals.append(combine_intervals[idx])
                else:
                    # print(
                    #     "\nZT",
                    #     combine_intervals[idx],
                    #     combine_intervals[idx - 1],
                    #     new_combine_intervals[-1],
                    # )
                    combine_intervals[idx][0] = new_combine_intervals[-1][1]
                    if combine_intervals[idx][0] < combine_intervals[idx][1]:
                        new_combine_intervals.append(combine_intervals[idx])
                    else:
                        # print(
                        #     " ******  combine_intervals[idx][0] == combine_intervals[idx][1]",
                        #     combine_intervals[idx],
                        #     new_combine_intervals[-1],
                        # )
                        continue

            else:
                print("add interval", combine_intervals[idx], "\n")
                new_combine_intervals.append(combine_intervals[idx])

    print("\nnew intervals : ", new_combine_intervals)

    if new_combine_intervals[0][0] != 0.0:
        new_combine_intervals.insert(0, [0.0, new_combine_intervals[0][0], "#"])

    # Créer le tier combiné et l'ajouter au TextGrid
    if tier == "TokensAlign":
        combined_tier = tgio.IntervalTier(
            "Combined",
            new_combine_intervals,
            minT=0,
            maxT=combined_textgrid.maxTimestamp,
        )
    if tier == "SyllAlign":
        combined_tier = tgio.IntervalTier(
            "SyllSil",
            new_combine_intervals,
            minT=0,
            maxT=combined_textgrid.maxTimestamp,
        )

    return combined_tier


def save_textgrid(
    token_syl_tier: tgio.IntervalTier, syllsil_tier: tgio.IntervalTier, output_path: str
) -> None:
    """
    Sauvegarde le TextGrid modifié dans un fichier

    Parameters:
    token_syl_tier (IntervalTier): Le tier contenant les intervalles de tokens/syllabes
    syllsil_tier (IntervalTier): Le tier contenant les intervalles de silence
    output_path (str): Le chemin de sortie du fichier TextGrid

    Returns:
    None

    Variables:
    new_textgrid (TextGrid): Le nouvel objet TextGrid
    """
    # Créer un nouvel objet TextGrid
    new_textgrid = tgio.Textgrid()

    # Ajouter les tiers au TextGrid
    new_textgrid.addTier(token_syl_tier)
    new_textgrid.addTier(syllsil_tier)

    new_textgrid.save(output_path)


# base_folder = "./TEXTGRID_WAV_nongold/"
base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad"
tsv_folder = "./TSV/"
# pitchtier_folder = "./Praat/non_gold/"
pitchtier_folder = "./Praat/"
all_phrases_with_hash = []


# Test the functions
# create_tier("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-ipus.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-id.TextGrid", "./Praat/JOS_01_People-Of-Plateau_MG.PitchTier", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syll.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")
# align_silence("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-ipus.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")
# detect_silence_in_sentence("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-id.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")

# Iterer sur les sous-dossiers
for subdir in tqdm(sorted(os.listdir(base_folder))):
    subdir_path = os.path.join(base_folder, subdir)

    # Checker si le sous-dossier est un dossier
    if os.path.isdir(subdir_path):
        # Liste pour stocker les noms des fichiers TextGrid
        ipus_files = []
        id_files = []
        sent_files = []
        syll_files = []

        # Iterer sur les fichiers dans le sous-dossier
        for file in os.listdir(subdir_path):
            # print(file)
            # if file.endswith("_M-ipus.TextGrid"):
            if file.endswith("_MG-ipus.TextGrid"):
                ipus_files.append(file)

            # elif file.endswith("_M-id.TextGrid"):
            elif file.endswith("_MG-id.TextGrid"):
                id_files.append(file)

            elif file.endswith("_MG-syll.TextGrid"):
                syll_files.append(file)

            # elif file.endswith("_M.TextGrid"):
            elif file.endswith("_MG.TextGrid"):
                sent_files.append(file)

        # Procéder si les fichiers TextGrid sont trouvés
        for ipus_file in ipus_files:
            # Construire les chemins vers les fichiers TextGrid
            ipus_textgrid_path = os.path.join(subdir_path, ipus_file)
            # id_textgrid_name = ipus_file.replace("_M-ipus.TextGrid", "_M-id.TextGrid")
            # sent_textgrid_name = ipus_file.replace("_M-ipus.TextGrid", "_M.TextGrid")
            id_textgrid_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG-id.TextGrid")
            sent_textgrid_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG.TextGrid")
            syll_textgrid_name = ipus_file.replace(
                "_MG-ipus.TextGrid", "_MG-syll.TextGrid"
            )
            sent_textgrid_path = None

            # Construire le chemin vers le fichier PitchTier correspondant
            # pitchtier_file_name = ipus_file.replace("_M-ipus.TextGrid", "_M.PitchTier")
            pitchtier_file_name = ipus_file.replace(
                "_MG-ipus.TextGrid", "_MG.PitchTier"
            )
            pitchtier_path = os.path.join(pitchtier_folder, pitchtier_file_name)

            # Vérifier si le fichier PitchTier existe
            if os.path.exists(pitchtier_path):
                for sent_file in sent_files:
                    # print(sent_file, sent_textgrid_name)
                    if sent_file == sent_textgrid_name:
                        sent_textgrid_path = os.path.join(subdir_path, sent_file)
                        break

                if id_textgrid_name in id_files and sent_textgrid_path is not None:
                    id_textgrid_path = os.path.join(subdir_path, id_textgrid_name)
                    print(id_textgrid_path)
                    syll_textgrid_path = os.path.join(subdir_path, syll_textgrid_name)

                    # Construire le chemin de sortie pour le tier syl_tok
                    # syl_tok_output_path = ipus_textgrid_path.replace("_M-ipus.TextGrid", "_M-syl_tok.TextGrid")
                    syl_tok_output_path = ipus_textgrid_path.replace(
                        "_MG-ipus.TextGrid", "_MG-syl_tok.TextGrid"
                    )

                    # Créer le tier syl_tok et aligner les silences
                    # print(file, ipus_textgrid_path, id_textgrid_path, pitchtier_path, syll_textgrid_path, syl_tok_output_path)
                    # if syl_tok_output_path == "./TEXTGRID_WAV_gold_non_gold_TALN_15ms_02-04/ABJ_GWA_12/ABJ_GWA_12_Accident_MG-syl_tok.TextGrid":
                    combined_tier = create_tier(
                        ipus_textgrid_path, id_textgrid_path, "TokensAlign"
                    )
                    syll_tier = create_tier(
                        ipus_textgrid_path, syll_textgrid_path, "SyllAlign"
                    )
                    save_textgrid(combined_tier, syll_tier, syl_tok_output_path)

                    align_silence(ipus_textgrid_path, syl_tok_output_path)
                    phrases_with_hash = detect_silence_in_sentence(
                        id_textgrid_path, sent_textgrid_path, syl_tok_output_path
                    )
                    all_phrases_with_hash.extend(phrases_with_hash)
                else:
                    print(f"PitchTier file not found for {ipus_file}\n")

# Ecrire les phrases avec des intervalles de silence dans un fichier TSV
output_tsv_path = os.path.join(tsv_folder, "global_silences-non_gold_10-05_05ms.tsv")
with open(output_tsv_path, "w", encoding="utf-8") as f:
    for item in all_phrases_with_hash:
        f.write("\t".join(item) + "\n")
