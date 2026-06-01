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
                ano = int(date_key[:4])  # Extrai os primeiros 4 caracteres e converte para int
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

        # 1. Carregar o JSON Bruto
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # 2. Extrair o dicionário principal de parâmetros
        parameters = raw_data.get("properties", {}).get("parameter", {})

        # Extrair o Código do País do nome do ficheiro (ex: raw_nasa_T2M_PT_2000_2023.json)
        parts = filename.replace('.json', '').split('_')
        country_code = parts[1].upper() 

        # 3. Transformar cada parâmetro num DataFrame individual
        df_t2m = self._extract_annual_data(parameters.get("T2M", {}), "T2M_Media_Anual", country_code)
        df_t2m_max = self._extract_annual_data(parameters.get("T2M_MAX", {}), "T2M_Maxima_Anual", country_code)
        df_t2m_min = self._extract_annual_data(parameters.get("T2M_MIN", {}), "T2M_Minima_Anual", country_code)

        # 4. Juntar (Merge) os DataFrames criados usando 'Ano' e 'Codigo_Pais' como chave
        # O 'reduce' aplica o pd.merge sequencialmente a todos os DataFrames não vazios
        dfs = [df for df in [df_t2m, df_t2m_max, df_t2m_min] if not df.empty]
        if not dfs:
            logging.warning("Nenhum dado anual (mês 13) foi encontrado.")
            return

        df_final = reduce(lambda left, right: pd.merge(left, right, on=["Ano", "Codigo_Pais"], how="outer"), dfs)

        # 5. Ordenar cronologicamente e resetar o índice
        df_final = df_final.sort_values(by="Ano").reset_index(drop=True)

        # 6. Guardar na camada Staging (Silver) em formato Parquet
        out_filename = f"staging_nasa_{country_code}.parquet"
        out_filepath = os.path.join(self.output_dir, out_filename)
        
        df_final.to_parquet(out_filepath, index=False)
        
        logging.info(f"Sucesso! DataFrame guardado em: {out_filepath}")
        logging.info(f"Amostra dos dados (Schema Limpo):\n{df_final.head(3)}")