import waveracepy.score as score
import waveracepy.leaderboard as leaderboard
import waveracepy.tally as tally
import pandas as pd
import numpy as np
import glob
import os
import datetime

def package_path(
    *paths,
    package_directory=os.path.dirname(
        os.path.abspath('__init__.py')
    )
):
    
    '''
    '''
    
    return os.path.join(
        package_directory,
        *paths
    )

def save(
    df,
    date,
    region='NTSC'
):
    
    df.to_csv(
        package_path(
            'data',
            f'{region}',
            'rankings',
            f'R.{region}.{date}.csv'
        )
    )  
    
    return None

def read(
    date,
    region='NTSC'
):
    
    '''
    '''
    
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'rankings',
            f'R.{region}.{date}.csv'
        ),
        index_col=0
    )
    
    df['Date'] = pd.to_datetime(date)
    
    return df

def get(
    date,
    region = 'NTSC',
    activity = 2,
    sMedian = 1/6
):
    
    '''
    '''

    # if leaderboard exists, read from csv
    if os.path.isfile(
        package_path(
            'data',
            f'{region}',
            'leaderboards',
            f'LB.{region}.{date}.csv'
        )
    ):
        lb = leaderboard.read(
            date,
            region
        )
    
    # if leaderboard does not exist, get from API
    else:
        lb = leaderboard.get(
            date,
            region
        )
    
    # calculate run scores
    df = score.get(
        lb,
        date,
        region,
        sMedian
    )
    
    # 
    if 'dS' in df.columns:
        df = df.groupby('Player')[['Score','dS']].sum(min_count=1).reset_index()
        
    #
    else:
        df = df.groupby('Player')['Score'].sum().reset_index()
    
    # determine which players are active/inactive
    df.insert(
        1,
        'Status',
        np.where(
            df['Player'].isin(
                lb[
                    lb['Run Date'] > 
                    (lb['Date'] - pd.DateOffset(years=activity))
                ]['Player']
            ),
            'Active',
            'Inactive'
        )
    )
    
    # rank all players
    df['Alltime Rank'] = df['Score'].rank(ascending=False,method='min')
    
    # rank active players
    active = df[df['Status']=='Active'].copy()
    active['Current Rank'] = active['Score'].rank(ascending=False,method='min')
    df = df.merge(active,how='outer')
    df = df.sort_values(by='Current Rank')
    
    # generate tallysheet
    T = tally.get(date)
    
    # save rankings to csv
    save(df,date,region)
    
    return df
    