from praatio import tgio
import textgrid
import os
import csv

def compare_silence(file_path):
    # Extract the base name of the file for output purposes
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Open the TextGrid file
    textgrid_sil = tgio.openTextgrid(file_path)
    
    # Lists to store silence intervals and durations
    combined_silences = []
    tokensalign_silences = []
    overlaps = []
    
    # Variables to store total silence duration
    total_combined_silence_duration = 0
    total_tokensalign_silence_duration = 0
    
    # Process the 'Combined' tier
    for interval in textgrid_sil.tierDict['Combined'].entryList:
        if "#" in interval[2]:
            xmin = interval[0]
            xmax = interval[1]
            combined_silences.append((xmin, xmax))
            total_combined_silence_duration += xmax - xmin
    
    # Process the 'TokensAlign' tier
    for interval in textgrid_sil.tierDict['TokensAlign'].entryList:
        if "#" in interval[2]:
            xmin = interval[0]
            xmax = interval[1]
            tokensalign_silences.append((xmin, xmax))
            total_tokensalign_silence_duration += xmax - xmin
    
    # Compare silences between 'Combined' and 'TokensAlign'
    for c_sil in combined_silences:
        c_start, c_end = c_sil
        for t_sil in tokensalign_silences:
            t_start, t_end = t_sil
            if (c_start >= t_start and c_end <= t_end) or (t_start >= c_start and t_end <= c_end):
                overlaps.append((c_start, c_end, t_start, t_end))

    return {
        "base_name": base_name,
        "combined_silences": len(combined_silences),
        "tokensalign_silences": len(tokensalign_silences),
        "overlaps": overlaps,
        "more_silence_in_combined": total_combined_silence_duration > total_tokensalign_silence_duration
    }

# Directory where your TextGrid files are located
folder_path = "MERGED/gold_non_gold"

# Prepare to collect all results
all_results = []

# Collect data for each TextGrid file in the folder
for file in os.listdir(folder_path):
    if file.endswith(".TextGrid"):
        file_path = os.path.join(folder_path, file)
        result = compare_silence(file_path)
        all_results.append(result)

# Sort results by file name
all_results.sort(key=lambda x: x["base_name"])

# TSV file to save the sorted results
tsv_file_path = "TSV/combined-tokensalign_silences_TALN.tsv"

with open(tsv_file_path, 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['File Name', 'Combined Silences', 'TokensAlign Silences', 'Overlapping Silences', 'More Silence in Combined'])
    # writer.writerow(['', 'Start Time', 'End Time', 'TokensAlign Start Time', 'TokensAlign End Time'])

    more_combined_silence_count = 0
    for result in all_results:
        writer.writerow([result["base_name"], result["combined_silences"], result["tokensalign_silences"], len(result["overlaps"]), result["more_silence_in_combined"]])
        # for overlap in result["overlaps"]:
        #     writer.writerow(['Overlap', overlap[0], overlap[1], overlap[2], overlap[3]])
        if result["more_silence_in_combined"]:
            more_combined_silence_count += 1

    writer.writerow(['Total files with more silence in Combined:', '', '', '', more_combined_silence_count])

print(f"Results saved to {tsv_file_path}")
