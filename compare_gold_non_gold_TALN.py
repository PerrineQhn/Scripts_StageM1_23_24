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

    punctuation_list = ['>', '<', '//', '?//', '[', ']', '{', '}', '|c', '>+', '||', '&//', '(', ')', '|r', '>=', '//+',
                        '?//]', '//]', '//=', '!//', '?//=', '!//=', '//)', '|a', '&?//']
    i = 0
    sentences_list = [word for s in non_gold_sentences for word in s]
    for punctuation in punctuation_list:
        if punctuation in sentences_list:
            sentences_list = [x for x in sentences_list if x != punctuation]
    idx_sentences_list = 0
    for sentence in non_gold_sentences:
            new_sentence = []
            j = 0
            while j < len(sentence):
                token = sentence[j]
                if i >= len(tier):
                    break
                token_label, xmin, xmax = tier[i]
                if token in punctuation_list:
                    new_sentence.append(token)
                    j = j + 1
                elif token_label == "#":
                    new_sentence.append("#")
                    print(i, token_label)
                    i = i + 1
                elif "'" in token and "'" not in token_label:
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' "'" in token and "'" not in token_label')
                    if token_label.upper() == 'DO':
                        token_label= token_label + tier[i+1][0] + "'" + tier[i+2][0]
                        move_step = 3
                    
                    if token_label.upper() == 'N':
                        token_label = token_label + "'" + tier[i+1][0]
                        move_step = 2

                    if token.upper() == token_label.upper():
                        i += move_step
                        j += 1
                        idx_sentences_list += 1

                elif token.upper() == token_label.upper():
                    new_sentence.append(token)
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label, ' - token.upper() == token_label.upper()')

                    i = i + 1
                    j = j + 1
                    idx_sentences_list += 1

                elif '~' == token[-1] and token[:-1].upper() == token_label.upper():
                    new_sentence.append(token)
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)

                    i = i + 1
                    j = j + 1
                    idx_sentences_list += 1

                elif tier[i-1][0] == '#' and (idx_sentences_list < len(sentences_list) -1) and sentences_list[idx_sentences_list+1].upper() == tier[i][0].upper() and sentences_list[idx_sentences_list] != tier[i][0].upper():
                    new_sentence.append(token)
                    print(sentence[j], j, '#', sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)
                    j = j + 1
                    idx_sentences_list += 1

                elif tier[i-1][0] == '#':
                    print(sentence[j], j, '#', sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)
                    while sentences_list[idx_sentences_list] != tier[i][0]:
                        if sentence[j] in punctuation_list:
                            new_sentence.append(sentence[j])
                            j += 1

                        print(new_sentence)
                        new_sentence.append('(' + sentences_list[idx_sentences_list] + ')')
                        idx_sentences_list += 1
                        j += 1
                    print(sentence[j], j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)
                else:
                    print(token, j, sentences_list[idx_sentences_list], idx_sentences_list, i, token_label)


            adjusted_non_gold_sentences.append(' '.join(new_sentence))

    return adjusted_non_gold_sentences




def write_to_tsv(gold_sentences, non_gold_sentences, output_file_path):
    """Write the gold and non-gold sentences to a TSV file."""
    with open(output_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['Gold', 'Non-Gold'])
        for gold, non_gold in zip(gold_sentences, non_gold_sentences):
            writer.writerow([gold, non_gold])

# Paths
gold_conllu_file_path = 'SUD_Naija-NSC-master/KAD_17_Turkeys_MG.conllu'
non_gold_conllu_file_path = 'SUD_Naija-NSC-master-gold-non-gold-TALN/KAD_17_Turkeys_MG.conllu'
textgrid_file_path = 'TEXTGRID_WAV_gold_non_gold_TALN/KAD_17/KAD_17_Turkeys_MG-syl_tok.TextGrid'
output_tsv_file_path = 'TSV/compare_gold_non_gold.tsv'

# Processing
gold_sentences = extract_sentences(gold_conllu_file_path)
new_gold_sentences = []
for sentence in gold_sentences:
    new_gold_sentences.append(' '.join(sentence))


tier_combined = extract_token_and_pause_times(textgrid_file_path)
non_gold_sentences = extract_sentences(non_gold_conllu_file_path)
adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(non_gold_sentences, tier_combined)

# # Writing to TSV
# write_to_tsv(new_gold_sentences, adjusted_non_gold_sentences, output_tsv_file_path)



# Paths
# output_tsv_file_path = "TSV/compare_gold_non_gold_hash_position.tsv"

# # Chemins des répertoires
# gold_dir = "SUD_Naija-NSC-master/"
# non_gold_dir = "SUD_Naija-NSC-master-gold-non-gold-TALN/"
# textgrid_dir = "TEXTGRID_WAV_gold_non_gold_TALN/"
# output_dir = "TSV/TSV_sentences_gold_non_gold_TALN/"

# # Obtenir tous les fichiers
# gold_files = get_files_from_directory(gold_dir, '.conllu')
# non_gold_files = get_files_from_directory(non_gold_dir, '.conllu')


# textgrid_files = get_files_from_directory(textgrid_dir, '.TextGrid')

# # Traitement pour chaque fichier
# for gold_file in gold_files:
#     base_name = os.path.basename(gold_file).split('.')[0]

#     if gold_file.endswith('MG.conllu') or gold_file.endswith('M.conllu'):
#         # Construire les chemins pour les fichiers non_gold et textgrid correspondants
#         non_gold_file = os.path.join(non_gold_dir, base_name + '.conllu')

#         if base_name.startswith('ABJ'):
#             folder = '_'.join(base_name.split('_')[:3])
#         else:
#             folder = '_'.join(base_name.split('_')[:2])

#         textgrid_file = os.path.join(textgrid_dir, folder + '/' + base_name + '-syl_tok.TextGrid')

#         output_tsv_file_path = os.path.join(output_dir, 'compare_gold_non_gold_' + base_name + '.tsv')

#         if non_gold_file in non_gold_files:
#             print(f"Traitement de {base_name}")
#             # Processing
#             gold_sentences = extract_sentences(gold_file)
#             new_gold_sentences = [' '.join(sentence) for sentence in gold_sentences]

#             tier_combined = extract_token_and_pause_times(textgrid_file)
#             non_gold_sentences = extract_sentences(non_gold_file)
#             adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(non_gold_sentences, tier_combined)

#             # Writing to TSV
#             write_to_tsv(new_gold_sentences, adjusted_non_gold_sentences, output_tsv_file_path)
#         else:
#             print(f"Fichier manquant pour {base_name}")