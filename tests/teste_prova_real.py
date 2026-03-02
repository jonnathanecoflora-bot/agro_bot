
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from agrobot.engine import AgroEnginePro, COMMERCIAL_FORMULAS

def run_test():
    print("="*60)
    print("TESTE PROVA REAL: SOLO ACIDO CRITICO & FORMULAS COMERCIAIS")
    print("="*60)
    
    # DADOS DE ENTRADA (MOCK)
    dados_solo = {
        "quimica": {
            "ph_cacl2": 4.5,
            "hidrogenio_cmolc": 5.2,
            "aluminio_cmolc": 1.0,
            "calcio_cmolc": 1.5,
            "magnesio_cmolc": 0.5,
            "potassio_mg": 39,
            "fosforo_mg": 6,
            "materia_organica": 25 # Adding reasonable MO
        },
        "fisica": {
            "argila": 600 # 600 g/kg
        }
    }
    
    dados_usuario = {
        "nome": "Validação Final",
        "cultura": "Milho",
        "expectativa": "Alta Produtividade",
        "propriedade": "Fazenda Teste"
    }

    print("\n[INPUT DADOS]:")
    print(f"pH: {dados_solo['quimica']['ph_cacl2']}")
    print(f"H: {dados_solo['quimica']['hidrogenio_cmolc']}")
    print(f"Al: {dados_solo['quimica']['aluminio_cmolc']}")
    print(f"Argila: {dados_solo['fisica']['argila']} g/kg")
    
    # Instanciar Engine
    engine = AgroEnginePro(dados_solo, dados_usuario)
    resultado = engine.processar()
    
    solo_proc = resultado['solo']
    diag = resultado['diagnostico']
    adub = resultado['adubacao']
    form = resultado['formulacao']
    
    # 1. CHECAGEM DA ARGILA
    print("\n[1. CHECAGEM DA ARGILA]")
    print(f"Original: 600 -> Processado: {solo_proc['argila']}%")
    if solo_proc['argila'] == 60.0:
        print("[PASS]")
    else:
        print(f"[FAIL] (Esperado 60.0)")

    # 2. CHECAGEM DA CTC
    print("\n[2. CHECAGEM DA CTC]")
    sb = solo_proc['SB']
    h_al = solo_proc['H_Al']
    ctc = solo_proc['CTC']
    print(f"SB: {sb} (Ca+Mg+K)")
    print(f"H+Al: {h_al} (Esperado: 5.2 + 1.0 = 6.2)") 
    # Note: User prompt said H=5.2, Al=1.0. 
    # Logic: If H explicit > 0, H_Al = H + Al. So 5.2 + 1.0 = 6.2.
    # User prompt 'Expected CTC ~8.3' => SB (1.5+0.5+0.1=2.1) + H+Al (6.2) = 8.3.
    
    if abs(h_al - 6.2) < 0.1:
        print(f"[PASS] H+Al calculado corretamente: {h_al}")
    else:
        print(f"[FAIL] H+Al incorreto: {h_al} (Esperado 6.2)")
        
    print(f"CTC Calculada: {ctc}")
    if abs(ctc - 8.3) < 0.2:
        print("[PASS] CTC PASS")
    else:
        print("[FAIL] CTC FAIL")

    # 3. CHECAGEM V%
    print("\n[3. CHECAGEM V%]")
    v_calc = solo_proc['V']
    v_esp = (sb / ctc) * 100 if ctc > 0 else 0
    print(f"V% Engine: {v_calc}%")
    print(f"V% Esperado: {v_esp:.1f}%")
    
    if abs(v_calc - v_esp) < 1.0 and v_calc < 30:
        print("[PASS] V% PASS (Baixo, coerente com solo ácido)")
    elif v_calc > 90:
        print("[FAIL] CRITICAL FAIL: V% estourou para ~100% (Erro de Acidez Zerada!)")
    else:
        print("[WARN] V% Divergente")

    # 4. CHECAGEM NPK
    print("\n[4. CHECAGEM FORMULACAO]")
    sugestao = form.get('sugestao', 'N/A')
    print(f"Fórmula Escolhida: {sugestao}")
    
    # Validar se está na lista
    validas = COMMERCIAL_FORMULAS['semeadura']
    if sugestao in validas:
        print(f"[PASS]: Fórmula '{sugestao}' existe na base comercial.")
    else:
        print(f"[FAIL]: Fórmula '{sugestao}' NÃO encontrada na lista permitida!")
        print(f"List: {validas}")

    print("\n[TEXTO GERADO (Trecho)]:")
    print(form.get('texto_completo', '')[:200] + "...")
    
    # GERAR PDF
    print("\n[GERANDO PDF DE VALIDACAO...]")
    from agrobot.pdf_generator import AgroPDFPro
    pdf_gen = AgroPDFPro()
    path = pdf_gen.gerar_pdf(resultado)
    print(f"PDF Gerado em: {path}")

if __name__ == "__main__":
    run_test()
