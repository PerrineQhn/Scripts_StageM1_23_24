import os
import re
import urllib.request
from conll3 import *
from tqdm import tqdm

# Function to extract occurrences of given terms from a single file
def extract_occurrences(file_path, term1 = None, term2 = None,  output_wav = None):
    occurrences = []  # List to store occurrences
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    wav_saved = False

    for tree in trees:
        # Extract sentence text and ID from the tree string
        tree_str = str(tree)
        sent = re.search(r'# text = (.+)', tree_str)
        sent_text = sent.group(1) if sent else ""
        sent_id_match = re.search(r'# sent_id = (.+)', tree_str)  # Search for sentence ID
        if sent_id_match:
            sent_id = sent_id_match.group(1)
        else:
            sent_id = "X"

        words = tree.words
        index = 1
        while index < len(words):
            # Extract information about the current word and its neighbors
            pos = tree[index].get("tag", "X")
            form = tree[index].get("t", "X")
            form_voisin_droit = tree[index+1].get("t", "X")
            form_voisin_gauche = tree[index - 1].get("t", "X") if index - 1 > 0 else "X"
            pos_voisin_droit = tree[index + 1].get("tag", "X")
            pos_voisin_gauche = tree[index - 1].get("tag", "X") if index - 1 > 0 else "X"
            misc = tree[index].get("misc", "")
            misc_dict = convert_misc_to_dict(misc)
            gov = tree[index+1].get("gov", {})
            relation = next(iter(gov.values()), "X")

            # Check if the current word index is less than the length of words list minus 1, and if the current word's form matches term1.
            if index < len(words) - 1 and (form==term1 or form==term2):
               # Extract various attributes of term1
                id = tree[index].get("id", "X")

                form = tree[index].get("t", "X")
                pos = tree[index].get("tag", "X")

                misc = tree[index].get("misc", "")
                misc_dict = convert_misc_to_dict(
                    misc) 
                
                durationGlobal = misc_dict.get("Syl1DurationGlobalZscore", "X")
                durationLocal = misc_dict.get("Syl1DurationLocalZscore", "X")
                durationNormalized = misc_dict.get("Syl1DurationNormalized", 'X')

                meanGLobal = misc_dict.get("Syl1MeanF0GlobalZscore", "X")
                meanLocal = misc_dict.get("Syl1MeanF0LocalZscore", "X")
                meanNormalized = misc_dict.get("Syl1MeanF0Normalized", 'X')
                semitonFromUtterance = misc_dict.get("Syl1SemitonesFromUtteranceMean", 'X')

                
                # misc_droit = tree[index + 1].get("misc", "")
                # misc_dict_voisin_droit = convert_misc_to_dict(
                #     misc_droit)

                # t1_align_begin = misc_dict.get("Syl1AlignBegin", "X")

                # form_voisin, duree_tok_voisin, semiton_tok_voisin, pos_voisin, duree_relative,  semiton_relatif, id_voisin, Syl1SlopeGloVoisin, Syl1SlopeLocVoisin, t2_align_end, Syl1SlopeVoisin = "X", "X", "X", "X", "X", "X", "X", "X", "X", "X", "X"

                # gov_bis = tree[index+1].get("gov", {})
                # gov_id, token_relation = next(iter(gov_bis.items()), ("X", "X"))

                # # Extract attributes for term2 when it appears to the right of term1
                # if form_voisin_droit == term2 :
                
                # # Check if the next word is a verb and does not contain "Syl2" in its miscellaneous information
                # if pos_voisin_droit == 'VERB' and "Syl2" not in misc_dict_voisin_droit :

                # # Check if the current word (term1) and the next word (term2) form a specific grammatical relationship,
                # # and "Syl2" is not in the miscellaneous information of the next word, and the next word is a VERB or AUX
                # if (gov_id == id) and (token_relation == 'comp:aux' or re.match(r'compound:sv.*', token_relation)) and ("Syl2" not in misc_dict_voisin_droit) and (pos_voisin_droit == 'VERB' or pos_voisin_droit == 'AUX'):
                #     Similar extraction for term2 if found
                #     id_voisin = tree[index+1].get("id", "X")
                #     pos_voisin = pos_voisin_droit
                #     form_voisin = tree[index+1].get("t", "X")
                #     misc_droit = tree[index + 1].get("misc", "")
                #     misc_dict_voisin_droit = convert_misc_to_dict(
                #         misc_droit)
                #     duree_tok_voisin = misc_dict_voisin_droit.get("Syl1Duree", "X")
                #     semiton_tok_voisin = misc_dict_voisin_droit.get("Syl1MoyenneSemitones", "X")

                #     Syl1SlopeGloVoisin = misc_dict_voisin_droit.get("Syl1SlopeGlo", 'X')
                #     Syl1SlopeLocVoisin = misc_dict_voisin_droit.get("Syl1SlopeLoc", 'X')

                #     Syl1SlopeVoisin = misc_dict_voisin_droit.get("Syl1Slope", 'X')

                #     t2_align_end = misc_dict_voisin_droit.get("Syl1AlignEnd", "X")

                # # Extract attributes for term2 when it appears to the left of term1
                # elif form_voisin_gauche == term2 and index - 1 != 0:
                # # Check if the word to the left of the current word is an 'AUX' (auxiliary) and it's not the first word in the sentence
                # # elif pos_voisin_gauche == 'AUX' and index - 1 != 0:
                #     misc_gauche = tree[index - 1].get("misc", "")
                #     misc_dict_voisin_gauche = convert_misc_to_dict(
                #         misc_gauche)
                #     if "Syl2" not in misc_dict_voisin_gauche :
                #         pos_voisin = pos_voisin_gauche
                #         form_voisin = tree[index - 1].get("t", "X")
                #         misc_gauche = tree[index - 1].get("misc", "")
                #         misc_dict_voisin_gauche = convert_misc_to_dict(
                #             misc_gauche)
                #         duree_tok_voisin = misc_dict_voisin_gauche.get("DureeSyl1", "X")
                #         semiton_tok_voisin = misc_dict_voisin_gauche.get("MoyenneSyl1Semitones", "X")

                # # Calculate relative duration and semitone values between term1 and term2
                # if form_voisin and duree_tok_voisin and semiton_tok_voisin:
                #     if duree > duree_tok_voisin and duree != 'X' and duree_tok_voisin != 'X':
                #         duree_relative = "D1>D2"
                #     elif duree_tok_voisin > duree and duree != 'X' and duree_tok_voisin != 'X':
                #         duree_relative = "D2>D1"
                #     elif duree_tok_voisin == duree and duree != 'X' and duree_tok_voisin != 'X':
                #         duree_relative = "D1=D2"

                #     if semitone > semiton_tok_voisin and semitone != 'X' and semiton_tok_voisin != 'X':
                #         semiton_relatif = "S1>S2"
                #     elif semiton_tok_voisin > semitone and semitone != 'X' and semiton_tok_voisin != 'X':
                #         semiton_relatif = "S2>S1"
                #     elif semiton_tok_voisin == semitone and semitone != 'X' and semiton_tok_voisin != 'X':
                #         semiton_relatif = "S1=S2"
                
                # Create an occurrence dictionary and add it to the list
                if durationGlobal != 'X' and durationLocal != 'X' and durationNormalized != 'X' and meanGLobal != 'X' and meanLocal != 'X' and meanNormalized != 'X' and semitonFromUtterance != 'X':
                    occurrence = {
                        "ID_File": file_name,
                        "ID_Sent": sent_id,
                        "SentTexte": sent_text,
                        "form": form,
                        "pos": pos,
                        "durationGlobal": durationGlobal,
                        "durationLocal": durationLocal,
                        "durationNormalized": durationNormalized,
                        "meanGlobal": meanGLobal,
                        "meanLocal": meanLocal,
                        "meanNormalized": meanNormalized,
                        "semitonFromUtterance": semitonFromUtterance,
                    }

                    occurrences.append(occurrence)
                    #print(occurrences)
                
                # Download and save the WAV file (if not already saved)
                if not wav_saved:
                    wav_path = extract_and_save_wav(file_path, output_wav)
                    if wav_path:
                        occurrence["wav_path"] = wav_path
                        wav_saved = True
            index += 1

    return occurrences

