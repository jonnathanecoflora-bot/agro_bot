
import os
import logging
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

from agrobot.vision import GeminiVision
from agrobot.engine import AgroBotEngine

load_dotenv()

app = Flask(__name__)

# Configurações do WhatsApp
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "") # Defina VERIFY_TOKEN no .env
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") # Token de acesso temporário/permanente
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID") # ID do número (não é o número de telefone!)

# Logger
logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Validação do Webhook pelo Facebook (Meta)"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.error("VERIFICATION_FAILED")
            return "Forbidden", 403
    return "Ignored", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Recebimento de Mensagens"""
    data = request.get_json()
    logging.info(f"Recebido: {data}")

    if data.get("object") == "whatsapp_business_account":
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for msg in value["messages"]:
                            process_message(msg)
        except Exception as e:
            logging.error(f"Erro ao processar mensagem: {e}")
            
    return "EVENT_RECEIVED", 200

def process_message(msg):
    """Lógica de roteamento da mensagem"""
    from_number = msg["from"]
    msg_type = msg["type"]
    
    # 1. Se for Texto
    if msg_type == "text":
        texto = msg["text"]["body"]
        send_whatsapp_message(from_number, f"Olá! Recebi sua mensagem: '{texto}'.\n\nSou o AgroBot. Por favor, envie uma FOTO ou PDF da sua análise de solo para eu gerar o laudo.")

    # 2. Se for Imagem ou Documento
    elif msg_type == "image" or msg_type == "document":
        media_id = msg[msg_type]["id"]
        send_whatsapp_message(from_number, "🚜 Recebi seu arquivo! Estou processando com IA... Aguarde um instante.")
        
        # Aqui entra a lógica de download e processamento
        handle_media_analysis(from_number, media_id, msg_type)

    else:
        send_whatsapp_message(from_number, "Desculpe, só entendo Texto, Fotos e PDFs de análise de solo.")

def handle_media_analysis(user_phone, media_id, media_type):
    """Baixa a mídia, passa no Gemini e devolve o Laudo"""
    try:
        # A. Obter URL da mídia
        url_info = f"https://graph.facebook.com/v21.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        resp = requests.get(url_info, headers=headers)
        
        if resp.status_code != 200:
            logging.error(f"Erro ao pegar URL da mídia: {resp.text}")
            return

        media_url = resp.json().get("url")
        
        # B. Baixar o Arquivo
        # Para downloads de mídia do WhatsApp é preciso autenticação no header
        media_resp = requests.get(media_url, headers=headers)
        
        filename = f"temp_{media_id}.{'jpg' if media_type == 'image' else 'pdf'}"
        with open(filename, "wb") as f:
            f.write(media_resp.content)
            
        # C. Visão Computacional
        vision = GeminiVision()
        dados_solo = vision.extract_data(filename)
        
        # D. Motor Agronômico
        if dados_solo:
            engine = AgroBotEngine(dados_solo, "Soja (Padrão)")
            resultado = engine.processar()
            
            # E. Gerar e Enviar Texto do Laudo
            # (Aqui simplificamos gerando texto, mas poderíamos gerar PDF)
            laudo_text = formatar_laudo_whatsapp(resultado)
            send_whatsapp_message(user_phone, laudo_text)
        else:
            send_whatsapp_message(user_phone, "❌ Não consegui ler os dados da análise. A foto está nítida?")
            
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        logging.error(f"Falha na análise: {e}")
        send_whatsapp_message(user_phone, f"Ocorreu um erro interno: {str(e)}")

def send_whatsapp_message(to, body):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body}
    }
    
    requests.post(url, headers=headers, json=payload)

def formatar_laudo_whatsapp(resultado):
    """Formata o dict de resultado em uma mensagem bonita do WhatsApp"""
    rec = resultado['recomendacao']
    diag = resultado['diagnostico']
    
    return f"""*🌱 LAUDO AGROBOT*
    
*Diagnóstico:*
🔬 Textura: {diag['textura']}
🧪 pH: {diag['ph_interp']}

*Recomendação:*
🚜 *Calagem*: {rec['calagem']['dose_ton_ha']} ton/ha
💊 *Fósforo*: {rec['adubacao']['fosforo']['dose_produto']} kg/ha ({rec['adubacao']['fosforo']['produto']})
💎 *Potássio*: {rec['adubacao']['potassio']['dose_total']} kg/ha

_Consulte sempre um Eng. Agrônomo local._
"""

if __name__ == "__main__":
    app.run(port=5000, debug=True)
