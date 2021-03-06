import waveracepy.rank as rank
import waveracepy.tally as tally
import waveracepy.score as score
import pandas as pd
import numpy as np

def newcomers(date):
    R = rank.read(date)
    new = R[np.isnan(R['dS'])]
    df = score.read(date)
    df = df[df['Player'].isin(new['Player'])]
    df['Submissions'] = np.where(np.isnan(df['Time']),0,1)
    df = df.groupby(['Player'])['Submissions'].sum().reset_index()
    df.sort_values(by=['Player'],key=lambda x: x.str.lower(),inplace=True)
    df.rename(columns={'Player':'New Player'},inplace=True)
    df.set_index(['New Player','Submissions'],inplace=True)
    return df

def pbs(date):
    df = score.read(date)
    df = df[df['dT']<-0.001]
    df['New PBs'] = 1
    df = df.groupby('Player')['New PBs'].sum().reset_index()
    df.sort_values(by=['Player'],key=lambda x: x.str.lower(),inplace=True)
    df.sort_values(by=['New PBs'],ascending=False,inplace=True)
    df.set_index(['Player','New PBs'],inplace=True)
    return df

def complete_sheet(date):
    df = tally.read(date)
    df = df[df['Sheet']==29].sort_values(['Player'],key=lambda x: x.str.lower())
    df.rename(columns={'Player':'Complete Sheet'},inplace=True)
    df = df[['Complete Sheet']].set_index('Complete Sheet')
    return df

def all_standards(date):
    df = tally.read(date)
    df = df[df['Standards']==24].sort_values(['Player'],key=lambda x: x.str.lower())
    df.rename(columns={'Player':'All Standards'},inplace=True)
    df = df[['All Standards']].set_index('All Standards')
    return df

def all_benchmarks(date):
    df = tally.read(date)
    df = df[df['Benchmarks']==24].sort_values(['Player'],key=lambda x: x.str.lower())
    df.rename(columns={'Player':'All Benchmarks'},inplace=True)
    df = df[['All Benchmarks']].set_index('All Benchmarks')
    return df

def all_medals(date):
    df = tally.read(date)
    df = df[df['Medals']==29].sort_values(['Player'],key=lambda x: x.str.lower())
    df.rename(columns={'Player':'All Medals'},inplace=True)
    df = df[['All Medals']].set_index('All Medals')
    return df
    