import os
import collections.abc
import glob
import re
import urllib.request
from conll3 import *

# Function to extract occurrences of term1 and term2 from a conllu file
def extract_occurrences_obj(file_path):
    # List to store all occurrences
    occurrences = []

    # Convert the conllu file to dependency trees
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    for tree in trees:
        # Convert the tree to a string
        tree_str = str(tree)

        # Extract the sentence ID (Sent_ID) and sentence text from the tree
        sent_id_match = re.search(r'# sent_id = (.+)', tree_str)
        sent = re.search(r'# text = (.+)', tree_str)
        sent_id = sent_id_match.group(1) if sent_id_match else "_"
        sent_text = sent.group(1) if sent else ""

        words = tree.words
        index = 1
        align_begin_sent, align_end_sent = '', ''

        # Variables to store information for each syllable (Syl1, Syl2, etc.)
        align_begin_T1_Syl2, align_begin_T1_Syl3, align_begin_T1_Syl4, align_begin_T1_Syl5, align_begin_T1_Syl6, align_begin_T1_Syl7, align_begin_T1_Syl8 = 0, 0, 0, 0, 0, 0, 0
        align_end_T1_Syl2, align_end_T1_Syl3, align_end_T1_Syl4, align_end_T1_Syl5, align_end_T1_Syl6, align_end_T1_Syl7, align_end_T1_Syl8 = 0, 0, 0, 0, 0, 0, 0
        duree_syl2, duree_syl3, duree_syl4, duree_syl5, duree_syl6, duree_syl7, duree_syl8 = 0, 0, 0, 0, 0, 0, 0
        index_inverse = len(words) - 1

        # Find the end alignment of the sentence by traversing the words in reverse order
        while index_inverse >= 1:
            pos = tree[index].get("tag", "_")
            if index_inverse == len(words) - 1 and pos != 'PUNCT':
                misc_word = tree[index_inverse].get("misc", "")
            elif index_inverse == len(words) - 1 and pos == 'PUNCT':
                misc_word = tree[index_inverse - 1].get("misc", "")
            misc_word_dict = convert_misc_to_dict(misc_word)
            align_end_sent = int(misc_word_dict.get("AlignEnd", "_"))

            index_inverse -= 1

        while index < len(words):
            pos = tree[index].get("tag", "_")

            # Find the start alignment of the sentence
            if index == 1 and pos == 'PUNCT':
                misc_begin = tree[index + 1].get("misc", "")
            elif index == 1 and pos != 'PUNCT':
                misc_begin = tree[index].get("misc", "")
            misc_begin_dict = convert_misc_to_dict(misc_begin)
            align_begin_sent = int(misc_begin_dict.get("AlignBegin", "_"))

            if pos != 'PUNCT':
                # Extract information for each word (T1) in the sentence
                id_T1 = tree[index].get("id")
                form_T1 = tree[index].get("t", "_")
                pos_T1 = tree[index].get("tag", "_")
                misc_T1 = tree[index].get("misc", "_")
                misc_T1_dict = convert_misc_to_dict(misc_T1)
                align_begin_T1_Syl1 = misc_T1_dict.get("Syl1AlignBegin", "_")
                align_end_T1_Syl1 = misc_T1_dict.get("Syl1AlignEnd", "_")
                if align_end_T1_Syl1 != '_':
                    duree_syl1 = int(align_end_T1_Syl1) - int(align_begin_T1_Syl1)
                else:
                    align_begin_T1_Syl1 = '_'
                    align_end_T1_Syl1 = '_'
                    duree_syl1 = 0

                # Extract information for the subsequent syllables (Syl2, Syl3, etc.) if they exist
                if "Syl2" in misc_T1_dict:
                    align_begin_T1_Syl2 = misc_T1_dict.get("Syl2AlignBegin", "_")
                    align_end_T1_Syl2 = misc_T1_dict.get("Syl2AlignEnd", "_")
                    if align_end_T1_Syl2 != '_':
                        duree_syl2 = int(align_end_T1_Syl2) - int(align_begin_T1_Syl2)
                    else:
                        duree_syl2 = 0
                else:
                    align_begin_T1_Syl2 = '_'
                    align_end_T1_Syl2 = '_'
                    duree_syl2 = 0

                # Extract information for the other syllables (Syl3, Syl4, etc.) in the same way
                if "Syl3" in misc_T1_dict:
                    align_begin_T1_Syl3 = misc_T1_dict.get("Syl3AlignBegin", "_")
                    align_end_T1_Syl3 = misc_T1_dict.get("Syl3AlignEnd", "_")
                    if align_end_T1_Syl3 != '_':
                        duree_syl3 = int(align_end_T1_Syl3) - int(align_begin_T1_Syl3)
                    else:
                        duree_syl3 = 0
                else:
                    align_begin_T1_Syl3 = '_'
                    align_end_T1_Syl3 = '_'
                    duree_syl3 = 0
                    syl3_slope_glo = '_'
                    syl3_slope_loc = '_'

                # Extract information for the other syllables (Syl3, Syl4, etc.) in the same way
                if "Syl4" in misc_T1_dict:
                    align_begin_T1_Syl4 = misc_T1_dict.get("Syl4AlignBegin", "_")
                    align_end_T1_Syl4 = misc_T1_dict.get("Syl4AlignEnd", "_")
                    if align_end_T1_Syl4 != '_':
                        duree_syl4 = int(align_end_T1_Syl4) - int(align_begin_T1_Syl4)
                    else:
                        duree_syl4 = 0
                else:
                    align_begin_T1_Syl4 = '_'
                    align_end_T1_Syl4 = '_'
                    duree_syl4 = 0

                if "Syl5" in misc_T1_dict:
                    align_begin_T1_Syl5 = misc_T1_dict.get("Syl5AlignBegin", "_")
                    align_end_T1_Syl5 = misc_T1_dict.get("Syl5AlignEnd", "_")
                    if align_end_T1_Syl5 != '_':
                        duree_syl5 = int(align_end_T1_Syl5) - int(align_begin_T1_Syl5)
                    else:
                        duree_syl5 = 0
                else:
                    align_begin_T1_Syl5 = '_'
                    align_end_T1_Syl5 = '_'
                    duree_syl5 = 0
                    syl5_slope_glo = '_'
                    syl5_slope_loc = '_'

                if "Syl6" in misc_T1_dict:
                    align_begin_T1_Syl6 = misc_T1_dict.get("Syl6AlignBegin", "_")
                    align_end_T1_Syl6 = misc_T1_dict.get("Syl6AlignEnd", "_")
                    if align_end_T1_Syl6 != '_':
                        duree_syl6 = int(align_end_T1_Syl6) - int(align_begin_T1_Syl6)
                    else:
                        duree_syl6 = 0
                else:
                    align_begin_T1_Syl6 = '_'
                    align_end_T1_Syl6 = '_'
                    duree_syl6 = 0

                if "Syl7" in misc_T1_dict:
                    align_begin_T1_Syl7 = misc_T1_dict.get("Syl7AlignBegin", "_")
                    align_end_T1_Syl7 = misc_T1_dict.get("Syl7AlignEnd", "_")
                    if align_end_T1_Syl7 != '_':
                        duree_syl7 = int(align_end_T1_Syl7) - int(align_begin_T1_Syl7)
                    else:
                        duree_syl7 = 0
                else:
                    align_begin_T1_Syl7 = '_'
                    align_end_T1_Syl7 = '_'
                    duree_syl7 = 0

                if "Syl8" in misc_T1_dict:
                    align_begin_T1_Syl8 = misc_T1_dict.get("Syl8AlignBegin", "_")
                    align_end_T1_Syl8 = misc_T1_dict.get("Syl8AlignEnd", "_")
                    if align_end_T1_Syl8 != '_':
                        duree_syl8 = int(align_end_T1_Syl8) - int(align_begin_T1_Syl8)
                    else:
                        duree_syl8 = 0
                else:
                    align_begin_T1_Syl8 = '_'
                    align_end_T1_Syl8 = '_'
                    duree_syl8 = 0

                # Create a dictionary to store information for the current occurrence
                occurrence = {
                    "file_name": file_name,
                    "sent_id": sent_id,
                    "id_T1": id_T1,
                    "form_T1": form_T1,
                    "pos_T1": pos_T1,
                    "align_begin_T1_Syl1": align_begin_T1_Syl1,
                    "align_end_T1_Syl1": align_end_T1_Syl1,
                    "align_begin_T1_Syl2": align_begin_T1_Syl2,
                    "align_end_T1_Syl2": align_end_T1_Syl2,
                    "align_begin_T1_Syl3": align_begin_T1_Syl3,
                    "align_end_T1_Syl3": align_end_T1_Syl3,
                    "align_begin_T1_Syl4": align_begin_T1_Syl4,
                    "align_end_T1_Syl4": align_end_T1_Syl4,
                    "align_begin_T1_Syl5": align_begin_T1_Syl5,
                    "align_end_T1_Syl5": align_end_T1_Syl5,
                    "align_begin_T1_Syl6": align_begin_T1_Syl6,
                    "align_end_T1_Syl6": align_end_T1_Syl6,
                    "align_begin_T1_Syl7": align_begin_T1_Syl7,
                    "align_end_T1_Syl7": align_end_T1_Syl7,
                    "align_begin_T1_Syl8": align_begin_T1_Syl8,
                    "align_end_T1_Syl8": align_end_T1_Syl8,
                    "align_begin_sent": align_begin_sent,
                    "align_end_sent": align_end_sent,
                    "duree_syl1": duree_syl1,
                    "duree_syl2": duree_syl2,
                    "duree_syl3": duree_syl3,
                    "duree_syl4": duree_syl4,
                    "duree_syl5": duree_syl5,
                    "duree_syl6": duree_syl6,
                    "duree_syl7": duree_syl7,
                    "duree_syl8": duree_syl8,
                }

                occurrences.append(occurrence)

            index += 1

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
        file.write("File\tSent_ID\tID_T1\tT1_Form\tT1_POS\tT1_Syl1AlignBegin\tT1_Syl1AlignEnd\tT1_Syl2AlignBegin\t"
                   "T1_Syl2AlignEnd\tT1_Syl3AlignBegin\tT1_Syl3AlignEnd\tT1_Syl4AlignBegin\tT1_Syl4AlignEnd\tT1_Syl5AlignBegin\tT1_Syl5AlignEnd\t"
                   "T1_Syl6AlignBegin\tT1_Syl6AlignEnd\tT1_Syl7AlignBegin\tT1_Syl7AlignEnd\tT1_Syl8AlignBegin\tT1_Syl8AlignEnd\t"
                   "DureeSyl1\tDureeSyl2\tDureeSyl3\tDureeSyl4\tDureeSyl5\tDureeSyl6\tDureeSyl7\tDureeSyl8\t"
                   "Sent_AlignBegin\tSent_AlignEnd\n")

        # Write the occurrences to the TSV file
        for occurrence in occurrences:
            file.write(
                f"{occurrence['file_name']}\t{occurrence['sent_id']}\t{occurrence['id_T1']}\t"
                f"{occurrence['form_T1']}\t"
                f"{occurrence['pos_T1']}\t"
                f"{occurrence['align_begin_T1_Syl1']}\t{occurrence['align_end_T1_Syl1']}\t"
                f"{occurrence['align_begin_T1_Syl2']}\t{occurrence['align_end_T1_Syl2']}\t"
                f"{occurrence['align_begin_T1_Syl3']}\t{occurrence['align_end_T1_Syl3']}\t"
                f"{occurrence['align_begin_T1_Syl4']}\t{occurrence['align_end_T1_Syl4']}\t"
                f"{occurrence['align_begin_T1_Syl5']}\t{occurrence['align_end_T1_Syl5']}\t"
                f"{occurrence['align_begin_T1_Syl6']}\t{occurrence['align_end_T1_Syl6']}\t"
                f"{occurrence['align_begin_T1_Syl7']}\t{occurrence['align_end_T1_Syl7']}\t"
                f"{occurrence['align_begin_T1_Syl8']}\t{occurrence['align_end_T1_Syl8']}\t"
                f"{occurrence['duree_syl1']}\t{occurrence['duree_syl2']}\t{occurrence['duree_syl3']}\t{occurrence['duree_syl4']}\t"
                f"{occurrence['duree_syl5']}\t{occurrence['duree_syl6']}\t{occurrence['duree_syl7']}\t{occurrence['duree_syl8']}\t"
                f"{occurrence['align_begin_sent']}\t{occurrence['align_end_sent']}\n"
                )


# Path to the directory containing the files
directory_path = "../SUD_Naija-NSC-master/"
# Path to the output TSV file
output_tsv_obj = "../TSV/align_begin_align_end_syl.tsv"

# Extract all occurrences from the files in the directory
occurrences_obj = extract_all_occurrences_obj(directory_path)
# Write the occurrences to the TSV file
write_occurrences_to_tsv(occurrences_obj, output_tsv_obj)
