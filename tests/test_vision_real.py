import os
import sys
import json
from agrobot.vision import GeminiVision
from agrobot.engine import AgroEnginePro
from agrobot.pdf_generator import AgroPDFPro

# Nome do arquivo de teste (deve existir na pasta)
TEST_FILE = "analise_teste.jpg" 

def test_real_pipeline():
    print("🚀 INICIANDO TESTE REAL DE VISÃO (STRING-ONLY MODE)")
    print("="*60)
    
    # SIMULAÇÃO DE DADOS PARA MISSÃO OFICIAL (CTC 7.33)
    # Cenário: Ca=2.4, Mg=0.98, K=125.2 mg (0.32 cmolc), H=3.63, Al=0.0.
    # SB = 2.4 + 0.98 + 0.32 = 3.70.
    # Acidez Potencial (H+Al) = 3.63 + 0 = 3.63.
    # CTC = SB + H + Al = 3.70 + 3.63 = 7.33.
    print("⚠️ Forçando dados manuais para Validação da FÓRMULA OFICIAL...")
    dados_raw = {
        "fisica": {"argila": "30%", "areia": "400", "silte": "null"},
        "quimica": {
            "ph_cacl2": "5,5", "ph_agua": "6.0",
            "fosforo_mg": "12,3", 
            "potassio_mg": "125,2",
            "calcio_cmolc": "2,4", 
            "magnesio_cmolc": "0,98",
            "aluminio_cmolc": "0,0",
            "hidrogenio_cmolc": "3,63", # H (Hidrogênio Puro)
            "materia_organica": "2,5%"
        }
    }

    print("\n📄 JSON RETORNADO PELA API:")
    print(json.dumps(dados_raw, indent=2, ensure_ascii=False))
    
    if not dados_raw:
        print("❌ Falha na extração.")
        return

    # 2. MOTOR (Normalização e Cálculo)
    print("\n⚙️  PROCESSANDO NO ENGINE...")
    
    user_data = {
        "nome": "Agricultor Teste",
        "propriedade": "Sítio Debug",
        "cultura": "Milho",
        "expectativa": "Alta"
    }
    
    # O Engine deve normalizar as strings "5,5" para floats 5.5 automaticamente
    engine = AgroEnginePro(dados_raw, user_data)
    resultado = engine.processar()
    
    if resultado.get("erro"):
        print("❌ Erro no Engine:")
        print(resultado.get("mensagens"))
    else:
        print("✅ Engine processou com sucesso!")
        print(f"   Diagnóstico P: {resultado['diagnostico'].get('P')}")
        # DEBUG SRE
        print(f"   CTC Calculada: {resultado['solo'].get('CTC')} cmolc/dm³ (Esperado ~7.33)")
        print(f"   V% Calculado: {resultado['solo'].get('V')}%")
        print(f"   Calagem: {resultado['calagem'].get('dose_t_ha')} t/ha")
        print(f"   Adubação NPK: {resultado['adubacao']['N']}-{resultado['adubacao']['P2O5']}-{resultado['adubacao']['K2O']}")

    # 3. PDF
    print("\n📄 GERANDO PDF...")
    resultado['meta_dados'] = user_data
    pdf_gen = AgroPDFPro()
    pdf_path = pdf_gen.gerar_pdf(resultado)
    
    if os.path.exists(pdf_path):
        print(f"✅ PDF Gerado: {pdf_path}")
    else:
        print("❌ Falha na geração do PDF")

if __name__ == "__main__":
    test_real_pipeline()
