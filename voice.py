import os
from PyQt5.QtWidgets import QFileDialog

class VoiceManager:
    @staticmethod
    def add_voice_file():
        """
        Add a new voice file to the application.
        """
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "Select Voice File", "", "wav Files (*.wav)")
        if file_path:
            target_path = f"./voices/{os.path.basename(file_path)}"
            shutil.copy(file_path, target_path)
            return os.path.splitext(os.path.basename(file_path))[0]
        return None

    @staticmethod
    def play_voice_file(selected_voice, player):
        """
        Play the selected voice file.
        """
        if selected_voice:
            file_path = f'./voices/{selected_voice}.wav'
            player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            player.play()
