import requests
import pandas as pd

country = 'PT'

indicators = {
    'Crescimento_PIB': 'NY.GDP.MKTP.KD.ZG',
    'PIB_per_capita': 'NY.GDP.PCAP.CD',
    'CO2_produzido_por_unidade_do_PIB': 'EN.GHG.CO2.RT.GDP.KD',
    'CO2_per_capita': 'EN.ATM.CO2E.PC',
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

final_df = pd.DataFrame()

for name, code in indicators.items():

    print(f"Recolhendo dados para o indicador: {name}...")

    url = f"http://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&date=2000:2023"

    response = requests.get(url).json()

    if len(response) > 1 and response[1] is not None:
        temp_df = pd.DataFrame(response[1])

        temp_df = temp_df[['date', 'value']]
        temp_df.columns = ['Ano', name]

        if final_df.empty:
            final_df = temp_df
        else:
            final_df = pd.merge(final_df, temp_df, on='Ano')
    else:
        print(f"Aviso: Não foram encontrados dados para o indicador {name}")

if not final_df.empty:
    final_df.to_csv("worldbank_pt.csv", index=False)
    print("Dados foram guaradados em 'worldbank_pt.csv'.")
else:
    print("Erro: Nenhum dado foi recuperado.")