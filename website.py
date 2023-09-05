from flask import Flask, request, render_template
from getMatches import get_summoner_puuid, get_match_ids, get_item_timeline, analyze_timelines, create_item_guide, D
from key import API_KEY

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        summoner_name = request.form.get('summoner_name')
        champion = request.form.get('champion')
        position = request.form.get('position')
        champId = D[champion]  # Assuming D dictionary is imported from your script
        # run your item guide generator
        puuid = get_summoner_puuid(summoner_name)
        matches = get_match_ids(puuid, champId, position, API_KEY)

        timelines = []
        for match in matches:
            timelines.append(get_item_timeline(match[0], match[1], API_KEY))

        H_sum, X, P, S, KK = analyze_timelines(timelines)
        
        sizeOfTimeline = len(timelines)

        guide = create_item_guide(H_sum, X, P, S, KK, summoner_name, champion, champId, position, sizeOfTimeline)

        # Return the guide as HTML. If your guide is a dictionary, you might need to iterate over it
        # in the template to display it correctly
        return render_template('result.html', guide=guide)

    # send your champion names to the template
    champion_names = list(D.keys())
    return render_template('home.html', champion_names=champion_names)

if __name__ == "__main__":
    app.run(debug=True)