# Function to extract all occurrences of given terms from all files in a directory
def extract_all_occurrences(directory_path, term1 = None, term2 = None, output_wav = None):
    occurrences = []  # Liste pour stocker toutes les occurrences
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".conllu") and "MG" in file:
                file_path = os.path.join(root, file)
                if term1 == None and term2 == None:
                    occurrences += extract_occurrences(file_path)
                elif term2 == None:
                    occurrences += extract_occurrences(file_path, term1)
                else:
                    occurrences += extract_occurrences(file_path, term1, term2)
    return occurrences

# Function to convert the miscellaneous information to a dictionary
def convert_misc_to_dict(misc):
    result_dict = {}  # Dictionnaire pour stocker les informations supplémentaires
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    #print(result_dict)
    return result_dict

# Function to extract and save the associated WAV file
def extract_and_save_wav(file_path, output_directory):
    # Extract sound_url from the CoNLL-U file and download the associated WAV file
    trees = conllFile2trees(file_path)
    for tree in trees:
        tree_str = str(tree)
        sound_url_match = re.search(r'# sound_url = (.+)', tree_str)
        if sound_url_match:
            sound_url = sound_url_match.group(1)
            if sound_url.endswith('.wav'):
                file_name = os.path.basename(file_path)
                file_name_without_ext = os.path.splitext(file_name)[0]
                output_file_name = f"{file_name_without_ext}.wav"
                if output_directory is not None:
                    output_path = os.path.join(output_directory, output_file_name)
                    urllib.request.urlretrieve(sound_url, output_path) 
                    return output_path
    return None

# Function to write occurrences to a TSV file
def write_occurrences_to_tsv(occurrences, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        # Write the header row for the TSV file
        file.write(
            "Form\tPOS\tDurationGlobal\tDurationLocal\tDurationNormalized\tMeanGlobal\tMeanLocal\tMeanNormalized\tSemitonFromUtterance\n")
        # Write each occurrence to the TSV file
        for occurrence in occurrences:
            file.write(
                f"{occurrence['form']}\t"
                f"{occurrence['pos']}\t"
                f"{occurrence['durationGlobal']}\t"
                f"{occurrence['durationLocal']}\t"
                f"{occurrence['durationNormalized']}\t"
                f"{occurrence['meanGlobal']}\t"
                f"{occurrence['meanLocal']}\t"
                f"{occurrence['meanNormalized']}\t"
                f"{occurrence['semitonFromUtterance']}\n"
            )
        print('TSV créé')



directory_path = "./SUD_Naija-NSC-master/"
#output_wav = "../WAV/GO_AUX_SVC/"
output_tsv = "./TSV/ArbreDecision/Sey-Say/arbre_decision_sey_say.tsv"
# output_tsv = "./TSV/ArbreDecision/DeyAux-DeyVerb/arbre_decision_dey_aux-dey_verb.tsv"
# output_tsv = "./TSV/ArbreDecision/GoAux-GoVerb/arbre_decision_go_aux-go_verb.tsv"
T1 = 'sey'
T2 = 'say'

occurrences = extract_all_occurrences(directory_path, T1, T2)
write_occurrences_to_tsv(occurrences, output_tsv)