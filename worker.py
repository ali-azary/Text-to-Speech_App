import os
import sys
import nltk
import sounddevice as sd
import soundfile as sf
import numpy as np
from threading import Event
from PyQt5.QtCore import QObject, pyqtSignal
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from PyQt5.QtWidgets import QFileDialog


class Worker(QObject):
    finished = pyqtSignal()
    update_status = pyqtSignal(str)

    def __init__(self, text, selected_voice, config, model, selected_language):
        super().__init__()
        self.text = text
        self.selected_voice = selected_voice
        self.selected_language = selected_language
        self.config = config
        self.model = model
        self.is_running = True
        self.file = None
        self.stop_event = Event()  # threading event to handle stop requests
        
    def stop(self):
        self.stop_event.set()  # signal all threads to stop
        sd.stop()
    
    def run(self):
        try:
            language = "en"  # Default language is English
            if self.selected_language == "Spanish":
                language = "es"
            elif self.selected_language == "French":
                language = "fr"
            elif self.selected_language == "Turkish":
                language = "tr"
            sentences = nltk.sent_tokenize(text=self.text)
            all_wavs = []
            for sentence in sentences:
                if self.stop_event.is_set():  # Early exit if stop requested
                    break
                
                output = self.model.synthesize(text=sentence, 
                                               config=self.config, 
                                               speaker_wav=f'./voices/{self.selected_voice}.wav', 
                                               language=language)
                sd.play(output['wav'], samplerate=23000)
                all_wavs.append(output['wav'])
                self.update_status.emit(sentence)
                sd.wait()
                while sd.get_stream().active:
                    if not self.is_running:
                        sd.stop()
                        break

            if not self.stop_event.is_set():
                concat_wav = np.concatenate(all_wavs)
                file_dialog = QFileDialog()
                file_path, _ = file_dialog.getSaveFileName(None, "Save File", "", "WAV Files (*.wav)")
                if file_path:
                    sf.write(file_path, concat_wav, 23000)
                    self.file = file_path


                self.update_status.emit("Audio generation finished.")

        except Exception as e:
            # Emit error message if an exception occurs
            self.update_status.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()
