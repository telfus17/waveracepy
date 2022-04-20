import waveracepy.rank as rank
import waveracepy.tally as tally
import waveracepy.score as score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import seaborn as sns
import datetime
import os
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def package_path(*paths, package_directory=os.path.dirname(os.path.abspath('__init__.py'))):
    return os.path.join(package_directory, *paths)

def plot():
    
    R = rank.read(date='2022-01-01')
    
    fig,ax = plt.subplots(figsize=(12,10))

    top10 = R[R['Current Rank']<=10]
    tier1hm = R[R['Player'].isin([
        'dosufura',
        'NickWarner',
        'RyanWarner',
        'ZubyDoo77'
    ])]
    tier2hm = R[R['Player'].isin([
        'AdomHaMez',
        'arata0503',
        'VR747_CHALON_Type_a8',
        'touhu_dnb'
    ])]

    ax.plot(
        R['Current Rank'],
        R['Total Score'],
        c = 'k',
        alpha = 0.5,
        zorder = 0,
        ls = '-',
        lw = 1
    )

    ax.scatter(
        R['Current Rank'],
        R['Total Score'],
        c = 'gainsboro',
        ec = 'k',
        zorder=1,
        clip_on = False
    )

    ax.scatter(
        top10['Current Rank'],
        top10['Total Score'],
        c = 'cornflowerblue',
        s = 150,
        ec = 'k',
        zorder = 2,
        label = 'Top 10',
        clip_on = False
    )

    ax.scatter(
        tier1hm['Current Rank'],
        tier1hm['Total Score'],
        c = 'yellowgreen',
        s = 150,
        ec = 'k',
        marker = 's',
        zorder = 2,
        label = 'Tier 1 HM',
        clip_on = False
    )

    ax.scatter(
        tier2hm['Current Rank'],
        tier2hm['Total Score'],
        c = 'gold',
        s = 175,
        ec = 'k',
        marker = '^',
        zorder = 2,
        label = 'Tier 2 HM',
        clip_on = False
    )

    for i in np.delete(np.arange(10),[4,5,6,7]):
        label = top10['Player'][i]
        ax.annotate(
            str(i+1) + '. ' + label,
            (
                top10['Current Rank'][i],
                top10['Total Score'][i]
            ),
            textcoords = 'offset points',
            xytext = (15,0),
            ha = 'left',
            va = 'center'
        )

    for i in np.arange(2):
        index = [4,6]
        j = index[i]
        label = top10['Player'][j]
        ax.annotate(
            str(j + 1) + '. ' + label,
            (
                top10['Current Rank'][j],
                top10['Total Score'][j]
            ),
            textcoords = 'offset points',
            xytext = (10,-60),
            ha = 'right',
            va = 'top',
            arrowprops = dict(
                arrowstyle = '->',
                connectionstyle = 'arc3,rad=-0.1',
                shrinkA = 2,
                shrinkB = 10
            )
        )

    for i in np.arange(2):
        index = [5,7]
        j = index[i]
        label = top10['Player'][j]
        ax.annotate(
            str(j + 1) + '. ' + label,
            (
                top10['Current Rank'][j],
                top10['Total Score'][j]
            ),
            textcoords = 'offset points',
            xytext = (30,30),
            ha = 'left',
            va = 'bottom',
            arrowprops = dict(
                arrowstyle = '->',
                connectionstyle = 'arc3,rad=-0.15',
                shrinkA = 2,
                shrinkB = 10
            )
        )

    ax.add_patch(Ellipse(xy=(3, 46.53), width=1.6, height=5, color='orangered', fill=False, lw=4, alpha=0.8, zorder=3))
    ax.add_patch(Ellipse(xy=(14, 5.65), width=1.6, height=5, color='orangered', fill=False, lw=4, alpha=0.8, zorder=3))
    ax.add_patch(Ellipse(xy=(7.5, 25.725), width=3.25, height=5, color='orangered', fill=False, lw=4, alpha=0.8, zorder=3))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_ylim([0,100])
    ax.legend()
    ax.set_title('2021 (Q4) Rankings',fontsize='xx-large')
    ax.set_ylabel('Total Score',fontsize='large')
    ax.set_xlabel('Current Rank',fontsize='large')
    ax.set_zorder(0)
    plt.tight_layout()
    
