import textgrid
import os

def generate_tiers_selection(directory):
    """
    Generates a selection of tiers from TextGrid files in a specific directory.

    :param directory: Path to the directory containing the TextGrid files.
    :return: Two dictionaries - one for the 'trans' tier and another for the other tiers.
    """
    tiers_trans = {}
    other_tiers = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith('.TextGrid'):
            # Tiers for phonetic and token alignment
            if 'MG-palign.TextGrid' in file:
                other_tiers[file] = ['TokensAlign', 'PhonAlign']
                #print(file, "palign")
            # Tiers for syllable alignment
            elif 'MG-syll.TextGrid' in file:
                other_tiers[file] = ['SyllAlign']
                #print(file)
            # Tiers for index alignment
            elif 'MG-id.TextGrid' in file:
                other_tiers[file] = ['index']
                #print(file)
            # Transcription tiers
            elif not any(substring in file for substring in ['MG-phon.TextGrid', 'MG-token.TextGrid', 'merged', 'MG-syll.TextGrid', 'MG-id.TextGrid']):
                tiers_trans[file] = ['trans']
                #print(file)

    return tiers_trans, other_tiers


def merge_textgrid_tiers(directory, tiers_trans, other_tiers, base_name_file, merged=None):
    """
    Merges different tiers from multiple TextGrid files into a single file.

    :param directory: Path to the directory containing the TextGrid files.
    :param tiers_trans: Dictionary of files with the 'trans' tier.
    :param other_tiers: Dictionary of other tiers to be merged.
    :param base_name_file: Base name for the output file.
    :param merged: Destination folder for the merged file (optional).
    """
    merged_textgrid = textgrid.TextGrid()

    # Ajout des tiers 'trans'
    for file, tiers_list in tiers_trans.items():
        tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
        for tier_name in tiers_list:
            tier = tg.getFirst(tier_name)
            print(tier)
            merged_textgrid.append(tier)

    # Définition de l'ordre spécifique des autres tiers
    tier_order = ['TokensAlign', 'SyllAlign', 'PhonAlign', 'index']

    # Ajout des autres tiers dans l'ordre spécifié
    for tier_name in tier_order:
        for file, tiers_list in other_tiers.items():
            if tier_name in tiers_list:
                tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
                tier = tg.getFirst(tier_name)
                merged_textgrid.append(tier)

    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f'{base_name_file}-merged.TextGrid'))
    else:
        merged_textgrid.write(os.path.join(directory, f'{base_name_file}-merged.TextGrid'))

def generate_tiers_selection_non_gold_silence(directory):
    """
    Generates a selection of tiers from TextGrid files in a specific directory.

    :param directory: Path to the directory containing the TextGrid files.
    :return: Two dictionaries - one for the 'trans' tier and another for the other tiers.
    """
    tiers_trans = {}
    other_tiers = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith('.TextGrid'):
            # Tiers for syllable alignment
            if 'M-syl_tok.TextGrid' in file:
                other_tiers[file] = ['Combined']
                # print(file)
            # Tiers for index alignment
            elif 'M-id.TextGrid' in file:
                other_tiers[file] = ['index']
                #print(file)
            elif 'M-palign.TextGrid' in file:
                other_tiers[file] = ['TokensAlign']
            # Transcription tiers
            elif not any(substring in file for substring in ['M-phon.TextGrid', 'M-token.TextGrid', 'merged', 'M-syll.TextGrid', 'M-id.TextGrid', 'M-syl_tok.TextGrid']):
                tiers_trans[file] = ['trans']
                #print(file)

    return tiers_trans, other_tiers

def merge_textgrid_non_gold_tiers(directory, tiers_trans, other_tiers, base_name_file, merged=None):
    """
    Merges different tiers from multiple TextGrid files into a single file.

    :param directory: Path to the directory containing the TextGrid files.
    :param tiers_trans: Dictionary of files with the 'trans' tier.
    :param other_tiers: Dictionary of other tiers to be merged.
    :param base_name_file: Base name for the output file.
    :param merged: Destination folder for the merged file (optional).
    """
    merged_textgrid = textgrid.TextGrid()

    # Add 'trans' tiers
    for file, tiers_list in tiers_trans.items():
        tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
        for tier_name in tiers_list:
            tier = tg.getFirst(tier_name)
            if tier is not None:  # Check if the tier is found
                merged_textgrid.append(tier)
            else:
                print(f"Tier '{tier_name}' not found in file: {file}")

    # Specific order of other tiers
    tier_order = ['TokensAlign', 'index', 'Combined']

    # Add other tiers in the specified order
    for tier_name in tier_order:
        for file, tiers_list in other_tiers.items():
            if tier_name in tiers_list:
                tg = textgrid.TextGrid.fromFile(os.path.join(directory, file))
                tier = tg.getFirst(tier_name)
                if tier is not None:  # Check if the tier is found
                    merged_textgrid.append(tier)
                else:
                    print(f"Tier '{tier_name}' not found in file: {file}")


    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f'{base_name_file}-merged.TextGrid'))
    else:
        merged_textgrid.write(os.path.join(directory, f'{base_name_file}-merged.TextGrid'))

