import os
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

class TTSModel:
    def __init__(self):
        self.config = XttsConfig()
        self.model = None
        self.load_model()

    def load_model(self):
        # Init TTS with the target model name
        self.config.load_json("./models/v2.0.2/config.json")
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir="./models/v2.0.2", eval=True)
        self.model.cpu()

    def synthesize(self, text, selected_voice, language='en'):
        sentence_wav = self.model.synthesize(text=text, config=self.config, speaker_wav=f'./voices/{selected_voice}.wav', language=language)
        return sentence_wav
