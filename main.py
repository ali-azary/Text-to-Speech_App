import sys
from PyQt5.QtWidgets import QApplication
from ui_TTS_only import TTSApp
from pathlib import Path

def main():
    app = QApplication(sys.argv)
    
    # theme
    app.setStyleSheet(Path('light.qss').read_text())
    
    window = TTSApp()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
