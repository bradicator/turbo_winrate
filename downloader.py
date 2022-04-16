"""
Match Data Downloader for Opendota.com
author: bradicator
created on: 2022/04/15
"""

import requests as _request
import pandas as _pd
import json as _json
from time import sleep as _sleep
from time import ctime as _ctime
import os as _os

class DataDownloader():
    
    def __init__(self, sleep_time=1):
        self._sleep_time = sleep_time
        self._lowest_match_id = None
        self.api_str = None
        if _os.path.exists("/Users/ruofeizhao/Documents/turbo_winrate/apikey.txt"):
            with open("/Users/ruofeizhao/Documents/turbo_winrate/apikey.txt") as f:
                self.api_str = f.readlines()[0].strip('\n')
        
    
    def get_match_ids(self, match_id_lessthan=None):
        address = "https://api.opendota.com/api/parsedMatches"
        if match_id_lessthan:
            if self.api_str:
                address += f"?less_than_match_id={match_id_lessthan}&api_key={self.api_str}"
            else:
                address += f"?api_key={self.api_str}"        
        _sleep(self._sleep_time)
        response = _request.get(address)
        mlist = _json.loads(response.content)
        return [item['match_id'] for item in mlist] 
        
    def get_raw_match_info(self, match_id):
        _sleep(self._sleep_time)
        if self.api_str:
            return _request.get(f"https://api.opendota.com/api/matches/{match_id}?api_key={self.api_str}")
        else: 
            return _request.get(f"https://api.opendota.com/api/matches/{match_id}")
        
    def get_parsed_match_info(self, match_id):
        response = self.get_raw_match_info(match_id)
        mdict = _json.loads(response.content)
        match_level_info = [mdict['match_id'], mdict['duration'], mdict['game_mode'],
                            mdict['human_players'], mdict['start_time'], mdict['version'],
                            mdict['patch'], mdict['radiant_win']]
        hero_info = [mdict['players'][i]['hero_id'] for i in range(10)]
        return match_level_info + hero_info
    
    def download_matches(self, fname, mode='w', epoch=1):
        """download matches and write to file, each epoch is 100 matches"""
        with open(fname, mode) as f:
            for e in range(epoch):
                print(e, _ctime())
                mids = self.get_match_ids(self._lowest_match_id)
                buf = ""
                if e > 0:
                    print(self._lowest_match_id, all([x < self._lowest_match_id for x in mids]))
                for id in mids:
                    data = self.get_parsed_match_info(id)
                    if self._lowest_match_id:
                        self._lowest_match_id = min(self._lowest_match_id, data[0])
                    else:
                        self._lowest_match_id = data[0]
                    buf += ','.join([str(datum) for datum in data]) + "\n"
                f.writelines(buf)
                f.flush()
        return
                
            
        
        