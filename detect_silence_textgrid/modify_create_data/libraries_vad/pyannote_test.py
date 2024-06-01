import contextlib
import os
import wave

import numpy as np
import textgrid
from pyannote.audio import Model
from pyannote.audio.pipelines import VoiceActivityDetection
from pydub import AudioSegment


# Fonction pour convertir le fichier wav à un taux d'échantillonnage de 16000 Hz
def convert_wav(input_path: str, output_path: str, target_sample_rate=16000):
    audio = AudioSegment.from_wav(input_path)
    audio = audio.set_frame_rate(target_sample_rate)
    audio = audio.set_channels(1)
    audio.export(output_path, format="wav")


# Lire le fichier wav converti
def read_wave(path: str):
    with contextlib.closing(wave.open(path, "rb")) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1, "Le fichier doit être mono"
        sample_width = wf.getsampwidth()
        assert sample_width == 2, "La largeur d'échantillon doit être de 2 octets"
        sample_rate = wf.getframerate()
        assert sample_rate in (
            8000,
            16000,
            32000,
            48000,
        ), f"Taux d'échantillonnage non supporté: {sample_rate}"
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


# Affiner les segments basés sur l'amplitude
def refine_segments(audio, segments, sample_rate, threshold_ratio=0.4):
    refined_segments = []
    audio_data = np.frombuffer(audio, dtype=np.int16)
    global_threshold = (
        np.mean(np.abs(audio_data)) * threshold_ratio
    )  # Calcul d'un seuil global basé sur l'amplitude moyenne

    for start, end in segments:
        segment_audio = audio_data[int(start * sample_rate) : int(end * sample_rate)]
        local_threshold = (
            np.mean(np.abs(segment_audio)) * threshold_ratio
        )  # Seuil local basé sur le segment
        non_silent = np.where(
            np.abs(segment_audio) > min(global_threshold, local_threshold)
        )[0]

        if len(non_silent) > 0:
            refined_start = start + non_silent[0] / sample_rate
            refined_end = start + non_silent[-1] / sample_rate
            refined_segments.append((refined_start, refined_end))

    return refined_segments


def process_file(textgrid_path, wav_path, access_token):
    # Convertir le fichier wav
    converted_wav_path = wav_path.replace(".wav", "_16000Hz.wav")
    convert_wav(wav_path, converted_wav_path)

    # Utiliser pyannote.audio pour détecter les segments de parole
    model = Model.from_pretrained("pyannote/segmentation-3.0", use_auth_token=access_token)

    pipeline = VoiceActivityDetection(segmentation=model)
    HYPER_PARAMETERS = {
        "min_duration_on": 0,
        "min_duration_off": 0,
    }

    pipeline.instantiate(HYPER_PARAMETERS)
    vad = pipeline(converted_wav_path)

    for turn, _, speaker in vad.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

    # Convertir les segments détectés en une liste de tuples (début, fin)
    detected_segments = [
        (turn.start, turn.end) for turn, _, speaker in vad.itertracks(yield_label=True)
    ]

    # Fusionner les segments chevauchants ou adjacents
    merged_segments = []
    for start, end in detected_segments:
        if not merged_segments:
            merged_segments.append([start, end])
        else:
            prev_start, prev_end = merged_segments[-1]
            if start <= prev_end:  # Fusionner les segments chevauchants ou adjacents
                merged_segments[-1][1] = max(prev_end, end)
            else:
                merged_segments.append([start, end])

    print("Segments de parole détectés:", len(merged_segments))

    refined_segments = refine_segments(
        read_wave(converted_wav_path)[0], merged_segments, 16000
    )

    print("Segments de parole affinés:", len(refined_segments))

    # Ajouter les segments de silence basés sur les niveaux sonores
    silence_threshold = -40  # Ajuster le seuil en dB pour détecter les silences
    min_silence_duration = 0.05  # Durée minimale des silences en secondes

    silence_segments = []
    for i in range(len(refined_segments) - 1):
        end_current = refined_segments[i][1]
        start_next = refined_segments[i + 1][0]
        if start_next - end_current >= min_silence_duration:
            segment = AudioSegment.from_wav(converted_wav_path)[
                int(end_current * 1000) : int(start_next * 1000)
            ]
            if segment.dBFS < silence_threshold:
                silence_segments.append((end_current, start_next))

    # Ajouter un segment de silence au début si le premier segment ne commence pas à 0
    if refined_segments and refined_segments[0][0] > 0:
        silence_segments.insert(0, (0, refined_segments[0][0]))

    # Ajouter un segment de silence à la fin si le dernier segment ne se termine pas à la fin du fichier
    with contextlib.closing(wave.open(converted_wav_path, "rb")) as wf:
        file_duration = wf.getnframes() / wf.getframerate()
    if refined_segments and refined_segments[-1][1] < file_duration:
        silence_segments.append((refined_segments[-1][1], file_duration))

    print("Segments de silence:", len(silence_segments))

    # Créer un nouveau TextGrid avec les segments détectés
    new_tg = textgrid.TextGrid()
    interval_tier = textgrid.IntervalTier(
        name="IPUs",
        minTime=0,
        maxTime=file_duration,
    )
    new_tg.append(interval_tier)

    # Ajouter les segments de parole détectés au TextGrid
    for i, (start, end) in enumerate(refined_segments):
        if start < end:  # Vérifier que la durée est positive
            interval_tier.add(start, end, f"IPU_{i}")

    # Ajouter les segments de silence détectés au TextGrid
    for start, end in silence_segments:
        if start < end:  # Vérifier que la durée est positive
            interval_tier.add(start, end, "#")

    # Sauvegarder le nouveau TextGrid
    new_textgrid_path = textgrid_path.replace(
        ".TextGrid", "_detected_pyannote.TextGrid"
    )
    new_tg.write(new_textgrid_path)
    print(f"Nouveau fichier TextGrid sauvegardé: {new_textgrid_path}")


# Parcourir les sous-dossiers dans TEXTGRID_WAV et traiter les fichiers
base_path = "../../../../TEXTGRID_WAV_gold_non_gold_TALN"
access_token = "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"  # Remplacer par le jeton d'accès Hugging Face
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith("WAZP_07_Imonirhua-Lifestory_MG.TextGrid"):
            textgrid_path = os.path.join(root, file)
            wav_path = textgrid_path.replace("_MG.TextGrid", "_MG.wav")
            if os.path.exists(wav_path):
                print(f"Traitement du fichier: {textgrid_path} et {wav_path}")
                process_file(textgrid_path, wav_path, access_token)
