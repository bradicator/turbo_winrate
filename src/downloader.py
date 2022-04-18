"""
Match Data Downloader for Opendota.com
author: bradicator
created on: 2022/04/15
"""

import json as _json
import os as _os
from time import ctime as _ctime
from time import sleep as _sleep

import requests as _request
from joblib import Parallel, delayed
from requests.adapters import HTTPAdapter, Retry


class DataDownloader():

    def __init__(self, sleep_time=1):
        self._sleep_time = sleep_time
        self._lowest_match_id = None
        self.api_key_steam = None
        self.api_str_opendota = None
        with open("../resources/api_key_steam.txt") as f:
            self.api_key_steam = f.readlines()[0].strip('\n')
        if _os.path.exists("../resources/api_key_opendota.txt"):
            with open("../resources/api_key_opendota.txt") as f:
                self.api_str_opendota = f.readlines()[0].strip('\n')
        retries = Retry(total=10, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        self.session = _request.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def get_match_ids(self, match_id_lessthan=None):
        api_path = f"https://api.opendota.com/api/parsedMatches?"
        if match_id_lessthan:
            api_path += f"&less_than_match_id={match_id_lessthan}"
        if self.api_str_opendota:
            api_path += f"&api_key={self.api_str_opendota}"
        response_raw = self.session.get(api_path, timeout=5)
        response = _json.loads(response_raw.content)
        return [item['match_id'] for item in response]

    def get_parsed_match_info(self, match_id):
        api_path = f"https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v1/?key={self.api_key_steam}"
        api_path += f"&match_id={match_id}"
        response_raw = self.session.get(api_path, timeout=5)
        response_raw.raise_for_status()
        mdict = _json.loads(response_raw.content)['result']
        match_level_info = [mdict['match_id'], mdict['duration'], mdict['game_mode'], mdict['lobby_type'],
                            mdict['human_players'], mdict['start_time'], mdict['radiant_win']]
        hero_info = [mdict['players'][i]['hero_id'] for i in range(10)]
        return match_level_info + hero_info

    def download_matches(self, fname, mode='w', epoch=1):
        """download matches and write to file, each epoch is 100 matches"""
        if mode == 'a':
            with open(fname, 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    self._lowest_match_id = int(lines[-1].split(",")[0])
                    print(f"Appending to existing data file from match_id {self._lowest_match_id}")
        with open(fname, mode) as f:
            for e in range(epoch):
                print(e, _ctime())
                mids = self.get_match_ids(self._lowest_match_id)
                if e > 0:
                    print(self._lowest_match_id, all([x < self._lowest_match_id for x in mids]))
                results = Parallel(n_jobs=5, backend='multiprocessing')(
                    delayed(self.get_parsed_match_info)(mid) for mid in mids)
                if self._lowest_match_id:
                    self._lowest_match_id = min(self._lowest_match_id, results[-1][0])
                else:
                    self._lowest_match_id = results[-1][0]
                f.writelines([','.join([str(datum) for datum in data]) + "\n" for data in results])
                f.flush()
                _sleep(self._sleep_time)
        return
