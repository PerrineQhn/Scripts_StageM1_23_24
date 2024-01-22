from praatio import tgio
import textgrid
from tqdm import tqdm
import os


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
    point_count = 0  # Compteur pour les points de pitch

    # Open the pitch file
    with open(pitch_file, 'r') as file:
        lignes = file.readlines()
        for ligne in lignes:
            if "number =" in ligne:
                nombre = float(ligne.split('=')[1])
                if start <= nombre <= end:
                    point_count += 1

    # Debugging: Afficher les informations
    # print(f"Interval: {start} - {end}, Points found: {point_count}")

    # S'il y a moins de 2 points, considérer comme un silence
    return point_count < 2


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


def create_tier(ipus_path, tokens_path, pitch_path, output_path):
    # Open the TextGrid files
    textgrid_ipus = tgio.openTextgrid(ipus_path)
    textgrid_tokens = tgio.openTextgrid(tokens_path)

    # Create a new TextGrid object for the combined intervals
    combined_textgrid = tgio.Textgrid()

    combine_intervals = []

    # Get the intervals from the 'IPUs' and 'TokensAlign' tiers
    ipus_tier = textgrid_ipus.tierDict['IPUs']
    tokens_tier = textgrid_tokens.tierDict['TokensAlign']

    ipus_intervals = ipus_tier.entryList
    tokens_intervals = tokens_tier.entryList

    # Process each token interval
    for token in tokens_intervals:
        token_start, token_end, token_label = token

        # Initialize the updated start and end times for the token
        updated_start = token_start
        updated_end = token_end
        silence_in_token = False

        # Check for silences within the token interval
        for ipu in ipus_intervals:
            ipu_start, ipu_end, ipu_label = ipu
            if ipu_label == '#' and token_start < ipu_end and token_end > ipu_start:
                # Utiliser la fonction mise à jour pour vérifier le silence
                is_silence = pitchtier_verify_silence(pitch_path, ipu_start, ipu_end)
                if is_silence:  # Si c'est un silence
                    silence_in_token = True
                    # Ajuster les bornes du token pour exclure le silence
                    if (ipu_start - token_start) > (token_end - ipu_end):
                        updated_end = min(ipu_start, updated_end)
                    else:
                        updated_start = max(ipu_end, updated_start)

        # Append either silence or token based on the check, ensuring correct order
        if updated_start < updated_end:
            combine_intervals.append([updated_start, updated_end, token_label])
        elif updated_start > updated_end:
            # Log or handle the anomaly here
            print(f"Anomaly : start={updated_start}, end={updated_end}, label={token_label}")


    # Create the combined tier and add it to the TextGrid
    combined_tier = tgio.IntervalTier("Combined", combine_intervals, minT=0, maxT=combined_textgrid.maxTimestamp)
    combined_textgrid.addTier(combined_tier)
    fill_gaps_with_silence(combined_tier, combined_textgrid.maxTimestamp)
    # Save the new TextGrid
    combined_textgrid.save(output_path)

# base_folder = "./TEXTGRID_WAV_nongold/"
base_folder = "./TEXTGRID_WAV_gold_non_gold_TALN/"
tsv_folder = "./TSV/"
# pitchtier_folder = "./Praat/non_gold/"
pitchtier_folder = "./Praat/"
all_phrases_with_hash = [] 


# # Test the functions
# create_tier("./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-ipus.TextGrid", "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-id.TextGrid", "./Praat/non_gold/KAD_24_Biography_M.PitchTier", "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-syl_tok.TextGrid")
# align_silence("./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-ipus.TextGrid", "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-syl_tok.TextGrid")
# detect_silence_in_sentence("./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-id.TextGrid", "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M.TextGrid", "./TEXTGRID_WAV_nongold/KAD_24/KAD_24_Biography_M-syl_tok.TextGrid")

# Iterate through all the subfolders
for subdir in tqdm(os.listdir(base_folder)):
    subdir_path = os.path.join(base_folder, subdir)

    # Check if the item is a folder
    if os.path.isdir(subdir_path):
        # List to store the names of .TextGrid files
        ipus_files = []
        id_files = []
        sent_files = []

        # Iterate through all files in the subfolder
        for file in os.listdir(subdir_path):
            # print(file)
            # if file.endswith("_M-ipus.TextGrid"):
            if file.endswith("_MG-ipus.TextGrid"):
                ipus_files.append(file)
            # elif file.endswith("_M-id.TextGrid"):
            elif file.endswith("_MG-id.TextGrid"):
                id_files.append(file)
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
                    # print(id_textgrid_path)
                    # Construct the output path for syl_tok tier
                    # syl_tok_output_path = ipus_textgrid_path.replace("_M-ipus.TextGrid", "_M-syl_tok.TextGrid")
                    syl_tok_output_path = ipus_textgrid_path.replace("_MG-ipus.TextGrid", "_MG-syl_tok.TextGrid")
                    # output_tsv_path = os.path.join(subdir_path, ipus_file.replace("_M-ipus.TextGrid", "_silences.tsv"))

                    # Create the syl_tok tier and align the silences
                    create_tier(ipus_textgrid_path, id_textgrid_path, pitchtier_path, syl_tok_output_path)
                    align_silence(ipus_textgrid_path, syl_tok_output_path)
                    phrases_with_hash = detect_silence_in_sentence(id_textgrid_path, sent_textgrid_path, syl_tok_output_path)
                    all_phrases_with_hash.extend(phrases_with_hash)
                else:
                    print(f"PitchTier file not found for {ipus_file}\n")

# # Write the accumulated results to a TSV file
# output_tsv_path = os.path.join(tsv_folder, "global_silences-non_gold.tsv")
# with open(output_tsv_path, 'w', encoding='utf-8') as f:
#     for item in all_phrases_with_hash:
#         f.write('\t'.join(item) + '\n')