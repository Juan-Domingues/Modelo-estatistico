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

    # Limita para os primeiros 10 jogadores para evitar excesso de requisições
    df_limited = df.head(10).copy()

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

    print(df_limited.head(10))
else:
    print(f"Erro: {response.status_code} - {response.text}")
