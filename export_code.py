
import os
import re

files_to_read = [
    "telegram_bot.py",
    "agrobot/engine.py",
    "agrobot/vision.py",
    "agrobot/pdf_generator.py", # Incluir PDF Generator
    "agrobot/main.py",
    ".env",
    "server.py", # Incluir server.py também
    "requirements.txt"  # Se existir
]

output_file = "agrobot_full_code_safe.md"

# Padrões para remover chaves (Regex)
PATTERNS = [
    (r'(GEMINI_API_KEY\s*=\s*)(.+)', r'\1[REDACTED_GEMINI_KEY]'),
    (r'(TELEGRAM_TOKEN\s*=\s*)(.+)', r'\1[REDACTED_TELEGRAM_TOKEN]'),
    (r'(WHATSAPP_TOKEN\s*=\s*)(.+)', r'\1[REDACTED_WHATSAPP_TOKEN]'),
    (r'(PHONE_NUMBER_ID\s*=\s*)(.+)', r'\1[REDACTED_PHONE_ID]'),
    (r'(VERIFY_TOKEN\s*=\s*)(["\'].+["\'])', r'\1"[REDACTED_VERIFY_TOKEN]"')
]

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("# AgroBot Source Code Dump (Sanitized)\n\n")
    
    for fname in files_to_read:
        if os.path.exists(fname):
            outfile.write(f"## File: `{fname}`\n")
            
            # Detecta linguagem para markdown
            ext = fname.split('.')[-1]
            lang = 'python' if ext == 'py' else 'text'
            if ext == 'env': lang = 'bash'
            
            outfile.write(f"```{lang}\n")
            
            with open(fname, "r", encoding="utf-8") as infile:
                content = infile.read()
                
                # Aplica censura
                for pattern, replace in PATTERNS:
                    content = re.sub(pattern, replace, content)
                
                outfile.write(content)
            
            outfile.write("\n```\n\n")
        else:
            # Não poluir o documento com arquivos que não existem
            pass

print(f"✅ Código SEGURO exportado para: {os.path.abspath(output_file)}")
