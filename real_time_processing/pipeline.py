import soundfile as sf
from models.text_translation.translation_model import TranslationModel
from models.speech_to_text.stt_model import SpeechToTextModel
from models.text_to_speech.tts_model import TextToSpeechModel
from audio_capture.audio_preprocessor import AudioPreprocessor
from utils.logger import logger

class RealTimePipeline:
    """
    Real-time speech translation pipeline that processes audio files and generates translated speech.
    """
    def __init__(self):
        self.audio_preprocessor = AudioPreprocessor()
        self.stt_model = SpeechToTextModel()
        self.tts_model = TextToSpeechModel()

    def process_audio(self, audio_data, original_file_path):
        """Process the audio input, perform STT, translation, and TTS."""
        preprocessed_audio = self.audio_preprocessor.preprocess(audio_data, orig_sample_rate=16000)
        
        # Perform speech-to-text and language detection
        transcribed_text, detected_language = self.stt_model.transcribe(preprocessed_audio)
        logger.info(f"Detected Language: {detected_language}")
        
        # Handle unsupported languages and skip translation if necessary
        supported_languages = ["fr", "en", "es", "de", "ja", "zh", "jap", "iir", "ko", "ru", "vi", "lus", "sv", "mt", "af", "aed", "alv", "mul"]
        if detected_language not in supported_languages:
            logger.error(f"Translation for language '{detected_language}' is not supported. Skipping translation.")
            translated_text = transcribed_text
        else:
            translation_model = TranslationModel(src_lang=detected_language, tgt_lang="en")
            translated_text = translation_model.translate(transcribed_text)
            logger.info(f"Translated Text: {translated_text}")
        
        # Synthesize speech from the translated text
        tts = self.tts_model.synthesize(translated_text, lang=detected_language)
        
        # Save the audio to a file
        self.tts_model.save_audio(tts, original_file_path, detected_language)

    def file_stream(self, file_path):
        """Process an audio file."""
        logger.info(f"Processing file: {file_path}")
        audio_data, sample_rate = sf.read(file_path)
        processed_audio = self.audio_preprocessor.preprocess(audio_data, orig_sample_rate=sample_rate)
        self.process_audio(processed_audio, file_path)

    def run(self):
        """Run the pipeline with file input."""
        file_path = input("Enter the path to the audio file: ")
        self.file_stream(file_path)
