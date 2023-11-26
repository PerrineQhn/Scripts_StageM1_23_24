from praatio import tgio
import re
from conll3 import *

def convert_misc_to_dict(misc):
    # Dictionnaire pour stocker les informations supplémentaires
    result_dict = {}
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

def create_textgrid(file_path, output_textgrid_path):
    textgrid = tgio.Textgrid()

    entryList = []  # Initialize entryList as an empty list

    trees = conllFile2trees(file_path)
    intervals = []
    intervals_token = []

    for tree_pos, tree in enumerate(trees):
        line = str(tree)
        #print(line)
        text_match = re.search(r'# text = (.+)', line)

        misc_list = []
        for l in line.split('\n'):
            if re.search(r"\d: ", l):
                idx = int(l.split(':')[0]) #get index
                misc_list.append({idx: convert_misc_to_dict(tree[idx].get("misc", ""))})

        words = tree.words
        for word_pos, word in enumerate(words):
            pos = tree[word_pos+1].get("tag")
            if pos == "PUNCT" and word!="#":
                continue
            if word_pos==0 and tree_pos == 0:
                align_end = misc_list[word_pos].get(word_pos + 1).get("AlignBegin")
                current_xmax = int(align_end) / 1000
                #intervals.append(tgio.Interval(0, current_xmax, "0"))
                intervals_token.append(tgio.Interval(0, current_xmax, "#"))
            iden = tree[word_pos+1].get("id", 0)
            align_begin = misc_list[word_pos].get(word_pos + 1).get("AlignBegin")
            current_xmin = int(align_begin) / 1000
            align_end = misc_list[word_pos].get(word_pos + 1).get("AlignEnd")
            current_xmax = int(align_end) / 1000
            current_id = f"{tree_pos+1}.{iden}"
            current_token = words[word_pos]
            if word != "#":
                intervals.append(tgio.Interval(current_xmin, current_xmax, current_id))
            intervals_token.append(tgio.Interval(current_xmin, current_xmax, current_token))

    token = tgio.IntervalTier("token", intervals_token)
    identifiant = tgio.IntervalTier("id", intervals)
    textgrid.addTier(token)
    textgrid.addTier(identifiant)
    textgrid.save(output_textgrid_path)

create_textgrid('../SUD_Naija-NSC-master/ABJ_GWA_12_Accident_MG.conllu', '../test/token_id/ABJ_GWA_12_Accident_MG-id.TextGrid')
