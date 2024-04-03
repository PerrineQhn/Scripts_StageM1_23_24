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
    special_cases = [
        "o'clock", 
        "billionaire's", 
        "dat's", 
        "Africa's", 
        "O'neill", 
        "a'ah", 
        "it's", 
        "John's", 
        "God's", 
        "voter's", 
        "admin's", 
        "Zimbabwe's", 
        "people's", 
        "guy's",
    ]
    hyphenated_special_cases = [
        "ex-soldier", 
        "self-sufficient", 
        "twenty-fourth", 
        "ninety-six", 
        "D-Morris", 
        "Port-Harcourt"
    ]
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
            # print(words[i], tmp_interval[2])

            pos = tree[i + 1].get("tag")
            if "'" in words[i] and words[i] not in special_cases:
                if words[i].upper() == "'M":
                    # print("words with an 'M : ", words[i], " :: ", tmp_interval[2])
                    if "'M" in words[i].upper() and tmp_interval[2].upper() == "M":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
                    i += 1

                elif words[i].upper() == "'S":
                    if "'S" in words[i].upper() and tmp_interval[2].upper() == "S":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
                    i += 1

                elif words[i].upper() == "'LL":
                    if "'LL" in words[i].upper() and tmp_interval[2].upper() == "LL":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
                    i += 1

                elif words[i].upper() == "'RE":
                    if "'RE" in words[i].upper() and tmp_interval[2].upper() == "RE":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
                    i += 1
                
                elif words[i].upper() == "CHAMPIONS'":
                    if "CHAMPIONS'" in words[i].upper() and tmp_interval[2].upper() == "CHAMPIONS":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]
                    i += 1

                elif words[i].upper() == "N'T":
                    if "N'" in words[i].upper() and tmp_interval[2].upper() == "N":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "'T" in words[i].upper() and tmp_interval[2].upper() == "T":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "HM'M":
                    if "HM'" in words[i].upper() and tmp_interval[2].upper() == "HM":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "M" in words[i].upper() and tmp_interval[2].upper() == "M":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MOMO'S":
                    if "MOMO'" in words[i].upper() and tmp_interval[2].upper() == "MOMO":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "S" in words[i].upper() and tmp_interval[2].upper() == "S":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    c = words[i].split("'")
                    print("words with an ' : ", words[i], " :: ", c)
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                            index_intervals.append(tmp_interval)
                            token_pos += 1
                        i += 1
                        token_pos += 1


            elif "-" in words[i] and words[i] not in hyphenated_special_cases:
                if words[i].upper() == "CO-COMMANDER":
                    if "CO-" in words[i].upper() and tmp_interval[2].upper() == "CO-":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "COMMANDER" in words[i].upper() and tmp_interval[2].upper() == "COMMANDER":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MA-FIREWOOD":
                    if "MA-" in words[i].upper() and tmp_interval[2].upper() == "MA":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "FIREWOOD" in words[i].upper() and tmp_interval[2].upper() == "FIREWOOD":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "MA-AKARA":
                    if "MA-" in words[i].upper() and tmp_interval[2].upper() == "MA":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "AKARA" in words[i].upper() and tmp_interval[2].upper() == "AKARA":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "UN-AFRICAN":
                    if "UN-" in words[i].upper() and tmp_interval[2].upper() == "UN":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "AFRICAN" in words[i].upper() and tmp_interval[2].upper() == "AFRICAN":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "E-SERVICES":
                    if "E-" in words[i].upper() and tmp_interval[2].upper() == "E":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "SERVICES" in words[i].upper() and tmp_interval[2].upper() == "SERVICES":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "PRE-DEGREE":
                    if "PRE-" in words[i].upper() and tmp_interval[2].upper() == "PRE":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "DEGREE" in words[i].upper() and tmp_interval[2].upper() == "DEGREE":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == "PRO-EUROPEAN":
                    if "PRO-" in words[i].upper() and tmp_interval[2].upper() == "PRO":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "EUROPEAN" in words[i].upper() and tmp_interval[2].upper() == "EUROPEAN":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1

                else :
                    c = words[i].split("-")
                    print("words with a - : ", words[i], " :: ", c)
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                            index_intervals.append(tmp_interval)
                            token_pos += 1
                        i += 1
                        token_pos += 1

            elif "." in words[i] and words[i] != 'p.m.':
                if words[i].upper() == 'O.D.S.':
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "D.S" in words[i].upper() and tmp_interval[2].upper() == "D.S":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1
                    
                elif words[i].upper() == 'A.M.':
                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "M." in words[i].upper() and tmp_interval[2].upper() == "M.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                    i += 1

                else:
                    words[i] = words[i].replace(".", " point ")
                    c = words[i].split()
                    for x in c:
                        if x == tmp_interval[2]:
                            tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                            index_intervals.append(tmp_interval)
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
                print(f"Error with word '{words[i]}' at position {i}, interval '{tmp_interval[2]}'")


    #print(index_intervals)
    t = tgio.IntervalTier("index", index_intervals)
    textgrid.addTier(t)
    textgrid.save(output_textgrid_path)


