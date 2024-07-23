import os
import shutil

# Dossiers source
# textgrid_folder = "../TEXTGRID"
# wav_folder = "../WAV"
textgrid_folder = "./TEXTGRID_nongold/non_gold/"
wav_folder = "./WAV_nongold/non_gold/"

# Dossier de destination
# destination_folder_base = "../TEXTGRID_WAV"
destination_folder_base = "./TEXTGRID_WAV_nongold"

# Obtenez tous les noms de fichiers .TextGrid et .wav
textgrid_files = {f for f in os.listdir(textgrid_folder) if f.endswith(".TextGrid")}
wav_files = {f for f in os.listdir(wav_folder) if f.endswith(".wav")}
print(wav_files)
# Parcourez tous les fichiers .TextGrid
for tg_file in textgrid_files:
    print(tg_file)
    base_name = tg_file.split("_")
    
    # Utilisez les premières parties du nom pour déterminer le dossier de destination
    if len(base_name) >= 3:
        #print(base_name)
        destination_subfolder = f"{destination_folder_base}/{'_'.join(base_name[:2])}"
        os.makedirs(destination_subfolder, exist_ok=True)

        #wav_file = f"{'_'.join(base_name[:-1])}_MG.wav"
        wav_file = f"{'_'.join(base_name[:-1])}_M.wav"
        print(wav_file)

        if wav_file in wav_files:
            # Déplacez les fichiers correspondants dans le sous-dossier
            shutil.move(os.path.join(textgrid_folder, tg_file), os.path.join(destination_subfolder, tg_file))
            shutil.move(os.path.join(wav_folder, wav_file), os.path.join(destination_subfolder, wav_file))
