import os
import time
import json
import logging
import requests
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NasaPowerExtractor:
    def __init__(self, output_dir="data/raw", community="RE"):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        self.output_dir = output_dir
        self.community = community
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.session = requests.Session()

    def _make_request_with_retry(self, params, max_retries=4, base_backoff=2):
        """
        Faz o pedido HTTP com Exponential Backoff para proteger o pipeline.
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                
                return response.json()
            
            except RequestException as e:
                logging.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                
                if attempt == max_retries - 1:
                    logging.error("Número máximo de tentativas atingido. A extração falhou.")
                    raise e
                
                sleep_time = base_backoff ** (attempt + 1)
                logging.info(f"A aguardar {sleep_time} segundos antes de tentar novamente...")
                time.sleep(sleep_time)

    def extract_centroid_data(self, country_code, lat, lon, start_year, end_year, parameters="T2M,T2M_MAX,T2M_MIN"):
        """
        Extrai os dados para o ponto centroid do país e guarda num ficheiro JSON.
        """
        logging.info(f"A iniciar extração da NASA POWER para {country_code} ({start_year}-{end_year})...")
        
        params = {
            "parameters": parameters,
            "community": self.community,
            "longitude": lon,
            "latitude": lat,
            "start": start_year,
            "end": end_year,
            "format": "JSON"
        }
        
        raw_data = self._make_request_with_retry(params)
        
        safe_params = parameters.split(",")[0] 
        filename = f"nasa_{country_code.lower()}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Dados guardados em: {filepath}")