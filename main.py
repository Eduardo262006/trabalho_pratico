import logging
from src.extract.nasa_power_extractor import NasaPowerExtractor

def main():
    logging.info("Extração NASA POWER")
    
    nasa_extractor = NasaPowerExtractor()
    
    # Parâmetros para Portugal (Centroid)
    country_code = "PT"
    lat = 39.3999
    lon = -8.2245
    start_year = "2000"
    end_year = "2023"
    
    try:
        nasa_extractor.extract_centroid_data(
            country_code=country_code,
            lat=lat,
            lon=lon,
            start_year=start_year,
            end_year=end_year
        )
        logging.info("Extração feita com sucesso.")
        
    except Exception as e:
        logging.error(f"Ocorreu um erro crítico durante a execução do main: {e}")

if __name__ == "__main__":
    main()