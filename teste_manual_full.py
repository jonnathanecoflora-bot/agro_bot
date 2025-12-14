
import os
from agrobot.engine import AgroEnginePro
from agrobot.pdf_generator import AgroPDFPro

def test_full_manual_flow():
    print("🚀 INICIANDO TESTE END-TO-END (SIMULAÇÃO MANUAL)")
    
    # 1. Simular Dicionário Estruturado (Igual ao output do novo telegram_bot.py)
    dados_solo = {
        "quimica": {
            "ph_agua": 5.5,
            "ph_cacl2": 4.8,
            "fosforo_mg": 8.0,
            "potassio_mg": 30.0,
            "calcio_cmolc": 1.2,
            "magnesio_cmolc": 0.5,
            "aluminio_cmolc": 0.8,
            "hidrogenio_cmolc": 4.0, # H explícito
            "h_al_cmolc": 0.0,      # H+Al (Ignorado pois tem H)
            "materia_organica": 25.0
        },
        "fisica": {
            "argila": 45.0, # 45%
            "areia": 0.0,
            "silte": 0.0
        }
    }
    
    dados_usuario = {
        'nome': 'Teste Stability',
        'propriedade': 'Fazenda Debug',
        'cultura': 'Milho',
        'expectativa': 'Alta'
    }
    
    # 2. Executar Engine
    print("\n⚙️  Executando AgroEnginePro...")
    engine = AgroEnginePro(dados_solo, dados_usuario)
    resultado = engine.processar()
    
    if resultado.get("erro"):
        print(f"❌ ERRO NO ENGINE: {resultado['mensagens']}")
        return
        
    print("✅ Engine Finalizado com Sucesso!")
    
    # Validação de Lógica Interna
    print("\n🔍 Validando Lógica V7...")
    plano = resultado.get('formulacao', {}).get('plano', {})
    plantio = plano.get('plantio', {})
    cobertura = plano.get('cobertura', [])
    
    H_Al_Calc = engine.solo['H_Al']
    print(f"   ► H+Al Calculado: {H_Al_Calc} (Esperado: 4.0 + 0.8 = 4.8)")
    
    if abs(H_Al_Calc - 4.8) < 0.1:
        print("   [PASS] Soma H+Al OK")
    else:
        print("   [FAIL] Erro na Soma H+Al")
        
    print(f"   ► Plantio: {plantio.get('formula')}")
    print(f"   ► Cobertura: {[x['nome'] for x in cobertura]}")
    
    # 3. Gerar PDF
    print("\n📄 Gerando PDF...")
    pdf_gen = AgroPDFPro()
    pdf_path = pdf_gen.gerar_pdf(resultado)
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"✅ PDF Gerado com Sucesso: {pdf_path}")
    else:
        print("❌ Falha na Geração do PDF")

if __name__ == "__main__":
    test_full_manual_flow()
