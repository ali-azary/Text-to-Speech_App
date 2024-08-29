import os
import shutil

def copy_file(source_path, target_path):
    """
    Copy a file from source_path to target_path.
    """
    shutil.copy(source_path, target_path)

def get_voice_files(directory):
    """
    Get a list of voice files (MP3) from the specified directory.
    """
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return []
    
    return [file for file in os.listdir(directory) if file.endswith(".mp3")]

def highlight_text(text, sentence):
    """
    Highlight a sentence within the text with HTML.
    """
    highlighted_text = text.replace(sentence, f"<span style='background-color: yellow; '>{sentence}</span>")
    return highlighted_text
