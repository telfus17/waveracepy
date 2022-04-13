from waveracepy import leaderboard
import pandas as pd
import numpy as np
import glob
import os

def package_path(*paths, package_directory=os.path.dirname(os.path.abspath('__init__.py'))):
    return os.path.join(package_directory, *paths)

def save(df,date,category,region='NTSC'):
    df.to_csv(
        package_path(
            'data',
            f'{region}',
            'scoresheets',
            f'{category}',
            f'{category}.{region}.{date}.csv'))  
    return None

def read(date,category,region='NTSC'):
    df = pd.read_csv(
        package_path(
            'data',
            f'{region}',
            'scoresheets',
            f'{category}',
            f'{category}.{region}.{date}.csv'),
        index_col=0)
    df['Run Date'] = pd.to_datetime(df['Run Date'])
    df['Date'] = pd.to_datetime(date)
    return df

def milestones(df):
    BM = df[df['Place'] == 3][['Category','Level','Time']].copy()
    if any(BM['Category'] == '1 Lap'):
        BM['3rd Time'] = BM['Time']
        BM['Benchmark Time'] = (np.ceil(2 * BM['Time']) / 2) - 0.001
        BM['Standard Time'] = BM['Benchmark Time'] + 0.5
    else:
        BM['3rd Time'] = BM['Time']
        BM['Benchmark Time'] = np.ceil(BM['Time']) - 0.001
        BM['Standard Time'] = BM['Benchmark Time'] + 1
    p4 = df[df['Place']==4][['Category','Level','Time']].copy()
    p4['4th Time'] = p4['Time']
    BM = BM.merge(p4[['Category','Level','4th Time']],how='outer')
    BM = BM[['Category','Level','Standard Time','Benchmark Time','3rd Time','4th Time']].copy()
    df = df.merge(BM, how = 'outer')
    return df

def base(df):
    df['Base Score'] = np.where(
        df['Time'] <= df['Standard Time'],
        df['Standard Time'],
        df['Time'])
    func = lambda x: (x.max() - x) / (x.max() - x.min())
    df['Base Score'] = df.groupby(['Category','Level'])['Base Score'].transform(func)
    df['Base Score'] = np.where(
        df['Category'] == '1 Lap',
        df['Base Score'] * 0.5,
        df['Base Score'] * 1)
    df['Base Score'] = df['Base Score'].round(2)
    return df

def standard(df):
    df['Standard Score'] = np.where(
        df['Time'] <= df['Benchmark Time'],
        df['Standard Time'] - df['Benchmark Time'],
        np.where(
            df['Time'] <= df['Standard Time'], 
            df['Standard Time'] - df['Time'],
            0))
    func = lambda x: x / x.max()
    df['Standard Score'] = df.groupby(['Category','Level'])['Standard Score'].transform(func)
    df['Standard Score'] = np.where(
        df['Category'] == '1 Lap',
        df['Standard Score'] * 1,
        df['Standard Score'] * 2)
    df['Standard Score'] = df['Standard Score'].round(2)
    return df

def benchmark(df):
    df['Benchmark Score'] = np.where(
        df['Time'] <= df['3rd Time'],
        df['Benchmark Time'] - df['3rd Time'],
        np.where(
            df['Time'] <= df['Benchmark Time'],
            df['Benchmark Time'] - df['Time'],
            0))
    func = lambda x: x / x.max()
    df['Benchmark Score'] = df.groupby(['Category','Level'])['Benchmark Score'].transform(func)
    df['Benchmark Score'] = np.where(
        df['Category'] == '1 Lap',
        df['Benchmark Score'] * 1.5,
        df['Benchmark Score'] * 3)
    df['Benchmark Score'] = df['Benchmark Score'].round(2)
    return df

def medal(df,IL=True):
    df['Medal Score'] = np.where(
        df['Place'] <= 4,
        df['4th Time'] - df['Time'],
        0)
    func = lambda x: x / x.max()
    df['Medal Score'] = df.groupby(['Category','Level'])['Medal Score'].transform(func)
    if not IL:
        df['Medal Score'] = np.where(
            df['Level'] == 'All Championships',
            df['Medal Score'] * 12,
            df['Medal Score'] * 3)
    else:
        df['Medal Score'] = np.where(
            df['Category'] == '1 Lap',
            df['Medal Score'] * 2,
            df['Medal Score'] * 4)
    df['Medal Score'] = df['Medal Score'].round(2)
    return df

def championship(df):
    func = lambda x: (x.max() - x) / (x.max() - x.min())
    df['Championship Score'] = df.groupby(['Level'])['Time'].transform(func)
    df['Championship Score'] = np.where(
        df['Level'] == 'All Championships',
        df['Championship Score'] * 8,
        df['Championship Score'] * 2)
    df['Championship Score'] = df['Championship Score'].round(2)
    return df

def previous(df,date,category,region='NTSC'):
    filePaths = sorted(glob.glob(package_path(
        'data',
        f'{region}',
        'scoresheets',
        f'{category}',
        '*')))
    prevPath = sorted([
            i for i in filePaths
            if i < package_path(
                'data',
                f'{region}',
                'scoresheets',
                f'{category}',
                f'{category}.{region}.{date}.csv')])
    if bool(prevPath):
        prevRun = pd.read_csv(prevPath[-1])[[
                'Player',
                'Category',
                'Level',
                'Time',
                'Run Score'
            ]]
        prevRun.rename(columns={'Run Score': 'Prev Run Score',
                                'Time': 'Prev Time'}, inplace=True)
        df = df.merge(prevRun, how='outer')
        df['dTIME'] = df['Time'] - df['Prev Time']
        df['dRUNSCORE'] = df['Run Score'] - df['Prev Run Score']
        df.drop(columns=['Prev Run Score','Prev Time'],inplace=True)
    return df

def IL(df,date):
    i3 = milestones(df[df['Category'] == '3 Lap'])
    i1 = milestones(df[df['Category'] == '1 Lap'])
    iR = milestones(df[df['Category'] == 'Reverse'])
    i = pd.concat([i3,i1,iR])
    i = base(i)
    i = standard(i)
    i = benchmark(i)
    i = medal(i)
    i = i.drop_duplicates()
    i['Run Score'] = i[['Base Score',
                          'Standard Score',
                          'Benchmark Score',
                          'Medal Score']].sum(axis=1).round(2)
    i = previous(i,date,'IL')
    save(i,date,'IL',region='NTSC')
    return i

def RTA(df,date):
    r = df[df['Category'] == 'RTA'].copy()
    p4 = r[r['Place']==4][['Category','Level','Time']].copy()
    p4['4th Time'] = p4['Time']
    r = r.merge(p4[['Category','Level','4th Time']],how='outer')
    r = championship(r)
    r = medal(r,IL=False)
    r = r.drop_duplicates()
    r['Run Score'] = r[['Championship Score','Medal Score']].sum(axis=1).round(2)
    r = previous(r,date,'RTA')
    save(r,date,'RTA',region='NTSC')
    return r