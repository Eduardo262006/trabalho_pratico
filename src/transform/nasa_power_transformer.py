import os
import json
import logging
import pandas as pd
from functools import reduce

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NasaPowerTransformer:
    def __init__(self, input_dir="data/raw", output_dir="data/staging"):
        """
        Inicializa o Transformador da NASA POWER.
        Define as diretorias de origem (Raw/Bronze) e destino (Staging/Silver).
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _extract_annual_data(self, param_data, col_name, country_code):
        """
        Método privado que itera sobre o dicionário de um parâmetro (ex: T2M),
        filtra as chaves terminadas em '13', e converte para um DataFrame do Pandas.
        """
        records = []
        for date_key, value in param_data.items():
            if date_key.endswith("13"):
                ano = int(date_key[:4])  
                records.append({
                    "Ano": ano,
                    "Codigo_Pais": country_code,
                    col_name: float(value)
                })
        return pd.DataFrame(records)

    def transform_file(self, filename):
        """
        Lê um ficheiro JSON bruto, limpa os dados e guarda em Parquet.
        """
        filepath = os.path.join(self.input_dir, filename)
        logging.info(f"A iniciar transformação do ficheiro: {filename}")

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        parameters = raw_data.get("properties", {}).get("parameter", {})

        parts = filename.replace('.json', '').split('_')
        country_code = parts[1].upper() 

        df_t2m = self._extract_annual_data(parameters.get("T2M", {}), "T2M_Media_Anual", country_code)
        df_t2m_max = self._extract_annual_data(parameters.get("T2M_MAX", {}), "T2M_Maxima_Anual", country_code)
        df_t2m_min = self._extract_annual_data(parameters.get("T2M_MIN", {}), "T2M_Minima_Anual", country_code)

        dfs = [df for df in [df_t2m, df_t2m_max, df_t2m_min] if not df.empty]
        if not dfs:
            logging.warning("Nenhum dado anual (mês 13) foi encontrado.")
            return

        df_final = reduce(lambda left, right: pd.merge(left, right, on=["Ano", "Codigo_Pais"], how="outer"), dfs)

        df_final = df_final.sort_values(by="Ano").reset_index(drop=True)

        out_filename = f"staging_nasa_{country_code}.parquet"
        out_filepath = os.path.join(self.output_dir, out_filename)
        
        df_final.to_parquet(out_filepath, index=False)
        
        logging.info(f"Sucesso! DataFrame guardado em: {out_filepath}")
        logging.info(f"Amostra dos dados (Schema Limpo):\n{df_final.head(3)}")