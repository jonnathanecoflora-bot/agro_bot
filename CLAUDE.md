# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Telegram bot (main entry point)
python telegram_bot.py

# Run the WhatsApp webhook server (legacy)
python server.py

# Test the agronomic engine directly
python agrobot/engine.py

# Test the PDF generator directly
python agrobot/pdf_generator.py

# Run integration tests
python tests/teste_manual_full.py
python tests/teste_prova_real.py
python tests/test_vision.py
```

## Environment Setup

Copy `.env.example` to `.env` and fill in:
- `GEMINI_API_KEY` — Google Gemini API key (used for structured data extraction from OCR text)
- `TELEGRAM_TOKEN` — Telegram Bot token
- `GCP_PROJECT_ID`, `DOCUMENTAI_LOCATION`, `DOCUMENTAI_PROCESSOR_ID` — Google Document AI credentials
- `VISION_BACKEND=documentai` — currently only `documentai` is supported
- `PREFER_AMOSTRA` — optional sample label to prefer when the lab report has multiple rows (e.g. `AM 7727`)

Google Document AI requires Application Default Credentials (ADC). Run:
```bash
gcloud auth application-default login
```

## Architecture

The bot is a **Telegram ConversationHandler** pipeline. Two input modes lead to the same output:

```
[Photo/PDF] → DocumentAIVision (OCR) → GeminiExtractor (JSON parse)
                                                     ↓
[/manual] ←→ ConversationHandler (3 states)  → AgroEnginePro.processar()
                  AGUARDANDO                          ↓
                  COLETANDO_INFO_USUARIO          gerar_laudo() (engine.py)
                  COLETANDO_PARAMETROS                ↓
                                              AgroPDFPro.gerar_laudo()
                                                      ↓
                                              send_document (PDF to user)
```

### Key modules

- **`telegram_bot.py`** — Entry point. `AgroBotV7Simplificado` wires the full conversation. `extract_data` is called via `asyncio.to_thread` with a 120s timeout to avoid blocking the event loop.
- **`agrobot/vision.py`** — `DocumentAIVision` sends the file to GCP Document AI for OCR, then passes the raw text to `GeminiExtractor` which returns structured JSON. The `_validate()` function rejects values outside agronomically plausible ranges before they reach the engine.
- **`agrobot/engine.py`** — Pure-Python agronomic calculator. `gerar_laudo(dados: dict)` is the core function. It classifies soil parameters, calculates liming (`calcular_calagem`) and fertilization (`calcular_adubacao`) based on **Embrapa Cerrados 2004** tables. `AgroEnginePro` is an adapter class that translates bot key names (e.g. `fosforo_mg`) to engine keys (e.g. `p`) via `_CHAVES_SOLO`.
- **`agrobot/pdf_generator.py`** — `gerar_pdf()` renders the full agronomic report using ReportLab. `AgroPDFPro` is a thin adapter used by the bot.
- **`agrobot/knowledge_base.py`** — Reference data (Embrapa Cerrados 2004 tables) in Python dict form. Currently used as documentation; the engine has the same logic hardcoded in its classification functions.
- **`server.py`** — Legacy WhatsApp webhook (Flask). Not in active use; imports `GeminiVision` and `AgroBotEngine` which are older class names no longer present in `vision.py` / `engine.py`.

### Data flow — key names

The bot collects soil parameters under these keys (from Document AI or manual input):
`ph_agua`, `ph_cacl2`, `argila`, `fosforo_mg`, `potassio_mg`, `materia_organica`, `calcio_cmolc`, `magnesio_cmolc`, `aluminio_cmolc`, `hidrogenio_cmolc`, `h_al_cmolc`

`_CHAVES_SOLO` in `engine.py` maps them to the engine's internal keys:
`ph_agua`, `ph_cacl2`, `argila`, `p`, `k`, `mo`, `ca`, `mg`, `al`, `h_al`

The `h_al` value is computed as `H + Al` when `h_al_cmolc` is absent.

### PDF generation

PDFs are written to `tempfile.gettempdir()` and deleted after being sent to the user. The file name pattern is `Laudo_<timestamp>_<solicitante>.pdf`.
