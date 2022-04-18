#!//anaconda/bin/python3
# change the line above to your python path
"""
Load and analyze match data
author: bradicator
created on: 2022/04/15
"""

from itertools import product as _product

import numpy as _np
import pandas as _pd

from utils import *


class Analyzer:
    def __init__(self, fpath, turbo_only=True):
        self.hdict = get_heroid_dict()
        colnames = ['match_id', 'duration', 'game_mode', 'lobby_type',
                    'human_players', 'start_time', 'radiant_win',
                    'hero0', 'hero1', 'hero2', 'hero3', 'hero4',
                    'hero5', 'hero6', 'hero7', 'hero8', 'hero9']
        if not isinstance(fpath, list):
            fpath = [fpath]
        frames = [_pd.read_csv(f, names=colnames, header=None) for f in fpath]
        self.df = _pd.concat(frames, ignore_index=True)
        # radiant_win can be -1 due to steam API response empty
        self.df = self.df.loc[self.df.radiant_win >= 0 and self.df.lobby_type == 0, :]
        if turbo_only:
            self.df = self.df.loc[self.df.game_mode == 23, :]
        self.fill_match_up_table()

    def fill_match_up_table(self):
        self.mutable = _np.zeros((138, 138))
        for idx, r in self.df.iterrows():
            for i, j in _product(range(5), range(5, 10)):
                if r.radiant_win:
                    self.mutable[r[f'hero{i}'], r[f'hero{j}']] += 1
                else:
                    self.mutable[r[f'hero{j}'], r[f'hero{i}']] += 1

    def get_hero_winrate(self, heroid):
        nwin = _np.sum(self.mutable[heroid, :])
        nloss = _np.sum(self.mutable[:, heroid])
        return nwin / (nwin + nloss), nwin / 5, nloss / 5

    def get_all_winrate(self):
        res = []
        for k, v in self.hdict.items():
            res.append([v, *self.get_hero_winrate(k)])
        winratedf = _pd.DataFrame(res, columns=['hero', 'winrate', 'nwin', 'nloss'])
        return winratedf.sort_values('winrate', ascending=False)

    def get_counter_winrate(self, heroid):
        res = []
        avgwinrate = self.get_hero_winrate(heroid)[0]
        for hid in range(138):
            if self.mutable[heroid, hid] > 0 or self.mutable[hid, heroid] > 0:
                wr = self.mutable[heroid, hid] / (self.mutable[heroid, hid] + self.mutable[hid, heroid])
                res.append((self.hdict[heroid], self.hdict[hid], self.mutable[heroid, hid], self.mutable[hid, heroid],
                            wr, avgwinrate))
        df = _pd.DataFrame(res, columns=['queried_hero', 'against_hero', 'nwin', 'nloss',
                                         'matchup_winrate', 'avg_winrate'])
        return df.sort_values('matchup_winrate')

    def get_all_counter_winrate(self):
        dfs = [self.get_counter_winrate(heroid) for heroid in range(138)]
        return _pd.concat(dfs, ignore_index=True)
