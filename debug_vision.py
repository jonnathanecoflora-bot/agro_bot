
import os
import sys
# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())

from agrobot.vision import GeminiVision

def test_image():
    # Caminho da imagem enviada pelo usuario (copiada para o dir local ou usada direto)
    img_path = r"C:/Users/Windows10/.gemini/antigravity/brain/4151d4cb-8668-48fe-a1fe-5fe92eae1dbb/uploaded_image_1765340953959.png"
    
    print(f"Testing vision on: {img_path}")
    
    try:
        vision = GeminiVision()
        data = vision.extract_data(img_path)
        print("RESULTADO:")
        print(data)
    except Exception as e:
        print("ERRO FATAL:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image()
