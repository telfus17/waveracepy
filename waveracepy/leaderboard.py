import waveracepy.api as api
import pandas as pd
import numpy as np
import os
import glob

def package_path(*paths, package_directory=os.path.dirname(os.path.abspath('__init__.py'))):
    return os.path.join(package_directory, *paths)

def save(df,date,region='NTSC'):
    df.to_csv(
        package_path(
            'data',
            f'{region}',
            'leaderboards',
            f'LB.{region}.{date}.csv'))  
    return None

def read(date,region='NTSC'):
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'leaderboards',
            f'LB.{region}.{date}.csv'),
        index_col=0)
    df['Run Date'] = pd.to_datetime(df['Run Date'])
    df['Date'] = pd.to_datetime(date)
    return df

def fill_missing(df):   
    categories = list(api.find_categories().values())
    players = np.unique(df['Player'].to_list())
    levels = list(api.find_levels().values())
    category = [
        c for c in categories
        if 'Championship' not in c 
        for l in levels
        for p in players
    ] + [
        'RTA' for c in categories
        if 'Championship' in c 
        for p in players
    ]
    level = [
        l for c in categories
        if 'Championship' not in c 
        for l in levels
        for p in players
    ] + [
        c for c in categories
        if 'Championship' in c 
        for p in players
    ]
    player = [
        p for c in categories
        if 'Championship' not in c 
        for l in levels
        for p in players
    ] + [
        p for c in categories
        if 'Championship' in c
        for p in players
    ]
    skeleton = pd.DataFrame.from_dict(
        {
            'Category' : category,
            'Level' : level,
            'Player' : player
        }
    )
    df = df.merge(skeleton,how='outer')
    return df
    

def get(date,region='NTSC'):
    regionID = api.find_regions()
    categoryID = api.find_categories()
    levelID = api.find_levels()
    leaderboardURI = api.find_leaderboards(
        date = date,
        categoryID = categoryID,
        levelID = levelID,
        region = region)
    dfList = [
        api.parse_leaderboard(URI,regionID,categoryID,levelID)
        for URI in leaderboardURI]
    df = pd.concat(dfList)
    # turn back on when AdomHaMez gets fixed in order to implement PAL
    # df = df[df['Region'] == region]
    place = df.groupby(['Category','Level'])['Place'].rank(method='dense')
    df['Place'] = place.astype(int).values
    df.rename(columns={'Date':'Run Date'},inplace=True)
    df['Run Date'] = pd.to_datetime(df['Run Date'])
    df = fill_missing(df)
    df['Region'] = region
    df['Date'] = pd.to_datetime(date)
    save(df,date,region)
    return df