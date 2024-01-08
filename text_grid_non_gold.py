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
    for tree_pos, tree in enumerate(trees):
        line = str(tree)
        # print(line)
        text_match = re.search(r'# text = (.+)', line)
        text_list = text_match.group(1).split()
        # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        # print(text_list)
        misc_list = []
        # print(line)
        for l in line.split('\n'):
            if re.search(r"\d: ", l):
                idx = int(l.split(':')[0]) #get index
                misc_list.append({idx: convert_misc_to_dict(tree[idx].get("misc", "#"))})
        # print(misc_list)
        # print("--------------------------------------------------------------------------------")
        words = tree.words
        # print(words)
        # print("=================================================================================")
        sentence = []
        i_text = 0
        current_text = ""
        current_xmin = 0
        current_xmax = 0
        for i in range(len(words)):
            if i==0 and tree_pos == 0:
                align_end = misc_list[i_text].get(i_text + 1).get("AlignBegin")
                current_xmax = int(align_end) / 1000
                if current_xmax != 0.0:
                    intervals.append(tgio.Interval(0, current_xmax, "#"))
            if words[i] != "#":
                sentence.append(words[i])
            if words[i] == "#" or i == len(words) - 1:
                if sentence:
                    # print('sentence: ', sentence)
                    sentence_without_punc = [sentence[j] for j in range(len(sentence)) if tree[(i_text + j+1)].get("tag") != "PUNCT"]
                    # put the words of the sentence into a string
                    current_text = " ".join(sentence_without_punc)
                    start = i_text
                    while i_text < len(text_list):
                        #print("text_list[i_text]:", text_list[i_text], "sentence[-1]:", sentence[-1], "i_text - start +1:", i_text - start +1, "len(sentence):", len(sentence), 'start:', start, 'i_text:',i_text, 'text_list[i_text]:', text_list[i_text] )
                        if len(sentence) == 1 and text_list[i_text] != "#":
                            align_begin = misc_list[i_text].get(i_text + 1).get("AlignBegin")
                            current_xmin = int(align_begin) / 1000
                            align_end = misc_list[i_text].get(i_text + 1).get("AlignEnd")
                            current_xmax = int(align_end) / 1000
                            if current_xmin != current_xmax:
                                intervals.append(tgio.Interval(current_xmin, current_xmax, current_text))
                            i_text += 1
                            break
                        elif text_list[i_text] == sentence[0] and start == i_text:
                            pos = tree[i_text+1].get("tag")
                            temp_i_text = i_text
                            while pos == "PUNCT" and words[i_text] != "#":
                                temp_i_text += 1
                                pos = tree[temp_i_text+1].get("tag")
                            align_begin = misc_list[temp_i_text].get(temp_i_text+1).get("AlignBegin")
                            current_xmin = int(align_begin) / 1000
                        elif text_list[i_text] == sentence[-1] and i_text - start +1 == len(sentence):
                            # print(sentence)
                            temp_i_text = i_text
                            pos = tree[temp_i_text+1].get("tag")
                            while pos == "PUNCT" and words[i_text] != "#":
                                temp_i_text -= 1
                                pos = tree[temp_i_text+1].get("tag")
                            align_end = misc_list[temp_i_text].get(temp_i_text+1).get("AlignEnd")
                            current_xmax = int(align_end) / 1000
                            if current_xmin != current_xmax:
                                intervals.append(tgio.Interval(current_xmin, current_xmax, current_text))
                            i_text += 1
                            break
                        i_text += 1

    tier = tgio.IntervalTier("trans", intervals)
    textgrid.addTier(tier)
    textgrid.save(output_textgrid_path)



dossier_conllu = './SUD_Naija-NSC-master/non_gold/'

# Loop through all files in the directory
for fichier in os.listdir(dossier_conllu):
    if fichier.endswith('MG.conllu') or fichier.endswith('M.conllu'):
        chemin_conllu = os.path.join(dossier_conllu, fichier)
        # Generate the output TextGrid file name
        nom_fichier_sans_extension = os.path.splitext(fichier)[0]
        if nom_fichier_sans_extension.startswith('ABJ'):
            folder = '_'.join(nom_fichier_sans_extension.split('_')[:3])
        else:
            folder = '_'.join(nom_fichier_sans_extension.split('_')[:2])

        print(nom_fichier_sans_extension)
        chemin_textgrid = os.path.join('', f'./TEXTGRID_WAV_nongold/{folder}/{nom_fichier_sans_extension}.TextGrid')

        # Call the function for each CoNLL-U file
        if nom_fichier_sans_extension != 'LAG_05_Government-Dey-Try_M':
            create_textgrid(chemin_conllu, chemin_textgrid)
            

print("Done !")