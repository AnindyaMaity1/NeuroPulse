from dotenv import load_dotenv
load_dotenv()

import os
import platform
import subprocess
from gtts import gTTS
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice

# Load ElevenLabs API key from environment
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

# === gTTS (Simple save to file) ===
def text_to_speech_with_gtts_old(input_text, output_filepath):
    audioobj = gTTS(text=input_text, lang="en", slow=False)
    audioobj.save(output_filepath)

# === ElevenLabs (Simple save to file) ===
def text_to_speech_with_elevenlabs_old(input_text, output_filepath):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech(
        text=input_text,
        voice=Voice(voice_id="EXAVITQu4vr4xnSDxMaL", name="Aria"),
        model="eleven_turbo_v2",
        output_format="mp3_22050_32"
    )
    with open(output_filepath, "wb") as f:
        f.write(audio)

# === gTTS with Auto Playback ===
def text_to_speech_with_gtts(input_text, output_filepath):
    audioobj = gTTS(text=input_text, lang="en", slow=False)
    audioobj.save(output_filepath)

    try:
        os_name = platform.system()
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")

# === ElevenLabs with Auto Playback ===
def text_to_speech_with_elevenlabs(input_text, output_filepath):
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech(
        text=input_text,
        voice=Voice(voice_id="EXAVITQu4vr4xnSDxMaL", name="Aria"),
        model="eleven_turbo_v2",
        output_format="mp3_22050_32"
    )
    with open(output_filepath, "wb") as f:
        f.write(audio)

    try:
        os_name = platform.system()
        if os_name == "Darwin":
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")

# === Entry point for direct testing ===
if __name__ == "__main__":
    text_to_speech_with_gtts_old(input_text, "gtts_testing.mp3")
    text_to_speech_with_elevenlabs_old(input_text, "eleven_testing.mp3")
