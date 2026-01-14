import google.generativeai as genai
import os
from dotenv import load_dotenv  # <--- IMPORTAR ESTO

load_dotenv()  # <--- CARGAR EL ARCHIVO .ENV

api_key = os.getenv('GEMINI_API_KEY') 
genai.configure(api_key=api_key)

print("🔍 Buscando modelos disponibles...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Disponible: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")