# turbo_winrate

Try something like:

from turbo_winrate import *
df = load_matches("./first_batch.txt")
muc = get_match_up_count_table(df)
for k, v in hdict.items():
print(v, get_hero_winrate(k, muc))
