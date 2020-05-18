import numpy as np
import pandas as pd


def shuffle_fighters(df):
    """Shuffle the order of the winning fighter

    ufcstats.com always includes the winning fighter as fighter 1. Always 
    having the same winning fighter can cause issues for some machine learning
    algorithms. To prevent these issues this function shuffles the order of
    the winning fighter into either red or blue.

    Parameters
    ----------
    df : pd.DataFrame
        The raw event_details data.

    Returns
    -------
    pd.DataFrame
        Shuffled event_details data.
    """    
    # shuffle fighter 1 and 2
    df['fight_id'] = df.index
    df['blue'] = np.random.choice(a=[1, 2], p=[0.5, 0.5], size=df.shape[0])
    df['red'] = df['blue'].apply(lambda x: 1 if x == 2 else 2)
    df['winner_colour'] = df['blue'].apply(lambda x: "blue" if x == 1 else "red")
    df['blue'] = df.apply(lambda x: x['fighter_1_name'] if x['blue'] == 1 else x['fighter_2_name'], axis=1)
    df['red'] = df.apply(lambda x: x['fighter_1_name'] if x['red'] == 1 else x['fighter_2_name'], axis=1)
    df['blue_url'] = df.apply(lambda x: x['fighter_1_url'] if x['blue'] == x['fighter_1_name'] else x['fighter_2_url'], axis=1)
    df['red_url'] = df.apply(lambda x: x['fighter_1_url'] if x['red'] == x['fighter_1_name'] else x['fighter_2_url'], axis=1)
    df['winner_name'] = df.apply(lambda x: x['blue'] if x['winner_colour'] == 'blue' else x['red'], axis=1)
    
    # stats
    df['blue_str'] = df.apply(lambda x: x['fighter_1_str'] if x['blue'] == x['fighter_1_name'] else x['fighter_2_str'], axis=1)
    df['red_str'] = df.apply(lambda x: x['fighter_1_str'] if x['red'] == x['fighter_1_name'] else x['fighter_2_str'], axis=1)
    df['blue_td'] = df.apply(lambda x: x['fighter_1_td'] if x['blue'] == x['fighter_1_name'] else x['fighter_2_td'], axis=1)
    df['red_td'] = df.apply(lambda x: x['fighter_1_td'] if x['red'] == x['fighter_1_name'] else x['fighter_2_td'], axis=1)
    df['blue_sub'] = df.apply(lambda x: x['fighter_1_sub'] if x['blue'] == x['fighter_1_name'] else x['fighter_2_sub'], axis=1)
    df['red_sub'] = df.apply(lambda x: x['fighter_1_sub'] if x['red'] == x['fighter_1_name'] else x['fighter_2_sub'], axis=1)
    df['blue_pass'] = df.apply(lambda x: x['fighter_1_pass'] if x['blue'] == x['fighter_1_name'] else x['fighter_2_pass'], axis=1)
    df['red_pass'] = df.apply(lambda x: x['fighter_1_pass'] if x['red'] == x['fighter_1_name'] else x['fighter_2_pass'], axis=1)

    # response variable
    df['blue_win'] = df['winner_colour'].apply(lambda x: 1 if x == 'blue' else 0)
    
    drop_cols = df.columns.str.startswith('fighter_')
    return df.loc[:,~drop_cols].drop(columns=['winner'])


