import os
import re
import urllib.request
from conll3 import *
import ssl
import warnings
import requests
from pydub import AudioSegment
import requests.packages.urllib3.exceptions as urllib3_exceptions

warnings.simplefilter("ignore", urllib3_exceptions.InsecureRequestWarning)

# Define the TLSAdapter class
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= 0x4
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def convert_to_mono(input_file, output_file):
    # Charger le fichier WAV d'entrée
    sound = AudioSegment.from_wav(input_file)
    
    # Convertir le fichier en mono (1 canal)
    mono_sound = sound.set_channels(1)
    
    # Sauvegarder le fichier WAV en mono
    mono_sound.export(output_file, format="wav")
    
def extract_and_save_wav(file_path, output_directory):
    """
    Extracts and saves WAV audio files from data files.

    Args:
        file_path (str): Path of the data files.
        output_directory (str): Output directory for the WAV audio files.

    Return:
        list of str: Paths of the extracted and saved WAV audio files.
    """
    wav_paths = []  # Create a list to store the paths of the downloaded audio files
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith(".conllu"):
                conllu_file_path = os.path.join(root, file)
                print(conllu_file_path)
                trees = conllFile2trees(conllu_file_path)
                for tree in trees:
                    tree_str = str(tree)
                    sound_url_match = re.search(r'# sound_url = (.+)', tree_str)  # Recherche de l'URL du fichier audio
                    if sound_url_match:
                        sound_url = sound_url_match.group(1)
                        print(sound_url)
                        if sound_url.endswith('.wav'):
                            file_name = os.path.basename(conllu_file_path)
                            file_name_without_ext = os.path.splitext(file_name)[0]
                            output_file_name = f"{file_name_without_ext}.wav"
                            if output_directory is not None:
                                output_path = os.path.join(output_directory, output_file_name)
                                with requests.session() as s:
                                    s.mount("https://", TLSAdapter())
                                    response = s.get(sound_url)
                                    with open(output_path, "wb") as f_out:
                                        f_out.write(response.content)
                                wav_paths.append(output_path)  # Append the path to the list
                                break
                        elif sound_url.endswith('.mp3'):
                            file_name = os.path.basename(conllu_file_path)
                            file_name_without_ext = os.path.splitext(file_name)[0]
                            mp3_output_path = os.path.join(output_directory, f"{file_name_without_ext}.mp3")
                            with requests.session() as s:
                                s.mount("https://", TLSAdapter())
                                response = s.get(sound_url)
                                with open(mp3_output_path, "wb") as f_out:
                                    f_out.write(response.content)
                            # Convert MP3 to WAV
                            mp3_audio = AudioSegment.from_mp3(mp3_output_path)
                            wav_output_path = os.path.join(output_directory, f"double_{file_name_without_ext}.wav")
                            mp3_audio.export(wav_output_path, format="wav")
                            
                            # Convertir le fichier WAV en mono (1 canal)
                            mono_sound = AudioSegment.from_wav(wav_output_path).set_channels(1)
                            mono_wav_output_path = os.path.join(output_directory, f"{file_name_without_ext}.wav")
                            mono_sound.export(mono_wav_output_path, format="wav")
                            
                            # Supprimer le fichier WAV original
                            os.remove(wav_output_path)
                            # Supprimer le fichier MP3 original
                            os.remove(mp3_output_path)
                            
                            wav_paths.append(mono_wav_output_path)
                            break  # Exit the inner loop to move to the next file

    return wav_paths

directory_path = "../SUD_Naija-NSC-master/"
output_wav = "../WAV/"

extract_and_save_wav(directory_path, output_wav)
