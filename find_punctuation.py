import re
import os
from conll3 import *

def convert_misc_to_dict(misc):
    result_dict = {}
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

def punctuation(file_path):
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    with open("punctuation_+_30ms.tsv", "a") as f:
        # Add header only if the file is empty
        if os.stat("punctuation_+_30ms.tsv").st_size == 0:
            f.write("File_Name\tWord\tAlign_Begin\tAlign_End\tDifference\tSent\n")
        
        for tree in trees:
            tree_str = str(tree)
            sent = re.search(r'# text = (.+)', tree_str)
            sent_text = sent.group(1)
            words = tree.words
            for word_pos, word in enumerate(words, 1):
                pos = tree[word_pos].get("tag")
                if pos == "PUNCT" and word != "#":
                    misc = tree[word_pos].get("misc", "")
                    misc_dict = convert_misc_to_dict(misc)
                    align_begin = misc_dict.get("AlignBegin")
                    align_end = misc_dict.get("AlignEnd")
                    if align_begin is not None and align_end is not None:
                        difference = int(align_end) - int(align_begin)
                        if difference > 30:
                            f.write(f"{file_name}\t{word}\t{align_begin}\t{align_end}\t{difference}\t{sent_text}\n")

def silence(file_path):
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    with open("silence.tsv", "a") as f:
        # Add header only if the file is empty
        if os.stat("silence.tsv").st_size == 0:
            f.write("File_Name\tWord\tAlign_Begin\tAlign_End\tSent\n")

        for tree in trees:
            tree_str = str(tree)
            sent = re.search(r'# text = (.+)', tree_str)
            sent_text = sent.group(1)
            words = tree.words
            for word_pos, word in enumerate(words, 1):
                pos = tree[word_pos].get("tag")
                if pos == "PUNCT" and word == "#":
                    misc = tree[word_pos].get("misc", "")
                    misc_dict = convert_misc_to_dict(misc)
                    align_begin = misc_dict.get("AlignBegin")
                    align_end = misc_dict.get("AlignEnd")
                    if align_begin is not None and align_end is not None and int(align_begin) == int(align_end):
                        f.write(f"{file_name}\t{word}\t{align_begin}\t{align_end}\t{sent_text}\n")

dossier_conllu = '../SUD_Naija-NSC-master'

# Loop through all files in the folder
for fichier in os.listdir(dossier_conllu):
    if fichier.endswith('MG.conllu') or fichier.endswith('M.conllu'):
        chemin_conllu = os.path.join(dossier_conllu, fichier)
        # Call the function for each CoNLL-U file
        punctuation(chemin_conllu)
        #silence(chemin_conllu)

print("Terminé!")
