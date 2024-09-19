import numpy as np
import librosa

class AudioPreprocessor:
    """Preprocess audio by normalizing and resampling it."""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate

    def normalize_audio(self, audio_data):
        max_val = np.max(np.abs(audio_data))
        return (audio_data / max_val).astype(np.float32) if max_val > 0 else audio_data.astype(np.float32)

    def resample_audio(self, audio_data, orig_sample_rate):
        return librosa.resample(audio_data, orig_sr=orig_sample_rate, target_sr=self.sample_rate).astype(np.float32) if orig_sample_rate != self.sample_rate else audio_data.astype(np.float32)

    def preprocess(self, audio_data, orig_sample_rate):
        return self.resample_audio(self.normalize_audio(audio_data), orig_sample_rate)
