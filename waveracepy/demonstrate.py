import waveracepy.rank as rank
import waveracepy.tally as tally
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

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
    