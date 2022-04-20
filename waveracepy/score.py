from waveracepy import leaderboard
import pandas as pd
import numpy as np
import glob
import os

def package_path(
    *paths,
    package_directory=os.path.dirname(
        os.path.abspath('__init__.py')
    )
):
    
    '''
    get absolute path to data folder
    '''
    
    return os.path.join(package_directory, *paths)

def save(
    df,
    date,
    region='NTSC'
):
    
    '''
    save scoresheet to csv
    '''
    
    # save scoresheet to csv
    df.to_csv(
        package_path(
            'data',
            f'{region}',
            'scoresheets',
            f'SC.{region}.{date}.csv'
        )
    )  
    
    return None

def read(
    date,
    region='NTSC'
):
    
    '''
    read scoresheet from csv
    '''
    
    # read scoresheet
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'scoresheets',
            f'SC.{region}.{date}.csv'
        ),
        index_col=0
    )
    
    # convert dates from string to datetime
    df['Run Date'] = pd.to_datetime(df['Run Date'])
    df['Date'] = pd.to_datetime(date)
    
    return df

def previous(df,date,region='NTSC'):
    
    '''
    '''
    
    # get sorted list of all previously saved scoresheets
    prevPaths = sorted(
        [
            i for i in glob.glob(
                package_path(
                    'data',
                    f'{region}',
                    'scoresheets',
                    '*'
                )
            )
            if i < package_path(
                'data',
                f'{region}',
                'scoresheets',
                f'SC.{region}.{date}.csv'
            )
        ]
    )
    
    # if the list is not empty
    if bool(prevPaths):
        
        # select necessary columns from the most recent scoresheet
        prevRun = pd.read_csv(prevPaths[-1])[
            [
                'Player',
                'Category',
                'Level',
                'dtWR',
                'Score'
            ]
        ]
        
        # rename score and time columns
        prevRun.rename(
            columns={
                'Score': 'pScore',
                'dtWR': 'pdtWR'
            },
            inplace=True
        )
        
        # merge with current scoresheet
        df = df.merge(prevRun, how='outer')
        
        # calculate the time improvement
        df['dT'] = (df['dtWR'] - df['pdtWR']).round(3)
        
        # calculate the score improvement
        df['dS'] = df['Score'] - df['pScore']
        
        # drop unnecessary columns
        df.drop(columns=['pScore','pdtWR'],inplace=True)
    
    return df

def get(
    df,
    date,
    region='NTSC',
    sMedian=0.15
):
    
    '''
    
    '''
    
    # get world record for each course
    df['tWR'] = df.groupby(['Category','Level'])['Time'].transform(
        lambda x : x.min()
    )
    
    # caclulate the difference between run time and world record time
    df['dtWR'] = df['Time'] - df['tWR']
    
    # calculate the median difference for each course
    df['dtMedian'] = df.groupby(['Category','Level'])['dtWR'].transform(
        lambda x : x.median()
    )
    
    # calculate score for each run
    df['Score'] = np.exp((np.log(sMedian) / df['dtMedian']) * df['dtWR'])
    
    # apply course-specific multipliers
    df['Score'] = np.where(
        df['Category'] == 'RTA',
        np.where(
            df['Level'] == 'All Championships',
            df['Score'] * 20,
            df['Score'] * 5
        ),
        np.where(
            df['Category'] == '1 Lap',
            df['Score'] * 5,
            df['Score'] * 10
        )
    )
    
    # replace nan with a score of 0
    df['Score'].fillna(0,inplace=True)
    
    # round scores to two decimal places
    df['Score'] = np.round(df['Score'],3)
    
    # compare with previous scores
    df = previous(df,date,region)
    
    # save scoresheet to csv
    save(df,date,region)

    return df
    
    