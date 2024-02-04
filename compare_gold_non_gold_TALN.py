from praatio import tgio
import csv
import os

# Fonction pour obtenir tous les fichiers d'un répertoire
def get_files_from_directory(directory_path, extension):
    return [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith(extension)]


def extract_sentences(conllu_file_path):
    """Extract gold sentences from the .conllu file."""
    gold_sentences = []
    with open(conllu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('# text ='):
                gold_sentence = line.split('=')
                new_gold_sentence = []
                for i in range(1, len(gold_sentence)):
                    gold_sentence_i= gold_sentence[i].split()
                    if i != len(gold_sentence)-1:
                        gold_sentence_i[-1] +='='
                    new_gold_sentence.extend(gold_sentence_i)
                gold_sentences.append(new_gold_sentence)
    return gold_sentences


def extract_token_and_pause_times(textgrid_file_path):
    """Extract the times of tokens and pauses from the TextGrid file."""
    tg = tgio.openTextgrid(textgrid_file_path)
    tier = tg.tierDict['Combined'] 

    tier_combined = []

    for interval in tier.entryList:
        label, xmin, xmax = interval[2], interval[0], interval[1] 

        tier_combined.append((label, xmin, xmax))
    return tier_combined


def insert_pauses_in_non_gold_sentences(non_gold_sentences, tier):
    """Insert pauses into the non-gold sentences based on the TextGrid."""
    adjusted_non_gold_sentences = []
    print(non_gold_sentences)

    punctuation_list = ['>', '<', '//', '?//', '[', ']', '{', '}', '|c', '>+', '||', '&//', '(', ')', '|r', '>=', '//+', '<+',
                        '?//]', '//]', '//=', '!//', '?//=', '!//=', '//)', '|a', '&?//', '!//]', '&//]', '//&', '!//]', '&//]', '//&', '?//)', '!//)']
    i = 0
    sentences_list = [word for s in non_gold_sentences for word in s]
    for punctuation in punctuation_list:
        if punctuation in sentences_list:
            sentences_list = [x.replace('~','') for x in sentences_list if x != punctuation]
    idx_sentences_list = 0
    l = 0
    while l < len(non_gold_sentences):
            sentence = non_gold_sentences[l]
            new_sentence = []
            j = 0
            while j < len(sentence):
                token = sentence[j]
                
                if i >= len(tier):
                    break
                token_label, xmin, xmax = tier[i]
                # print(token_label, sentences_list[idx_sentences_list])
                if token in punctuation_list:
                    new_sentence.append(token)
                    j = j + 1

                elif token_label == "#":
                  if i == 0 and tier[i+1][0] == '#':
                        i += 1
                        continue
                  else:
                    new_sentence.append("#")
                    try_time = 3
                    idx_tier_try = i + 1
                    idx_word_try = idx_sentences_list
                    current_try = 0

                    while current_try < try_time:
                        while idx_word_try<len(sentences_list) and sentences_list[idx_word_try] in punctuation_list:
                            idx_word_try += 1
                        if idx_word_try<len(sentences_list) and idx_tier_try < len(tier) and tier[idx_tier_try][0].upper() != sentences_list[idx_word_try].upper() and tier[idx_tier_try][0].upper() != '#':
                            break
                        if tier[idx_tier_try][0].upper() == '#':
                            idx_tier_try += 1
                        if idx_tier_try < len(tier) - 1 and idx_word_try < len(sentences_list):
                            idx_tier_try += 1
                            idx_word_try += 1
                        current_try += 1
                    print('current_try < try_time: ',current_try, try_time)
                    if current_try < try_time:  # #hide somethings
                        if idx_sentences_list < len(sentences_list)-2 and sentences_list[idx_sentences_list].upper() == sentences_list[idx_sentences_list+2].upper() and sentences_list[idx_sentences_list+1].upper() == sentences_list[idx_sentences_list+3].upper()\
                                and sentences_list[idx_sentences_list].upper() == tier[i + 1][0].upper() and sentences_list[idx_sentences_list].upper() != 'HOUSE'and sentences_list[idx_sentences_list].upper() != 'PEPPER' :
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(' '.join(new_sentence))
                                new_sentence = []
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(' '.join(new_sentence))
                                new_sentence = []
                        if idx_sentences_list < len(sentences_list) and sentences_list[idx_sentences_list].upper() == 'I' and sentences_list[idx_sentences_list + 1].upper()== 'SAY' and \
                        sentences_list[idx_sentences_list + 2].upper() == 'AH':
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(' '.join(new_sentence))
                                new_sentence = []
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(' '.join(new_sentence))
                                new_sentence = []
                            new_sentence.append(sentence[j])
                            idx_sentences_list += 1
                            j += 1
                            if j == len(sentence):
                                j = 0
                                l += 1
                                sentence = non_gold_sentences[l]
                                adjusted_non_gold_sentences.append(' '.join(new_sentence))
                                new_sentence = []
                        if idx_sentences_list < len(sentences_list) - 2 and i + 3 < len(tier):
                            print('current_try < try_time: ', sentences_list[idx_sentences_list].upper(),sentences_list[idx_sentences_list+1].upper(),sentences_list[idx_sentences_list+2].upper(), i, tier[i + 1][0].upper(),tier[i + 2][0].upper(),tier[i + 3][0].upper())

                    print(i, token_label)
                    i = i + 1

                elif "'" in token and "'" not in token_label and token.upper() != "A'AH":
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' "'" in token and "'" not in token_label')
                    move_step = 0
                    if token_label.upper() == 'DO':
                        tmp = tier[i+1][0]
                        if tier[i+1][0] == '#' and tier[i+2][0].upper() == 'T':
                            new_sentence.append('#')
                            tmp = 'N'
                            token_label = token_label + tmp + "'" + tier[i+2][0]
                            move_step = 3
                        elif tier[i + 1][0].upper() == 'N' and tier[i + 2][0].upper() == 'T':
                            token_label = token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                            move_step = 3
                        elif tier[i + 1][0].upper() == 'N' and tier[i + 2][0].upper() == '#' and tier[i + 3][0].upper() == 'T':
                            new_sentence.append('#')
                            token_label = token_label + tier[i + 1][0] + "'" + tier[i+3][0]
                            move_step = 4
                        else:
                            print('This case has not been handled')
                            token_label = token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                            move_step = 3
                    
                    if token_label.upper() == 'DID':
                        if tier[i + 1][0].upper() == 'N' and tier[i + 2][0].upper() == 'T':
                            token_label = token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                            move_step = 3

                    if token_label.upper() == 'CA':
                        if tier[i + 1][0].upper() == 'N' and tier[i + 2][0].upper() == 'T':
                            token_label = token_label + tier[i + 1][0] + "'" + tier[i + 2][0]
                            move_step = 3

                    if token_label.upper() == 'CHAMPIONS':
                        token_label = token_label + "'"
                        move_step = 1

                    if token_label.upper() == 'M':
                        token_label = "'" + token_label
                        move_step = 1

                    if token_label.upper() == 'S':
                        token_label = "'" + token_label
                        move_step = 1

                    if token_label.upper() == 'IT':
                        token_label = token_label + "'" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'N':
                        token_label = token_label + "'" + tier[i+1][0]
                        move_step = 2

                    if token_label.upper() == 'I':
                        token_label = token_label + "'" + tier[i+1][0]
                        move_step = 2

                    if token_label.upper() == 'WE':
                        token_label = token_label + "'" + tier[i+1][0]
                        move_step = 2

                    if token_label.upper() == 'MOMO':
                        token_label = token_label + "'" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'WHAT':
                        token_label = token_label + "'" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'DAT':
                        token_label = token_label + "'" + tier[i + 1][0]
                        move_step = 2
                    if token_label.upper() == 'HM':
                        if tier[i + 1][0] == '#':
                            token_label = token_label + "'" + 'm'
                        else:
                            token_label = token_label + "'" + tier[i + 1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        new_sentence.append(token)
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif "-" in token and "-" not in token_label and token.upper() != 'CO-COMMANDER':
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' "-" in token and "-" not in token_label')
                    move_step = 0
                    if token_label.upper() == 'PRO':
                        token_label = token_label + "-" + tier[i+1][0]
                        move_step = 2

                    if token_label.upper() == 'UN':
                        token_label = token_label + "-" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'MA':
                        token_label = token_label + "-" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'E':
                        token_label = token_label + "-" + tier[i + 1][0]
                        move_step = 2

                    if token_label.upper() == 'PRE':
                        token_label = token_label + "-" + tier[i + 1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        new_sentence.append(token)
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif "." in token and len(token) != len(token_label):
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' "." in token and "." not in token_label')
                    move_step = 0
                    if token_label.upper() == 'O.':
                        if tier[i+1][0].upper() == 'A.':
                            token_label = token_label + tier[i+1][0]
                            move_step = 2
                        else :
                            token_label = token_label + tier[i+1][0] + "."
                            move_step = 2

                    if token_label.upper() == 'A.':
                        token_label = token_label + tier[i+1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        new_sentence.append(token)
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif sentences_list[idx_sentences_list].upper() == 'CANNOT':
                    move_step = 1
                    if tier[i+1][0].upper() == 'NOT':
                        token_label = 'CAN' + tier[i+1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        new_sentence.append(token)
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif sentences_list[idx_sentences_list].upper() == 'CO-COMMANDER':
                    if tier[i+1][0].upper() == 'COMMANDER':
                        token_label = 'CO-' + tier[i+1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        new_sentence.append(token)
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif sentences_list[idx_sentences_list].upper() == token_label.upper():
                    c_tier = 0
                    c_word = 0
                    idx_tier = i+1
                    idx_word = idx_sentences_list + 1
                    flag_diese = False
                    while idx_tier < len(tier):
                        if token_label.upper() == tier[idx_tier][0].upper():
                            idx_tier += 1
                            c_tier += 1
                        elif '#' == tier[idx_tier][0]:
                            try_time = 3
                            idx_tier_try = idx_tier + 1
                            idx_word_try = idx_word
                            current_try = 0
                            while current_try < try_time:
                                while idx_word_try < len(sentences_list) and sentences_list[idx_word_try] in punctuation_list:
                                    idx_word_try +=1
                                if idx_word_try < len(sentences_list):
                                    print(sentences_list[idx_word_try],idx_word_try, tier[idx_tier_try][0].upper(),idx_tier_try, ' - flag_diese = COompare')

                                if idx_tier_try < len(tier) and idx_word_try < len(sentences_list) and tier[idx_tier_try][0].upper() != sentences_list[idx_word_try].upper() and tier[idx_tier_try][0].upper() != '#':
                                    break
                                if idx_tier_try < len(tier) -1 and idx_word_try < len(sentences_list):
                                    idx_tier_try += 1
                                    idx_word_try += 1
                                current_try += 1
                            if current_try < try_time: # #hide somethings
                                flag_diese = True
                                print(token_label.upper(), tier[idx_tier][0].upper(),' - flag_diese = True')
                            idx_tier += 1
                            continue
                        else:
                            break
                    while idx_word < len(sentences_list):
                        if sentences_list[idx_sentences_list].upper() == sentences_list[idx_word].upper():
                            idx_word += 1
                            c_word += 1
                        elif sentences_list[idx_word] in punctuation_list:
                            idx_word += 1
                            continue
                        elif flag_diese is True and (sentences_list[idx_word].upper() == 'I' or sentences_list[idx_word].upper() == "'M"):
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'SAID':
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'DI' and sentences_list[idx_sentences_list].upper() != "PERFUME":
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'YOU':
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'FIT':
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'GO':
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'IM':
                            idx_word += 1
                            continue
                        elif flag_diese is True and sentences_list[idx_word].upper() == 'DEY':
                            idx_word += 1
                            continue

                        else:
                            break
                    print('c_tier == c_word:', c_tier, c_word)
                    if c_tier == c_word:
                        new_sentence.append(token)
                        print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' - token.upper() == token_label.upper() =')
                        i = i + 1
                        j = j + 1
                        idx_sentences_list += 1
                    else:
                        new_sentence.append(token)
                        print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' - token.upper() == token_label.upper() !=')
                        j = j + 1
                        idx_sentences_list += 1

                elif tier[i-1][0] == '#':
                    print(sentence[j], j, '#', sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)
                    print(sentences_list[idx_sentences_list], tier[i][0])
                    print("new_sentence: ", new_sentence)
                    if sentences_list[idx_sentences_list].upper() == tier[i][0].upper():
                        new_sentence.append('(' + sentences_list[idx_sentences_list] + ')')
                        j = j + 1
                        idx_sentences_list += 1
                    while sentences_list[idx_sentences_list].upper() != tier[i][0].upper():
                        if sentence[j] in punctuation_list:
                            new_sentence.append(sentence[j])
                            j += 1
                        elif sentence[j].upper() == "DON'T" and tier[i][0].upper() == 'DO':
                                break
                        elif sentence[j].upper() == "DON'T" and tier[i][0].upper() == 'T':
                            new_sentence.append(sentences_list[idx_sentences_list])
                            idx_sentences_list += 1
                            j += 1
                            i += 1
                            break
                        else:
                            print(new_sentence)
                            new_sentence.append('(' + sentences_list[idx_sentences_list] + ')')
                            idx_sentences_list += 1
                            j += 1
                        if j == len(sentence):
                            j = 0
                            l += 1
                            sentence = non_gold_sentences[l]
                            adjusted_non_gold_sentences.append(' '.join(new_sentence))
                            new_sentence = []
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, 'tier[i-1][0] == #')
                else:
                    print(token, j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label ,'====================else')
            l += 1
            adjusted_non_gold_sentences.append(' '.join(new_sentence))

    return adjusted_non_gold_sentences


