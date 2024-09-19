class AudioConfig:
    """Configuration for audio processing."""
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    FORMAT = "int16"
    NOISE_REDUCTION = True
    NORMALIZATION = True
