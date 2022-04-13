from waveracepy import score
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

def get(df,date,region='NTSC'):
    i = score.IL(df,date)
    r = score.RTA(df,date)
    t = i.merge(r,how='outer')
    t['Sheet'] = 1
    t['IL Sheet'] = np.where(t['Category']!='RTA',1,0)
    t['RTA Sheet'] = np.where(t['Category']=='RTA',1,0)
    t['Standards'] = np.where(t['Time']<=t['Standard Time'],1,0)
    t['Benchmarks'] = np.where(t['Time']<=t['Benchmark Time'],1,0)
    t['Bronze'] = np.where(t['Place']==3,1,0)
    t['Silver'] = np.where(t['Place']==2,1,0)
    t['Gold'] = np.where(t['Place']==1,1,0)
    t['Medals'] = np.where(t['Place']<=3,1,0)
    t = t[['Player','Sheet','IL Sheet',
           'RTA Sheet','Standards','Benchmarks',
           'Bronze','Silver','Gold',
           'Medals']].groupby(['Player']).sum()
    t['Date'] = date
    save(t,date,region)
    return t