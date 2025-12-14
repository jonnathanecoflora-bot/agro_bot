
import sys
import os
import json

# Adiciona o diretório atual ao path para import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agrobot.vision import GeminiVision 
from agrobot.engine import AgroBotEngine

def main():
    print("🚜 Iniciando AgroBot v1.0 (Integration Test)...")
    
    # 1. Simula entrada do usuário
    caminho_arquivo = "analise_teste.jpg"
    
    # 2. Visão Computacional (REAL ou MOCK se falhar)
    try:
        vision = GeminiVision()
        # Se você não tiver API Key configurada, pode falhar.
        # Para teste seguro sem gastar token ou sem key, poderiamos usar um mock.
        # Mas vamos tentar usar o real se o arquivo existir.
        if os.path.exists(caminho_arquivo):
            print(f"👁️  Lendo arquivo: {caminho_arquivo}")
            dados_solo = vision.extract_data(caminho_arquivo)
        else:
            print("⚠️ Arquivo 'analise_teste.jpg' não encontrado. Usando DADOS MOCK para teste.")
            dados_solo = {
                "fisica": {"argila": 40.0, "areia": 50.0},
                "quimica": {
                    "ph_cacl2": 4.8, "fosforo_mg": 4.0, "potassio_mg": 35.0,
                    "calcio_cmolc": 1.2, "magnesio_cmolc": 0.4, "aluminio_cmolc": 0.3,
                    "ctc_total": 8.0, "v_percentual": 35.0
                },
                "micronutrientes": {"boro": 0.1, "zinco": 0.5}
            }
    except Exception as e:
        print(f"⚠️ Erro Vision: {e}. Usando dados Mock.")
        dados_solo = {
                "fisica": {"argila": 40.0, "areia": 50.0},
                "quimica": {
                    "ph_cacl2": 4.8, "fosforo_mg": 4.0, "potassio_mg": 35.0,
                    "calcio_cmolc": 1.2, "magnesio_cmolc": 0.4, "aluminio_cmolc": 0.3,
                    "ctc_total": 8.0, "v_percentual": 35.0
                }
        }

    if not dados_solo:
        print("❌ Falha crítica: Dados do solo vazios.")
        return
    
    # 3. Motor Agronômico
    cultura_selecionada = "Soja" # Teste padrão
    print(f"🧠 Processando recomendação para: {cultura_selecionada}...")
    
    try:
        motor = AgroBotEngine(dados_solo, cultura_selecionada)
        resultado = motor.processar()
    except Exception as e:
        print(f"❌ Erro no Motor: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Exibe Resultado Detalhado
    print("\n" + "="*60)
    print("📄 LAUDO TÉCNICO AGROBOT - INTEGRADO")
    print("="*60)
    
    diag = resultado['diagnostico']
    rec = resultado['recomendacao']
    
    print(f"\n1. DIAGNÓSTICO DO SOLO")
    print(f"   - pH (CaCl2): {motor.solo['ph_cacl2']} -> {diag.get('ph')}")
    print(f"   - Fósforo: {motor.solo['P']} mg/dm³ -> {diag.get('P')}")
    print(f"   - Potássio: {motor.solo['K']} mg/dm³ -> {diag.get('K')}")
    print(f"   - V%: {motor.solo['V']}% -> {diag.get('V')}")
    print(f"   - Matéria Orgânica: {motor.solo['MO']} g/dm³ -> {diag.get('MO')}")
    if 'Zn' in diag:
        print(f"   - Zinco: {motor.solo['Zn']} -> {diag.get('Zn')}")
    
    print(f"\n2. CORREÇÃO (CALAGEM)")
    cal = rec['calagem']
    print(f"   - Dose Recomendada: {cal['dose_t_ha']} ton/ha (PRNT {cal['prnt']}%)")
    print(f"   - Método Escolhido: {cal['metodo_utilizado']}")
    print(f"   - Detalhes Cálculo: {cal['detalhes']}")
    
    print(f"\n3. ADUBAÇÃO ({cultura_selecionada.upper()})")
    adub = rec['adubacao']
    print(f"   - Origem: {adub['origem']}")
    print(f"   - Nitrogênio (N): {adub['N']} kg/ha")
    print(f"   - Fósforo (P2O5): {adub['P2O5']} kg/ha")
    print(f"   - Potássio (K2O): {adub['K2O']} kg/ha")
    print(f"   - Enxofre (S): {adub['S']} kg/ha")
    
    if adub['obs']:
        print(f"\n   ⚠️ OBSERVAÇÕES:")
        for obs in adub['obs']:
            print(f"   - {obs}")
            
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
