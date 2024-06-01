import os
import shutil
import random

# Définir les chemins des dossiers
audio_dir = '../../../WAV_Gold/audio'
rttm_dir = '../../../WAV_Gold/rttm'
output_dir = '../../../WAV_Gold/sortie'

# Créer les dossiers de sortie s'ils n'existent pas
for subset in ['train', 'test', 'dev']:
    os.makedirs(os.path.join(output_dir, subset, 'audio'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, subset, 'rttm'), exist_ok=True)

# Lister les fichiers audio et RTTM
audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
rttm_files = [f for f in os.listdir(rttm_dir) if f.endswith('.rttm')]

# Vérifier que chaque fichier audio a un fichier RTTM correspondant
audio_basename = set(os.path.splitext(f)[0] for f in audio_files)
rttm_basename = set(os.path.splitext(f)[0] for f in rttm_files)
common_files = list(audio_basename.intersection(rttm_basename))

# Mélanger les fichiers pour la répartition aléatoire
random.shuffle(common_files)

# Définir les proportions des ensembles
train_ratio = 0.8
dev_ratio = 0.1
test_ratio = 0.1

# Calculer les tailles des ensembles
num_files = len(common_files)
num_train = int(train_ratio * num_files)
num_dev = int(dev_ratio * num_files)
num_test = num_files - num_train - num_dev

# Diviser les fichiers
train_files = common_files[:num_train]
dev_files = common_files[num_train:num_train + num_dev]
test_files = common_files[num_train + num_dev:]

# Fonction pour copier les fichiers
def copy_files(file_list, subset):
    for file_base in file_list:
        audio_src = os.path.join(audio_dir, file_base + '.wav')
        rttm_src = os.path.join(rttm_dir, file_base + '.rttm')
        audio_dst = os.path.join(output_dir, subset, 'audio', file_base + '.wav')
        rttm_dst = os.path.join(output_dir, subset, 'rttm', file_base + '.rttm')
        shutil.copy(audio_src, audio_dst)
        shutil.copy(rttm_src, rttm_dst)

# Copier les fichiers dans les dossiers respectifs
copy_files(train_files, 'train')
copy_files(dev_files, 'dev')
copy_files(test_files, 'test')

print("Fichiers divisés en ensembles d'entraînement, de développement et de test.")
