import streamlit as st
import pandas as pd
import numpy as np
from random import shuffle

def assign_players(df, n_seeds):
    # Sort players by points
    df = df.sort_values(by='points', ascending=False).reset_index(drop=True)

    # Mark the top n_seeds as seeds and assign seed number
    df['seed'] = np.nan
    df.loc[:n_seeds-1, 'seed'] = range(1, n_seeds+1)

    # If the number of total players is odd, the highest seed(s) get a bye
    byes = []
    if df.shape[0] % 2 != 0:
        for seed in range(1, n_seeds+1):
            byes.append({'Player 1': df[df['seed'] == seed]['player name'].values[0], 'Player 2': None, 'Seed': seed})
            df = df[df['seed'] != seed]
            if df.shape[0] % 2 == 0:  
                break

    seeds_df = df[df['seed'].notna()]
    non_seeds_df = df[df['seed'].isna()]

    seed_matchups = []
    for index, seed in seeds_df.iterrows():
        if len(non_seeds_df) > 0:
            matchup = non_seeds_df.iloc[0]
            non_seeds_df = non_seeds_df.iloc[1:]
            seed_matchups.append({'Player 1': seed['player name'], 'Player 2': matchup['player name'], 'Seed': seed['seed']})

    non_seeds = list(non_seeds_df['player name'])
    shuffle(non_seeds)
    non_seed_matchups = [{'Player 1': non_seeds[i], 'Player 2': non_seeds[i+1], 'Seed': np.nan} for i in range(0, len(non_seeds), 2)]

    byes_df = pd.DataFrame(byes)
    seed_matchups_df = pd.DataFrame(seed_matchups)
    non_seed_matchups_df = pd.DataFrame(non_seed_matchups)
    matchups_df = pd.DataFrame()

    if n_seeds >= 2:
        first_seed = byes_df[byes_df['Seed'] == 1] if not byes_df.empty and 1 in byes_df['Seed'].values else seed_matchups_df[seed_matchups_df['Seed'] == 1]
        second_seed = byes_df[byes_df['Seed'] == 2] if not byes_df.empty and 2 in byes_df['Seed'].values else seed_matchups_df[seed_matchups_df['Seed'] == 2]
        third_seed = byes_df[byes_df['Seed'] == 3] if not byes_df.empty and 3 in byes_df['Seed'].values else seed_matchups_df[seed_matchups_df['Seed'] == 3] if n_seeds >= 3 else pd.DataFrame()
        fourth_seed = byes_df[byes_df['Seed'] == 4] if not byes_df.empty and 4 in byes_df['Seed'].values else seed_matchups_df[seed_matchups_df['Seed'] == 4] if n_seeds >= 4 else pd.DataFrame()

        non_seed_half = len(non_seed_matchups_df) // 2
        first_half = non_seed_matchups_df.iloc[:non_seed_half]
        second_half = non_seed_matchups_df.iloc[non_seed_half:]

        matchups_df = pd.concat([first_seed, first_half, third_seed, fourth_seed, second_half, second_seed]).reset_index(drop=True)
    
    return matchups_df

st.title('Player Matcher')

uploaded_file = st.file_uploader("Upload an Excel file", type=['xlsx'])

if uploaded_file is not None:
    data = pd.read_excel(uploaded_file)
    n_seeds = st.slider('Number of seeds:', min_value=1, max_value=4)
    df = assign_players(data, n_seeds)
    st.dataframe(df)
else:
    st.write("Please upload a file.")
