from gtts import gTTS
import os

class TextToSpeechModel:
    """
    A class for text-to-speech synthesis using gTTS.
    """
    def synthesize(self, text, lang="en"):
        """Synthesize speech from the given text using gTTS."""
        tts = gTTS(text=text, lang=lang)
        return tts

    def save_audio(self, tts, original_file_path, detected_language):
        """
        Save the synthesized speech as a .mp3 file. The output file is named based on the original input
        file name and detected language, and saved in the 'output' directory.
        """
        base_name = os.path.basename(original_file_path)
        file_name = f"{os.path.splitext(base_name)[0]}_{detected_language}.mp3"
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)  # Create 'output' directory if it doesn't exist
        output_path = os.path.join(output_dir, file_name)

        tts.save(output_path)
        print(f"Audio saved as {output_path}")
