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
        
        # Garante que a pasta da base de dados existe
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Define o caminho do ficheiro da base de dados física
        self.db_path = os.path.join(self.db_dir, "analytical_warehouse.duckdb")

    def load_gold_layer(self, country_code="PT"):
        logging.info("--- A iniciar a Fase 3: Carregamento (Load) no DuckDB ---")
        
        parquet_file = os.path.join(self.curated_dir, f"gold_analytical_{country_code}.parquet")
        
        if not os.path.exists(parquet_file):
            logging.error(f"Ficheiro {parquet_file} não encontrado. Executa o Merge primeiro.")
            return

        # Ligar ao DuckDB (cria o ficheiro automaticamente se não existir)
        conn = duckdb.connect(self.db_path)
        
        # O nome da nossa One Big Table (OBT)
        table_name = f"gold_metrics_{country_code.lower()}"
        
        try:
            # 1. Estratégia de Carga: Full Load / Overwrite
            # Garante a idempotência (podemos correr o script as vezes que quisermos sem duplicar dados)
            logging.info(f"A criar/substituir a tabela analítica '{table_name}'...")
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # O DuckDB consegue criar o esquema da tabela lendo a tipagem diretamente do Parquet
            conn.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{parquet_file}')
            """)
            
            # 2. Documentar e Aplicar Índices e Constraints de Performance
            # Criamos um índice único no 'Ano' para acelerar queries cronológicas 
            # e garantir que nunca existem anos duplicados (Integridade)
            logging.info("A aplicar Constraints e Índices de Performance...")
            conn.execute(f"CREATE UNIQUE INDEX idx_ano ON {table_name} (Ano)")
            
            # 3. Validação Pós-Carga (Sanity Check pedido pelo professor)
            logging.info("A realizar validações pós-carga...")
            
            # Conta o número de registos
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            
            # Traz uma amostra dos dados diretamente da base de dados (prova de conceito)
            sample = conn.execute(f"SELECT Ano, Amplitude_Termica, Crescimento_PIB FROM {table_name} LIMIT 2").df()
            
            logging.info(f"VITÓRIA! Carregamento concluído. {count} registos inseridos e consolidados na base de dados.")
            logging.info(f"Amostra consultável (via SQL):\n{sample}")
            logging.info(f"O teu Data Warehouse está pronto em: {self.db_path}")
            
        except Exception as e:
            logging.error(f"Erro ao carregar dados no DuckDB: {e}")
            raise e
        finally:
            # Fechar a ligação é uma boa prática fundamental em bases de dados
            conn.close()