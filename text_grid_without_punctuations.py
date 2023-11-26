from praatio import tgio
import re
from conll3 import *

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


def create_textgrid(file_path, output_textgrid_path):
    """
    Creates a TextGrid file from a CoNLL-U formatted file.
    
    :param file_path: Path to the CoNLL-U file.
    :param output_textgrid_path: Path where the output TextGrid file will be saved.
    """
    textgrid = tgio.Textgrid()
    entryList = []
    trees = conllFile2trees(file_path)
    last_end_time = 0
    #post_start_time = 0
    intervals = []

    # Process each tree (sentence) in the CoNLL-U file
    for tree_pos, tree in enumerate(trees):
        line = str(tree)
        misc_list = []
        # Extract miscellaneous information for each word
        for l in line.split('\n'):
            if re.search(r"\d: ", l):
                idx = int(l.split(':')[0]) #get index
                misc_list.append({idx: convert_misc_to_dict(tree[idx].get("misc", "#"))})
        words = tree.words
        sentence = []
        i_text = 0
        current_xmin = 0
        current_xmax = 0
        # Process each word in the sentence
        for i in range(len(words)):
            if i == 0 and tree_pos == 0:
                align_end = misc_list[i_text].get(i_text + 1).get("AlignBegin")
                current_xmax = int(align_end) / 1000
                if current_xmax != 0.0:
                    intervals.append(tgio.Interval(0, current_xmax, "#"))
            if words[i] != "#":
                sentence.append(words[i])
            if words[i] == "#" or i == len(words) - 1:
                if sentence:
                    # Remove all punctuations except #
                    print("sentence:", sentence)
                    sentence_without_punc = [sentence[j] for j in range(len(sentence)) if tree[(i_text + j+1)].get("tag") != "PUNCT"]
                    current_text = " ".join(sentence_without_punc)
                    print("sentence_without_punc: ", current_text)
                    start = i_text
                    while i_text < len(words):
                        if len(sentence) == 1 and words[i_text] != "#":
                            align_begin = misc_list[i_text].get(i_text + 1).get("AlignBegin")
                            current_xmin = int(align_begin) / 1000
                            align_end = misc_list[i_text].get(i_text + 1).get("AlignEnd")
                            current_xmax = int(align_end) / 1000
                            if current_xmin != current_xmax:
                                intervals.append(tgio.Interval(current_xmin, current_xmax, current_text))
                            i_text += 1
                            break
                        elif words[i_text] == sentence[0] and start == i_text:
                            pos = tree[i_text+1].get("tag")
                            temp_i_text = i_text
                            while pos == "PUNCT" and words[i_text] != "#":
                                temp_i_text += 1
                                pos = tree[temp_i_text+1].get("tag")
                            align_begin = misc_list[temp_i_text].get(temp_i_text+1).get("AlignBegin")
                            current_xmin = int(align_begin) / 1000
                        elif words[i_text] == sentence[-1] and i_text - start +1 == len(sentence):
                            temp_i_text = i_text
                            pos = tree[temp_i_text+1].get("tag")
                            while pos == "PUNCT" and words[i_text] != "#":
                                temp_i_text -= 1
                                pos = tree[temp_i_text+1].get("tag")
                            align_end = misc_list[temp_i_text].get(temp_i_text+1).get("AlignEnd")
                            current_xmax = int(align_end) / 1000
                            last_element = [intervals[-1].start, intervals[-1].end, intervals[-1].label]
                            if last_element[1] != current_xmin and last_element[2] =="#":
                                last_element[1] = current_xmin
                                intervals = intervals[:-1]
                                if last_element[0] != last_element[1]:
                                    intervals.append(tgio.Interval(last_element[0], last_element[1], last_element[2]))
                            if current_xmin != current_xmax:
                                intervals.append(tgio.Interval(current_xmin, current_xmax, current_text))
                            i_text += 1
                            break
                        i_text += 1
                sentence = []
                if words[i] == "#":
                    while i_text < len(words):
                        if words[i_text] == "#":
                            current_text = "#"
                            align_begin = misc_list[i_text].get(i_text + 1).get("AlignBegin")
                            current_xmin = int(align_begin) / 1000
                            align_end = misc_list[i_text].get(i_text + 1).get("AlignEnd")
                            current_xmax = int(align_end) / 1000
                            last_element = [intervals[-1].start, intervals[-1].end, intervals[-1].label]
                            if(last_element[1] != current_xmin):
                                current_xmin = last_element[1]
                            if current_xmin != current_xmax:
                                intervals.append(tgio.Interval(current_xmin, current_xmax, current_text))
                            i_text += 1
                            break
                        i_text += 1

    tier = tgio.IntervalTier("trans", intervals)
    textgrid.addTier(tier)
    textgrid.save(output_textgrid_path)

#create_textgrid('../SUD_Naija-NSC-master/non_gold/ABJ_INF_02_Cooking-Recipes_M.conllu', '../test/ABJ_INF_02.TextGrid')

dossier_conllu = '../SUD_Naija-NSC-master/'


# Loop through all files in the directory
for fichier in os.listdir(dossier_conllu):
    if fichier.endswith('MG.conllu') or fichier.endswith('M.conllu'):
        chemin_conllu = os.path.join(dossier_conllu, fichier)
        # Generate the output TextGrid file name
        nom_fichier_sans_extension = os.path.splitext(fichier)[0]
        #print(nom_fichier_sans_extension)
        chemin_textgrid = os.path.join('', f'../TEXTGRID/{nom_fichier_sans_extension}.TextGrid')
        # Call the function for each CoNLL-U file
        if nom_fichier_sans_extension != 'IBA_03_Womanisers_MG':
            create_textgrid(chemin_conllu, chemin_textgrid)

print("Terminé !")