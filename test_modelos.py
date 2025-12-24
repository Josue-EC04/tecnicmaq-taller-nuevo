import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Cargamos tu clave
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

print("--------------------------------------------------")
if not api_key:
    print("❌ ERROR: No encontré ninguna clave en el archivo .env")
else:
    print(f"🔑 Clave detectada: {api_key[:10]}...")

    # 2. Configuramos Google
    genai.configure(api_key=api_key)

    print("\n📡 Preguntando a Google qué modelos puedes usar...")
    print("(Esto puede tardar unos segundos)")
    
    try:
        encontrados = False
        for m in genai.list_models():
            # Solo buscamos modelos que sirvan para chatear (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ DISPONIBLE: {m.name}")
                encontrados = True
        
        if not encontrados:
            print("⚠️ No se encontraron modelos compatibles. Revisa si tu API Key tiene permisos.")
            
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
print("--------------------------------------------------")