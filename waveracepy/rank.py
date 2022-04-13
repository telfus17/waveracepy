import waveracepy.score as score
import waveracepy.leaderboard as leaderboard
import waveracepy.tally as tally
import pandas as pd
import numpy as np
import glob
import os
import datetime

def package_path(*paths, package_directory=os.path.dirname(os.path.abspath('__init__.py'))):
    return os.path.join(package_directory, *paths)

def save(df,date,region='NTSC'):
    df.to_csv(
        package_path(
            'data',
            f'{region}',
            'rankings',
            f'R.{region}.{date}.csv'))  
    return None

def read(date,region='NTSC'):
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'rankings',
            f'R.{region}.{date}.csv'),
        index_col=0)
    df['Date'] = pd.to_datetime(date)
    return df

def current(r,df,date):
    df['Date'] = pd.to_datetime(df['Date'])
    eligDate = pd.to_datetime(date) - pd.DateOffset(years=2)
    eligRank = r[r['Player'].isin(df[df['Run Date']>eligDate]['Player'])].copy()
    eligRank['Current Rank'] = eligRank['Overall Rank'].rank(ascending=True,method='min')
    r = r.merge(eligRank,how='outer')
    return r

def previous(r,region,date):
    filePaths = sorted(glob.glob(package_path('data',f'{region}','rankings','*')))
    prevPath = sorted([
            i for i in filePaths
            if i < package_path('data',f'{region}','rankings',f'R.{region}.{date}.csv')
        ])
    if bool(prevPath):
        prevRank = pd.read_csv(prevPath[-1])[[
                'Player',
                'Total Score'
            ]]
        prevRank.rename(columns={'Total Score': 'Prev Total Score'}, inplace=True)
        r = r.merge(prevRank, how='outer')
        r['dSCORE'] = r['Total Score'] - r['Prev Total Score']
        r = r[[
            'Player',
            'Current Rank',
            'Total Score',
            'IL Score',
            'RTA Score',
            'dSCORE',
            'Overall Rank'
        ]]
    else:
        r = r[[
            'Player',
            'Current Rank',
            'Total Score',
            'IL Score',
            'RTA Score',
            'Overall Rank'
        ]]
    return r

def get(date,read=False,region='NTSC'):
    if bool(read):
        df = leaderboard.read(date,region)
    else:
        df = leaderboard.get(date,region)
    iSheet = score.IL(df,date)
    iScore = iSheet.groupby('Player')['Run Score'].sum().reset_index()
    iScore.rename(columns={'Run Score':'IL Score'},inplace=True)
    rSheet = score.RTA(df,date)
    rScore = rSheet.groupby('Player')['Run Score'].sum().reset_index()
    rScore.rename(columns={'Run Score':'RTA Score'},inplace=True)
    r = pd.merge(iScore,rScore,how='outer').fillna(0)
    r['Total Score'] = r[['IL Score','RTA Score']].sum(axis=1)
    r['Total Score'] = np.round((100/240) * r['Total Score'],2)
    r['IL Score'] = np.round((100/200) * r['IL Score'],2)
    r['RTA Score'] = np.round((100/40) * r['RTA Score'],2)
    r['Overall Rank'] = r['Total Score'].rank(ascending=False,method='min')
    r = current(r,df,date).sort_values(by='Current Rank').reset_index(drop=True)
    r = previous(r,region,date)
    r['Date'] = pd.to_datetime(date)
    save(r,date,region)
    t = tally.get(df,date)
    return r
    