import waveracepy.tally as tally
import waveracepy.rank as rank
import waveracepy.score as score
import numpy as np
import pandas as pd
import requests

def top_players(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    mvp = r.nlargest(3,['Total Score','dSCORE'])[[
        'Player',
        'Current Rank',
        'Total Score'
    ]].set_index(['Player','Current Rank','Total Score'])
    return mvp

def top_newcomers(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    rooks = r[np.isnan(r['dSCORE'])].copy()
    roy = rooks.nlargest(3,'Total Score',keep='all')
    roy = roy[[
        'Player',
        'Current Rank',
        'dSCORE',
        'Total Score'
    ]].set_index([
        'Player',
        'Total Score',
        'Current Rank',
        'dSCORE'])
    return roy

def most_improved_players(date,region='NTSC'):
    r = rank.read(date,region)
    r = r[~np.isnan(r['Current Rank'])]
    mip = r.nlargest(3,['dSCORE','Total Score'])
    mip = mip[[
        'Player',
        'dSCORE',
        'Current Rank',
        'Total Score'
    ]].set_index([
        'Player',
        'dSCORE',
        'Total Score',
        'Current Rank'
    ])
    return mip

def most_improved_courses(date):
    IL = score.read(date,category='IL')
    RTA = score.read(date,category='RTA')
    df = pd.concat([IL,RTA])
    df['Best'] = df.groupby('Category')['dTIME'].transform(lambda x: x.min())
    df = df[(df['dTIME']<0)&(df['dTIME']==df['Best'])]
    df = df[[
        'Category','Player','Level',
        'dTIME','Place','Time','ID']].rename(columns={'ID':'Link'})
    uri = 'https://www.speedrun.com/api/v1/runs/'
    func = lambda x: requests.get(uri + x).json()['data']['videos']['links'][0]['uri']
    df['Link'] = df['Link'].apply(func)
    df.set_index(['Category','Player','Level','dTIME','Time','Place','Link'],inplace=True)
    return df
    
    



