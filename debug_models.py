import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key não encontrada no .env")
    exit()

print(f"🔑 Testando Key: {api_key[:5]}...{api_key[-3:]}")

genai.configure(api_key=api_key)

print("\n🔍 Listando modelos disponíveis:")
try:
    models = list(genai.list_models())
    if not models:
        print("⚠️ Nenhum modelo retornado pela API.")
    
    for m in models:
        # print(f"RAW: {m}") # Debug if needed
        name = getattr(m, 'name', 'UNKNOWN')
        methods = getattr(m, 'supported_generation_methods', [])
        
        if 'generateContent' in methods:
            print(f"   ✅ AVAILABLE: {name}")
            
except Exception as e:
    print(f"❌ Erro ao listar modelos: {e}")
