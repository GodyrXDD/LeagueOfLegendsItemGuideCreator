import requests
import json
import time
from key import API_KEY
REGION = 'na1'  # region

HEADERS = {
    "X-Riot-Token": API_KEY
}

def get_summoner_puuid(summoner_name):
    URL = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    response = requests.get(URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data['puuid']
    else:
        print(f"Error code: {response.status_code}")
        return None

summoner_name = input("Enter Summoner name: ")
puuid = get_summoner_puuid(summoner_name)

print("Summoner PUUID:", puuid)
