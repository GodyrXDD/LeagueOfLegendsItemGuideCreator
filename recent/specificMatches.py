import requests
from key import API_KEY

def get_match_ids(puuid, champion, position, api_key):
    region = "AMERICAS"  # adjust according to your needs
    base_url = f"https://{region}.api.riotgames.com/lol/match/v5"
    headers = {"X-Riot-Token": api_key}

    # Get the list of match ids by puuid
    response = requests.get(f"{base_url}/matches/by-puuid/{puuid}/ids", headers=headers)
    response.raise_for_status()  # raise exception if request was not successful
    match_ids = response.json()

    matching_matches = []

    # In your for loop
    for match_id in match_ids:
        response = requests.get(f"{base_url}/matches/{match_id}", headers=headers)
        response.raise_for_status()
        match_data = response.json()

        # Check if the player played the specified champion in the specified position
        for participant in match_data['info']['participants']:
            if participant['puuid'] == puuid:
                print(f"In match {match_id}, played as {participant['championName']} in position {participant['teamPosition']}")  # Debug print
                if participant['championName'] == champion and participant['teamPosition'] == position:
                    matching_matches.append(match_id)
                    break  # break the loop if we found a matching participant

    return matching_matches  # Ensure this list is returned even if empty

# usage
puuid = "DIQsArYXw23n8Zdrp9msjG-hzryhC2tbeupuRMvLd04NxxT5kTZCwdOLpM1jsHpmzSnIez6mls807g"
champion = "Gangplank"
position = "MIDDLE"  # one of "TOP", "JUNGLE", "BOTTOM", "MIDDLE", "UTILITY"

matches = get_match_ids(puuid, champion, position, API_KEY)
print(matches)
