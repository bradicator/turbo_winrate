"""
Util functions for turbo_winrate
author: bradicator
created on: 2022/04/15
"""
import json as _json
import re as _re

def get_heroid_dict(hero_path="./heroinfo.json"):
    with open(hero_path) as f:
        herojson = f.readlines()
    hero_json_dict = _json.loads(herojson[0])
    hdict = dict()
    for k, v in hero_json_dict.items():
       hdict[v['id']] = v['localized_name']
    return hdict

def guess_hero_id(heroname):
    hdict = get_heroid_dict()
    lower_hname = heroname.lower()
    for id, name in hdict.items():
        if _re.search(lower_hname, name.lower()):
            return id
    return None