def pivot_longer(df):
    """Pivot the dataframe longer.

    Pivots the ufc events dataframe so that each row has only 1 fighter. This
    results in each fight having two rows.

    Parameters
    ----------
    df : pd.DataFrame
        The raw event_details data.

    Returns
    -------
    pd.DataFrame
        Longer dataframe.
    """    
    cols_to_pivot = ['red', 'blue']

    df_long = df.melt(
        value_vars=cols_to_pivot,
        id_vars=[i for i in df.columns if i not in cols_to_pivot],
        value_name="name", var_name="colour"
    )

    df_long = df_long.sort_values(by='fight_id')

    df_long['fighter_url'] = df_long.apply(lambda x: x['blue_url'] if x['colour'] == 'blue' else  x['red_url'], axis=1)

    df_long['str'] = df_long.apply(lambda x: x['blue_str'] if x['colour'] == 'blue' else  x['red_str'], axis=1)
    df_long['td'] = df_long.apply(lambda x: x['blue_td'] if x['colour'] == 'blue' else  x['red_td'], axis=1)
    df_long['sub'] = df_long.apply(lambda x: x['blue_sub'] if x['colour'] == 'blue' else  x['red_sub'], axis=1)
    df_long['pass'] = df_long.apply(lambda x: x['blue_pass'] if x['colour'] == 'blue' else  x['red_pass'], axis=1)

    df_long['winner'] = df_long.apply(lambda x: 1 if x['winner_colour'] == x['colour'] else 0, axis=1)
    df_long['loser'] = df_long.apply(lambda x: 1 if x['winner_colour'] != x['colour'] else 0, axis=1)

    df_long = df_long[[
        'event_name', 'fight_id', 'date', 'weight_class', 'win_method', 
        'win_round',  'win_time',  'name', 'fighter_url', 'colour',  'str', 
        'td', 'sub', 'pass',  'winner', 'loser', 'blue_win'
    ]]

    return df_long


def win_method_binner(x):
    """Categorize win methods into bins."""
    if "DEC" in x:
        return "DEC"
    elif "TKO" in x:
        return "TKO"
    elif "SUB" in x:
        return "SUB"
    elif "Overturned" in x:
        return "Overturned"
    else:
        return x


def calculate_running_totals(df_long):
    """Calculate features that are running totals.

    Parameters
    ----------
    df_long : pd.DataFrame
        The dataframe that is returned by function `pivot_longer`.

    Returns
    -------
    pd.DataFrame
        Dataframe with additional features
    """    
    # calculate running total stats for the fighers.
    # Ideas for features:
    # wins, loss, TKO, TKO received, days since last fight, height, weight, 
    # # wing_span, win streak, loss streak, last fight time
    df_long = df_long.sort_values(by=['name', 'date'])
    df_long = df_long.reset_index(drop=True)
    df_long['win_method_bin'] = df_long['win_method'].apply(win_method_binner)
    df_long['num_fights'] = df_long.groupby('name')['event_name'].cumcount() + 1
    df_long['wins'] = df_long.groupby('name')['winner'].cumsum()
    df_long['losses'] = df_long.groupby('name')['loser'].cumsum()
    df_long['days_since_last_fight'] = df_long.groupby('name')['date'].diff().dt.days.fillna(0)
    df_long['tko_recieved'] = df_long.apply(lambda x: 1 if x['winner'] == 0 and x['win_method_bin'] == "TKO" else 0, axis=1)
    df_long['total_tko_recieved'] = df_long.groupby('name')['tko_recieved'].cumsum()
    df_long['fight_time'] = df_long.apply(lambda x: (x['win_round'] - 1) * 5 + float(x['win_time'][-2])/60 + float(x['win_time'][0]), axis=1)
    df_long['total_octagon_time'] = df_long.groupby('name')['fight_time'].cumsum()
    df_long['last_fight_time'] = df_long.groupby('name')['fight_time'].shift(periods=1).fillna(0)
    df_long['last_fight_tko_received'] = df_long.groupby('name')['tko_recieved'].shift(periods=1).fillna(0).astype(int)
    df_long['last_fight_win'] = df_long.groupby('name')['winner'].shift(periods=1).fillna(0).astype(int)
    df_long['last_fight_loss'] = df_long.groupby('name')['loser'].shift(periods=1).fillna(0).astype(int)
    # df_long['win_streak'] = np.NaN
    # df_long['loss_streak'] = np.NaN 

    return df_long
