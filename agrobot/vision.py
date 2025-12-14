import os
import json
import time
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiVision:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY ausente.")
        
        genai.configure(api_key=api_key)
        
        # Estratégia V7: Single Model Stability
        # Usamos apenas o flash estável para evitar flutuações e erros de key
        model_candidates = ["gemini-1.5-flash"]
        
        self.model = None
        self.model_name = ""
        
        for model_name in model_candidates:
            try:
                print(f"🔄 Tentando carregar modelo: {model_name}...")
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.1
                    }
                )
                
                # Teste de validação (Ping)
                # SE FALHAR AQUI (429/Quota), não deve crashar o bot inteiro, apenas desabilitar vision
                print(f"   🧪 Validando {model_name}...")
                response = model.generate_content("Ping")
                if not response:
                    raise ValueError("Resposta vazia no teste de validação.")
                
                self.model = model
                self.model_name = model_name
                print(f"✅ Modelo Vision validado e carregado: {self.model_name}")
                break
                
            except Exception as e:
                # Tratamento de Erro Robusto (V7)
                print(f"⚠️ Aviso: Falha ao carregar Vision AI ({model_name}): {e}")
                # Não raise RuntimeError aqui. Permite iniciar sem Vision.
        
        if self.model is None:
            print("❌ ALERTA: Vision AI indisponível (Cota/Erro). O Bot funcionará apenas em modo /manual.")
            # Não crashar app. Deixar self.model = None e tratar no extract_data.

    def extract_data(self, file_path):
        """Extrai dados e retorna valores como STRINGS para evitar quebra de JSON"""
        
        if not self.model:
            print("❌ Modelo não inicializado.")
            return None

        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            return None
        
        try:
            print(f"📤 Upload: {os.path.basename(file_path)}")
            
            # Determinar MIME
            mime_type = "application/pdf" if file_path.lower().endswith('.pdf') else "image/jpeg"
            
            # Upload com Retry Simples
            gemini_file = genai.upload_file(file_path, mime_type=mime_type)
            
            # Active Wait
            for _ in range(10):
                time.sleep(1)
                gemini_file = genai.get_file(gemini_file.name)
                if gemini_file.state.name == "ACTIVE":
                    break
            
            if gemini_file.state.name != "ACTIVE":
                print("❌ Falha: Arquivo não ficou ativo no Gemini.")
                return None
            
            # PROMPT DE SRE 4.0: AGGRESSIVE EXTRACTION (H & Al FOCUS)
            prompt = """
            ATUE COMO UM ENGENHEIRO AGRÔNOMO DE DADOS SÊNIOR. 
            SUA MISSÃO: Extrair TODOS os parâmetros da análise de solo com precisão cirúrgica.

            ⚠️ INSTRUÇÕES DE EXTRAÇÃO (PRIORIDADE MÁXIMA):
            
            1. **HIDROGÊNIO (H) E ALUMÍNIO (Al)**:
               - O CAMPO "H" (Hidrogênio) É OBRIGATÓRIO (CRÍTICO).
               - Procure por colunas: "H", "H+", "Hidrogênio", "H (Hidrogênio)", "Acidez H".
               - Se encontrar um número na coluna "H" (ex: "3,63", "5,2"), EXTRAIA-O para "hidrogenio_cmolc".
               - NÃO CONFUNDA "H" com "H+Al". Se tiverem colunas separadas, pegue as duas.
               - Se só tiver "H+Al", extraia para "h_al_cmolc".
               - Se ver "Al" separado (ex: 0,0 ou 0,3), EXTRAIA-O para "aluminio_cmolc".
               - ALERTA: Em solos ácidos, H costuma ser > 2.0. Não ignore.
            
            2. **MACRONUTRIENTES (Ca, Mg)**:
               - IGNORE colunas de soma como "Ca+Mg" ou "Soma de Bases" na extração principal.
               - Extraia "Ca" e "Mg" das colunas individuais.
               - Apenas se falhar, use "soma_ca_mg_cmolc" como último recurso.
            
            3. **UNIDADES**:
               - Argila/Areia > 100? Extraia o número bruto (ex: "534"). NÃO CONVERTA.
               - Mantenha casas decimais (vírgula ou ponto).

            JSON ALVO (ESTRITO):
            {
                "quimica": {
                    "ph_agua": "string",
                    "ph_cacl2": "string",
                    "fosforo_mg": "string",
                    "potassio_mg": "string",
                    "calcio_cmolc": "string",
                    "magnesio_cmolc": "string",
                    "aluminio_cmolc": "string",  # BUSCA AGRESSIVA
                    "hidrogenio_cmolc": "string", # BUSCA AGRESSIVA (H Puro)
                    "h_al_cmolc": "string",
                    "materia_organica": "string"
                },
                "fisica": {
                    "argila": "string",
                    "areia": "string",
                    "silte": "string"
                }
            }
            """
            
            print("🧠 Processando com Gemini (Mode: String-Only)...")
            response = self.model.generate_content([prompt, gemini_file])
            
            # Limpeza Hardcore do JSON
            raw_text = response.text
            cleaned_json = self._clean_json_string(raw_text)
            
            try:
                dados = json.loads(cleaned_json)
                print("✅ JSON Parseado com sucesso!")
                return dados
            except json.JSONDecodeError as e:
                print(f"❌ Erro de JSON: {e}")
                print(f"❌ Dump: {cleaned_json}")
                return None
            finally:
                genai.delete_file(gemini_file.name)

        except Exception as e:
            print(f"❌ Exceção Vision: {e}")
            return None

    def _clean_json_string(self, text):
        """Remove Markdown e espaços extras para garantir JSON válido"""
        # Remove blocos de código
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Encontra o primeiro { e o último }
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            return text[start:end+1]
        
        return text.strip()
