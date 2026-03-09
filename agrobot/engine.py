"""
AgroBot V7 - engine.py
Motor de cálculo agronômico baseado em Embrapa Cerrados, 2004
Autor: Jonnathan Marques, Eng. Agrônomo
Adubação calculada em FONTES SIMPLES: Ureia, Superfosfato Simples, Cloreto de Potássio
"""

# =============================================================================
# FONTES SIMPLES
# =============================================================================
FONTES = {
    "ureia": {"formula": "45-00-00", "N": 0.45, "P": 0.00, "K": 0.00},
    "ssp":   {"formula": "00-18-00", "N": 0.00, "P": 0.18, "K": 0.00},  # + 10% S
    "kcl":   {"formula": "00-00-60", "N": 0.00, "P": 0.00, "K": 0.60},
}
SSP_S_PERCENT = 0.10  # Superfosfato Simples fornece ~10% de S
SULFATO_AMONIO_S = 0.24  # Sulfato de Amônio fornece ~24% de S


# =============================================================================
# TABELAS DE INTERPRETAÇÃO - EMBRAPA CERRADOS 2004
# =============================================================================

def classificar_fosforo(p_mgdm3, argila_pct):
    if argila_pct <= 15:
        limites = [6.0, 12.0, 18.0, 25.0]
    elif argila_pct <= 35:
        limites = [5.0, 10.0, 15.0, 20.0]
    elif argila_pct <= 60:
        limites = [3.0, 5.0, 8.0, 12.0]
    else:
        limites = [2.0, 3.0, 4.0, 6.0]

    if p_mgdm3 <= limites[0]:   return "MUITO BAIXO"
    elif p_mgdm3 <= limites[1]: return "BAIXO"
    elif p_mgdm3 <= limites[2]: return "MÉDIO"
    elif p_mgdm3 <= limites[3]: return "ADEQUADO"
    else:                       return "ALTO"


def classificar_potassio(k_mgdm3, ctc):
    k_cmol = k_mgdm3 / 391.0
    if ctc < 4.0:
        if k_cmol <= 0.038:   return "BAIXO"
        elif k_cmol <= 0.078: return "MÉDIO"
        elif k_cmol <= 0.100: return "ADEQUADO"
        else:                 return "ALTO"
    else:
        if k_cmol <= 0.064:   return "BAIXO"
        elif k_cmol <= 0.128: return "MÉDIO"
        elif k_cmol <= 0.200: return "ADEQUADO"
        else:                 return "ALTO"


def classificar_ph_cacl2(ph):
    if ph <= 4.4:   return "BAIXO"
    elif ph <= 4.8: return "MÉDIO"
    elif ph <= 5.5: return "ADEQUADO"
    elif ph <= 5.8: return "ALTO"
    else:           return "MUITO ALTO"


def classificar_ph_h2o(ph):
    if ph <= 5.1:   return "BAIXO"
    elif ph <= 5.5: return "MÉDIO"
    elif ph <= 6.3: return "ADEQUADO"
    elif ph <= 6.6: return "ALTO"
    else:           return "MUITO ALTO"


def classificar_mo(mo_gdm3, argila_pct):
    if argila_pct < 15:       # Arenosa
        limites = [8, 10, 15]
    elif argila_pct < 35:     # Média
        limites = [16, 20, 30]
    elif argila_pct <= 60:    # Argilosa
        limites = [24, 30, 45]
    else:                     # Muito argilosa
        limites = [28, 35, 52]

    if mo_gdm3 < limites[0]:    return "BAIXA"
    elif mo_gdm3 <= limites[1]: return "MÉDIA"
    elif mo_gdm3 <= limites[2]: return "ADEQUADA"
    else:                       return "ALTA"


def classificar_ca(ca):
    if ca < 1.5:    return "BAIXO"
    elif ca <= 7.0: return "ADEQUADO"
    else:           return "ALTO"


def classificar_mg(mg):
    if mg < 0.5:    return "BAIXO"
    elif mg <= 2.0: return "ADEQUADO"
    else:           return "ALTO"


def classificar_al(al_cmol):
    if al_cmol <= 0.20:   return "MUITO BAIXO"
    elif al_cmol <= 0.50: return "BAIXO"
    elif al_cmol <= 1.00: return "MÉDIO"
    elif al_cmol <= 2.00: return "ALTO"
    else:                 return "MUITO ALTO"


def classificar_v(v_pct):
    if v_pct <= 20:   return "BAIXO"
    elif v_pct <= 40: return "MÉDIO"
    elif v_pct <= 60: return "ADEQUADO"
    else:             return "ALTO"


