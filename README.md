# AgroBot V7 — Sistema de Recomendação Agronômica com IA

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google-Document_AI-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Google-Gemini-8E44AD?style=for-the-badge&logo=google&logoColor=white"/>
  <img src="https://img.shields.io/badge/Base_Técnica-Embrapa_Cerrados_2004-green?style=for-the-badge"/>
</p>

<p align="center">
  <b>Bot de Telegram que lê fotos e PDFs de análise de solo com IA (Document AI + Gemini) e gera laudos técnicos de calagem e adubação em PDF — para pequenos produtores rurais.</b>
</p>

---

## Sobre o Projeto

O **AgroBot V7** democratiza o acesso à assistência técnica agronômica no Brasil. Pequenos produtores enviam uma foto ou PDF da análise de solo pelo Telegram e recebem em segundos um laudo técnico completo com:

- Diagnóstico de fertilidade do solo (pH, MO, P, K, Ca, Mg, Al, CTC, V%, m%)
- Cálculo de calagem pelo método de Saturação por Bases (Embrapa Cerrados, 2004)
- Recomendação de adubação NPK+S em fontes simples (Ureia, SSP, KCl)
- Laudo técnico em PDF para guardar e compartilhar

> **Ferramenta de apoio** — complementa, não substitui, o acompanhamento de um Engenheiro Agrônomo habilitado.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Leitura por foto ou PDF | Google Document AI faz o OCR; Gemini estrutura os dados em JSON |
| Entrada manual | Fluxo guiado passo a passo via conversa no Telegram |
| Diagnóstico de fertilidade | Interpretação de todos os parâmetros do laudo de solo |
| Cálculo de calagem | Método Saturação por Bases — `NC = [(V2 - V1) × T] / PRNT` |
| Adubação por cultura | Tabelas específicas para Soja, Milho e genéricas para demais culturas |
| Fontes simples | Cálculo em Ureia (45-00-00), Superfosfato Simples (00-18-00) e KCl (00-00-60) |
| Laudo em PDF | Gerado automaticamente com ReportLab e enviado direto no chat |

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.11 | Linguagem principal |
| python-telegram-bot 20.x (async) | Interface com a API do Telegram |
| Google Document AI | OCR de fotos e PDFs de laudos de solo |
| Google Gemini 2.5 Flash | Extração estruturada dos dados (JSON) a partir do texto OCR |
| ReportLab | Geração do laudo técnico em PDF |
| Pillow | Pré-processamento de imagem para melhorar qualidade do OCR |
| Base científica: Embrapa Cerrados 2004 | Tabelas de interpretação, calagem e adubação |

---

## Estrutura do Projeto

```
agro_bot/
├── agrobot/
│   ├── engine.py          # Motor agronômico (Embrapa Cerrados 2004)
│   ├── pdf_generator.py   # Geração de laudos em PDF
│   ├── vision.py          # OCR + extração via DocumentAI + Gemini
│   └── knowledge_base.py  # Tabelas de referência (documentação)
├── tests/
│   ├── teste_prova_real.py
│   ├── test_vision.py
│   └── verify_corn_logic.py
├── telegram_bot.py        # Entry point do bot
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

---

## Arquitetura

```
telegram_bot.py               ← Entrada principal (ConversationHandler)
│
├── agrobot/vision.py         ← DocumentAIVision: OCR via GCP + GeminiExtractor: parsing JSON
├── agrobot/engine.py         ← Motor agronômico: classificações + calagem + adubação
├── agrobot/pdf_generator.py  ← Geração do laudo PDF com ReportLab
└── agrobot/knowledge_base.py ← Tabelas de referência Embrapa Cerrados 2004 (documentação)
```

**Fluxo de dados:**

```
Foto/PDF enviado pelo usuário
        ↓
DocumentAIVision.extract_data()
  ├── GCP Document AI → texto OCR bruto
  └── GeminiExtractor → JSON estruturado validado
        ↓
AgroEnginePro.processar()
  └── gerar_laudo() → classificações + calagem + adubação + fontes simples
        ↓
AgroPDFPro.gerar_laudo()
  └── gerar_pdf() → arquivo .pdf em /tmp
        ↓
Bot envia o PDF ao usuário via send_document()
```

**Modo manual** segue o mesmo caminho a partir de `gerar_laudo()`, pulando a etapa de Vision.

---

## Instalação

### Pré-requisitos

- Python 3.11+
- Conta no Google Cloud com Document AI habilitado e um processador do tipo **OCR** criado
- Chave de API do [Google AI Studio](https://aistudio.google.com/) (Gemini)
- Bot criado no Telegram via [@BotFather](https://t.me/BotFather)
- Google Cloud SDK instalado e autenticado (`gcloud auth application-default login`)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/jonnathanecoflora-bot/agro_bot.git
cd agro_bot

# 2. Crie um ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas chaves (veja seção abaixo)
```

---

## Configuração do `.env`

Copie `.env.example` para `.env` e preencha **todas** as variáveis:

```env
# Google Gemini — https://aistudio.google.com/app/apikey
GEMINI_API_KEY=sua_chave_gemini_aqui

# Telegram Bot — obtido via @BotFather
TELEGRAM_TOKEN=seu_token_telegram_aqui

# Google Cloud Document AI
GCP_PROJECT_ID=seu_project_id_gcp
DOCUMENTAI_LOCATION=us
DOCUMENTAI_PROCESSOR_ID=id_do_seu_processador_documentai

# Backend de visão (somente documentai é suportado)
VISION_BACKEND=documentai

# Opcional: nome da amostra preferencial quando o laudo tem múltiplas linhas
# Exemplo: PREFER_AMOSTRA=AM 01
PREFER_AMOSTRA=
```

> **Atenção:** O arquivo `.env` nunca deve ser commitado. Ele está no `.gitignore`.

---

## Como Rodar

```bash
# Ativar o ambiente virtual (se ainda não ativado)
.venv\Scripts\activate

# Iniciar o bot
python telegram_bot.py
```

O bot ficará em polling aguardando mensagens. Para parar, use `Ctrl+C`.

**Testar módulos individualmente:**

```bash
# Motor agronômico (roda um caso de teste embutido)
python agrobot/engine.py

# Gerador de PDF
python agrobot/pdf_generator.py

# Fluxo manual completo (sem Telegram)
python tests/teste_prova_real.py
```

---

## Base Técnica

Todos os cálculos são baseados em:

> **SOUSA, D. M. G. de; LOBATO, E. (Ed.).** *Cerrado: correção do solo e adubação.* 2. ed. Brasília, DF: Embrapa Informação Tecnológica, 2004. 416 p.

**Calagem — Método Saturação por Bases:**

```
NC (t/ha) = [(V2 - V1) × T] / PRNT

V1 = saturação por bases atual do solo (%)
V2 = saturação desejada para a cultura (Soja/Milho: 60%, Arroz/Sorgo: 50%)
T  = CTC a pH 7,0 (cmolc/dm³) = SB + H+Al
PRNT = poder relativo de neutralização do calcário (padrão: 80%)
```

**Culturas suportadas:** Soja, Milho, Feijão, Café, Arroz, Trigo, Sorgo, Milheto e outras (tabela genérica).

---

## Autor

**Jonnathan Marques** — Engenheiro Agrônomo
jonnathan.ecoflora@gmail.com

Desenvolvido para levar tecnologia de precisão ao campo brasileiro, com foco em agricultores familiares e pequenos produtores sem acesso fácil à assistência técnica qualificada.

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">Feito para o campo brasileiro</p>
