from waveracepy import score
from waveracepy import rank
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
            'tallysheets',
            f'T.{region}.{date}.csv'))  
    return None

def read(date,region='NTSC'):
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'tallysheets',
            f'T.{region}.{date}.csv'))
    df['Date'] = pd.to_datetime(date)
    return df

def milestones(df):
    
    df['tBM'] = np.where(
        df['Category'] == 'RTA',
        np.nan,
        np.where(
            df['Category'] == '1 Lap',
            df.groupby('Level')['Time'].transform(
                lambda x : (np.ceil(2*x.nsmallest(3).max())/2)-0.001
            ),
            df.groupby(['Category','Level'])['Time'].transform(
                lambda x : np.ceil(x.nsmallest(3).max())-0.001
            )
        )
    )

    df['tST'] = np.where(
        df['Category'] == 'RTA',
        np.nan,
        np.where(
            df['Category'] == '1 Lap',
            df['tBM'] + 0.5,
            df['tBM'] + 1
        )
    )
    
    return df

def get(date,region='NTSC'):
    S = score.read(date)
    S = milestones(S)
    S['Sheet'] = np.where(np.isnan(S['Time']),0,1)
    S['Standards'] = np.where(S['Time']<=S['tST'],1,0)
    S['Benchmarks'] = np.where(S['Time']<=S['tBM'],1,0)
    S['Bronze'] = np.where(S['Place']==3,1,0)
    S['Silver'] = np.where(S['Place']==2,1,0)
    S['Gold'] = np.where(S['Place']==1,1,0)
    S['Medals'] = np.where(S['Place']<=3,1,0)
    R = rank.read(date)
    S = S.merge(R[['Player','Current Rank','Alltime Rank']],how='outer')
    T = S[
        [
            'Player',
            'Sheet',
            'Standards',
            'Benchmarks',
            'Bronze',
            'Silver',
            'Gold',
            'Medals'
        ]
    ].groupby('Player').sum().reset_index()
    T = T.merge(R[
        [
            'Player',
            'Alltime Rank',
            'Current Rank'
        ]
    ],how='outer').sort_values(
        by=[
        'Current Rank',
        'Alltime Rank'
        ]
    )
    T['Date'] = date
    save(T,date,region)
    return T