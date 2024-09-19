import whisper

class SpeechToTextModel:
    """Convert speech to text using Whisper."""
    def __init__(self):
        self.model = whisper.load_model("base")

    def transcribe(self, audio_data):
        result = self.model.transcribe(audio_data)
        return result["text"], result["language"]
