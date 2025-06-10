from dotenv import load_dotenv
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    raise ValueError("Missing GOOGLE_API_KEY in environment variables.")

# Load image using PIL
def load_image(image_path):
    try:
        return Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found at path: {image_path}")
    except Exception as e:
        raise Exception(f"Error loading image: {e}")

# Analyze image with Gemini 1.5 Flash (or Pro)
def analyze_image_with_gemini(query, image_path):
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        image = load_image(image_path)

        response = model.generate_content(
            [query, image],
            stream=False
        )

        return response.text.strip() if response.text else "No response received."
    except Exception as e:
        return f"Error during analysis: {e}"

# # Test locally
# if __name__ == "__main__":
#     query = "Is there something wrong with my face?"
#     image_path = "acne.jpg"
#     result = analyze_image_with_gemini(query, image_path)
#     print("Doctor's Analysis:", result)
