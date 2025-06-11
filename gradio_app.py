from dotenv import load_dotenv
import os
import gradio as gr

from brain_of_the_doctor import analyze_image_with_gemini
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# System prompt for the doctor
system_prompt = """
You are a professional doctor. Given a patient's symptoms (via audio) and an optional image of the affected area, provide a clinical response including diagnosis and advice. Respond with empathy and clarity. Avoid unnecessary filler.
"""

# === Core Processing Function ===
def process_inputs(audio_filepath, image_filepath):
    print("Audio path received:", audio_filepath)
    print("Image path received:", image_filepath)

    transcript = ""
    doctor_response = ""
    output_audio_path = None

    if not audio_filepath:
        return "No audio received.", "Please provide an audio input.", None

    try:
        # Transcribe audio using Groq
        transcript = transcribe_with_groq(
            GROQ_API_KEY=GROQ_API_KEY,
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
    except Exception as e:
        return "Transcription failed.", f"Error: {e}", None

    try:
        # Analyze image (if provided)
        if image_filepath:
            full_query = f"{system_prompt}\n{transcript}"
            doctor_response = analyze_image_with_gemini(full_query, image_filepath)
        else:
            doctor_response = "No image provided. Diagnosis based on symptoms only:\n\n" + transcript
    except Exception as e:
        doctor_response = f"Image analysis failed. Proceeding with audio only. Error: {e}"

    try:
        # Convert doctor's response to speech
        output_audio_path = "final_response.mp3"
        text_to_speech_with_elevenlabs(doctor_response, output_audio_path)
    except Exception as e:
        doctor_response += f"\n\n(Note: Voice generation failed: {e})"
        output_audio_path = None

    return transcript, doctor_response, output_audio_path

# === Gradio UI ===
with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown("## 🧠 AI Health Companion")
    gr.Markdown("Speak your symptoms and optionally upload an image of the affected area. A doctor-like AI will respond.")

    with gr.Row():
        audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎤 Speak your symptoms")
        image_input = gr.Image(type="filepath", label="🖼️ Upload affected area (optional)")

    with gr.Row():
        submit_btn = gr.Button("🔍 Submit")
        clear_btn = gr.Button("🧹 Clear")

    transcript_output = gr.Textbox(label="📝 Transcribed Text")
    response_output = gr.Textbox(label="🧑‍⚕️ Doctor's Response")
    voice_output = gr.Audio(label="🔊 Voice of the Doctor")

    # Button functionality
    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[transcript_output, response_output, voice_output]
    )

    clear_btn.click(
        fn=lambda: ("", "", None),
        inputs=[],
        outputs=[transcript_output, response_output, voice_output]
    )

# === Launch Gradio App ===
if __name__ == "__main__":
    iface.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        show_error=True
    )
