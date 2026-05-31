import os
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GoldMerger:
    def __init__(self, staging_dir="data/staging", curated_dir="data/curated"):
        """
        Inicializa o Merger que vai cruzar a camada Silver (Staging) 
        para criar a camada Gold (Curated).
        """
        self.staging_dir = staging_dir
        self.curated_dir = curated_dir
        
        # Garante que a pasta curated (gold) é criada automaticamente
        os.makedirs(self.curated_dir, exist_ok=True)

    def create_analytical_dataset(self, country_code="PT"):
        logging.info("--- A iniciar a fusão (Merge) para a Camada Gold ---")
        
        # 1. Caminhos dos ficheiros Staging
        # A NASA vem do teu pipeline (Parquet), o WB vem do script do colega (CSV)
        nasa_filepath = os.path.join(self.staging_dir, f"staging_nasa_{country_code}.parquet")
        wb_filepath = os.path.join(self.staging_dir, f"worldbank_{country_code.lower()}.csv")
        
        # Verificações de segurança
        if not os.path.exists(nasa_filepath):
            logging.error(f"Erro: Ficheiro da NASA não encontrado em {nasa_filepath}")
            return
            
        if not os.path.exists(wb_filepath):
            logging.error(f"Erro: Ficheiro do World Bank não encontrado em {wb_filepath}")
            return

        # 2. Ler os ficheiros (Lida perfeitamente com os dois formatos distintos)
        logging.info("A ler os dados da NASA (Parquet) e World Bank (CSV)...")
        df_nasa = pd.read_parquet(nasa_filepath)
        df_wb = pd.read_csv(wb_filepath)
        
        # 3. O Grande Merge
        # Como o colega não guardou o Codigo_Pais, cruzamos APENAS pelo 'Ano'
        logging.info("A cruzar os dados (Inner Join no 'Ano')...")
        df_gold = pd.merge(df_nasa, df_wb, on="Ano", how="inner")
        
        # 4. Criar Métrica Derivada (Exigência do Enunciado)
        # Calculamos a Amplitude Térmica anual
        logging.info("A calcular métricas derivadas (Amplitude Térmica)...")
        df_gold["Amplitude_Termica"] = df_gold["T2M_Maxima_Anual"] - df_gold["T2M_Minima_Anual"]
        
        # Reordenar colunas para colocar a métrica nova ao pé das outras temperaturas
        cols = list(df_gold.columns)
        if 'Amplitude_Termica' in cols:
            cols.insert(5, cols.pop(cols.index('Amplitude_Termica'))) 
            df_gold = df_gold[cols]

        # 5. Guardar na camada Curated (Gold) em ambos os formatos
        parquet_out = os.path.join(self.curated_dir, f"gold_analytical_{country_code}.parquet")
        csv_out = os.path.join(self.curated_dir, f"gold_analytical_{country_code}.csv")
        
        df_gold.to_parquet(parquet_out, index=False)
        df_gold.to_csv(csv_out, index=False)
        
        logging.info(f"VITÓRIA! Camada Gold criada com sucesso.")
        logging.info(f"O Dataset Final tem {df_gold.shape[0]} linhas e {df_gold.shape[1]} colunas.")
        logging.info(f"Ficheiros guardados em: {self.curated_dir}/")