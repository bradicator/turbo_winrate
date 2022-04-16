#!//anaconda/bin/python3
# change the line above to your python path
"""
Load and analyze match data
author: bradicator
created on: 2022/04/15
"""

import pandas as _pd
import numpy as _np
import sys
sys.path.append("/Users/ruofeizhao/Documents/turbo_winrate/") # change this to module's path
from itertools import product as _product
from collections import defaultdict as _ddict
from turbo_winrate.utils import *

class Analyzer:
    def __init__(self, fpath, turbo_only=True):
        self.hdict = get_heroid_dict()
        colnames = ['match_id', 'duration', 'game_mode',
                            'human_players', 'start_time', 'version',
                            'patch', 'radiant_win', 'hero0', 'hero1',
                            'hero2', 'hero3', 'hero4', 'hero5',
                            'hero6', 'hero7', 'hero8', 'hero9']
        if not isinstance(fpath, list):
            fpath = [fpath]
        self.df = _pd.DataFrame([], columns=colnames)
        for f in fpath:
            df_batch = _pd.read_csv(f)
            df_batch.columns = colnames
            self.df = self.df.append(df_batch)
        if turbo_only:
            self.df = self.df.loc[self.df.game_mode == 23, :]
            
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
        return nwin / (nwin+nloss), nwin/5, nloss/5 
    
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

if __name__ == "__main__":
    az = Analyzer("./data0416.txt")
    az.fill_match_up_table()
    hdict = get_heroid_dict()
    if sys.argv[1] == "-w" or sys.argv[1] == "-winrate":
        if sys.argv[2].isdigit():
            hid = int(sys.argv[2])
        else:
            hid = guess_hero_id(sys.argv[2])
        if not hid:
            print("can't find this hero, try another name")
        print(hdict[hid], az.get_hero_winrate(hid))
    elif sys.argv[1] == "-a" or sys.argv[1] == "-all":
        print(az.get_all_winrate().to_string())
    elif sys.argv[1] == "-c" or sys.argv[1] == "-counter":
        if sys.argv[2].isdigit():
            hid = int(sys.argv[2])
        else:
            hid = guess_hero_id(sys.argv[2])
        if not hid:
            print("can't find this hero, try another name")
        print(az.get_counter_winrate(hid).to_string())
    else:
        helpinfo = """
        Help Info:
        use -w {heroid|heroname} or -winrate {heroid|heroname} to check a hero's winrate in turbo
        example: analyzer.py -w 2
        example: analyzer.py -w terror
        
        use -a or -all to print out all heroes' wr in turbo
        example: analyzer.py -a
        
        use -c {heroid|heroname} or -counter {heroid|heroname} to check what counters a hero in turbo
        example: analyzer.py -c 2
        example: analyzer.py -c ogre
        """
        print(helpinfo)
        
