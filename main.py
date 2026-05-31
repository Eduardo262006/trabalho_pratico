import logging
import os
import sys
import subprocess

# Importações da NASA
from src.extract.nasa_power_extractor import NasaPowerExtractor
from src.transform.nasa_power_transformer import NasaPowerTransformer

# Importação do Merger Final (Camada Gold)
from src.transform.gold_merger import GoldMerger

# Importação do Loader (Base de Dados)
from src.load.duckdb_loader import DuckDBLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("=== A iniciar o Pipeline de Dados (Economia Global & Desenvolvimento) ===")
    
    country_code = "PT"
    start_year = "2000"
    end_year = "2023"
    
    nasa_raw_filename = f"nasa_{country_code.lower()}.json"
    nasa_raw_filepath = os.path.join("data/raw", nasa_raw_filename)

    # ==========================================
    # FASE 1: EXTRAÇÃO (BRONZE)
    # ==========================================
    logging.info("--- Iniciando Fase 1: Extração (Bronze) ---")
    
    # NASA
    if not os.path.exists(nasa_raw_filepath):
        logging.info("A iniciar extração NASA...")
        nasa_extractor = NasaPowerExtractor()
        try:
            nasa_extractor.extract_centroid_data(country_code, 39.3999, -8.2245, start_year, end_year)
        except Exception as e:
            logging.error(f"Erro NASA: {e}")
            sys.exit(1)
    else:
        logging.info("Dados NASA já existem. A saltar extração.")

    # World Bank (Execução isolada para proteger o código do colega)
    logging.info("A iniciar extração World Bank (Script do Colega)...")
    try:
        subprocess.run([sys.executable, "src/extract/world_bank_extractor.py"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error("O script de extração do World Bank falhou.")
        sys.exit(1)


    # ==========================================
    # FASE 2: TRANSFORMAÇÃO (SILVER)
    # ==========================================
    logging.info("--- Iniciando Fase 2: Transformação (Silver) ---")
    
    # NASA
    nasa_transformer = NasaPowerTransformer()
    try:
        nasa_transformer.transform_file(nasa_raw_filename)
    except Exception as e:
        logging.error(f"Erro Transformação NASA: {e}")
        sys.exit(1)

    # World Bank
    logging.info("A iniciar transformação World Bank (Script do Colega)...")
    try:
        subprocess.run([sys.executable, "src/transform/world_bank_transformer.py"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error("O script de transformação do World Bank falhou.")
        sys.exit(1)


    # ==========================================
    # FASE 3: INTEGRAÇÃO (GOLD)
    # ==========================================
    logging.info("--- Iniciando Fase 3: Integração Final (Gold) ---")
    merger = GoldMerger()
    try:
        merger.create_analytical_dataset(country_code=country_code)
    except Exception as e:
        logging.error(f"Erro crítico no Merge final: {e}")
        sys.exit(1)


    # ==========================================
    # FASE 4: CARREGAMENTO (SEMANA 3 - DUCKDB)
    # ==========================================
    logging.info("--- Iniciando Fase 4: Carregamento no Data Warehouse ---")
    loader = DuckDBLoader()
    try:
        loader.load_gold_layer(country_code=country_code)
    except Exception as e:
        logging.error(f"Erro crítico ao carregar dados para o DuckDB: {e}")
        sys.exit(1)

    logging.info("=== Pipeline 100% concluído com sucesso! ===")

if __name__ == "__main__":
    main()