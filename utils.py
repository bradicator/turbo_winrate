"""
Util functions for turbo_winrate
author: bradicator
created on: 2022/04/15
"""
import json as _json

def get_heroid_dict(hero_path="./heroinfo.json"):
    with open(hero_path) as f:
        herojson = f.readlines()
    hero_json_dict = _json.loads(herojson[0])
    hdict = dict()
    for k, v in hero_json_dict.items():
       hdict[v['id']] = v['localized_name']
    return hdict

 