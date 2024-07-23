import os
import collections.abc
import glob
import re
import urllib.request
from conll3 import *

def extract_syllable_info(misc_dict, syl_num):
    """ Extrait les informations d'une syllabe spécifique. """
    base_key = f"Syl{syl_num}"
    align_begin = misc_dict.get(f"{base_key}AlignBegin", "_")
    # print(align_begin)
    align_end = misc_dict.get(f"{base_key}AlignEnd", "_")
    slope_glo = misc_dict.get(f"{base_key}SlopeGlo", "_")
    slope_loc = misc_dict.get(f"{base_key}SlopeLoc", "_")
    duree = int(align_end) - int(align_begin) if align_end != '_' else 0

    return align_begin, align_end, slope_glo, slope_loc, duree

def extract_occurrences_obj(file_path):
    occurrences = []
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    for tree in trees:
        tree_str = str(tree)
        sent_id_match = re.search(r'# sent_id = (.+)', tree_str)
        sent_id = sent_id_match.group(1) if sent_id_match else "_"
        words = tree.words
        index_inverse = len(words) - 1

        # Extraction des alignements de fin de phrase
        align_end_sent = "_"
        while index_inverse >= 0:
            word = tree[index_inverse]
            pos = word.get("tag", "_")
            if pos != 'PUNCT':
                misc_word_dict = convert_misc_to_dict(word.get("misc", ""))
                align_end_sent = int(misc_word_dict.get("AlignEnd", "_"))
                break
            index_inverse -= 1

        # Extraction des alignements de début de phrase
        align_begin_sent = "_"
        for index in range(1, len(words)+1):
            word = tree[index]
            pos = word.get("tag", "_")
            if pos != 'PUNCT':
                misc_begin_dict = convert_misc_to_dict(word.get("misc", ""))
                align_begin_sent = int(misc_begin_dict.get("AlignBegin", "_"))
                break

        for index in range(1, len(words)+1):
            word = tree[index]
            pos = word.get("tag", "_")
            if pos != 'PUNCT':
                misc_dict = convert_misc_to_dict(word.get("misc", "_"))
                syllables_info = {f"Syl{syl_num}": extract_syllable_info(misc_dict, syl_num) for syl_num in range(1, 9)}

                occurrence = {
                    "file_name": file_name,
                    "sent_id": sent_id,
                    "id": word.get("id"),
                    "form": word.get("t", "_"),
                    "pos": pos,
                    "align_begin_sent": align_begin_sent,
                    "align_end_sent": align_end_sent,
                }

                for syl_num, info in syllables_info.items():
                    occurrence[f"align_begin_{syl_num}"] = info[0]
                    occurrence[f"align_end_{syl_num}"] = info[1]
                    occurrence[f"{syl_num}_slope_glo"] = info[2]
                    occurrence[f"{syl_num}_slope_loc"] = info[3]
                    occurrence[f"duree_{syl_num}"] = info[4]

                occurrences.append(occurrence)

    # print(occurrences)
    return occurrences

# Function to extract all occurrences from files in a directory
def extract_all_occurrences_obj(directory_path):
    occurrences = []  # List to store all occurrences
    for root, dirs, files in os.walk(directory_path):
        if "non_gold" in dirs:
            dirs.remove("non_gold")
        for file in files:
            if file.endswith(".conllu") and "MG" in file:
                file_path = os.path.join(root, file)
                occurrences += extract_occurrences_obj(file_path)
    return occurrences

# Function to convert a "misc" string to a dictionary
def convert_misc_to_dict(misc):
    result_dict = {}  # Dictionary to store additional information
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