def textura_solo(argila_pct):
    if argila_pct < 15:
        return "ARENOSA"
    elif argila_pct < 35:
        return "MÉDIA"
    elif argila_pct <= 60:
        return "ARGILOSA"
    else:
        return "MUITO ARGILOSA"


# =============================================================================
# CALAGEM - Método Saturação por Bases (Embrapa Cerrados 2004)
# NC (t/ha) = [(V2 - V1) x T] / PRNT
# =============================================================================

V2_CULTURA = {
    "milho":    60,
    "soja":     60,
    "arroz":    50,
    "trigo":    50,
    "sorgo":    50,
    "milheto":  50,
    "algodao":  70,
    "feijao":   60,
    "girassol": 60,
}


def calcular_calagem(v1_pct, ctc, cultura, prnt=80):
    v2 = V2_CULTURA.get(cultura.lower(), 60)
    if v1_pct < v2:
        nc_v = ((v2 - v1_pct) * ctc) / prnt
    else:
        nc_v = 0.0
    nc_v = round(nc_v, 2)
    return {
        "v1":              v1_pct,
        "v2":              v2,
        "ctc":             ctc,
        "prnt":            prnt,
        "nc_v":            nc_v,
        "nc_recomendado":  nc_v,
    }


# =============================================================================
# ADUBAÇÃO - Fontes simples por cultura
# Embrapa Cerrados 2004
# =============================================================================

