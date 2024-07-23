import csv
import os
import re
from hertz_to_semitone import *

# Path to the existing TSV file
existing_tsv_path = "TSV/align_begin_align_end_syl_29_01.tsv"

# Path to the directory containing the TXT files
txt_folder_path = "pitchtier_18janv/txt_syll/"

# Path to the new TSV file with the additional columns
new_tsv_path = "TSV/align_begin_align_end_syl_29_01_hertz.tsv"

# # Read the existing TSV file
# data = []
# with open(existing_tsv_path, "r", newline="") as tsv_file:
#     reader = csv.DictReader(tsv_file, delimiter="\t")
#     for row in reader:
#         data.append(row)

# # Iterate over the data and add the moyenne_t1 and moyenne_t2 values
# for row in data:
#     sent_id = row["Sent_ID"]
#     token_id = row["ID"]
#     txt_file_path = os.path.join(txt_folder_path, f"{sent_id}_{token_id}.txt")
#     # print(txt_file_path)

#     # Read the values from the corresponding TXT file
#     with open(txt_file_path, "r") as txt_file:
#         txt_content = txt_file.read()

#     # Initialize lists for syllable values
#     moyenne_syl_values = []

#     # Parse the values from the TXT content
#     for i in range(1, 9):
#         moyenne_syl_match = re.findall(r"moyenne_syl{} = (\d+(?:\.\d+)?)".format(i), txt_content)
#         if moyenne_syl_match:
#            moyenne_syl_values.append(float(moyenne_syl_match[0]))
#         # print(moyenne_syl_values)

#     moyenne_sent_match = re.findall(r"moyenne_sent = (\d+(?:\.\d+)?)", txt_content)
#     moyenne_sent = float(moyenne_sent_match[0]) if moyenne_sent_match else 0.0

#     # Add rows
#     for i in range(1, 9):
#         # print(len(moyenne_syl_values))
#         if len(moyenne_syl_values) >= i:
#             moyenne_syl = moyenne_syl_values[i-1]
#             print(moyenne_syl)
#             row[f"Moyenne_Syl{i}_Hertz"] = moyenne_syl
#             row[f"MoyenneSyl{i}Semitones"] = semitones_between(moyenne_syl, moyenne_sent)
#         else:
#             row[f"Moyenne_Syl{i}_Hertz"] = 0
#             row[f"MoyenneSyl{i}Semitones"] = 0
#     row["Moyenne_Sent_Hertz"] = moyenne_sent

# # Write the updated data to the new TSV file
# fieldnames = data[0].keys() if data else []
# with open(new_tsv_path, "w", newline="") as new_tsv_file:
#     writer = csv.DictWriter(new_tsv_file, delimiter="\t", fieldnames=fieldnames)
#     writer.writeheader()
#     writer.writerows(data)

def update_tsv_with_pitch_data(existing_tsv_path, txt_folder_path, new_tsv_path):
    """
    Reads data from an existing TSV file, processes it by reading corresponding TXT files,
    calculates additional values, and writes the updated data to a new TSV file.

    Parameters:
    existing_tsv_path (str): Path to the existing TSV file.
    txt_folder_path (str): Path to the directory containing TXT files.
    new_tsv_path (str): Path to the new TSV file with additional columns.

    Returns:
    None
    """

    # Read the existing TSV file
    data = []
    try:
        with open(existing_tsv_path, "r", newline="") as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter="\t")
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"Error reading TSV file: {e}")
        return

    # Iterate over the data and add the moyenne_t1 and moyenne_t2 values
    for row in data:
        sent_id = row["Sent_ID"]
        token_id = row["ID"]
        txt_file_path = os.path.join(txt_folder_path, f"{sent_id}_{token_id}.txt")

        # Read the values from the corresponding TXT file
        try:
            with open(txt_file_path, "r") as txt_file:
                txt_content = txt_file.read()
        except Exception as e:
            print(f"Error reading TXT file {txt_file_path}: {e}")
            continue

        # Initialize lists for syllable values
        moyenne_syl_values = []

        # Parse the values from the TXT content
        for i in range(1, 9):
            moyenne_syl_match = re.findall(r"moyenne_syl{} = (\d+(?:\.\d+)?)".format(i), txt_content)
            if moyenne_syl_match:
                moyenne_syl_values.append(float(moyenne_syl_match[0]))

        moyenne_sent_match = re.findall(r"moyenne_sent = (\d+(?:\.\d+)?)", txt_content)
        moyenne_sent = float(moyenne_sent_match[0]) if moyenne_sent_match else 0.0

        # Add rows
        for i in range(1, 9):
            if len(moyenne_syl_values) >= i:
                moyenne_syl = moyenne_syl_values[i-1]
                row[f"Moyenne_Syl{i}_Hertz"] = moyenne_syl
                row[f"MoyenneSyl{i}Semitones"] = semitones_between(moyenne_syl, moyenne_sent)
            else:
                row[f"Moyenne_Syl{i}_Hertz"] = 0
                row[f"MoyenneSyl{i}Semitones"] = 0
        row["Moyenne_Sent_Hertz"] = moyenne_sent

    # Write the updated data to the new TSV file
    try:
        fieldnames = data[0].keys() if data else []
        with open(new_tsv_path, "w", newline="") as new_tsv_file:
            writer = csv.DictWriter(new_tsv_file, delimiter="\t", fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        print(f"Error writing to TSV file: {e}")
        return

    print("TSV file has been successfully updated.")

# Exemple d'utilisation
update_tsv_with_pitch_data(existing_tsv_path, txt_folder_path, new_tsv_path)