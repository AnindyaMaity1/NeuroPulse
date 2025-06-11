from dotenv import load_dotenv
import os
import gradio as gr
from flask import Flask
import threading

from brain_of_the_doctor import analyze_image_with_gemini
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts, text_to_speech_with_elevenlabs

# Load environment variables
load_dotenv()

# System prompt for the doctor
system_prompt = """You have to act as a professional doctor, I know you are not but this is for learning purposes. 
What's in this image? Do you find anything wrong with it medically? 
If you make a differential, suggest some remedies for them. Do not add any numbers or special characters in 
your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
Do not say 'In the image I see' but say 'With what I see, I think you have ....'
Don't respond as an AI model in markdown. Your answer should mimic that of an actual doctor, not an AI bot. 
Keep your answer concise (max 2 sentences). No preamble, start your answer right away please."""

# Core logic
def process_inputs(audio_filepath, image_filepath):
    print("🔈 Received audio:", audio_filepath)
    print("🖼️ Received image:", image_filepath)

    if not audio_filepath:
        print("❌ No audio received.")
        return "No audio received.", "", None

    try:
        print("🎙️ Transcribing...")
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
        print("✅ Transcription:", speech_to_text_output)
    except Exception as e:
        print("❌ Error during transcription:", e)
        return f"Error transcribing audio: {e}", "", None

    if image_filepath:
        try:
            print("🧠 Analyzing image with Gemini...")
            query = system_prompt + " " + speech_to_text_output
            doctor_response = analyze_image_with_gemini(query, image_filepath)
            print("✅ Analysis complete:", doctor_response)
        except Exception as e:
            print("❌ Error analyzing image:", e)
            doctor_response = f"Error analyzing image: {e}"
    else:
        doctor_response = "No image provided for me to analyze."

    try:
        output_audio_path = "/tmp/final.mp3"
        print("🗣️ Generating TTS...")
        text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath=output_audio_path
        )
        print("✅ TTS saved to:", output_audio_path)
        return speech_to_text_output, doctor_response, output_audio_path
    except Exception as e:
        print("❌ Error during TTS:", e)
        return speech_to_text_output, doctor_response, None

# Gradio Interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎤 Speak your symptoms"),
        gr.Image(type="filepath", label="🖼️ Upload image of affected area")
    ],
    outputs=[
        gr.Textbox(label="📝 Transcribed"),
        gr.Textbox(label="🧑‍⚕️ Doctor's Response"),
        gr.Audio(label="Voice of the Doctor", type="filepath")
    ],
    title="🧠 NeuroPulse",
    description="Speak your symptoms and upload a medical image for instant analysis. Powered by Gemini + Groq + ElevenLabs."
)

# Optional health check endpoint for Render
health_app = Flask(__name__)

@health_app.route("/health")
def health():
    return "NeuroPulse is running!", 200

# Launch everything
if __name__ == "__main__":
    # Start health check server
    threading.Thread(target=lambda: health_app.run(port=5001)).start()

    # Launch Gradio interface
    port = int(os.environ.get("PORT", 7860))
    iface.launch(server_name="0.0.0.0", server_port=port)
