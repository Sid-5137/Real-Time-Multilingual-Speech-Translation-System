# Real-Time Multilingual Speech Translation System

This project implements a real-time multilingual speech translation system. It includes modules for audio capture, speech-to-text, text translation, and text-to-speech, providing a comprehensive pipeline for translating spoken language in real-time.

## Setup

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Run the Pipeline**: `python main.py`
3. **Install Flutter:** Ensure you have Flutter installed on your machine. If not, follow the instructions on the official [Flutter website](https://docs.flutter.dev/get-started/install/windows/desktop) to set it up.
4. **Install App Dependencies**: Then, navigate to the Flutter app directory and run. `flutter pub get`
5. **Run the App**: `flutter run`

## Directory Structure

#### Python Backend:
- `audio_capture/`: Handles audio capture and preprocessing.
- `models/`: Contains pretrained models for STT, translation, and TTS.
- `real_time_processing/`: Integrates the pipeline components.
- `utils/`: Utility functions and classes.
- `tests/`: Unit tests for each module.
- `scripts/`: Helper scripts for dataset preparation and pipeline execution.
- `config/`: Configuration files for models and pipelines.

#### Flutter App:
- `lib/`: Contains the Flutter app's core codebase.
- `assets/`: Stores assets like icons and images.
- `android/`: Android-specific configurations and files.
- `ios/`: iOS-specific configurations and files.

## License

This project is licensed under the MIT License.
