import requests
import pandas as pd

api_key = "RGAPI-3d7cc833-a022-4f6c-bffe-e8ab54cdd12e"

base_url = "https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
headers = {
    "X-Riot-Token": api_key
}

response = requests.get(base_url, headers=headers)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data['entries'])

    # Função para buscar gamename e tagline
    def get_account_info(puuid):
        account_url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
        resp = requests.get(account_url, headers=headers)
        if resp.status_code == 200:
            acc = resp.json()
            return acc.get('gameName', ''), acc.get('tagLine', '')
        else:
            return '', ''

    # Usa o conjunto completo de dados
    df_limited = df.copy()

    # Busca gamename e tagline para cada puuid com indicador de progresso
    from time import sleep
    gamename_tagline = []
    for idx, puuid in enumerate(df_limited['puuid']):
        print(f"Buscando conta {idx+1}/{len(df_limited)}...")
        gamename_tagline.append(get_account_info(puuid))
        sleep(1)  # Aguarda 1 segundo entre requisições para evitar rate limit

    df_limited['gamename'], df_limited['tagline'] = zip(*gamename_tagline)

    # Reordena as colunas
    cols = ['puuid', 'gamename', 'tagline'] + [col for col in df_limited.columns if col not in ['puuid', 'gamename', 'tagline']]
    df_limited = df_limited[cols]

    # Calcula total de partidas e win rate
    df_limited['total_partidas'] = df_limited['wins'] + df_limited['losses']
    df_limited['win_rate'] = (df_limited['wins'] / df_limited['total_partidas']) * 100

    print(df_limited.head(10))

    # Clusterização por win rate
    from sklearn.cluster import KMeans
    import numpy as np

    # Seleciona apenas a coluna win_rate para clusterização
    X = df_limited[['win_rate']].values

    # Define o número de clusters (exemplo: 3)
    k = 3
    kmeans = KMeans(n_clusters=k, random_state=42)
    df_limited['cluster'] = kmeans.fit_predict(X)

    # Mostra os centroides
    print("Centroides dos clusters:", kmeans.cluster_centers_)
    print(df_limited[['gamename', 'win_rate', 'cluster']])

    # Exporta os dados para CSV
    df_limited.to_csv('dados_legends.csv', index=False, encoding='utf-8')
    print('Arquivo CSV "dados_legends.csv" gerado com sucesso!')

    # Plot do gráfico de clusters
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    scatter = plt.scatter(df_limited['win_rate'], df_limited['total_partidas'], c=df_limited['cluster'], cmap='viridis', s=80)
    plt.xlabel('Win Rate (%)')
    plt.ylabel('Total de Partidas')
    plt.title('Clusterização dos Jogadores por Win Rate')
    plt.colorbar(scatter, label='Cluster')
    # Exibe os centroides
    for centroide in kmeans.cluster_centers_:
        plt.scatter(centroide[0], df_limited['total_partidas'].mean(), marker='X', color='red', s=120, label='Centroide')
    # Adiciona um X na média de win rate
    plt.scatter(df_limited['win_rate'].mean(), df_limited['total_partidas'].mean(), marker='X', color='blue', s=150, label='Média Win Rate')
    plt.legend(['Jogadores', 'Centroide', 'Média Win Rate'])
    plt.show()
else:
    print(f"Erro: {response.status_code} - {response.text}")
