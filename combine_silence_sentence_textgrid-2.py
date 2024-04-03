from praatio import tgio
import textgrid
from tqdm import tqdm
import os
import time
eps = 0.25

def fill_gaps_with_silence(tier, max_timestamp):
    new_intervals = []
    last_end = 0

    # Add existing intervals and look for gaps to fill with silence
    for start, end, label in tier.entryList:
        # If there's a gap before the current interval, add a silence
        if start > last_end:
            new_intervals.append((last_end, start, '#'))
        new_intervals.append((start, end, label))
        last_end = end

    # Check for a gap at the end
    if last_end < max_timestamp:
        new_intervals.append((last_end, max_timestamp, '#'))

    # Update the tier with the new intervals
    tier.entryList = new_intervals


def pitchtier_verify_silence(pitch_file, start, end):
    # Calculer la durée de l'intervalle
    interval_duration = end - start

    # Vérifier si la durée est supérieure à 0.15 seconde
    if interval_duration <= 0.15:
        # Considérer comme non silencieux directement
        return False
    else:
        return True


def align_silence(ipus_path, tokens_path):
    # Open the TextGrid files
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)

    # Get the tiers from the TextGrid objects
    ipus_tier = textgrid_ipus.tierDict['IPUs']
    combined_tier = textgrid_tokens.tierDict['Combined']

    # Loop over the intervals in the Combined tier
    for i, combined_interval in enumerate(combined_tier.entryList):
        if combined_interval.label == '#': 
            # Find the closest matching silence interval from IPUs tier
            closest_silence_ipu = min(
                [ipu_interval for ipu_interval in ipus_tier.entryList if ipu_interval.label == '#'],
                key=lambda x: abs(x.start - combined_interval.start)
            )

            # Create a new interval with the start and end times of the closest silence
            new_combined_interval = tgio.Interval(
                closest_silence_ipu.start,
                closest_silence_ipu.end,
                combined_interval.label)

            # Replace the interval in the combined tier
            combined_tier.entryList[i] = new_combined_interval

    # Save or return the modified TextGrid
    textgrid_tokens.tierDict['Combined'] = combined_tier
    return textgrid_tokens


def detect_silence_in_sentence(id_path, sent_path, syl_tok_path, output_tsv=None):
    base_name = os.path.splitext(os.path.basename(sent_path))[0]

    # Open the TextGrid files
    textgrid_id = tgio.openTextgrid(id_path)
    textgrid_sent = tgio.openTextgrid(sent_path)
    textgrid_syl_tok = tgio.openTextgrid(syl_tok_path)

    # Retrieve intervals with "#" in the 'Combined' tier
    phrases_with_hash = []
    for interval in textgrid_syl_tok.tierDict['Combined'].entryList:
        if "#" in interval[2]:
            xmin = interval[0]
            xmax = interval[1]

            # Find the corresponding phrases in the 'trans' tier
            for sent_interval in textgrid_sent.tierDict['trans'].entryList:
                if sent_interval[0] <= xmin and sent_interval[1] >= xmax:
                    # Initialize the index labels before and after the '#' interval
                    prev_index_label = None
                    next_index_label = None

                    # Iterate over the index intervals to find the previous label
                    for index_interval in reversed(textgrid_id.tierDict['index'].entryList):
                        if index_interval[1] <= xmin:
                            prev_index_label = index_interval[2]
                            break

                    # Iterate over the index intervals to find the next label
                    found_next_index = False
                    for index_interval in textgrid_id.tierDict['index'].entryList:
                        if index_interval[0] >= xmax:
                            next_index_label = index_interval[2]
                            found_next_index = True
                            break

                    # If the next index label is not found, use the last index label of the phrase
                    if not found_next_index:
                        next_index_label = textgrid_id.tierDict['index'].entryList[-1][2]

                    if prev_index_label is None:
                        print(f"Anomaly detected: file={base_name}, prev={prev_index_label}, next={next_index_label}, label={sent_interval[2]}")
                    else:
                        # Add the phrase and index labels to the list
                        phrases_with_hash.append((base_name, prev_index_label, next_index_label, sent_interval[2]))

    # # Write the phrases_with_hash to a TSV file
    # with open(output_tsv, 'w', encoding='utf-8') as f:
    #     for item in phrases_with_hash:
    #         f.write('\t'.join(item) + '\n')

    return phrases_with_hash