# Function to write occurrences to a TSV file
def write_occurrences_to_tsv(occurrences, output_path):
    with open(output_path, "w") as file:
        # Write the header row for the TSV file
        file.write("File\tSent_ID\tID\tForm\tPOS\tSyl1AlignBegin\tSyl1AlignEnd\tSyl2AlignBegin\t"
                   "Syl2AlignEnd\tSyl3AlignBegin\tSyl3AlignEnd\tSyl4AlignBegin\tSyl4AlignEnd\tSyl5AlignBegin\tSyl5AlignEnd\t"
                   "Syl6AlignBegin\tSyl6AlignEnd\tSyl7AlignBegin\tSyl7AlignEnd\tSyl8AlignBegin\tSyl8AlignEnd\t"
                   "DureeSyl1\tDureeSyl2\tDureeSyl3\tDureeSyl4\tDureeSyl5\tDureeSyl6\tDureeSyl7\tDureeSyl8\t"
                   "Sent_AlignBegin\tSent_AlignEnd\t"
                   "Syl1SlopeGlo\tSyl2SlopeGlo\tSyl3SlopeGlo\tSyl4SlopeGlo\tSyl5SlopeGlo\tSyl6SlopeGlo\tSyl7SlopeGlo\tSyl8SlopeGlo\t"
                   "Syl1SlopeLoc\tSyl2SlopeLoc\tSyl3SlopeLoc\tSyl4SlopeLoc\tSyl5SlopeLoc\tSyl6SlopeLoc\tSyl7SlopeLoc\tSyl8SlopeLoc\n")

        # Write the occurrences to the TSV file
        for occurrence in occurrences:
            # print(occurrence)
            file.write(
                f"{occurrence['file_name']}\t{occurrence['sent_id']}\t{occurrence['id']}\t"
                f"{occurrence['form']}\t"
                f"{occurrence['pos']}\t"
                f"{occurrence['align_begin_Syl1']}\t{occurrence['align_end_Syl1']}\t"
                f"{occurrence['align_begin_Syl2']}\t{occurrence['align_end_Syl2']}\t"
                f"{occurrence['align_begin_Syl3']}\t{occurrence['align_end_Syl3']}\t"
                f"{occurrence['align_begin_Syl4']}\t{occurrence['align_end_Syl4']}\t"
                f"{occurrence['align_begin_Syl5']}\t{occurrence['align_end_Syl5']}\t"
                f"{occurrence['align_begin_Syl6']}\t{occurrence['align_end_Syl6']}\t"
                f"{occurrence['align_begin_Syl7']}\t{occurrence['align_end_Syl7']}\t"
                f"{occurrence['align_begin_Syl8']}\t{occurrence['align_end_Syl8']}\t"
                f"{occurrence['duree_Syl1']}\t{occurrence['duree_Syl2']}\t{occurrence['duree_Syl3']}\t{occurrence['duree_Syl4']}\t"
                f"{occurrence['duree_Syl5']}\t{occurrence['duree_Syl6']}\t{occurrence['duree_Syl7']}\t{occurrence['duree_Syl8']}\t"
                f"{occurrence['align_begin_sent']}\t{occurrence['align_end_sent']}\t"
                f"{occurrence['Syl1_slope_glo']}\t{occurrence['Syl2_slope_glo']}\t{occurrence['Syl3_slope_glo']}\t{occurrence['Syl4_slope_glo']}\t"
                f"{occurrence['Syl5_slope_glo']}\t{occurrence['Syl5_slope_glo']}\t{occurrence['Syl7_slope_glo']}\t{occurrence['Syl8_slope_glo']}\t"
                f"{occurrence['Syl1_slope_loc']}\t{occurrence['Syl2_slope_loc']}\t{occurrence['Syl3_slope_loc']}\t{occurrence['Syl4_slope_loc']}\t"
                f"{occurrence['Syl5_slope_loc']}\t{occurrence['Syl6_slope_loc']}\t{occurrence['Syl7_slope_loc']}\t{occurrence['Syl8_slope_loc']}\n"
            )


# Path to the directory containing the files
directory_path = "conllu_syllables_18janv/"

# Path to the output TSV file
output_tsv_obj = "TSV/align_begin_align_end_syl_29_01.tsv"

# Extract all occurrences from the files in the directory
occurrences_obj = extract_all_occurrences_obj(directory_path)
# Write the occurrences to the TSV file
write_occurrences_to_tsv(occurrences_obj, output_tsv_obj)
