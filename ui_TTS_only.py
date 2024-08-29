import os
import shutil
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QHBoxLayout, QLabel, QComboBox, QFileDialog, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from worker import Worker
from model import XttsConfig, Xtts
from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt


class TTSApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("text-to-speech app")
        self.resize(600, 800)
        self.setWindowIcon(QIcon('text-speech_8984813.ico'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Theme selector dropdown
        self.themeSelector = QComboBox(self)
        self.themeSelector.addItems(['light', 'dark'])
        self.themeSelector.currentIndexChanged.connect(self.changeTheme)
        self.layout.addWidget(QLabel('Select Theme:'))
        self.layout.addWidget(self.themeSelector)
        
        self.text_edit = QTextEdit()
        self.layout.addWidget(self.text_edit)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.play_button = QPushButton("Generate speech")
        self.play_button.clicked.connect(self.play_audio)
        self.button_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_audio)
        self.button_layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)

        self.voice_label = QLabel("Select Voice:")
        self.layout.addWidget(self.voice_label)

        self.voice_combo_box = QComboBox()
        self.populate_voice_list()
        self.layout.addWidget(self.voice_combo_box)
        
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)
        self.play_voice_button = QPushButton("Play Voice File")
        self.play_voice_button.clicked.connect(self.play_voice_file)
        self.button_layout.addWidget(self.play_voice_button)

        self.add_voice_button = QPushButton("Add New Voice File")
        self.add_voice_button.clicked.connect(self.add_voice_file)
        self.button_layout.addWidget(self.add_voice_button)

        self.status_label = QLabel()
        self.layout.addWidget(self.status_label)

        self.init_tts_model()
        self.worker = None
        self.player = QMediaPlayer()
        
        # Language selection dropdown
        self.language_label = QLabel("Select Language:")
        self.layout.addWidget(self.language_label)

        self.language_combo_box = QComboBox()
        self.language_combo_box.addItems(["English", "Spanish", "French", "Turkish"])  # Add more languages as needed
        self.layout.addWidget(self.language_combo_box)
        
        # Sample rate slider
        self.sample_rate_label = QLabel("Sample Rate:")
        self.layout.addWidget(self.sample_rate_label)

        self.sample_rate_slider = QSlider()
        self.sample_rate_slider.setOrientation(Qt.Horizontal)
        self.sample_rate_slider.setMinimum(1000)  # Minimum sample rate
        self.sample_rate_slider.setMaximum(50000)  # Maximum sample rate
        self.sample_rate_slider.setValue(23000)  # Default sample rate
        self.sample_rate_slider.setTickInterval(1000)  # Tick interval for slider
        self.sample_rate_slider.setTickPosition(QSlider.TicksBelow)  # Tick position
        self.sample_rate_slider.valueChanged.connect(self.update_sample_rate_label)
        self.layout.addWidget(self.sample_rate_slider)

        self.sample_rate_value_label = QLabel(f"Current Sample Rate: {self.sample_rate_slider.value()} Hz")
        self.layout.addWidget(self.sample_rate_value_label)
        
        # TTS engine selection dropdown
        self.engine_label = QLabel("Select TTS Engine:")
        self.layout.addWidget(self.engine_label)

        self.engine_combo_box = QComboBox()
        self.engine_combo_box.addItems(["XTTS"])  # Add more engines as needed
        self.layout.addWidget(self.engine_combo_box)
        
    def changeTheme(self):
        theme = self.themeSelector.currentText()
        try:
            with open(f"./themes/{theme}.qss", "r") as stylefile:
                stylesheet = stylefile.read()
                QApplication.instance().setStyleSheet(stylesheet)  # Apply stylesheet to the entire application
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")
            
            
    def update_sample_rate_label(self):
        self.sample_rate_value_label.setText(f"Current Sample Rate: {self.sample_rate_slider.value()} Hz")
    
    def add_voice_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Voice File", "", "wav Files (*.wav)")
        if file_path:
            target_path = f"./voices/{os.path.basename(file_path)}"
            shutil.copy(file_path, target_path)
            self.voice_combo_box.addItem(os.path.splitext(os.path.basename(file_path))[0])
            self.status_label.setText(f"Added new voice: {os.path.basename(file_path)}")

    def play_voice_file(self):
        selected_voice = self.voice_combo_box.currentText()
        if selected_voice:
            file_path = f'./voices/{selected_voice}.wav'
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.player.play()
    
    
    
    def init_tts_model(self):
        # Init TTS with the target model name
        self.config = XttsConfig()
        self.config.load_json("./models/v2.0.2/config.json")
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir="./models/v2.0.2", eval=True)
        self.model.cpu()

    def populate_voice_list(self):
        voices_dir = "./voices"
        if not os.path.exists(voices_dir) or not os.path.isdir(voices_dir):
            return

        voices = [file.split('.')[0] for file in os.listdir(voices_dir) if file.endswith(".wav")]
        self.voice_combo_box.addItems(voices)

    def play_audio(self):
        if self.worker is not None and self.worker.is_running:
            self.status_label.setText("Speech generation is already in progress.")
            return

        if hasattr(self, 'worker_thread') and self.worker_thread.isRunning():
            # If a previous worker thread is running, wait for it to finish
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        text = self.text_edit.toPlainText()
        selected_voice = self.voice_combo_box.currentText()
        selected_language = self.language_combo_box.currentText()
        self.worker = Worker(text, selected_voice, self.config, self.model, selected_language)
        self.worker.finished.connect(self.audio_generation_finished)
        self.worker.update_status.connect(self.update_status_label)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def audio_generation_finished(self):
        
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.worker.file:
            self.status_label.setText(f"Audio saved to {self.worker.file}")
        self.worker = None  # Resetting the worker instance

    def update_status_label(self, sentence):
        highlighted_text = self.highlight_sentence(sentence)
        self.text_edit.setHtml(highlighted_text)
        
    def highlight_sentence(self, sentence):
        text = self.text_edit.toPlainText()
        highlighted_text = text.replace(sentence, f"<span style='background-color: yellow; '>{sentence}</span>")
        return highlighted_text

    def stop_audio(self):
        if self.worker is not None:
            self.worker.stop()
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait()
            self.status_label.setText("Speech generation stopped.")
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)

