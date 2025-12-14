#!/usr/bin/env python3
"""
AgroBot V7 - By Jonnathan Marques (Dez/2025)
Bot Profissional de Agronomia - Versão Simplificada
"""

import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

from agrobot.vision import GeminiVision
from agrobot.engine import AgroEnginePro
from agrobot.pdf_generator import AgroPDFPro

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ESTADOS SIMPLIFICADOS
AGUARDANDO = 0
COLETANDO_PARAMETROS = 1
COLETANDO_INFO_USUARIO = 2
PROCESSANDO = 3

class AgroBotV7Simplificado:
    def __init__(self):
        self.vision = GeminiVision()
        self.pdf_gen = AgroPDFPro()
        self.dados_manuais = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando inicial"""
        user = update.effective_user.first_name
        msg = f"""
        🌱 *AGROBOT V7 - Por Jonnathan Marques*
        
        Olá {user}! Sou seu assistente agronômico digital.
        
        *Escolha uma opção:*
        1️⃣ Envie uma *FOTO* ou *PDF* da análise de solo
        2️⃣ Digite */manual* para entrada manual de dados
        3️⃣ Digite */sobre* para conhecer o projeto
        
        *Desenvolvido por:* Jonnathan Marques, Eng. Agrônomo
        *Email:* jonnathan.ecoflora@gmail.com
        *Dezembro de 2025*
        """
        await update.message.reply_text(msg, parse_mode='Markdown')
        return AGUARDANDO
    
    async def sobre(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sobre o projeto"""
        carta = """
        📜 *CARTA ABERTA AOS AGRICULTORES*
        
        Aos pequenos produtores, agricultores familiares, produtores rurais 
        e estudantes de Agronomia e Ciências Agrárias:
        
        Este sistema foi desenvolvido com o propósito de democratizar 
        o acesso à tecnologia de análise de solo e recomendações técnicas 
        precisas. Reconhecemos os desafios enfrentados por quem produz 
        alimentos no Brasil, especialmente no que diz respeito ao acesso 
        à assistência técnica qualificada.
        
        O AgroBot V7 nasce como uma ferramenta de apoio, complementando 
        (não substituindo) o trabalho do(a) engenheiro(a) agrônomo(a). 
        
        *Nossos objetivos:*
        1. Facilitar a interpretação de análises de solo
        2. Democratizar o conhecimento técnico-científico
        3. Otimizar o uso de corretivos e fertilizantes
        4. Contribuir para uma agricultura mais sustentável
        
        Que esta ferramenta possa auxiliar no dia a dia do campo, 
        trazendo mais tecnologia, precisão e produtividade.
        
        *Atenciosamente,*
        *Jonnathan Marques*
        *Engenheiro Agrônomo - CREA/PR*
        *Dezembro de 2025*
        """
        await update.message.reply_text(carta, parse_mode='Markdown')
        return AGUARDANDO
    
    async def manual(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia entrada manual completa"""
        self.dados_manuais = {}
        
        msg = """
        📝 *ENTRADA MANUAL COMPLETA - REQUERIDA*
        
        Para calcular a CTC exata, preciso de TODOS os parâmetros abaixo.
        Se não tiver algum valor, digite 0.
        
        *Ordem das perguntas:*
        1. pH (Água)
        2. pH (CaCl2)
        3. Argila
        4. Fósforo (P)
        5. Potássio (K)
        6. Matéria Orgânica (MO)
        7. Cálcio (Ca)
        8. Magnésio (Mg)
        9. Alumínio (Al)
        10. Hidrogênio (H) - *Crucial para CTC*
        
        *Vamos começar?*
        """
        await update.message.reply_text(msg, parse_mode='Markdown')
        
        context.user_data['parametros'] = [
            'ph_agua',       # 1
            'ph_cacl2',      # 2
            'argila',        # 3
            'fosforo_mg',    # 4
            'potassio_mg',   # 5
            'materia_organica', # 6
            'calcio_cmolc',  # 7
            'magnesio_cmolc',# 8
            'aluminio_cmolc',# 9
            'hidrogenio_cmolc', # 10 (Item H)
            'h_al_cmolc'        # 11 (H+Al - Fallback)
        ]
        context.user_data['parametro_atual'] = 0
        
        return COLETANDO_INFO_USUARIO
        
        resumo += "\n*Agora preciso de algumas informações:*\n"
        resumo += "*1. Seu nome completo:*"
        
        await update.message.reply_text(resumo, parse_mode='Markdown')
        
        # Limpar dados temporários do contexto
        if 'parametros' in context.user_data:
            del context.user_data['parametros']
        if 'parametro_atual' in context.user_data:
            del context.user_data['parametro_atual']
        
        return COLETANDO_INFO_USUARIO
    
    async def coletar_info_usuario(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Coleta informações do usuário"""
        texto = update.message.text.strip()
        
        if 'nome' not in context.user_data:
            context.user_data['nome'] = texto
            await update.message.reply_text(
                "🏡 *2. Nome da propriedade/fazenda:*"
            )
            return COLETANDO_INFO_USUARIO
        
        elif 'propriedade' not in context.user_data:
            context.user_data['propriedade'] = texto
            
            keyboard = [['Soja', 'Milho'], ['Café', 'Feijão'], ['Outros']]
            await update.message.reply_text(
                "🌱 *3. Para qual cultura?*",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            )
            return COLETANDO_INFO_USUARIO
        
        elif 'cultura' not in context.user_data:
            context.user_data['cultura'] = texto
            
            await update.message.reply_text(
                "📈 *4. Expectativa de produtividade?*\n"
                "(Ex: Alta, Média, Baixa, 60 sc/ha)",
                reply_markup=ReplyKeyboardRemove()
            )
            return COLETANDO_INFO_USUARIO
        
        else:
            context.user_data['expectativa'] = texto
            
            # Iniciar processamento
            await update.message.reply_text(
                "⚙️ *Processando análise...*\n"
                "Calculando com base na Embrapa Cerrados...",
                parse_mode='Markdown'
            )
            
            return await self.gerar_laudo(update, context)
    
    async def gerar_laudo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gera o laudo completo"""
        try:
            # 1. Preparar dados do usuário
            dados_usuario = {
                'nome': context.user_data.get('nome'),
                'propriedade': context.user_data.get('propriedade'),
                'cultura': context.user_data.get('cultura'),
                'expectativa': context.user_data.get('expectativa', 'Média')
            }
            
            # 2. Processamento Inteligente (Auto ou Manual)
            dados_automaticos = context.user_data.get('dados_solo')
            
            logger.info(f"Gerando laudo para {dados_usuario['nome']}. Modo Auto: {bool(dados_automaticos)}")
            
            if dados_automaticos:
                # MODO AUTOMÁTICO (Visão)
                logger.info(f"DADOS ENVIADOS AO ENGINE: {dados_automaticos}")
                engine = AgroEnginePro(dados_automaticos, dados_usuario)
                resultado = engine.processar()
            else:
                # MODO MANUAL
                logger.info(f"DADOS MANUAIS ENVIADOS: {self.dados_manuais}")
                engine = AgroEnginePro({}, dados_usuario)
                resultado = engine.processar_com_dados_manuais(self.dados_manuais)
            
            if resultado.get("erro"):
                erro_msg = resultado.get("mensagens", ["Erro desconhecido"])[0]
                await update.message.reply_text(
                    f"❌ *Erro:* {erro_msg}\n\n"
                    "Use /manual para tentar novamente.",
                    parse_mode='Markdown'
                )
                return ConversationHandler.END
            
            # 4. Adicionar dados do usuário
            resultado['meta_dados'] = dados_usuario
            
            # 5. Gerar PDF
            pdf_path = self.pdf_gen.gerar_pdf(resultado)
            
            if not pdf_path or not os.path.exists(pdf_path):
                raise Exception("Falha ao gerar PDF")
            
            # 6. Enviar PDF
            with open(pdf_path, 'rb') as pdf_file:
                caption = f"""
                📄 *LAUDO TÉCNICO GERADO*
                
                👤 *Cliente:* {dados_usuario['nome']}
                🏡 *Propriedade:* {dados_usuario['propriedade']}
                🌱 *Cultura:* {dados_usuario['cultura']}
                
                *Desenvolvido por:*
                Jonnathan Marques - Eng. Agrônomo
                jonnathan.ecoflora@gmail.com
                Dezembro/2025
                """
                
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=pdf_file,
                    caption=caption,
                    parse_mode='Markdown'
                )
            
            # 7. Limpar arquivo temporário
            try:
                os.remove(pdf_path)
            except:
                pass
            
            # 8. Mensagem final
            await update.message.reply_text(
                "✅ *Análise concluída com sucesso!*\n\n"
                "O laudo técnico foi enviado em PDF.\n\n"
                "*Recomendações gerais:*\n"
                "• Aplique calcário 60-90 dias antes do plantio\n"
                "• Siga as dosagens recomendadas\n"
                "• Monitore a cultura regularmente\n"
                "• Consulte um engenheiro agrônomo local\n\n"
                "*Para nova análise, digite /start*",
                parse_mode='Markdown'
            )
            
            # Limpar dados
            self.dados_manuais.clear()
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Erro ao gerar laudo: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ *Erro ao processar análise.*\n\n"
                "Detalhes: " + str(e)[:100] + "\n\n"
                "Tente novamente com /start",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
    
    async def receber_arquivo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Recebe arquivo (foto/PDF)"""
        try:
            # Determinar tipo de arquivo
            if update.message.document:
                file_obj = await update.message.document.get_file()
                ext = ".pdf"
                tipo = "PDF"
            else:
                # Foto
                file_obj = await update.message.photo[-1].get_file()
                ext = ".jpg"
                tipo = "foto"
            
            # Download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_id = update.effective_user.id
            file_path = f"temp_{user_id}_{timestamp}{ext}"
            
            await file_obj.download_to_drive(file_path)
            
            # Mensagem de processamento
            msg = await update.message.reply_text(
                f"🔍 *Lendo {tipo}...*\n"
                "Processando com IA...",
                parse_mode='Markdown'
            )
            
            # Extrair dados
            dados = self.vision.extract_data(file_path)
            
            # Limpar arquivo
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if not dados:
                await msg.edit_text(
                    "❌ *Não consegui ler os dados.*\n\n"
                    "Possíveis causas:\n"
                    "• Imagem/PDF de baixa qualidade\n"
                    "• Análise fora do padrão\n"
                    "• Reflexos/brilho na foto\n\n"
                    "Tente uma foto mais nítida ou use /manual",
                    parse_mode='Markdown'
                )
                return AGUARDANDO
            
            # Armazenar dados
            context.user_data['dados_solo'] = dados
            context.user_data['modo'] = 'automático'
            
            # Mostrar resumo
            q = dados.get('quimica', {})
            f = dados.get('fisica', {})
            
            # Preparar Argila para exibição
            argila_raw = f.get('argila', 'N/D')
            argila_display = argila_raw
            
            # Tentar limpar para verificar valor
            try:
                if isinstance(argila_raw, str):
                    val = float(argila_raw.replace('%', '').replace(',', '.'))
                else:
                    val = float(argila_raw)
                    
                if val > 100:
                    argila_display = f"{val/10}% (convertido de g/kg)"
                else:
                    argila_display = f"{argila_raw}%"
            except:
                pass

            resumo = f"""
            ✅ *LEITURA CONCLUÍDA*
            
            *Dados extraídos:*
            • pH: {q.get('ph_cacl2', 'N/D')}
            • Argila: {argila_display}
            • P: {q.get('fosforo_mg', 'N/D')} mg/dm³
            • K: {q.get('potassio_mg', 'N/D')} mg/dm³
            • Ca: {q.get('calcio_cmolc', 'N/D')} cmolc/dm³
            • Mg: {q.get('magnesio_cmolc', 'N/D')} cmolc/dm³
            • MO: {q.get('materia_organica', 'N/D')} g/dm³
            
            *Agora preciso de suas informações:*
            *1. Seu nome completo:*
            """
            
            await msg.edit_text(resumo, parse_mode='Markdown')
            
            # Limpar dados manuais se existirem
            self.dados_manuais.clear()
            
            return COLETANDO_INFO_USUARIO
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ *Erro ao processar arquivo.*\n\n"
                "Use /manual para entrada manual.",
                parse_mode='Markdown'
            )
            return AGUARDANDO
    
    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancela operação atual"""
        await update.message.reply_text(
            "❌ Operação cancelada.\n\n"
            "Digite /start para começar novamente.",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Limpar dados
        self.dados_manuais.clear()
        context.user_data.clear()
        
        return ConversationHandler.END
    
    def main(self):
        """Função principal"""
        if not TOKEN:
            print("❌ ERRO: TELEGRAM_TOKEN não configurada no arquivo .env")
            print("Adicione: TELEGRAM_TOKEN=seu_token_aqui")
            return
        
        app = ApplicationBuilder().token(TOKEN).build()
        
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                CommandHandler('manual', self.manual),
                CommandHandler('sobre', self.sobre),
                MessageHandler(filters.PHOTO | filters.Document.PDF, self.receber_arquivo)
            ],
            states={
                AGUARDANDO: [
                    CommandHandler('manual', self.manual),
                    CommandHandler('sobre', self.sobre),
                    MessageHandler(filters.PHOTO | filters.Document.PDF, self.receber_arquivo)
                ],
                COLETANDO_PARAMETROS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.coletar_parametro)
                ],
                COLETANDO_INFO_USUARIO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.coletar_info_usuario)
                ]
            },
            fallbacks=[CommandHandler('cancelar', self.cancelar)]
        )
        
        app.add_handler(conv_handler)
        
        print("=" * 60)
        print("🤖 AGROBOT V7 - SISTEMA DE ANÁLISE DE SOLO")
        print("👨‍🌾 Desenvolvido por: Jonnathan Marques, Eng. Agrônomo")
        print("📧 jonnathan.ecoflora@gmail.com")
        print("📅 Dezembro de 2025")
        print("=" * 60)
        
        app.run_polling()

if __name__ == '__main__':
    bot = AgroBotV7Simplificado()
    bot.main()
