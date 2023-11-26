import re
import os

def extract_text(file_path, output_directory):
    """
    Extracts and saves WAV audio files from data files.

    Args:
        file_path (str): Path of the data files.
        output_directory (str): Output directory for the WAV audio files.

    Return:
        list of str: Paths of the extracted and saved WAV audio files.
    """
    text_files = []  # Create a list to store the paths of the downloaded audio files
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith(".conllu"):
                conllu_file_path = os.path.join(root, file)
                with open(conllu_file_path, 'r', encoding='utf-8') as conllu_file:
                    text_lines = []  # Create a list to store the extracted sentences
                    for line in conllu_file:
                        if line.startswith('# text = '):
                            # Extract the sentence and remove any leading/trailing whitespace
                            sentence = line[len('# text = '):].strip()
                            text_lines.append(sentence)
                    if text_lines:
                        # Create a text file with the same name as the CoNLL-U file
                        output_file_path = os.path.join(output_directory, os.path.splitext(file)[0] + '.txt')
                        with open(output_file_path, 'w', encoding='utf-8') as output_file:
                            output_file.write('\n'.join(text_lines))
                            text_files.append(output_file_path)
    return text_files


directory_path = "../SUD_Naija-NSC-master/non_gold/"
output_txt = "../TXT/non_gold/"

extract_text(directory_path, output_txt)