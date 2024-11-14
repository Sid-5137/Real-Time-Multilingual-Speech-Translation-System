import os
import torch
import whisper
import soundfile as sf
import torchaudio
from speechbrain.inference import EncoderClassifier, Tacotron2, HIFIGAN as HifiGan  
from transformers import MarianMTModel, MarianTokenizer
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import logging
import uvicorn
import traceback

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

    def transcribe(self, audio_data):
        try:
            logger.debug(f"Audio data shape: {audio_data.shape}")
            result = self.model.transcribe(audio_data)
            logger.info(f"Transcription result: {result}")
            return result["text"], result["language"]
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise ValueError("Speech-to-Text transcription failed.")

# Translation model using MarianMT
class TranslationModel:
    def __init__(self, src_lang, tgt_lang="en"):
        try:
            model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
            logger.info("Translation model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading translation model: {e}")
            raise RuntimeError("Failed to initialize the translation model.")

    def translate(self, text):
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = self.model.generate(**inputs)
            return self.tokenizer.decode(translated[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise ValueError("Translation failed.")

# TTS model with Tacotron2 and HifiGan for voice cloning
class VoiceCloningTTS:
    def __init__(self):
        try:
            self.encoder = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", run_opts={"device": "cpu"})
            self.tts_model = Tacotron2.from_hparams(source="speechbrain/tts-tacotron2-ljspeech", run_opts={"device": "cpu"})
            self.vocoder = HifiGan.from_hparams(source="speechbrain/tts-hifigan-ljspeech", run_opts={"device": "cpu"})
            logger.info("TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading TTS model: {e}")
            raise RuntimeError("Failed to initialize the TTS model.")

    def synthesize(self, text, embedding):
        try:
            mel_output = self.tts_model(text, embedding)
            waveform = self.vocoder(mel_output)
            return waveform
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise ValueError("TTS synthesis failed.")

# Voice cloning pipeline
class VoiceCloningPipeline:
    def __init__(self):
        self.stt_model = SpeechToTextModel()
        self.tts_model = VoiceCloningTTS()

    def preprocess_audio(self, audio_path):
        try:
            audio_data, sample_rate = torchaudio.load(audio_path)
            if sample_rate != 16000:
                audio_data = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(audio_data)
            if audio_data.size(0) > 1:
                audio_data = torch.mean(audio_data, dim=0, keepdim=True)
            return audio_data
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            raise ValueError("Failed to preprocess audio.")

    def process_audio(self, audio_path):
        try:
            audio_data = self.preprocess_audio(audio_path)
            transcribed_text, detected_language = self.stt_model.transcribe(audio_data)
            logger.info(f"Transcribed text: {transcribed_text}, Detected language: {detected_language}")
            return transcribed_text, detected_language
        except ValueError as ve:
            logger.error(f"Processing error: {ve}")
            raise HTTPException(status_code=500, detail=str(ve))
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Unexpected error during audio processing: {e}\nDetails:\n{error_details}")
            raise HTTPException(status_code=500, detail="Unexpected error occurred during processing.")

    def process_text_to_speech(self, text, audio_path):
        try:
            embedding = self.tts_model.encoder.encode_batch(audio_path)
            synthesized_speech = self.tts_model.synthesize(text, embedding)
            output_path = os.path.join("output", "synthesized_speech.wav")
            torchaudio.save(output_path, synthesized_speech.squeeze(0).cpu(), 16000)
            return output_path
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error in TTS process: {e}\nDetails:\n{error_details}")
            raise HTTPException(status_code=500, detail="Failed to save audio file.")

pipeline = VoiceCloningPipeline()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(input_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        transcribed_text, detected_language = pipeline.process_audio(input_file_path)
        tts_output_path = pipeline.process_text_to_speech(transcribed_text, input_file_path)
        return JSONResponse(content={
            "message": "File processed successfully",
            "transcribed_text": transcribed_text,
            "detected_language": detected_language,
            "tts_output_file": tts_output_path
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Unexpected error: {e}\nDetails:\n{error_details}")
        raise HTTPException(status_code=500, detail="Unexpected error occurred during processing.")

# Run the API with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