def compare_styles():
    T = tally.read(date='2022-01-01')
    T = T[T['Player'].isin([
        'AS_Money',
        'Illudude',
        'VR747_CHALON_Type_a8']
    )]
    T.drop(columns=['Bronze','Silver','Gold','Date'],inplace=True)
    T.set_index('Player',inplace=True)
    T.index.name = None
    return T

def top10():
    R = rank.read(date='2022-01-01')
    R = R[R['Current Rank']<=10]
    R.set_index('Player',inplace=True)
    R.drop(columns='Date',inplace=True)
    R.index.name = None
    return R

def compare_t10(date):
    S = score.read(date)
    S['Score'] = S.groupby(['Category','Level'])['Score'].transform(lambda x : 10 * x / x.max())
    R = rank.read(date)
    S = tally.milestones(S)
    S['Achievement'] = np.where(
        S['Place'] <= 3,
        'Medal',
        np.where(
            S['Time'] <= S['tST'],
            np.where(
                S['Time'] <= S['tBM'],
                'Benchmark',
                'Standard'
            ),
            'None'
        )
    )

    fig,ax = plt.subplots(ncols=1,figsize=(21,7))

    players = R[R['Current Rank']<=12]['Player']

    sns.violinplot(
        data = S[(S['Player'].isin(players))],
        y = 'Score',
        x ='Player',
        scale = 'width',
        bw=0.1,
        cut=1,
        inner = None,
        order = players,
        palette = sns.color_palette('colorblind'),
        linewidth = 0.5,
        zorder = 0
    )

    sns.swarmplot(
        data = S[(S['Player'].isin(players))],
        y = 'Score',
        x ='Player',
        order = players,
        size = 2,
        linewidth = 1,
        color = 'black',
        alpha = 0.5,
        zorder = 2
    )

    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax.set_xlabel('Current Rank')
    ax.set_ylim([-0.4,10.4])
    ax.grid(zorder=0,alpha=0.05,which='major',axis='y')
    ax.axvline(9.5,c='orangered',ls='--',lw=2,label='Top 10 Cutoff')
    ax.legend(prop={'size': 15})
    plt.tight_layout()
    