def calcular_adubacao(cultura, expectativa, nivel_p, nivel_k, argila_pct, ctc):
    cultura     = cultura.lower()
    expectativa = expectativa.lower()
    nivel_p     = nivel_p.upper()
    nivel_k     = nivel_k.upper()

    # ------------------------------------------------------------------
    # MILHO
    # ------------------------------------------------------------------
    if cultura == "milho":
        # N total por expectativa de produtividade
        n_map = {"baixa": 80, "media": 120, "alta": 160}
        n_total      = n_map.get(expectativa, 120)
        n_semeadura  = 30
        n_cobertura  = n_total - n_semeadura  # cobertura V4-V6

        # P2O5 por nível de P e teor de argila (Tabela Embrapa Cerrados 2004)
        if argila_pct <= 15:
            p_doses = {"MUITO BAIXO": 60,  "BAIXO": 30,  "MÉDIO": 15,  "ADEQUADO": 0,  "ALTO": 0}
        elif argila_pct <= 35:
            p_doses = {"MUITO BAIXO": 100, "BAIXO": 50,  "MÉDIO": 25,  "ADEQUADO": 0,  "ALTO": 0}
        elif argila_pct <= 60:
            p_doses = {"MUITO BAIXO": 200, "BAIXO": 100, "MÉDIO": 50,  "ADEQUADO": 25, "ALTO": 0}
        else:
            p_doses = {"MUITO BAIXO": 280, "BAIXO": 140, "MÉDIO": 70,  "ADEQUADO": 35, "ALTO": 0}

        # P alto/adequado em solo argiloso: adubação de manutenção
        if nivel_p == "ALTO" and argila_pct > 35:
            p2o5 = 50
        elif nivel_p == "ADEQUADO" and argila_pct > 35:
            p2o5 = 50
        else:
            p2o5 = p_doses.get(nivel_p, 50)

        # K2O por nível e CTC (Tabela Embrapa Cerrados 2004)
        if ctc < 4.0:
            k_doses = {"BAIXO": 50,  "MÉDIO": 25,  "ADEQUADO": 0,  "ALTO": 0}
        else:
            k_doses = {"BAIXO": 100, "MÉDIO": 50,  "ADEQUADO": 25, "ALTO": 0}

        # Para alta expectativa, reposição de K mesmo em nível médio/adequado
        if expectativa == "alta":
            if nivel_k in ("MÉDIO", "ADEQUADO"):
                k2o = 110
            elif nivel_k == "ALTO":
                k2o = 80
            else:
                k2o = k_doses.get(nivel_k, 80)
        else:
            k2o = k_doses.get(nivel_k, 50)

        k_semeadura = 50
        k_cobertura = max(0, k2o - k_semeadura)

        # Enxofre
        s_dose = 30 if expectativa == "alta" else 20

        # Inoculante
        inoculante = (
            "Azospirillum brasilense (Ab-V5 + Ab-V6) — 100-200 mL / 60.000 sementes. "
            "Compatível com TS fungicida/inseticida quando aplicados separadamente."
        )

    # ------------------------------------------------------------------
    # SOJA
    # ------------------------------------------------------------------
    elif cultura == "soja":
        n_total     = 0  # FBN
        n_semeadura = 0
        n_cobertura = 0

        if argila_pct <= 15:
            p_doses = {"MUITO BAIXO": 60,  "BAIXO": 30,  "MÉDIO": 15,  "ADEQUADO": 0,  "ALTO": 0}
        elif argila_pct <= 35:
            p_doses = {"MUITO BAIXO": 100, "BAIXO": 50,  "MÉDIO": 25,  "ADEQUADO": 0,  "ALTO": 0}
        elif argila_pct <= 60:
            p_doses = {"MUITO BAIXO": 200, "BAIXO": 100, "MÉDIO": 50,  "ADEQUADO": 25, "ALTO": 0}
        else:
            p_doses = {"MUITO BAIXO": 280, "BAIXO": 140, "MÉDIO": 70,  "ADEQUADO": 35, "ALTO": 0}

        p2o5 = 50 if nivel_p in ("ALTO", "ADEQUADO") else p_doses.get(nivel_p, 60)

        if ctc < 4.0:
            k_doses = {"BAIXO": 50,  "MÉDIO": 25,  "ADEQUADO": 0,  "ALTO": 0}
        else:
            k_doses = {"BAIXO": 100, "MÉDIO": 50,  "ADEQUADO": 25, "ALTO": 0}

        k2o         = k_doses.get(nivel_k, 50)
        k_semeadura = k2o
        k_cobertura = 0
        s_dose      = 20

        inoculante = (
            "Bradyrhizobium japonicum (SEMIA 5079 + SEMIA 5080) + Co-Mo — "
            "dose conforme fabricante. Não misturar com fungicida no mesmo momento."
        )

    # ------------------------------------------------------------------
    # CULTURAS GENÉRICAS (arroz, trigo, sorgo, milheto)
    # ------------------------------------------------------------------
    else:
        n_map       = {"baixa": 60, "media": 90, "alta": 120}
        n_total     = n_map.get(expectativa, 90)
        n_semeadura = 20
        n_cobertura = n_total - n_semeadura

        p_doses_base = {"MUITO BAIXO": 120, "BAIXO": 80, "MÉDIO": 50, "ADEQUADO": 30, "ALTO": 20}
        p2o5         = p_doses_base.get(nivel_p, 50)

        k_doses_base = {"BAIXO": 80, "MÉDIO": 50, "ADEQUADO": 30, "ALTO": 20}
        k2o          = k_doses_base.get(nivel_k, 50)
        k_semeadura  = k2o
        k_cobertura  = 0
        s_dose       = 20

        inoculante = "Consultar recomendação específica para a cultura."

    # ------------------------------------------------------------------
    # CÁLCULO DAS FONTES SIMPLES (kg/ha)
    # ------------------------------------------------------------------

    # Semeadura
    ureia_semeadura = round(n_semeadura / FONTES["ureia"]["N"], 1) if n_semeadura > 0 else 0.0
    ssp_semeadura   = round(p2o5        / FONTES["ssp"]["P"], 1)
    kcl_semeadura   = round(k_semeadura / FONTES["kcl"]["K"], 1) if k_semeadura > 0 else 0.0

    # Cobertura
    ureia_cobertura = round(n_cobertura / FONTES["ureia"]["N"], 1) if n_cobertura > 0 else 0.0
    kcl_cobertura   = round(k_cobertura / FONTES["kcl"]["K"], 1) if k_cobertura > 0 else 0.0

    # S fornecido via SSP e complemento
    s_via_ssp       = round(ssp_semeadura * SSP_S_PERCENT, 1)
    s_complementar  = round(max(0.0, s_dose - s_via_ssp), 1)
    sulfato_comp_kg = round(s_complementar / SULFATO_AMONIO_S, 1) if s_complementar > 0 else 0.0

    return {
        # Nutrientes puros (kg/ha)
        "N_total":         n_total,
        "N_semeadura":     n_semeadura,
        "N_cobertura":     n_cobertura,
        "P2O5":            p2o5,
        "K2O_total":       k2o,
        "K2O_semeadura":   k_semeadura,
        "K2O_cobertura":   k_cobertura,
        "S_dose":          s_dose,
        "S_via_SSP":       s_via_ssp,
        "S_complementar":  s_complementar,

        # Fontes simples - SEMEADURA (kg/ha)
        "ureia_semeadura": ureia_semeadura,
        "ssp_semeadura":   ssp_semeadura,
        "kcl_semeadura":   kcl_semeadura,

        # Fontes simples - COBERTURA (kg/ha)
        "ureia_cobertura": ureia_cobertura,
        "kcl_cobertura":   kcl_cobertura,

        # Complemento de enxofre
        "sulfato_comp_kg": sulfato_comp_kg,

        # Inoculante
        "inoculante": inoculante,
    }


