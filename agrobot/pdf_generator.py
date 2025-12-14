
import os
import json
import locale
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

# Tentar configurar locale
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    pass

class AgroPDFPro:
    def __init__(self):
        self.db_file = "relatorios_db.json"
        self._init_db()
        self.style = self._criar_estilos()

    def _init_db(self):
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump({"ultimo_id": 1000, "laudos": []}, f)
                
    def _get_next_id(self):
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
            new_id = data.get("ultimo_id", 1000) + 1
            data["ultimo_id"] = new_id
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
            return new_id
        except:
            return 1001

    def _add_laudo_to_db(self, info):
        try:
            with open(self.db_file, 'r') as f:
                data = json.load(f)
            data["laudos"].append(info)
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    @staticmethod
    def _limpar_texto(valor):
        if valor is None: return "-"
        if isinstance(valor, (float, int)):
            return f"{valor:.2f}".replace('.', ',')
        texto = str(valor)
        for item in ['$', '{', '}', '~', '**', '*']:
            texto = texto.replace(item, '')
        return texto.replace('^3', '³').replace('^2', '²').replace('cmolc', 'cmol/dm³').strip()

    def _criar_estilos(self):
        """Define estilos corporativos e corrige o erro de COR_TEXTO"""
        styles = getSampleStyleSheet()
        COR_TEXTO = colors.black  # <--- CORREÇÃO AQUI
        
        # Estilos Personalizados que faltavam
        styles.add(ParagraphStyle(
            name='AgroTitulo',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#1B5E20')
        ))
        
        styles.add(ParagraphStyle(
            name='AgroSecao',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#2E7D32'),
            keepWithNext=True
        ))
        
        styles.add(ParagraphStyle(
            name='AgroTexto',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            leading=14
        ))

        styles.add(ParagraphStyle(
            name='TabelaHeader',
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='TabelaCell',
            fontName='Helvetica',
            fontSize=9,
            textColor=COR_TEXTO,
            alignment=TA_CENTER
        ))

        return styles

    def gerar_pdf(self, dados):
        if dados.get("erro"): return None
            
        meta = dados.get('meta_dados', {})
        solo = dados.get('solo', {})
        diag = dados.get('diagnostico', {})
        adubacao = dados.get('adubacao', {})
        calagem = dados.get('calagem', {})
        eco = dados.get('economia', {})
        formulacao = dados.get('formulacao', {})
        
        laudo_id = self._get_next_id()
        nome_clean = meta.get('nome', 'Alvo').replace(' ', '_')
        nome_arquivo = f"Laudo_{laudo_id}_{nome_clean}.pdf"
        
        doc = SimpleDocTemplate(nome_arquivo, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
        story = []
        styles = self.style
        
        # CABEÇALHO
        self._construir_cabecalho(story, meta, laudo_id)
        
        # METODOLOGIA
        story.append(Paragraph("1. METODOLOGIA E CONTEXTO", styles['AgroSecao']))
        story.append(Paragraph("Este laudo utiliza algoritmos baseados na Embrapa Cerrados (2024).", styles['AgroTexto']))
        
        # DIAGNÓSTICO
        story.append(Paragraph("2. DIAGNÓSTICO DA FERTILIDADE", styles['AgroSecao']))
        self._tabela_resultados(story, solo, diag)
        
        # INTERPRETAÇÃO
        story.append(Paragraph("3. INTERPRETAÇÃO TÉCNICA", styles['AgroSecao']))
        texto = dados.get('texto_interpretativo', '').replace('*', '')
        for p in texto.split('<br/><br/>'):
            if p.strip():
                story.append(Paragraph(p, styles['AgroTexto']))
                story.append(Spacer(1, 0.2*cm))
        
        # CALAGEM
        if calagem:
            story.append(Paragraph("4. PLANO DE CORREÇÃO", styles['AgroSecao']))
            self._tabela_calagem(story, calagem)
            
        # ADUBAÇÃO
        story.append(Paragraph("5. PLANO DE ADUBAÇÃO (NPK)", styles['AgroSecao']))
        self._tabela_adubacao(story, adubacao, formulacao)
        
        # RODAPÉ
        self._construir_rodape(story)
        
        try:
            doc.build(story)
            self._add_laudo_to_db({"id": laudo_id, "nome": meta.get('nome'), "arquivo": nome_arquivo})
            return nome_arquivo
        except Exception as e:
            print(f"Erro PDF: {e}")
            return None

    def _construir_cabecalho(self, story, meta, laudo_id):
        styles = self.style
        story.append(Paragraph("AGROBOT - INTELIGÊNCIA AGRONÔMICA", styles['AgroTitulo']))
        
        data = [
            [f"SOLICITANTE: {self._limpar_texto(meta.get('nome')).upper()}", f"LAUDO: {laudo_id}"],
            [f"PROPRIEDADE: {self._limpar_texto(meta.get('propriedade')).upper()}", f"DATA: {datetime.now().strftime('%d/%m/%Y')}"],
            [f"CULTURA: {self._limpar_texto(meta.get('cultura')).upper()}", ""]
        ]
        t = Table(data, colWidths=[12*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2E7D32')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F8E9')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    def _tabela_resultados(self, story, solo, diag):
        styles = self.style
        header = ["PARÂMETRO", "VALOR", "UNIDADE", "NÍVEL"]
        data = [header]
        
        # Inserir Argila explicitamente
        argila = solo.get('argila', 0)
        data.append(["Argila", f"{argila:.1f}", "%", "TEXTURA"])
        
        params = [
            ('pH (CaCl₂)', 'ph_cacl2', '', 'ph'),
            ('Matéria Orgânica', 'MO', 'g/dm³', 'MO'),
            ('Fósforo (P)', 'P', 'mg/dm³', 'P'),
            ('Potássio (K)', 'K', 'cmol/dm³', 'K'),
            ('Cálcio (Ca)', 'Ca', 'cmol/dm³', 'Ca'),
            ('Magnésio (Mg)', 'Mg', 'cmol/dm³', 'Mg'),
            ('Acidez (H+Al)', 'H_Al', 'cmol/dm³', '-'),
            ('Soma de Bases', 'SB', 'cmol/dm³', '-'),
            ('CTC (pH 7)', 'CTC', 'cmol/dm³', '-'),
            ('Saturação (V%)', 'V', '%', 'V'),
        ]
        
        for label, key, unit, diag_key in params:
            val = self._limpar_texto(solo.get(key))
            nivel = diag.get(diag_key, '-').upper() if diag_key != '-' else '-'
            
            # Formatação condicional
            cell_style = styles['TabelaCell']
            if nivel in ['BAIXO', 'MUITO BAIXO']:
                cell_content = Paragraph(f"<font color='red'><b>{nivel}</b></font>", cell_style)
            else:
                cell_content = Paragraph(nivel, cell_style)
                
            data.append([label, val, unit, cell_content])
            
        t = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (1,0), (-1,-1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    def _tabela_calagem(self, story, calagem):
        styles = self.style
        data = [
            ["INSUMO", "DOSE", "PRNT", "MÉTODO"],
            ["Calcário Dolomítico", f"{calagem.get('dose_t_ha')} t/ha", "80%", "Saturação Bases"]
        ]
        t = Table(data, colWidths=[5*cm, 4*cm, 2*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

    def _tabela_adubacao(self, story, adubacao, formulacao):
        styles = self.style
        # Tabela Nutrientes
        data = [["NUTRIENTE", "DOSE (kg/ha)"]]
        for nut in ['N', 'P2O5', 'K2O', 'S']:
            data.append([nut, str(adubacao.get(nut, 0))])
            
        t = Table(data, colWidths=[5*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))
        
        # Sugestão Prática
        txt = f"<b>SUGESTÃO DE MANEJO:</b><br/>{formulacao.get('texto_completo', 'Sem sugestão.')}"
        story.append(Paragraph(txt, styles['AgroTexto']))

    def _construir_rodape(self, story):
        styles = self.style
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"AgroBot V7 - Gerado em {datetime.now().strftime('%d/%m/%Y')}", styles['TabelaCell']))
