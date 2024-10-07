# api/index.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import whisper
from gtts import gTTS
import soundfile as sf

app = FastAPI()

# Define the Speech-To-Text Model using Whisper
class SpeechToTextModel:
    def __init__(self):
        self.model = whisper.load_model("base",device="cpu")

    def transcribe(self, audio_data):
        result = self.model.transcribe(audio_data)
        return result["text"], result["language"]

# Define the Text-To-Speech Model using gTTS
class TextToSpeechModel:
    def synthesize(self, text, lang="en"):
        tts = gTTS(text=text, lang=lang)
        return tts

    def save_audio(self, tts, original_file_path, detected_language):
        base_name = os.path.basename(original_file_path)
        file_name = f"{os.path.splitext(base_name)[0]}_{detected_language}.mp3"
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, file_name)
        tts.save(output_path)
        return output_path

# Real-time processing pipeline
class RealTimePipeline:
    def __init__(self):
        self.stt_model = SpeechToTextModel()
        self.tts_model = TextToSpeechModel()

    def process_audio(self, audio_data, original_file_path):
        transcribed_text, detected_language = self.stt_model.transcribe(audio_data)

        # Check if translation is required or supported
        supported_languages = ["fr", "en", "es", "de", "ja", "zh"]
        if detected_language not in supported_languages:
            translated_text = transcribed_text
        else:
            translated_text = transcribed_text  # Assume no translation

        tts = self.tts_model.synthesize(translated_text, lang=detected_language)
        output_path = self.tts_model.save_audio(tts, original_file_path, detected_language)
        return output_path

    def file_stream(self, file_path):
        audio_data, _ = sf.read(file_path)
        return self.process_audio(audio_data, file_path)

pipeline = RealTimePipeline()

OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    input_file_path = os.path.join(OUTPUT_DIR, file.filename)

    with open(input_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        output_file_path = pipeline.file_stream(input_file_path)
        return JSONResponse(content={
            "message": "File processed successfully",
            "output_file": os.path.basename(output_file_path)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/output/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