def write_to_tsv(gold_sentences, non_gold_sentences, output_file_path, filename=None):
    """Write the gold and non-gold sentences to a TSV file."""
    if filename:
        with open(output_file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            for gold, non_gold in zip(gold_sentences, non_gold_sentences):
                writer.writerow([filename, gold, non_gold])
    else:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['Gold', 'Non-Gold'])
            for gold, non_gold in zip(gold_sentences, non_gold_sentences):
                writer.writerow([gold, non_gold])


# # Paths
# # WAZL_15_MC-Abi_MG
# gold_conllu_file_path = 'WAZL_15_MC-Abi_MG.conllu'
# non_gold_conllu_file_path = 'WAZL_15_MC-Abi_MG-non_gold.conllu'
# textgrid_file_path = 'WAZL_15_MC-Abi_MG-syl_tok.TextGrid'
# output_tsv_file_path = 'WAZL_15_MC-Abi_MG.tsv'

# # Processing
# gold_sentences = extract_sentences(gold_conllu_file_path)
# new_gold_sentences = []
# for sentence in gold_sentences:
#     new_gold_sentences.append(' '.join(sentence))

# tier_combined = extract_token_and_pause_times(textgrid_file_path)
# non_gold_sentences = extract_sentences(non_gold_conllu_file_path)
# adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(non_gold_sentences, tier_combined)
# # Writing to TSV
# write_to_tsv(new_gold_sentences, adjusted_non_gold_sentences, output_tsv_file_path)


