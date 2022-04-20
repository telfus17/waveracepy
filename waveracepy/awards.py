import waveracepy.tally as tally
import waveracepy.rank as rank
import waveracepy.score as score
import numpy as np
import pandas as pd
import requests

def top_players(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    mvp = r.nlargest(3,['Score','dS'])[[
        'Player',
        'Current Rank',
        'Score'
    ]].set_index(['Player','Current Rank','Score'])
    return mvp

def top_newcomers(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    rooks = r[np.isnan(r['dS'])].copy()
    roy = rooks.nlargest(3,'Score',keep='all')
    roy = roy[[
        'Player',
        'Current Rank',
        'dS',
        'Score'
    ]].set_index([
        'Player',
        'Score',
        'Current Rank',
        'dS'])
    return roy

def most_improved_players(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    mip = r.nlargest(3,['dS','Score'])
    mip = mip[[
        'Player',
        'dS',
        'Current Rank',
        'Score'
    ]].set_index([
        'Player',
        'dS',
        'Score',
        'Current Rank'
    ])
    return mip

def most_improved_courses(date):
    df = score.read(date)
    df['Best'] = df.groupby('Category')['dT'].transform(lambda x : x.min())
    df = df[(df['dT']<0)&(df['dT']==df['Best'])]
    df = df[[
            'Category','Player','Level',
            'dT','Place','Time','ID']].rename(columns={'ID':'Link'})
    uri = 'https://www.speedrun.com/api/v1/runs/'
    func = lambda x: requests.get(uri + x).json()['data']['videos']['links'][0]['uri']
    df['Link'] = df['Link'].apply(func)
    df.set_index(['Category','Player','Level','dT','Time','Place','Link'],inplace=True)
    return df
    
    



