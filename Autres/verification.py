from conll3 import *
import os
from tqdm import tqdm
import re


pitchtier_path = "./Praat/"
conll_path = "./SUD_Naija-NSC-master/"


def extract_times_pitchtier(pitchtier_lines):
    """
    Extracts the first and last time values from a list of lines in a PitchTier file.

    Args:
    pitchtier_lines (list of str): The lines from a PitchTier file.

    Returns:
    tuple: A tuple containing two elements, the first and last time values. 
           The first element is the first time value encountered in the list, 
           and the last element is the last time value.
    """
    time_first = None
    time_last = None
    for line in pitchtier_lines:
        if line.strip().startswith('number'):
            # print(line)
            time_current = float(line.strip().split('=')[1].strip())
            if time_first is None:
                time_first = time_current
            time_last = time_current  # Always update to the last found
    return time_first, time_last

def convert_misc_to_dict(misc):
    """
    Converts a 'misc' formatted string into a dictionary. Each key-value pair in the string 
    is separated by '|', and key and value within a pair are separated by '='.

    Args:
    misc (str): The 'misc' formatted string containing key-value pairs.

    Returns:
    dict: A dictionary with keys and values extracted from the 'misc' string.
    """
    result_dict = {} 
    pairs = misc.split("|")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict

def extract_alignbegin_alignend(file_path):
    """
    Extracts the first 'AlignBegin' and last 'AlignEnd' times from the Conllu file.

    Args:
    file_path (str): Path to the Conllu file.

    Returns:
    tuple: A tuple containing two elements - the first 'AlignBegin' and the last 'AlignEnd' time values.
    """
    # Convert the conllu file to dependency trees
    trees = conllFile2trees(file_path)

    align_begin_first = None
    align_end_last = None

    for tree in trees:
        words = tree.words
        index = 1
        while index < len(words):
            misc = tree[index].get("misc", "_")
            if misc != "_":  # Check if the misc field is not empty
                misc_dict = convert_misc_to_dict(misc)
                align_begin = misc_dict.get("AlignBegin")
                align_end = misc_dict.get("AlignEnd")

                if align_begin is not None:
                    if align_begin_first is None:
                        align_begin_first = align_begin
                if align_end is not None:
                    align_end_last = align_end

            index += 1

    return align_begin_first, align_end_last

def extract_slam(file_path, output_file):
    """
    Extracts SLAM related information from Conllu files and prints it to a specified output file.

    Args:
    file_path (str): Path to the Conllu file.
    output_file: The file object to which the extracted information is to be printed.
    """
    # Convert the conllu file to dependency trees
    trees = conllFile2trees(file_path)

    for tree in trees:
        tree_str = str(tree)
        sent_id_match = re.search(r'# sent_id = (.+)', tree_str)
        sent_id = sent_id_match.group(1) if sent_id_match else "_"
        words = tree.words
        index = 1
        while index < len(words):
            word = tree[index].get("t")
            idx = tree[index].get("id")
            misc = tree[index].get("misc", "_")
            if word == "#":
                if misc != "_":  # Check if the misc field is not empty
                    misc_dict = convert_misc_to_dict(misc)
                    Syl1SlopeGlo = misc_dict.get("Syl1SlopeGlo")
                    Syl1AvgHeightGlo = misc_dict.get("Syl1AvgHeightGlo")
                    Syl1PitchRangeGlo = misc_dict.get("Syl1PitchRangeGlo")
                    Syl1SlopeLoc = misc_dict.get("Syl1SlopeLoc")
                    Syl1AvgHeightLoc = misc_dict.get("Syl1AvgHeightLoc")
                    Syl1PitchRangeLoc = misc_dict.get("Syl1PitchRangeLoc")

                    # Check if any of the attributes are not None
                    if any(attr is not None for attr in [Syl1SlopeGlo, Syl1AvgHeightGlo, Syl1PitchRangeGlo, Syl1SlopeLoc, Syl1AvgHeightLoc, Syl1PitchRangeLoc]):
                        print(f"Sent ID: {sent_id}", file=output_file)
                        print(f"    ID # with contour SLAM: {idx} {word} \n", file=output_file)
                        # print(f"    Syl1SlopeGlo: {Syl1SlopeGlo}")
                        # print(f"    Syl1AvgHeightGlo: {Syl1AvgHeightGlo}")
                        # print(f"    Syl1PitchRangeGlo: {Syl1PitchRangeGlo}")
                        # print(f"    Syl1SlopeLoc: {Syl1SlopeLoc}")
                        # print(f"    Syl1AvgHeightLoc: {Syl1AvgHeightLoc}")
                        # print(f"    Syl1PitchRangeLoc: {Syl1PitchRangeLoc} \n")

            index += 1


