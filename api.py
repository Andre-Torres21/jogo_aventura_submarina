import requests

BASE_URL = 'http://127.0.0.1:8000/'

def salvar_score(nome_jogador, score):
    response = requests.post(
        f"{BASE_URL}salvar_score/",
        json={'nome_jogador': nome_jogador, 'score': score}
    )
    return response.json()

def get_ranking():
    response = requests.get(f"{BASE_URL}ranking/")
    return response.json()
