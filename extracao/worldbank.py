import requests
import pandas as pd

# PT = Portugal
country = 'PT'

# Indicadores:
# NY.GDP.MKTP.KD.ZG = Crescimento do PIB (% anual)
# EN.ATM.CO2E.PC    = Emissões de CO2 (toneladas métricas per capita)
indicators = {
    'Crescimento_PIB': 'NY.GDP.MKTP.KD.ZG',
    'Emissoes_CO2': 'EN.ATM.CO2E.PC'
}

final_df = pd.DataFrame()

for name, code in indicators.items():
    url = f"http://api.worldbank.org/v2/country/{country}/indicator/{code}?format=json&date=2000:2023"

    response = requests.get(url).json()

    # Verifica se a resposta tem o formato esperado e se há dados no índice [1]
    if len(response) > 1 and response[1] is not None:
        temp_df = pd.DataFrame(response[1])

        # Mantemos apenas as colunas que interessam: data e o valor
        temp_df = temp_df[['date', 'value']]
        temp_df.columns = ['Ano', name]

        if final_df.empty:
            final_df = temp_df
        else:
            final_df = pd.merge(final_df, temp_df, on='Ano')
    else:
        print(f"Aviso: Não foram encontrados dados para o indicador {name}")

if not final_df.empty:
    print("\n--- Dados de Economia e Ambiente (Portugal) ---")
    print(final_df.head())
    # Opcional: Salvar em CSV para o teu trabalho
    final_df.to_csv("economia_ambiente_pt.csv", index=False)
else:
    print("Erro crítico: Nenhum dado foi recuperado.")