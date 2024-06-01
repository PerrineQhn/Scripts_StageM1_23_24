
from pyannote.database import registry, FileFinder
from pyannote.audio.tasks import VoiceActivityDetection
from pyannote.audio.models.segmentation import PyanNet


# Remplacer par le chemin vers votre fichier de configuration
config_file = "../../WAV_Gold/config.yml"
registry.load_database(config_file)

preprocessors = {"audio": FileFinder()}

training = registry.get_protocol("SpeakerDiarization", preprocessors=preprocessors).as_dict()["train"]

first_training_file = next(iter(training.values()))
reference = first_training_file["annotation"]


vad = VoiceActivityDetection(training, duration=2., batch_size=128)
model = PyanNet(sincnet={'stride': 10}, task=vad)
