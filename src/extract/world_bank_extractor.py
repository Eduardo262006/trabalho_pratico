import requests
import pandas as pd
import os

country = 'PT'

indicators = {
    'Crescimento_PIB': 'NY.GDP.MKTP.KD.ZG',
    'PIB_per_capita': 'NY.GDP.PCAP.CD',
    'CO2_produzido_por_unidade_do_PIB': 'EN.GHG.CO2.RT.GDP.KD',
    'CO2_per_capita': 'EN.GHG.CO2.PC.CE.AR5',
    'Inflação(% anual)': 'FP.CPI.TOTL.ZG',
    'Desemprego(% trabalhadores)': 'SL.UEM.TOTL.ZS',
    'Divida_do_Governo(% PIB)': 'GC.DOD.TOTL.GD.ZS',
    'Investimento_Estrangeiro': 'BX.KLT.DINV.WD.GD.ZS',
    'Populacao': 'SP.POP.TOTL',
    'Esperança_de_Vida': 'SP.DYN.LE00.IN',
    'Acesso_a_Eletricidade(% populacao)': 'EG.ELC.ACCS.ZS',
    'Utilizadores_de_Internet(% populacao)': 'IT.NET.USER.ZS',
    'Gastos_com_Educacao(% PIB)': 'SE.XPD.TOTL.GD.ZS',
    'Gastos_com_Saude_per_capita(US$)': 'SH.XPD.CHEX.PC.CD',
    'Taxa_de_Albetizacao_adulta': 'SE.ADT.LITR.ZS',
    'Consumo_de_Energia_Renovavel(% do total)': 'EG.FEC.RNEW.ZS',
    'Producao_de_Energia_Renovavel(% do total)': 'EG.ELC.RNEW.ZS',
    'Area_Florestal(% do total)': 'AG.LND.FRST.ZS',
    'Despesas_Governo_na_Educacao': 'SE.XPD.TOTL.GD.ZS',
    'Incricoes_Escolares': 'SE.PRM.ENRR'
}

# 1. Descobrir onde este script está guardado (.../trabalho_pratico/src/extract)
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Subir dois níveis para chegar à raiz do projeto (.../trabalho_pratico)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

# 3. Juntar a raiz do projeto com o caminho desejado (data/raw)
output_dir = os.path.join(project_root, 'data', 'raw')

# Garantir que a pasta existe (cria a pasta caso não exista)
os.makedirs(output_dir, exist_ok=True)

for name, code in indicators.items():

    print(f"Recolhendo dados para o indicador: {name}...")

    url = f"http://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&date=2000:2023"

    response = requests.get(url).json()

    if len(response) > 1 and response[1] is not None:
        temp_df = pd.DataFrame(response[1])

        # Filtrar as colunas e renomear
        temp_df = temp_df[['date', 'value']]
        temp_df.columns = ['Ano', name]

        # Guardar num CSV individual para este indicador
        file_path = os.path.join(output_dir, f"{name}.csv")
        temp_df.to_csv(file_path, index=False)
        print(f"-> Ficheiro guardado com sucesso em: {file_path}")

    else:
        print(f"Aviso: Não foram encontrados dados para o indicador {name}")

print("\nProcesso concluído!")