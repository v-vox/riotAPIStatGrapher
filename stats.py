# i love sakamata chloe
import time
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import requests
import os.path
import os
import json
import numpy
# data
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com"
}

load_dotenv()
key = os.getenv('RIOT')

#funcs

#get id, returns puuid of user
def getid(name):
    request = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}', headers = headers)
    data = json.loads(request.content)
    return str(data['puuid'])

#get matches, returns string list of match IDs
#puuid- str puuid of summoner
#count- number of matches
#idx- start idx of matches
def getmatches(puuid, count, idx):
    request = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={idx}&count={count}&api_key={key}', headers = headers)
    data = json.loads(request.content)
    return data

#get match data, returns match data of one player given puuid
def matchData(puuid, matchid):
    #debug
    #print(matchid)
    
    request = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={key}', headers = headers)
    if request.status_code == 429:
        time.sleep(120)
        print('timeout')
        request = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={key}', headers = headers)

    data = json.loads(request.content)
    if 'info' not in data:
        print
        return 'err'
    if data['info']['gameDuration'] == 0:
        return 'err'
    for x in range(0, 9):
        if data['info']['participants'][x]['puuid'] == puuid:
            return data['info']['participants'][x]

#gets winloss, key value from matchdata
def getWLKV(key, matchdata):
    if matchdata is not None:
        wl = matchdata['win']
        kv = matchdata[key]
        return [wl, kv]
    return 'err'

#compile a dictionary with key values of key, containing data of arrays with win/loss
#https://developer.riotgames.com/apis#match-v5/GET_getMatch possible keys in 'ParticipantDto'
def compileWLKV(key, mlist, puuid):
    data = dict()
    for matchid in mlist:
        curr = matchData(puuid, matchid)
        if curr == 'err':
            continue

        temp = getWLKV(key, curr)
        
        if temp == 'err':
            continue

        game = [0,1]
        if temp[0]:
            game = [1,0]
        
        if temp[1] in data:
            data[temp[1]][0] += game[0]
            data[temp[1]][1] += game[1]
        else:
            data.update({temp[1]: game})

    return data

#function to combine two dictionaries 
def combineDict(d1, d2):
    print(d1)
    print(d2)
    combined = dict()

    for key in set(d1.keys()).union(d2.keys()):
        if key in d1 and key in d2:
            v1 = d1[key][0]
            v2 = d2[key][0]
            combined[key] = [v1 + v2, d1[key][1] + d2[key][1]]
        elif key in dict1:
            combined[key] = d1[key]
        else:
            combined[key] = d2[key]

    return combined

#plotting
def plotDblBar(keyvalue, data):
    x_values = list(data.keys())
    y1_values = [pair[0] for pair in data.values()]
    y2_values = [pair[1] for pair in data.values()]

    #axis and par width
    fig, ax = plt.subplots()
    bar_width = 0.35

    bar_positions1 = [x - bar_width/2 for x in x_values]
    bar_positions2 = [x + bar_width/2 for x in x_values]
    ax.bar(bar_positions1, y1_values, bar_width, label='wins')
    ax.bar(bar_positions2, y2_values, bar_width, label='losses')

    #labels
    ax.set_xlabel(keyvalue)
    ax.set_ylabel('games')
    ax.set_title('among us')
    ax.legend()

    plt.show()


#Usage
r = getid('HanooStreet')
r2 = getmatches(r,100,0)
print('1')
r3 = getmatches(r,100,100)
print('2')
r4 = getmatches(r,100,200)
print('3')
r5 = r2 + r3 + r4

r6 = compileWLKV('kills', r5, r)

plotDblBar('kills', r6)
