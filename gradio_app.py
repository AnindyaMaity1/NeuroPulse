from dotenv import load_dotenv
import os
import gradio as gr

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
Keep your answer concise (max 5 sentences). No preamble, start your answer right away please."""

# Core logic for processing inputs
def process_inputs(audio_filepath, image_filepath):
    if not audio_filepath:
        return "No audio received.", "", None

    try:
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
    except Exception as e:
        return f"Error transcribing audio: {e}", "", None

    if image_filepath:
        try:
            query = system_prompt + " " + speech_to_text_output
            doctor_response = analyze_image_with_gemini(query, image_filepath)
        except Exception as e:
            doctor_response = f"Error analyzing image: {e}"
    else:
        doctor_response = "No image provided for me to analyze."

    try:
        output_audio_path = "final.mp3"
        text_to_speech_with_elevenlabs(
            input_text=doctor_response,
            output_filepath=output_audio_path
        )
        return speech_to_text_output, doctor_response, output_audio_path
    except Exception as e:
        return speech_to_text_output, doctor_response, None

# Gradio UI
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Speak your symptoms"),
        gr.Image(type="filepath", label="Upload image of affected area")
    ],
    outputs=[
        gr.Textbox(label="📝 Transcribed"),
        gr.Textbox(label="🧑‍⚕️ Doctor's Response"),
        # gr.Audio(label="Voice of the Doctor", type="filepath")
    ],
    title="NeuroPulse",
    description="Speak your symptoms in English and upload a photo."
)

# Launch Gradio app with Render-friendly config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    iface.launch(server_name="0.0.0.0", server_port=port)
