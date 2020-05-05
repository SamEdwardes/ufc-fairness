import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

df = pd.read_csv("../data/fight_results.csv")
df['date'] = pd.to_datetime(df['date'])
df.head()


# shuffle the order of fighers. UFC always has the winning figher as fighter 1
df['fight_id'] = df.index
df['blue'] = np.random.choice(a=[1, 2], p=[0.5, 0.5], size=df.shape[0])
df['red'] = df['blue'].apply(lambda x: 1 if x == 2 else 2)
df['winner_colour'] = df['blue'].apply(lambda x: "blue" if x == 1 else "red")
df['blue'] = df.apply(lambda x: x['fighter_1_name'] if x['blue'] == 1 else x['fighter_2_name'], axis=1)
df['red'] = df.apply(lambda x: x['fighter_1_name'] if x['red'] == 1 else x['fighter_2_name'], axis=1)
df


# pivot longer
cols_to_pivot = ['fighter_1_name', 'fighter_2_name']

df_long = df.melt(
    value_vars=cols_to_pivot,
    id_vars=[i for i in df.columns if i not in cols_to_pivot],
    value_name="fighter_name", var_name="fighter_number"
)

df_long['colour'] = df_long.apply(lambda x: 'blue' if x['blue'] == x['fighter_name'] else 'red', axis=1)
df_long['opponent_name'] = df_long.apply(lambda x: x['blue'] if x['red'] == x['fighter_name'] else x['red'], axis=1)
df_long['str'] = df_long.apply(lambda x: x['fighter_1_str'] if x['fighter_number'] == 'fighter_1_name' else  x['fighter_2_str'], axis=1)
df_long['td'] = df_long.apply(lambda x: x['fighter_1_td'] if x['fighter_number'] == 'fighter_1_name' else  x['fighter_2_td'], axis=1)
df_long['sub'] = df_long.apply(lambda x: x['fighter_1_sub'] if x['fighter_number'] == 'fighter_1_name' else  x['fighter_2_sub'], axis=1)
df_long['pass'] = df_long.apply(lambda x: x['fighter_1_pass'] if x['fighter_number'] == 'fighter_1_name' else  x['fighter_2_pass'], axis=1)

df_long['opp_str'] = df_long.apply(lambda x: x['fighter_1_str'] if x['fighter_number'] == 'fighter_2_name' else  x['fighter_2_str'], axis=1)
df_long['opp_td'] = df_long.apply(lambda x: x['fighter_1_td'] if x['fighter_number'] == 'fighter_2_name' else  x['fighter_2_td'], axis=1)
df_long['opp_sub'] = df_long.apply(lambda x: x['fighter_1_sub'] if x['fighter_number'] == 'fighter_2_name' else  x['fighter_2_sub'], axis=1)
df_long['opp_pass'] = df_long.apply(lambda x: x['fighter_1_pass'] if x['fighter_number'] == 'fighter_2_name' else  x['fighter_2_pass'], axis=1)

df_long['winner'] = df_long.apply(lambda x: 1 if x['winner_colour'] == x['colour'] else 0, axis=1)

df_long = df_long[['event_name', 'date', 'weight_class', 'win_method', 'win_round', 'win_time',
                   'fight_id', 'fighter_name',  'str', 'td', 'sub', 'pass', 
                   'opponent_name', 'opp_str', 'opp_td', 'opp_sub', 'opp_pass',
                   'winner']]

df_long
df_long.query("fight_id == 0")