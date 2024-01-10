from praatio import tgio
from conll3 import *
import os


def create_textgrid(file_path, input_textgrid_path, output_textgrid_path):
    textgrid = tgio.openTextgrid(input_textgrid_path)
    tier = textgrid.tierDict['TokensAlign']
    tokens_align_intervals = tier.entryList
    index_intervals = []
    token_pos = 0
    trees = conllFile2trees(file_path)
    for tree_pos, tree in enumerate(trees):
        #print(tree_pos)
        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
        if tmp_interval[2] == '#':
            index_intervals.append(tmp_interval)
            token_pos += 1
        words = tree.words
        i = 0
        while i < len(words) and token_pos < len(tokens_align_intervals):
            tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
            #print(words[i], tmp_interval[2])
            pos = tree[i + 1].get("tag")
            if "'" in words[i]:
                c = words[i].split("'")
                for x in c:
                    if x == tmp_interval[2]:
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        token_pos += 1
                    i += 1
                    token_pos += 1
                    index_intervals.append(tmp_interval)
            elif words[i].strip('~').upper() == tmp_interval[2].upper():
                if words[i] != '#':
                    tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                token_pos += 1
                i += 1
                index_intervals.append(tmp_interval)

            elif pos == "PUNCT":
                i += 1
                continue
            else:
                i += 1
                print("error")

    #print(index_intervals)
    t = tgio.IntervalTier("index", index_intervals)
    textgrid.addTier(t)
    textgrid.save(output_textgrid_path)


def create_textgrid_nongold(file_path, input_textgrid_path, output_textgrid_path):
    textgrid = tgio.openTextgrid(input_textgrid_path)
    tier = textgrid.tierDict['TokensAlign']
    tokens_align_intervals = tier.entryList
    index_intervals = []
    token_pos = 0
    trees = conllFile2trees(file_path)
    for tree_pos, tree in enumerate(trees):        
        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
        if tmp_interval[2] == '#':
            index_intervals.append(tmp_interval)
            token_pos += 1
        words = tree.words
        words = [word.lower() for word in words]
        i = 0
        while i < len(words) and token_pos < len(tokens_align_intervals) :
            # print(len(words))
            # print(token_pos, tokens_align_intervals[token_pos])
            tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
            pos = tree[i + 1].get("tag")

            if "{" in tmp_interval[2] and "}" in tmp_interval[2] and "|c" in tmp_interval[2]:
                tmp_interval[2] = tmp_interval[2].replace("{", "").replace("}", "").replace("|c", "")

            elif "{" in tmp_interval[2] and "}" in tmp_interval[2] and "|" in tmp_interval[2]:
                tmp_interval[2] = tmp_interval[2].replace("{", "").replace("}", "").replace("|", "")
            

            symbols_to_remove = ("]", "[", ".", ",", "<", "|c", ")", "//", "'", "||")
            if pos != "PUNCT" and words[i].endswith(symbols_to_remove):
                for symbol in symbols_to_remove:
                    if words[i].endswith(symbol):
                        words[i] = words[i][:-len(symbol)]
                        break


            elif words[i].startswith("'") : 
                words[i] = words[i].replace("'", "")


            if pos == "PUNCT":
                i += 1
                continue

            elif "'" in words[i] and "'" not in tokens_align_intervals[token_pos][2]:
                c = words[i].split("'")
                for x in c:
                    tmp_value = tokens_align_intervals[token_pos][2]
                    if x == tmp_interval[2]:
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1
            
            elif "-" in words[i] and words[i] != "vice-president" and "'" not in tokens_align_intervals[token_pos][2]:
                c = words[i].split("-")
                for x in c:
                    # print(x, tokens_align_intervals[token_pos][2])
                    tmp_value = tokens_align_intervals[token_pos][2]
                    if x == tmp_value:
                        tmp_interval = [tokens_align_intervals[token_pos][0], 
                        tokens_align_intervals[token_pos][1], 
                        '{}.{}'.format(tree_pos + 1, i + 1)]
                        # print(tmp_interval, x, tokens_align_intervals[token_pos][2])
                        index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1
            
            elif "." in words[i] and "'" not in tokens_align_intervals[token_pos][2]:
                words[i] = words[i].replace(".", " point ")
                c = words[i].split()
                for x in c:
                    # print(x, tokens_align_intervals[token_pos][2])
                    tmp_value = tokens_align_intervals[token_pos][2]
                    if x == tmp_value:
                        tmp_interval = [tokens_align_intervals[token_pos][0], 
                        tokens_align_intervals[token_pos][1], 
                        '{}.{}'.format(tree_pos + 1, i + 1)]
                        # print(tmp_interval, x, tokens_align_intervals[token_pos][2])
                        index_intervals.append(tmp_interval)
                    token_pos += 1
                i += 1

            elif words[i].strip('~').upper() == tmp_interval[2].upper():
                if words[i] != '#':
                    tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                token_pos += 1
                i += 1
                index_intervals.append(tmp_interval)

            else:
                print(words[i])
                i += 1
                print("error \n")


    #print(index_intervals)
    t = tgio.IntervalTier("index", index_intervals)
    textgrid.addTier(t)
    textgrid.save(output_textgrid_path)

if __name__ == "__main__":
    # conllu_folder = './SUD_Naija-NSC-master'
    # textgrid_base_folder = './TEXTGRID_WAV/'
    conllu_folder = './SUD_Naija-NSC-master/non_gold/'
    textgrid_base_folder = './TEXTGRID_WAV_nongold/'

    for files in os.listdir(conllu_folder):
        # if files.endswith('MG.conllu') : 
        if files.endswith('M.conllu'):
            file_path = os.path.join(conllu_folder, files)
            #print(file_path)
            # Adjust the folder path based on the file name
            if files.startswith('ABJ'):
                folder_name = '_'.join(files.split('_')[:3])
            else:
                folder_name = '_'.join(files.split('_')[:2])

            # Construct the specific TextGrid folder path
            textgrid_folder = os.path.join(textgrid_base_folder, folder_name)

            # Construct the paths for input and output TextGrid files
            input_textgrid_path = os.path.join(textgrid_folder, files.replace('.conllu', '-palign.TextGrid'))
            # print(input_textgrid_path)
            output_textgrid_path = os.path.join(textgrid_folder, files.replace('.conllu', '-id.TextGrid'))

            # Create TextGrid
            # create_textgrid(file_path, input_textgrid_path, output_textgrid_path)
            if files != "LAG_24_Focus-On-Your-Life_M.conllu":
                create_textgrid_nongold(file_path, input_textgrid_path, output_textgrid_path)