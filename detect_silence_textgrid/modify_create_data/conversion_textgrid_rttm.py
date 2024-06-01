import os
from textgrid import TextGrid
from pyannote.core import Segment, Annotation

def textgrid_to_rttm(textgrid_file, rttm_file):
    tg = TextGrid.fromFile(textgrid_file)
    annotation = Annotation()

    # Parcourir uniquement le tier "trans"
    for tier in tg:
        if tier.name == "trans":
            for interval in tier:
                start = interval.minTime
                end = interval.maxTime
                label = interval.mark.strip()
            
                if label.lower() == '#':
                    speaker = 'non-speech'
                elif label.lower() != '#':
                    speaker = 'speech'
                else:
                    continue
                
                segment = Segment(start, end)
                annotation[segment] = speaker

    with open(rttm_file, 'w') as f:
        for segment, track, label in annotation.itertracks(yield_label=True):
            f.write(f"SPEAKER {os.path.basename(textgrid_file).split('.')[0]} 1 {segment.start:.3f} "
                    f"{segment.duration:.3f} <NA> <NA> {label} <NA> <NA>\n")

# Dossier contenant les fichiers TextGrid
base_path = "../../../TEXTGRID_WAV/"
# Dossier pour enregistrer les fichiers RTTM
rttm_folder = "../../../WAV_Gold/"

if not os.path.exists(rttm_folder):
    os.makedirs(rttm_folder)

# Conversion des fichiers TextGrid en fichiers RTTM
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith("_MG.TextGrid"):
            textgrid_path = os.path.join(root, file)
            rttm_file = os.path.join(rttm_folder, file.replace(".TextGrid", ".rttm"))
            textgrid_to_rttm(textgrid_path, rttm_file)

print("Conversion terminée.")
