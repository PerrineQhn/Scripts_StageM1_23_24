from conll3 import *
import os
import re

def convert_misc_to_dict(misc):
    """
    Converts miscellaneous information from a string to a dictionary.
    
    :param misc: A string containing miscellaneous data in key=value format, separated by '|'.
    :return: A dictionary with key-value pairs extracted from the misc string.
    """
    result_dict = {}
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

def clean_text(text):
    if text.startswith('#'):
        # Supprime uniquement les '#' qui ne sont pas au début
        return '#' + text[1:].replace('#', '')
    return text

def write_trees_to_file(trees, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for tree in trees:
            tree_str = str(tree)

            # Extract the sentence ID (Sent_ID) and sentence text from the tree
            global_column = re.search(r'# global.columns = (.+)', tree_str)
            sent_id_match = re.search(r'# sent_id = (.+)', tree_str)
            sound_url = re.search(r'# sound_url = (.+)', tree_str)
            speaker_id = re.search(r'# speaker_id = (.+)', tree_str)
            speaker_naija_competency = re.search(r'# speaker_naija_competency = (.+)', tree_str)
            speaker_primary_other_language = re.search(r'# speaker_primary_other_language = (.+)', tree_str)
            speaker_residence = re.search(r'# speaker_residence = (.+)', tree_str)
            speaker_sex = re.search(r'# speaker_sex = (.+)', tree_str)
            
            text = re.search(r'# text = (.+)', tree_str)
            text_en = re.search(r'# text_en = (.+)', tree_str)
            text_ortho = re.search(r'# text_ortho = (.+)', tree_str)

            print(sent_id_match.group(0))
            file.write(f"{global_column.group(0)}\n") if global_column else None
            file.write(f"{sent_id_match.group(0)}\n")
            file.write(f"{sound_url.group(0)}\n")
            file.write(f"{speaker_id.group(0)}\n")
            file.write(f"{speaker_naija_competency.group(0)}\n")
            file.write(f"{speaker_primary_other_language.group(0)}\n")
            file.write(f"{speaker_residence.group(0)}\n")
            file.write(f"{speaker_sex.group(0)}\n")
            
            file.write(clean_text(text.group(0)) + '\n')
            file.write(f"{text_en.group(0)}\n")
            file.write(f"{text_ortho.group(0)}\n") if text_ortho else None

            # Écrire les données de l'arbre
            for word_pos in tree:
                word = tree[word_pos]
                # print(word)

                feats_keys = [k for k in word if k not in ['id', 't', 'lemma', 'tag', 'xpos', 'gov', 'egov', 'misc']]
                feats = '|'.join(f"{key}={word[key]}" for key in feats_keys)

                head_keys = list(word['gov'].keys())
                deprel_values = list(word['gov'].values())

                head = head_keys[0] if head_keys else '_'
                deprel = deprel_values[0] if deprel_values else '_'

                line = f"{word['id']}\t{word['t']}\t{word['lemma']}\t{word['tag']}\t{word['xpos']}\t{feats}\t{head}\t{deprel}\t_\t{word['misc']}\n"
                file.write(line)
            
            file.write("\n")  # Ajoute une ligne vide entre les arbres

def delete_silence(file_path):
    trees = conllFile2trees(file_path)
    # print(str(trees))
    for tree in trees:
        original_length = len(tree.words)
        words_to_delete = []
        for word_id, word in enumerate(tree.words, 1):
            token = tree[word_id].get("t")
            # print(word_id, word)
            if token == "#":
                words_to_delete.append(word_id)
        
        # print("word id to delete", words_to_delete)
        # print(tree)

        if words_to_delete:  # Continue only if there are tokens to delete
            for offset, word_id in enumerate(words_to_delete):
                del tree[word_id]  # Adjust index for previous deletions

            # print("tree after deletion", tree)
            # Update IDs of remaining tokens
            new_word_id = 1
            # print(original_length)
            for word_id in range(1, original_length+1):
                if word_id in tree:
                    tree[word_id]["id"] = new_word_id
                    new_word_id += 1

    # print(trees)
    write_trees_to_file(trees, file_path)



dossier_conllu = './SUD_Naija-NSC-master-gold-non-gold-TALN/'

# Loop through all files in the folder
for fichier in os.listdir(dossier_conllu):
    if fichier.endswith('MG.conllu'):
        chemin_conllu = os.path.join(dossier_conllu, fichier)
        print(chemin_conllu)
        delete_silence(chemin_conllu)
# delete_silence('./SUD_Naija-NSC-master-gold-non-gold-TALN/ABJ_GWA_03_Cost-Of-Living-In-Abuja_MG.conllu')
