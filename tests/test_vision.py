
import sys
import os
import json
sys.path.append(os.getcwd())

from agrobot.vision import GeminiVision

def test_vision(file_path):
    print(f"🔧 Testando Vision com: {file_path}")
    
    try:
        vision = GeminiVision()
        data = vision.extract_data(file_path)
        
        if data:
            print("✅ SUCCESS!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Validação básica
            if 'fisica' in data and 'quimica' in data:
                print(f"\n📊 Resumo:")
                print(f"  Argila: {data.get('fisica', {}).get('argila', 'N/D')}")
                print(f"  pH: {data.get('quimica', {}).get('ph_cacl2', 'N/D')}")
                print(f"  P: {data.get('quimica', {}).get('fosforo_mg', 'N/D')}")
            return True
        else:
            print("❌ Vision retornou None/vazio")
            return False
            
    except Exception as e:
        print(f"💥 ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Se nao passar arquivo, tenta usar um padrao se existir
    path = sys.argv[1] if len(sys.argv) > 1 else "debug_vision.py" # Placeholder
    # Mas vamos usar o arquivo que ja sabemos que existe se o user nao passar nada
    default_img = r"C:/Users/Windows10/.gemini/antigravity/brain/4151d4cb-8668-48fe-a1fe-5fe92eae1dbb/uploaded_image_1765340953959.png"
    
    if len(sys.argv) < 2 and os.path.exists(default_img):
        print(f"Usando imagem default: {default_img}")
        path = default_img
    elif len(sys.argv) < 2:
        print("Uso: python test_vision.py <caminho_do_arquivo>")
        sys.exit(1)
        
    test_vision(path)
