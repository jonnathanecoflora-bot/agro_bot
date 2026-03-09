"""
AgroBot V7 - pdf_generator.py
Geração do laudo PDF com fontes simples
Autor: Jonnathan Marques, Eng. Agrônomo
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


# =============================================================================
# CORES
# =============================================================================
VERDE_ESCURO = colors.HexColor("#1B5E20")
VERDE_MEDIO  = colors.HexColor("#2E7D32")
CINZA_CLARO  = colors.HexColor("#F5F5F5")
CINZA_LINHA  = colors.HexColor("#E0E0E0")
BRANCO       = colors.white
PRETO        = colors.black
LARANJA      = colors.HexColor("#E65100")
AZUL_ESCURO  = colors.HexColor("#0D47A1")


# =============================================================================
# ESTILOS
# =============================================================================
def get_styles():
    return {
        "titulo": ParagraphStyle(
            "titulo", fontSize=16, textColor=BRANCO,
            fontName="Helvetica-Bold", alignment=TA_CENTER
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", fontSize=9, textColor=BRANCO,
            fontName="Helvetica", alignment=TA_CENTER
        ),
        "secao": ParagraphStyle(
            "secao", fontSize=9, textColor=BRANCO,
            fontName="Helvetica-Bold", alignment=TA_LEFT, leftIndent=6
        ),
        "corpo": ParagraphStyle(
            "corpo", fontSize=8, textColor=PRETO,
            fontName="Helvetica", alignment=TA_JUSTIFY,
            leading=12, spaceAfter=3
        ),
        "rodape": ParagraphStyle(
            "rodape", fontSize=7, textColor=colors.grey,
            fontName="Helvetica-Oblique", alignment=TA_CENTER
        ),
        "alerta": ParagraphStyle(
            "alerta", fontSize=7.5, textColor=LARANJA,
            fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10
        ),
    }


# =============================================================================
# HELPERS
# =============================================================================
def secao_bar(texto, styles, bg=VERDE_ESCURO):
    t = Table([[Paragraph(texto, styles["secao"])]], colWidths=["100%"])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def tabela(dados, col_widths, header_bg=VERDE_MEDIO):
    t = Table(dados, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  BRANCO),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CINZA_CLARO, BRANCO]),
        ("GRID",           (0, 0), (-1, -1), 0.4, CINZA_LINHA),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
    ]))
    return t


def cor_nivel(nivel):
    mapa = {
        "MUITO BAIXO": colors.HexColor("#B71C1C"),
        "BAIXO":       colors.HexColor("#C62828"),
        "MÉDIO":       colors.HexColor("#E65100"),
        "MEDIA":       colors.HexColor("#E65100"),
        "ADEQUADO":    colors.HexColor("#2E7D32"),
        "ADEQUADA":    colors.HexColor("#2E7D32"),
        "ALTO":        colors.HexColor("#1565C0"),
        "ALTA":        colors.HexColor("#1565C0"),
        "MUITO ALTO":  colors.HexColor("#4A148C"),
        "BAIXA":       colors.HexColor("#C62828"),
    }
    return mapa.get(nivel.upper().strip(), PRETO)


# =============================================================================
# GERADOR PRINCIPAL
# =============================================================================
def gerar_pdf(resultado: dict, numero_laudo: str, output_dir: str = ".") -> str:
    """
    Recebe o dict de gerar_laudo() e gera o PDF completo.
    Retorna o caminho do arquivo gerado.
    """
    styles = get_styles()
    nome_arquivo = f"Laudo_{numero_laudo}_{resultado['solicitante']}.pdf"
    caminho = os.path.join(output_dir, nome_arquivo)

    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=2.0*cm
    )
    W = A4[0] - 3.0*cm  # largura util
    story = []

    # -----------------------------------------------------------------------
    # CABEÇALHO
    # -----------------------------------------------------------------------
    cab = Table([[
        Paragraph("AGROBOT V7", styles["titulo"]),
        Paragraph("LAUDO TÉCNICO DE ANÁLISE DE SOLO", styles["subtitulo"])
    ]], colWidths=[W * 0.28, W * 0.72])
    cab.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), VERDE_ESCURO),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(cab)
    story.append(Spacer(1, 0.35*cm))

    # -----------------------------------------------------------------------
    # IDENTIFICAÇÃO
    # -----------------------------------------------------------------------
    story.append(secao_bar("■ IDENTIFICAÇÃO", styles))
    id_rows = [
        ["Solicitante", resultado["solicitante"],   "Laudo Nº",      numero_laudo],
        ["Propriedade", resultado["propriedade"],   "Data",          datetime.now().strftime("%d/%m/%Y")],
        ["Cultura",     resultado["cultura"].title(),"Expectativa",  resultado["expectativa"].title()],
        ["Camada",      "0-20 cm",                  "Base técnica",  "Embrapa Cerrados, 2004"],
    ]
    t_id = Table(id_rows, colWidths=[W*0.15, W*0.35, W*0.15, W*0.35])
    t_id.setStyle(TableStyle([
        ("FONTNAME",       (0, 0), (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",       (2, 0), (2, -1),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CINZA_CLARO, BRANCO]),
        ("GRID",           (0, 0), (-1, -1), 0.3, CINZA_LINHA),
        ("TOPPADDING",     (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t_id)
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # DIAGNÓSTICO DE FERTILIDADE
    # -----------------------------------------------------------------------
    story.append(secao_bar("DIAGNÓSTICO DA FERTILIDADE DO SOLO", styles))
    r = resultado
    diag_rows = [
        ["Parâmetro",           "Valor",                    "Unidade",      "Nível"],
        ["Argila",              f"{r['argila']:.1f}",       "%",            r["textura"]],
        ["pH em Água",          f"{r['ph_agua']:.2f}",      "-",            r["nivel_ph_h2o"]],
        ["pH em CaCl2",         f"{r['ph_cacl2']:.2f}",     "-",            r["nivel_ph"]],
        ["Matéria Orgânica",    f"{r['mo']:.1f}",           "g/dm3",        r["nivel_mo"]],
        ["Fósforo (P)",         f"{r['p']:.1f}",            "mg/dm3",       r["nivel_p"]],
        ["Potássio (K)",        f"{r['k']:.1f}",            "mg/dm3",       r["nivel_k"]],
        ["Cálcio (Ca)",         f"{r['ca']:.2f}",           "cmolc/dm3",    r["nivel_ca"]],
        ["Magnésio (Mg)",       f"{r['mg']:.2f}",           "cmolc/dm3",    r["nivel_mg"]],
        ["Alumínio (Al)",       f"{r['al']:.2f}",           "cmolc/dm3",    r["nivel_al"]],
        ["H+Al",                f"{r['h_al']:.2f}",         "cmolc/dm3",    "-"],
        ["Soma de Bases (SB)",  f"{r['sb']:.2f}",           "cmolc/dm3",    "-"],
        ["CTC (pH 7,0)",        f"{r['ctc']:.2f}",          "cmolc/dm3",    "-"],
        ["Saturação V%",        f"{r['v_pct']:.1f}",        "%",            r["nivel_v"]],
        ["Saturação Al (m%)",   f"{r['m_pct']:.1f}",        "%",
         "BAIXO" if r["m_pct"] < 20 else "ALTO"],
    ]
    t_diag = tabela(diag_rows, [W*0.38, W*0.18, W*0.18, W*0.26])
    # Colorir coluna Nível por classificação
    for i, row in enumerate(diag_rows[1:], start=1):
        nivel_val = row[3]
        if nivel_val and nivel_val != "-":
            t_diag.setStyle(TableStyle([
                ("TEXTCOLOR", (3, i), (3, i), cor_nivel(nivel_val)),
                ("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"),
            ]))
    story.append(t_diag)
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # INTERPRETAÇÃO TÉCNICA
    # -----------------------------------------------------------------------
    story.append(secao_bar("■ INTERPRETAÇÃO TÉCNICA DOS RESULTADOS", styles))
    ca_mg_ratio = round(r["ca"] / r["mg"], 1) if r["mg"] > 0 else 0
    relacao_txt = "adequada" if 2 <= ca_mg_ratio <= 10 else ("estreita (excesso relativo de Mg)" if ca_mg_ratio < 2 else "alta")

    interpretacoes = [
        f"<b>pH (CaCl2 = {r['ph_cacl2']:.2f} - {r['nivel_ph']}):</b> "
        + ("Reação adequada para a maioria das culturas." if r["nivel_ph"] in ("ADEQUADO", "ALTO", "MUITO ALTO")
           else "Reação ácida. Recomenda-se correção para otimizar disponibilidade de nutrientes, especialmente P e Mo."),

        f"<b>Matéria Orgânica ({r['mo']:.1f} g/dm3 - {r['nivel_mo']}):</b> "
        + ("Nível satisfatório. Manter práticas conservacionistas como plantio direto e rotação de culturas."
           if r["nivel_mo"] in ("MÉDIA", "ADEQUADA", "ALTA")
           else "Nível baixo. Incrementar aporte de matéria orgânica com culturas de cobertura e adubação verde."),

        f"<b>Fósforo - Mehlich-1 ({r['p']:.1f} mg/dm3 - {r['nivel_p']}):</b> "
        + ("Nível alto. Manter adubação de manutenção." if r["nivel_p"] == "ALTO"
           else "Nível adequado. Manter adubação de reposição." if r["nivel_p"] == "ADEQUADO"
           else "Nível abaixo do ideal. Aplicar dose corretiva conforme recomendação."),

        f"<b>Potássio ({r['k']:.1f} mg/dm3 = {r['k_cmol']:.3f} cmolc/dm3 - {r['nivel_k']}):</b> "
        + ("Nível adequado/alto. Manter adubação de reposição da exportação pela colheita."
           if r["nivel_k"] in ("ADEQUADO", "ALTO")
           else "Nível abaixo do ideal. Aplicar dose corretiva."),

        f"<b>Cálcio ({r['ca']:.2f} cmolc/dm3 - {r['nivel_ca']}) e Magnésio ({r['mg']:.2f} cmolc/dm3 - {r['nivel_mg']}):</b> "
        + f"Relação Ca/Mg = {ca_mg_ratio} ({relacao_txt}). Níveis satisfatórios.",

        f"<b>Alumínio Tóxico ({r['al']:.2f} cmolc/dm3) | Saturação por Al (m% = {r['m_pct']:.1f}% - "
        + ("BAIXO" if r["m_pct"] < 20 else "ALTO") + "):</b> "
        + ("Sem toxidez por alumínio." if r["al"] <= 0.2 else "Atenção: alumínio em nível tóxico. Priorizar calagem."),

        f"<b>Saturação por Bases (V% = {r['v_pct']:.1f}% - {r['nivel_v']}):</b> "
        + ("V% em nível adequado para bom desenvolvimento das culturas."
           if r["nivel_v"] in ("ADEQUADO", "ALTO")
           else "V% abaixo do ideal. Necessário corrigir com calagem."),
    ]
    for txt in interpretacoes:
        story.append(Paragraph(f"- {txt}", styles["corpo"]))
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # CALAGEM
    # -----------------------------------------------------------------------
    story.append(secao_bar("■ RECOMENDAÇÃO DE CALAGEM", styles))
    cal = r["calagem"]
    story.append(Paragraph(
        f"Com base no método da Saturação por Bases (Embrapa Cerrados, 2004), o solo apresenta V% atual "
        f"de {cal['v1']:.1f}%, {'abaixo' if cal['v1'] < cal['v2'] else 'igual ou acima'} "
        f"do ideal de {cal['v2']}% para a cultura de {resultado['cultura'].title()}.",
        styles["corpo"]
    ))
    story.append(Spacer(1, 0.2*cm))

    cal_rows = [
        ["Parâmetro", "Valor"],
        ["V% atual do solo",                           f"{cal['v1']:.1f}%"],
        ["V% ideal para " + resultado["cultura"].title(), f"{cal['v2']}%"],
        ["NC pelo método V% (t/ha)",                   f"{cal['nc_v']:.2f}"],
        ["NC pela neutralização de Al (t/ha)",         "0,00"],
        [f"DOSE RECOMENDADA (PRNT {cal['prnt']}%)",   f"{cal['nc_recomendado']:.2f} t/ha"],
    ]
    t_cal = tabela(cal_rows, [W*0.65, W*0.35])
    # Negrito na última linha
    t_cal.setStyle(TableStyle([
        ("FONTNAME",    (0, len(cal_rows)-1), (-1, len(cal_rows)-1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (1, len(cal_rows)-1), (1, len(cal_rows)-1), AZUL_ESCURO),
    ]))
    story.append(t_cal)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Produto sugerido: <b>Calcário Dolomítico (PRNT >= 80%)</b>. "
        "Aplicar 60-90 dias antes do plantio, preferencialmente a lanço com incorporação. "
        "Para solos com Al > 0,5 cmolc/dm3, dar prioridade à aplicação imediata.",
        styles["corpo"]
    ))
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # ADUBAÇÃO - RESUMO DE NUTRIENTES PUROS
    # -----------------------------------------------------------------------
    ad = r["adubacao"]
    story.append(secao_bar(
        f"RECOMENDAÇÃO DE ADUBAÇÃO - {resultado['cultura'].upper()}  "
        f"(Expectativa: {resultado['expectativa'].title()})",
        styles
    ))
    story.append(Paragraph(
        f"Recomendação elaborada para <b>{resultado['cultura'].title()}</b> com expectativa de "
        f"produtividade <b>{resultado['expectativa'].title()}</b>, considerando fósforo em nível "
        f"<b>{r['nivel_p']}</b> e potássio em nível <b>{r['nivel_k']}</b> "
        f"para solo com {r['argila']:.0f}% de argila (textura {r['textura'].lower()}).",
        styles["corpo"]
    ))
    story.append(Spacer(1, 0.2*cm))

    nut_rows = [
        ["Nutriente", "Dose (kg/ha)", "Observação"],
        ["N (Nitrogênio total)",
         str(ad["N_total"]),
         f"{ad['N_semeadura']} kg/ha semeadura + {ad['N_cobertura']} kg/ha cobertura (V4-V6)"],
        ["P2O5 (Fósforo)",
         str(ad["P2O5"]),
         "100% na semeadura, preferencialmente na linha"],
        ["K2O (Potássio)",
         str(ad["K2O_total"]),
         f"{ad['K2O_semeadura']} kg/ha semeadura + {ad['K2O_cobertura']} kg/ha cobertura (V4-V6)"],
        ["S (Enxofre)",
         str(ad["S_dose"]),
         f"Aplicar na semeadura ({ad['S_via_SSP']} kg via SSP"
         + (f" + {ad['S_complementar']} kg complementar via Sulfato de Amônio)" if ad["S_complementar"] > 0 else ")")],
    ]
    story.append(tabela(nut_rows, [W*0.25, W*0.15, W*0.60]))
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # SEMEADURA - FONTES SIMPLES
    # -----------------------------------------------------------------------
    story.append(secao_bar("  SEMEADURA — Fontes Simples (kg/ha)", styles, bg=VERDE_MEDIO))
    sem_rows = [["Produto", "Dose (kg/ha)", "Nutriente fornecido", "Fórmula"]]
    if ad["ureia_semeadura"] > 0:
        sem_rows.append([
            "Ureia",
            f"{ad['ureia_semeadura']:.1f}",
            f"{ad['N_semeadura']} kg N",
            "45-00-00"
        ])
    sem_rows.append([
        "Superfosfato Simples",
        f"{ad['ssp_semeadura']:.1f}",
        f"{ad['P2O5']} kg P2O5  +  {ad['S_via_SSP']:.1f} kg S",
        "00-18-00 + 10% S"
    ])
    if ad["kcl_semeadura"] > 0:
        sem_rows.append([
            "Cloreto de Potássio",
            f"{ad['kcl_semeadura']:.1f}",
            f"{ad['K2O_semeadura']} kg K2O",
            "00-00-60"
        ])
    if ad["S_complementar"] > 0:
        sem_rows.append([
            "Sulfato de Amônio (compl. S)",
            f"{ad['sulfato_comp_kg']:.1f}",
            f"{ad['S_complementar']} kg S",
            "20-00-00 + 24% S"
        ])
    story.append(tabela(sem_rows, [W*0.30, W*0.18, W*0.32, W*0.20]))
    story.append(Spacer(1, 0.35*cm))

    # -----------------------------------------------------------------------
    # COBERTURA - FONTES SIMPLES
    # -----------------------------------------------------------------------
    if ad["ureia_cobertura"] > 0 or ad["kcl_cobertura"] > 0:
        story.append(secao_bar("  COBERTURA (V4-V6) — Fontes Simples (kg/ha)", styles, bg=VERDE_MEDIO))
        cob_rows = [["Produto", "Dose (kg/ha)", "Nutriente fornecido", "Fórmula"]]
        if ad["ureia_cobertura"] > 0:
            cob_rows.append([
                "Ureia",
                f"{ad['ureia_cobertura']:.1f}",
                f"{ad['N_cobertura']} kg N",
                "45-00-00"
            ])
        if ad["kcl_cobertura"] > 0:
            cob_rows.append([
                "Cloreto de Potássio",
                f"{ad['kcl_cobertura']:.1f}",
                f"{ad['K2O_cobertura']} kg K2O",
                "00-00-60"
            ])
        story.append(tabela(cob_rows, [W*0.30, W*0.18, W*0.32, W*0.20]))
        story.append(Spacer(1, 0.35*cm))

    # -----------------------------------------------------------------------
    # INOCULANTE
    # -----------------------------------------------------------------------
    story.append(Paragraph(
        f"<b>Tratamento de Sementes (TS):</b> {ad['inoculante']}",
        styles["corpo"]
    ))
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # RECOMENDAÇÕES GERAIS
    # -----------------------------------------------------------------------
    story.append(secao_bar("■ RECOMENDAÇÕES GERAIS DE MANEJO", styles))
    recomendacoes = [
        "Realizar a calagem pelo menos 60-90 dias antes do plantio para completa reação no solo.",
        "Adotar o plantio direto ou mínimo revolvimento para preservar a matéria orgânica e a biologia do solo.",
        f"Realizar tratamento de sementes (TS) com {ad['inoculante']}",
        "Monitorar a umidade do solo durante o desenvolvimento inicial — solo seco reduz a eficiência da calagem.",
        f"Realizar nova análise de solo em 2-3 anos para ajuste do plano de fertilização de {resultado['propriedade']}.",
        "Micronutrientes: Verificar necessidade de Zn (0,5-1,0 kg/ha) e B (0,5 kg/ha) via foliar ou no sulco, "
        "especialmente em solos arenosos.",
        "Doses de K2O acima de 80 kg/ha a lanço devem ser parceladas para evitar salinização.",
    ]
    for rec in recomendacoes:
        story.append(Paragraph(f"- {rec}", styles["corpo"]))
    story.append(Spacer(1, 0.4*cm))

    # -----------------------------------------------------------------------
    # RODAPÉ
    # -----------------------------------------------------------------------
    story.append(HRFlowable(width=W, thickness=0.5, color=VERDE_MEDIO))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "AVISO: Este laudo é uma ferramenta de apoio à decisão e não substitui o acompanhamento de um "
        "Engenheiro Agrônomo habilitado. As recomendações são baseadas em tabelas da Embrapa Cerrados (2004) "
        "e devem ser adaptadas às condições específicas da propriedade.",
        styles["alerta"]
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "AgroBot V7 — Desenvolvido por Jonnathan Marques, Eng. Agrônomo | jonnathan.ecoflora@gmail.com",
        styles["rodape"]
    ))

    doc.build(story)
    return caminho


# =============================================================================
# TESTE LOCAL
# =============================================================================
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from engine import gerar_laudo

    dados = {
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

    resultado = gerar_laudo(dados)
    caminho = gerar_pdf(resultado, "1008", output_dir=os.path.dirname(os.path.abspath(__file__)))
    print(f"PDF gerado: {caminho}")


# =============================================================================
# ADAPTADOR - telegram_bot.py importa AgroPDFPro
# =============================================================================

import tempfile as _tempfile

class AgroPDFPro:
    def gerar_laudo(self, resultado: dict, dados_usuario: dict) -> str:
        from datetime import datetime
        numero_laudo = datetime.now().strftime("%Y%m%d%H%M%S")
        output_dir   = _tempfile.gettempdir()
        if not resultado.get("solicitante"):
            resultado["solicitante"] = dados_usuario.get("nome", "cliente")
        if not resultado.get("propriedade"):
            resultado["propriedade"] = dados_usuario.get("propriedade", "propriedade")
        return gerar_pdf(resultado, numero_laudo, output_dir=output_dir)