def create_tier(ipus_path, tokens_path, tier:str):
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)
    combined_textgrid = tgio.Textgrid()
    combine_intervals = []
    ipus_tier = textgrid_ipus.tierDict['IPUs']
    tokens_tier = textgrid_tokens.tierDict[tier]
    ipus_intervals = ipus_tier.entryList
    tokens_intervals = tokens_tier.entryList

    pos_ipu = 0
    size_ipu = len(ipus_intervals)
    pos_token = 0
    size_token = len(tokens_intervals)
    print("tokens_intervals: ", tokens_intervals)
    last_combine_end = 0
    is_inserted_diese = False
    is_after_space = False
    while pos_ipu < size_ipu and pos_token < size_token:
        # get ipu interval
        ipu_start, ipu_end, ipu_label = ipus_intervals[pos_ipu]
        # Process each token interval
        token_start, token_end, token_label = tokens_intervals[pos_token]
        if pos_token > 0 and tokens_intervals[pos_token - 1] != token_start:
            is_after_space = True
        if ipu_label == '#':
            print('#', ipu_start, ipu_end, token_start, token_end, last_combine_end)
            if pos_ipu == 0 and ipu_start > token_end:
                combine_intervals.append([token_start, token_end, token_label])
                last_combine_end = token_end
                pos_token += 1
                continue
            if ipu_start <= token_start <= token_end <= ipu_end:
                last_combine_end = ipu_start
                pos_token += 1
                is_inserted_diese = False
                print('A1')

            elif token_start < ipu_start and token_end < ipu_end :
                if is_after_space and last_combine_end < token_start:
                    token_start = last_combine_end
                    is_after_space = False
                combine_intervals.append([token_start, ipu_start, token_label])
                last_combine_end = ipu_start
                pos_token += 1
                is_inserted_diese = False
                print('A2')

            elif ipu_start <= token_start <= ipu_end <= token_end or pos_token == 0:
                if token_label == '#':
                    # At the beginning of the text
                    combine_intervals.append([min(ipu_start, token_start), ipu_end, '#'])
                    last_combine_end = ipu_end
                else:
                    if is_inserted_diese is False:
                        combine_intervals.append([last_combine_end, ipu_end, '#'])
                        is_inserted_diese = True
                    combine_intervals.append([ipu_end, token_end, token_label])
                    last_combine_end = token_end
                is_inserted_diese = False
                pos_ipu += 1
                pos_token += 1
                print(ipu_start, ipu_end, ipu_label, token_start, token_end, token_label)
                print('A3')
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
                    if combine_intervals[-1][2] == '#' and combine_intervals[-1][1] <= ipu_end:
                        combine_intervals[-1][1] = ipu_end
                    else:
                        combine_intervals.append([ipu_start, ipu_end, "#"])
                    combine_intervals.append([ipu_end, token_end, token_label])
                    last_combine_end = token_end
                pos_ipu += 1
                pos_token += 1
                is_inserted_diese = True
                print('A4.5')
            # Because of a space
            elif ipu_end <= token_start:
                print("????", combine_intervals[-1][0], combine_intervals[-1][1], ipu_start, ipu_end, ipu_start, ipu_end, '#')
                if is_after_space and combine_intervals[-1][1] != ipu_start:
                    combine_intervals[-1][1] = ipu_start
                if combine_intervals[-1][2] == '#' and combine_intervals[-1][1] <= ipu_end:
                    combine_intervals[-1][1] = ipu_end
                else:
                    combine_intervals.append([ipu_start, ipu_end, '#'])
                last_combine_end = ipu_end
                pos_ipu += 1
                is_inserted_diese = True
                print('A5')
            else:
                time.sleep(1000)
                print('impossible?')
            if pos_ipu == size_ipu -1:
                combine_intervals.append([ipu_start, ipu_end, '#'])
        else:
            #insert diese if "" is inluded in ipu and > 0.25
            if is_after_space:
                if ipu_start <= tokens_intervals[pos_token - 1][1] < token_start < ipu_end:
                    if token_start - tokens_intervals[pos_token - 1][1] > eps:
                        if combine_intervals[-1][2] == '#' and combine_intervals[-1][1] <= token_start:
                            combine_intervals[-1][1] = token_start
                        else:
                            combine_intervals.append([tokens_intervals[pos_token - 1][1], token_start, '#'])
                        last_combine_end = token_start
                        print('A #')
            if ipu_start <= token_start and token_end < ipu_end:
                pos_token += 1
                combine_intervals.append([last_combine_end, token_end, token_label])
                last_combine_end = token_end
                print(ipu_start, ipu_end, token_start, token_end, token_label)
                print('A7')
                is_inserted_diese = False

            elif ipu_start <= token_start and token_end >= ipu_end:
                if len(combine_intervals) > 1 and combine_intervals[-1][1] > ipu_end and combine_intervals[-2][2] == '#':
                    print('len(combine_intervals) > 1 and combine_intervals[-1][1] > ipu_end and combine_intervals[-2][2] == ',combine_intervals[-1][1], ipu_end, combine_intervals[-2][2] == '#')
                    combine_intervals[-1][1] = ipu_end
                    last_combine_end = ipu_end
                pos_ipu += 1
                is_inserted_diese = False
                print(ipu_start, ipu_end, ipu_label, token_start, token_end, token_label)
                print('A9')

            elif ipu_end < token_start:
                print('normal?')
                print(ipu_start, ipu_end, token_start, token_end)
                pos_ipu += 1
                is_inserted_diese = True
                print('A10')
            else:
                print(ipu_start, ipu_end, ipu_label, token_start, token_end, token_label)
                time.sleep(111)
                print("impossible cases ?")

    # Créer le tier combiné et l'ajouter au TextGrid
    if tier == 'TokensAlign':
        combined_tier = tgio.IntervalTier("Combined", combine_intervals, minT=0, maxT=combined_textgrid.maxTimestamp)
    if tier == 'SyllAlign':
        combined_tier = tgio.IntervalTier("SyllSil", combine_intervals, minT=0, maxT=combined_textgrid.maxTimestamp)

    return combined_tier

