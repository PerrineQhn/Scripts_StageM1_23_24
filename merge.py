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


base_folder = './TEXTGRID_WAV'
merged = './MERGED'

for subdir in os.listdir(base_folder):
    subdir_path = os.path.join(base_folder, subdir)
    base_name_file = os.path.basename(subdir_path)
    if os.path.isdir(subdir_path):
        print(subdir_path)
        # Generate tier selections and merge TextGrids
        tiers_trans, other_tiers = generate_tiers_selection(subdir_path)
        #merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file)
        merge_textgrid_tiers(subdir_path, tiers_trans, other_tiers, base_name_file, merged)
