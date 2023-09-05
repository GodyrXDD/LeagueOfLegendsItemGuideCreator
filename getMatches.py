import requests
import json
import re
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

def get_match_ids(puuid, champion_id, position, api_key):
    region = "AMERICAS"  # adjust according to your needs
    base_url = f"https://{region}.api.riotgames.com/lol/match/v5"
    headers = {"X-Riot-Token": api_key}

    response = requests.get(f"{base_url}/matches/by-puuid/{puuid}/ids", headers=headers)
    response.raise_for_status()
    match_ids = response.json()

    matching_matches = []

    for match_id in match_ids:
        response = requests.get(f"{base_url}/matches/{match_id}", headers=headers)
        response.raise_for_status()
        match_data = response.json()

        for participant in match_data['info']['participants']:
            if participant['puuid'] == puuid:
                if participant['championId'] == champion_id and participant['teamPosition'] == position:
                    matching_matches.append((match_id, participant['participantId']))
                    break

    return matching_matches


def get_item_timeline(match_id, participant_id, api_key):
    region = "AMERICAS"  # adjust according to your needs
    base_url = f"https://{region}.api.riotgames.com/lol/match/v5"
    headers = {"X-Riot-Token": api_key}

    response = requests.get(f"{base_url}/matches/{match_id}/timeline", headers=headers)
    response.raise_for_status()
    data = response.json()

    timeline = []

    def iterate_items(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    iterate_items(value)
                elif key == 'type' and obj.get('participantId') == participant_id:
                    if value == 'ITEM_PURCHASED':
                        item_event = {'itemId': obj['itemId'], 'timestamp': obj['timestamp']}
                        timeline.append(item_event)
                    elif value == 'ITEM_UNDO':
                        if timeline:  # only try to remove if the timeline is not empty
                            timeline.pop()  # removes the most recent item

        elif isinstance(obj, list):
            for item in obj:
                iterate_items(item)

    iterate_items(data)

    return timeline


from itemTree import A, B, C, D, E, Z

def analyze_timelines(timelines):
    H_sum = {}
    X = {}
    P = []
    S = {}
    KK = {}
    lastItem = -1

    for timeline in timelines:
        G = []
        G2 = []
        curItem = -1
        starterItems = []
        processed_situational_items = set()  # For tracking processed situational items

        for item in timeline:
            itemId = item['itemId']
            timestamp = item['timestamp']
            if timestamp <= 60000:  # item is a starter item
                starterItems.append(itemId)
            elif itemId in B:  # item is a final item
                curItem += 1
                F = itemId
                processed_situational_items.clear()  # Reset for each final item

                if F not in KK:
                    KK[F] = {}

                if lastItem != -1:
                    KK[F][lastItem] = KK[F].get(lastItem, 0) + 1

                lastItem = F

                if len(P) <= curItem:
                    P.append({})

                P[curItem].setdefault(F, 0)
                P[curItem][F] += 1

                H_sum.setdefault(F, {})

                currentRank = 0
                processed_components = set()

                to_remove_G2 = []
                for i, component in enumerate(G2):  
                    if component in A[F] and component not in processed_components:
                        H_sum[F][component] = H_sum[F].get(component, 0) + currentRank
                        currentRank += 1
                        processed_components.add(component)
                        to_remove_G2.append(i)
                for i in reversed(to_remove_G2):  # Remove items in reverse order to avoid index errors
                    del G2[i]

                to_remove_G = []
                for i, component in enumerate(G):  
                    if component in A[F] and component not in processed_components:
                        H_sum[F][component] = H_sum[F].get(component, 0) + currentRank
                        currentRank += 1
                        processed_components.add(component)
                        to_remove_G.append(i)
                    elif component not in C[F] and component not in processed_situational_items:
                        X.setdefault(curItem, {})
                        X[curItem][component] = X[curItem].get(component, 0) + 1
                        processed_situational_items.add(component)
                        G2.append(component)  
                        to_remove_G.append(i)
                for i in reversed(to_remove_G):  # Remove items in reverse order to avoid index errors
                    del G[i]

                for kekw in A[F]:
                    if kekw not in processed_components:
                        H_sum[F][kekw] = H_sum[F].get(kekw, 0) + currentRank

            else:
                G.append(itemId)

        starterItemsTuple = tuple(starterItems)
        S[starterItemsTuple] = S.get(starterItemsTuple, 0) + 1

    print('H_sum:', H_sum)
    print('X:', X)
    print('P:', P)
    print('S:', S)
    print('KK:', KK)
    return H_sum, X, P, S, KK

import json

def create_item_guide(H_sum, X, P, S, KK, summoner_name, champion, champion_id, position, sizeOfTimeline):
    guide = {
        "title": f"{summoner_name} {champion} {position} Guide",
        "associatedMaps": [11],
        "associatedChampions": [champion_id],
        "blocks": []
    }

    # Calculate total games for percentage calculation
    total_games = sum([count for starter_items, count in S.items()])

    # Add the top 3 most common starter items to the guide, with their purchase rates
    starters_sorted = sorted(S.items(), key=lambda x: x[1], reverse=True)[:3]
    for i, (items, count) in enumerate(starters_sorted):
        percent = round((count / total_games) * 100)
        guide["blocks"].append({
            "items": [{"id": str(item), "count": 1} for item in items],
            "type": f"{percent}% Starter Items"
        })


    # Modified build order sequence
    SS = 0
    while SS < len(P):
        # Initialize the blocks for this step
        step_blocks = []
        theS = sum(P[SS].values())

        # Sort the current items based on the second index (count)
        current_items = sorted(P[SS].items(), key=lambda x: x[1], reverse=True)
        for item, count in current_items:
            # Check if the item exists in H_sum dictionary
            if item not in H_sum:
                continue

            # Get the components for the current item
            components = sorted(H_sum[item].items(), key=lambda x: x[1])

            # If the item is in Z, then repeat the component that appears twice
            if item in Z:
                repeated_component = list(Z[item])[0]  # Get the repeated component
                new_components = []
                for comp in components:
                    new_components.append(comp)
                    if comp[0] == repeated_component:
                        new_components.append(comp)
                components = new_components

            # Calculate the purchase rate and prepare the title for the block
            # Calculate the purchase rate and prepare the title for the block
            purchase_rate = round((count / theS) * 100)
            item_name = E.get(item, item)  # Use the name from E if available, otherwise use the item code
            title = f"{SS}) {purchase_rate}% {item_name}"

            # Add the most frequently purchased item before the current item
            if SS > 0:
                # Check if the item exists in KK dictionary
                if item not in KK:
                    continue

                # Get the item that was most frequently bought before the current item
                previous_items = sorted(KK[item].items(), key=lambda x: x[1], reverse=True)
                most_common_previous_items = [E.get(i[0], i[0]) for i in previous_items if i[1] == previous_items[0][1]]

                # Append this information to the title
                title += f" after {'/'.join(most_common_previous_items)}"


            # Add the block to the guide
            step_blocks.append({
                "items": [{"id": str(item[0]), "count": 1} for item in components] + [{"id": str(item), "count": 1}],
                "type": title
            })

        # Add the situational items for the current step, sorted by frequency
        if SS in X:
            situational_items = sorted(X[SS].items(), key=lambda x: x[1], reverse=True)[:10]
            situational_percentages = [round((count / theS) * 100) for _, count in situational_items]

            step_blocks.append({
                "items": [{"id": str(item), "count": count} for item, count in situational_items],
                "type": ', '.join([str(p) + "%" for p in situational_percentages])
            })


        # Check if the step blocks have any items before adding to the guide
        if step_blocks:
            # Add the blocks for this step to the guide
            guide["blocks"].extend(step_blocks)

        SS += 1

    # Convert the guide into a JSON string without new lines
    guide_json = json.dumps(guide, separators=(',', ':'))

    return guide_json

"""
summoner_name = "Solarbacca"
#input("Enter Summoner name: ")
champion = "Gangplank"
#input("Enter Champion name: ")
position = "TOP"
#input("Enter Position: ")  # one of "TOP", "JUNGLE", "BOTTOM", "MIDDLE", "UTILITY"

puuid = get_summoner_puuid(summoner_name)

matches = get_match_ids(puuid, champion, position, API_KEY)

#for match in matches:
#    print(f"\nTimeline for match {match[0]} with participant ID {match[1]}:")
#    get_item_timeline(match[0], match[1], API_KEY)

timelines = []
for match in matches:
    print(f"\nTimeline for match {match[0]} with participant ID {match[1]}:")
    timelines.append(get_item_timeline(match[0], match[1], API_KEY))

# Analyze the timelines
H_sum, X, P, S, KK = analyze_timelines(timelines)
sizeOfTimeline = len(timelines)
champId = D[champion]
# Create the item guide
guide = create_item_guide(H_sum, X, P, S, KK, summoner_name, champion, champId, position, sizeOfTimeline)

print(guide)
"""