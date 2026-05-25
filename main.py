import logging
import os
import sys  # Garante a paragem segura do script em caso de falha

from src.extract.nasa_power_extractor import NasaPowerExtractor
from src.transform.nasa_power_transformer import NasaPowerTransformer

# Configuração padrão de logging para acompanhar a execução no terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("=== A iniciar o pipeline de Dados (Economia Global & Desenvolvimento) ===")
    
    # Parâmetros globais do pipeline
    country_code = "PT"
    start_year = "2000"
    end_year = "2023"
    
    # PADRONIZAÇÃO CRÍTICA: O nome segue rigidamente a convenção da Spec
    # PADRONIZAÇÃO CRÍTICA: O novo nome limpo
    nasa_raw_filename = f"nasa_{country_code.lower()}.json"
    nasa_raw_filepath = os.path.join("data/raw", nasa_raw_filename)

    # ==========================================
    # FASE 1: EXTRAÇÃO (SEMANA 1)
    # ==========================================
    
    # 1.1 Verificação e Extração NASA
    if not os.path.exists(nasa_raw_filepath):
        logging.info("Ficheiro bruto da NASA não encontrado. A iniciar extração...")
        nasa_extractor = NasaPowerExtractor()
        lat = 39.3999
        lon = -8.2245
        try:
            nasa_extractor.extract_centroid_data(
                country_code=country_code,
                lat=lat,
                lon=lon,
                start_year=start_year,
                end_year=end_year
            )
        except Exception as e:
            logging.error(f"Erro crítico na extração da NASA: {e}")
            sys.exit(1)  # Proteção contra erros em cascata
    else:
        logging.info(f"Dados brutos da NASA já existem em: {nasa_raw_filepath}. A saltar extração.")

    # Nota: A integração dos ficheiros do World Bank do teu colega entrará aqui 
    # assim que a classe de extração dele for integrada no fluxo principal.

    # ==========================================
    # FASE 2: TRANSFORMAÇÃO (SEMANA 2)
    # ==========================================
    logging.info("--- A iniciar a Fase de Transformação da NASA ---")
    transformer = NasaPowerTransformer()
    
    try:
        # Executa a transformação do JSON bruto para a camada staging em Parquet
        transformer.transform_file(nasa_raw_filename)
        logging.info("Transformação dos dados da NASA concluída com sucesso.")
        
    except Exception as e:
        logging.error(f"Erro crítico na transformação da NASA: {e}")
        sys.exit(1)

    logging.info("=== Pipeline executado com sucesso até à Fase 2 ===")

if __name__ == "__main__":
    main()