def old_v_new():
    fig,ax = plt.subplots(ncols=3,figsize=(12,4))
    multiplier = 10
    date = '2022-01-01'
    sMedian = 1/6
    category = '3 Lap'
    level = 'Sunny Beach'
    S = score.read(date)
    pS = pd.read_csv(package_path('data','NTSC','scoresheets','IL.NTSC.2022-01-01.csv'))
    S = S[(S['Category']==category) & (S['Level']==level)]
    pS = pS[(pS['Category']==category) & (pS['Level']==level)]
    pS['tWR'] = pS.groupby(['Category','Level'])['Time'].transform(lambda x : x.min())
    pS['dtWR'] = pS['Time'] - pS['tWR']
    dtMedian = S['dtMedian'].max()
    x = np.arange(0,S['dtWR'].max(),0.001)
    y = np.exp((np.log(sMedian) / dtMedian) * x) * multiplier
    ax[0].plot(x,y,c='k',alpha=0.2,zorder=0)
    ax[0].scatter(
        S['dtWR'],
        S['Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s = 45,
        label='New Scores'
    )
    ax[0].scatter(
        pS['dtWR'],
        pS['Run Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s=45,
        label='Old Scores'
    )
    ax[0].legend()
    ax[0].set_title(f'{level} ({category})')
    ax[0].set_xlabel('dtWR')
    ax[0].set_ylabel('score')
    multiplier = 10
    date = '2022-01-01'
    sMedian = 1/6
    category = 'Reverse'
    level = 'Port Blue'
    S = score.read(date)
    pS = pd.read_csv(package_path('data','NTSC','scoresheets','IL.NTSC.2022-01-01.csv'))
    S = S[(S['Category']==category) & (S['Level']==level)]
    pS = pS[(pS['Category']==category) & (pS['Level']==level)]
    pS['tWR'] = pS.groupby(['Category','Level'])['Time'].transform(lambda x : x.min())
    pS['dtWR'] = pS['Time'] - pS['tWR']
    dtMedian = S['dtMedian'].max()
    x = np.arange(0,S['dtWR'].max(),0.001)
    y = np.exp((np.log(sMedian) / dtMedian) * x) * multiplier
    ax[2].plot(x,y,c='k',alpha=0.2,zorder=0)
    ax[2].scatter(
        S['dtWR'],
        S['Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s = 45,
        label='New Scores'
    )
    ax[2].scatter(
        pS['dtWR'],
        pS['Run Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s=45,
        label='Old Scores'
    )
    ax[2].legend()
    ax[2].set_title(f'{level} ({category})')
    ax[2].set_xlabel('dtWR')
    ax[2].set_ylabel('score')
    multiplier = 5
    date = '2022-01-01'
    sMedian = 1/6
    category = '1 Lap'
    level = 'Drake Lake'
    S = score.read(date)
    pS = pd.read_csv(package_path('data','NTSC','scoresheets','IL.NTSC.2022-01-01.csv'))
    S = S[(S['Category']==category) & (S['Level']==level)]
    pS = pS[(pS['Category']==category) & (pS['Level']==level)]
    pS['tWR'] = pS.groupby(['Category','Level'])['Time'].transform(lambda x : x.min())
    pS['dtWR'] = pS['Time'] - pS['tWR']
    dtMedian = S['dtMedian'].max()
    x = np.arange(0,S['dtWR'].max(),0.001)
    y = np.exp((np.log(sMedian) / dtMedian) * x) * multiplier
    ax[1].plot(x,y,c='k',alpha=0.2,zorder=0)
    ax[1].scatter(
        S['dtWR'],
        S['Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s = 45,
        label='New Scores'
    )
    ax[1].scatter(
        pS['dtWR'],
        pS['Run Score'],
        ec='k',
        alpha=0.9,
        zorder=1,
        s=45,
        label='Old Scores'
    )
    ax[1].legend()
    ax[1].set_title(f'{level} ({category})')
    ax[1].set_xlabel('dtWR')
    ax[1].set_ylabel('score')
    plt.tight_layout()

def score_curve(df,category,multiplier):
    sMedian = 1/6
    df = df[df['Category']==category].copy()
    x = np.arange(0,multiplier,0.001)
    df = df.groupby('Level')['dtMedian'].median().reset_index()
    y = [np.exp((np.log(sMedian) / i) * x) * multiplier for i in df['dtMedian']] 
    level = [i for i in df['Level']]
    y = dict(zip(level,y))
    return x,y   
    
def compare_curves():
    date = '2022-01-01'
    S = score.read(date)

    fig,ax = plt.subplots(ncols=3,figsize=(12,4))

    x,y = score_curve(S,'3 Lap',10)
    levels = list(y.keys())
    for i in levels:
        ax[0].plot(
            x,
            y[i],
            label=i
        )
    ax[0].legend()
    ax[0].set_title('3 Lap')

    x,y = score_curve(S,'1 Lap',5)
    levels = list(y.keys())
    for i in levels:
        ax[1].plot(
            x,
            y[i],
            label=i
        )
    ax[1].legend()
    ax[1].set_title('1 Lap')

    x,y = score_curve(S,'Reverse',10)
    levels = list(y.keys())
    for i in levels:
        ax[2].plot(
            x,
            y[i],
            label=i
        )
    ax[2].legend()
    ax[2].set_title('Reverse')
    plt.tight_layout()
