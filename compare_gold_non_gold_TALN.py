from praatio import tgio
import csv

def extract_gold_sentences(conllu_file_path):
    """Extract gold sentences from the .conllu file."""
    gold_sentences = []
    with open(conllu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('# text ='):
                gold_sentence = line.split('=')[1].strip()
                gold_sentences.append(gold_sentence)
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

    punctuation_list = ['>', '<', '//', '?//', '[', ']', '{', '}', '|c', '>+', '||', '&//', '(', ')', '|r', '>=']

    for sentence in non_gold_sentences:
        tokens = sentence.split()

        new_sentence = []

        for token in tokens:
            if token in punctuation_list:
                new_sentence.append(token)

            for token_label, xmin, xmax in tier:
                if token == token_label:
                    new_sentence.append(token)
                    break

                elif token_label == "#":
                    new_sentence.append("#")

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
gold_conllu_file_path = 'SUD_Naija-NSC-master/ABJ_GWA_03_Cost-Of-Living-In-Abuja_MG.conllu'
non_gold_conllu_file_path = 'SUD_Naija-NSC-master-gold-non-gold-TALN/ABJ_GWA_03_Cost-Of-Living-In-Abuja_MG.conllu'
textgrid_file_path = 'TEXTGRID_WAV_gold_non_gold_TALN/ABJ_GWA_03/ABJ_GWA_03_Cost-Of-Living-In-Abuja_MG-syl_tok.TextGrid'
output_tsv_file_path = 'TSV/compare_gold_non_gold.tsv'

# Processing
gold_sentences = extract_gold_sentences(gold_conllu_file_path)
tier_combined = extract_token_and_pause_times(textgrid_file_path)
non_gold_sentences = extract_gold_sentences(non_gold_conllu_file_path)
adjusted_non_gold_sentences = insert_pauses_in_non_gold_sentences(non_gold_sentences, tier_combined)

# Writing to TSV
write_to_tsv(gold_sentences, adjusted_non_gold_sentences, output_tsv_file_path)




# gold_file_path = "/SUD_Naija-NSC-master/"
# non_gold_file_path = "/SUD_Naija-NSC-master-gold-non-gold-TALN/"
# non_gold_textgrid_path = "TEXTGRID_WAV_gold_non_gold_TALN/"

# output_tsv_file_path = "TSV/compare_gold_non_gold_hash_position.tsv"

