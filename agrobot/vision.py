import os
import json
import re
from typing import Dict, Optional, Any

from dotenv import load_dotenv
load_dotenv()


def _mime(path: str) -> str:
    p = (path or "").lower()
    if p.endswith(".pdf"):
        return "application/pdf"
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".jpg") or p.endswith(".jpeg"):
        return "image/jpeg"
    return "application/octet-stream"


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if not s:
        return None
    m = re.search(r"(-?\d+(?:[.,]\d+)?)", s)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def _gkg_to_pct(v: Optional[float]) -> Optional[float]:
    if v is None:
        return None
    return v / 10.0 if v > 100 else v


def _clean_numeric_dict(d: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for k, v in (d or {}).items():
        fv = _to_float(v)
        if fv is None:
            continue
        out[k] = fv
    return out


def _validate(d: Dict[str, float]) -> bool:
    # sanity check (não é heurística de extração; é proteção contra lixo tipo Protocolo no pH)
    def ok(k, lo, hi):
        return (k not in d) or (lo <= d[k] <= hi)

    return all([
        ok("ph_agua", 3.0, 8.8),
        ok("ph_cacl2", 3.0, 8.8),
        ok("fosforo_mg", 0.0, 300.0),
        ok("potassio_mg", 0.0, 1000.0),
        ok("calcio_cmolc", 0.0, 20.0),
        ok("magnesio_cmolc", 0.0, 20.0),
        ok("aluminio_cmolc", 0.0, 10.0),
        ok("hidrogenio_cmolc", 0.0, 25.0),
        ok("materia_organica", 0.0, 100.0),
        ok("areia_gkg", 0.0, 1000.0),
        ok("silte_gkg", 0.0, 1000.0),
        ok("argila_gkg", 0.0, 1000.0),
    ])


class GeminiExtractor:
    def __init__(self):
        self.api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not self.api_key:
            self.model = None
            return

        # Biblioteca antiga ainda funciona, mas vamos usar ela por compatibilidade mínima.
        # Se quiser migrar depois para google-genai, a interface muda (fazemos isso numa segunda etapa).
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)

        # Modelo confirmado pelo seu teste:
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json", "temperature": 0.0},
        )

    def extract(self, ocr_text: str, prefer_amostra: Optional[str] = None) -> Optional[Dict[str, float]]:
        if not self.model:
            return None

        prefer = (prefer_amostra or "").strip().upper()
        prefer_hint = f"Priorize a linha da amostra '{prefer}'." if prefer else "Se houver mais de uma amostra, extraia a primeira linha de dados da tabela."

        prompt = f"""
Você é um extrator de dados de análise de solo (laudo de laboratório).
Receberá TEXTO OCR de um laudo com tabela.

{prefer_hint}

Extraia APENAS os valores numéricos da TABELA de resultados (ignore protocolo, CNPJ, endereços, datas).
Retorne JSON estrito com as chaves abaixo (somente as que encontrar):

ph_agua
ph_cacl2
fosforo_mg
potassio_mg
calcio_cmolc
magnesio_cmolc
aluminio_cmolc
hidrogenio_cmolc
materia_organica
areia_gkg
silte_gkg
argila_gkg

Regras:
- Não invente valores.
- Se houver duas amostras, não misture as linhas.
- Valores como número (ponto ou vírgula).
- Resposta deve ser SOMENTE JSON.

OCR TEXT:
\"\"\"{ocr_text}\"\"\"
""".strip()

        try:
            resp = self.model.generate_content(prompt)
            raw = (resp.text or "").strip()
            raw = re.sub(r"^```json", "", raw, flags=re.I).strip()
            raw = re.sub(r"```$", "", raw).strip()
            data = json.loads(raw)
            if not isinstance(data, dict):
                return None
            cleaned = _clean_numeric_dict(data)
            if not cleaned:
                return None
            if not _validate(cleaned):
                return None
            return cleaned
        except Exception:
            return None


class DocumentAIVision:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("DOCUMENTAI_LOCATION", "us")
        self.processor_id = os.getenv("DOCUMENTAI_PROCESSOR_ID")

        if not self.project_id or not self.processor_id:
            raise ValueError("Document AI: faltou GCP_PROJECT_ID ou DOCUMENTAI_PROCESSOR_ID no .env")

        from google.cloud import documentai_v1 as documentai
        opts = {"api_endpoint": f"{self.location}-documentai.googleapis.com"}
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        self.name = self.client.processor_path(self.project_id, self.location, self.processor_id)

        self.gemini = GeminiExtractor()

    def extract_data(self, file_path: str) -> Optional[Dict[str, str]]:
        from google.cloud import documentai_v1 as documentai

        if not os.path.exists(file_path):
            return None

        with open(file_path, "rb") as f:
            content = f.read()

        req = documentai.ProcessRequest(
            name=self.name,
            raw_document=documentai.RawDocument(content=content, mime_type=_mime(file_path)),
        )

        result = self.client.process_document(request=req, timeout=60)
        doc = result.document
        ocr_text = doc.text or ""
        if not ocr_text.strip():
            return None

        prefer = (os.getenv("PREFER_AMOSTRA") or "").strip()
        prefer = prefer if prefer else None

        extracted = self.gemini.extract(ocr_text, prefer_amostra=prefer)
        if not extracted:
            return None

        return self._normalize(extracted)

    def _normalize(self, d: Dict[str, float]) -> Dict[str, str]:
        out: Dict[str, str] = {}

        def put(k: str, v: Optional[float], nd=2):
            if v is None:
                return
            s = str(round(float(v), nd)).rstrip("0").rstrip(".")
            out[k] = s

        put("ph_agua", d.get("ph_agua"), 2)
        put("ph_cacl2", d.get("ph_cacl2"), 2)
        put("fosforo_mg", d.get("fosforo_mg"), 1)
        put("potassio_mg", d.get("potassio_mg"), 1)

        put("calcio_cmolc", d.get("calcio_cmolc"), 2)
        put("magnesio_cmolc", d.get("magnesio_cmolc"), 2)
        put("aluminio_cmolc", d.get("aluminio_cmolc"), 2)
        put("hidrogenio_cmolc", d.get("hidrogenio_cmolc"), 2)

        put("materia_organica", d.get("materia_organica"), 1)

        # textura: g/kg -> %
        arg_pct = _gkg_to_pct(d.get("argila_gkg"))
        if arg_pct is not None:
            put("argila", arg_pct, 2)

        # H+Al automático
        h = d.get("hidrogenio_cmolc")
        al = d.get("aluminio_cmolc")
        if h is not None and al is not None:
            put("h_al_cmolc", h + al, 2)

        return out


def get_vision():
    backend = (os.getenv("VISION_BACKEND") or "documentai").strip().lower()
    if backend != "documentai":
        raise ValueError("Use VISION_BACKEND=documentai")
    return DocumentAIVision()
