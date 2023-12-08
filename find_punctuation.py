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

    with open("punctuation_+_30ms_with_#.tsv", "a") as f:
        # Add header only if the file is empty
        if os.stat("punctuation_+_30ms_with_#.tsv").st_size == 0:
            f.write("File_Name\tWord\tAlign_Begin\tAlign_End\tDifference\tToken_Before\tTB_Align_End\tToken_after\tTA_Align_Begin\tSent\n")
        
        for indx, tree in enumerate(trees):
            tree_str = str(tree)
            sent = re.search(r'# text = (.+)', tree_str)
            if sent is not None:
                sent_text = sent.group(1)
            else:   
                continue
            #print(sent_text)
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
                                token_before, tb_align_end = "", ""
                                token_after, ta_align_begin = "", ""
                               # Trouver le token avant la ponctuation
                                for bp in range(word_pos - 1, 0, -1):
                                    #print(f"Checking position {bp}: {tree[bp].get('t')} with tag {tree[bp].get('tag')}")
                                    if tree[bp].get("tag") != "PUNCT":
                                    #if tree[bp].get("tag") != "PUNCT" or tree[bp].get("tag") == "PUNCT" and tree[bp].get("t") == "#":
                                        token_before = tree[bp].get("t")
                                        tb_misc = tree[bp].get("misc", "")
                                        tb_misc_dict = convert_misc_to_dict(tb_misc)
                                        tb_align_end = tb_misc_dict.get("AlignEnd")
                                        break

                                # Trouver le token après la ponctuation
                                for ap in range(word_pos + 1, len(tree) + 1):
                                    if tree[ap].get("tag") != "PUNCT":
                                    #if tree[ap].get("tag") != "PUNCT" or tree[ap].get("tag") == "PUNCT" and tree[ap].get("t") == "#":
                                        token_after = tree[ap].get("t")
                                        ta_misc = tree[ap].get("misc", "")
                                        ta_misc_dict = convert_misc_to_dict(ta_misc)
                                        ta_align_begin = ta_misc_dict.get("AlignBegin")
                                        break

                                # Écrire dans le fichier si tous les éléments nécessaires sont présents
                                if all([token_before, tb_align_end, token_after, ta_align_begin]):
                                    f.write(f"{file_name}\t{word}\t{align_begin}\t{align_end}\t{difference}\t{token_before}\t{tb_align_end}\t{token_after}\t{ta_align_begin}\t{sent_text}\n")

                            


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