def create_textgrid_nongold(file_path, input_textgrid_path, output_textgrid_path):
    print(file_path)
    textgrid = tgio.openTextgrid(input_textgrid_path)
    tier = textgrid.tierDict['TokensAlign']
    tokens_align_intervals = tier.entryList
    index_intervals = []
    token_pos = 0
    special_cases = [
        "o'clock", 
        "billionaire's", 
        "dat's", 
        "Africa's", 
        "O'neill", 
        "a'ah", 
        "it's", 
        "John's", 
        "God's", 
        "voter's", 
        "admin's", 
        "Zimbabwe's", 
        "people's", 
        "guy's",
    ]
    hyphenated_special_cases = [
        "ex-soldier", 
        "self-sufficient", 
        "twenty-fourth", 
        "ninety-six", 
        "D-Morris", 
        "Port-Harcourt",
        "port-harcourt",
        "d-morris"
    ]
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
            

            symbols_to_remove = ("]", "[", ",", ".", "<", "|c", ")", "//", "'", "||")
            if pos != "PUNCT" and words[i].endswith(symbols_to_remove) and words[i] != "p.m." and words[i] != "a.m." and words[i] != "o.a." and words[i] != "o.d.s." and words[i] != "s.":
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
            
            elif "-" in words[i] and words[i] != "vice-president" and words[i] not in hyphenated_special_cases and "'" not in tokens_align_intervals[token_pos][2]:
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
                if words[i].upper() == 'A.M.':
                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "M." in words[i].upper() and tmp_interval[2].upper() == "M.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == 'O.A.':
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "A." in words[i].upper() and tmp_interval[2].upper() == "A.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        # print(tmp_interval)
                        token_pos += 1
                    i += 1

                elif words[i].upper() == 'O.D.S.':
                    if "O." in words[i].upper() and tmp_interval[2].upper() == "O.":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                        tmp_interval = [tokens_align_intervals[token_pos][0], tokens_align_intervals[token_pos][1], tokens_align_intervals[token_pos][2]]

                    if "D.S" in words[i].upper() and tmp_interval[2].upper() == "D.S":
                        tmp_interval[2] = '{}.{}'.format(tree_pos + 1, i + 1)
                        index_intervals.append(tmp_interval)
                        token_pos += 1
                    i += 1
                
                else:
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

# file_path = 'WAZA_09_Tv-News_MG.conllu'
# input_textgrid_path = 'WAZA_09_Tv-News_MG-palign.TextGrid'
# output_textgrid_path = 'WAZA_09_Tv-News_MG-id.TextGrid'
# create_textgrid(file_path, input_textgrid_path, output_textgrid_path)

if __name__ == "__main__":
    conllu_folder = './SUD_Naija-NSC-master'
    # textgrid_base_folder = './TEXTGRID_WAV/'
    textgrid_base_folder = './TEXTGRID_WAV_gold_non_gold_TALN/'
    # conllu_folder = './SUD_Naija-NSC-master/non_gold/'
    # textgrid_base_folder = './TEXTGRID_WAV_nongold/'

    for files in os.listdir(conllu_folder):
        if files.endswith('MG.conllu') : 
        # if files.endswith('M.conllu'):
            file_path = os.path.join(conllu_folder, files)
            # print(file_path)
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
            # if files == "WAZP_04_Ponzi-Scheme_MG.conllu":
            # create_textgrid(file_path, input_textgrid_path, output_textgrid_path)
            # print('###################################################################\n')

            # if files == "WAZP_04_Ponzi-Scheme_MG.conllu":
            create_textgrid_nongold(file_path, input_textgrid_path, output_textgrid_path)