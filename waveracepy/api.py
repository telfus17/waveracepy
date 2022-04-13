import requests
import pandas as pd

categoryURI = 'https://www.speedrun.com/api/v1/games/y655346e/categories'
levelURI = 'https://www.speedrun.com/api/v1/games/y655346e/levels'
regionURI = 'https://www.speedrun.com/api/v1/regions'
leaderboardURI = 'https://www.speedrun.com/api/v1/leaderboards/y655346e'

def find_categories():
    categoryID = {
        k:v
        for i in [{j['id']:j['name']} 
        for j in requests.get(categoryURI).json()['data']] 
        for k,v in i.items()
    }
    rtaID = dict(filter(lambda item: 'Championship' in item[1], categoryID.items()))
    ilID = dict(filter(lambda item: 'Championship' not in item[1], categoryID.items()))
    return categoryID

def find_levels():
    levelID = {
        k:v 
        for i in [
            {j['id']:j['name']} 
            for j in requests.get(levelURI).json()['data']
            ] 
        for k,v in i.items()
    }
    return levelID

def find_regions():
    regionID = {
        k:v
        for i in [
            {j['id']:j['name']}
            for j in requests.get(regionURI).json()['data']
        ]
        for k,v in i.items()
    }
    return regionID

def find_leaderboards(date,categoryID,levelID,region='NTSC'):
    RTAcategoryID = dict(filter(lambda item: 'Championship' in item[1], categoryID.items()))
    ILcategoryID = dict(filter(lambda item: 'Championship' not in item[1], categoryID.items()))
    regionID = '&region=e6lxy1dz&platform=w89rwelk' if region == 'PAL' else ''
    ILleaderboardURI = [
        f"{leaderboardURI}/level/{lk}/{ck}?date={date}{regionID}"
        for lk,lv in levelID.items()
        for ck,cv in ILcategoryID.items()
    ]
    RTAleaderboardURI = [
        f"{leaderboardURI}/category/{k}?date={date}{regionID}"
        for k,v in RTAcategoryID.items()
    ]
    leaderboardURIlist = ILleaderboardURI + RTAleaderboardURI
    return leaderboardURIlist

def get_name(run):
    URI = run['players'][0]['uri']
    player = requests.get(URI).json()
    name = player['data']['names']['international']
    return name

def parse_run(run,regionID,categoryID,levelID):
    place = run['place']
    run = run['run']
    name = get_name(run)
    region = run['system']['region']
    if region:
        if 'PAL' in regionID[region]:
            region = 'PAL'
        else:
            region = 'NTSC'
    else:
        region = 'NTSC'
    if run['level']:
        level = levelID[run['level']]
        category = categoryID[run['category']]
    else:
        level = categoryID[run['category']]
        category = 'RTA'
    runDict = {
        'Region': region,
        'Category': category,
        'Level': level,
        'Place': place,
        'Player': name,
        'Time': run['times']['primary_t'],
        'Date': run['date'],
        'ID': run['id']
    }
    return runDict

# THIS IS FOR VIDEO PROOF RUNS ONLY
def parse_leaderboard(URI,regionID,categoryID,levelID):
    leaderboard = requests.get(URI).json()['data']
    runs = [
        parse_run(run,regionID,categoryID,levelID) for run in leaderboard['runs']
        if run['run']['players'][0]['rel'] == 'user'
        if bool(run['run']['videos'])
    ]
    df = pd.DataFrame(runs)
    return df

# # THIS IS FOR ALL VERIFIED RUNS
# def parse_leaderboard(URI,regionID,categoryID,levelID):
#     leaderboard = requests.get(URI).json()['data']
#     runs = [
#         parse_run(run,regionID,categoryID,levelID) for run in leaderboard['runs']
#         if run['run']['players'][0]['rel'] == 'user'
#     ]
#     df = pd.DataFrame(runs)
#     return df