import parselmouth
import numpy as np
import pandas as pd
import os
import glob
from tqdm import tqdm

def is_floatable(value):
    """ Vérifie si la valeur peut être convertie en flottant. """
    try:
        float(value)
        return True
    except ValueError:
        return False

def calculate_amplitudes(audio_file, start_time, end_time):
    """ Calcule l'amplitude maximale et moyenne d'un segment audio. """
    try:
        duration = end_time - start_time
        sound = parselmouth.Sound(audio_file)
        segment = sound.extract_part(from_time=start_time, to_time=end_time)
        amplitudes = segment.to_intensity().values.T
        # print(amplitudes)
        # print("Max:", np.max(amplitudes))
        # print("Mean:", np.mean(amplitudes))
        return np.max(amplitudes), np.mean(amplitudes)
        
    except Exception as e:
        return 0, 0

# Charger le fichier TSV
tsv_file_path = '../TSV/align_begin_align_end_syl.tsv'
tsv_data = pd.read_csv(tsv_file_path, sep='\t')
tsv_data.columns = [col.strip() for col in tsv_data.columns]

# Ajouter des colonnes pour les amplitudes
for syl_num in range(1, 9):
    tsv_data[f'Syl{syl_num}AvgAmplitude'] = np.nan
    tsv_data[f'Syl{syl_num}MaxAmplitude'] = np.nan

# Chemin de base pour les fichiers audio
audio_base_path = '../TEXTGRID_WAV/'

# Itération sur les lignes du TSV
for index, row in tqdm(tsv_data.iterrows(), desc="Processing form", total=len(tsv_data)):
    file_base = '_'.join(row['File'].split('_')[:2])
    if row['File'].startswith('ABJ'):
        file_base = '_'.join(row['File'].split('_')[:3])

    folder_paths = glob.glob(os.path.join(audio_base_path, file_base + '*'))
    if folder_paths:
        folder_path = folder_paths[0]
        audio_file_paths = glob.glob(os.path.join(folder_path, '*.wav'))
        if audio_file_paths:
            audio_file_path = audio_file_paths[0]

            for syl_num in range(1, 9):
                start_col_name = f'T1_Syl{syl_num}AlignBegin'
                end_col_name = f'T1_Syl{syl_num}AlignEnd'
                if is_floatable(row[start_col_name]) and is_floatable(row[end_col_name]):
                    start_time = float(row[start_col_name]) / 1000
                    end_time = float(row[end_col_name]) / 1000
                    max_amp, avg_amp = calculate_amplitudes(audio_file_path, start_time, end_time)
                else:
                    max_amp, avg_amp = 0, 0
                    
                tsv_data.loc[index, f'Syl{syl_num}AvgAmplitude'] = avg_amp
                tsv_data.loc[index, f'Syl{syl_num}MaxAmplitude'] = max_amp
                    

# Sauvegarder le DataFrame modifié
output_path = '../TSV/align_begin_align_end_syl_dB.tsv'
tsv_data.to_csv(output_path, sep='\t', index=False)