def generate_tiers_selection_gold_non_gold_silence(directory, directory_gold):
    """
    Generates a selection of tiers from TextGrid files in a specific directory.

    :param directory: Path to the directory containing the TextGrid files.
    :return: Two dictionaries - one for the 'trans' tier and another for the other tiers.
    """
    tiers = {}
    tiers_combined = {}
    for file in sorted(os.listdir(directory)):
        if file.endswith('.TextGrid'):
            # Tiers for syllable alignment
            if 'MG-syl_tok.TextGrid' in file:
                tiers_combined[file] = ['Combined', 'SyllSil']
                # print(file)
    
    for file in sorted(os.listdir(directory_gold)):
        if file.endswith('.TextGrid'):
            if 'MG-palign.TextGrid' in file:
                tiers[file] = ['TokensAlign']
            # Tiers for index alignment
            elif 'MG-id.TextGrid' in file:
                tiers[file] = ['index']
                #print(file)
            elif 'MG-syll.TextGrid' in file:
                tiers[file] = ['SyllAlign']
            # Transcription tiers
            elif not any(substring in file for substring in ['MG-phon.TextGrid', 'MG-token.TextGrid', 'merged', 'MG-syll.TextGrid', 'MG-id.TextGrid', 'MG-syl_tok.TextGrid']):
                tiers[file] = ['trans']
                # print(file)

    return tiers, tiers_combined

def merge_gold_non_gold(directory, directory_gold, tiers, tiers_combined, base_name_file, merged=None):
    """
    Merges different tiers from multiple TextGrid files into a single file.

    :param directory: Path to the directory containing the TextGrid files.
    :param tiers_trans: Dictionary of files with the 'trans' tier.
    :param other_tiers: Dictionary of other tiers to be merged.
    :param base_name_file: Base name for the output file.
    :param merged: Destination folder for the merged file (optional).
    """
    merged_textgrid = textgrid.TextGrid()
    tier_order = ['trans', 'TokensAlign', 'SyllAlign', 'index', 'Combined', 'SyllSil']
    added_tiers = set()  # To track already added tiers

    for tier_name in tier_order:
        for file, tiers_list in (tiers.items() if tier_name != 'Combined' and tier_name != 'SyllSil' else tiers_combined.items()):
            # print(file, tiers_list)
            directory_used = directory_gold if tier_name != 'Combined' and tier_name != 'SyllSil' else directory
            for tier in tiers_list:
                # print(tier)
                if tier_name not in added_tiers:  # Check if the tier has already been added
                    print(f"Adding tier '{tier_name}' from file: {directory_used}, {file}")
                    tg = textgrid.TextGrid.fromFile(os.path.join(directory_used, file))
                    current_tier = tg.getFirst(tier_name)
                    if current_tier is not None:
                        merged_textgrid.append(current_tier)
                        added_tiers.add(tier_name)
                # else:
                #     print(f"Tier '{tier_name}' not found in file: {file}")

    # Sauvegarde du fichier TextGrid fusionné
    if merged:
        merged_textgrid.write(os.path.join(merged, f'{base_name_file}-merged.TextGrid'))
    else:
        merged_textgrid.write(os.path.join(directory, f'{base_name_file}-merged.TextGrid'))


# base_folder = './TEXTGRID_WAV'
# merged = './MERGED'

# base_folder = './TEXTGRID_WAV_nongold'
# merged = './MERGED/non_gold'

base_folder = 'TEXTGRID_WAV_gold_non_gold_TALN/'
base_folder_gold = 'TEXTGRID_WAV/'
merged = 'MERGED/gold_non_gold_01avril/'

for subdir in os.listdir(base_folder):
    subdir_path = os.path.join(base_folder, subdir)
    base_name_file = os.path.basename(subdir_path)
    if os.path.isdir(subdir_path):
        # Generate tier selections and merge TextGrids
        # tiers_trans, other_tiers = generate_tiers_selection(subdir_path)
        # merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file)
        # merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file, merged)
        
        # tiers_trans, other_tiers = generate_tiers_selection_non_gold_silence(subdir_path)
        # merge_textgrid_non_gold_tiers(subdir_path, tiers_trans, other_tiers, base_name_file, merged)

        # print(subdir_path)
        gold_file = os.path.join(base_folder_gold, base_name_file)
        tiers, tiers_combined = generate_tiers_selection_gold_non_gold_silence(subdir_path, gold_file)
        # print(tiers, tiers_combined)
        merge_gold_non_gold(subdir_path, gold_file, tiers, tiers_combined, base_name_file, merged)