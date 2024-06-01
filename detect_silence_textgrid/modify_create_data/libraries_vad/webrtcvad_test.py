import collections
import contextlib
import os
import sys
import wave

import numpy as np
import textgrid
from praatio import tgio
import webrtcvad
from pydub import AudioSegment

LOG_FILE = "processed_files_webrtcvad.log"


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


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset : offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    voiced_frames = []
    segments = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write("1" if is_speech else "0")
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.6 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write("+(%s)" % (ring_buffer[0][0].timestamp,))
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.6 * ring_buffer.maxlen:
                sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
                triggered = False
                segments.append(voiced_frames)
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
    sys.stdout.write("\n")
    if voiced_frames:
        segments.append(voiced_frames)
    return segments


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


def read_processed_files():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as log:
            return set(log.read().splitlines())
    return set()


def log_processed_file(file):
    with open(LOG_FILE, "a") as log:
        log.write(file + "\n")
    print(f"Fichier traité ajouté au fichier de log: {file}")

def rename_intervals(intervals: list) -> list:
    """
    Renommer les intervalles IPU en ipu_1, ipu_2, etc.

    Parameters:
    - intervals (list): liste des intervalles

    Returns:
    - list: liste des nouveaux intervalles

    Variables:
    - new_intervals (list): liste des nouveaux intervalles
    """
    new_intervals = []
    counter = 1
    for interval in intervals:
        start, end, label = interval
        if "#" in label:
            new_intervals.append([start, end, label])
        else:
            new_label = f"ipu_{counter}"
            new_intervals.append([start, end, new_label])
            counter += 1
    return new_intervals

def merge_consecutive_ipus(intervals: list) -> list:
    """
    Fusionne les IPUs consécutifs.

    Parameters:
    - intervals (list): liste des intervalles

    Returns:
    - list: liste des intervalles fusionnés
    """
    merged_intervals = []
    for interval in intervals:
        if not merged_intervals:
            merged_intervals.append(interval)
        else:
            prev_interval = merged_intervals[-1]
            if prev_interval[2].startswith("ipu") and interval[2].startswith("ipu"):
                # Fusionner les IPUs consécutifs
                merged_intervals[-1][1] = interval[1]
            else:
                merged_intervals.append(interval)
    return merged_intervals

def process_file(textgrid_path, wav_path):
    # Initialiser VAD avec la sensibilité la plus élevée
    vad = webrtcvad.Vad(3)

    # Convertir le fichier wav
    converted_wav_path = wav_path.replace(".wav", "_16000Hz.wav")
    convert_wav(wav_path, converted_wav_path)

    # Utiliser VAD pour détecter les segments de parole
    audio, sample_rate = read_wave(converted_wav_path)
    frames = frame_generator(10, audio, sample_rate)  # 10 ms par trame
    segments = vad_collector(sample_rate, 10, 40, vad, list(frames))

    # Convertir les segments détectés en une liste de tuples (début, fin)
    detected_segments = []
    for segment in segments:
        start_time = segment[0].timestamp
        end_time = segment[-1].timestamp + segment[-1].duration
        detected_segments.append((start_time, end_time))

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

    refined_segments = refine_segments(audio, merged_segments, sample_rate)

    print("Segments de parole affinés:", len(refined_segments))

    # Ajouter les segments de silence basés sur les niveaux sonores
    silence_threshold = -40  # Ajuster le seuil en dB pour détecter les silences
    min_silence_duration = 0.10  # Durée minimale des silences en secondes

    silence_segments = []
    for i in range(len(refined_segments) - 1):
        end_current = refined_segments[i][1]
        start_next = refined_segments[i + 1][0]
        if start_next - end_current >= min_silence_duration:
            silence_segments.append((end_current, start_next))
        else:
            refined_segments[i + 1] = (end_current, refined_segments[i + 1][1])

    # Ajouter un segment de silence au début si le premier segment ne commence pas à 0
    if refined_segments and refined_segments[0][0] > 0:
        silence_segments.insert(0, (0, refined_segments[0][0]))

    # Ajouter un segment de silence à la fin si le dernier segment ne se termine pas à la fin du fichier
    if refined_segments and refined_segments[-1][1] < wave.open(converted_wav_path).getnframes() / sample_rate:
        silence_segments.append((refined_segments[-1][1], wave.open(converted_wav_path).getnframes() / sample_rate))

    print("Segments de silence:", len(silence_segments))

    # Renommer les segments IPU
    all_intervals = [(start, end, "ipu") for start, end in refined_segments]
    all_intervals.extend([(start, end, "#") for start, end in silence_segments])
    all_intervals = sorted(all_intervals)

    renamed_intervals = rename_intervals(all_intervals)

    # Fusionner les IPUs consécutifs
    merged_intervals = merge_consecutive_ipus(renamed_intervals)

    intervals = rename_intervals(merged_intervals)

    # Créer un nouveau TextGrid avec les segments détectés
    max_time = wave.open(converted_wav_path).getnframes() / sample_rate
    new_tg = tgio.Textgrid()
    interval_tier = tgio.IntervalTier(
        "IPUs",
        intervals,
        0,
        max_time,
    )
    new_tg.addTier(interval_tier)

    print(refined_segments)
    
    # Sauvegarder le nouveau TextGrid
    new_textgrid_path = textgrid_path.replace(".TextGrid", "-ipus.TextGrid")
    new_tg.save(new_textgrid_path)
    print(f"Nouveau fichier TextGrid sauvegardé: {new_textgrid_path}")

    # Enregistrer le fichier traité dans le fichier de log
    log_processed_file(textgrid_path)


def main():
    # Lire les fichiers déjà traités
    processed_files = read_processed_files()

    base_path = "/Users/perrine/Desktop/Stage_2023-2024/TEXTGRID_WAV_gold_non_gold_TALN_04-05_10ms_webrtcvad/"
    for root, dirs, files in os.walk(base_path):
        files.sort()
        for file in files:
            if file.endswith("_MG.TextGrid"):
                textgrid_path = os.path.join(root, file)
                if textgrid_path in processed_files:
                    print(f"Fichier déjà traité: {file}")
                    continue
                wav_path = textgrid_path.replace("_MG.TextGrid", "_MG.wav")
                if os.path.exists(wav_path):
                    print(f"Traitement du fichier: {textgrid_path} et {wav_path}")
                    try:
                        process_file(textgrid_path, wav_path)
                    except Exception as e:
                        print(f"Erreur lors du traitement du fichier {file}: {e}")


if __name__ == "__main__":
    main()
