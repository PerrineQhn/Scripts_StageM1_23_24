import math
import os
import re
import glob
from conll3 import conllFile2trees, trees2conllFile

def dico2FeatureString(dico):
    """Transforms a dictionary of Conll features into a string with MeanF0Step just after MeanF0"""
    features = []
    keys = list(dico.keys())
    for i, key in enumerate(keys):
        if not isinstance(dico[key], dict):
            features.append(f"{key}={dico[key]}")
            if key.endswith("MeanF0"):
                step_key = key.replace("MeanF0", "MeanF0Step")
                if step_key in dico:
                    features.append(f"{step_key}={dico[step_key]}")
    return "|".join(features)

def build_feature_dico(misc_features_string):
    """Turns a string of CONLL features into a callable dictionary"""
    feature_dico = {}
    for feature in misc_features_string.split("|"):
        if "=" in feature:
            key, value = feature.split("=", 1)  # Split only on the first '='
            feature_dico[key] = value
    return feature_dico

def extract_trees_and_metadata(file_path: str) -> tuple:
    """Extracts trees and their metadata from a CoNLL file."""
    trees = conllFile2trees(file_path)
    file_name = os.path.basename(file_path)

    metadata = []
    for tree in trees:
        tree_str = str(tree)
        sent_id_match = re.search(r"# sent_id = (.+)", tree_str)
        sent_id = sent_id_match.group(1) if sent_id_match else "_"
        words = [{"t": tree[token]["t"], "tag": tree[token]["tag"]} for token in tree]  # Properly extract words as dicts
        metadata.append((tree, sent_id, words))

    return trees, file_name, metadata

def frequency_from_semitones(frequency: float, semitones: float) -> float:
    """Calculates the frequency in Hertz a given number of semitones above a base frequency."""
    return frequency * (2 ** (semitones / 12))

def add_meanf0step_to_dico(feature_dico):
    """Adds MeanF0Step to the feature dictionary if MeanF0 exists."""
    keys_to_update = [key for key in feature_dico if key.endswith("MeanF0")]
    for key in keys_to_update:
        if feature_dico[key] == "X":
            step_key = key.replace("MeanF0", "MeanF0Step")
            feature_dico[step_key] = "X"
        else:
            try:
                mean_f0 = float(feature_dico[key])
                if mean_f0 > 0:
                    mean_f0_step = round(frequency_from_semitones(mean_f0, 2), 3)
                    step_key = key.replace("MeanF0", "MeanF0Step")
                    feature_dico[step_key] = mean_f0_step
            except ValueError:
                continue
    return feature_dico

def modify_metadata(tree, sent_id, words):
    """Modifies metadata to include sentence_type before text"""
    sentence_type = None

    if words and words[-1]['tag'] == 'PUNCT':
        sentence_type = words[-1]['t']

    metadata_lines = []

    for line in str(tree).split("\n"):
        if line and sentence_type:
            metadata_lines.append(f"# sent_type = {sentence_type}")
        metadata_lines.append(line)

    tree.sentencefeatures = {}
    for line in metadata_lines:
        if line.startswith("#"):
            key, value = line[1:].split("=", 1)
            tree.sentencefeatures[key.strip()] = value.strip()


CONLL_DIR = glob.glob("CONLL_files/gold/*.conllu")
OUTPUT_DIR = "CONLL_outfiles/gold/"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def main(conllu_files: list, output_dir: str = OUTPUT_DIR):
    for infile in conllu_files:
        basename = os.path.basename(infile)[:-9]
        trees, _, metadata = extract_trees_and_metadata(infile)
        for treei, (tree, sent_id, words) in enumerate(metadata):
            modify_metadata(tree, sent_id, words)
            
            
            for tok in tree:
                token_data = tree[tok]
                feature_dico = build_feature_dico(token_data["misc"])

                # Check if token is #
                if token_data['t'] == "#":
                    if 'AlignBegin' in feature_dico and 'AlignEnd' in feature_dico:
                        # print("Found AlignBegin and AlignEnd in #")
                        align_begin = int(feature_dico['AlignBegin'])
                        align_end = int(feature_dico['AlignEnd'])
                        feature_dico['Syl1AlignBegin'] = align_begin
                        feature_dico['Syl1AlignEnd'] = align_end
                        feature_dico['Syl1Duration'] = align_end - align_begin

                # Ajout de MeanF0Step au dictionnaire des caractéristiques
                feature_dico = add_meanf0step_to_dico(feature_dico)

                feature_string = dico2FeatureString(feature_dico)
                token_data["misc"] = feature_string

        output_file = os.path.join(output_dir, os.path.basename(infile))
        trees2conllFile(trees, output_file)

main(CONLL_DIR)
