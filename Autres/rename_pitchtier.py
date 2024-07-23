import os
import shutil

source_folder = "/Users/perrine/Desktop/Stage_2023-2024/Praat/"
destination_folder = "/Users/perrine/Desktop/Stage_2023-2024/SLAMplus/data"

# Assurez-vous que le dossier de destination existe
os.makedirs(destination_folder, exist_ok=True)

for filename in os.listdir(source_folder):
    if filename.endswith(".PitchTier"):
        if filename.startswith("ABJ"):
            new_file_name = "_".join(filename.split("_")[:3]) + ".PitchTier"
        else:
            new_file_name = "_".join(filename.split("_")[:2]) + ".PitchTier"
        
        # Construct the full file paths
        old_file_path = os.path.join(source_folder, filename)
        new_file_path = os.path.join(destination_folder, new_file_name)
        
        # Copy the file to the new destination
        shutil.copy(old_file_path, new_file_path)
        print(f"Copied and renamed {old_file_path} to {new_file_path}")
