import os
import time
import json
import logging
import requests
from requests.exceptions import RequestException

# Configuração simples de logging para o terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NasaPowerExtractor:
    def __init__(self, output_dir="data/raw", community="RE"):
        """
        Inicializa o extrator da NASA POWER.
        :param output_dir: Diretório onde os dados brutos serão guardados.
        :param community: Comunidade da NASA (RE = Renewable Energy, AG = Agroclimatology).
        """
        # O endpoint base já reflete a nossa decisão: temporal/monthly/point
        self.base_url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        self.output_dir = output_dir
        self.community = community
        
        # Garante a existência da pasta raw (imutabilidade)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Uso de uma Session melhora a performance em múltiplos pedidos HTTP para o mesmo host
        self.session = requests.Session()

    def _make_request_with_retry(self, params, max_retries=4, base_backoff=2):
        """
        Faz o pedido HTTP com Exponential Backoff.
        Se falhar, espera 2s, depois 4s, depois 8s, etc., até max_retries.
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=15)
                
                # O método raise_for_status() dispara uma exceção para códigos 4xx e 5xx
                response.raise_for_status()
                
                return response.json()
            
            except RequestException as e:
                logging.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                
                # Se for a última tentativa, desiste e propaga o erro
                if attempt == max_retries - 1:
                    logging.error("Número máximo de tentativas atingido. A extração falhou.")
                    raise e
                
                # Exponential Backoff: 2s, 4s, 8s...
                sleep_time = base_backoff ** (attempt + 1)
                logging.info(f"A aguardar {sleep_time} segundos antes de tentar novamente...")
                time.sleep(sleep_time)

    def extract_centroid_data(self, country_code, lat, lon, start_year, end_year, parameters="T2M,T2M_MAX,T2M_MIN"):
        """
        Orquestra a extração para um país e guarda o JSON bruto.
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
        filename = f"extracao_nasa_{start_year}_a_{end_year}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Dados guardados em: {filepath}")