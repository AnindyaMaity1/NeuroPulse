from dotenv import load_dotenv
load_dotenv()

import os
import logging
from io import BytesIO
import speech_recognition as sr
from pydub import AudioSegment
from groq import Groq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Records audio from the microphone and saves it as an MP3 file.

    Args:
        file_path (str): Destination path for saving MP3.
        timeout (int): Time to wait for speaking to start (in seconds).
        phrase_time_limit (int): Maximum length of recording (in seconds).
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            logging.info("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("🎧 Listening...")
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            # Convert to mp3
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            logging.info(f"✅ Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"❌ Error recording audio: {e}")


def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """
    Transcribes audio using Groq + Whisper.

    Args:
        stt_model (str): Name of the transcription model (e.g. whisper-large-v3).
        audio_filepath (str): Path to audio file.
        GROQ_API_KEY (str): Your Groq API key.

    Returns:
        str: Transcribed text.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set.")

    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        logging.error(f"❌ Error during transcription: {e}")
        return "Transcription failed."


# Optional test
if __name__ == "__main__":
    file_path = "test_audio.mp3"
    record_audio(file_path, timeout=10, phrase_time_limit=5)

    api_key = os.environ.get("GROQ_API_KEY")
    model = "whisper-large-v3"

    if os.path.exists(file_path):
        result = transcribe_with_groq(model, file_path, api_key)
        print("📝 Transcription:", result)
