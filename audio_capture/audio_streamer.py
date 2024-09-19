import pyaudio
import numpy as np

class AudioStreamer:
    """Stream audio from the microphone in real-time."""
    def __init__(self, sample_rate=16000, chunk_size=1024, channels=1):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.audio_interface = pyaudio.PyAudio()

    def start_stream(self, callback):
        """Start audio streaming and handle the callback."""
        stream = self.audio_interface.open(format=pyaudio.paInt16, channels=self.channels, rate=self.sample_rate, input=True, frames_per_buffer=self.chunk_size, stream_callback=callback)
        stream.start_stream()
        try:
            while stream.is_active():
                pass
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()
            self.audio_interface.terminate()

def audio_callback(in_data, frame_count, time_info, status):
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    return in_data, pyaudio.paContinue
