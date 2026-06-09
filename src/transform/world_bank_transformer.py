import pandas as pd
import os
import glob

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

        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').astype('Int64')
        df = df.dropna(subset=['Ano'])
        df[indicator_name] = pd.to_numeric(df[indicator_name], errors='coerce')

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on='Ano', how='outer')

    merged_df = merged_df.sort_values(by='Ano', ascending=True).reset_index(drop=True)

    if 'Despesas_Governo_na_Educacao' in merged_df.columns:
        merged_df = merged_df.drop(columns=['Despesas_Governo_na_Educacao'])

    limite_nulos = 0.75
    colunas_removidas = []

    for col in merged_df.columns:
        if col != 'Ano':
            if merged_df[col].isnull().mean() > limite_nulos:
                colunas_removidas.append(col)

    if colunas_removidas:
        print(f"A remover {len(colunas_removidas)} coluna(s) com mais de 75% de dados em falta:")
        for col in colunas_removidas:
            print(f"   - {col}")

        merged_df = merged_df.drop(columns=colunas_removidas)

    merged_df = merged_df.interpolate(method='linear').bfill().ffill()

    output_file = os.path.join(output_dir, 'worldbank_pt.csv')
    merged_df.to_csv(output_file, index=False)

    print("\nProcesso de Limpeza e União Concluído!")
    print(f"-> Ficheiro final guardado em: {output_file}")

    total_nulos = merged_df.isnull().sum().sum()
    print(f"-> Total de valores nulos no ficheiro final: {total_nulos} (Tem de ser 0!)")

    if total_nulos == 0:
        print("O ficheiro final está limpo e pronto para a Transformação.")