def verification_syllables(file_path, output_file):
    """
    Verifies if all the necessary syllable information is present for each word in the Conllu file.
    If any information is missing, it prints the details into the specified output file.

    Args:
    file_path (str): Path to the Conllu file.
    output_file: The file object to which the missing information details are to be printed.
    """
    # Convert the conllu file to dependency trees
    trees = conllFile2trees(file_path)
    for tree in trees:
        tree_str = str(tree)
        sent_id_match = re.search(r'# sent_id = (.+)', tree_str)
        sent_id = sent_id_match.group(1) if sent_id_match else "_"
        words = tree.words
        index = 1
        while index < len(words):
            word = tree[index].get("t")
            idx = tree[index].get("id")
            pos = tree[index].get("tag")
            misc = tree[index].get("misc", "_")
            misc_dict = convert_misc_to_dict(misc)
            syllables_count = misc_dict.get("SyllableCount", "_")
            if syllables_count != "_" and pos != "PUNCT":
                for i in range(1, int(syllables_count)):
                    syl = misc_dict.get(f"Syl{i}")
                    sylLoc = misc_dict.get(f"Syl{i}Loc")
                    if (syl != "FUSED") and (sylLoc != "X"):
                        syllable_info = {
                            "Syl": misc_dict.get(f"Syl{i}"),
                            "SylLoc": misc_dict.get(f"Syl{i}Loc"),
                            "SylGlo": misc_dict.get(f"Syl{i}Glo"),
                            "SylAvgHeightGlo": misc_dict.get(f"Syl{i}AvgHeightGlo"),
                            "SylAvgHeightLoc": misc_dict.get(f"Syl{i}AvgHeightLoc"),
                            "SylPitchRangeGlo": misc_dict.get(f"Syl{i}PitchRangeGlo"),
                            "SylPitchRangeLoc": misc_dict.get(f"Syl{i}PitchRangeLoc"),
                            "SylSlopeGlo": misc_dict.get(f"Syl{i}SlopeGlo"),
                            "SylSlopeLoc": misc_dict.get(f"Syl{i}SlopeLoc")
                        }

                        missing_info = [key for key, value in syllable_info.items() if value is None]
                        if missing_info:
                            print(f"Sent ID: {sent_id}", file=output_file)
                            print(f"    ID Word: {idx} {word}", file=output_file)
                            print(f"    Missing information for Syllable {i}: {syl} : {', '.join(missing_info)} \n", file=output_file)

            index += 1
                        

if __name__ == "__main__":
    # Get a list of all PitchTier files
    pitchtier_files = [f for f in os.listdir(pitchtier_path) if f.endswith('.PitchTier')]
    # Get a list of all Conllu files
    conllu_files = [f for f in os.listdir(conll_path) if f.endswith('.conllu')]

    # Define a threshold for significant difference (in milliseconds)
    significant_difference_threshold = 1000

    with open('verification_pitchtier_conllu_duration_pause_syll.txt', 'w') as output_file:
        # Loop through each file
        for conllu_file in conllu_files:
            base_name = os.path.splitext(conllu_file)[0]
            corresponding_pitchtier = base_name + ".PitchTier"
            
            if corresponding_pitchtier in pitchtier_files:
                # Read the contents of the PitchTier file
                with open(os.path.join(pitchtier_path, corresponding_pitchtier), 'r') as pt_file:
                    pitchtier_lines = pt_file.readlines()
                
                # Read the contents of the Conllu file
                conllu_file_path = os.path.join(conll_path, conllu_file)
                
                # Extract times from PitchTier and Conllu
                pitchtier_first, pitchtier_last = extract_times_pitchtier(pitchtier_lines)
                conllu_first, conllu_last = extract_alignbegin_alignend(conllu_file_path)
                
                # Convert times to milliseconds and compare
                pitchtier_span = (pitchtier_first + pitchtier_last) * 1000  # assuming seconds to milliseconds
                conllu_span = int(conllu_first) + int(conllu_last) # assuming the values are in milliseconds
                
                # Print or store the comparison
                # print(f"File: {base_name}")
                # print(f"PitchTier span: {pitchtier_span} ms, Conllu span: {conllu_span} ms")

                # Check for significant difference
                if abs(pitchtier_span - conllu_span) > significant_difference_threshold:
                    print(f"File: {base_name}", file=output_file)
                    print(f"  Significant difference found:", file=output_file)
                    print(f"     PitchTier span: {pitchtier_span} ms, Conllu span: {conllu_span} ms", file=output_file)
                    print(f"     Difference: {abs(pitchtier_span - conllu_span)} ms \n", file=output_file)

                # Extract slam values from Conllu for pause words #
                extract_slam(conllu_file_path, output_file)

                # Verification of syllables 
                verification_syllables(conllu_file_path, output_file)

                