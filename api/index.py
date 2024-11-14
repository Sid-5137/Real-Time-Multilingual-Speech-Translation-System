import os
import torch
import whisper
import torchaudio
from speechbrain.inference import Tacotron2, HIFIGAN
from transformers import MarianMTModel, MarianTokenizer
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
import uvicorn

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Speech-to-Text Model using Whisper
class SpeechToTextModel:
    def __init__(self):
        try:
            self.model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise RuntimeError("Failed to initialize the Whisper model.")

    def transcribe(self, audio_path):
        try:
            result = self.model.transcribe(audio_path)
            logger.info(f"Transcription result: {result}")
            return result["text"], result["language"]
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise ValueError("Speech-to-Text transcription failed.")

# Text Translation Model
class TextTranslator:
    def __init__(self):
        self.model_name = "Helsinki-NLP/opus-mt-mul-en"
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.model = MarianMTModel.from_pretrained(self.model_name)
        logger.info("Translation model loaded successfully.")

    def translate(self, text, source_lang="en", target_lang="en"):
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            translated = self.model.generate(**inputs)
            translated_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
            logger.info(f"Translation result: {translated_text}")
            return translated_text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise ValueError("Text translation failed.")

# Voice Cloning TTS Model
class VoiceCloningTTS:
    def __init__(self):
        try:
            self.tts_model = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", savedir="tmpdir_tts")
            self.vocoder = HIFIGAN.from_hparams(source="speechbrain/tts-hifigan-ljspeech", savedir="tmpdir_vocoder")
            logger.info("TTS and HiFi-GAN vocoder loaded successfully.")
        except Exception as e:
            logger.error(f"TTS model loading error: {e}")
            raise RuntimeError("Failed to initialize TTS model and vocoder.")

    def synthesize(self, text):
        try:
            mel_output, _, _ = self.tts_model.encode_text(text)
            wav = self.vocoder.decode_batch(mel_output)
            return wav.squeeze(1)  # Ensure correct dimensions
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise ValueError("Text-to-Speech synthesis failed.")

    def save_audio(self, wav, file_path):
        try:
            output_dir = os.path.dirname(file_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Ensure tensor is 2D with shape [channels, samples] and save
            if wav.dim() == 1:
                wav = wav.unsqueeze(0)  # Convert to 2D for single channel audio
            torchaudio.save(file_path, wav, 22050)
            logger.info(f"Audio saved as {file_path}")
        except Exception as e:
            logger.error(f"Audio saving error: {e}")
            raise RuntimeError("Failed to save audio file.")

# Real-time processing pipeline
class VoiceCloningPipeline:
    def __init__(self):
        self.stt_model = SpeechToTextModel()
        self.translator = TextTranslator()
        self.tts_model = VoiceCloningTTS()

    def process_audio(self, audio_path):
        try:
            logger.info("Starting transcription.")
            transcribed_text, detected_language = self.stt_model.transcribe(audio_path)
            logger.info(f"Transcribed text: {transcribed_text}, Detected language: {detected_language}")

            translated_text = self.translator.translate(transcribed_text, source_lang=detected_language, target_lang="en")
            tts_output = self.tts_model.synthesize(translated_text)

            output_file_path = os.path.join("output", os.path.basename(audio_path).replace(".wav", "_translated.wav"))
            self.tts_model.save_audio(tts_output, output_file_path)
            return translated_text, output_file_path
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

pipeline = VoiceCloningPipeline()
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)

    with open(input_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        translated_text, output_file_path = pipeline.process_audio(input_file_path)
        return JSONResponse(content={
            "message": "File processed successfully",
            "translated_text": translated_text,
            "output_file": output_file_path
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred during processing.")

# Run the API with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
