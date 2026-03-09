#!/usr/bin/env python3
"""
AgroBot V7 - Telegram Bot
Correção:
- extract_data (DocumentAI/Gemini) é bloqueante e travava o event loop.
  Agora roda em thread + timeout.
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)


from PIL import Image, ImageEnhance, ImageOps
from agrobot.vision import get_vision
from agrobot.engine import AgroEnginePro
from agrobot.pdf_generator import AgroPDFPro

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

AGUARDANDO = 0
COLETANDO_PARAMETROS = 1
COLETANDO_INFO_USUARIO = 2

PARAMETROS_SOLO = [
    "ph_agua",
    "ph_cacl2",
    "argila",
    "fosforo_mg",
    "potassio_mg",
    "materia_organica",
    "calcio_cmolc",
    "magnesio_cmolc",
    "aluminio_cmolc",
    "hidrogenio_cmolc",
    "h_al_cmolc",
]

NOMES_PARAMETROS = {
    "ph_agua": "pH em Agua",
    "ph_cacl2": "pH em CaCl2",
    "argila": "Argila (%)",
    "fosforo_mg": "Fosforo P (mg/dm3)",
    "potassio_mg": "Potassio K (mg/dm3)",
    "materia_organica": "Materia Organica (g/dm3)",
    "calcio_cmolc": "Calcio Ca (cmolc/dm3)",
    "magnesio_cmolc": "Magnesio Mg (cmolc/dm3)",
    "aluminio_cmolc": "Aluminio Al (cmolc/dm3)",
    "hidrogenio_cmolc": "Hidrogenio H (cmolc/dm3)",
    "h_al_cmolc": "H+Al (cmolc/dm3)",
}



def preprocess_for_ocr(input_path: str) -> str:
    """
    Pré-processamento leve para melhorar OCR em tabelas pequenas:
    - Converte para PNG
    - Corrige rotação EXIF
    - Autocontraste
    - Aumenta contraste
    - Upscale 2x (Lanczos)
    Retorna o caminho do arquivo processado.
    """
    img = Image.open(input_path)
    img = ImageOps.exif_transpose(img)

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(1.4)

    w, h = img.size
    img = img.resize((w * 2, h * 2), resample=Image.LANCZOS)

    out_path = str(Path(input_path).with_suffix("")) + "_ocr.png"
    img.save(out_path, format="PNG", optimize=True)
    return out_path

def _safe_ext_from_filename(filename: str) -> str:
    if not filename:
        return ".pdf"
    name = filename.lower().strip()
    _, ext = os.path.splitext(name)
    if ext in (".pdf", ".png", ".jpg", ".jpeg"):
        return ext
    return ".pdf"


class AgroBotV7Simplificado:
    def __init__(self):
        self.vision = get_vision()
        self.pdf_gen = AgroPDFPro()
        self.dados_manuais = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user.first_name
        msg = (
            f"AGROBOT V7\n\n"
            f"Ola {user}.\n\n"
            "Opcoes:\n"
            "1) Envie FOTO ou PDF da analise de solo\n"
            "2) Digite /manual para entrada manual\n"
            "3) Digite /sobre\n"
        )
        await update.message.reply_text(msg)
        return AGUARDANDO

    async def sobre(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        carta = (
            "AGROBOT V7\n\n"
            "Ferramenta de apoio para interpretacao de analise de solo e recomendacoes.\n"
            "Nao substitui Engenheiro Agronomo.\n"
        )
        await update.message.reply_text(carta)
        return AGUARDANDO

    async def manual(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data.clear()
        self.dados_manuais = {}
        context.user_data["modo_manual"] = True
        context.user_data["dados_solo"] = None
        await update.message.reply_text("Entrada manual.\n\n1) Seu nome completo:")
        return COLETANDO_INFO_USUARIO

    async def coletar_info_usuario(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        texto = update.message.text.strip()
        modo_manual = bool(context.user_data.get("modo_manual"))

        if "nome" not in context.user_data:
            context.user_data["nome"] = texto
            await update.message.reply_text("2) Nome da propriedade/fazenda:")
            return COLETANDO_INFO_USUARIO

        if "propriedade" not in context.user_data:
            context.user_data["propriedade"] = texto
            keyboard = [["Soja", "Milho"], ["Cafe", "Feijao"], ["Outros"]]
            await update.message.reply_text(
                "3) Cultura:",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
            )
            return COLETANDO_INFO_USUARIO

        if "cultura" not in context.user_data:
            context.user_data["cultura"] = texto
            await update.message.reply_text(
                "4) Expectativa de produtividade? (Ex: Alta, Media, Baixa, 60 sc/ha)",
                reply_markup=ReplyKeyboardRemove(),
            )
            return COLETANDO_INFO_USUARIO

        context.user_data["expectativa"] = texto if texto else "Media"

        if not modo_manual:
            await update.message.reply_text("Processando analise...")
            return await self.gerar_laudo(update, context)

        context.user_data["parametros"] = list(PARAMETROS_SOLO)
        context.user_data["parametro_atual"] = 0
        self.dados_manuais = {}

        p0 = context.user_data["parametros"][0]
        await update.message.reply_text(
            f"Agora os dados do solo.\n\n1) {NOMES_PARAMETROS.get(p0, p0)}:\n(Digite 0 se nao tiver)"
        )
        return COLETANDO_PARAMETROS

    async def coletar_parametro(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        texto = update.message.text.strip().replace(",", ".")
        parametros = context.user_data.get("parametros", [])
        idx = int(context.user_data.get("parametro_atual", 0))

        if not parametros or idx >= len(parametros):
            await update.message.reply_text("Erro interno. Use /manual novamente.")
            return ConversationHandler.END

        try:
            valor = float(texto)
        except ValueError:
            await update.message.reply_text("Valor invalido. Digite apenas numeros.")
            return COLETANDO_PARAMETROS

        chave = parametros[idx]
        self.dados_manuais[chave] = valor

        idx += 1
        context.user_data["parametro_atual"] = idx

        if idx < len(parametros):
            prox = parametros[idx]
            await update.message.reply_text(
                f"{idx+1}) {NOMES_PARAMETROS.get(prox, prox)}:\n(Digite 0 se nao tiver)"
            )
            return COLETANDO_PARAMETROS

        context.user_data["dados_manuais"] = dict(self.dados_manuais)
        await update.message.reply_text("Dados coletados. Processando analise...")
        return await self.gerar_laudo(update, context)

    async def gerar_laudo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            dados_usuario = {
                "nome": context.user_data.get("nome"),
                "propriedade": context.user_data.get("propriedade"),
                "cultura": context.user_data.get("cultura"),
                "expectativa": context.user_data.get("expectativa", "Media"),
            }

            dados_automaticos = context.user_data.get("dados_solo")
            dados_manuais_ctx = context.user_data.get("dados_manuais") or {}
            modo_manual = bool(context.user_data.get("modo_manual")) or bool(dados_manuais_ctx)

            if modo_manual:
                dados_para_engine = dados_manuais_ctx if dados_manuais_ctx else self.dados_manuais
                engine = AgroEnginePro({}, dados_usuario)
                resultado = engine.processar_com_dados_manuais(dados_para_engine)
            else:
                engine = AgroEnginePro(dados_automaticos, dados_usuario)
                resultado = engine.processar()

            mensagens = resultado.get("mensagens", [])
            tem_aviso_apenas = all("AVISO" in m for m in mensagens) if mensagens else False
            if resultado.get("erro") and not tem_aviso_apenas:
                err_msg = mensagens[0] if mensagens else "Erro desconhecido"
                await update.message.reply_text(f"Erro: {err_msg}\nUse /manual para tentar novamente.")
                return ConversationHandler.END

            resultado["meta_dados"] = dados_usuario

            pdf_path = self.pdf_gen.gerar_laudo(resultado, dados_usuario)
            if not pdf_path or not os.path.exists(pdf_path):
                raise RuntimeError("Falha ao gerar PDF")

            with open(pdf_path, "rb") as pdf_file:
                caption = (
                    "LAUDO TECNICO GERADO\n\n"
                    f"Cliente: {dados_usuario.get('nome')}\n"
                    f"Propriedade: {dados_usuario.get('propriedade')}\n"
                    f"Cultura: {dados_usuario.get('cultura')}\n"
                )
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=pdf_file,
                    caption=caption,
                )

            try:
                os.remove(pdf_path)
            except Exception:
                pass

            self.dados_manuais.clear()
            context.user_data.clear()

            await update.message.reply_text("Concluido. Para nova analise, use /start")
            return ConversationHandler.END

        except Exception as e:
            logger.error("Erro ao gerar laudo: %s", e, exc_info=True)
            await update.message.reply_text("Erro ao processar. Use /start.")
            return ConversationHandler.END

    async def receber_arquivo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file_path = None
        try:
            if update.message.document:
                file_obj = await update.message.document.get_file()
                ext = _safe_ext_from_filename(update.message.document.file_name or "")
            else:
                file_obj = await update.message.photo[-1].get_file()
                ext = ".jpg"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_id = update.effective_user.id
            file_path = f"temp_{user_id}_{timestamp}{ext}"

            await file_obj.download_to_drive(file_path)
            await update.message.reply_text("Lendo arquivo e extraindo dados...")

            extract_coro = asyncio.to_thread(self.vision.extract_data, file_path)
            try:
                dados = await asyncio.wait_for(extract_coro, timeout=120)
            except asyncio.TimeoutError:
                logger.error("Timeout na extracao de dados (%s)", file_path)
                await update.message.reply_text(
                    "Demorou demais para ler o arquivo (timeout). "
                    "Tente novamente com uma foto mais nítida ou use /manual."
                )
                return AGUARDANDO

            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                file_path = None

            if not dados:
                await update.message.reply_text("Nao consegui ler os dados. Use /manual.")
                return AGUARDANDO

            context.user_data.clear()
            context.user_data["modo_manual"] = False
            context.user_data["dados_solo"] = dados

            await update.message.reply_text("Leitura concluida.\n\n1) Seu nome completo:")
            return COLETANDO_INFO_USUARIO

        except Exception as e:
            logger.error("Erro ao processar arquivo: %s", e, exc_info=True)
            await update.message.reply_text("Erro ao processar arquivo. Use /manual.")
            return AGUARDANDO

        finally:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.dados_manuais.clear()
        context.user_data.clear()
        await update.message.reply_text("Cancelado. Use /start.")
        return ConversationHandler.END

    def main(self):
        if not TOKEN:
            print("ERRO: TELEGRAM_TOKEN nao configurada no .env")
            return

        app = ApplicationBuilder().token(TOKEN).build()

        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.start),
                CommandHandler("manual", self.manual),
                CommandHandler("sobre", self.sobre),
                MessageHandler(filters.PHOTO | filters.Document.ALL, self.receber_arquivo),
            ],
            states={
                AGUARDANDO: [
                    CommandHandler("manual", self.manual),
                    CommandHandler("sobre", self.sobre),
                    MessageHandler(filters.PHOTO | filters.Document.ALL, self.receber_arquivo),
                ],
                COLETANDO_PARAMETROS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.coletar_parametro)
                ],
                COLETANDO_INFO_USUARIO: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.coletar_info_usuario)
                ],
            },
            fallbacks=[CommandHandler("cancelar", self.cancelar)],
        )

        app.add_handler(conv_handler)
        app.run_polling()


if __name__ == "__main__":
    bot = AgroBotV7Simplificado()
    bot.main()
