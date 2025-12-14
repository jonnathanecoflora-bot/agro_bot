import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agrobot.vision import GeminiVision
from agrobot.engine import AgroEnginePro
from agrobot.pdf_generator import AgroPDFPro

def test_pipeline():
    logger.info("🚀 STARTING CRITICAL SYSTEM VERIFICATION")
    
    # --- STEP 1: TEST ENGINE & PDF WITH MOCK DATA (Simulate Manual Input) ---
    logger.info("--- STEP 1: SIMULATING MANUAL INPUT FLOW ---")
    
    # Mock data as if it came from the manual conversation (flat structure mostly)
    # The user manual flow collects these. 
    # Let's verify if we need to restructure it HERE or if the Bot does it.
    # The requirement is that the Bot MUST restructure it. 
    # So we will verify if AgroEnginePro accepts the NESTED structure correctly.
    
    nested_mock_data = {
        'fisica': {
            'argila': 33.6,
            'areia': 60.0, # Adding values to be safe
            'silte': 6.4
        },
        'quimica': {
            'ph_cacl2': 5.3,
            'ph_agua': 0,
            'fosforo_mg': 5.7,
            'potassio_mg': 47.5,
            'calcio_cmolc': 1.0,
            'magnesio_cmolc': 0.41,
            'aluminio_cmolc': 0.33,
            'h_al_cmolc': 3.43,
            'ctc_total': 4.96,
            'v_percentual': 30.0,
            'm_percentual': 15.0,
            'materia_organica': 17.4
        },
        'micronutrientes': {
            'enxofre': 10.0,
            'boro': 0.5,
            'zinco': 2.0,
            'cobre': 0,
            'manganes': 0,
            'ferro': 0
        }
    }
    
    user_data = {
        'nome': 'Debug User',
        'propriedade': 'Debug Farm',
        'cultura': 'Milho',
        'expectativa': 'Alta'
    }

    try:
        logger.info("Initializing AgroEnginePro...")
        engine = AgroEnginePro(nested_mock_data, user_data)
        
        logger.info("Processing data...")
        results = engine.processar()
        
        if results.get('erro'):
            logger.error(f"❌ Engine Error: {results.get('mensagens')}")
            return False
        else:
            logger.info("✅ Engine processed successfully.")
            
        # Add metadata for PDF
        results['meta_dados'] = user_data
        
        logger.info("Generating PDF...")
        pdf_gen = AgroPDFPro()
        pdf_path = pdf_gen.gerar_pdf(results)
        
        if os.path.exists(pdf_path):
            logger.info(f"✅ PDF Generated: {pdf_path}")
        else:
            logger.error("❌ PDF file was not created.")
            return False

    except Exception as e:
        logger.error(f"❌ Exception in Manual/Engine/PDF Pipeline: {e}", exc_info=True)
        return False


    # --- STEP 2: TEST VISION RECOGNITION (Mocking the Image Processing) ---
    logger.info("\n--- STEP 2: TESTING VISION MODULE (Mock File) ---")
    
    # We can't easily rely on a real API call without a real file and key.
    # But we can check if the class instantiates and has the cleaning logic.
    
    try:
        vision = GeminiVision()
        
        # Test clean_json_string logic if exposed, or check a private method if we add one.
        # For now, let's just assert the class exists.
        logger.info("✅ GeminiVision instantiated.")
        
        # Verify if api key is present
        if not os.getenv("GEMINI_API_KEY"):
             logger.warning("⚠️ GEMINI_API_KEY not found in env.")
        else:
             logger.info("✅ GEMINI_API_KEY found.")

    except Exception as e:
        logger.error(f"❌ Vision Init Failed: {e}")
        return False
        
    logger.info("\n🚀 SYSTEM VERIFICATION COMPLETED SUCCESSFULLY")
    return True

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
