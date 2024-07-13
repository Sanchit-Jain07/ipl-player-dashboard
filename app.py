import streamlit as st
import pandas as pd
from data_extract import get_all_players, get_batting_stats, match_number, get_player_espn_id, get_player_meta, get_bowling_stats, get_player_teams

player_names = get_all_players()
st.title('IPL Player Stats')
player_name = st.selectbox("Select Player", player_names)
data = get_player_meta(get_player_espn_id(player_name))

st.header(data["player_full_name"])

player_image_col, player_teams_col = st.columns([2, 3])

with player_teams_col:
    st.markdown('#### Teams')
    with st.expander("Show Teams"):
        player_teams = get_player_teams(player_name)
        start_season = None
        end_season = None
        current_team = None
        for season, team in sorted(player_teams.items()):
            if current_team is None:
                current_team = team
                start_season = season
                end_season = season
            elif current_team != team:
                st.markdown(f'{start_season}-{end_season}: {current_team}')
                current_team = team
                start_season = season
                end_season = season
            else:
                end_season = season
        st.markdown(f'{start_season}-{end_season}: {current_team}')

with player_image_col:
    st.image(data["player_img"], width=200)

batting_style, bowling_style, playing_role = st.columns(3)

with batting_style:
    st.markdown('#### Batting Style')
    st.markdown(data["batting_style"])

with bowling_style:
    st.markdown('#### Bowling Style')
    st.markdown(data["bowling_style"])

with playing_role:
    st.markdown('#### Playing Role')
    st.markdown(data["playing_role"])

st.markdown('### Batting Stats')

matches, runs, balls, fours, sixes, dismissals = st.columns(6)

batting_data = None
bowling_data = None
strike_rate_df = None
economy_df = None
player_matches = None

with st.spinner('Fetching Stats'):
    player_matches = match_number(player_name)
    batting_data, season_batting_data = get_batting_stats(player_name)
    bowling_data, season_bowling_data = get_bowling_stats(player_name)
    strike_rate_df = pd.DataFrame(columns=["Season", "Strike Rate"])
    for season, stats in season_batting_data.items():
        if stats["balls"] != 0:
            strike_rate = round(stats["runs"] * 100 / stats["balls"], 2)
        else:
            strike_rate = 0
        strike_rate_df = pd.concat([strike_rate_df, pd.DataFrame({"Season": [str(season)], "Strike Rate": [strike_rate]})])

    economy_df = pd.DataFrame(columns=["Season", "Economy"])
    for season, stats in season_bowling_data.items():
        if stats["balls"] != 0:
            economy = round(stats["runs"] * 6 / stats["balls"], 2)
        else:
            economy = 0
        economy_df = pd.concat([economy_df, pd.DataFrame({"Season": [str(season)], "Economy": [economy]})])

with matches:
    st.metric('Matches', player_matches)

with runs:
    st.metric('Runs', batting_data["runs"])

with balls:
    st.metric('Balls', batting_data["balls"])

with fours:
    st.metric('Fours', batting_data["fours"])

with sixes:
    st.metric('Sixes', batting_data["sixes"])

with dismissals:
    st.metric('Dismissals', batting_data["dismissals"])

batting_strike_rate, batting_average, fifties, hundreds = st.columns(4)

with batting_strike_rate:
    if batting_data["balls"] == 0:
        st.metric('Strike Rate', 0)
    else:
        st.metric('Strike Rate', round(batting_data["runs"] * 100 / batting_data["balls"], 2))

with batting_average:
    if batting_data["dismissals"] == 0:
        st.metric('Average', 0)
    else:
        st.metric('Average', round(batting_data["runs"] / batting_data["dismissals"], 2))

with fifties:
    st.metric('Fifties', batting_data["fifties"])

with hundreds:
    st.metric('Hundreds', batting_data["hundreds"])

st.markdown('### Bowling Stats')

matches, wickets, runs, balls, economy, average = st.columns(6)

with matches:
    st.metric('Matches', player_matches)

with wickets:
    st.metric('Wickets', bowling_data["wickets"])

with runs:
    st.metric('Runs', bowling_data["runs"])

with balls:
    st.metric('Balls', bowling_data["balls"])

with economy:
    if bowling_data["balls"] == 0:
        st.metric('Economy', 0)
    else:
        st.metric('Economy', round(bowling_data["runs"] * 6 / bowling_data["balls"], 2))

with average:
    if bowling_data["wickets"] == 0:
        st.metric('Average', 0)
    else:
        st.metric('Average', round(bowling_data["runs"] / bowling_data["wickets"], 2))

st.markdown('### Season Wise Batting Strike Rate')
st.line_chart(strike_rate_df.set_index("Season"), x_label="Season", y_label="Strike Rate")

st.markdown('### Season Wise Bowling Economy')
st.line_chart(economy_df.set_index("Season"), x_label="Season", y_label="Economy")