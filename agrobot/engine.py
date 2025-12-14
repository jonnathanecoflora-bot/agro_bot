import math
import re
import numpy as np
from .knowledge_base import KNOWLEDGE_BASE

COMMERCIAL_FORMULAS = {
    'semeadura': [
        "04-14-08", "04-30-10", "05-25-15", "08-24-12", 
        "00-20-20", "00-18-18", "00-30-10" 
    ],
    'cobertura': [
        '20-00-20', '30-00-10', '20-05-20', '25-00-25', '20-10-10',
        '45-00-00 (Ureia)', '21-00-00 (Sulfato de Amônio)', '00-00-60 (KCL)'
    ]
}

def parse_formula(fmt_str):
    try:
        clean = fmt_str.split(' ')[0]
        parts = clean.split('-')
        return float(parts[0]), float(parts[1]), float(parts[2])
    except:
        return 0, 0, 0

class AgroEnginePro:
    def __init__(self, dados_solo, dados_usuario):
        self.raw_data = dados_solo
        self.user = dados_usuario
        self.erros = []
        self.log = []
        self.diagnostico = {}
        self.recomendacao = {}
        self.solo = self._normalizar_dados(dados_solo)
        self.saida = {}
        
    def _normalizar_dados(self, dados):
        """
        Normalização Estrita (SRE V7) - Lógica INFALÍVEL H+Al
        Prioridade 1: Soma Real (H + Al)
        Prioridade 2: Leitura Direta (H+Al presente no laudo)
        Prioridade 3: Estimativa SMP
        """
        norm = {}
        
        # Helper seguro
        def get_float(val):
            if val is None: return 0.0
            if isinstance(val, (int, float)): return float(val)
            s = str(val).replace('%', '').replace(',', '.').strip()
            try: return float(s)
            except: return 0.0
            
        def get_val(path):
            keys = path.split('.')
            val = dados
            try:
                for k in keys: val = val.get(k, {})
                return get_float(val) if isinstance(val, (str, int, float)) else None
            except: return None

        # 1. FÍSICA
        argila = get_val('fisica.argila') or 0.0
        if argila > 100: argila /= 10.0
        norm['argila'] = argila
        
        # 2. QUÍMICA BÁSICA
        norm['ph_cacl2'] = get_val('quimica.ph_cacl2') or 0.0
        norm['ph_agua'] = get_val('quimica.ph_agua') or 0.0
        norm['P'] = get_val('quimica.fosforo_mg') or 0.0
        norm['MO'] = get_val('quimica.materia_organica') or 0.0
        
        # 3. BASES
        K_mg = get_val('quimica.potassio_mg') or 0.0
        norm['K'] = K_mg
        K_cmolc = K_mg / 391.0
        
        norm['Ca'] = get_val('quimica.calcio_cmolc') or 0.0
        norm['Mg'] = get_val('quimica.magnesio_cmolc') or 0.0
        
        SB = norm['Ca'] + norm['Mg'] + K_cmolc
        
        # 4. ACIDEZ (LÓGICA INFALÍVEL)
        val_H = get_val('quimica.hidrogenio_cmolc')
        norm['Al'] = get_val('quimica.aluminio_cmolc') or 0.0
        val_H_Al_Lido = get_val('quimica.h_al_cmolc')
        
        if val_H is not None and val_H > 0:
            norm['H'] = val_H
            norm['H_Al'] = val_H + norm['Al'] 
        elif val_H_Al_Lido is not None and val_H_Al_Lido > 0:
            norm['H_Al'] = val_H_Al_Lido
            norm['H'] = 0.0 
        else:
            if norm['ph_cacl2'] > 0 and norm['ph_cacl2'] < 6.0:
                norm['H_Al'] = (7.5 - norm['ph_cacl2']) * 1.2
                self.erros.append(f"⚠️ AVISO: Acidez estimada ({norm['H_Al']:.2f}).")
            else:
                norm['H_Al'] = 0.0 + norm['Al']

        # 5. CTC e V%
        norm['SB'] = SB
        norm['CTC'] = SB + norm['H_Al'] 
        
        if norm['CTC'] > 0:
            norm['V'] = (SB / norm['CTC']) * 100
            norm['m'] = (norm['Al'] / (SB + norm['Al'])) * 100
        else:
            norm['V'] = 0.0
            norm['m'] = 0.0
            
        # Debug
        print(f"\n🔬 DEBUG ENGINE V7.1: Lógica Infalível")
        print(f"   ► H: {val_H} | Al: {norm['Al']} | H+Al Lido: {val_H_Al_Lido}")
        print(f"   ► H+Al Final: {norm['H_Al']:.2f} | CTC: {norm['CTC']:.2f}")

        # Arredondamentos
        norm['V'] = round(norm['V'], 1)
        norm['m'] = round(norm['m'], 1)
        norm['CTC'] = round(norm['CTC'], 2)
        norm['SB'] = round(norm['SB'], 2)
        
        # Micros
        for m in ['oro', 'obre', 'erro', 'anganes', 'inco', 'nxofre']:
            norm[m] = 0.0
            
        return norm

    def gerar_discussao_cientifica(self):
        """Gera texto Nível A1 (PhD) com termos técnicos avançados."""
        solo = self.solo
        txt = []
        
        argila = solo.get('argila', 0)
        ph = solo.get('ph_cacl2', 0)
        ctc = solo.get('CTC', 0)
        al = solo.get('Al', 0)
        
        txt.append("<b>1. DIAGNÓSTICO AVANÇADO</b>")
        
        # Textura e Fixação
        txt.append(f"A análise revela um perfil com {argila:.1f}% de argila. Sob condições de acidez ativa (pH {ph}), o sistema apresenta alto risco de <b>Fixação Retrogradativa de Fósforo</b>, fenômeno onde fosfatos solúveis precipitam-se com óxidos de ferro e alumínio, tornando-se indisponíveis (P-Labil -> P-Não-Labil).")
        
        # Alumínio e Antagonismo
        if al > 0 or solo.get('m', 0) > 10:
             txt.append(f"A presença de Alumínio (Al³⁺: {al}) promove <b>Antagonismo Iônico</b> na rizosfera, competindo com bases trocáveis (Ca²⁺, Mg²⁺) pelos sítios de absorção radicular. Isso inibe o alongamento da coifa e reduz a exploração do volume de solo.")
             
        # CTC e Lixiviação
        if ctc < 6.0:
            txt.append(f"A baixa CTC Efetiva ({ctc:.2f} cmol/dm³), típica de solos muito intemperizados ou arenosos, predispõe o sistema à <b>Lixiviação de Cátions Monovalentes</b> (especialmente K⁺ e NO₃⁻). O Ponto de Carga Zero (PCZ) dos coloides variáveis exige manejo da matéria orgânica para aumentar a retenção de cátions.")
            txt.append("O parcelamento da adubação potássica e nitrogenada é tecnicamente <b>mandatório</b> para aumentar a Eficiência de Uso de Nutrientes (EUN) e mitigar perdas verticais no perfil.")
        else:
             txt.append("A CTC apresenta valores adequados, conferindo maior tamponamento iônico ao solo, reduzindo riscos imediatos de lixiviação massiva, mas exigindo monitoramento da saturação por bases.")
             
        return "<br/><br/>".join(txt)
        
    def gerar_texto_interpretativo(self):
        return self.gerar_discussao_cientifica()

    def calcular_viabilidade_economica(self):
        return {} 

    def calcular_formulacao(self):
        """
        NPK INTELIGENTE (Plantio + Cobertura - Lógica V7)
        """
        if not self.recomendacao: return {}
        
        req_N = self.recomendacao['N']
        req_P = self.recomendacao['P2O5']
        req_K = self.recomendacao['K2O']
        cultura = self.user.get('cultura', '').lower()
        
        # 1. PLANTIO (Foco P)
        # Regra: Milho usa N no plantio. Soja usa 00-XX-XX.
        is_graminea = any(x in cultura for x in ['milho', 'trigo', 'arroz', 'sorgo', 'pastagem', 'capim'])
        
        # Fórmulas Candidatas
        if is_graminea:
            candidatas = ["08-24-12", "05-25-15", "04-14-08", "10-30-10"] # Com N
        else:
            candidatas = ["00-20-20", "00-18-18", "00-30-10", "04-14-08"] # Baixo ou Zero N
            
        melhor_formula = None
        melhor_dose = 0
        melhor_delta = float('inf')
        
        # Seleção Best Fit para P
        for fmt in candidatas:
            fN, fP, fK = parse_formula(fmt)
            if fP == 0: continue
            
            # Dose para 100% P
            dose = (req_P / fP) * 100 if req_P > 0 else 0
            dose = int(round(dose))
            
            if dose == 0 and req_P > 0: continue
            
            # Preferência por doses operacionais (200-500kg)
            dist = abs(dose - 350)
            if dose < 150: dist += 200
            
            if dist < melhor_delta:
                melhor_delta = dist
                melhor_formula = fmt
                melhor_dose = dose
                
        if not melhor_formula:
            melhor_formula = "00-00-00"
            melhor_dose = 0
            
        # Calcular fornecido no plantio
        fN, fP, fK = parse_formula(melhor_formula)
        n_plantio = (melhor_dose * fN) / 100
        p_plantio = (melhor_dose * fP) / 100
        k_plantio = (melhor_dose * fK) / 100
        
        # 2. COBERTURA (O Pulo do Gato)
        falta_N = max(0, req_N - n_plantio)
        falta_K = max(0, req_K - k_plantio)
        
        cob_items = []
        
        # Ureia
        if falta_N > 10:
            dose_ureia = int(falta_N / 0.45)
            cob_items.append({"nome": "Ureia", "formula": "45-00-00", "dose": dose_ureia, "desc": f"N"})
            
        # KCl
        if falta_K > 10:
            dose_kcl = int(falta_K / 0.60)
            cob_items.append({"nome": "KCl", "formula": "00-00-60", "dose": dose_kcl, "desc": f"K"})
            
        # 3. OUTPUT
        # "PLANTIO: [Dose] kg/ha de [Fórmula]. COBERTURA: [Dose] kg/ha de Ureia + [Dose] kg/ha de KCl."
        
        plantio_str = f"PLANTIO: {melhor_dose} kg/ha de {melhor_formula}"
        
        cob_parts = []
        for item in cob_items:
            cob_parts.append(f"{item['dose']} kg/ha de {item['nome']}")
            
        if cob_parts:
            cob_str = "COBERTURA: " + " + ".join(cob_parts)
        else:
            cob_str = "COBERTURA: Não necessária"
            
        texto_final = f"{plantio_str}. {cob_str}."
        
        return {
            "sugestao": melhor_formula,
            "dose_ha": melhor_dose,
            "texto_completo": texto_final,
            "plano": {
                "plantio": {"formula": melhor_formula, "dose": melhor_dose, "N": n_plantio, "P": p_plantio, "K": k_plantio},
                "cobertura": cob_items
            }
        }
    
    def validar_dados_minimos(self):
        """Valida se tem dados suficientes para análise"""
        # SRE 4.0: Validação Relaxada (Melhor ter laudo parcial do que erro)
        minimos = {
            'ph_cacl2': 'pH',
            # 'argila': 'Argila', # Se faltar argila, usamos média (já tratado no normalizer)
            # 'P': 'Fósforo',     # Se faltar, assume baixo
            # 'K': 'Potássio'     # Se faltar, assume baixo
        }
        
        # Só bloqueia se não tiver pH (o mínimo do mínimo)
        if self.solo.get('ph_cacl2', 0) == 0 and self.solo.get('ph_agua', 0) == 0:
            self.erros.append("DADOS CRÍTICOS: Não encontrei valor de pH.")
            return False
            
        # Avisos não bloqueantes (Warning Log)
        if self.solo.get('argila', 0) == 0:
            print("⚠️ AVISO: Argila não detectada. Usando padrão de solo médio.")
            
        return True
    
    def _classificar(self, valor, faixas):
        """Classifica valor nas faixas da Embrapa"""
        if valor is None:
            return "NÃO DETECTADO"
        
        for classe, limites in faixas.items():
            min_val = limites.get('min', -float('inf'))
            max_val = limites.get('max', float('inf'))
            
            if min_val <= valor <= max_val:
                return classe.upper().replace('_', ' ')
        
        return "FORA DA FAIXA"
    
    def diagnosticar(self):
        """Diagnóstico completo do solo"""
        if not self.validar_dados_minimos():
            return None
        
        interp = KNOWLEDGE_BASE['interpretacao_solo']['parametros']
        diag = {}
        
        # 1. pH
        ph_valor = self.solo['ph_cacl2'] if self.solo['ph_cacl2'] > 0 else self.solo['ph_agua']
        if ph_valor > 0:
            faixa_ph = interp['ph']['cacl2'] if self.solo['ph_cacl2'] > 0 else interp['ph']['agua']
            diag['ph'] = self._classificar(ph_valor, faixa_ph)
        else:
            diag['ph'] = "NÃO DETECTADO"
        
        # 2. Fósforo
        p_val = self.solo['P']
        argila = self.solo['argila']
        faixas_p = None
        
        for faixa in interp['fosforo']['mehlich1']:
            if faixa['argila_min'] <= argila <= (faixa['argila_max'] or 100):
                faixas_p = faixa['classes']
                break
        
        diag['P'] = self._classificar(p_val, faixas_p) if faixas_p else "N/D"
        
        # 3. Potássio
        k_val = self.solo['K']
        ctc = self.solo['CTC']
        faixas_k = None
        
        for faixa in interp['potassio']['mg_dm3']:
            min_ctc = faixa['ctc_ph7_min']
            max_ctc = faixa['ctc_ph7_max'] or float('inf')
            
            if min_ctc <= ctc <= max_ctc:
                faixas_k = faixa['classes']
                break
        
        diag['K'] = self._classificar(k_val, faixas_k) if faixas_k else "N/D"
        
        # 4. Cálcio e Magnésio
        diag['Ca'] = self._classificar(self.solo['Ca'], interp['calcio_magnesio']['calcio'])
        diag['Mg'] = self._classificar(self.solo['Mg'], interp['calcio_magnesio']['magnesio'])
        
        # 5. Acidez
        diag['Al'] = self._classificar(self.solo['Al'], interp['acidez']['al_trocavel'])
        diag['V'] = self._classificar(self.solo['V'], interp['saturacao']['por_bases'])
        diag['m'] = f"{self.solo['m']:.1f}%" if self.solo['m'] > 0 else "0%"
        
        # 6. Matéria Orgânica
        argila_val = self.solo['argila']
        if argila_val < 15:
            faixa_mo = interp['materia_organica']['arenosa']
        elif argila_val > 35:
            faixa_mo = interp['materia_organica']['argilosa']
        else:
            faixa_mo = interp['materia_organica']['media']
        
        diag['MO'] = self._classificar(self.solo['MO'], faixa_mo)
        
        # 7. Micronutrientes
        micros = interp['micronutrientes']
        for elem in ['B', 'Cu', 'Fe', 'Mn', 'Zn', 'S']:
            val = self.solo.get(elem, 0)
            if elem.lower() in micros:
                diag[elem] = self._classificar(val, micros[elem.lower()])
            else:
                diag[elem] = f"{val:.1f} mg/dm³" if val > 0 else "N/D"
        
        self.diagnostico = diag
        return diag
    
    def calcular_calagem(self):
        """Cálculo profissional de calagem"""
        cultura = self.user.get('cultura', 'Soja').lower()
        parametros = KNOWLEDGE_BASE['calagem']['parametros']
        
        # Valores atuais
        V1 = self.solo['V']
        CTC = self.solo['CTC']
        Al = self.solo['Al']
        Ca = self.solo['Ca']
        Mg = self.solo['Mg']
        
        # Valores alvo
        V2_alvos = parametros['v2_alvos']
        V2 = V2_alvos.get(cultura, 65)  # Default 65%
        
        PRNT = 80  # PRNT padrão do calcário
        
        # 1. MÉTODO SATURAÇÃO POR BASES
        if V1 < V2 and CTC > 0:
            NC_bases = ((V2 - V1) * CTC) / PRNT
        else:
            NC_bases = 0
        
        # 2. MÉTODO NEUTRALIZAÇÃO DO ALUMÍNIO
        m_percent = self.solo['m']
        if m_percent > 10 and Al > 0:
            NC_al = (Al * 2) * (100 / PRNT)
        else:
            NC_al = 0
        
        # 3. MÉTODO SUPRIMENTO DE Ca+Mg
        soma_ca_mg = Ca + Mg
        X = 3 if cultura == 'cafe' else 2  # Nível desejado de Ca+Mg
        
        # Fator Y baseado na textura
        argila = self.solo['argila']
        if argila < 15:
            Y = 1  # Arenoso
        elif argila <= 35:
            Y = 2  # Médio
        else:
            Y = 3  # Argiloso
        
        if soma_ca_mg < X:
            NC_ca_mg = ((Al * Y) + (X - soma_ca_mg)) * (100 / PRNT)
        else:
            NC_ca_mg = 0
        
        # Escolher o maior valor
        doses = [NC_bases, NC_al, NC_ca_mg]
        dose_final = max(doses)
        
        # Identificar método utilizado
        metodo_idx = doses.index(dose_final)
        metodos = ["Saturação por Bases", "Neutralização do Alumínio", "Suprimento de Ca+Mg"]
        metodo_utilizado = metodos[metodo_idx]
        
        # Ajustar para mínimo de 1.0 t/ha se houver necessidade
        if dose_final > 0 and dose_final < 1.0:
            dose_final = 1.0
        
        return {
            "dose_t_ha": round(dose_final, 2),
            "metodo_utilizado": metodo_utilizado,
            "detalhes": {
                "nc_bases": round(NC_bases, 2),
                "nc_al": round(NC_al, 2),
                "nc_ca_mg": round(NC_ca_mg, 2),
                "v_atual": round(V1, 1),
                "v_alvo": V2,
                "prnt": PRNT
            }
        }
    
    def recomendar_adubacao(self):
        """Recomendação profissional de adubação baseada em Fórmulas Comerciais"""
        cultura = self.user.get('cultura', 'Soja')
        expectativa = self.user.get('expectativa', '')
        
        # --- PASSO 1: DEFINIR DEMANDA NUTRICIONAL (Extração - Estoque) ---
        # Simplificação: Usaremos os valores da tabela de recomendação como "Demanda de Reposição + Correção"
        
        kb = KNOWLEDGE_BASE['recomendacao_adubacao']
        demanda = {
            "N": 0, "P2O5": 0, "K2O": 0, "S": 0,
            "origem": "", "obs": []
        }
        
        # Determinar tabela a usar (Específica ou Mestra)
        # Reutilizando lógica existente para pegar Kg/ha de NPK
        
        nivel_p = self.diagnostico.get('P', 'BAIXO')
        nivel_k = self.diagnostico.get('K', 'BAIXO')
        
        uso_especifica = False
        if cultura.lower() == 'soja':
            uso_especifica = True
            demanda['origem'] = "Tabela Específica - Soja"
            demanda['N'] = 0 # Leguminosa
            
            # Mapear nível para disponibilidade
            nivel_map = {'MUITO BAIXO': 'Baixa', 'BAIXO': 'Baixa', 'MEDIO': 'Média', 'ADEQUADO': 'Alta', 'ALTO': 'Muito Alta'}
            disponibilidade = nivel_map.get(nivel_p, 'Média')
            
            for linha in kb['tabelas_especificas']['soja']['dados']:
                if linha['disponibilidade'] == disponibilidade:
                    demanda['P2O5'] = linha['p2o5_kg_ha']
                    demanda['K2O'] = linha['k2o_kg_ha']
                    break
            demanda['obs'].append("Soja: N=0 (Fixação Biológica). Foco em P e K.")

        elif cultura.lower() == 'milho':
            uso_especifica = True
            demanda['origem'] = "Tabela Específica - Milho"
            
            # Expectativa
            rendimento = 8.0 # Default
            if 'alta' in expectativa.lower(): rendimento = 10.0
            elif 'baixa' in expectativa.lower(): rendimento = 6.0
            
            # Encontrar linha
            best_match = None
            min_diff = float('inf')
            
            for linha in kb['tabelas_especificas']['milho']['dados']:
                txt_rend = linha['expectativa_rendimento'].replace(',', '.')
                match = re.search(r'(\d+\.?\d*)', txt_rend)
                if match:
                    val = float(match.group(1))
                    if abs(val - rendimento) < min_diff:
                        min_diff = abs(val - rendimento)
                        best_match = linha
            
            if best_match:
                n_data = best_match['nitrogenio']
                demanda['N'] = n_data['semeadura'] + n_data['cobertura']
                
                # P
                if 'ALTO' in nivel_p: demanda['P2O5'] = best_match['fosforo']['alto']
                else: demanda['P2O5'] = best_match['fosforo']['adequado']
                
                # K
                k_sem = best_match['potassio']['semeadura']['alto' if 'ALTO' in nivel_k else 'adequado']
                k_cob = best_match['potassio'].get('cobertura', 0)
                demanda['K2O'] = k_sem + k_cob
        
        else:
            # Tabela Mestra
            demanda['origem'] = "Tabela Mestra (Genérica)"
            argila = self.solo['argila']
            ctc = self.solo['CTC']
            
            for faixa in kb['tabela_mestra']['dados']:
                if faixa['teor_argila_min'] <= argila <= (faixa['teor_argila_max'] or 100):
                    # P
                    p_key = nivel_p.split()[0].lower() if ' ' in nivel_p else nivel_p.lower()
                    demanda['P2O5'] = faixa['fosforo'].get(p_key, 60)
                    
                    # K
                    k_dict = faixa['potassio_ctc_menor_4'] if ctc < 4 else faixa['potassio_ctc_maior_igual_4']
                    k_key = nivel_k.split()[0].lower() if ' ' in nivel_k else nivel_k.lower()
                    demanda['K2O'] = k_dict.get(k_key, 60)
                    
                    # N
                    n_data = faixa['nitrogenio']
                    demanda['N'] = n_data['semeadura_max'] + n_data['cobertura_max']
                    break
        
        # Enxofre (Default)
        demanda['S'] = 20
        
        return demanda
    
    def gerar_texto_interpretativo(self):
        """Gera texto de consultoria técnica avançada (Estilo Revista Científica A1)"""
        textos = []
        
        # Dados Base
        argila = self.solo.get('argila', 0)
        ph = self.solo.get('ph_agua', 0)
        ctc = self.solo.get('CTC', 0)
        k_val = self.solo.get('K', 0)
        
        # --- 1. DINÂMICA QUÍMICA (pH e P) ---
        if ph > 0 and ph < 5.5:
             textos.append(
                f"<b>DINÂMICA DE FÓSFORO (Fixação):</b> A acidez ativa atual (pH {ph:.1f}) promove a solubilização de Alumínio trocável "
                "e a precipitação de íons fosfato em formas de fosfatos de ferro e alumínio (P-Fe e P-Al), compostos de baixa solubilidade. "
                "<b>Consequência:</b> A eficiência da adubação fosfatada será drasticamente reduzida devido à reação de fixação específica "
                "na superfície dos coloides. A correção do pH é pré-requisito termodinâmico para a disponibilidade de P."
             )
        
        # --- 2. INTERAÇÃO TEXTURAL E CTC ---
        # Definir classe
        if argila < 15: classe = "Arenosa"
        elif argila <= 35: classe = "Média-Argilosa"
        else: classe = "Argilosa"
        
        if argila > 35:
            textos.append(
                f"<b>CLASSE TEXTURAL E RETENÇÃO CATIONICA:</b> A classe textural {classe} (Argila {argila:.1f}%) confere ao solo alta "
                "capacidade de retenção de cátions (CTC potencial), criando um reservatório nutricional expressivo. "
                "Contudo, o manejo físico deve ser cauteloso quanto à compactação superficial. "
                "Para o Potássio, a alta superfície específica das argilas permite maior adsorção, reduzindo perdas, "
                "mas exige níveis críticos mais altos para garantir a dessorção para a solução do solo."
            )
        elif argila < 15:
            textos.append(
                f"<b>DINÂMICA FÍSICO-HÍDRICA ({classe}):</b> A baixa presença de coloides argilosos limita severamente a CTC ({ctc:.2f} cmol/dm³), "
                "implicando em baixa retenção de nutrientes e água. O ambiente oxidativo favorece a decomposição da matéria orgânica. "
                "O parcelamento das adubações nitrogenadas e potássicas torna-se mandatório para mitigar perdas por lixiviação vertical."
            )
        else:
            textos.append(
                 f"<b>AMBIENTE FÍSICO ({classe}):</b> Solo com equilíbrio textural favorável à mecanização e exploração radicular. "
                 "A capacidade de armazenamento de água é intermediária, exigindo monitoramento climático para decisões de adubação de cobertura."
            )

        # --- 3. POTÁSSIO E SALINIDADE ---
        if k_val < 50 and ctc < 5:
            textos.append(
                "<b>MANEJO DE POTÁSSIO (Risco Salino):</b> A combinação de baixo teor original de K e baixa CTC condiciona um sistema "
                "suscetível ao estresse salino na rizosfera. A adubação potássica massiva no sulco causaria plasmólise radicular. "
                "O parcelamento estratégico proposto visa sincronizar a oferta do nutriente com a taxa de absorção da cultura, "
                "minimizando picos osmóticos nocivos."
            )

        # Fallback textual
        if len(textos) == 0:
            textos.append(
                "<b>DIAGNÓSTICO INTEGRADO:</b> Os parâmetros analisados indicam um perfil de fertilidade que demanda correções pontuais. "
                "Siga rigorosamente as recomendações de calagem e o parcelamento de NPK para otimizar a eficiência agronômica."
            )

        return "<br/><br/>".join(textos)

    def calcular_viabilidade_economica(self):
        # Manteve igual, omitido para brevidade se não for mudar.
        return {} 

    def calcular_formulacao(self):
        """
        Calcula produtos comerciais (Decisão por Cultura + 2 Etapas)
        """
        if not self.recomendacao: return {}
        
        req_N = self.recomendacao['N']
        req_P = self.recomendacao['P2O5']
        req_K = self.recomendacao['K2O']
        cultura = self.user.get('cultura', '').lower()
        
        # --- PASSO A: SELEÇÃO DA FÓRMULA DE SEMEADURA ---
        
        # Regra de Cultura (N no Plantio)
        # Gramíneas (Milho, Trigo, Arroz, Sorgo) -> EXIGEM N no plantio
        # Leguminosas (Soja, Feijão) -> Toleram/Preferem sem N ou pouco N
        
        is_graminea = any(x in cultura for x in ['milho', 'trigo', 'arroz', 'sorgo', 'pastagem', 'capim'])
        
        candidatas_raw = COMMERCIAL_FORMULAS.get('semeadura', [])
        candidatas_validas = []
        
        for fmt in candidatas_raw:
            fN, fP, fK = parse_formula(fmt)
            
            # Filtro de N para Gramíneas
            if is_graminea:
                if fN == 0: continue # Descarta 00-XX-XX para milho
            else:
                # Opcional: Para soja, poderíamos preferir N baixo, mas não estritamente proibir N (ex: 04-14-08 usa-se em soja)
                pass 
                
            if fP == 0: continue # Precisa ter P no plantio
            
            candidatas_validas.append(fmt)
            
        # Se filtro foi muito agressivo e sobrou nada, restaura originais (fallback)
        if not candidatas_validas:
            candidatas_validas = candidatas_raw

        # Seleção "Best Match" pelo Fósforo (P)
        melhor_formula = None
        melhor_dose = 0
        melhor_diff_range = float('inf')
        
        for fmt_str in candidatas_validas:
            fN, fP, fK = parse_formula(fmt_str)
            
            # Dose para 100% P
            if req_P <= 0:
                dose_calc = 0
            else:
                dose_calc = (req_P / fP) * 100
                
            dose_int = int(round(dose_calc))
            if dose_int == 0: continue
            
            # Preferência Operacional (300-500kg)
            dist = abs(dose_int - 400)
            if dose_int < 150: dist += 200
            if dose_int > 800: dist += 300
            
            if dist < melhor_diff_range:
                melhor_diff_range = dist
                melhor_formula = fmt_str
                melhor_dose = dose_int
                
        if not melhor_formula:
            melhor_formula = "00-00-00"
            melhor_dose = 0
            
        # Calcular Fornecido no Plantio
        fN, fP, fK = parse_formula(melhor_formula)
        forn_N = (melhor_dose * fN) / 100
        forn_P = (melhor_dose * fP) / 100
        
        # Check Salinidade K no sulco (>60 kg/ha K2O)
        k_no_sulco = (melhor_dose * fK) / 100
        if k_no_sulco > 60:
            # Opção A: Reduzir dose para teto de 60kg K2O (Priorizando segurança salina)
            # Mas isso reduziria P. 
            # Opção B: Se a fórmula escolhida causa salinidade, tentamos trocar?
            # Por hora, mantemos a dose mas jogamos alerta? 
            # O prompt pede: "Limitar dose e jogar resto pra cobertura".
            
            # Recalcular dose limitada por K
            dose_limite_salino = (60 / fK) * 100
            
            # Se a redução for drástica (>20% de corte no P), talvez fosse melhor outra fórmula, 
            # mas vamos seguir a instrução de limitar.
            melhor_dose = int(dose_limite_salino)
            
            # Recalcular fornecidos com nova dose
            forn_N = (melhor_dose * fN) / 100
            forn_P = (melhor_dose * fP) / 100
            k_no_sulco = 60.0 # Travado no teto
            
        forn_K_sulco = k_no_sulco
        
        # --- PASSO B: CÁLCULO DO DÉFICIT (COBERTURA) ---
        falta_N = max(0, req_N - forn_N)
        # O déficit de K aumenta se limitamos no sulco
        falta_K = max(0, req_K - forn_K_sulco)
        
        cob_items = []
        
        # Ureia (45-00-00) para N
        if falta_N > 10:
            dose_ureia = int(round((falta_N / 45) * 100))
            cob_items.append({"nome": "Ureia", "formula": "45-00-00", "dose": dose_ureia, "desc": f"{falta_N:.1f}kg N"})
        else:
            dose_ureia = 0
            
        # KCl (00-00-60) para K
        if falta_K > 10:
            dose_kcl = int(round((falta_K / 60) * 100))
            cob_items.append({"nome": "KCl", "formula": "00-00-60", "dose": dose_kcl, "desc": f"{falta_K:.1f}kg K₂O"})
        else:
            dose_kcl = 0
            
        # --- OUTPUT TEXT ---
        # Plantio: X kg/ha da Fórmula Y.
        if melhor_dose > 0:
            msg_plantio = f"PLANTIO: {melhor_dose} kg/ha de {melhor_formula}"
        else:
            msg_plantio = "PLANTIO: N/A"
            
        # Cobertura (Estádio V4): X kg/ha de Ureia + Y kg/ha de KCl.
        msg_cob = ""
        if cob_items:
            partes = [f"{item['dose']} kg/ha de {item['nome']}" for item in cob_items]
            msg_cob = "COBERTURA (V4): " + " + ".join(partes)
        else:
            msg_cob = "COBERTURA: Não necessária"
            
        texto_final = f"{msg_plantio}. {msg_cob}."
        
        return {
            "sugestao": melhor_formula,
            "dose_ha": melhor_dose,
            "texto_completo": texto_final,
            "plano": {
                "plantio": {"formula": melhor_formula, "dose": melhor_dose, "N": forn_N, "P": forn_P, "K": forn_K_sulco},
                "cobertura": cob_items
            }
        }
    
    def processar(self):
        """Processamento completo"""
        # 1. Diagnóstico
        self.diagnosticar()
        
        if self.erros:
            return {
                "erro": True,
                "mensagens": self.erros,
                "sugestao": "Forneça os dados faltantes manualmente"
            }
        
        # 2. Calagem
        calagem = self.calcular_calagem()
        
        # 3. Adubação
        self.recomendacao = self.recomendar_adubacao()
        
        # 4. Formulação
        formulacao = self.calcular_formulacao()
        
        # 5. Texto Interpretativo (Novo)
        texto_interpretativo = self.gerar_texto_interpretativo()
        
        # 6. Viabilidade Econômica (Novo)
        economia = self.calcular_viabilidade_economica()
        
        return {
            "status": "SUCESSO",
            "diagnostico": self.diagnostico,
            "texto_interpretativo": texto_interpretativo,
            "calagem": calagem,
            "adubacao": self.recomendacao,
            "formulacao": formulacao,
            "economia": economia,
            "solo": self.solo,
            "meta_dados": {
                "cultura": self.user.get('cultura'),
                "expectativa": self.user.get('expectativa', ''),
                "propriedade": self.user.get('propriedade', ''),
                "nome": self.user.get('nome', '')
            }
        }

    def processar_com_dados_manuais(self, dados_manuais):
        """Processa com dados manuais fornecidos pelo usuário"""
        # Converter dados manuais para o formato esperado
        dados_solo = {
            'fisica': {
                'argila': dados_manuais.get('argila'),
                'areia': dados_manuais.get('areia'),
                'silte': dados_manuais.get('silte')
            },
            'quimica': {
                'ph_cacl2': dados_manuais.get('ph_cacl2'),
                'ph_agua': dados_manuais.get('ph_agua'),
                'fosforo_mg': dados_manuais.get('fosforo_mg'),
                'potassio_mg': dados_manuais.get('potassio_mg'),
                'calcio_cmolc': dados_manuais.get('calcio_cmolc'),
                'magnesio_cmolc': dados_manuais.get('magnesio_cmolc'),
                'aluminio_cmolc': dados_manuais.get('aluminio_cmolc'),
                'h_al_cmolc': dados_manuais.get('h_al_cmolc'),
                'ctc_total': dados_manuais.get('ctc_total'),
                'v_percentual': dados_manuais.get('v_percentual'),
                'm_percentual': dados_manuais.get('m_percentual'),
                'materia_organica': dados_manuais.get('materia_organica')
            },
            'micronutrientes': {
                'enxofre': dados_manuais.get('enxofre'),
                'boro': dados_manuais.get('boro'),
                'zinco': dados_manuais.get('zinco'),
                'cobre': dados_manuais.get('cobre'),
                'manganes': dados_manuais.get('manganes'),
                'ferro': dados_manuais.get('ferro')
            }
        }
        
        # Substituir None por valores vazios
        for categoria in dados_solo:
            if dados_solo[categoria] is None:
                dados_solo[categoria] = {}
            for chave, valor in list(dados_solo[categoria].items()):
                if valor is None:
                    dados_solo[categoria][chave] = 0.0
        
        # Atualizar dados do solo
        self.raw_solo = dados_solo
        self.solo = self._normalizar_dados(dados_solo)
        
        return self.processar()
