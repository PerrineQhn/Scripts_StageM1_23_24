import os
from textgrid import TextGrid, IntervalTier


def trans_to_speech_non_speech(textgrid_input, textgrid_output):
    tg = TextGrid.fromFile(textgrid_input)

    speech_non_speech_intervals = []

    # Parcourir uniquement le tier "trans"
    for tier in tg:
        if tier.name == "trans":
            for interval in tier:
                start = interval.minTime
                end = interval.maxTime
                label = interval.mark.strip()
            
                if label.lower() == '#':
                    speech_non_speech_intervals.append([start, end, 0])
                elif label.lower() != '#':
                    speech_non_speech_intervals.append([start, end, 1])

    tg_out = TextGrid()
    speech_non_speech_tier = IntervalTier(name="silence", minTime=0, maxTime=tg.maxTime)

    for start, end, label in speech_non_speech_intervals:
        speech_non_speech_tier.add(start, end, str(label))

    tg_out.append(speech_non_speech_tier)
    tg_out.write(textgrid_output)

# Dossier contenant les fichiers TextGrid
base_path = "/Users/perrine/Desktop/Stage_2023-2024/TEXTGRID_WAV"

# Conversion des fichiers TextGrid en fichiers RTTM
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith("_MG.TextGrid"):
            print("Création du fichier speech_non_speech pour le fichier", file)
            textgrid_input = os.path.join(root, file)
            textgrid_output = os.path.join(root, file.replace(".TextGrid", "_speech_non_speech.TextGrid"))
            trans_to_speech_non_speech(textgrid_input, textgrid_output)



print("Création terminée.")