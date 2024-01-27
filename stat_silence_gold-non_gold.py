from praatio import tgio
import os
import csv


def compare_silence(file_path, global_writer):
    textgrid_sil = tgio.openTextgrid(file_path)
    
    combined_silences = [(interval[0], interval[1]) for interval in textgrid_sil.tierDict['Combined'].entryList if "#" in interval[2]]
    tokensalign_silences = [(interval[0], interval[1]) for interval in textgrid_sil.tierDict['TokensAlign'].entryList if "#" in interval[2]]

    def check_overlap(interval1, interval2):
        return max(interval1[0], interval2[0]) < min(interval1[1], interval2[1])

    exact_matches, partial_overlaps, unique_combined, unique_tokensalign = [], [], [], []

    for c_sil in combined_silences:
        for t_sil in tokensalign_silences:
            if c_sil == t_sil:
                exact_matches.append(c_sil)
            elif check_overlap(c_sil, t_sil):
                partial_overlaps.append((c_sil, t_sil))

    unique_combined = [c_sil for c_sil in combined_silences if c_sil not in exact_matches and not any(check_overlap(c_sil, t_sil) for t_sil in tokensalign_silences)]
    unique_tokensalign = [t_sil for t_sil in tokensalign_silences if t_sil not in exact_matches and not any(check_overlap(t_sil, c_sil) for c_sil in combined_silences)]

    # Write individual file details
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    individual_tsv_path = os.path.join("TSV/silence_details_TALN", base_name + "_details.tsv")
    with open(individual_tsv_path, 'w', newline='') as file:
        individual_writer = csv.writer(file, delimiter='\t')
        individual_writer.writerow(['Category', 'Start Time', 'End Time'])
        # Write each category
        for match in exact_matches:
            individual_writer.writerow(['Exact Match', match[0], match[1]])
        for overlap in partial_overlaps:
            individual_writer.writerow(['Partial Overlap', overlap[0][0], overlap[0][1]])
        for unique in unique_combined:
            individual_writer.writerow(['Unique in Combined', unique[0], unique[1]])
        for unique in unique_tokensalign:
            individual_writer.writerow(['Unique in TokensAlign', unique[0], unique[1]])

    # Add to global data
    global_writer.writerow([base_name, len(combined_silences), len(tokensalign_silences), len(exact_matches), len(partial_overlaps), len(unique_combined), len(unique_tokensalign)])

# Main processing
folder_path = "MERGED/gold_non_gold"
tsv_file_path = "TSV/combined-tokensalign_silences_TALN.tsv"

# Prepare global TSV writer
with open(tsv_file_path, 'w', newline='') as global_file:
    global_writer = csv.writer(global_file, delimiter='\t')
    global_writer.writerow(['File Name', 'Combined Silences', 'TokensAlign Silences', 'Exact Matches', 'Partial Overlaps', 'Unique Combined', 'Unique TokensAlign'])

    # Process each TextGrid file
    for file in os.listdir(folder_path):
        if file.endswith(".TextGrid"):
            file_path = os.path.join(folder_path, file)
            compare_silence(file_path, global_writer)

print(f"Global results saved to {tsv_file_path}")
