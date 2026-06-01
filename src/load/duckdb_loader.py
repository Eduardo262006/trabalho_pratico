import duckdb
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DuckDBLoader:
    def __init__(self, curated_dir="data/curated", db_dir="data/database"):
        """
        Inicializa o Loader. 
        Define de onde vêm os dados (Curated/Gold) e para onde vão (Database).
        """
        self.curated_dir = curated_dir
        self.db_dir = db_dir
        
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.db_path = os.path.join(self.db_dir, "analytical_warehouse.duckdb")

    def load_gold_layer(self, country_code="PT"):
        logging.info("Carregamento (Load) no DuckDB")
        
        parquet_file = os.path.join(self.curated_dir, f"gold_analytical_{country_code}.parquet")
        
        if not os.path.exists(parquet_file):
            logging.error(f"Ficheiro {parquet_file} não encontrado. Executa o Merge primeiro.")
            return

        conn = duckdb.connect(self.db_path)
        
        table_name = f"gold_metrics_{country_code.lower()}"
        
        try:
            logging.info(f"A criar/substituir a tabela analítica '{table_name}'...")
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{parquet_file}')
            """)
            
            logging.info("A aplicar Constraints e Índices de Performance...")
            conn.execute(f"CREATE UNIQUE INDEX idx_ano ON {table_name} (Ano)")
            
            logging.info("A realizar validações pós-carga...")
            
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            sample = conn.execute(f"SELECT Ano, Amplitude_Termica, Crescimento_PIB FROM {table_name} LIMIT 2").df()
            
            logging.info(f"VITÓRIA! Carregamento concluído. {count} registos inseridos e consolidados na base de dados.")
            logging.info(f"Amostra consultável (via SQL):\n{sample}")
            logging.info(f"O teu Data Warehouse está pronto em: {self.db_path}")
            
        except Exception as e:
            logging.error(f"Erro ao carregar dados no DuckDB: {e}")
            raise e
        finally:
            conn.close()