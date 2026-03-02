# 🌱 AgroBot V7 — Sistema de Recomendação Agronômica com IA

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Base_Técnica-Embrapa_Cerrados-green?style=for-the-badge"/>
</p>

<p align="center">
  <b>Bot de Telegram que analisa fotos de laudos de solo com IA e gera recomendações técnicas de calagem e adubação — gratuito para pequenos produtores rurais.</b>
</p>

---

## 🎯 Sobre o Projeto

O **AgroBot V7** nasceu da necessidade de democratizar o acesso à assistência técnica agronômica no Brasil. Pequenos produtores rurais muitas vezes não têm acesso fácil a um engenheiro agrônomo para interpretar análises de solo — esse bot resolve isso via Telegram, de forma gratuita e acessível.

O produtor tira uma foto da análise de solo no laboratório, envia para o bot, e em segundos recebe:
- Diagnóstico completo da fertilidade do solo
- Recomendação de calagem com cálculo preciso
- Recomendação de adubação por cultura
- Sugestão de formulação NPK
- Laudo técnico em PDF para guardar e compartilhar

> ⚠️ **Ferramenta de apoio** — complementa, não substitui, o trabalho do(a) Engenheiro(a) Agrônomo(a).

---

## 🚀 Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📸 Leitura por foto | Envia foto do laudo de solo e a IA extrai os dados automaticamente |
| ✍️ Entrada manual | Inserção passo a passo dos dados da análise |
| 🧪 Diagnóstico de fertilidade | Interpretação completa de pH, MO, P, K, Ca, Mg, Al, CTC |
| 🪨 Cálculo de calagem | 3 métodos: SMP, Saturação por Bases, Neutralização de Al |
| 🌽 Adubação por cultura | Recomendações específicas para soja, milho, algodão e outras |
| 📦 Formulação NPK | Sugestão da melhor formulação com base nos resultados |
| 📄 Laudo em PDF | Geração automática de laudo técnico para download |
| 🗄️ Banco de laudos | Histórico de análises realizadas por usuário |

---

## 🏗️ Arquitetura

```
agro_bot/
├── agrobot/              # Módulos principais
│   ├── soil_analyzer.py  # Análise e diagnóstico do solo
│   ├── calculator.py     # Cálculos de calagem e adubação
│   ├── pdf_generator.py  # Geração de laudos em PDF
│   └── vision.py         # Leitura de fotos com Google Gemini
├── tests/                # Testes de validação
├── docs/                 # Documentação e imagens
├── telegram_bot.py       # Interface com o Telegram
├── server.py             # Servidor de suporte
├── main.py               # Ponto de entrada
└── requirements.txt
```

**Fluxo principal:**

```
Usuário envia foto/dados
        ↓
Google Gemini Vision (extração dos dados)
        ↓
Motor de Análise (diagnóstico de fertilidade)
        ↓
Calculadora Agronômica (Embrapa Cerrados)
        ↓
Gerador de Laudo PDF
        ↓
Usuário recebe recomendações + PDF no Telegram
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11** — linguagem principal
- **Google Gemini Vision** — leitura e interpretação de fotos de laudos
- **python-telegram-bot** — integração com a API do Telegram
- **ReportLab** — geração de laudos em PDF
- **Base técnica: Embrapa Cerrados** — algoritmos de recomendação

---

## ⚙️ Como Rodar Localmente

### Pré-requisitos
- Python 3.11+
- Conta no [Telegram](https://telegram.org/) e um bot criado via [@BotFather](https://t.me/BotFather)
- Chave de API do [Google Gemini](https://aistudio.google.com/)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/jonnathanecoflora-bot/agro_bot.git
cd agro_bot

# 2. Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves
```

### Configuração do `.env`

```env
TELEGRAM_TOKEN=seu_token_aqui
GEMINI_API_KEY=sua_chave_aqui
```

### Execução

```bash
python main.py
```

---

## 🌾 Exemplo de Uso

1. Abra o bot no Telegram
2. Envie `/start`
3. Escolha **"Analisar por foto"** ou **"Entrada manual"**
4. Envie a foto do laudo de solo (se escolheu por foto)
5. Informe a cultura desejada (soja, milho, etc.)
6. Receba o diagnóstico completo + laudo em PDF

---

## 📁 Estrutura de Testes

A pasta `tests/` contém scripts de validação dos principais módulos:

- `test_vision.py` — testa a leitura de laudos por imagem
- `test_vision_real.py` — testa com imagens reais de campo
- `teste_manual_full.py` — testa o fluxo completo de entrada manual
- `verify_corn_logic.py` — valida os cálculos de adubação para milho

---

## 👨‍🌾 Sobre o Autor

**Jonnathan Marques** — Engenheiro Agrônomo  
📧 jonnathan.ecoflora@gmail.com

Desenvolvido com o propósito de levar tecnologia de precisão ao campo brasileiro, especialmente para agricultores familiares e pequenos produtores que não têm acesso fácil à assistência técnica qualificada.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Feito com 💚 para o campo brasileiro
</p>
