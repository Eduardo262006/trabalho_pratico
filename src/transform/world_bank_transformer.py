import pandas as pd
import os
import glob

# 1. Configurar os caminhos
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

input_dir = os.path.join(project_root, 'data', 'raw')
output_dir = os.path.join(project_root, 'data', 'staging')

os.makedirs(output_dir, exist_ok=True)

csv_files = glob.glob(os.path.join(input_dir, '*.csv'))

if not csv_files:
    print(f"Erro: Nenhum ficheiro CSV encontrado em {input_dir}")
else:
    print(f"Encontrados {len(csv_files)} ficheiros. A iniciar processamento completo...\n")

    merged_df = None

    for file in csv_files:
        indicator_name = os.path.basename(file).replace('.csv', '')
        df = pd.read_csv(file)

        # --- LIMPEZA BÁSICA ---
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').astype('Int64')
        df = df.dropna(subset=['Ano'])
        df[indicator_name] = pd.to_numeric(df[indicator_name], errors='coerce')

        # --- MERGE ---
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='Ano', how='outer')

    # Ordenar cronologicamente
    merged_df = merged_df.sort_values(by='Ano', ascending=True).reset_index(drop=True)

    # ==========================================================
    # --- PASSO 1: REMOVER COLUNAS LIXO (> 75% NULOS) ---
    # ==========================================================
    # Remover duplicado conhecido
    if 'Despesas_Governo_na_Educacao' in merged_df.columns:
        merged_df = merged_df.drop(columns=['Despesas_Governo_na_Educacao'])

    limite_nulos = 0.75
    colunas_removidas = []

    for col in merged_df.columns:
        if col != 'Ano':
            if merged_df[col].isnull().mean() > limite_nulos:
                colunas_removidas.append(col)

    if colunas_removidas:
        print(f"⚠️ A remover {len(colunas_removidas)} coluna(s) com mais de 75% de dados em falta:")
        for col in colunas_removidas:
            print(f"   - {col}")

        merged_df = merged_df.drop(columns=colunas_removidas)

    # ==========================================================
    # --- PASSO 2: PREENCHER OS BURACOS RESTANTES (IMPUTATION) ---
    # ==========================================================
    # interpolate(): preenche buracos no meio (ex: 2016 se faltar entre 2015 e 2017)
    # bfill(): preenche valores no início (ex: ano 2000 usando o valor de 2001)
    # ffill(): preenche valores no fim (ex: anos 2022/2023 usando o valor de 2021)
    merged_df = merged_df.interpolate(method='linear').bfill().ffill()

    # ==========================================================

    # Guardar o ficheiro final
    output_file = os.path.join(output_dir, 'worldbank_pt.csv')
    merged_df.to_csv(output_file, index=False)

    print("\nProcesso de Limpeza e União Concluído!")
    print(f"-> Ficheiro final guardado em: {output_file}")

    # Verificação final de sanidade
    total_nulos = merged_df.isnull().sum().sum()
    print(f"-> Total de valores nulos no ficheiro final: {total_nulos} (Tem de ser 0!)")

    if total_nulos == 0:
        print("✅ Sucesso absoluto! Os teus dados estão imaculados e prontos para a visualização.")