# =============================================================================
# FUNÇÃO PRINCIPAL - recebe dados do usuário e retorna laudo completo
# =============================================================================

def gerar_laudo(dados: dict) -> dict:
    """
    Parâmetros de entrada (dict):
        solicitante, propriedade, cultura, expectativa
        argila, ph_agua, ph_cacl2, mo, p, k, ca, mg, al, h_al

    Retorna dict completo com interpretação + calagem + adubação + fontes simples.
    """
    argila      = float(dados["argila"])
    ph_agua     = float(dados["ph_agua"])
    ph_cacl2    = float(dados["ph_cacl2"])
    mo          = float(dados["mo"])
    p           = float(dados["p"])
    k           = float(dados["k"])
    ca          = float(dados["ca"])
    mg          = float(dados["mg"])
    al          = float(dados.get("al", 0.0))
    h_al        = float(dados["h_al"])
    cultura     = dados["cultura"]
    expectativa = dados["expectativa"]

    # Derivados
    k_cmol = round(k / 391.0, 4)
    sb     = round(ca + mg + k_cmol, 2)
    ctc    = round(sb + h_al, 2)
    v_pct  = round((sb / ctc) * 100, 1) if ctc > 0 else 0.0
    m_pct  = round((al / (al + sb)) * 100, 1) if (al + sb) > 0 else 0.0

    # Classificações
    nivel_p   = classificar_fosforo(p, argila)
    nivel_k   = classificar_potassio(k, ctc)
    nivel_ph  = classificar_ph_cacl2(ph_cacl2)
    nivel_ph_h2o = classificar_ph_h2o(ph_agua)
    nivel_mo  = classificar_mo(mo, argila)
    nivel_v   = classificar_v(v_pct)
    nivel_al  = classificar_al(al)
    nivel_ca  = classificar_ca(ca)
    nivel_mg  = classificar_mg(mg)
    textura   = textura_solo(argila)

    # Calagem
    calagem = calcular_calagem(v_pct, ctc, cultura)

    # Adubação
    adubacao = calcular_adubacao(cultura, expectativa, nivel_p, nivel_k, argila, ctc)

    return {
        # Identificação
        "solicitante": dados.get("solicitante", ""),
        "propriedade": dados.get("propriedade", ""),
        "cultura":     cultura,
        "expectativa": expectativa,

        # Parâmetros brutos
        "argila":   argila,
        "ph_agua":  ph_agua,
        "ph_cacl2": ph_cacl2,
        "mo":       mo,
        "p":        p,
        "k":        k,
        "k_cmol":   k_cmol,
        "ca":       ca,
        "mg":       mg,
        "al":       al,
        "h_al":     h_al,

        # Derivados
        "sb":    sb,
        "ctc":   ctc,
        "v_pct": v_pct,
        "m_pct": m_pct,

        # Classificações
        "textura":       textura,
        "nivel_p":       nivel_p,
        "nivel_k":       nivel_k,
        "nivel_ph":      nivel_ph,
        "nivel_ph_h2o":  nivel_ph_h2o,
        "nivel_mo":      nivel_mo,
        "nivel_v":       nivel_v,
        "nivel_al":      nivel_al,
        "nivel_ca":      nivel_ca,
        "nivel_mg":      nivel_mg,

        # Calagem e Adubação
        "calagem":  calagem,
        "adubacao": adubacao,
    }