def save_textgrid(token_syl_tier, syllsil_tier, output_path):
    # Create a new TextGrid object
    new_textgrid = tgio.Textgrid()

    # Add the tiers to the new TextGrid
    new_textgrid.addTier(token_syl_tier)
    new_textgrid.addTier(syllsil_tier)

    new_textgrid.save(output_path)

# base_folder = "./TEXTGRID_WAV_nongold/"
base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN/"
# tsv_folder = "./TSV/"
# pitchtier_folder = "./Praat/non_gold/"
pitchtier_folder = "./Praat/"
all_phrases_with_hash = [] 


# Test the functions
# create_tier("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-ipus.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-id.TextGrid", "./Praat/JOS_01_People-Of-Plateau_MG.PitchTier", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syll.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")
# align_silence("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-ipus.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")
# detect_silence_in_sentence("./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-id.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG.TextGrid", "./TEXTGRID_WAV_gold_non_gold_TALN/JOS_01/JOS_01_People-Of-Plateau_MG-syl_tok.TextGrid")

# Iterate through all the subfolders
for subdir in tqdm(sorted(os.listdir(base_folder))):
    subdir_path = os.path.join(base_folder, subdir)

    # Check if the item is a folder
    if os.path.isdir(subdir_path):
        # List to store the names of .TextGrid files
        ipus_files = []
        id_files = []
        sent_files = []
        syll_files = []

        # Iterate through all files in the subfolder
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

        # Process the files if they are present
        for ipus_file in ipus_files:
            # Construct the paths to the ipus and id TextGrids
            ipus_textgrid_path = os.path.join(subdir_path, ipus_file)
            # id_textgrid_name = ipus_file.replace("_M-ipus.TextGrid", "_M-id.TextGrid")
            # sent_textgrid_name = ipus_file.replace("_M-ipus.TextGrid", "_M.TextGrid")
            id_textgrid_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG-id.TextGrid")
            sent_textgrid_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG.TextGrid")
            syll_textgrid_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG-syll.TextGrid")
            sent_textgrid_path = None

            # Construire le chemin vers le fichier PitchTier correspondant
            # pitchtier_file_name = ipus_file.replace("_M-ipus.TextGrid", "_M.PitchTier")
            pitchtier_file_name = ipus_file.replace("_MG-ipus.TextGrid", "_MG.PitchTier")
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

                    # Construct the output path for syl_tok tier
                    # syl_tok_output_path = ipus_textgrid_path.replace("_M-ipus.TextGrid", "_M-syl_tok.TextGrid")
                    syl_tok_output_path = ipus_textgrid_path.replace("_MG-ipus.TextGrid", "_MG-syl_tok.TextGrid")
                    # syl_tok_output_path = ipus_textgrid_path.replace("_MG-ipus.TextGrid", "_MG-syl_tok-15mars.TextGrid")
                    # output_tsv_path = os.path.join(subdir_path, ipus_file.replace("_M-ipus.TextGrid", "_silences.tsv"))

                    # Create the syl_tok tier and align the silences
                    # print(file, ipus_textgrid_path, id_textgrid_path, pitchtier_path, syll_textgrid_path, syl_tok_output_path)
                    # if ipus_textgrid_path == "./TEXTGRID_WAV_gold_non_gold_TALN/LAG_12/LAG_12_Insurance_MG-ipus.TextGrid":
                    combined_tier = create_tier(ipus_textgrid_path, id_textgrid_path, 'TokensAlign')
                    syll_tier = create_tier(ipus_textgrid_path, syll_textgrid_path, 'SyllAlign')

                    save_textgrid(combined_tier, syll_tier, syl_tok_output_path)

                    # align_silence(ipus_textgrid_path, syl_tok_output_path)
                    # phrases_with_hash = detect_silence_in_sentence(id_textgrid_path, sent_textgrid_path, syl_tok_output_path)
                    # all_phrases_with_hash.extend(phrases_with_hash)
                else:
                    print(f"PitchTier file not found for {ipus_file}\n")

# Write the accumulated results to a TSV file
# # output_tsv_path = os.path.join(tsv_folder, "global_silences-non_gold_15mars.tsv")
# output_tsv_path = os.path.join(tsv_folder, "global_silences-non_gold.tsv")
# with open(output_tsv_path, 'w', encoding='utf-8') as f:
#     for item in all_phrases_with_hash:
#         f.write('\t'.join(item) + '\n')