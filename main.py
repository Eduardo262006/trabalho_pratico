import logging
import os
import sys
import subprocess
from src.extract.nasa_power_extractor import NasaPowerExtractor
from src.transform.nasa_power_transformer import NasaPowerTransformer
from src.transform.gold_merger import GoldMerger
from src.load.duckdb_loader import DuckDBLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Extração, Transformação, Carregamento ")
    
    country_code = "PT"
    start_year = "2000"
    end_year = "2023"
    
    nasa_raw_filename = f"nasa_{country_code.lower()}.json"
    nasa_raw_filepath = os.path.join("data/raw", nasa_raw_filename)

    # FASE 1: EXTRAÇÃO (BRONZE)
   
    logging.info("Extração (Bronze)")
    
    if not os.path.exists(nasa_raw_filepath):
        nasa_extractor = NasaPowerExtractor()
        try:
            nasa_extractor.extract_centroid_data(country_code, 39.3999, -8.2245, start_year, end_year)
        except Exception as e:
            logging.error(f"Erro NASA: {e}")
            sys.exit(1)
    else:
        logging.info("Dados NASA já existem. A saltar extração.")

    try:
        subprocess.run([sys.executable, "src/extract/world_bank_extractor.py"], check=True)
    except subprocess.CalledProcessError:
        logging.error("O script de extração do World Bank falhou.")
        sys.exit(1)

    # FASE 2: TRANSFORMAÇÃO (SILVER)
  
    logging.info("Transformação (Silver)")
    
    nasa_transformer = NasaPowerTransformer()
    try:
        nasa_transformer.transform_file(nasa_raw_filename)
    except Exception as e:
        logging.error(f"Erro Transformação NASA: {e}")
        sys.exit(1)

    try:
        subprocess.run([sys.executable, "src/transform/world_bank_transformer.py"], check=True)
    except subprocess.CalledProcessError:
        logging.error("O script de transformação do World Bank falhou.")
        sys.exit(1)

    # FASE 3: INTEGRAÇÃO (GOLD)

    logging.info("Integração (Gold)")
    merger = GoldMerger()
    try:
        merger.create_analytical_dataset(country_code=country_code)
    except Exception as e:
        logging.error(f"Erro no Merge: {e}")
        sys.exit(1)

    # FASE 4: CARREGAMENTO (DUCKDB)
    
    logging.info("Carregamento (DuckDB)")
    loader = DuckDBLoader()
    try:
        loader.load_gold_layer(country_code=country_code)
    except Exception as e:
        logging.error(f"Erro crítico ao carregar dados para o DuckDB: {e}")
        sys.exit(1)

    logging.info("Base de Dados pronta na pasta data/database/ ===")

if __name__ == "__main__":
    main()