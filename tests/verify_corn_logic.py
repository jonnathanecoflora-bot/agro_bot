
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from agrobot.engine import AgroEnginePro, COMMERCIAL_FORMULAS, parse_formula

def verify_corn():
    print("="*60)
    print("TESTE DE LOGICA: MILHO (CORN CHECK)")
    print("="*60)
    
    # DADOS DE ENTRADA (MOCK)
    # Solo "Pobre" para forçar altas demandas
    dados_solo = {
        "quimica": {
            "ph_cacl2": 4.8, 
            "ph_agua": 5.2, # Added so fixation check works
            "hidrogenio_cmolc": 4.0,
            "aluminio_cmolc": 0.8,
            "calcio_cmolc": 1.2,
            "magnesio_cmolc": 0.5,
            "potassio_mg": 30, # Baixo K
            "fosforo_mg": 4,   # Baixo P
            "materia_organica": 20
        },
        "fisica": {
            "argila": 450 # Argiloso
        }
    }
    
    dados_usuario = {
        "nome": "Agro Corn Check",
        "cultura": "Milho Safrinha", 
        "expectativa": "Alta Tecnologia",
        "propriedade": "Fazenda Modelo"
    }

    # Instanciar Engine
    engine = AgroEnginePro(dados_solo, dados_usuario)
    
    # Run process to init everything
    engine.processar()
    
    # FORCE DEMAND NPK (Simulation of User Request constraints)
    print("\n[FORCING DEMAND FOR TEST]: 160N - 100P - 150K")
    engine.recomendacao['N'] = 160
    engine.recomendacao['P2O5'] = 100
    engine.recomendacao['K2O'] = 150 # Force high K demand to test KCl
    
    # Re-run formulation LOGIC ONLY
    form = engine.calcular_formulacao()
    # No need to store back in engine for this test
    # engine.resultado_final['formulacao'] = form 
    
    print("\n[DEMANDA FINAL]:")
    print(f"N: {engine.recomendacao['N']} kg/ha")
    print(f"P2O5: {engine.recomendacao['P2O5']} kg/ha")
    print(f"K2O: {engine.recomendacao['K2O']} kg/ha")
    
    # 1. VERIFICAR PLANTIO (Deve ter Nitrogênio)
    print("\n[1. CHECK PLANTIO]")
    plantio_str = form['plano']['plantio']['formula']
    print(f"Fórmula Escolhida: {plantio_str}")
    
    fN, fP, fK = parse_formula(plantio_str)
    
    if fN > 0:
        print("[PASS] Fórmula tem Nitrogênio (Regra de Gramíneas).")
    else:
        print("[FAIL] Fórmula SEM Nitrogênio (Erro Crítico para Gramíneas).")
        
    # 2. VERIFICAR COBERTURA (Deve ter Ureia e KCl)
    print("\n[2. CHECK COBERTURA]")
    items = form['plano']['cobertura']
    tem_ureia = any('Ureia' in item['nome'] for item in items)
    tem_kcl = any('KCl' in item['nome'] for item in items)
    
    if tem_ureia:
        print("[PASS] Recomendou Ureia para déficit de N.")
    else:
        print(f"[FAIL] Não recomendou Ureia! (Déficit N esperado)")
        
    if tem_kcl:
        print("[PASS] Recomendou KCl para déficit de K.")
    else:
         print(f"[FAIL] Não recomendou KCl! (Déficit K esperado)")

    # 3. VERIFICAR FORMATO TEXTO
    print("\n[3. CHECK TEXTO]")
    txt = form['texto_completo']
    print(f"Texto: {txt}")
    
    # Updated: Case sensitive per implementation
    if "PLANTIO:" in txt and "COBERTURA" in txt:
        print("[PASS] Formato String OK.")
    else:
        print("[FAIL] Formato String Inválido.")

    # 4. VERIFICAR TEXTO CIENTIFICO
    print("\n[4. CHECK DISCUSSÃO CIENTÍFICA]")
    interp = engine.gerar_discussao_cientifica() # Updated method name
    print(interp[:400] + "...")
    
    keywords = ["fixação", "antagonismo", "lixiviação", "mandatória"]
    # Check simple presence
    score = 0
    for k in keywords:
        if k in interp.lower(): score += 1
        
    if score >= 2:
        print(f"[PASS] Texto Contém termos técnicos avançados ({score}/4).")
    else:
        print(f"[FAIL] Texto parece genérico. Score: {score}")

if __name__ == "__main__":
    verify_corn()
