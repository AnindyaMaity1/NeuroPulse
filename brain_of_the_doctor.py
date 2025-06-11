from dotenv import load_dotenv
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")  # Default model is flash

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    raise ValueError("❌ Missing GOOGLE_API_KEY in environment variables.")

# === Load Image using PIL ===
def load_image(image_path):
    try:
        return Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"🖼️ Image not found at: {image_path}")
    except Exception as e:
        raise Exception(f"🔍 Error loading image: {e}")

# === Analyze Image with Gemini ===
def analyze_image_with_gemini(query, image_path):
    try:
        image = load_image(image_path)
        model = genai.GenerativeModel(GEMINI_MODEL)

        response = model.generate_content([query, image], stream=False)

        if response and response.text:
            return response.text.strip()
        else:
            return "🤖 Gemini returned no meaningful response."
    except Exception as e:
        return f"❌ Error during analysis: {e}"

# === Optional: Local Test ===
# if __name__ == "__main__":
#     query = "Is there something wrong with this skin condition?"
#     image_path = "example_skin.jpg"
#     print(analyze_image_with_gemini(query, image_path))
