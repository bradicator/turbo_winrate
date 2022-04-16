"""
Match Data Downloader for Opendota.com
author: bradicator
created on: 2022/04/15
"""

import requests as _request
import pandas as _pd
import json as _json
from time import sleep as _sleep


class DataDownloader():
    def __init__(self, sleep_time=1):
        self._sleep_time = sleep_time
        self._lowest_match_id = None
    
    def get_match_ids(self, match_id_lessthan=None):
        address = "https://api.opendota.com/api/parsedMatches"
        if match_id_lessthan:
            address += f"?less_than_match_id={match_id_lessthan}"
        _sleep(self._sleep_time)
        response = _request.get(address)
        mlist = _json.loads(response.content)
        return [item['match_id'] for item in mlist] 
        
    def get_raw_match_info(self, match_id):
        _sleep(self._sleep_time)
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
                mids = self.get_match_ids(self._lowest_match_id)
                for id in mids:
                    data = self.get_parsed_match_info(id)
                    if self._lowest_match_id:
                        self._lowest_match_id = min(self._lowest_match_id, data[0])
                    else:
                        self.lowest_match_id = data[0]
                    f.write(','.join([str(datum) for datum in data]) + "\n")
        return
                
            
        
        