# =============================================================================
# TESTE LOCAL
# =============================================================================
if __name__ == "__main__":
    dados_teste = {
        "solicitante": "Jonnathan",
        "propriedade": "Ecoflora",
        "cultura":     "milho",
        "expectativa": "alta",
        "argila":   53.4,
        "ph_agua":  6.00,
        "ph_cacl2": 5.20,
        "mo":       26.4,
        "p":        13.4,
        "k":        125.2,
        "ca":       2.40,
        "mg":       0.98,
        "al":       0.00,
        "h_al":     3.63,
    }

    r = gerar_laudo(dados_teste)
    a = r["adubacao"]
    c = r["calagem"]

    print("=" * 60)
    print("AGROBOT V7 - TESTE engine.py")
    print("=" * 60)
    print(f"Textura:   {r['textura']}")
    print(f"SB:  {r['sb']}  |  CTC: {r['ctc']}  |  V%: {r['v_pct']}%")
    print(f"P:   {r['nivel_p']}  |  K: {r['nivel_k']}")
    print()
    print(f"CALAGEM:  {c['nc_recomendado']} t/ha  (V1={c['v1']}%  V2={c['v2']}%  PRNT={c['prnt']}%)")
    print()
    print("NUTRIENTES PUROS (kg/ha):")
    print(f"  N total:  {a['N_total']}  (semeadura {a['N_semeadura']} + cobertura {a['N_cobertura']})")
    print(f"  P2O5:     {a['P2O5']}")
    print(f"  K2O:      {a['K2O_total']}  (semeadura {a['K2O_semeadura']} + cobertura {a['K2O_cobertura']})")
    print(f"  S:        {a['S_dose']}  (via SSP {a['S_via_SSP']} + complementar {a['S_complementar']})")
    print()
    print("SEMEADURA - FONTES SIMPLES:")
    print(f"  Ureia:               {a['ureia_semeadura']:>7.1f} kg/ha  →  {a['N_semeadura']} kg N")
    print(f"  Superfosfato Simples:{a['ssp_semeadura']:>7.1f} kg/ha  →  {a['P2O5']} kg P2O5")
    print(f"  Cloreto de Potassio: {a['kcl_semeadura']:>7.1f} kg/ha  →  {a['K2O_semeadura']} kg K2O")
    print()
    print("COBERTURA V4-V6 - FONTES SIMPLES:")
    print(f"  Ureia:               {a['ureia_cobertura']:>7.1f} kg/ha  →  {a['N_cobertura']} kg N")
    print(f"  Cloreto de Potassio: {a['kcl_cobertura']:>7.1f} kg/ha  →  {a['K2O_cobertura']} kg K2O")
    if a['s_complementar'] > 0 if 's_complementar' in a else a['S_complementar'] > 0:
        print(f"  Sulfato de Amonio:   {a['sulfato_comp_kg']:>7.1f} kg/ha  →  {a['S_complementar']} kg S")
    print()
    print(f"INOCULANTE: {a['inoculante']}")


# =============================================================================
# ADAPTADOR - telegram_bot.py importa AgroEnginePro
# =============================================================================

_CHAVES_SOLO = {
    "ph_agua":          "ph_agua",
    "ph_cacl2":         "ph_cacl2",
    "argila":           "argila",
    "fosforo_mg":       "p",
    "potassio_mg":      "k",
    "materia_organica": "mo",
    "calcio_cmolc":     "ca",
    "magnesio_cmolc":   "mg",
    "aluminio_cmolc":   "al",
    "h_al_cmolc":       "h_al",
}


def _normalizar_dados_solo(dados_brutos: dict) -> dict:
    normalizado = {}
    for chave_bot, chave_engine in _CHAVES_SOLO.items():
        if chave_bot in dados_brutos:
            normalizado[chave_engine] = float(dados_brutos[chave_bot])
    if "h_al" not in normalizado and "hidrogenio_cmolc" in dados_brutos:
        al = float(dados_brutos.get("aluminio_cmolc", 0.0))
        h  = float(dados_brutos.get("hidrogenio_cmolc", 0.0))
        normalizado["h_al"] = round(h + al, 2)
    return normalizado


class AgroEnginePro:
    def __init__(self, dados_solo: dict, dados_usuario: dict):
        self._dados_solo    = dados_solo or {}
        self._dados_usuario = dados_usuario or {}

    def _montar_entrada(self, dados_solo: dict) -> dict:
        normalizado = _normalizar_dados_solo(dados_solo)
        normalizado["solicitante"] = self._dados_usuario.get("nome", "")
        normalizado["propriedade"] = self._dados_usuario.get("propriedade", "")
        normalizado["cultura"]     = self._dados_usuario.get("cultura", "outros")
        normalizado["expectativa"] = self._dados_usuario.get("expectativa", "media")
        return normalizado

    def _executar(self, dados_solo: dict) -> dict:
        entrada = self._montar_entrada(dados_solo)
        campos_obrigatorios = ["ph_agua", "ph_cacl2", "argila", "p", "k", "mo", "ca", "mg", "h_al"]
        faltando = [c for c in campos_obrigatorios if c not in entrada]
        if faltando:
            return {"erro": True, "mensagens": [f"AVISO: Parametros ausentes: {', '.join(faltando)}"]}
        try:
            resultado = gerar_laudo(entrada)
            resultado["erro"]      = False
            resultado["mensagens"] = []
            return resultado
        except Exception as e:
            return {"erro": True, "mensagens": [f"Erro no processamento: {str(e)}"]}

    def processar(self) -> dict:
        return self._executar(self._dados_solo)

    def processar_com_dados_manuais(self, dados_manuais: dict) -> dict:
        return self._executar(dados_manuais)
