import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agrobot.vision import GeminiVision
from agrobot.engine import AgroEnginePro

def testar_motor_agronomico():
    """Testa o motor agronômico com dados de exemplo"""
    print("🧪 TESTANDO MOTOR AGRONÔMICO")
    print("=" * 60)
    
    # Dados de exemplo (formato manual)
    dados_manuais = {
        'ph_cacl2': 5.3,
        'argila': 33.6,
        'fosforo_mg': 5.7,
        'potassio_mg': 47.5,
        'materia_organica': 17.4,
        'calcio_cmolc': 1.0,
        'magnesio_cmolc': 0.41,
        'aluminio_cmolc': 0.33
    }
    
    # Calcular valores derivados
    ca = dados_manuais['calcio_cmolc']
    mg = dados_manuais['magnesio_cmolc']
    k_mg = dados_manuais['potassio_mg']
    k_cmolc = k_mg / 391
    al = dados_manuais['aluminio_cmolc']
    
    # CTC aproximada
    ctc_aproximada = ca + mg + k_cmolc + al
    h_al_aproximado = ctc_aproximada * 0.3
    
    # Adicionar valores calculados
    dados_manuais['h_al_cmolc'] = round(h_al_aproximado, 2)
    dados_manuais['ctc_total'] = round(ctc_aproximada + h_al_aproximado, 2)
    
    # Calcular V% e m%
    v_percentual = round(((ca + mg + k_cmolc) / ctc_aproximada) * 100, 1)
    m_percentual = round((al / ctc_aproximada) * 100, 1)
    
    dados_manuais['v_percentual'] = v_percentual
    dados_manuais['m_percentual'] = m_percentual
    
    print("📊 Dados de entrada:")
    for chave, valor in dados_manuais.items():
        print(f"  {chave}: {valor}")
    
    # Dados do usuário
    dados_usuario = {
        'nome': 'Produtor Teste',
        'propriedade': 'Fazenda Esperança',
        'cultura': 'Soja',
        'expectativa': 'Média (60-70 sc/ha)'
    }
    
    # Formatar para o engine
    dados_solo = {
        'fisica': {
            'argila': dados_manuais['argila'],
            'areia': 0,
            'silte': 0
        },
        'quimica': {
            'ph_cacl2': dados_manuais['ph_cacl2'],
            'ph_agua': 0,
            'fosforo_mg': dados_manuais['fosforo_mg'],
            'potassio_mg': dados_manuais['potassio_mg'],
            'calcio_cmolc': dados_manuais['calcio_cmolc'],
            'magnesio_cmolc': dados_manuais['magnesio_cmolc'],
            'aluminio_cmolc': dados_manuais['aluminio_cmolc'],
            'h_al_cmolc': dados_manuais['h_al_cmolc'],
            'ctc_total': dados_manuais['ctc_total'],
            'v_percentual': dados_manuais['v_percentual'],
            'm_percentual': dados_manuais['m_percentual'],
            'materia_organica': dados_manuais['materia_organica']
        },
        'micronutrientes': {
            'enxofre': 0,
            'boro': 0,
            'zinco': 0,
            'cobre': 0,
            'manganes': 0,
            'ferro': 0
        }
    }
    
    try:
        # Criar e processar
        engine = AgroEnginePro(dados_solo, dados_usuario)
        resultado = engine.processar()
        
        if resultado.get("status") == "SUCESSO":
            print("\n✅ PROCESSAMENTO BEM-SUCEDIDO!")
            print("=" * 60)
            
            # Mostrar diagnóstico
            print("\n🔬 DIAGNÓSTICO:")
            diag = resultado['diagnostico']
            for param, valor in diag.items():
                print(f"  {param}: {valor}")
            
            # Mostrar calagem
            cal = resultado['calagem']
            print(f"\n🧪 CALAGEM: {cal['dose_t_ha']} t/ha")
            print(f"   Método: {cal['metodo_utilizado']}")
            
            # Mostrar adubação
            adub = resultado['adubacao']
            print(f"\n💰 ADUBAÇÃO:")
            print(f"   N: {adub['N']} kg/ha")
            print(f"   P₂O₅: {adub['P2O5']} kg/ha")
            print(f"   K₂O: {adub['K2O']} kg/ha")
            print(f"   S: {adub['S']} kg/ha")
            
            # Mostrar formulação
            form = resultado['formulacao']
            if form:
                print(f"\n🧪 FORMULAÇÃO SUGERIDA: {form.get('sugestao', 'N/A')}")
            
        else:
            print("\n❌ ERRO NO PROCESSAMENTO")
            print(resultado.get("mensagens", ["Erro desconhecido"]))
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

def testar_vision():
    """Testa o sistema de visão"""
    print("\n👁️  TESTANDO SISTEMA DE VISÃO")
    print("=" * 60)
    
    arquivo_teste = "analise_teste.jpg"
    
    if os.path.exists(arquivo_teste):
        try:
            vision = GeminiVision()
            print(f"📤 Processando: {arquivo_teste}")
            dados = vision.extract_data(arquivo_teste)
            
            if dados:
                print("✅ Dados extraídos com sucesso!")
                print(json.dumps(dados, indent=2, ensure_ascii=False))
            else:
                print("❌ Falha na extração de dados")
        except Exception as e:
            print(f"❌ Erro: {e}")
    else:
        print(f"⚠️ Arquivo '{arquivo_teste}' não encontrado")
        print("Criando dados mock para teste...")
        
        # Dados mock
        dados_mock = {
            "fisica": {"argila": 35.0, "areia": 45.0, "silte": 20.0},
            "quimica": {
                "ph_cacl2": 5.2, "ph_agua": 5.8,
                "fosforo_mg": 8.5, "potassio_mg": 45.0,
                "calcio_cmolc": 2.1, "magnesio_cmolc": 0.8,
                "aluminio_cmolc": 0.5, "h_al_cmolc": 3.5,
                "ctc_total": 7.0, "v_percentual": 45.0,
                "m_percentual": 12.5, "materia_organica": 25.0
            },
            "micronutrientes": {
                "enxofre": 10.0, "boro": 0.5, "zinco": 2.0,
                "cobre": 1.5, "manganes": 15.0, "ferro": 30.0
            }
        }
        
        print(json.dumps(dados_mock, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("🚜 AGROBOT V7 - SISTEMA DE TESTE")
    print("👨‍🌾 Por Jonnathan Marques, Eng. Agrônomo")
    print("=" * 60)
    
    testar_motor_agronomico()
    testar_vision()
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