def main():

    # Chemins des répertoires
    gold_dir = "SUD_Naija-NSC-master/"
    non_gold_dir = "SUD_Naija-NSC-master-gold-non-gold-TALN/"
    textgrid_dir = "TEXTGRID_WAV_gold_non_gold_TALN/"
    output_dir = "TSV/TSV_sentences_gold_non_gold_TALN/"

    # Obtenir tous les fichiers
    gold_files = get_files_from_directory(gold_dir, '.conllu')
    non_gold_files = get_files_from_directory(non_gold_dir, '.conllu')
    textgrid_files = get_files_from_directory(textgrid_dir, '.TextGrid')

    # Traitement pour chaque fichier
    for gold_file in gold_files:
        base_name = os.path.basename(gold_file).split('.')[0]

        if gold_file.endswith('MG.conllu') or gold_file.endswith('M.conllu'):
            # Construire les chemins pour les fichiers non_gold et textgrid correspondants
            non_gold_file = os.path.join(non_gold_dir, base_name + '.conllu')

            if base_name.startswith('ABJ'):
                folder = '_'.join(base_name.split('_')[:3])
            else:
                folder = '_'.join(base_name.split('_')[:2])

            textgrid_file = os.path.join(textgrid_dir, folder + '/' + base_name + '-syl_tok.TextGrid')

            output_tsv_file_path = os.path.join(output_dir, 'compare_gold_non_gold_' + base_name + '.tsv')
            output_global_tsv_file_path = os.path.join(output_dir, 'all_sentences.tsv')
            
            if not os.path.exists(output_global_tsv_file_path):
                with open(output_global_tsv_file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter='\t')
                    writer.writerow(['File Name', 'Gold', 'Non-Gold'])

            if non_gold_file in non_gold_files:
                print(f"Traitement de {base_name}")

                # if gold_file not in list_file:
                # if "WAZL" in gold_file: 
                gold_sentences = extract_sentences(gold_file)
                new_gold_sentences = [' '.join(sentence) for sentence in gold_sentences]

                tier_combined = extract_token_and_pause_times(textgrid_file)
                non_gold_sentences = extract_sentences(non_gold_file)
                adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(non_gold_sentences, tier_combined)

                # Writing to TSV
                write_to_tsv(new_gold_sentences, adjusted_non_gold_sentences, output_tsv_file_path)
                write_to_tsv(new_gold_sentences, adjusted_non_gold_sentences, output_global_tsv_file_path, filename=base_name)

            else:
                print(f"Fichier manquant pour {base_name}")


if __name__ == "__main__":
    main()